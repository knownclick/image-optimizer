"""image_optimizer crop — single file crop."""

import sys

import click

from image_optimizer.cli.formatters import print_result
from image_optimizer.core.types import ImageOptimizerError, OverwritePolicy


@click.command("crop")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("-a", "--aspect-ratio", default=None, help="Aspect ratio preset (1:1, 4:3, 3:2, 16:9, 9:16, 3:4, 2:3)")
@click.option("--anchor", default="center", help="Anchor position (center, top-left, top-right, bottom-left, bottom-right)")
@click.option("-W", "--width", "crop_width", type=int, default=None, help="Crop width in pixels")
@click.option("-H", "--height", "crop_height", type=int, default=None, help="Crop height in pixels")
@click.option("-x", type=int, default=None, help="Crop X coordinate (top-left)")
@click.option("-y", type=int, default=None, help="Crop Y coordinate (top-left)")
@click.option("-f", "--format", "fmt", default=None, help="Output format")
@click.option("-q", "--quality", type=int, default=None, help="Output quality")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
def crop_cmd(input_file, output_file, aspect_ratio, anchor, crop_width, crop_height, x, y, fmt, quality, overwrite):
    """Crop an image by aspect ratio, center crop, or coordinates."""
    policy = OverwritePolicy.OVERWRITE if overwrite else OverwritePolicy.RENAME

    try:
        from image_optimizer.core.cropper import crop_image
        result = crop_image(
            input_file, output_file,
            aspect_ratio=aspect_ratio,
            crop_width=crop_width, crop_height=crop_height,
            x=x, y=y, anchor=anchor,
            fmt=fmt, quality=quality,
            policy=policy,
        )
        print_result(result)
        sys.exit(0 if result.success else 2)
    except ImageOptimizerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
