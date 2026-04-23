#!/bin/bash
echo "--- HockeyMatch AI: Starting ---"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python."
    read -p "Press enter to exit"
    exit 1
fi

# 2. Check/Create venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || { echo "Failed to create venv"; read -p "Press enter to exit"; exit 1; }
fi

# 3. Activate
source venv/bin/activate || { echo "Failed to activate venv"; read -p "Press enter to exit"; exit 1; }

# 4. Install
echo "Checking requirements..."
pip install -r requirements.txt

# 5. Run
echo "Launching application on http://127.0.0.1:5001"
python3 app.py

if [ $? -ne 0 ]; then
    echo "ERROR: Application crashed."
fi

read -p "Press enter to exit"
