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
import re

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
        # Use the same Python executable that's running this script
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies (exit code: {e.returncode})")
        print("\nTroubleshooting:")
        print("  - Make sure pip is available: python -m pip --version")
        print("  - Try upgrading pip: python -m pip install --upgrade pip")
        print(f"  - Run manually: {sys.executable} -m pip install -r requirements.txt")
        return False
    except FileNotFoundError:
        print("❌ pip not found. This should not happen with Python 3.4+")
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

def get_credentials():
    """Interactively get credentials from user"""
    print("\n" + "=" * 50)
    print("Configure Credentials")
    print("=" * 50)
    print("These will be stored securely in a .env file.\n")
    
    while True:
        username = input("Enter your campus network username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            continue
        break
    
    while True:
        password = input("Enter your campus network password: ").strip()
        if not password:
            print("❌ Password cannot be empty")
            continue
        break
    
    return username, password

def save_env_file(username, password):
    """Save credentials to .env file"""
    env_file = Path(".") / ".env"
    
    # Create .env content
    env_content = f"""# Captive Portal Credentials
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

CAPTIVE_PORTAL_USERNAME="{username}"
CAPTIVE_PORTAL_PASSWORD="{password}"
"""
    
    try:
        # Write to .env file
        env_file.write_text(env_content)
        
        # On Unix, restrict permissions to owner only
        if platform.system() != "Windows":
            os.chmod(env_file, 0o600)
        
        print(f"✅ Credentials saved to .env file")
        
        # Verify it's in .gitignore
        gitignore_file = Path(".") / ".gitignore"
        if gitignore_file.exists():
            gitignore_content = gitignore_file.read_text()
            if ".env" not in gitignore_content:
                with open(gitignore_file, "a") as f:
                    f.write("\n# Environment variables\n.env\n")
                print("✅ Added .env to .gitignore")
        
        return True
    except Exception as e:
        print(f"❌ Failed to save .env file: {e}")
        return False

def setup_environment_variables():
    """Offer to set environment variables as alternative"""
    print("\n" + "=" * 50)
    print("Environment Variables Setup")
    print("=" * 50)
    print("\nAlternatively, you can set environment variables:")
    
    if platform.system() == "Windows":
        print("\nOn Windows (Command Prompt):")
        print('  set CAPTIVE_PORTAL_USERNAME=your_username')
        print('  set CAPTIVE_PORTAL_PASSWORD=your_password')
        print("\nOr set them permanently via System Properties > Environment Variables")
    else:
        print("\nOn Linux/macOS (add to ~/.bashrc or ~/.zshrc):")
        print('  export CAPTIVE_PORTAL_USERNAME="your_username"')
        print('  export CAPTIVE_PORTAL_PASSWORD="your_password"')

def setup_cron_on_linux():
    """Set up cron job on Linux with confirmation"""
    if platform.system() != "Linux":
        return
    
    response = input("\nWould you like to set up a cron job for automatic login? (y/n): ").strip().lower()
    if response not in ["y", "yes"]:
        print("\nSkipping cron setup.")
        return
    
    project_path = os.path.abspath(".")
    cron_command = f"0 0 * * * {project_path}/linux/login.sh >> {project_path}/log/auto-login.log 2>&1"
    
    print("\n" + "=" * 60)
    print("CRON JOB SETUP INSTRUCTIONS")
    print("=" * 60)
    print("\nFollow these steps to set up automatic login:")
    print("\n1. Open your crontab editor:")
    print("   $ crontab -e")
    print("\n2. Add this line to schedule the login script at midnight daily:")
    print(f"   {cron_command}")
    print("\n3. Save and exit the editor (for nano: Ctrl+O, Enter, Ctrl+X)")
    print("\nNote: Log output will be saved to: " + os.path.join(project_path, "log", "auto-login.log"))
    print("=" * 60)
    
    # Wait for confirmation
    while True:
        confirmation = input("\nHave you completed the cron setup? (y/n): ").strip().lower()
        if confirmation in ["y", "yes"]:
            print("✅ Cron job setup confirmed!")
            break
        elif confirmation in ["n", "no"]:
            print("\nNo problem! You can set it up later manually.")
            break
        else:
            print("Please enter 'y' or 'n'")

def setup_task_scheduler_on_windows():
    """Set up Task Scheduler on Windows with confirmation"""
    if platform.system() != "Windows":
        return
    
    response = input("\nWould you like to set up Task Scheduler for automatic login? (y/n): ").strip().lower()
    if response not in ["y", "yes"]:
        print("\nSkipping Task Scheduler setup.")
        return
    
    project_path = os.path.abspath(".")
    bat_path = os.path.join(project_path, "windows", "autologin.bat")
    
    print("\n" + "=" * 60)
    print("TASK SCHEDULER SETUP INSTRUCTIONS")
    print("=" * 60)
    print("\nFollow these step-by-step instructions:")
    print("\n1. Open Task Scheduler:")
    print("   - Press Win+S and search for 'Task Scheduler'")
    print("   - Click 'Task Scheduler'")
    print("\n2. Create a new task:")
    print("   - On the right panel, click 'Create Task'")
    print("\n3. Configure the GENERAL tab:")
    print('   - Name: "Campus Network Auto-Login"')
    print("   - Description: (Optional) Auto-login to captive portal")
    print("   - Check the box: 'Run whether user is logged on or not'")
    print("   - Check the box: 'Run with highest privileges' (recommended)")
    print("\n4. Configure the TRIGGERS tab:")
    print("   - Click 'New...'")
    print("   - Begin the task: 'On a schedule'")
    print("   - Set to: 'Daily' at your preferred time (e.g., 8:00 AM)")
    print("   - Click OK")
    print("\n5. Configure the ACTIONS tab:")
    print("   - Click 'New...'")
    print("   - Action: 'Start a program'")
    print(f"   - Program/script: {bat_path}")
    print("   - Click OK")
    print("\n6. Click OK to save the task:")
    print("   - You may be prompted to enter your password")
    print("   - Enter your Windows password and click OK")
    print("=" * 60)
    
    # Wait for confirmation
    while True:
        confirmation = input("\nHave you completed the Task Scheduler setup? (y/n): ").strip().lower()
        if confirmation in ["y", "yes"]:
            print("✅ Task Scheduler setup confirmed!")
            break
        elif confirmation in ["n", "no"]:
            print("\nNo problem! You can set it up later manually.")
            break
        else:
            print("Please enter 'y' or 'n'")

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "=" * 50)
    print("✅ Installation Complete!")
    print("=" * 50)
    print("\nYou can now use the following commands to run the auto-login:\n")
    
    if platform.system() == "Windows":
        print("Windows:")
        print("  windows\\autologin.bat")
    else:
        print("Linux/macOS:")
        print("  ./linux/login.sh")
    
    print("\nFor automation:")
    if platform.system() == "Windows":
        print("  - Use Task Scheduler (see instructions above)")
    else:
        print("  - Use crontab (see instructions above)")
    
    print("\nTo update credentials later:")
    print("  - Edit .env file, or")
    print("  - Set environment variables: CAPTIVE_PORTAL_USERNAME and CAPTIVE_PORTAL_PASSWORD")

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
    
    # Get and save credentials
    username, password = get_credentials()
    if not save_env_file(username, password):
        sys.exit(1)
    
    # Offer environment variable setup info
    setup_environment_variables()
    
    # Platform-specific automation setup
    if platform.system() == "Windows":
        setup_task_scheduler_on_windows()
    elif platform.system() == "Linux":
        setup_cron_on_linux()
    
    print_next_steps()

if __name__ == "__main__":
    main()
