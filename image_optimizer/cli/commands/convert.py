"""image_optimizer convert — single file format conversion."""

import sys

import click

from image_optimizer.cli.formatters import print_result
from image_optimizer.core.types import ImageOptimizerError, OverwritePolicy


@click.command("convert")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("-f", "--format", "fmt", required=True, help="Target format (jpg, png, webp, avif)")
@click.option("-q", "--quality", type=int, default=None, help="Output quality")
@click.option("--lossless", is_flag=True, help="Lossless compression (WebP/AVIF)")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
@click.option("--skip", is_flag=True, help="Skip if output exists")
@click.option("--no-metadata", is_flag=True, help="Do not preserve metadata")
def convert_cmd(input_file, output_file, fmt, quality, lossless, overwrite, skip, no_metadata):
    """Convert an image to a different format."""
    policy = OverwritePolicy.OVERWRITE if overwrite else (OverwritePolicy.SKIP if skip else OverwritePolicy.RENAME)

    try:
        from image_optimizer.core.converter import convert_image
        result = convert_image(
            input_file, output_file, fmt,
            quality=quality,
            lossless=lossless,
            policy=policy,
            preserve_metadata=not no_metadata,
        )
        print_result(result)
        sys.exit(0 if result.success else 2)
    except ImageOptimizerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
