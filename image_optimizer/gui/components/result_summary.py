"""Post-operation results display."""

from __future__ import annotations

import customtkinter as ctk

from image_optimizer.core.types import OperationResult, BulkResult
from image_optimizer.core.utils import format_file_size
from image_optimizer.gui.theme import COLORS, FONTS


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
            self._status.configure(text="Success", text_color=COLORS["success"])
            details = []
            if result.output_path:
                details.append(f"Saved: {result.output_path}")
            # Show input vs output size with savings
            input_size = result.metadata.get("input_size")
            output_size = result.metadata.get("output_size")
            if input_size and output_size:
                savings = 1.0 - (output_size / input_size) if input_size > 0 else 0
                details.append(
                    f"Size: {format_file_size(input_size)} → {format_file_size(output_size)} "
                    f"({savings:+.1%})"
                )
            elif output_size:
                details.append(f"Size: {format_file_size(output_size)}")
            if "compression_ratio" in result.metadata:
                details.append(f"Ratio: {result.metadata['compression_ratio']:.1%}")
            if result.warnings:
                details.append(f"Warnings: {'; '.join(result.warnings)}")
            self._details.configure(text="\n".join(details))
        else:
            self._status.configure(text="Failed", text_color=COLORS["error"])
            self._details.configure(text=result.error_message or "Unknown error")

    def show_bulk_result(self, result: BulkResult) -> None:
        # Switch to scrollable log view
        self._details.pack_forget()
        self._log.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        if result.failed == 0:
            color = COLORS["success"]
            status = f"Done: {result.succeeded}/{result.total} succeeded"
        else:
            color = COLORS["warning"]
            status = f"Done: {result.succeeded} OK, {result.failed} failed"
            if result.skipped:
                status += f", {result.skipped} skipped"
        self._status.configure(text=status, text_color=color)

        # Build detailed log
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")

        failures = []
        others = []
        for r in result.results:
            name = r.input_path.name if r.input_path else "?"
            if r.success:
                if r.metadata.get("dry_run"):
                    out_name = r.output_path.name if r.output_path else "?"
                    others.append(f"  OK  {name} -> {out_name} (dry run)")
                elif r.warnings:
                    others.append(f"  OK  {name} (warning: {'; '.join(r.warnings)})")
                else:
                    # Show all processed files with size info
                    out_size = r.metadata.get("output_size")
                    size_info = f" ({format_file_size(out_size)})" if out_size else ""
                    others.append(f"  OK  {name}{size_info}")
            else:
                reason = r.error_message or "Unknown error"
                failures.append(f"FAIL  {name}: {reason}")

        # Failures first, then successes
        lines = failures + others
        if not lines and result.succeeded > 0:
            lines.append(f"All {result.succeeded} file(s) processed successfully.")

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
