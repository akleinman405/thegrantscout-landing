# REPORT: CLAUDE.md Recommendations for TheGrantScout

**Date:** 2025-12-16
**Prepared by:** Claude Code CLI
**Current File:** `C:\TheGrantScout\.claude\CLAUDE.md`
**Current Length:** ~400 lines

---

## Executive Summary

TheGrantScout's CLAUDE.md is comprehensive but **too long** (400 lines vs. recommended 50-100). Much content is valuable but belongs in separate reference files. Key recommendations:

1. **Reduce core file to ~100 lines** - Move detailed content to `.claude/rules/` or referenced docs
2. **Add emphasis markers** - Critical rules need "IMPORTANT:" prefix
3. **Remove outdated sections** - "Current Focus (Week of 2025-12-05)" is stale
4. **Leverage existing docs** - Reference the many guides already in `.claude/`

---

## Current File Analysis

### Strengths (Keep)

| Section | Lines | Assessment |
|---------|-------|------------|
| Project Overview | 15 | Excellent - concise, clear value prop |
| Environment | 20 | Essential - DB connection, OS info |
| Key File Paths | 10 | Good - but could be shorter |
| Quick Reference | 10 | Excellent - scannable metrics |
| Known Gotchas | 25 | High value - prevents repeated errors |
| Data Conventions | 10 | Good - prevents data handling errors |

### Weaknesses (Change or Move)

| Section | Lines | Issue | Recommendation |
|---------|-------|-------|----------------|
| Current Focus | 10 | **Stale** (Dec 5) | Remove or use STATUS_current.md |
| Database Schema | 30 | Too detailed | Move to `@rules/database.md` |
| Common Queries | 30 | Task-specific | Move to `@rules/queries.md` |
| 10-Signal Algorithm | 20 | Reference only | Keep summary, link to full spec |
| Beta Testers | 40 | Changes frequently | Move to client tracking doc |
| Report Quality | 25 | Task-specific | Move to `@rules/reports.md` |
| Document Naming | 35 | Detailed taxonomy | Move to `@rules/naming.md` |
| Work Log Protocol | 20 | Process doc | Move to guide file |
| Agent Protocols | 30 | Advanced usage | Already in TEAM_COLLABORATION_GUIDE.md |
| Folder Structure | 25 | Reference | Keep abbreviated version |

### Missing (Add)

| Element | Why Needed |
|---------|------------|
| **IMPORTANT markers** | Critical rules get lost in text |
| **Semantic embeddings reference** | New major capability |
| **Updated table counts** | Quick Reference shows old numbers |
| **Rules directory structure** | Leverage .claude/rules/ pattern |

---

## Proposed Structure

### New Core CLAUDE.md (~100 lines)

```markdown
# CLAUDE.md - TheGrantScout

**Purpose:** Context for Claude Code CLI. For full docs: See `.claude/guides/`

---

## Project Overview

TheGrantScout helps nonprofits find foundations most likely to fund them.

**Core Promise:** "Your mission deserves funding. We'll help you find it."

---

## Quick Reference

| Item | Value |
|------|-------|
| Foundations in DB | 143,184 |
| Historical grants | 8.3M |
| Semantic embeddings | 9.2M |
| Data years | 2016-2024 |
| Primary schema | f990_2025 |
| DB Host | 172.26.16.1:5432 |

---

## Environment

- **OS:** Windows 11 (forward slashes work in Python)
- **Database:** PostgreSQL on WSL2
- **Python:** 3.11+ (psycopg2, pandas, sentence-transformers)
- **Credentials:** `C:\TheGrantScout\1. Database\Postgresql Info.txt`

```python
import psycopg2
conn = psycopg2.connect(
    host='172.26.16.1', port=5432, database='postgres',
    user='postgres', password='<see Postgresql_Info.txt>'
)
```

---

## Critical Rules

**IMPORTANT - Database:**
- Always use schema prefix: `f990_2025.table_name`
- Use `foundation_ein` not `filer_ein` in fact_grants
- EINs are VARCHAR (preserve leading zeros, no dashes)

**IMPORTANT - Data Quality:**
- `only_contri_to_preselected_ind = FALSE` means open to applications
- Filter websites: exclude "N/A", "NONE", "0" values
- Use `tax_year` for temporal analysis (grant dates often NULL)

**IMPORTANT - Files:**
- Follow naming: `DOCTYPE_YYYY-MM-DD_description.ext`
- Output files go in same folder as prompt unless specified

---

## Key Paths

| Item | Path |
|------|------|
| Database credentials | `1. Database\Postgresql Info.txt` |
| Matching algorithm | `matching_algorithm.py` |
| Embeddings scripts | `1. Database\4. Semantic Embeddings\` |
| Client questionnaires | `2. Clients\Questionnaires\` |

---

## Gotchas

| Issue | Solution |
|-------|----------|
| XML namespace fails | Use `safe_xpath()` with both paths |
| COPY schema error | SET search_path first |
| Duplicate XMLs | Check processed_xml_files table |
| Schema drop danger | Always `drop_existing=False` |

---

## See Also

- `@.claude/rules/database.md` - Schema details, common queries
- `@.claude/rules/reports.md` - Report quality criteria
- `@.claude/rules/naming.md` - DOCTYPE taxonomy
- `@.claude/guides/` - Team collaboration, state persistence

---

## Changelog

| Date | Changes |
|------|---------|
| 2025-12-16 | v3.0 - Restructured per best practices |
| 2025-12-05 | v2.0 - Added schema, gotchas, beta context |
| 2025-12-01 | v1.0 - Initial version |
```

