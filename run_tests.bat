@echo off
REM Run Initiative Viewer Tests
REM Quick script to run the test suite

echo ============================================================
echo Initiative Viewer - Test Suite
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "..\Obeya\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ..\Obeya\Scripts\activate.bat
)

echo.
echo Installing/Checking test dependencies...
python -m pip install -r requirements-test.txt --quiet

echo.
echo ============================================================
echo Running Tests
echo ============================================================
echo.

REM Run tests with different options based on argument
if "%1"=="coverage" (
    echo Running tests with coverage report...
    pytest tests\test_initiative_viewer.py -v --cov=. --cov-report=html --cov-report=term
    echo.
    echo Coverage report generated in htmlcov\index.html
) else if "%1"=="quick" (
    echo Running quick tests...
    pytest tests\test_initiative_viewer.py -v --tb=short
) else if "%1"=="pdf" (
    echo Running PDF generation tests only...
    pytest tests\test_initiative_viewer.py::TestPDFGeneration -v
) else if "%1"=="web" (
    echo Running web interface tests only...
    pytest tests\test_initiative_viewer.py::TestWebInterface -v
) else (
    echo Running all tests...
    pytest tests\test_initiative_viewer.py -v
)

echo.
echo ============================================================
echo Test Run Complete!
echo ============================================================
echo.
echo Usage:
echo   run_tests.bat          - Run all tests
echo   run_tests.bat quick    - Run tests without detailed output
echo   run_tests.bat coverage - Run tests with coverage report
echo   run_tests.bat pdf      - Run only PDF generation tests
echo   run_tests.bat web      - Run only web interface tests
echo.
pause
