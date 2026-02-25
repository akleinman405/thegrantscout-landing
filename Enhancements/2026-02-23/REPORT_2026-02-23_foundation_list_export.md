# Bay Area Youth & Education Foundation List Export

**Date:** 2026-02-23
**Prompt:** Generate branded PDF of top 150 Bay Area foundations funding youth/education for LinkedIn lead gen
**Status:** Complete
**Owner:** Aleck

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-23 | Claude | Initial version |
| 2.0 | 2026-02-23 | Claude | Refactored to reusable CLI tool + `/foundation-list` slash command |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Data Summary](#data-summary)
3. [Top 10 Foundations](#top-10-foundations)
4. [City Distribution](#city-distribution)
5. [Name Cleaning Approach](#name-cleaning-approach)
6. [Data Quality Notes](#data-quality-notes)
7. [Files Created](#files-created)

---

## Executive Summary

Generated a branded PDF listing the top 150 Bay Area private foundations that have funded youth and education programs (2022-2024). The list is intended as a free LinkedIn lead gen asset: prospects download it to see WHAT exists, then TheGrantScout upsells personalized reports showing HOW to approach them.

**Key metrics:**

- **150 foundations** listed (from 1,270 matching the query)
- **$1,533,369,110** combined youth/education giving
- **6,881 grants** in the category
- **54 foundations** based in San Francisco (36%)
- **9 Bay Area counties** covered

## Data Summary

**Query filters:**

- Foundation state = CA
- Foundation city in 70 Bay Area cities across 9 counties
- Grant tax year >= 2022, amount > 0
- Purpose text matches regex: youth, education, school, student, children, after-school, tutoring, literacy, scholarship, elementary, secondary, K-12, young people, child
- Ranked by total giving DESC, limited to top 150

**Data source:** IRS 990-PF filings via fact_grants + dim_foundations (f990_2025 schema)

## Top 10 Foundations

| Rank | Foundation | City | Total Giving | Grants |
|------|-----------|------|-------------|--------|
| 1 | The Ann & Gordon Getty Foundation | San Francisco | $152,390,000 | 28 |
| 2 | Tosa Foundation | Portola Valley | $88,414,340 | 52 |
| 3 | Valhalla Foundation | Woodside | $73,332,058 | 76 |
| 4 | Crankstart Foundation | San Jose | $62,014,000 | 167 |
| 5 | The William & Flora Hewlett Foundation | Menlo Park | $61,753,318 | 234 |
| 6 | XQ Institute | Oakland | $53,270,009 | 49 |
| 7 | Gordon E and Betty I Moore Foundation | Palo Alto | $51,430,929 | 123 |
| 8 | Charles and Helen Schwab Foundation | San Francisco | $45,342,052 | 111 |
| 9 | Salesforce Foundation | San Francisco | $42,895,000 | 33 |
| 10 | The Leonard & Sophie Davis Fund | San Francisco | $40,637,020 | 259 |

## City Distribution

| City | Foundations | % of Total |
|------|-----------|-----------|
| San Francisco | 54 | 36.0% |
| Palo Alto | 19 | 12.7% |
| San Jose | 7 | 4.7% |
| Oakland | 6 | 4.0% |
| Los Altos | 6 | 4.0% |
| Menlo Park | 5 | 3.3% |
| Redwood City | 4 | 2.7% |
| San Rafael | 4 | 2.7% |
| Mill Valley | 3 | 2.0% |
| Walnut Creek | 3 | 2.0% |
| Other (31 cities) | 39 | 26.0% |

## Name Cleaning Approach

IRS 990-PF data truncates foundation names at ~35-40 characters. The script applies three layers of cleanup:

1. **EIN-keyed overrides** (18 foundations): Manual corrections for truncated names confirmed via web search and DB cross-reference. Examples: "THE ERIC AND WENDY SCHMIDT FUND FOR" restored to full name.

2. **General title-case logic:** Articles/prepositions lowercased mid-name (and, of, for, the), Roman numerals preserved (II, III), known acronyms kept uppercase (RJM, AAM, KLA, MZ, XQ, KHR, UCSF).

3. **Special patterns:** O'Donnell-style names capitalize after apostrophe; Mc/Mac prefixes handled; "Inc" suffix stripped; "Fdn" expanded to "Foundation".

## Data Quality Notes

- **Duplicate entity:** Sandberg Goldberg Bernthal Family Foundation appears twice (ranks 62 and 70) because Sheryl Sandberg's family operates two separate legal entities with different EINs. Both are legitimate.
- **"Accepts applications" field:** Many foundations show FALSE but still accept unsolicited proposals. This field reflects the 990-PF checkbox, not real-world practice.
- **Purpose text matching:** Regex-based, so some grants may be tangentially related (e.g., a foundation funding a school's building project would match "school"). The top 150 by dollar volume are overwhelmingly genuine youth/education funders.
- **Assets data:** Some foundations show very low assets (e.g., Getty Foundation at $29K) because the dim_foundations table may store the most recent filing's assets, and some years show pass-through giving patterns.

## Files Created

| File | Path | Description |
|------|------|-------------|
| Branded PDF | `Enhancements/2026-02-23/Bay_Area_Youth_Education_Foundations_2026.pdf` | 95KB, letter-size, navy/gold branding, 150-row table + CTA |
| Markdown source | `Enhancements/2026-02-23/Bay_Area_Youth_Education_Foundations_2026.md` | Source of truth for PDF conversion |
| HTML intermediate | `Enhancements/2026-02-23/Bay_Area_Youth_Education_Foundations_2026.html` | Debug/preview version |
| CSV export | `Enhancements/2026-02-23/bay_area_youth_education_foundations_2026.csv` | 150 rows, includes EIN/assets/accepts_applications/most_recent_year |
| Generator script | `Enhancements/2026-02-23/generate_foundation_list.py` | Reproducible: query + format + write |
| Session report | `Enhancements/2026-02-23/REPORT_2026-02-23_foundation_list_export.md` | This file |

## V2.0: Reusable CLI Tool + Slash Command

The original `generate_foundation_list.py` was hardcoded for Bay Area + Youth/Education. V2 refactors it into a reusable tool.

**What changed:**

- **`0. Tools/generate_foundation_list.py`** (~310 lines): Argparse CLI with `--state`, `--cities`, `--topic-regex`, `--topic-label`, `--geo-label`, `--output-dir`, `--limit`, `--min-year`, `--skip-pdf`. DB connection uses `get_connection()` env var pattern (from `pull_funder_snapshots.py`). Dynamic `--min-year` defaults to `current_year - 3`. Output filenames auto-derived from geo/topic labels. Truncation warning for names >= 35 chars not in overrides.
- **`.claude/commands/foundation-list.md`** (~80 lines): Slash command with frontmatter. Maps natural language args ("Bay Area Youth Education") to script parameters. Includes known tested combinations and regex patterns for common topics. Runs COUNT(*) validation for untested combos. STOP gate before PDF generation.
- **CLAUDE.md** updated: Skills table + Tools Reference table entries added.

**Verification:** Ran with `--min-year 2022` to match original params. All 150 EINs match, 0 amount mismatches. PDF generates successfully (95KB).

**Extension:** To run a new geography/topic, invoke `/foundation-list NYC Arts Culture`. Claude maps it to args, validates with COUNT(*), then runs the script.

## Notes

- PDF uses existing `0. Tools/md_to_pdf.py` with TGS branding (navy headers, gold borders, alternating row shading)
- WeasyPrint handles the 150-row table gracefully across multiple pages with per-row page-break avoidance
- CTA section is on its own page (via `<!-- PAGE_BREAK -->` marker) with clickable links to thegrantscout.com, LinkedIn, and email
- No em dashes used anywhere in the document
- `--state` is mandatory to prevent unbounded national scans (8.3M rows)
- "Based in" filter: v1 filters by foundation home location, not grant destination

## Files Created/Modified (V2)

| File | Path | Description |
|------|------|-------------|
| CLI tool | `0. Tools/generate_foundation_list.py` | Reusable argparse script |
| Slash command | `.claude/commands/foundation-list.md` | `/foundation-list` command |
| CLAUDE.md | `.claude/CLAUDE.md` | Skills + Tools Reference updated |
| Session report | `Enhancements/2026-02-23/REPORT_2026-02-23_foundation_list_export.md` | This file (v2.0) |

---

*Generated by Claude Code on 2026-02-23*
