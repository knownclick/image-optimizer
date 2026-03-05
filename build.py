#!/usr/bin/env python3
"""Cross-platform build script for Image Optimizer.

Usage:
    python build.py                 # Build folder distribution
    python build.py --onefile       # Build single executable
    python build.py --clean         # Remove build artifacts
    python build.py --install-deps  # Only install dependencies

Automatically creates a virtual environment if needed.
Works on Windows, macOS, and Linux.
Created by Hency Prajapati (Known Click Technologies)
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
VENV_DIR = PROJECT_ROOT / ".venv"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and print it."""
    print(f"  > {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def _get_venv_python() -> str:
    """Return the path to the venv Python executable."""
    if sys.platform == "win32":
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python3")


def _get_venv_pip() -> list[str]:
    """Return the pip command for the venv."""
    return [_get_venv_python(), "-m", "pip"]


def ensure_venv():
    """Create a virtual environment if one doesn't exist, and re-exec inside it."""
    venv_python = _get_venv_python()

    # If we're already in the venv, nothing to do
    if sys.prefix != sys.base_prefix:
        return

    # If venv exists and has a working python, re-exec into it
    if Path(venv_python).exists():
        print(f"    Using existing venv: {VENV_DIR}")
        os.execv(venv_python, [venv_python] + sys.argv)

    # Create venv
    print(f"\n[0] Creating virtual environment at {VENV_DIR}...")
    try:
        run([sys.executable, "-m", "venv", str(VENV_DIR)])
    except subprocess.CalledProcessError:
        # ensurepip not available — create without pip, then bootstrap
        print("    ensurepip not available, creating venv without pip...")
        run([sys.executable, "-m", "venv", "--without-pip", str(VENV_DIR)])
        print("    Bootstrapping pip...")
        import urllib.request
        get_pip = PROJECT_ROOT / "get-pip.py"
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", str(get_pip))
        run([venv_python, str(get_pip), "--quiet"])
        get_pip.unlink(missing_ok=True)

    print(f"    Venv created. Re-launching build inside venv...")
    os.execv(venv_python, [venv_python] + sys.argv)


def install_deps():
    """Install all dependencies including PyInstaller."""
    print("\n[1] Installing dependencies...")
    pip = _get_venv_pip()
    run([*pip, "install", "-r", "requirements.txt", "--quiet"])
    run([*pip, "install", "-r", "requirements-build.txt", "--quiet"])
    run([*pip, "install", "-e", ".", "--quiet"])
    print("    Dependencies installed.")


def clean():
    """Remove build artifacts."""
    print("\nCleaning build artifacts...")
    for d in [BUILD_DIR, DIST_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"    Removed {d}")
    print("    Done.")


def build(onefile: bool = False):
    """Build the executable with PyInstaller."""
    spec = "mediamanager_onefile.spec" if onefile else "mediamanager.spec"
    mode = "single-file" if onefile else "folder"

    print(f"\n[2] Building {mode} distribution...")
    run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", spec])

    print(f"\n[3] Build complete!")
    if onefile:
        if sys.platform == "win32":
            exe = DIST_DIR / "ImageOptimizer.exe"
        else:
            exe = DIST_DIR / "ImageOptimizer"
        print(f"    Output: {exe}")
    else:
        out_dir = DIST_DIR / "ImageOptimizer"
        if sys.platform == "win32":
            exe = out_dir / "ImageOptimizer.exe"
        else:
            exe = out_dir / "ImageOptimizer"
        print(f"    Output: {out_dir}/")
        print(f"    Executable: {exe}")

    print(f"\n    CLI usage:  {exe.name} convert input.jpg output.png -f png")
    print(f"    GUI usage:  {exe.name} --gui")


def main():
    parser = argparse.ArgumentParser(description="Build Image Optimizer executable")
    parser.add_argument("--onefile", action="store_true", help="Build single .exe file")
    parser.add_argument("--clean", action="store_true", help="Remove build artifacts")
    parser.add_argument("--install-deps", action="store_true", help="Only install dependencies")
    args = parser.parse_args()

    print("=" * 50)
    print("  Image Optimizer Build Script")
    print("  Hency Prajapati (Known Click Technologies)")
    print("=" * 50)

    if args.clean:
        clean()
        return

    ensure_venv()
    install_deps()

    if args.install_deps:
        return

    build(onefile=args.onefile)


if __name__ == "__main__":
    main()
