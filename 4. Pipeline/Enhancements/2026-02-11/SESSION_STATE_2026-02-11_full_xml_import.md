# SESSION STATE: Full XML Import Pipeline - All Fields from IRS 990 XML into PostgreSQL

**Last Updated:** 2026-02-11 20:00
**Working Folder:** `1. Database/1. Import F990/F990-2025/1. Import/`
**Status:** Complete

---

## RESUME POINT (Read This First)

### Do This Next
The full XML import pipeline is **complete**. All major work is done. Only minor cleanup remains:

1. **Drop np_revenue_detail table** - Empty dead table with no parser code. Run: `DROP TABLE f990_2025.np_revenue_detail;`
2. **Phase 7: Column reference docs** - Generate md + docx documentation for all new/modified tables
3. **Optional:** Improve checkpoint system to XML-level tracking (prevents dupes on future mid-ZIP restarts)

### Remaining Steps
1. Drop np_revenue_detail dead table
2. Generate column reference documentation for new tables
3. Optional: Improve checkpoint/resume system

---

## What's Done
- **Phase 0:** Disk cleanup (~28GB freed)
- **Phase 1:** XML field discovery (cataloged all elements across 1,200+ sample files)
- **Phase 2:** Schema design - `migration_full_xml_import.sql` executed (35+ new pf_returns cols, 36+ new nonprofit_returns cols, 15 new tables)
- **Phase 3:** Shared `xml_utils.py` + updated parsers (parse_990pf.py, parse_990.py, parse_990ez.py)
- **Phase 4:** Schedule parsers created (parse_schedules.py: Schedule I, D, F, R, J, O, A)
- **Phase 5:** Import orchestrator updated (import_f990.py: schedule detection, 15 new insert methods, --schedules flag)
- **Phase 6:** Import complete. All 12 ZIPs processed (728,719 XML files). 610,995 returns, 0 failures.
- **Backfill 01A-03A:** Combined script fixed 3 parser bugs: 11,195 contractors + 42,279 PF officers + 34,849 balance sheet rows, 0 errors
- **Deduplication:** Removed 47,907 duplicate parent rows + ~1.85M cascaded child rows from ZIP 04A mid-restart. Zero duplicates remain.
- **Validation:** All queries passed. Report: `REPORT_2026-02-11.2_import_validation.md`
- **3 parser bugs fixed:**
  - parse_990pf.py: Officer container XPath `OfficerDirTrstKeyEmplInfoGrp` -> `OfficerDirTrstKeyEmplInfoGrp/OfficerDirTrstKeyEmplGrp`
  - parse_990.py: Balance sheet `LandBldgEquipCostOrOtherBssAmt` -> `LandBldgEquipBasisNetGrp`
  - parse_schedules.py: Schedule J `BonusFilingOrganizationAmount` -> `BonusFilingOrganizationAmt`
- **manage_import.sh** CLI, signal handling, verification agents all complete

## What's Partially Done
- Nothing partially done - all phases complete

## What's Not Started
- Phase 7: Column reference documentation (md + docx for all new tables)
- Drop np_revenue_detail dead table
- Optional: Improve checkpoint system to XML-level tracking

---

## Decisions Made

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Import 2024 TEOS data only | Re-import all 2019-2025 data | Disk space, time; legacy data has most fields already |
| ZIP-level checkpointing | XML-level tracking | Simpler implementation; caused dupes on mid-ZIP resume |
| Deferred Schedule B,C,E,G,K,L,M,N | Import all schedules | Low value for grant matching; can add later |
| Combined backfill_01a_03a.py | Separate scripts per bug | One pass through XML = faster, simpler |
| Dedup by keeping highest id | Keep lowest id | Highest id = imported with fixed parser code |
| Kill old import + resume with fixed code | Let old import finish | ZIPs 04A-12A get correct data immediately |

---

## What Was Tried (Failed Approaches)

| Approach | Why It Failed | Lesson |
|----------|--------------|--------|
| Graceful stop (SIGINT) on running process | Process loaded old code without signal handler | Must kill and restart to pick up code changes |
| formation_yr XPath in 990-PF | Element doesn't exist in 990-PF XML | formation_yr is in BMF, not 990-PF filings |
| mission_desc / primary_exempt_purpose on pf_returns | These are 990/990-EZ elements, not 990-PF | 0% on pf_returns is expected |
| MCP tool for multi-query validation | Timeout on large queries (611K rows) | Use psql via Bash for heavy queries |

---

## Files Created/Modified

