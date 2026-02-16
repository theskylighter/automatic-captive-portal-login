@echo off
REM Captive Portal Auto-Login for Windows
REM This script runs the login.py from the src folder

cd /d "%~dp0\.."

REM Try to find Python executable (works across different Python installations)
for %%i in (python.exe python py.exe) do (
    %%i --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=%%i"
        goto :found_python
    )
)

:python_not_found
echo.
echo ❌ Error: Python not found in PATH!
echo.
echo Please install Python 3.6+ or add it to your system PATH
echo Download from: https://www.python.org/downloads/
echo.
pause
exit /b 1

:found_python
REM Load .env file if it exists
if exist .env (
    for /f "usebackq delims== tokens=1,*" %%A in (.env) do (
        if not "%%A"=="" (
            if not "%%A:~0,1%%"=="#" (
                set "%%A=%%B"
            )
        )
    )
)

REM Check if credentials are set
if not defined CAPTIVE_PORTAL_USERNAME (
    echo.
    echo ❌ Error: Credentials not configured!
    echo.
    echo Please run: python install\install.py
    echo.
    pause
    exit /b 1
)

REM Run the Python script
%PYTHON_CMD% "src\login.py"

REM If you want to keep the window open to see output, uncomment the next line:
REM pause

