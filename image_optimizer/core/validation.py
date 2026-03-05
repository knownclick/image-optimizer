"""All input validation — raises typed errors on invalid input."""

from __future__ import annotations

import os
import re
import warnings
from pathlib import Path

from image_optimizer.core.constants import (
    EXTENSION_TO_FORMAT,
    FORMAT_ALIASES,
    MAX_DIMENSION,
    MIN_DIMENSION,
    QUALITY_RANGES,
)
from image_optimizer.core.types import (
    ImageFormat,
    OverwritePolicy,
    ValidationError,
    FormatNotAvailableError,
)
from image_optimizer.core.utils import ensure_avif_support, generate_unique_path


def validate_input_path(path: str | Path) -> Path:
    """Verify file exists, is readable, and is non-empty."""
    p = Path(path).resolve()
    if not p.exists():
        raise ValidationError(f"File not found: {p}")
    if not p.is_file():
        raise ValidationError(f"Not a file: {p}")
    if not os.access(p, os.R_OK):
        raise ValidationError(f"Permission denied (not readable): {p}")
    if p.stat().st_size == 0:
        raise ValidationError(f"File is empty (zero bytes): {p}")
    return p


def validate_output_path(
    path: str | Path,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> Path | None:
    """Verify output path is writable. Returns None if policy=SKIP and file exists."""
    p = Path(path).resolve()

    if p.exists():
        if policy == OverwritePolicy.SKIP:
            return None
        if policy == OverwritePolicy.RENAME:
            p = generate_unique_path(p)
        elif policy == OverwritePolicy.OVERWRITE:
            pass  # will overwrite
        elif policy == OverwritePolicy.ASK:
            raise ValidationError(
                f"Output file already exists: {p}. "
                "Use --overwrite, --skip, or --rename to handle."
            )

    # Create parent dirs only after policy checks pass
    p.parent.mkdir(parents=True, exist_ok=True)

    if not os.access(p.parent, os.W_OK):
        raise ValidationError(f"Permission denied (directory not writable): {p.parent}")

    return p


def validate_format(format_str: str) -> str:
    """Normalize a format string like 'jpg' → 'JPEG'. Checks AVIF availability."""
    key = format_str.strip().lower()
    pillow_name = FORMAT_ALIASES.get(key)
    if pillow_name is None:
        supported = ", ".join(sorted(FORMAT_ALIASES.keys()))
        raise ValidationError(
            f"Unsupported format: '{format_str}'. Supported: {supported}"
        )

    if pillow_name == "AVIF" and not ensure_avif_support():
        raise FormatNotAvailableError(
            "AVIF format is not available. Install it with: pip install pillow-avif-plugin"
        )

    return pillow_name


def validate_dimensions(
    width: int | None,
    height: int | None,
    allow_none: bool = False,
) -> tuple[int | None, int | None]:
    """Check dimension range. Returns (width, height)."""
    for name, val in [("width", width), ("height", height)]:
        if val is None:
            if not allow_none:
                raise ValidationError(f"{name} is required")
            continue
        if not isinstance(val, int):
            raise ValidationError(f"{name} must be an integer, got {type(val).__name__}")
        if val < MIN_DIMENSION:
            raise ValidationError(f"{name} must be >= {MIN_DIMENSION}, got {val}")
        if val > MAX_DIMENSION:
            raise ValidationError(f"{name} must be <= {MAX_DIMENSION}, got {val}")
    return (width, height)


def validate_quality(quality: int, fmt: ImageFormat) -> int:
    """Check quality is in valid range for the format. Clamps + warns if out of range."""
    qrange = QUALITY_RANGES.get(fmt)
    if qrange is None:
        return quality  # format has no quality concept (e.g. ICO)

    lo, hi = qrange
    if quality < lo:
        warnings.warn(f"Quality {quality} below minimum {lo} for {fmt.value}; clamped to {lo}")
        return lo
    if quality > hi:
        warnings.warn(f"Quality {quality} above maximum {hi} for {fmt.value}; clamped to {hi}")
        return hi
    return quality


def validate_percentage(pct: float) -> float:
    """Check resize percentage is sane."""
    if pct <= 0:
        raise ValidationError(f"Percentage must be > 0, got {pct}")
    if pct > 10000:
        raise ValidationError(f"Percentage must be <= 10000, got {pct}")
    if pct > 400:
        warnings.warn(f"Resize percentage {pct}% is very large — result may be huge")
    return pct


def validate_rename_pattern(
    pattern: str,
    filenames: list[str],
    start_number: int = 1,
) -> list[str]:
    """Dry-run rename pattern against filenames, detect collisions.

    Supported placeholders: {name}, {ext}, {n}, {n:03d}, {date}, {w}, {h}, {format}.
    For dry-run we substitute {w}, {h}, {format}, {date} with placeholders.
    """
    if not pattern:
        raise ValidationError("Rename pattern cannot be empty")

    results: list[str] = []
    for i, fname in enumerate(filenames):
        stem = Path(fname).stem
        ext = Path(fname).suffix.lstrip(".")
        n = start_number + i

        # Build a temp name using the pattern
        name = pattern
        name = name.replace("{name}", stem)
        name = name.replace("{ext}", ext)
        # Handle {n:XXX} format specifiers
        name = re.sub(r"\{n:([^}]+)\}", lambda m: format(n, m.group(1)), name)
        name = name.replace("{n}", str(n))
        # Placeholders for metadata-dependent tokens (filled at rename time)
        name = name.replace("{date}", "00000000")
        name = name.replace("{w}", "0")
        name = name.replace("{h}", "0")
        name = name.replace("{format}", ext)

        if not name or name.isspace():
            raise ValidationError(f"Pattern produces empty filename for '{fname}'")

        # Check for invalid path characters
        invalid = set('<>:"|?*\x00')
        bad_chars = invalid & set(name)
        if bad_chars:
            raise ValidationError(
                f"Pattern produces invalid characters {bad_chars} for '{fname}'"
            )

        results.append(name)

    # Detect collisions
    seen: dict[str, int] = {}
    for i, name in enumerate(results):
        lower = name.lower()
        if lower in seen:
            raise ValidationError(
                f"Rename collision: '{filenames[seen[lower]]}' and '{filenames[i]}' "
                f"both map to '{name}'"
            )
        seen[lower] = i

    return results


KNOWN_EXIF_FIELDS: set[str] = {
    # Original fields
    "artist", "copyright", "description", "software", "datetime", "comment",
    # Camera / device
    "make", "model",
    # Additional dates
    "datetime_original", "datetime_digitized",
    # Windows XP extended fields
    "title", "keywords", "subject",
    # Lens info
    "lens_make", "lens_model",
    # Numeric fields
    "orientation", "iso",
    # GPS
    "gps_latitude", "gps_longitude",
}

_DATETIME_FIELDS: set[str] = {"datetime", "datetime_original", "datetime_digitized"}


def validate_exif_fields(fields: dict[str, str]) -> dict[str, str]:
    """Check EXIF field keys are recognized and values are valid."""
    unknown = set(fields.keys()) - KNOWN_EXIF_FIELDS
    if unknown:
        suggestions = ", ".join(sorted(KNOWN_EXIF_FIELDS))
        raise ValidationError(
            f"Unknown EXIF fields: {', '.join(sorted(unknown))}. "
            f"Supported: {suggestions}"
        )

    # Validate datetime fields
    for key in _DATETIME_FIELDS:
        if key in fields:
            validate_datetime_format(fields[key], key)

    # Validate orientation
    if "orientation" in fields:
        validate_orientation(fields["orientation"])

    # Validate ISO
    if "iso" in fields:
        try:
            val = int(fields["iso"])
            if val < 1 or val > 65535:
                raise ValidationError(
                    f"ISO must be between 1 and 65535, got {val}"
                )
        except ValueError:
            raise ValidationError(
                f"ISO must be an integer, got '{fields['iso']}'"
            )

    # Validate GPS coordinates
    for coord in ("gps_latitude", "gps_longitude"):
        if coord in fields:
            validate_gps_coordinate(fields[coord], coord)

    return fields


def validate_datetime_format(value: str, field_name: str = "datetime") -> str:
    """Validate EXIF datetime format: 'YYYY:MM:DD HH:MM:SS'."""
    dt_pattern = re.compile(r"^\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}$")
    if not dt_pattern.match(value):
        raise ValidationError(
            f"'{field_name}' must be in EXIF format 'YYYY:MM:DD HH:MM:SS', "
            f"got '{value}'"
        )
    return value


def validate_orientation(value: str) -> int:
    """Validate EXIF orientation value (1-8)."""
    try:
        val = int(value)
    except ValueError:
        raise ValidationError(
            f"Orientation must be an integer 1-8, got '{value}'"
        )
    if val < 1 or val > 8:
        raise ValidationError(
            f"Orientation must be between 1 and 8, got {val}"
        )
    return val


def validate_gps_coordinate(value: str, field_name: str) -> float:
    """Validate a GPS coordinate (decimal degrees)."""
    try:
        coord = float(value)
    except ValueError:
        raise ValidationError(
            f"'{field_name}' must be a decimal number, got '{value}'"
        )
    if "latitude" in field_name and (coord < -90.0 or coord > 90.0):
        raise ValidationError(
            f"Latitude must be between -90 and 90, got {coord}"
        )
    if "longitude" in field_name and (coord < -180.0 or coord > 180.0):
        raise ValidationError(
            f"Longitude must be between -180 and 180, got {coord}"
        )
    return coord
