# PROMPT: Comprehensive F990_2025 Schema Audit & Database Review

**Document Type:** PROMPT  
**Date:** 2025-02-20  
**Target:** Claude Code CLI  
**Estimated Scope:** Multi-phase, self-orchestrating  

---

## Situation

TheGrantScout uses a PostgreSQL database with the `f990_2025` schema as the primary data layer. The schema was originally built in late 2025 to import IRS Form 990-PF XML data, then expanded with additional tables for matching, reporting, and enrichment. Since the last comprehensive documentation (DATA_DICTIONARY.md from Nov 2025, SPEC_2025-12-08_database.md), we have:

- Imported additional F990 data (new tax years, new form types)
- Created new derived/working tables
- Built report generation pipelines
- Added tables that may not be documented anywhere

The existing documentation is likely **stale and incomplete**. We need a ground-truth audit of what actually exists in the database right now.

---

## Phase 1: Discovery — Read Before You Touch

Before running any SQL, read the following files to understand what was *intended* and *documented*:

### Documentation to Read
1. `1. Database/DATA_DICTIONARY.md` — original field-level docs
2. `0. The Grant Scout Specs/SPEC_2025-12-08_database.md` — database architecture spec
3. `1. Database/Build Plan.md` — original build roadmap
4. `.claude/Team Enhancements/` — read ALL markdown files in every Enhancements subfolder (2025-11-27, 2025-12-05, and any others). These contain schema changes, gotchas, and enhancement notes.
5. `1. Database/F990-2025/2. Import review + fixes/` — all reports in this folder
6. `1. Database/F990-2025/1. Import/schema.sql` — the DDL that created the schema
7. `1. Database/F990-2025/1. Import/config.yaml` — import configuration
8. Any `REPORT_*.md` files in the project root or subdirectories

### Report Generation Pipeline Files to Read
9. `2. Beta Testing/1. Reports/` — examine folder structure, any scripts or templates
10. `.claude/agents/reporter.md` — the reporter agent definition
11. Any Python files that generate reports (search for `report` or `generate` in filenames)
12. The matching algorithm file(s) — search for `matching` or `algorithm` in filenames

**Deliverable after Phase 1:** Write a brief summary of what the docs SAY exists vs what you expect to find. Note any contradictions or gaps between documents. Save as `REPORT_2025-02-20_phase1_doc_review.md`.

---

## Phase 2: Schema Audit — What Actually Exists

Connect to the database and catalog everything in the `f990_2025` schema AND the `public` schema.

### For EVERY table in f990_2025 schema, capture:
- Table name
- Row count (`SELECT COUNT(*) FROM ...`)
- Column names, types, and nullable status
- Primary keys, foreign keys, indexes
- Sample of 3 rows (first 3)
- Apparent purpose (inferred from name + columns + data)
- Date range of data (if applicable — check tax_year, created_at, etc.)
- Whether it appears in existing documentation or is undocumented

### For EVERY table in public schema, capture the same.

### Also check for:
- Any OTHER schemas besides f990_2025 and public
- Extensions installed (`SELECT * FROM pg_extension`)
- Views and materialized views
- Functions and stored procedures
- Sequences
- Orphaned indexes or constraints

### SQL to run for schema discovery:
```sql
-- All schemas
SELECT schema_name FROM information_schema.schemata;

-- All tables per schema
SELECT table_schema, table_name, 
       (xpath('/row/cnt/text()', xml_count))[1]::text::int as row_count
FROM information_schema.tables t
LEFT JOIN LATERAL (
    SELECT query_to_xml(format('SELECT COUNT(*) AS cnt FROM %I.%I', t.table_schema, t.table_name), false, true, '') AS xml_count
) x ON true
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;

-- All columns
SELECT table_schema, table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema IN ('f990_2025', 'public')
ORDER BY table_schema, table_name, ordinal_position;

-- All indexes
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname IN ('f990_2025', 'public');

-- All foreign keys
SELECT tc.table_schema, tc.table_name, kcu.column_name,
       ccu.table_schema AS foreign_table_schema,
       ccu.table_name AS foreign_table_name,
       ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema IN ('f990_2025', 'public');

-- Extensions
SELECT * FROM pg_extension;

-- Views
SELECT table_schema, table_name FROM information_schema.views
WHERE table_schema NOT IN ('pg_catalog', 'information_schema');

-- Functions
SELECT routine_schema, routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema NOT IN ('pg_catalog', 'information_schema');
```

**Deliverable after Phase 2:** Save complete findings as `REPORT_2025-02-20_phase2_schema_audit.md` with a table-by-table catalog.

---

## Phase 3: Pipeline & Lineage Review

