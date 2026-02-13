# Foundation Verification Report

**Date:** 2026-01-20
**Prompt:** Foundation candidate verification for 5 beta clients
**Status:** Complete with Critical Issues Identified
**Owner:** Claude Code CLI

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | Claude Code | Initial version with full verification |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Pipeline Failure Analysis](#pipeline-failure-analysis)
3. [Client Results](#client-results)
4. [Foundation Verification Details](#foundation-verification-details)
5. [Files Created/Modified](#files-createdmodified)
6. [Recommendations](#recommendations)

---

## Executive Summary

### What Was Done
- Extracted 54 foundation candidates from database for 5 beta clients
- Performed web verification on all 54 foundations
- Assessed match quality with 6 specialized review agents
- Documented fit assessments and discovery stages in Excel

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Foundations Reviewed | 54 |
| Strong Matches | 15 (28%) |
| Moderate Matches | 9 (17%) |
| Weak Matches | 7 (13%) |
| **Should Be Removed** | **21 (39%)** |
| Existing Funders Identified | 8 |

### Critical Finding

**16 foundations (30%) should have been filtered out in Phase A but were not.** These foundations have explicit geographic restrictions that make them ineligible to fund the client's location. This represents a **pipeline failure** in the scoring/filtering system.

---

## Pipeline Failure Analysis

### Root Cause

The Phase A database query filtered on:
- `target_grants_to_siblings > 0` (has funded similar organizations)
- `open_to_applicants = TRUE` (accepts applications)

But it **DID NOT** filter on:
- `geo_eligible = TRUE` (foundation funds client's geographic area)
- Foundation state vs. client state alignment

### Why This Happened

The `calc_client_foundation_scores` table contains a `geo_eligible` column, but the extraction query did not use it. The scoring algorithm found foundations that gave to "sibling" organizations (similar nonprofits), but those siblings may have been in **different states** than the client.

**Example:** SNS is in California. The algorithm found that Anschutz Family Foundation gave grants to senior services organizations. But those grants were in **Colorado**, and Anschutz only funds Colorado. This was not caught until Phase B web verification.

### Affected Clients

| Client | State | Phase A Failures | % of List |
|--------|-------|------------------|-----------|
| SNS | California | 12 foundations | 80% |
| Friendship Circle | California (SD) | 5 foundations | 50% |
| Horizons | Multi-state | 0 | 0% |
| RHF | Multi-state | 0 | 0% |
| PSMF | National | 0 | 0% |

### Specific Failures

**SNS (California):** These foundations were recommended but CANNOT fund California:
| Foundation | State | Actual Coverage |
|------------|-------|-----------------|
| Oleson Foundation | MI | NW Michigan only |
| Anschutz Family Foundation | CO | Colorado only |
| McKeen Fund | FL | FL/MA/NY only |
| White Family Foundation | FL | Florida only |
| W J Brace Charitable Trust | TX | Kansas City/MO only |
| MetroWest Health Foundation | MA | MetroWest Boston only |
| TD Charitable Foundation | ME | East Coast only |
| The Dr P Phillips Foundation | FL | Orange/Osceola FL only |
| Fundacion Triple-S | PR | Puerto Rico only |
| The Myron Stratton Home | CO | SE Colorado only |
| NextFifty Initiative | CO | Colorado only |
| Direct Supply Foundation | WI | No public application |

**Friendship Circle (San Diego):** These foundations were recommended but CANNOT fund San Diego:
| Foundation | State | Actual Coverage |
|------------|-------|-----------------|
| Russell J Salvatore Foundation | NY | Buffalo NY only |
| Anschutz Family Foundation | CO | Colorado only |
| Richard Reed Foundation | AZ | CO & N. California only |
| Carolyn Smith Foundation | TN | Middle Tennessee only |
| June & Julian Foss Foundation | WA | Seattle/Portland/SF/Phoenix/Miami (not SD) |

---

## Client Results

### PSMF (Patient Safety Movement Foundation)
**Verdict: GOOD LIST** (with 2 removals)

| Foundation | Fit Rating | Status | Notes |
|------------|------------|--------|-------|
| Josiah Macy Jr Foundation | **STRONG** | Verified Open | Healthcare education - perfect fit |
| The Commonwealth Fund | **STRONG** | Verified Open | Healthcare policy - strong fit |
| John A Hartford Foundation | **STRONG** | Invite Only | Best fit but no unsolicited apps |
| WK Kellogg Foundation | WEAK | Verified Open | Mission mismatch - children/equity focus |
| The Schooner Foundation | REMOVE | Invite Only | No healthcare alignment at all |

**Viable: 3 | Weak: 1 | Remove: 1**

---

### RHF (Retirement Housing Foundation)
**Verdict: GOOD LIST** (with 2-3 weak matches)

| Foundation | Fit Rating | Status | Geographic Match |
|------------|------------|--------|------------------|
| The McKnight Foundation | **STRONG** | Verified Open | Minnesota |
| Otto Bremer Trust | **STRONG** | Invite Only | MN/MT/ND/WI |
| The Ahmanson Foundation | **STRONG** | Verified Open | LA County, CA |
| Meyer Memorial Trust | **STRONG** | Verified Open | Oregon |
| The Collins Foundation | **STRONG** | Verified Open | Oregon |
| Joseph B Whitehead Foundation | **STRONG** | Verified Open | Metro Atlanta |
| WSFS Cares Foundation | **STRONG** | Verified Open | DE/PA |
| FR Bigelow Foundation | MODERATE | Verified Open | MN East Metro |
| Karen E Henry Foundation | MODERATE | Needs Review | Texas |
| Conrad N Hilton Foundation | MODERATE | Invite Only | National |
| Banc of California | MODERATE | Needs Review | California |
| Liberty Mutual Foundation | MODERATE | Verified Open | Boston/Seattle/Dallas |
| John & Susan Dewan Foundation | WEAK | Verified Open | Chicago - wrong population |
| The Lotus US Foundation | WEAK | Needs Review | Wrong population focus |
| Mortenson Family Foundation | WEAK | Verified Open | Children/families, not seniors |

**Viable: 12 | Weak: 3**

---

### SNS (Senior Network Services)
**Verdict: CRITICAL FAILURE** - 80% of list is geographically ineligible

| Foundation | Fit Rating | Issue |
|------------|------------|-------|
| Christine & Jalmer Berg | MODERATE | Verify - Humboldt vs Riverside |
| Glen & Dorothy Stillwell | WEAK | Verify - Pasadena focus |
| American Woodmark | WEAK | Verify - Sacramento area |
| 12 others | **REMOVE** | Geographic disqualification |

**Viable: 1-3 | Remove: 12**

---

### Horizons (Horizons National)
**Verdict: GOOD LIST** - but mostly existing funders

| Foundation | Fit Rating | Notes |
|------------|------------|-------|
| Georgia Power Foundation | **STRONG** | Existing funder (invite only) |
| Joseph B Whitehead Foundation | **STRONG** | Existing funder - $400K-$500K grants |
| AEC Trust | **STRONG** | Existing funder (invite only) |
| Jack and Anne Glenn | **STRONG** | Existing funder |
| Webber Family Foundation | MODERATE | Existing funder - small grants |
| Cloudbreak Foundation | MODERATE | Existing funder |
| Jack Kent Cooke Foundation | WEAK | Scholarship focus, rarely funds orgs |
| California Wellness Foundation | REMOVE | Wrong organization (data error) |
| Pelino Charitable Foundation | REMOVE | Closed to applications |

**Viable: 7 | Remove: 2**

**Note:** 7 of 9 are existing Horizons funders, not new prospects.

---

### Friendship Circle (San Diego)
**Verdict: CRITICAL FAILURE** - 70% of list is geographically ineligible

| Foundation | Fit Rating | Issue |
|------------|------------|-------|
| Stanley W Ekstrom Foundation | **STRONG** | Existing funder - pursue |
| Gloria Estefan Foundation | MODERATE | National reach, disability focus |
| Umpqua Bank | MODERATE | Verify SD branch coverage |
| Oak Tree Charitable | REMOVE | Equine focus only |
| 6 others | **REMOVE** | Geographic disqualification |

**Viable: 2-3 | Remove: 7**

---

## Foundation Verification Details

### Verification Status Summary

| Status | Count | % |
|--------|-------|---|
| Verified Open | 34 | 63% |
| Invite Only | 10 | 19% |
| Needs Review | 10 | 19% |

### Match Quality Summary

| Rating | Count | % |
|--------|-------|---|
| Strong Match | 15 | 28% |
| Moderate Match | 9 | 17% |
| Weak Match | 7 | 13% |
| Remove | 21 | 39% |
| Existing Funder | 8 | 15% |

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| EXCEL_2026-01-20_foundation_candidates.xlsx | Same folder | 7-tab workbook with all data |
| PHASE_A_REVIEW_2026-01-20.md | Same folder | Phase A agent review consensus |
| PHASE_B_REVIEW_2026-01-20.md | Same folder | Phase B agent review consensus |
| REPORT_2026-01-20_foundation_verification.md | Same folder | This report |

### Excel Workbook Contents

| Tab | Contents | Rows |
|-----|----------|------|
| Summary | Client overview, top 5 per client | 5 |
| PSMF | 5 foundations with verification + fit assessment | 5 |
| RHF | 15 foundations with verification + fit assessment | 15 |
| SNS | 15 foundations with verification + fit assessment | 15 |
| Horizons | 9 foundations with verification + fit assessment | 9 |
| Friendship Circle | 10 foundations with verification + fit assessment | 10 |
| Target Grant Examples | 129 sample grants | 129 |

### Excel Columns (per client sheet)

| Column | Content |
|--------|---------|
| B | Foundation Name |
| C | EIN |
| D | State |
| E | Assets |
| F | Target Grants |
| G | Gold Standard |
| H | Total to Siblings |
| I | Median Grant |
| J | Grant Range |
| K | States Funded |
| L | Most Recent Year |
| M | IRS Open |
| N | Website |
| O-Q | Sample Grants 1-3 |
| R | Verification Status |
| S | Verification Notes |
| T | **Fit Assessment** (new) |
| U | **Discovery Stage** (new) |

---

## Recommendations

### Immediate Actions

1. **For SNS:** Regenerate foundation list with strict California geographic filter
2. **For Friendship Circle:** Regenerate foundation list with San Diego/SoCal filter
3. **For Horizons:** Consider adding NEW prospects (current list is mostly existing funders)

### Pipeline Fixes Required

1. **Add geographic filter to Phase A extraction query:**
   ```sql
   WHERE geo_eligible = TRUE
   ```

2. **Consider filtering by foundation state matching client state:**
   ```sql
   WHERE foundation_state = client_state
      OR foundation grants to client_state > threshold
   ```

3. **Add validation step after extraction:**
   - Cross-check foundation coverage against client location
   - Flag foundations with strict regional restrictions

### Quality Assurance Additions

1. Add match quality review **before** web verification to catch obvious mismatches earlier
2. Implement geographic eligibility scoring that accounts for:
   - Foundation headquarters state
   - States where foundation has historically given
   - Foundation's stated geographic restrictions (from 990-PF)

---

## Notes

### What Worked Well
- Web verification accurately identified application status
- Match quality review caught mission/population mismatches
- Multi-agent review process identified issues from multiple angles
- Excel formatting and structure meet requirements

### What Failed
- **Geographic filtering not applied in Phase A** - critical gap
- **Name-based matching caused data errors** (Horizons Foundation vs Horizons National)
- Phase A review agents focused on data quality, not match quality

### Lessons Learned
1. Geographic eligibility must be a **mandatory filter**, not optional
2. Match quality should be assessed **before** spending time on web research
3. "Sibling" organization matching can produce false positives across state lines
4. Celebrity/family foundation names can cause incorrect matches

---

*Generated by Claude Code on 2026-01-20*
