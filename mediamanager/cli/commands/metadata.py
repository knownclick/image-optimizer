"""mediamanager metadata — read/write/strip EXIF metadata."""

import sys

import click

from mediamanager.cli.formatters import print_metadata, print_result
from mediamanager.core.types import MediaManagerError, OverwritePolicy


@click.group("metadata")
def metadata_group():
    """Read, write, or strip image metadata."""


@metadata_group.command("read")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def metadata_read(input_file, as_json):
    """Show image metadata."""
    try:
        from mediamanager.core.metadata import read_metadata
        meta = read_metadata(input_file)
        print_metadata(meta, as_json=as_json)
    except MediaManagerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)


@metadata_group.command("strip")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path(), required=False)
@click.option("--in-place", is_flag=True, help="Modify file in-place")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
def metadata_strip(input_file, output_file, in_place, overwrite):
    """Strip all metadata from an image."""
    if in_place:
        output_file = input_file
    elif output_file is None:
        click.secho("Provide OUTPUT_FILE or use --in-place", fg="red", err=True)
        sys.exit(3)

    policy = OverwritePolicy.OVERWRITE if (overwrite or in_place) else OverwritePolicy.RENAME

    try:
        from mediamanager.core.metadata import strip_metadata
        result = strip_metadata(input_file, output_file, policy=policy)
        print_result(result)
        sys.exit(0 if result.success else 2)
    except MediaManagerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)


@metadata_group.command("write")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--artist", default=None, help="Artist name")
@click.option("--copyright", default=None, help="Copyright notice")
@click.option("--description", default=None, help="Image description")
@click.option("--software", default=None, help="Software used")
@click.option("--datetime", "dt", default=None, help="Date/time string")
@click.option("--comment", default=None, help="User comment")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
def metadata_write(input_file, output_file, artist, copyright, description, software, dt, comment, overwrite):
    """Write custom EXIF fields to an image."""
    fields = {}
    if artist:
        fields["artist"] = artist
    if copyright:
        fields["copyright"] = copyright
    if description:
        fields["description"] = description
    if software:
        fields["software"] = software
    if dt:
        fields["datetime"] = dt
    if comment:
        fields["comment"] = comment

    if not fields:
        click.secho("No metadata fields specified", fg="yellow", err=True)
        sys.exit(3)

    policy = OverwritePolicy.OVERWRITE if overwrite else OverwritePolicy.RENAME

    try:
        from mediamanager.core.metadata import write_metadata
        result = write_metadata(input_file, output_file, fields, policy=policy)
        print_result(result)
        sys.exit(0 if result.success else 2)
    except MediaManagerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
