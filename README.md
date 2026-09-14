# Captive Portal Auto-Login

Automatic login to campus network captive portal with **one-command installation**.

## 🚀 Quick Start

### One-Command Installation (Most People Use This)

**Linux/macOS:**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.sh)
```

**Windows (Command Prompt):**
```cmd
curl -fsSL https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.cmd -o %temp%\install.cmd && %temp%\install.cmd
```

**Windows (PowerShell):**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.ps1')"
```


That's it! The installer will:
- ✅ Clone the repository
- ✅ Check Python installation
- ✅ Install dependencies
- ✅ Prompt for your credentials
- ✅ Save configuration securely
- ✅ Done!

---

<details>
<summary><b>📁 Project Structure</b></summary>

```
automatic-captive-portal-login/
├── install.sh                   # One-command bootstrap (Linux/macOS)
├── install.ps1                  # One-command bootstrap (Windows)
├── install.cmd                  # Legacy batch installer (Windows)
│
├── src/
│   ├── login.py                 # Core login script (--continuous for 24/7)
│   ├── service.py               # Windows service wrapper (24/7 autostart)
│   └── config.py                # Configuration manager
├── windows/
│   └── autologin.bat            # Windows launcher
├── linux/
│   └── login.sh                 # Linux/macOS launcher
├── install/
│   ├── install.py               # Universal Python installer
│   └── install_service.py       # Windows service install/manage/uninstall
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

</details>

---

<details>
<summary><b>📋 Pre-Requisites</b></summary>

- Python 3.6 or higher
- pip (Python package manager)
- Internet connection
- Git (for cloning, but optional if downloading manually)

</details>

---

<details>
<summary><b>� No curl/PowerShell? Download & Run Locally</b></summary>

After downloading the repository, run from project root:

**Linux/macOS:**
```bash
bash install.sh
```

**Windows:**
```cmd
install.cmd
```

</details>

---

## ⚙️ Setup Instructions

The installer will automatically:
- ✅ Check Python installation
- ✅ Install dependencies
- ✅ Ask for your credentials
- ✅ Save everything to `.env` (protected file)
- ✅ On Windows: ask about the **24/7 auto-login service** (default: Yes) and
  install it — it starts at boot and monitors around the clock (no Task Scheduler)
- ✅ Create a desktop shortcut for manual login (Windows)
- ✅ All done!

**Running the script:**

By default, the script runs in **24/7 continuous mode**, constantly monitoring your network and re-logging in automatically whenever the captive portal drops your session.

**Windows:** 
```cmd
windows\autologin.bat
```

**Linux/macOS:** 
```bash
./linux/login.sh
```

**Manual / One-Shot Mode (Check once, log in if down, and exit):**
```bash
# Linux/macOS
./linux/login.sh --once
# Windows
windows\autologin.bat --once
# Direct Python
python3 src/login.py --once
```

---

<details>
<summary><b>🔐 Credential Management & Security</b></summary>

### Where are my credentials stored?

Your credentials are saved in a `.env` file:
- ✅ Automatically added to `.gitignore` (can't be accidentally committed)
- ✅ Restricted to owner-only permissions on Linux/macOS (mode 600)
- ✅ Contains: `CAPTIVE_PORTAL_USERNAME` and `CAPTIVE_PORTAL_PASSWORD`

### How to update credentials?

**Option 1: Re-run installer**
```bash
python3 install/install.py    # or install.sh / install.cmd
```

**Option 2: Edit .env file directly**
```
CAPTIVE_PORTAL_USERNAME="new_username"
CAPTIVE_PORTAL_PASSWORD="new_password"
```

**Option 3: Environment variables (advanced)**
```bash
export CAPTIVE_PORTAL_USERNAME="your_username"
export CAPTIVE_PORTAL_PASSWORD="your_password"
```

### Is my password secure?

The `.env` file is protected by:
- `.gitignore` entry (won't commit to GitHub)
- File permissions (600 on Unix = owner-only)
- Not hardcoded in source code

**⚠️ Note:** This is suitable for campus/institutional networks with non-critical credentials. For sensitive passwords, use environment variables instead.

</details>

---

<details>
<summary><b>⏰ Set Up 24/7 Background Service (Auto-Start at Boot)</b></summary>

### Linux - 24/7 systemd User Service

The installer configures this automatically. It starts at boot / login, monitors 24/7, and automatically re-authenticates whenever disconnected.

To manage it manually at any time:

```bash
./linux/service.sh install      # Install and start the 24/7 service
./linux/service.sh status       # Check service status
./linux/service.sh logs         # View live journal logs
./linux/service.sh restart      # Restart service
./linux/service.sh stop         # Stop service
./linux/service.sh uninstall    # Remove service
```

### macOS - 24/7 launchd Agent

Configured during setup via `~/Library/LaunchAgents/com.captiveportal.autologin.plist`.

```bash
# Check status
launchctl list | grep captiveportal

