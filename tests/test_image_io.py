"""Tests for core/image_io.py."""

import warnings
from pathlib import Path

import pytest
from PIL import Image

from mediamanager.core.image_io import load_image, save_image, detect_format, image_to_bytes
from mediamanager.core.types import (
    ImageFormat,
    ImageLoadError,
    OverwritePolicy,
)


class TestLoadImage:
    def test_load_jpeg(self, tmp_images):
        img, info = load_image(tmp_images["jpeg"])
        assert info.format == "JPEG"
        assert info.width == 100
        assert info.height == 80
        assert info.mode == "RGB"
        assert not info.has_transparency
        img.close()

    def test_load_png_rgba(self, tmp_images):
        img, info = load_image(tmp_images["png_rgba"])
        assert info.format == "PNG"
        assert info.has_transparency
        img.close()

    def test_load_corrupt(self, corrupt_image):
        with pytest.raises(ImageLoadError):
            load_image(corrupt_image)

    def test_wrong_extension_warns(self, wrong_ext_image):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            img, info = load_image(wrong_ext_image)
            assert any("actually" in str(warning.message).lower() or
                       "suggests" in str(warning.message).lower()
                       for warning in w)
            img.close()


class TestSaveImage:
    def test_save_jpeg(self, tmp_images, tmp_path):
        img, _ = load_image(tmp_images["jpeg"])
        out = tmp_path / "output.jpg"
        result = save_image(img, out, ImageFormat.JPEG)
        assert result.success
        assert out.exists()
        img.close()

    def test_save_png(self, tmp_images, tmp_path):
        img, _ = load_image(tmp_images["png_rgb"])
        out = tmp_path / "output.png"
        result = save_image(img, out, ImageFormat.PNG)
        assert result.success
        img.close()

    def test_rgba_to_jpeg(self, tmp_images, tmp_path):
        img, _ = load_image(tmp_images["png_rgba"])
        out = tmp_path / "output.jpg"
        result = save_image(img, out, ImageFormat.JPEG)
        assert result.success
        assert any("transparency" in w.lower() or "composite" in w.lower() for w in result.warnings)
        img.close()

    def test_skip_existing(self, tmp_images, tmp_path):
        img, _ = load_image(tmp_images["jpeg"])
        # Save first
        out = tmp_path / "out.jpg"
        save_image(img, out, ImageFormat.JPEG)
        # Try again with SKIP
        result = save_image(img, out, ImageFormat.JPEG, policy=OverwritePolicy.SKIP)
        assert result.success
        assert "Skipped" in result.warnings[0]
        img.close()


class TestDetectFormat:
    def test_jpeg(self, tmp_images):
        assert detect_format(tmp_images["jpeg"]) == "JPEG"

    def test_png(self, tmp_images):
        assert detect_format(tmp_images["png_rgb"]) == "PNG"

    def test_wrong_ext(self, wrong_ext_image):
        assert detect_format(wrong_ext_image) == "PNG"


class TestImageToBytes:
    def test_jpeg_bytes(self, tmp_images):
        img, _ = load_image(tmp_images["jpeg"])
        data = image_to_bytes(img, ImageFormat.JPEG, quality=50)
        assert len(data) > 0
        assert data[:2] == b"\xff\xd8"  # JPEG magic
        img.close()

    def test_png_bytes(self, tmp_images):
        img, _ = load_image(tmp_images["png_rgb"])
        data = image_to_bytes(img, ImageFormat.PNG)
        assert len(data) > 0
        assert data[:4] == b"\x89PNG"
        img.close()
