#!/bin/bash

# Captive Portal Auto-Login for Linux
# This script runs the login.py from the src folder

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate Python environment if needed (uncomment if using venv)
# source "$PROJECT_ROOT/venv/bin/activate"

# Run the Python script
python3 "$PROJECT_ROOT/src/login.py"
