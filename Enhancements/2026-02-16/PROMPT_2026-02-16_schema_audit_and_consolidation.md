# PROMPT: Database Schema Audit & Number Reconciliation

**Date:** 2026-02-16
**Agent:** Claude Code CLI
**Type:** Audit → Recommend (no changes without approval)
**Priority:** HIGH — blocks implementation of all pipeline work

---

## Start in Planning Mode

Read everything listed in Context, run the queries, present findings. Do NOT create, alter, or drop any tables without explicit approval.

## Context

We just completed 8 research reports on URL discovery, email discovery, and contact enrichment for our email outreach pipeline. The reports surfaced two problems that need fixing before we implement anything:

### Problem 1: Conflicting Numbers

Different reports give different foundation URL coverage numbers. All of these appeared in today's reports:

| Claim | Source Report | Definition Used |
|-------|-------------|-----------------|
| 9.9% (14,107) | Synthesis report, confirmed | `org_type = 'foundation' AND url_validated = true` |
| 13.3% (19,094) | Synthesis report | IRS-filed URL (pre-cleaning) |
| 33.3% (47,690) | No-URL report | "Has website URL" (any URL, validated or not) |
| 56.5% (80,930) | Data sources report (WRONG) | Counted scraped_low/medium as "validated" — synthesis corrected this |

We need ONE canonical query that defines each coverage tier clearly, run against the live database, so all future work uses consistent numbers.

### Problem 2: Schema Fragmentation

We have multiple overlapping tables built at different times for different purposes:

- `f990_2025.org_url_enrichment` — 813K rows, one per EIN, foundations + nonprofits. Used by URL pipeline scripts 01-07.
- `f990_2025.foundation_prospects2` — built last week, all foundations
- `f990_2025.nonprofit_prospects2` — built last week, all nonprofits
- `grantscout_campaign.foundation_prospects` — older version, 761 rows
- `grantscout_campaign.nonprofit_prospects` — older version, 74K rows
- `f990_2025.pf_returns` — source data, 638K rows, multiple filings per EIN
- `f990_2025.officers` — 26.3M records
- `f990_2025.fact_grants` / `dim_recipients` — grant data
- `web_emails`, `web_staff`, `web_org_metadata`, `web_pages`, `web_best_email` — designed in scraper analysis but TABLES DON'T EXIST YET
- `grantscout_campaign` schema — senders, sends, responses, etc.

It's unclear which table is the single source of truth. The pipeline scripts write to `org_url_enrichment`, the prospects2 tables were built as master prospect tables, and the campaign tables are what the email sender reads from. Data may be inconsistent between them.

## Tasks

### Phase 1: Inventory (report only)

1. **List every table in both schemas** (`f990_2025` and `grantscout_campaign`):
   - Table name, row count, column count, key columns (first 5-6 most relevant)
   - When it was created (check pg_stat_user_tables or table comments if available)
   - What it appears to be used for

2. **Map column overlap:**
   - Which tables have URL columns? Are the values consistent across tables for the same EIN?
   - Which tables have email columns? Same question.
   - Which tables have org name, EIN, NTEE, address, phone? Flag any redundancy.

3. **Run the canonical coverage queries:**
   For foundations (using whatever table is most complete):
   ```
   - Total unique foundation EINs
   - Has any URL (raw, pre-cleaning)
   - Has cleaned URL
   - Has validated URL (HTTP alive)
   - Has validated URL by source (irs_filing, scraped_high, scraped_medium, scraped_low, pattern_guess, ein_propagation)
   - Has email (app_contact_email from pf_returns)
   - Has phone
   - Has URL OR email (contactable)
   - Breakdown by asset tier ($0-100K, $100K-1M, $1M-10M, $10M-100M, $100M+)
   ```
   
   For nonprofits (same structure):
   ```
   - Total unique nonprofit EINs
   - Has any URL
   - Has validated URL
   - Has email
   - Has phone
   - Contactable (URL or email)
   ```

4. **Check prospects2 vs org_url_enrichment:**
   - How many EINs are in foundation_prospects2 that aren't in org_url_enrichment? Vice versa?
   - Do URL values match for shared EINs?
   - What columns does prospects2 have that org_url_enrichment doesn't?

5. **Check v1 vs v2 prospect tables:**
   - Is grantscout_campaign.foundation_prospects a subset of f990_2025.foundation_prospects2?
   - Can the v1 tables be dropped?
   - What does the campaign sender pipeline actually read from?

6. **Assess the web_* tables design:**
   - The scraper analysis designed these tables but they were never created. Review the DDL.
   - Do they need foreign keys to org_url_enrichment or prospects2?
   - What schema should they live in?

Present all findings in a structured report. Stop here and wait for approval before Phase 2.

### Phase 2: Recommend Target Architecture (after approval)

Based on findings, propose:

1. **One master org table per type** (or explain why not). Should `foundation_prospects2` and `nonprofit_prospects2` become the single source of truth that consolidates:
   - IRS data (name, EIN, address, NTEE, officers)
   - URL enrichment (cleaned URL, validated URL, URL source, validation date)
   - Email enrichment (best email, source, validation status)
   - Contact info (contact name, phone, title)
   - Profile data for future use (mission summary, grant history, bank trustee)
   - Campaign status (has been emailed, last contact date, response)

2. **What happens to org_url_enrichment?** Options:
   - Keep it as the enrichment staging table (scripts write here, then sync to prospects2)
   - Merge its columns into prospects2 and retire it
   - Keep both with clear roles

3. **What happens to the grantscout_campaign prospect tables?**
   - Are they views? Copies? Do they need to stay in sync?
   - Should the campaign sender read from prospects2 instead?

4. **Where do the web_* tables go?**
   - f990_2025 schema or a new enrichment schema?
   - Foreign key to which parent table?

5. **Migration plan** if changes are recommended:
   - What data needs to move
   - What scripts need updating (list the script names and what table references change)
   - What can be dropped
   - Rollback plan

## Output

### Deliverables

1. `REPORT_2026-02-16_schema_audit.md` with:
   - Complete table inventory (both schemas)
   - Canonical coverage numbers (the ONE set of numbers all future work should use)
   - Column overlap matrix
   - Consistency check results
   - Recommended target architecture (Phase 2)
   - Migration plan if applicable

2. Update `SPEC_email_pipeline.md` "Current State" section with the canonical numbers (after approval)

## Notes

- Do NOT create, alter, or drop any tables. This is read-only audit + recommendation.
- The goal is: after this prompt, every future prompt knows exactly which table to read from and write to, and uses the same numbers.
- If you discover tables I didn't list above, include them in the inventory.
- Pay special attention to the `url_source` column values and what they mean — this is where the 56.5% vs 9.9% confusion originated.
