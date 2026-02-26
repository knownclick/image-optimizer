"""mediamanager compress — single file compression."""

import sys

import click

from mediamanager.cli.formatters import print_result
from mediamanager.core.types import MediaManagerError, OverwritePolicy


@click.command("compress")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("-q", "--quality", type=int, default=None, help="Output quality")
@click.option("--lossless", is_flag=True, help="Lossless compression")
@click.option("-f", "--format", "fmt", default=None, help="Output format")
@click.option("--max-size", type=int, default=None, help="Target max file size in KB")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
def compress_cmd(input_file, output_file, quality, lossless, fmt, max_size, overwrite):
    """Compress/optimize an image."""
    policy = OverwritePolicy.OVERWRITE if overwrite else OverwritePolicy.RENAME

    try:
        from mediamanager.core.compressor import compress_image
        result = compress_image(
            input_file, output_file,
            quality=quality,
            lossless=lossless,
            fmt=fmt,
            max_file_size_kb=max_size,
            policy=policy,
        )
        print_result(result)
        sys.exit(0 if result.success else 2)
    except MediaManagerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
