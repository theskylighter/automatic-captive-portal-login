# Captive Portal Auto-Login

Automatic login to campus network captive portal with **one-command installation**.

## 🚀 Quick Start

### One-Command Installation (Most People Use This)

**Linux/macOS:**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.sh)
```

**Windows (PowerShell):**
```powershell
iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.cmd')
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
├── install.cmd                  # One-command bootstrap (Windows)
│
├── src/
│   ├── login.py                 # Core login script
│   └── config.py                # Configuration manager
├── windows/
│   └── autologin.bat            # Windows launcher
├── linux/
│   └── login.sh                 # Linux/macOS launcher
├── install/
│   └── install.py               # Universal Python installer
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

### Windows - Task Scheduler

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

### Linux/macOS - Crontab

```bash
crontab -e
```

Add this line:
```bash
0 0 * * * /path/to/project/linux/login.sh >> /path/to/project/log/auto-login.log 2>&1
```

Replace `/path/to/project` with your actual project path.

**What it does:** Runs daily at 12:00 AM (midnight)

</details>

---

<details>
<summary><b>📝 How It Works</b></summary>

The script:
1. Continuously monitors network connectivity (checks every 1 second)
2. Detects when a captive portal appears
3. Automatically sends your login credentials
4. On success: Script exits ✅
5. On failure: Retries every 5 seconds (up to 15 minutes)

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
**Windows:** Check Task Scheduler → View Results
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


