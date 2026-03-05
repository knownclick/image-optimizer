"""Tests for bulk_process() and bulk_thumbnails() in core/bulk.py."""

from pathlib import Path

import pytest
from PIL import Image

from image_optimizer.core.bulk import bulk_process, bulk_thumbnails
from image_optimizer.core.thumbnail import generate_thumbnails
from image_optimizer.core.types import BulkOperationError, ResizeMode


class TestBulkProcess:
    def test_format_conversion_only(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_process(image_dir, out_dir, target_format="png")
        assert result.total == 3  # 3 JPEGs in root (non-recursive)
        assert result.succeeded == 3
        assert result.failed == 0
        for r in result.results:
            if r.success and r.output_path:
                assert r.output_path.suffix == ".png"

    def test_resize_only_width(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_process(
            image_dir, out_dir,
            resize_width=50,
            resize_mode=ResizeMode.FIT,
        )
        assert result.succeeded == 3
        for r in result.results:
            if r.success and r.output_path:
                img = Image.open(r.output_path)
                assert img.width == 50
                assert img.height == 50
                img.close()

    def test_resize_and_convert_combined(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_process(
            image_dir, out_dir,
            target_format="webp",
            resize_width=60,
            resize_mode=ResizeMode.FIT,
        )
        assert result.succeeded == 3
        for r in result.results:
            if r.success and r.output_path:
                assert r.output_path.suffix == ".webp"
                img = Image.open(r.output_path)
                assert img.width == 60
                img.close()

    def test_auto_format_preserves_original(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_process(
            image_dir, out_dir,
            target_format=None,
            resize_width=50,
        )
        assert result.succeeded == 3
        for r in result.results:
            if r.success and r.output_path:
                assert r.output_path.suffix == ".jpg"

    def test_recursive_mirrors_subdirectories(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_process(
            image_dir, out_dir,
            target_format="png",
            recursive=True,
        )
        assert result.total == 4
        assert result.succeeded == 4
        assert (out_dir / "sub" / "nested.png").exists()

    def test_empty_directory(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        out = tmp_path / "out"
        result = bulk_process(empty, out, target_format="png")
        assert result.total == 0
        assert result.succeeded == 0
        assert result.failed == 0

    def test_not_a_directory(self, tmp_images, tmp_path):
        with pytest.raises(BulkOperationError, match="Not a directory"):
            bulk_process(tmp_images["jpeg"], tmp_path / "out", target_format="png")

    def test_progress_callback(self, image_dir, tmp_path):
        calls = []
        def cb(current, total, name):
            calls.append((current, total, name))

        out_dir = tmp_path / "output"
        bulk_process(image_dir, out_dir, target_format="png", progress_callback=cb)
        assert len(calls) == 3

    def test_resize_height_only(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_process(
            image_dir, out_dir,
            resize_height=40,
            resize_mode=ResizeMode.FIT,
        )
        assert result.succeeded == 3
        for r in result.results:
            if r.success and r.output_path:
                img = Image.open(r.output_path)
                assert img.height == 40
                img.close()

    def test_strip_metadata(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_process(
            image_dir, out_dir,
            target_format="png",
            strip_metadata=True,
        )
        assert result.succeeded == 3

    def test_quality_setting(self, image_dir, tmp_path):
        out_dir = tmp_path / "output"
        result = bulk_process(
            image_dir, out_dir,
            target_format="jpeg",
            quality=50,
        )
        assert result.succeeded == 3

    def test_metadata_fields(self, image_dir, tmp_path):
        """bulk_process with metadata_fields writes EXIF to JPEG files."""
        out_dir = tmp_path / "output"
        result = bulk_process(
            image_dir, out_dir,
            target_format="jpeg",
            metadata_fields={"artist": "Test Author", "copyright": "2026"},
        )
        assert result.succeeded == 3


class TestBulkThumbnails:
    def test_single_size(self, image_dir, tmp_path):
        out_dir = tmp_path / "thumbs"
        result = bulk_thumbnails(image_dir, out_dir, sizes=[64])
        assert result.total == 3  # 3 images * 1 size
        assert result.succeeded == 3

    def test_multiple_sizes(self, image_dir, tmp_path):
        out_dir = tmp_path / "thumbs"
        result = bulk_thumbnails(image_dir, out_dir, sizes=[64, 150])
        assert result.total == 6  # 3 images * 2 sizes
        assert result.succeeded == 6

    def test_custom_prefix(self, image_dir, tmp_path):
        out_dir = tmp_path / "thumbs"
        result = bulk_thumbnails(image_dir, out_dir, sizes=[64], prefix="myprefix")
        assert result.succeeded == 3
        for r in result.results:
            if r.success and r.output_path:
                assert r.output_path.name.startswith("myprefix_")

    def test_recursive(self, image_dir, tmp_path):
        out_dir = tmp_path / "thumbs"
        result = bulk_thumbnails(image_dir, out_dir, sizes=[64], recursive=True)
        assert result.total == 4  # 3 root + 1 nested
        assert result.succeeded == 4
        # Subdirectory mirrored
        assert (out_dir / "sub").is_dir()

    def test_empty_dir(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        out = tmp_path / "thumbs"
        result = bulk_thumbnails(empty, out, sizes=[64])
        assert result.total == 0

    def test_no_sizes_error(self, image_dir, tmp_path):
        with pytest.raises(BulkOperationError, match="No sizes"):
            bulk_thumbnails(image_dir, tmp_path / "out", sizes=[])

    def test_progress_callback(self, image_dir, tmp_path):
        calls = []
        def cb(current, total, name):
            calls.append((current, total, name))

        out_dir = tmp_path / "thumbs"
        bulk_thumbnails(image_dir, out_dir, sizes=[64, 150], progress_callback=cb)
        assert len(calls) == 6  # 3 images * 2 sizes

    def test_crop_to_square(self, image_dir, tmp_path):
        out_dir = tmp_path / "thumbs"
        result = bulk_thumbnails(image_dir, out_dir, sizes=[64], crop_to_square=True)
        assert result.succeeded == 3


class TestGenerateThumbnails:
    def test_multi_size_single_image(self, tmp_images, tmp_path):
        out_dir = tmp_path / "thumbs"
        results = generate_thumbnails(
            tmp_images["jpeg"], out_dir,
            sizes=[64, 150, 300],
        )
        assert len(results) == 3
        for r in results:
            assert r.success
            assert r.output_path.exists()

    def test_custom_prefix(self, tmp_images, tmp_path):
        out_dir = tmp_path / "thumbs"
        results = generate_thumbnails(
            tmp_images["jpeg"], out_dir,
            sizes=[64],
            prefix="preview",
        )
        assert len(results) == 1
        assert results[0].output_path.name.startswith("preview_")

    def test_output_naming(self, tmp_images, tmp_path):
        out_dir = tmp_path / "thumbs"
        results = generate_thumbnails(
            tmp_images["jpeg"], out_dir,
            sizes=[150],
            prefix="thumb",
        )
        assert "thumb_red_150x150" in results[0].output_path.stem

    def test_suffix(self, tmp_images, tmp_path):
        out_dir = tmp_path / "thumbs"
        results = generate_thumbnails(
            tmp_images["jpeg"], out_dir,
            sizes=[64],
            prefix="thumb",
            suffix="web",
        )
        assert len(results) == 1
        assert "thumb_red_64x64_web" in results[0].output_path.stem

    def test_suffix_empty(self, tmp_images, tmp_path):
        out_dir = tmp_path / "thumbs"
        results = generate_thumbnails(
            tmp_images["jpeg"], out_dir,
            sizes=[64],
            prefix="thumb",
            suffix="",
        )
        assert "thumb_red_64x64" in results[0].output_path.stem
        assert results[0].output_path.stem.count("_") == 2  # no trailing _

    def test_tuple_size(self, tmp_images, tmp_path):
        out_dir = tmp_path / "thumbs"
        results = generate_thumbnails(
            tmp_images["jpeg"], out_dir,
            sizes=[(120, 80)],
            prefix="thumb",
        )
        assert len(results) == 1
        assert "120x80" in results[0].output_path.stem


class TestBulkThumbnailsSuffix:
    def test_suffix(self, image_dir, tmp_path):
        out_dir = tmp_path / "thumbs"
        result = bulk_thumbnails(image_dir, out_dir, sizes=[64], suffix="web")
        assert result.succeeded == 3
        for r in result.results:
            if r.success and r.output_path:
                assert "web" in r.output_path.stem

    def test_tuple_size(self, image_dir, tmp_path):
        out_dir = tmp_path / "thumbs"
        result = bulk_thumbnails(image_dir, out_dir, sizes=[(100, 75)])
        assert result.succeeded == 3
        for r in result.results:
            if r.success and r.output_path:
                assert "100x75" in r.output_path.stem
