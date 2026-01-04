# Foundation B2B Segment Extraction

**Date:** 2025-12-16
**Context:** Testing B2B sales to foundations who might purchase TheGrantScout for their grantees
**Input:** REPORT_2025-12-15_foundation_segmentation_research.md

---

## Task

Extract 6 foundation segments for outreach testing. Include contact info (phone, website, top officer).

---

## Output Requirements

**File:** `OUTPUT_2025-12-16_foundation_b2b_segments.csv`

**Columns:**
- ein
- business_name
- state
- total_assets
- grantee_count (unique recipient_eins, 2022+)
- cb_grant_count (capacity building grants)
- intermediary_grant_count (TA/training/eval grants)
- phone
- website
- top_officer_name (prefer Executive Director > President > Trustee)
- top_officer_title
- segment (which segment they qualified for)
- segment_priority (1-6)

---

## Segment Definitions

### Segment 1: Intermediary Funders (Priority 1) - FULL EXTRACT
```sql
-- 10+ grants with TA/training/eval keywords, 50+ grantees, open, active 2022+
WHERE purpose_text ILIKE ANY(ARRAY['%evaluation%', '%training%', '%technical assistance%', '%consulting%', '%assessment%'])
HAVING COUNT(*) >= 10 AND COUNT(DISTINCT recipient_ein) >= 50
-- Filter: only_contri_to_preselected_ind = FALSE OR NULL
```

### Segment 2: High-Volume Regional (Priority 2) - FULL EXTRACT
```sql
-- 100+ grantees, >80% of grants to one state, open, active 2022+
-- Calculate: state_concentration = MAX(grants_to_state) / total_grants
WHERE state_concentration > 0.80
  AND grantee_count >= 100
-- Filter: only_contri_to_preselected_ind = FALSE OR NULL
```

### Segment 3: Large CB Foundations (Priority 3) - FULL EXTRACT
```sql
-- Assets >$100M, 50+ grantees, 5+ CB grants, open, active 2022+
WHERE total_assets_eoy_amt > 100000000
  AND grantee_count >= 50
  AND cb_grant_count >= 5
-- Filter: only_contri_to_preselected_ind = FALSE OR NULL
```

**CB Keywords:** capacity building, technical assistance, organizational development, general operating, operating support

### Segment 4: California CB (Priority 4) - SAMPLE 200
```sql
-- CA-based, 20+ grantees, 3+ CB grants, open, active 2022+
WHERE state = 'CA'
  AND grantee_count >= 20
  AND cb_grant_count >= 3
-- Random sample of 200
```

### Segment 5: Education Specialists (Priority 5) - SAMPLE 200
```sql
-- >50% grants to NTEE B%, 20+ grantees, open, active 2022+
-- Calculate education_pct from recipient NTEE codes
WHERE education_pct > 0.50
  AND grantee_count >= 20
```

### Segment 6: Random Baseline (Priority 6) - SAMPLE 200
```sql
-- Any foundation with 10+ grantees, active 2022+, open
-- Random sample for control group
WHERE grantee_count >= 10
ORDER BY RANDOM()
LIMIT 200
```

---

## Notes

- A foundation can appear in multiple segments; assign to HIGHEST priority segment only
- Phone/website from pf_returns table
- Officer data from pf_officers; dedupe by foundation, pick best title
- Active = has grants in tax_year >= 2022
- Open = only_contri_to_preselected_ind is FALSE or NULL

---

## Deliverables

1. `OUTPUT_2025-12-16_foundation_b2b_segments.csv` - All extracted foundations
2. Brief summary: counts per segment, any data quality issues

---

## Reference

- Schema: f990_2025
- Tables: pf_returns, pf_officers, fact_grants
- Prior report has working SQL snippets for most segments
