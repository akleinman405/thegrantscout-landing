# SESSION STATE: Schema Reference Consolidation (3 Deliverables + Review)

**Last Updated:** 2026-02-25 18:00
**Working Folder:** `Enhancements/2026-02-23/`
**Status:** In Progress (review fixes pending)

---

## RESUME POINT (Read This First)

### Do This Next
Fix 3 findings from comprehensive review, then write the REVIEW report file:

1. **Fix schema.md line 131** — `cohort_foundation_lists_v2` says `PK: cohort_id` but v2 has no `cohort_id` column (that's v1). Replace with `UNIQUE: (state, ntee_sector, foundation_rank)`. Verify constraint via: `SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'f990_2025.cohort_foundation_lists_v2'::regclass;`

2. **Fix DATABASE_SCHEMA_REFERENCE.md line ~50** — nonprofit_returns section uses wrong column names: `net_assets` should be `net_assets_eoy` / `net_assets_boy`, and `program_service_desc_1` should be `program_1_desc`. Verify via: `SELECT column_name FROM information_schema.columns WHERE table_schema='f990_2025' AND table_name='nonprofit_returns' AND column_name LIKE 'net_assets%' OR column_name LIKE 'program_%' ORDER BY column_name;`

3. **Verify DATABASE_SCHEMA_REFERENCE.md line ~397** — `sales_prospects` view references `grantscout_campaign.nonprofit_prospects` schema. Verify via: `SELECT definition FROM pg_views WHERE viewname='sales_prospects';`

4. **Write review report** — `Enhancements/2026-02-23/REVIEW_2026-02-25_schema_reference_consolidation.md` using comprehensive-review format (see skill instructions)

5. **Update existing report** — `Enhancements/2026-02-23/REPORT_2026-02-25_schema_reference_consolidation.md` to note review was completed and fixes applied

### Remaining Steps
1. Apply 3 review fixes (above)
2. Write REVIEW report file
3. Update completion report to note review status

---

## What's Done
- **Deliverable 1:** `.claude/rules/schema.md` (214 lines) — auto-loaded every session, column gotchas at top, 12 join patterns, 15 high-use tables, email/client pipeline tables, views, filter patterns
- **Deliverable 2:** `2. Docs/thegrantscout_schema.json` (135KB) — 63 tables + 2 MVs + 10 views, all columns with types/FKs/PKs, 7 gotchas, 12 join patterns
- **Deliverable 3:** 8 new column reference files + `DATABASE_SCHEMA_REFERENCE.md` overview (see Files below)
- **data-dictionary.md** updated: fixed 6+ wrong column names, removed 5 phantom tables, added 12+ missing tables, added MVs/views/public schema sections
- **database.md** slimmed to behavioral rules only (92 lines), points to schema.md for details
- **CLAUDE.md** updated: Database Reference section points to schema.md, fixed docs path
- **sop-reminder.sh** updated: added 4-line column gotchas block
- **Completion report** written: `REPORT_2026-02-25_schema_reference_consolidation.md`
- **Comprehensive review** completed: 6 passes, found 2 Important + 1 Moderate findings

## What's Partially Done
- Review fixes: findings identified but NOT yet applied (user requested fix in another terminal)

## What's Not Started
- REVIEW report file (persistent record of the comprehensive review)
- Upload `thegrantscout_schema.json` to Claude Chat project for testing

---

## Decisions Made

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|---------|
| `.claude/rules/` (auto-loaded) | `~/.claude/` (manual) | Auto-loaded every session, prevents column guessing |
| Compact inline format (1 line/table) | Full markdown tables | Saves ~60% tokens, fits under 250 lines |
| Gotchas at top of schema.md | Bottom or separate file | Read before any SQL is written |
| Bulk psql query for metadata | 79 individual MCP calls | One query, no aborted-state risk |
| 3 deliverables (CLI/Chat/Human) | Single file | Different audiences need different formats |
| COUNT(*) UNION ALL for row counts | pg_stat_user_tables | pg_stat returned 0 without ANALYZE |

---

## What Was Tried (Failed Approaches)

| Approach | Why It Failed | Lesson |
|----------|--------------|--------|
| MCP information_schema query (all columns) | 440K chars exceeded max tokens | Save to file, parse with Python for large metadata queries |
| pg_stat_user_tables for row counts | Returns 0 for all tables without ANALYZE | Use COUNT(*) UNION ALL instead |
| Write session_state.md without reading first | Write tool requires reading existing files first | Always Read before Write for existing files |

---

## Files Created/Modified

| File | Status | Description |
|------|--------|-------------|
| `.claude/rules/schema.md` | Created | Auto-loaded schema reference (214 lines) |
| `2. Docs/thegrantscout_schema.json` | Created | Comprehensive JSON for Claude Chat (135KB) |
| `2. Docs/DATABASE_SCHEMA_REFERENCE.md` | Created | Human-readable overview (476 lines) — HAS REVIEW FINDING |
| `2. Docs/dim_foundations_column_reference.md` | Created | 12 columns documented |
| `2. Docs/dim_recipients_column_reference.md` | Created | 11 columns documented |
| `2. Docs/dim_clients_column_reference.md` | Created | 40 columns documented |
| `2. Docs/fact_grants_column_reference.md` | Created | 14 columns documented |
| `2. Docs/fact_foundation_client_scores_column_reference.md` | Created | 7 columns documented |
| `2. Docs/officers_column_reference.md` | Created | 23 columns documented |
| `2. Docs/calc_foundation_profiles_column_reference.md` | Created | 22 columns documented |
| `2. Docs/campaign_prospect_status_column_reference.md` | Created | 29 columns documented |
| `2. Docs/data-dictionary.md` | Modified | Fixed 6+ wrong cols, +12 tables, -5 phantom tables |
| `.claude/rules/database.md` | Modified | Slimmed to 92 lines, behavioral rules only |
| `.claude/CLAUDE.md` | Modified | Updated Database Reference pointers |
| `.claude/hooks/sop-reminder.sh` | Modified | Added column gotchas block |
| `Enhancements/2026-02-23/REPORT_2026-02-25_schema_reference_consolidation.md` | Created | Completion report |

---

## Database Changes Made

No database changes this session.

---

## Reports Created

| File | Description |
|------|-------------|
| `Enhancements/2026-02-23/REPORT_2026-02-25_schema_reference_consolidation.md` | Completion report for schema consolidation |

---

## Database Queries That Worked

```sql
-- Bulk column metadata dump (all schemas)
SELECT table_schema, table_name, column_name, data_type,
       character_maximum_length, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema IN ('f990_2025','public')
ORDER BY table_schema, table_name, ordinal_position;

-- Accurate row counts (pg_stat returns 0 without ANALYZE)
SELECT 'fact_grants' as tbl, COUNT(*) as cnt FROM f990_2025.fact_grants
UNION ALL SELECT 'dim_foundations', COUNT(*) FROM f990_2025.dim_foundations
UNION ALL ...;

-- Verify cohort_foundation_lists_v2 constraints
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'f990_2025.cohort_foundation_lists_v2'::regclass;
```

---

## Key Data Findings

- 66 total objects: 63 tables + 2 materialized views + 10 views (+ 1 public schema table)
- 1,486 total columns across all tables
- dim_recipients has grown from 263,895 to 1,652,766 rows since CLAUDE.md was last updated
- Two `_bak_*` backup tables exist but were excluded from all documentation

---

## Blockers (if any)

None. Review findings are straightforward to fix.

---

## Review Findings (3 total)

| ID | Severity | Location | Issue |
|----|----------|----------|-------|
| F1 | Important | `schema.md:131` | `PK: cohort_id` wrong for v2 (v1 column) |
| F2 | Important | `DATABASE_SCHEMA_REFERENCE.md:~50` | Wrong nonprofit_returns column names |
| F3 | Moderate | `DATABASE_SCHEMA_REFERENCE.md:~397` | sales_prospects view schema reference unverified |

---

*Generated by Claude Code on 2026-02-25 18:00*
