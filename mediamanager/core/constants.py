"""Format maps, quality ranges, size limits, and other constants."""

from mediamanager.core.types import ImageFormat, ThumbnailPreset

# ── Extension → Format mapping ─────────────────────────────────────────────

EXTENSION_TO_FORMAT: dict[str, ImageFormat] = {
    ".jpg": ImageFormat.JPEG,
    ".jpeg": ImageFormat.JPEG,
    ".jpe": ImageFormat.JPEG,
    ".png": ImageFormat.PNG,
    ".webp": ImageFormat.WEBP,
    ".avif": ImageFormat.AVIF,
    ".ico": ImageFormat.ICO,
}

FORMAT_TO_EXTENSION: dict[ImageFormat, str] = {
    ImageFormat.JPEG: ".jpg",
    ImageFormat.PNG: ".png",
    ImageFormat.WEBP: ".webp",
    ImageFormat.AVIF: ".avif",
    ImageFormat.ICO: ".ico",
}

# Pillow format name → our enum
PILLOW_FORMAT_MAP: dict[str, ImageFormat] = {
    "JPEG": ImageFormat.JPEG,
    "PNG": ImageFormat.PNG,
    "WEBP": ImageFormat.WEBP,
    "AVIF": ImageFormat.AVIF,
    "ICO": ImageFormat.ICO,
}

# String aliases for user input
FORMAT_ALIASES: dict[str, str] = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "avif": "AVIF",
    "ico": "ICO",
}

# ── Formats that support EXIF writing via piexif ───────────────────────────

EXIF_WRITABLE_FORMATS: set[ImageFormat] = {ImageFormat.JPEG, ImageFormat.WEBP}

# ── Quality ranges per format ──────────────────────────────────────────────

QUALITY_RANGES: dict[ImageFormat, tuple[int, int]] = {
    ImageFormat.JPEG: (1, 95),
    ImageFormat.PNG: (0, 9),      # PNG compression level (not quality)
    ImageFormat.WEBP: (1, 100),
    ImageFormat.AVIF: (1, 100),
}

DEFAULT_QUALITY: dict[ImageFormat, int] = {
    ImageFormat.JPEG: 85,
    ImageFormat.PNG: 6,
    ImageFormat.WEBP: 80,
    ImageFormat.AVIF: 75,
}

# ── Thumbnail preset sizes ─────────────────────────────────────────────────

THUMBNAIL_SIZES: dict[ThumbnailPreset, tuple[int, int]] = {
    ThumbnailPreset.SMALL: (64, 64),
    ThumbnailPreset.MEDIUM: (150, 150),
    ThumbnailPreset.LARGE: (300, 300),
    ThumbnailPreset.XLARGE: (600, 600),
}

# ── Favicon standard sizes ─────────────────────────────────────────────────

FAVICON_SIZES: list[int] = [16, 32, 48, 64, 128, 256]

# ── Safety limits ──────────────────────────────────────────────────────────

MAX_DIMENSION: int = 65535
MAX_PIXELS: int = 178_956_970  # Pillow decompression bomb threshold
MIN_DIMENSION: int = 1
MAX_ICO_SIZE: int = 256

# ── Supported image extensions for scanning ────────────────────────────────

SUPPORTED_EXTENSIONS: set[str] = set(EXTENSION_TO_FORMAT.keys())
