# Email Campaign Data Audit & Migration Report

**Date:** 2026-02-16
**Prompt:** PROMPT_2026-02-16_email_data_audit.md
**Status:** Complete
**Owner:** Claude Code

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial: audit, reconciliation, migration of Steps 4-6 |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Task 1: Local Campaign File Audit](#task-1-local-campaign-file-audit)
3. [Task 2: Email Source Reconciliation](#task-2-email-source-reconciliation)
4. [Task 3: Migration Execution](#task-3-migration-execution)
5. [Task 4: Verification](#task-4-verification)
6. [Files Created/Modified](#files-createdmodified)
7. [Notes](#notes)

---

## Executive Summary

Completed the deferred Steps 4-6 from the schema audit. Consolidated all email addresses and campaign history from legacy tables (grantscout_campaign) and local CSV files into the v2 tables (foundation_prospects2, nonprofits_prospects2) and a new campaign_prospect_status tracking table.

**Key outcomes:**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Foundation emails (fp2) | 10,092 (8,608 valid) | 10,185 (8,712 valid) | +93 new, +12 fixed |
| Nonprofit emails (np2) | 0 | 6,372 | +6,372 (new column) |
| Campaign history tracked | 0 (in DB) | 1,836 records | Full CSV migration |
| Foundation enrichment records | 34 | 374 | +340 research records |
| Redundant tables dropped | 0 | 2 | sales_foundation/nonprofit_prospects |

---

## Task 1: Local Campaign File Audit

### grant_alerts_prospects.csv

| Metric | Value |
|--------|-------|
| Location | `6. Business/3. sales-marketing/5. Email_Campaign/` |
| Total rows | 6,370 |
| Rows with email | 6,367 |
| Unique emails | 6,366 |
| Columns | org_name, email, first_name, website, address_state |
| Has EIN? | No |

These are **nonprofit prospects** used for the grant_alerts email campaign. No EIN column, but 99.8% matched to np2 by org_name.

### sent_tracker.csv

| Metric | Value |
|--------|-------|
| Total rows | 2,690 |
| Unique emails | 1,836 |
| Date range | 2025-11-03 to 2025-12-22 |

**By vertical:**

| Vertical | Initial | Followup | Total Sent |
|----------|---------|----------|------------|
| grant_alerts | 1,395 | 846 | 2,241 |
| debarment | 229 | 0 | 229 |
| food_recall | 220 | 0 | 220 |

**By status:**

| Status | Count |
|--------|-------|
| SUCCESS | 2,567 |
| BOUNCED | 113 |
| FAILED | 10 |

### response_tracker.csv

| Metric | Value |
|--------|-------|
| Total rows | 1,841 |
| Grant alerts tracked | 1,392 |
| Actual replies (YES) | 4 |
| Dated reply (non-standard) | 1 |
| Bounced | 113 |
| Pending | 1,723 |
| With followup date | 840 |

**Reply details:**

| Email | Status |
|-------|--------|
| anthony@reefci.com | 11/11/2025 (dated) |
| derek.durst@arborbrook.org | YES |
| kaya@livingstonfrc.org | YES |
| guestservices@skyranch.org | YES |
| office@bnotshirah.org | YES |

### error_log.csv

| Metric | Value |
|--------|-------|
| Total errors | 10 |
| All vertical | grant_alerts |
| Error type | SEND_FAILURE (DNS resolution: getaddrinfo failed) |
| Date | 2025-12-22 |

### bounce_list.csv

Empty (header only). Bounce data is tracked in sent_tracker and response_tracker instead.

### campaign_control.db

SQLite database for campaign coordination. Campaign state data (not individual records).

### Overlap Analysis

The CSV files are internally consistent:
- 1,390 of 1,391 sent_tracker grant_alerts emails are in grant_alerts_prospects.csv
- 1,387 of 1,388 response_tracker grant_alerts emails are in grant_alerts_prospects.csv
- Debarment/food_recall (444 unique emails) are separate business verticals, not in the prospect file

---

## Task 2: Email Source Reconciliation

### All Email Sources

| Source | Total Rows | With Email | Unique Emails | Notes |
|--------|-----------|------------|---------------|-------|
| fp2.app_contact_email | 143,184 | 10,092 | 8,890 | 1,484 not real emails (N/A, URLs) |
| grantscout_campaign.foundation_prospects | 761 | 148 | 147 | All 148 EINs in fp2 |
| grantscout_campaign.nonprofit_prospects | 74,175 | 63 | 60 | 5 junk (sentry, email@email) |
| grant_alerts_prospects.csv | 6,370 | 6,367 | 6,366 | No EIN column |
| org_url_enrichment.app_contact_email | 813,698 | 10,092 | 8,890 | Same as fp2 (backfilled in Step 1) |
| filtered_campaign.prospects | 20,109 | 6,730 | 4,004 | Therapist vertical, NOT TGS |
| sales_foundation_prospects | 761 | 148 | 147 | Identical to gc.foundation (redundant) |
| sales_nonprofit_prospects | 74,175 | 63 | 60 | Identical to gc.nonprofit (redundant) |

### Deduplication Results

| Source | Unique Valid Emails |
|--------|-------------------|
| fp2 (valid only, contains @) | 8,261 |
| gc.foundation_prospects | 147 |
| gc.nonprofit_prospects | 60 |
| CSV grant_alerts_prospects | 6,366 |
| **Grand total unique** | **14,813** |
| Already in fp2 | 8,261 |
| **NOT in fp2 or np2** | **6,552** |

### Foundation Email Overlap (gc vs fp2)

Of 148 gc.foundation_prospects emails:

| Category | Count | Action |
|----------|-------|--------|
| Same email already in fp2 | 10 | Skip |
| Different email (fp2 has real email) | 33 | Keep fp2 value |
| Different email (fp2 has junk: N/A, URL) | 12 | **Overwrite with gc** |
| fp2 has NO email | 93 | **Add gc email** |

### CSV-to-EIN Matching

The CSV has no EIN column. Matched by UPPER(org_name) against np2.organization_name:

| Metric | Count |
|--------|-------|
| CSV rows with email | 6,367 |
| Matched to np2 EIN | 6,355 (99.8%) |
| Unique EINs matched | 6,330 |
| Unmatched | 12 |

**12 unmatched orgs** (minor name mismatches or not in np2):

| Organization | Email | State |
|-------------|-------|-------|
| 'R KIDS INC | rkids@rkidsct.org | CT |
| HUDSON LAB SCHOOL | hello@hudsonlabschool.com | NY |
| THE NETHERWOOD ACADEMY INC | tfisher@... | NJ |
| BESSIE BOLEY FOUNDATION INC | info@boleycenters.org | FL |
| THE FLATWATER FOUNDATION | info@flatwater.org | TX |
| CAMP WESTMINISTER FOUNDATION INC | administrator@... | GA |
| HOMEAID ATLANTA INC | info@homeaidga.org | GA |
| Alaska Literacy Program | info@alaskaliteracyprogram.org | AK |
| KOREAN COMMUNITY DEVELOPMENT SERVICES CENTER | dyu@koreancenter.org | PA |
| Housing Rights Committee of | info@hrcsf.org | CA |
| Center for Traditional Music and Dance Inc | traditions@ctmd.org | NY |
| NEW MAINERS PUBLIC HEALTH | info@nmphi.org | ME |

---

## Task 3: Migration Execution

### Step 4a: Foundation Emails (gc -> fp2)

```
UPDATE 93 rows: Added new emails where fp2.app_contact_email was NULL
UPDATE 12 rows: Replaced junk values (N/A, URLs) with real emails from gc
UPDATE 105 rows: Synced same changes to org_url_enrichment
```

### Step 4b: Nonprofit Emails (gc + CSV -> np2)

```
ALTER TABLE: Added contact_email column to nonprofits_prospects2
UPDATE 46 rows: Migrated from grantscout_campaign.nonprofit_prospects (58 good, minus 12 already matched)
UPDATE 6,326 rows: Imported from grant_alerts_prospects.csv (matched by org_name)
UPDATE 6,371 rows: Synced to org_url_enrichment
```

### Step 4c: Campaign Tracking Table

Created `f990_2025.campaign_prospect_status` with:
- 23 columns covering send, bounce, reply, error, and unsubscribe tracking
- Unique constraint on (email, vertical)
- Indexes on ein, email, vertical, campaign_status

Migrated 1,836 records from CSV files (sent_tracker + response_tracker + error_log).

### Step 4d: Foundation Research Migration

Migrated 340 research/rating records from grantscout_campaign.foundation_prospects to foundation_enrichment (rating, why_rating, notes, call_notes, LinkedIn contacts consolidated into enrichment_notes).

### Step 5: Updated Views

Created `f990_2025.v_campaign_prospects` view joining campaign_prospect_status with fp2 and np2.

### Step 6: Dropped Redundant Tables

| Table | Action | Backup |
|-------|--------|--------|
| f990_2025.sales_foundation_prospects (761 rows) | Dropped | _bak_sales_foundation_prospects |
| f990_2025.sales_nonprofit_prospects (74,175 rows) | Dropped | _bak_sales_nonprofit_prospects |

**Not dropped (kept for now):** grantscout_campaign.foundation_prospects and grantscout_campaign.nonprofit_prospects. These still have some columns (icp_score, personalization data, Google Places enrichment) that may be referenced by the campaign sender scripts. Recommend dropping after sender refactor.

---

## Task 4: Verification

### Foundation Emails (fp2)

| Metric | Before | After |
|--------|--------|-------|
| Total foundations | 143,184 | 143,184 |
| With any email value | 10,092 | 10,185 |
| With valid email (contains @) | 8,608 | 8,712 |
| With bad value (N/A, URL, etc) | 1,484 | 1,473 |

**+93 new emails, +12 junk-to-real fixes = 105 improvements.**

### Nonprofit Emails (np2)

| Metric | Before | After |
|--------|--------|-------|
| Total nonprofits | 673,381 | 673,381 |
| contact_email column | Did not exist | Created |
| With email | 0 | 6,372 |
| Unique emails | 0 | 6,372 |

### Org URL Enrichment (oue)

| Org Type | Valid Emails |
|----------|-------------|
| Foundation | 8,721 |
| Nonprofit | 6,362 |
| **Total** | **15,083** |

### Campaign History Preservation

| Metric | CSV Source | DB After | Match? |
|--------|-----------|----------|--------|
| Total tracked prospects | 1,836 | 1,836 | Yes |
| Grant alerts | 1,392 | 1,388 | ~Yes (4 dedup) |
| Debarment | 229 | 226 | ~Yes (3 dedup) |
| Food recall | 220 | 219 | ~Yes (1 dedup) |
| Replies | 5 | 5 | Yes |
| Bounced | 113 | 113 | Yes |
| Send errors | 10 | 10 | Yes |
| Initial sends | 1,844 | 1,836 | Match (unique emails) |
| Followup sends | 846 | 846 | Yes |

### Orphan Emails (no EIN match)

| Vertical | Count |
|----------|-------|
| debarment | 225 |
| food_recall | 219 |
| grant_alerts | 5 |
| **Total** | **449** |

The 444 debarment/food_recall orphans are expected: these are business contacts (restaurants, contractors) that have no EIN in our nonprofit/foundation database. The 5 grant_alerts orphans are the unmatched orgs listed above.

### Foundation Enrichment

| Metric | Before | After |
|--------|--------|-------|
| Total records | 34 | 374 |
| Added from gc research | -- | 340 |

### Data Quality Issues Found

1. **1,473 bad emails in fp2:** Values like "N/A" (635), "NONE" (130), "NA" (53), URLs without @ (697). These come from pf_returns IRS filings. Recommend a cleanup pass: set these to NULL and mark email_source = 'irs_junk'.

2. **12 unmatched CSV orgs:** Minor org_name mismatches vs np2. Could be matched with fuzzy matching but not worth the effort for 12 records.

3. **grantscout_campaign tables still exist:** Kept because the campaign sender scripts may reference them. Recommend dropping after sender refactor is complete.

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| REPORT_2026-02-16_email_migration.md | Enhancements/2026-02-16/ | This report |

### Database Changes

| Object | Change | Rows Affected |
|--------|--------|---------------|
| f990_2025.foundation_prospects2 | Updated app_contact_email (93 new + 12 fixed) | 105 |
| f990_2025.nonprofits_prospects2 | Added contact_email column, imported 6,372 emails | 6,372 |
| f990_2025.org_url_enrichment | Updated app_contact_email for 6,476 rows | 6,476 |
| f990_2025.campaign_prospect_status | **Created** table + 4 indexes | 1,836 rows |
| f990_2025.foundation_enrichment | Inserted 340 research records | 340 |
| f990_2025.v_campaign_prospects | **Created** view | -- |
| f990_2025.sales_foundation_prospects | **Dropped** | Backed up to _bak_ |
| f990_2025.sales_nonprofit_prospects | **Dropped** | Backed up to _bak_ |
| f990_2025._bak_sales_foundation_prospects | **Created** backup | 761 |
| f990_2025._bak_sales_nonprofit_prospects | **Created** backup | 74,175 |

### Schema Audit Steps Completed

| Step | Description | Status |
|------|-------------|--------|
| Step 1 | Add email to fp2 | Done (previous session) |
| Step 2 | Expand org_url_enrichment | Done (previous session) |
| Step 3 | Create web_* tables | Done (previous session) |
| **Step 4** | **Migrate campaign V1 data** | **Done (this session)** |
| **Step 5** | **Update views** | **Done (this session)** |
| **Step 6** | **Drop redundant tables** | **Done (sales_* dropped, gc kept for now)** |

---

## Notes

### Recommendations

1. **Clean fp2 email junk:** Run `UPDATE f990_2025.foundation_prospects2 SET app_contact_email = NULL WHERE app_contact_email NOT ILIKE '%@%';` to remove 1,473 non-email values. This would bring valid email count to 8,712 clean records.

2. **Drop grantscout_campaign tables:** After refactoring the campaign sender to use campaign_prospect_status + fp2/np2, drop grantscout_campaign.foundation_prospects and grantscout_campaign.nonprofit_prospects.

3. **Drop backup tables:** After confirming the migration is stable (1-2 weeks), drop _bak_sales_foundation_prospects and _bak_sales_nonprofit_prospects.

4. **Email enrichment pipeline:** The CSV file (6,366 emails) was the biggest source of nonprofit emails. Running a similar scraping campaign for the remaining 667,009 nonprofits without emails would significantly expand outreach capacity.

### Campaign Sender Script Impact

The campaign sender (`Email Campaign 2025-11-3/`) currently reads from grantscout_campaign tables. To use the new structure:
- Read prospects from fp2/np2 (with email)
- Read/write campaign status to campaign_prospect_status
- The v_campaign_prospects view provides a unified read interface

---

*Generated by Claude Code on 2026-02-16*
