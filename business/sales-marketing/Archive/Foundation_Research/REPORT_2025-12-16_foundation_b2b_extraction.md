# Foundation B2B Segment Extraction Report

**Date:** 2025-12-16
**Task:** PROMPT_2025-12-16_foundation_b2b_segments.md
**Output:** OUTPUT_2025-12-16_foundation_b2b_segments.csv

---

## Executive Summary

Extracted **641 foundations** across 6 segments for B2B outreach testing. Data quality is excellent (98%+ coverage on contact fields). Key insight: the priority segments (Intermediary Funders, High-Volume Regional, Large CB) captured most high-value targets, leaving fewer foundations for lower-priority segments.

---

## Process

### Step 1: Foundation Metrics Calculation
Built a temporary table with metrics for all 101,129 active foundations (grants in 2022+):
- `grantee_count`: Unique recipient EINs
- `cb_grant_count`: Grants with capacity-building keywords
- `intermediary_grant_count`: Grants with TA/training/evaluation keywords

### Step 2: Sequential Segment Extraction
Extracted segments in priority order, assigning each foundation to its **highest priority segment only**:

1. **Intermediary Funders** - Full extract
2. **High-Volume Regional** - Full extract (required state concentration calculation)
3. **Large CB Foundations** - Full extract
4. **California CB** - Filtered out those already in segments 1-3, then sampled
5. **Education Specialists** - Filtered, then sampled
6. **Random Baseline** - Filtered, then sampled 200

### Step 3: Contact Enrichment
- Pulled `phone_num` and `website_url` from most recent pf_returns record
- Pulled officers and ranked by title priority (Executive Director > CEO > President > Director > Trustee)

### Step 4: Export
Combined all segments into single CSV with segment assignment column.

---

## Results

| Segment | Priority | Target | Actual | % of Target |
|---------|----------|--------|--------|-------------|
| Intermediary Funders | 1 | Full | 122 | 100% |
| High-Volume Regional | 2 | Full | 143 | 100% |
| Large CB Foundations | 3 | Full | 115 | 100% |
| California CB | 4 | 200 | 49 | 25% |
| Education Specialists | 5 | 200 | 12 | 6% |
| Random Baseline | 6 | 200 | 200 | 100% |
| **TOTAL** | - | - | **641** | - |

### Data Quality

| Field | Records | Missing | Coverage |
|-------|---------|---------|----------|
| EIN | 641 | 0 | 100% |
| Business Name | 641 | 0 | 100% |
| State | 641 | 0 | 100% |
| Total Assets | 641 | 0 | 100% |
| Phone | 641 | 11 | 98.3% |
| Website | 641 | 11 | 98.3% |
| Officer Name | 641 | 3 | 99.5% |
| Officer Title | 641 | 3 | 99.5% |

---

## Segment Analysis

### Segment 1: Intermediary Funders (122 foundations)
**Criteria:** 10+ grants with TA/training/eval keywords, 50+ grantees, open, active 2022+

**Top 5 by Grantee Count:**
| Foundation | State | Assets | Grantees |
|------------|-------|--------|----------|
| The Allstate Foundation | IL | $78M | 2,182 |
| Fidelity Foundation | MA | $3.8B | 1,717 |
| Robert Wood Johnson Foundation | NJ | $13.7B | 1,628 |
| Lilly Endowment Inc | IN | $19.4B | 1,277 |
| Ford Foundation | NY | $16.8B | 1,221 |

**Insight:** Corporate foundations (Allstate, Fidelity) dominate this segment - they invest heavily in grantee training and evaluation.

### Segment 2: High-Volume Regional (143 foundations)
**Criteria:** 100+ grantees, >80% grants to one state, open, active 2022+

**Top 5 by Grantee Count:**
| Foundation | State | Assets | Grantees |
|------------|-------|--------|----------|
| Eastern Bank Foundation | MA | $250M | 1,188 |
| Marie Lamfrom Charitable Foundation | OR | $375M | 754 |
| Bristol-Myers Squibb Foundation | NJ | $69M | 659 |
| JP Morgan Chase Foundation | NY | $357M | 569 |
| The Duke Endowment | NC | $4.3B | 446 |

**Insight:** Mix of corporate (Eastern Bank, BMS) and legacy foundations with strong regional focus.

### Segment 3: Large CB Foundations (115 foundations)
**Criteria:** Assets >$100M, 50+ grantees, 5+ CB grants, open, active 2022+

**Top 5 by Grantee Count:**
| Foundation | State | Assets | Grantees |
|------------|-------|--------|----------|
| Bank of America Charitable | NC | $250M | 17,586 |
| Bill & Melinda Gates Foundation | WA | $77B | 875 |
| Truist Foundation | NC | $436M | 788 |
| Wells Fargo Foundation | CA | $352M | 743 |
| US Bank Foundation | MN | $123M | 553 |

