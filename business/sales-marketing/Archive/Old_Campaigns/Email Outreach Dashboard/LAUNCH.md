# 🚀 Launch Guide - Campaign Control Center

**Quick Start:** Get your dashboard running in 5 minutes!

---

## Prerequisites Check ✅

Before launching, ensure you have:
- [ ] Python 3.10+ installed
- [ ] Windows OS (current version optimized for Windows)
- [ ] Terminal/Command Prompt access
- [ ] Internet connection (for first-time setup)

---

## Option 1: First-Time Launch (New Installation)

### Step 1: Open Terminal
```powershell
# Open PowerShell or Command Prompt
# Navigate to dashboard directory
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"
```

### Step 2: Create Virtual Environment
```powershell
# Create venv (first time only)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# You should see (venv) in your prompt
```

### Step 3: Install Dependencies
```powershell
# Install all required packages
pip install -r requirements.txt

# This takes 2-3 minutes
# You'll see packages being installed
```

### Step 4: Launch Dashboard
```powershell
# Start the dashboard
streamlit run dashboard.py

# Dashboard will open in your browser automatically!
# If not, go to: http://localhost:8501
```

### Step 5: Initial Setup (In Browser)

Dashboard opens → Follow these steps:

1. **Welcome Page**
   - Read the quick start guide
   - Check system status

2. **Setup Email Account**
   - Go to: 📧 Email Accounts (sidebar)
   - Click "Add Email Account"
   - Fill in SMTP details
   - Test connection
   - Save

3. **Create Vertical**
   - Go to: 🔧 Verticals Manager
   - Click "Create New Vertical"
   - Enter vertical ID (e.g., "debarment")
   - Enter display name (e.g., "Debarment Services")
   - Enter target industry
   - Save

4. **Upload Prospects**
   - Go to: 📥 Prospects Manager
   - Select vertical
   - Drag-and-drop CSV file
   - Verify upload

5. **Create Templates**
   - Go to: ✉️ Templates Manager
   - Create Initial Outreach template
   - Create Follow-up template
   - **Important:** Click "📥 Sync All Templates to Files" at bottom!

6. **Sync Templates to Files** ⭐ CRITICAL
   - Still in Templates Manager
   - Scroll to bottom
   - Click **"📥 Sync All Templates to Files"**
   - Wait for success message
   - Now email scripts can use your templates!

7. **Ready!**
   - Go to: 📊 Dashboard
   - View your campaign metrics
   - Start sending emails!

---

## Option 2: Regular Launch (Already Set Up)

### Quick Launch:
```powershell
# Navigate to dashboard folder
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"

# Activate virtual environment
.\venv\Scripts\activate

# Launch
streamlit run dashboard.py
```

### One-Liner (PowerShell):
```powershell
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"; .\venv\Scripts\activate; streamlit run dashboard.py
```

---

## Option 3: Launch with WSL (Windows Subsystem for Linux)

### If Running from WSL Terminal:
```bash
# Navigate to dashboard
cd "/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences/Email Outreach Dashboard"

# Activate venv
source venv/bin/activate

# Launch
streamlit run dashboard.py
```

---

## Stopping the Dashboard

### Method 1: Terminal
Press `Ctrl + C` in the terminal where Streamlit is running

### Method 2: Close Browser
Just close the browser tab (terminal keeps running in background)

### Method 3: Kill Process (If Stuck)
```powershell
# Find Streamlit process
tasklist | findstr streamlit

# Kill it
taskkill /IM streamlit.exe /F
```

---

## Troubleshooting Launch Issues

### Issue 1: "Python not found"
**Solution:**
```powershell
# Check if Python is installed
python --version

# If not installed, download from: https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

### Issue 2: "streamlit command not found"
**Solution:**
```powershell
# Make sure venv is activated (you should see (venv) in prompt)
.\venv\Scripts\activate

# If still not working, reinstall
pip install streamlit
```

### Issue 3: "Port 8501 already in use"
**Solution:**
```powershell
# Kill existing Streamlit process
taskkill /IM streamlit.exe /F

# Or use different port
streamlit run dashboard.py --server.port 8502
```

### Issue 4: Dashboard opens but shows errors
**Solution:**
```powershell
# Check if database is initialized
# Look for campaign_control.db in data/ folder

# If missing, dashboard will create it automatically on first run

# Check logs in terminal for specific error messages
```

### Issue 5: "Module not found" errors
**Solution:**
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue 6: Templates not syncing
**Solution:**
1. Go to Templates Manager
2. Scroll to bottom
3. Click "📥 Sync All Templates to Files"
4. Check for success message
5. Verify files exist in templates/ folders

---

## Dashboard URLs

### Main Dashboard:
```
http://localhost:8501
```

### Alternative Port (if 8501 busy):
```
http://localhost:8502
```

### Network URL (Access from other devices):
```
http://YOUR-IP-ADDRESS:8501
# Find your IP: ipconfig (Windows) or ifconfig (Linux)
```

---

## Running Multiple Dashboards

You can run multiple instances on different ports:

```powershell
# Terminal 1 (Dashboard for Team A)
streamlit run dashboard.py --server.port 8501

# Terminal 2 (Dashboard for Team B)
streamlit run dashboard.py --server.port 8502 --server.baseUrlPath /teamB
```

---

## Auto-Launch on Startup (Advanced)

### Create Batch File:
Create `launch_dashboard.bat`:
```batch
@echo off
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"
call venv\Scripts\activate
streamlit run dashboard.py
```

### Double-click to launch!

### Add to Startup (Optional):
1. Press `Win + R`
2. Type `shell:startup`
3. Copy `launch_dashboard.bat` to startup folder
4. Dashboard launches on Windows startup

---

## Performance Tips

### Speed Up Launch:
```powershell
# Skip browser auto-open
streamlit run dashboard.py --server.headless true

