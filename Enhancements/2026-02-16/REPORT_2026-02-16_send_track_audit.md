# Phase 5 (Send) & Phase 6 (Track) — Script Audit

**Date:** 2026-02-16
**Prompt:** PROMPT_2026-02-16_send_track_audit.md
**Status:** Complete
**Owner:** Aleck Kleinman

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial audit |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Script-by-Script Audit](#1-script-by-script-audit)
3. [CSV vs PostgreSQL Reality Map](#2-csv-vs-postgresql-reality-map)
4. [Data Flow Diagram](#3-data-flow-diagram)
5. [Configuration Audit](#4-configuration-audit)
6. [Integration Points](#5-integration-points)
7. [Runtime Risk Assessment](#6-runtime-risk-assessment)
8. [Idempotency Check](#7-idempotency-check)
9. [Logging Audit](#8-logging-audit)
10. [Import & Environment Validation](#9-import--environment-validation)
11. [Concurrency & Locking](#10-concurrency--locking)
12. [What's Missing](#11-whats-missing)
13. [Files Created/Modified](#files-createdmodified)
14. [Notes](#notes)

---

## Executive Summary

The Phase 5/6 scripts have been **partially migrated** from CSV to PostgreSQL. The suspicion in the prompt was correct: the Feb 9, 2026 migration rewired the core scripts but left significant gaps.

**Key findings:**

- **13 active Python scripts** totaling 4,939 lines in `Email Campaign 2025-11-3/`
- **5 archived scripts** totaling 4,068 lines in `OLD/`
- **The new system (campaign_manager.py, send_generated_emails.py) is fully PostgreSQL-backed.** Zero CSV reads or writes at runtime.
- **The old system (OLD/) was entirely CSV-based.** Zero PostgreSQL usage.
- **1,844 emails were sent via the OLD system** (Nov 2025). The new system has sent zero.
- **PostgreSQL tables exist but are all empty** (0 rows in send_log, responses, generated_emails, sender_daily_stats). The CSV files contain the only real send history (2,690 sent records, 1,841 response records).
- **export_bounces.py is broken** -- imports a removed config variable (`SENT_TRACKER`), will crash on startup.
- **shutdown_hooks.py is broken** -- imports `coordination` module that doesn't exist in the directory.
- **No process lock exists** -- running two instances simultaneously will produce duplicate sends.
- **SMTP-before-DB write order** creates a narrow window for duplicate sends on crash.
- **No suppression list, no response classification, no follow-up automation, no open/click tracking** -- all spec features still missing.

| Metric | Value |
|--------|-------|
| Active scripts | 13 (4,939 lines) |
| Archived scripts | 5 (4,068 lines) |
| PostgreSQL tables used | 7 (all empty) |
| CSV files with data | 4 (11K+ rows total) |
| Broken scripts | 2 (export_bounces.py, shutdown_hooks.py) |
| Critical risks | 3 |
| High risks | 4 |
| Medium risks | 6 |

---

## 1. Script-by-Script Audit

### Active Scripts (Email Campaign 2025-11-3/)

#### campaign_manager.py (1,143 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Long-running daemon with 4 subcommands: `send` (infinite loop: business hours check, sender rotation, SMTP send, DB log), `check` (Gmail API bounce/reply detection), `status` (aggregate stats), `senders` (pool utilization) |
| **Reads from** | PostgreSQL: nonprofit_prospects, foundation_prospects, send_log, senders, sender_daily_stats. Gmail API (bounces/replies). Config module. |
| **Writes to** | PostgreSQL: send_log (INSERT/upsert), contact_events (INSERT), nonprofit/foundation_prospects (UPDATE status), sender_daily_stats (upsert), responses (INSERT). SMTP outbound email. credentials/token.json (OAuth refresh). |
| **PostgreSQL** | psycopg2 + RealDictCursor. Schema: grantscout_campaign. No connection pooling -- fresh connection per operation. `log_send_and_update_prospect()` wraps send_log INSERT + prospect UPDATE in single transaction. |
| **CSV** | None. Deprecated CSV path defined in config but never accessed. |
| **External APIs** | SMTP: smtp.gmail.com:587 via smtplib, Google App Password auth, send-as aliases. Gmail API: OAuth2 read-only, bounce/reply search. |
| **Key logic** | Subdomain spread rotation via SenderPool. Business hours (Mon-Fri 9am-7pm ET). 3-layer dedup (prospect status filter, application-level email set, DB unique constraint). Rolling 24h limit (400/day). 50/50 initial/followup capacity split. 5-failure circuit breaker (30min pause). A/B test infrastructure exists in config but this script hardcodes Variant D only. |
| **Error handling** | Per-email SMTP failures caught and logged. 5-consecutive circuit breaker. DB failures caught and printed to stdout. Gmail auth failures handled gracefully. SIGINT handler runs shutdown hooks then exits. No file-based logging. |
| **Dependencies** | psycopg2, pytz (required). google-auth, google-auth-oauthlib, google-api-python-client (optional for Gmail). Local: config, sender_pool, db_helpers. |

#### send_generated_emails.py (608 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Sends pre-generated emails from `generated_emails` table (status='pending'). Atomic claim mechanism. Not a daemon -- runs once, sends all pending, exits. |
| **Reads from** | PostgreSQL: generated_emails, nonprofit/foundation_prospects (contact_email join), senders, sender_daily_stats. |
| **Writes to** | PostgreSQL: generated_emails (status updates), nonprofit/foundation_prospects (campaign_status), send_log (INSERT), sender_daily_stats (upsert). Daily log file. |
| **PostgreSQL** | psycopg2. Same connection-per-operation pattern. Atomic claim: `UPDATE SET status='sending' WHERE status='pending'` with rowcount check. |
| **CSV** | None at runtime. |
| **External APIs** | SMTP only (smtp.gmail.com:587). No Gmail API. |
| **Key logic** | Atomic claim prevents concurrent duplicate sends. Exponential delay distribution for duration-based pacing. 5-failure circuit breaker. Crash recovery: resets stuck 'sending' emails to 'pending' on startup. Business hours NOT enforced (operator responsibility). |
| **Error handling** | Failed emails reset to 'pending' (retryable). Crash between SMTP and DB write orphans email in 'sending' status until next run's recovery. Log file write errors not caught (would crash send loop). |
| **Dependencies** | psycopg2. Local: config, db_helpers, sender_pool, campaign_logger. |

#### generate_emails.py (625 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Generates personalized emails from prospect data + A/B test variant templates. Inserts into generated_emails table with status='pending'. |
| **Reads from** | PostgreSQL: nonprofit/foundation_prospects, generated_emails (existence check), ab_test_results (view). |
| **Writes to** | PostgreSQL: generated_emails (INSERT). |
| **PostgreSQL** | psycopg2. NOT EXISTS subquery prevents regenerating for prospects with existing pending/sent email. New connection per insert (1000 emails = 1000 connections). |
| **Key logic** | Uses config.assign_variant() for weighted random A/B assignment. Variant C restricted to new_to_foundations segment. str.format_map with defaultdict prevents KeyError on missing template vars. |
| **Dependencies** | psycopg2. Local: config, db_helpers. |

#### config.py (339 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Central configuration: SMTP credentials, sending limits, A/B test variants, email templates, file paths. |
| **Key constants** | TEST_MODE=False, TOTAL_DAILY_LIMIT=400, BUSINESS_HOURS 9-19 ET, BASE_DELAY 5-10s, BREAK every 10-20 emails. 4 variants (A/B/C/D) x 2 types (initial/followup) = 8 email templates. |
| **Issues** | Empty string defaults for all credentials (silent auth failure). Windows BASE_DIR hardcoded (stale). Deprecated CSV path still in VERTICALS dict. Personal phone/Calendly hardcoded in all 8 templates. assign_variant() is non-deterministic and stateless. |

#### sender_pool.py (260 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Manages sender aliases with subdomain spread rotation and daily cap tracking. |
| **PostgreSQL** | Reads senders + sender_daily_stats. Writes sender_daily_stats (upsert). |
| **Key logic** | Round-robin through subdomains, pick lowest-usage sender within each. In-memory sent_today counter + DB-level atomic upsert. |
| **Issues** | No locking mechanism. Dead import of config. record_send() silently swallows DB errors. refresh_senders() only called at init (stale data in long runs). |

#### db_helpers.py (195 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Shared DB utility: connection factory, dual-table prospect lookups, flag updates, first-name extraction. |
| **PostgreSQL** | psycopg2. Connection string from DATABASE_URL or POSTGRES_PASSWORD env var. Schema: grantscout_campaign. |
| **Key logic** | find_prospect_by_email() searches nonprofit first then foundation. update_prospect_flag() handles 'NOW()' as inline SQL. |

#### campaign_logger.py (174 lines)

| Field | Details |
|-------|---------|
| **Purpose** | File-based logging: pipe-delimited daily log files. |
| **Writes to** | `logs/campaign_YYYY-MM-DD.log` (append mode). |
| **Issues** | No try/except on file writes (crash propagates). No log rotation. |

#### campaign_status.py (659 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Read-only CLI for campaign stats. 6 subcommands: today, log, sent, pending, search, responses. |
| **Reads from** | PostgreSQL: send_log, senders, generated_emails, nonprofit/foundation_prospects. Log files. |
| **Writes to** | Nothing (stdout only). |

#### track_response.py (346 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Manual CLI for recording replies, bounces, unsubscribes. Also supports bulk CSV import and status summary. |
| **Reads from** | PostgreSQL: nonprofit/foundation_prospects. Optional user-supplied CSV for bulk import. |
| **Writes to** | PostgreSQL: nonprofit/foundation_prospects (UPDATE replied/bounced/unsubscribed flags + campaign_status). |
| **Issues** | hard_bounce flag is cosmetic only (no DB distinction). notes and error_message params accepted but never stored. Double-lookup per row in bulk import. |

#### assign_variants.py (178 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Assigns A/B test variant letters to nonprofit prospects based on segment weights. |
| **Writes to** | PostgreSQL: nonprofit_prospects (UPDATE ab_test_variant). |
| **Key logic** | Batch UPDATE via execute_values (500-row batches). Only operates on nonprofit_prospects, never foundation. |

#### export_bounces.py (99 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Reads sent_tracker.csv, filters bounced rows, writes bounce_list.csv. |
| **Status** | **BROKEN.** Imports `SENT_TRACKER` from config.py which no longer defines it. Will crash with ImportError on startup. |
| **Data** | Pure CSV-to-CSV. Zero PostgreSQL. Legacy script. |

#### send_test_email.py (109 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Sends test emails to verify SMTP config. Supports single sender, next-in-rotation, or all senders. |
| **Writes to** | SMTP only. Does NOT record to DB (no send_log, no stats). |
| **Issues** | Accesses pool._senders (private attribute) directly. |

#### shutdown_hooks.py (204 lines)

| Field | Details |
|-------|---------|
| **Purpose** | Automatic cleanup on script exit: mark coordination state, CRM sync, Gmail bounce check. |
| **Status** | **BROKEN.** Imports `coordination` at module level (line 26) but coordination.py doesn't exist in the directory. Will crash with ModuleNotFoundError. Also references crm_integration and campaign_tracker (lazy imports, handled by try/except). |
| **Data** | References CSV trackers (sent_tracker.csv, response_tracker.csv) via legacy campaign_tracker module. |

### Archived Scripts (OLD/)

| Script | Lines | Data Store | Status |
|--------|-------|-----------|--------|
| send_initial_outreach.py | 1,109 | CSV only | Archived. Business hours 9am-3pm. Coordination.json state. |
| send_followup.py | 949 | CSV only | Archived. Followup 3+ days after initial. |
| campaign_tracker.py | 976 | CSV + Gmail API | Archived. Gmail OAuth2 bounce/reply detection. |
| coordination_v1.py | 759 | CSV + JSON | Archived. Rolling 24h capacity, vertical breakdowns. |
| coordination.py.backup | 275 | JSON only | Archived. Original minimal coordination. |

### Additional Data Stores

| Store | Type | Status |
|-------|------|--------|
| campaign_control.db | SQLite | 5 tables (verticals, email_accounts, account_verticals, email_templates, campaign_settings). Legacy from original multi-vertical system. Not referenced by any active script. |
| coordination.json | JSON file | Last updated 2026-01-04. All zeros. Stale. |
| credentials/ | OAuth2 | credentials.json (client secrets) + token.json (access token). Used by campaign_manager.py Gmail integration. |

---

## 2. CSV vs PostgreSQL Reality Map

| Data | Spec says | Code actually uses | Gap? |
|------|-----------|-------------------|------|
| **Sent emails log** | grantscout_campaign.send_log | campaign_manager.py: PostgreSQL. export_bounces.py: sent_tracker.csv (broken). | Partial. New system uses DB. Old data only in CSV (2,690 rows). **CSV data was never migrated to DB.** |
| **Response tracking** | grantscout_campaign.responses | campaign_manager.py: PostgreSQL. shutdown_hooks.py: response_tracker.csv (broken). | Partial. New system uses DB. Old data only in CSV (1,841 rows). **CSV data was never migrated to DB.** |
| **Bounce tracking** | grantscout_campaign.responses + prospect.bounced flag | campaign_manager.py: PostgreSQL. export_bounces.py: bounce_list.csv (broken). | Partial. New system uses DB. Old bounce data only in CSV. |
| **Error log** | Not specified | error_log.csv (10 rows, parent dir). Not referenced by any active script. | Orphaned. |
| **Sender pool** | grantscout_campaign.senders | sender_pool.py: PostgreSQL (10 rows). | Fully migrated. |
| **Daily stats** | grantscout_campaign.sender_daily_stats | sender_pool.py: PostgreSQL. | Fully migrated (but empty -- no sends yet). |
| **Generated emails queue** | grantscout_campaign.generated_emails | generate_emails.py and send_generated_emails.py: PostgreSQL. | Fully migrated (but empty). |
| **Suppression list** | grantscout_campaign.suppression_list (per spec) | **Does not exist.** No table, no code. | Missing entirely. |
| **Prospect data** | grantscout_campaign.nonprofit_prospects + foundation_prospects | All active scripts: PostgreSQL. | Fully migrated (74,175 nonprofit + 761 foundation rows). |
| **Coordination state** | Replaced by sender_daily_stats | coordination.json exists but is stale. campaign_manager.py ignores it. | Fully migrated. |

**Bottom line:** The core send/track path is PostgreSQL-backed. But the old campaign's 1,844 sends and responses exist only in CSV files that no active script reads. Historical data was not migrated.

---

## 3. Data Flow Diagram

```
WHAT TRIGGERS A SEND?

  Path A: campaign_manager.py send (daemon mode)
  ================================================

  1. Operator runs: python campaign_manager.py send
  2. Check business hours (Mon-Fri 9am-7pm ET)
       |-- Outside hours? Sleep 15 min, retry
  3. Check rolling 24h capacity (send_log COUNT WHERE sent_at > NOW()-24h)
       |-- At limit (400)? Sleep 15 min, retry
  4. SenderPool.get_next_sender() checks sender_daily_stats
       |-- All senders at daily cap? Sleep 15 min, retry
  5. Query nonprofit_prospects WHERE campaign_status='not_contacted'
     + UNION foundation_prospects (for followups)
  6. Filter out emails already in send_log (dedup set)
  7. For each prospect:
       a. Format email from config.VERTICALS['grant_alerts'] template
       b. SMTP send via smtplib (smtp.gmail.com:587, TLS, App Password)
       c. On success: INSERT send_log + UPDATE prospect status (single txn)
       d. SenderPool.record_send() updates sender_daily_stats
       e. Sleep (evenly-paced delay with +/-10% jitter)
  8. After batch: sleep 15 min, goto step 2
  9. On Ctrl+C: run shutdown hooks (Gmail bounce/reply check)


  Path B: send_generated_emails.py (batch mode)
  ================================================

  1. Operator runs: python send_generated_emails.py send
  2. Recover stuck emails (reset 'sending' -> 'pending')
  3. Query generated_emails WHERE status='pending'
     JOIN prospect tables for contact_email
  4. For each pending email:
       a. Atomic claim: UPDATE status='sending' WHERE status='pending'
       b. SenderPool.get_next_sender()
       c. SMTP send
       d. On success: UPDATE generated_emails status='sent'
          + UPDATE prospect campaign_status + INSERT send_log
       e. On failure: reset to 'pending' for retry
  5. Exit when queue empty or 5 consecutive failures


  HOW DOES TRACKING FIND THE RESPONSE?
  =====================================

  Path A (automated): campaign_manager.py check
    1. Authenticate Gmail API (OAuth2)
    2. Search for bounces (5 query patterns: mailer-daemon, postmaster, etc.)
    3. Parse bounce messages for recipient email
    4. Match email against sent_log recipients
    5. UPDATE prospect: bounced=TRUE, campaign_status='bounced'
    6. INSERT into responses table + contact_events

  Path B (manual): track_response.py
    1. Operator runs: python track_response.py bounce "user@org.com"
    2. Lookup in nonprofit_prospects then foundation_prospects
    3. UPDATE prospect: bounced/replied/unsubscribed flags


  FEEDBACK LOOP (HOW DOES IT FEED BACK TO NEXT SEND?)
  =====================================================

  - Bounced prospects: campaign_status='bounced' -> excluded from send queries
  - Replied prospects: campaign_status='replied' -> excluded from send queries
  - Unsubscribed: campaign_status='unsubscribed' -> excluded
  - NO feedback to Phase 2 (web_emails validation status not updated)
  - NO feedback to Phase 4 (A/B reply rates not fed back to template selection)
```

---

## 4. Configuration Audit

Source: `config.py` (339 lines)

### All Constants

| Constant | Value | Configurable? |
|----------|-------|---------------|
| TEST_MODE | False | Hardcoded |
| TEST_EMAIL_ADDRESSES | 4 personal emails | Hardcoded |
| OUTREACH_EMAIL / OUTREACH_NAME | Env var (empty default) | Env var |
| OUTREACH_APP_PASSWORD | Env var (empty default) | Env var |
| OUTREACH_SMTP_SERVER | Env var (default: smtp.gmail.com) | Env var |
| OUTREACH_SMTP_PORT | Env var (default: 587) | Env var |
| TGS_AUTH_EMAIL | Env var (empty default) | Env var |
| TGS_APP_PASSWORD | Env var (empty default) | Env var |
| EMAILS_PER_VERTICAL_PER_DAY | 150 | Hardcoded |
| TOTAL_DAILY_LIMIT | 400 | Hardcoded |
| BUSINESS_HOURS_START | 9 | Hardcoded |
| BUSINESS_HOURS_END | 19 | Hardcoded |
| TIMEZONE | US/Eastern | Hardcoded |
| USE_CONSERVATIVE_PACING | True | Hardcoded |
| NATURAL_HOURLY_RATE | 40.0 | Hardcoded |
| BASE_DELAY_MIN | 5 | Hardcoded |
| BASE_DELAY_MAX | 10 | Hardcoded |
| BREAK_FREQUENCY_MIN | 10 | Hardcoded |
| BREAK_FREQUENCY_MAX | 20 | Hardcoded |
| BREAK_DURATION_MIN | 30 | Hardcoded |
| BREAK_DURATION_MAX | 90 | Hardcoded |
| AB_TEST_NAME | gov_funding_feb2026 | Hardcoded |
| INPUT_CSV_GRANTS | grant_alerts_prospects.csv | Hardcoded (deprecated) |
| LOG_DIR | {script_dir}/logs/ | Hardcoded |

### Hardcoded Values That Should Be Configurable

1. **Personal phone number** `(281) 245-4596` in all 8 email templates
2. **Calendly URL** in followup templates
3. **LinkedIn URL** in variant D initial template
4. **AB_TEST_NAME** string
5. **4 test email addresses**

### Broken/Stale Paths

| Path | Status |
|------|--------|
| `C:\TheGrantScout\4. Sales & Marketing\Email Campaign` | Windows path, stale (macOS migration) |
| `INPUT_CSV_GRANTS` (grant_alerts_prospects.csv) | Deprecated per comment, but still in VERTICALS dict |
| `SENT_TRACKER` | Removed from config.py but still imported by export_bounces.py |

### Environment Variables Required

| Variable | Required by | Default |
|----------|------------|---------|
| TGS_AUTH_EMAIL | campaign_manager, send_generated_emails, send_test_email | Empty string (sends will fail) |
| TGS_APP_PASSWORD | Same scripts | Empty string (sends will fail) |
| POSTGRES_PASSWORD | All DB scripts | "postgres" |
| DATABASE_URL | All DB scripts | Built from POSTGRES_PASSWORD |

---

## 5. Integration Points

### How Phase 5/6 Connect to Phase 2 Data

| Question | Answer |
|----------|--------|
| Do they read from org_url_enrichment? | No |
| Do they read from web_best_email? | No (table doesn't exist yet) |
| Do they read from web_emails? | No (table doesn't exist yet) |
| Do they read from nonprofit_prospects? | Yes -- this is the primary prospect source |
| Do they read from foundation_prospects? | Yes -- secondary prospect source |

**The connection between Phase 2 (email scraping) and Phase 5 (sending) is through the `contact_email` column in the prospect tables.** Phase 2's Script 07 (materialize best email) has a `--backfill` flag that copies best emails into the prospect tables. Without running Phase 2, the prospect tables contain whatever email data was loaded during the original data migration.

### How Would a New Email Get Into the Send Queue?

Two paths:

1. **generate_emails.py path:** Prospect must have `campaign_status='not_contacted'` and a valid `contact_email`. Script generates a row in `generated_emails` with status='pending'. Then `send_generated_emails.py` picks it up.

2. **campaign_manager.py path:** Directly queries prospects with `campaign_status='not_contacted'` and sends immediately. No intermediate queue.

### Gap Between "Email Validated" and "Email Ready to Send"

Yes. Phase 2 validates emails (syntax + MX) and stores them in `web_emails` / `web_best_email`. But the prospect tables have their own `contact_email` column that is NOT automatically synced with web_best_email. The Script 07 `--backfill` is a manual, one-time copy. There is no trigger or scheduled job to keep them in sync.

---

## 6. Runtime Risk Assessment

### Critical Risks

| # | Risk | Severity | Safeguard? | Detail |
|---|------|----------|-----------|--------|
| C1 | **Duplicate sends on crash** | Will happen (eventually) | Partial | If SMTP succeeds but the DB write fails or process crashes between the two, the email is sent but not recorded. Next run re-selects the prospect and sends again. The window is narrow (milliseconds) but inevitable over thousands of sends. |
| C2 | **No suppression list** | Will happen (if unsubscribe received) | None | There is no suppression_list table and no mechanism to honor unsubscribe requests across campaign restarts. track_response.py can mark individual prospects as unsubscribed, but there's no global email-level suppression. |
| C3 | **export_bounces.py crashes on import** | Will happen | None | `from config import SENT_TRACKER` fails because SENT_TRACKER was removed from config.py. Script is dead code. |

### High Risks

| # | Risk | Severity | Safeguard? | Detail |
|---|------|----------|-----------|--------|
| H1 | **Concurrent instance sends duplicates** | Could happen | None | No process lock. Two `campaign_manager.py send` instances will query overlapping prospect lists, both send, both try to write (upsert overwrites). |
| H2 | **Sender overuse with concurrent instances** | Could happen | Partial | In-memory sender stats go stale across instances. DB-level upsert is atomic per row, but each instance's in-memory counter only sees its own sends. |
| H3 | **Follow-up sent to already-replied prospects** | Could happen | Partial | campaign_manager.py's followup query filters `replied IS NOT TRUE`, but there's a TOCTOU gap: a reply could arrive between the query and the send. The Gmail check only runs on shutdown, not continuously. |
| H4 | **shutdown_hooks.py crashes on import** | Will happen | None | Imports `coordination` module that doesn't exist. Any script that imports shutdown_hooks will fail. |

### Medium Risks

| # | Risk | Severity | Safeguard? | Detail |
|---|------|----------|-----------|--------|
| M1 | **Silent credential failure** | Could happen | None | Empty string defaults for TGS_AUTH_EMAIL and TGS_APP_PASSWORD. If env vars not set, SMTP login will fail with a confusing error rather than a clear "credentials not configured" message. |
| M2 | **No connection pooling** | Performance | None | Every DB operation opens/closes a fresh psycopg2 connection. send_generated_emails.py: ~3-4 connections per email. generate_emails.py: 1 connection per insert. |
| M3 | **Log file write crashes send loop** | Could happen | None | campaign_logger._write() has no try/except. Filesystem error (disk full, permissions) propagates up and kills the send loop. |
| M4 | **Same email in both prospect tables gets two emails** | Could happen | None | Dedup is by (prospect_type, prospect_id, message_type), not by recipient_email. An email appearing in both nonprofit_prospects and foundation_prospects gets separate sends. |
| M5 | **Gmail API rate limiting inadequate** | Could happen | Minimal | 100ms pause every 10 messages. No exponential backoff. Could hit Gmail API quotas on large mailboxes. |
| M6 | **No stdout persistence** | Could happen | None | campaign_manager.py logs only to stdout. If terminal session dies, all output is lost. Only DB records survive. |

---

## 7. Idempotency Check

| Script | If run twice, duplicates? | Dedup mechanism | Cron double-fire? |
|--------|--------------------------|-----------------|-------------------|
| **campaign_manager.py send** | Generally no (3-layer dedup). Yes on crash between SMTP and DB. | Prospect status filter + email set filter + DB unique constraint (upsert) | Second instance runs concurrently. No lock. Will send duplicates. |
| **send_generated_emails.py send** | Generally no (atomic claim). Yes on crash between SMTP and mark_sent. | Atomic UPDATE WHERE status='pending' (rowcount check). Crash recovery resets stuck emails. | Second instance safely skipped by atomic claim (same emails won't be double-claimed). BUT crash recovery could reset legitimately-sending emails. |
| **generate_emails.py generate** | No | NOT EXISTS subquery checks generated_emails for non-failed rows per prospect/type | Safe. Existing pending/sent emails block regeneration. |
| **assign_variants.py** | No (updates idempotently) | Default mode: WHERE ab_test_variant IS NULL. --reassign mode: overwrites all. | Safe. Last write wins. |
| **track_response.py** | Partial (timestamps change) | UPDATE by prospect id. No guard for "already replied." | Safe. Same UPDATE re-applied. |
| **export_bounces.py** | N/A (broken) | Full overwrite of output CSV | N/A |
| **campaign_manager.py check** | Yes (duplicate response records) | No dedup on responses table INSERT. Running check twice for same bounces inserts duplicate rows. | Will create duplicate response records. |

---

## 8. Logging Audit

| Aspect | campaign_manager.py | send_generated_emails.py | Other scripts |
|--------|-------------------|------------------------|---------------|
| **Where** | stdout only | Daily file (logs/campaign_YYYY-MM-DD.log) + stdout | stdout only |
| **Timestamped?** | No (Python print) | Yes (YYYY-MM-DD HH:MM:SS in log file) | No |
| **Structured?** | No (plain text) | Semi-structured (pipe-delimited) | No |
| **Log rotation?** | N/A | Daily files (one per day). No deletion/archival. | N/A |
| **Reconstruct "what happened"?** | Partially, from send_log table | Yes, from log file + send_log table | No |

**Critical gap:** campaign_manager.py (the primary send script) has no file-based logging. If the terminal dies, the only record is the PostgreSQL send_log table. The config.py defines LOG_DIR and campaign_logger.py exists, but campaign_manager.py never uses them. Only send_generated_emails.py uses the file logger.

**Existing log file:** `logs/campaign_2026-02-10.log` contains 1 line: a test message. No real send data.

---

## 9. Import & Environment Validation

### Missing/Broken Imports

| Script | Import | Status |
|--------|--------|--------|
| export_bounces.py | `from config import SENT_TRACKER` | **BROKEN.** SENT_TRACKER removed from config.py. |
| shutdown_hooks.py | `import coordination` | **BROKEN.** coordination.py doesn't exist in directory. |
| shutdown_hooks.py | `import crm_integration` (lazy) | Missing but handled by try/except ImportError. |
| shutdown_hooks.py | `import campaign_tracker` (lazy) | Missing but handled by try/except ImportError. |
| sender_pool.py | `import config` | Dead import (config never referenced in file). |
| campaign_manager.py | Gmail packages (google-auth, etc.) | Optional. GMAIL_AVAILABLE flag handles absence gracefully. |

### Windows Path Assumptions

| Location | Issue |
|----------|-------|
| config.py line 60 | `C:\TheGrantScout\4. Sales & Marketing\Email Campaign` -- Windows path, unreachable on macOS |
| shutdown_hooks.py | `os.fsync()` calls (WSL compatibility) -- unnecessary on macOS but harmless |
| TRACKER_SETUP.md | `/mnt/c/Business Factory...` WSL paths in documentation |

### Hardcoded Paths That Exist

| Path | Exists? |
|------|---------|
| config.LOG_DIR (`{script_dir}/logs/`) | Yes |
| credentials/credentials.json | Yes |
| credentials/token.json | Yes |
| BASE_DIR (parent `Email_Campaign/` dir) | Yes |

### Environment Variables

| Variable | Required? | How to verify |
|----------|-----------|---------------|
| TGS_AUTH_EMAIL | Yes (for sending) | Must be set in .env or shell |
| TGS_APP_PASSWORD | Yes (for sending) | Must be set in .env or shell |
| POSTGRES_PASSWORD | Depends | Default "postgres" works locally |
| DATABASE_URL | No | Auto-built if not set |

---

## 10. Concurrency & Locking

### Locking Mechanisms

| Mechanism | Present? |
|-----------|----------|
| File lock (flock/lockfile) | No |
| PostgreSQL advisory lock | No |
| PID file | No |
| Named semaphore | No |
| SELECT ... FOR UPDATE | No |
| Mutex/threading lock | No |

### Can Scripts Run Simultaneously?

| Combination | Safe? | Risk |
|-------------|-------|------|
| campaign_manager.py send x2 | **No** | Duplicate sends, exceeded rate limits |
| send_generated_emails.py x2 | **Mostly yes** | Atomic claim prevents duplicate sends. In-memory sender stats may drift, risking sender overuse. |
| campaign_manager.py + send_generated_emails.py | **No** | Both write to send_log and prospect tables. Shared sender pool with stale in-memory state. |
| campaign_manager.py send + check | **Yes** | check is read-Gmail + write-DB. send is read-DB + write-SMTP. No conflict. |
| Any script + campaign_status.py | **Yes** | campaign_status is read-only. |
| Any script + track_response.py | **Mostly yes** | track_response writes to prospect tables. Could race with campaign_manager on the same prospect (unlikely). |

### Coordination Beyond coordination.py

`coordination.py` no longer exists in the active directory. The current coordination mechanism is:

1. **sender_daily_stats table:** Atomic upsert tracks per-sender daily counts. Works correctly for single-instance. Drifts with multiple instances.
2. **send_log table:** Unique constraint on (prospect_type, prospect_id, message_type) with ON CONFLICT DO UPDATE. Prevents duplicate DB records but not duplicate SMTP sends.
3. **Prospect campaign_status:** Status transitions (not_contacted -> initial_sent -> followup_sent) prevent re-selection. But TOCTOU gap exists between SELECT and UPDATE.

---

## 11. What's Missing

Features the spec describes but the code doesn't implement:

| Feature | Spec Section | Code Status |
|---------|-------------|-------------|
| **Suppression list / unsubscribe** | Phase 6 DB tables | No table, no code. track_response.py can mark individual prospects but no global suppression. |
| **Response classification** (interested/not interested/wrong person) | Phase 6 Response Classification | No code. track_response.py is manual entry only. No AI or rule-based classification. |
| **Follow-up sequence automation** | Phase 6 Follow-Up Sequences | No automation. campaign_manager.py can send followups manually but no 3-4-7-14 day cadence logic. No follow_up_queue table. |
| **Open tracking** (tracking pixel) | Phase 6 Response Tracking | No code, no infrastructure. |
| **Click tracking** (redirect URLs) | Phase 6 Response Tracking | No code, no infrastructure. |
| **Feedback loop: bounces -> Phase 2** | Phase 6 Feedback Loop | No code. Bounces update prospect status but NOT web_emails.mx_valid. |
| **Feedback loop: reply rates -> Phase 4** | Phase 6 Feedback Loop | No code. ab_test_results view exists but no automated template selection. |
| **A/B variant tracking in campaign_manager.py** | Phase 4 / Phase 5 | campaign_manager.py hardcodes Variant D. A/B infrastructure only used by generate_emails.py + send_generated_emails.py path. |
| **response_classifications table** | Phase 6 DB tables | Not created. |
| **follow_up_queue table** | Phase 6 DB tables | Not created. |
| **suppression_list table** | Phase 6 DB tables | Not created. |
| **Hard vs soft bounce distinction** | Phase 6 Response Classification | track_response.py accepts --hard flag but doesn't store it. No DB column for bounce type. |
| **Automated Gmail polling** (cron) | Phase 6 | No scheduler. campaign_manager.py only checks Gmail on shutdown (Ctrl+C). |
| **Historical data migration** | Implicit | 1,844 sends in CSV never migrated to send_log. 1,841 response records never migrated to responses table. |

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| REPORT_2026-02-16_send_track_audit.md | Enhancements/2026-02-16/ | This report |

---

## Notes

### Recommendations (Priority Order)

1. **Add process lock** to campaign_manager.py (PID file or PostgreSQL advisory lock). Prevents concurrent instances.
2. **Create suppression_list table** and check it before every send. This is a CAN-SPAM compliance requirement.
3. **Fix export_bounces.py** -- either delete it (it's legacy) or rewrite to read from send_log table.
4. **Fix shutdown_hooks.py** -- remove coordination import (dead code) or delete the file entirely.
5. **Add file-based logging** to campaign_manager.py (it already imports config.LOG_DIR).
6. **Migrate historical CSV data** to PostgreSQL (2,690 sent records, 1,841 response records). This is the only record of the Nov 2025 campaign.
7. **Add connection pooling** or at minimum a shared connection object to reduce the per-email overhead.
8. **Wrap send_log + prospect UPDATE in a single transaction** that occurs BEFORE the SMTP send. Use a "pending" -> "sending" -> "sent" state machine (like send_generated_emails.py already does) to prevent duplicates.
9. **Add campaign_manager.py check to a cron schedule** rather than only running on shutdown.
10. **Remove dead code:** VERTICALS dict in config.py, coordination.json, campaign_control.db, Windows paths, unused BREAK_* constants.

### Key Architecture Decision

There are two parallel send paths that should be consolidated:

- **Path A:** campaign_manager.py queries prospects directly, formats emails from hardcoded templates, sends immediately.
- **Path B:** generate_emails.py creates pre-generated emails in DB queue, send_generated_emails.py sends from queue with atomic claiming.

Path B is architecturally superior (supports A/B testing, has atomic claim dedup, separates content generation from delivery). Path A is the "quick and dirty" path that bypasses the generation queue entirely. The spec implies Path B is the intended architecture.

---

*Generated by Claude Code on 2026-02-16*
