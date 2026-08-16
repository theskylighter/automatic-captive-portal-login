#!/usr/bin/env python3
"""
Manage the Captive Portal Auto-Login Windows service (24/7, boot autostart).

This replaces the Task Scheduler setup: the service keeps monitoring and
re-logging-in around the clock, and starts automatically at boot.

Usage:
    python install/install_service.py install               # install + start (run once)
    python install/install_service.py install --no-service-log   # same, but skip log/service.log
    python install/install_service.py uninstall             # stop + remove
    python install/install_service.py start
    python install/install_service.py stop
    python install/install_service.py restart
    python install/install_service.py status

'install', 'uninstall', 'start', 'stop' and 'restart' require Administrator
rights; the script will re-launch itself elevated (a UAC prompt appears).
"""

import os
import subprocess
import sys
from pathlib import Path

SERVICE_NAME = "CaptivePortalLogin"
SERVICE_SCRIPT = Path(__file__).resolve().parent.parent / "src" / "service.py"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "log"
# Marker file that disables the service's own log (log/service.log).
NO_SERVICE_LOG_MARKER = PROJECT_ROOT / ".service_no_log"

# Packages the service needs. Installed system-wide so the service (which
# runs as LocalSystem) can import them -- per-user pip installs are NOT
# visible to services.
PACKAGES = ["pywin32>=305", "requests>=2.28,<3.0"]


def is_admin():
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def self_elevate():
    """Re-run this script with Administrator rights if not already elevated."""
    if is_admin():
        return
    import ctypes
    params = " ".join(f'"{a}"' for a in sys.argv[1:]) if len(sys.argv) > 1 else '"install"'
    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        f'"{Path(__file__)}" {params}',
        str(PROJECT_ROOT),
        1,
    )
    if result <= 32:
        print("[ERROR] Elevation was cancelled or failed (code %d)." % result)
        sys.exit(1)
    sys.exit(0)


def run_service(*args):
    """Delegate the pywin32 service handling to src/service.py."""
    return subprocess.call([sys.executable, str(SERVICE_SCRIPT), *args])


def _imports_ok_system_wide():
    """Return True if pywin32 + requests import from the global site-packages.

    Uses ``-s`` (no user site) to simulate the service account, which has its
    own empty per-user site-packages.
    """
    import sysconfig
    global_site = sysconfig.get_paths()["purelib"]
    check = subprocess.run(
        [
            sys.executable, "-s", "-c",
            "import requests, win32serviceutil, win32event;"
            "print(requests.__file__); print(win32serviceutil.__file__)",
        ],
        capture_output=True,
        text=True,
    )
    return check.returncode == 0 and global_site in check.stdout, check


def ensure_system_packages():
    """Ensure pywin32 + requests are installed in the global site-packages.

    Services run under the LocalSystem account, which has its own (empty)
    per-user site-packages. They can only import packages from the global
    site-packages of the Python interpreter.

    If the packages are already visible system-wide this does nothing, so a
    re-install never tries to overwrite DLLs currently loaded by the running
    service (which would fail with "Access is denied").
    """
    import sysconfig
    global_site = sysconfig.get_paths()["purelib"]

    ok, check = _imports_ok_system_wide()
    if ok:
        print(f"[OK] pywin32 + requests already installed system-wide ({global_site})")
        return

    print("[*] Installing pywin32 + requests system-wide (needed by the service)...")
    env = os.environ.copy()
    env["PIP_USER"] = "0"  # force global install, never --user
    rc = subprocess.call(
        [
            sys.executable, "-m", "pip", "install",
            "--disable-pip-version-check", "--no-warn-script-location",
            "--ignore-installed",  # user-site copies would otherwise be "satisfied"
            *PACKAGES,
        ],
        env=env,
    )
    if rc != 0:
        print("[ERROR] pip install failed. Please fix and re-run install.")
        sys.exit(rc)

    # Run pywin32's postinstall so pythoncom/pywintypes DLLs are properly
    # placed for service usage. Non-fatal if missing or it fails.
    postinstall = Path(sysconfig.get_paths()["scripts"]) / "pywin32_postinstall.py"
    if postinstall.exists():
        print("[*] Running pywin32 postinstall...")
        subprocess.call([sys.executable, str(postinstall), "-install"], env=env)

    ok, check = _imports_ok_system_wide()
    output = check.stdout.strip()
    print(output or check.stderr.strip())
    if not ok:
        print(f"[WARNING] Packages are NOT visible system-wide (expected under {global_site}).")
        print("          The service may fail to start. Re-run install as Administrator.")
    else:
        print(f"[OK] Packages visible system-wide ({global_site})")


