@echo off
REM Captive Portal Auto-Login - Windows Installer
REM This script sets up the application on Windows

echo.
echo ======================================
echo Captive Portal Auto-Login - Installation
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.x from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install requirements
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Create Task Scheduler entry
echo.
echo Setting up Task Scheduler entry...
echo Note: You may need to run this installer as Administrator for Task Scheduler setup
REM TODO: Add Task Scheduler setup command here

echo.
echo ✅ Installation complete!
echo.
echo Next steps:
echo 1. Edit src\login.py and update USERNAME and PASSWORD with your credentials
echo 2. Run windows\autologin.bat to test the script
echo.
pause
