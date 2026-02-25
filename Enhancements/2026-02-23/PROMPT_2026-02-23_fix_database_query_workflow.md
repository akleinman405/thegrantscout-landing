# Fix: Claude Code PostgreSQL Query Workflow

**Document Type:** PROMPT
**Purpose:** Fix recurring database query failures — wrong column names, cascade errors from parallel execution, and stuck transactions
**Date:** 2026-02-23
**Priority:** HIGH (impacts every database task)

---

## Problem

Every time Claude Code runs SQL queries against our PostgreSQL database, we hit the same three failures:

1. **Wrong column names** — Claude guesses column names (e.g. `purpose` instead of `purpose_text`) because it doesn't inspect the schema first. This causes the first query to fail.
2. **Parallel cascade failures** — Claude runs all queries simultaneously. When the first one errors, every sibling query fails with "Sibling tool call errored" even though those queries might be fine.
3. **Stuck transactions** — After an error, PostgreSQL enters "aborted transaction" state. All subsequent queries fail with "current transaction is aborted, commands ignored until end of transaction block" until someone issues a ROLLBACK. Claude doesn't do this automatically.

The result: a simple 3-query task turns into 15+ failed attempts and wastes time/tokens.

---

## Required Fix

### 1. Pre-flight schema check (MANDATORY before any SQL)

Before writing ANY query, Claude MUST inspect the target tables first:

```sql
-- Option A: Quick column list
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'f990_2025' AND table_name = 'fact_grants'
ORDER BY ordinal_position;

-- Option B: psql shorthand
\d f990_2025.fact_grants
```

**Rule:** Never assume a column name. Always verify against actual schema. This applies even for tables you've queried before — column names may have changed.

### 2. Sequential execution (NEVER parallel for database queries)

**Rule:** Run database queries ONE AT A TIME. Wait for each result before running the next. Never use parallel/sibling tool calls for SQL.

Why: PostgreSQL MCP connections share a transaction. One error poisons all parallel queries. Sequential execution means only the bad query fails.

### 3. Auto-recover from errors

**Rule:** After ANY SQL error, immediately run:

```sql
ROLLBACK;
```

Then fix the query and retry. Don't attempt other queries while the transaction is in an aborted state.

---

## Implementation

Add these rules to CLAUDE.md or the project's Claude Code configuration so they persist across sessions:

```markdown
## Database Query Rules

1. **ALWAYS inspect schema before querying.** Run `SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '<schema>' AND table_name = '<table>'` for every table you plan to query. Do this BEFORE writing any SQL.
2. **NEVER run SQL queries in parallel.** Execute one query at a time. Wait for the result before running the next.
3. **After any SQL error, immediately run `ROLLBACK;`** before attempting any other query.
4. **Primary schema is `f990_2025`.** Key tables: dim_foundations, dim_recipients, dim_clients, fact_grants, fact_foundation_client_scores, pf_returns, pf_grants, nonprofit_returns, nonprofits_prospects2, campaign_prospect_status.
```

### Optional: Create a schema reference file

Generate a quick-reference file Claude can read at the start of any database task:

```bash
psql -h 172.26.16.1 -U alec -d thegrantscout -c "
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'f990_2025' 
  AND table_name IN (
    'dim_foundations','dim_recipients','dim_clients',
    'fact_grants','fact_foundation_client_scores',
    'pf_returns','pf_grants','nonprofit_returns',
    'nonprofits_prospects2','campaign_prospect_status'
  )
ORDER BY table_name, ordinal_position;
" > ~/.claude/db_schema_reference.txt
```

Then instruct Claude Code to `cat ~/.claude/db_schema_reference.txt` at the start of any database prompt.

---

## Acceptance Criteria

- [ ] CLAUDE.md updated with the 4 database query rules above
- [ ] Schema reference file generated at `~/.claude/db_schema_reference.txt`
- [ ] Test: run 3 queries sequentially against different tables — all succeed on first attempt
- [ ] Test: intentionally cause an error — Claude auto-rolls back and retries successfully
