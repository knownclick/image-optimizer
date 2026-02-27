"""Main CustomTkinter window with tabbed layout."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.gui.theme import FONTS, WIDGET_COLORS
from mediamanager.gui.tabs.process_tab import ProcessTab
from mediamanager.gui.tabs.thumbnail_tab import ThumbnailTab
from mediamanager.gui.tabs.metadata_tab import MetadataTab
from mediamanager.gui.tabs.favicon_tab import FaviconTab
from mediamanager.gui.tabs.bulk_tab import BulkTab
from mediamanager.gui.tabs.profiles_tab import ProfilesTab
from mediamanager.gui.tabs.cli_tab import CLITab


class MediaManagerApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("Image Optimizer")
        self.geometry("1000x700")
        self.minsize(800, 600)

        # Graceful close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Header
        header = ctk.CTkFrame(self, height=40)
        header.pack(fill="x", padx=5, pady=(5, 0))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Image Optimizer", font=FONTS["heading"]).pack(side="left", padx=10)
        ctk.CTkLabel(
            header,
            text="Created by Hency Prajapati (Known Click Technologies)",
            font=FONTS["small"],
            text_color="gray",
        ).pack(side="left", padx=(5, 0))

        self._theme_var = ctk.StringVar(value="dark")
        ctk.CTkSegmentedButton(
            header, values=["dark", "light"],
            variable=self._theme_var,
            command=self._toggle_theme,
            selected_color=WIDGET_COLORS["dropdown_fg"],
            selected_hover_color=WIDGET_COLORS["dropdown_hover"],
            text_color=WIDGET_COLORS["dropdown_text"],
        ).pack(side="right", padx=10)

        # Tab view
        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(fill="both", expand=True, padx=5, pady=5)

        # Create tabs
        process_tab = self._tabs.add("Process")
        ProcessTab(process_tab).pack(fill="both", expand=True)

        thumbnail_tab = self._tabs.add("Thumbnail")
        ThumbnailTab(thumbnail_tab).pack(fill="both", expand=True)

        metadata_tab = self._tabs.add("Metadata")
        MetadataTab(metadata_tab).pack(fill="both", expand=True)

        favicon_tab = self._tabs.add("Favicon")
        FaviconTab(favicon_tab).pack(fill="both", expand=True)

        bulk_tab = self._tabs.add("Bulk")
        BulkTab(bulk_tab).pack(fill="both", expand=True)

        profiles_tab = self._tabs.add("Profiles")
        ProfilesTab(profiles_tab).pack(fill="both", expand=True)

        cli_tab = self._tabs.add("CLI")
        CLITab(cli_tab).pack(fill="both", expand=True)

    def _toggle_theme(self, value):
        ctk.set_appearance_mode(value)

    def _on_close(self):
        """Handle window close — destroy cleanly."""
        self.destroy()
