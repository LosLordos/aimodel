#!/bin/bash
echo "--- HockeyMatch AI: Starting ---"

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
echo "Checking requirements..."
pip install -r requirements.txt

# Run the app
echo "Launching application on http://127.0.0.1:5001"
python app.py
