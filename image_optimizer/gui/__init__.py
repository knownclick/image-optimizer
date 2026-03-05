"""GUI interface using CustomTkinter."""

import sys


def _hide_console_window():
    """Hide the console window on Windows when running as a frozen .exe."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
        except Exception:
            pass


def launch_gui():
    """Launch the Image Optimizer GUI."""
    _hide_console_window()
    from image_optimizer.gui.app import ImageOptimizerApp
    app = ImageOptimizerApp()
    app.mainloop()
