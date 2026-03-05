# Image Optimizer - Project Report

**A Desktop Image Optimization Tool for Web Developers**

**Developed by:** Hency Prajapati
**Organization:** Known Click Technologies (knownclick.com)
**Technology:** Python 3.10+, Pillow, CustomTkinter, Click
**Version:** 1.0.0

---

## Table of Contents

| Sr. No. | Subject | Page No. |
|---------|---------|----------|
| 1 | Project Profile & Company Profile | |
| 2 | Introduction to Tools | |
| 3 | System Study (Requirement Analysis) | |
| 3.1 | Existing System | |
| 3.2 | Proposed System | |
| 3.3 | Scope of the Proposed System | |
| 3.4 | Aims and Objectives | |
| 3.5 | Feasibility Study | |
| 3.5.1 | Operational Feasibility | |
| 3.5.2 | Technical Feasibility | |
| 3.5.3 | Economic Feasibility | |
| 4 | System Analysis | |
| 4.1 | Requirements Specification (With System Modules) | |
| 4.2 | Use Case Diagram | |
| 4.3 | Activity Diagram | |
| 4.4 | Class Diagram / System Flowchart | |
| 4.5 | Data Flow Diagram | |
| 4.5.1 | Context Level DFD | |
| 4.5.2 | First Level DFD | |
| 4.5.3 | Second Level DFD | |
| 4.6 | ER Diagram | |
| 5 | System Design | |
| 5.1 | Data Dictionary | |
| 5.2 | Screen Layouts / UI Design | |
| 5.3 | Reports | |
| 6 | System Implementation | |
| 6.1 | Module Implementation | |
| 7 | System Testing | |
| 7.1 | Testing Strategies | |
| 7.2 | Test Cases | |
| 8 | Future Enhancement | |
| 9 | Bibliography/References | |
| 10 | Internal Guide's Report | |

---

## 1. Project Profile & Company Profile

### 1.1 Project Profile

| Field | Details |
|-------|---------|
| **Project Title** | Image Optimizer - A Desktop Image Optimization Tool for Web Developers |
| **Technology** | Python 3.10+ |
| **Libraries** | Pillow (image processing), Click (CLI framework), CustomTkinter (GUI toolkit), piexif (EXIF metadata) |
| **Platform** | Cross-platform (Windows, macOS, Linux) |
| **Type** | Desktop Application (GUI + CLI) |
| **Developer** | Hency Prajapati |
| **Organization** | Known Click Technologies |

### 1.2 Company Profile

**Known Click Technologies** is a technology company specializing in web development and digital solutions. The company focuses on building practical tools and services that streamline the workflow of web developers and digital professionals. Known Click Technologies is committed to delivering efficient, user-friendly software solutions that address real-world challenges in web development and digital media management.

**Website:** knownclick.com

---

## 2. Introduction to Tools

### 2.1 Python 3.10+

Python is a high-level, interpreted, general-purpose programming language known for its clear syntax and readability. Python 3.10 introduced structural pattern matching and improved error messages. It is widely used for scripting, automation, data science, web development, and desktop application development. Python's extensive standard library and third-party ecosystem make it an ideal choice for rapid application development.

### 2.2 Pillow (PIL Fork)

Pillow is the modern fork of the Python Imaging Library (PIL). It provides extensive file format support, efficient internal representation, and powerful image processing capabilities. Pillow supports reading and writing over 30 image formats including JPEG, PNG, WebP, AVIF, BMP, TIFF, and GIF. Key features include:

- Image resizing with multiple resampling filters (LANCZOS, BILINEAR, etc.)
- Image cropping, rotation, and transformation
- Color mode conversion (RGB, RGBA, CMYK, grayscale)
- EXIF metadata access
- Image compression and quality control
- Decompression bomb protection for security

### 2.3 CustomTkinter

CustomTkinter is a modern Python GUI library based on Tkinter. It provides a set of widgets with a contemporary look and feel, including built-in dark/light theme support. Unlike standard Tkinter, CustomTkinter offers:

- Modern flat design widgets (buttons, sliders, switches, dropdowns)
- Dark and light mode switching at runtime
- Consistent cross-platform appearance
- Scrollable frames and tabbed views
- High-DPI display support

### 2.4 Click

Click (Command Line Interface Creation Kit) is a Python package for creating command-line interfaces with minimal code. It provides:

- Decorators for defining commands and options
- Automatic help page generation
- Type validation for command arguments
- Nested command groups for organizing subcommands
- Colored terminal output support

### 2.5 piexif

piexif is a Python library for reading, writing, and stripping EXIF metadata in JPEG and TIFF files. It provides direct access to EXIF IFD (Image File Directory) structures and supports:

- Reading all standard EXIF tags
- Writing custom EXIF data (artist, copyright, GPS, camera info)
- Lossless EXIF stripping from JPEG files
- Support for Windows XP extended fields

### 2.6 PyInstaller

PyInstaller is used to package the Python application into standalone executables. It bundles the Python interpreter, all dependencies, and application code into a single distributable package that runs without requiring a Python installation on the target machine.

### 2.7 pytest

pytest is the testing framework used for the project's test suite. It provides:

- Simple test discovery and execution
- Fixtures for test setup and teardown
- Parameterized testing
- Detailed assertion introspection
- Plugin ecosystem (pytest-tmp-files for temporary file handling)

---

## 3. System Study (Requirement Analysis)

### 3.1 Existing System

Web developers currently face several challenges when optimizing images for websites:

1. **Multiple Tools Required:** Developers typically need separate tools for format conversion (e.g., ImageMagick), compression (e.g., TinyPNG web service), resizing (e.g., Photoshop/GIMP), metadata editing (e.g., ExifTool), and favicon generation (e.g., online favicon generators). This fragmented workflow wastes time and creates context-switching overhead.

2. **Online Dependency:** Many image optimization services are web-based (TinyPNG, Squoosh, CloudConvert), requiring internet connectivity and file uploads. This raises privacy concerns for client images and introduces upload/download delays for large files.

3. **No Batch Processing:** Most free tools process one image at a time. Developers working with large image sets (product catalogs, photo galleries) must manually repeat operations hundreds of times.

4. **Complex Command-Line Tools:** Tools like ImageMagick are powerful but have steep learning curves. Simple operations require memorizing complex syntax and flag combinations.

5. **Metadata Management Gap:** EXIF metadata operations (reading, writing, stripping) are typically handled by specialized tools (ExifTool) that are separate from image processing tools, creating further workflow fragmentation.

6. **No Profile/Preset System:** Developers working with multiple clients or projects must re-enter the same settings repeatedly. There is no way to save and reuse common configurations.

### 3.2 Proposed System

Image Optimizer is a unified desktop application that consolidates all common image optimization tasks into a single tool. It provides:

1. **Dual Interface:** Both a graphical user interface (GUI) for interactive use and a full-featured command-line interface (CLI) for scripting and automation. Every operation available in the GUI is also available from the command line.

2. **Seven Core Operations:**
   - **Format Conversion:** Convert between JPEG, PNG, WebP, and AVIF with quality control
   - **Resizing:** Four modes (Fit, Exact, Fill, Percentage) with aspect ratio preservation
   - **Cropping:** Three modes (Aspect ratio presets, Center crop, Coordinate-based) with visual crop dialog
   - **Compression:** Quality slider, lossless mode, and target file size with binary search
   - **Thumbnail Generation:** Multiple preset sizes with custom dimensions and naming
   - **Metadata Management:** Read, write, and strip EXIF data with 20+ supported fields
   - **Favicon Creation:** Multi-size ICO file generation from any source image

3. **Bulk Operations:** Process, crop, thumbnail, and rename entire directories with progress tracking, error recovery, and per-file result reporting.

4. **Pipeline Architecture:** Chain multiple operations (resize + crop + convert + compress + metadata) in a single pass, loading the image once and saving once for maximum efficiency.

