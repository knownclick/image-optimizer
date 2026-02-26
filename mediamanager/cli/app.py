"""Click CLI entry point — command group and top-level options."""

from __future__ import annotations

import sys

import click

from mediamanager import __version__
from mediamanager.cli.commands.convert import convert_cmd
from mediamanager.cli.commands.resize import resize_cmd
from mediamanager.cli.commands.compress import compress_cmd
from mediamanager.cli.commands.thumbnail import thumbnail_cmd
from mediamanager.cli.commands.metadata import metadata_group
from mediamanager.cli.commands.favicon import favicon_cmd
from mediamanager.cli.commands.bulk import bulk_group


@click.group(invoke_without_command=True)
@click.option("--gui", is_flag=True, help="Launch the GUI interface")
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context, gui: bool) -> None:
    """Image Optimizer tool for Web Developers.

    Created by Hency Prajapati (Known Click Technologies)
    """
    if gui:
        try:
            from mediamanager.gui import launch_gui
            launch_gui()
        except ImportError as e:
            click.secho(f"GUI unavailable: {e}", fg="red", err=True)
            click.echo("Install customtkinter: pip install customtkinter", err=True)
            sys.exit(4)
        return

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


main.add_command(convert_cmd, "convert")
main.add_command(resize_cmd, "resize")
main.add_command(compress_cmd, "compress")
main.add_command(thumbnail_cmd, "thumbnail")
main.add_command(metadata_group, "metadata")
main.add_command(favicon_cmd, "favicon")
main.add_command(bulk_group, "bulk")
