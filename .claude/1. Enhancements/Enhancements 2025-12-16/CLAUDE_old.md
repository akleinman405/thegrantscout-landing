# CLAUDE.md - TheGrantScout Project Context

**Purpose:** Context file for Claude Code CLI sessions. Read this first.

---

## Project Overview

**TheGrantScout** helps nonprofits find foundations and grant opportunities most likely to fund them. We surface funders they didn't already know about and provide intelligence to maximize success.

**Core Promise:** "Your mission deserves funding. We'll help you find it."

**Value Proposition:**
- Discovery of NEW funding sources (not reminders of known ones)
- Comprehensive funder intelligence in one place
- Positioning strategies based on foundation giving patterns
- Time savings vs. weeks of manual research

**For full business context:** See the most current `THEGRANTSCOUT_SUMMARY yyyy-mm-dd` located here: "C:\TheGrantScout"

---

## Current Focus (Week of 2025-12-05)

- Finishing Round 2 beta reports for BG1
- Grant purpose text parser bug fix (wrong XPath)
- Enhance CLAUDE.md with domain context
- Follow up with VetsBoats/Matt Gettleman
- Next: Horizons National first report

**Current status file:** `STATUS_current.md`

---

## Key File Paths

| Item | Path |
|------|------|
| Database credentials | `C:\TheGrantScout\1. Database\Postgresql Info.txt` |
| Schema definition | `C:\TheGrantScout\1. Database\F990-2025\schema.sql` |
| Matching algorithm | `C:\TheGrantScout\matching_algorithm.py` |
| Import scripts | `C:\TheGrantScout\1. Database\F990-2025\1. Import\` |
| Beta questionnaires | `C:\TheGrantScout\2. Clients\Questionnaires\` |
| Report templates | `C:\TheGrantScout\3. Reports\Templates\` |

---

## Database Schema (Quick Reference)

### Core Tables (f990_2025 schema)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| pf_returns | Private foundation 990-PF filings | ein, business_name, state, total_assets_eoy_amt, grants_to_organizations_ind, only_contri_to_preselected_ind |
| pf_grants | Individual grant records | filer_ein, recipient_name, recipient_state, amount, purpose, tax_year |
| nonprofit_returns | 990/990-EZ filings | ein, organization_name, state, total_revenue, mission_description, ntee_code |
| officers | Board/officers from all forms | ein, person_nm, title_txt, compensation_amt |
| schedule_a | Charity classifications | ein, public_charity_509a1_ind, supporting_org_509a3_ind |
| import_log | ETL tracking | import_run_id, status, records_success, records_failed |

### Key Relationships
- `pf_grants.return_id` → `pf_returns.id` (CASCADE delete)
- `pf_grants.filer_ein` → `pf_returns.ein`

### Data Conventions
- **Amounts:** NUMERIC(15,2) - dollars with cents, NULL = not reported
- **Dates:** YYYY-MM-DD (ISO 8601)
- **EINs:** VARCHAR(20) - preserves leading zeros, no dashes
- **Booleans:** TRUE/FALSE/NULL (NULL = not applicable)

### Critical Filter Fields
- `grants_to_organizations_ind = TRUE` → Makes grants to orgs
- `only_contri_to_preselected_ind = FALSE` → Open to applications (KEY!)

**Full schema:** See `SCHEMA_SUMMARY.md`

---

## Environment

- **OS:** Windows 11 (use backslashes in paths, or forward slashes in Python)
- **Database:** PostgreSQL on WSL2 (Host: 172.26.16.1, Port: 5432)
- **Python:** 3.11+
- **Key packages:** psycopg2, pandas, lxml

### Database Connection Pattern

```python
import psycopg2

