"""Tests for core/metadata.py."""

from pathlib import Path

import piexif
import pytest

from image_optimizer.core.metadata import (
    build_exif_bytes,
    read_metadata,
    strip_metadata,
    write_metadata,
)
from image_optimizer.core.types import MetadataWriteUnsupportedError, OverwritePolicy, ValidationError


class TestReadMetadata:
    def test_basic_info(self, tmp_images):
        meta = read_metadata(tmp_images["jpeg"])
        assert meta["format"] == "JPEG"
        assert "100" in meta["dimensions"]
        assert "80" in meta["dimensions"]

    def test_png_info(self, tmp_images):
        meta = read_metadata(tmp_images["png_rgba"])
        assert meta["format"] == "PNG"
        assert meta["has_transparency"] is True

    def test_reads_written_fields(self, tmp_images, tmp_path):
        """Verify read_metadata can parse fields we wrote."""
        out = tmp_path / "with_meta.jpg"
        write_metadata(
            tmp_images["jpeg"], out,
            fields={"artist": "Read Test", "copyright": "2025 Test"},
        )
        meta = read_metadata(out)
        assert meta["has_exif"] is True
        assert "Read Test" in str(meta.get("exif", {}))


class TestStripMetadata:
    def test_strip_jpeg(self, tmp_images, tmp_path):
        out = tmp_path / "stripped.jpg"
        result = strip_metadata(tmp_images["jpeg"], out)
        assert result.success

    def test_strip_png(self, tmp_images, tmp_path):
        out = tmp_path / "stripped.png"
        result = strip_metadata(tmp_images["png_rgb"], out)
        assert result.success


