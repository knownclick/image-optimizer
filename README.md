# Image Optimizer tool for Web Developers

A desktop image optimizer built for web developers who need to process images quickly. Handles format conversion, resizing, compression, thumbnail generation, metadata editing, and favicon creation — both through a graphical interface and a full-featured command line.

Created by **Hency Prajapati** at [Known Click Technologies](https://knownclick.com).

---

## Features

- **Format conversion** — JPEG, PNG, WebP, AVIF with quality control and lossless options
- **Resize** — Fit, exact, fill (crop), and percentage modes with auto-scaling
- **Compression** — Quality slider, lossless mode, target file size
- **Thumbnails** — Multiple preset sizes, custom dimensions, prefix/suffix naming, square crop
- **Metadata** — Read, write, and strip EXIF data (artist, copyright, description, etc.)
- **Metadata profiles** — Save and load reusable metadata presets (e.g., per-client or per-project)
- **Favicon** — Generate multi-size ICO files from any image
- **Bulk operations** — Process, rename, and thumbnail entire folders with progress tracking
- **Error reporting** — Per-file error logging during bulk operations with detailed results
- **Dark/light themes** — Toggle between dark and light mode in the GUI

## Supported Formats

| Format | Read | Write |
|--------|------|-------|
| JPEG (.jpg, .jpeg) | Yes | Yes |
| PNG (.png) | Yes | Yes |
| WebP (.webp) | Yes | Yes |
| AVIF (.avif) | Yes | Yes* |
| BMP (.bmp) | Yes | — |
| TIFF (.tif, .tiff) | Yes | — |
| GIF (.gif) | Yes (first frame) | — |
| ICO (.ico) | — | Yes (favicon) |

*AVIF requires `pillow-avif-plugin`.

---

## Installation

### Requirements

- Python 3.10 or later
- pip

### Install from source

```bash
git clone https://github.com/knownclick/image-optimizer.git
cd image-optimizer
pip install -e .
```

For AVIF support:

```bash
pip install pillow-avif-plugin
```

### Standalone binary

Pre-built binaries are available on the [Releases](https://github.com/knownclick/image-optimizer/releases) page. Download `ImageOptimizer` for your platform and run it directly — no Python installation needed.

---

## Usage

### GUI

Launch the graphical interface:

```bash
python -m mediamanager --gui
```

Or if using the standalone binary, just double-click `ImageOptimizer`.

The GUI has seven tabs:

| Tab | Purpose |
|-----|---------|
| **Process** | Convert, resize, compress, and write metadata for a single image |
| **Thumbnail** | Generate thumbnails at multiple sizes with naming options |
| **Metadata** | View, edit, or strip EXIF data |
| **Favicon** | Create multi-size ICO favicons |
| **Bulk** | Process, thumbnail, or rename entire folders |
| **Profiles** | Create, edit, and delete reusable metadata profiles |
| **CLI** | Built-in reference for command line usage |

The Process, Metadata, and Bulk tabs include a profile dropdown that loads saved metadata values into their fields.

### Command Line

Every operation available in the GUI also works from the terminal.

```bash
# Show all commands
python -m mediamanager --help

# Show help for a specific command
python -m mediamanager convert --help
```

#### Convert

```bash
python -m mediamanager convert photo.jpg photo.webp -f webp
python -m mediamanager convert photo.png photo.jpg -f jpg -q 90
python -m mediamanager convert logo.png logo.avif -f avif --lossless
```

#### Resize

```bash
# Fit within 800px width, auto height
python -m mediamanager resize photo.jpg small.jpg -W 800

# Scale to 50%
python -m mediamanager resize photo.jpg half.jpg -p 50 --mode percentage

# Crop to fill 400x400
python -m mediamanager resize photo.jpg square.jpg -W 400 -H 400 --mode fill
```

#### Compress

```bash
python -m mediamanager compress photo.jpg optimized.jpg -q 75
python -m mediamanager compress photo.jpg small.jpg --max-size 500
```

#### Thumbnail

```bash
python -m mediamanager thumbnail photo.jpg thumb.jpg -s small
python -m mediamanager thumbnail photo.jpg thumb.jpg -s 200
python -m mediamanager thumbnail photo.jpg thumb.jpg -s medium --square
```

#### Metadata

```bash
# Read
python -m mediamanager metadata read photo.jpg
python -m mediamanager metadata read photo.jpg --json

# Strip
python -m mediamanager metadata strip photo.jpg clean.jpg
python -m mediamanager metadata strip photo.jpg --in-place

# Write
python -m mediamanager metadata write photo.jpg out.jpg --artist "Hency" --copyright "2024"
```

#### Favicon

```bash
python -m mediamanager favicon logo.png favicon.ico
python -m mediamanager favicon logo.png favicon.ico --sizes 16,32,48,64,128,256
```

#### Bulk Convert

```bash
python -m mediamanager bulk convert ./photos ./webp_output -f webp
python -m mediamanager bulk convert ./imgs ./output -f png -r
python -m mediamanager bulk convert ./raw ./jpg -f jpg --source-formats png,bmp -q 85
```

#### Bulk Rename

```bash
python -m mediamanager bulk rename ./photos --pattern "photo_{n:03d}.{ext}"
python -m mediamanager bulk rename ./photos --pattern "{date}_{name}.{ext}" --dry-run
```

Rename pattern tokens: `{name}`, `{ext}`, `{n}`, `{n:03d}`, `{date}`, `{w}`, `{h}`, `{format}`.

---

## Building from Source

### Development setup

```bash
git clone https://github.com/knownclick/image-optimizer.git
cd image-optimizer
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

pip install -e ".[dev]"
```

### Run tests

```bash
pytest tests/ -v
```

### Build standalone binary

The included build script handles venv creation, dependency installation, and PyInstaller packaging automatically:

```bash
python build.py              # Folder distribution
python build.py --onefile    # Single executable
python build.py --clean      # Remove build artifacts
```

Or build manually:

```bash
pip install -r requirements-build.txt
pyinstaller --clean --noconfirm mediamanager_onefile.spec
```

The binary will be at `dist/ImageOptimizer`.

---

## Project Structure

```
mediamanager/
    __init__.py              # Version and metadata
    __main__.py              # Entry point
    cli/
        app.py               # Click command group
        commands/             # One file per CLI command
    core/
        bulk.py              # Bulk operations (convert, process, thumbnails, rename)
        compressor.py        # Compression with quality and size targets
        constants.py         # Format maps, limits, defaults
        converter.py         # Format conversion
        favicon.py           # ICO favicon generation
        image_io.py          # Safe image load/save with error handling
        metadata.py          # EXIF read/write/strip
        pipeline.py          # Fluent API for chaining operations
        resizer.py           # Resize with multiple modes
        thumbnail.py         # Thumbnail generation
        types.py             # Enums, dataclasses, error hierarchy
        utils.py             # File discovery, path utilities
        validation.py        # Input validation
    gui/
        app.py               # Main window with tabbed layout
        theme.py             # Colors, fonts, platform-specific settings
        field_defs.py        # Shared metadata field constants
        profiles.py          # Profile CRUD (JSON persistence)
        profiles/            # Saved profile JSON files
        tabs/                # One file per tab
        components/          # Reusable GUI widgets
        workers.py           # Threading for non-blocking operations
tests/                       # Pytest test suite
```

---

## License

Proprietary. Copyright Hency Prajapati / Known Click Technologies.
