"""Tests for core/favicon.py."""

import warnings
from pathlib import Path

import pytest
from PIL import Image

from image_optimizer.core.favicon import generate_favicon
from image_optimizer.core.types import OverwritePolicy, ValidationError


class TestGenerateFavicon:
    def test_default_sizes(self, tmp_images, tmp_path):
        out = tmp_path / "favicon.ico"
        result = generate_favicon(tmp_images["jpeg"], out)
        assert result.success
        assert result.output_path.suffix == ".ico"
        assert "sizes" in result.metadata

    def test_custom_sizes(self, tmp_images, tmp_path):
        out = tmp_path / "favicon.ico"
        result = generate_favicon(tmp_images["jpeg"], out, sizes=[16, 32, 64])
        assert result.success
        assert result.metadata["sizes"] == [16, 32, 64]

    def test_non_square_crop(self, tmp_images, tmp_path):
        out = tmp_path / "favicon.ico"
        result = generate_favicon(tmp_images["wide"], out, sizes=[32])
        assert result.success
        assert any("non-square" in w.lower() or "center-crop" in w.lower() for w in result.warnings)

    def test_clamp_large_size(self, tmp_images, tmp_path):
        out = tmp_path / "favicon.ico"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = generate_favicon(tmp_images["jpeg"], out, sizes=[512])
        assert result.success
        # 512 should be clamped to 256
        assert 256 in result.metadata["sizes"]
        assert 512 not in result.metadata["sizes"]

    def test_ensures_ico_extension(self, tmp_images, tmp_path):
        out = tmp_path / "favicon.png"
        result = generate_favicon(tmp_images["jpeg"], out, sizes=[32])
        assert result.success
        assert result.output_path.suffix == ".ico"

    def test_rgba_conversion(self, tmp_images, tmp_path):
        # JPEG source is RGB — should be converted to RGBA for ICO
        out = tmp_path / "favicon.ico"
        result = generate_favicon(tmp_images["jpeg"], out, sizes=[16])
        assert result.success
