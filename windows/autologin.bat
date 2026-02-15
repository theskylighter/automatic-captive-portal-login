@echo off
REM Captive Portal Auto-Login for Windows
REM This script runs the login.py from the src folder

cd /d "%~dp0\.."
python.exe "src\login.py"

REM If you want to keep the window open to see output, uncomment the next line:
REM pause
