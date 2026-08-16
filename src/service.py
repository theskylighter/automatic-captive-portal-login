#!/usr/bin/env python3
"""
Captive Portal Auto-Login Windows service (24/7).

Runs ``src/login.py --continuous --no-service-log`` as a child process and
automatically restarts it if it ever exits, so the machine stays logged in
around the clock. Starts automatically at boot.

Manage it from an elevated prompt (or use install/install_service.py):

    python src/service.py install --startup delayed
    python src/service.py start
    python src/service.py stop
    python src/service.py remove

Logs:
    log/service.out.log   - stdout of the login script
    log/service.err.log   - stderr of the login script
    log/service.log       - service lifecycle events (start/stop/restarts)
                           (disabled when installed with --no-service-log)
"""

import subprocess
import sys
import time
from pathlib import Path

import win32event
import win32service
import win32serviceutil

SERVICE_NAME = "CaptivePortalLogin"
SERVICE_DISPLAY_NAME = "Captive Portal Auto-Login"
SERVICE_DESCRIPTION = (
    "Monitors network connectivity and auto-logs into the campus captive "
    "portal 24/7. Starts automatically at boot."
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGIN_SCRIPT = PROJECT_ROOT / "src" / "login.py"
LOG_DIR = PROJECT_ROOT / "log"
STDOUT_LOG = LOG_DIR / "service.out.log"
STDERR_LOG = LOG_DIR / "service.err.log"
SERVICE_LOG = LOG_DIR / "service.log"
# When this marker file exists, the service does NOT write to log/service.log.
# Created by: python install/install_service.py install --no-service-log
NO_SERVICE_LOG_MARKER = PROJECT_ROOT / ".service_no_log"
POLL_INTERVAL_MS = 1000
RESTART_DELAY_SECONDS = 5


def _write_service_event(message):
    """Append a lifecycle event to log/service.log (no-op with --no-service-log)."""
    if NO_SERVICE_LOG_MARKER.exists():
        return
    try:
        with open(SERVICE_LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception:
        pass


def _python_exe():
    """Return the real python.exe to run login.py with.

    When running as a service, sys.executable is pythonservice.exe (pywin32's
    service host), which cannot run arbitrary scripts. Resolve the actual
    interpreter from sys.exec_prefix instead.
    """
    exe = Path(sys.executable)
    if not exe.name.lower().startswith("pythonservice"):
        return str(exe)
    for candidate in (
        Path(sys.exec_prefix) / "python.exe",
        Path(sys.exec_prefix) / "Scripts" / "python.exe",
    ):
        if candidate.exists():
            return str(candidate)
    raise RuntimeError("Could not locate python.exe next to pythonservice.exe")


class CaptivePortalLoginService(win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = SERVICE_DESCRIPTION

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        """Signal the run loop to stop and terminate the child."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def _stop_child(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        _write_service_event("Service started (running src/login.py --continuous --no-service-log)")
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        with open(STDOUT_LOG, "ab", 0) as stdout_log, \
             open(STDERR_LOG, "ab", 0) as stderr_log:
            while True:
                self.process = subprocess.Popen(
                    [_python_exe(), str(LOGIN_SCRIPT), "--continuous", "--no-service-log"],
                    cwd=str(PROJECT_ROOT),
                    stdout=stdout_log,
                    stderr=stderr_log,
                )

                # Wait for the child to exit, polling for the stop signal.
                while True:
                    rc = win32event.WaitForSingleObject(
                        self.hWaitStop, POLL_INTERVAL_MS
                    )
                    if rc == win32event.WAIT_OBJECT_0:
                        _write_service_event("Service stopping")
                        self._stop_child()
                        self.process = None
                        return
                    if self.process.poll() is not None:
                        break

                exit_code = self.process.returncode
                self.process = None
                _write_service_event(
                    f"login.py exited (code {exit_code}); "
                    f"restarting in {RESTART_DELAY_SECONDS}s"
                )
                time.sleep(RESTART_DELAY_SECONDS)


if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(CaptivePortalLoginService)
