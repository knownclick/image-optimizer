"""Chain operations: load once, apply transforms in memory, save once."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from image_optimizer.core.constants import DEFAULT_QUALITY, PILLOW_FORMAT_MAP
from image_optimizer.core.image_io import load_image, save_image
from image_optimizer.core.types import (
    ImageFormat,
    OperationResult,
    OverwritePolicy,
    ResizeMode,
    ValidationError,
)
from image_optimizer.core.cropper import calculate_crop_box
from image_optimizer.core.resizer import calculate_dimensions
from image_optimizer.core.validation import validate_input_path


class Pipeline:
    """Fluent API to chain image operations.

    Usage:
        Pipeline("input.jpg")
            .resize(width=800, mode=ResizeMode.FIT)
            .convert("WEBP")
            .compress(quality=80)
            .strip_metadata()
            .execute("output.webp")
    """

    def __init__(self, input_path: str | Path):
        self._input_path = validate_input_path(input_path)
        self._operations: list[tuple[str, dict]] = []
        self._target_format: str | None = None
        self._quality: int | None = None
        self._lossless: bool = False
        self._strip_exif: bool = False
        self._exif_fields: dict[str, str] | None = None

    def resize(
        self,
        width: int | None = None,
        height: int | None = None,
        percentage: float | None = None,
        mode: ResizeMode = ResizeMode.FIT,
    ) -> Pipeline:
        self._operations.append(("resize", {
            "width": width,
            "height": height,
            "percentage": percentage,
            "mode": mode,
        }))
        return self

    def convert(self, target_format: str) -> Pipeline:
        from image_optimizer.core.validation import validate_format
        self._target_format = validate_format(target_format)
        return self

    def compress(self, quality: int | None = None, lossless: bool = False) -> Pipeline:
        self._quality = quality
        self._lossless = lossless
        return self

    def crop(
        self,
        aspect_ratio: str | None = None,
        crop_width: int | None = None,
        crop_height: int | None = None,
        x: int | None = None,
        y: int | None = None,
        anchor: str = "center",
    ) -> Pipeline:
        self._operations.append(("crop", {
            "aspect_ratio": aspect_ratio,
            "crop_width": crop_width,
            "crop_height": crop_height,
            "x": x,
            "y": y,
            "anchor": anchor,
        }))
        return self

    def strip_metadata(self) -> Pipeline:
        self._strip_exif = True
        return self

    def write_metadata(self, fields: dict[str, str]) -> Pipeline:
        if self._strip_exif:
            raise ValidationError(
                "Cannot combine strip_metadata() and write_metadata() in one pipeline. "
                "Use separate operations instead."
            )
        from image_optimizer.core.validation import validate_exif_fields
        self._exif_fields = validate_exif_fields(fields)
        return self

    def execute(
        self,
        output_path: str | Path,
        policy: OverwritePolicy = OverwritePolicy.RENAME,
    ) -> OperationResult:
        """Run the pipeline: load → transforms → save."""
        img, info = load_image(self._input_path)
        all_warnings: list[str] = []

        # Apply resize and crop operations
        for op_name, kwargs in self._operations:
            if op_name == "resize":
                new_w, new_h = calculate_dimensions(
                    img.width, img.height,
                    kwargs["width"], kwargs["height"],
                    kwargs["mode"], kwargs.get("percentage"),
                )
                # FILL mode: resize then center-crop
                if kwargs["mode"] == ResizeMode.FILL:
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    tw, th = kwargs["width"], kwargs["height"]
                    if tw and th and (img.width != tw or img.height != th):
                        left = (img.width - tw) // 2
                        top = (img.height - th) // 2
                        img = img.crop((left, top, left + tw, top + th))
                else:
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            elif op_name == "crop":
                box = calculate_crop_box(
                    img.width, img.height,
                    aspect_ratio=kwargs.get("aspect_ratio"),
                    crop_width=kwargs.get("crop_width"),
                    crop_height=kwargs.get("crop_height"),
                    x=kwargs.get("x"),
                    y=kwargs.get("y"),
                    anchor=kwargs.get("anchor", "center"),
                )
                img = img.crop(box)

        # Determine output format
        if self._target_format:
            target_fmt = ImageFormat(self._target_format)
        else:
            pillow_fmt = PILLOW_FORMAT_MAP.get(info.format)
            target_fmt = pillow_fmt if pillow_fmt else ImageFormat.PNG

        # Handle EXIF
        exif_bytes = None
        if not self._strip_exif:
            if self._exif_fields:
                try:
                    from image_optimizer.core.metadata import build_exif_bytes
                    existing = img.info.get("exif", b"")
                    exif_bytes, exif_warnings = build_exif_bytes(existing, self._exif_fields)
                    all_warnings.extend(exif_warnings)
                except ImportError:
                    all_warnings.append("piexif not available, metadata not written")
            elif info.has_exif:
                exif_bytes = img.info.get("exif")

        out = Path(output_path)
        try:
            result = save_image(
                img, out, target_fmt,
                quality=self._quality,
                lossless=self._lossless,
                exif_bytes=exif_bytes,
                policy=policy,
            )
        finally:
            img.close()

        result.input_path = self._input_path
        result.warnings = all_warnings + result.warnings
        result.metadata["pipeline"] = True
        return result
