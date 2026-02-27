"""Progress bar and scrollable log for bulk operations."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.gui.theme import COLORS


class ProgressPanel(ctk.CTkFrame):
    """Progress bar + scrollable log with error support."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._progress_var = ctk.DoubleVar(value=0)
        self._progress_bar = ctk.CTkProgressBar(self, variable=self._progress_var)
        self._progress_bar.pack(fill="x", padx=5, pady=5)

        self._status_label = ctk.CTkLabel(self, text="Ready", anchor="w")
        self._status_label.pack(fill="x", padx=5)

        self._error_count = 0
        self._error_label = ctk.CTkLabel(self, text="", anchor="w", text_color=COLORS["error"])
        self._error_label.pack(fill="x", padx=5)

        self._log = ctk.CTkTextbox(self, height=150, state="disabled")
        self._log.pack(fill="both", expand=True, padx=5, pady=5)

    def reset(self) -> None:
        self._progress_var.set(0)
        self._status_label.configure(text="Ready")
        self._error_count = 0
        self._error_label.configure(text="")
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

    def update_progress(self, current: int, total: int, message: str = "") -> None:
        if total > 0:
            self._progress_var.set(current / total)
        self._status_label.configure(text=f"{current}/{total} {message}")

    def log(self, text: str) -> None:
        self._log.configure(state="normal")
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def log_error(self, filename: str, error: str) -> None:
        """Log a per-file error in the progress log."""
        self._error_count += 1
        self._error_label.configure(text=f"Errors: {self._error_count}")
        self._log.configure(state="normal")
        self._log.insert("end", f"FAIL  {filename}: {error}\n")
        self._log.see("end")
        self._log.configure(state="disabled")
