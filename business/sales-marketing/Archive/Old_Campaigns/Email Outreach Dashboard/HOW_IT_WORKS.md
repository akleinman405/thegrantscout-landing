# How Dashboard & Email Scripts Work Together

**Critical Question:** What actually controls the email sending?

**Answer:** The **email scripts** read from **CSV files**, not the dashboard directly!

---

## The Relationship (Simple Version)

```
Dashboard             CSV Files              Email Scripts
   ↓                     ↓                        ↓
Manages data    ←→   Shared storage    →    Reads data
(UI for you)         (single source         (does the work)
                      of truth)
```

### In Plain English:
1. **Dashboard** = Your control panel (you edit things here)
2. **CSV Files** = The actual data files (shared between both)
3. **Email Scripts** = The workers (read CSVs and send emails)

**Key Point:** Dashboard changes CSVs → Scripts read updated CSVs → Scripts send emails

---

## What the Dashboard Actually Changes

### 1. ✅ Prospect Lists (CSV Files)

**Dashboard Action:** Upload prospects via Prospects Manager
**What Happens:**
```
You drag-and-drop CSV
     ↓
Dashboard writes to: debarment_prospects.csv
     ↓
Email script reads: debarment_prospects.csv
     ↓
Script sends to those prospects
```

**Files Written:**
```
/outreach_sequences/debarment_prospects.csv
/outreach_sequences/food_recall_prospects.csv
/outreach_sequences/[vertical]_prospects.csv
```

**Result:** ✅ Scripts use YOUR uploaded prospects

---

### 2. ✅ Email Templates (Template Files)

**Dashboard Action:** Edit template + **Click "Sync to Files"**
**What Happens:**
```
You edit template in dashboard
     ↓
Template saved to database
     ↓
You click "Sync All Templates to Files" ⭐ REQUIRED!
     ↓
Dashboard writes to: templates/debarment/initial_template.txt
     ↓
Email script reads: templates/debarment/initial_template.txt
     ↓
Script uses your template
```

**Files Written:**
```
/outreach_sequences/templates/[vertical]/initial_template.txt
/outreach_sequences/templates/[vertical]/followup_template.txt
```

**Result:** ✅ Scripts use YOUR templates (ONLY if you sync!)

---

### 3. ⚠️ Email Accounts (Database Only)

**Dashboard Action:** Add email account
**What Happens:**
```
You add account in dashboard
     ↓
Saved to: campaign_control.db (database)
     ↓
Scripts DON'T read this! ❌
     ↓
Scripts have their own email config
```

**Result:** ⚠️ Scripts DON'T automatically use dashboard accounts

**Why:** Scripts were built separately with hardcoded email config

**Workaround:** Manually update script config to match dashboard accounts

---

### 4. ⚠️ Verticals (Database Only)

**Dashboard Action:** Create vertical
**What Happens:**
```
You create vertical in dashboard
     ↓
Saved to: campaign_control.db (database)
     ↓
Scripts DON'T read this! ❌
     ↓
Scripts look for CSV files by name
```

**Result:** ⚠️ Scripts don't need dashboard verticals

**Why:** Scripts find prospects by CSV filename (e.g., `debarment_prospects.csv`)

**Important:** Vertical ID in dashboard should match CSV filename

---

## Data Flow Diagram

### Prospect Upload Flow:
```
┌────────────────────────────────────────────────────────────┐
│                     Dashboard (UI)                         │
│  - You upload debarment_prospects.csv                     │
│  - Dashboard validates: email, first_name, etc.           │
└────────────────────────────────────────────────────────────┘
                            ↓ writes
┌────────────────────────────────────────────────────────────┐
│                  CSV Files (Disk Storage)                  │
│  /outreach_sequences/debarment_prospects.csv              │
│  Columns: email, first_name, company_name, state, etc.   │
└────────────────────────────────────────────────────────────┘
                            ↑ reads
┌────────────────────────────────────────────────────────────┐
│              Email Script (send_initial_outreach.py)       │
│  - Reads debarment_prospects.csv                          │
│  - Filters: initial_sent_date == null                     │
│  - Sends emails                                            │
│  - Updates: initial_sent_date = today                     │
│  - Writes back to CSV                                      │
└────────────────────────────────────────────────────────────┘
                            ↓ updates
┌────────────────────────────────────────────────────────────┐
│                     CSV Updated                            │
│  Now has: initial_sent_date filled for sent prospects     │
└────────────────────────────────────────────────────────────┘
                            ↑ reads
┌────────────────────────────────────────────────────────────┐
│                  Dashboard Refreshes                       │
│  - Shows updated prospect status                          │
│  - Displays metrics                                        │
└────────────────────────────────────────────────────────────┘
```

