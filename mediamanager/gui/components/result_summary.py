"""Post-operation results display."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.core.types import OperationResult, BulkResult
from mediamanager.core.utils import format_file_size
from mediamanager.gui.theme import FONTS


class ResultSummary(ctk.CTkFrame):
    """Display operation result with status and details."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._status = ctk.CTkLabel(self, text="", font=FONTS["subheading"], anchor="w")
        self._status.pack(fill="x", padx=5, pady=(5, 2))

        # Simple label for single-file results
        self._details = ctk.CTkLabel(self, text="", justify="left", anchor="w", wraplength=600)
        self._details.pack(fill="x", padx=5, pady=(0, 5))

        # Scrollable log for bulk results (hidden until needed)
        self._log = ctk.CTkTextbox(self, height=150, state="disabled")

    def show_result(self, result: OperationResult) -> None:
        self._log.pack_forget()
        self._details.pack(fill="x", padx=5, pady=(0, 5))

        if result.success:
            self._status.configure(text="Success", text_color="#16A34A")
            details = []
            if result.output_path:
                details.append(f"Saved: {result.output_path}")
            if "output_size" in result.metadata:
                details.append(f"Size: {format_file_size(result.metadata['output_size'])}")
            if "compression_ratio" in result.metadata:
                details.append(f"Ratio: {result.metadata['compression_ratio']:.1%}")
            if result.warnings:
                details.append(f"Warnings: {'; '.join(result.warnings)}")
            self._details.configure(text="\n".join(details))
        else:
            self._status.configure(text="Failed", text_color="#DC2626")
            self._details.configure(text=result.error_message or "Unknown error")

    def show_bulk_result(self, result: BulkResult) -> None:
        # Switch to scrollable log view
        self._details.pack_forget()
        self._log.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        if result.failed == 0:
            color = "#16A34A"
            status = f"Done: {result.succeeded}/{result.total} succeeded"
        else:
            color = "#D97706"
            status = f"Done: {result.succeeded} OK, {result.failed} failed"
            if result.skipped:
                status += f", {result.skipped} skipped"
        self._status.configure(text=status, text_color=color)

        # Build detailed log
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")

        lines = []
        for r in result.results:
            name = r.input_path.name if r.input_path else "?"
            if r.success:
                if r.warnings:
                    lines.append(f"  OK  {name} (warning: {'; '.join(r.warnings)})")
                # Don't list every success — only failures, warnings, skips
                elif r.metadata.get("dry_run"):
                    out_name = r.output_path.name if r.output_path else "?"
                    lines.append(f"  OK  {name} -> {out_name} (dry run)")
            else:
                reason = r.error_message or "Unknown error"
                lines.append(f"FAIL  {name}: {reason}")

        if not lines:
            if result.succeeded > 0:
                lines.append(f"All {result.succeeded} file(s) processed successfully.")
        else:
            # Put failures first
            failures = [l for l in lines if l.startswith("FAIL")]
            others = [l for l in lines if not l.startswith("FAIL")]
            lines = failures + others

        self._log.insert("1.0", "\n".join(lines))
        self._log.configure(state="disabled")

    def clear(self) -> None:
        self._status.configure(text="")
        self._details.configure(text="")
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")
        self._log.pack_forget()
        self._details.pack(fill="x", padx=5, pady=(0, 5))
