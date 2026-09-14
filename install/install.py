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
        # Write to .env file (utf-8 so non-ASCII credentials survive on Windows)
        env_file.write_text(env_content, encoding="utf-8")
        
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

def setup_service_on_linux():
    """Set up 24/7 systemd user service on Linux (starts at boot/login)"""
    if platform.system() != "Linux":
        return

    print("\n" + "=" * 60)
    print("24/7 LINUX BACKGROUND SERVICE (RECOMMENDED)")
    print("=" * 60)
    print("\nInstall the auto-login background service that:")
    print("  - Starts automatically on boot / login")
    print("  - Monitors the network 24/7 and re-authenticates on drops")
    print("  - Auto-restarts if it ever crashes")

    response = input("\nInstall the 24/7 auto-login systemd user service? (Y/n): ").strip().lower()
    if response in ["", "y", "yes"]:
        service_sh = os.path.abspath("linux/service.sh")
        if os.path.exists(service_sh):
            try:
                ret = subprocess.call(["/bin/bash", service_sh, "install"])
                if ret == 0:
                    print("\n[OK] 24/7 background service installed and running!")
                    return
            except Exception as e:
                print(f"[WARNING] systemd service setup encountered an error: {e}")

    # Fallback to crontab @reboot if systemd was skipped or unavailable
    print("\nSkipping systemd service. You can set it up anytime with:")
    print("  ./linux/service.sh install")


def setup_windows_service():
    """Install the 24/7 auto-login Windows service (default, replaces Task Scheduler)"""
    if platform.system() != "Windows":
        return

    print("\n" + "=" * 60)
    print("24/7 WINDOWS SERVICE (RECOMMENDED)")
    print("=" * 60)
    print("\nInstead of Task Scheduler, this project now ships a real Windows")
    print("service that:")
    print("  - Starts automatically at boot (no login required)")
    print("  - Monitors the network continuously")
    print("  - Re-logs-in automatically whenever the portal drops the session")
    print("  - Auto-restarts the login script if it ever crashes")

    response = input("\nInstall the 24/7 auto-login Windows service? (Y/n): ").strip().lower()
    if response in ["", "y", "yes"]:
        print("\nLaunching the service installer...")
        print("NOTE: A UAC (admin) prompt will appear. Click 'Yes' to continue.")
        print("The elevated installer runs in its own window and shows progress.\n")
        installer = os.path.join(os.path.abspath("."), "install", "install_service.py")
        subprocess.call([sys.executable, installer, "install"])
        print("\nThe elevated installer has been launched. Wait for it to finish,")
        print("then verify with:  python install\\install_service.py status")
        return

    print("\nSkipping the Windows service. You have two options later:")
    print("  (a) RECOMMENDED - Install the 24/7 service:")
    print("        python install\\install_service.py install")
    print("  (b) Legacy - Manual Task Scheduler setup (see README for steps)")


def create_desktop_shortcut_on_windows():
    """Create a desktop shortcut to autologin.bat for manual use when automation fails"""
    if platform.system() != "Windows":
        return

    project_path = os.path.abspath(".")
    bat_path = os.path.join(project_path, "windows", "autologin.bat")
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop_path, "Captive Portal Login.lnk")

    print("\nCreating desktop shortcut to autologin.bat...")

    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{bat_path}'
$Shortcut.WorkingDirectory = '{project_path}'
$Shortcut.Description = 'Captive Portal Auto-Login - Run manually if auto-login fails'
$Shortcut.Save()
"""

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"[OK] Desktop shortcut created: {shortcut_path}")
            print("[INFO] Use it to trigger login manually if the service hasn't logged in yet.")
        else:
            print(f"[WARNING] Could not create desktop shortcut: {result.stderr.strip()}")
    except FileNotFoundError:
        print("[WARNING] PowerShell not found; skipping desktop shortcut creation.")
    except Exception as e:
        print(f"[WARNING] Desktop shortcut creation failed: {e}")


def setup_launchd_on_macos():
    """Set up 24/7 launchd agent on macOS (starts at boot/login)"""
    if platform.system() != "Darwin":
        return

    print("\n" + "=" * 60)
    print("24/7 MACOS BACKGROUND SERVICE (RECOMMENDED)")
    print("=" * 60)
    print("\nInstall the auto-login launchd agent that:")
    print("  - Starts automatically at boot / login")
    print("  - Keeps monitoring 24/7 and re-authenticates on drops")
    print("  - Auto-restarts if it ever crashes")

    response = input("\nInstall the 24/7 auto-login launchd agent? (Y/n): ").strip().lower()
    if response not in ["", "y", "yes"]:
        print("\nSkipping launchd setup. You can set it up manually later.")
        return

    project_path = os.path.abspath(".")
    login_sh = os.path.join(project_path, "linux", "login.sh")
    launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
    plist_path = os.path.join(launch_agents_dir, "com.captiveportal.autologin.plist")
    log_dir = os.path.join(project_path, "log")

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
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{log_dir}/service.out.log</string>
    <key>StandardErrorPath</key>
    <string>{log_dir}/service.err.log</string>
</dict>
</plist>
"""

    try:
        os.makedirs(launch_agents_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        with open(plist_path, "w", encoding="utf-8") as f:
            f.write(plist_content)
        subprocess.call(["launchctl", "unload", plist_path], stderr=subprocess.DEVNULL)
        subprocess.call(["launchctl", "load", plist_path])
        print(f"[OK] 24/7 launchd agent installed and running!")
        print("\nTo stop / remove later:")
        print(f"  launchctl unload {plist_path}")
        print(f"  rm -f {plist_path}")
    except Exception as e:
        print(f"\n[ERROR] Could not install launchd agent: {e}")


def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "=" * 50)
    print("[OK] Installation Complete!")
    print("=" * 50)
    print("\nYou can now use the following commands:\n")
    
    if platform.system() == "Windows":
        print("Windows:")
        print("  windows\\autologin.bat           # Run 24/7 in foreground")
        print("  windows\\autologin.bat --once    # Run once manually")
        print("\n24/7 Background Service:")
        print("  python install\\install_service.py status")
        print("  python install\\install_service.py uninstall")
    elif platform.system() == "Darwin":
        print("macOS:")
        print("  ./linux/login.sh               # Run 24/7 in foreground")
        print("  ./linux/login.sh --once        # Run once manually")
        print("\n24/7 Background Service (launchd):")
        print("  launchctl list | grep captiveportal")
    else:
        print("Linux:")
        print("  ./linux/login.sh               # Run 24/7 in foreground")
        print("  ./linux/login.sh --once        # Run once manually")
        print("\n24/7 Background Service (systemd):")
        print("  ./linux/service.sh status      # Check background service status")
        print("  ./linux/service.sh logs        # View live service logs")
        print("  ./linux/service.sh restart     # Restart service")
        print("  ./linux/service.sh uninstall   # Remove service")
    
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
        setup_windows_service()
        create_desktop_shortcut_on_windows()
    elif platform.system() == "Linux":
        setup_service_on_linux()
    elif platform.system() == "Darwin":
        setup_launchd_on_macos()
    
    print_next_steps()


if __name__ == "__main__":
    main()
