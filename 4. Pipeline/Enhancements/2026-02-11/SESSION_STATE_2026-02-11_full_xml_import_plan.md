# SESSION STATE: Comprehensive IRS 990 XML "All Fields" Import Plan

**Last Updated:** 2026-02-11
**Purpose:** Plan to build a script that imports ALL fields from IRS 990 XML files into PostgreSQL
**Status:** Plan complete, pending user approval on scope (disk space constraint)

---

## CURRENT STATUS - WHERE WE ARE

### What Happened This Session
We did extensive research and planning to design a system that imports literally every field from IRS Form 990, 990-PF, 990-EZ XML files and all attached schedules (A through R) into the existing PostgreSQL database.

### The Plan File
**The complete plan is at:** `/Users/aleckleinman/.claude/plans/calm-finding-matsumoto.md`

This file contains:
- 10 implementation phases (0-9)
- Every new table with columns, data types, and XPaths
- Every ALTER TABLE change for existing tables
- Corrections from two verification agents that checked the plan against real XML data
- Prioritized as P1 (critical), P2 (medium), P3 (low value)

### What Needs to Happen Next
1. **Resolve disk space constraint** - Only 7.1GB free on disk, DB is 13GB. P1 alone needs ~2GB, full import needs ~5GB.
   - Options: do P1 only, free up space first, or use external storage
   - `calc_foundation_avg_embedding` (803MB) may be droppable since embeddings were archived
   - Old raw ZIP files (2019-2021) could be moved off disk
