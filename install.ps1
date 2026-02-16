# Captive Portal Auto-Login - PowerShell Installer
# Usage: powershell -Command "iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.ps1')"
#    or: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      Captive Portal Auto-Login - Installation             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if running locally or from download
if ((Test-Path ".git") -and (Test-Path "install\install.py")) {
    Write-Host "✅ Running from local repository"
    $installDir = Get-Location
} else {
    # Set installation directory
    $repoUrl = "https://github.com/theskylighter/automatic-captive-portal-login.git"
    $installDir = Join-Path $env:USERPROFILE ".captive-portal-login"

    # Check if git is installed
    try {
        $null = git --version 2>$null
    } catch {
        Write-Host "❌ Git is not installed" -ForegroundColor Red
        Write-Host "Please install Git and try again, or:" -ForegroundColor Yellow
        Write-Host "  1. Download the repository manually from $repoUrl"
        Write-Host "  2. Extract and run: python install\install.py"
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Clone repository if not exists
    if (Test-Path $installDir) {
        Write-Host "📁 Repository already exists at $installDir"
    } else {
        Write-Host "📥 Cloning repository..."
        try {
            git clone $repoUrl $installDir
            Write-Host "✅ Repository cloned to $installDir"
        } catch {
            Write-Host "❌ Failed to clone repository" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }

    Set-Location $installDir
}

# Verify installation files exist
if (-not (Test-Path "install\install.py")) {
    Write-Host "❌ Installation files not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🔧 Running setup..."
Write-Host ""

# Run the main installer
try {
    python install\install.py
    if ($LASTEXITCODE -ne 0) {
        throw "Installer exited with code $LASTEXITCODE"
    }
} catch {
    Write-Host ""
    Write-Host "❌ Installation failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "═════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "                 ✅ Installation Complete!" -ForegroundColor Green
Write-Host "═════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Project location: $installDir"
Write-Host ""
Write-Host "🚀 To run the script:"
Write-Host "   windows\autologin.bat"
Write-Host ""
Write-Host "📚 For more information: type README.md"
Write-Host ""
Read-Host "Press Enter to exit"