Trace how data flows from IRS XML files → f990_2025 tables → public tables → reports.

### Questions to answer:
1. What scripts populate the f990_2025 tables? (trace import_f990.py, any other importers)
2. What scripts/queries move data from f990_2025 → public schema tables (foundations, historical_grants, etc.)?
3. What scripts generate the monthly reports? What tables do they query?
4. Are there any tables that are populated but never queried by anything?
5. Are there any tables that are queried but empty or stale?
6. What is the EIN enrichment status? (how many grants have recipient EINs vs just names?)

### Data quality checks to run:
```sql
-- Grant purpose coverage
SELECT COUNT(*) as total_grants,
       COUNT(grant_purpose) as has_purpose,
       ROUND(COUNT(grant_purpose)::numeric / COUNT(*)::numeric * 100, 1) as pct_with_purpose
FROM f990_2025.pf_grants;

-- Recipient EIN coverage
SELECT COUNT(*) as total_grants,
       COUNT(recipient_ein) as has_ein,
       ROUND(COUNT(recipient_ein)::numeric / COUNT(*)::numeric * 100, 1) as pct_with_ein
FROM f990_2025.pf_grants;

-- Tax year distribution in pf_returns
SELECT tax_year, COUNT(*) as returns FROM f990_2025.pf_returns GROUP BY tax_year ORDER BY tax_year;

-- Tax year distribution in pf_grants
SELECT tax_year, COUNT(*) as grants FROM f990_2025.pf_grants GROUP BY tax_year ORDER BY tax_year;

-- foundations table freshness
SELECT MIN(created_at), MAX(created_at), COUNT(*) FROM public.foundations;

-- historical_grants freshness
SELECT MIN(grant_year), MAX(grant_year), COUNT(*) FROM public.historical_grants;

-- Check for tables that might be new/undocumented
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'f990_2025' 
AND table_name NOT IN ('pf_returns', 'pf_grants', 'nonprofit_returns', 'officers', 'schedule_a', 'import_log');
```

**Deliverable after Phase 3:** Save as `REPORT_2025-02-20_phase3_pipeline_review.md`.

---

## Phase 4: Self-Review & Consolidated Report

Review your own Phase 1-3 reports. Then produce a single consolidated document:

### `REPORT_2025-02-20_database_audit_complete.md` should contain:

1. **Executive Summary** — 5-bullet overview of database state
2. **Complete Table Catalog** — Every table across all schemas, organized by:
   - Schema
   - Purpose category (source, production, derived, staging, orphaned)
   - Row count, column count
   - Documentation status (documented / undocumented / stale docs)
3. **Data Pipeline Map** — ASCII or text diagram showing data flow from IRS XML → tables → reports
4. **Data Quality Scorecard** — Coverage percentages for key fields (EIN, purpose, amounts, etc.)
5. **Documentation Gaps** — What exists in the DB but not in docs, and vice versa
6. **New Since Last Audit** — Tables, columns, or data that were added after the Dec 2025 specs
7. **Recommendations** — Prioritized list of:
   - Tables to drop (orphaned/duplicate)
   - Tables to create (missing but needed)
   - Indexes to add
   - Data to backfill
   - Schema changes needed
   - Documentation to update

---

## Output Naming Convention

All outputs go in the project root:
- `REPORT_2025-02-20_phase1_doc_review.md`
- `REPORT_2025-02-20_phase2_schema_audit.md`
- `REPORT_2025-02-20_phase3_pipeline_review.md`
- `REPORT_2025-02-20_database_audit_complete.md` (final consolidated)

---

## Important Context

- **Database:** PostgreSQL, host 172.26.16.1, port 5432, database `postgres`
- **Primary schema:** `f990_2025` — use this exclusively, ignore `public` schema tables unless tracing lineage
- **The `public` schema** has production tables (foundations, historical_grants, matches, etc.) plus legacy staging tables (irs_bmf_eo1-4, emails_temp, nonprofits_merged)
- **Known stale docs:** DATA_DICTIONARY.md is from Nov 2025, SPEC is from Dec 2025
- **Known issue:** Grant purpose field had a bug that was fixed via backfill_grant_purpose.py
- **Known issue:** Recipient EIN coverage was ~43%, enrichment was planned but status unknown
- **The Team Enhancements folders** contain the most recent change logs — READ THESE FIRST

---

## Rules

1. Read ALL documentation before running any queries
2. Do not modify any data — this is READ-ONLY audit
3. If a query times out, add LIMIT or sample instead of skipping
4. Flag anything surprising or contradictory
5. Be specific about row counts — no rounding, give exact numbers
6. When you find undocumented tables, try to infer their purpose from column names and sample data
7. Save each phase report before moving to the next
