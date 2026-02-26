"""Runtime hook: patch CTkFrame._draw to handle attribute errors gracefully.

In frozen (PyInstaller) builds, a Tk widget name resolution issue can cause
self._canvas to temporarily point to a child CTkLabel instead of the internal
CTkCanvas. This hook wraps _draw to catch and suppress that harmless error.
"""

import importlib


def _apply_patch():
    try:
        mod = importlib.import_module(
            "customtkinter.windows.widgets.ctk_frame"
        )
        CTkFrame = mod.CTkFrame
    except (ImportError, AttributeError):
        return

    _original_draw = CTkFrame._draw

    def _safe_draw(self, no_color_updates=False):
        try:
            _original_draw(self, no_color_updates)
        except AttributeError:
            # Tk name resolution glitch in frozen builds — skip this draw cycle
            pass

    CTkFrame._draw = _safe_draw


_apply_patch()
