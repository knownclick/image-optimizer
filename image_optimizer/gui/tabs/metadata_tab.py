"""Metadata tab — EXIF read/write/strip interface."""

from __future__ import annotations

import json

import customtkinter as ctk

from image_optimizer.gui.components.file_picker import FilePicker
from image_optimizer.gui.components.profile_selector import ProfileSelector
from image_optimizer.gui.components.result_summary import ResultSummary
from image_optimizer.gui.components.error_dialog import show_error
from image_optimizer.gui.field_defs import ALL_FIELD_GROUPS, FIELD_LABELS, FIELD_PLACEHOLDERS
from image_optimizer.gui.workers import WorkerThread
from image_optimizer.gui.scrollable_mixin import ScrollableFixMixin
from image_optimizer.gui.theme import FONTS, WIDGET_COLORS
from image_optimizer.core.types import OverwritePolicy


class MetadataTab(ScrollableFixMixin, ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._worker = None

        # Input
        ctk.CTkLabel(self, text="Input", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))
        self._input = FilePicker(self, label="Input:")
        self._input.pack(fill="x", padx=10, pady=2)

        # Read section
        ctk.CTkLabel(self, text="Read Metadata", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))
        self._read_btn = ctk.CTkButton(
            self, text="Read Metadata", command=self._read,
            fg_color=WIDGET_COLORS["button_primary"],
            hover_color=WIDGET_COLORS["button_primary_hover"],
        )
        self._read_btn.pack(anchor="w", padx=10, pady=2)

        self._meta_display = ctk.CTkTextbox(self, height=180, state="disabled")
        self._meta_display.pack(fill="x", padx=10, pady=5)

        # Strip section
        ctk.CTkLabel(self, text="Strip Metadata", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))
        self._strip_output = FilePicker(self, label="Save as:", mode="save")
        self._strip_output.pack(fill="x", padx=10, pady=2)
        self._strip_btn = ctk.CTkButton(
            self, text="Strip All Metadata", command=self._strip,
            fg_color=WIDGET_COLORS["button_danger"],
            hover_color=WIDGET_COLORS["button_danger_hover"],
        )
        self._strip_btn.pack(anchor="w", padx=10, pady=2)

        # Write section
        ctk.CTkLabel(self, text="Write Metadata", font=FONTS["subheading"]).pack(anchor="w", padx=10, pady=(10, 2))

        self._profile_selector = ProfileSelector(self, on_select=self._load_profile)
        self._profile_selector.pack(fill="x", padx=10, pady=(0, 5))

        self._fields: dict[str, ctk.CTkEntry] = {}

        def add_field_group(parent, label: str, field_names: list[str]):
            ctk.CTkLabel(parent, text=label, font=FONTS["section"]).pack(
                anchor="w", padx=5, pady=(6, 1)
            )
            frame = ctk.CTkFrame(parent)
            frame.pack(fill="x", padx=5, pady=2)
            for field_name in field_names:
                row = ctk.CTkFrame(frame)
                row.pack(fill="x", pady=1)
                display_label = FIELD_LABELS.get(field_name, field_name.replace("_", " ").title())
                ctk.CTkLabel(row, text=f"{display_label}:", width=110, anchor="w").pack(side="left")
                entry = ctk.CTkEntry(row, placeholder_text=FIELD_PLACEHOLDERS.get(field_name, ""))
                entry.pack(side="left", fill="x", expand=True, padx=5)
                self._fields[field_name] = entry

        fields_frame = ctk.CTkFrame(self)
        fields_frame.pack(fill="x", padx=10, pady=2)

        for group_label, field_names in ALL_FIELD_GROUPS:
            add_field_group(fields_frame, group_label, field_names)

        self._write_output = FilePicker(self, label="Save as:", mode="save")
        self._write_output.pack(fill="x", padx=10, pady=2)
        self._write_btn = ctk.CTkButton(
            self, text="Write Metadata", command=self._write,
            fg_color=WIDGET_COLORS["button_primary"],
            hover_color=WIDGET_COLORS["button_primary_hover"],
        )
        self._write_btn.pack(anchor="w", padx=10, pady=2)

        self._result = ResultSummary(self)
        self._result.pack(fill="x", padx=10, pady=(5, 10))

    def _set_buttons_state(self, state):
        for btn in (self._read_btn, self._strip_btn, self._write_btn):
            btn.configure(state=state)

    def _read(self):
        if self._worker and self._worker.is_running:
            return
        inp = self._input.get_path()
        if not inp:
            show_error(self, "Error", "Select an input file")
            return

        self._set_buttons_state("disabled")

        from image_optimizer.core.metadata import read_metadata
        self._worker = WorkerThread(
            target=read_metadata, args=(inp,),
            on_complete=self._on_read_complete,
            on_error=self._on_error,
            widget=self,
        )
        self._worker.start()

    def _on_read_complete(self, meta):
        self._set_buttons_state("normal")
        self._meta_display.configure(state="normal")
        self._meta_display.delete("1.0", "end")
        self._meta_display.insert("1.0", json.dumps(meta, indent=2, default=str))
        self._meta_display.configure(state="disabled")

    def _strip(self):
        if self._worker and self._worker.is_running:
            return
        inp = self._input.get_path()
        out = self._strip_output.get_path()
        if not inp:
            show_error(self, "Error", "Select an input file")
            return
        if not out:
            show_error(self, "Error", "Select an output file")
            return

        self._set_buttons_state("disabled")

        from image_optimizer.core.metadata import strip_metadata
        self._worker = WorkerThread(
            target=strip_metadata, args=(inp, out),
            kwargs={"policy": OverwritePolicy.RENAME},
            on_complete=self._on_op_complete,
            on_error=self._on_error,
            widget=self,
        )
        self._worker.start()

    def _write(self):
        if self._worker and self._worker.is_running:
            return
        inp = self._input.get_path()
        out = self._write_output.get_path()
        if not inp:
            show_error(self, "Error", "Select an input file")
            return
        if not out:
            show_error(self, "Error", "Select an output file")
            return

        fields = {}
        for name, entry in self._fields.items():
            val = entry.get().strip()
            if val:
                fields[name] = val

        if not fields:
            show_error(self, "Error", "Enter at least one metadata field")
            return

        self._set_buttons_state("disabled")

        from image_optimizer.core.metadata import write_metadata
        self._worker = WorkerThread(
            target=write_metadata, args=(inp, out, fields),
            kwargs={"policy": OverwritePolicy.RENAME},
            on_complete=self._on_op_complete,
            on_error=self._on_error,
            widget=self,
        )
        self._worker.start()

    def _on_op_complete(self, result):
        self._set_buttons_state("normal")
        self._result.show_result(result)

    def _load_profile(self, fields: dict[str, str]) -> None:
        """Fill the write-section entries from a profile."""
        for name, entry in self._fields.items():
            entry.delete(0, "end")
            value = fields.get(name, "")
            if value:
                entry.insert(0, value)

    def _on_error(self, error):
        self._set_buttons_state("normal")
        show_error(self, "Error", str(error))
