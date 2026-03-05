"""image_optimizer bulk — bulk convert, process, thumbnail, and rename operations."""

import sys

import click

from image_optimizer.cli.formatters import print_bulk_result, print_result, progress_callback
from image_optimizer.core.types import ImageOptimizerError, OverwritePolicy, ResizeMode


@click.group("bulk")
def bulk_group():
    """Bulk image operations (convert, process, thumbnail, rename)."""


@bulk_group.command("convert")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_dir", type=click.Path())
@click.option("-f", "--format", "fmt", required=True, help="Target format")
@click.option("-r", "--recursive", is_flag=True, help="Process subdirectories")
@click.option("--source-formats", default=None, help="Only convert these formats (comma-separated)")
@click.option("-q", "--quality", type=int, default=None, help="Output quality")
@click.option("--lossless", is_flag=True, help="Lossless compression")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
@click.option("--skip", is_flag=True, help="Skip existing output files")
@click.option("--no-metadata", is_flag=True, help="Do not preserve metadata")
def bulk_convert_cmd(input_dir, output_dir, fmt, recursive, source_formats, quality,
                     lossless, overwrite, skip, no_metadata):
    """Convert all images in a directory."""
    policy = OverwritePolicy.OVERWRITE if overwrite else (OverwritePolicy.SKIP if skip else OverwritePolicy.RENAME)

    src_fmts = None
    if source_formats:
        src_fmts = {s.strip() for s in source_formats.split(",")}

    try:
        from image_optimizer.core.bulk import bulk_convert
        result = bulk_convert(
            input_dir, output_dir, fmt,
            recursive=recursive,
            source_formats=src_fmts,
            quality=quality,
            lossless=lossless,
            policy=policy,
            preserve_metadata=not no_metadata,
            progress_callback=progress_callback,
        )

        # Print per-file failures
        for r in result.results:
            if not r.success:
                print_result(r)

        print_bulk_result(result)

        if result.failed > 0:
            sys.exit(1)
        sys.exit(0)
    except ImageOptimizerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)


@bulk_group.command("process")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_dir", type=click.Path())
@click.option("-f", "--format", "fmt", default=None, help="Target format (omit to keep original)")
@click.option("-r", "--recursive", is_flag=True, help="Process subdirectories")
@click.option("-q", "--quality", type=int, default=None, help="Output quality")
@click.option("--lossless", is_flag=True, help="Lossless compression")
@click.option("-W", "--width", type=int, default=None, help="Resize width")
@click.option("-H", "--height", type=int, default=None, help="Resize height")
@click.option("-p", "--percentage", type=float, default=None, help="Scale by percentage")
@click.option("--resize-mode", type=click.Choice(["fit", "exact", "fill", "percentage"]),
              default="fit", help="Resize mode")
@click.option("--crop", "crop_ratio", default=None, help="Crop aspect ratio (e.g. 16:9)")
@click.option("--crop-anchor", default="center",
              type=click.Choice(["center", "top-left", "top-right", "bottom-left", "bottom-right"]),
              help="Crop anchor position")
@click.option("--strip-metadata", is_flag=True, help="Remove EXIF metadata")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
@click.option("--skip", is_flag=True, help="Skip existing output files")
def bulk_process_cmd(input_dir, output_dir, fmt, recursive, quality, lossless,
                     width, height, percentage, resize_mode, crop_ratio, crop_anchor,
                     strip_metadata, overwrite, skip):
    """Process all images: convert, resize, crop, compress, and strip metadata."""
    policy = OverwritePolicy.OVERWRITE if overwrite else (OverwritePolicy.SKIP if skip else OverwritePolicy.RENAME)

    try:
        from image_optimizer.core.bulk import bulk_process
        result = bulk_process(
            input_dir, output_dir,
            target_format=fmt,
            recursive=recursive,
            quality=quality,
            lossless=lossless,
            resize_width=width,
            resize_height=height,
            resize_percentage=percentage,
            resize_mode=ResizeMode(resize_mode),
            strip_metadata=strip_metadata,
            crop_aspect_ratio=crop_ratio,
            crop_anchor=crop_anchor,
            policy=policy,
            progress_callback=progress_callback,
        )

        for r in result.results:
            if not r.success:
                print_result(r)

        print_bulk_result(result)

        if result.failed > 0:
            sys.exit(1)
        sys.exit(0)
    except ImageOptimizerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)


@bulk_group.command("thumbnail")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_dir", type=click.Path())
@click.option("-s", "--sizes", required=True, help="Comma-separated sizes (e.g. 64,150,300)")
@click.option("--prefix", default="thumb", help="Filename prefix")
@click.option("--suffix", default="", help="Filename suffix")
@click.option("-r", "--recursive", is_flag=True, help="Process subdirectories")
@click.option("-f", "--format", "fmt", default=None, help="Output format")
@click.option("-q", "--quality", type=int, default=None, help="Output quality")
@click.option("--square", is_flag=True, help="Crop to square before thumbnailing")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
@click.option("--skip", is_flag=True, help="Skip existing output files")
def bulk_thumbnail_cmd(input_dir, output_dir, sizes, prefix, suffix, recursive,
                       fmt, quality, square, overwrite, skip):
    """Generate thumbnails for all images in a directory."""
    policy = OverwritePolicy.OVERWRITE if overwrite else (OverwritePolicy.SKIP if skip else OverwritePolicy.RENAME)

    size_list: list[int] = []
    for s in sizes.split(","):
        s = s.strip()
        if not s.isdigit() or int(s) <= 0:
            click.secho(f"Invalid size: '{s}' (must be a positive integer)", fg="red", err=True)
            sys.exit(2)
        size_list.append(int(s))

    try:
        from image_optimizer.core.bulk import bulk_thumbnails
        result = bulk_thumbnails(
            input_dir, output_dir, size_list,
            prefix=prefix,
            suffix=suffix,
            recursive=recursive,
            fmt=fmt,
            quality=quality,
            crop_to_square=square,
            policy=policy,
            progress_callback=progress_callback,
        )

        for r in result.results:
            if not r.success:
                print_result(r)

        print_bulk_result(result)

        if result.failed > 0:
            sys.exit(1)
        sys.exit(0)
    except ImageOptimizerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)


@bulk_group.command("rename")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.option("--pattern", required=True, help="Rename pattern (e.g. img_{n:03d}.{ext})")
@click.option("-r", "--recursive", is_flag=True, help="Process subdirectories")
@click.option("--dry-run", is_flag=True, help="Show what would be renamed without changing anything")
@click.option("--start", type=int, default=1, help="Starting number for {n}")
@click.option("--overwrite", is_flag=True, help="Overwrite existing files")
def bulk_rename_cmd(input_dir, pattern, recursive, dry_run, start, overwrite):
    """Rename image files using a pattern."""
    policy = OverwritePolicy.OVERWRITE if overwrite else OverwritePolicy.SKIP

    try:
        from image_optimizer.core.bulk import bulk_rename
        result = bulk_rename(
            input_dir, pattern,
            recursive=recursive,
            dry_run=dry_run,
            start_number=start,
            policy=policy,
            progress_callback=None if dry_run else progress_callback,
        )

        if dry_run:
            click.secho("Dry run — no files changed:", bold=True)
            for r in result.results:
                click.echo(f"  {r.input_path.name} → {r.output_path.name}")
        else:
            print_bulk_result(result)

        if result.failed > 0:
            sys.exit(1)
        sys.exit(0)
    except ImageOptimizerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
