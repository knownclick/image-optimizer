"""Reusable profile selector dropdown."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from mediamanager.gui.profiles import list_profiles, load_profile
from mediamanager.gui.theme import WIDGET_COLORS


class ProfileSelector(ctk.CTkFrame):
    """Profile dropdown with refresh button.

    Parameters
    ----------
    on_select : callable receiving ``fields: dict[str, str]``
        Called when the user picks a profile from the dropdown.
    """

    _NONE = "(none)"

    def __init__(self, master, *, on_select: Callable[[dict[str, str]], None], **kwargs):
        super().__init__(master, **kwargs)
        self._on_select = on_select

        ctk.CTkLabel(self, text="Profile:", width=80, anchor="w").pack(side="left", padx=(0, 5))

        self._var = ctk.StringVar(value=self._NONE)
        self._menu = ctk.CTkOptionMenu(
            self,
            values=[self._NONE],
            variable=self._var,
            command=self._on_pick,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            button_color=WIDGET_COLORS["dropdown_fg"],
            button_hover_color=WIDGET_COLORS["dropdown_hover"],
            text_color=WIDGET_COLORS["dropdown_text"],
            width=180,
        )
        self._menu.pack(side="left", padx=(0, 5))

        self._refresh_btn = ctk.CTkButton(
            self, text="Refresh", width=70, command=self.refresh,
            fg_color=WIDGET_COLORS["dropdown_fg"],
            hover_color=WIDGET_COLORS["dropdown_hover"],
        )
        self._refresh_btn.pack(side="left")

        self.refresh()

    def refresh(self) -> None:
        """Reload the profile list from disk."""
        names = list_profiles()
        values = [self._NONE] + names
        self._menu.configure(values=values)
        if self._var.get() not in values:
            self._var.set(self._NONE)

    def _on_pick(self, value: str) -> None:
        if value == self._NONE:
            return
        fields = load_profile(value)
        if self._on_select:
            self._on_select(fields)