# Unload / stop
launchctl unload ~/Library/LaunchAgents/com.captiveportal.autologin.plist
```

### Windows - 24/7 Windows Service

```cmd
python install\install_service.py install    REM Install and start service
python install\install_service.py status     REM Check status
python install\install_service.py restart    REM Restart service
python install\install_service.py uninstall  REM Remove service
```

</details>

---

<details>
<summary><b>🚀 24/7 Windows Service (Recommended — no Task Scheduler)</b></summary>

The Windows service keeps monitoring and re-logging-in **around the clock**
(no daily schedule needed) and **starts automatically at boot**. It replaces
the Task Scheduler approach entirely.

### Install (run once, from an elevated prompt — a UAC prompt will appear)

```cmd
python install\install_service.py install
```

To also disable the service's own log (`log/service.log`):

```cmd
python install\install_service.py install --no-service-log
```

Re-run `install` **without** the flag to re-enable service logging.

This will:
- ✅ Install `pywin32` + `requests` **system-wide** (required — services run as
  LocalSystem and cannot see per-user pip installs)
- ✅ Register the `CaptivePortalLogin` service (Automatic → delayed start)
- ✅ Start the service immediately
- ✅ Configure auto-restart if the login script ever crashes

### Manage

```cmd
python install\install_service.py status     REM check state / start type
python install\install_service.py stop
python install\install_service.py start
python install\install_service.py restart
python install\install_service.py uninstall  REM stop + remove service
```

> The service replaces Task Scheduler. The desktop shortcut is still created
> during install — use it (or `windows\autologin.bat`) for manual on-demand
> login whenever you want.

### Logs

| File                     | Contents                                  |
|--------------------------|-------------------------------------------|
| `log/login.log`          | Login attempts / connectivity status      |
| `log/service.out.log`    | Login script stdout                       |
| `log/service.err.log`    | Login script errors                       |
| `log/service.log`        | Service lifecycle events (disabled by `--no-service-log`) |

</details>

---

<details>
<summary><b>📝 How It Works</b></summary>

The script:
1. Continuously monitors network connectivity (checks every 10s by default)
2. Detects when a captive portal appears via fast HTTP/IP probing
3. Automatically posts your login credentials and verifies internet restoration
4. When connection drops (e.g. idle timeout, IP refresh, or midnight resets), automatically re-authenticates

### Default 24/7 Continuous Mode

By default, the script stays resident and keeps you logged in 24/7:

```bash
python3 src/login.py
```

### Manual / One-Shot Mode (`--once`)

If you prefer the script to check connectivity, log in once if down, and exit immediately:

```bash
python3 src/login.py --once
```

Add `--quiet` (or `--no-service-log`) to suppress all console output:

```bash
python3 src/login.py --quiet
```

### Configuration

All settings are in `src/login.py`:
- `LOGIN_URL` - Captive portal URL
- `TIMEOUT_SECONDS` - Max wait time (default: 900 = 15 min)
- `HEADERS` - HTTP headers for request
- Credentials loaded from `.env` or environment variables

</details>

---

<details>
<summary><b>🐛 Troubleshooting</b></summary>

### Credentials not configured
**Error:** `❌ Error: Credentials not configured!`

**Fix:**
```bash
python3 install/install.py    # Re-run installer
# OR manually create .env file with credentials
```

### Python not found
**Windows:** 
- Open Command Prompt → `python --version`
- If not found: [Install Python](https://www.python.org)

**Linux/macOS:**
- Use `python3` instead of `python`

### "requests" module not found
```bash
pip install -r requirements.txt
```

### Connection errors
- Check `LOGIN_URL` in `src/login.py` is correct
- Verify credentials in `.env` are correct
- Test network connection manually

### Script doesn't run on schedule
**Windows:** `python install\install_service.py status` → check service is RUNNING; if it isn't, run `python install\install_service.py start`
**Linux:** `grep CRON /var/log/syslog`

</details>

---

<details>
<summary><b>❓ FAQ</b></summary>

**Q: How do I uninstall?**
A: Just delete the project folder. The script isn't installed system-wide.

**Q: Can I modify the code?**
A: Yes! It's open source. Edit:
- `Login URL` → change `LOGIN_URL` variable
- `Credentials behavior` → edit `login_to_network()` function
- `Timeout` → change `TIMEOUT_SECONDS`

**Q: Will this work with my campus network?**
A: If your campus uses an HTTP captive portal (like Sophos), yes. Some proprietary portals may need URL adjustment in `src/login.py`.

**Q: What if I have multiple campuses?**
A: Edit `LOGIN_URL` and `PAYLOAD` in `src/login.py` for each network, or run installer again with different credentials.

**Q: Does this work on macOS?**
A: Yes! Use `install.sh` or Linux/macOS installers. Everything is the same.

**Q: How do I find my Python executable path?**
```bash
python -c "import sys; print(sys.executable)"
```

</details>

---

<details>
<summary><b>📄 License & Contributing</b></summary>

This project is open source. Feel free to:
- ✅ Fork and modify
- ✅ Submit pull requests
- ✅ Report issues
- ✅ Share improvements

See GitHub repository for license details.

</details>

---

## 📌 TODO

- [ ] **Add a quick login command to PATH / `.bashrc`** — expose a short command (e.g. `log`) so the user can trigger a login from anywhere in the terminal without navigating to the project folder.
- [ ] **Auto `cd` into the install directory on first run** — when the user runs the installer for the first time, automatically switch to (or instruct the shell to switch to) the project directory so the manual test commands (`./linux/login.sh`, etc.) work immediately without the user having to `cd` there themselves.


