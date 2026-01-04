# PROMPT: Email Campaign Quick Fix

**Date:** 2025-12-16  
**For:** Claude Code CLI  
**Location:** `C:\TheGrantScout\4. Sales & Marketing\Email Campaign\Email Campaign 2025-11-3\`

---

## Situation

Email campaign system audit complete. Need to make minimum changes to send follow-up emails today. 1,718 valid targets waiting.

Reference: `REPORT_2025-12-16_email_campaign_audit.md`

---

## Tasks

### 1. Delete Security Risk
Delete `config OLD.py` — contains hardcoded Gmail app password.

### 2. Update BASE_DIR in config.py
Find the BASE_DIR line (around line 49) and update path to current location:
```python
# FROM:
BASE_DIR = r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"

# TO:
BASE_DIR = r"C:\TheGrantScout\4. Sales & Marketing\Email Campaign"
```

### 3. Update Calendly Link in Follow-up Template
In `config.py`, find `GRANT_ALERT_FOLLOWUP` template and replace `[Calendly link]` with:
```
https://calendly.com/alec_kleinman/meeting-with-alec
```

### 4. Verify Environment Variables
Check if these are set (don't output values, just confirm set/not set):
- OUTREACH_EMAIL
- OUTREACH_NAME
- OUTREACH_APP_PASSWORD

If not set, add instructions for setting them.

### 5. Run Dry-Run Test
```bash
python send_followup.py --dry-run
```
Capture output. Confirm it shows valid targets and no errors.

---

## Output

**File:** `REPORT_2025-12-16_email_quickfix.md`

Short report with:
1. ✅/❌ for each task completed
2. Dry-run output summary (how many targets, any errors)
3. Exact command to run when ready to send
4. Any blockers found

---

## Notes

- Don't send actual emails yet — dry-run only
- If env variables aren't set, provide the export commands (leave password as placeholder)
- Keep it simple — cleanup/restructure is a separate task
