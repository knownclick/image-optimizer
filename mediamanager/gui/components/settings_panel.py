"""Quality slider, dimension inputs, and other settings widgets."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.gui.theme import WIDGET_COLORS


class QualitySlider(ctk.CTkFrame):
    """A labeled quality slider with value display."""

    def __init__(self, master, label: str = "Quality:", min_val: int = 1,
                 max_val: int = 95, default: int = 85, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(1, weight=1)

        self._label = ctk.CTkLabel(self, text=label, width=80, anchor="w")
        self._label.grid(row=0, column=0, padx=(0, 5))

        self._value_var = ctk.IntVar(value=default)
        self._slider = ctk.CTkSlider(
            self, from_=min_val, to=max_val,
            variable=self._value_var,
            command=self._on_slide,
        )
        self._slider.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        self._display = ctk.CTkLabel(self, text=str(default), width=40)
        self._display.grid(row=0, column=2)

    def _on_slide(self, value):
        self._display.configure(text=str(int(value)))

    def get(self) -> int:
        return self._value_var.get()

    def set(self, value: int):
        self._value_var.set(value)
        self._display.configure(text=str(value))


class DimensionInput(ctk.CTkFrame):
    """Width x Height input fields."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._w_label = ctk.CTkLabel(self, text="Width:", width=50, anchor="w")
        self._w_label.grid(row=0, column=0)
        self._width = ctk.CTkEntry(self, width=80, placeholder_text="auto")
        self._width.grid(row=0, column=1, padx=5)

        self._x_label = ctk.CTkLabel(self, text="x", width=20)
        self._x_label.grid(row=0, column=2)

        self._h_label = ctk.CTkLabel(self, text="Height:", width=50, anchor="w")
        self._h_label.grid(row=0, column=3)
        self._height = ctk.CTkEntry(self, width=80, placeholder_text="auto")
        self._height.grid(row=0, column=4, padx=5)

    def get_width(self) -> int | None:
        val = self._width.get().strip()
        return int(val) if val and val.isdigit() else None

    def get_height(self) -> int | None:
        val = self._height.get().strip()
        return int(val) if val and val.isdigit() else None

    def set_state(self, state: str):
        self._width.configure(state=state)
        self._height.configure(state=state)


class FormatSelector(ctk.CTkFrame):
    """Dropdown to select image format."""

    FORMATS = ["JPEG", "PNG", "WebP", "AVIF"]

    def __init__(self, master, label: str = "Format:", include_auto: bool = False,
                 on_change: callable = None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_change = on_change

        ctk.CTkLabel(self, text=label, width=80, anchor="w").pack(side="left", padx=(0, 5))

        values = (["Auto"] + self.FORMATS) if include_auto else self.FORMATS
        self._var = ctk.StringVar(value=values[0])
        self._menu = ctk.CTkOptionMenu(
            self, values=values, variable=self._var,
            command=self._on_select,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            button_color=WIDGET_COLORS["dropdown_fg"],
            button_hover_color=WIDGET_COLORS["dropdown_hover"],
            text_color=WIDGET_COLORS["dropdown_text"],
        )
        self._menu.pack(side="left")

    def _on_select(self, value):
        if self._on_change:
            self._on_change(self.get())

    def get(self) -> str | None:
        val = self._var.get()
        return None if val == "Auto" else val.lower()


class MetadataFields(ctk.CTkFrame):
    """EXIF metadata field entries for write operations."""

    FIELD_NAMES = [
        "artist", "copyright", "description", "title",
        "keywords", "software", "comment", "datetime",
    ]

    _PLACEHOLDERS = {
        "datetime": "YYYY:MM:DD HH:MM:SS",
        "keywords": "keyword1; keyword2; ...",
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._entries: dict[str, ctk.CTkEntry] = {}

        for field_name in self.FIELD_NAMES:
            row = ctk.CTkFrame(self)
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"{field_name.title()}:", width=90, anchor="w").pack(side="left")
            placeholder = self._PLACEHOLDERS.get(field_name, "")
            entry = ctk.CTkEntry(row, placeholder_text=placeholder)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            self._entries[field_name] = entry

    def get_fields(self) -> dict[str, str]:
        """Return only non-empty field values."""
        fields = {}
        for name, entry in self._entries.items():
            val = entry.get().strip()
            if val:
                fields[name] = val
        return fields

    def set_fields(self, fields: dict[str, str]) -> None:
        """Clear all entries, then fill from *fields* dict.

        Keys not present in this widget are silently ignored.
        """
        for name, entry in self._entries.items():
            entry.delete(0, "end")
            value = fields.get(name, "")
            if value:
                entry.insert(0, value)

    def set_state(self, state: str):
        for entry in self._entries.values():
            entry.configure(state=state)
