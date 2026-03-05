"""Interactive crop canvas — displays an image with a draggable crop overlay."""

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk


# Handle size in canvas pixels
_HANDLE_SIZE = 8
_HANDLE_HALF = _HANDLE_SIZE // 2

# Minimum crop region in canvas pixels
_MIN_CROP = 10


class CropCanvas(ctk.CTkFrame):
    """Canvas widget that shows an image with a draggable crop rectangle.

    The crop box is maintained in *canvas* coordinates.  Use
    ``get_crop_box_image_coords()`` / ``set_crop_box_image_coords()`` to
    convert to/from original-image pixel coordinates.
    """

    def __init__(self, master, max_w: int = 600, max_h: int = 500,
                 on_change=None, **kwargs):
        super().__init__(master, **kwargs)

        self._max_w = max_w
        self._max_h = max_h
        self._on_change = on_change  # callback(x, y, w, h) in image coords

        self._canvas = tk.Canvas(
            self, width=max_w, height=max_h,
            bg="#2B2B2B", highlightthickness=0,
        )
        self._canvas.pack(fill="both", expand=True)

        # State
        self._pil_image: Image.Image | None = None
        self._tk_image: ImageTk.PhotoImage | None = None
        self._scale: float = 1.0
        self._img_offset_x: int = 0  # canvas offset if image is smaller
        self._img_offset_y: int = 0
        self._img_display_w: int = 0
        self._img_display_h: int = 0

        # Crop rectangle in canvas coords (relative to image origin on canvas)
        self._crop_x: float = 0
        self._crop_y: float = 0
        self._crop_w: float = 0
        self._crop_h: float = 0

        # Aspect ratio constraint: (w_ratio, h_ratio) or None
        self._aspect: tuple[int, int] | None = None

        # Drag state
        self._drag_mode: str | None = None  # 'move', 'new', or handle name
        self._drag_start_x: int = 0
        self._drag_start_y: int = 0
        self._drag_orig_crop: tuple[float, float, float, float] = (0, 0, 0, 0)

        # Bind mouse
        self._canvas.bind("<ButtonPress-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._canvas.bind("<Motion>", self._on_hover)

    # ── Public API ────────────────────────────────────────────

    def load_image(self, path: str) -> None:
        """Load and display an image, fitting it within max dimensions."""
        self._pil_image = Image.open(path)
        img_w, img_h = self._pil_image.size

        # Scale to fit canvas
        scale_x = self._max_w / img_w
        scale_y = self._max_h / img_h
        self._scale = min(scale_x, scale_y, 1.0)  # don't upscale

        self._img_display_w = int(img_w * self._scale)
        self._img_display_h = int(img_h * self._scale)

        # Center image on canvas
        self._img_offset_x = (self._max_w - self._img_display_w) // 2
        self._img_offset_y = (self._max_h - self._img_display_h) // 2

        # Create display image
        display = self._pil_image.resize(
            (self._img_display_w, self._img_display_h), Image.LANCZOS,
        )
        self._tk_image = ImageTk.PhotoImage(display)

        # Default crop = full image
        self.reset_to_full_image()

    def reset_to_full_image(self) -> None:
        """Reset crop box to the full image."""
        self._crop_x = 0
        self._crop_y = 0
        self._crop_w = float(self._img_display_w)
        self._crop_h = float(self._img_display_h)
        self._redraw()
        self._notify_change()

    def set_aspect_ratio(self, ratio: tuple[int, int] | None) -> None:
        """Lock crop to aspect ratio (w, h) or None for free."""
        self._aspect = ratio
        if ratio and self._pil_image:
            self._constrain_aspect()
            self._redraw()
            self._notify_change()

    def get_crop_box_image_coords(self) -> tuple[int, int, int, int]:
        """Return (x, y, w, h) in original image pixel coordinates."""
        if not self._pil_image:
            return (0, 0, 0, 0)
        x = int(round(self._crop_x / self._scale))
        y = int(round(self._crop_y / self._scale))
        w = int(round(self._crop_w / self._scale))
        h = int(round(self._crop_h / self._scale))
        # Clamp to image bounds
        img_w, img_h = self._pil_image.size
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = max(1, min(w, img_w - x))
        h = max(1, min(h, img_h - y))
        return (x, y, w, h)

    def set_crop_box_image_coords(self, x: int, y: int, w: int, h: int) -> None:
        """Set crop from original image coordinates."""
        if not self._pil_image:
            return
        self._crop_x = x * self._scale
        self._crop_y = y * self._scale
        self._crop_w = w * self._scale
        self._crop_h = h * self._scale
        self._clamp_crop()
        self._redraw()
        self._notify_change()

    # ── Drawing ───────────────────────────────────────────────

    def _redraw(self) -> None:
        """Redraw image, overlay, and handles."""
        c = self._canvas
        c.delete("all")

        if not self._tk_image:
            return

        # Draw image
        c.create_image(
            self._img_offset_x, self._img_offset_y,
            anchor="nw", image=self._tk_image,
        )

        ox = self._img_offset_x
        oy = self._img_offset_y

        # Dim regions outside crop (4 rectangles)
        cx, cy = self._crop_x + ox, self._crop_y + oy
        cw, ch = self._crop_w, self._crop_h
        iw, ih = self._img_display_w, self._img_display_h

        dim_color = "#000000"
        # Top strip
        if cy > oy:
            c.create_rectangle(ox, oy, ox + iw, cy,
                               fill=dim_color, stipple="gray50", outline="")
        # Bottom strip
        if cy + ch < oy + ih:
            c.create_rectangle(ox, cy + ch, ox + iw, oy + ih,
                               fill=dim_color, stipple="gray50", outline="")
        # Left strip (between top/bottom)
        if cx > ox:
            c.create_rectangle(ox, cy, cx, cy + ch,
                               fill=dim_color, stipple="gray50", outline="")
        # Right strip (between top/bottom)
        if cx + cw < ox + iw:
            c.create_rectangle(cx + cw, cy, ox + iw, cy + ch,
                               fill=dim_color, stipple="gray50", outline="")

        # Crop rectangle outline
        c.create_rectangle(cx, cy, cx + cw, cy + ch,
                           outline="white", width=2)

        # Rule-of-thirds lines
        for i in (1, 2):
            third_x = cx + cw * i / 3
            third_y = cy + ch * i / 3
            c.create_line(third_x, cy, third_x, cy + ch,
                          fill="white", dash=(4, 4), width=1)
            c.create_line(cx, third_y, cx + cw, third_y,
                          fill="white", dash=(4, 4), width=1)

        # Handles
        handle_color = "#3B82F6"
        for hx, hy in self._handle_positions():
            c.create_rectangle(
                hx - _HANDLE_HALF, hy - _HANDLE_HALF,
                hx + _HANDLE_HALF, hy + _HANDLE_HALF,
                fill=handle_color, outline="white", width=1,
            )

    def _handle_positions(self) -> list[tuple[float, float]]:
        """Return canvas-absolute positions of the 8 handles."""
        ox = self._img_offset_x
        oy = self._img_offset_y
        cx, cy = self._crop_x + ox, self._crop_y + oy
        cw, ch = self._crop_w, self._crop_h
        mx, my = cx + cw / 2, cy + ch / 2
        return [
            (cx, cy), (mx, cy), (cx + cw, cy),           # top-left, top-mid, top-right
            (cx, my), (cx + cw, my),                      # mid-left, mid-right
            (cx, cy + ch), (mx, cy + ch), (cx + cw, cy + ch),  # bot-left, bot-mid, bot-right
        ]

    # ── Handle names for each index ──────────────────────────

    _HANDLE_NAMES = [
        "tl", "tm", "tr",
        "ml", "mr",
        "bl", "bm", "br",
    ]

    _HANDLE_CURSORS = {
        "tl": "top_left_corner", "tr": "top_right_corner",
        "bl": "bottom_left_corner", "br": "bottom_right_corner",
        "tm": "top_side", "bm": "bottom_side",
        "ml": "left_side", "mr": "right_side",
    }

    # ── Mouse handling ────────────────────────────────────────

    def _hit_test(self, mx: int, my: int) -> str | None:
        """Return handle name, 'move', 'new', or None."""
        handles = self._handle_positions()
        for i, (hx, hy) in enumerate(handles):
            if abs(mx - hx) <= _HANDLE_HALF + 2 and abs(my - hy) <= _HANDLE_HALF + 2:
                return self._HANDLE_NAMES[i]

        # Inside crop rect?
        ox, oy = self._img_offset_x, self._img_offset_y
        cx, cy = self._crop_x + ox, self._crop_y + oy
        if cx <= mx <= cx + self._crop_w and cy <= my <= cy + self._crop_h:
            return "move"

        # Inside image but outside crop?
        if (ox <= mx <= ox + self._img_display_w and
                oy <= my <= oy + self._img_display_h):
            return "new"

        return None

    def _on_press(self, event):
        mode = self._hit_test(event.x, event.y)
        if not mode:
            return
        self._drag_mode = mode
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._drag_orig_crop = (self._crop_x, self._crop_y, self._crop_w, self._crop_h)

        if mode == "new":
            # Start a new selection from mouse position
            rel_x = event.x - self._img_offset_x
            rel_y = event.y - self._img_offset_y
            self._crop_x = max(0, min(rel_x, self._img_display_w))
            self._crop_y = max(0, min(rel_y, self._img_display_h))
            self._crop_w = 0
            self._crop_h = 0
            self._drag_mode = "br"  # growing from top-left via bottom-right handle
            self._drag_orig_crop = (self._crop_x, self._crop_y, 0, 0)

    def _on_drag(self, event):
        if not self._drag_mode:
            return

        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        ox, oy, ow, oh = self._drag_orig_crop

        if self._drag_mode == "move":
            self._crop_x = ox + dx
            self._crop_y = oy + dy
            self._crop_w = ow
            self._crop_h = oh
        else:
            # Resize via handle
            self._resize_by_handle(self._drag_mode, ox, oy, ow, oh, dx, dy)

        self._clamp_crop()

        if self._aspect:
            self._constrain_aspect()

        self._redraw()
        self._notify_change()

    def _on_release(self, event):
        if self._drag_mode:
            # Ensure minimum size
            if self._crop_w < _MIN_CROP or self._crop_h < _MIN_CROP:
                self.reset_to_full_image()
            self._drag_mode = None

    def _on_hover(self, event):
        mode = self._hit_test(event.x, event.y)
        if mode is None:
            self._canvas.configure(cursor="")
        elif mode == "move":
            self._canvas.configure(cursor="fleur")
        elif mode == "new":
            self._canvas.configure(cursor="crosshair")
        else:
            cursor = self._HANDLE_CURSORS.get(mode, "crosshair")
            self._canvas.configure(cursor=cursor)

    # ── Resize logic ──────────────────────────────────────────

    def _resize_by_handle(self, handle: str, ox, oy, ow, oh, dx, dy):
        """Update crop rect based on which handle is being dragged."""
        x, y, w, h = ox, oy, ow, oh

        if "l" in handle:
            x = ox + dx
            w = ow - dx
        elif "r" in handle:
            w = ow + dx

        if "t" in handle:
            y = oy + dy
            h = oh - dy
        elif "b" in handle:
            h = oh + dy

        # Handle edge-only drags (tm/bm only change height, ml/mr only width)
        if handle in ("tm", "bm"):
            x, w = ox, ow
        if handle in ("ml", "mr"):
            y, h = oy, oh

        # Prevent negative dimensions by flipping
        if w < 0:
            x = x + w
            w = -w
        if h < 0:
            y = y + h
            h = -h

        self._crop_x = x
        self._crop_y = y
        self._crop_w = max(w, _MIN_CROP)
        self._crop_h = max(h, _MIN_CROP)

    def _constrain_aspect(self) -> None:
        """Adjust crop dimensions to match the locked aspect ratio."""
        if not self._aspect:
            return
        ar_w, ar_h = self._aspect
        target = ar_w / ar_h

        current_w = self._crop_w
        current_h = self._crop_h

        # Fit within current dimensions
        if current_w / max(current_h, 1) > target:
            # Too wide — shrink width
            self._crop_w = current_h * target
        else:
            # Too tall — shrink height
            self._crop_h = current_w / target

        self._clamp_crop()

    def _clamp_crop(self) -> None:
        """Ensure crop box stays within image bounds."""
        iw = float(self._img_display_w)
        ih = float(self._img_display_h)

        self._crop_w = max(_MIN_CROP, min(self._crop_w, iw))
        self._crop_h = max(_MIN_CROP, min(self._crop_h, ih))
        self._crop_x = max(0, min(self._crop_x, iw - self._crop_w))
        self._crop_y = max(0, min(self._crop_y, ih - self._crop_h))

    # ── Notification ──────────────────────────────────────────

    def _notify_change(self) -> None:
        if self._on_change and self._pil_image:
            x, y, w, h = self.get_crop_box_image_coords()
            self._on_change(x, y, w, h)
