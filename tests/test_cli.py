"""Tests for CLI commands using Click's test runner."""

from pathlib import Path

import pytest
from click.testing import CliRunner
from PIL import Image

from image_optimizer.cli.app import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_jpeg(tmp_path):
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    p = tmp_path / "test.jpg"
    img.save(str(p), "JPEG")
    return p


class TestConvertCommand:
    def test_convert_to_png(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "out.png"
        result = runner.invoke(main, ["convert", str(sample_jpeg), str(out), "-f", "png"])
        assert result.exit_code == 0
        assert out.exists()

    def test_convert_missing_format(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "out.png"
        result = runner.invoke(main, ["convert", str(sample_jpeg), str(out)])
        assert result.exit_code != 0  # Missing required -f


class TestResizeCommand:
    def test_resize_fit(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "resized.jpg"
        result = runner.invoke(main, [
            "resize", str(sample_jpeg), str(out),
            "-W", "50", "-H", "50", "--mode", "fit",
        ])
        assert result.exit_code == 0

    def test_resize_percentage(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "resized.jpg"
        result = runner.invoke(main, [
            "resize", str(sample_jpeg), str(out),
            "-p", "50", "--mode", "percentage",
        ])
        assert result.exit_code == 0


class TestCompressCommand:
    def test_compress(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "compressed.jpg"
        result = runner.invoke(main, [
            "compress", str(sample_jpeg), str(out), "-q", "50",
        ])
        assert result.exit_code == 0


class TestThumbnailCommand:
    def test_thumbnail_preset(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "thumb.jpg"
        result = runner.invoke(main, [
            "thumbnail", str(sample_jpeg), str(out), "-s", "small",
        ])
        assert result.exit_code == 0

    def test_thumbnail_custom(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "thumb.jpg"
        result = runner.invoke(main, [
            "thumbnail", str(sample_jpeg), str(out), "-s", "48",
        ])
        assert result.exit_code == 0


class TestMetadataCommands:
    def test_read(self, runner, sample_jpeg):
        result = runner.invoke(main, ["metadata", "read", str(sample_jpeg)])
        assert result.exit_code == 0
        assert "JPEG" in result.output

    def test_read_json(self, runner, sample_jpeg):
        result = runner.invoke(main, ["metadata", "read", str(sample_jpeg), "--json"])
        assert result.exit_code == 0
        assert "{" in result.output

    def test_strip(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "stripped.jpg"
        result = runner.invoke(main, ["metadata", "strip", str(sample_jpeg), str(out)])
        assert result.exit_code == 0

    def test_write(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "meta.jpg"
        result = runner.invoke(main, [
            "metadata", "write", str(sample_jpeg), str(out),
            "--artist", "Test",
        ])
        assert result.exit_code == 0


class TestFaviconCommand:
    def test_favicon(self, runner, sample_jpeg, tmp_path):
        out = tmp_path / "favicon.ico"
        result = runner.invoke(main, [
            "favicon", str(sample_jpeg), str(out), "--sizes", "16,32",
        ])
        assert result.exit_code == 0
        assert out.exists()


class TestBulkCommands:
    def test_bulk_convert(self, runner, tmp_path):
        # Create source images
        src = tmp_path / "src"
        src.mkdir()
        for i in range(3):
            img = Image.new("RGB", (50, 50), color=(i * 80, 0, 0))
            img.save(str(src / f"img_{i}.jpg"), "JPEG")

        out = tmp_path / "out"
        result = runner.invoke(main, [
            "bulk", "convert", str(src), str(out), "-f", "png",
        ])
        assert result.exit_code == 0
        assert "3" in result.output  # Total count

    def test_bulk_rename_dry_run(self, runner, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        for i in range(3):
            img = Image.new("RGB", (50, 50))
            img.save(str(src / f"img_{i}.jpg"), "JPEG")

        result = runner.invoke(main, [
            "bulk", "rename", str(src),
            "--pattern", "photo_{n:03d}.{ext}",
            "--dry-run",
        ])
        assert result.exit_code == 0
        assert "photo_001.jpg" in result.output


class TestMainGroup:
    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Image Optimizer" in result.output
        assert "Hency Prajapati" in result.output
        assert "Known Click Technologies" in result.output

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_no_args_shows_help(self, runner):
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert "Image Optimizer" in result.output
