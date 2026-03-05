"""Mixin to fix scroll region updates in CTkScrollableFrame.

CTkScrollableFrame doesn't always recalculate its scroll region when child
widgets are toggled via pack_forget()/pack().  This mixin exposes a single
helper that forces a recalculation after the geometry manager has finished.

It also auto-refreshes on <Map> so lazily-created tabs get the correct
scroll region the first time they become visible.
"""

from __future__ import annotations


class ScrollableFixMixin:
    """Mix into any CTkScrollableFrame subclass, then call
    ``self._refresh_scroll_region()`` after every layout change."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Map>", self._on_map_refresh, add="+")

    def _on_map_refresh(self, event=None):
        self._refresh_scroll_region()

    def _refresh_scroll_region(self):
        def _do():
            try:
                self._parent_canvas.configure(
                    scrollregion=self._parent_canvas.bbox("all")
                )
            except Exception:
                pass

        self.after_idle(_do)
