#!/bin/bash

# Captive Portal Auto-Login - Linux/macOS Installer
# This script sets up the application on Linux/macOS

echo ""
echo "======================================"
echo "Captive Portal Auto-Login - Installation"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.x using your package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

echo "✅ Python found"
python3 --version

# Install requirements
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x linux/login.sh

# Optional: Set up cron job
echo ""
echo "Would you like to set up a cron job to run this automatically? (y/n)"
read -r response

if [[ "$response" == "y" || "$response" == "Y" ]]; then
    echo "Edit your crontab with: crontab -e"
    echo "Example: Add this line to run daily at 12:00 AM"
    echo "0 0 * * * /path/to/project/linux/login.sh >> /path/to/project/log/auto-login.log 2>&1"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit src/login.py and update USERNAME and PASSWORD with your credentials"
echo "2. Run linux/login.sh to test the script"
echo ""