**Insight:** Bank foundations dominate - they have high volume AND capacity building focus.

### Segment 4: California CB (49 foundations)
**Criteria:** CA-based, 20+ grantees, 3+ CB grants, open, active 2022+

**Why under target:** Only 83 foundations met all criteria. Of those, 34 were already captured by higher-priority segments (Intermediary Funders or Large CB).

### Segment 5: Education Specialists (12 foundations)
**Criteria:** >50% grants to NTEE B (Education), 20+ grantees, open, active 2022+

**Why severely under target:**
1. Most education-focused foundations are **preselected-only** (donor-advised, family foundations)
2. Many that were open were already captured by higher segments
3. The 50% threshold is strict - foundations often give to multiple sectors

**Recommendation:** Relax criteria to 40% education focus OR include preselected foundations for research.

### Segment 6: Random Baseline (200 foundations)
**Criteria:** 10+ grantees, active 2022+, open - random sample

Full 200-foundation sample achieved. This serves as control group.

---

## Lessons Learned

### What Worked Well
1. **Priority-based deduplication** - Assigning to highest segment prevents double-counting
2. **Temp table for metrics** - Pre-computing grantee/CB/intermediary counts made segment queries fast
3. **Officer title ranking** - Simple priority system (ED > CEO > President > Trustee) worked well

### Challenges

| Challenge | Impact | Solution Used |
|-----------|--------|---------------|
| Education segment too restrictive | Only 12 foundations | Accept smaller segment for now |
| California overlaps with national | 34 CA foundations in higher segments | Expected behavior - proof segments overlap |
| State concentration query slow | Added ~60 seconds | Acceptable for one-time extraction |

### Data Quality Issues

1. **Phone/Website 98% coverage** - 11 foundations missing contact info; likely very small or inactive
2. **3 foundations missing officers** - May be new filings not yet processed
3. **Some officer names are institutions** (e.g., "HUNTINGTON NATIONAL BANK" as trustee) - corporate trustees for trust-based foundations

### Recommendations for Phase 2

1. **Enrich missing contacts** - 11 foundations need manual lookup
2. **Add LinkedIn lookup** - Officer names available; can find email/profile
3. **Consider relaxing Education criteria** - 40% threshold would capture more
4. **Track segment source** - When a foundation qualifies for multiple segments, note all (for analysis)

---

## SQL Queries Used

### Foundation Metrics
```sql
WITH active_foundations AS (
    SELECT DISTINCT foundation_ein FROM f990_2025.fact_grants WHERE tax_year >= 2022
),
grantee_counts AS (
    SELECT foundation_ein, COUNT(DISTINCT recipient_ein) as grantee_count
    FROM f990_2025.fact_grants WHERE tax_year >= 2022 GROUP BY foundation_ein
),
cb_counts AS (
    SELECT foundation_ein, COUNT(*) as cb_grant_count
    FROM f990_2025.fact_grants
    WHERE purpose_text ILIKE ANY(ARRAY['%capacity building%', '%technical assistance%',
        '%organizational development%', '%general operating%', '%operating support%'])
    GROUP BY foundation_ein
)
-- Join all metrics
```

### State Concentration (for Regional segment)
```sql
WITH state_concentration AS (
    SELECT foundation_ein, recipient_state,
           COUNT(*) as state_grants,
           SUM(COUNT(*)) OVER (PARTITION BY foundation_ein) as total_grants
    FROM f990_2025.fact_grants
    WHERE tax_year >= 2022 AND recipient_state IS NOT NULL
    GROUP BY foundation_ein, recipient_state
)
SELECT foundation_ein, MAX(state_grants::float / total_grants) as max_state_pct
FROM state_concentration GROUP BY foundation_ein
```

### Education Percentage (for Education segment)
```sql
WITH education_grants AS (
    SELECT fg.foundation_ein,
           COUNT(*) FILTER (WHERE LEFT(dr.ntee_code, 1) = 'B') as edu_grants,
           COUNT(*) as total_grants
    FROM f990_2025.fact_grants fg
    LEFT JOIN f990_2025.dim_recipients dr ON fg.recipient_ein = dr.ein
    WHERE fg.tax_year >= 2022
    GROUP BY fg.foundation_ein
)
SELECT foundation_ein, edu_grants::float / total_grants as edu_pct
FROM education_grants WHERE total_grants > 0
```

---

## File Outputs

| File | Records | Description |
|------|---------|-------------|
| OUTPUT_2025-12-16_foundation_b2b_segments.csv | 641 | All extracted foundations with contact info |

---

## Next Steps

1. **Outreach prioritization** - Start with Segment 1 (Intermediary Funders) - highest likelihood of understanding value prop
2. **Contact enrichment** - Fill 11 missing phone/websites via manual lookup
3. **Email discovery** - Use officer names + foundation websites to find email addresses
4. **CRM import** - Load CSV into outreach system with segment tags

---

*Report generated: 2025-12-16*