5. **Metadata Profiles:** Save, load, and manage reusable metadata presets for different clients or projects.

6. **Offline Operation:** All processing happens locally. No internet connection or file uploads required.

7. **Standalone Distribution:** Available as a standalone executable (via PyInstaller) that requires no Python installation.

### 3.3 Scope of the Proposed System

The scope of Image Optimizer covers the following areas:

**In Scope:**
- Image format conversion (JPEG, PNG, WebP, AVIF)
- Image resizing with four modes (Fit, Exact, Fill, Percentage)
- Image cropping with three modes (Aspect ratio, Center, Coordinates)
- Image compression with quality control and target file size
- Thumbnail generation at multiple sizes
- EXIF metadata reading, writing, and stripping
- Favicon (ICO) generation with multiple sizes
- Bulk processing of directories with progress tracking
- Bulk renaming with pattern-based naming
- Metadata profiles for reusable presets
- Dark/light theme GUI
- Cross-platform standalone binary distribution
- Read support for BMP, TIFF, and GIF (first frame) as input formats

**Out of Scope:**
- Video processing or editing
- Vector image (SVG) processing
- Cloud storage integration
- Image editing features (filters, effects, drawing, text overlay)
- RAW camera file processing (CR2, NEF, ARW)
- Animated GIF/WebP output
- Database-backed image management or cataloging
- Multi-user/network collaboration

### 3.4 Aims and Objectives

**Aim:** To develop a comprehensive, offline, cross-platform image optimization tool that streamlines the image preparation workflow for web developers.

**Objectives:**

1. **Consolidation:** Replace multiple fragmented tools with a single unified application that handles format conversion, resizing, cropping, compression, thumbnailing, metadata editing, and favicon generation.

2. **Dual Interface:** Provide both a modern GUI for interactive use and a complete CLI for scripting, automation, and CI/CD pipeline integration.

3. **Efficiency:** Implement a pipeline architecture that chains multiple operations in a single image load/save cycle, minimizing disk I/O and processing time.

4. **Bulk Processing:** Enable batch operations on entire directories with progress tracking, error recovery (continue on per-file failure), and detailed result reporting.

5. **Ease of Use:** Design an intuitive interface with sensible defaults, format-specific quality presets, and always-visible (but contextually disabled) settings sections.

6. **Reusability:** Implement metadata profiles to save and load common EXIF configurations across sessions and projects.

7. **Safety:** Include comprehensive input validation, overwrite protection (Skip/Overwrite/Rename policies), decompression bomb prevention, and a typed error hierarchy.

8. **Portability:** Support cross-platform deployment (Windows, macOS, Linux) with standalone binary distribution requiring no Python installation.

9. **Testability:** Maintain a comprehensive test suite (174+ tests) covering all core modules to ensure reliability and facilitate maintenance.

### 3.5 Feasibility Study

#### 3.5.1 Operational Feasibility

Image Optimizer is operationally feasible for the following reasons:

- **Target Users:** Web developers, graphic designers, and digital marketing professionals who regularly prepare images for websites. These users are technically proficient and familiar with concepts like image formats, compression, and metadata.
- **Dual Interface:** The GUI lowers the barrier for casual use, while the CLI enables power users to integrate the tool into scripts and automated workflows.
- **Intuitive Design:** The GUI uses a tabbed interface with clearly labeled sections. Settings use toggle switches with grayed-out (not hidden) sections, so users always see what options are available.
- **Sensible Defaults:** All operations have format-specific default quality values (JPEG: 85, WebP: 80, AVIF: 75) and standard presets (thumbnail sizes, favicon sizes), reducing the configuration burden.
- **Error Handling:** Clear error messages with colored output (CLI) and dialog boxes (GUI) guide users when inputs are invalid.
- **Built-in Help:** The CLI tab in the GUI serves as integrated documentation, and every CLI command supports `--help` flags.

#### 3.5.2 Technical Feasibility

The project is technically feasible based on the following:

- **Mature Libraries:** The core image processing relies on Pillow, a well-maintained library with 10+ years of development, comprehensive format support, and active community maintenance.
- **Python Ecosystem:** Python 3.10+ provides modern language features (type hints, dataclasses, enums, structural pattern matching) that support clean, maintainable code.
- **Cross-Platform GUI:** CustomTkinter provides consistent modern appearance across Windows, macOS, and Linux without platform-specific code.
- **Standalone Distribution:** PyInstaller enables packaging into self-contained executables, eliminating deployment complexity.
- **Testing Infrastructure:** pytest provides a robust testing framework with fixtures, parameterization, and plugin support.
- **Hardware Requirements:** Image processing operations run efficiently on standard desktop hardware. Pillow's LANCZOS resampling and JPEG/WebP codecs are implemented in optimized C extensions.

**Minimum System Requirements:**
- Python 3.10 or later (for development/source install)
- 100 MB disk space for installation
- 512 MB RAM (recommended 2 GB for large images)
- Any modern operating system (Windows 10+, macOS 10.15+, Linux with X11/Wayland)

#### 3.5.3 Economic Feasibility

The project is economically feasible due to:

- **Zero Licensing Cost:** All dependencies are open-source (Pillow: HPND License, Click: BSD, CustomTkinter: MIT, piexif: MIT, pytest: MIT).
- **No Infrastructure Cost:** The application runs entirely offline on the developer's machine. No server hosting, cloud storage, or API subscriptions required.
- **Development Tools:** Python and all development tools (pytest, PyInstaller) are free and open-source.
- **Reduced Subscription Costs:** Replaces paid online services (TinyPNG Pro, CloudConvert, Adobe tools) for common image optimization tasks.
- **Time Savings:** Bulk processing eliminates manual repetitive work. Pipeline architecture processes images in a single pass. Metadata profiles eliminate re-entering common settings.
- **No Ongoing Costs:** Once built, the standalone binary has no recurring costs or dependencies on external services.

---

## 4. System Analysis

### 4.1 Requirements Specification (With System Modules)

#### 4.1.1 Functional Requirements

**Module 1: Format Conversion**
- FR-1.1: Convert images between JPEG, PNG, WebP, and AVIF formats
- FR-1.2: Support lossless conversion for WebP and AVIF
- FR-1.3: Accept BMP, TIFF, and GIF (first frame) as input-only formats
- FR-1.4: Preserve EXIF metadata during conversion (optional)
- FR-1.5: Handle animated GIF input by extracting first frame with warning

**Module 2: Image Resizing**
- FR-2.1: Resize in FIT mode — scale within bounds preserving aspect ratio
- FR-2.2: Resize in EXACT mode — stretch to target dimensions (with aspect ratio warning)
- FR-2.3: Resize in FILL mode — scale and center-crop to exact dimensions
- FR-2.4: Resize in PERCENTAGE mode — scale by percentage (1%–10000%)
- FR-2.5: Use LANCZOS resampling for high-quality output

**Module 3: Image Cropping**
- FR-3.1: Crop by aspect ratio preset (1:1, 4:3, 3:2, 16:9, 9:16, 3:4, 2:3)
- FR-3.2: Crop from anchor position (center, top-left, top-right, bottom-left, bottom-right)
- FR-3.3: Center crop by specified width and height
- FR-3.4: Coordinate-based crop by x, y, width, height
- FR-3.5: Visual crop dialog with interactive selection in GUI

**Module 4: Image Compression**
- FR-4.1: Compress with format-specific quality slider (JPEG: 1-95, PNG: 0-9, WebP: 1-100, AVIF: 1-100)
- FR-4.2: Support lossless compression for WebP and AVIF
- FR-4.3: Compress to target file size (KB) using binary search algorithm
- FR-4.4: Report compression ratio and size reduction in results

