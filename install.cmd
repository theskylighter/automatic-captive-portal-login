@echo off
REM Captive Portal Auto-Login - One-Command Bootstrap Installer
REM Usage: powershell -Command "iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/user/repo/main/install.cmd')"
REM    or: install.cmd

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Captive Portal Auto-Login - Installation
echo ============================================================
echo.

REM Check if running locally or from download
if exist ".git" (
    if exist "install\install.py" (
        echo [OK] Running from local repository
        set "INSTALL_DIR=%cd%"
        goto :run_installer
    )
)

REM Clone from GitHub
echo [*] Cloning repository...

set "REPO_URL=https://github.com/theskylighter/automatic-captive-portal-login.git"
set "INSTALL_DIR=%USERPROFILE%\.captive-portal-login"

REM Check if git is installed
where git >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Git is not installed
    echo Please install Git and try again, or:
    echo   1. Download the repository manually
    echo   2. Run: python install\install.py
    pause
    exit /b 1
)

REM Clone repository
if exist "!INSTALL_DIR!" (
    echo [*] Repository already exists at !INSTALL_DIR!
) else (
    git clone "!REPO_URL!" "!INSTALL_DIR!"
    if errorlevel 1 (
        echo [ERROR] Failed to clone repository
        pause
        exit /b 1
    )
    echo [OK] Repository cloned to !INSTALL_DIR!
)

cd /d "!INSTALL_DIR!"

:run_installer
REM Verify installation files exist
if not exist "install\install.py" (
    echo [ERROR] Installation files not found
    pause
    exit /b 1
)

echo.
echo [*] Running setup...
echo.

REM Try to find Python executable (works across different Python installations)
for %%i in (python.exe python py.exe) do (
    %%i --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=%%i"
        goto :found_python
    )
)

:python_not_found
echo [ERROR] Python not found in PATH!
echo.
echo Please install Python 3.6+ or add it to your system PATH
echo Download from: https://www.python.org/downloads/
echo.
pause
exit /b 1

:found_python
REM Run the main installer
%PYTHON_CMD% install\install.py

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo                 Installation Complete!
echo ============================================================
echo.
echo Project location: !INSTALL_DIR!
echo.
echo To run the script:
echo   windows\autologin.bat
echo.
echo For more information: type README.md
echo.
pause
