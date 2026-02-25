# Phase 1: Consolidate Database Schema Reference File

**Document Type:** PROMPT
**Purpose:** Create a single, authoritative schema reference file for the thegrantscout database that Claude Code can read before any SQL task
**Date:** 2026-02-23
**Priority:** HIGH (blocks efficient database work)

---

## Situation

We have database documentation scattered across multiple files in two locations. Every time Claude Code runs SQL, it guesses column names wrong because there's no single reference file to read first. We need ONE consolidated file that is the source of truth.

---

## Source Locations

Explore both of these first before deciding your approach:

1. **Docs folder:** `/Users/aleckleinman/Documents/TheGrantScout/2. Docs`
2. **Recent enhancements:** `/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-20`

These contain prior attempts at data dictionaries, schema audits, and database documentation. Some may be outdated or incomplete.

---

## Tasks

### Task 1: Explore existing documentation

- List and skim all database-related files in both folders above
- Identify what's current vs outdated vs redundant
- Note any conflicts between docs (e.g. column names that don't match)

### Task 2: Verify against the live database

Don't trust the docs blindly. For every table you include, confirm columns against the actual database:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'f990_2025' AND table_name = '<table>'
ORDER BY ordinal_position;
```

**Important:** Query tables ONE AT A TIME (not in parallel). After any error, run `ROLLBACK;` before retrying.

Focus on these high-use tables first:
- dim_foundations, dim_recipients, dim_clients
- fact_grants, fact_foundation_client_scores
- pf_returns, pf_grants, nonprofit_returns
- nonprofits_prospects2, foundation_prospects2
- campaign_prospect_status
- cohort_foundation_lists_v2, cohort_viability

Then catalog remaining tables more briefly (name, purpose, row count, key columns only).

### Task 3: Build the consolidated reference file

Create a single file: `~/.claude/db_schema_reference.md`

Structure it as:

```
# TheGrantScout Database Schema Reference
# Generated: <date>
# Source: Live database verification + existing docs

## Quick Stats
- Database: thegrantscout
- Host: 172.26.16.1 
- Schema: f990_2025 (primary), filtered_campaign, grantscout_campaign
- Total tables: X

## High-Use Tables (full column listing)

### dim_foundations (X rows)
| Column | Type | Notes |
|--------|------|-------|
...

### fact_grants (X rows)
...

## Other Tables (name + purpose + key columns only)

### pf_balance_sheet (X rows)
Purpose: 990-PF balance sheet line items
Key columns: pf_return_id, ein, tax_year, line_item, eoy_amt

...
```

### Task 4: Also save a copy in Docs

Copy the file to: `/Users/aleckleinman/Documents/TheGrantScout/2. Docs/DATABASE_SCHEMA_REFERENCE.md`

### Task 5: Update CLAUDE.md

Add a line to the Database Query Rules section of CLAUDE.md telling future sessions to read `~/.claude/db_schema_reference.md` before running any SQL queries.

---

## Approach Guidelines

- **You decide the best method.** Explore the existing files first and figure out the most efficient path. If the existing docs are 90% accurate, verify and patch. If they're a mess, query the database directly and build from scratch.
- **Accuracy > completeness.** Every column name in the reference file MUST match the live database. It's better to have 15 tables verified correctly than 50 tables with guessed columns.
- **Keep it scannable.** This file will be read by Claude Code at the start of tasks — make it easy to ctrl+F for a column name.

---

## Expected Outputs

1. `~/.claude/db_schema_reference.md` — the consolidated reference
2. `/Users/aleckleinman/Documents/TheGrantScout/2. Docs/DATABASE_SCHEMA_REFERENCE.md` — same file, backup copy
3. Updated CLAUDE.md with pointer to the reference file
4. Brief REPORT noting: what docs were outdated, what conflicts you found, what you verified vs took on trust

**Report naming:** `REPORT_2026-02-23_schema_reference_consolidation.md` saved in the Enhancements folder for today.
