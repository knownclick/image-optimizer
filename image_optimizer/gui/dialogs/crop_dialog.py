"""Modal crop dialog — visual crop with aspect ratio controls and dimension entries."""

from __future__ import annotations

import customtkinter as ctk

from image_optimizer.gui.components.crop_canvas import CropCanvas
from image_optimizer.gui.theme import FONTS, WIDGET_COLORS
from image_optimizer.core.cropper import ASPECT_RATIOS


# Aspect ratio choices shown in dropdown
_AR_CHOICES = ["Free", "1:1", "4:3", "3:2", "16:9", "9:16", "3:4", "2:3", "Custom"]


class CropDialog(ctk.CTkToplevel):
    """Modal dialog for interactive visual cropping.

    Parameters
    ----------
    master : widget
        Parent widget.
    image_path : str
        Path to the image to crop.
    on_apply : callable(x, y, w, h)
        Called with image-pixel coordinates when user clicks Apply.
    initial_crop : tuple(x, y, w, h) | None
        Optional initial crop box in image coordinates.
    initial_aspect_ratio : str | None
        Optional initial aspect ratio (e.g. "16:9").
    """

    def __init__(
        self,
        master,
        image_path: str,
        on_apply,
        initial_crop: tuple[int, int, int, int] | None = None,
        initial_aspect_ratio: str | None = None,
    ):
        super().__init__(master)
        self.title("Visual Crop")
        self.geometry("750x650")
        self.resizable(True, True)
        self.transient(master.winfo_toplevel())
        self.lift()

        self._on_apply = on_apply
        self._updating_entries = False

        # ── Top controls row ──────────────────────────────────
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(top, text="Aspect Ratio:", anchor="w").pack(side="left", padx=(0, 5))
        self._ar_var = ctk.StringVar(value="Free")
        self._ar_menu = ctk.CTkOptionMenu(
            top, values=_AR_CHOICES, variable=self._ar_var,
            command=self._on_ar_change,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            button_color=WIDGET_COLORS["dropdown_fg"],
            button_hover_color=WIDGET_COLORS["dropdown_hover"],
            text_color=WIDGET_COLORS["dropdown_text"],
            width=100,
        )
        self._ar_menu.pack(side="left", padx=(0, 10))

        # Custom ratio entry (hidden by default)
        self._custom_frame = ctk.CTkFrame(top)
        self._custom_w_entry = ctk.CTkEntry(self._custom_frame, width=50, placeholder_text="W")
        self._custom_w_entry.pack(side="left")
        ctk.CTkLabel(self._custom_frame, text=":").pack(side="left", padx=2)
        self._custom_h_entry = ctk.CTkEntry(self._custom_frame, width=50, placeholder_text="H")
        self._custom_h_entry.pack(side="left")
        self._custom_set_btn = ctk.CTkButton(
            self._custom_frame, text="Set", width=40,
            command=self._apply_custom_ratio,
        )
        self._custom_set_btn.pack(side="left", padx=(5, 0))

        # ── Dimension entries row ─────────────────────────────
        dim_row = ctk.CTkFrame(self)
        dim_row.pack(fill="x", padx=10, pady=2)

        for label_text, attr in [("X:", "_entry_x"), ("Y:", "_entry_y"),
                                  ("W:", "_entry_w"), ("H:", "_entry_h")]:
            ctk.CTkLabel(dim_row, text=label_text, width=20).pack(side="left")
            entry = ctk.CTkEntry(dim_row, width=60)
            entry.pack(side="left", padx=(0, 8))
            setattr(self, attr, entry)

        self._dim_set_btn = ctk.CTkButton(
            dim_row, text="Set", width=40, command=self._apply_dim_entries,
        )
        self._dim_set_btn.pack(side="left", padx=(5, 0))

        # ── Canvas ────────────────────────────────────────────
        self._canvas = CropCanvas(self, max_w=600, max_h=450, on_change=self._on_crop_change)
        self._canvas.pack(fill="both", expand=True, padx=10, pady=5)

        # ── Info label ────────────────────────────────────────
        self._info_label = ctk.CTkLabel(
            self, text="", font=FONTS["small"], text_color="gray", anchor="w",
        )
        self._info_label.pack(fill="x", padx=10)

        # ── Bottom buttons ────────────────────────────────────
        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(
            bottom, text="Reset", width=70, command=self._reset,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            hover_color=WIDGET_COLORS["dropdown_hover"],
        ).pack(side="left")

        ctk.CTkButton(
            bottom, text="Apply", width=80, command=self._apply,
            fg_color=WIDGET_COLORS["button_primary"],
            hover_color=WIDGET_COLORS["button_primary_hover"],
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            bottom, text="Cancel", width=80, command=self.destroy,
        ).pack(side="right")

        # ── Load image and set initial state ──────────────────
        self._canvas.load_image(image_path)

        if initial_aspect_ratio and initial_aspect_ratio in ASPECT_RATIOS:
            self._ar_var.set(initial_aspect_ratio)
            ratio = ASPECT_RATIOS[initial_aspect_ratio]
            self._canvas.set_aspect_ratio(ratio)

        if initial_crop:
            x, y, w, h = initial_crop
            if w > 0 and h > 0:
                self._canvas.set_crop_box_image_coords(x, y, w, h)

        def _grab():
            try:
                self.grab_set()
                self.focus_force()
            except Exception:
                pass

        self.after(200, _grab)

    # ── Callbacks ─────────────────────────────────────────────

    def _on_ar_change(self, value: str) -> None:
        if value == "Free":
            self._custom_frame.pack_forget()
            self._canvas.set_aspect_ratio(None)
        elif value == "Custom":
            self._custom_frame.pack(side="left", padx=(5, 0),
                                    in_=self._ar_menu.master)
        else:
            self._custom_frame.pack_forget()
            ratio = ASPECT_RATIOS.get(value)
            self._canvas.set_aspect_ratio(ratio)

    def _apply_custom_ratio(self) -> None:
        try:
            w = int(self._custom_w_entry.get().strip())
            h = int(self._custom_h_entry.get().strip())
            if w > 0 and h > 0:
                self._canvas.set_aspect_ratio((w, h))
        except (ValueError, TypeError):
            pass

    def _on_crop_change(self, x: int, y: int, w: int, h: int) -> None:
        """Called by CropCanvas whenever the crop box changes."""
        self._updating_entries = True
        for entry, val in [(self._entry_x, x), (self._entry_y, y),
                           (self._entry_w, w), (self._entry_h, h)]:
            entry.delete(0, "end")
            entry.insert(0, str(val))
        self._updating_entries = False
        self._info_label.configure(text=f"Crop: {w} x {h} px  (from {x}, {y})")

    def _apply_dim_entries(self) -> None:
        """Read x/y/w/h entries and position the crop box.

        When an aspect ratio is locked, auto-calculate the missing or
        stale dimension: if W was changed, derive H from the ratio
        (and vice-versa).  When both are provided and a ratio is
        locked, W takes precedence.
        """
        try:
            x = int(self._entry_x.get().strip() or 0)
            y = int(self._entry_y.get().strip() or 0)
            w_str = self._entry_w.get().strip()
            h_str = self._entry_h.get().strip()
            w = int(w_str) if w_str else 0
            h = int(h_str) if h_str else 0

            ratio = self._canvas._aspect  # locked (rw, rh) or None
            if ratio:
                rw, rh = ratio
                if w > 0:
                    h = max(1, round(w * rh / rw))
                elif h > 0:
                    w = max(1, round(h * rw / rh))

            if w > 0 and h > 0:
                self._canvas.set_crop_box_image_coords(x, y, w, h)
        except (ValueError, TypeError):
            pass

    def _reset(self) -> None:
        self._ar_var.set("Free")
        self._custom_frame.pack_forget()
        self._canvas.set_aspect_ratio(None)
        self._canvas.reset_to_full_image()

    def _apply(self) -> None:
        x, y, w, h = self._canvas.get_crop_box_image_coords()
        self._on_apply(x, y, w, h)
        self.destroy()
