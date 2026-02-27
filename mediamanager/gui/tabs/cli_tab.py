"""CLI Help tab — reference guide for using Image Optimizer from the command line."""

from __future__ import annotations

import customtkinter as ctk

from mediamanager.gui.theme import FONTS

_CLI_REFERENCE = """\
IMAGE OPTIMIZER — CLI REFERENCE
================================

Image Optimizer can be used entirely from the command line using Python.
All operations available in the GUI are also available as CLI commands.


GETTING STARTED
---------------

  # Show help and available commands
  python -m mediamanager --help

  # Launch the GUI from CLI
  python -m mediamanager --gui

  # Show version
  python -m mediamanager --version


CONVERT
-------
Convert an image to a different format.

  python -m mediamanager convert INPUT OUTPUT -f FORMAT

  Options:
    -f, --format       Target format: jpg, png, webp, avif (required)
    -q, --quality      Output quality (1-100 for JPEG/WebP, 0-9 for PNG)
    --lossless         Lossless compression (WebP/AVIF only)
    --overwrite        Overwrite if output file exists
    --skip             Skip if output file exists
    --no-metadata      Do not preserve EXIF metadata

  Examples:
    python -m mediamanager convert photo.jpg photo.webp -f webp
    python -m mediamanager convert photo.png photo.jpg -f jpg -q 90
    python -m mediamanager convert logo.png logo.avif -f avif --lossless


RESIZE
------
Resize an image with multiple modes.

  python -m mediamanager resize INPUT OUTPUT [OPTIONS]

  Options:
    -W, --width        Target width in pixels
    -H, --height       Target height in pixels
    -p, --percentage   Resize by percentage (e.g. 50 for 50%)
    --mode             Resize mode: fit, exact, fill, percentage (default: fit)
    -f, --format       Output format (default: same as input)
    -q, --quality      Output quality
    --overwrite        Overwrite existing output

  Modes:
    fit          Resize to fit within dimensions, keeping aspect ratio
    exact        Stretch to exact dimensions (may distort)
    fill         Resize and crop to fill exact dimensions
    percentage   Scale by percentage value

  Examples:
    python -m mediamanager resize photo.jpg small.jpg -W 800
    python -m mediamanager resize photo.jpg half.jpg -p 50 --mode percentage
    python -m mediamanager resize photo.jpg cropped.jpg -W 400 -H 400 --mode fill


COMPRESS
--------
Compress or optimize an image file.

  python -m mediamanager compress INPUT OUTPUT [OPTIONS]

  Options:
    -q, --quality      Output quality
    --lossless         Lossless compression
    -f, --format       Output format
    --max-size         Target maximum file size in KB
    --overwrite        Overwrite existing output

  Examples:
    python -m mediamanager compress photo.jpg optimized.jpg -q 75
    python -m mediamanager compress photo.jpg small.jpg --max-size 500
    python -m mediamanager compress photo.png optimized.webp -f webp --lossless


THUMBNAIL
---------
Generate a thumbnail from an image.

  python -m mediamanager thumbnail INPUT OUTPUT [OPTIONS]

  Options:
    -s, --size         Preset (small/medium/large/xlarge) or pixel size (default: medium)
    -f, --format       Output format
    -q, --quality      Output quality
    --square           Crop to square before thumbnailing
    --overwrite        Overwrite existing output

  Presets:
    small    =  64 x 64
    medium   = 150 x 150
    large    = 300 x 300
    xlarge   = 600 x 600

  Examples:
    python -m mediamanager thumbnail photo.jpg thumb.jpg -s small
    python -m mediamanager thumbnail photo.jpg thumb.jpg -s 200
    python -m mediamanager thumbnail photo.jpg thumb.jpg -s medium --square


METADATA
--------
Read, write, or strip image EXIF metadata.

  # Read metadata
  python -m mediamanager metadata read INPUT
  python -m mediamanager metadata read INPUT --json

  # Strip all metadata
  python -m mediamanager metadata strip INPUT OUTPUT
  python -m mediamanager metadata strip INPUT --in-place

  # Write custom EXIF fields
  python -m mediamanager metadata write INPUT OUTPUT [OPTIONS]

  Write options:
    --artist           Artist name
    --copyright        Copyright notice
    --description      Image description
    --title            Image title
    --keywords         Keywords (semicolon-separated)
    --subject          Subject description
    --software         Software used
    --comment          User comment (supports Unicode)
    --make             Camera manufacturer
    --model            Camera model
    --lens-make        Lens manufacturer
    --lens-model       Lens model
    --datetime         Date/time (YYYY:MM:DD HH:MM:SS)
    --datetime-original  Original capture date
    --datetime-digitized Digitized date
    --orientation      Image orientation (1-8)
    --iso              ISO speed (1-65535)
    --gps-latitude     GPS latitude in decimal degrees
    --gps-longitude    GPS longitude in decimal degrees
    --overwrite        Overwrite existing output

  Examples:
    python -m mediamanager metadata read photo.jpg
    python -m mediamanager metadata read photo.jpg --json
    python -m mediamanager metadata strip photo.jpg clean.jpg
    python -m mediamanager metadata strip photo.jpg --in-place
    python -m mediamanager metadata write photo.jpg out.jpg --artist "John" --copyright "2024"
    python -m mediamanager metadata write photo.jpg out.jpg --make "Canon" --model "EOS R5"
    python -m mediamanager metadata write photo.jpg out.jpg --gps-latitude 40.7128 --gps-longitude -74.0060


FAVICON
-------
Generate a multi-size ICO favicon from any image.

  python -m mediamanager favicon INPUT OUTPUT [OPTIONS]

  Options:
    --sizes            Comma-separated sizes (default: 16,32,48,64)
    --overwrite        Overwrite existing output

  Examples:
    python -m mediamanager favicon logo.png favicon.ico
    python -m mediamanager favicon logo.png favicon.ico --sizes 16,32,48,64,128,256


BULK CONVERT
------------
Convert all images in a directory.

  python -m mediamanager bulk convert INPUT_DIR OUTPUT_DIR -f FORMAT [OPTIONS]

  Options:
    -f, --format           Target format (required)
    -r, --recursive        Process subdirectories
    --source-formats       Only convert these formats (comma-separated)
    -q, --quality          Output quality
    --lossless             Lossless compression
    --overwrite            Overwrite existing output
    --skip                 Skip existing output files
    --no-metadata          Do not preserve metadata

  Examples:
    python -m mediamanager bulk convert ./photos ./webp_photos -f webp
    python -m mediamanager bulk convert ./imgs ./output -f png -r
    python -m mediamanager bulk convert ./raw ./jpg -f jpg --source-formats png,bmp -q 85


BULK RENAME
-----------
Rename image files using a pattern with tokens.

  python -m mediamanager bulk rename INPUT_DIR --pattern PATTERN [OPTIONS]

  Options:
    --pattern              Rename pattern (required)
    -r, --recursive        Process subdirectories
    --dry-run              Preview renames without making changes
    --start                Starting number for {n} token (default: 1)
    --overwrite            Overwrite existing files

  Pattern tokens:
    {name}       Original filename (without extension)
    {ext}        Original extension
    {n}          Sequential number
    {n:03d}      Zero-padded number (001, 002, ...)
    {date}       File modification date (YYYYMMDD)
    {w}          Image width in pixels
    {h}          Image height in pixels
    {format}     Image format (jpeg, png, etc.)

  Examples:
    python -m mediamanager bulk rename ./photos --pattern "photo_{n:03d}.{ext}"
    python -m mediamanager bulk rename ./photos --pattern "{date}_{name}.{ext}" --dry-run
    python -m mediamanager bulk rename ./photos --pattern "img_{n:04d}.{ext}" --start 100


SUPPORTED FORMATS
-----------------
  JPEG (.jpg, .jpeg)     Read/Write
  PNG  (.png)            Read/Write
  WebP (.webp)           Read/Write
  AVIF (.avif)           Read/Write (requires pillow-avif-plugin)
  BMP  (.bmp)            Read only
  TIFF (.tif, .tiff)     Read only
  GIF  (.gif)            Read only (first frame)
  ICO  (.ico)            Write only (favicon)


TIPS
----
  - Use --overwrite or --skip to handle existing files in scripts
  - Combine bulk convert with --source-formats to convert only specific types
  - Use --dry-run with bulk rename to preview changes before committing
  - Quality 80-85 for JPEG/WebP gives a good balance of size and quality
  - For lossless compression, use WebP with --lossless flag
  - EXIF metadata writing works with JPEG, PNG, and WebP formats
"""


