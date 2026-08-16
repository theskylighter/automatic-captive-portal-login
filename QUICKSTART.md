# ⚡ Quick Start Guide

## 🚀 Installation (30 seconds) - Pick ONE:

### Linux/macOS
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.sh)
```

### Windows (Command Prompt)
```cmd
curl -fsSL https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.cmd -o %temp%\install.cmd && %temp%\install.cmd
```


### Windows (PowerShell)
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/theskylighter/automatic-captive-portal-login/main/install.ps1')"
```


---

## ✅ What's Next?

The installer will:
1. Clone the repo (if needed)
2. Install Python dependencies
3. Ask for your credentials
4. Save everything securely
5. **Done!** 🎉

---

<details>
<summary><b>� No curl/PowerShell? Download & Run Locally</b></summary>

Download from GitHub, then:

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

## 🎯 Run the Script Manually

**Windows:**
```batch
windows\autologin.bat
```

**Linux/macOS:**
```bash
./linux/login.sh
```

---

<details>
<summary><b>⏰ Setup Automation (Optional)</b></summary>

### Windows - 24/7 Service (default, no Task Scheduler)

The one-click installer (`install.cmd`) asks **"Install the 24/7 auto-login
Windows service? (Y/n)"** — press **Enter** (default) to install it. The
service:

- Starts automatically at boot
- Monitors and re-logs-in continuously (no schedule needed)

If you skipped it, install it later with:

```batch
python install\install_service.py install
```

Check status / uninstall:

```batch
python install\install_service.py status
python install\install_service.py uninstall
```

### Linux/macOS - Crontab
```bash
crontab -e
```
Add this line:
```bash
0 0 * * * /path/to/project/linux/login.sh
```
(Runs daily at 12:00 AM)

</details>

---

<details>
<summary><b>🔐 Update Credentials Later</b></summary>

### Option 1: Re-run installer
```bash
python3 install/install.py    # or install.sh / install.cmd
```

### Option 2: Edit .env file
In project root, edit `.env`:
```
CAPTIVE_PORTAL_USERNAME="new_username"
CAPTIVE_PORTAL_PASSWORD="new_password"
```

### Option 3: Environment variables
```bash
export CAPTIVE_PORTAL_USERNAME="your_username"
export CAPTIVE_PORTAL_PASSWORD="your_password"
```

</details>

---

## 📚 Need More Help?

See [README.md](README.md) for full documentation.