---

## New Rules Files

### `.claude/rules/database.md`

Move from current CLAUDE.md:
- Database Schema (Quick Reference)
- Key Relationships
- Data Conventions
- Common Queries
- Critical Filter Fields

### `.claude/rules/reports.md`

Move from current CLAUDE.md:
- Report Quality Criteria
- Required Elements checklist
- Quality Checks Before Delivery
- What Makes a Bad Report
- What Clients Value

### `.claude/rules/naming.md`

Move from current CLAUDE.md:
- Document Naming Convention
- DOCTYPE Categories
- Document Types (SPEC, PROMPT, REPORT, OUTPUT)
- Examples

### `.claude/rules/clients.md`

Move from current CLAUDE.md:
- Beta Testers (BG1)
- Beta Group 2
- Key Feedback Quotes
- Three Customer Types

---

## Specific Changes Summary

### Remove Entirely

| Section | Reason |
|---------|--------|
| Current Focus (Week of 2025-12-05) | Stale, use STATUS_current.md |
| Work Log Protocol | Duplicates existing guides |
| Agent Protocols | Already in TEAM_COLLABORATION_GUIDE.md |
| Scope Assessment table | Too detailed for core file |
| Code Requirements | Standard practice, not project-specific |

### Add

| Element | Content |
|---------|---------|
| IMPORTANT markers | Prefix critical rules |
| Embeddings reference | New 9.2M embedding capability |
| Updated counts | 143K foundations, 8.3M grants |
| Rules directory imports | `@.claude/rules/` references |

### Keep (Condensed)

| Section | Change |
|---------|--------|
| Project Overview | Keep as-is |
| Quick Reference | Update numbers |
| Environment | Keep as-is |
| Key File Paths | Abbreviate paths |
| Gotchas | Keep top 5-6 only |

---

## Implementation Steps

1. **Create `.claude/rules/` directory**
2. **Extract database.md** from current schema/queries sections
3. **Extract reports.md** from quality criteria sections
4. **Extract naming.md** from DOCTYPE sections
5. **Extract clients.md** from beta tester sections
6. **Rewrite core CLAUDE.md** using proposed structure above
7. **Update Quick Reference** with current metrics
8. **Add IMPORTANT markers** to critical rules
9. **Test** with a few prompts to verify Claude follows new structure

---

## Expected Benefits

| Metric | Before | After |
|--------|--------|-------|
| Core file length | ~400 lines | ~100 lines |
| Context efficiency | Low (much ignored) | High (all relevant) |
| Maintenance burden | High (one big file) | Low (modular) |
| Instruction adherence | Variable | Improved (emphasis markers) |
| Staleness risk | High (current focus section) | Low (removed) |

---

## Questions for Human Review

1. **Should beta tester info stay in core file?** It changes frequently but is often relevant.
2. **Create rules directory?** Requires new folder structure.
3. **Update via PR or direct edit?** Version control consideration.
4. **Which gotchas are highest priority?** Current list has 7+, recommend top 5.

---

*Generated by Claude Code CLI on 2025-12-16*