db_conn = psycopg2.connect(
    host='172.26.16.1',
    port=5432,
    database='postgres',
    user='postgres',
    password='<see Postgresql_Info.txt>'
)
```

---

## Known Gotchas

| Issue | Details | Solution |
|-------|---------|----------|
| **XML Element Names** | Parser used wrong element (`PurposeOfGrantTxt`) vs IRS actual (`GrantOrContributionPurposeTxt`) | Verify XPath against actual XML samples before implementing |
| **IRS XML Namespace** | Direct XPath fails without namespace | Use `safe_xpath()` with both namespaced and non-namespaced paths |
| **Duplicate XMLs** | Same files in multiple IRS ZIPs cause UNIQUE violations | Track in `processed_xml_files` table, skip duplicates |
| **Schema Drop Danger** | `create_schema()` drops tables by default | Always use `drop_existing=False` for incremental imports |
| **Website Placeholders** | 79.6% have "website" but only 15.6% are real URLs | Filter out "N/A", "NONE", "0" values |
| **Recipient EINs Missing** | 990-PF forms often omit recipient EINs | Requires external enrichment (ProPublica API) |
| **Grant Dates Sparse** | Many grants have NULL dates | Use `tax_year` for temporal analysis instead |

### Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `UNIQUE constraint on filename` | Duplicate XML in ZIP | Use processed_xml_files tracking |
| `ET.ParseError: malformed XML` | Corrupted file | Catch, log warning, skip file |
| `Database connection refused` | PostgreSQL not running | Check WSL2 service is up |
| `NULL purpose text (0%)` | Wrong XPath | Use `GrantOrContributionPurposeTxt` |

**Full gotchas list:** See `OUTPUT_GOTCHAS.md`

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
SELECT recipient_name, recipient_state, amount, purpose, tax_year
FROM f990_2025.pf_grants
WHERE filer_ein = '123456789'
ORDER BY tax_year DESC, amount DESC;
```

### Check field population rates
```sql
SELECT
    'purpose' as field,
    COUNT(*) as total,
    COUNT(purpose) as populated,
    ROUND(100.0 * COUNT(purpose) / COUNT(*), 1) as pct
FROM f990_2025.pf_grants;
```

---

## 10-Signal Scoring Algorithm

| Signal | Points | Description |
|--------|--------|-------------|
| Prior Relationship | 40 | Has foundation funded this nonprofit before? |
| Geographic Match | 15 | In-state funding preference (3-5x more likely) |
| Grant Size Alignment | 12 | Typical grant size matches nonprofit's ask? |
| Repeat Funding Rate | 10 | Does foundation favor existing grantees? |
| Portfolio Concentration | 8 | How focused on specific sectors? |
| Purpose Text Match | 5 | Semantic similarity to past grant purposes |
| Recipient Validation | 4 | Foundation's grantee quality patterns |
| Foundation Size | 3 | Capacity to fund at requested level |
| Regional Proximity | 2 | Cross-state giving corridors |
| Grant Frequency | 1 | Active vs. sporadic grantmaker |

**Total Possible Score:** 100 points

---

## Beta Testers (BG1)

| Code | Organization | Sector | Geography | Status |
|------|--------------|--------|-----------|--------|
| SNS | Senior Network Services | Senior services | California | Report 1 delivered, errors found |
| PSMF | Patient Safety Movement Foundation | Healthcare education | National/Global | Wants foundation-focused reports |
| RHF | Retirement Housing Foundation | Senior housing | Multi-state | Values organization/reminders |
| KU | Ka Ulukoa | Youth athletics | Hawaii | Report 2 held (deadline issue) |
| ACA | Arborbrook Christian Academy | K-12 athletics | North Carolina | Awaiting feedback |

### Beta Group 2

| Code | Organization | Contact | Status |
|------|--------------|---------|--------|
| HN | Horizons National | Alex Hof | Form filled, ready for first report |

### What Clients Value
- **Discovery:** Finding NEW foundations (not ones they already know)
- **Fit:** Clear explanation of WHY this foundation matches their work
- **Actionability:** Contact info, deadlines, recent similar grants
- **Organization:** Info in one place, even if they knew some opportunities

### What Makes a Bad Report
- Wrong grant names (CSNSGP = Security, not Nutrition/Services)
- Expired deadlines included (AAA RFP from Jan 2025)
- Broken links (NCOA grants page)
- Foundations they already have relationships with
- Foundations that don't fund their geography
- Foundations inactive for 3+ years

### Key Feedback Quotes

**Mariam (SNS):** "The way you broke down the work ensures no action is overlooked." Suggested annual calendar with selective alerts. Only 1 of 5 opps was truly new. Asked about grant writing concierge tier.

**Andy (RHF):** Info organized in one place was valuable even though he knew most opportunities. Validates "calendar manager" use case.

**Consuelo (PSMF):** Multi-mission orgs need foundation-first approach. Prefers ~5 foundations with relationship-building info. Fellowship Program is priority target. Interested in political/family foundation connections.

---

## Report Quality Criteria

### Required Elements (Every Report)
- [ ] Each match includes: foundation name, EIN, assets, location
- [ ] Each match includes: 2-3 recent similar grants with amounts
- [ ] Each match includes: contact info or application URL
- [ ] No foundations from client's existing relationships
- [ ] All foundations have given grants in past 3 years
- [ ] All deadlines are current (not expired)
- [ ] All links verified working

### Quality Checks Before Delivery
- [ ] Spell-check completed
- [ ] Dollar amounts formatted consistently ($X,XXX)
- [ ] No duplicate foundations within report
- [ ] Grant examples are relevant to client's focus areas
- [ ] Grant names are accurate (verify against source)