**Module 5: Thumbnail Generation**
- FR-5.1: Generate thumbnails at preset sizes (Small 64px, Medium 150px, Large 300px, XLarge 600px)
- FR-5.2: Support custom dimensions (width x height or single value for square)
- FR-5.3: Optional square crop before thumbnailing
- FR-5.4: Configurable prefix/suffix for output filenames
- FR-5.5: Prevent upscaling (warn if source smaller than target)

**Module 6: Metadata Management**
- FR-6.1: Read EXIF metadata from images and display structured output
- FR-6.2: Write EXIF fields: artist, copyright, description, software, comment, title, keywords, subject
- FR-6.3: Write camera fields: make, model, lens_make, lens_model
- FR-6.4: Write date fields: datetime, datetime_original, datetime_digitized
- FR-6.5: Write other fields: orientation (1-8), ISO speed
- FR-6.6: Write GPS fields: latitude, longitude (decimal degrees)
- FR-6.7: Strip all EXIF metadata (lossless for JPEG via piexif)
- FR-6.8: Support JSON output format for metadata reading (CLI)

**Module 7: Favicon Generation**
- FR-7.1: Generate multi-size ICO files from any source image
- FR-7.2: Support standard favicon sizes: 16, 32, 48, 64, 128, 256 pixels
- FR-7.3: Auto center-crop non-square source images
- FR-7.4: Convert to RGBA for transparency support

**Module 8: Bulk Operations**
- FR-8.1: Bulk convert entire directories with optional recursive scanning
- FR-8.2: Bulk process with pipeline (resize + crop + compress + metadata)
- FR-8.3: Bulk crop directories with aspect ratio and anchor
- FR-8.4: Bulk rename with pattern support ({name}, {ext}, {n}, {n:03d}, {date}, {w}, {h}, {format})
- FR-8.5: Bulk thumbnail generation
- FR-8.6: Source format filtering for selective processing
- FR-8.7: Progress callbacks with current/total/filename reporting
- FR-8.8: Continue on per-file failure with error logging
- FR-8.9: Cancellation support (cooperative flag)
- FR-8.10: Return aggregated BulkResult with per-file details

**Module 9: Pipeline (Operation Chaining)**
- FR-9.1: Chain resize, crop, convert, compress, metadata operations
- FR-9.2: Load image once, apply all transforms in memory, save once
- FR-9.3: Fluent API returning self for method chaining
- FR-9.4: Prevent conflicting operations (e.g., strip + write metadata)

**Module 10: Metadata Profiles**
- FR-10.1: Save metadata field sets as named profiles (JSON)
- FR-10.2: Load profiles to populate metadata fields in GUI
- FR-10.3: List, edit, and delete saved profiles
- FR-10.4: Profile selector available in Process, Metadata, and Bulk tabs

**Module 11: GUI Interface**
- FR-11.1: Tabbed interface with 7 tabs (Process, Thumbnail, Metadata, Favicon, Bulk, Profiles, CLI)
- FR-11.2: Dark/light theme toggle
- FR-11.3: Image preview with dimensions, format, and file size
- FR-11.4: File/folder picker with tooltip for full path
- FR-11.5: Progress bar and cancel button for long operations
- FR-11.6: Result summary with success/error status and size change percentage
- FR-11.7: Lazy tab loading for fast startup

**Module 12: CLI Interface**
- FR-12.1: Full feature parity with GUI operations
- FR-12.2: Colored terminal output with error/success/warning colors
- FR-12.3: Structured exit codes (0: success, 1: partial failure, 2: error, 3: invalid args, 4: GUI unavailable)
- FR-12.4: Automatic help page generation for all commands

#### 4.1.2 Non-Functional Requirements

- **NFR-1:** All processing must occur offline without internet connectivity
- **NFR-2:** Response time for single image operations should be under 5 seconds for typical web images
- **NFR-3:** GUI must remain responsive during long operations (threaded processing)
- **NFR-4:** Application must handle images up to 65535 x 65535 pixels with decompression bomb protection
- **NFR-5:** Cross-platform compatibility (Windows, macOS, Linux)
- **NFR-6:** Standalone binary distribution with no Python dependency for end users
- **NFR-7:** Comprehensive test suite with 174+ test cases

### 4.2 Use Case Diagram

```
                        +---------------------------+
                        |     Image Optimizer        |
                        +---------------------------+
                        |                           |
           +----------->| Convert Format            |
           |            |                           |
           +----------->| Resize Image              |
           |            |                           |
           +----------->| Crop Image                |
           |            |   - Aspect Ratio           |
           |            |   - Center Crop            |
           |            |   - Coordinate Crop        |
           |            |   - Visual Crop (GUI)      |
           |            |                           |
           +----------->| Compress Image             |
           |            |   - Quality Slider          |
  +--------+--+        |   - Target File Size        |
  |            |        |                           |
  | Web        +------->| Generate Thumbnails        |
  | Developer  |        |   - Preset Sizes            |
  |            |        |   - Custom Sizes            |
  +--------+--+        |                           |
           |            |                           |
           +----------->| Manage Metadata            |
           |            |   - Read Metadata           |
           |            |   - Write Metadata          |
           |            |   - Strip Metadata          |
           |            |                           |
           +----------->| Generate Favicon           |
           |            |                           |
           +----------->| Bulk Process               |
           |            |   - Bulk Convert            |
           |            |   - Bulk Crop               |
           |            |   - Bulk Rename             |
           |            |   - Bulk Thumbnail          |
           |            |                           |
           +----------->| Manage Profiles            |
           |            |   - Save Profile            |
           |            |   - Load Profile            |
           |            |   - Delete Profile          |
           |            |                           |
           +----------->| Switch Theme               |
                        | (Dark/Light)               |
                        +---------------------------+
```

*Note: Create a proper UML Use Case Diagram using tools like draw.io, Lucidchart, or StarUML based on this textual representation.*

### 4.3 Activity Diagram

#### Single Image Processing Activity

```
[Start]
   |
   v
[Select Input Image]
   |
   v
[Validate Input File]----> (Invalid) ----> [Show Error] ----> [End]
   |
   (Valid)
   |
   v
[Load Image into Memory]
   |
   v
[Configure Operations]
   |
   +----> [Enable Resize?] --Yes--> [Set Mode, Width, Height]
   |
   +----> [Enable Crop?] --Yes--> [Set Aspect/Center/Coords]
   |
   +----> [Enable Convert?] --Yes--> [Set Target Format]
   |
   +----> [Enable Compress?] --Yes--> [Set Quality/Size]
   |
   +----> [Enable Metadata?] --Yes--> [Set Fields or Strip]
   |
   v
[Select Output Path]
   |
   v
[Execute Pipeline]
   |
   +----> [Apply Resize] (if enabled)
   |
   +----> [Apply Crop] (if enabled)
   |
   +----> [Convert Format] (if enabled)
   |
   +----> [Handle EXIF] (strip or write)
   |
   +----> [Save with Quality/Compression]
   |
   v
[Display Result Summary]
   |
   v
[End]
```

#### Bulk Processing Activity

```
[Start]
   |
   v
[Select Input Directory]
   |
   v
[Scan for Image Files] ---(recursive option)
   |
   v
[Configure Bulk Settings]
   |
   v
[Begin Processing] ----> [Initialize Progress Bar]
   |
   v
[For Each Image File]
   |
   +----> [Process Image via Pipeline]
   |        |
   |        +---> (Success) --> [Record Success]
   |        |
   |        +---> (Error) --> [Record Error, Continue]
   |
   +----> [Update Progress] (current/total/filename)
   |
   +----> [Check Cancel Flag] --Yes--> [Stop Processing]
   |
   v
[All Files Processed]
   |
   v
[Display Bulk Result Summary]
   (total, succeeded, failed, skipped)
   |
   v
[End]
```

