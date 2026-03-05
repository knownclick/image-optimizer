"""Enums, dataclasses, and error hierarchy for Image Optimizer."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Enums ──────────────────────────────────────────────────────────────────

class ImageFormat(enum.Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    AVIF = "AVIF"
    ICO = "ICO"


class ResizeMode(enum.Enum):
    EXACT = "exact"
    FIT = "fit"
    FILL = "fill"
    PERCENTAGE = "percentage"


class CompressionMode(enum.Enum):
    LOSSY = "lossy"
    LOSSLESS = "lossless"


class OverwritePolicy(enum.Enum):
    SKIP = "skip"
    OVERWRITE = "overwrite"
    RENAME = "rename"
    ASK = "ask"


class ThumbnailPreset(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"


# ── Result Types ───────────────────────────────────────────────────────────

@dataclass
class OperationResult:
    success: bool
    input_path: Path | None = None
    output_path: Path | None = None
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BulkResult:
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    results: list[OperationResult] = field(default_factory=list)


@dataclass
class ImageInfo:
    path: Path
    format: str
    mode: str
    width: int
    height: int
    file_size: int
    is_animated: bool = False
    has_exif: bool = False
    has_transparency: bool = False


# ── Error Hierarchy ────────────────────────────────────────────────────────

class ImageOptimizerError(Exception):
    """Base exception for all Image Optimizer errors."""


class ValidationError(ImageOptimizerError):
    """Invalid user input."""


class ImageLoadError(ImageOptimizerError):
    """Failed to load/decode image."""


class ImageSaveError(ImageOptimizerError):
    """Failed to save/encode image."""


class FormatNotAvailableError(ImageOptimizerError):
    """Requested format codec not installed (e.g. AVIF)."""


class FormatConversionError(ImageOptimizerError):
    """Conversion between two formats failed."""


class MetadataError(ImageOptimizerError):
    """General metadata operation failure."""


class MetadataWriteUnsupportedError(MetadataError):
    """Format does not support writing EXIF metadata."""


class PermissionDeniedError(ImageOptimizerError):
    """Cannot read/write file due to permissions."""


class DiskFullError(ImageOptimizerError):
    """Not enough disk space to save output."""


class BulkOperationError(ImageOptimizerError):
    """Fatal error during bulk operation (not per-file)."""
