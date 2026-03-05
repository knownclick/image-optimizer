"""Multi-size ICO (favicon) generation."""

from __future__ import annotations

import warnings
from pathlib import Path

from PIL import Image

from image_optimizer.core.constants import FAVICON_SIZES, MAX_ICO_SIZE
from image_optimizer.core.image_io import load_image
from image_optimizer.core.types import (
    ImageSaveError,
    OperationResult,
    OverwritePolicy,
    ValidationError,
)
from image_optimizer.core.validation import validate_input_path, validate_output_path


def generate_favicon(
    input_path: str | Path,
    output_path: str | Path,
    sizes: list[int] | None = None,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Generate a multi-size ICO file.

    Auto-crops non-square sources to square (center crop).
    Clamps sizes to 16–256.
    """
    inp = validate_input_path(input_path)
    out = Path(output_path)

    # Ensure .ico extension
    if out.suffix.lower() != ".ico":
        out = out.with_suffix(".ico")

    out_resolved = validate_output_path(out, policy)
    if out_resolved is None:
        return OperationResult(
            success=True,
            input_path=inp,
            output_path=out,
            warnings=["Skipped (file exists)"],
        )

    if sizes is None:
        sizes = FAVICON_SIZES[:]

    all_warnings: list[str] = []

    # Validate and clamp sizes
    clamped: list[int] = []
    for s in sizes:
        if s < 1:
            raise ValidationError(f"Favicon size must be >= 1, got {s}")
        if s > MAX_ICO_SIZE:
            all_warnings.append(f"Favicon size {s} clamped to {MAX_ICO_SIZE}")
            s = MAX_ICO_SIZE
        clamped.append(s)
    sizes = sorted(set(clamped))

    img, info = load_image(inp)

    # Center-crop to square if needed
    if img.width != img.height:
        side = min(img.width, img.height)
        left = (img.width - side) // 2
        top = (img.height - side) // 2
        img = img.crop((left, top, left + side, top + side))
        all_warnings.append(
            f"Non-square source ({info.width}x{info.height}) "
            f"center-cropped to {side}x{side}"
        )

    # Ensure RGBA for ICO transparency
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # Generate each size
    ico_images: list[Image.Image] = []
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        ico_images.append(resized)

    try:
        ico_images[0].save(
            str(out_resolved),
            format="ICO",
            append_images=ico_images[1:],
        )
    except Exception as e:
        # Cleanup partial
        if out_resolved.exists():
            try:
                out_resolved.unlink()
            except OSError:
                pass
        raise ImageSaveError(f"Failed to save ICO: {e}")
    finally:
        img.close()
        for im in ico_images:
            im.close()

    return OperationResult(
        success=True,
        input_path=inp,
        output_path=out_resolved,
        warnings=all_warnings,
        metadata={
            "sizes": sizes,
            "output_size": out_resolved.stat().st_size,
        },
    )
