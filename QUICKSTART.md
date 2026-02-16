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

### Windows - Task Scheduler
1. Search for "Task Scheduler" → Click "Create Task"
2. **General:** Name it "Campus Network Login"
3. **Triggers:** Click "New" → Daily at 12:00 AM
4. **Actions:** Start program → `windows\autologin.bat`
5. Click OK, done!

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
