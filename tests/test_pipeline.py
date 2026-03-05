"""Tests for core/pipeline.py."""

from pathlib import Path

import pytest
from PIL import Image

from image_optimizer.core.pipeline import Pipeline
from image_optimizer.core.types import ResizeMode


class TestPipeline:
    def test_resize_and_convert(self, tmp_images, tmp_path):
        out = tmp_path / "pipeline.webp"
        result = (
            Pipeline(tmp_images["jpeg"])
            .resize(width=50, mode=ResizeMode.FIT)
            .convert("webp")
            .execute(out)
        )
        assert result.success
        assert result.metadata.get("pipeline") is True
        img = Image.open(result.output_path)
        assert img.width <= 50
        img.close()

    def test_compress_only(self, tmp_images, tmp_path):
        out = tmp_path / "pipeline.jpg"
        result = (
            Pipeline(tmp_images["jpeg"])
            .compress(quality=50)
            .execute(out)
        )
        assert result.success

    def test_strip_metadata(self, tmp_images, tmp_path):
        out = tmp_path / "pipeline.jpg"
        result = (
            Pipeline(tmp_images["jpeg"])
            .strip_metadata()
            .execute(out)
        )
        assert result.success

    def test_full_pipeline(self, tmp_images, tmp_path):
        out = tmp_path / "pipeline.webp"
        result = (
            Pipeline(tmp_images["jpeg"])
            .resize(width=60, mode=ResizeMode.FIT)
            .convert("webp")
            .compress(quality=70)
            .strip_metadata()
            .execute(out)
        )
        assert result.success
        img = Image.open(result.output_path)
        assert img.format == "WEBP"
        assert img.width <= 60
        img.close()

    def test_resize_percentage(self, tmp_images, tmp_path):
        out = tmp_path / "pipeline.jpg"
        result = (
            Pipeline(tmp_images["jpeg"])
            .resize(percentage=50, mode=ResizeMode.PERCENTAGE)
            .execute(out)
        )
        assert result.success
        img = Image.open(result.output_path)
        assert img.width == 50
        img.close()
