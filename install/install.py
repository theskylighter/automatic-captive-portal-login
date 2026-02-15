#!/usr/bin/env python3
"""
Universal installer for Captive Portal Auto-Login
Works on Windows, Linux, and macOS
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def print_header():
    print("\n" + "=" * 50)
    print("Captive Portal Auto-Login - Installation")
    print("=" * 50 + "\n")

def check_python():
    """Verify Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python 3.6+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} found")
    return True

def install_requirements():
    """Install Python packages from requirements.txt"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def make_scripts_executable():
    """Make shell scripts executable on Unix systems"""
    if platform.system() != "Windows":
        print("\nMaking scripts executable...")
        try:
            os.chmod("linux/login.sh", 0o755)
            print("✅ Scripts made executable")
            return True
        except Exception as e:
            print(f"⚠️ Could not make scripts executable: {e}")
            return False
    return True

def setup_cron_on_linux():
    """Offer to set up cron job on Linux"""
    if platform.system() != "Linux":
        return
    
    response = input("\nWould you like to set up a cron job? (y/n): ").strip().lower()
    if response in ["y", "yes"]:
        project_path = os.path.abspath(".")
        cron_command = f"0 0 * * * {project_path}/linux/login.sh >> {project_path}/log/auto-login.log 2>&1"
        print(f"\nAdd this line to your crontab (crontab -e):\n{cron_command}")

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "=" * 50)
    print("✅ Installation Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Edit src/login.py and update credentials:")
    print("   - USERNAME = 'your_username'")
    print("   - PASSWORD = 'your_password'")
    print("\n2. Test the script:")
    
    if platform.system() == "Windows":
        print("   - Run: windows\\autologin.bat")
    else:
        print("   - Run: ./linux/login.sh")
    
    print("\n3. Set up automation:")
    if platform.system() == "Windows":
        print("   - Use Task Scheduler to run windows\\autologin.bat periodically")
    else:
        print("   - Use crontab to schedule linux/login.sh")

def main():
    print_header()
    
    # Change to script directory if needed
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    if not check_python():
        sys.exit(1)
    
    if not install_requirements():
        sys.exit(1)
    
    if not make_scripts_executable():
        pass  # Don't exit, it's not critical
    
    setup_cron_on_linux()
    print_next_steps()

if __name__ == "__main__":
    main()