# Then manually open: http://localhost:8501
```

### Reduce Memory Usage:
```powershell
# Limit Streamlit memory
streamlit run dashboard.py --server.maxUploadSize 50
```

### Clear Cache:
In the dashboard:
- Go to Settings (⚙️)
- Click "Clear Cache"
- Refresh page

---

## Testing After Launch

### Quick Test Checklist:
- [ ] Dashboard opens in browser
- [ ] All 8 pages accessible in sidebar
- [ ] Welcome page displays
- [ ] Dashboard shows metrics (may be 0 if first time)
- [ ] Email Accounts page loads
- [ ] Verticals Manager loads
- [ ] Templates Manager loads
- [ ] Campaign Planner loads
- [ ] Campaign Control loads
- [ ] Settings page loads

### Full Test (After Setup):
- [ ] Add email account successfully
- [ ] Create vertical successfully
- [ ] Upload prospects CSV
- [ ] Create initial template
- [ ] Create followup template
- [ ] Sync templates to files (success message)
- [ ] Send test email (works)
- [ ] View live feed (shows sent emails)

---

## What's Running?

When dashboard is launched:
- **Python Process**: Runs Streamlit server
- **Web Server**: Serves dashboard on port 8501
- **Database**: SQLite file-based (no separate server)
- **File Watcher**: Monitors for code changes (auto-reload)

---

## Directory Structure (After Launch)

```
Email Outreach Dashboard/
├── dashboard.py              # ← Launch this file
├── campaign_control.db       # Created on first run
├── .encryption_key           # Created on first run
├── venv/                     # Virtual environment
├── pages/                    # Dashboard pages
├── components/               # UI components
├── database/                 # Database layer
├── integrations/             # External integrations
└── utils/                    # Utilities
```

---

## Common Workflows

### Workflow 1: Daily Check
```
1. Launch dashboard
2. Go to Dashboard page
3. Check today's metrics
4. Go to Campaign Control → Live Feed
5. Monitor sent emails
```

### Workflow 2: Add New Prospects
```
1. Launch dashboard
2. Go to Prospects Manager
3. Select vertical
4. Upload CSV
5. Verify count updated
```

### Workflow 3: Edit Templates
```
1. Launch dashboard
2. Go to Templates Manager
3. Click Edit on template
4. Make changes
5. Save
6. **Click "Sync All Templates to Files"** ← Don't forget!
7. Email scripts now use updated templates
```

### Workflow 4: Send Test Email
```
1. Launch dashboard
2. Go to Campaign Control
3. Click "Test Emails" tab
4. Select account and vertical
5. Enter your email
6. Click "Send Test Email"
7. Check your inbox
```

---

## Keyboard Shortcuts

While dashboard is running:

- `Ctrl + C` - Stop dashboard
- `R` (in browser) - Refresh dashboard
- `C` (in browser) - Clear cache
- `Ctrl + Shift + R` - Hard refresh (clear cache)

---

## Browser Compatibility

### Recommended Browsers:
- ✅ Google Chrome (best)
- ✅ Microsoft Edge (best)
- ✅ Firefox (good)
- ⚠️ Safari (works but slower)
- ❌ Internet Explorer (not supported)

---

## Security Notes

### Port Access:
- Dashboard listens on localhost (127.0.0.1) by default
- Only accessible from your computer
- To allow network access: `--server.address 0.0.0.0` (not recommended for production)

### Data Security:
- Email passwords encrypted with Fernet
- Encryption key stored in `.encryption_key`
- SQLite database stores all data locally
- No data sent to external servers

### Best Practices:
- Don't commit `.encryption_key` to Git
- Don't share `campaign_control.db`
- Keep virtual environment activated
- Close dashboard when not in use

---

## Useful Commands Reference

```powershell
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Update Streamlit
pip install --upgrade streamlit

# Check Streamlit version
streamlit version

# View Streamlit config
streamlit config show

# Clear Streamlit cache (filesystem)
streamlit cache clear

# Get help
streamlit --help
```

---

## Next Steps After Launch

### 1. Complete Initial Setup
Follow Step 5 from "First-Time Launch" above

### 2. Configure Email Scripts
- Ensure email scripts read from template files
- Test script execution
- Verify coordination with dashboard

### 3. Test Full Workflow
- Send test email from dashboard
- Run email script manually
- Verify Live Feed shows sent emails
- Check Dashboard metrics update

### 4. Review Documentation
- Read `SETUP_INSTRUCTIONS.md` for detailed setup
- Read `TROUBLESHOOTING.md` for common issues
- Read `docs/USER_GUIDE.md` for features

### 5. Customize
- Adjust settings in Settings page
- Configure business hours
- Set email quotas
- Customize templates

---

## Getting Help

### If Dashboard Won't Launch:
1. Check this guide's Troubleshooting section
2. Read `TROUBLESHOOTING.md`
3. Check terminal output for error messages
4. Verify all prerequisites installed

### If Features Don't Work:
1. Check Dashboard → Settings for configuration
2. Review page-specific help text
3. Check `docs/USER_GUIDE.md`
4. Test with fresh data

---

## Success! 🎉

If you see the dashboard in your browser:

✅ **You're ready to go!**

**Next:** Complete the initial setup (Step 5 above) to start managing your email campaigns!

---

**Created By:** Claude Code
**Date:** November 4, 2025
**Version:** 1.0

**Quick Launch Command:**
```powershell
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"; .\venv\Scripts\activate; streamlit run dashboard.py
```
