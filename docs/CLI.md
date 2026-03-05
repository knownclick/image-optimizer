# Image Optimizer — CLI Documentation

Complete reference for all command line operations. Image Optimizer uses Python's Click framework, so every command supports `--help` for detailed usage.

```bash
python -m image_optimizer --help
```

---

## Table of Contents

- [Getting Started](#getting-started)
- [convert](#convert)
- [resize](#resize)
- [crop](#crop)
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
python -m image_optimizer --gui

# Show version
python -m image_optimizer --version

# List commands
python -m image_optimizer --help
```

If installed via pip, you can also use the `image-optimizer` entry point directly:

```bash
image-optimizer convert photo.jpg photo.webp -f webp
```

> **Metadata profiles** (save/load reusable metadata presets) are available in the GUI only. Use the Profiles tab to manage them, then load profiles from the dropdown in the Process, Metadata, or Bulk tabs.

---

## convert

Convert an image to a different format.

```
python -m image_optimizer convert INPUT OUTPUT -f FORMAT [OPTIONS]
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
python -m image_optimizer convert photo.jpg photo.webp -f webp

# PNG to JPEG at quality 90
python -m image_optimizer convert screenshot.png screenshot.jpg -f jpg -q 90

# Lossless AVIF
python -m image_optimizer convert logo.png logo.avif -f avif --lossless

# Convert without metadata
python -m image_optimizer convert photo.jpg clean.png -f png --no-metadata
```

**Notes:**
- RGBA images converted to JPEG get a white background (JPEG has no transparency)
- Animated images are reduced to the first frame
- Extension mismatch between format and output path is auto-corrected

---

## resize

Resize an image using different modes.

```
python -m image_optimizer resize INPUT OUTPUT [OPTIONS]
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
python -m image_optimizer resize photo.jpg resized.jpg -W 800

# Exact dimensions
python -m image_optimizer resize photo.jpg exact.jpg -W 1920 -H 1080 --mode exact

# Fill and crop to square
python -m image_optimizer resize photo.jpg square.jpg -W 500 -H 500 --mode fill

# Scale to 25%
python -m image_optimizer resize photo.jpg quarter.jpg -p 25 --mode percentage
```

---

## crop

Crop an image by aspect ratio, center crop, or coordinates.

```
python -m image_optimizer crop INPUT OUTPUT [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-a`, `--aspect-ratio` | string | — | Aspect ratio preset: `1:1`, `4:3`, `3:2`, `16:9`, `9:16`, `3:4`, `2:3` |
| `--anchor` | string | `center` | Anchor position: `center`, `top-left`, `top-right`, `bottom-left`, `bottom-right` |
| `-W`, `--width` | integer | — | Crop width in pixels (for center/coordinate crop) |
| `-H`, `--height` | integer | — | Crop height in pixels (for center/coordinate crop) |
| `-x` | integer | — | Crop X coordinate (top-left corner) |
| `-y` | integer | — | Crop Y coordinate (top-left corner) |
| `-f`, `--format` | string | same as input | Output format |
| `-q`, `--quality` | integer | — | Output quality |
| `--overwrite` | flag | — | Overwrite existing output |

**Crop Modes:**

| Mode | Usage | Description |
|------|-------|-------------|
| Aspect ratio | `-a 16:9` | Crop to a preset aspect ratio from the anchor position |
| Center crop | `-W 400 -H 300` | Crop a WxH region from the center of the image |
| Coordinates | `-W 400 -H 300 -x 100 -y 50` | Crop a WxH region starting at (x, y) |

**Examples:**

```bash
# Crop to square (1:1) from center
python -m image_optimizer crop photo.jpg square.jpg -a 1:1

# Crop to 16:9 from top-left corner
python -m image_optimizer crop photo.jpg wide.jpg -a 16:9 --anchor top-left

# Center crop 400x400 pixels
python -m image_optimizer crop photo.jpg center.jpg -W 400 -H 400

# Coordinate-based crop: 200x200 starting at (100, 50)
python -m image_optimizer crop photo.jpg region.jpg -W 200 -H 200 -x 100 -y 50
```

---

## compress

Compress or optimize an image.

```
python -m image_optimizer compress INPUT OUTPUT [OPTIONS]
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
python -m image_optimizer compress photo.jpg optimized.jpg -q 75

# Compress to under 500KB (binary search for optimal quality)
python -m image_optimizer compress photo.jpg small.jpg --max-size 500

# Lossless WebP compression
python -m image_optimizer compress photo.png optimized.webp -f webp --lossless
```

---

## thumbnail

Generate a thumbnail image.

```
python -m image_optimizer thumbnail INPUT OUTPUT [OPTIONS]
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
python -m image_optimizer thumbnail photo.jpg thumb_sm.jpg -s small
python -m image_optimizer thumbnail photo.jpg thumb_200.jpg -s 200
python -m image_optimizer thumbnail photo.jpg thumb_sq.jpg -s large --square
```

**Note:** Thumbnails never upscale. If the source is smaller than the requested size, the output will match the source dimensions.

---

## metadata

Read, write, or strip EXIF metadata. This is a command group with subcommands.

### metadata read

```
python -m image_optimizer metadata read INPUT [--json]
```

Displays image metadata including format, dimensions, file size, and EXIF tags.

```bash
python -m image_optimizer metadata read photo.jpg
python -m image_optimizer metadata read photo.jpg --json
```

### metadata strip

```
python -m image_optimizer metadata strip INPUT [OUTPUT] [OPTIONS]
```

Remove all EXIF metadata from an image.

| Option | Description |
|--------|-------------|
| `--in-place` | Modify the file in-place (no output path needed) |
| `--overwrite` | Overwrite existing output |

```bash
python -m image_optimizer metadata strip photo.jpg clean.jpg
python -m image_optimizer metadata strip photo.jpg --in-place
```

For JPEG files modified in-place, piexif performs a lossless strip without re-encoding.

### metadata write

```
python -m image_optimizer metadata write INPUT OUTPUT [OPTIONS]
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
python -m image_optimizer metadata write photo.jpg tagged.jpg \
  --artist "Jane Doe" \
  --copyright "2024 Jane Doe" \
  --description "Sunset at the beach"
```

---

## favicon

Generate a multi-size ICO favicon from any image.

```
python -m image_optimizer favicon INPUT OUTPUT [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--sizes` | string | `16,32,48,64` | Comma-separated icon sizes |
| `--overwrite` | flag | — | Overwrite existing output |

The input image is center-cropped to square if it isn't already, then each size layer is generated and packed into a single `.ico` file.

```bash
python -m image_optimizer favicon logo.png favicon.ico
python -m image_optimizer favicon logo.png favicon.ico --sizes 16,32,48,64,128,256
```

---

## bulk

Bulk operations on entire directories. This is a command group with subcommands.

### bulk convert

Convert all images in a directory.

```
python -m image_optimizer bulk convert INPUT_DIR OUTPUT_DIR -f FORMAT [OPTIONS]
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
python -m image_optimizer bulk convert ./photos ./webp_output -f webp

# Recursive, only PNGs
python -m image_optimizer bulk convert ./assets ./converted -f jpg -r --source-formats png

# High quality with metadata stripped
python -m image_optimizer bulk convert ./raw ./processed -f webp -q 95 --no-metadata
```

### bulk rename

Rename image files using pattern tokens.

```
python -m image_optimizer bulk rename INPUT_DIR --pattern PATTERN [OPTIONS]
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
python -m image_optimizer bulk rename ./photos --pattern "photo_{n:03d}.{ext}"

# Preview first, then commit
python -m image_optimizer bulk rename ./photos --pattern "img_{n}.{ext}" --dry-run
python -m image_optimizer bulk rename ./photos --pattern "img_{n}.{ext}"

# Include dimensions in filename
python -m image_optimizer bulk rename ./photos --pattern "{name}_{w}x{h}.{ext}"
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
python -m image_optimizer bulk convert ./src/images ./dist/images -f webp -q 80 -r
```

**Generate responsive thumbnails:**
```bash
# Use the GUI Bulk > Thumbnail mode with sizes 150, 300, 600
# Or script it with the single-file command:
for img in ./photos/*.jpg; do
  python -m image_optimizer thumbnail "$img" "./thumbs/sm_$(basename $img)" -s small
  python -m image_optimizer thumbnail "$img" "./thumbs/md_$(basename $img)" -s medium
  python -m image_optimizer thumbnail "$img" "./thumbs/lg_$(basename $img)" -s large
done
```

**Crop all images to 16:9 for social media:**
```bash
# Single file
python -m image_optimizer crop photo.jpg social.jpg -a 16:9

# Bulk (use the GUI Bulk tab with crop enabled)
```

**Clean metadata before publishing:**
```bash
python -m image_optimizer bulk convert ./photos ./clean -f jpg --no-metadata
```

**Batch rename for consistency:**
```bash
# Preview first
python -m image_optimizer bulk rename ./uploads --pattern "product_{n:04d}.{ext}" --dry-run
# If it looks right, run for real
python -m image_optimizer bulk rename ./uploads --pattern "product_{n:04d}.{ext}"
```