*Note: Create proper UML Activity Diagrams using tools like draw.io, Lucidchart, or StarUML based on these textual representations.*

### 4.4 Class Diagram / System Flowchart

#### Core Class Structure

```
+----------------------+       +---------------------+
|   ImageFormat (Enum) |       |  ResizeMode (Enum)  |
+----------------------+       +---------------------+
| JPEG                 |       | EXACT               |
| PNG                  |       | FIT                 |
| WEBP                 |       | FILL                |
| AVIF                 |       | PERCENTAGE          |
| ICO                  |       +---------------------+
+----------------------+

+----------------------+       +---------------------+
| CompressionMode(Enum)|       | OverwritePolicy(Enum)|
+----------------------+       +---------------------+
| LOSSY                |       | SKIP                |
| LOSSLESS             |       | OVERWRITE           |
+----------------------+       | RENAME              |
                               | ASK                 |
+----------------------+       +---------------------+
| ThumbnailPreset(Enum)|
+----------------------+
| SMALL (64x64)        |
| MEDIUM (150x150)     |
| LARGE (300x300)      |
| XLARGE (600x600)     |
+----------------------+

+--------------------------+
|    ImageInfo             |
+--------------------------+
| + path: Path             |
| + format: str            |
| + mode: str              |
| + width: int             |
| + height: int            |
| + file_size: int         |
| + is_animated: bool      |
| + has_exif: bool         |
| + has_transparency: bool |
+--------------------------+

+--------------------------+
|    OperationResult       |
+--------------------------+
| + success: bool          |
| + input_path: Path       |
| + output_path: Path      |
| + error: str             |
| + warnings: list[str]    |
| + metadata: dict         |
+--------------------------+

+--------------------------+
|    BulkResult            |
+--------------------------+
| + total: int             |
| + succeeded: int         |
| + failed: int            |
| + skipped: int           |
| + results: list[OpResult]|
+--------------------------+

+--------------------------+        +--------------------------+
|    Pipeline              |        | ImageOptimizerApp        |
+--------------------------+        |    (ctk.CTk)             |
| - _input_path: Path     |        +--------------------------+
| - _operations: list     |        | - tabview: CTkTabview    |
| - _target_format: str   |        | - _tabs_loaded: set      |
| - _quality: int         |        +--------------------------+
| - _lossless: bool       |        | + launch_gui()           |
| - _strip_exif: bool     |        | + toggle_theme()         |
| - _exif_fields: dict    |        | + _on_tab_changed()      |
+--------------------------+        +--------------------------+
| + resize() -> Pipeline   |
| + crop() -> Pipeline     |
| + convert() -> Pipeline  |
| + compress() -> Pipeline |
| + strip_metadata()       |
| + write_metadata()       |
| + execute() -> OpResult  |
+--------------------------+

+--------------------------+
|  ImageOptimizerError     |
+--------------------------+
         |
    +----+----+----+----+----+----+----+----+
    |    |    |    |    |    |    |    |    |
  Valid. Load Save FmtNA FmtConv Meta MetaWr Perm Disk Bulk
  Error Error Error Error Error Error Error Error Error Error
```

*Note: Create proper UML Class Diagrams using tools like draw.io, Lucidchart, or StarUML based on this textual representation.*

#### System Flowchart

```
+==================+
|    Application   |
|    Entry Point   |
+========+=========+
         |
    +----+----+
    |         |
    v         v
+-------+ +-------+
|  CLI  | |  GUI  |
+---+---+ +---+---+
    |         |
    v         v
+---+---------+---+
|                 |
|   Core Layer    |
|                 |
| +-------------+ |
| | validation  | |
| +------+------+ |
|        |        |
| +------v------+ |
| |  image_io   | |
| | (load/save) | |
| +------+------+ |
|        |        |
| +------v------+ |
| |  pipeline   | |
| +------+------+ |
|        |        |
|  +-----+-----+  |
|  |     |     |   |
|  v     v     v   |
| resize crop conv |
| compress meta    |
| thumbnail favicon|
| bulk             |
+------------------+
```

### 4.5 Data Flow Diagram

#### 4.5.1 Context Level DFD (Level 0)

```
+----------+                                              +----------+
|          |  Input Image(s) / Settings / Commands        |          |
|   Web    | ------------------------------------------->  |  Image   |
| Developer|                                              | Optimizer|
|          | <-------------------------------------------  |  System  |
|          |  Processed Image(s) / Results / Reports      |          |
+----------+                                              +----------+
```

#### 4.5.2 First Level DFD (Level 1)

```
                    +----------+
                    |   Web    |
                    | Developer|
                    +----+-----+
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
    +-----+----+   +-----+----+  +-----+------+
    | 1.0      |   | 2.0      |  | 3.0        |
    | Single   |   | Bulk     |  | Profile    |
    | Image    |   | Process  |  | Management |
    | Process  |   |          |  |            |
    +-----+----+   +-----+----+  +-----+------+
          |              |              |
          v              v              v
    +-----+----+   +-----+----+  +-----+------+
    | Output   |   | Output   |  | Profile    |
    | Image    |   | Directory|  | Storage    |
    | File     |   |          |  | (JSON)     |
    +----------+   +----------+  +------------+
```

#### 4.5.3 Second Level DFD (Level 2) — Process 1.0: Single Image Processing

```
                    +----------+
                    | Input    |
                    | Image    |
                    +----+-----+
                         |
                         v
                  +------+------+
                  | 1.1         |
                  | Validate    |
                  | Input       |
                  +------+------+
                         |
                         v
                  +------+------+
                  | 1.2         |
                  | Load Image  |
                  +------+------+
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
   +------+------+ +----+------+ +-----+------+
   | 1.3         | | 1.4       | | 1.5        |
   | Resize/Crop | | Convert   | | Compress   |
   |             | | Format    | |            |
   +------+------+ +----+------+ +-----+------+
          |              |              |
          +--------------+--------------+
                         |
                         v
                  +------+------+
                  | 1.6         |
                  | Handle EXIF |
                  | Metadata    |
                  +------+------+
                         |
                         v
                  +------+------+
                  | 1.7         |
                  | Save Output |
                  +------+------+
                         |
                         v
                  +------+------+
                  | Output      |
                  | Image File  |
                  +-------------+
```

### 4.6 ER Diagram

*Note: Image Optimizer is a file-processing tool, not a database-driven application. It does not use a traditional database. However, the following entity-relationship representation shows the data structures used internally.*

```
+------------------+        +-------------------+
|    InputImage    |        |  OutputImage      |
+------------------+        +-------------------+
| path (PK)        |  1..* | path (PK)         |
| format           |----->>| format            |
| width            |       | width             |
| height           |       | height            |
| file_size        |       | file_size         |
| mode             |       | quality           |
| has_exif         |       | compression_ratio |
| has_transparency |       +-------------------+
| is_animated      |
+------------------+
        |
        | 1..1
        v
+------------------+        +-------------------+
|  OperationResult |        | MetadataProfile   |
+------------------+        +-------------------+
| success          |        | name (PK)         |
| error            |        | artist            |
| warnings[]       |        | copyright         |
| metadata{}       |        | description       |
+------------------+        | make              |
        |                   | model             |
        | *..1              | datetime          |
        v                   | gps_latitude      |
+------------------+        | gps_longitude     |
|   BulkResult     |        | ...               |
+------------------+        +-------------------+
| total            |
| succeeded        |
| failed           |
| skipped          |
| results[]        |
+------------------+
```

*Note: Create proper ER Diagrams using tools like draw.io, Lucidchart, or MySQL Workbench based on this textual representation.*

---

## 5. System Design

### 5.1 Data Dictionary

#### 5.1.1 Enumerations

