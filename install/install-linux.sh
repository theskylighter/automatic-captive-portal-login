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

# Get credentials
echo ""
echo "======================================"
echo "Configure Credentials"
echo "======================================"
echo ""

read -p "Enter your campus network username: " USERNAME
read -sp "Enter your campus network password: " PASSWORD
echo ""

# Create .env file
cat > .env << EOF
# Captive Portal Credentials
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

CAPTIVE_PORTAL_USERNAME="$USERNAME"
CAPTIVE_PORTAL_PASSWORD="$PASSWORD"
EOF

# Restrict permissions on .env file
chmod 600 .env

echo "✅ Credentials saved to .env file"

# Add to .gitignore if not present
if ! grep -q "\.env" .gitignore; then
    echo "" >> .gitignore
    echo "# Environment variables" >> .gitignore
    echo ".env" >> .gitignore
    echo "✅ Added .env to .gitignore"
fi

# Optional: Set up cron job
echo ""
echo "======================================"
echo "Optional: Cron Job Setup"
echo "======================================"
read -p "Would you like to set up a cron job? (y/n): " response

if [[ "$response" == "y" || "$response" == "Y" ]]; then
    PROJECT_PATH="$(pwd)"
    CRON_COMMAND="0 7 * * * $PROJECT_PATH/linux/login.sh >> $PROJECT_PATH/log/auto-login.log 2>&1"
    
    echo ""
    echo "Add this line to your crontab (crontab -e):"
    echo "$CRON_COMMAND"
    echo ""
    echo "This will run the script daily at 7:00 AM"
    echo "To edit crontab: crontab -e"
fi

echo ""
echo "======================================"
echo "✅ Installation Complete!"
echo "======================================"
echo ""
echo "You can now run the script with:"
echo "  ./linux/login.sh"
echo ""
