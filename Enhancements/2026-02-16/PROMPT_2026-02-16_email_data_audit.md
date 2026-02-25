# PROMPT: Email Campaign Data Audit & Migration

**Date:** 2026-02-16
**For:** Claude Code CLI
**Schema:** f990_2025

---

## Situation

A schema audit (REPORT_2026-02-16_schema_audit.md) was already completed. It:
- Added `app_contact_email` to fp2 and backfilled 10,092 emails from pf_returns (Step 1 done)
- Expanded org_url_enrichment with contact columns (Step 2 done)
- Created web_* tables (Step 3 done)
- **Deferred Steps 4-6:** Migrating old campaign data, updating views, dropping redundant tables

The old campaign data is in TWO places:
1. **Database:** `grantscout_campaign.foundation_prospects` (761 rows, 148 emails) and `grantscout_campaign.nonprofit_prospects` (74K rows, 63 emails)
2. **Local CSV files:** `C:\TheGrantScout\4. Sales & Marketing\Email Campaign\` — grant_alerts_prospects.csv, sent_tracker.csv, response_tracker.csv, error_log.csv, campaign_control.db

We need to finish Step 4: consolidate all email addresses and campaign history into the v2 tables (fp2/np2).

## Tasks

### 1. Audit Local Campaign Files
- How many total prospects in grant_alerts_prospects.csv? What columns (EIN, email, org name, org type)?
- How many emails sent (sent_tracker.csv)?
- How many bounced (error_log.csv)?
- How many responded / unsubscribed (response_tracker.csv)?
- Do the CSV emails overlap with grantscout_campaign DB tables, or are they different records?

### 2. Reconcile All Email Sources
Compare these sources and produce a deduplicated count:
- fp2.app_contact_email (10,092 — already imported)
- grantscout_campaign.foundation_prospects.contact_email (148)
- grantscout_campaign.nonprofit_prospects.contact_email (63)
- Local CSV files (grant_alerts_prospects.csv)
- Grant_Alerts_Questionnaire_16.csv (check for email column)
- Any other CSV/Excel files in Sales & Marketing folder with emails

How many UNIQUE email addresses exist across all sources? How many are NOT yet in fp2 or np2?

### 3. Execute Migration (Step 4 from Schema Audit)
Per the schema audit migration plan:
1. Migrate 148 foundation contact_emails from grantscout_campaign → fp2.app_contact_email (skip duplicates already in the 10,092)
2. Add contact_email column to np2 if not exists, migrate 63 nonprofit emails
3. Import any NEW emails from local CSV files not already in the DB
4. Create `campaign_prospect_status` table for campaign tracking history (sent_at, replied, bounced, etc.)
5. Migrate campaign tracking data from old tables + CSV files into campaign_prospect_status
6. Preserve campaign history — do NOT lose who was already emailed, bounced, or responded

### 4. Verify & Report
- Final count: how many foundations now have emails in fp2?
- Final count: how many nonprofits now have emails in np2?
- Campaign history preserved? (sent count, bounce count, response count)
- Any orphan emails (not matching an EIN in fp2 or np2)?

## Output

`REPORT_2026-02-16_email_migration.md` with:
- Before/after email counts per table
- Deduplication results
- Campaign history summary (total sent, bounced, responded — preserved in new table)
- Any data quality issues found
- Confirmation that Steps 4-6 from schema audit are complete
