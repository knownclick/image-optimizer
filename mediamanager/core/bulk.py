"""Bulk convert and rename operations."""

from __future__ import annotations

import shutil
import warnings
from datetime import datetime
from pathlib import Path
from typing import Callable

from mediamanager.core.constants import (
    EXTENSION_TO_FORMAT,
    FORMAT_TO_EXTENSION,
    SUPPORTED_EXTENSIONS,
)
from mediamanager.core.converter import convert_image
from mediamanager.core.image_io import load_image
from mediamanager.core.pipeline import Pipeline
from mediamanager.core.types import (
    BulkOperationError,
    BulkResult,
    ImageFormat,
    OperationResult,
    OverwritePolicy,
    ResizeMode,
    ValidationError,
)
from mediamanager.core.utils import get_image_files, sanitize_filename
from mediamanager.core.validation import validate_format, validate_rename_pattern

ProgressCallback = Callable[[int, int, str], None]  # (current, total, filename)
ErrorCallback = Callable[[str, str], None]  # (filename, error_message)


def bulk_convert(
    input_dir: str | Path,
    output_dir: str | Path,
    target_format: str,
    recursive: bool = False,
    source_formats: set[str] | None = None,
    quality: int | None = None,
    lossless: bool = False,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
    preserve_metadata: bool = True,
    progress_callback: ProgressCallback | None = None,
    error_callback: ErrorCallback | None = None,
) -> BulkResult:
    """Convert all images in a directory. Never stops on individual failure."""
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)

    if not in_dir.is_dir():
        raise BulkOperationError(f"Not a directory: {in_dir}")

    fmt_str = validate_format(target_format)
    fmt = ImageFormat(fmt_str)

    # Filter by source formats if specified
    allowed_exts = None
    if source_formats:
        allowed_exts = set()
        for sf in source_formats:
            for ext, ifmt in EXTENSION_TO_FORMAT.items():
                if ifmt.value.lower() == sf.lower():
                    allowed_exts.add(ext)

    files = get_image_files(in_dir, recursive=recursive, formats=allowed_exts)
    result = BulkResult(total=len(files))

    if not files:
        warnings.warn(f"No image files found in {in_dir}")
        return result

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise BulkOperationError(f"Permission denied creating output directory: {out_dir}")

    for i, fpath in enumerate(files):
        if progress_callback:
            progress_callback(i + 1, len(files), fpath.name)

        # Mirror directory structure
        rel = fpath.relative_to(in_dir)
        out_path = out_dir / rel.with_suffix(FORMAT_TO_EXTENSION[fmt])
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            op_result = convert_image(
                fpath, out_path, target_format,
                quality=quality,
                lossless=lossless,
                policy=policy,
                preserve_metadata=preserve_metadata,
            )
            result.results.append(op_result)
            if op_result.success:
                result.succeeded += 1
            else:
                result.failed += 1
        except Exception as e:
            result.failed += 1
            result.results.append(OperationResult(
                success=False,
                input_path=fpath,
                error_message=str(e),
            ))
            if error_callback:
                error_callback(fpath.name, str(e))

    return result


