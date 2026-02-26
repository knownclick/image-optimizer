"""mediamanager thumbnail — thumbnail generation."""

import sys

import click

from mediamanager.cli.formatters import print_result
from mediamanager.core.types import MediaManagerError, OverwritePolicy, ThumbnailPreset


@click.command("thumbnail")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("-s", "--size", default="medium",
              help="Preset (small/medium/large/xlarge) or integer pixels")
@click.option("-f", "--format", "fmt", default=None, help="Output format")
@click.option("-q", "--quality", type=int, default=None, help="Output quality")
@click.option("--square", is_flag=True, help="Crop to square before thumbnailing")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
def thumbnail_cmd(input_file, output_file, size, fmt, quality, square, overwrite):
    """Generate a thumbnail."""
    policy = OverwritePolicy.OVERWRITE if overwrite else OverwritePolicy.RENAME

    # Parse size — preset name or integer
    try:
        thumb_size = ThumbnailPreset(size.lower())
    except ValueError:
        try:
            thumb_size = int(size)
        except ValueError:
            click.secho(f"Invalid size: {size}. Use a preset or integer.", fg="red", err=True)
            sys.exit(3)

    try:
        from mediamanager.core.thumbnail import generate_thumbnail
        result = generate_thumbnail(
            input_file, output_file,
            size=thumb_size,
            fmt=fmt, quality=quality,
            crop_to_square=square,
            policy=policy,
        )
        print_result(result)
        sys.exit(0 if result.success else 2)
    except MediaManagerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
