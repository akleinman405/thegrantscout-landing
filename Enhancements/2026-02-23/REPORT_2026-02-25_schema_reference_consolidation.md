# Schema Reference Consolidation

**Date:** 2026-02-25
**Prompt:** Consolidate database schema reference into auto-loaded context for Claude Code, JSON for Claude Chat, and updated human docs
**Status:** Complete
**Owner:** Claude Code

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-25 | Claude Code | Initial version |
| 1.1 | 2026-02-25 | Claude Code | Review completed: 3 findings (2 fixed, 1 verified OK) |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem](#problem)
3. [Solution](#solution)
4. [Deliverables](#deliverables)
5. [Verification](#verification)
6. [Files Created/Modified](#files-createdmodified)
7. [Notes](#notes)

---

## Executive Summary

Consolidated database schema documentation from 15+ scattered files into three purpose-built deliverables:

1. **Auto-loaded rules file** (`.claude/rules/schema.md`, 214 lines) with column gotchas, join patterns, and all table definitions
2. **Comprehensive JSON** (`2. Docs/thegrantscout_schema.json`, 63 tables + 2 MVs + 10 views) for Claude Chat persistent context
3. **8 new column reference files** + combined overview for human reference

Also updated: `data-dictionary.md` (fixed 6+ wrong column names, added 12+ missing tables), `database.md` (slimmed to behavioral rules only), `CLAUDE.md` (updated pointers), SOP hook (added column gotchas).

## Problem

Claude Code repeatedly guessed wrong column names:
- `filer_ein` instead of `foundation_ein` in fact_grants
- `purpose` instead of `purpose_text` in fact_grants
- `mission_statement` instead of `mission_text` in dim_clients
- `business_name` instead of `name` in dim_foundations

Database documentation existed across 15+ files but none were auto-loaded into context. The data dictionary (`data-dictionary.md`) had stale entries: 6+ wrong column names, tables that no longer exist (calc_foundation_behavior, calc_foundation_primary_sector, calc_recipient_profiles, calc_recipient_prior_funders, calc_recipient_prior_grants), and 12+ missing tables (email pipeline, cohort, calc_client_*).

## Solution

### Approach
- One bulk psql query to dump all 1,486 columns across 66 tables
- Live `COUNT(*)` for accurate row counts
- Three deliverables targeting three audiences (CLI, Chat, humans)
- Column gotchas placed at the top of the auto-loaded file (prevents the #1 documented error)

### Key Design Decisions
1. **schema.md in `.claude/rules/`** (auto-loaded every session) vs. `~/.claude/` (requires manual loading)
2. **Compact inline format** for tables (one line per table with key columns) instead of full markdown tables (saves ~60% tokens)
3. **Gotchas at the top** of the file to ensure they're read before any SQL is written
4. **Join patterns section** addresses the #2 error source (wrong join conditions)

## Deliverables

### 1. `.claude/rules/schema.md` (214 lines)

| Section | Content |
|---------|---------|
| Column Gotchas | 10 confusable column pairs with correct/wrong/table/notes |
| Common Joins | 12 join patterns with aliases |
| High-Use Tables | 15 tables with full column listings |
| Email Pipeline | 6 tables for campaign system |
| Client Pipeline | 6 tables for client scoring |
| Other Tables | 20+ tables in compact format |
| Views | 10 views listed |
| Filter Patterns | 4 common WHERE clause patterns |

### 2. `2. Docs/thegrantscout_schema.json` (135 KB)

| Metric | Count |
|--------|-------|
| Tables | 63 |
| Materialized Views | 2 |
| Views | 10 |
| Total Columns | 1,373 |
| Gotchas | 7 |
| Join Patterns | 12 |

Structured JSON with types simplified, defaults cleaned up, FK annotations on 30+ columns.

### 3. Column Reference Files (8 new + 1 overview)

| File | Table | Columns |
|------|-------|---------|
| dim_foundations_column_reference.md | dim_foundations | 12 |
| dim_recipients_column_reference.md | dim_recipients | 11 |
| dim_clients_column_reference.md | dim_clients | 40 |
| fact_grants_column_reference.md | fact_grants | 14 |
| fact_foundation_client_scores_column_reference.md | fact_foundation_client_scores | 7 |
| officers_column_reference.md | officers | 23 |
| calc_foundation_profiles_column_reference.md | calc_foundation_profiles | 22 |
| campaign_prospect_status_column_reference.md | campaign_prospect_status | 29 |
| DATABASE_SCHEMA_REFERENCE.md | All tables | Overview |

## Verification

| Check | Result |
|-------|--------|
| schema.md under 250 lines | 214 lines |
| JSON parses cleanly | 63 tables, 2 MVs, 10 views |
| fact_grants column names correct | foundation_ein, purpose_text (verified against live DB) |
| dim_clients column names correct | mission_text, project_need_text (verified) |
| SOP hook includes gotchas | 4 lines added |
| New column ref files exist | 8 created + 1 overview |

## Files Created/Modified

| File | Path | Action |
|------|------|--------|
| schema.md | `.claude/rules/schema.md` | CREATE |
| thegrantscout_schema.json | `2. Docs/thegrantscout_schema.json` | CREATE |
| DATABASE_SCHEMA_REFERENCE.md | `2. Docs/DATABASE_SCHEMA_REFERENCE.md` | CREATE |
| dim_foundations_column_reference.md | `2. Docs/` | CREATE |
| dim_recipients_column_reference.md | `2. Docs/` | CREATE |
| dim_clients_column_reference.md | `2. Docs/` | CREATE |
| fact_grants_column_reference.md | `2. Docs/` | CREATE |
| fact_foundation_client_scores_column_reference.md | `2. Docs/` | CREATE |
| officers_column_reference.md | `2. Docs/` | CREATE |
| calc_foundation_profiles_column_reference.md | `2. Docs/` | CREATE |
| campaign_prospect_status_column_reference.md | `2. Docs/` | CREATE |
| data-dictionary.md | `2. Docs/data-dictionary.md` | EDIT |
| database.md | `.claude/rules/database.md` | EDIT |
| CLAUDE.md | `.claude/CLAUDE.md` | EDIT |
| sop-reminder.sh | `.claude/hooks/sop-reminder.sh` | EDIT |
| This report | `Enhancements/2026-02-23/` | CREATE |

## Review

Comprehensive 6-pass review completed. See `REVIEW_2026-02-25_schema_reference_consolidation.md` for full details.

| Finding | Severity | Resolution |
|---------|----------|------------|
| schema.md: wrong PK for cohort_foundation_lists_v2 | Important | Fixed: `No PK. Logical key: (state, ntee_sector, foundation_rank)` |
| DATABASE_SCHEMA_REFERENCE.md: wrong nonprofit_returns columns | Important | Fixed: `net_assets_eoy`/`_boy`, `program_1_desc` |
| DATABASE_SCHEMA_REFERENCE.md: sales_prospects cross-schema ref | Moderate | Verified correct, no change |

## Notes

- **Remaining TODO:** Upload `thegrantscout_schema.json` to a Claude Chat project as persistent context file and test query accuracy
- The data dictionary still references archived embedding tables for historical documentation; those table definitions are preserved but clearly marked as ARCHIVED
- `dim_recipients` row count has grown from 263,895 to 1,652,766 since CLAUDE.md was last updated; the Quick Reference table in CLAUDE.md may need a separate update pass
- Two `_bak_*` backup tables exist but were intentionally excluded from all documentation

---

*Generated by Claude Code on 2026-02-25*
