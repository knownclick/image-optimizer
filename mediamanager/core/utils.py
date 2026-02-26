"""Path helpers, filename sanitizer, and utility functions."""

from __future__ import annotations

import re
from pathlib import Path

from mediamanager.core.constants import SUPPORTED_EXTENSIONS

# Cached AVIF support check
_avif_available: bool | None = None


def ensure_avif_support() -> bool:
    """Try importing AVIF plugin, cache result."""
    global _avif_available
    if _avif_available is None:
        try:
            import pillow_avif  # noqa: F401
            _avif_available = True
        except ImportError:
            _avif_available = False
    return _avif_available


def generate_unique_path(path: Path, max_attempts: int = 10000) -> Path:
    """Append _1, _2, etc. to path stem until no collision."""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    for counter in range(1, max_attempts + 1):
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
    # Fallback: use timestamp
    import time
    return parent / f"{stem}_{int(time.time())}{suffix}"


# Windows reserved names
_RESERVED_NAMES = frozenset({
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
})


def sanitize_filename(name: str) -> str:
    """Remove invalid characters and handle Windows reserved names."""
    # Strip control characters and path separators
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = name.strip(". ")

    if not name:
        return "unnamed"

    # Handle Windows reserved names
    stem = Path(name).stem.upper()
    if stem in _RESERVED_NAMES:
        name = f"_{name}"

    return name


def get_image_files(
    directory: Path,
    recursive: bool = False,
    formats: set[str] | None = None,
) -> list[Path]:
    """Scan directory for supported image files, sorted by name."""
    allowed = formats if formats else SUPPORTED_EXTENSIONS
    pattern = "**/*" if recursive else "*"

    files = []
    for p in directory.glob(pattern):
        if p.is_file() and p.suffix.lower() in allowed:
            files.append(p)

    return sorted(files)


def format_file_size(size_bytes: int) -> str:
    """Format bytes as human-readable string (e.g. '1.5 MB')."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
