# SETUP INSTRUCTIONS
**Campaign Control Center Dashboard - Step-by-Step Installation Guide**

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [First-Time Setup](#first-time-setup)
4. [Running the Dashboard](#running-the-dashboard)
5. [Configuration](#configuration)
6. [Integration Verification](#integration-verification)
7. [Next Steps](#next-steps)

---

## Prerequisites

### System Requirements

**Operating System:**
- Windows 10 (64-bit) or later
- Windows 11 (64-bit) recommended

**Python Version:**
- Python 3.9 or later (Python 3.10+ recommended)
- To check your Python version, open Command Prompt and run:
  ```cmd
  python --version
  ```
- If you see "Python 3.9.x" or higher, you're good to go
- If not installed, download from: https://www.python.org/downloads/

**Disk Space:**
- Minimum: 100 MB for dashboard files
- Recommended: 500 MB (including database growth)

**Memory:**
- Minimum: 2 GB RAM
- Recommended: 4 GB RAM or more

**Required Folders:**
Your existing email outreach system should already have these folders:
```
C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\
```

### Verify Prerequisites

**Step 1: Check Python Installation**

Open Command Prompt (press `Win + R`, type `cmd`, press Enter) and run:

```cmd
python --version
```

Expected output: `Python 3.9.x` or higher

**Step 2: Check pip (Python Package Installer)**

```cmd
pip --version
```

Expected output: `pip 23.x.x from ...`

If pip is not installed:
```cmd
python -m ensurepip --upgrade
```

**Step 3: Check Existing Data Files**

Navigate to your outreach sequences directory:

```cmd
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"
dir
```

You should see files like:
- `sent_tracker.csv`
- `response_tracker.csv`
- `coordination.json`
- Prospect CSV files (e.g., `debarment_prospects.csv`)

If these files don't exist yet, that's okay - the dashboard will create empty templates.

---

## Installation Steps

### Step 1: Navigate to Dashboard Directory

Open Command Prompt and navigate to the dashboard folder:

```cmd
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"
```

**Verify you're in the right place:**

```cmd
dir
```

You should see files like:
- `dashboard.py`
- `requirements.txt`
- `database\` (folder)
- `pages\` (folder)
- `integrations\` (folder)

### Step 2: Create Virtual Environment (Recommended)

Creating a virtual environment keeps dashboard dependencies separate from your system Python:

```cmd
python -m venv venv
```

This creates a `venv` folder in your dashboard directory.

**Activate the virtual environment:**

```cmd
venv\Scripts\activate
```

Your command prompt should now show `(venv)` at the beginning:

```
(venv) C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard>
```

**Note:** You'll need to activate this virtual environment every time you want to run the dashboard.

### Step 3: Install Python Dependencies

With the virtual environment activated, install required packages:

```cmd
pip install -r requirements.txt
```

This will install:
- `streamlit` - Dashboard framework
- `pandas` - Data manipulation
- `plotly` - Interactive charts
- `cryptography` - Password encryption
- `pytz` - Timezone support
- `email-validator` - Email validation

**Expected output:**
```
Successfully installed streamlit-1.28.0 pandas-2.0.0 plotly-5.17.0 cryptography-41.0.0 pytz-2023.3 ...
```

**Verify installation:**

```cmd
streamlit --version
```

Expected output: `Streamlit, version 1.28.x`

### Step 4: Verify Existing Script Locations

Check that your existing email scripts are in place:

```cmd
cd ..
dir "Email Campaign 2025-11-3"
```

You should see:
- `send_initial_outreach.py`
- `send_followup.py`
- `config.py`
- `coordination.py`

**Return to dashboard directory:**

```cmd
cd "Email Outreach Dashboard"
```

### Step 5: Initialize Database

The dashboard will automatically create its database on first run, but you can manually initialize it:

```cmd
python database\schema.py
```

**Expected output:**
```
Database initialized successfully at: campaign_control.db
Tables created: verticals, email_accounts, account_verticals, email_templates, settings
```

**Verify database creation:**

```cmd
dir *.db
```

You should see: `campaign_control.db`

### Step 6: Configure Base Paths (Windows Only)

The dashboard needs to know where your outreach files are located. Open `utils\windows_paths.py` in a text editor:

```cmd
notepad utils\windows_paths.py
```

**Check the BASE_DIR setting:**

```python
BASE_DIR = r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"
```

If your folder location is different, update this path. Make sure to:
- Use raw strings (prefix with `r`)
- Use backslashes (`\`) or forward slashes (`/`)
- Include the full absolute path

**Save and close the file.**

### Step 7: Migrate Existing Data (Optional)

If you have existing prospect lists, you can migrate them to the dashboard's format:

**Create verticals folder structure:**

```cmd
mkdir verticals
cd verticals
mkdir debarment
mkdir food_recall
mkdir grant_alerts
cd ..
```

**Copy existing prospect CSVs:**

```cmd
copy ..\debarment_prospects.csv verticals\debarment\prospects.csv
copy ..\food_recall_prospects.csv verticals\food_recall\prospects.csv
copy ..\grant_alerts_prospects.csv verticals\grant_alerts\prospects.csv
```

**Note:** This step is optional. You can also upload prospects through the dashboard UI later.

---

## First-Time Setup

### Launch the Dashboard

With your virtual environment activated, run:

```cmd
streamlit run dashboard.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.xxx:8501
```

**The dashboard will automatically open in your default web browser.**

If it doesn't open automatically, copy and paste the Local URL into your browser:
```
http://localhost:8501
```

### Welcome Screen

You should see the Campaign Control Center home page with:
- Main title: "Campaign Control Center"
- Welcome message
- Navigation instructions
- Quick start cards

### Step 1: Add Your First Email Account

1. Click **"📧 Email Accounts"** in the left sidebar
2. Click **"➕ Add New Email Account"** button
3. Fill in the form:

   **Example for Gmail:**
   ```
   Email Address: yourname@gmail.com
   Display Name: Main Campaign Account
   SMTP Host: smtp.gmail.com
   SMTP Port: 587
   SMTP Username: yourname@gmail.com
   Password: your-app-specific-password
   Daily Send Limit: 100
   Use TLS: Yes (checked)
   Assigned Verticals: (select applicable verticals)
   ```

   **Example for Outlook:**
   ```
   Email Address: yourname@outlook.com
   Display Name: Main Campaign Account
   SMTP Host: smtp-mail.outlook.com
   SMTP Port: 587
   SMTP Username: yourname@outlook.com
   Password: your-password
   Daily Send Limit: 100
   Use TLS: Yes (checked)
   Assigned Verticals: (select applicable verticals)
   ```

4. Click **"Test Connection"** to verify SMTP settings
5. If successful, click **"Save Account"**

**Important Notes:**
- For Gmail, you must use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password
- For Outlook, ensure SMTP access is enabled in your account settings
- Passwords are encrypted before being stored in the database

### Step 2: Create Your First Vertical

1. Click **"🔧 Verticals Manager"** in the left sidebar
2. Click **"➕ Add New Vertical"** button
3. Fill in the form:

   **Example:**
   ```
   Vertical ID: debarment
   Display Name: Federal Debarment Monitoring
   Target Industry: Federal Contractors
   Active: Yes (checked)
   ```

4. Click **"Create Vertical"**

**This will automatically:**
- Create database entry
- Create folder: `verticals\debarment\`
- Create empty prospect CSV: `verticals\debarment\prospects.csv`
- Create templates folder: `verticals\debarment\templates\`

### Step 3: Upload Your First Prospect List

1. Click **"📥 Prospects Manager"** in the left sidebar
2. Select your vertical from the dropdown (e.g., "debarment")
3. Click **"Upload Prospects CSV"** or drag-and-drop a CSV file

**Your CSV must have these columns (minimum):**
- `email` - Prospect email address (required)
- `first_name` - First name (required)
- `company` - Company name (required)
- `state` - State abbreviation (required)

**Optional columns:**
- `last_name`
- `title`
- `phone`
- `city`
- `zip`
- `industry`

**Example CSV format:**
```csv
email,first_name,last_name,company,state,title
john@example.com,John,Smith,Acme Corp,CA,CEO
jane@example.com,Jane,Doe,Example LLC,NY,Director
```

4. Click **"Upload"** and wait for validation
5. Review upload summary (new prospects, duplicates skipped)
6. Click **"Confirm Upload"**

### Step 4: Configure Your First Email Template

1. Click **"✉️ Templates Manager"** in the left sidebar
2. Select your vertical from the tabs
3. Click **"➕ Create New Template"** button
4. Fill in the form:

   **Example Initial Outreach Template:**
   ```
   Template Name: Initial Outreach v1
   Template Type: Initial
   Subject Line: Important notice for {company}
   
   Email Body:
   Hi {first_name},
   
   I wanted to reach out regarding a critical compliance matter that may affect {company}.
   
   As a {title} in {state}, you should be aware of recent developments in federal contractor debarment monitoring.
   
   Would you have 10 minutes this week to discuss?
   
   Best regards,
   Your Name
   ```

5. Use the **Live Preview** pane to see how your template renders
6. Available variables:
   - `{first_name}` - Prospect's first name
   - `{last_name}` - Prospect's last name
   - `{company}` - Company name
   - `{state}` - State
   - `{title}` - Job title
   - `{email}` - Email address
   - `{greeting}` - Auto-generated greeting (Hi First, Dear Mr. Last, etc.)

7. Click **"Save Template"**

**Note:** Template changes are immediately available to the dashboard. For integration with your existing email scripts, see the Integration Verification section below.

### Step 5: Verify Dashboard Metrics

1. Click **"📊 Dashboard"** in the left sidebar (home page)
2. You should now see:
   - Prospect counts for your vertical
   - Email account status showing your account
   - Charts (may be empty if no emails sent yet)

**Initial setup is complete!**

---

## Running the Dashboard

### Starting the Dashboard

**Every time you want to use the dashboard:**

1. Open Command Prompt
2. Navigate to dashboard directory:
   ```cmd
   cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"
   ```

3. Activate virtual environment:
   ```cmd
   venv\Scripts\activate
   ```

4. Run Streamlit:
   ```cmd
   streamlit run dashboard.py
   ```

5. Dashboard opens in browser at: `http://localhost:8501`

### Expected Startup Output

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.xxx:8501

  For better performance, install watchdog:
    pip install watchdog
```

### Accessing in Browser

- **Local URL:** `http://localhost:8501` (use this on your computer)
- **Network URL:** Use this to access from other devices on your network

### Stopping the Dashboard

To stop the dashboard:

1. Go to the Command Prompt window where Streamlit is running
2. Press `Ctrl + C`
3. Confirm by pressing `Y` if prompted

**Alternative:** Just close the Command Prompt window

### Troubleshooting Startup Issues

**Issue: "python is not recognized as an internal or external command"**

**Solution:**
1. Python is not in your PATH
2. Reinstall Python and check "Add Python to PATH" during installation
3. Or use full path: `C:\Python39\python.exe dashboard.py`

---

**Issue: "streamlit: command not found"**

**Solution:**
1. Virtual environment not activated
2. Run: `venv\Scripts\activate`
3. Verify: command prompt shows `(venv)` prefix

---

**Issue: "Address already in use"**

**Solution:**
1. Another instance of Streamlit is running
2. Close the other instance or use a different port:
   ```cmd
   streamlit run dashboard.py --server.port 8502
   ```

---

**Issue: "ModuleNotFoundError: No module named 'streamlit'"**

**Solution:**
1. Dependencies not installed
2. Run: `pip install -r requirements.txt`
3. Verify: `pip list | findstr streamlit`

---

**Issue: "Database is locked"**

**Solution:**
1. Dashboard already running in another window
2. Close other instance
3. If persists, delete `campaign_control.db-journal` file

---

## Configuration

### Adjusting Base Directory Paths

**File:** `utils\windows_paths.py`

**Edit this file to change where the dashboard looks for data:**

```python
# Base directory for all outreach data
BASE_DIR = r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"

# You can customize subdirectories (optional)
VERTICALS_DIR = os.path.join(BASE_DIR, "verticals")
SENT_TRACKER = os.path.join(BASE_DIR, "sent_tracker.csv")
RESPONSE_TRACKER = os.path.join(BASE_DIR, "response_tracker.csv")
COORDINATION_FILE = os.path.join(BASE_DIR, "coordination.json")
```

**After editing, restart the dashboard for changes to take effect.**

### Setting Business Hours

**Page:** ⚙️ Settings

1. Navigate to Settings page in dashboard
2. Scroll to **"Campaign Timing Settings"**
3. Adjust:
   - **Business Hours Start:** Default 9:00 AM EST
   - **Business Hours End:** Default 3:00 PM EST
   - **Timezone:** Default US/Eastern
4. Click **"Save Settings"**

**These settings control when automated campaigns can send emails.**

### Adjusting Rate Limits

**Per Email Account:**

1. Go to **📧 Email Accounts** page
2. Click **"Edit"** next to the account
3. Change **"Daily Send Limit"**
4. Click **"Save Changes"**

**Global Rate Limiting:**

1. Go to **⚙️ Settings** page
2. Scroll to **"Anti-Spam Settings"**
3. Adjust:
   - **Minimum Delay Between Emails:** Default 10 seconds
   - **Maximum Delay Between Emails:** Default 30 seconds
   - **Break Frequency:** Every 50 emails
   - **Break Duration:** 5 minutes
4. Click **"Save Settings"**

### Enabling/Disabling Features

**Conservative Pacing Mode:**

1. Go to **⚙️ Settings** page
2. Toggle **"Conservative Pacing Mode"**
   - **On:** Slower, more cautious sending
   - **Off:** Faster sending (up to limits)
3. Click **"Save Settings"**

**Pausing All Campaigns:**

1. Go to **📅 Campaign Planner** page
2. Click **"⏸️ Pause All Campaigns"** button
3. Confirm action

**Resuming Campaigns:**

1. Go to **📅 Campaign Planner** page
2. Click **"▶️ Resume All Campaigns"** button

---

## Integration Verification

### Verify Dashboard Reads Script Data

**Test 1: Verify sent_tracker.csv is read correctly**

1. Manually add a test entry to `sent_tracker.csv`:
   ```csv
   vertical_id,prospect_email,email_type,sent_datetime,email_account
   debarment,test@example.com,initial,2025-11-04 10:00:00,yourname@gmail.com
   ```

2. Go to dashboard **📊 Dashboard** page
3. Refresh the page (F5)
4. Check metrics:
   - "Emails Sent Today" should increase by 1
   - "Emails Sent This Week" should increase by 1

**If metrics don't update:**
- Check that `BASE_DIR` in `utils\windows_paths.py` is correct
- Check that `sent_tracker.csv` exists in that location
- Check CSV formatting (no extra spaces, correct column names)

---

**Test 2: Verify response_tracker.csv is read correctly**

1. Manually add a test entry to `response_tracker.csv`:
   ```csv
   vertical_id,prospect_email,response_datetime,response_type
   debarment,test@example.com,2025-11-04 11:00:00,reply
   ```

2. Go to dashboard **📊 Dashboard** page
3. Refresh the page (F5)
4. Check:
   - Response rate should update
   - Response chart should show data

---

**Test 3: Verify coordination.json is read correctly**

1. Check if `coordination.json` exists in your outreach sequences folder
2. Go to dashboard **📅 Campaign Planner** page
3. You should see:
   - Current campaign status
   - Scripts running indicator
   - Capacity information

**If coordination status shows "File not found":**
- File doesn't exist yet (normal if scripts haven't run)
- Dashboard will create default coordination.json on first save

---

### Verify Scripts Can Read Dashboard Data

**Test 1: Verify scripts can access uploaded prospects**

1. Upload a prospect CSV via dashboard to a vertical (e.g., "debarment")
2. Open Command Prompt and run:
   ```cmd
   cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"
   python -c "import pandas as pd; df = pd.read_csv('verticals/debarment/prospects.csv'); print(df.head())"
   ```

3. You should see the first few rows of your uploaded prospects

**If you get an error:**
- Check file path is correct
- Verify CSV was uploaded successfully in dashboard
- Check file permissions

---

**Test 2: Verify coordination system**

1. From dashboard, pause campaigns: **📅 Campaign Planner** → **"⏸️ Pause All Campaigns"**
2. Open `coordination.json` in a text editor:
   ```cmd
   notepad ..\coordination.json
   ```

3. You should see:
   ```json
   {
     "status": "paused",
     "last_updated": "2025-11-04 14:30:00",
     ...
   }
   ```

4. From dashboard, resume campaigns: **▶️ Resume All Campaigns**
5. Check `coordination.json` again - status should be "active"

---

**Test 3: Verify template updates propagate**

**Note:** In v1.0, templates are stored in the database only. For full integration with scripts, you'll need to export templates to text files (coming in v1.1).

**Current workflow:**
1. Edit templates in dashboard
2. Templates are saved to database
3. Your scripts need to be updated to read from the dashboard's database OR
4. Export templates manually via Settings page

---

### Integration Health Checklist

Run through this checklist to ensure everything is connected:

- [ ] Dashboard can read `sent_tracker.csv` (metrics update)
- [ ] Dashboard can read `response_tracker.csv` (response rates show)
- [ ] Dashboard can read `coordination.json` (planner shows status)
- [ ] Dashboard can read existing prospect CSVs
- [ ] Dashboard can write new prospect CSVs that scripts can read
- [ ] Dashboard can update `coordination.json` (pause/resume works)
- [ ] Email accounts are configured correctly (test connection passes)
- [ ] All verticals are created and have prospect folders
- [ ] Templates are saved and visible in dashboard

**All checkboxes checked?** You're fully integrated! ✅

---

## Next Steps

### For Daily Use

**Morning Routine:**
1. Start dashboard: `streamlit run dashboard.py`
2. Check **📊 Dashboard** for overnight metrics
3. Review **📅 Campaign Planner** for today's plan
4. Check **📧 Email Accounts** for quota usage
5. Monitor campaigns throughout the day

**Before Running Email Scripts:**
1. Verify daily quotas not exceeded
2. Check business hours settings
3. Ensure coordination.json shows "active"
4. Review prospect lists have available contacts

**After Running Email Scripts:**
1. Refresh dashboard to see updated metrics
2. Verify sent counts match script output
3. Check for any errors in error_log.csv
4. Review response rates

### For Adding New Verticals

1. **📊 Verticals Manager** → Create new vertical
2. **📥 Prospects Manager** → Upload prospects for new vertical
3. **✉️ Templates Manager** → Create email templates for new vertical
4. **📧 Email Accounts** → Assign email account(s) to new vertical
5. Test with small prospect list first
6. Monitor performance on **📊 Dashboard**

### For Campaign Optimization

1. **Track response rates** on Dashboard page
2. **A/B test templates** - create multiple templates per vertical
3. **Adjust send times** based on response patterns
4. **Monitor account health** - watch quota usage
5. **Review weekly trends** in charts
6. **Optimize daily limits** based on capacity needs

### For Troubleshooting

If you encounter any issues:

1. **Check TROUBLESHOOTING.md** - Common issues and solutions
2. **Review error_log.csv** - Detailed error messages
3. **Test SMTP connections** - Email Accounts page
4. **Verify file paths** - Settings page
5. **Restart dashboard** - Close and reopen
6. **Check database** - Recreate if corrupted

### For Advanced Features (Coming in v1.1)

- Automated template export to text files
- Real-time script monitoring
- Advanced analytics and reporting
- Multi-user support with authentication
- Automated backup and restore
- API endpoints for script integration

---

## Quick Reference Commands

**Start Dashboard:**
```cmd
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"
venv\Scripts\activate
streamlit run dashboard.py
```

**Stop Dashboard:**
```
Ctrl + C
```

**Reinstall Dependencies:**
```cmd
pip install -r requirements.txt --upgrade
```

**Reset Database (WARNING: Deletes all data):**
```cmd
del campaign_control.db
python database\schema.py
```

**Check Dashboard Version:**
```cmd
python -c "import streamlit; print(streamlit.__version__)"
```

---

## Support and Documentation

**Documentation Files:**
- `SETUP_INSTRUCTIONS.md` (this file) - Installation and setup
- `TROUBLESHOOTING.md` - Common issues and fixes
- `README.md` - Project overview and architecture
- `INTEGRATION_API_GUIDE.md` - For developers integrating with scripts

**Getting Help:**
- Review documentation files above
- Check `error_log.csv` for error details
- Review test report: `TEST_REPORT.md`
- Contact project administrator

---

**Setup Complete!** 🎉

You now have a fully functional Campaign Control Center dashboard integrated with your email outreach system.

**Dashboard URL:** http://localhost:8501

Happy campaigning! 📧✨

---

**Document Version:** 1.0  
**Last Updated:** November 4, 2025  
**Compatible With:** Campaign Control Center v1.0
