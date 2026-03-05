"""EXIF metadata read/write/strip operations."""

from __future__ import annotations

import os
import warnings
from pathlib import Path

from image_optimizer.core.constants import EXIF_WRITABLE_FORMATS, PILLOW_FORMAT_MAP
from image_optimizer.core.image_io import load_image, save_image
from image_optimizer.core.types import (
    ImageFormat,
    MetadataError,
    MetadataWriteUnsupportedError,
    OperationResult,
    OverwritePolicy,
)
from image_optimizer.core.validation import validate_exif_fields, validate_input_path

# Maximum EXIF string value length (bytes)
_MAX_EXIF_VALUE = 65535

# Field encoding types
_ENC_ASCII = "ascii"        # Standard ASCII string → bytes
_ENC_COMMENT = "comment"    # UserComment with charset prefix
_ENC_XP = "xp"             # Windows XP fields → UTF-16LE + null
_ENC_SHORT = "short"        # Unsigned 16-bit integer
_ENC_GPS = "gps"           # GPS coordinate (handled separately)


def read_metadata(input_path: str | Path) -> dict:
    """Read all EXIF metadata into a structured dict."""
    inp = validate_input_path(input_path)
    img, info = load_image(inp)

    result: dict = {
        "format": info.format,
        "mode": info.mode,
        "dimensions": f"{info.width}x{info.height}",
        "file_size": info.file_size,
        "has_exif": info.has_exif,
        "has_transparency": info.has_transparency,
        "is_animated": info.is_animated,
    }

    if info.has_exif:
        try:
            import piexif
            exif_bytes = img.info.get("exif", b"")
            if exif_bytes:
                exif_dict = piexif.load(exif_bytes)
                parsed: dict = {}
                for ifd_name in ("0th", "Exif", "GPS", "1st"):
                    ifd = exif_dict.get(ifd_name, {})
                    for tag, value in ifd.items():
                        try:
                            tag_name = piexif.TAGS[ifd_name].get(tag, {}).get("name", str(tag))
                        except (KeyError, TypeError):
                            tag_name = str(tag)
                        # Decode to string where possible
                        _XP_TAGS = (40091, 40092, 40093, 40094, 40095)
                        if tag in _XP_TAGS:
                            try:
                                if isinstance(value, (tuple, list)):
                                    raw = bytes(value)
                                elif isinstance(value, bytes):
                                    raw = value
                                else:
                                    raw = None
                                if raw is not None:
                                    value = raw.decode("utf-16-le").rstrip("\x00")
                            except Exception:
                                value = repr(value)
                        elif isinstance(value, bytes):
                            try:
                                value = value.decode("utf-8", errors="replace").rstrip("\x00")
                            except Exception:
                                value = repr(value)
                        parsed[tag_name] = value
                result["exif"] = parsed
        except ImportError:
            result["exif"] = {"error": "piexif not installed"}
        except Exception as e:
            result["exif"] = {"error": str(e)}

    img.close()
    return result