| Name | Values | Description |
|------|--------|-------------|
| ImageFormat | JPEG, PNG, WEBP, AVIF, ICO | Supported output image formats |
| ResizeMode | EXACT, FIT, FILL, PERCENTAGE | Image resize strategy |
| CompressionMode | LOSSY, LOSSLESS | Compression type |
| OverwritePolicy | SKIP, OVERWRITE, RENAME, ASK | File overwrite behavior |
| ThumbnailPreset | SMALL (64), MEDIUM (150), LARGE (300), XLARGE (600) | Thumbnail size presets |

#### 5.1.2 Data Structures

**ImageInfo**

| Field | Type | Description |
|-------|------|-------------|
| path | Path | File system path to the image |
| format | str | Detected image format (e.g., "JPEG", "PNG") |
| mode | str | Color mode (RGB, RGBA, CMYK, L, P) |
| width | int | Image width in pixels |
| height | int | Image height in pixels |
| file_size | int | File size in bytes |
| is_animated | bool | True if image has multiple frames (GIF) |
| has_exif | bool | True if EXIF metadata is present |
| has_transparency | bool | True if image has alpha channel |

**OperationResult**

| Field | Type | Description |
|-------|------|-------------|
| success | bool | Whether the operation completed successfully |
| input_path | Path | Path to the source image |
| output_path | Path | Path to the output image |
| error | str | Error message if operation failed |
| warnings | list[str] | Non-fatal warning messages |
| metadata | dict | Operation-specific data (sizes, ratios, etc.) |

**BulkResult**

| Field | Type | Description |
|-------|------|-------------|
| total | int | Total number of files found |
| succeeded | int | Number of successfully processed files |
| failed | int | Number of files that failed processing |
| skipped | int | Number of files skipped (overwrite policy) |
| results | list[OperationResult] | Per-file detailed results |

**MetadataProfile (JSON)**

| Field | Type | Description |
|-------|------|-------------|
| name | str | Profile name (used as filename) |
| artist | str | Artist/creator name |
| copyright | str | Copyright notice |
| description | str | Image description |
| software | str | Software name |
| comment | str | User comment |
| title | str | Image title |
| keywords | str | Keywords/tags |
| subject | str | Image subject |
| make | str | Camera manufacturer |
| model | str | Camera model |
| lens_make | str | Lens manufacturer |
| lens_model | str | Lens model |
| datetime | str | Date/time (YYYY:MM:DD HH:MM:SS) |
| datetime_original | str | Original capture date |
| datetime_digitized | str | Digitization date |
| orientation | str | EXIF orientation (1-8) |
| iso | str | ISO speed rating |
| gps_latitude | str | GPS latitude (decimal degrees) |
| gps_longitude | str | GPS longitude (decimal degrees) |

#### 5.1.3 Constants

| Constant | Value | Description |
|----------|-------|-------------|
| MAX_DIMENSION | 65535 | Maximum allowed pixel dimension |
| MIN_DIMENSION | 1 | Minimum allowed pixel dimension |
| MAX_PIXELS | 178,956,970 | Pillow decompression bomb threshold |
| MAX_ICO_SIZE | 256 | Maximum favicon size in pixels |
| DEFAULT_QUALITY (JPEG) | 85 | Default JPEG compression quality |
| DEFAULT_QUALITY (WebP) | 80 | Default WebP compression quality |
| DEFAULT_QUALITY (AVIF) | 75 | Default AVIF compression quality |
| DEFAULT_QUALITY (PNG) | 6 | Default PNG compression level (0-9) |
| FAVICON_SIZES | [16, 32, 48, 64, 128, 256] | Standard favicon sizes |

#### 5.1.4 Format Mappings

| Extension | ImageFormat | Pillow Format |
|-----------|-------------|---------------|
| .jpg, .jpeg | JPEG | JPEG |
| .png | PNG | PNG |
| .webp | WEBP | WEBP |
| .avif | AVIF | AVIF |
| .ico | ICO | ICO |
| .bmp | (input only) | BMP |
| .tif, .tiff | (input only) | TIFF |
| .gif | (input only) | GIF |

### 5.2 Screen Layouts / UI Design

#### 5.2.1 Main Window

```
+----------------------------------------------------------+
|  Image Optimizer              [Dark/Light Toggle]         |
|  Created by Hency Prajapati - Known Click Technologies   |
+----------------------------------------------------------+
| Process | Thumbnail | Metadata | Favicon | Bulk | Profiles| CLI |
+----------------------------------------------------------+
|                                                          |
|                   (Active Tab Content)                    |
|                                                          |
+----------------------------------------------------------+
```

- Window size: 1000x700 (default), 800x600 (minimum)
- Header: Application title, creator credit, theme toggle button
- Tab bar: 7 tabs, lazy-loaded on first selection

#### 5.2.2 Process Tab

```
+----------------------------------------------------------+
| Input File: [________________________] [Browse]           |
|                                                          |
| +--------------------+                                   |
| |   Image Preview    |  1920x1080 | JPEG | RGB | 2.4 MB |
| |    (200x200)       |                                   |
| +--------------------+                                   |
|                                                          |
| [Toggle] Convert Format                                  |
|   Format: [JPEG v]  [ ] Lossless                        |
|                                                          |
| [Toggle] Resize                                          |
|   Mode: [Fit v]  Width: [____]  Height: [____]          |
|                                                          |
| [Toggle] Crop                                            |
|   Aspect: [16:9 v]  Anchor: [center v]  [Visual Crop]  |
|                                                          |
| [Toggle] Compress                                        |
|   Quality: [----o---------] 75                           |
|   [ ] Lossless                                           |
|                                                          |
| [ ] Strip Metadata                                       |
|                                                          |
| [Toggle] Write Metadata                                  |
|   Profile: [Select Profile v] [Load]                    |
|   Artist: [________________]                            |
|   Copyright: [_____________]                            |
|   ...                                                    |
|                                                          |
| Output File: [________________________] [Browse]         |
|                                                          |
|               [Process Image]                            |
|                                                          |
| [======= Progress Bar =======]                          |
| [Result: Success | 2.4 MB -> 1.1 MB (54% reduction)]   |
+----------------------------------------------------------+
```

#### 5.2.3 Thumbnail Tab

```
+----------------------------------------------------------+
| Input File: [________________________] [Browse]           |
|                                                          |
| +--------------------+                                   |
| |   Image Preview    |  1920x1080 | JPEG | RGB          |
| +--------------------+                                   |
|                                                          |
| Sizes:                                                   |
|   [x] Small (64x64)    [x] Medium (150x150)            |
|   [x] Large (300x300)  [x] XLarge (600x600)            |
|   Custom: [____] x [____]                               |
|                                                          |
| [ ] Square Crop                                          |
| Format: [PNG v]   Quality: [----o-----] 85              |
| Prefix: [thumb]   Suffix: [________]                    |
|                                                          |
| Output Folder: [________________________] [Browse]       |
|                                                          |
|             [Generate Thumbnails]                        |
+----------------------------------------------------------+
```

#### 5.2.4 Metadata Tab

```
+----------------------------------------------------------+
| --- Read Metadata ---                                    |
| Input: [________________________] [Browse]               |
| [Read Metadata]                                          |
| +------------------------------------------------------+|
| | File: photo.jpg                                      ||
| | Format: JPEG | 1920x1080 | RGB | 2.4 MB             ||
| | Artist: John Doe                                     ||
| | Copyright: 2024 Company                              ||
| | ...                                                  ||
| +------------------------------------------------------+|
|                                                          |
| --- Strip Metadata ---                                   |
| Output: [________________________] [Browse]              |
| [Strip Metadata]                                         |
|                                                          |
| --- Write Metadata ---                                   |
| Input: [________________________] [Browse]               |
| Profile: [Select Profile v] [Load]                      |
|                                                          |
| Basic:                                                   |
|   Artist: [________________]  Copyright: [____________] |
|   Description: [__________]  Software: [______________] |
|                                                          |
| Camera & Lens:                                           |
|   Make: [__________________]  Model: [________________] |
|   Lens Make: [_____________]  Lens Model: [___________] |
|                                                          |
| Date/Time:                                               |
|   DateTime: [______________]  Original: [_____________] |
|                                                          |
| GPS:                                                     |
|   Latitude: [______________]  Longitude: [____________] |
|                                                          |
| Output: [________________________] [Browse]              |
| [Write Metadata]                                         |
+----------------------------------------------------------+
```

