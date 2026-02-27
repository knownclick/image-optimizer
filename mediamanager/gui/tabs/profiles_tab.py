"""Profiles tab — create, edit, and delete reusable metadata profiles."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.gui.components.profile_selector import ProfileSelector
from mediamanager.gui.field_defs import ALL_FIELD_GROUPS, FIELD_LABELS, FIELD_PLACEHOLDERS
from mediamanager.gui.profiles import delete_profile, list_profiles, save_profile
from mediamanager.gui.theme import FONTS, WIDGET_COLORS


class ProfilesTab(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # ── Profile selector + New / Delete ──────────────────────
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=(10, 5))

        self._selector = ProfileSelector(top, on_select=self._on_profile_selected)
        self._selector.pack(side="left", fill="x", expand=True)

        self._delete_btn = ctk.CTkButton(
            top, text="Delete", width=70, command=self._delete,
            fg_color=WIDGET_COLORS["button_danger"],
            hover_color=WIDGET_COLORS["button_danger_hover"],
        )
        self._delete_btn.pack(side="right", padx=(5, 0))

        # ── Name entry ───────────────────────────────────────────
        name_frame = ctk.CTkFrame(self)
        name_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(name_frame, text="Profile Name:", width=110, anchor="w").pack(side="left")
        self._name_entry = ctk.CTkEntry(name_frame, placeholder_text="e.g. Company A")
        self._name_entry.pack(side="left", fill="x", expand=True, padx=5)

        # ── Field editor ─────────────────────────────────────────
        self._fields: dict[str, ctk.CTkEntry] = {}
        fields_frame = ctk.CTkFrame(self)
        fields_frame.pack(fill="x", padx=10, pady=5)

        for group_label, field_names in ALL_FIELD_GROUPS:
            ctk.CTkLabel(fields_frame, text=group_label, font=FONTS["section"]).pack(
                anchor="w", padx=5, pady=(6, 1),
            )
            group = ctk.CTkFrame(fields_frame)
            group.pack(fill="x", padx=5, pady=2)
            for field_name in field_names:
                row = ctk.CTkFrame(group)
                row.pack(fill="x", pady=1)
                display = FIELD_LABELS.get(field_name, field_name.replace("_", " ").title())
                ctk.CTkLabel(row, text=f"{display}:", width=110, anchor="w").pack(side="left")
                entry = ctk.CTkEntry(row, placeholder_text=FIELD_PLACEHOLDERS.get(field_name, ""))
                entry.pack(side="left", fill="x", expand=True, padx=5)
                self._fields[field_name] = entry

        # ── Actions ──────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=(10, 5))

        self._save_btn = ctk.CTkButton(
            btn_frame, text="Save Profile", command=self._save,
            fg_color=WIDGET_COLORS["button_primary"],
            hover_color=WIDGET_COLORS["button_primary_hover"],
        )
        self._save_btn.pack(side="left", padx=(0, 5))

        self._clear_btn = ctk.CTkButton(
            btn_frame, text="Clear Fields", width=100, command=self._clear,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            hover_color=WIDGET_COLORS["dropdown_hover"],
        )
        self._clear_btn.pack(side="left")

        self._status = ctk.CTkLabel(self, text="", text_color="gray", font=FONTS["small"])
        self._status.pack(anchor="w", padx=10, pady=(0, 10))

    # ── Callbacks ────────────────────────────────────────────

    def _on_profile_selected(self, fields: dict[str, str]) -> None:
        """Fill name + field entries from a loaded profile."""
        selected_name = self._selector._var.get()
        self._name_entry.delete(0, "end")
        self._name_entry.insert(0, selected_name)
        for name, entry in self._fields.items():
            entry.delete(0, "end")
            value = fields.get(name, "")
            if value:
                entry.insert(0, value)
        self._status.configure(text=f"Loaded profile: {selected_name}")

    def _save(self) -> None:
        name = self._name_entry.get().strip()
        if not name:
            self._status.configure(text="Enter a profile name first")
            return
        fields = {}
        for field_name, entry in self._fields.items():
            val = entry.get().strip()
            if val:
                fields[field_name] = val
        save_profile(name, fields)
        self._selector.refresh()
        self._selector._var.set(name)
        self._status.configure(text=f"Saved profile: {name}")

    def _delete(self) -> None:
        name = self._selector._var.get()
        if not name or name == ProfileSelector._NONE:
            self._status.configure(text="Select a profile to delete")
            return
        delete_profile(name)
        self._clear()
        self._selector.refresh()
        self._status.configure(text=f"Deleted profile: {name}")

    def _clear(self) -> None:
        self._name_entry.delete(0, "end")
        for entry in self._fields.values():
            entry.delete(0, "end")
        self._status.configure(text="")
