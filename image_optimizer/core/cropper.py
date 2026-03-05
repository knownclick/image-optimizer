"""Crop images by aspect ratio, center crop, or coordinates."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from image_optimizer.core.constants import PILLOW_FORMAT_MAP
from image_optimizer.core.image_io import load_image, save_image
from image_optimizer.core.types import (
    ImageFormat,
    OperationResult,
    OverwritePolicy,
    ValidationError,
)
from image_optimizer.core.validation import validate_input_path

# Aspect ratio presets: name -> (width_ratio, height_ratio)
ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "1:1": (1, 1),
    "4:3": (4, 3),
    "3:2": (3, 2),
    "16:9": (16, 9),
    "9:16": (9, 16),
    "3:4": (3, 4),
    "2:3": (2, 3),
}

# Anchor positions for aspect ratio cropping
ANCHORS = ("center", "top-left", "top-right", "bottom-left", "bottom-right")


def calculate_crop_box(
    img_w: int,
    img_h: int,
    *,
    aspect_ratio: str | None = None,
    crop_width: int | None = None,
    crop_height: int | None = None,
    x: int | None = None,
    y: int | None = None,
    anchor: str = "center",
) -> tuple[int, int, int, int]:
    """Calculate (left, top, right, bottom) crop box.

    Modes:
      1. aspect_ratio + anchor: crop to aspect ratio from anchor position
      2. crop_width + crop_height (+ optional x, y): center crop or coordinate crop
    """
    if aspect_ratio is not None:
        if aspect_ratio not in ASPECT_RATIOS:
            raise ValidationError(
                f"Unknown aspect ratio: '{aspect_ratio}'. "
                f"Choices: {', '.join(ASPECT_RATIOS)}"
            )
        ar_w, ar_h = ASPECT_RATIOS[aspect_ratio]
        target_ratio = ar_w / ar_h
        current_ratio = img_w / img_h

        if current_ratio > target_ratio:
            # Image is wider — crop width
            new_h = img_h
            new_w = int(round(img_h * target_ratio))
        else:
            # Image is taller — crop height
            new_w = img_w
            new_h = int(round(img_w / target_ratio))

        new_w = min(new_w, img_w)
        new_h = min(new_h, img_h)

        return _anchor_box(img_w, img_h, new_w, new_h, anchor)

    if crop_width is not None and crop_height is not None:
        if crop_width <= 0 or crop_height <= 0:
            raise ValidationError("Crop dimensions must be positive")
        if crop_width > img_w or crop_height > img_h:
            raise ValidationError(
                f"Crop size {crop_width}x{crop_height} exceeds image size {img_w}x{img_h}"
            )

        if x is not None and y is not None:
            # Coordinate-based crop
            if x < 0 or y < 0:
                raise ValidationError("Crop coordinates must be non-negative")
            if x + crop_width > img_w or y + crop_height > img_h:
                raise ValidationError(
                    f"Crop region ({x},{y})+({crop_width}x{crop_height}) "
                    f"exceeds image bounds ({img_w}x{img_h})"
                )
            return (x, y, x + crop_width, y + crop_height)

        # Center crop
        return _anchor_box(img_w, img_h, crop_width, crop_height, "center")

    raise ValidationError("Specify either aspect_ratio or crop_width + crop_height")


def _anchor_box(
    img_w: int, img_h: int,
    crop_w: int, crop_h: int,
    anchor: str,
) -> tuple[int, int, int, int]:
    """Position a crop_w x crop_h box within img_w x img_h at the given anchor."""
    if anchor == "center":
        left = (img_w - crop_w) // 2
        top = (img_h - crop_h) // 2
    elif anchor == "top-left":
        left, top = 0, 0
    elif anchor == "top-right":
        left = img_w - crop_w
        top = 0
    elif anchor == "bottom-left":
        left = 0
        top = img_h - crop_h
    elif anchor == "bottom-right":
        left = img_w - crop_w
        top = img_h - crop_h
    else:
        raise ValidationError(f"Unknown anchor: '{anchor}'. Choices: {', '.join(ANCHORS)}")

    return (left, top, left + crop_w, top + crop_h)


def crop_image(
    input_path: str | Path,
    output_path: str | Path,
    *,
    aspect_ratio: str | None = None,
    crop_width: int | None = None,
    crop_height: int | None = None,
    x: int | None = None,
    y: int | None = None,
    anchor: str = "center",
    fmt: str | None = None,
    quality: int | None = None,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Crop an image and save the result."""
    inp = validate_input_path(input_path)
    img, info = load_image(inp)

    box = calculate_crop_box(
        img.width, img.height,
        aspect_ratio=aspect_ratio,
        crop_width=crop_width, crop_height=crop_height,
        x=x, y=y, anchor=anchor,
    )

    cropped = img.crop(box)

    # Determine output format
    out = Path(output_path)
    if fmt:
        from image_optimizer.core.validation import validate_format
        fmt_str = validate_format(fmt)
        target_fmt = ImageFormat(fmt_str)
    else:
        pillow_fmt = PILLOW_FORMAT_MAP.get(info.format)
        target_fmt = pillow_fmt if pillow_fmt else ImageFormat.PNG

    exif_bytes = img.info.get("exif") if info.has_exif else None

    try:
        result = save_image(
            cropped, out, target_fmt,
            quality=quality,
            exif_bytes=exif_bytes,
            policy=policy,
        )
    finally:
        img.close()
        cropped.close()

    result.input_path = inp
    result.metadata["original_dimensions"] = f"{info.width}x{info.height}"
    result.metadata["crop_box"] = f"{box[0]},{box[1]},{box[2]},{box[3]}"
    result.metadata["new_dimensions"] = f"{box[2]-box[0]}x{box[3]-box[1]}"
    return result
