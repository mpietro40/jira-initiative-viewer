@echo off
echo ========================================
echo  Initiative Viewer - Starting...
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "C:\Users\a788055\GITREPO\JiraObeya\Obeya\Scripts\activate.bat" (
    echo Activating virtual environment...
    call C:\Users\a788055\GITREPO\JiraObeya\Obeya\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Using system Python...
)

echo.
echo Checking dependencies...
pip install -q -r requirements_initiative_viewer.txt

echo.
echo ========================================
echo  Starting Initiative Viewer
echo  Access at: http://localhost:5001
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python initiative_viewer.py

pause