class TestWriteMetadata:
    def test_write_to_jpeg(self, tmp_images, tmp_path):
        out = tmp_path / "meta.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={"artist": "Test Author", "copyright": "2024 Test"},
        )
        assert result.success
        assert "fields_written" in result.metadata

    def test_write_to_webp(self, tmp_images, tmp_path):
        out = tmp_path / "meta.webp"
        result = write_metadata(
            tmp_images["webp"], out,
            fields={"artist": "WebP Author"},
        )
        assert result.success

    def test_write_to_png(self, tmp_images, tmp_path):
        """PNG EXIF writing should now work."""
        out = tmp_path / "meta.png"
        result = write_metadata(
            tmp_images["png_rgb"], out,
            fields={"artist": "PNG Author", "description": "Test PNG metadata"},
        )
        assert result.success
        assert "artist" in result.metadata["fields_written"]
        # Verify it can be read back
        meta = read_metadata(out)
        assert meta["has_exif"] is True

    def test_write_camera_fields(self, tmp_images, tmp_path):
        out = tmp_path / "camera.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={"make": "Canon", "model": "EOS R5"},
        )
        assert result.success
        assert "make" in result.metadata["fields_written"]
        assert "model" in result.metadata["fields_written"]
        # Verify
        meta = read_metadata(out)
        exif = meta.get("exif", {})
        assert exif.get("Make") == "Canon"
        assert exif.get("Model") == "EOS R5"

    def test_write_datetime_fields(self, tmp_images, tmp_path):
        out = tmp_path / "dated.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={
                "datetime": "2025:06:15 14:30:00",
                "datetime_original": "2025:06:15 14:30:00",
            },
        )
        assert result.success
        meta = read_metadata(out)
        assert "2025:06:15 14:30:00" in str(meta.get("exif", {}))

    def test_write_datetime_invalid_format(self, tmp_images, tmp_path):
        out = tmp_path / "bad_date.jpg"
        with pytest.raises(ValidationError, match="EXIF format"):
            write_metadata(
                tmp_images["jpeg"], out,
                fields={"datetime": "2025-06-15"},
            )

    def test_write_xp_fields(self, tmp_images, tmp_path):
        """Title/keywords/subject use UTF-16LE encoding."""
        out = tmp_path / "xp.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={
                "title": "Sunset Photo",
                "keywords": "sunset; beach; vacation",
                "subject": "Nature photography",
            },
        )
        assert result.success
        meta = read_metadata(out)
        exif = meta.get("exif", {})
        assert exif.get("XPTitle") == "Sunset Photo"
        assert "sunset" in exif.get("XPKeywords", "")

    def test_write_lens_fields(self, tmp_images, tmp_path):
        out = tmp_path / "lens.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={"lens_make": "Canon", "lens_model": "RF 50mm f/1.2L"},
        )
        assert result.success
        meta = read_metadata(out)
        exif = meta.get("exif", {})
        assert exif.get("LensMake") == "Canon"
        assert "RF 50mm" in exif.get("LensModel", "")

    def test_write_orientation(self, tmp_images, tmp_path):
        out = tmp_path / "oriented.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={"orientation": "6"},
        )
        assert result.success
        meta = read_metadata(out)
        assert meta["exif"].get("Orientation") == 6

    def test_write_orientation_invalid(self, tmp_images, tmp_path):
        out = tmp_path / "bad_orient.jpg"
        with pytest.raises(ValidationError, match="1 and 8"):
            write_metadata(
                tmp_images["jpeg"], out,
                fields={"orientation": "9"},
            )

    def test_write_iso(self, tmp_images, tmp_path):
        out = tmp_path / "iso.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={"iso": "400"},
        )
        assert result.success
        meta = read_metadata(out)
        assert meta["exif"].get("ISOSpeedRatings") == 400

    def test_write_gps(self, tmp_images, tmp_path):
        out = tmp_path / "gps.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={"gps_latitude": "40.7128", "gps_longitude": "-74.0060"},
        )
        assert result.success
        assert "gps_latitude" in result.metadata["fields_written"]
        meta = read_metadata(out)
        exif = meta.get("exif", {})
        assert exif.get("GPSLatitudeRef") == "N"
        assert exif.get("GPSLongitudeRef") == "W"

    def test_write_gps_invalid_latitude(self, tmp_images, tmp_path):
        out = tmp_path / "bad_gps.jpg"
        with pytest.raises(ValidationError, match="Latitude"):
            write_metadata(
                tmp_images["jpeg"], out,
                fields={"gps_latitude": "91.0"},
            )

    def test_write_gps_invalid_longitude(self, tmp_images, tmp_path):
        out = tmp_path / "bad_gps.jpg"
        with pytest.raises(ValidationError, match="Longitude"):
            write_metadata(
                tmp_images["jpeg"], out,
                fields={"gps_longitude": "181.0"},
            )

    def test_write_comment_ascii(self, tmp_images, tmp_path):
        out = tmp_path / "comment.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={"comment": "Simple ASCII comment"},
        )
        assert result.success

    def test_write_comment_unicode(self, tmp_images, tmp_path):
        """Non-ASCII comments should use UNICODE charset prefix."""
        out = tmp_path / "unicode_comment.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={"comment": "Kommentar mit Umlauten: \u00e4\u00f6\u00fc"},
        )
        assert result.success

    def test_write_unknown_field_rejected(self, tmp_images, tmp_path):
        out = tmp_path / "unknown.jpg"
        with pytest.raises(ValidationError, match="Unknown EXIF fields"):
            write_metadata(
                tmp_images["jpeg"], out,
                fields={"nonexistent_field": "value"},
            )

    def test_write_preserves_existing_exif(self, tmp_images, tmp_path):
        """Writing new fields should preserve existing EXIF data."""
        step1 = tmp_path / "step1.jpg"
        write_metadata(
            tmp_images["jpeg"], step1,
            fields={"artist": "First Author"},
        )
        step2 = tmp_path / "step2.jpg"
        write_metadata(
            step1, step2,
            fields={"copyright": "2025 Test"},
        )
        meta = read_metadata(step2)
        exif = meta.get("exif", {})
        assert exif.get("Artist") == "First Author"
        assert "2025 Test" in exif.get("Copyright", "")

    def test_write_all_fields_together(self, tmp_images, tmp_path):
        """Comprehensive test writing many fields at once."""
        out = tmp_path / "all_fields.jpg"
        result = write_metadata(
            tmp_images["jpeg"], out,
            fields={
                "artist": "John Doe",
                "copyright": "2025 ACME",
                "description": "A test image",
                "title": "Test Image",
                "make": "Nikon",
                "model": "Z9",
                "datetime": "2025:01:15 10:00:00",
                "software": "MediaManager",
                "orientation": "1",
                "iso": "200",
                "gps_latitude": "48.8566",
                "gps_longitude": "2.3522",
            },
        )
        assert result.success
        assert len(result.metadata["fields_written"]) == 12


class TestBuildExifBytes:
    def test_returns_bytes_and_warnings(self):
        exif_bytes, warnings = build_exif_bytes(b"", {"artist": "Test"})
        assert isinstance(exif_bytes, bytes)
        assert len(exif_bytes) > 0
        assert isinstance(warnings, list)

    def test_preserves_existing_data(self):
        """build_exif_bytes should merge, not replace."""
        exif_dict = {"0th": {piexif.ImageIFD.Artist: b"Original"}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        existing = piexif.dump(exif_dict)
        new_bytes, _ = build_exif_bytes(existing, {"copyright": "2025"})
        loaded = piexif.load(new_bytes)
        assert loaded["0th"][piexif.ImageIFD.Artist] == b"Original"
        assert loaded["0th"][piexif.ImageIFD.Copyright] == b"2025"
