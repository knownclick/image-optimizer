"""image_optimizer resize — single file resize."""

import sys

import click

from image_optimizer.cli.formatters import print_result
from image_optimizer.core.types import ImageOptimizerError, OverwritePolicy, ResizeMode


@click.command("resize")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("-W", "--width", type=int, default=None, help="Target width")
@click.option("-H", "--height", type=int, default=None, help="Target height")
@click.option("-p", "--percentage", type=float, default=None, help="Resize by percentage")
@click.option("--mode", type=click.Choice(["exact", "fit", "fill", "percentage"]), default="fit", help="Resize mode")
@click.option("-f", "--format", "fmt", default=None, help="Output format")
@click.option("-q", "--quality", type=int, default=None, help="Output quality")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
def resize_cmd(input_file, output_file, width, height, percentage, mode, fmt, quality, overwrite):
    """Resize an image."""
    policy = OverwritePolicy.OVERWRITE if overwrite else OverwritePolicy.RENAME
    resize_mode = ResizeMode(mode)

    try:
        from image_optimizer.core.resizer import resize_image
        result = resize_image(
            input_file, output_file,
            width=width, height=height,
            percentage=percentage,
            mode=resize_mode,
            fmt=fmt, quality=quality,
            policy=policy,
        )
        print_result(result)
        sys.exit(0 if result.success else 2)
    except ImageOptimizerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
