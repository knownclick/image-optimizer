"""Process tab — unified convert + resize + compress + metadata interface."""

from __future__ import annotations

import customtkinter as ctk

from image_optimizer.gui.components.file_picker import FilePicker
from image_optimizer.gui.components.image_preview import ImagePreview
from image_optimizer.gui.components.profile_selector import ProfileSelector
from image_optimizer.gui.components.settings_panel import (
    DimensionInput,
    FormatSelector,
    MetadataFields,
    QualitySlider,
)
from image_optimizer.gui.components.result_summary import ResultSummary
from image_optimizer.gui.components.error_dialog import show_error
from image_optimizer.gui.workers import WorkerThread
from image_optimizer.gui.scrollable_mixin import ScrollableFixMixin
from image_optimizer.gui.theme import FONTS, WIDGET_COLORS
from image_optimizer.core.types import OverwritePolicy, ResizeMode

# Format name -> file extension
_FORMAT_EXT = {"jpeg": ".jpg", "png": ".png", "webp": ".webp", "avif": ".avif"}

# User-friendly resize mode labels
_RESIZE_MODES = {
    "Fit (keep ratio)": "fit",
    "Exact (stretch)": "exact",
    "Fill (crop)": "fill",
    "Scale by %": "percentage",
}

_DISABLED_FG = "gray50"

# Widgets whose fg stays blue when disabled → grey text on blue = unreadable.
# We swap their colors to a muted palette when disabled and restore on enable.
_BLUE_BG_WIDGETS = (ctk.CTkOptionMenu,)
_DISABLED_BLUE = {"fg_color": "gray30", "button_color": "gray30"}
_ENABLED_BLUE = {
    "fg_color": WIDGET_COLORS["dropdown_fg"],
    "button_color": WIDGET_COLORS["dropdown_fg"],
    "button_hover_color": WIDGET_COLORS["dropdown_hover"],
}

_STATEFUL_WIDGETS = (ctk.CTkEntry, ctk.CTkOptionMenu, ctk.CTkSlider, ctk.CTkCheckBox, ctk.CTkButton)


def _set_children_state(frame, state: str):
    """Recursively enable/disable all input widgets in a frame."""
    for child in frame.winfo_children():
        if isinstance(child, _STATEFUL_WIDGETS):
            try:
                child.configure(state=state)
                if isinstance(child, _BLUE_BG_WIDGETS):
                    child.configure(**(_DISABLED_BLUE if state == "disabled" else _ENABLED_BLUE))
            except Exception:
                pass
        if child.winfo_children():
            _set_children_state(child, state)


