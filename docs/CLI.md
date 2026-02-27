# Image Optimizer — CLI Documentation

Complete reference for all command line operations. Image Optimizer uses Python's Click framework, so every command supports `--help` for detailed usage.

```bash
python -m mediamanager --help
```

---

## Table of Contents

- [Getting Started](#getting-started)
- [convert](#convert)
- [resize](#resize)
- [compress](#compress)
- [thumbnail](#thumbnail)
- [metadata](#metadata)
  - [metadata read](#metadata-read)
  - [metadata strip](#metadata-strip)
  - [metadata write](#metadata-write)
- [favicon](#favicon)
- [bulk](#bulk)
  - [bulk convert](#bulk-convert)
  - [bulk rename](#bulk-rename)
- [Supported Formats](#supported-formats)
- [Exit Codes](#exit-codes)
- [Tips and Workflows](#tips-and-workflows)

---

## Getting Started

```bash
# Install
pip install -e .

# Launch the GUI
python -m mediamanager --gui

# Show version
python -m mediamanager --version

# List commands
python -m mediamanager --help
```

If installed via pip, you can also use the `mediamanager` entry point directly:

```bash
mediamanager convert photo.jpg photo.webp -f webp
```

> **Metadata profiles** (save/load reusable metadata presets) are available in the GUI only. Use the Profiles tab to manage them, then load profiles from the dropdown in the Process, Metadata, or Bulk tabs.

---

## convert

Convert an image to a different format.

```
python -m mediamanager convert INPUT OUTPUT -f FORMAT [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `INPUT` | Path to the source image |
| `OUTPUT` | Path for the converted output |

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `-f`, `--format` | string | Target format: `jpg`, `png`, `webp`, `avif` (required) |
| `-q`, `--quality` | integer | Output quality (1-100 for JPEG/WebP, 0-9 for PNG) |
| `--lossless` | flag | Use lossless compression (WebP and AVIF only) |
| `--overwrite` | flag | Overwrite if output file already exists |
| `--skip` | flag | Silently skip if output file already exists |
| `--no-metadata` | flag | Do not preserve EXIF metadata in output |

**Examples:**

```bash
# JPEG to WebP
python -m mediamanager convert photo.jpg photo.webp -f webp

# PNG to JPEG at quality 90
python -m mediamanager convert screenshot.png screenshot.jpg -f jpg -q 90

# Lossless AVIF
python -m mediamanager convert logo.png logo.avif -f avif --lossless

# Convert without metadata
python -m mediamanager convert photo.jpg clean.png -f png --no-metadata
```

**Notes:**
- RGBA images converted to JPEG get a white background (JPEG has no transparency)
- Animated images are reduced to the first frame
- Extension mismatch between format and output path is auto-corrected

---

## resize

Resize an image using different modes.

```
python -m mediamanager resize INPUT OUTPUT [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-W`, `--width` | integer | — | Target width in pixels |
| `-H`, `--height` | integer | — | Target height in pixels |
| `-p`, `--percentage` | float | — | Scale by percentage (e.g. `50` for half size) |
| `--mode` | choice | `fit` | Resize mode: `fit`, `exact`, `fill`, `percentage` |
| `-f`, `--format` | string | same as input | Output format |
| `-q`, `--quality` | integer | — | Output quality |
| `--overwrite` | flag | — | Overwrite existing output |

**Resize Modes:**

| Mode | Behavior |
|------|----------|
| `fit` | Scale to fit within the given dimensions, preserving aspect ratio. Set only width or height to auto-calculate the other. |
| `exact` | Stretch to exact dimensions. May distort the image if aspect ratio differs. |
| `fill` | Scale up to cover the dimensions, then center-crop to the exact size. |
| `percentage` | Scale by a percentage value. Requires `-p`. |

**Examples:**

```bash
# Fit within 800px wide (height auto-calculated)
python -m mediamanager resize photo.jpg resized.jpg -W 800

# Exact dimensions
python -m mediamanager resize photo.jpg exact.jpg -W 1920 -H 1080 --mode exact

# Fill and crop to square
python -m mediamanager resize photo.jpg square.jpg -W 500 -H 500 --mode fill

# Scale to 25%
python -m mediamanager resize photo.jpg quarter.jpg -p 25 --mode percentage
```

---

## compress

Compress or optimize an image.

```
python -m mediamanager compress INPUT OUTPUT [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `-q`, `--quality` | integer | Output quality |
| `--lossless` | flag | Lossless compression |
| `-f`, `--format` | string | Output format (default: same as input) |
| `--max-size` | integer | Target maximum file size in KB |
| `--overwrite` | flag | Overwrite existing output |

**Examples:**

```bash
# Reduce JPEG quality
python -m mediamanager compress photo.jpg optimized.jpg -q 75

# Compress to under 500KB (binary search for optimal quality)
python -m mediamanager compress photo.jpg small.jpg --max-size 500

# Lossless WebP compression
python -m mediamanager compress photo.png optimized.webp -f webp --lossless
```

---

## thumbnail

Generate a thumbnail image.

```
python -m mediamanager thumbnail INPUT OUTPUT [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-s`, `--size` | string | `medium` | Preset name or pixel size |
| `-f`, `--format` | string | same as input | Output format |
| `-q`, `--quality` | integer | — | Output quality |
| `--square` | flag | — | Center-crop to square before generating thumbnail |
| `--overwrite` | flag | — | Overwrite existing output |

**Size Presets:**

| Preset | Dimensions |
|--------|-----------|
| `small` | 64 x 64 |
| `medium` | 150 x 150 |
| `large` | 300 x 300 |
| `xlarge` | 600 x 600 |

Pass an integer instead of a preset name for custom square sizes.

**Examples:**

```bash
python -m mediamanager thumbnail photo.jpg thumb_sm.jpg -s small
python -m mediamanager thumbnail photo.jpg thumb_200.jpg -s 200
python -m mediamanager thumbnail photo.jpg thumb_sq.jpg -s large --square
```

**Note:** Thumbnails never upscale. If the source is smaller than the requested size, the output will match the source dimensions.

---

## metadata

Read, write, or strip EXIF metadata. This is a command group with subcommands.

### metadata read

```
python -m mediamanager metadata read INPUT [--json]
```

Displays image metadata including format, dimensions, file size, and EXIF tags.

```bash
python -m mediamanager metadata read photo.jpg
python -m mediamanager metadata read photo.jpg --json
```

### metadata strip

```
python -m mediamanager metadata strip INPUT [OUTPUT] [OPTIONS]
```

Remove all EXIF metadata from an image.

| Option | Description |
|--------|-------------|
| `--in-place` | Modify the file in-place (no output path needed) |
| `--overwrite` | Overwrite existing output |

```bash
python -m mediamanager metadata strip photo.jpg clean.jpg
python -m mediamanager metadata strip photo.jpg --in-place
```

For JPEG files modified in-place, piexif performs a lossless strip without re-encoding.

### metadata write

```
python -m mediamanager metadata write INPUT OUTPUT [OPTIONS]
```

Write custom EXIF fields. Only JPEG and WebP support EXIF writing.

| Option | Description |
|--------|-------------|
| `--artist` | Artist name |
| `--copyright` | Copyright notice |
| `--description` | Image description |
| `--software` | Software used |
| `--datetime` | Date/time string |
| `--comment` | User comment |
| `--overwrite` | Overwrite existing output |

```bash
python -m mediamanager metadata write photo.jpg tagged.jpg \
  --artist "Jane Doe" \
  --copyright "2024 Jane Doe" \
  --description "Sunset at the beach"
```

---

## favicon

Generate a multi-size ICO favicon from any image.

```
python -m mediamanager favicon INPUT OUTPUT [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--sizes` | string | `16,32,48,64` | Comma-separated icon sizes |
| `--overwrite` | flag | — | Overwrite existing output |

The input image is center-cropped to square if it isn't already, then each size layer is generated and packed into a single `.ico` file.

```bash
python -m mediamanager favicon logo.png favicon.ico
python -m mediamanager favicon logo.png favicon.ico --sizes 16,32,48,64,128,256
```

---

## bulk

Bulk operations on entire directories. This is a command group with subcommands.

### bulk convert

Convert all images in a directory.

```
python -m mediamanager bulk convert INPUT_DIR OUTPUT_DIR -f FORMAT [OPTIONS]
```

| Option | Type | Description |
|--------|------|-------------|
| `-f`, `--format` | string | Target format (required) |
| `-r`, `--recursive` | flag | Process subdirectories |
| `--source-formats` | string | Only convert these formats (comma-separated, e.g. `png,bmp`) |
| `-q`, `--quality` | integer | Output quality |
| `--lossless` | flag | Lossless compression |
| `--overwrite` | flag | Overwrite existing output files |
| `--skip` | flag | Skip existing output files |
| `--no-metadata` | flag | Do not preserve metadata |

When `--recursive` is used, the directory structure is mirrored in the output folder.

```bash
# Convert all images to WebP
python -m mediamanager bulk convert ./photos ./webp_output -f webp

# Recursive, only PNGs
python -m mediamanager bulk convert ./assets ./converted -f jpg -r --source-formats png

# High quality with metadata stripped
python -m mediamanager bulk convert ./raw ./processed -f webp -q 95 --no-metadata
```

### bulk rename

Rename image files using pattern tokens.

```
python -m mediamanager bulk rename INPUT_DIR --pattern PATTERN [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--pattern` | string | — | Rename pattern (required) |
| `-r`, `--recursive` | flag | — | Process subdirectories |
| `--dry-run` | flag | — | Preview renames without making changes |
| `--start` | integer | `1` | Starting number for `{n}` token |
| `--overwrite` | flag | — | Overwrite existing files |

**Pattern Tokens:**

| Token | Description | Example |
|-------|-------------|---------|
| `{name}` | Original filename without extension | `photo_001` |
| `{ext}` | Original file extension | `jpg` |
| `{n}` | Sequential number | `1`, `2`, `3` |
| `{n:03d}` | Zero-padded number | `001`, `002`, `003` |
| `{date}` | File modification date | `20240315` |
| `{w}` | Image width in pixels | `1920` |
| `{h}` | Image height in pixels | `1080` |
| `{format}` | Detected image format | `jpeg` |

Rename uses a two-phase process to prevent conflicts (e.g. swapping A and B).

```bash
# Sequential numbering
python -m mediamanager bulk rename ./photos --pattern "photo_{n:03d}.{ext}"

# Preview first, then commit
python -m mediamanager bulk rename ./photos --pattern "img_{n}.{ext}" --dry-run
python -m mediamanager bulk rename ./photos --pattern "img_{n}.{ext}"

# Include dimensions in filename
python -m mediamanager bulk rename ./photos --pattern "{name}_{w}x{h}.{ext}"
```

---

## Supported Formats

| Format | Extensions | Read | Write | EXIF Write |
|--------|-----------|------|-------|------------|
| JPEG | `.jpg`, `.jpeg` | Yes | Yes | Yes |
| PNG | `.png` | Yes | Yes | No |
| WebP | `.webp` | Yes | Yes | Yes |
| AVIF | `.avif` | Yes | Yes | No |
| BMP | `.bmp` | Yes | No | No |
| TIFF | `.tif`, `.tiff` | Yes | No | No |
| GIF | `.gif` | Yes | No | No |
| ICO | `.ico` | No | Yes | No |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (invalid input, failed operation) |
| 2 | Invalid arguments (Click usage error) |
| 4 | GUI unavailable (missing customtkinter) |

---

## Tips and Workflows

**Web optimization pipeline:**
```bash
# Convert all PNGs to WebP at quality 80, recursively
python -m mediamanager bulk convert ./src/images ./dist/images -f webp -q 80 -r
```

**Generate responsive thumbnails:**
```bash
# Use the GUI Bulk > Thumbnail mode with sizes 150, 300, 600
# Or script it with the single-file command:
for img in ./photos/*.jpg; do
  python -m mediamanager thumbnail "$img" "./thumbs/sm_$(basename $img)" -s small
  python -m mediamanager thumbnail "$img" "./thumbs/md_$(basename $img)" -s medium
  python -m mediamanager thumbnail "$img" "./thumbs/lg_$(basename $img)" -s large
done
```

**Clean metadata before publishing:**
```bash
python -m mediamanager bulk convert ./photos ./clean -f jpg --no-metadata
```

**Batch rename for consistency:**
```bash
# Preview first
python -m mediamanager bulk rename ./uploads --pattern "product_{n:04d}.{ext}" --dry-run
# If it looks right, run for real
python -m mediamanager bulk rename ./uploads --pattern "product_{n:04d}.{ext}"
```
