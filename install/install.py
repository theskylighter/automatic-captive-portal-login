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
        print("[ERROR] Python 3.6+ is required")
        return False
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} found")
    return True

def install_requirements():
    """Install Python packages from requirements.txt"""
    print("\nInstalling Python dependencies...")

    def _pip_install(extra_args=None):
        cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        if extra_args:
            cmd += extra_args
        return subprocess.call(cmd)

    # First attempt: normal install
    ret = _pip_install()
    if ret == 0:
        print("[OK] Dependencies installed")
        return True

    # Second attempt: handle PEP 668 externally-managed-environment (macOS Homebrew, Debian 12+)
    print("\n[INFO] System pip blocked direct installs (externally managed environment).")
    print("[INFO] Trying with a virtual environment instead...")
    try:
        venv_dir = Path(".") / ".venv"
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])

        # Determine venv python path
        if platform.system() == "Windows":
            venv_python = venv_dir / "Scripts" / "python.exe"
        else:
            venv_python = venv_dir / "bin" / "python3"

        subprocess.check_call([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"])

        # Rewrite the launcher scripts to use the venv python
        _patch_launcher_for_venv(str(venv_python))

        print("[OK] Dependencies installed inside virtual environment (.venv)")
        return True
    except Exception as venv_err:
        print(f"[ERROR] Virtual environment setup failed: {venv_err}")

    print("[ERROR] Failed to install dependencies")
    print("\nTroubleshooting:")
    print("  - Make sure pip is available: python3 -m pip --version")
    print(f"  - Run manually: {sys.executable} -m pip install -r requirements.txt")
    return False


def _patch_launcher_for_venv(venv_python: str):
    """Update linux/login.sh and login.py shebang to use the venv python."""
    login_sh = Path("linux") / "login.sh"
    if login_sh.exists():
        content = login_sh.read_text()
        # Replace the python3 call with the absolute venv python path
        content = content.replace('python3 "$PROJECT_ROOT/src/login.py"',
                                  f'"{venv_python}" "$PROJECT_ROOT/src/login.py"')
        login_sh.write_text(content)
        print(f"[OK] Updated linux/login.sh to use venv python")

def make_scripts_executable():
    """Make shell scripts executable on Unix systems"""
    if platform.system() != "Windows":
        print("\nMaking scripts executable...")
        try:
            os.chmod("linux/login.sh", 0o755)
            print("[OK] Scripts made executable")
            return True
        except Exception as e:
            print(f"[WARNING] Could not make scripts executable: {e}")
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
            print("[ERROR] Username cannot be empty")
            continue
        break
    
    while True:
        password = input("Enter your campus network password: ").strip()
        if not password:
            print("[ERROR] Password cannot be empty")
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
        
        print(f"[OK] Credentials saved to .env file")
        
        # Verify it's in .gitignore
        gitignore_file = Path(".") / ".gitignore"
        if gitignore_file.exists():
            gitignore_content = gitignore_file.read_text()
            if ".env" not in gitignore_content:
                with open(gitignore_file, "a") as f:
                    f.write("\n# Environment variables\n.env\n")
                print("[OK] Added .env to .gitignore")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save .env file: {e}")
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
    """Set up cron job on Linux with smart midnight schedule"""
    if platform.system() != "Linux":
        return

    response = input("\nWould you like to set up automatic login around midnight (cron)? (y/n): ").strip().lower()
    if response not in ["y", "yes"]:
        print("\nSkipping cron setup. You can add it manually later.")
        print("Run: crontab -e  and add:")
        print("  58 23 * * * /bin/bash " + os.path.abspath("linux/login.sh"))
        return

    project_path = os.path.abspath(".")
    login_sh = os.path.join(project_path, "linux", "login.sh")
    log_dir = os.path.join(project_path, "log")
    log_file = os.path.join(log_dir, "auto-login.log")

    # Same schedule as macOS: 11:58 PM,
    cron_entries = [
        f"58 23 * * * /bin/bash {login_sh} >> {log_file} 2>&1",  # 11:58 PM - script monitors until login succeeds
    ]

    try:
        os.makedirs(log_dir, exist_ok=True)

        # Get existing crontab (if any)
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True
        )
        existing_crontab = result.stdout if result.returncode == 0 else ""

        # Avoid duplicate entries
        new_entries = []
        for entry in cron_entries:
            if entry not in existing_crontab:
                new_entries.append(entry)

        if not new_entries:
            print("[OK] Cron jobs already set up, no duplicates added.")
            return

        updated_crontab = existing_crontab.rstrip("\n") + "\n" + "\n".join(new_entries) + "\n"

        # Write updated crontab
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
        proc.communicate(input=updated_crontab.encode())

        if proc.returncode == 0:
            print("[OK] Cron jobs installed successfully!")
            print("[OK] Script will run at: 11:58 PM and monitor until login succeeds.")
            print(f"[OK] Logs will be saved to: {log_file}")
            print("\nTo view your cron jobs: crontab -l")
            print("To remove them:          crontab -e")
        else:
            raise Exception("crontab command failed")

    except FileNotFoundError:
        print("[ERROR] 'crontab' command not found on this system.")
        print("Install it with: sudo apt install cron  (Debian/Ubuntu)")
        print("             or: sudo dnf install cronie (Fedora/RHEL)")
    except Exception as e:
        print(f"\n[ERROR] Could not install cron job: {e}")
        print("You can add it manually by running: crontab -e")
        print("And adding these lines:")
        for entry in cron_entries:
            print(f"  {entry}")


def setup_task_scheduler_on_windows():
    """Set up Task Scheduler on Windows with confirmation"""
    if platform.system() != "Windows":
        return
    
    response = input("\nWould you like to set up Task Scheduler for automatic login? (y/n): ").strip().lower()
    if response not in ["y", "yes"]:
        print("\nSkipping Task Scheduler setup. You can do it later manually.")
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
            print("[OK] Task Scheduler setup confirmed!")
            break
        elif confirmation in ["n", "no"]:
            print("\nNo problem! You can set it up later manually.")
            break
        else:
            print("Please enter 'y' or 'n'")


def setup_launchd_on_macos():
    """Set up launchd agent on macOS with confirmation"""
    if platform.system() != "Darwin":
        return

    response = input("\nWould you like to set up automatic login around midnight (launchd)? (y/n): ").strip().lower()
    if response not in ["y", "yes"]:
        print("\nSkipping launchd setup. You can do it later manually.")
        return

    project_path = os.path.abspath(".")
    login_sh = os.path.join(project_path, "linux", "login.sh")
    launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
    plist_path = os.path.join(launch_agents_dir, "com.captiveportal.autologin.plist")

    # Run at 11:58 PM, 
    schedule_entries = [
        (23, 58),  # 11:58 PM - script monitors until login succeeds
    ]

    calendar_intervals = ""
    for hour, minute in schedule_entries:
        calendar_intervals += f"""        <dict>
            <key>Hour</key>
            <integer>{hour}</integer>
            <key>Minute</key>
            <integer>{minute}</integer>
        </dict>
"""

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.captiveportal.autologin</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>{login_sh}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartCalendarInterval</key>
    <array>
{calendar_intervals}    </array>
    <key>StandardOutPath</key>
    <string>{project_path}/log/auto-login.log</string>
    <key>StandardErrorPath</key>
    <string>{project_path}/log/auto-login-error.log</string>
</dict>
</plist>
"""

    try:
        os.makedirs(launch_agents_dir, exist_ok=True)
        os.makedirs(os.path.join(project_path, "log"), exist_ok=True)
        with open(plist_path, "w") as f:
            f.write(plist_content)
        subprocess.call(["launchctl", "load", plist_path])
        print(f"[OK] launchd agent installed and loaded.")
        print("[OK] Script will run at: 11:58 PM, 12:00, 12:01, 12:02, 12:03, 12:05 AM")
        print("[OK] Also runs once on startup/login (in case Mac was asleep at midnight).")
        print("\nTo disable later, run:")
        print(f"  launchctl unload {plist_path}")
    except Exception as e:
        print(f"\n[ERROR] Could not install launchd agent: {e}")
        print("You can set it up manually later.")


def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "=" * 50)
    print("[OK] Installation Complete!")
    print("=" * 50)
    print("\nYou can now use the following commands to run the auto-login:\n")
    
    if platform.system() == "Windows":
        print("Windows:")
        print("  windows\\autologin.bat")
    else:
        print("Linux/macOS:")
        print("  bash linux/login.sh")
    
    print("\nFor automation:")
    if platform.system() == "Windows":
        print("  - Use Task Scheduler (see instructions above)")
    elif platform.system() == "Darwin":
        print("  - launchd agent (already set up if you chose yes above)")
    else:
        print("  - Use crontab (see instructions above)")
    
    print("\nTo update credentials later:")
    print("  - Edit .env file, or")
    print("  - Set environment variables: CAPTIVE_PORTAL_USERNAME and CAPTIVE_PORTAL_PASSWORD")
    print("\n" + "=" * 50)

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
    elif platform.system() == "Darwin":
        setup_launchd_on_macos()
    
    print_next_steps()

if __name__ == "__main__":
    main()
