"""CLI output: progress display, tables, colors."""

from __future__ import annotations

import sys

import click

from image_optimizer.core.types import BulkResult, OperationResult
from image_optimizer.core.utils import format_file_size


def print_result(result: OperationResult) -> None:
    """Print a single operation result."""
    if result.success:
        click.secho("OK", fg="green", nl=False)
        if result.output_path:
            click.echo(f"  {result.output_path}")
        else:
            click.echo()
    else:
        click.secho("FAIL", fg="red", nl=False)
        click.echo(f"  {result.error_message or 'Unknown error'}")

    for w in result.warnings:
        click.secho(f"  Warning: {w}", fg="yellow")

    # Print key metadata
    meta = result.metadata
    if "compression_ratio" in meta:
        ratio = meta["compression_ratio"]
        click.echo(f"  Compression: {ratio:.1%} of original")
    if "size_reduction" in meta:
        click.echo(f"  Saved: {meta['size_reduction']}")
    if "output_size" in meta:
        click.echo(f"  Output: {format_file_size(meta['output_size'])}")


def print_bulk_result(result: BulkResult) -> None:
    """Print bulk operation summary."""
    click.echo()
    click.secho("─── Summary ───", bold=True)
    click.echo(f"  Total:     {result.total}")
    click.secho(f"  Succeeded: {result.succeeded}", fg="green")
    if result.failed:
        click.secho(f"  Failed:    {result.failed}", fg="red")
    if result.skipped:
        click.secho(f"  Skipped:   {result.skipped}", fg="yellow")


def print_metadata(metadata: dict, as_json: bool = False) -> None:
    """Print metadata dict."""
    if as_json:
        import json
        click.echo(json.dumps(metadata, indent=2, default=str))
        return

    for key, value in metadata.items():
        if isinstance(value, dict):
            click.secho(f"\n{key}:", bold=True)
            for k, v in value.items():
                click.echo(f"  {k}: {v}")
        else:
            click.echo(f"{key}: {value}")


def progress_callback(current: int, total: int, filename: str) -> None:
    """Simple progress display for bulk operations."""
    pct = current / total * 100 if total else 0
    bar_len = 30
    filled = int(bar_len * current / total) if total else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    sys.stdout.write(f"\r  {bar} {pct:5.1f}% ({current}/{total}) {filename[:40]:<40}")
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")
