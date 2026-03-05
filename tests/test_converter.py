"""Tests for core/converter.py."""

from pathlib import Path

import pytest
from PIL import Image

from image_optimizer.core.converter import convert_image
from image_optimizer.core.types import OverwritePolicy, ValidationError


class TestConvertImage:
    def test_jpeg_to_png(self, tmp_images, tmp_path):
        out = tmp_path / "output.png"
        result = convert_image(tmp_images["jpeg"], out, "png")
        assert result.success
        assert result.output_path.suffix == ".png"
        img = Image.open(result.output_path)
        assert img.format == "PNG"
        img.close()

    def test_png_to_jpeg(self, tmp_images, tmp_path):
        out = tmp_path / "output.jpg"
        result = convert_image(tmp_images["png_rgb"], out, "jpg")
        assert result.success
        img = Image.open(result.output_path)
        assert img.format == "JPEG"
        img.close()

    def test_rgba_png_to_jpeg(self, tmp_images, tmp_path):
        out = tmp_path / "output.jpg"
        result = convert_image(tmp_images["png_rgba"], out, "jpeg")
        assert result.success
        # Should warn about transparency
        assert any("transparency" in w.lower() or "composite" in w.lower() for w in result.warnings)

    def test_jpeg_to_webp(self, tmp_images, tmp_path):
        out = tmp_path / "output.webp"
        result = convert_image(tmp_images["jpeg"], out, "webp", quality=80)
        assert result.success

    def test_wrong_output_extension_corrected(self, tmp_images, tmp_path):
        out = tmp_path / "output.xyz"
        result = convert_image(tmp_images["jpeg"], out, "png")
        assert result.success
        assert result.output_path.suffix == ".png"

    def test_palette_to_jpeg(self, tmp_images, tmp_path):
        out = tmp_path / "output.jpg"
        result = convert_image(tmp_images["palette"], out, "jpeg")
        assert result.success

    def test_metadata_in_result(self, tmp_images, tmp_path):
        out = tmp_path / "output.png"
        result = convert_image(tmp_images["jpeg"], out, "png")
        assert "source_format" in result.metadata
        assert "target_format" in result.metadata
        assert result.metadata["target_format"] == "PNG"