#### 5.2.5 Bulk Tab

```
+----------------------------------------------------------+
| Mode: [ Process | Thumbnail | Rename ]                   |
|                                                          |
| Input Folder: [________________________] [Browse]        |
| Output Folder: [________________________] [Browse]       |
| [ ] Recursive                                            |
|                                                          |
| --- Settings (varies by mode) ---                        |
| Format: [Auto v]   Quality: [----o-----] 85             |
| Resize Mode: [Fit v]  W: [____]  H: [____]             |
| Crop: [None v]  Anchor: [center v]                      |
| [ ] Strip Metadata                                       |
| Overwrite: [Rename v]                                    |
|                                                          |
|        [Start Bulk Processing]  [Cancel]                 |
|                                                          |
| [======= Progress Bar =======]                          |
| Processing: photo_042.jpg (42/150)                      |
|                                                          |
| +------------------------------------------------------+|
| | Results:                                             ||
| | [OK] photo_001.jpg -> output/photo_001.webp          ||
| | [OK] photo_002.jpg -> output/photo_002.webp          ||
| | [FAIL] photo_003.jpg: Unsupported format             ||
| | ...                                                  ||
| +------------------------------------------------------+|
+----------------------------------------------------------+
```

### 5.3 Reports

Image Optimizer generates the following output reports:

#### 5.3.1 Single Operation Result

After each single-file operation, the system reports:
- **Status:** Success or Error
- **Input/Output Paths:** Source and destination file locations
- **Size Change:** Original size, new size, percentage reduction
- **Compression Ratio:** Ratio of output to input size
- **Warnings:** Non-fatal messages (e.g., aspect ratio change, source smaller than target)
- **Operation Metadata:** Format-specific data (dimensions, quality used, etc.)

#### 5.3.2 Bulk Operation Result

After bulk processing, the system reports:
- **Summary Statistics:** Total files, succeeded, failed, skipped
- **Per-File Results:** Individual success/failure with file paths and error messages
- **Progress Log:** Real-time per-file status during processing
- **Error Details:** Specific error messages for each failed file

#### 5.3.3 Metadata Report

When reading metadata, the system displays:
- **File Information:** Path, format, dimensions, color mode, file size
- **EXIF Fields:** All readable EXIF tags with human-readable labels
- **JSON Output:** Optional structured JSON format for programmatic use (CLI)

---

## 6. System Implementation

### 6.1 Module Implementation

#### 6.1.1 Core Layer (`image_optimizer/core/`)

The core layer contains all image processing logic with zero UI dependencies. This separation ensures the processing engine can be used independently as a Python library.

**types.py — Type Definitions**

Defines the project's type system using Python enums and dataclasses. The `ImageFormat` enum maps to Pillow format names. The `OperationResult` dataclass provides a standardized return type for all operations, carrying success status, file paths, error messages, warnings, and operation-specific metadata. The error hierarchy extends from a base `ImageOptimizerError` class with specialized subclasses for validation, I/O, format, metadata, permission, and bulk operation errors.

**constants.py — Configuration Registry**

Centralizes all format mappings, quality ranges, size limits, and presets. Extension-to-format and format-to-extension mappings enable bidirectional format resolution. Quality ranges are defined per format (JPEG: 1-95, WebP: 1-100, AVIF: 1-100, PNG compression: 0-9). Safety constants prevent decompression bombs (MAX_PIXELS: 178,956,970) and invalid dimensions (MAX_DIMENSION: 65535).

**validation.py — Input Validation**

Provides comprehensive validation functions that raise typed errors. `validate_input_path()` checks file existence, readability, and non-empty size. `validate_output_path()` implements the four overwrite policies. `validate_format()` normalizes format strings and checks AVIF plugin availability. `validate_dimensions()` clamps values to safe ranges. `validate_exif_fields()` filters against a known field whitelist. `validate_rename_pattern()` performs dry-run expansion with collision detection.

**image_io.py — Image I/O**

Wraps Pillow's `Image.open()` and `Image.save()` with safety features. `load_image()` performs `verify()`, detects format via file header, checks for EXIF/transparency/animation, and returns an `ImageInfo` alongside the PIL Image. `save_image()` handles format-specific kwargs (JPEG quality, PNG compression, WebP/AVIF quality and lossless), color mode conversion (CMYK to RGB, RGBA to RGB for JPEG, palette mode handling), and EXIF embedding. `image_to_bytes()` encodes images to in-memory bytes for the compressor's binary search.

**resizer.py — Image Resizing**

Implements four resize modes. `calculate_dimensions()` is a pure math function that computes new width and height based on the mode, making it easily testable. FIT mode scales the image to fit within the target bounds while preserving the aspect ratio. EXACT mode stretches to the target dimensions (with a warning if the aspect ratio changes). FILL mode scales to cover the target area and center-crops the excess. PERCENTAGE mode scales by a given factor (1%–10000%). All modes use LANCZOS resampling for quality.

**cropper.py — Image Cropping**

Supports three cropping modes. Aspect ratio mode crops to predefined ratios (1:1, 4:3, 3:2, 16:9, 9:16, 3:4, 2:3) from a specified anchor position. Center crop extracts a rectangle of specified width and height from the image center. Coordinate crop extracts a region starting at (x, y) with given dimensions. `calculate_crop_box()` returns a (left, top, right, bottom) tuple suitable for PIL's `Image.crop()`.

**converter.py — Format Conversion**

Handles format conversion between JPEG, PNG, WebP, and AVIF. Accepts BMP, TIFF, and GIF as input-only formats. Extracts the first frame from animated GIFs with a warning. Preserves EXIF metadata by default (optional stripping). Delegates to `save_image()` for format-specific encoding.

**compressor.py — Image Compression**

Provides quality-based and file-size-based compression. Quality mode applies the specified quality setting directly. File-size mode uses binary search: it encodes the image at progressively lower quality levels until the output fits within the target size in KB. Returns compression ratio and size reduction metadata. Warns if the output is larger than the input.

**metadata.py — EXIF Operations**

Uses piexif to read, write, and strip EXIF metadata. `read_metadata()` parses EXIF bytes into a structured dictionary with human-readable labels, handling Windows XP extended fields (UTF-16LE encoded). `write_metadata()` builds EXIF bytes from a field dictionary with validation (datetime format, orientation range, GPS coordinates). `strip_metadata()` removes all EXIF data losslessly for JPEG files.

**thumbnail.py — Thumbnail Generation**

Generates thumbnails without upscaling. `generate_thumbnail()` creates a single thumbnail from a preset size, integer, or (width, height) tuple. `generate_thumbnails()` creates batch thumbnails with configurable naming: `{prefix}_{stem}_{W}x{H}_{suffix}.{ext}`. Optional square crop (center crop to 1:1) before thumbnailing.

**favicon.py — Favicon Generation**

Creates multi-size ICO files for web favicons. Auto center-crops non-square source images. Clamps sizes to 1-256 pixels. Converts to RGBA for transparency support. Default sizes: [16, 32, 48, 64, 128, 256].

**pipeline.py — Operation Chaining**

Implements a fluent API (builder pattern) for chaining operations. The Pipeline class stores operations as a list of (name, kwargs) tuples. `execute()` loads the image once, applies all resize and crop operations in order, determines the output format, handles EXIF (strip or write), and saves once. This single-pass approach minimizes disk I/O and avoids repeated encoding/decoding losses.

