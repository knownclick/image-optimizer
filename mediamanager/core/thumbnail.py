"""Thumbnail generation with presets and custom sizes."""

from __future__ import annotations

import warnings
from pathlib import Path

from PIL import Image

from mediamanager.core.constants import (
    DEFAULT_QUALITY,
    FORMAT_TO_EXTENSION,
    PILLOW_FORMAT_MAP,
    THUMBNAIL_SIZES,
)
from mediamanager.core.image_io import load_image, save_image
from mediamanager.core.types import (
    ImageFormat,
    OperationResult,
    OverwritePolicy,
    ThumbnailPreset,
    ValidationError,
)
from mediamanager.core.validation import validate_input_path


def generate_thumbnails(
    input_path: str | Path,
    output_dir: str | Path,
    sizes: list[int | tuple[int, int]],
    prefix: str = "thumb",
    suffix: str = "",
    fmt: str | None = None,
    quality: int | None = None,
    crop_to_square: bool = False,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> list[OperationResult]:
    """Generate thumbnails at multiple sizes for a single image.

    Output filenames: {prefix}_{stem}_{W}x{H}_{suffix}.{ext}
    Suffix part is omitted if empty.
    """
    inp = Path(input_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for size in sizes:
        if isinstance(size, tuple):
            size_label = f"{size[0]}x{size[1]}"
        else:
            size_label = f"{size}x{size}"

        parts = [prefix, inp.stem, size_label]
        if suffix:
            parts.append(suffix)
        out_name = "_".join(parts) + inp.suffix
        out_path = out_dir / out_name

        result = generate_thumbnail(
            inp, out_path, size=size, fmt=fmt, quality=quality,
            crop_to_square=crop_to_square, policy=policy,
        )
        results.append(result)

    return results


def generate_thumbnail(
    input_path: str | Path,
    output_path: str | Path,
    size: int | ThumbnailPreset | tuple[int, int] = ThumbnailPreset.MEDIUM,
    fmt: str | None = None,
    quality: int | None = None,
    crop_to_square: bool = False,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Generate a thumbnail. Uses Pillow thumbnail() — never upscales.

    Args:
        size: Preset, single int (square), or (w, h) tuple.
        crop_to_square: If True, center-crop to square before thumbnailing.
    """
    inp = validate_input_path(input_path)
    img, info = load_image(inp)
    all_warnings: list[str] = []

    # Resolve size
    if isinstance(size, ThumbnailPreset):
        thumb_size = THUMBNAIL_SIZES[size]
    elif isinstance(size, int):
        thumb_size = (size, size)
    elif isinstance(size, tuple) and len(size) == 2:
        thumb_size = size
    else:
        raise ValidationError(f"Invalid thumbnail size: {size}")

    # Warn if source is smaller than requested thumbnail
    if info.width < thumb_size[0] or info.height < thumb_size[1]:
        all_warnings.append(
            f"Source ({info.width}x{info.height}) is smaller than requested "
            f"thumbnail ({thumb_size[0]}x{thumb_size[1]}) — will not upscale"
        )

    # Optional square crop
    if crop_to_square and img.width != img.height:
        side = min(img.width, img.height)
        left = (img.width - side) // 2
        top = (img.height - side) // 2
        img = img.crop((left, top, left + side, top + side))

    # Generate thumbnail (modifies in-place, never upscales)
    img.thumbnail(thumb_size, Image.Resampling.LANCZOS)

    # Capture dimensions before close
    thumb_w, thumb_h = img.width, img.height

    # Determine output format
    out = Path(output_path)
    if fmt:
        from mediamanager.core.validation import validate_format
        fmt_str = validate_format(fmt)
        target_fmt = ImageFormat(fmt_str)
        expected_ext = FORMAT_TO_EXTENSION[target_fmt]
        if out.suffix.lower() != expected_ext:
            out = out.with_suffix(expected_ext)
    else:
        pillow_fmt = PILLOW_FORMAT_MAP.get(info.format)
        target_fmt = pillow_fmt if pillow_fmt else ImageFormat.PNG

    try:
        result = save_image(img, out, target_fmt, quality=quality, policy=policy)
    finally:
        img.close()

    result.input_path = inp
    result.warnings = all_warnings + result.warnings
    result.metadata["thumbnail_size"] = f"{thumb_w}x{thumb_h}"
    result.metadata["original_dimensions"] = f"{info.width}x{info.height}"
    return result
