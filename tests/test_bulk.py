"""Tests for core/bulk.py."""

from pathlib import Path

import pytest
from PIL import Image

from image_optimizer.core.bulk import bulk_convert, bulk_rename
from image_optimizer.core.types import BulkOperationError, OverwritePolicy, ValidationError


class TestBulkConvert:
    def test_convert_directory(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_convert(image_dir, out_dir, "png")
        assert result.total == 3  # 3 JPEGs in root (non-recursive)
        assert result.succeeded == 3
        assert result.failed == 0

    def test_convert_recursive(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_convert(image_dir, out_dir, "png", recursive=True)
        assert result.total == 4  # 3 JPEGs + 1 nested PNG
        assert result.succeeded == 4

    def test_convert_to_webp(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_convert(image_dir, out_dir, "webp")
        assert result.succeeded > 0
        # Check output files are WebP
        for r in result.results:
            if r.success and r.output_path:
                assert r.output_path.suffix == ".webp"

    def test_empty_directory(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        out = tmp_path / "out"
        result = bulk_convert(empty, out, "png")
        assert result.total == 0

    def test_not_a_directory(self, tmp_images, tmp_path):
        with pytest.raises(BulkOperationError, match="Not a directory"):
            bulk_convert(tmp_images["jpeg"], tmp_path / "out", "png")

    def test_progress_callback(self, image_dir, tmp_path):
        calls = []
        def cb(current, total, name):
            calls.append((current, total, name))

        out_dir = tmp_path / "output"
        bulk_convert(image_dir, out_dir, "png", progress_callback=cb)
        assert len(calls) == 3


class TestBulkRename:
    def test_basic_rename(self, image_dir):
        result = bulk_rename(image_dir, "photo_{n:03d}.{ext}", dry_run=True)
        assert result.total == 3
        assert result.succeeded == 3
        for r in result.results:
            assert r.metadata.get("dry_run") is True

    def test_actual_rename(self, image_dir):
        result = bulk_rename(image_dir, "renamed_{n}.{ext}")
        assert result.succeeded == 3
        # Verify files were actually renamed
        for r in result.results:
            assert r.output_path.exists()
            assert "renamed_" in r.output_path.name

    def test_collision_detection(self, image_dir):
        with pytest.raises(ValidationError, match="collision"):
            bulk_rename(image_dir, "same.{ext}")

    def test_custom_start_number(self, image_dir):
        result = bulk_rename(image_dir, "img_{n:03d}.{ext}", dry_run=True, start_number=10)
        names = [r.output_path.name for r in result.results]
        assert "img_010.jpg" in names