**bulk.py — Batch Operations**

Processes entire directories with error recovery. `bulk_convert()`, `bulk_process()`, `bulk_rename()`, and `bulk_thumbnail()` all follow the same pattern: scan for image files, iterate with progress callbacks, process each file independently (catching per-file errors), and aggregate results into a `BulkResult`. A cooperative cancellation flag allows the GUI to stop long-running operations. Error callbacks enable real-time per-file error reporting.

#### 6.1.2 CLI Layer (`image_optimizer/cli/`)

**app.py — Entry Point**

The Click command group serves as the application entry point. The `--gui` flag launches the CustomTkinter interface. Without a subcommand, it displays help text. Commands are registered via `add_command()`.

**commands/ — Individual Commands**

Each command file wraps a core function with Click decorators:

- `convert.py`: Format conversion with `-f/--format` (required), `-q/--quality`, `--lossless`, `--no-metadata`
- `resize.py`: Resizing with `-W/--width`, `-H/--height`, `-p/--percentage`, `--mode`
- `crop.py`: Cropping with `-a/--aspect-ratio`, `--anchor`, `-W/--width`, `-H/--height`, `-x/-y`
- `compress.py`: Compression with `-q/--quality`, `--lossless`, `--max-size`
- `thumbnail.py`: Thumbnailing with `-s/--size` (preset or integer), `--square`
- `metadata.py`: Read/strip/write subcommands with 17 field options
- `favicon.py`: Favicon generation with `--sizes`
- `bulk.py`: Bulk convert/process/crop/rename/thumbnail subcommands

**formatters.py — Output Formatting**

Pretty-prints results with colored terminal output. `print_result()` shows success/error status, file sizes, and compression ratios. `print_bulk_result()` shows summary statistics. `progress_callback()` displays real-time progress.

**Exit Codes:**
- 0: Success
- 1: Bulk partial failure (some files failed)
- 2: Error
- 3: Invalid arguments
- 4: GUI unavailable

#### 6.1.3 GUI Layer (`image_optimizer/gui/`)

**app.py — Main Window**

`ImageOptimizerApp` extends `ctk.CTk` (CustomTkinter root window). Sets up a 1000x700 window with a header containing the title, creator credit, and dark/light theme toggle. Creates a `CTkTabview` with 7 tabs. Only the Process tab is loaded eagerly on startup; other tabs are loaded lazily when first selected, ensuring fast application launch.

**Tabs:**

- **ProcessTab**: Unified single-file processing with toggle sections for convert, resize, crop, compress, and metadata. Uses `CTkSwitch` widgets that gray out sections (not hide them), so users always see available options. Includes image preview, profile selector, indeterminate progress bar, and result summary.

- **ThumbnailTab**: Multi-size thumbnail generation with preset size checkboxes, custom dimension input, square crop option, prefix/suffix naming, and format/quality controls.

- **MetadataTab**: Three sections — Read (display EXIF in a text box), Strip (remove all metadata), Write (17 field entries organized by group with profile selector).

- **FaviconTab**: ICO generation with size checkboxes (16-256), image preview, and auto .ico extension enforcement.

- **BulkTab**: Segmented button to switch between Process, Thumbnail, and Rename modes. Each mode shows relevant settings. Includes progress panel with cancel button and scrollable result log.

- **ProfilesTab**: Create, edit, and delete metadata profiles. Profile name entry, 17 metadata field entries, save/load/delete buttons.

- **CLITab**: Built-in reference documentation for command-line usage with example commands.

**Components:**

- **FilePicker**: Label + read-only entry + browse button with tooltip for full paths. Modes: load, save, folder. File type filtering.
- **ImagePreview**: 200x200 thumbnail display with dimensions/format/mode/size info line.
- **ResultSummary**: Status display with color coding, size change percentage, compression ratio, and scrollable bulk result log.
- **SettingsPanel**: Contains QualitySlider, DimensionInput, FormatSelector, MetadataFields, ProgressPanel, and ProfileSelector widgets.
- **CropCanvas**: Interactive crop area selection for the visual crop dialog.
- **ErrorDialog**: CTk messagebox wrapper for error display.

**workers.py — Thread Management**

`WorkerThread` runs processing operations in daemon threads to keep the GUI responsive. Uses a cooperative cancel flag. Completion and error callbacks are marshaled to the main thread via `widget.after()`. Progress callbacks are throttled to 20 updates/second to prevent GUI flooding.

**profiles.py — Profile Persistence**

CRUD operations for metadata profiles stored as JSON files in `image_optimizer/gui/profiles/`. Functions: `save_profile()`, `load_profile()`, `list_profiles()`, `delete_profile()`.

**theme.py — Styling**

Centralizes platform-specific fonts (Segoe UI on Windows, SF Pro on macOS, Sans on Linux), color palette (primary blue, success green, error red), and widget styling constants.

---

## 7. System Testing

### 7.1 Testing Strategies

The project employs a comprehensive testing approach using pytest with 174+ test cases across 13 test files.

**Unit Testing:** Each core module has a dedicated test file that tests individual functions in isolation. Pure functions like `calculate_dimensions()` and `calculate_crop_box()` are tested with various input combinations. Validation functions are tested with both valid and invalid inputs.

**Integration Testing:** The pipeline tests verify that multiple operations chain correctly — resize followed by crop followed by conversion produces the expected output. Bulk operation tests verify directory scanning, progress callbacks, and error recovery.

**CLI Testing:** Click's `CliRunner` is used to invoke commands programmatically and verify exit codes, output messages, and generated files.

**Fixture-Based Setup:** Tests use pytest fixtures to create temporary directories, generate sample images (JPEG, PNG, WebP at known dimensions), and clean up after execution.

**Edge Case Coverage:** Tests cover boundary conditions (minimum/maximum dimensions, zero-byte files, missing files, unsupported formats), error paths (invalid quality values, corrupt images, permission errors), and format-specific behaviors (RGBA to JPEG conversion, animated GIF handling, EXIF preservation).

### 7.2 Test Cases

#### 7.2.1 Validation Tests (test_validation.py — 25 tests)

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| test_valid_input_path | Valid image file path | Returns validated Path object |
| test_input_path_not_found | Non-existent file | Raises ValidationError |
| test_input_path_empty_file | Zero-byte file | Raises ValidationError |
| test_valid_format_jpeg | Format string "jpg" | Returns "JPEG" |
| test_valid_format_webp | Format string "webp" | Returns "WEBP" |
| test_invalid_format | Format string "xyz" | Raises ValidationError |
| test_valid_dimensions | Width=800, Height=600 | Returns (800, 600) |
| test_dimension_too_large | Width=100000 | Clamps to MAX_DIMENSION |
| test_dimension_zero | Width=0 | Raises ValidationError |
| test_valid_quality_jpeg | Quality=85, Format=JPEG | Returns 85 |
| test_quality_out_of_range | Quality=200 | Clamps with warning |
| test_valid_percentage | Percentage=50 | Returns 50.0 |
| test_percentage_zero | Percentage=0 | Raises ValidationError |
| test_overwrite_skip | Existing file, SKIP policy | Returns skip result |
| test_overwrite_rename | Existing file, RENAME policy | Returns path with _1 suffix |
| test_valid_exif_fields | Known fields (artist, copyright) | Returns validated dict |
| test_invalid_exif_field | Unknown field name | Filters out with warning |
| test_valid_datetime | "2024:01:15 10:30:00" | Returns validated string |
| test_invalid_datetime | "2024-01-15" (wrong separator) | Raises ValidationError |
| test_valid_orientation | Orientation=1 | Returns 1 |
| test_invalid_orientation | Orientation=9 | Raises ValidationError |
| test_valid_gps | Latitude=40.7128 | Returns validated float |
| test_invalid_gps_latitude | Latitude=91.0 | Raises ValidationError |
| test_rename_pattern_valid | Pattern="{name}_{n}.{ext}" | Returns expanded list |
| test_rename_pattern_collision | Pattern causing duplicate names | Raises ValidationError |

