# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Image Optimizer.

Builds a single-folder distribution with all dependencies bundled.
Run: pyinstaller mediamanager.spec
"""

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect CustomTkinter assets (themes, images)
ctk_datas = collect_data_files("customtkinter")

# Collect all mediamanager submodules
mm_hiddenimports = collect_submodules("mediamanager")

# Optional: pillow-avif-plugin
try:
    import pillow_avif
    avif_imports = ["pillow_avif"]
except ImportError:
    avif_imports = []

a = Analysis(
    ["mediamanager/__main__.py"],
    pathex=[],
    binaries=[],
    datas=ctk_datas,
    hiddenimports=[
        *mm_hiddenimports,
        "PIL",
        "PIL.Image",
        "PIL.ExifTags",
        "PIL.IcoImagePlugin",
        "PIL.JpegImagePlugin",
        "PIL.PngImagePlugin",
        "PIL.WebPImagePlugin",
        "PIL.BmpImagePlugin",
        "PIL.GifImagePlugin",
        "PIL._tkinter_finder",
        "piexif",
        "click",
        "customtkinter",
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        *avif_imports,
    ],
    hookspath=["hooks"],
    hooksconfig={},
    runtime_hooks=["hooks/rthook_ctk_fix.py"],
    excludes=[
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "IPython",
        "notebook",
        "pytest",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ImageOptimizer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,   # Console visible for CLI usage; hides automatically when --gui used
    icon=None,      # Set to "assets/icon.ico" if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ImageOptimizer",
)