def bulk_process(
    input_dir: str | Path,
    output_dir: str | Path,
    target_format: str | None = None,
    recursive: bool = False,
    quality: int | None = None,
    lossless: bool = False,
    resize_width: int | None = None,
    resize_height: int | None = None,
    resize_mode: ResizeMode = ResizeMode.FIT,
    strip_metadata: bool = False,
    metadata_fields: dict[str, str] | None = None,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
    progress_callback: ProgressCallback | None = None,
    error_callback: ErrorCallback | None = None,
) -> BulkResult:
    """Process all images: optionally convert, resize, compress, and write metadata.

    - target_format=None keeps original format & extension.
    - Both resize dims None skips resize entirely.
    - Only width set with FIT mode auto-calculates height.
    - metadata_fields: dict of EXIF fields to write (artist, copyright, etc.)
    - Mirrors subdirectory structure in output.
    """
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)

    if not in_dir.is_dir():
        raise BulkOperationError(f"Not a directory: {in_dir}")

    fmt = None
    if target_format is not None:
        fmt_str = validate_format(target_format)
        fmt = ImageFormat(fmt_str)

    files = get_image_files(in_dir, recursive=recursive)
    result = BulkResult(total=len(files))

    if not files:
        warnings.warn(f"No image files found in {in_dir}")
        return result

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise BulkOperationError(f"Permission denied creating output directory: {out_dir}")

    do_resize = resize_width is not None or resize_height is not None

    for i, fpath in enumerate(files):
        if progress_callback:
            progress_callback(i + 1, len(files), fpath.name)

        # Mirror directory structure
        rel = fpath.relative_to(in_dir)
        if fmt is not None:
            out_path = out_dir / rel.with_suffix(FORMAT_TO_EXTENSION[fmt])
        else:
            out_path = out_dir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            pipe = Pipeline(fpath)

            if do_resize:
                pipe.resize(
                    width=resize_width,
                    height=resize_height,
                    mode=resize_mode,
                )

            if fmt is not None:
                pipe.convert(target_format)

            pipe.compress(quality=quality, lossless=lossless)

            if strip_metadata:
                pipe.strip_metadata()
            elif metadata_fields:
                pipe.write_metadata(metadata_fields)

            op_result = pipe.execute(out_path, policy=policy)
            result.results.append(op_result)
            if op_result.success:
                result.succeeded += 1
            else:
                result.failed += 1
        except Exception as e:
            result.failed += 1
            result.results.append(OperationResult(
                success=False,
                input_path=fpath,
                error_message=str(e),
            ))
            if error_callback:
                error_callback(fpath.name, str(e))

    return result


def bulk_thumbnails(
    input_dir: str | Path,
    output_dir: str | Path,
    sizes: list[int | tuple[int, int]],
    prefix: str = "thumb",
    suffix: str = "",
    recursive: bool = False,
    fmt: str | None = None,
    quality: int | None = None,
    crop_to_square: bool = False,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
    progress_callback: ProgressCallback | None = None,
    error_callback: ErrorCallback | None = None,
) -> BulkResult:
    """Generate thumbnails of multiple sizes for all images in a directory."""
    from mediamanager.core.thumbnail import generate_thumbnail

    in_dir = Path(input_dir)
    out_dir = Path(output_dir)

    if not in_dir.is_dir():
        raise BulkOperationError(f"Not a directory: {in_dir}")

    if not sizes:
        raise BulkOperationError("No sizes specified")

    files = get_image_files(in_dir, recursive=recursive)
    total_ops = len(files) * len(sizes)
    result = BulkResult(total=total_ops)

    if not files:
        warnings.warn(f"No image files found in {in_dir}")
        return result

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise BulkOperationError(f"Permission denied creating output directory: {out_dir}")
    done = 0

    for fpath in files:
        rel = fpath.relative_to(in_dir)
        file_out_dir = out_dir / rel.parent
        file_out_dir.mkdir(parents=True, exist_ok=True)

        for size in sizes:
            done += 1
            if isinstance(size, tuple):
                size_label = f"{size[0]}x{size[1]}"
            else:
                size_label = f"{size}x{size}"

            if progress_callback:
                progress_callback(done, total_ops, f"{fpath.name} ({size_label})")

            parts = [prefix, fpath.stem, size_label]
            if suffix:
                parts.append(suffix)
            out_name = "_".join(parts) + fpath.suffix
            out_path = file_out_dir / out_name

            try:
                op_result = generate_thumbnail(
                    fpath, out_path,
                    size=size,
                    fmt=fmt,
                    quality=quality,
                    crop_to_square=crop_to_square,
                    policy=policy,
                )
                result.results.append(op_result)
                if op_result.success:
                    result.succeeded += 1
                else:
                    result.failed += 1
            except Exception as e:
                result.failed += 1
                result.results.append(OperationResult(
                    success=False,
                    input_path=fpath,
                    error_message=str(e),
                ))
                if error_callback:
                    error_callback(fpath.name, str(e))

    return result


