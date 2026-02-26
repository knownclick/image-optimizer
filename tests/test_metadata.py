"""Tests for core/metadata.py."""

from pathlib import Path

import pytest

from mediamanager.core.metadata import read_metadata, strip_metadata, write_metadata
from mediamanager.core.types import MetadataWriteUnsupportedError, OverwritePolicy


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

    def test_write_to_png_fails(self, tmp_images, tmp_path):
        out = tmp_path / "meta.png"
        with pytest.raises(MetadataWriteUnsupportedError):
            write_metadata(
                tmp_images["png_rgb"], out,
                fields={"artist": "Test"},
            )

    def test_write_to_webp(self, tmp_images, tmp_path):
        out = tmp_path / "meta.webp"
        result = write_metadata(
            tmp_images["webp"], out,
            fields={"artist": "WebP Author"},
        )
        assert result.success
