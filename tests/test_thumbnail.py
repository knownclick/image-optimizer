"""Tests for core/thumbnail.py."""

from pathlib import Path

import pytest
from PIL import Image

from image_optimizer.core.thumbnail import generate_thumbnail
from image_optimizer.core.types import ThumbnailPreset


class TestGenerateThumbnail:
    def test_preset_medium(self, tmp_images, tmp_path):
        out = tmp_path / "thumb.jpg"
        result = generate_thumbnail(tmp_images["jpeg"], out, size=ThumbnailPreset.MEDIUM)
        assert result.success
        img = Image.open(result.output_path)
        assert img.width <= 150
        assert img.height <= 150
        img.close()

    def test_preset_small(self, tmp_images, tmp_path):
        out = tmp_path / "thumb.jpg"
        result = generate_thumbnail(tmp_images["jpeg"], out, size=ThumbnailPreset.SMALL)
        assert result.success
        img = Image.open(result.output_path)
        assert img.width <= 64
        assert img.height <= 64
        img.close()

    def test_custom_size_int(self, tmp_images, tmp_path):
        out = tmp_path / "thumb.jpg"
        result = generate_thumbnail(tmp_images["jpeg"], out, size=75)
        assert result.success
        img = Image.open(result.output_path)
        assert img.width <= 75
        assert img.height <= 75
        img.close()

    def test_custom_size_tuple(self, tmp_images, tmp_path):
        out = tmp_path / "thumb.jpg"
        result = generate_thumbnail(tmp_images["jpeg"], out, size=(80, 60))
        assert result.success

    def test_crop_to_square(self, tmp_images, tmp_path):
        out = tmp_path / "thumb.jpg"
        result = generate_thumbnail(
            tmp_images["jpeg"], out,
            size=ThumbnailPreset.MEDIUM,
            crop_to_square=True,
        )
        assert result.success

    def test_no_upscale_warning(self, tmp_images, tmp_path):
        out = tmp_path / "thumb.png"
        result = generate_thumbnail(
            tmp_images["tiny"], out,
            size=ThumbnailPreset.LARGE,  # 300x300 > 30x20
        )
        assert result.success
        assert any("smaller" in w.lower() for w in result.warnings)
        # Should not upscale
        img = Image.open(result.output_path)
        assert img.width <= 30
        assert img.height <= 20
        img.close()
