"""Modal error display dialog."""

from __future__ import annotations

import customtkinter as ctk

from image_optimizer.gui.theme import FONTS


class ErrorDialog(ctk.CTkToplevel):
    """Simple modal error dialog."""

    def __init__(self, master, title: str = "Error", message: str = ""):
        super().__init__(master)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, True)
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self.lift()

        ctk.CTkLabel(
            self, text=title, font=FONTS["subheading"],
        ).pack(padx=20, pady=(20, 10))

        ctk.CTkLabel(
            self, text=message, wraplength=360, justify="left",
        ).pack(padx=20, pady=5, fill="both", expand=True)

        ctk.CTkButton(self, text="OK", command=self.destroy, width=100).pack(pady=15)

        self.after(100, self.focus_force)


def show_error(master, title: str, message: str) -> None:
    """Convenience function to show an error dialog."""
    try:
        master.winfo_exists()
        ErrorDialog(master, title=title, message=message)
    except Exception:
        pass  # Widget was destroyed; silently ignore
