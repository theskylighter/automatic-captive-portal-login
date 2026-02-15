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

REM Get credentials
echo.
echo ======================================
echo Configure Credentials
echo ======================================
echo.
set /p USERNAME="Enter your campus network username: "
set /p PASSWORD="Enter your campus network password: "

REM Create .env file
echo # Captive Portal Credentials > .env
echo # DO NOT COMMIT THIS FILE TO VERSION CONTROL >> .env
echo. >> .env
echo CAPTIVE_PORTAL_USERNAME="%USERNAME%" >> .env
echo CAPTIVE_PORTAL_PASSWORD="%PASSWORD%" >> .env

echo ✅ Credentials saved to .env file

REM Add to .gitignore if not present
findstr /M "\.env" .gitignore >nul 2>&1
if errorlevel 1 (
    echo. >> .gitignore
    echo # Environment variables >> .gitignore
    echo .env >> .gitignore
    echo ✅ Added .env to .gitignore
)

echo.
echo ✅ Installation complete!
echo.
echo You can now run: windows\autologin.bat
echo.
echo To set up Task Scheduler:
echo 1. Press Win+S and search for 'Task Scheduler'
echo 2. Create a new task to run windows\autologin.bat periodically
echo.
pause

