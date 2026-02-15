#!/bin/bash

# Captive Portal Auto-Login for Linux/macOS
# This script runs the login.py from the src folder

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load .env file if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Check if credentials are set
if [ -z "$CAPTIVE_PORTAL_USERNAME" ]; then
    echo ""
    echo "❌ Error: Credentials not configured!"
    echo ""
    echo "Please run: python3 install/install.py"
    echo ""
    exit 1
fi

# Activate Python environment if needed (uncomment if using venv)
# source "$PROJECT_ROOT/venv/bin/activate"

# Run the Python script
python3 "$PROJECT_ROOT/src/login.py"