---

## Document Naming Convention

### Format
```
DOCTYPE_YYYY-MM-DD[.version]_description.ext
```

- **version** = order of that file type on that day (e.g., `.1`, `.2` for multiple PROMPTs on same day)
- Version is optional if only one file of that type exists for that date

### Examples
- `REPORT_2025-12-05_beta_feedback_summary.md`
- `SPEC_2025-11-17.1_opportunity_matcher.md` (first SPEC on Nov 17)
- `PROMPT_2025-12-05.1_schema_gathering.md` (first PROMPT on Dec 5)
- `PROMPT_2025-12-05.2_validation_check.md` (second PROMPT on Dec 5)

### DOCTYPE Categories

| Type | Direction | Purpose |
|------|-----------|---------|
| SPEC | Input → Agent | Requirements, specifications |
| PROMPT | Input → Agent | Instructions for Claude |
| TASK | Input → Agent | Assigned work items |
| REPORT | Agent → Output | Analysis, findings, summaries |
| OUTPUT | Agent → Output | Deliverables, generated content |
| LOG | Agent → Output | Activity logs, status updates |
| DATA | Bidirectional | Data files, exports |
| README | Reference | Project/folder documentation (standard convention) |
| QUICKSTART | Reference | Getting started guides |

---

## Document Types (DOCTYPE)

### SPEC (Specification)
- Requirements documents
- Algorithm specifications
- API contracts
- **Required sections:** Overview, Requirements, Acceptance Criteria

### PROMPT
- Instructions for Claude Code CLI
- Task assignments
- **Required sections:** Context, Task, Expected Output

### REPORT
- Analysis findings
- Status updates
- Research summaries
- **Required sections:** Executive Summary, Findings, Recommendations

### OUTPUT
- Generated deliverables
- Client-facing documents
- **Required sections:** Varies by deliverable type

---

## Work Log Protocol

Every session should update `WORK_LOG.md`:

```markdown
## YYYY-MM-DD HH:MM - [Agent/Human]

### Completed
- [What was done]

### In Progress
- [What's partially done]

### Blocked
- [What's waiting on something]

### Next Steps
- [What should happen next]
```

**Why:** Enables session continuity. New sessions can pick up where previous left off.

---

## Agent Protocols

### Two-Agent Review Process

1. **Agent 1:** Creates deliverable
2. **Agent 2:** Reviews against criteria, creates `PROMPT_REVIEWED` output
3. **Human:** Final approval before client delivery

### Scope Assessment

Before starting work, assess complexity:

| Complexity | Tool Calls | Time Estimate | Action |
|------------|------------|---------------|--------|
| Simple | <10 | <30 min | Proceed |
| Medium | 10-20 | 1-2 hours | Proceed with updates |
| Complex | 20+ | Half day+ | **Stop and confirm with human** |

### Code Requirements

All code must be tested before committing:
- Unit tests for new functions
- Integration test for database operations
- Manual verification of outputs

---

## Folder Structure Reference

```
C:\TheGrantScout\
├── .claude\
│   └── CLAUDE.md (this file)
├── 1. Database\
│   ├── F990-2025\
│   │   ├── 1. Import\
│   │   └── 2. Import review + fixes\
│   ├── Postgresql_Info.txt
│   └── DATA_DICTIONARY.md
├── 2. Clients\
│   ├── BG1\ (Beta Group 1)
│   ├── BG2\ (Beta Group 2)
│   └── Questionnaires\
├── 3. Reports\
│   ├── Templates\
│   └── Delivered\
├── 4. Research\
│   └── Lessons-learned\
└── 5. Website\
```

---

## Preferences

- **Response length:** Brief unless asked for detail
- **Output format:** Downloadable .md files in `/mnt/user-data/outputs/`
- **Confirmations:** Confirm before writing long documents (bullet what you'll cover)
- **Recommendations:** Answer the question asked; don't add extras unless requested

---

## Quick Reference

| Item | Value |
|------|-------|
| Foundations in DB | 85,470 |
| Historical grants | 1,624,501 |
| Data years | 2016-2024 |
| Target price | ~$100/mo (founding rate) |
| Primary schema | f990_2025 |
| DB Host | 172.26.16.1:5432 |

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-05 | 2.0 | Added: Schema reference, Gotchas, Beta tester context, Report quality criteria, 10-signal algorithm, Common queries. Reorganized per feedback recommendations. |
| 2025-12-01 | 1.0 | Initial version with DOCTYPE taxonomy, work log protocol, agent protocols |
