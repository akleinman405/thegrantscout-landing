# PROMPT: Phase 5 (Send) & Phase 6 (Track) — Script Audit

**Date:** 2026-02-16
**Agent:** Claude Code CLI
**Type:** Read-only audit
**Priority:** HIGH — must run before the research prompt

---

## Start in Planning Mode

Read all scripts, present findings. Do NOT modify any files.

## Context

We have a 6-phase email pipeline. Phases 5 (Send) and 6 (Track & Respond) were built in Nov 2025, partially rewired to PostgreSQL on Feb 9, 2026, but have never been audited since. The spec (`Enhancements/2026-02-16/SPEC_email_pipeline.md`) claims the migration happened, but we suspect the actual code still uses CSV files for tracking.

### Scripts to Audit

**Phase 5 (sending) — in `6. Business/3. sales-marketing/5. Email_Campaign/`:**
- `send_initial_outreach.py` (~1,090 lines)
- `send_followup.py` (~917 lines)
- `campaign_manager.py`
- `send_generated_emails.py`
- `sender_pool.py`
- `config.py`
- `coordination.py`

**Phase 6 (tracking) — same directory:**
- `campaign_tracker.py` (~977 lines)
- `export_bounces.py`
- `track_response.py` (if it exists)

**Supporting files:**
- Any `.json`, `.csv`, or state files in the same directory
- Gmail API credentials setup
- The `credentials/` subdirectory

If any of these files don't exist, note that.

## Tasks

### 1. Script-by-Script Audit

For EACH script, document:

| Field | What to capture |
|-------|----------------|
| **File** | Exact filename and path |
| **Lines** | Line count |
| **Purpose** | What it actually does (read the code, don't trust the docstring) |
| **Reads from** | Every data source — CSV files, PostgreSQL tables, JSON state files, Gmail API |
| **Writes to** | Every data destination — same categories |
| **PostgreSQL usage** | Which tables does it query? Which does it write to? Via what library (psycopg2, SQLAlchemy, etc)? |
| **CSV usage** | Which CSV files does it read/write? What data is in them? |
| **External APIs** | Gmail API, SMTP, etc — how authenticated, what scopes |
| **Key logic** | Sender rotation, business hours, dedup, rate limiting — summarize how each works |
| **Error handling** | What happens on failure? Crash? Retry? Log and continue? |
| **Dependencies** | Imports and config references |

### 2. CSV vs PostgreSQL Reality Map

Create a definitive table:

| Data | Where the spec says it lives | Where the code actually reads/writes | Gap? |
|------|------------------------------|--------------------------------------|------|

Cover: sent emails log, response tracking, bounce tracking, error log, sender pool, daily stats, suppression list, generated emails queue.

### 3. Data Flow Diagram

Map the actual flow:

```
What triggers a send? → Where does it get the email list? → How does it pick a sender? → 
How does it send? → Where does it log the send? → How does tracking find the response? → 
Where does it log the response? → How does it feed back into the next send?
```

### 4. Configuration Audit

Read `config.py` and document:
- All constants (send limits, timing, paths, credentials)
- Hardcoded values that should be configurable
- Paths that may have broken in the Windows→macOS migration or Feb 9 reorganization

### 5. Integration Points

- How do Phase 5/6 scripts connect to Phase 2 data (email addresses)?
- Do they read from `org_url_enrichment`? `web_best_email`? `nonprofit_prospects`? `foundation_prospects`?
- How would a new email discovered by the scraping pipeline get into the send queue?
- Is there a gap between "email validated" and "email ready to send"?

### 6. Runtime Risk Assessment

Evaluate operational fragility. Specifically identify any areas that could cause:
- **Duplicate sends** — if a script is run twice, does it send twice?
- **Silent failures** — errors that are swallowed without logging or alerting
- **Follow-up misfires** — follow-ups sent to people who already replied
- **Sender overuse** — exceeding daily caps due to race conditions or missing checks
- **Infinite loops** — any unbounded retry or polling logic
- **Race conditions** — if multiple scripts or instances run simultaneously, what breaks?

For each risk found, note severity (will happen / could happen / unlikely) and whether there's a safeguard in place.

### 7. Idempotency Check

For each script that sends email or modifies state:
- If run twice with the same inputs, does it produce duplicate sends?
- What dedup mechanism exists? (DB unique constraint, in-memory set, CSV lookup, none?)
- If cron or launchd fires the script twice by accident, what happens?

### 8. Logging Audit

Document the logging strategy across all scripts:
- Where are logs written? (stdout, file, database?)
- Are they timestamped?
- Structured (JSON) or plain text?
- Is there log rotation?
- Could you reconstruct "what happened" from logs if a campaign goes wrong?

### 9. Import & Environment Validation

Verify that all imports resolve in the current macOS environment:
- Note any missing modules or broken dependencies
- Check for Windows-specific path assumptions (backslashes, drive letters)
- Verify any hardcoded file paths exist on the current system
- Note any environment variables or credential files that scripts expect

### 10. Concurrency & Locking

- Does `sender_pool.py` use any locking mechanism (file lock, DB lock, advisory lock)?
- Can `send_initial_outreach.py` and `send_followup.py` run simultaneously without conflict?
- Is there any coordination mechanism beyond what `coordination.py` provides?

### 11. What's Missing

List features that the spec describes but the code doesn't implement:
- Suppression list / unsubscribe
- Response classification (interested / not interested / wrong person)
- Follow-up sequence automation
- Open/click tracking
- Feedback loop (bounces → update validation)
- A/B variant tracking
- Anything else

## Output

`REPORT_2026-02-16_send_track_audit.md` with all findings organized by the sections above.

## Notes

- Read the actual code, not just docstrings. The Feb 9 migration may have been partial.
- If `config.py` references file paths, check whether those paths exist on the current macOS system.
- The `credentials/` folder may contain OAuth tokens — note what's there but do NOT output any secrets.
- This report will be the input for a follow-up research prompt, so be thorough and precise.
