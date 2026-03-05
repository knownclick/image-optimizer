"""Main CustomTkinter window with tabbed layout."""

from __future__ import annotations

import customtkinter as ctk

from image_optimizer.gui.theme import FONTS, WIDGET_COLORS


class ImageOptimizerApp(ctk.CTk):
    """Main application window."""

    _TAB_NAMES = ["Process", "Thumbnail", "Metadata", "Favicon", "Bulk", "Profiles", "CLI"]

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

        # Tab view — lazy loading for fast startup
        self._tabs = ctk.CTkTabview(self, command=self._on_tab_change)
        self._tabs.pack(fill="both", expand=True, padx=5, pady=5)

        self._tab_frames = {}
        for name in self._TAB_NAMES:
            self._tab_frames[name] = self._tabs.add(name)

        self._loaded_tabs: set[str] = set()

        # Only load the first (visible) tab eagerly
        self._load_tab("Process")

    def _on_tab_change(self):
        name = self._tabs.get()
        if name not in self._loaded_tabs:
            self._load_tab(name)

    def _load_tab(self, name: str):
        frame = self._tab_frames[name]
        if name == "Process":
            from image_optimizer.gui.tabs.process_tab import ProcessTab
            ProcessTab(frame).pack(fill="both", expand=True)
        elif name == "Thumbnail":
            from image_optimizer.gui.tabs.thumbnail_tab import ThumbnailTab
            ThumbnailTab(frame).pack(fill="both", expand=True)
        elif name == "Metadata":
            from image_optimizer.gui.tabs.metadata_tab import MetadataTab
            MetadataTab(frame).pack(fill="both", expand=True)
        elif name == "Favicon":
            from image_optimizer.gui.tabs.favicon_tab import FaviconTab
            FaviconTab(frame).pack(fill="both", expand=True)
        elif name == "Bulk":
            from image_optimizer.gui.tabs.bulk_tab import BulkTab
            BulkTab(frame).pack(fill="both", expand=True)
        elif name == "Profiles":
            from image_optimizer.gui.tabs.profiles_tab import ProfilesTab
            ProfilesTab(frame).pack(fill="both", expand=True)
        elif name == "CLI":
            from image_optimizer.gui.tabs.cli_tab import CLITab
            CLITab(frame).pack(fill="both", expand=True)
        self._loaded_tabs.add(name)

    def _toggle_theme(self, value):
        ctk.set_appearance_mode(value)

    def _on_close(self):
        """Handle window close — destroy cleanly."""
        self.destroy()
