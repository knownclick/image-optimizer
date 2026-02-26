"""File and folder selector widget."""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk


class FilePicker(ctk.CTkFrame):
    """A row with a label, text entry, and browse button."""

    def __init__(
        self,
        master,
        label: str = "File:",
        mode: str = "file",  # "file", "save", or "folder"
        filetypes: list[tuple[str, str]] | None = None,
        on_change: callable = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._mode = mode
        self._filetypes = filetypes or [
            ("Image files", "*.jpg *.jpeg *.png *.webp *.avif *.ico"),
            ("All files", "*.*"),
        ]
        self._on_change = on_change

        self.columnconfigure(1, weight=1)

        self._label = ctk.CTkLabel(self, text=label, width=80, anchor="w")
        self._label.grid(row=0, column=0, padx=(0, 5))

        self._entry = ctk.CTkEntry(self, placeholder_text="Select a file...")
        self._entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        self._btn = ctk.CTkButton(self, text="Browse", width=80, command=self._browse)
        self._btn.grid(row=0, column=2)

    def _browse(self):
        if self._mode == "file":
            path = filedialog.askopenfilename(filetypes=self._filetypes)
        elif self._mode == "save":
            path = filedialog.asksaveasfilename(filetypes=self._filetypes)
        elif self._mode == "folder":
            path = filedialog.askdirectory()
        else:
            return

        if path:
            self.set_path(path)
            if self._on_change:
                self._on_change(path)

    def get_path(self) -> str:
        return self._entry.get().strip()

    def set_path(self, path: str):
        self._entry.delete(0, "end")
        self._entry.insert(0, path)
