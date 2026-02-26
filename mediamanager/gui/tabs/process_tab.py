"""Process tab — unified convert + resize + compress + metadata interface."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.gui.components.file_picker import FilePicker
from mediamanager.gui.components.image_preview import ImagePreview
from mediamanager.gui.components.settings_panel import (
    DimensionInput,
    FormatSelector,
    MetadataFields,
    QualitySlider,
)
from mediamanager.gui.components.result_summary import ResultSummary
from mediamanager.gui.components.error_dialog import show_error
from mediamanager.gui.workers import WorkerThread
from mediamanager.gui.theme import FONTS
from mediamanager.core.types import OverwritePolicy, ResizeMode

# Format name -> file extension
_FORMAT_EXT = {"jpeg": ".jpg", "png": ".png", "webp": ".webp", "avif": ".avif"}

# User-friendly resize mode labels
_RESIZE_MODES = {
    "Fit (keep ratio)": "fit",
    "Exact (stretch)": "exact",
    "Fill (crop)": "fill",
    "Scale by %": "percentage",
}

_DROPDOWN_FG = "#2563EB"
_DROPDOWN_HOVER = "#1D4ED8"
_DROPDOWN_TEXT = "#FFFFFF"


class ProcessTab(ctk.CTkScrollableFrame):
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
        ctk.CTkCheckBox(
            self._convert_section, text="Convert format", variable=self._convert_var,
            command=self._toggle_convert, font=FONTS["subheading"],
        ).pack(anchor="w", padx=0, pady=2)

        self._convert_frame = ctk.CTkFrame(self._convert_section)
        # Not packed — hidden by default

        self._format = FormatSelector(self._convert_frame, label="Format:",
                                      on_change=self._on_format_change)
        self._format.pack(fill="x", padx=5, pady=2)

        self._lossless_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._convert_frame, text="Lossless (WebP/AVIF)", variable=self._lossless_var,
        ).pack(anchor="w", padx=5, pady=2)

        # ── Resize section ───────────────────────────────────────
        self._resize_section = ctk.CTkFrame(self)
        self._resize_section.pack(fill="x", padx=10, pady=(5, 0))

        self._resize_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._resize_section, text="Resize image", variable=self._resize_var,
            command=self._toggle_resize, font=FONTS["subheading"],
        ).pack(anchor="w", padx=0, pady=2)

        self._resize_frame = ctk.CTkFrame(self._resize_section)
        # Not packed — hidden by default

        mode_frame = ctk.CTkFrame(self._resize_frame)
        mode_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(mode_frame, text="Mode:", width=80, anchor="w").pack(side="left", padx=(0, 5))
        self._mode_var = ctk.StringVar(value="Fit (keep ratio)")
        self._mode_menu = ctk.CTkOptionMenu(
            mode_frame, values=list(_RESIZE_MODES.keys()),
            variable=self._mode_var,
            command=self._on_resize_mode_change,
            fg_color=_DROPDOWN_FG,
            button_color=_DROPDOWN_FG,
            button_hover_color=_DROPDOWN_HOVER,
            text_color=_DROPDOWN_TEXT,
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

        # ── Quality section ──────────────────────────────────────
        self._quality_section = ctk.CTkFrame(self)
        self._quality_section.pack(fill="x", padx=10, pady=(5, 0))

        self._quality_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._quality_section, text="Set quality", variable=self._quality_var,
            command=self._toggle_quality, font=FONTS["subheading"],
        ).pack(anchor="w", padx=0, pady=2)

        self._quality_frame = ctk.CTkFrame(self._quality_section)
        # Not packed — hidden by default

        self._quality = QualitySlider(self._quality_frame, label="Quality:")
        self._quality.pack(fill="x", padx=5, pady=2)

        self._strip_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._quality_frame, text="Strip metadata", variable=self._strip_var,
        ).pack(anchor="w", padx=5, pady=2)

        # ── Write Metadata section ───────────────────────────────
        self._meta_section = ctk.CTkFrame(self)
        self._meta_section.pack(fill="x", padx=10, pady=(5, 0))

        self._meta_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._meta_section, text="Write metadata", variable=self._meta_var,
            command=self._toggle_metadata, font=FONTS["subheading"],
        ).pack(anchor="w", padx=0, pady=2)

        self._meta_frame = ctk.CTkFrame(self._meta_section)
        # Not packed — hidden by default

        self._meta_fields = MetadataFields(self._meta_frame)
        self._meta_fields.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(
            self._meta_frame,
            text="Only JPEG and WebP support EXIF writing",
            text_color="gray", font=FONTS["small"],
        ).pack(anchor="w", padx=5, pady=(0, 2))

        # ── Output ───────────────────────────────────────────────
        ctk.CTkLabel(self, text="Output", font=FONTS["subheading"]).pack(
            anchor="w", padx=10, pady=(10, 2)
        )
        self._output = FilePicker(self, label="Save as:", mode="save",
                                  on_change=self._on_output_manual)
        self._output.pack(fill="x", padx=10, pady=2)

        # ── Action ───────────────────────────────────────────────
        self._btn = ctk.CTkButton(self, text="Process", command=self._run, height=36)
        self._btn.pack(padx=10, pady=10)

        self._result = ResultSummary(self)
        self._result.pack(fill="x", padx=10, pady=(0, 10))

    # ── Input / output auto-fill ─────────────────────────────

    def _on_input_change(self, path):
        self._preview.load(path)
        self._update_output_path()

    def _on_format_change(self, fmt):
        self._update_output_path()

    def _on_output_manual(self, path):
        self._auto_output = False

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

    # ── Section toggle — show/hide ────────────────────────────

    def _toggle_convert(self):
        if self._convert_var.get():
            self._convert_frame.pack(fill="x", padx=10, pady=2)
        else:
            self._convert_frame.pack_forget()
        self._update_output_path()

    def _toggle_resize(self):
        if self._resize_var.get():
            self._resize_frame.pack(fill="x", padx=10, pady=2)
        else:
            self._resize_frame.pack_forget()

    def _toggle_quality(self):
        if self._quality_var.get():
            self._quality_frame.pack(fill="x", padx=10, pady=2)
        else:
            self._quality_frame.pack_forget()

    def _toggle_metadata(self):
        if self._meta_var.get():
            self._meta_frame.pack(fill="x", padx=10, pady=2)
        else:
            self._meta_frame.pack_forget()

    # ── Resize mode switching ────────────────────────────────

    def _on_resize_mode_change(self, label):
        mode = _RESIZE_MODES[label]
        if mode == "percentage":
            self._dims_frame.pack_forget()
            self._pct_frame.pack(fill="x", padx=5, pady=2,
                                 in_=self._resize_frame, after=self._resize_frame.winfo_children()[0])
        else:
            self._pct_frame.pack_forget()
            self._dims_frame.pack(fill="x", padx=5, pady=2,
                                  in_=self._resize_frame, after=self._resize_frame.winfo_children()[0])
            # Update hint based on mode
            hints = {
                "fit": "Leave one blank to auto-scale",
                "exact": "Image will be stretched to exact dimensions",
                "fill": "Image will be cropped to fill exact dimensions",
            }
            self._dims_hint.configure(text=hints.get(mode, ""))

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
        do_quality = self._quality_var.get()
        do_meta = self._meta_var.get()

        if not do_convert and not do_resize and not do_quality and not do_meta:
            show_error(self, "Error", "Enable at least one section")
            return

        def run_pipeline():
            from mediamanager.core.pipeline import Pipeline
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

            if do_convert:
                fmt = self._format.get()
                if fmt:
                    pipe.convert(fmt)

            lossless = self._lossless_var.get() if do_convert else False
            quality = self._quality.get() if do_quality else None
            pipe.compress(quality=quality, lossless=lossless)

            if do_quality and self._strip_var.get():
                pipe.strip_metadata()
            elif do_meta:
                fields = self._meta_fields.get_fields()
                if fields:
                    pipe.write_metadata(fields)

            return pipe.execute(out, policy=OverwritePolicy.RENAME)

        self._btn.configure(state="disabled", text="Processing...")
        self._result.clear()

        self._worker = WorkerThread(
            target=run_pipeline,
            on_complete=self._on_complete,
            on_error=self._on_error,
            widget=self,
        )
        self._worker.start()

    def _on_complete(self, result):
        self._btn.configure(state="normal", text="Process")
        self._result.show_result(result)

    def _on_error(self, error):
        self._btn.configure(state="normal", text="Process")
        show_error(self, "Process Error", str(error))
