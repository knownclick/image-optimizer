@echo off
REM Quick-start script for Image Optimizer (Windows)
REM Usage: setup.bat          — Install and launch the GUI
REM        setup.bat --cli    — Install only (no GUI launch)
REM
REM Created by Hency Prajapati (Known Click Technologies)

setlocal

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"

REM Find Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3.10+ is required but not found.
    echo Install it from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    exit /b 1
)

REM Check Python version
for /f "tokens=*" %%v in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PY_VERSION=%%v
for /f "tokens=*" %%v in ('python -c "import sys; print(sys.version_info.major)"') do set PY_MAJOR=%%v
for /f "tokens=*" %%v in ('python -c "import sys; print(sys.version_info.minor)"') do set PY_MINOR=%%v

if %PY_MAJOR% lss 3 (
    echo Error: Python 3.10+ is required (found %PY_VERSION%)
    exit /b 1
)
if %PY_MAJOR% equ 3 if %PY_MINOR% lss 10 (
    echo Error: Python 3.10+ is required (found %PY_VERSION%)
    exit /b 1
)

echo ===================================================
echo   Image Optimizer — Quick Setup
echo   Python %PY_VERSION%
echo ===================================================

REM Create venv if needed
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo.
    echo [1/3] Creating virtual environment...
    python -m venv "%VENV_DIR%"
) else (
    echo.
    echo [1/3] Virtual environment already exists.
)

REM Activate venv
call "%VENV_DIR%\Scripts\activate.bat"

REM Install dependencies
echo [2/3] Installing dependencies...
pip install -e "%SCRIPT_DIR%." --quiet 2>nul
pip install pillow-avif-plugin --quiet 2>nul

echo [3/3] Setup complete!
echo.
echo Usage:
echo   .venv\Scripts\activate
echo   python -m image_optimizer --gui          — Launch GUI
echo   python -m image_optimizer --help         — Show CLI help
echo.

REM Launch GUI unless --cli flag was passed
if "%1" neq "--cli" (
    echo Launching GUI...
    python -m image_optimizer --gui
)