### Template Sync Flow:
```
┌────────────────────────────────────────────────────────────┐
│              Dashboard (Templates Manager)                 │
│  - You edit initial outreach template                     │
│  - Saved to database immediately                          │
└────────────────────────────────────────────────────────────┘
                            ↓ stores
┌────────────────────────────────────────────────────────────┐
│                Database (campaign_control.db)              │
│  templates table: template_id, vertical_id, subject, body │
└────────────────────────────────────────────────────────────┘
                            ↓
             ⚠️ SCRIPTS CAN'T SEE THIS YET! ⚠️
                            ↓
┌────────────────────────────────────────────────────────────┐
│    You click "📥 Sync All Templates to Files" button      │
└────────────────────────────────────────────────────────────┘
                            ↓ writes
┌────────────────────────────────────────────────────────────┐
│              Template Files (Disk Storage)                 │
│  /outreach_sequences/templates/debarment/initial.txt      │
└────────────────────────────────────────────────────────────┘
                            ↑ reads
┌────────────────────────────────────────────────────────────┐
│              Email Script (send_initial_outreach.py)       │
│  - Reads templates/debarment/initial.txt                  │
│  - Uses it to format emails                               │
└────────────────────────────────────────────────────────────┘
```

---

## What Dashboard Changes Affect Scripts?

### ✅ DOES Affect Scripts:

1. **Prospect Uploads**
   - Dashboard writes CSV → Script reads CSV
   - Immediate effect

2. **Templates (After Sync)**
   - Dashboard writes template files → Script reads template files
   - Effect after clicking "Sync to Files"

3. **Tracking Data (Indirect)**
   - Scripts write to sent_tracker.csv
   - Dashboard reads and displays metrics
   - Two-way relationship

### ❌ DOES NOT Affect Scripts:

1. **Email Accounts**
   - Dashboard stores in database
   - Scripts have separate config
   - Must manually match

2. **Verticals (Metadata)**
   - Dashboard stores vertical info (display name, industry)
   - Scripts only care about CSV filenames
   - Just use matching names

3. **Settings**
   - Dashboard settings are UI-only
   - Scripts have their own settings
   - Not connected (yet)

4. **Campaign Control Buttons**
   - Start/Stop buttons in dashboard are for display
   - Don't actually control scripts
   - Scripts run independently

---

## The Truth About Control

### Who Controls What:

| Feature | Controlled By | Notes |
|---------|--------------|-------|
| **Which prospects to email** | CSV files | Both dashboard and scripts read/write |
| **Email templates** | Template files | Dashboard writes (after sync), scripts read |
| **When to send** | Email scripts | Scripts decide timing and pacing |
| **Email account used** | Email scripts | Scripts have hardcoded config |
| **Daily limits** | Email scripts | Scripts enforce their own limits |
| **Business hours** | Email scripts | Scripts check time before sending |

### Dashboard's Role:
- 📋 **Data Management** - Upload prospects, manage CSVs
- 📝 **Template Editor** - Easy template editing with preview
- 📊 **Monitoring** - View metrics, track sends
- 🧪 **Testing** - Send test emails, verify templates
- 📁 **Organization** - Centralized view of all data

### Email Scripts' Role:
- 📧 **Actual Sending** - Connect to SMTP, send emails
- ⏰ **Timing** - Respect business hours, pacing
- 📝 **Tracking** - Write to sent_tracker.csv
- 🔄 **Coordination** - Handle initial/followup split
- 🛡️ **Safety** - Rate limiting, error handling

---

## Recommended Workflow

### For Maximum Integration:

1. **Use Dashboard For:**
   - Uploading new prospects
   - Editing email templates
   - Viewing metrics and analytics
   - Sending test emails
   - Monitoring campaign progress

2. **Use Email Scripts For:**
   - Actual campaign execution
   - Running in background/terminal
   - Sending production emails
   - Handling timing and pacing

3. **Sync Process:**
   ```
   Edit in Dashboard → Sync to Files → Scripts Use Updated Data
   ```

