#!/bin/bash

# Captive Portal Auto-Login - One-Command Bootstrap Installer
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/user/repo/main/install.sh)
#    or: bash install.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      Captive Portal Auto-Login - Installation             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect if we're running from curl or local file
REPO_URL="https://github.com/theskylighter/automatic-captive-portal-login.git"
INSTALL_DIR="${HOME}/.captive-portal-login"

# Check if repo is already cloned (running locally)
if [ -d ".git" ] && [ -f "install/install.py" ]; then
    echo -e "${GREEN}✅ Running from local repository${NC}"
    INSTALL_DIR=$(pwd)
else
    # Clone from GitHub
    echo -e "${BLUE}📥 Cloning repository...${NC}"
    
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git is not installed${NC}"
        echo "Please install Git and try again, or:"
        echo "  1. Download the repository manually"
        echo "  2. Run: python3 install/install.py"
        exit 1
    fi
    
    # Check if directory already exists
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${BLUE}📁 Repository already exists at $INSTALL_DIR${NC}"
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
        echo -e "${GREEN}✅ Repository cloned to $INSTALL_DIR${NC}"
    fi
    
    cd "$INSTALL_DIR"
fi

# Verify required files
if [ ! -f "install/install.py" ]; then
    echo -e "${RED}❌ Installation files not found${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🔧 Running setup...${NC}"
echo ""

# Run the main installer
python3 install/install.py

echo ""
echo -e "${GREEN}═════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}              ✅ Installation Complete!${NC}"
echo -e "${GREEN}═════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📍 Project location: $INSTALL_DIR"
echo ""
echo "🚀 To run the script:"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "   ./linux/login.sh"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   ./linux/login.sh"
fi
echo ""
echo "📚 For more information: cat README.md"
echo ""