#### 7.2.2 Image I/O Tests (test_image_io.py)

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| test_load_jpeg | Load valid JPEG | Returns Image + ImageInfo |
| test_load_png_rgba | Load PNG with alpha | has_transparency=True |
| test_load_nonexistent | Load missing file | Raises ImageLoadError |
| test_save_jpeg | Save as JPEG with quality | File created at path |
| test_save_webp_lossless | Save WebP lossless | Lossless WebP output |
| test_mode_conversion_cmyk | CMYK input to JPEG | Converts to RGB |
| test_exif_preservation | Save with EXIF bytes | EXIF present in output |

#### 7.2.3 Resizer Tests (test_resizer.py)

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| test_fit_width_only | FIT mode, width=400 | Scales proportionally |
| test_fit_both | FIT mode, 400x300 | Fits within bounds |
| test_exact_stretch | EXACT mode, 400x400 | Stretches to target |
| test_fill_crop | FILL mode, 400x400 | Scales + center-crops |
| test_percentage_50 | PERCENTAGE mode, 50% | Half dimensions |
| test_percentage_200 | PERCENTAGE mode, 200% | Double dimensions |
| test_no_upscale_warning | Target larger than source | Warns about upscaling |

#### 7.2.4 Cropper Tests (test_cropper.py — tests for cropping logic)

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| test_aspect_1_1_center | 1:1 ratio from center | Square center crop |
| test_aspect_16_9_center | 16:9 ratio from center | Widescreen center crop |
| test_aspect_top_left | 1:1 from top-left | Crop from (0,0) |
| test_center_crop | 400x400 center | Centered extraction |
| test_coordinate_crop | x=100, y=50, 200x200 | Region at coordinates |
| test_crop_exceeds_bounds | Crop larger than image | Clamps to image bounds |

#### 7.2.5 Compression Tests (test_compressor.py)

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| test_quality_compression | Quality=75 JPEG | Output smaller than input |
| test_lossless_webp | Lossless WebP | Lossless output created |
| test_target_file_size | Max size 50KB | Output <= 50KB |
| test_compression_ratio | Compress image | Reports ratio in metadata |

#### 7.2.6 Pipeline Tests (test_pipeline.py)

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| test_resize_convert | Resize then convert | Both operations applied |
| test_full_pipeline | Resize+crop+convert+compress | All operations in one pass |
| test_strip_and_write_conflict | strip + write metadata | Raises ValidationError |
| test_metadata_through_pipeline | Write EXIF via pipeline | EXIF present in output |

#### 7.2.7 Bulk Tests (test_bulk.py, test_bulk_process.py)

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| test_bulk_convert_directory | Convert folder to WebP | All files converted |
| test_bulk_recursive | Recursive directory scan | Subdirectory files included |
| test_bulk_source_filter | Filter by source format | Only matching files processed |
| test_bulk_progress_callback | Progress during processing | Callback called per file |
| test_bulk_error_recovery | Corrupt file in batch | Continues, reports failure |
| test_bulk_cancel | Cancel mid-processing | Stops after current file |
| test_bulk_rename_pattern | Rename with {name}_{n} | Files renamed correctly |

#### 7.2.8 Other Module Tests

| Test File | Module Tested | Key Tests |
|-----------|---------------|-----------|
| test_converter.py | Format conversion | Format pairs, animation handling, metadata preservation |
| test_thumbnail.py | Thumbnail generation | Preset sizes, custom sizes, square crop, no-upscale warning |
| test_favicon.py | Favicon generation | Multi-size ICO, non-square input, RGBA conversion |
| test_metadata.py | EXIF operations | Read/write/strip, field validation, GPS coordinates |
| test_cli.py | CLI commands | All commands with various option combinations, exit codes |

---

## 8. Future Enhancement

The following enhancements are planned or considered for future versions of Image Optimizer:

1. **Watermarking:** Add text or image watermarks with configurable position, opacity, size, and rotation. Support batch watermarking for bulk operations.

2. **Image Filters and Effects:** Basic adjustments such as brightness, contrast, saturation, sharpness, and blur. Color adjustments including hue/saturation/lightness controls.

3. **Drag-and-Drop Support:** Enable drag-and-drop file input in the GUI for faster workflow. Support dropping entire folders for bulk operations.

4. **Preset Processing Profiles:** Save complete processing configurations (resize + crop + compress settings) as reusable profiles, extending the current metadata-only profile system.

5. **Watch Folder / Hot Folder:** Monitor a directory for new images and automatically process them with predefined settings.

6. **HEIF/HEIC Support:** Add support for Apple's HEIF/HEIC image format, which is increasingly common from iPhone cameras.

7. **RAW Format Support:** Basic support for camera RAW formats (CR2, NEF, ARW, DNG) as input formats for conversion.

8. **Multi-Language Support:** Internationalization (i18n) for the GUI with language selection.

9. **Undo/History:** Operation history with the ability to undo and redo changes.

10. **Image Comparison View:** Side-by-side before/after comparison in the GUI to preview compression quality trade-offs.

11. **SVG to Raster Conversion:** Convert SVG vector images to PNG/JPEG at specified dimensions.

12. **Animated WebP/GIF Output:** Support for creating and optimizing animated WebP and GIF files.

13. **Plugin Architecture:** Allow third-party plugins for custom processing operations and format support.

14. **Cloud Integration:** Optional integration with cloud storage services (S3, Google Cloud Storage) for batch processing workflows.

---

## 9. Bibliography/References

1. **Python Official Documentation.** Python Software Foundation. https://docs.python.org/3/

2. **Pillow (PIL Fork) Documentation.** Alex Clark and Contributors. https://pillow.readthedocs.io/

3. **CustomTkinter Documentation.** Tom Schimansky. https://customtkinter.tomschimansky.com/

4. **Click Documentation.** Pallets Projects. https://click.palletsprojects.com/

5. **piexif Documentation.** hMatoba. https://piexif.readthedocs.io/

6. **PyInstaller Manual.** PyInstaller Development Team. https://pyinstaller.org/en/stable/

7. **pytest Documentation.** pytest Development Team. https://docs.pytest.org/

8. **EXIF Standard.** Japan Electronics and Information Technology Industries Association. JEITA CP-3451C (Exif 2.32).

9. **ICO File Format.** Microsoft Corporation. https://learn.microsoft.com/en-us/previous-versions/ms997538(v=msdn.10)

10. **WebP Documentation.** Google Developers. https://developers.google.com/speed/webp

11. **AVIF Format.** Alliance for Open Media. https://aomediacodec.github.io/av1-avif/

12. **JPEG Standard.** ISO/IEC 10918-1:1994 — Digital compression and coding of continuous-tone still images.

13. **PNG Specification.** W3C. https://www.w3.org/TR/png/

14. **Python Packaging User Guide.** Python Packaging Authority. https://packaging.python.org/

15. **Software Engineering: A Practitioner's Approach.** Roger S. Pressman, Bruce R. Maxim. McGraw-Hill Education.

---

## 10. Internal Guide's Report

*(This section is to be filled by the Internal Guide)*

| Field | Details |
|-------|---------|
| Student Name | Hency Prajapati |
| Project Title | Image Optimizer - A Desktop Image Optimization Tool for Web Developers |
| Guide Name | |
| Guide Signature | |
| Date | |

### Guide's Remarks:

*(To be filled by the Internal Guide)*

---

---

*This report was prepared as part of the academic project submission for Image Optimizer v1.0.0.*
*Developer: Hency Prajapati | Organization: Known Click Technologies*
