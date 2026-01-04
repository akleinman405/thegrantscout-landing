# PROMPT: Email Campaign System Audit

**Date:** 2025-12-15  
**For:** Claude Code CLI  
**Location:** `C:\TheGrantScout\4. Sales & Marketing\Email Campaign\`

---

## Standards

Follow CLAUDE.md conventions for file naming, output format, and lessons learned section.

---

## Situation

Email campaign system was built for beta outreach in November 2025. Now need to:
1. Understand current state (what was sent, what bounced, who's available)
2. Clean up redundant files
3. Identify BusinessFactory references to rebrand to TheGrantScout
4. Prep follow-up campaign to offer "founding member" pricing

**Key files to examine:**
- `grant_alerts_prospects.csv` (537 KB) - master prospect list
- `sent_tracker.csv` (258 KB) - who was emailed
- `response_tracker.csv` (106 KB) - responses/status
- `error_log.csv` - bounces/failures
- `campaign_control.db` - campaign state
- `Email Campaign 2025-11-3/` subfolder - scripts and docs

---

## Tasks

### 1. Data State Assessment

```
- Total prospects in grant_alerts_prospects.csv
- Total sent (from sent_tracker.csv)
- Bounces/failures (from error_log.csv)
- Responses/unsubscribes (from response_tracker.csv)
- Available for follow-up = sent - bounced - unsubscribed
```

### 2. Script Inventory

For each .py file in `Email Campaign 2025-11-3/`:
- **Purpose:** What does it do?
- **Status:** Active / Legacy / Test file?
- **Dependencies:** What does it import/require?
- **BusinessFactory refs:** Any strings to update?

Key scripts to examine:
- `send_initial_outreach.py`
- `send_followup.py`
- `campaign_tracker.py`
- `coordination.py`
- `export_bounces.py`
- `config.py` vs `config OLD.py`

### 3. Documentation Inventory

For each .md file:
- **Current/Outdated?**
- **Keep/Archive/Delete?**

Files to check:
- USER_GUIDE.md
- README.md
- QUICK_START.md
- TRACKER_SETUP.md
- IMPLEMENTATION_SUMMARY_2025-11-12.md
- FIX_REPORT_2025-11-11.md
- DUPLICATE_FIX_REPORT.md
- Others...

### 4. Branding Audit

Search all files for:
- "BusinessFactory"
- "businessfactory"
- "business factory"
- Old email addresses/domains
- Any non-TheGrantScout branding

### 5. Follow-Up Target List

Generate list of valid follow-up targets:
```
Criteria:
- Was sent initial email
- Did NOT bounce
- Did NOT unsubscribe
- Did NOT already respond/convert

Output: Count + ready for export
```

### 6. Folder Cleanup Recommendations

Propose clean structure:
```
Email Campaign/
├── scripts/           # Active .py files
├── config/            # Config files
├── data/              # CSVs and trackers
├── docs/              # Current documentation only
├── archive/           # Old/unused files
└── campaigns/         # Campaign-specific folders
```

### 7. File Renaming Recommendations

For files worth keeping, propose new names following CLAUDE.md naming convention:
```
DOCTYPE_YYYY-MM-DD_description.ext
```

Example renames:
- `IMPLEMENTATION_SUMMARY_2025-11-12.md` → keep as-is (already compliant)
- `USER_GUIDE.md` → `GUIDE_2025-11-03_email_campaign_usage.md`
- `QUICK_START.md` → `GUIDE_2025-11-03_email_campaign_quickstart.md`

Provide a rename table for all documentation files worth keeping.

---

## Output

**File:** `REPORT_2025-12-15_email_campaign_audit.md`

### Sections Required:

**1. Executive Summary**
- Total prospects / sent / bounced / available for follow-up
- System health (working? issues?)

**2. Data State**
- Table with counts
- Any data quality issues (duplicates, missing fields, etc.)

**3. Script Assessment**

| Script | Purpose | Status | Action |
|--------|---------|--------|--------|
| send_initial_outreach.py | ... | Active | Keep |
| ... | ... | ... | ... |

**4. Documentation Assessment**

| Doc | Status | Action |
|-----|--------|--------|
| USER_GUIDE.md | Current | Keep |
| FIX_REPORT_2025-11-11.md | Outdated | Archive |
| ... | ... | ... |

**5. Branding Changes Needed**
- List of files with BusinessFactory references
- Specific strings to find/replace

**6. Follow-Up Campaign Readiness**
- Count of valid targets
- Any blockers?
- Recommended next steps

**7. Best Practices Assessment**

| Area | Status | Issues | Recommendations |
|------|--------|--------|-----------------|
| Credentials security | 🟢/🟡/🔴 | ... | ... |
| Duplicate prevention | 🟢/🟡/🔴 | ... | ... |
| Error handling | 🟢/🟡/🔴 | ... | ... |
| Resume capability | 🟢/🟡/🔴 | ... | ... |
| Logging | 🟢/🟡/🔴 | ... | ... |
| Hardcoded paths | 🟢/🟡/🔴 | ... | ... |

**8. File Renaming Recommendations**

| Current Name | Proposed Name | Rationale |
|--------------|---------------|-----------|
| USER_GUIDE.md | GUIDE_YYYY-MM-DD_... | ... |
| ... | ... | ... |

**9. Cleanup Recommendations**
- Files to delete
- Files to archive
- Proposed folder structure

**10. Lessons Learned**
- What's working well in the system
- What's overly complicated
- Simplification opportunities

---

## Software Best Practices Review

### Security/Config
- Are credentials hardcoded or in environment variables/separate config file?
- Is `.gitignore` present and protecting sensitive files (credentials/, *.csv, config.py)?
- Any API keys, passwords, or tokens visible in scripts?
- Are email credentials stored securely?

### Reliability
- **Error handling:** Do scripts fail gracefully or crash on errors?
- **Duplicate prevention:** What stops sending to same person twice?
- **Dry-run mode:** Can you test without actually sending emails?
- **Rate limiting:** Any throttling to avoid spam flags or API limits?
- **Validation:** Does it check email format before sending?

### Maintainability
- Is there a `requirements.txt` or dependency list?
- Hardcoded paths (e.g., `C:\Users\Alec\...`) vs. relative paths?
- Logging - can you debug issues after the fact? Where do logs go?
- Code comments - are complex sections explained?
- Config vs. code separation - can you change settings without editing scripts?

### Recovery
- Can scripts resume if interrupted mid-batch?
- Is there a backup strategy for trackers before modifying?
- What happens if script crashes halfway through a send?
- Can you rollback or identify where it stopped?

---

## Questions to Answer

1. How many people can I email for the follow-up campaign?
2. Is send_followup.py ready to use, or does it need updates?
3. What's the minimum I need to do to send a follow-up this week?
4. What can I safely delete without breaking anything?
5. Are there any security concerns to fix before using again?
6. What's the risk of accidentally double-emailing someone?

---

## Notes

- Don't modify any files yet - audit only
- Focus on actionable recommendations
- If scripts have hardcoded paths, note them
- Check if credentials/ folder has sensitive data that shouldn't be in reports
