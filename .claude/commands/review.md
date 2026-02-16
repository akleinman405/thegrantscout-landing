---
description: Run TheGrantScout-specific code review on current changes
argument-hint: Files or scope (optional)
allowed-tools: Read, Grep, Glob, Bash(git *), Task
---

# Structured Code Review

Run a directed code review against current changes using TheGrantScout-specific checks.

Optional scope (defaults to all uncommitted changes): $ARGUMENTS

## Instructions

1. **Determine review scope**:
   - If `$ARGUMENTS` specifies files or a scope, review those
   - Otherwise, run `git diff` and `git diff --cached` to get all uncommitted changes
   - If no uncommitted changes exist, review the most recent commit with `git diff HEAD~1`

2. **Collect the changed code**: Read the full current version of every modified file (not just the diff) so you have complete context for the review.

3. **Run three review passes in parallel** using sub-agents:

### Agent 1 — Correctness & Logic
- Are Python functions handling errors properly? (try/except, edge cases, empty DataFrames)
- Are SQL queries correct? (joins, GROUP BY, aggregations, NULL handling)
- Are pandas operations safe? (checking for empty results, correct merge keys, dtype mismatches)
- Are file paths constructed correctly? (spaces in folder names like `4. Pipeline/`)
- Are nullable values checked before use?
- Do loops and iterations handle empty collections?
- Are return types consistent with what callers expect?
- Are database connections properly closed? (use context managers or try/finally)

### Agent 2 — Security & Data Safety
- No database passwords, API keys, or secrets in code or comments
- No credentials hardcoded (should reference `.env` or `Postgresql Info.txt`)
- SQL queries use parameterized queries (not string formatting/f-strings for user input)
- No sensitive data (EINs, client names) in log output or error messages that could leak
- File paths and user input are sanitized
- `.env` files not committed to git

### Agent 3 — TheGrantScout-Specific Patterns
- **Schema prefix**: All SQL queries use `f990_2025.table_name` (not bare table names)?
- **Database name**: Connections use `thegrantscout` (not `postgres`)?
- **EIN handling**: EINs treated as VARCHAR, leading zeros preserved, no integer casts, no dashes?
- **fact_grants joins**: Uses `foundation_ein` (not `filer_ein`) when joining fact_grants?
- **Data quality filters**: `only_contri_to_preselected_ind = FALSE` applied? Website junk values ("N/A", "NONE", "0") filtered?
- **File naming**: Output files follow `DOCTYPE_YYYY-MM-DD.N_description.ext` convention?
- **Excel formatting**: Follows standards? (blank row 1/col A, zoom 140%, TableStyleMedium2, Calibri 10pt, bold headers on dark blue, commas in numbers, `"$"#,##0` for currency)
- **Report structure**: Includes required sections? (TOC, Revision History, Executive Summary)
- **Client known funders**: Excluded from results where applicable?
- **Dollar formatting**: Consistent `$X,XXX` format in reports?
- **Production filters**: Applied where needed? (assets >= $100K, unique_recipients >= 5, preselected_only = FALSE)
- **Python commands**: Uses `python3`/`pip3` (not `python`/`pip`)?

4. **Compile results** into this format:

```markdown
## Code Review: [scope description]

**Files Reviewed:** [count]
**Review Date:** YYYY-MM-DD

---

### Critical Issues (Must Fix)

| # | Severity | File:Line | Issue | Suggested Fix |
|---|----------|-----------|-------|---------------|
| 1 | CRITICAL | `file.py:42` | Description | How to fix |

### Warnings (Should Fix)

| # | Severity | File:Line | Issue | Suggested Fix |
|---|----------|-----------|-------|---------------|
| 1 | WARNING | `file.py:15` | Description | How to fix |

### Info (Consider)

| # | File:Line | Suggestion |
|---|-----------|------------|
| 1 | `file.py:8` | Optional improvement |

---

### Passed Checks

**Correctness & Logic:**
- [x] SQL queries correct (joins, aggregations, NULLs)
- [x] Error paths handled
- [x] Pandas operations safe
- [x] File paths handle spaces
- [x] DB connections properly closed

**Security & Data Safety:**
- [x] No secrets in code
- [x] Parameterized SQL queries
- [x] No sensitive data in logs
- [x] .env not committed

**TheGrantScout-Specific:**
- [x] Schema prefix (f990_2025.) used
- [x] EIN handling correct (VARCHAR, leading zeros)
- [x] foundation_ein used in fact_grants joins
- [x] Data quality filters applied
- [x] File naming convention followed
- [x] Excel formatting standards met (if applicable)
- [x] Report structure complete (if applicable)
- [x] Client known funders excluded (if applicable)
- [x] Dollar formatting consistent
- [x] Production filters applied (if applicable)

---

### Summary

[1-2 sentences: overall assessment and whether changes are ready to commit]
```

5. **Present the review** to the user. If there are CRITICAL issues, emphasize them clearly. If the review is clean, say so concisely.