class ProcessTab(ScrollableFixMixin, ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._worker = None
        self._auto_output = True

        # ── Input ────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Input", font=FONTS["subheading"]).pack(
            anchor="w", padx=10, pady=(10, 2)
        )
        self._input = FilePicker(self, label="Input:", on_change=self._on_input_change)
        self._input.pack(fill="x", padx=10, pady=2)

        self._preview = ImagePreview(self)
        self._preview.pack(padx=10, pady=5)

        # ── Format section ───────────────────────────────────────
        self._convert_section = ctk.CTkFrame(self)
        self._convert_section.pack(fill="x", padx=10, pady=(10, 0))

        self._convert_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            self._convert_section, text="Convert format", variable=self._convert_var,
            command=self._toggle_convert, font=FONTS["subheading"],
        ).pack(anchor="w", padx=5, pady=4)

        self._convert_frame = ctk.CTkFrame(self._convert_section)
        self._convert_frame.pack(fill="x", padx=10, pady=2)

        self._format = FormatSelector(self._convert_frame, label="Format:",
                                      on_change=self._on_format_change)
        self._format.pack(fill="x", padx=5, pady=2)

        self._lossless_var = ctk.BooleanVar(value=False)
        self._lossless_cb = ctk.CTkCheckBox(
            self._convert_frame, text="Lossless (WebP/AVIF)", variable=self._lossless_var,
            command=self._on_lossless_toggle,
        )
        self._lossless_cb.pack(anchor="w", padx=5, pady=2)

        _set_children_state(self._convert_frame, "disabled")

        # ── Resize section ───────────────────────────────────────
        self._resize_section = ctk.CTkFrame(self)
        self._resize_section.pack(fill="x", padx=10, pady=(5, 0))

        self._resize_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            self._resize_section, text="Resize image", variable=self._resize_var,
            command=self._toggle_resize, font=FONTS["subheading"],
        ).pack(anchor="w", padx=5, pady=4)

        self._resize_frame = ctk.CTkFrame(self._resize_section)
        self._resize_frame.pack(fill="x", padx=10, pady=2)

        self._mode_row = ctk.CTkFrame(self._resize_frame)
        self._mode_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(self._mode_row, text="Mode:", width=80, anchor="w").pack(side="left", padx=(0, 5))
        self._mode_var = ctk.StringVar(value="Fit (keep ratio)")
        self._mode_menu = ctk.CTkOptionMenu(
            self._mode_row, values=list(_RESIZE_MODES.keys()),
            variable=self._mode_var,
            command=self._on_resize_mode_change,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            button_color=WIDGET_COLORS["dropdown_fg"],
            button_hover_color=WIDGET_COLORS["dropdown_hover"],
            text_color=WIDGET_COLORS["dropdown_text"],
        )
        self._mode_menu.pack(side="left")

        # Dimensions (shown for fit/exact/fill)
        self._dims_frame = ctk.CTkFrame(self._resize_frame)
        self._dims_frame.pack(fill="x", padx=5, pady=2)
        self._dims = DimensionInput(self._dims_frame)
        self._dims.pack(fill="x")
        self._dims_hint = ctk.CTkLabel(
            self._dims_frame, text="Leave one blank to auto-scale",
            text_color="gray", font=FONTS["small"],
        )
        self._dims_hint.pack(anchor="w", padx=5)

        # Percentage (shown only for scale by %)
        self._pct_frame = ctk.CTkFrame(self._resize_frame)
        ctk.CTkLabel(self._pct_frame, text="Scale:", width=80, anchor="w").pack(side="left", padx=(0, 5))
        self._pct_entry = ctk.CTkEntry(self._pct_frame, width=80, placeholder_text="e.g. 50")
        self._pct_entry.pack(side="left")
        ctk.CTkLabel(self._pct_frame, text="%", width=20).pack(side="left", padx=5)
        # pct_frame is hidden by default, shown when "Scale by %" selected

        _set_children_state(self._resize_frame, "disabled")

        # ── Crop section ─────────────────────────────────────────
        self._crop_section = ctk.CTkFrame(self)
        self._crop_section.pack(fill="x", padx=10, pady=(5, 0))

        self._crop_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            self._crop_section, text="Crop", variable=self._crop_var,
            command=self._toggle_crop, font=FONTS["subheading"],
        ).pack(anchor="w", padx=5, pady=4)

        self._crop_frame = ctk.CTkFrame(self._crop_section)
        self._crop_frame.pack(fill="x", padx=10, pady=2)

        # Crop sub-mode selector
        self._crop_mode_row = ctk.CTkFrame(self._crop_frame)
        self._crop_mode_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(self._crop_mode_row, text="Mode:", width=80, anchor="w").pack(side="left", padx=(0, 5))
        self._crop_mode_var = ctk.StringVar(value="Aspect Ratio")
        self._crop_mode_menu = ctk.CTkOptionMenu(
            self._crop_mode_row, values=["Aspect Ratio", "Center Crop", "Coordinates"],
            variable=self._crop_mode_var,
            command=self._on_crop_mode_change,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            button_color=WIDGET_COLORS["dropdown_fg"],
            button_hover_color=WIDGET_COLORS["dropdown_hover"],
            text_color=WIDGET_COLORS["dropdown_text"],
        )
        self._crop_mode_menu.pack(side="left")

        # Aspect ratio sub-panel
        self._crop_ar_frame = ctk.CTkFrame(self._crop_frame)
        self._crop_ar_frame.pack(fill="x", padx=5, pady=2)

        ar_row = ctk.CTkFrame(self._crop_ar_frame)
        ar_row.pack(fill="x")
        ctk.CTkLabel(ar_row, text="Ratio:", width=80, anchor="w").pack(side="left", padx=(0, 5))
        self._crop_ar_var = ctk.StringVar(value="1:1")
        ctk.CTkOptionMenu(
            ar_row, values=["1:1", "4:3", "3:2", "16:9", "9:16", "3:4", "2:3"],
            variable=self._crop_ar_var,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            button_color=WIDGET_COLORS["dropdown_fg"],
            button_hover_color=WIDGET_COLORS["dropdown_hover"],
            text_color=WIDGET_COLORS["dropdown_text"],
        ).pack(side="left")

        anchor_row = ctk.CTkFrame(self._crop_ar_frame)
        anchor_row.pack(fill="x", pady=2)
        ctk.CTkLabel(anchor_row, text="Anchor:", width=80, anchor="w").pack(side="left", padx=(0, 5))
        self._crop_anchor_var = ctk.StringVar(value="center")
        ctk.CTkOptionMenu(
            anchor_row, values=["center", "top-left", "top-right", "bottom-left", "bottom-right"],
            variable=self._crop_anchor_var,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            button_color=WIDGET_COLORS["dropdown_fg"],
            button_hover_color=WIDGET_COLORS["dropdown_hover"],
            text_color=WIDGET_COLORS["dropdown_text"],
        ).pack(side="left")

        # Center crop sub-panel
        self._crop_center_frame = ctk.CTkFrame(self._crop_frame)
        center_row = ctk.CTkFrame(self._crop_center_frame)
        center_row.pack(fill="x")
        ctk.CTkLabel(center_row, text="Width:", width=50, anchor="w").pack(side="left")
        self._crop_cw = ctk.CTkEntry(center_row, width=80, placeholder_text="px")
        self._crop_cw.pack(side="left", padx=5)
        ctk.CTkLabel(center_row, text="x", width=20).pack(side="left")
        ctk.CTkLabel(center_row, text="Height:", width=50, anchor="w").pack(side="left")
        self._crop_ch = ctk.CTkEntry(center_row, width=80, placeholder_text="px")
        self._crop_ch.pack(side="left", padx=5)

        # Coordinates sub-panel
        self._crop_coords_frame = ctk.CTkFrame(self._crop_frame)
        coords_row1 = ctk.CTkFrame(self._crop_coords_frame)
        coords_row1.pack(fill="x")
        ctk.CTkLabel(coords_row1, text="X:", width=50, anchor="w").pack(side="left")
        self._crop_x = ctk.CTkEntry(coords_row1, width=70, placeholder_text="0")
        self._crop_x.pack(side="left", padx=5)
        ctk.CTkLabel(coords_row1, text="Y:", width=50, anchor="w").pack(side="left")
        self._crop_y = ctk.CTkEntry(coords_row1, width=70, placeholder_text="0")
        self._crop_y.pack(side="left", padx=5)
        coords_row2 = ctk.CTkFrame(self._crop_coords_frame)
        coords_row2.pack(fill="x", pady=2)
        ctk.CTkLabel(coords_row2, text="Width:", width=50, anchor="w").pack(side="left")
        self._crop_coord_w = ctk.CTkEntry(coords_row2, width=70, placeholder_text="px")
        self._crop_coord_w.pack(side="left", padx=5)
        ctk.CTkLabel(coords_row2, text="Height:", width=50, anchor="w").pack(side="left")
        self._crop_coord_h = ctk.CTkEntry(coords_row2, width=70, placeholder_text="px")
        self._crop_coord_h.pack(side="left", padx=5)

        # Visual Crop button
        self._visual_crop_btn = ctk.CTkButton(
            self._crop_frame, text="Visual Crop...", width=120,
            command=self._open_visual_crop,
        )
        self._visual_crop_btn.pack(anchor="w", padx=5, pady=(4, 2))

        _set_children_state(self._crop_frame, "disabled")

        # ── Quality section ──────────────────────────────────────
        self._quality_section = ctk.CTkFrame(self)
        self._quality_section.pack(fill="x", padx=10, pady=(5, 0))

        self._quality_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            self._quality_section, text="Set quality", variable=self._quality_var,
            command=self._toggle_quality, font=FONTS["subheading"],
        ).pack(anchor="w", padx=5, pady=4)

        self._quality_frame = ctk.CTkFrame(self._quality_section)
        self._quality_frame.pack(fill="x", padx=10, pady=2)

        self._quality = QualitySlider(self._quality_frame, label="Quality:")
        self._quality.pack(fill="x", padx=5, pady=2)

        _set_children_state(self._quality_frame, "disabled")

        # ── Strip Metadata (independent) ──────────────────────────
        self._strip_section = ctk.CTkFrame(self)
        self._strip_section.pack(fill="x", padx=10, pady=(5, 0))

        self._strip_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            self._strip_section, text="Strip metadata", variable=self._strip_var,
            command=self._on_strip_toggle, font=FONTS["subheading"],
        ).pack(anchor="w", padx=5, pady=4)

        # ── Write Metadata section ───────────────────────────────
        self._meta_section = ctk.CTkFrame(self)
        self._meta_section.pack(fill="x", padx=10, pady=(5, 0))

        self._meta_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            self._meta_section, text="Write metadata", variable=self._meta_var,
            command=self._toggle_metadata, font=FONTS["subheading"],
        ).pack(anchor="w", padx=5, pady=4)

        self._meta_frame = ctk.CTkFrame(self._meta_section)
        self._meta_frame.pack(fill="x", padx=10, pady=2)

        self._profile_selector = ProfileSelector(self._meta_frame, on_select=self._load_profile)
        self._profile_selector.pack(fill="x", padx=5, pady=(2, 5))

        self._meta_fields = MetadataFields(self._meta_frame)
        self._meta_fields.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(
            self._meta_frame,
            text="JPEG, PNG, and WebP support EXIF writing",
            text_color="gray", font=FONTS["small"],
        ).pack(anchor="w", padx=5, pady=(0, 2))

        _set_children_state(self._meta_frame, "disabled")

        # ── Output ───────────────────────────────────────────────
        ctk.CTkLabel(self, text="Output", font=FONTS["subheading"]).pack(
            anchor="w", padx=10, pady=(10, 2)
        )
        output_row = ctk.CTkFrame(self)
        output_row.pack(fill="x", padx=10, pady=2)
        self._output = FilePicker(output_row, label="Save as:", mode="save",
                                  on_change=self._on_output_manual)
        self._output.pack(side="left", fill="x", expand=True)
        self._auto_btn = ctk.CTkButton(
            output_row, text="Auto", width=50, command=self._reset_auto_output,
        )
        self._auto_btn.pack(side="left", padx=(5, 0))

        # ── Action ───────────────────────────────────────────────
        self._progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        # Not packed until processing starts

        self._btn = ctk.CTkButton(
            self, text="Process", command=self._run, height=36,
            fg_color=WIDGET_COLORS["button_primary"],
            hover_color=WIDGET_COLORS["button_primary_hover"],
        )
        self._btn.pack(padx=10, pady=10)

        self._result = ResultSummary(self)
        self._result.pack(fill="x", padx=10, pady=(0, 10))

    # ── Input / output auto-fill ─────────────────────────────

    def _on_input_change(self, path):
        self._preview.load(path)
        self._auto_output = True
        self._update_output_path()

    def _on_format_change(self, fmt):
        self._update_output_path()

    def _on_output_manual(self, path):
        self._auto_output = False

    def _reset_auto_output(self):
        self._auto_output = True
        self._update_output_path()

    def _update_output_path(self):
        inp = self._input.get_path()
        if not inp or not self._auto_output:
            return
        from pathlib import Path
        p = Path(inp)
        fmt = self._format.get() if self._convert_var.get() else None
        if fmt and fmt in _FORMAT_EXT:
            out = p.with_stem(p.stem + "_processed").with_suffix(_FORMAT_EXT[fmt])
        else:
            out = p.with_stem(p.stem + "_processed")
        self._output.set_path(str(out))

    # ── Section toggle — enable/disable ──────────────────────

    def _toggle_convert(self):
        state = "normal" if self._convert_var.get() else "disabled"
        _set_children_state(self._convert_frame, state)
        self._update_output_path()
        self._refresh_scroll_region()

    def _toggle_resize(self):
        state = "normal" if self._resize_var.get() else "disabled"
        _set_children_state(self._resize_frame, state)
        self._refresh_scroll_region()

    def _toggle_crop(self):
        state = "normal" if self._crop_var.get() else "disabled"
        _set_children_state(self._crop_frame, state)
        self._refresh_scroll_region()

    def _on_crop_mode_change(self, mode):
        self._crop_ar_frame.pack_forget()
        self._crop_center_frame.pack_forget()
        self._crop_coords_frame.pack_forget()
        if mode == "Aspect Ratio":
            self._crop_ar_frame.pack(fill="x", padx=5, pady=2, in_=self._crop_frame,
                                     after=self._crop_mode_row)
        elif mode == "Center Crop":
            self._crop_center_frame.pack(fill="x", padx=5, pady=2, in_=self._crop_frame,
                                         after=self._crop_mode_row)
        else:
            self._crop_coords_frame.pack(fill="x", padx=5, pady=2, in_=self._crop_frame,
                                         after=self._crop_mode_row)
        self._refresh_scroll_region()

    def _toggle_quality(self):
        if self._quality_var.get() and self._convert_var.get() and self._lossless_var.get():
            self._lossless_var.set(False)
        state = "normal" if self._quality_var.get() else "disabled"
        _set_children_state(self._quality_frame, state)
        self._refresh_scroll_region()

    def _on_lossless_toggle(self):
        if self._lossless_var.get() and self._quality_var.get():
            self._quality_var.set(False)
            _set_children_state(self._quality_frame, "disabled")

    def _toggle_metadata(self):
        state = "normal" if self._meta_var.get() else "disabled"
        _set_children_state(self._meta_frame, state)
        if self._meta_var.get() and self._strip_var.get():
            self._strip_var.set(False)
        self._refresh_scroll_region()

    # ── Resize mode switching ────────────────────────────────

    def _on_resize_mode_change(self, label):
        mode = _RESIZE_MODES[label]
        if mode == "percentage":
            self._dims_frame.pack_forget()
            self._pct_frame.pack(fill="x", padx=5, pady=2,
                                 in_=self._resize_frame, after=self._mode_row)
        else:
            self._pct_frame.pack_forget()
            self._dims_frame.pack(fill="x", padx=5, pady=2,
                                  in_=self._resize_frame, after=self._mode_row)
            # Update hint based on mode
            hints = {
                "fit": "Leave one blank to auto-scale",
                "exact": "Image will be stretched to exact dimensions",
                "fill": "Image will be cropped to fill exact dimensions",
            }
            self._dims_hint.configure(text=hints.get(mode, ""))
        self._refresh_scroll_region()

    def _on_strip_toggle(self):
        if self._strip_var.get() and self._meta_var.get():
            self._meta_var.set(False)
            self._toggle_metadata()

    def _load_profile(self, fields: dict[str, str]) -> None:
        self._meta_fields.set_fields(fields)

    # ── Visual Crop ──────────────────────────────────────────

    def _open_visual_crop(self):
        """Open the visual crop dialog for the loaded image."""
        inp = self._input.get_path()
        if not inp:
            show_error(self, "Error", "Load an image first")
            return

        from pathlib import Path
        if not Path(inp).is_file():
            show_error(self, "Error", f"File not found: {inp}")
            return

        # Read current crop state for initial values
        initial_crop = None
        crop_mode = self._crop_mode_var.get()
        if crop_mode == "Coordinates":
            try:
                cx = int(self._crop_x.get().strip())
                cy = int(self._crop_y.get().strip())
                cw = int(self._crop_coord_w.get().strip())
                ch = int(self._crop_coord_h.get().strip())
                if cw > 0 and ch > 0:
                    initial_crop = (cx, cy, cw, ch)
            except (ValueError, TypeError):
                pass

        initial_ar = None
        if crop_mode == "Aspect Ratio":
            initial_ar = self._crop_ar_var.get()

        from image_optimizer.gui.dialogs.crop_dialog import CropDialog
        CropDialog(
            self,
            image_path=inp,
            on_apply=self._apply_visual_crop,
            initial_crop=initial_crop,
            initial_aspect_ratio=initial_ar,
        )

    def _apply_visual_crop(self, x: int, y: int, w: int, h: int):
        """Callback from CropDialog — fill coordinate fields."""
        # Switch to Coordinates mode
        self._crop_mode_var.set("Coordinates")
        self._on_crop_mode_change("Coordinates")

        # Fill in the coordinate fields
        for entry, val in [(self._crop_x, x), (self._crop_y, y),
                           (self._crop_coord_w, w), (self._crop_coord_h, h)]:
            entry.delete(0, "end")
            entry.insert(0, str(val))

    # ── Run ──────────────────────────────────────────────────

    def _run(self):
        if self._worker and self._worker.is_running:
            return

        inp = self._input.get_path()
        out = self._output.get_path()
        if not inp:
            show_error(self, "Error", "Select an input file")
            return
        if not out:
            show_error(self, "Error", "Select an output file")
            return

        do_convert = self._convert_var.get()
        do_resize = self._resize_var.get()
        do_crop = self._crop_var.get()
        do_quality = self._quality_var.get()
        do_strip = self._strip_var.get()
        do_meta = self._meta_var.get()

        if not do_convert and not do_resize and not do_crop and not do_quality and not do_strip and not do_meta:
            show_error(self, "Error", "Enable at least one operation")
            return

        def run_pipeline():
            from image_optimizer.core.pipeline import Pipeline
            pipe = Pipeline(inp)

            if do_resize:
                mode_label = self._mode_var.get()
                mode = ResizeMode(_RESIZE_MODES[mode_label])
                pct = None
                if mode == ResizeMode.PERCENTAGE:
                    pct_str = self._pct_entry.get().strip()
                    if not pct_str:
                        raise ValueError("Enter a scale percentage")
                    try:
                        pct = float(pct_str)
                    except ValueError:
                        raise ValueError(f"Invalid percentage: '{pct_str}'")
                    if pct <= 0 or pct > 1000:
                        raise ValueError("Percentage must be between 0 and 1000")
                pipe.resize(
                    width=self._dims.get_width(),
                    height=self._dims.get_height(),
                    percentage=pct,
                    mode=mode,
                )

            if do_crop:
                crop_mode = self._crop_mode_var.get()
                if crop_mode == "Aspect Ratio":
                    pipe.crop(
                        aspect_ratio=self._crop_ar_var.get(),
                        anchor=self._crop_anchor_var.get(),
                    )
                elif crop_mode == "Center Crop":
                    cw = self._crop_cw.get().strip()
                    ch = self._crop_ch.get().strip()
                    if not cw or not ch:
                        raise ValueError("Enter both width and height for center crop")
                    pipe.crop(crop_width=int(cw), crop_height=int(ch))
                else:
                    cx = self._crop_x.get().strip()
                    cy = self._crop_y.get().strip()
                    cw = self._crop_coord_w.get().strip()
                    ch = self._crop_coord_h.get().strip()
                    if not all([cx, cy, cw, ch]):
                        raise ValueError("Enter x, y, width, and height for coordinate crop")
                    pipe.crop(
                        crop_width=int(cw), crop_height=int(ch),
                        x=int(cx), y=int(cy),
                    )

            if do_convert:
                fmt = self._format.get()
                if fmt:
                    pipe.convert(fmt)

            lossless = self._lossless_var.get() if do_convert else False
            quality = self._quality.get() if do_quality else None
            pipe.compress(quality=quality, lossless=lossless)

            if do_strip:
                pipe.strip_metadata()
            elif do_meta:
                fields = self._meta_fields.get_fields()
                if fields:
                    pipe.write_metadata(fields)

            return pipe.execute(out, policy=OverwritePolicy.RENAME)

        self._btn.configure(state="disabled", text="Processing...")
        self._result.clear()
        self._progress_bar.pack(fill="x", padx=10, pady=(0, 5))
        self._progress_bar.start()

        self._worker = WorkerThread(
            target=run_pipeline,
            on_complete=self._on_complete,
            on_error=self._on_error,
            widget=self,
        )
        self._worker.start()

    def _stop_progress(self):
        self._progress_bar.stop()
        self._progress_bar.pack_forget()
        self._refresh_scroll_region()

    def _on_complete(self, result):
        self._stop_progress()
        self._btn.configure(state="normal", text="Process")
        self._result.show_result(result)

    def _on_error(self, error):
        self._stop_progress()
        self._btn.configure(state="normal", text="Process")
        show_error(self, "Process Error", str(error))
