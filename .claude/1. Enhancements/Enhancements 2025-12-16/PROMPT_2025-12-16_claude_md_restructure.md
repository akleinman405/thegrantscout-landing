# PROMPT: Restructure CLAUDE.md with Rules Directory

**Date:** 2025-12-16  
**For:** Claude Code CLI  
**Context:** Research completed in REPORT_2025-12-16_claude_md_best_practices.md and REPORT_2025-12-16_claude_md_recommendations.md

---

## Situation

Current CLAUDE.md is ~400 lines. Research shows optimal is 50-100 lines. Claude ignores content it deems irrelevant, so brevity matters. We're implementing the recommended modular structure with a rules directory.

---

## Tasks

### 1. Backup Current File

Copy current `C:\TheGrantScout\.claude\CLAUDE.md` to:
```
C:\TheGrantScout\.claude\1. Enhancements\Enhancements 2025-12-16\CLAUDE_old.md
```

### 2. Create New Core CLAUDE.md (~100 lines)

Location: `C:\TheGrantScout\.claude\CLAUDE.md`

Include:
- **Project Overview** - One paragraph, core value prop
- **Quick Reference table** - Updated numbers:
  - Foundations: 143,184
  - Historical grants: 8.3M
  - Semantic embeddings: 9.2M
  - Data years: 2016-2024
  - Primary schema: f990_2025
  - DB Host: 172.26.16.1:5432
- **Environment** - OS, database, Python, credentials path
- **Critical Rules** - Use `IMPORTANT:` prefix for each:
  - Always use schema prefix `f990_2025.table_name`
  - Use `foundation_ein` not `filer_ein` in fact_grants
  - EINs are VARCHAR (preserve leading zeros, no dashes)
  - `only_contri_to_preselected_ind = FALSE` means open to applications
  - Follow naming: `DOCTYPE_YYYY-MM-DD_description.ext`
- **Key Paths** - Brief table (credentials, matching algorithm, embeddings, clients)
- **Gotchas** - Top 5-6 only, table format
- **See Also** - References to:
  - `@.claude/rules/database.md`
  - `@.claude/rules/reports.md`
  - `@.claude/rules/naming.md`
  - `@.claude/rules/clients.md`
  - `@.claude/guides/` for team collaboration, state persistence

**Do NOT include:**
- "Current Focus" section (stale)
- Detailed agent protocols (already in guides)
- Full schema details (moving to rules/)
- Work log protocol

### 3. Create Rules Directory

Create: `C:\TheGrantScout\.claude\rules\`

#### 3a. database.md
Extract from old CLAUDE.md:
- Database Schema Quick Reference
- Key table relationships (dim_foundations, fact_grants, dim_grantees, etc.)
- Data conventions (EIN format, tax_year usage, NULL handling)
- Common queries section
- Critical filter fields (only_contri_to_preselected_ind, etc.)

#### 3b. reports.md
Extract from old CLAUDE.md:
- Report Quality Criteria
- Required Elements checklist
- Quality Checks Before Delivery
- What Makes a Bad Report
- What Clients Value

#### 3c. naming.md
Extract from old CLAUDE.md:
- Document Naming Convention: `DOCTYPE_YYYY-MM-DD_description.ext`
- DOCTYPE Categories (with full taxonomy)
- Document Types (SPEC, PROMPT, REPORT, OUTPUT, etc.)
- Examples

#### 3d. clients.md
Extract from old CLAUDE.md:
- Beta Testers (BG1) list
- Beta Group 2 info
- Key Feedback Quotes
- Three Customer Types (calendar model, consolidated format, relationship building)

---

## Outputs

1. `C:\TheGrantScout\.claude\1. Enhancements\Enhancements 2025-12-16\CLAUDE_old.md` (backup)
2. `C:\TheGrantScout\.claude\CLAUDE.md` (new, ~100 lines)
3. `C:\TheGrantScout\.claude\rules\database.md`
4. `C:\TheGrantScout\.claude\rules\reports.md`
5. `C:\TheGrantScout\.claude\rules\naming.md`
6. `C:\TheGrantScout\.claude\rules\clients.md`

---

## Deliverables

- All 6 files created
- Brief REPORT confirming what was moved where
- Note any content from old file that was intentionally dropped (and why)
