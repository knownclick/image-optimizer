@echo off
REM ============================================================
REM  Image Optimizer — Windows Build Script
REM  Created by Hency Prajapati (Known Click Technologies)
REM
REM  Usage:
REM    build_windows.bat            Build folder distribution
REM    build_windows.bat onefile    Build single .exe file
REM    build_windows.bat clean      Remove build artifacts
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo  Image Optimizer Build Script
echo  ============================
echo.

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+ and add it to PATH.
    exit /b 1
)

REM Check we're in the right directory
if not exist "image_optimizer\__init__.py" (
    echo ERROR: Run this script from the project root directory.
    exit /b 1
)

REM Handle 'clean' argument
if "%1"=="clean" (
    echo Cleaning build artifacts...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    echo Done.
    exit /b 0
)

REM Install dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt -r requirements-build.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    exit /b 1
)

REM Install the package itself in editable mode
pip install -e . --quiet
if errorlevel 1 (
    echo ERROR: Failed to install image_optimizer package.
    exit /b 1
)

REM Choose spec file
if "%1"=="onefile" (
    set SPEC=mediamanager_onefile.spec
    echo [2/3] Building single-file executable...
) else (
    set SPEC=mediamanager.spec
    echo [2/3] Building folder distribution...
)

REM Run PyInstaller
pyinstaller --clean --noconfirm !SPEC!
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed.
    exit /b 1
)

echo.
echo [3/3] Build complete!
echo.

if "%1"=="onefile" (
    echo Output: dist\ImageOptimizer.exe
    echo.
    echo To run: dist\ImageOptimizer.exe --gui
) else (
    echo Output: dist\ImageOptimizer\ImageOptimizer.exe
    echo.
    echo To run: dist\ImageOptimizer\ImageOptimizer.exe --gui
    echo.
    echo To distribute: zip the dist\ImageOptimizer folder.
)

echo.
echo CLI usage:  ImageOptimizer.exe convert input.jpg output.png -f png
echo GUI usage:  ImageOptimizer.exe --gui
echo.