| File | Status | Description |
|------|--------|-------------|
| `1. Import/xml_parsers/xml_utils.py` | Created | Shared XPath utilities |
| `1. Import/xml_parsers/parse_990pf.py` | Modified | +35 fields, officer XPath fix |
| `1. Import/xml_parsers/parse_990.py` | Modified | +30 fields, LandBldgEquip fix |
| `1. Import/xml_parsers/parse_990ez.py` | Modified | +applicable fields |
| `1. Import/xml_parsers/parse_schedules.py` | Created | Schedule I, D, F, R, J, O, A |
| `1. Import/import_f990.py` | Modified | 15 new insert methods, schedule detection, signal handling |
| `1. Import/migration_full_xml_import.sql` | Created | Schema migration (ALTER + CREATE) |
| `1. Import/manage_import.sh` | Created | CLI: start/stop/status/resume/tail/backfill/validate |
| `1. Import/backfill_01a_03a.py` | Created | Combined backfill for 3 bugs in ZIPs 01A-03A |
| `1. Import/validate_import.sql` | Modified | Fixed median/round syntax |
| `1. Import/config.yaml` | Modified | Added schedule_mode, new table configs |
| `REPORT_2026-02-11.2_import_validation.md` | Created | Final validation report with dedup results |

---

## Database Changes Made

- **15 new tables** created via migration_full_xml_import.sql
- **~70 new columns** added to pf_returns, nonprofit_returns, officers, pf_grants
- **18.6M total new rows** across all tables (after deduplication)
- **Deduplication:** Removed 47,907 duplicate parent rows + ~1.85M cascaded child rows

### Final Table Counts (post-dedup)

| Table | Records |
|-------|---------|
| pf_returns | 638,082 |
| nonprofit_returns | 2,956,959 |
| officers | 26,281,615 |
| pf_grants | 1,758,527 |
| schedule_i_grants | 996,940 |
| pf_capital_gains | 3,740,163 |
| schedule_o_narratives | 2,950,168 |
| np_balance_sheet | 2,717,584 |
| pf_investments | 1,844,771 |
| pf_revenue_expenses | 1,353,353 |
| schedule_r_related_orgs | 850,773 |
| pf_balance_sheet | 679,634 |
| schedule_a | 574,037 |
| np_functional_expenses | 360,191 |
| schedule_j_compensation | 286,308 |
| contractors | 107,020 |
| schedule_f_grants | 81,561 |
| schedule_d_endowments | 36,936 |

---

## Reports Created

| File | Description |
|------|-------------|
| `4. Pipeline/Enhancements/2026-02-11/REPORT_2026-02-11.2_import_validation.md` | Full validation report with table counts, field population rates, spot checks, backfill results, and deduplication results |

---

## Database Queries That Worked

```sql
-- Dedup pf_returns (keep highest id per EIN+tax_year)
DELETE FROM f990_2025.pf_returns
WHERE id IN (
    SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY ein, tax_year ORDER BY id DESC) as rn
        FROM f990_2025.pf_returns WHERE source_file LIKE '2024_TEOS%'
    ) sub WHERE rn > 1
);

-- Verify zero duplicates remain
SELECT count(*) as total, count(DISTINCT (ein, tax_year)) as unique_pairs,
       count(*) - count(DISTINCT (ein, tax_year)) as remaining_dupes
FROM f990_2025.pf_returns WHERE source_file LIKE '2024_TEOS%';

-- Count cascade impact before dedup
WITH pf_dupes AS (
    SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY ein, tax_year ORDER BY id DESC) as rn
        FROM f990_2025.pf_returns WHERE source_file LIKE '2024_TEOS%'
    ) sub WHERE rn > 1
)
SELECT 'pf_grants' as child_table, count(*) as rows_to_cascade
FROM f990_2025.pf_grants WHERE return_id IN (SELECT id FROM pf_dupes);
```

---

## Key Data Findings

- **728,719 total XML files** across 12 ZIPs, 610,995 returns imported (after dedup: 126,366 PF + 574,037 NP)
- **Schedule I grants: 996,940 records** from 48,092 public charity grantmakers. 94.1% have recipient EIN (vs 0% for 990-PF grants).
- **Backfill improved PF officers** from 1.0 to 3.3 per return for ZIPs 01A-03A
- **Top foundations confirmed:** Gates ($77B), Lilly ($62B), Wellcome ($49B), Ford ($17B)
- **Top Schedule I grantmakers:** Fidelity Charitable ($115B), Schwab ($55B), National Philanthropic Trust ($23B)
- **62.3% population rate** for governance fields on nonprofit_returns exactly matches Form 990 share (990-EZ doesn't have these fields)
- **Dedup removed ~1.9M total rows** (47K parents + 1.85M cascaded children) - mostly from ZIP 04A mid-restart

---

## Blockers (if any)

None - all work complete.

---

*Generated by Claude Code on 2026-02-11 20:00*
