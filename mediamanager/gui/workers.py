"""Threading wrappers to keep the GUI responsive during operations."""

from __future__ import annotations

import threading
from typing import Any, Callable


def _safe_after(widget, delay: int, callback, *args):
    """Call widget.after() but silently ignore if the widget is destroyed."""
    try:
        widget.after(delay, callback, *args)
    except Exception:
        pass  # Widget was destroyed


class WorkerThread:
    """Run a function in a daemon thread, reporting results to the GUI main thread."""

    def __init__(
        self,
        target: Callable[..., Any],
        args: tuple = (),
        kwargs: dict | None = None,
        on_complete: Callable[[Any], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        widget=None,
    ):
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}
        self._on_complete = on_complete
        self._on_error = on_error
        self._widget = widget  # A tkinter widget for .after() scheduling
        self._cancel_flag = threading.Event()
        self._thread: threading.Thread | None = None
        self._running = False

    @property
    def cancelled(self) -> bool:
        return self._cancel_flag.is_set()

    @property
    def is_running(self) -> bool:
        return self._running

    def cancel(self) -> None:
        """Set cooperative cancel flag."""
        self._cancel_flag.set()

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            result = self._target(*self._args, **self._kwargs)
            if not self._cancel_flag.is_set() and self._on_complete and self._widget:
                _safe_after(self._widget, 0, self._on_complete, result)
        except Exception as e:
            if not self._cancel_flag.is_set() and self._on_error and self._widget:
                _safe_after(self._widget, 0, self._on_error, e)
        finally:
            self._running = False


def make_threadsafe_progress_cb(widget) -> Callable[[int, int, str], None]:
    """Create a progress callback that marshals updates to the main thread."""
    _last_update = [0.0]

    def cb(current: int, total: int, filename: str) -> None:
        import time
        now = time.monotonic()
        # Throttle to at most ~20 updates/sec to avoid flooding the event queue
        if now - _last_update[0] < 0.05 and current < total:
            return
        _last_update[0] = now
        _safe_after(widget, 0, widget._on_progress, current, total, filename)

    return cb


def make_threadsafe_error_cb(widget) -> Callable[[str, str], None]:
    """Create an error callback that marshals per-file errors to the main thread."""

    def cb(filename: str, error_message: str) -> None:
        _safe_after(widget, 0, widget._on_file_error, filename, error_message)

    return cb
