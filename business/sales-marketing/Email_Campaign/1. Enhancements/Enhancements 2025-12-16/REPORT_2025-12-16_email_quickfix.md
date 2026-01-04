# REPORT: Email Campaign Quick Fix

**Date:** 2025-12-16
**Status:** Ready to Send (after setting environment variables)

---

## Task Completion

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Delete `config OLD.py` | ✅ Done | File already deleted/not present |
| 2 | Update BASE_DIR in config.py | ✅ Done | Changed to `C:\TheGrantScout\4. Sales & Marketing\Email Campaign` |
| 3 | Update Calendly link | ✅ Done | Added `https://calendly.com/alec_kleinman/meeting-with-alec` |
| 4 | Verify environment variables | ⚠️ Not Set | Need to set before sending |
| 5 | Run dry-run test | ⚠️ Partial | Simulated in WSL; actual dry-run needs Windows Python |

---

## Dry-Run Summary

### Follow-up Candidates Found

| Vertical | Count |
|----------|-------|
| grant_alerts | 1,387 |
| debarment | 229 |
| food_recall | 220 |
| **Total** | **1,836** |

**Note:** Config has `ACTIVE_VERTICALS = ["grant_alerts"]`, so only **1,387 grant_alerts** recipients will receive follow-ups.

### Sample Recipients

```
grant.dick@usfingroup.com
prince.levy@techsolllc.us
yolanda.avery@dcid63.com
douglas.nadeau@ranfpe.com
christine.tremonti@wfteng.com
john.pelosi@nexusdesignllc.com
ralph.james@rjajenterprises.com
catherine.collins@biztransform.net
a.closson@synegygroupjv.com
info@lesorelle-restaurant.com
... and 1,377 more
```

---

## Blockers

### 1. Environment Variables Not Set

**Issue:** Required credentials are not set in the environment.

**Fix:** Run these commands in PowerShell before sending:

```powershell
# Option A: Set for current session only
$env:OUTREACH_EMAIL = "alec.m.kleinman@gmail.com"
$env:OUTREACH_NAME = "Alec Kleinman"
$env:OUTREACH_APP_PASSWORD = "xxxx xxxx xxxx xxxx"  # Your Gmail app password
```

Or for permanent setup:

```powershell
# Option B: Set permanently (User environment)
[Environment]::SetEnvironmentVariable("OUTREACH_EMAIL", "alec.m.kleinman@gmail.com", "User")
[Environment]::SetEnvironmentVariable("OUTREACH_NAME", "Alec Kleinman", "User")
[Environment]::SetEnvironmentVariable("OUTREACH_APP_PASSWORD", "xxxx xxxx xxxx xxxx", "User")
# Restart PowerShell after setting
```

### 2. Run from Windows (Not WSL)

**Issue:** The scripts use `pytz` timezone library that has issues in WSL.

**Fix:** Run all scripts from Windows PowerShell, not WSL/Linux.

---

## Commands to Send Follow-ups

### Step 1: Open PowerShell

Navigate to script folder:
```powershell
cd "C:\TheGrantScout\4. Sales & Marketing\Email Campaign\Email Campaign 2025-11-3"
```

### Step 2: Set Environment Variables (if not already set)

```powershell
$env:OUTREACH_EMAIL = "alec.m.kleinman@gmail.com"
$env:OUTREACH_NAME = "Alec Kleinman"
$env:OUTREACH_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
```

### Step 3: Run Dry-Run Test

```powershell
python send_followup.py --dry-run
```

Expected output:
- Shows 1,387 grant_alerts candidates
- No actual emails sent
- Preview of what would be sent

### Step 4: Send Follow-ups

```powershell
python send_followup.py
```

The script will:
- Send during business hours (9am-3pm EST, Mon-Fri)
- Pace at ~75 emails/hour
- Log all sends to `sent_tracker.csv`
- Update `response_tracker.csv` with followup dates
- Can be safely stopped with Ctrl+C

---

## Config Changes Made

### config.py Line 49 (BASE_DIR)

```python
# BEFORE:
BASE_DIR = r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"

# AFTER:
BASE_DIR = r"C:\TheGrantScout\4. Sales & Marketing\Email Campaign"
```

### config.py Line 205 (Calendly Link)

```python
# BEFORE:
Book a call: [Calendly link]

# AFTER:
Book a call: https://calendly.com/alec_kleinman/meeting-with-alec
```

---

## Follow-up Email Preview

**Subject:** Follow-up on funding help

**Body:**
```
Hi {first_name},

A few months ago I reached out about the AI grant matching tool I built. Quick update:

We finished beta testing with 6 nonprofits and are launching in January. Based on feedback, we shifted from weekly alerts to a monthly report with 5 curated foundation matches — more focused, less noise. Each match includes funder intelligence and positioning strategy.

See a sample report: https://thegrantscout.com

Founding member pricing is $99/month (or $83/month annually).

If you're still looking for help finding foundation funding, I'd love a quick 10-minute call to see if it's a fit.

Book a call: https://calendly.com/alec_kleinman/meeting-with-alec

Best,
Alec Kleinman
(281) 245-4596
```

---

## Checklist Before Sending

- [ ] Set environment variables (OUTREACH_EMAIL, OUTREACH_NAME, OUTREACH_APP_PASSWORD)
- [ ] Run from Windows PowerShell (not WSL)
- [ ] Verify dry-run shows expected candidates
- [ ] Confirm it's business hours (9am-3pm EST, Mon-Fri)
- [ ] Have a way to monitor (keep terminal open)

---

*Generated: 2025-12-16*
