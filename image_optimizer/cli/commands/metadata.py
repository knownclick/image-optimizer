"""image_optimizer metadata — read/write/strip EXIF metadata."""

import sys

import click

from image_optimizer.cli.formatters import print_metadata, print_result
from image_optimizer.core.types import ImageOptimizerError, OverwritePolicy


@click.group("metadata")
def metadata_group():
    """Read, write, or strip image metadata."""


@metadata_group.command("read")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def metadata_read(input_file, as_json):
    """Show image metadata."""
    try:
        from image_optimizer.core.metadata import read_metadata
        meta = read_metadata(input_file)
        print_metadata(meta, as_json=as_json)
    except ImageOptimizerError as e:
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
        from image_optimizer.core.metadata import strip_metadata
        result = strip_metadata(input_file, output_file, policy=policy)
        print_result(result)
        sys.exit(0 if result.success else 2)
    except ImageOptimizerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)


@metadata_group.command("write")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
# Standard fields
@click.option("--artist", default=None, help="Artist / photographer name")
@click.option("--copyright", default=None, help="Copyright notice")
@click.option("--description", default=None, help="Image description")
@click.option("--software", default=None, help="Software used")
@click.option("--comment", default=None, help="User comment (supports Unicode)")
# Title / keywords / subject (Windows XP extended fields)
@click.option("--title", default=None, help="Image title")
@click.option("--keywords", default=None, help="Keywords (semicolon-separated)")
@click.option("--subject", default=None, help="Subject description")
# Camera / lens
@click.option("--make", default=None, help="Camera manufacturer")
@click.option("--model", default=None, help="Camera model")
@click.option("--lens-make", default=None, help="Lens manufacturer")
@click.option("--lens-model", default=None, help="Lens model")
# Date/time (format: YYYY:MM:DD HH:MM:SS)
@click.option("--datetime", "dt", default=None, help="Date/time (YYYY:MM:DD HH:MM:SS)")
@click.option("--datetime-original", "dt_orig", default=None, help="Original capture date (YYYY:MM:DD HH:MM:SS)")
@click.option("--datetime-digitized", "dt_digi", default=None, help="Digitized date (YYYY:MM:DD HH:MM:SS)")
# Numeric fields
@click.option("--orientation", default=None, help="Image orientation (1-8)")
@click.option("--iso", default=None, help="ISO speed (1-65535)")
# GPS
@click.option("--gps-latitude", default=None, help="GPS latitude in decimal degrees (e.g. 40.7128)")
@click.option("--gps-longitude", default=None, help="GPS longitude in decimal degrees (e.g. -74.0060)")
# Output policy
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
def metadata_write(
    input_file, output_file,
    artist, copyright, description, software, comment,
    title, keywords, subject,
    make, model, lens_make, lens_model,
    dt, dt_orig, dt_digi,
    orientation, iso,
    gps_latitude, gps_longitude,
    overwrite,
):
    """Write EXIF metadata fields to an image (JPEG, WebP, PNG)."""
    fields = {}
    # Map CLI option names to field names
    option_map = {
        "artist": artist,
        "copyright": copyright,
        "description": description,
        "software": software,
        "comment": comment,
        "title": title,
        "keywords": keywords,
        "subject": subject,
        "make": make,
        "model": model,
        "lens_make": lens_make,
        "lens_model": lens_model,
        "datetime": dt,
        "datetime_original": dt_orig,
        "datetime_digitized": dt_digi,
        "orientation": orientation,
        "iso": iso,
        "gps_latitude": gps_latitude,
        "gps_longitude": gps_longitude,
    }

    for key, value in option_map.items():
        if value:
            fields[key] = value

    if not fields:
        click.secho("No metadata fields specified", fg="yellow", err=True)
        sys.exit(3)

    policy = OverwritePolicy.OVERWRITE if overwrite else OverwritePolicy.RENAME

    try:
        from image_optimizer.core.metadata import write_metadata
        result = write_metadata(input_file, output_file, fields, policy=policy)
        print_result(result)
        sys.exit(0 if result.success else 2)
    except ImageOptimizerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
