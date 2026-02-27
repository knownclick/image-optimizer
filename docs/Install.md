# Installation Guide

Step-by-step instructions for installing, building, and running Image Optimizer on macOS, Windows, and Linux.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [macOS](#macos)
  - [Windows](#windows)
  - [Linux](#linux)
- [Running the Application](#running-the-application)
- [Building a Standalone Binary](#building-a-standalone-binary)
  - [Build on macOS](#build-on-macos)
  - [Build on Windows](#build-on-windows)
  - [Build on Linux](#build-on-linux)
- [Optional: AVIF Support](#optional-avif-support)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.10 or later** — Download from [python.org](https://www.python.org/downloads/)
- **pip** — Comes bundled with Python 3.10+
- **git** — For cloning the repository

Verify your Python installation:

```bash
python --version    # Should show 3.10 or higher
pip --version
```

> On some systems, use `python3` and `pip3` instead of `python` and `pip`.

---

## Installation

### macOS

1. **Install Python** (if not already installed):

   ```bash
   # Using Homebrew (recommended)
   brew install python@3.12

   # Or download from python.org
   ```

2. **Clone the repository:**

   ```bash
   git clone https://github.com/knownclick/image-optimizer.git
   cd image-optimizer
   ```

3. **Create a virtual environment and install:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

4. **Verify installation:**

   ```bash
   python -m mediamanager --version
   ```

### Windows

1. **Install Python:**

   Download Python 3.12+ from [python.org](https://www.python.org/downloads/windows/). During installation, check **"Add Python to PATH"**.

2. **Open Command Prompt or PowerShell:**

   ```cmd
   git clone https://github.com/knownclick/image-optimizer.git
   cd image-optimizer
   ```

3. **Create a virtual environment and install:**

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e .
   ```

4. **Verify installation:**

   ```cmd
   python -m mediamanager --version
   ```

### Linux

1. **Install Python and Tkinter:**

   ```bash
   # Ubuntu / Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv python3-tk

   # Fedora
   sudo dnf install python3 python3-pip python3-tkinter

   # Arch
   sudo pacman -S python python-pip tk
   ```

2. **Clone the repository:**

   ```bash
   git clone https://github.com/knownclick/image-optimizer.git
   cd image-optimizer
   ```

3. **Create a virtual environment and install:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

4. **Verify installation:**

   ```bash
   python -m mediamanager --version
   ```

> **Note:** Linux requires `python3-tk` (or equivalent) for the GUI. The CLI works without it.

---

## Running the Application

### Launch the GUI

```bash
# Activate the virtual environment first
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

python -m mediamanager --gui
```

### Use the CLI

```bash
python -m mediamanager --help
python -m mediamanager convert photo.jpg photo.webp -f webp
```

See [CLI.md](CLI.md) for the full command reference.

---

## Building a Standalone Binary

Build a single-file executable that runs without Python installed. Useful for distributing to team members or deploying on machines without a Python environment.

### Using the build script (recommended)

The included `build.py` script handles everything automatically — venv creation, dependency installation, and PyInstaller packaging. It works on all platforms:

```bash
python build.py              # Folder distribution (faster startup)
python build.py --onefile    # Single executable (easier to distribute)
python build.py --clean      # Remove build artifacts
python build.py --install-deps  # Only install dependencies (no build)
```

The script will create a virtual environment if needed and re-launch itself inside it.

### Manual build

If you prefer to build manually:

#### Install build dependencies

```bash
pip install -r requirements-build.txt
```

This installs PyInstaller and any other build-time dependencies.

#### Build on macOS

```bash
source .venv/bin/activate
pyinstaller --clean --noconfirm mediamanager_onefile.spec
```

The binary is created at `dist/ImageOptimizer`. To run it:

```bash
./dist/ImageOptimizer --gui       # Launch GUI
./dist/ImageOptimizer --help      # Show CLI help
```

To make it accessible system-wide:

```bash
cp dist/ImageOptimizer /usr/local/bin/image-optimizer
```

#### Build on Windows

```cmd
.venv\Scripts\activate
pyinstaller --clean --noconfirm mediamanager_onefile.spec
```

The executable is created at `dist\ImageOptimizer.exe`. To run it:

```cmd
dist\ImageOptimizer.exe --gui
dist\ImageOptimizer.exe --help
```

Double-click `ImageOptimizer.exe` to launch the GUI directly (a console window will appear briefly — this is normal).

#### Build on Linux

```bash
source .venv/bin/activate
pyinstaller --clean --noconfirm mediamanager_onefile.spec
```

The binary is created at `dist/ImageOptimizer`. To run it:

```bash
chmod +x dist/ImageOptimizer
./dist/ImageOptimizer --gui
```

To install system-wide:

```bash
sudo cp dist/ImageOptimizer /usr/local/bin/image-optimizer
```

### Build output

| Platform | Output | Size (approx.) |
|----------|--------|----------------|
| macOS | `dist/ImageOptimizer` | 25-35 MB |
| Windows | `dist\ImageOptimizer.exe` | 25-35 MB |
| Linux | `dist/ImageOptimizer` | 25-35 MB |

> The binary is self-contained. It extracts temporarily on first run, so the first launch takes a few seconds longer.

---

## Optional: AVIF Support

AVIF is a modern image format with excellent compression. To enable it:

```bash
pip install pillow-avif-plugin
```

After installing, AVIF will be available in both the GUI format dropdowns and the CLI `-f avif` option.

If building a standalone binary, install the plugin before running PyInstaller — it will be bundled automatically.

---

## Troubleshooting

### "command not found: python"

Use `python3` instead of `python`. On some systems (especially macOS and Linux), Python 3 is only available as `python3`.

### GUI won't start — "No module named tkinter"

Install the Tkinter package for your system:

```bash
# Ubuntu / Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (Homebrew Python includes Tkinter by default)
brew reinstall python-tk@3.12
```

### GUI won't start — "No module named customtkinter"

Make sure you installed the project dependencies:

```bash
pip install -e .
```

Or install CustomTkinter directly:

```bash
pip install customtkinter
```

### PyInstaller build fails

Make sure you're using the virtual environment and have the build dependencies:

```bash
source .venv/bin/activate
pip install -r requirements-build.txt
pyinstaller --clean --noconfirm mediamanager_onefile.spec
```

If the build still fails, try upgrading PyInstaller:

```bash
pip install --upgrade pyinstaller
```

### AVIF images not recognized

Install the AVIF plugin:

```bash
pip install pillow-avif-plugin
```

### Permission denied errors on Linux/macOS

If you get permission errors saving files, check that the output directory is writable:

```bash
ls -la /path/to/output/directory
```

### Dark mode looks broken

The application uses CustomTkinter's dark/light theme toggle. If widgets appear invisible or unreadable, try switching themes using the toggle in the top-right corner of the application window.
