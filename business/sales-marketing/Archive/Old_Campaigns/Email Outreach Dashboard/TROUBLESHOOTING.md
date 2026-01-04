# TROUBLESHOOTING GUIDE
**Campaign Control Center Dashboard - Common Issues and Solutions**

---

## Table of Contents
1. [Dashboard Startup Issues](#dashboard-startup-issues)
2. [Database Errors](#database-errors)
3. [File and Path Issues](#file-and-path-issues)
4. [CSV Upload Issues](#csv-upload-issues)
5. [SMTP and Email Account Issues](#smtp-and-email-account-issues)
6. [Template Issues](#template-issues)
7. [Metrics and Data Issues](#metrics-and-data-issues)
8. [Integration Issues](#integration-issues)
9. [Performance Issues](#performance-issues)
10. [Common Error Messages](#common-error-messages)
11. [FAQ](#faq)

---

## Dashboard Startup Issues

### Issue: Dashboard Won't Start

**Symptom:**
When running `streamlit run dashboard.py`, nothing happens or you get an error.

**Likely Causes:**
1. Virtual environment not activated
2. Streamlit not installed
3. Python not in PATH
4. Wrong directory

**Solutions:**

**Solution 1: Verify Virtual Environment**
```cmd
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"
venv\Scripts\activate
```
Your prompt should show `(venv)` at the beginning.

**Solution 2: Reinstall Dependencies**
```cmd
pip install -r requirements.txt --upgrade
```

**Solution 3: Check Python Installation**
```cmd
python --version
```
Should show Python 3.9 or higher.

**Solution 4: Verify Directory**
```cmd
dir dashboard.py
```
If file not found, you're in the wrong directory.

**Prevention:**
- Always activate virtual environment before running dashboard
- Create a shortcut script (see FAQ #1)

---

### Issue: "Address Already in Use" Error

**Symptom:**
```
OSError: [Errno 98] Address already in use
```

**Likely Causes:**
1. Dashboard already running in another window
2. Another application using port 8501
3. Previous dashboard instance didn't close properly

**Solutions:**

**Solution 1: Close Existing Instance**
1. Check for other Command Prompt windows running Streamlit
2. Close them with `Ctrl + C`

**Solution 2: Use Different Port**
```cmd
streamlit run dashboard.py --server.port 8502
```
Then access at: `http://localhost:8502`

**Solution 3: Kill Process (Windows)**
```cmd
netstat -ano | findstr :8501
taskkill /PID <process_id> /F
```
Replace `<process_id>` with the PID from netstat output.

**Prevention:**
- Always close dashboard with `Ctrl + C` instead of closing window directly
- Use Task Manager to close orphaned Python processes

---

### Issue: Browser Doesn't Open Automatically

**Symptom:**
Dashboard starts successfully but browser doesn't open.

**Solution:**
Manually open browser and navigate to:
```
http://localhost:8501
```

**Alternative Solution:**
Copy the URL from Command Prompt output and paste into browser.

**Prevention:**
Set default browser in Windows settings.

---

### Issue: "ModuleNotFoundError"

**Symptom:**
```
ModuleNotFoundError: No module named 'streamlit'
```
or similar for `pandas`, `plotly`, etc.

**Likely Causes:**
1. Dependencies not installed
2. Virtual environment not activated
3. Wrong Python interpreter

**Solutions:**

**Solution 1: Install Dependencies**
```cmd
pip install -r requirements.txt
```

**Solution 2: Verify Virtual Environment**
```cmd
venv\Scripts\activate
pip list
```
Check that all required packages are listed.

**Solution 3: Recreate Virtual Environment**
```cmd
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Prevention:**
- Always activate virtual environment before running dashboard
- Check `pip list` to verify installations

---

## Database Errors

### Issue: "Database is Locked"

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Likely Causes:**
1. Multiple dashboard instances accessing database
2. Another process has database file open
3. Database file opened in SQLite browser/editor

**Solutions:**

**Solution 1: Close Other Instances**
1. Close all dashboard windows
2. Wait 10 seconds
3. Restart dashboard

**Solution 2: Delete Journal File**
```cmd
del campaign_control.db-journal
```
**WARNING:** Only do this when dashboard is NOT running.

**Solution 3: Restart Computer**
If problem persists, restart Windows to clear file locks.

**Prevention:**
- Run only one dashboard instance at a time
- Don't open database file in SQLite browser while dashboard is running

---

### Issue: "Database Corruption" or "Malformed Database"

**Symptom:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Likely Causes:**
1. Dashboard crashed during database write
2. Power failure
3. Disk errors

**Solutions:**

**Solution 1: Restore from Backup**
If you have a backup:
```cmd
copy campaign_control.db.backup campaign_control.db
```

**Solution 2: Recreate Database (WARNING: Loses Data)**
```cmd
ren campaign_control.db campaign_control.db.corrupt
python database\schema.py
```
This creates a fresh database. You'll need to:
- Re-add email accounts
- Re-create verticals
- Re-upload prospects

**Solution 3: Try SQLite Recovery**
```cmd
sqlite3 campaign_control.db ".recover" | sqlite3 campaign_control_recovered.db
```

**Prevention:**
- Enable automatic backups in Settings page (coming in v1.1)
- Manually backup database regularly:
  ```cmd
  copy campaign_control.db campaign_control.db.backup
  ```
- Don't force-close dashboard (use `Ctrl + C`)

---

### Issue: "No Such Table" Error

**Symptom:**
```
sqlite3.OperationalError: no such table: verticals
```

**Likely Causes:**
1. Database not initialized
2. Database file deleted
3. Wrong database file being used

**Solutions:**

**Solution 1: Initialize Database**
```cmd
python database\schema.py
```

**Solution 2: Check Database Location**
```cmd
dir campaign_control.db
```
Should be in dashboard root directory.

**Solution 3: Run Migrations**
```cmd
python database\migrations.py
```

**Prevention:**
- Don't delete `campaign_control.db` file
- Initialize database before first run

---

## File and Path Issues

### Issue: "File Not Found" Errors

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'C:\...\sent_tracker.csv'
```

**Likely Causes:**
1. Incorrect BASE_DIR configuration
2. File doesn't exist yet
3. Path separator issues (backslash vs forward slash)
4. Permissions issues

**Solutions:**

**Solution 1: Check BASE_DIR Configuration**
```cmd
notepad utils\windows_paths.py
```
Verify `BASE_DIR` points to correct location:
```python
BASE_DIR = r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"
```

**Solution 2: Create Missing Files**
If `sent_tracker.csv` doesn't exist:
```cmd
echo email,vertical_id,email_type,sent_datetime,email_account > sent_tracker.csv
```

If `response_tracker.csv` doesn't exist:
```cmd
echo email,vertical_id,response_datetime,response_type > response_tracker.csv
```

**Solution 3: Check File Exists**
```cmd
dir "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\sent_tracker.csv"
```

**Prevention:**
- Run dashboard from correct directory
- Verify BASE_DIR configuration after installation
- Create empty template files if they don't exist

---

### Issue: Windows Path Issues

**Symptom:**
Paths with spaces or special characters cause errors.

**Solutions:**

**Solution 1: Use Raw Strings**
In `windows_paths.py`:
```python
BASE_DIR = r"C:\Path With Spaces\folder"
```

**Solution 2: Use Forward Slashes**
```python
BASE_DIR = "C:/Path With Spaces/folder"
```

**Solution 3: Use os.path.join**
```python
import os
BASE_DIR = os.path.join("C:", "Business Factory (Research) 11-1-2025", "06_GO_TO_MARKET", "outreach_sequences")
```

**Prevention:**
- Always use raw strings (`r"..."`) for Windows paths
- Use `os.path.join()` when building paths programmatically

---

### Issue: Permission Denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: 'campaign_control.db'
```

**Likely Causes:**
1. File opened in another program
2. Insufficient user permissions
3. File is read-only

**Solutions:**

**Solution 1: Close Other Programs**
Close any programs that might have the file open (SQLite browser, Excel, etc.)

**Solution 2: Run as Administrator**
Right-click Command Prompt → "Run as Administrator"

**Solution 3: Check File Properties**
1. Right-click file → Properties
2. Uncheck "Read-only" if checked
3. Click Apply

**Solution 4: Change Folder Permissions**
1. Right-click dashboard folder → Properties → Security
2. Ensure your user account has "Full control"

**Prevention:**
- Don't open database files in other programs while dashboard is running
- Ensure proper folder permissions

---

## CSV Upload Issues

### Issue: CSV Upload Fails with Validation Error

**Symptom:**
"CSV validation failed: Missing required columns"

**Likely Causes:**
1. CSV missing required columns
2. Incorrect column names
3. Wrong delimiter (semicolon instead of comma)

**Solutions:**

**Solution 1: Check Required Columns**
Your CSV must have these columns (exact names, case-sensitive):
- `email`
- `first_name`
- `company`
- `state`

**Solution 2: Verify CSV Format**
Open in text editor (not Excel) and check:
```csv
email,first_name,company,state
john@example.com,John,Acme Corp,CA
jane@example.com,Jane,Example LLC,NY
```

**Solution 3: Fix Delimiter**
If using semicolons, convert to commas:
1. Open in Excel
2. Save As → CSV (Comma delimited)

**Solution 4: Use Template**
Download template from dashboard:
1. Go to Prospects Manager
2. Click "Download CSV Template"
3. Fill in your data
4. Upload completed template

**Prevention:**
- Always use dashboard's CSV template
- Verify column names are lowercase
- Use comma delimiter

---

### Issue: Duplicate Prospects Not Skipped

**Symptom:**
Upload shows "0 duplicates skipped" when you expect duplicates.

**Likely Causes:**
1. Email addresses differ in capitalization
2. Extra spaces in email addresses
3. Different email addresses (not actually duplicates)

**Solutions:**

**Solution 1: Check Email Formatting**
Duplicates are detected by email address (case-insensitive).
- `John@Example.com` and `john@example.com` are considered the same
- `john@example.com` and `john @example.com` (with space) are different

**Solution 2: Clean Data**
Before uploading:
1. Remove leading/trailing spaces
2. Convert emails to lowercase
3. Deduplicate in Excel/Pandas first

**Prevention:**
- Clean data before uploading
- Use Excel's "Remove Duplicates" feature first

---

### Issue: Large CSV Upload Takes Too Long

**Symptom:**
Uploading CSV with 10,000+ rows is very slow or times out.

**Solutions:**

**Solution 1: Split Into Smaller Files**
Split CSV into files of 1,000-2,000 rows each and upload sequentially.

**Solution 2: Increase Timeout**
Edit `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 200
maxMessageSize = 200
```

**Solution 3: Use Direct File Copy**
For very large files, copy directly to verticals folder:
```cmd
copy large_prospects.csv "verticals\<vertical_id>\prospects.csv"
```

**Prevention:**
- Keep uploads under 5,000 rows
- Split large lists into batches

---

### Issue: CSV Shows Wrong Data After Upload

**Symptom:**
Uploaded data doesn't appear correctly in prospect viewer.

**Solutions:**

**Solution 1: Refresh Page**
Press F5 to refresh the dashboard page.

**Solution 2: Clear Cache**
In dashboard, press `C` to clear cache, then refresh.

**Solution 3: Check File Encoding**
CSV must be UTF-8 encoded:
1. Open in Notepad
2. Save As → Select "UTF-8" encoding

**Prevention:**
- Always save CSVs with UTF-8 encoding
- Refresh page after upload

---

## SMTP and Email Account Issues

### Issue: Test Connection Fails

**Symptom:**
"SMTP connection failed: [Errno 10061] Connection refused"

**Likely Causes:**
1. Incorrect SMTP host or port
2. Firewall blocking connection
3. SMTP access disabled in email provider
4. Wrong credentials

**Solutions:**

**Solution 1: Verify SMTP Settings**

**Gmail:**
- SMTP Host: `smtp.gmail.com`
- SMTP Port: `587` (TLS) or `465` (SSL)
- Must use App Password (not regular password)
- Enable "Less secure app access" or use App Password

**Outlook/Hotmail:**
- SMTP Host: `smtp-mail.outlook.com`
- SMTP Port: `587`
- Must enable SMTP in account settings

**Office 365:**
- SMTP Host: `smtp.office365.com`
- SMTP Port: `587`
- May need to enable SMTP AUTH

**Solution 2: Check Firewall**
Temporarily disable firewall to test. If it works, add exception for Streamlit/Python.

**Solution 3: Test with telnet**
```cmd
telnet smtp.gmail.com 587
```
If connection refused, check network/firewall.

**Solution 4: Enable App Passwords**
For Gmail:
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate new app password
4. Use generated password in dashboard

**Prevention:**
- Use App Passwords for Gmail
- Verify SMTP settings with email provider documentation
- Test connection before saving account

---

### Issue: Emails Not Sending (Quota Exceeded)

**Symptom:**
Dashboard shows "Daily limit reached" for email account.

**Solutions:**

**Solution 1: Wait Until Tomorrow**
Daily quotas reset at midnight. Wait until next day.

**Solution 2: Increase Daily Limit**
1. Go to Email Accounts page
2. Edit account
3. Increase "Daily Send Limit"
4. **WARNING:** Don't exceed your provider's actual limit

**Solution 3: Add Additional Email Account**
Distribute sending across multiple accounts:
1. Add new email account
2. Assign to same verticals
3. Dashboard will balance load

**Solution 4: Manual Reset (Testing Only)**
```cmd
python -c "from database import models; models.reset_daily_counts()"
```
**WARNING:** Use only for testing. Violating provider limits risks account suspension.

**Prevention:**
- Set daily limits below provider maximums
- Use multiple accounts for high-volume campaigns
- Monitor quota usage on dashboard

---

### Issue: Password Decryption Error

**Symptom:**
```
cryptography.fernet.InvalidToken: Invalid token
```

**Likely Causes:**
1. Encryption key changed
2. Database copied from different installation
3. `.encryption_key` file deleted or corrupted

**Solutions:**

**Solution 1: Regenerate Encryption Key**
**WARNING:** This will invalidate all stored passwords.
```cmd
del .encryption_key
```
Restart dashboard. It will create new key. You'll need to re-enter all email passwords.

**Solution 2: Restore Encryption Key**
If you have backup of `.encryption_key`:
```cmd
copy .encryption_key.backup .encryption_key
```

**Prevention:**
- Backup `.encryption_key` file
- Don't copy database between installations without encryption key
- Don't edit `.encryption_key` file manually

---

## Template Issues

### Issue: Template Changes Not Saving

**Symptom:**
Edit template, click Save, but changes don't persist.

**Solutions:**

**Solution 1: Check for Errors**
Look for error messages on page after clicking Save.

**Solution 2: Verify Database Connection**
Check that `campaign_control.db` is not locked by another process.

**Solution 3: Refresh Page**
After saving, refresh page (F5) to verify changes saved.

**Solution 4: Check Template Name**
Template name must be unique within vertical. Duplicate names may cause issues.

**Prevention:**
- Wait for "Template saved successfully" message before navigating away
- Use unique template names
- Refresh page to verify changes

---

### Issue: Template Variables Not Rendering

**Symptom:**
Live preview shows `{first_name}` instead of actual name.

**Solutions:**

**Solution 1: Use Correct Variable Names**
Available variables:
- `{first_name}` (lowercase)
- `{last_name}`
- `{company}`
- `{state}`
- `{title}`
- `{email}`
- `{greeting}`

Variable names are case-sensitive.

**Solution 2: Check Sample Data**
Live preview uses sample data. If sample data is empty, variables won't render.

**Prevention:**
- Always use lowercase variable names
- Test template with real prospect data

---

### Issue: Template Not Showing in List

**Symptom:**
Created template but it doesn't appear in template list.

**Solutions:**

**Solution 1: Check Active Status**
Template may be inactive:
1. In template list, check "Active" toggle
2. Toggle to active

**Solution 2: Check Vertical Selection**
Ensure you're viewing the correct vertical's templates.

**Solution 3: Refresh Page**
Press F5 to refresh.

**Prevention:**
- Always set templates as "Active" when creating
- Verify vertical selection

---

## Metrics and Data Issues

### Issue: Metrics Showing Zero Despite Sent Emails

**Symptom:**
Dashboard shows "0 emails sent" but you know emails were sent.

**Likely Causes:**
1. `sent_tracker.csv` not found
2. `sent_tracker.csv` empty
3. BASE_DIR configuration incorrect
4. CSV format incorrect

**Solutions:**

**Solution 1: Verify sent_tracker.csv Exists**
```cmd
dir "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\sent_tracker.csv"
```

**Solution 2: Check CSV Format**
Open `sent_tracker.csv` and verify format:
```csv
vertical_id,prospect_email,email_type,sent_datetime,email_account
debarment,john@example.com,initial,2025-11-04 10:00:00,sender@gmail.com
```

**Solution 3: Check BASE_DIR**
```cmd
notepad utils\windows_paths.py
```
Verify `SENT_TRACKER` path is correct.

**Solution 4: Force Refresh**
In dashboard, press `R` to rerun, or `Ctrl + F5` for hard refresh.

**Prevention:**
- Verify BASE_DIR configuration
- Check CSV format matches expected schema
- Refresh dashboard after email scripts run

---

### Issue: Prospect Count Mismatch

**Symptom:**
Dashboard shows different prospect count than actual CSV rows.

**Solutions:**

**Solution 1: Check for Duplicates**
Dashboard deduplicates by email. Two rows with same email count as one.

**Solution 2: Check Status Filters**
Prospect viewer may have filters applied:
1. Clear all filters
2. Refresh count

**Solution 3: Recount Manually**
```cmd
python -c "import pandas as pd; df = pd.read_csv('verticals/<vertical_id>/prospects.csv'); print(len(df))"
```

**Prevention:**
- Understand deduplication logic
- Clear filters before checking counts

---

### Issue: Charts Not Rendering

**Symptom:**
Charts show blank or "No data available".

**Likely Causes:**
1. No data in time range
2. JavaScript disabled in browser
3. Plotly not installed
4. Browser compatibility issue

**Solutions:**

**Solution 1: Check Date Range**
Expand date range or filter to "All time".

**Solution 2: Verify Data Exists**
Check that sent_tracker.csv has data in expected date range.

**Solution 3: Reinstall Plotly**
```cmd
pip install plotly --upgrade
```

**Solution 4: Try Different Browser**
Test in Chrome, Firefox, or Edge.

**Solution 5: Clear Browser Cache**
Press `Ctrl + Shift + Delete` and clear cache.

**Prevention:**
- Use modern browser (Chrome, Firefox, Edge)
- Ensure JavaScript enabled
- Keep Plotly updated

---

## Integration Issues

### Issue: Scripts Can't Find Templates

**Symptom:**
Email scripts report "Template not found" error.

**Likely Causes:**
1. Templates stored in database only (v1.0 behavior)
2. Scripts looking in wrong location
3. Template file not exported

**Solutions:**

**Solution 1: Export Templates to Files**
In v1.0, templates are database-only. For script integration:
1. Go to Templates Manager
2. Copy template text
3. Manually create template file in `verticals/<vertical_id>/templates/`
4. Save as `initial_template_1.txt` or similar

**Solution 2: Update Scripts to Read Database**
Modify your email scripts to read templates from dashboard database instead of text files.

**Solution 3: Wait for v1.1**
Automatic template export coming in v1.1.

**Prevention:**
- Document template changes
- Manually sync templates until v1.1

---

### Issue: Coordination Not Working

**Symptom:**
Pausing campaigns in dashboard doesn't stop scripts.

**Likely Causes:**
1. Scripts not reading `coordination.json`
2. `coordination.json` not in expected location
3. Scripts running on old config

**Solutions:**

**Solution 1: Verify coordination.json Location**
```cmd
dir "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\coordination.json"
```

**Solution 2: Check coordination.json Content**
```cmd
notepad coordination.json
```
Should show:
```json
{
  "status": "paused",
  ...
}
```

**Solution 3: Update Scripts**
Ensure your email scripts read coordination.json before sending:
```python
import json
with open('coordination.json') as f:
    coord = json.load(f)
if coord['status'] == 'paused':
    print("Campaigns paused. Exiting.")
    exit()
```

**Prevention:**
- Verify scripts check coordination status
- Test pause/resume functionality
- Check coordination.json after each dashboard change

---

### Issue: Sent Tracker Not Updating in Dashboard

**Symptom:**
Run email scripts, but dashboard metrics don't update.

**Solutions:**

**Solution 1: Refresh Dashboard**
Press `F5` or click "Rerun" button.

**Solution 2: Check sent_tracker.csv Timestamp**
```cmd
dir sent_tracker.csv
```
Verify "Modified" timestamp updated recently.

**Solution 3: Verify CSV Format**
Open `sent_tracker.csv` and check format is correct.

**Solution 4: Check for Errors**
Look for errors in dashboard when loading page.

**Prevention:**
- Refresh dashboard after running scripts
- Verify scripts successfully write to sent_tracker.csv
- Check error logs

---

### Issue: Dashboard and Scripts Out of Sync

**Symptom:**
Dashboard shows different data than scripts are using.

**Solutions:**

**Solution 1: Verify BASE_DIR**
Ensure dashboard and scripts using same base directory:
- Dashboard: Check `utils\windows_paths.py`
- Scripts: Check `config.py` or hardcoded paths

**Solution 2: Check File Locations**
Confirm both dashboard and scripts reading from:
- Same `sent_tracker.csv`
- Same `response_tracker.csv`
- Same prospect CSVs
- Same `coordination.json`

**Solution 3: Restart Both**
1. Close dashboard
2. Stop any running scripts
3. Restart dashboard
4. Run scripts again

**Prevention:**
- Use consistent file paths across all tools
- Document file locations
- Test integration after any path changes

---

## Performance Issues

### Issue: Slow Page Loads

**Symptom:**
Dashboard pages take 5+ seconds to load.

**Likely Causes:**
1. Large CSV files (10,000+ rows)
2. Too many database records
3. Inefficient queries
4. No caching enabled

**Solutions:**

**Solution 1: Enable Caching**
Already enabled by default in v1.0. To force cache clear: Press `C` in dashboard.

**Solution 2: Limit Data Display**
Use pagination or filters to limit displayed rows.

**Solution 3: Archive Old Data**
Move old sent_tracker.csv entries to archive:
1. Create `sent_tracker_archive.csv`
2. Move entries older than 90 days
3. Keep only recent data in `sent_tracker.csv`

**Solution 4: Optimize Database**
```cmd
sqlite3 campaign_control.db "VACUUM;"
```

**Prevention:**
- Archive old data regularly
- Use filters and pagination
- Limit CSV file sizes

---

### Issue: High Memory Usage

**Symptom:**
Dashboard uses 500MB+ RAM or system slows down.

**Solutions:**

**Solution 1: Restart Dashboard**
Close and restart dashboard to clear memory.

**Solution 2: Reduce Data Load**
Close unused browser tabs showing dashboard.

**Solution 3: Check for Memory Leaks**
If memory grows continuously, report as bug.

**Prevention:**
- Restart dashboard daily
- Close when not in use
- Archive old data

---

### Issue: Database Locked for Long Periods

**Symptom:**
"Database is locked" errors persist for minutes.

**Solutions:**

**Solution 1: Enable WAL Mode**
```cmd
sqlite3 campaign_control.db "PRAGMA journal_mode=WAL;"
```
This allows concurrent reads during writes.

**Solution 2: Reduce Concurrent Access**
Don't run multiple dashboard instances or database browsers simultaneously.

**Prevention:**
- Use WAL mode (recommended)
- Limit concurrent database access

---

## Common Error Messages

### Error: "Cannot import name 'models' from 'database'"

**Meaning:** Database module initialization failed.

**Solution:**
```cmd
cd database
python schema.py
cd ..
```

---

### Error: "Expecting value: line 1 column 1 (char 0)"

**Meaning:** JSON file empty or corrupted (usually coordination.json).

**Solution:**
Delete and recreate:
```cmd
echo {"status": "active", "last_updated": ""} > coordination.json
```

---

### Error: "UnicodeDecodeError: 'charmap' codec can't decode byte"

**Meaning:** CSV file not UTF-8 encoded.

**Solution:**
1. Open CSV in Notepad
2. Save As → Select "UTF-8" encoding
3. Re-upload

---

### Error: "KeyError: 'email'"

**Meaning:** CSV missing required 'email' column.

**Solution:**
Add 'email' column to CSV with valid email addresses.

---

### Error: "IntegrityError: UNIQUE constraint failed"

**Meaning:** Attempting to add duplicate record (usually email account with duplicate email address).

**Solution:**
1. Check existing email accounts
2. Delete duplicate before adding
3. Or edit existing account instead

---

### Error: "PermissionError: [WinError 32] The process cannot access the file"

**Meaning:** File is open in another program.

**Solution:**
1. Close Excel, Notepad, or other programs with file open
2. Try operation again

---

## FAQ

### Q1: How do I create a shortcut to start the dashboard?

**A:** Create a batch file:

1. Open Notepad
2. Paste this:
   ```batch
   @echo off
   cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Outreach Dashboard"
   call venv\Scripts\activate
   streamlit run dashboard.py
   pause
   ```
3. Save as `start_dashboard.bat` in dashboard folder
4. Double-click `start_dashboard.bat` to start dashboard

---

### Q2: Can I run the dashboard on a different port?

**A:** Yes:
```cmd
streamlit run dashboard.py --server.port 8502
```
Access at: `http://localhost:8502`

---

### Q3: How do I backup my dashboard data?

**A:** Backup these files:
```cmd
copy campaign_control.db campaign_control.db.backup
copy .encryption_key .encryption_key.backup
xcopy /E /I verticals verticals_backup
```

To restore:
```cmd
copy campaign_control.db.backup campaign_control.db
copy .encryption_key.backup .encryption_key
```

---

### Q4: Can I access the dashboard from another computer?

**A:** Yes, if on same network:

1. Start dashboard with:
   ```cmd
   streamlit run dashboard.py --server.address 0.0.0.0
   ```

2. Find your IP address:
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address"

3. On other computer, navigate to:
   ```
   http://<your-ip-address>:8501
   ```

**WARNING:** This allows anyone on your network to access the dashboard.

---

### Q5: How do I reset a forgotten email account password?

**A:** You can't retrieve it (encrypted), but you can reset:

1. Go to Email Accounts page
2. Click "Edit" on account
3. Enter new password
4. Click "Test Connection" to verify
5. Click "Save"

---

### Q6: Can I export all my data?

**A:** Yes:

**Option 1: Manual Export**
- Copy `campaign_control.db`
- Copy `verticals\` folder
- Copy `.encryption_key`

**Option 2: From Dashboard (v1.1+)**
- Go to Settings page
- Click "Export All Data"
- Downloads ZIP file

---

### Q7: How often should I backup my data?

**A:** Recommended schedule:
- **Daily:** Before major changes (adding 100+ prospects, etc.)
- **Weekly:** Routine backup
- **Before updates:** Always backup before updating dashboard

---

### Q8: Can I use the dashboard on Mac or Linux?

**A:** Partially. The dashboard is designed for Windows, but can run on Mac/Linux with modifications:

1. Path separators (change `\` to `/`)
2. Virtual environment activation (`source venv/bin/activate`)
3. File path configurations

**Not officially supported in v1.0.**

---

### Q9: What's the maximum number of prospects I can manage?

**A:** Tested with:
- 10,000 prospects per vertical (good performance)
- 50 verticals total (good performance)
- 100,000+ total prospects (acceptable performance)

For larger datasets, consider pagination and archiving old data.

---

### Q10: Can multiple people use the dashboard simultaneously?

**A:** No. v1.0 is single-user. Multi-user support planned for v1.1.

**Workaround:** Deploy separate dashboard instance per user.

---

### Q11: How do I update to a new dashboard version?

**A:** (When updates available)

1. Backup data (see Q3)
2. Backup dashboard folder
3. Download new version
4. Copy `campaign_control.db` and `.encryption_key` to new version
5. Run migrations if required:
   ```cmd
   python database\migrations.py
   ```
6. Test thoroughly before production use

---

### Q12: The dashboard is frozen. What should I do?

**A:**

1. Wait 30 seconds (may be processing large dataset)
2. If still frozen, press `Ctrl + C` in Command Prompt
3. Restart dashboard
4. If problem persists, check error logs

---

### Q13: How do I clear the cache?

**A:** Two methods:

**Method 1: From Dashboard**
- Press `C` key while viewing dashboard
- Click "Clear cache" button

**Method 2: From Command Line**
```cmd
streamlit cache clear
```

---

### Q14: Can I customize the dashboard appearance?

**A:** Limited customization available:

Edit `.streamlit\config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

Restart dashboard after changes.

---

### Q15: Where are error logs stored?

**A:** Multiple locations:

1. **Dashboard errors:** Displayed on page
2. **Email script errors:** `error_log.csv` in outreach sequences folder
3. **System errors:** Command Prompt window output

---

## Still Having Issues?

If your issue isn't covered here:

1. **Check other documentation:**
   - `SETUP_INSTRUCTIONS.md` - Installation steps
   - `README.md` - Architecture overview
   - `TEST_REPORT.md` - Known issues

2. **Review error logs:**
   - Command Prompt output
   - `error_log.csv`
   - Dashboard error messages

3. **Test with minimal data:**
   - Create fresh database
   - Add one test account
   - Add one test vertical
   - Upload small test CSV (10 rows)
   - Isolate the problem

4. **Check file integrity:**
   - Verify all required files present
   - Check file permissions
   - Look for corrupt files

5. **Contact support:**
   - Provide error message text
   - Describe steps to reproduce
   - Include Python version, Windows version
   - Attach relevant error logs

---

## Quick Diagnostic Checklist

Run through this checklist to diagnose issues:

- [ ] Python 3.9+ installed: `python --version`
- [ ] Virtual environment activated: `(venv)` in prompt
- [ ] Dependencies installed: `pip list | findstr streamlit`
- [ ] In correct directory: `dir dashboard.py`
- [ ] Database exists: `dir campaign_control.db`
- [ ] BASE_DIR correct: `notepad utils\windows_paths.py`
- [ ] Encryption key exists: `dir .encryption_key`
- [ ] sent_tracker.csv exists: Check in BASE_DIR
- [ ] No other dashboard instances running
- [ ] Port 8501 available
- [ ] Firewall allows Python/Streamlit
- [ ] Sufficient disk space
- [ ] Sufficient memory (2GB+ free)

**All checked?** Dashboard should work. If not, review error messages carefully.

---

**Document Version:** 1.0  
**Last Updated:** November 4, 2025  
**Compatible With:** Campaign Control Center v1.0

**For additional help, consult SETUP_INSTRUCTIONS.md or contact your system administrator.**

---

**END OF TROUBLESHOOTING GUIDE**
