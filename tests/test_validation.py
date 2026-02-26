"""Tests for core/validation.py."""

import warnings
from pathlib import Path

import pytest

from mediamanager.core.types import (
    ImageFormat,
    OverwritePolicy,
    ValidationError,
    FormatNotAvailableError,
)
from mediamanager.core.validation import (
    validate_input_path,
    validate_output_path,
    validate_format,
    validate_dimensions,
    validate_quality,
    validate_percentage,
    validate_rename_pattern,
    validate_exif_fields,
)


class TestValidateInputPath:
    def test_valid_file(self, tmp_images):
        result = validate_input_path(tmp_images["jpeg"])
        assert result.exists()

    def test_nonexistent_file(self):
        with pytest.raises(ValidationError, match="File not found"):
            validate_input_path("/nonexistent/file.jpg")

    def test_directory(self, tmp_path):
        with pytest.raises(ValidationError, match="Not a file"):
            validate_input_path(tmp_path)

    def test_zero_byte(self, zero_byte_file):
        with pytest.raises(ValidationError, match="empty"):
            validate_input_path(zero_byte_file)


class TestValidateOutputPath:
    def test_new_file(self, tmp_path):
        out = tmp_path / "output.jpg"
        result = validate_output_path(out, OverwritePolicy.RENAME)
        assert result == out

    def test_existing_skip(self, tmp_images):
        result = validate_output_path(tmp_images["jpeg"], OverwritePolicy.SKIP)
        assert result is None

    def test_existing_rename(self, tmp_images):
        result = validate_output_path(tmp_images["jpeg"], OverwritePolicy.RENAME)
        assert result != tmp_images["jpeg"]
        assert "_1" in result.name

    def test_existing_overwrite(self, tmp_images):
        result = validate_output_path(tmp_images["jpeg"], OverwritePolicy.OVERWRITE)
        assert result == tmp_images["jpeg"]

    def test_existing_ask(self, tmp_images):
        with pytest.raises(ValidationError, match="already exists"):
            validate_output_path(tmp_images["jpeg"], OverwritePolicy.ASK)

    def test_auto_create_dir(self, tmp_path):
        out = tmp_path / "new_dir" / "output.jpg"
        result = validate_output_path(out, OverwritePolicy.RENAME)
        assert result.parent.exists()


class TestValidateFormat:
    def test_jpg(self):
        assert validate_format("jpg") == "JPEG"

    def test_jpeg(self):
        assert validate_format("jpeg") == "JPEG"

    def test_png(self):
        assert validate_format("png") == "PNG"

    def test_webp(self):
        assert validate_format("webp") == "WEBP"

    def test_case_insensitive(self):
        assert validate_format("PNG") == "PNG"
        assert validate_format("Jpg") == "JPEG"

    def test_unsupported(self):
        with pytest.raises(ValidationError, match="Unsupported format"):
            validate_format("bmp")


class TestValidateDimensions:
    def test_valid(self):
        assert validate_dimensions(800, 600) == (800, 600)

    def test_none_allowed(self):
        assert validate_dimensions(800, None, allow_none=True) == (800, None)

    def test_none_not_allowed(self):
        with pytest.raises(ValidationError, match="required"):
            validate_dimensions(800, None, allow_none=False)

    def test_zero(self):
        with pytest.raises(ValidationError, match=">="):
            validate_dimensions(0, 600)

    def test_negative(self):
        with pytest.raises(ValidationError, match=">="):
            validate_dimensions(-1, 600)

    def test_too_large(self):
        with pytest.raises(ValidationError, match="<="):
            validate_dimensions(100000, 600)


class TestValidateQuality:
    def test_valid_jpeg(self):
        assert validate_quality(85, ImageFormat.JPEG) == 85

    def test_clamp_low(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = validate_quality(0, ImageFormat.JPEG)
            assert result == 1
            assert len(w) == 1

    def test_clamp_high(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = validate_quality(100, ImageFormat.JPEG)
            assert result == 95
            assert len(w) == 1

    def test_ico_passthrough(self):
        assert validate_quality(50, ImageFormat.ICO) == 50


class TestValidatePercentage:
    def test_valid(self):
        assert validate_percentage(50.0) == 50.0

    def test_zero(self):
        with pytest.raises(ValidationError, match="> 0"):
            validate_percentage(0)

    def test_negative(self):
        with pytest.raises(ValidationError, match="> 0"):
            validate_percentage(-10)

    def test_too_large(self):
        with pytest.raises(ValidationError, match="<= 10000"):
            validate_percentage(20000)

    def test_warn_large(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_percentage(500)
            assert len(w) == 1


class TestValidateRenamePattern:
    def test_basic(self):
        result = validate_rename_pattern(
            "img_{n:03d}.{ext}",
            ["a.jpg", "b.jpg", "c.jpg"],
        )
        assert result == ["img_001.jpg", "img_002.jpg", "img_003.jpg"]

    def test_name_token(self):
        result = validate_rename_pattern("{name}_copy.{ext}", ["photo.jpg"])
        assert result == ["photo_copy.jpg"]

    def test_collision(self):
        with pytest.raises(ValidationError, match="collision"):
            validate_rename_pattern("same.{ext}", ["a.jpg", "b.jpg"])

    def test_empty_pattern(self):
        with pytest.raises(ValidationError, match="empty"):
            validate_rename_pattern("", ["a.jpg"])


class TestValidateExifFields:
    def test_valid(self):
        result = validate_exif_fields({"artist": "Test", "copyright": "2024"})
        assert result == {"artist": "Test", "copyright": "2024"}

    def test_unknown(self):
        with pytest.raises(ValidationError, match="Unknown EXIF"):
            validate_exif_fields({"unknown_field": "value"})