### Golden Rules:

1. **After editing templates:** Always click "Sync to Files"
2. **After uploading prospects:** Scripts will automatically see them
3. **Check dashboard metrics:** But remember scripts do the sending
4. **Test emails:** Use dashboard's Test Email feature first
5. **Production sends:** Use scripts, not dashboard

---

## Future Improvements (Not Yet Implemented)

### Could Be Added:

1. **Email Account Sync**
   - Scripts read accounts from dashboard database
   - No more hardcoded credentials
   - Centralized management

2. **True Campaign Control**
   - Dashboard actually starts/stops scripts
   - Real-time control from UI
   - Process management

3. **Automatic Template Sync**
   - Templates sync to files on save
   - No manual button click needed
   - Seamless integration

4. **Settings Sync**
   - Scripts read settings from dashboard
   - Single source of configuration
   - No duplicate settings

---

## Current Limitations

### 1. No Direct Script Control
**Problem:** Dashboard can't start/stop email scripts
**Workaround:** Run scripts manually in terminal
**Solution:** See `OUTSTANDING_REQUESTS_SUMMARY.md` for planned improvements

### 2. Email Accounts Not Synced
**Problem:** Scripts don't use dashboard email accounts
**Workaround:** Manually keep script config in sync with dashboard
**Solution:** Could be implemented (requires script changes)

### 3. Manual Template Sync Required
**Problem:** Must click "Sync to Files" button
**Workaround:** Remember to sync after editing
**Solution:** Could auto-sync on save (future enhancement)

---

## Testing the Integration

### Test 1: Prospect Upload
```
1. Upload CSV in dashboard (Prospects Manager)
2. Check file exists: /outreach_sequences/debarment_prospects.csv
3. Run email script
4. Verify script sends to your prospects
✅ If emails sent → Integration working
```

### Test 2: Template Changes
```
1. Edit template in dashboard (Templates Manager)
2. Click "Sync All Templates to Files"
3. Check file exists: /outreach_sequences/templates/debarment/initial.txt
4. Run email script
5. Check sent email uses new template
✅ If new template used → Integration working
```

### Test 3: Metrics Display
```
1. Run email script (sends emails)
2. Check sent_tracker.csv has new rows
3. Go to dashboard
4. View Dashboard page
5. Check metrics updated
✅ If metrics show new sends → Integration working
```

---

## Quick Reference: File Locations

### Shared Files (Both Read/Write):
```
/outreach_sequences/
├── debarment_prospects.csv          # Prospects
├── food_recall_prospects.csv        # Prospects
├── sent_tracker.csv                 # Tracking data
├── response_tracker.csv             # Response data
└── coordination.json                # Campaign coordination
```

### Template Files (Dashboard Writes, Scripts Read):
```
/outreach_sequences/templates/
├── debarment/
│   ├── initial_template.txt
│   └── followup_template.txt
└── food_recall/
    ├── initial_template.txt
    └── followup_template.txt
```

### Dashboard-Only Files (Scripts Don't Read):
```
/Email Outreach Dashboard/
└── campaign_control.db              # Email accounts, verticals metadata
```

---

## Summary: What You Need to Know

### The Big Picture:
1. **Dashboard = Your UI** for managing data
2. **CSV/Template Files = Shared storage** both use
3. **Email Scripts = The workers** that actually send

### What Dashboard Controls:
- ✅ Prospect lists (writes CSV files)
- ✅ Email templates (writes template files after sync)
- ✅ Metrics display (reads tracking files)
- ✅ Test emails (sends directly via SMTP)

### What Dashboard Doesn't Control (Yet):
- ❌ Email script execution (manual start/stop)
- ❌ Email account selection in scripts (hardcoded)
- ❌ Campaign timing (scripts decide)
- ❌ Script settings (separate configuration)

### Key Action Items:
1. **Always sync templates** after editing ("Sync to Files" button)
2. **Upload prospects** through dashboard (easiest way)
3. **Run email scripts** manually in terminal (for actual sending)
4. **Monitor progress** in dashboard (metrics, live feed)
5. **Test first** using dashboard's Test Email feature

---

**Bottom Line:** Dashboard prepares the data, Scripts do the work!

---

**Created By:** Claude Code
**Date:** November 4, 2025
**Version:** 1.0
