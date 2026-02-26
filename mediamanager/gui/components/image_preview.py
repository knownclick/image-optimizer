"""Thumbnail preview with image info display."""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk

from mediamanager.core.utils import format_file_size


class ImagePreview(ctk.CTkFrame):
    """Shows a thumbnail preview and basic image info."""

    PREVIEW_SIZE = (200, 200)

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._photo = None  # prevent GC

        self._canvas = ctk.CTkLabel(self, text="No image loaded", width=200, height=200)
        self._canvas.pack(padx=5, pady=5)

        self._info_label = ctk.CTkLabel(self, text="", justify="left", anchor="w")
        self._info_label.pack(padx=5, pady=(0, 5), fill="x")

    def load(self, path: str | Path) -> None:
        """Load an image and display thumbnail + info."""
        img = None
        thumb = None
        try:
            p = Path(path)
            img = Image.open(p)

            info_text = (
                f"{img.width} x {img.height} | {img.format or '?'} | {img.mode}\n"
                f"{format_file_size(p.stat().st_size)}"
            )

            # Create thumbnail for preview
            thumb = img.copy()
            thumb.thumbnail(self.PREVIEW_SIZE, Image.Resampling.LANCZOS)

            # Convert to RGBA for display
            if thumb.mode not in ("RGB", "RGBA"):
                thumb = thumb.convert("RGBA")

            self._photo = ImageTk.PhotoImage(thumb)
            self._canvas.configure(image=self._photo, text="")
            self._info_label.configure(text=info_text)
        except Exception as e:
            self.clear()
            self._info_label.configure(text=f"Error: {e}")
        finally:
            if img is not None:
                try:
                    img.close()
                except Exception:
                    pass
            if thumb is not None:
                try:
                    thumb.close()
                except Exception:
                    pass

    def clear(self) -> None:
        self._photo = None
        self._canvas.configure(image="", text="No image loaded")
        self._info_label.configure(text="")
