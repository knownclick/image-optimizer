"""Bulk tab — bulk process, thumbnail, and rename interface."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.gui.components.file_picker import FilePicker
from mediamanager.gui.components.settings_panel import (
    DimensionInput,
    FormatSelector,
    MetadataFields,
    QualitySlider,
)
from mediamanager.gui.components.progress_panel import ProgressPanel
from mediamanager.gui.components.result_summary import ResultSummary
from mediamanager.gui.components.error_dialog import show_error
from mediamanager.gui.workers import WorkerThread, make_threadsafe_progress_cb, make_threadsafe_error_cb
from mediamanager.gui.theme import FONTS
from mediamanager.core.types import OverwritePolicy, ResizeMode

_DROPDOWN_FG = "#2563EB"
_DROPDOWN_HOVER = "#1D4ED8"
_DROPDOWN_TEXT = "#FFFFFF"


class BulkTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._worker = None

        # Mode selector
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(mode_frame, text="Mode:", width=80, anchor="w").pack(side="left")
        self._mode_var = ctk.StringVar(value="process")
        self._mode_btn = ctk.CTkSegmentedButton(
            mode_frame, values=["process", "thumbnail", "rename"],
            variable=self._mode_var, command=self._on_mode_change,
            selected_color=_DROPDOWN_FG,
            selected_hover_color=_DROPDOWN_HOVER,
            text_color=_DROPDOWN_TEXT,
        )
        self._mode_btn.pack(side="left", padx=5)

        # Input folder
        ctk.CTkLabel(self, text="Input", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(5, 2))
        self._input = FilePicker(self, label="Folder:", mode="folder")
        self._input.pack(fill="x", padx=10, pady=2)

        self._recursive_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Include subdirectories", variable=self._recursive_var).pack(
            anchor="w", padx=10, pady=2
        )

        # Settings container — we swap contents based on mode
        self._settings_frame = ctk.CTkFrame(self)
        self._settings_frame.pack(fill="x", padx=10, pady=5)

        # ── Process settings ─────────────────────────────────────
        self._process_frame = ctk.CTkFrame(self._settings_frame)

        # Output
        ctk.CTkLabel(self._process_frame, text="Output", font=FONTS["subheading"]).pack(anchor="w", padx=5, pady=2)
        self._output_dir = FilePicker(self._process_frame, label="Output:", mode="folder")
        self._output_dir.pack(fill="x", padx=5, pady=2)

        # Format
        ctk.CTkLabel(self._process_frame, text="Format", font=FONTS["subheading"]).pack(anchor="w", padx=5, pady=(5, 2))
        self._format = FormatSelector(self._process_frame, label="Format:", include_auto=True)
        self._format.pack(fill="x", padx=5, pady=2)
        self._quality = QualitySlider(self._process_frame, label="Quality:")
        self._quality.pack(fill="x", padx=5, pady=2)

        self._lossless_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._process_frame, text="Lossless (WebP/AVIF)", variable=self._lossless_var,
        ).pack(anchor="w", padx=5, pady=2)

        # Resize — toggle to show/hide
        self._resize_section = ctk.CTkFrame(self._process_frame)
        self._resize_section.pack(fill="x", padx=5, pady=(5, 0))

        self._resize_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._resize_section, text="Resize images", variable=self._resize_var,
            command=self._toggle_resize, font=FONTS["subheading"],
        ).pack(anchor="w", padx=0, pady=2)

        self._resize_frame = ctk.CTkFrame(self._resize_section)
        # Not packed — hidden by default

        mode_row = ctk.CTkFrame(self._resize_frame)
        mode_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(mode_row, text="Mode:", width=80, anchor="w").pack(side="left", padx=(0, 5))
        self._resize_mode_var = ctk.StringVar(value="fit")
        ctk.CTkOptionMenu(
            mode_row, values=["fit", "exact", "fill"],
            variable=self._resize_mode_var,
            fg_color=_DROPDOWN_FG,
            button_color=_DROPDOWN_FG,
            button_hover_color=_DROPDOWN_HOVER,
            text_color=_DROPDOWN_TEXT,
        ).pack(side="left")

        self._dims = DimensionInput(self._resize_frame)
        self._dims.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(
            self._resize_frame, text="Set only width or height to auto-scale",
            text_color="gray", font=FONTS["small"],
        ).pack(anchor="w", padx=5, pady=(0, 2))

        # Options
        ctk.CTkLabel(self._process_frame, text="Options", font=FONTS["subheading"]).pack(anchor="w", padx=5, pady=(5, 2))

        self._strip_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._process_frame, text="Strip metadata", variable=self._strip_var,
        ).pack(anchor="w", padx=5, pady=2)

        # Write metadata — toggle to show/hide
        self._meta_section = ctk.CTkFrame(self._process_frame)
        self._meta_section.pack(fill="x", padx=5, pady=(2, 0))

        self._meta_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._meta_section, text="Write metadata", variable=self._meta_var,
            command=self._toggle_meta,
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

        # ── Thumbnail settings ───────────────────────────────────
        self._thumb_frame = ctk.CTkFrame(self._settings_frame)

        ctk.CTkLabel(self._thumb_frame, text="Output", font=FONTS["subheading"]).pack(anchor="w", padx=5, pady=2)
        self._thumb_output_dir = FilePicker(self._thumb_frame, label="Output:", mode="folder")
        self._thumb_output_dir.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(self._thumb_frame, text="Sizes", font=FONTS["subheading"]).pack(anchor="w", padx=5, pady=(5, 2))

        self._thumb_size_vars = {}
        sizes_frame = ctk.CTkFrame(self._thumb_frame)
        sizes_frame.pack(fill="x", padx=5, pady=2)
        for label_text, px in [("Small (64 x 64)", 64), ("Medium (150 x 150)", 150),
                               ("Large (300 x 300)", 300), ("XLarge (600 x 600)", 600)]:
            var = ctk.BooleanVar(value=(label_text.startswith("Medium")))
            ctk.CTkCheckBox(sizes_frame, text=label_text, variable=var).pack(anchor="w", padx=5, pady=1)
            self._thumb_size_vars[px] = var

        # Custom size — supports WxH or single number (square)
        custom_row = ctk.CTkFrame(sizes_frame)
        custom_row.pack(fill="x", padx=5, pady=2)
        self._thumb_custom_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(custom_row, text="Custom:", variable=self._thumb_custom_var).pack(side="left")
        self._thumb_custom_w = ctk.CTkEntry(custom_row, width=70, placeholder_text="width")
        self._thumb_custom_w.pack(side="left", padx=(5, 2))
        ctk.CTkLabel(custom_row, text="x").pack(side="left")
        self._thumb_custom_h = ctk.CTkEntry(custom_row, width=70, placeholder_text="height")
        self._thumb_custom_h.pack(side="left", padx=(2, 5))
        ctk.CTkLabel(custom_row, text="px", text_color="gray").pack(side="left")

        ctk.CTkLabel(
            sizes_frame,
            text="Leave height blank for square thumbnail",
            text_color="gray", font=FONTS["small"],
        ).pack(anchor="w", padx=5, pady=(0, 2))

        ctk.CTkLabel(self._thumb_frame, text="Settings", font=FONTS["subheading"]).pack(anchor="w", padx=5, pady=(5, 2))

        # Prefix
        prefix_row = ctk.CTkFrame(self._thumb_frame)
        prefix_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(prefix_row, text="Prefix:", width=80, anchor="w").pack(side="left")
        self._thumb_prefix = ctk.CTkEntry(prefix_row, width=120, placeholder_text="thumb")
        self._thumb_prefix.insert(0, "thumb")
        self._thumb_prefix.pack(side="left", padx=5)

        # Suffix
        suffix_row = ctk.CTkFrame(self._thumb_frame)
        suffix_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(suffix_row, text="Suffix:", width=80, anchor="w").pack(side="left")
        self._thumb_suffix = ctk.CTkEntry(suffix_row, width=120, placeholder_text="(optional)")
        self._thumb_suffix.pack(side="left", padx=5)

        # Naming hint
        ctk.CTkLabel(
            self._thumb_frame,
            text="Output: {prefix}_{name}_{size}_{suffix}.ext",
            text_color="gray", font=FONTS["small"],
        ).pack(anchor="w", padx=5, pady=(0, 2))

        self._thumb_square_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self._thumb_frame, text="Crop to square", variable=self._thumb_square_var,
        ).pack(anchor="w", padx=5, pady=2)

        self._thumb_format = FormatSelector(self._thumb_frame, label="Format:", include_auto=True)
        self._thumb_format.pack(fill="x", padx=5, pady=2)
        self._thumb_quality = QualitySlider(self._thumb_frame, label="Quality:")
        self._thumb_quality.pack(fill="x", padx=5, pady=2)

        # ── Rename settings ──────────────────────────────────────
        self._rename_frame = ctk.CTkFrame(self._settings_frame)
        ctk.CTkLabel(self._rename_frame, text="Rename Settings", font=FONTS["subheading"]).pack(anchor="w", padx=5, pady=2)
        pat_row = ctk.CTkFrame(self._rename_frame)
        pat_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(pat_row, text="Pattern:", width=80, anchor="w").pack(side="left")
        self._pattern_entry = ctk.CTkEntry(pat_row, placeholder_text="img_{n:03d}.{ext}")
        self._pattern_entry.pack(side="left", fill="x", expand=True, padx=5)

        start_row = ctk.CTkFrame(self._rename_frame)
        start_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(start_row, text="Start #:", width=80, anchor="w").pack(side="left")
        self._start_entry = ctk.CTkEntry(start_row, width=60)
        self._start_entry.insert(0, "1")
        self._start_entry.pack(side="left")

        self._dry_run_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self._rename_frame, text="Dry run (preview only)", variable=self._dry_run_var).pack(anchor="w", padx=5, pady=2)

        ctk.CTkLabel(
            self._rename_frame,
            text="Tokens: {name} {ext} {n} {n:03d} {date} {w} {h} {format}",
            text_color="gray", font=FONTS["small"],
        ).pack(anchor="w", padx=5, pady=(0, 2))

        # Show process settings by default
        self._process_frame.pack(fill="x")

        # Progress + action
        self._progress = ProgressPanel(self)
        self._progress.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        self._btn = ctk.CTkButton(btn_frame, text="Start", command=self._run, height=36)
        self._btn.pack(side="left", padx=(0, 5))
        self._cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=self._cancel,
                                          height=36, state="disabled", fg_color="#DC2626")
        self._cancel_btn.pack(side="left")

        self._result = ResultSummary(self)
        self._result.pack(fill="x", padx=10, pady=(0, 10))

    def _toggle_resize(self):
        if self._resize_var.get():
            self._resize_frame.pack(fill="x", padx=10, pady=2)
        else:
            self._resize_frame.pack_forget()

    def _toggle_meta(self):
        if self._meta_var.get():
            self._meta_frame.pack(fill="x", padx=10, pady=2)
        else:
            self._meta_frame.pack_forget()

    def _on_mode_change(self, value):
        self._process_frame.pack_forget()
        self._thumb_frame.pack_forget()
        self._rename_frame.pack_forget()
        if value == "process":
            self._process_frame.pack(fill="x", in_=self._settings_frame)
        elif value == "thumbnail":
            self._thumb_frame.pack(fill="x", in_=self._settings_frame)
        else:
            self._rename_frame.pack(fill="x", in_=self._settings_frame)

    def _on_progress(self, current, total, filename):
        self._progress.update_progress(current, total, filename)
        self._progress.log(f"[{current}/{total}] {filename}")

    def _on_file_error(self, filename, error_message):
        """Called on main thread when a single file fails during bulk operation."""
        self._progress.log_error(filename, error_message)

    def _get_thumb_sizes(self) -> list[int | tuple[int, int]] | str:
        """Return list of sizes, or error string if custom value is invalid."""
        sizes: list[int | tuple[int, int]] = []
        for px, var in self._thumb_size_vars.items():
            if var.get():
                sizes.append(px)
        if self._thumb_custom_var.get():
            w_str = self._thumb_custom_w.get().strip()
            h_str = self._thumb_custom_h.get().strip()
            if not w_str:
                return "Custom size is checked but no width entered"
            if not w_str.isdigit() or int(w_str) <= 0:
                return f"Invalid custom width: '{w_str}' (must be a positive integer)"
            w = int(w_str)
            if w > 10000:
                return f"Custom width {w} is too large (max 10000)"
            if h_str:
                if not h_str.isdigit() or int(h_str) <= 0:
                    return f"Invalid custom height: '{h_str}' (must be a positive integer)"
                h = int(h_str)
                if h > 10000:
                    return f"Custom height {h} is too large (max 10000)"
                sizes.append((w, h))
            else:
                sizes.append(w)  # square
        return sizes

    def _run(self):
        inp = self._input.get_path()
        if not inp:
            show_error(self, "Error", "Select an input folder")
            return

        if self._worker and self._worker.is_running:
            return

        self._btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")
        self._mode_btn.configure(state="disabled")
        self._progress.reset()
        self._result.clear()

        mode = self._mode_var.get()
        progress_cb = make_threadsafe_progress_cb(self)
        error_cb = make_threadsafe_error_cb(self)

        if mode == "process":
            out = self._output_dir.get_path()
            if not out:
                show_error(self, "Error", "Select an output folder")
                self._reset_buttons()
                return

            fmt = self._format.get()
            do_resize = self._resize_var.get()

            if fmt is None and not do_resize:
                show_error(self, "Error", "Select a format or enable resize")
                self._reset_buttons()
                return

            resize_width = None
            resize_height = None
            resize_mode = ResizeMode.FIT
            if do_resize:
                resize_width = self._dims.get_width()
                resize_height = self._dims.get_height()
                resize_mode = ResizeMode(self._resize_mode_var.get())
                if resize_width is None and resize_height is None:
                    show_error(self, "Error", "Enter at least a width or height for resize")
                    self._reset_buttons()
                    return

            metadata_fields = None
            if self._meta_var.get() and not self._strip_var.get():
                metadata_fields = self._meta_fields.get_fields()

            from mediamanager.core.bulk import bulk_process
            self._worker = WorkerThread(
                target=bulk_process,
                args=(inp, out),
                kwargs={
                    "target_format": fmt,
                    "recursive": self._recursive_var.get(),
                    "quality": self._quality.get(),
                    "lossless": self._lossless_var.get(),
                    "resize_width": resize_width,
                    "resize_height": resize_height,
                    "resize_mode": resize_mode,
                    "strip_metadata": self._strip_var.get(),
                    "metadata_fields": metadata_fields,
                    "policy": OverwritePolicy.RENAME,
                    "progress_callback": progress_cb,
                    "error_callback": error_cb,
                },
                on_complete=self._on_complete,
                on_error=self._on_error,
                widget=self,
            )

        elif mode == "thumbnail":
            out = self._thumb_output_dir.get_path()
            if not out:
                show_error(self, "Error", "Select an output folder")
                self._reset_buttons()
                return

            sizes = self._get_thumb_sizes()
            if isinstance(sizes, str):
                show_error(self, "Error", sizes)
                self._reset_buttons()
                return
            if not sizes:
                show_error(self, "Error", "Select at least one thumbnail size")
                self._reset_buttons()
                return

            prefix = self._thumb_prefix.get().strip() or "thumb"
            suffix = self._thumb_suffix.get().strip()

            from mediamanager.core.bulk import bulk_thumbnails
            self._worker = WorkerThread(
                target=bulk_thumbnails,
                args=(inp, out, sizes),
                kwargs={
                    "prefix": prefix,
                    "suffix": suffix,
                    "recursive": self._recursive_var.get(),
                    "fmt": self._thumb_format.get(),
                    "quality": self._thumb_quality.get(),
                    "crop_to_square": self._thumb_square_var.get(),
                    "policy": OverwritePolicy.RENAME,
                    "progress_callback": progress_cb,
                    "error_callback": error_cb,
                },
                on_complete=self._on_complete,
                on_error=self._on_error,
                widget=self,
            )

        else:
            pattern = self._pattern_entry.get().strip()
            if not pattern:
                show_error(self, "Error", "Enter a rename pattern")
                self._reset_buttons()
                return

            start_str = self._start_entry.get().strip()
            if not start_str:
                start = 1
            else:
                try:
                    start = int(start_str)
                except ValueError:
                    show_error(self, "Error", f"Invalid start number: '{start_str}'")
                    self._reset_buttons()
                    return
                if start < 0:
                    show_error(self, "Error", "Start number cannot be negative")
                    self._reset_buttons()
                    return

            from mediamanager.core.bulk import bulk_rename
            self._worker = WorkerThread(
                target=bulk_rename,
                args=(inp, pattern),
                kwargs={
                    "recursive": self._recursive_var.get(),
                    "dry_run": self._dry_run_var.get(),
                    "start_number": start,
                    "policy": OverwritePolicy.SKIP,
                    "progress_callback": progress_cb,
                },
                on_complete=self._on_complete,
                on_error=self._on_error,
                widget=self,
            )

        self._worker.start()

    def _reset_buttons(self):
        self._btn.configure(state="normal")
        self._cancel_btn.configure(state="disabled")
        self._mode_btn.configure(state="normal")

    def _cancel(self):
        if self._worker:
            self._worker.cancel()
        self._progress.log("Cancelled by user")
        self._reset_buttons()

    def _on_complete(self, result):
        self._reset_buttons()
        self._result.show_bulk_result(result)

    def _on_error(self, error):
        self._reset_buttons()
        show_error(self, "Bulk Error", str(error))
