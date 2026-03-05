#!/usr/bin/env bash
# Quick-start script for Image Optimizer
# Usage: ./setup.sh          — Install and launch the GUI
#        ./setup.sh --cli    — Install only (no GUI launch)
#
# Created by Hency Prajapati (Known Click Technologies)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Find python3
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Error: Python 3.10+ is required but not found."
    echo "Install it from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$($PYTHON -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$($PYTHON -c 'import sys; print(sys.version_info.minor)')

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "Error: Python 3.10+ is required (found $PY_VERSION)"
    exit 1
fi

echo "==================================================="
echo "  Image Optimizer — Quick Setup"
echo "  Python $PY_VERSION"
echo "==================================================="

# Create venv if needed
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "[1/3] Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
else
    echo ""
    echo "[1/3] Virtual environment already exists."
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "[2/3] Installing dependencies..."
pip install -e "$SCRIPT_DIR" --quiet 2>/dev/null
pip install pillow-avif-plugin --quiet 2>/dev/null || true

echo "[3/3] Setup complete!"
echo ""
echo "Usage:"
echo "  source .venv/bin/activate"
echo "  python -m image_optimizer --gui          # Launch GUI"
echo "  python -m image_optimizer --help         # Show CLI help"
echo ""

# Launch GUI unless --cli flag was passed
if [ "$1" != "--cli" ]; then
    echo "Launching GUI..."
    python -m image_optimizer --gui
fi