2. **Approve the plan** - User needs to review and approve before coding begins
3. **Run Phase 0** - XML element catalog script (not yet run - agent couldn't execute in plan mode)
4. **Begin Phase 1** - Schema design (CREATE/ALTER TABLE SQL)

---

## What's Done

- Explored all existing parsers: `parse_990pf.py`, `parse_990.py`, `parse_990ez.py` at `1. Database/1. Import F990/F990-2025/1. Import/xml_parsers/`
- Explored existing schema: `schema.sql` (6 tables: pf_returns, nonprofit_returns, pf_grants, officers, schedule_a, import_log)
- Read and analyzed the column reference document format (`2. Docs/pf_returns_column_reference.md` and docx generation scripts)
- Comprehensive web research on IRS 990 XML schemas, all schedules A-R, open source tools (IRSx, Master Concordance File, Giving Tuesday parsers)
- Designed complete schema with all tables, columns, XPaths
- Two verification agents checked plan against 200+ real 990-PF XMLs and 7 richly-scheduled 990 XMLs
- All verification corrections incorporated into plan appendix

## What's NOT Done

- Phase 0: XML element catalog script (needs to be run)
- All coding (Phases 1-6)
- Import execution (Phase 7)
- Validation (Phase 8)
- Documentation generation (Phase 9)

---

## Key Decisions Made

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Use normalized tables for 990-PF Part I (revenue/expenses) and Part II (balance sheet) | Flat columns (90+ columns added to pf_returns) | Part I has 4 columns per line item (30 lines x 4 = 120 fields). Normalized = ~3 columns + line_item key. Cleaner, more maintainable. |
| Prioritize Schedule I grants as #1 new data source | Could start with any schedule | Schedule I contains domestic grants from public charities - could add 500K-1M grant records, complementing the 8.3M from 990-PF |
| Target 2024 TEOS ZIP files (12 files, ~4.4GB) | Could do 2023 or all years | 2024 is the most recent complete year of XML data on disk |
| Skip 990-T parsing | Could include it | 990-T has unrelated business income, no grant data - low value for grant matching |

## Verification Agent Findings (Critical Fixes in Plan)

6 XPath errors found that would cause silent data loss:
1. `membership_dues_amt`: Plan had wrong XPath (`AllOtherContributionsAmt`), correct is `MembershipDuesAmt`
2. `schedule_i_grants.recipient_ein`: Plan had `EINOfRecipient`, correct is `RecipientEIN`
3. `pension_plan` in functional expenses: Plan had `PensionPlanAccrualsGrp`, correct is `PensionPlanContributionsGrp`
4. Investment schedules live at `ReturnData/*` level, OUTSIDE `IRS990PF` element
5. Schedule R only extracted Part II, needs Parts I, IV, V, VI too
6. Several element name mismatches for lobbying and fundraising indicators

Also found missing high-value fields:
- `Organization501c3Ind` (critical for distinguishing charities)
- `GrantsToOrganizationsInd` (identifies public charity grantmakers)
- All prior-year (PY) amounts for trend analysis
- `FinalReturnInd` / `InitialReturnInd` (lifecycle indicators)
- `GrantOrContriApprvForFutGrp` (grants approved for future, not just paid)

All corrections are documented in the plan file's Appendix section.

---

## Key Files

| File | Description |
|------|-------------|
| `/Users/aleckleinman/.claude/plans/calm-finding-matsumoto.md` | **THE PLAN** - Complete implementation plan with all tables, columns, XPaths, phases, and verification corrections |
| `1. Database/1. Import F990/F990-2025/1. Import/schema.sql` | Current schema (6 tables) |
| `1. Database/1. Import F990/F990-2025/1. Import/xml_parsers/parse_990pf.py` | Current 990-PF parser (~635 lines) |
| `1. Database/1. Import F990/F990-2025/1. Import/xml_parsers/parse_990.py` | Current 990 parser (~503 lines) |
| `1. Database/1. Import F990/F990-2025/1. Import/xml_parsers/parse_990ez.py` | Current 990-EZ parser (~429 lines) |
| `1. Database/1. Import F990/F990-2025/1. Import/import_f990.py` | Main import orchestrator |
| `1. Database/1. Import F990/F990-2025/1. Import/config.yaml` | Import configuration |
| `2. Docs/pf_returns_column_reference.md` | Template for column reference docs |
| `2. Docs/generate_pf_returns_docx.py` | Template for docx generation |
| `8. Data/raw/` | Raw IRS XML ZIP files (12 for 2024, 12 for 2023, plus older years) |

---

## Database State

- **Schema:** f990_2025
- **DB size:** 13GB
- **Disk free:** 7.1GB (CONSTRAINT)
- **Key table sizes:** officers=4GB, nonprofit_returns=2.7GB, fact_grants=1.8GB, pf_returns=427MB
- **Potentially droppable:** calc_foundation_avg_embedding (803MB, embeddings archived 2026-01-04)

---

## New Tables in Plan (Summary)

**P1 (Critical, ~2GB):**
- `pf_revenue_expenses` - Normalized Part I line items (4 amount columns per line)
- `pf_balance_sheet` - Normalized Part II line items (BOY/EOY/FMV)
- `schedule_i_grants` - PUBLIC CHARITY GRANTS (the big new data source)
- `schedule_d_endowments` - Endowment fund data
- `schedule_f_grants` - Foreign grants
- `schedule_r_related_orgs` - Related organization networks
- Plus ALTER TABLE on pf_returns (~15 cols), nonprofit_returns (~25 cols), pf_grants (2 cols), officers (3 cols)

**P2 (Medium, ~2GB more):**
- `np_balance_sheet` - Form 990 Part X balance sheet detail
- `np_revenue_detail` - Form 990 Part VIII revenue breakdown
- `np_functional_expenses` - Part IX expense breakdown (program/management/fundraising)
- `pf_capital_gains` - Capital gains/losses detail
- `pf_investments` - Investment holdings (stocks, bonds, etc.)
- `schedule_j_compensation` - Detailed compensation
- `schedule_o_narratives` - Supplemental text
- `contractors` - Highest paid contractors

**P3 (Low, ~1GB more):**
- Schedules B, C, E, G, H, K, L, M, N

---

## Web Research Resources Found

- **IRS Master Concordance File:** github.com/Nonprofit-Open-Data-Collective/irs-efile-master-concordance-file (~10K XPaths mapped)
- **IRSx:** github.com/jsfenfen/990-xml-reader + irsx.info (version-aware XPath mappings)
- **IRS Official XSD Schemas:** irs.gov schema pages per tax year
- **Giving Tuesday XML Mapper:** github.com/Giving-Tuesday/form-990-xml-mapper (generates field catalog from XSD)
- **IRS TEOS Dataset Guide:** irs.gov/pub/irs-pdf/p5891.pdf

---

## How to Resume

1. Read this file and the plan file at `/Users/aleckleinman/.claude/plans/calm-finding-matsumoto.md`
2. Resolve disk space question (P1 only vs free space first vs proceed anyway)
3. Approve the plan (or request changes)
4. Begin Phase 0: Run XML element catalog script
5. Begin Phase 1: Write and execute schema SQL (ALTER TABLE + CREATE TABLE)
6. Continue through remaining phases

---

*Generated by Claude Code on 2026-02-11*
