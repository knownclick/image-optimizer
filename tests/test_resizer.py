"""Tests for core/resizer.py."""

from pathlib import Path

import pytest
from PIL import Image

from mediamanager.core.resizer import calculate_dimensions, resize_image
from mediamanager.core.types import ResizeMode, ValidationError


class TestCalculateDimensions:
    def test_exact(self):
        assert calculate_dimensions(1000, 800, 500, 400, ResizeMode.EXACT) == (500, 400)

    def test_percentage(self):
        assert calculate_dimensions(1000, 800, None, None, ResizeMode.PERCENTAGE, 50) == (500, 400)

    def test_percentage_small(self):
        # Should clamp to at least 1x1
        w, h = calculate_dimensions(2, 2, None, None, ResizeMode.PERCENTAGE, 1)
        assert w >= 1 and h >= 1

    def test_fit_width_constrained(self):
        w, h = calculate_dimensions(1000, 500, 200, 200, ResizeMode.FIT)
        assert w == 200
        assert h == 100

    def test_fit_height_constrained(self):
        w, h = calculate_dimensions(500, 1000, 200, 200, ResizeMode.FIT)
        assert w == 100
        assert h == 200

    def test_fit_width_only(self):
        w, h = calculate_dimensions(1000, 500, 200, None, ResizeMode.FIT)
        assert w == 200
        assert h == 100

    def test_fill(self):
        w, h = calculate_dimensions(1000, 500, 200, 200, ResizeMode.FILL)
        # Should scale so that both dimensions are >= target
        assert w >= 200
        assert h >= 200

    def test_percentage_missing(self):
        with pytest.raises(ValidationError):
            calculate_dimensions(100, 100, None, None, ResizeMode.PERCENTAGE)


class TestResizeImage:
    def test_resize_fit(self, tmp_images, tmp_path):
        out = tmp_path / "resized.jpg"
        result = resize_image(
            tmp_images["jpeg"], out,
            width=50, height=50, mode=ResizeMode.FIT,
        )
        assert result.success
        img = Image.open(result.output_path)
        assert img.width <= 50
        assert img.height <= 50
        img.close()

    def test_resize_exact(self, tmp_images, tmp_path):
        out = tmp_path / "resized.jpg"
        result = resize_image(
            tmp_images["jpeg"], out,
            width=50, height=30, mode=ResizeMode.EXACT,
        )
        assert result.success
        img = Image.open(result.output_path)
        assert img.width == 50
        assert img.height == 30
        img.close()

    def test_resize_percentage(self, tmp_images, tmp_path):
        out = tmp_path / "resized.jpg"
        result = resize_image(
            tmp_images["jpeg"], out,
            percentage=50, mode=ResizeMode.PERCENTAGE,
        )
        assert result.success
        img = Image.open(result.output_path)
        assert img.width == 50  # 100 * 0.5
        assert img.height == 40  # 80 * 0.5
        img.close()

    def test_resize_fill(self, tmp_images, tmp_path):
        out = tmp_path / "resized.jpg"
        result = resize_image(
            tmp_images["jpeg"], out,
            width=50, height=50, mode=ResizeMode.FILL,
        )
        assert result.success
        img = Image.open(result.output_path)
        assert img.width == 50
        assert img.height == 50
        img.close()

    def test_resize_with_format(self, tmp_images, tmp_path):
        out = tmp_path / "resized.png"
        result = resize_image(
            tmp_images["jpeg"], out,
            width=50, mode=ResizeMode.FIT, fmt="png",
        )
        assert result.success
        assert result.output_path.suffix == ".png"

    def test_aspect_ratio_warning(self, tmp_images, tmp_path):
        out = tmp_path / "resized.jpg"
        result = resize_image(
            tmp_images["jpeg"], out,
            width=50, height=50, mode=ResizeMode.EXACT,
        )
        # 100x80 → 50x50 changes aspect ratio
        assert any("aspect" in w.lower() for w in result.warnings)