def strip_metadata(
    input_path: str | Path,
    output_path: str | Path,
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Re-save image without any metadata.

    For JPEG: uses piexif.remove for lossless strip when saving in-place.
    """
    inp = validate_input_path(input_path)
    out = Path(output_path)

    img, info = load_image(inp)
    pillow_fmt = PILLOW_FORMAT_MAP.get(info.format)
    target_fmt = pillow_fmt if pillow_fmt else ImageFormat.PNG

    # Try lossless piexif.remove for JPEG in-place
    out_resolved = out.resolve()
    is_same_file = False
    try:
        is_same_file = inp.exists() and out_resolved.exists() and os.path.samefile(inp, out_resolved)
    except (OSError, ValueError):
        is_same_file = str(inp) == str(out_resolved)
    if target_fmt == ImageFormat.JPEG and is_same_file:
        try:
            import piexif
            piexif.remove(str(inp))
            img.close()
            return OperationResult(
                success=True,
                input_path=inp,
                output_path=inp,
                metadata={"method": "piexif.remove (lossless)"},
            )
        except Exception as exc:
            warnings.warn(
                f"Lossless EXIF strip failed ({exc}), falling back to re-save"
            )

    # Re-save without exif
    try:
        result = save_image(img, out, target_fmt, exif_bytes=None, policy=policy)
    finally:
        img.close()

    result.input_path = inp
    result.metadata["method"] = "re-save without metadata"
    return result


# ── Field map: name → (ifd_name, tag_id, encoding_type) ──────────────────

_EXIF_FIELD_MAP: dict[str, tuple[str, int, str]] = {}


def _init_field_map():
    """Lazily initialize the EXIF field mapping."""
    global _EXIF_FIELD_MAP
    if _EXIF_FIELD_MAP:
        return
    try:
        import piexif
        _EXIF_FIELD_MAP.update({
            # Standard ASCII string fields (0th IFD)
            "artist":       ("0th", piexif.ImageIFD.Artist, _ENC_ASCII),
            "copyright":    ("0th", piexif.ImageIFD.Copyright, _ENC_ASCII),
            "description":  ("0th", piexif.ImageIFD.ImageDescription, _ENC_ASCII),
            "software":     ("0th", piexif.ImageIFD.Software, _ENC_ASCII),
            "make":         ("0th", piexif.ImageIFD.Make, _ENC_ASCII),
            "model":        ("0th", piexif.ImageIFD.Model, _ENC_ASCII),

            # DateTime fields (validated format, stored as ASCII)
            "datetime":           ("0th", piexif.ImageIFD.DateTime, _ENC_ASCII),
            "datetime_original":  ("Exif", piexif.ExifIFD.DateTimeOriginal, _ENC_ASCII),
            "datetime_digitized": ("Exif", piexif.ExifIFD.DateTimeDigitized, _ENC_ASCII),

            # UserComment (special charset prefix encoding)
            "comment": ("Exif", piexif.ExifIFD.UserComment, _ENC_COMMENT),

            # Windows XP fields (UTF-16LE encoded)
            "title":    ("0th", piexif.ImageIFD.XPTitle, _ENC_XP),
            "keywords": ("0th", piexif.ImageIFD.XPKeywords, _ENC_XP),
            "subject":  ("0th", piexif.ImageIFD.XPSubject, _ENC_XP),

            # Lens info (Exif IFD, ASCII)
            "lens_make":  ("Exif", piexif.ExifIFD.LensMake, _ENC_ASCII),
            "lens_model": ("Exif", piexif.ExifIFD.LensModel, _ENC_ASCII),

            # Integer fields
            "orientation": ("0th", piexif.ImageIFD.Orientation, _ENC_SHORT),
            "iso":         ("Exif", piexif.ExifIFD.ISOSpeedRatings, _ENC_SHORT),

            # GPS (handled via special encoding)
            "gps_latitude":  ("GPS", None, _ENC_GPS),
            "gps_longitude": ("GPS", None, _ENC_GPS),
        })
    except ImportError:
        pass


def _encode_field_value(
    field_name: str,
    value: str,
    encoding: str,
) -> bytes | int | None:
    """Encode a metadata field value according to its EXIF type.

    Returns bytes for string/comment/xp fields, int for short fields,
    or None for GPS (handled separately).
    """
    if encoding == _ENC_ASCII:
        return value.encode("utf-8")

    if encoding == _ENC_COMMENT:
        # EXIF UserComment: 8-byte charset ID + encoded text
        # Use Unicode charset for full UTF-8 support
        try:
            value.encode("ascii")
            return b"ASCII\x00\x00\x00" + value.encode("ascii")
        except UnicodeEncodeError:
            return b"UNICODE\x00" + value.encode("utf-8")

    if encoding == _ENC_XP:
        # Windows XP fields: UTF-16LE with null terminator
        return value.encode("utf-16-le") + b"\x00\x00"

    if encoding == _ENC_SHORT:
        return int(value)

    # GPS is handled by _apply_gps_fields
    return None


def _decimal_to_dms_rational(decimal_degrees: float) -> tuple:
    """Convert decimal degrees to EXIF DMS rational format.

    Returns ((deg_num, deg_den), (min_num, min_den), (sec_num, sec_den)).
    """
    abs_deg = abs(decimal_degrees)
    degrees = int(abs_deg)
    minutes_float = (abs_deg - degrees) * 60
    minutes = int(minutes_float)
    seconds_float = (minutes_float - minutes) * 60
    # Use 10000 denominator for ~0.01 arc-second precision
    seconds_num = int(round(seconds_float * 10000))
    return ((degrees, 1), (minutes, 1), (seconds_num, 10000))


def _apply_gps_fields(exif_dict: dict, fields: dict[str, str]) -> list[str]:
    """Write GPS latitude/longitude into the EXIF GPS IFD.

    Returns a list of warnings (if any).
    """
    import piexif

    gps_warnings: list[str] = []

    if "gps_latitude" in fields:
        lat = float(fields["gps_latitude"])
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = b"N" if lat >= 0 else b"S"
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = _decimal_to_dms_rational(lat)

    if "gps_longitude" in fields:
        lon = float(fields["gps_longitude"])
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = b"E" if lon >= 0 else b"W"
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = _decimal_to_dms_rational(lon)

    return gps_warnings


def build_exif_bytes(
    existing_exif: bytes,
    fields: dict[str, str],
) -> tuple[bytes, list[str]]:
    """Build EXIF bytes from existing data + new fields.

    Shared helper used by both write_metadata() and Pipeline.execute().
    Returns (exif_bytes, warnings).
    """
    import piexif

    _init_field_map()

    try:
        exif_dict = piexif.load(existing_exif) if existing_exif else {
            "0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None,
        }
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    all_warnings: list[str] = []

    # Handle GPS fields first (they set multiple tags)
    gps_fields = {k: v for k, v in fields.items() if k.startswith("gps_")}
    if gps_fields:
        gps_warnings = _apply_gps_fields(exif_dict, gps_fields)
        all_warnings.extend(gps_warnings)

    # Handle all other fields
    for field_name, value in fields.items():
        if field_name.startswith("gps_"):
            continue  # already handled above

        mapping = _EXIF_FIELD_MAP.get(field_name)
        if mapping is None:
            all_warnings.append(f"Unknown EXIF field: {field_name}")
            continue

        ifd_name, tag_id, encoding = mapping

        encoded = _encode_field_value(field_name, value, encoding)

        if isinstance(encoded, int):
            # Integer fields (SHORT) — no truncation needed
            exif_dict[ifd_name][tag_id] = encoded
        elif isinstance(encoded, bytes):
            # Truncate byte values to EXIF spec limit
            if len(encoded) > _MAX_EXIF_VALUE:
                encoded = encoded[:_MAX_EXIF_VALUE]
                all_warnings.append(f"Truncated '{field_name}' to {_MAX_EXIF_VALUE} bytes")
            exif_dict[ifd_name][tag_id] = encoded

    return piexif.dump(exif_dict), all_warnings


def write_metadata(
    input_path: str | Path,
    output_path: str | Path,
    fields: dict[str, str],
    policy: OverwritePolicy = OverwritePolicy.RENAME,
) -> OperationResult:
    """Write EXIF metadata fields to an image.

    Supports JPEG, WebP, and PNG formats.
    """
    inp = validate_input_path(input_path)
    fields = validate_exif_fields(fields)
    out = Path(output_path)

    img, info = load_image(inp)
    pillow_fmt = PILLOW_FORMAT_MAP.get(info.format)
    target_fmt = pillow_fmt if pillow_fmt else ImageFormat.JPEG

    if target_fmt not in EXIF_WRITABLE_FORMATS:
        img.close()
        supported = ", ".join(f.value for f in sorted(EXIF_WRITABLE_FORMATS, key=lambda f: f.value))
        raise MetadataWriteUnsupportedError(
            f"Cannot write EXIF metadata to {target_fmt.value}. "
            f"Supported formats: {supported}."
        )

    try:
        import piexif  # noqa: F401
    except ImportError:
        img.close()
        raise MetadataError("piexif is required for writing metadata: pip install piexif")

    existing_exif = img.info.get("exif", b"")
    exif_bytes, all_warnings = build_exif_bytes(existing_exif, fields)

    try:
        result = save_image(img, out, target_fmt, exif_bytes=exif_bytes, policy=policy)
    finally:
        img.close()

    result.input_path = inp
    result.warnings = all_warnings + result.warnings
    result.metadata["fields_written"] = list(fields.keys())
    return result
