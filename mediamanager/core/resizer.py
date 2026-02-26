"""Resize by dimensions, percentage, fit, or fill."""

from __future__ import annotations

import warnings
from pathlib import Path

from PIL import Image

from mediamanager.core.constants import DEFAULT_QUALITY, FORMAT_TO_EXTENSION, PILLOW_FORMAT_MAP
from mediamanager.core.image_io import load_image, save_image
from mediamanager.core.types import (
    ImageFormat,
    OperationResult,
    OverwritePolicy,
    ResizeMode,
    ValidationError,
)
from mediamanager.core.validation import (
    validate_dimensions,
    validate_input_path,
    validate_percentage,
)


def calculate_dimensions(
    orig_w: int,
    orig_h: int,
    target_w: int | None,
    target_h: int | None,
    mode: ResizeMode,
    percentage: float | None = None,
) -> tuple[int, int]:
    """Pure function for dimension math.

    Returns (new_width, new_height).
    """
    if mode == ResizeMode.PERCENTAGE:
        if percentage is None:
            raise ValidationError("Percentage required for PERCENTAGE mode")
        new_w = max(1, round(orig_w * percentage / 100))
        new_h = max(1, round(orig_h * percentage / 100))
        return new_w, new_h

    if mode == ResizeMode.EXACT:
        if target_w is None or target_h is None:
            raise ValidationError("Both width and height required for EXACT mode")
        return target_w, target_h

    if mode == ResizeMode.FIT:
        # Scale to fit within target, preserving aspect ratio
        if target_w is None and target_h is None:
            raise ValidationError("At least one dimension required for FIT mode")
        ratio = orig_w / orig_h
        if target_w is not None and target_h is not None:
            # Fit within both constraints
            if target_w / target_h > ratio:
                new_h = target_h
                new_w = max(1, round(new_h * ratio))
            else:
                new_w = target_w
                new_h = max(1, round(new_w / ratio))
        elif target_w is not None:
            new_w = target_w
            new_h = max(1, round(new_w / ratio))
        else:
            new_h = target_h  # type: ignore[assignment]
            new_w = max(1, round(new_h * ratio))
        return new_w, new_h

    if mode == ResizeMode.FILL:
        # Scale + center-crop to fill target exactly
        if target_w is None or target_h is None:
            raise ValidationError("Both width and height required for FILL mode")
        ratio = orig_w / orig_h
        target_ratio = target_w / target_h
        if ratio > target_ratio:
            # Image is wider — scale by height, crop width
            scale_h = target_h
            scale_w = max(1, round(scale_h * ratio))
        else:
            # Image is taller — scale by width, crop height
            scale_w = target_w
            scale_h = max(1, round(scale_w / ratio))
        return scale_w, scale_h

    raise ValidationError(f"Unknown resize mode: {mode}")


def resize_image(
    input_path: str | Path,
    output_path: str | Path,
    width: int | None = None,
    height: int | None = None,
    percentage: float | None = None,
    mode: ResizeMode = ResizeMode.FIT,
    resample: Image.Resampling = Image.Resampling.LANCZOS,
    fmt: str | None = None,
    quality: int | None = None,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Resize image in 4 modes: EXACT, FIT, FILL, PERCENTAGE."""
    inp = validate_input_path(input_path)

    if mode == ResizeMode.PERCENTAGE:
        if percentage is None:
            raise ValidationError("Percentage is required for PERCENTAGE mode")
        validate_percentage(percentage)
    else:
        validate_dimensions(width, height, allow_none=(mode == ResizeMode.FIT))

    img, info = load_image(inp)
    all_warnings: list[str] = []

    # Calculate new dimensions
    new_w, new_h = calculate_dimensions(
        info.width, info.height, width, height, mode, percentage
    )

    # Warn about aspect ratio change in EXACT mode
    if mode == ResizeMode.EXACT:
        orig_ratio = info.width / info.height
        new_ratio = new_w / new_h
        if abs(orig_ratio - new_ratio) > 0.01:
            all_warnings.append(
                f"Aspect ratio changed from {orig_ratio:.2f} to {new_ratio:.2f}"
            )

    # Resize
    resized = img.resize((new_w, new_h), resample=resample)

    # FILL mode: center-crop to exact target
    if mode == ResizeMode.FILL and width and height:
        if resized.width != width or resized.height != height:
            left = (resized.width - width) // 2
            top = (resized.height - height) // 2
            resized = resized.crop((left, top, left + width, top + height))

    # Record final dimensions after any cropping
    final_w, final_h = resized.width, resized.height

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
        # Use source format or infer from extension
        pillow_fmt = PILLOW_FORMAT_MAP.get(info.format)
        if pillow_fmt:
            target_fmt = pillow_fmt
        else:
            target_fmt = ImageFormat.PNG  # safe default

    exif_bytes = img.info.get("exif") if info.has_exif else None

    try:
        result = save_image(
            resized, out, target_fmt,
            quality=quality,
            exif_bytes=exif_bytes,
            policy=policy,
        )
    finally:
        img.close()
        resized.close()

    result.input_path = inp
    result.warnings = all_warnings + result.warnings
    result.metadata["original_dimensions"] = f"{info.width}x{info.height}"
    result.metadata["new_dimensions"] = f"{final_w}x{final_h}"
    result.metadata["resize_mode"] = mode.value
    return result
