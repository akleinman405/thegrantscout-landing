# SPEC: TheGrantScout Matching Algorithm v1.0 (Final)

**Date:** 2025-12-20
**Status:** Validated and Ready for Production
**Schema:** f990_2025

---

## Algorithm Overview

```yaml
algorithm:
  name: "TheGrantScout Matching Algorithm v1.0"
  method: "Collaborative Filtering with Content-Based Fallback"

  primary_signal:
    name: collaborative_filtering
    weight: 1.0
    description: "Foundations that funded similar nonprofits"

  fallback_signals:  # For cold start (no history)
    - name: sector_match
      weight: 0.6
      description: "Foundations that fund same NTEE sector"
    - name: geographic_match
      weight: 0.4
      description: "Same-state foundations"

  excluded_signals:
    - name: semantic_similarity
      reason: "Only 7x random; 81% of grant purposes too generic"

  performance:
    hit_rate_50: 26%
    hit_rate_100: 30%
    recall_100: 11.4%
    mrr: 0.077
    vs_random: 57x better
```

---

## How It Works

### Primary: Collaborative Filtering

For nonprofits with 3+ historical funders:

```
1. Find "sibling" nonprofits: organizations funded by the same foundations
   - Sibling threshold: shares at least 2 funders with target nonprofit

2. Find candidate foundations: what OTHER foundations funded those siblings?
   - Exclude foundations already known to the nonprofit

3. Rank by signal strength: how many siblings did each foundation fund?
   - More siblings = stronger collaborative signal

4. Return top 100 recommendations
```

### Fallback: Content-Based (Cold Start)

For nonprofits with <3 historical funders:

```
1. Match nonprofit's NTEE sector to foundation sector preferences
   - Score = foundation's % of grants in nonprofit's sector

2. Match geography: same-state bonus
   - Same state = 1.0, different state = 0.0

3. Combined score = 0.6 * sector_score + 0.4 * geo_score

4. Return top 100 by combined score
```

---

## Validated Performance

### Overall (Collaborative Filtering)

| Metric | Value | vs Random |
|--------|-------|-----------|
| Hit Rate@50 | 26.0% | 87x |
| Hit Rate@100 | 30.0% | 57x |
| Recall@100 | 11.4% | 21x |
| MRR | 0.077 | 1400x |

**Interpretation:** In 30% of cases, at least one actual future funder appears in the top 100 recommendations.

### By Nonprofit History Depth

| Historical Funders | Hit Rate@100 | Performance |
|-------------------|--------------|-------------|
| 3-5 funders | 10.9% | 21x random |
| 6-10 funders | 36.0% | 68x random |
| 11-20 funders | 42.0% | 79x random |
| 20+ funders | 48.0% | 91x random |

**Finding:** More history = dramatically better performance. Nonprofits with 20+ historical funders achieve 48% Hit Rate.

### Cold Start (Sector + Geographic)

| Signal | Hit Rate@100 | vs Random |
|--------|--------------|-----------|
| Sector alone | 22% | 42x |
| Geographic alone | 13% | 25x |
| Combined (0.6/0.4) | ~25% | ~47x (estimated) |

---

## Implementation Requirements

### Database Tables Needed

```sql
-- Test set (already created)
f990_2025.validation_test_nonprofits

-- Results (already created)
f990_2025.validation_signal_results

-- For production, consider pre-computing:
-- Foundation sector preferences
-- Foundation-nonprofit sibling relationships (materialized view)
```

### Key SQL Pattern

```sql
-- Collaborative filtering query
WITH sibling_nonprofits AS (
    SELECT recipient_ein, COUNT(DISTINCT foundation_ein) as shared_funders
    FROM f990_2025.fact_grants
    WHERE foundation_ein = ANY(client_funders)  -- Client's known funders
      AND recipient_ein != client_ein
      AND recipient_ein IS NOT NULL
      AND tax_year <= 2022
    GROUP BY recipient_ein
    HAVING COUNT(DISTINCT foundation_ein) >= 2
),
candidate_foundations AS (
    SELECT fg.foundation_ein, COUNT(DISTINCT s.recipient_ein) as sibling_count
    FROM sibling_nonprofits s
    JOIN f990_2025.fact_grants fg ON fg.recipient_ein = s.recipient_ein
    WHERE fg.tax_year <= 2022
      AND fg.foundation_ein != ALL(client_funders)  -- Exclude known
    GROUP BY fg.foundation_ein
)
SELECT foundation_ein, sibling_count
FROM candidate_foundations
ORDER BY sibling_count DESC
LIMIT 100;
```

---

## Defensible Accuracy Claim

> "TheGrantScout's matching algorithm identifies foundation matches **57x more accurately than random search**, successfully surfacing actual future funders in the top 100 recommendations for **30% of nonprofits tested**. Performance improves to **48% accuracy for organizations with rich funding history** (20+ historical funders)."

---

## Known Limitations

### 1. Cold Start Problem
- Nonprofits with <3 historical funders: collaborative signal unavailable
- Fall back to sector + geographic (lower accuracy: ~25% vs 30%)
- **Mitigation:** Content-based signals provide reasonable baseline

### 2. EIN Coverage Gap
- 44.2% of grants lack recipient EIN
- Limits collaborative signal for some nonprofits
- **Mitigation:** Future work to improve EIN matching

### 3. History Dependency
- New nonprofits perform worse than established ones
- 3-5 funders: 11% vs 20+ funders: 48%
- **Mitigation:** Set expectations appropriately for new orgs

### 4. Sector Concentration Bias
- Large sectors (Education, Health) have more data
- Niche sectors may have less signal
- **Mitigation:** Monitor by sector, adjust as needed

---

## What's NOT Included (and Why)

| Signal | Status | Reason |
|--------|--------|--------|
| Semantic Similarity | Excluded | Only 7x random; grant purposes too generic |
| Grant Size Matching | Not tested | Future improvement |
| Repeat Funding Rate | Not tested | Future improvement |
| Foundation Openness | Not tested | Future improvement |

---

## Future Improvements

### Priority 1: Production Optimization
1. Pre-compute sibling relationships (materialized view)
2. Cache foundation profiles
3. Index optimization for collaborative queries

### Priority 2: Signal Enhancement
1. Add grant size alignment signal
2. Add repeat funding rate signal
3. Add foundation "openness" (% new grantees)
4. Add recency weighting (recent grants weighted higher)

### Priority 3: Data Quality
1. Improve EIN matching (target: 80%+ coverage)
2. Enrich sector data for more recipients
3. Curate foundation profiles for semantic matching

---

## Validation Summary

| Checkpoint | Status | Notes |
|------------|--------|-------|
| Test set sanity | PASS | 92,829 nonprofits, well distributed |
| Random baseline | PASS | 0.53% as expected |
| Best signal > 10x random | PASS | 57x achieved |
| Combination improves single | FAIL | Single signal is best |
| Segment analysis | PASS | Clear trend with history |
| Client validation | PARTIAL | Limited client history |

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-20 | 1.0 | Initial validated specification |
