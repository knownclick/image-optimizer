"""Tests for core/compressor.py."""

from pathlib import Path

import pytest
from PIL import Image

from image_optimizer.core.compressor import compress_image
from image_optimizer.core.types import OverwritePolicy, ValidationError


class TestCompressImage:
    def test_compress_jpeg(self, tmp_images, tmp_path):
        out = tmp_path / "compressed.jpg"
        result = compress_image(tmp_images["jpeg"], out, quality=50)
        assert result.success
        assert "compression_ratio" in result.metadata

    def test_compress_with_max_size(self, tmp_path):
        # Create a large-ish image
        img = Image.new("RGB", (500, 500), color=(128, 64, 32))
        src = tmp_path / "large.jpg"
        img.save(str(src), "JPEG", quality=95)
        img.close()

        out = tmp_path / "small.jpg"
        result = compress_image(src, out, max_file_size_kb=5)
        assert result.success
        # Check that it tried to hit the target
        assert "quality_used" in result.metadata

    def test_already_under_target(self, tmp_images, tmp_path):
        out = tmp_path / "compressed.jpg"
        result = compress_image(
            tmp_images["jpeg"], out,
            max_file_size_kb=10000,  # Very large target
        )
        assert result.success
        assert any("already under" in w.lower() for w in result.warnings)

    def test_invalid_max_size(self, tmp_images, tmp_path):
        with pytest.raises(ValidationError, match="> 0"):
            compress_image(tmp_images["jpeg"], tmp_path / "out.jpg", max_file_size_kb=0)

    def test_lossless_webp(self, tmp_images, tmp_path):
        out = tmp_path / "lossless.webp"
        result = compress_image(tmp_images["webp"], out, lossless=True)
        assert result.success