class CLITab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            header, text="CLI Reference",
            font=FONTS["heading"],
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            header,
            text="Use Image Optimizer from the terminal with Python",
            font=FONTS["small"], text_color="gray",
        ).pack(side="left", padx=10)

        # Search bar
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(search_frame, text="Search:", width=60, anchor="w").pack(side="left", padx=5)
        self._search_var = ctk.StringVar()
        self._search_entry = ctk.CTkEntry(
            search_frame, textvariable=self._search_var,
            placeholder_text="Type to filter (e.g. convert, resize, bulk...)",
        )
        self._search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self._search_var.trace_add("write", self._on_search)

        self._clear_btn = ctk.CTkButton(
            search_frame, text="Clear", width=60,
            command=self._clear_search,
        )
        self._clear_btn.pack(side="left", padx=5)

        # Textbox with monospace font for the CLI reference
        self._textbox = ctk.CTkTextbox(
            self, font=FONTS["mono"], wrap="none",
            state="normal",
        )
        self._textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._textbox.insert("1.0", _CLI_REFERENCE)
        self._textbox.configure(state="disabled")

        # Store original text for search filtering
        self._full_text = _CLI_REFERENCE

    def _on_search(self, *_args):
        query = self._search_var.get().strip().lower()
        if not query:
            self._show_full_text()
            return

        # Filter sections that contain the query
        sections = self._full_text.split("\n\n\n")
        matches = []
        for section in sections:
            if query in section.lower():
                matches.append(section)

        if matches:
            filtered = "\n\n\n".join(matches)
        else:
            filtered = f"No results for '{query}'.\n\nTry: convert, resize, compress, thumbnail, metadata, favicon, bulk"

        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.insert("1.0", filtered)
        self._textbox.configure(state="disabled")

    def _show_full_text(self):
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.insert("1.0", self._full_text)
        self._textbox.configure(state="disabled")

    def _clear_search(self):
        self._search_var.set("")
        self._show_full_text()
