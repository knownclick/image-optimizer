"""mediamanager bulk — bulk convert and rename operations."""

import sys

import click

from mediamanager.cli.formatters import print_bulk_result, print_result, progress_callback
from mediamanager.core.types import MediaManagerError, OverwritePolicy


@click.group("bulk")
def bulk_group():
    """Bulk image operations (convert, rename)."""


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
        from mediamanager.core.bulk import bulk_convert
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
    except MediaManagerError as e:
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
        from mediamanager.core.bulk import bulk_rename
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
    except MediaManagerError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
