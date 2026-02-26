"""Favicon tab — ICO generation interface."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.gui.components.file_picker import FilePicker
from mediamanager.gui.components.image_preview import ImagePreview
from mediamanager.gui.components.result_summary import ResultSummary
from mediamanager.gui.components.error_dialog import show_error
from mediamanager.gui.workers import WorkerThread
from mediamanager.gui.theme import FONTS
from mediamanager.core.types import OverwritePolicy


class FaviconTab(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._worker = None

        # Input
        ctk.CTkLabel(self, text="Input", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))
        self._input = FilePicker(self, label="Input:", on_change=self._on_input_change)
        self._input.pack(fill="x", padx=10, pady=2)

        self._preview = ImagePreview(self)
        self._preview.pack(padx=10, pady=5)

        # Settings
        ctk.CTkLabel(self, text="Sizes", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))
        sizes_frame = ctk.CTkFrame(self)
        sizes_frame.pack(fill="x", padx=10, pady=2)

        self._size_vars: dict[int, ctk.BooleanVar] = {}
        for s in [16, 32, 48, 64, 128, 256]:
            var = ctk.BooleanVar(value=True)
            self._size_vars[s] = var
            ctk.CTkCheckBox(sizes_frame, text=f"{s}x{s}", variable=var).pack(side="left", padx=5)

        # Output
        ctk.CTkLabel(self, text="Output", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))
        self._output = FilePicker(self, label="Save as:", mode="save",
                                  filetypes=[("ICO files", "*.ico"), ("All files", "*.*")])
        self._output.pack(fill="x", padx=10, pady=2)

        # Action
        self._btn = ctk.CTkButton(self, text="Generate Favicon", command=self._run, height=36)
        self._btn.pack(padx=10, pady=10)

        self._result = ResultSummary(self)
        self._result.pack(fill="x", padx=10, pady=(0, 10))

    def _on_input_change(self, path):
        self._preview.load(path)

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

        sizes = [s for s, var in self._size_vars.items() if var.get()]
        if not sizes:
            show_error(self, "Error", "Select at least one size")
            return

        self._btn.configure(state="disabled", text="Generating...")
        self._result.clear()

        from mediamanager.core.favicon import generate_favicon
        self._worker = WorkerThread(
            target=generate_favicon,
            args=(inp, out),
            kwargs={"sizes": sizes, "policy": OverwritePolicy.RENAME},
            on_complete=self._on_complete,
            on_error=self._on_error,
            widget=self,
        )
        self._worker.start()

    def _on_complete(self, result):
        self._btn.configure(state="normal", text="Generate Favicon")
        self._result.show_result(result)

    def _on_error(self, error):
        self._btn.configure(state="normal", text="Generate Favicon")
        show_error(self, "Favicon Error", str(error))
