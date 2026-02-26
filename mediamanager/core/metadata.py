"""EXIF metadata read/write/strip operations."""

from __future__ import annotations

import os
import warnings
from pathlib import Path

from mediamanager.core.constants import EXIF_WRITABLE_FORMATS, PILLOW_FORMAT_MAP
from mediamanager.core.image_io import load_image, save_image
from mediamanager.core.types import (
    ImageFormat,
    MetadataError,
    MetadataWriteUnsupportedError,
    OperationResult,
    OverwritePolicy,
)
from mediamanager.core.validation import validate_exif_fields, validate_input_path

# Maximum EXIF string value length
_MAX_EXIF_VALUE = 65535


def read_metadata(input_path: str | Path) -> dict:
    """Read all EXIF metadata into a structured dict."""
    inp = validate_input_path(input_path)
    img, info = load_image(inp)

    result: dict = {
        "format": info.format,
        "mode": info.mode,
        "dimensions": f"{info.width}x{info.height}",
        "file_size": info.file_size,
        "has_exif": info.has_exif,
        "has_transparency": info.has_transparency,
        "is_animated": info.is_animated,
    }

    if info.has_exif:
        try:
            import piexif
            exif_bytes = img.info.get("exif", b"")
            if exif_bytes:
                exif_dict = piexif.load(exif_bytes)
                parsed: dict = {}
                for ifd_name in ("0th", "Exif", "GPS", "1st"):
                    ifd = exif_dict.get(ifd_name, {})
                    for tag, value in ifd.items():
                        try:
                            tag_name = piexif.TAGS[ifd_name].get(tag, {}).get("name", str(tag))
                        except (KeyError, TypeError):
                            tag_name = str(tag)
                        # Decode bytes to string where possible
                        if isinstance(value, bytes):
                            try:
                                value = value.decode("utf-8", errors="replace").rstrip("\x00")
                            except Exception:
                                value = repr(value)
                        parsed[tag_name] = value
                result["exif"] = parsed
        except ImportError:
            result["exif"] = {"error": "piexif not installed"}
        except Exception as e:
            result["exif"] = {"error": str(e)}

    img.close()
    return result


def strip_metadata(
    input_path: str | Path,
    output_path: str | Path,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Re-save image without any metadata.

    For JPEG: uses piexif.remove for lossless strip when saving in-place.
    """
    inp = validate_input_path(input_path)
    out = Path(output_path)

    img, info = load_image(inp)
    pillow_fmt = PILLOW_FORMAT_MAP.get(info.format)
    target_fmt = pillow_fmt if pillow_fmt else ImageFormat.PNG

    # Try lossless piexif.remove for JPEG in-place
    out_resolved = out.resolve()
    is_same_file = False
    try:
        is_same_file = inp.exists() and out_resolved.exists() and os.path.samefile(inp, out_resolved)
    except (OSError, ValueError):
        is_same_file = str(inp) == str(out_resolved)
    if target_fmt == ImageFormat.JPEG and is_same_file:
        try:
            import piexif
            piexif.remove(str(inp))
            img.close()
            return OperationResult(
                success=True,
                input_path=inp,
                output_path=inp,
                metadata={"method": "piexif.remove (lossless)"},
            )
        except Exception as exc:
            warnings.warn(
                f"Lossless EXIF strip failed ({exc}), falling back to re-save"
            )

    # Re-save without exif
    try:
        result = save_image(img, out, target_fmt, exif_bytes=None, policy=policy)
    finally:
        img.close()

    result.input_path = inp
    result.metadata["method"] = "re-save without metadata"
    return result


# Mapping of our field names → piexif IFD + tag
_EXIF_FIELD_MAP: dict[str, tuple[str, int]] = {}


def _init_field_map():
    """Lazily initialize the EXIF field mapping."""
    global _EXIF_FIELD_MAP
    if _EXIF_FIELD_MAP:
        return
    try:
        import piexif
        _EXIF_FIELD_MAP.update({
            "artist": ("0th", piexif.ImageIFD.Artist),
            "copyright": ("0th", piexif.ImageIFD.Copyright),
            "description": ("0th", piexif.ImageIFD.ImageDescription),
            "software": ("0th", piexif.ImageIFD.Software),
            "datetime": ("0th", piexif.ImageIFD.DateTime),
            "comment": ("Exif", piexif.ExifIFD.UserComment),
        })
    except ImportError:
        pass


def write_metadata(
    input_path: str | Path,
    output_path: str | Path,
    fields: dict[str, str],
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Write custom EXIF fields. Only JPEG/WebP supported."""
    inp = validate_input_path(input_path)
    fields = validate_exif_fields(fields)
    out = Path(output_path)

    img, info = load_image(inp)
    pillow_fmt = PILLOW_FORMAT_MAP.get(info.format)
    target_fmt = pillow_fmt if pillow_fmt else ImageFormat.JPEG

    if target_fmt not in EXIF_WRITABLE_FORMATS:
        img.close()
        raise MetadataWriteUnsupportedError(
            f"Cannot write EXIF metadata to {target_fmt.value}. "
            f"Only JPEG and WebP are supported."
        )

    try:
        import piexif
    except ImportError:
        img.close()
        raise MetadataError("piexif is required for writing metadata: pip install piexif")

    _init_field_map()

    # Load existing EXIF or start fresh
    existing_exif = img.info.get("exif", b"")
    try:
        exif_dict = piexif.load(existing_exif) if existing_exif else {
            "0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None,
        }
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    all_warnings: list[str] = []

    for field_name, value in fields.items():
        mapping = _EXIF_FIELD_MAP.get(field_name)
        if mapping is None:
            all_warnings.append(f"Unknown EXIF field: {field_name}")
            continue

        ifd_name, tag_id = mapping

        # UserComment requires special encoding
        if field_name == "comment":
            value_bytes = b"ASCII\x00\x00\x00" + value.encode("utf-8")
        else:
            value_bytes = value.encode("utf-8")

        # Truncate to byte limit (EXIF spec)
        if len(value_bytes) > _MAX_EXIF_VALUE:
            value_bytes = value_bytes[:_MAX_EXIF_VALUE]
            all_warnings.append(f"Truncated '{field_name}' to {_MAX_EXIF_VALUE} bytes")

        exif_dict[ifd_name][tag_id] = value_bytes

    exif_bytes = piexif.dump(exif_dict)

    try:
        result = save_image(img, out, target_fmt, exif_bytes=exif_bytes, policy=policy)
    finally:
        img.close()

    result.input_path = inp
    result.warnings = all_warnings + result.warnings
    result.metadata["fields_written"] = list(fields.keys())
    return result
