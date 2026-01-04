# Known Gotchas & Common Errors

**Generated:** 2025-12-05
**Purpose:** Document known issues, bugs, fixes, and lessons learned for CLAUDE.md

---

## Known Gotchas

| Issue | Details | Solution |
|-------|---------|----------|
| **XML Element Name Mismatch** | 990-PF parser used wrong element names (`PurposeOfGrantTxt`) instead of IRS actual element (`GrantOrContributionPurposeTxt`) | Always verify XML element names against actual IRS data samples before implementing parsers |
| **IRS XML Namespace Handling** | IRS XML files use the `http://www.irs.gov/efile` namespace. Direct XPath queries fail without namespace prefixes | Use `safe_xpath()` helper that tries both namespaced and non-namespaced paths |
| **IRS Republishes Same XMLs** | Same XML files appear in multiple IRS ZIP archives, causing UNIQUE constraint violations | Track processed files in `processed_xml_files` table, skip duplicates |
| **Schema Drop Protection** | `create_schema()` by default drops and recreates tables - can wipe entire database during incremental runs | Always pass `drop_existing=False` for incremental imports; require explicit confirmation for rebuilds |
| **Website URL Placeholders** | Many 990-PF "website" values are placeholders like "N/A", "NONE", "0" | Filter placeholders when using website URLs; only ~15.6% have real URLs |
| **Duplicate IRS BMF Tables** | irs_bmf_eo1 through eo4 are exact duplicates of irs_bmf data | Use only `irs_bmf`; delete eo1-eo4 tables |
| **historical_grants Date Range** | Data dictionary says 2016-2024 but table only has 2024 data | grants_paid has 2016-2023; need to merge or document separately |
| **officers_directors Undocumented** | 13.4M row table not in data dictionary | Document and determine relationship to board_members |
| **SAM.gov Rate Limits** | API returns 429 errors with rate limiting | Implement backoff/retry logic; wait and retry later |
| **Import Checkpoint Files** | Checkpoint only works if using same config.yaml between runs | Delete checkpoint.json to start fresh if config changed |
| **Beta Tester Report Errors** | SNS found wrong grant name, expired deadline, broken links in report | Validate grant data before sending; check deadline dates; verify URLs |
| **NTEE Codes Stored as Text** | ntee_codes and program_areas stored as text instead of arrays | Consider migration to proper array types |

---

## Common Errors & Fixes

| Error Message | Cause | Fix |
|--------------|-------|-----|
| `UNIQUE constraint violation on filename` | IRS ZIP files contain duplicate XMLs | Use `processed_xml_files` tracking table; skip already-processed files |
| `ET.ParseError: malformed XML` | Corrupted or invalid XML file in ZIP | Catch `ET.ParseError` separately; log warning and skip file; don't crash batch |
| `ModuleNotFoundError: lxml` | Missing Python dependency | `pip install lxml` or `pip install -r requirements.txt` |
| `Database connection refused` | PostgreSQL not running or wrong host/port | Verify PostgreSQL is running; check `config.yaml` credentials |
| `Table already exists` | Running fresh import on existing schema | Use `--skip-schema` flag or drop schema first |
| `Permission denied on ZIP` | Incorrect file paths in config | Check paths in `config.yaml` match actual file locations |
| `Out of memory` during import | Batch size too large | Reduce `batch_size` in config.yaml (default: 1000) |
| `NULL purpose text` (0% populated) | Parser using wrong XPath for grant purpose | Use `GrantOrContributionPurposeTxt` as primary XPath |
| `KeyError: 'recipient_ein'` | Field doesn't exist in some form versions | Always use `get()` with default or check existence before access |
| `Checkpoint not resuming` | checkpoint.json deleted or corrupted | Delete checkpoint.json and restart from beginning |

---

## Data Quality Notes

### Field Population Rates (f990_2025)

| Field | Source | Population Rate | Notes |
|-------|--------|-----------------|-------|
| total_assets_eoy_amt | pf_returns | 100% | Reliable |
| grant amount | pf_grants | 99.7% | Reliable |
| recipient_name | pf_grants | 100% | Reliable |
| recipient_state | pf_grants | 99.6% | Reliable |
| website_url | pf_returns | 79.6% (15.6% real) | Most are placeholders |
| application_submission_info | pf_returns | 22.4% | Sparse |
| purpose | pf_grants | 100% (after fix) | Was 0% before fix |
| recipient_ein | pf_grants | 0% | Needs enrichment |

### Known Data Issues

1. **Recipient EINs Missing** - 990-PF forms often don't include recipient EINs; requires external enrichment
2. **Grant Dates Sparse** - Many grants have NULL dates; use tax_year for temporal analysis instead
3. **Mission/Purpose Text Quality** - Free text from filings; varies widely in quality and detail
4. **Tax Year Distribution** - 2025 TEOS data heavily weighted to 2023-2024 filings
5. **Activity Codes** - Only 3 activity codes available per foundation; not standardized NTEE

