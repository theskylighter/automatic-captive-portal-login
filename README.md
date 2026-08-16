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

**Test the script:**

**Windows:** 
```bash
windows\autologin.bat
```

**Linux/macOS:** 
```bash
./linux/login.sh
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
<summary><b>⏰ Set Up Automation (12:00 AM Daily)</b></summary>

### Windows - 24/7 Service (no Task Scheduler)

> 💡 The installer handles this automatically — it will ask during setup and,
> by default (press **Enter**), installs the **24/7 Windows service** which
> auto-logs-in at boot and monitors around the clock. No Task Scheduler needed.

If you skipped it during install, or want the manual alternative:

- **(Recommended)** Install the service:
  ```cmd
  python install\install_service.py install
  ```
  (See the [🚀 24/7 Windows Service](#-247-windows-service-recommended--no-task-scheduler)
  section below for full details.)

- **(Legacy, not recommended)** Manual Task Scheduler:
  1. Press `Win + S` → search "Task Scheduler" → Open
  2. Right-click → **Create Task**
  3. **General tab:**
     - Name: "Campus Network Auto-Login"
     - ☑️ "Run whether user is logged on or not"
  4. **Triggers tab:**
     - Click **New** → Daily → 12:00 AM → OK
  5. **Actions tab:**
     - Click **New** → Action: "Start a program"
     - Program/script: `windows\autologin.bat`
     - OK
  6. Enter password, done!

### Linux - Crontab

> 💡 The installer handles this automatically — it will ask during setup and register the cron job at **11:58 PM** daily (no manual steps needed).

If you skipped it or want to add it manually:

```bash
crontab -e
```

Add this line:
```bash
58 23 * * * /bin/bash /path/to/project/linux/login.sh >> /path/to/project/log/auto-login.log 2>&1
```

Replace `/path/to/project` with your actual project path.

To view or remove the job: `crontab -l` / `crontab -e`

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
1. Continuously monitors network connectivity
2. Detects when a captive portal appears
3. Automatically sends your login credentials
4. On success: Script exits ✅ *(one-shot mode — used by `windows\autologin.bat`)*
5. On failure: Retries every 5 seconds (up to 15 minutes)

### 24/7 mode

When run with `--continuous` (used by the Windows service), the script never
times out or exits:

1. Monitors connectivity every 10 seconds
2. When the captive portal drops the session (e.g. daily midnight resets), it
   re-logs-in automatically
3. Keeps monitoring forever

```bash
python src/login.py --continuous
```

Add `--quiet` (or `--no-service-log`) to suppress all output (no console, no
log files):

```bash
python src/login.py --continuous --quiet
```

The Windows service runs the script as `python src/login.py --continuous
--no-service-log` (fully silent), so the only file it produces is
`log/service.out.log` (empty) unless the service is stopped.

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


