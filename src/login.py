#!/usr/bin/env python3
import requests
import time
import sys
import socket
import argparse
import logging
import os
from pathlib import Path

# Import config manager
try:
    from config import load_config
    use_config_manager = True
except ImportError:
    use_config_manager = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Windows consoles/pipes default to cp1252 and crash on emoji log messages.
# Use UTF-8 with lossless-ish replacement so headless/redirected runs survive.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

# Get the directory to store response files (cross-platform)
def get_response_file_path():
    """Get cross-platform path for storing login responses."""
    project_root = Path(__file__).parent.parent
    return project_root / "last_login_response.html"


def load_credentials():
    """Load credentials from config manager, environment variables, or .env file."""
    global use_config_manager

    if use_config_manager:
        try:
            config = load_config()
            u, p = config.get_credentials()
            return u.strip('"\''), p.strip('"\'')
        except Exception as e:
            logging.warning(f"Config manager error: {e}")
            use_config_manager = False

    # Fallback: environment variables
    username = os.getenv('CAPTIVE_PORTAL_USERNAME')
    password = os.getenv('CAPTIVE_PORTAL_PASSWORD')

    if username and password:
        return username.strip('"\''), password.strip('"\'')

    # Fallback: .env file in project root
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        try:
            # utf-8-sig: handles BOM and non-ASCII passwords (Windows default
            # locale is cp1252 and would fail on UTF-8 characters)
            with open(env_file, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('CAPTIVE_PORTAL_USERNAME='):
                        username = line.split('=', 1)[1].strip().strip("'\"")
                    elif line.startswith('CAPTIVE_PORTAL_PASSWORD='):
                        password = line.split('=', 1)[1].strip().strip("'\"")
        except Exception as e:
            logging.warning(f"Could not read .env file: {e}")

    if not username or not password:
        # Write to stderr so it's captured in log/service.err.log even when
        # the service runs the script with --no-service-log (silent mode).
        print("❌ Credentials not found!", file=sys.stderr)
        print("Please set environment variables:", file=sys.stderr)
        print("  - CAPTIVE_PORTAL_USERNAME", file=sys.stderr)
        print("  - CAPTIVE_PORTAL_PASSWORD", file=sys.stderr)
        print("Or run the installer: python install.py", file=sys.stderr)
        sys.exit(1)

    return username, password


def build_request_params(username, password):
    """Build login URL, headers, and payload from config if available."""
    login_url = "http://172.16.1.3:8002/index.php?zone=lan"
    redirect_url = "https://www.mnit.ac.in"

    if use_config_manager:
        try:
            config = load_config()
            login_url = config.get_login_url()
            redirect_url = config.get_redirect_url()
        except Exception:
            pass

    headers = {
        "Host": "172.16.1.3:8002",
        "Cache-Control": "max-age=0",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "http://172.16.1.3:8002",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "http://172.16.1.3:8002/index.php?zone=lan&redirurl=http%3A%2F%2Fedge-http.microsoft.com%2Fcaptiveportal%2Fgenerate_204",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

# Form data (captured from your request)
PAYLOAD = {
    "redirurl": "https://www.mnit.ac.in",
    "zone": "lan",
    "auth_user": USERNAME,
    "auth_pass": PASSWORD,
    "accept": "LOGIN"
}

# Connectivity check interval (seconds) while the network is up.
# One-shot mode keeps the historical 1s cadence; continuous (24/7) mode
# checks less often to avoid hammering the connectivity server.
MONITOR_INTERVAL_SECONDS = 10

def is_network_down():
    """Return True if the internet is not reachable (captive portal or no link)."""
    try:
        response = requests.get(
            "http://connectivitycheck.gstatic.com/generate_204",
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
        )
        return response.status_code != 204
    except Exception as e:
        logging.debug(f"Connectivity check failed: {e}")
        return True  # Unreachable → treat as down


def login_to_network(login_url, headers, payload):
    """POST credentials to the captive portal. Returns True only if internet is confirmed up."""
    try:
        response = requests.post(login_url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            # Save response for debugging (captive portals return 200 even on wrong password)
            try:
                with open(get_response_file_path(), "w", encoding="utf-8", errors="replace") as f:
                    f.write(response.text)
            except Exception as file_error:
                logging.warning(f"⚠️ Could not save response file: {file_error}")

            # Verify the login actually worked — don't trust the 200 OK alone
            logging.info("⏳ Verifying internet connectivity...")
            time.sleep(2)  # Give the network a moment to authorise

            if not is_network_down():
                logging.info("✅ Login verified! Internet is active.")
                return True
            else:
                logging.warning("⚠️ Portal returned 200 OK but internet is still down.")
                logging.warning("   (Wrong password, or portal error)")
                logging.info(f"   Portal response snippet: {response.text[:500]}")
                return False
        else:
            logging.warning(f"⚠️ Login returned unexpected status: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Error while sending login request: {e}")
    
    return False  # Login failed

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Captive Portal Auto-Login")
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run 24/7: keep monitoring and re-login automatically whenever the "
             "captive portal drops the session (used by the Windows service).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress all console and file logging.",
    )
    parser.add_argument(
        "--no-service-log",
        action="store_true",
        help="Alias for --quiet: suppress all console and file logging "
             "(used by the Windows service).",
    )
    return parser.parse_args()


def setup_file_logging():
    """Add a file handler so headless runs (e.g. under the service) still log."""
    log_dir = Path(__file__).resolve().parent.parent / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_dir / "login.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(handler)


def main():
    """Keep checking network status and login when needed."""
    args = parse_args()
    continuous = args.continuous

    if args.quiet or args.no_service_log:
        # Silent mode: suppress everything (console and file).
        logging.disable(logging.CRITICAL)
    elif continuous:
        setup_file_logging()

    logging.info("🌐 Monitoring network status..." + (" [continuous mode]" if continuous else ""))

    # One-shot mode gives up after 15 minutes; continuous mode runs forever.
    TIMEOUT_SECONDS = None if continuous else 15 * 60  # 900 seconds
    start_time = time.time()
    last_status_was_down = False

    while True:
        elapsed_time = time.time() - start_time

        # Check if timeout exceeded (one-shot mode only)
        if TIMEOUT_SECONDS is not None and elapsed_time > TIMEOUT_SECONDS:
            logging.info(f"⏰ Timeout reached! ({TIMEOUT_SECONDS // 60} minutes elapsed). Exiting.")
            sys.exit(1)  # Exit with error code

        if is_network_down():
            remaining = ""
            if TIMEOUT_SECONDS is not None:
                remaining_secs = int(TIMEOUT_SECONDS - elapsed_time)
                remaining = f" ({remaining_secs // 60}m {remaining_secs % 60}s remaining)"
            logging.warning(f"🚫 Network down. Trying to log in...{remaining}")
            if login_to_network():
                logging.info("✅ Login successful.")
                if not continuous:
                    sys.exit()  # Exit script once login is successful
            else:
                logging.error("❌ Login attempt failed. Retrying in 5 seconds...")
                time.sleep(5)
            last_status_was_down = True

            if login_to_network(login_url, headers, payload):
                logging.info("✅ Logged in successfully. Resuming monitoring...")
                last_status_was_down = False
                # Brief pause to let the session stabilise before re-checking
                time.sleep(5)
            else:
                logging.error(f"❌ Login failed. Retrying in {RETRY_INTERVAL}s...")
                time.sleep(RETRY_INTERVAL)
        else:
            if last_status_was_down:
                logging.info("✅ Network restored.")
                last_status_was_down = False
            time.sleep(MONITOR_INTERVAL_SECONDS if continuous else 1)

if __name__ == "__main__":
    main()
