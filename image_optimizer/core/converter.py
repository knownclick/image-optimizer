"""Format conversion between image types."""

from __future__ import annotations

import warnings
from pathlib import Path

from image_optimizer.core.constants import FORMAT_TO_EXTENSION, PILLOW_FORMAT_MAP
from image_optimizer.core.image_io import load_image, save_image
from image_optimizer.core.types import (
    FormatConversionError,
    ImageFormat,
    OperationResult,
    OverwritePolicy,
)
from image_optimizer.core.validation import validate_format, validate_input_path


def convert_image(
    input_path: str | Path,
    output_path: str | Path,
    target_format: str,
    quality: int | None = None,
    lossless: bool = False,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
    preserve_metadata: bool = True,
) -> OperationResult:
    """Convert image to a different format.

    Handles animated→first-frame, transparency, color mode conversions,
    and optional EXIF carry-over.
    """
    inp = validate_input_path(input_path)
    fmt_str = validate_format(target_format)
    fmt = ImageFormat(fmt_str)

    out = Path(output_path)
    # Ensure correct extension
    expected_ext = FORMAT_TO_EXTENSION[fmt]
    if out.suffix.lower() != expected_ext:
        out = out.with_suffix(expected_ext)

    img, info = load_image(inp)
    all_warnings: list[str] = []

    # Animated → first frame
    if info.is_animated:
        img.seek(0)
        all_warnings.append("Animated image — only first frame converted")

    # Carry over EXIF if possible
    exif_bytes = None
    if preserve_metadata and info.has_exif:
        exif_bytes = img.info.get("exif")

    try:
        result = save_image(
            img, out, fmt,
            quality=quality,
            lossless=lossless,
            exif_bytes=exif_bytes,
            policy=policy,
        )
    except Exception as e:
        raise FormatConversionError(
            f"Failed converting {info.format} → {fmt.value}: {e}"
        )
    finally:
        img.close()

    result.input_path = inp
    result.warnings = all_warnings + result.warnings
    result.metadata["source_format"] = info.format
    result.metadata["target_format"] = fmt.value
    result.metadata["input_size"] = info.file_size
    return result
