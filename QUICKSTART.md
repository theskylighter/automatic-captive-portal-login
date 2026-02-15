# Quick Start Guide

## Installation (5 minutes)

### Option 1: Universal Installer (Recommended)
```bash
python3 install/install.py
```

### Option 2: Windows
```batch
install\install-windows.bat
```

### Option 3: Linux/macOS
```bash
./install/install-linux.sh
```

## Run the Script

**Windows:**
```batch
windows\autologin.bat
```

**Linux/macOS:**
```bash
./linux/login.sh
```

## Setup Automation

### Windows - Task Scheduler
1. Search for "Task Scheduler"
2. Create Task
3. Set trigger: Daily at desired time
4. Set action: Run `windows\autologin.bat`

### Linux/macOS - Crontab
```bash
crontab -e
# Add this line to run daily at 7 AM:
0 7 * * * /path/to/project/linux/login.sh
```

## Update Credentials

Edit `.env` file or run installer again.

## Need Help?

See [README.md](README.md) for detailed documentation.
