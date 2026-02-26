"""Shared fixtures: sample images for testing."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def tmp_images(tmp_path: Path) -> dict[str, Path]:
    """Create sample test images and return paths dict."""
    images = {}

    # RGB JPEG
    img = Image.new("RGB", (100, 80), color=(255, 0, 0))
    p = tmp_path / "red.jpg"
    img.save(str(p), "JPEG")
    images["jpeg"] = p

    # RGBA PNG (with transparency)
    img = Image.new("RGBA", (120, 90), color=(0, 255, 0, 128))
    p = tmp_path / "green.png"
    img.save(str(p), "PNG")
    images["png_rgba"] = p

    # RGB PNG
    img = Image.new("RGB", (200, 150), color=(0, 0, 255))
    p = tmp_path / "blue.png"
    img.save(str(p), "PNG")
    images["png_rgb"] = p

    # WebP
    img = Image.new("RGB", (80, 80), color=(255, 255, 0))
    p = tmp_path / "yellow.webp"
    img.save(str(p), "WEBP")
    images["webp"] = p

    # Small image for thumbnail tests
    img = Image.new("RGB", (30, 20), color=(128, 128, 128))
    p = tmp_path / "tiny.png"
    img.save(str(p), "PNG")
    images["tiny"] = p

    # Non-square image for favicon tests
    img = Image.new("RGB", (200, 100), color=(255, 128, 0))
    p = tmp_path / "wide.png"
    img.save(str(p), "PNG")
    images["wide"] = p

    # Palette mode image
    img = Image.new("P", (50, 50))
    p = tmp_path / "palette.png"
    img.save(str(p), "PNG")
    images["palette"] = p

    return images


@pytest.fixture
def corrupt_image(tmp_path: Path) -> Path:
    """Create a corrupt image file."""
    p = tmp_path / "corrupt.jpg"
    p.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 50)  # JPEG header + garbage
    return p


@pytest.fixture
def zero_byte_file(tmp_path: Path) -> Path:
    """Create a zero-byte file."""
    p = tmp_path / "empty.jpg"
    p.write_bytes(b"")
    return p


@pytest.fixture
def wrong_ext_image(tmp_path: Path) -> Path:
    """Create a PNG file with .jpg extension."""
    img = Image.new("RGB", (50, 50), color=(100, 100, 100))
    p = tmp_path / "actually_png.jpg"
    img.save(str(p), "PNG")  # Save as PNG but with .jpg extension
    return p


@pytest.fixture
def image_dir(tmp_path: Path) -> Path:
    """Create a directory with multiple images for bulk testing."""
    d = tmp_path / "images"
    d.mkdir()
    for i, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
        img = Image.new("RGB", (100, 100), color=color)
        img.save(str(d / f"img_{i}.jpg"), "JPEG")

    sub = d / "sub"
    sub.mkdir()
    img = Image.new("RGB", (50, 50), color=(128, 128, 128))
    img.save(str(sub / "nested.png"), "PNG")

    return d
