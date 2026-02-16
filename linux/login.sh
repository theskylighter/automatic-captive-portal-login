#!/bin/bash

# Captive Portal Auto-Login for Linux/macOS
# This script runs the login.py from the src folder

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Verify Python is available
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "❌ Error: Python 3 not found!"
    echo ""
    echo "Please install Python 3.6+ first."
    echo "On Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "On macOS: brew install python3"
    echo ""
    exit 1
fi

# Load .env file if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
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

