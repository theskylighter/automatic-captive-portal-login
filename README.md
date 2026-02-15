# Captive Portal Auto-Login

Automatic login to campus network captive portal with multi-platform support.

## 📁 Project Structure

```
automatic-captive-portal-login-v2/
├── src/
│   └── login.py                 # Core login script (shared for all platforms)
├── windows/
│   └── autologin.bat            # Windows launcher script
├── linux/
│   └── login.sh                 # Linux/macOS launcher script
├── install/
│   ├── install.py               # 🎯 Universal installer (Python)
│   ├── install-windows.bat      # Windows-specific installer
│   └── install-linux.sh         # Linux/macOS installer
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Universal Installation (All Platforms)
```bash
python3 install/install.py
```

### Platform-Specific Installation

**Windows:**
```batch
install\install-windows.bat
```

**Linux/macOS:**
```bash
chmod +x install/install-linux.sh
./install/install-linux.sh
```

## 📋 Pre-Requisites

- Python 3.6 or higher
- pip (Python package manager)
- Internet connection

## ⚙️ Setup Instructions

1. **Clone or download the repository**

2. **Run the installer for your platform** (see Quick Start above)
   - This will install required Python dependencies automatically

3. **Configure your credentials**
   - Open `src/login.py` in a text editor
   - Replace the placeholder credentials:
     ```python
     USERNAME = "your_username"
     PASSWORD = "your_password"
     ```

4. **Test the script**
   - **Windows:** Double-click `windows\autologin.bat` or run it from command prompt
   - **Linux/macOS:** Run `./linux/login.sh` from terminal

## 🔄 Periodic Automation

### Windows (Task Scheduler)
1. Press `Win + S` and search for "Task Scheduler"
2. Click "Create Task" in the right panel
3. **General tab:**
   - Name: "Campus Network Auto-Login"
   - Check "Run whether user is logged on or not"
4. **Triggers tab:**
   - Click "New"
   - Set to "Daily" at your preferred time (e.g., 12:00 AM)
5. **Actions tab:**
   - Click "New"
   - Action: "Start a program"
   - Program: `windows\autologin.bat`
6. Click OK and enter your password if prompted

### Linux/macOS (Crontab)
1. Open crontab editor: `crontab -e`
2. Add a line to run the script periodically:
   ```bash
   # Run daily at 12:00 AM
   0 0 * * * /path/to/project/linux/login.sh >> /path/to/project/log/auto-login.log 2>&1
   ```
3. Replace `/path/to/project` with the actual path to your project directory

## 📝 How It Works

- The script continuously monitors network connectivity
- When a captive portal is detected, it automatically sends login credentials
- Upon successful login, the script exits
- If login fails, it retries after 5 seconds (up to 15 minutes timeout)

## 🐛 Troubleshooting

### Python not found
- **Windows:** Make sure Python is installed and added to PATH
  - Check: Open Command Prompt and run `python --version`
- **Linux/macOS:** Use `python3` instead of `python`

### "requests" module not found
- Run: `pip install -r requirements.txt`
- Or manually: `pip install requests`

### Connection errors
- Verify the captive portal URL is correct in `src/login.py` (LOGIN_URL variable)
- Check your credentials are correct

### Script doesn't run on schedule
- **Windows:** Check Task Scheduler logs for errors
- **Linux:** Check cron logs with `grep CRON /var/log/syslog`

## 📚 FAQ

### How do I find my Python path?
```bash
python -c "import sys; print(sys.executable)"
```

### Can I edit the code?
Yes! The code is open source. Feel free to modify:
- `LOGIN_URL` - Change the captive portal URL
- `HEADERS` - Update HTTP headers if needed
- `TIMEOUT_SECONDS` - Adjust the maximum wait time

### Is my password secure?
**No!** The password is stored in plain text in `src/login.py`. This is only suitable for institutional/campus networks with non-critical credentials.

**For sensitive passwords:** Consider using environment variables or a config file with restricted permissions.

## 📄 License

Check the repository for license information.

## 🤝 Contributing

Feel free to fork, modify, and improve the project!