### Database Integrity Notes

1. **Grants Table Relationships** - Three grants tables exist with unclear relationships:
   - `grants_paid` (4.5M rows, 2016-2023) - UNDOCUMENTED
   - `historical_grants` (1.6M rows, 2024) - Production
   - `f990_grants` (1.6M rows) - Source data

2. **Foundation Duplication** - Both `f990_foundations` and `foundations` have same 85,470 EINs:
   - `f990_foundations` = raw IRS source (read-only archive)
   - `foundations` = production table with enrichments

3. **Officer Data Gap** - `officers_directors` (13.4M rows) vs `f990_officers` (41K rows) - 326x difference

---

## IRS Form 990-PF XPath Reference

Critical XML element names for grant extraction:

| Field | Correct XPath | Common Wrong XPath |
|-------|--------------|-------------------|
| Purpose | `GrantOrContributionPurposeTxt` | `PurposeOfGrantTxt`, `GrantPurpose` |
| Amount | `Amt` | `Amount` |
| Recipient Name | `RecipientBusinessName/BusinessNameLine1Txt` | `RecipientName` |
| Recipient EIN | `RecipientEIN` | `EIN` |
| Recipient State | `RecipientUSAddress/StateAbbreviationCd` | `State` |

### Parser Tips

1. **Always use fallback XPaths** - IRS schema evolves; try multiple paths
2. **Handle namespace** - Use `{'irs': 'http://www.irs.gov/efile'}` namespace
3. **Check actual XML samples** - Don't assume element names from documentation
4. **Test with `--sample 5`** - Validate field population before full import
5. **Add post-import validation** - Query field population rates after import

---

## Import Script Safety Checklist

Before running imports:

- [ ] PostgreSQL is running on 172.26.16.1:5432
- [ ] Database credentials verified in config.yaml
- [ ] Source ZIP files accessible at configured paths
- [ ] Schema created with `schema.sql` (for fresh installs)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Test with `--sample 5` first

Before full imports:

- [ ] Backup database: `pg_dump -h 172.26.16.1 -U postgres -d postgres > backup.sql`
- [ ] Verify checkpoint.json doesn't have stale data
- [ ] Check disk space (estimated 3-5 GB for database)
- [ ] Monitor with `tail -f import.log`

---

## Validation Queries

### Check Field Population Rates

```sql
SELECT
    'purpose' as field,
    COUNT(*) as total,
    COUNT(purpose) as populated,
    ROUND(100.0 * COUNT(purpose) / COUNT(*), 1) as pct
FROM f990_2025.pf_grants;
```

### Find Potential Duplicates

```sql
SELECT filename, COUNT(*)
FROM f990_data.processed_xml_files
GROUP BY filename
HAVING COUNT(*) > 1;
```

### Check Import Progress

```sql
SELECT
    source_zip,
    COUNT(*) as files_processed,
    MAX(processed_at) as last_processed
FROM f990_data.processed_xml_files
GROUP BY source_zip
ORDER BY last_processed DESC;
```

---

## Lessons Learned

1. **Verify XML element names against actual IRS data** - Don't trust documentation alone; inspect sample XMLs
2. **Keep raw XML accessible** - Original ZIPs enable backfill without re-downloading
3. **Build validation into imports** - Check field population rates immediately after import
4. **Use stream processing** - Extract XML from ZIP in-memory; no temp file extraction needed
5. **Checkpoint frequently** - Save every 500 records for resume capability
6. **Isolate errors** - Don't let one bad XML file crash entire batch
7. **Track processed files** - Prevent duplicate processing across multiple ZIPs
8. **Safe defaults for incremental** - Never drop existing data without explicit confirmation
9. **Test with small samples** - `--sample 5` before committing to full import
10. **Document undocumented tables** - Large tables without documentation cause confusion

---

## Related Files

| File | Purpose |
|------|---------|
| `1. Database/F990-2025/1. Import/xml_parsers/parse_990pf.py` | 990-PF XML parser (fixed) |
| `1. Database/F990-2025/1. Import/backfill_grant_purpose.py` | Backfill script for purpose field |
| `1. Database/F990-2025/2. Import review + fixes/REPORT 2025-12-5.1 grant purpose bug.md` | Bug fix documentation |
| `1. Database/F990-2025/2. Import review + fixes/REPORT 2025-12-4.1 import validation.md` | Validation report |
| `1. Database/OLD/1. Historical Data/SCHEMA_CLEANUP_REPORT.md` | Database schema analysis |
| `1. Database/DATA_DICTIONARY.md` | Data dictionary |
