"""Colors, fonts, and appearance settings for the GUI."""

import platform

# Platform-specific font selection
_system = platform.system()
if _system == "Windows":
    _SANS = "Segoe UI"
    _MONO = "Consolas"
elif _system == "Darwin":
    _SANS = "SF Pro"
    _MONO = "Menlo"
else:
    _SANS = "Sans"
    _MONO = "Monospace"

COLORS = {
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "success": "#16A34A",
    "error": "#DC2626",
    "warning": "#D97706",
    "bg_dark": "#1E1E2E",
    "bg_light": "#F8FAFC",
    "text_dark": "#E2E8F0",
    "text_light": "#1E293B",
}

WIDGET_COLORS = {
    "dropdown_fg": "#2563EB",
    "dropdown_hover": "#1D4ED8",
    "dropdown_text": "#FFFFFF",
    "button_primary": "#2563EB",
    "button_primary_hover": "#1D4ED8",
    "button_danger": "#DC2626",
    "button_danger_hover": "#B91C1C",
}

FONTS = {
    "heading": (_SANS, 16, "bold"),
    "subheading": (_SANS, 13, "bold"),
    "section": (_SANS, 11, "bold"),
    "body": (_SANS, 12),
    "small": (_SANS, 10),
    "mono": (_MONO, 11),
}

PADDING = {
    "section": 15,
    "widget": 8,
    "inner": 5,
}
