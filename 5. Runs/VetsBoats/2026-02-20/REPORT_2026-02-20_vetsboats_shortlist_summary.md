# VetsBoats Hard-Filtered Foundation Shortlist

**Date:** 2026-02-20
**Prompt:** PROMPT_2026-02-20_vetsboats_hardfiltered_shortlist.md
**Status:** Complete
**Owner:** Alec Kleinman

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-20 | Claude Code | Initial version |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Funnel Summary](#funnel-summary)
3. [Filter Methodology](#filter-methodology)
4. [Data Quality Notes](#data-quality-notes)
5. [Top Prospects](#top-prospects)
6. [Near-Miss Analysis](#near-miss-analysis)
7. [SQL Used](#sql-used)
8. [Files Created](#files-created)

---

## Executive Summary

Applied three hard filters (open to applicants, CA geography, PF-to-PF grants) to a pool of 4,553 candidate foundations for VetsBoats (EIN 464194065). **340 foundations passed all three filters.** An additional 1,197 near misses passed 2 of 3 filters.

Key metrics:

- 327 of 340 have veteran-related grants in their history
- 21 come from sibling analysis (fund VetsBoats peer orgs), 327 from veteran keyword search, 8 from both
- 0 known funders appear in the results (all 5 excluded as expected)
- The typical passed foundation has made grants to private foundations AND gives in California AND is open to applicants

**Note on EIN:** The prompt referenced EIN 273960435, which does not exist in pf_returns. VetsBoats' correct EIN per dim_clients is **464194065**. All queries used the correct EIN.

## Funnel Summary

| Stage | Count | % of Pool |
|-------|------:|----------:|
| Total candidate pool (Source A + B) | 4,553 | 100% |
| Passed F1: Open to applicants | 1,518 | 33.3% |
| Passed F1 + F2: Open + CA geography | 809 | 17.8% |
| **Passed ALL 3 filters** | **340** | **7.5%** |
| Near misses (2 of 3) | 1,197 | 26.3% |

### Candidate Pool Breakdown

| Source | Count |
|--------|------:|
| Source A: Sibling analysis (calc_client_foundation_scores) | 143 |
| Source B: Veteran keyword search (fact_grants purpose_text) | 4,447 |
| Overlap (in both) | 37 |
| **Combined (A union B)** | **4,553** |

### Filter Results (Independent)

| Filter | Pass | Fail |
|--------|-----:|-----:|
| F1: Open to applicants | 1,518 | 3,035 |
| F2: CA geography | 2,691 | 1,862 |
| F3: PF-to-PF grants | 1,256 | 3,297 |

## Filter Methodology

### Filter 1: Open to Applicants

Uses the **most recent** pf_returns filing per foundation (ordered by tax_year DESC, return_timestamp DESC).

**Pass condition:** `only_contri_to_preselected_ind` is FALSE or NULL.

**Why grants_to_organizations_ind was excluded:** In the candidate pool, 1,388 foundations have `grants_to_organizations_ind = FALSE` on their latest filing but `only_contri_to_preselected_ind = FALSE`. Since ALL candidates were identified through actual grant records (they demonstrably make grants), the `grants_to_organizations_ind` flag reflects the specific filing year, not the foundation's general behavior. Including it as a hard filter would incorrectly exclude 1,388 open foundations.

### Filter 2: CA Geography

**Pass condition:** Foundation has made at least 1 grant to a CA recipient in fact_grants, OR is headquartered in California (state = 'CA' on latest pf_returns).

The CA headquarters carve-out catches national funders based in CA that may have grants recorded without state data.

### Filter 3: PF-to-PF Grants

**Pass condition:** Foundation has at least 1 grant in fact_grants where `recipient_ein` matches an EIN in pf_returns (confirming the recipient is a private foundation).

**Method:** `JOIN fact_grants fg ... WHERE EXISTS (SELECT 1 FROM pf_returns pr WHERE pr.ein = fg.recipient_ein)`

This is the most restrictive filter due to recipient_ein coverage limitations (see Data Quality section).

## Data Quality Notes

### Recipient EIN Coverage (Critical for Filter 3)

- **56.1%** of fact_grants records have `recipient_ein` populated (4,665,642 of 8,310,650)
- Filter 3 relies entirely on this join. Foundations that fund PFs but whose grant records lack recipient EINs will **false-negative** on this filter.
- **Mitigation:** Near-miss foundations that failed ONLY Filter 3 (469 foundations) should be prioritized for manual website review. Many may actually fund PFs but the evidence isn't in our EIN-linked data.

### Field Reliability

| Field | Notes |
|-------|-------|
| `only_contri_to_preselected_ind` | Generally reliable. Checked on latest filing only. |
| `grants_to_organizations_ind` | Unreliable as a hard filter. Reflects specific filing year, not foundation behavior. |
| `recipient_state` | Well-populated in fact_grants. CA grant counts are reliable. |
| `website_url` | Mixed quality. Some contain "N/A", "NONE", "0". Filtered in HTML display. |
| `mission_desc` / `activity_or_mission_desc` | Longer of the two is shown. Some are empty. |

### Known Limitations

1. **PF-to-PF detection is conservative.** We only detect PF recipients that exist in pf_returns AND have a matching recipient_ein. Foundations giving to PFs via fiscal sponsors or under variant names will be missed.
2. **Veteran keyword search is English-only** and covers: veteran, military, armed forces, service member, wounded warrior, adaptive sailing, therapeutic sailing, adaptive recreation.
3. **"Open to applicants" may change year-to-year.** A foundation that was preselected-only in 2022 but open in 2023 (latest filing) passes the filter.

## Top Prospects

### Top 10 by PF-to-PF Grant Count (Passed All 3)

| # | Foundation | State | PF Grants | CA Grants | Vet Grants | Assets | Source |
|---|-----------|-------|----------:|----------:|-----------:|-------:|--------|
| 1 | Bank of America Charitable | NC | 372 | 35,133 | 0 | $7.6M | sibling |
| 2 | Ford Foundation | NY | 78 | 1,470 | 6 | $16.8B | both |
| 3 | Carnegie Corporation of NY | NY | 66 | 360 | 22 | $4.5B | keyword |
| 4 | W.K. Kellogg Foundation | MI | 63 | 780 | 3 | $454M | keyword |
| 5 | Duke Energy Foundation | NC | 53 | 208 | 0 | $6.2M | sibling |
| 6 | Enterprise Holdings Foundation | MO | 48 | 3,924 | 0 | $545M | sibling |
| 7 | MacArthur Foundation | IL | 47 | 749 | 15 | $8.7B | keyword |
| 8 | Xcel Energy Foundation | MN | 41 | 164 | 0 | $3.7M | sibling |
| 9 | Hewlett Foundation | CA | 37 | 3,251 | 2 | $13.3B | keyword |
| 10 | Meyer Memorial Trust | OR | 33 | 120 | 18 | $885M | keyword |

### Top Veteran-Focused (Passed All 3, Sorted by Veteran Grant Count)

Foundations with the most veteran-related grants that also pass all filters are the highest-priority prospects for VetsBoats.

## Near-Miss Analysis

### Distribution by Failed Filter

| Failed Filter | Count | Priority for Manual Review |
|---------------|------:|---------------------------|
| Open to Applicants | 573 | LOW: Preselected-only on latest filing. May require relationship approach. |
| PF-to-PF Grants | 469 | HIGH: May fund PFs but EIN data missing. Check websites. |
| CA Geography | 155 | MEDIUM: No CA grants on record. Some may give nationally. |

The 469 near misses that failed only Filter 3 are the most promising for manual follow-up. They are open to applicants and give in California, but we lack PF-to-PF evidence in our data. Given 56.1% EIN coverage, roughly half of these may actually fund PFs.

## SQL Used

### Candidate Pool

**Source A (Sibling Analysis):**
```sql
SELECT DISTINCT foundation_ein
FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = '464194065'
```

**Source B (Veteran Keywords):**
```sql
SELECT DISTINCT foundation_ein
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '(veteran|military|armed forces|service member
  |wounded warrior|adaptive sailing|therapeutic sailing|adaptive recreation)'
```

### Filter 1: Open to Applicants

```sql
WITH latest AS (
    SELECT DISTINCT ON (ein)
        ein, only_contri_to_preselected_ind, grants_to_organizations_ind, tax_year
    FROM f990_2025.pf_returns
    WHERE ein = ANY($1)
    ORDER BY ein, tax_year DESC, return_timestamp DESC NULLS LAST
)
SELECT ein FROM latest
WHERE only_contri_to_preselected_ind IS NOT TRUE
```

### Filter 2: CA Geography

```sql
SELECT foundation_ein, COUNT(*) as ca_grant_count
FROM f990_2025.fact_grants
WHERE foundation_ein = ANY($1)
  AND recipient_state = 'CA'
GROUP BY foundation_ein
-- Also pass foundations where latest pf_returns.state = 'CA'
```

### Filter 3: PF-to-PF Grants

```sql
SELECT fg.foundation_ein,
       COUNT(DISTINCT fg.id) as pf_grant_count,
       COALESCE(SUM(fg.amount), 0) as pf_grant_total
FROM f990_2025.fact_grants fg
WHERE fg.foundation_ein = ANY($1)
  AND fg.recipient_ein IS NOT NULL
  AND EXISTS (
      SELECT 1 FROM f990_2025.pf_returns pr
      WHERE pr.ein = fg.recipient_ein
  )
GROUP BY fg.foundation_ein
```

## Files Created

| File | Path | Description |
|------|------|-------------|
| REVIEW_2026-02-20_vetsboats_prospects.html | 5. Runs/VetsBoats/2026-02-20/ | Interactive HTML review with cards, badges, search (PRIMARY) |
| DATA_2026-02-20_vetsboats_hardfiltered_prospects.csv | 5. Runs/VetsBoats/2026-02-20/ | Full CSV with all 4,553 candidates and filter results |
| REPORT_2026-02-20_vetsboats_shortlist_summary.md | 5. Runs/VetsBoats/2026-02-20/ | This summary report |
| build_shortlist.py | 5. Runs/VetsBoats/2026-02-20/ | Script that generated all outputs |

## Notes

1. **340 is a manageable shortlist** for website review. Sorted by PF-to-PF count, the most proven PF funders appear first.
2. **Near misses that failed only Filter 3** (469 foundations) deserve manual checking given 56.1% recipient EIN coverage.
3. **The sibling analysis only contributed 21 foundations** to the passed list (vs 327 from keyword search). This makes sense: the sibling set was designed for general nonprofit matching, and most foundations in it have never funded another PF.
4. **Corporate foundations** (Bank of America, Duke Energy, Enterprise, Xcel) appear because they technically fund PFs and give in CA, but their PF grants may be to corporate-related entities, not external PFs like VetsBoats. Worth manual verification.

---

*Generated by Claude Code on 2026-02-20*
