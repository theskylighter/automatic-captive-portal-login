# Captive Portal Auto-Login - PowerShell Installer
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -Command "iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.ps1')"

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "      Captive Portal Auto-Login - Installation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$repoUrl = "https://github.com/theskylighter/automatic-captive-portal-login.git"
$installDir = Join-Path $env:USERPROFILE ".captive-portal-login"

# Check if running locally
if ((Test-Path ".git") -and (Test-Path "install\install.py")) {
    Write-Host "[OK] Running from local repository"
} else {
    # Check if git is installed
    git --version 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Git is not installed" -ForegroundColor Red
        Write-Host "Please install Git: https://git-scm.com/download/win" -ForegroundColor Yellow
        exit 1
    }

    # Clone repository if not exists
    if (Test-Path $installDir) {
        Write-Host "[DIR] Repository already exists at $installDir"
    } else {
        Write-Host "[DOWNLOAD] Cloning repository..."
        & git clone $repoUrl $installDir
        Write-Host "[OK] Repository cloned to $installDir"
    }

    Set-Location $installDir
}

# Verify installation files exist
if (-not (Test-Path "install\install.py")) {
    Write-Host "[ERROR] Installation files not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[SETUP] Running setup..."
Write-Host ""

# Run the main installer
& python install\install.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Installation failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                 Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "[INFO] Project location: $installDir"
Write-Host ""
Write-Host "[RUN] To run the script:"
Write-Host "   windows\autologin.bat"
Write-Host ""
Write-Host "[DOCS] For more information: type README.md"
Write-Host ""
