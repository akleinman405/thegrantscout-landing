# Database Rules - TheGrantScout

**Schema:** f990_2025 | **Host:** localhost:5432 | **Database:** thegrantscout

For table/column details, see `rules/schema.md` (auto-loaded).

---

## SQL Execution Rules (MANDATORY)

**IMPORTANT — Follow for EVERY database query:**

1. **Pre-flight:** Before writing SQL, verify column names against `rules/schema.md` COLUMN GOTCHAS. For unfamiliar tables, run: `SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'f990_2025' AND table_name = '<table>'`
2. **Sequential only:** NEVER run SQL queries in parallel. Execute one at a time, wait for result before the next.
3. **No SQL comments:** Never include `--` or `/* */` in MCP queries (triggers "Only SELECT" error).
4. **After any MCP error:** The connection is permanently poisoned. Do NOT retry via MCP. Switch immediately to psql via Bash with heredoc syntax.
5. **psql default for 3+ queries:** For sessions needing 3+ queries, start with psql from the beginning.
6. **psql heredoc syntax:** Always use `<<'EOSQL'` (single-quoted), never `-c "..."`. This prevents shell escaping issues with `!~`, `%`, and backslashes.

### MCP vs psql Decision

| Scenario | Tool |
|----------|------|
| 1-2 quick lookups | MCP `execute_query` |
| 3+ queries in a session | psql via Bash (heredoc) |
| After any MCP error | psql via Bash (only option) |
| Queries with regex (`!~`, `~*`) | psql via Bash |
| Write operations (INSERT/UPDATE) | Either (MCP has transaction safety) |
| Schema inspection | MCP `execute_query` with information_schema (NOT `describe_table`) |

### Broken MCP Tools (Do NOT Use)

- `list_tables` — returns only `public` schema tables
- `describe_table` — prepends `public.`, fails for f990_2025

---

## Pre-Flight Check (before writing SQL)

1. Check `rules/schema.md` COLUMN GOTCHAS section for confusable names
2. Use `f990_2025.` schema prefix on every table reference
3. For grant analysis, use `fact_grants` (not `pf_grants`) with `foundation_ein` (not `filer_ein`)
4. EINs are always VARCHAR — never cast to integer, never add dashes

---

## Data Conventions

| Field Type | Format | Notes |
|------------|--------|-------|
| Amounts | NUMERIC(15,2) or BIGINT | fact_grants.amount is bigint (no cents) |
| Dates | YYYY-MM-DD | ISO 8601 |
| EINs | VARCHAR | Preserve leading zeros, no dashes, 9 chars standard |
| Booleans | TRUE/FALSE/NULL | NULL = not applicable |
| Embeddings | ARCHIVED | Tables dropped 2026-01-04 |

---

## Critical Filter Fields

```sql
-- Foundation makes grants to organizations
grants_to_organizations_ind = TRUE

-- Foundation is open to applications (KEY!)
-- NULL often means open, so use:
(only_contri_to_preselected_ind = FALSE OR only_contri_to_preselected_ind IS NULL)

-- Valid website (exclude junk values)
website_url IS NOT NULL AND website_url NOT IN ('N/A', 'NONE', '0', '')

-- Use tax_year for temporal analysis (grant dates often NULL)
```

---

## Common Queries

### Find foundations accepting applications
```sql
SELECT ein, business_name, state, total_assets_eoy_amt
FROM f990_2025.pf_returns
WHERE grants_to_organizations_ind = TRUE
  AND (only_contri_to_preselected_ind = FALSE OR only_contri_to_preselected_ind IS NULL)
ORDER BY total_assets_eoy_amt DESC NULLS LAST;
```

### Get grant history for a foundation
```sql
SELECT recipient_name_raw, recipient_state, amount, purpose_text, tax_year
FROM f990_2025.fact_grants
WHERE foundation_ein = '123456789'
ORDER BY tax_year DESC, amount DESC;
```

### Foundation profile with calculated metrics
```sql
SELECT *
FROM f990_2025.calc_foundation_profiles
WHERE ein = '123456789';
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Column not found: filer_ein | Wrong table | Use `foundation_ein` in fact_grants |
| Column not found: purpose | Wrong table | Use `purpose_text` in fact_grants |
| Column not found: mission_statement | Wrong column | Use `mission_text` in dim_clients |
| UNIQUE constraint on filename | Duplicate XML | Check stg_processed_xml_files first |
| NULL purpose text | Wrong XPath | Use `GrantOrContributionPurposeTxt` |
| Connection refused | PostgreSQL not running | `brew services start postgresql` |
| MCP "aborted" state | SQL error in prior query | Use psql via Bash for multi-query research |
| MCP "Only SELECT" | SQL comments (--) | Remove comments from queries |

---

*For full schema: `rules/schema.md`. For column details: `2. Docs/data-dictionary.md`.*
