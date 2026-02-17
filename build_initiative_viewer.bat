@echo off
REM Build Initiative Viewer Executable
REM This script builds a standalone Windows executable for the Initiative Viewer

echo ============================================================
echo Building Initiative Viewer Executable
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "Obeya\Scripts\activate.bat" (
    echo Found virtual environment, activating...
    call ..\Obeya\Scripts\activate.bat
) else if exist "..\Obeya\Scripts\activate.bat" (
    echo Found virtual environment in parent directory, activating...
    call ..\Obeya\Scripts\activate.bat
) else (
    echo WARNING: No virtual environment found
    echo Using system Python...
)

echo.
echo Installing/Checking dependencies...
python -m pip install -r requirements.txt --quiet

echo.
echo Running build script...
python build_initiative_viewer.py

echo.
echo ============================================================
echo Build Complete!
echo ============================================================
echo.
echo The executable can be found in the 'dist' folder
echo.
pause