def install(no_service_log=False):
    # Stop a running instance first so pywin32 DLLs aren't locked if a
    # reinstall becomes necessary. The service is (re)started below anyway.
    run_service("stop")

    # --no-service-log: create (or remove) the marker that disables
    # log/service.log. Re-installing without the flag re-enables logging.
    if no_service_log:
        NO_SERVICE_LOG_MARKER.touch()
        print(f"[OK] Service logging DISABLED ({NO_SERVICE_LOG_MARKER.name})")
    else:
        try:
            NO_SERVICE_LOG_MARKER.unlink()
        except FileNotFoundError:
            pass

    ensure_system_packages()

    print(f"[*] Registering service '{SERVICE_NAME}'...")
    rc = run_service("--startup", "delayed", "install")
    if rc != 0:
        print("[ERROR] Service registration failed.")
        sys.exit(rc)

    # Auto-restart the service if it (or the login script) ever crashes.
    subprocess.call(
        ["sc", "failure", SERVICE_NAME, "reset= 86400",
         "actions= restart/5000/restart/5000/restart/5000"]
    )

    print("[*] Starting service...")
    # "restart" handles both a fresh install and an already-running service
    # (it stops first if needed, then starts).
    rc = run_service("--wait", "30", "restart")
    if rc != 0:
        print("[ERROR] Service failed to start. Check the logs:")
        print(f"    {LOG_DIR / 'service.log'}")
        print(f"    {LOG_DIR / 'service.err.log'}")
        sys.exit(rc)

    print()
    print(f"[OK] Service '{SERVICE_NAME}' installed and running.")
    print("[OK] It auto-starts at boot (Automatic, delayed) and monitors 24/7.")
    print()
    print("Useful commands (from an elevated prompt):")
    print(f"    python install\\install_service.py status")
    print(f"    python install\\install_service.py stop")
    print(f"    python install\\install_service.py start")
    print(f"    python install\\install_service.py uninstall")
    print()
    print("Logs:")
    print(f"    {LOG_DIR / 'login.log'}          # login attempts / connectivity")
    print(f"    {LOG_DIR / 'service.out.log'}     # script output")
    print(f"    {LOG_DIR / 'service.err.log'}     # script errors")
    if NO_SERVICE_LOG_MARKER.exists():
        print(f"    {LOG_DIR / 'service.log'}         # DISABLED (--no-service-log)")
    else:
        print(f"    {LOG_DIR / 'service.log'}         # service lifecycle events")


def uninstall():
    print(f"[*] Stopping service '{SERVICE_NAME}'...")
    run_service("stop")
    print(f"[*] Removing service '{SERVICE_NAME}'...")
    run_service("remove")


def show_status():
    try:
        import win32service
    except ImportError:
        print("[ERROR] pywin32 is not installed. Run: python -m pip install pywin32")
        sys.exit(1)

    try:
        hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_CONNECT)
    except Exception as e:
        print(f"[ERROR] Cannot connect to the Service Control Manager: {e}")
        sys.exit(1)

    try:
        try:
            hs = win32service.OpenService(
                hscm, SERVICE_NAME,
                win32service.SERVICE_QUERY_STATUS | win32service.SERVICE_QUERY_CONFIG,
            )
        except win32service.error:
            print(f"[INFO] Service '{SERVICE_NAME}' is not installed.")
            print("       Install it with: python install/install_service.py install")
            return
        try:
            status = win32service.QueryServiceStatus(hs)
            config = win32service.QueryServiceConfig(hs)
        finally:
            win32service.CloseServiceHandle(hs)
    finally:
        win32service.CloseServiceHandle(hscm)

    STATES = {
        1: "STOPPED", 2: "START_PENDING", 3: "STOP_PENDING",
        4: "RUNNING", 5: "CONTINUE_PENDING", 6: "PAUSE_PENDING", 7: "PAUSED",
    }
    START_TYPES = {0: "BOOT", 1: "SYSTEM", 2: "AUTO", 3: "DEMAND", 4: "DISABLED"}
    print(f"Service : {SERVICE_NAME}")
    print(f"State   : {STATES.get(status[1], status[1])}")
    print(f"Start   : {START_TYPES.get(config[1], config[1])} (delayed)" if config[1] == 2 else
          f"Start   : {START_TYPES.get(config[1], config[1])}")
    print(f"Logs    : {LOG_DIR}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()
    extra = [a.lower() for a in sys.argv[2:]]
    no_service_log = "--no-service-log" in extra

    if command == "status":
        show_status()
        return

    self_elevate()

    if command == "install":
        install(no_service_log=no_service_log)
    elif command == "uninstall":
        uninstall()
    elif command == "start":
        run_service("--wait", "30", "start")
    elif command == "stop":
        run_service("stop")
    elif command == "restart":
        run_service("--wait", "30", "restart")
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
