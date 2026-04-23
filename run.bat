@echo off
echo --- HockeyMatch AI: Starting ---

:: Check if venv exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate and install dependencies
call venv\Scripts\activate
echo Checking requirements...
pip install -r requirements.txt

:: Run the app
echo Launching application on http://127.0.0.1:5001
python app.py
pause
