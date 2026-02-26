"""mediamanager favicon — multi-size ICO generation."""

import sys

import click

from mediamanager.cli.formatters import print_result
from mediamanager.core.types import MediaManagerError, OverwritePolicy


@click.command("favicon")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--sizes", default=None, help="Comma-separated sizes (e.g. 16,32,48,64)")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
def favicon_cmd(input_file, output_file, sizes, overwrite):
    """Generate a multi-size ICO favicon."""
    policy = OverwritePolicy.OVERWRITE if overwrite else OverwritePolicy.RENAME

    size_list = None
    if sizes:
        try:
            size_list = [int(s.strip()) for s in sizes.split(",")]
        except ValueError:
            click.secho(f"Invalid sizes: {sizes}. Use comma-separated integers.", fg="red", err=True)
            sys.exit(3)

    try:
        from mediamanager.core.favicon import generate_favicon
        result = generate_favicon(
            input_file, output_file,
            sizes=size_list,
            policy=policy,
        )
        print_result(result)
        if result.metadata.get("sizes"):
            click.echo(f"  Sizes: {result.metadata['sizes']}")
        sys.exit(0 if result.success else 2)
    except MediaManagerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
