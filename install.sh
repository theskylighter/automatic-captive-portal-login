#!/bin/bash

# Captive Portal Auto-Login - One-Command Bootstrap Installer
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.sh)
#    or: bash install.sh

set -e

echo ""
echo "============================================================"
echo "   Captive Portal Auto-Login - Installation"
echo "============================================================"
echo ""

# Detect if we're running from curl or local file
REPO_URL="https://github.com/theskylighter/automatic-captive-portal-login.git"
INSTALL_DIR="${HOME}/.captive-portal-login"

# Check if repo is already cloned (running locally)
if [ -d ".git" ] && [ -f "install/install.py" ]; then
    echo "[OK] Running from local repository"
    INSTALL_DIR=$(pwd)
else
    # Clone from GitHub
    echo "[*] Cloning repository..."

    if ! command -v git &> /dev/null; then
        echo "[ERROR] Git is not installed"
        echo "Please install Git and try again, or:"
        echo "  1. Download the repository manually"
        echo "  2. Run: python3 install/install.py"
        exit 1
    fi

    # Remove existing directory to ensure fresh install
    if [ -d "$INSTALL_DIR" ]; then
        echo "[*] Removing old version..."
        rm -rf "$INSTALL_DIR"
    fi

    git clone "$REPO_URL" "$INSTALL_DIR"
    echo "[OK] Repository cloned to $INSTALL_DIR"

    cd "$INSTALL_DIR"
fi

# Verify required files
if [ ! -f "install/install.py" ]; then
    echo "[ERROR] Installation files not found"
    exit 1
fi

echo ""
echo "[*] Running setup..."
echo ""

# Run the main installer
if ! python3 install/install.py; then
    echo ""
    echo "[ERROR] Installation failed. See errors above."
    exit 1
fi

echo ""
echo "============================================================"
echo "              Installation Complete!"
echo "============================================================"
echo ""
echo "Project location: $INSTALL_DIR"
echo ""
echo "To run the script:"
echo "   bash linux/login.sh"
echo ""
echo "For more information: cat README.md"
echo ""
