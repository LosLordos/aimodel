@echo off
setlocal
echo --- HockeyMatch AI: Starting ---

:: 1. Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from python.org
    pause
    exit /b
)

:: 2. Check/Create Virtual Environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b
    )
)

:: 3. Activate Virtual Environment
echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b
)

:: 4. Install Dependencies
echo Checking/Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo WARNING: Some requirements failed to install.
)

:: 5. Run the Application
echo Launching application...
echo ---------------------------------------
echo Open your browser at: http://127.0.0.1:5001
echo ---------------------------------------
python app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: The application crashed with exit code %errorlevel%.
)

pause
