"""File and folder selector widget."""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk


class _Tooltip:
    """Simple hover tooltip for a widget."""

    def __init__(self, widget, text: str = ""):
        self._widget = widget
        self._text = text
        self._tw = None
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def update(self, text: str):
        self._text = text

    def _on_enter(self, _event):
        if not self._text:
            return
        import tkinter as tk
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 2
        self._tw = tk.Toplevel(self._widget)
        self._tw.wm_overrideredirect(True)
        self._tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self._tw, text=self._text, justify="left",
            background="#333333", foreground="#eeeeee",
            relief="solid", borderwidth=1, padx=6, pady=3,
            font=("Sans", 9),
        )
        label.pack()

    def _on_leave(self, _event):
        if self._tw:
            self._tw.destroy()
            self._tw = None


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

        self._entry = ctk.CTkEntry(self, placeholder_text="Select a file...", state="disabled")
        self._entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        self._tooltip = _Tooltip(self._entry)

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
        self._entry.configure(state="normal")
        val = self._entry.get().strip()
        self._entry.configure(state="disabled")
        return val

    def set_path(self, path: str):
        self._entry.configure(state="normal")
        self._entry.delete(0, "end")
        self._entry.insert(0, path)
        self._entry.configure(state="disabled")
        self._tooltip.update(path)
