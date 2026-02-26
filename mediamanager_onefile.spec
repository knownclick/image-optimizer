# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Image Optimizer — single-file .exe build.

Produces one standalone .exe (larger, slower startup, but easy to distribute).
Run: pyinstaller mediamanager_onefile.spec
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
    a.binaries,
    a.datas,
    [],
    name="ImageOptimizer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # Console visible for CLI usage; hides automatically when --gui used
    icon=None,      # Set to "assets/icon.ico" if you have one
)
