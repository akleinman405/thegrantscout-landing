# Manual Testing Checklist
**Campaign Control Center Dashboard**

Use this checklist to verify all functionality before deployment.

---

## Pre-Testing Setup

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify BASE_DIR path in `utils/windows_paths.py`
- [ ] Back up existing database if present
- [ ] Launch dashboard: `streamlit run dashboard.py`
- [ ] Verify dashboard opens in browser (default: http://localhost:8501)

---

## Page 1: Home / Welcome Page

### Initial Load
- [ ] Page loads without errors
- [ ] Welcome message displays
- [ ] Quick Start section shows setup progress
- [ ] System Status shows 0 active accounts, 0 active verticals (first run)
- [ ] Getting Started guide expands/collapses
- [ ] Debug info checkbox shows paths (optional)

### After Setup
- [ ] Quick Start shows ✅ for configured items
- [ ] System Status updates with real counts
- [ ] Metrics display correctly

**Notes:** _________________________________

---

## Page 2: Dashboard (Metrics)

### Metrics Display
- [ ] Total emails sent displays (0 on first run)
- [ ] Emails sent today displays
- [ ] Emails sent this week displays
- [ ] Emails sent this month displays
- [ ] Response rate displays (% format)

### Vertical Filter
- [ ] "All Verticals" dropdown appears
- [ ] Selecting vertical filters metrics correctly
- [ ] Charts update when filter changes

### Charts
- [ ] Line chart: Emails Over Time renders
- [ ] Bar chart: Emails by Vertical renders
- [ ] Donut chart: Response Rates renders
- [ ] Charts are interactive (hover shows values)

### Account Status Table
- [ ] Table shows all email accounts
- [ ] Progress bars show quota usage
- [ ] Active/Inactive status displays correctly
- [ ] Assigned verticals show as badges

### Campaign Status
- [ ] Shows data from coordination.json (if exists)
- [ ] Displays "No coordination data" if file missing
- [ ] Status shows running/idle correctly

**Notes:** _________________________________

---

## Page 3: Prospects Manager

### Upload Section
- [ ] Vertical zones display for each active vertical
- [ ] File uploader accepts .csv files
- [ ] Upload button appears after file selected

### CSV Validation
- [ ] **Test: Upload valid CSV** → Success message appears
- [ ] **Test: Upload CSV with missing columns** → Error message shown
- [ ] **Test: Upload CSV with invalid emails** → Error messages shown
- [ ] **Test: Upload duplicate prospects** → Deduplication message shown

### Prospect Viewer
- [ ] Vertical dropdown lists all verticals
- [ ] Selecting vertical loads prospects table
- [ ] Table displays: email, first_name, company_name, state, website
- [ ] Empty vertical shows "No prospects" message

### Filters
- [ ] Search box filters by email/company
- [ ] Status filter (not contacted/initial sent/followup sent/responded) works
- [ ] Filters combine correctly

### Actions
- [ ] Export button downloads CSV
- [ ] Delete selected button prompts confirmation
- [ ] Statistics show correct counts (total, contacted, etc.)

**Notes:** _________________________________

---

## Page 4: Email Accounts

### Account List
- [ ] Table displays all accounts
- [ ] Shows: email, display name, SMTP host, port, daily limit, status
- [ ] Assigned verticals display as badges

### Add Account
- [ ] "Add Account" button opens form
- [ ] Form has all required fields
- [ ] **Test: Submit with empty fields** → Validation errors shown
- [ ] **Test: Submit with invalid port** → Error shown
- [ ] **Test: Submit with valid data** → Success, account appears in list

### Edit Account
- [ ] Edit button pre-fills form with account data
- [ ] Password field shows "[encrypted]" placeholder
- [ ] Updating works, changes saved
- [ ] Updated timestamp changes

### Delete Account
- [ ] Delete button shows confirmation dialog
- [ ] Confirming deletes account
- [ ] Canceling preserves account
- [ ] Cascade delete removes assignments

### Test SMTP Connection
- [ ] "Test Connection" button appears
- [ ] **Test: Click with valid credentials** → Success message
- [ ] **Test: Click with invalid credentials** → Error message with details

### Account-Vertical Assignment
- [ ] Assignment matrix displays (accounts × verticals)
- [ ] Checkboxes toggle assignments
- [ ] Changes save immediately
- [ ] Visual feedback on save

### Capacity Summary
- [ ] Total daily capacity calculates correctly
- [ ] Sent today shows correct count
- [ ] Remaining capacity = Total - Sent
- [ ] Capacity by vertical shows breakdown

**Notes:** _________________________________

---

## Page 5: Verticals Manager

### Vertical List
- [ ] Table displays all verticals
- [ ] Shows: ID, display name, industry, prospect count, status
- [ ] Active/inactive toggle works
- [ ] Stats display correctly (prospect count, template count)

### Add Vertical
- [ ] "Add Vertical" button opens form
- [ ] Form has: vertical_id, display_name, target_industry, active toggle
- [ ] **Test: Submit with invalid ID (spaces/special chars)** → Error
- [ ] **Test: Submit with duplicate ID** → Error
- [ ] **Test: Submit valid data** → Success, vertical created

### Edit Vertical
- [ ] Edit button pre-fills form
- [ ] Vertical ID field is disabled (cannot change primary key)
- [ ] Other fields editable
- [ ] Changes save correctly

### Delete Vertical
- [ ] Delete button shows confirmation
- [ ] Warning mentions cascade delete (templates, assignments)
- [ ] **Test: Delete vertical** → Removed from list
- [ ] **Test: Check templates deleted** → Templates gone (cascade)

### Vertical Details
- [ ] Click "View Details" opens expanded view
- [ ] Shows prospect count, templates, assigned accounts
- [ ] CSV filename displays
- [ ] Created/updated timestamps shown

**Notes:** _________________________________

---

## Page 6: Templates Manager

### Vertical Selector
- [ ] Tabs or dropdown shows all verticals
- [ ] Selecting vertical loads its templates
- [ ] Template count badge shows on each tab

### Template List
- [ ] Shows all templates for selected vertical
- [ ] Displays: type (initial/followup), name, subject preview
- [ ] Active/inactive status toggle works
- [ ] Last modified date shown

### Add Template
- [ ] "Add Template" button opens editor
- [ ] Form has: type dropdown, name, subject, body
- [ ] Type dropdown has "Initial" and "Followup" only

### Template Editor
- [ ] Large text area for email body
- [ ] Subject line input field
- [ ] Available variables list displayed ({first_name}, {company_name}, etc.)
- [ ] Character count shown (optional)

### Live Preview
- [ ] Preview pane shows below editor
- [ ] Uses sample data (e.g., "John", "Acme Corp")
- [ ] Variables replaced with sample values
- [ ] Updates as you type (or on button click)

### Save Template
- [ ] Save button saves changes
- [ ] Success message appears
- [ ] Template appears in list
- [ ] Updated timestamp changes

### Duplicate Template
- [ ] **Test: Create duplicate name** → Error shown
- [ ] Duplicate button creates copy with "(Copy)" suffix

### Delete Template
- [ ] Delete button shows confirmation
- [ ] **Test: Delete template** → Removed from list

### Test Send (Optional Feature)
- [ ] "Send Test" button appears
- [ ] Prompts for test email address
- [ ] Sends test email (if configured)

**Notes:** _________________________________

---

## Page 7: Campaign Planner

### Today's Plan
- [ ] Displays plan from coordination.json
- [ ] Table shows: vertical, type, allocated, sent, remaining, status
- [ ] If coordination.json missing → "No plan available" message
- [ ] Status colors: green=running, yellow=idle, red=error

### Weekly Forecast
- [ ] Shows next 7 days
- [ ] Calculates based on:
  - Available prospects
  - Daily limits per account
  - Business hours
- [ ] Skips weekends (Saturday/Sunday)
- [ ] Shows breakdown by vertical and type

### Manual Controls (Future Feature)
- [ ] Pause Campaign button (if implemented)
- [ ] Resume Campaign button (if implemented)
- [ ] Adjust Daily Limits (if implemented)
- [ ] Skip Today button (if implemented)

### Capacity Calculator
- [ ] Input field for number of prospects
- [ ] "Calculate" button computes days required
- [ ] Shows breakdown by vertical and account
- [ ] Accounts for daily limits and business hours

**Notes:** _________________________________

---

## Page 8: Settings

### Global Campaign Settings
- [ ] Business hours start (dropdown or number input)
- [ ] Business hours end (dropdown or number input)
- [ ] Timezone (dropdown with common timezones)
- [ ] Conservative pacing toggle (on/off)
- [ ] Hourly rate display (calculated, read-only)

### Anti-Spam Settings
- [ ] Base delay min (minutes)
- [ ] Base delay max (minutes)
- [ ] Break frequency (emails between breaks)
- [ ] Break duration (seconds)

### File Paths (Display Only)
- [ ] Base directory shown
- [ ] Database path shown
- [ ] Sent tracker path shown
- [ ] Response tracker path shown
- [ ] Error log path shown

### Data Management
- [ ] "Export All Data" button (if implemented)
- [ ] "Import Data" button (if implemented)
- [ ] "Reset Daily Counters" button (if implemented)
- [ ] "Clear Test Data" button (if implemented)

### System Info
- [ ] Dashboard version displayed
- [ ] Database file size shown
- [ ] Total prospects count shown
- [ ] Total sent emails count shown
- [ ] Python version shown (optional)
- [ ] Streamlit version shown (optional)

### Save Settings
- [ ] "Save Settings" button at bottom
- [ ] Changes persist after save
- [ ] Success message appears
- [ ] **Test: Reload page** → Settings retained

**Notes:** _________________________________

---

## Integration Testing

### Dashboard → Email Scripts
- [ ] **Test: Upload 10 prospects** via dashboard
- [ ] Verify CSV file created/updated in correct location
- [ ] **Test: Run email script** (e.g., send_initial_outreach.py)
- [ ] Verify script can read new prospects
- [ ] Verify script sends emails successfully

### Email Scripts → Dashboard
- [ ] **Test: Run email script** to send 5 emails
- [ ] Wait for script to complete
- [ ] **Refresh dashboard** (Page 2: Dashboard)
- [ ] Verify "Sent Today" metric increased by 5
- [ ] Verify sent_tracker.csv has new entries
- [ ] Verify charts updated

### Template Sync
- [ ] **Test: Update template** in dashboard
- [ ] Save changes
- [ ] **Test: Email script** uses new template (if script reads from DB)
- [ ] Verify email sent contains new template content

### Coordination Sync
- [ ] **Test: Run email script** (should update coordination.json)
- [ ] Navigate to Page 6: Campaign Planner
- [ ] Verify status shows "running" or "idle"
- [ ] Verify allocated/sent counts match coordination.json
- [ ] Stop script
- [ ] **Refresh planner** → Status updates

**Notes:** _________________________________

---

## Error Handling Testing

### Invalid Inputs
- [ ] **Test: Enter invalid email** → Validation error shown
- [ ] **Test: Upload malformed CSV** → Clear error message
- [ ] **Test: Create vertical with existing ID** → Duplicate error
- [ ] **Test: Delete non-existent record** → Graceful handling

### Missing Files
- [ ] **Test: Delete sent_tracker.csv** → Dashboard shows 0 metrics (no crash)
- [ ] **Test: Delete coordination.json** → Planner shows "No data" (no crash)
- [ ] **Test: Delete prospects CSV** → Prospects page shows empty (no crash)

### Database Errors
- [ ] **Test: Corrupt database** (delete key table) → Error message shown
- [ ] **Test: Database locked** (if possible) → Retry or error message

### Network Errors (SMTP)
- [ ] **Test: Invalid SMTP credentials** → Connection test fails gracefully
- [ ] **Test: SMTP server unreachable** → Timeout with error message

**Notes:** _________________________________

---

## Performance Testing

### Large Datasets
- [ ] **Test: Upload CSV with 1000 rows** → Upload completes in <5s
- [ ] **Test: Load prospects table with 1000 rows** → Renders in <3s
- [ ] **Test: Query 50 verticals** → Page loads in <2s
- [ ] **Test: Generate charts with 1000+ data points** → Renders in <3s

### Responsiveness
- [ ] Dashboard remains responsive during CSV upload
- [ ] No freezing during database operations
- [ ] Charts render smoothly without lag
- [ ] Search/filter operations feel instant (<500ms)

### Memory Usage
- [ ] Dashboard starts with ~50MB memory
- [ ] Loading large datasets doesn't exceed 200MB
- [ ] No memory leaks over 30 minutes of use

**Notes:** _________________________________

---

## Security Testing (Manual Verification)

### Input Sanitization
- [ ] **Test: Enter `<script>alert('XSS')</script>` in display name** → Stored but not executed
- [ ] **Test: Enter SQL injection string** → Query fails gracefully, no data exposed
- [ ] **Test: Upload file with path traversal name** (`../../etc/passwd.csv`) → Sanitized

### Password Security
- [ ] Passwords never displayed in UI (show masked or "[encrypted]")
- [ ] No passwords in browser console (check DevTools)
- [ ] No passwords in page source (View Source)
- [ ] Encryption key file (`.encryption_key`) has restricted permissions

### File Upload Security
- [ ] **Test: Upload .exe file** → Rejected
- [ ] **Test: Upload huge file (>50MB)** → Rejected
- [ ] **Test: Upload non-CSV file** → Rejected or warned

**Notes:** _________________________________

---

## Browser Compatibility (Optional)

### Chrome
- [ ] All pages load correctly
- [ ] Charts render correctly
- [ ] Forms work correctly

### Firefox
- [ ] All pages load correctly
- [ ] Charts render correctly
- [ ] Forms work correctly

### Edge
- [ ] All pages load correctly
- [ ] Charts render correctly
- [ ] Forms work correctly

**Notes:** _________________________________

---

## Final Checks

- [ ] All critical functionality working
- [ ] No unhandled errors in console
- [ ] No broken links or buttons
- [ ] All forms validate correctly
- [ ] All data persists correctly
- [ ] Performance acceptable (<3s page loads)
- [ ] Integration with email scripts verified
- [ ] Documentation matches actual behavior

---

## Sign-Off

**Tested By:** ____________________  
**Date:** ____________________  
**Environment:** ☐ Development  ☐ Staging  ☐ Production  
**Status:** ☐ Pass ☐ Fail (see notes)  

**Issues Found:** ____________________

**Approved for Deployment:** ☐ Yes ☐ No  

**Signature:** ____________________

---

## Notes / Issues Discovered

```
[Record any issues, bugs, or unexpected behavior here]









```

---

**Checklist Version:** 1.0  
**Last Updated:** November 4, 2025

