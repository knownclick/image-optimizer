"""Safe image load/save with Pillow."""

from __future__ import annotations

import errno
import os
import warnings
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from mediamanager.core.constants import (
    DEFAULT_QUALITY,
    EXIF_WRITABLE_FORMATS,
    FORMAT_TO_EXTENSION,
    MAX_PIXELS,
    PILLOW_FORMAT_MAP,
)
from mediamanager.core.types import (
    DiskFullError,
    ImageFormat,
    ImageInfo,
    ImageLoadError,
    ImageSaveError,
    OperationResult,
    OverwritePolicy,
    PermissionDeniedError,
)
from mediamanager.core.validation import validate_output_path


def detect_format(path: Path) -> str | None:
    """Read header bytes to detect real image format."""
    try:
        with Image.open(path) as img:
            return img.format
    except Exception:
        return None


def load_image(
    path: Path,
    max_pixels: int = MAX_PIXELS,
) -> tuple[Image.Image, ImageInfo]:
    """Open, verify, and return image with metadata info.

    The caller is responsible for closing the returned Image.
    """
    Image.MAX_IMAGE_PIXELS = max_pixels

    try:
        img = Image.open(path)
    except UnidentifiedImageError:
        raise ImageLoadError(f"Not a valid image file: {path}")
    except Image.DecompressionBombError:
        raise ImageLoadError(
            f"Image exceeds {max_pixels:,} pixels (decompression bomb protection). "
            f"Pass a higher max_pixels value to override."
        )
    except PermissionError:
        raise PermissionDeniedError(f"Cannot read file: {path}")
    except Exception as e:
        raise ImageLoadError(f"Failed to open image: {path}: {e}")

    # Verify the image data is intact (verify invalidates the image, so close after)
    try:
        img.verify()
    except Exception as e:
        try:
            img.close()
        except Exception:
            pass
        raise ImageLoadError(f"Corrupt or truncated image: {path}: {e}")
    finally:
        try:
            img.close()
        except Exception:
            pass

    # Re-open after verify
    img = Image.open(path)
    img.load()

    # Detect format mismatch
    real_format = img.format or ""
    ext_lower = path.suffix.lower()
    if real_format and ext_lower:
        from mediamanager.core.constants import EXTENSION_TO_FORMAT
        expected = EXTENSION_TO_FORMAT.get(ext_lower)
        actual = PILLOW_FORMAT_MAP.get(real_format)
        if expected and actual and expected != actual:
            warnings.warn(
                f"Extension '{ext_lower}' suggests {expected.value} "
                f"but file is actually {actual.value}"
            )

    # Gather info
    is_animated = getattr(img, "is_animated", False)
    has_transparency = (
        img.mode in ("RGBA", "LA", "PA")
        or "transparency" in img.info
    )
    has_exif = "exif" in img.info

    info = ImageInfo(
        path=path,
        format=real_format,
        mode=img.mode,
        width=img.width,
        height=img.height,
        file_size=path.stat().st_size,
        is_animated=is_animated,
        has_exif=has_exif,
        has_transparency=has_transparency,
    )

    return img, info


def _prepare_for_save(
    img: Image.Image,
    fmt: ImageFormat,
) -> tuple[Image.Image, list[str]]:
    """Convert image mode as needed for the target format. Returns (img, warnings)."""
    warns: list[str] = []

    # CMYK → RGB
    if img.mode == "CMYK":
        img = img.convert("RGB")
        warns.append("Converted CMYK to RGB")

    # 16-bit / floating point → 8-bit
    if img.mode in ("I", "I;16", "F"):
        img = img.convert("L")
        warns.append("Converted 16-bit/float to 8-bit")

    # Palette mode
    if img.mode == "P":
        if "transparency" in img.info and fmt != ImageFormat.JPEG:
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")
        warns.append("Converted palette mode")

    # RGBA → RGB for JPEG (composite on white)
    if fmt == ImageFormat.JPEG and img.mode in ("RGBA", "LA", "PA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1])
        img = background
        warns.append("Transparency composited on white background (JPEG has no alpha)")

    # Ensure RGB/L for JPEG
    if fmt == ImageFormat.JPEG and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    return img, warns


def save_image(
    img: Image.Image,
    path: Path,
    fmt: ImageFormat,
    quality: int | None = None,
    lossless: bool = False,
    exif_bytes: bytes | None = None,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Save image with format-specific kwargs. Cleans up partial file on error."""
    out = validate_output_path(path, policy)
    if out is None:
        return OperationResult(
            success=True,
            input_path=None,
            output_path=path,
            warnings=["Skipped (file exists)"],
        )

    img, mode_warnings = _prepare_for_save(img, fmt)

    # Build save kwargs
    kwargs: dict = {}
    pillow_format = fmt.value
    if fmt == ImageFormat.WEBP:
        pillow_format = "WEBP"

    if quality is not None:
        if fmt == ImageFormat.PNG:
            kwargs["compress_level"] = quality
        else:
            kwargs["quality"] = quality
    elif fmt in DEFAULT_QUALITY:
        if fmt == ImageFormat.PNG:
            kwargs["compress_level"] = DEFAULT_QUALITY[fmt]
        else:
            kwargs["quality"] = DEFAULT_QUALITY[fmt]

    if lossless and fmt in (ImageFormat.WEBP, ImageFormat.AVIF):
        kwargs["lossless"] = True

    if fmt == ImageFormat.PNG:
        kwargs["optimize"] = True

    if exif_bytes and fmt in EXIF_WRITABLE_FORMATS:
        kwargs["exif"] = exif_bytes

    if fmt == ImageFormat.JPEG:
        kwargs.setdefault("optimize", True)

    try:
        img.save(str(out), format=pillow_format, **kwargs)
    except PermissionError:
        if out.exists():
            try:
                out.unlink()
            except OSError:
                pass
        raise PermissionDeniedError(f"Permission denied writing to: {out}")
    except OSError as e:
        # Clean up partial file
        if out.exists():
            try:
                out.unlink()
            except OSError:
                pass
        if e.errno == errno.ENOSPC:
            raise DiskFullError(f"Disk full while saving: {out}")
        raise ImageSaveError(f"Failed to save image: {out}: {e}")
    except Exception as e:
        if out.exists():
            try:
                out.unlink()
            except OSError:
                pass
        raise ImageSaveError(f"Failed to save image: {out}: {e}")

    return OperationResult(
        success=True,
        output_path=out,
        warnings=mode_warnings,
        metadata={
            "output_size": out.stat().st_size,
            "format": fmt.value,
        },
    )


def image_to_bytes(
    img: Image.Image,
    fmt: ImageFormat,
    quality: int | None = None,
    lossless: bool = False,
) -> bytes:
    """Encode image to bytes in memory (used by compressor for binary search)."""
    img, _ = _prepare_for_save(img, fmt)

    kwargs: dict = {}
    pillow_format = fmt.value

    if quality is not None:
        if fmt == ImageFormat.PNG:
            kwargs["compress_level"] = quality
        else:
            kwargs["quality"] = quality

    if lossless and fmt in (ImageFormat.WEBP, ImageFormat.AVIF):
        kwargs["lossless"] = True

    buf = BytesIO()
    img.save(buf, format=pillow_format, **kwargs)
    return buf.getvalue()