def bulk_rename(
    input_dir: str | Path,
    pattern: str,
    recursive: bool = False,
    dry_run: bool = False,
    start_number: int = 1,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
    progress_callback: ProgressCallback | None = None,
) -> BulkResult:
    """Rename image files using a pattern.

    Pattern tokens: {name}, {ext}, {n}, {n:03d}, {date}, {w}, {h}, {format}.
    Uses two-phase rename to avoid A↔B swap collisions.
    """
    in_dir = Path(input_dir)
    if not in_dir.is_dir():
        raise BulkOperationError(f"Not a directory: {in_dir}")

    files = get_image_files(in_dir, recursive=recursive)
    result = BulkResult(total=len(files))

    if not files:
        warnings.warn(f"No image files found in {in_dir}")
        return result

    # Pre-flight: compute all new names and check for collisions
    filenames = [f.name for f in files]
    import re

    renames: list[tuple[Path, Path]] = []  # (old, new)
    for i, fpath in enumerate(files):
        n = start_number + i
        stem = fpath.stem
        ext = fpath.suffix.lstrip(".")

        name = pattern
        name = name.replace("{name}", stem)
        name = name.replace("{ext}", ext)
        name = re.sub(r"\{n:([^}]+)\}", lambda m: format(n, m.group(1)), name)
        name = name.replace("{n}", str(n))

        # Metadata-dependent tokens
        try:
            img, info = load_image(fpath)
            img.close()
            name = name.replace("{w}", str(info.width))
            name = name.replace("{h}", str(info.height))
            name = name.replace("{format}", info.format.lower() if info.format else ext)
            mtime = datetime.fromtimestamp(fpath.stat().st_mtime)
            name = name.replace("{date}", mtime.strftime("%Y%m%d"))
        except Exception:
            name = name.replace("{w}", "0")
            name = name.replace("{h}", "0")
            name = name.replace("{format}", ext)
            name = name.replace("{date}", "00000000")

        name = sanitize_filename(name)
        new_path = fpath.parent / name
        renames.append((fpath, new_path))

    # Check for collisions
    new_names = [r[1].name.lower() for r in renames]
    seen: dict[str, int] = {}
    for idx, nm in enumerate(new_names):
        if nm in seen:
            raise ValidationError(
                f"Rename collision: '{renames[seen[nm]][0].name}' and "
                f"'{renames[idx][0].name}' both map to '{renames[idx][1].name}'"
            )
        seen[nm] = idx

    if dry_run:
        for old, new in renames:
            result.results.append(OperationResult(
                success=True,
                input_path=old,
                output_path=new,
                metadata={"dry_run": True},
            ))
            result.succeeded += 1
        return result

    # Two-phase rename: first rename all to temp, then to final
    import uuid
    temp_renames: list[tuple[Path, Path, Path]] = []  # (original, temp, final)
    for old, new in renames:
        temp = old.parent / f".mm_rename_{uuid.uuid4().hex}{old.suffix}"
        temp_renames.append((old, temp, new))

    # Phase 1: rename to temp
    completed_phase1: list[tuple[Path, Path]] = []
    try:
        for old, temp, final in temp_renames:
            try:
                old.rename(temp)
            except OSError:
                shutil.move(str(old), str(temp))
            completed_phase1.append((old, temp))
    except Exception as e:
        # Rollback phase 1
        for orig, tmp in reversed(completed_phase1):
            try:
                tmp.rename(orig)
            except Exception:
                pass
        raise BulkOperationError(f"Rename failed during phase 1: {e}")

    # Phase 2: rename temp to final
    for i, (old, temp, final) in enumerate(temp_renames):
        if progress_callback:
            progress_callback(i + 1, len(temp_renames), old.name)
        try:
            if final.exists() and policy == OverwritePolicy.SKIP:
                temp.rename(old)  # restore
                result.skipped += 1
                result.results.append(OperationResult(
                    success=True,
                    input_path=old,
                    output_path=old,
                    warnings=["Skipped (target exists)"],
                ))
                continue

            try:
                temp.rename(final)
            except OSError:
                shutil.move(str(temp), str(final))

            result.succeeded += 1
            result.results.append(OperationResult(
                success=True,
                input_path=old,
                output_path=final,
            ))
        except Exception as e:
            # Try to restore original filename from temp
            try:
                temp.rename(old)
            except Exception:
                pass  # temp file stranded; original name lost
            result.failed += 1
            result.results.append(OperationResult(
                success=False,
                input_path=old,
                error_message=str(e),
            ))

    return result
