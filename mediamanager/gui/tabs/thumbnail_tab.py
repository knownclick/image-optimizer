"""Thumbnail tab — multi-size thumbnail generation interface."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.gui.components.file_picker import FilePicker
from mediamanager.gui.components.image_preview import ImagePreview
from mediamanager.gui.components.settings_panel import FormatSelector, QualitySlider
from mediamanager.gui.components.result_summary import ResultSummary
from mediamanager.gui.components.error_dialog import show_error
from mediamanager.gui.workers import WorkerThread
from mediamanager.gui.theme import COLORS, FONTS, WIDGET_COLORS
from mediamanager.core.types import OverwritePolicy


class ThumbnailTab(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._worker = None
        self._auto_output = True

        # ── Input ────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Input", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))
        self._input = FilePicker(self, label="Input:", on_change=self._on_input_change)
        self._input.pack(fill="x", padx=10, pady=2)

        self._preview = ImagePreview(self)
        self._preview.pack(padx=10, pady=5)

        # ── Sizes ────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Sizes", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))
        ctk.CTkLabel(
            self, text="Select one or more sizes to generate:",
            text_color="gray", font=FONTS["small"],
        ).pack(anchor="w", padx=10)

        sizes_frame = ctk.CTkFrame(self)
        sizes_frame.pack(fill="x", padx=10, pady=2)

        self._size_vars: dict[int, ctk.BooleanVar] = {}
        for label_text, px in [("Small (64 x 64)", 64), ("Medium (150 x 150)", 150),
                               ("Large (300 x 300)", 300), ("XLarge (600 x 600)", 600)]:
            var = ctk.BooleanVar(value=(label_text.startswith("Medium")))
            ctk.CTkCheckBox(sizes_frame, text=label_text, variable=var).pack(anchor="w", padx=10, pady=1)
            self._size_vars[px] = var

        # Custom size — supports WxH or single number (square)
        custom_row = ctk.CTkFrame(sizes_frame)
        custom_row.pack(fill="x", padx=10, pady=2)
        self._custom_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(custom_row, text="Custom:", variable=self._custom_var).pack(side="left")
        self._custom_w_entry = ctk.CTkEntry(custom_row, width=70, placeholder_text="width")
        self._custom_w_entry.pack(side="left", padx=(5, 2))
        ctk.CTkLabel(custom_row, text="x").pack(side="left")
        self._custom_h_entry = ctk.CTkEntry(custom_row, width=70, placeholder_text="height")
        self._custom_h_entry.pack(side="left", padx=(2, 5))
        ctk.CTkLabel(custom_row, text="px", text_color="gray").pack(side="left")

        ctk.CTkLabel(
            sizes_frame,
            text="Leave height blank for square thumbnail",
            text_color="gray", font=FONTS["small"],
        ).pack(anchor="w", padx=10, pady=(0, 2))

        # ── Settings ─────────────────────────────────────────────
        ctk.CTkLabel(self, text="Settings", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))

        self._square_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Crop to square before thumbnailing", variable=self._square_var).pack(
            anchor="w", padx=10, pady=2
        )

        # Prefix
        prefix_row = ctk.CTkFrame(self)
        prefix_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(prefix_row, text="Prefix:", width=80, anchor="w").pack(side="left")
        self._prefix = ctk.CTkEntry(prefix_row, width=120, placeholder_text="thumb")
        self._prefix.insert(0, "thumb")
        self._prefix.pack(side="left", padx=5)

        # Suffix
        suffix_row = ctk.CTkFrame(self)
        suffix_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(suffix_row, text="Suffix:", width=80, anchor="w").pack(side="left")
        self._suffix = ctk.CTkEntry(suffix_row, width=120, placeholder_text="(optional)")
        self._suffix.pack(side="left", padx=5)

        # Naming hint
        ctk.CTkLabel(
            self, text="Output: {prefix}_{name}_{size}_{suffix}.ext",
            text_color="gray", font=FONTS["small"],
        ).pack(anchor="w", padx=10, pady=(0, 2))

        self._format = FormatSelector(self, label="Format:", include_auto=True)
        self._format.pack(fill="x", padx=10, pady=2)

        self._quality = QualitySlider(self, label="Quality:")
        self._quality.pack(fill="x", padx=10, pady=2)

        # ── Output ───────────────────────────────────────────────
        ctk.CTkLabel(self, text="Output Folder", font=FONTS["subheading"]).pack(
            anchor="w", padx=10, pady=(10, 2)
        )
        self._output = FilePicker(self, label="Folder:", mode="folder",
                                  on_change=self._on_output_manual)
        self._output.pack(fill="x", padx=10, pady=2)

        # ── Action ───────────────────────────────────────────────
        self._btn = ctk.CTkButton(
            self, text="Generate Thumbnails", command=self._run, height=36,
            fg_color=WIDGET_COLORS["button_primary"],
            hover_color=WIDGET_COLORS["button_primary_hover"],
        )
        self._btn.pack(padx=10, pady=10)

        self._result = ResultSummary(self)
        self._result.pack(fill="x", padx=10, pady=(0, 10))

    def _on_input_change(self, path):
        self._preview.load(path)
        if self._auto_output:
            from pathlib import Path
            p = Path(path)
            self._output.set_path(str(p.parent / "thumbnails"))

    def _on_output_manual(self, path):
        self._auto_output = False

    def _get_sizes(self) -> list[int | tuple[int, int]] | str:
        """Return list of sizes, or error string if custom value is invalid."""
        sizes: list[int | tuple[int, int]] = []
        for px, var in self._size_vars.items():
            if var.get():
                sizes.append(px)
        if self._custom_var.get():
            w_str = self._custom_w_entry.get().strip()
            h_str = self._custom_h_entry.get().strip()
            if not w_str:
                return "Custom size is checked but no width entered"
            if not w_str.isdigit() or int(w_str) <= 0:
                return f"Invalid custom width: '{w_str}'"
            w = int(w_str)
            if w > 10000:
                return f"Custom width {w} is too large (max 10000)"
            if h_str:
                if not h_str.isdigit() or int(h_str) <= 0:
                    return f"Invalid custom height: '{h_str}'"
                h = int(h_str)
                if h > 10000:
                    return f"Custom height {h} is too large (max 10000)"
                sizes.append((w, h))
            else:
                sizes.append(w)  # square
        return sizes

    def _run(self):
        if self._worker and self._worker.is_running:
            return
        inp = self._input.get_path()
        out_dir = self._output.get_path()
        if not inp:
            show_error(self, "Error", "Select an input file")
            return
        if not out_dir:
            show_error(self, "Error", "Select an output folder")
            return

        sizes = self._get_sizes()
        if isinstance(sizes, str):
            show_error(self, "Error", sizes)
            return
        if not sizes:
            show_error(self, "Error", "Select at least one thumbnail size")
            return

        prefix = self._prefix.get().strip() or "thumb"
        suffix = self._suffix.get().strip()

        self._btn.configure(state="disabled", text="Generating...")
        self._result.clear()

        from mediamanager.core.thumbnail import generate_thumbnails
        self._worker = WorkerThread(
            target=generate_thumbnails,
            args=(inp, out_dir, sizes),
            kwargs={
                "prefix": prefix,
                "suffix": suffix,
                "fmt": self._format.get(),
                "quality": self._quality.get(),
                "crop_to_square": self._square_var.get(),
                "policy": OverwritePolicy.RENAME,
            },
            on_complete=self._on_complete,
            on_error=self._on_error,
            widget=self,
        )
        self._worker.start()

    def _on_complete(self, results):
        self._btn.configure(state="normal", text="Generate Thumbnails")
        # Show summary of all results
        succeeded = sum(1 for r in results if r.success)
        failed = len(results) - succeeded
        if failed == 0:
            self._result._status.configure(text=f"Done: {succeeded} thumbnail(s) generated", text_color=COLORS["success"])
        else:
            self._result._status.configure(text=f"Done: {succeeded} OK, {failed} failed", text_color=COLORS["warning"])
        details = []
        for r in results:
            if r.success and r.output_path:
                size = r.metadata.get("thumbnail_size", "?")
                details.append(f"{r.output_path.name} ({size})")
            elif not r.success:
                details.append(f"Failed: {r.error_message}")
        self._result._details.configure(text="\n".join(details))

    def _on_error(self, error):
        self._btn.configure(state="normal", text="Generate Thumbnails")
        show_error(self, "Thumbnail Error", str(error))
