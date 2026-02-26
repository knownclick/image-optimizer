"""Lossy, lossless, and target-size compression."""

from __future__ import annotations

import warnings
from pathlib import Path

from mediamanager.core.constants import DEFAULT_QUALITY, PILLOW_FORMAT_MAP, QUALITY_RANGES
from mediamanager.core.image_io import image_to_bytes, load_image, save_image
from mediamanager.core.types import (
    ImageFormat,
    OperationResult,
    OverwritePolicy,
    ValidationError,
)
from mediamanager.core.validation import validate_input_path, validate_quality
from mediamanager.core.utils import format_file_size


def compress_image(
    input_path: str | Path,
    output_path: str | Path,
    quality: int | None = None,
    lossless: bool = False,
    fmt: str | None = None,
    max_file_size_kb: int | None = None,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Compress an image. If max_file_size_kb is set, binary-search quality."""
    inp = validate_input_path(input_path)
    img, info = load_image(inp)

    # Determine target format
    if fmt:
        from mediamanager.core.validation import validate_format
        fmt_str = validate_format(fmt)
        target_fmt = ImageFormat(fmt_str)
    else:
        pillow_fmt = PILLOW_FORMAT_MAP.get(info.format)
        target_fmt = pillow_fmt if pillow_fmt else ImageFormat.JPEG

    all_warnings: list[str] = []
    out = Path(output_path)

    exif_bytes = img.info.get("exif") if info.has_exif else None

    if max_file_size_kb is not None:
        if max_file_size_kb <= 0:
            raise ValidationError("max_file_size_kb must be > 0")

        # Check if already under target
        target_bytes = max_file_size_kb * 1024
        if info.file_size <= target_bytes:
            all_warnings.append(
                f"File already under target size "
                f"({format_file_size(info.file_size)} <= {format_file_size(target_bytes)})"
            )

        # Binary search for quality
        qrange = QUALITY_RANGES.get(target_fmt)
        if qrange is None or target_fmt == ImageFormat.PNG:
            # PNG doesn't have lossy quality — just save with max compression
            final_quality = quality
        else:
            lo, hi = qrange
            # Use user quality as ceiling if provided
            if quality is not None and quality < hi:
                hi = max(lo, quality)
            best_quality = lo
            for _ in range(10):  # max 10 iterations
                mid = (lo + hi) // 2
                data = image_to_bytes(img, target_fmt, quality=mid)
                if len(data) <= target_bytes:
                    best_quality = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
                if lo > hi:
                    break
            final_quality = best_quality

            # Check if we can actually hit the target
            data = image_to_bytes(img, target_fmt, quality=final_quality)
            if len(data) > target_bytes:
                all_warnings.append(
                    f"Cannot reach target size {format_file_size(target_bytes)} "
                    f"even at minimum quality (got {format_file_size(len(data))})"
                )
    else:
        if quality is not None:
            final_quality = validate_quality(quality, target_fmt)
        else:
            final_quality = DEFAULT_QUALITY.get(target_fmt)

    try:
        result = save_image(
            img, out, target_fmt,
            quality=final_quality,
            lossless=lossless,
            exif_bytes=exif_bytes,
            policy=policy,
        )
    finally:
        img.close()

    result.input_path = inp
    result.warnings = all_warnings + result.warnings

    # Compute compression ratio
    output_size = result.metadata.get("output_size", 0)
    if info.file_size > 0 and output_size > 0:
        ratio = output_size / info.file_size
        result.metadata["compression_ratio"] = round(ratio, 3)
        diff = info.file_size - output_size
        result.metadata["size_reduction"] = format_file_size(abs(diff))
        if output_size > info.file_size:
            result.warnings.append(
                f"Output ({format_file_size(output_size)}) is larger than "
                f"input ({format_file_size(info.file_size)})"
            )

    result.metadata["input_size"] = info.file_size
    result.metadata["quality_used"] = final_quality
    return result
