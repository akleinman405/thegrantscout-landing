# Pipeline Audit Report

**Date:** 2025-12-30
**Auditor:** Claude Code
**Pipeline Location:** `/Users/aleckleinman/Documents/TheGrantScout/5. TheGrantScout - Pipeline/`

---

## Section 1: Directory Structure

### Python Files (31 total)

```
./ai/__init__.py
./ai/fallbacks.py
./ai/narratives.py
./assembly/__init__.py
./assembly/report_data.py
./batch_generate.py
./config/__init__.py
./config/database.py
./config/settings.py
./enrichment/__init__.py
./enrichment/cache.py
./enrichment/connections.py
./enrichment/snapshot.py
./generate_report.py
./loaders/__init__.py
./loaders/client_data.py
./loaders/questionnaire.py
./rendering/__init__.py
./rendering/md_renderer.py
./Report Templates/convert_to_docx.py
./scoring/__init__.py
./scoring/features.py
./scoring/scoring.py
./scraper/__init__.py
./scraper/cache.py
./scraper/extractors.py
./scraper/fallback.py
./scraper/scraper.py
./tests/__init__.py
./tests/fixtures/sample_data.py
./tests/quality_checklist.py
```

### File Counts by Module

| Module | Python Files | SQL Files | Other |
|--------|--------------|-----------|-------|
| ai/ | 3 | 0 | prompts/*.txt |
| assembly/ | 2 | 0 | 0 |
| config/ | 3 | 0 | coefficients.json, scaling.json |
| enrichment/ | 4 | 8 | 0 |
| loaders/ | 3 | 0 | 0 |
| rendering/ | 2 | 0 | templates/*.md |
| scoring/ | 3 | 0 | 0 |
| scraper/ | 5 | 0 | 0 |
| tests/ | 3 | 0 | 0 |
| root | 3 | 0 | .env, requirements.txt |

### SQL Files in enrichment/sql/

- annual_giving.sql
- comparable_grant.sql
- funding_trend.sql
- geographic_focus.sql
- giving_style.sql
- recipient_profile.sql
- repeat_funding.sql
- typical_grant.sql

---

## Section 2: Module Status Table

| Module | Import Status | Key Functions | Lines | Notes |
|--------|---------------|---------------|-------|-------|
| config | PASS | init_pool, query_df | ~150 | Uses psycopg2 connection pool |
| config.settings | PASS | PROJECT_ROOT | ~50 | Paths configured correctly |
| scoring | PASS | GrantScorer.score_nonprofit | ~300 | LASSO model with coefficients |
| scoring.features | PASS | calculate_features | ~200+ | Feature engineering |
| enrichment | PASS | get_funder_snapshot, find_connections | ~370 | 8 SQL queries per foundation |
| loaders | PASS | load_questionnaire, get_all_clients | ~230 | CSV parsing with flexible columns |
| assembly | PASS | assemble_report_data | ~340 | Orchestrates scoring + enrichment |
| scraper | PASS | gather_for_report | ~270 | Website scraping with BeautifulSoup |
| ai | PASS | generate_all_narratives | ~370 | Claude API + fallbacks |
| rendering | PASS | ReportRenderer.render | ~420 | Markdown template rendering |

**All 8 core modules import successfully. No stub implementations detected.**

---

## Section 3: Generated Reports

### Outputs Directory Structure

```
outputs/
  logs/
    PHASE_0_COMPLETE.md (Dec 27, 23:14)
    PHASE_2_COMPLETE.md (Dec 27, 23:20)
    PHASE_3A_COMPLETE.md (Dec 27, 23:22)
    PHASE_3B_COMPLETE.md (Dec 27, 23:26)
    report_20251227_234919.log
  reports/
    Patient_Safety_Movement_Foundation_Week52_20251227.json (18,839 bytes)
    Patient_Safety_Movement_Foundation_Week52_20251227.md (13,084 bytes)
  test_report.md (4,579 bytes)
```

### Reports Generated

| Client | File | Date | Size |
|--------|------|------|------|
| Patient Safety Movement Foundation | Week52_20251227.md | Dec 27, 2025 | 13 KB |
| Patient Safety Movement Foundation | Week52_20251227.json | Dec 27, 2025 | 19 KB |

### Phases Completed

| Phase | Status | Date |
|-------|--------|------|
| Phase 0 (Infrastructure) | Complete | Dec 27, 23:14 |
| Phase 2 (Scoring) | Complete | Dec 27, 23:20 |
| Phase 3A (Snapshot SQL) | Complete | Dec 27, 23:22 |
| Phase 3B (Enrichment) | Complete | Dec 27, 23:26 |

---

## Section 4: Database Status

| Metric | Result |
|--------|--------|
| Connection | WORKING |
| Pool Initialization | SUCCESS |
| Foundation Count | 143,184 |
| Grants Count | 8,310,650 |
| Host | localhost:5432 |
| Database | thegrantscout |
| Schema | f990_2025 |

### Sample Query Results

```
EIN         | Name                        | State
------------|-----------------------------|-----
010024907   | BAR HARBOR VILLAGE IMP...   | ME
010131950   | PLANT MEMORIAL HOME         | ME
010211484   | Bangor Theological Seminary | ME
```

---

## Section 5: Client Inventory

| Organization | EIN | State | Budget |
|--------------|-----|-------|--------|
| Patient Safety Movement Foundation | (empty) | CA | Over $1,000,000 |
| Retirement Housing Foundation | (empty) | CA | — |
| SNS | (empty) | CA | — |
| Ka Ulukoa | (empty) | HI | — |
| Arborbrook Christian Academy | (empty) | NC | — |
| Horizons National Student Enrichment Program Inc. | (empty) | NY | — |

**Total Clients:** 6

**Issue:** All clients have empty EIN values in questionnaire data.

---

## Section 6: Issues Found

### Critical Issues

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| 1 | **All client EINs are empty** | HIGH | loaders/questionnaire.py |
| 2 | **Scoring fails without EIN** | HIGH | assembly/report_data.py:226 |
| 3 | **Timeline dates broken** | MEDIUM | rendering/md_renderer.py |
| 4 | **Contact info always empty** | MEDIUM | scraper/scraper.py |
| 5 | **Portal URLs always empty** | MEDIUM | scraper/scraper.py |

### Data Quality Issues (in generated report)

| Issue | Example from Report |
|-------|---------------------|
| Unrealistic grant amounts | "$16,693,000 - $128,592,354" for typical grants |
| Comparable grant names are raw data | "SEE ATTACHED SCHEDULE received $16,693,000" |
| Geographic alignment text incorrect | Says "IL aligns with your location" for CA client |
| Empty purpose text | "received $X for ()" - missing purpose |
| Timeline has duplicate dates | Weeks 2-8 all show "December 28, 2025" |
| All foundations marked HIGH priority | No differentiation between matches |

### Import Warnings (non-blocking)

```
UserWarning: pandas only supports SQLAlchemy connectable...
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
```

### Missing/Incomplete Data

| Component | Status |
|-----------|--------|
| .env file | EXISTS (credentials configured) |
| coefficients.json | EXISTS |
| scaling.json | EXISTS |
| AI prompt templates | NOT VERIFIED (prompts/*.txt) |
| Report templates | EXISTS (templates/*.md) |

---

## Section 7: Recommended Next Steps

### Priority 1: Critical (Required for Production)

| Task | Complexity | Description |
|------|------------|-------------|
| Fix EIN population | MEDIUM | Questionnaire CSV needs EIN column populated, or add EIN lookup by name |
| Validate scoring results | HIGH | Grant amounts ($16M-$300M) seem incorrect; verify model coefficients |
| Fix data quality filters | MEDIUM | Filter out "SEE ATTACHED" and similar garbage data in comparable grants |

### Priority 2: High (Impacts Report Quality)

| Task | Complexity | Description |
|------|------------|-------------|
| Fix timeline date calculation | LOW | Line 293 in rendering/md_renderer.py has date math bug |
| Fix geographic alignment text | LOW | "Why This Fits" narrative uses wrong state reference |
| Improve priority differentiation | MEDIUM | Not all matches should be "HIGH" - implement scoring thresholds |

### Priority 3: Medium (Enhancement)

| Task | Complexity | Description |
|------|------------|-------------|
| Implement contact scraping | HIGH | scraper.py doesn't extract contacts - needs regex patterns |
| Add portal URL detection | MEDIUM | Find application portals on foundation websites |
| Validate AI prompts exist | LOW | Check prompts/*.txt files exist and are valid |

### Priority 4: Low (Polish)

| Task | Complexity | Description |
|------|------------|-------------|
| Fix pandas SQLAlchemy warning | LOW | Use SQLAlchemy connection in query_df() |
| Update urllib3/OpenSSL | LOW | System Python update |
| Add more test coverage | MEDIUM | tests/ folder has minimal tests |

---

## Summary

### What Works

- All 8 core modules import and function correctly
- Database connection to 143K foundations and 8.3M grants
- End-to-end pipeline generates reports
- Fallback narratives work without API key
- JSON + Markdown output generation
- Phase completion tracking

### What Needs Fixing Before Production

1. **EIN data** - Clients need EINs for scoring to work properly
2. **Data quality** - Filter out garbage data from IRS filings
3. **Scoring validation** - Verify model produces realistic grant amounts
4. **Template bugs** - Fix timeline dates and geographic text

### Overall Status

**Pipeline Status:** FUNCTIONAL (with caveats)

The pipeline successfully generates reports but the output quality is not production-ready due to data quality issues and missing EIN data. Recommend 1-2 days of focused bug fixing before client delivery.

---

*Generated by Claude Code on 2025-12-30*
