# SPEC: Matching Algorithm Validation Framework

**Date:** 2025-12-20
**Version:** 1.0
**Schema:** f990_2025

---

## Overview

This specification defines the validation framework for TheGrantScout's foundation-nonprofit matching algorithm. The framework uses time-based splitting to simulate real-world prediction tasks and establishes baseline performance for each signal type.

---

## Test Set Definition

### Data Split Strategy

**Time-based split** simulates real use (predicting future grants from past patterns):

| Period | Years | Grants | Purpose |
|--------|-------|--------|---------|
| Training | 2016-2022 | 6.4M | Build signals, learn patterns |
| Test | 2023-2024 | 1.9M | Validate predictions |

### Test Data Distribution by Year

| Tax Year | Grants | Foundations | Recipients with EIN |
|----------|--------|-------------|---------------------|
| 2016 | 1,171 | 110 | 421 |
| 2017 | 102,595 | 5,882 | 27,125 |
| 2018 | 937,249 | 61,168 | 124,433 |
| 2019 | 1,143,440 | 70,777 | 143,860 |
| 2020 | 1,587,184 | 89,052 | 174,632 |
| 2021 | 969,218 | 64,479 | 134,969 |
| 2022 | 1,684,257 | 93,397 | 193,073 |
| **2023** | 1,611,609 | 91,314 | 195,111 |
| **2024** | 273,927 | 22,293 | 67,255 |

### Test Nonprofit Selection Criteria

Nonprofits in the test set must:

1. **Have recipient_ein populated** (enables entity matching)
2. **Received grants in BOTH periods** (can test prediction)
3. **Have 3+ funders in training period** (enough signal for collaborative filtering)

**Result:** 92,829 test nonprofits qualify

### Test Set Statistics

| Metric | Value |
|--------|-------|
| Test nonprofits | 92,829 |
| Avg training funders per nonprofit | 14.9 |
| Avg test funders per nonprofit | 7.9 |
| Min training funders | 3 |
| Max training funders | 5,202 |

### Distribution of Training Funder Counts

| Range | Nonprofits | Percentage |
|-------|------------|------------|
| 3-5 | 39,523 | 42.6% |
| 6-10 | 24,005 | 25.9% |
| 11-20 | 15,727 | 16.9% |
| 21-50 | 9,792 | 10.5% |
| 50+ | 3,782 | 4.1% |

---

## Database Table

```sql
-- Table: f990_2025.validation_test_nonprofits
CREATE TABLE f990_2025.validation_test_nonprofits AS
WITH training_funders AS (
    SELECT recipient_ein,
           array_agg(DISTINCT foundation_ein) as train_funders,
           COUNT(DISTINCT foundation_ein) as train_funder_count
    FROM f990_2025.fact_grants
    WHERE tax_year <= 2022 AND recipient_ein IS NOT NULL
    GROUP BY recipient_ein
    HAVING COUNT(DISTINCT foundation_ein) >= 3
),
test_funders AS (
    SELECT recipient_ein,
           array_agg(DISTINCT foundation_ein) as test_funders,
           COUNT(DISTINCT foundation_ein) as test_funder_count
    FROM f990_2025.fact_grants
    WHERE tax_year >= 2023 AND recipient_ein IS NOT NULL
    GROUP BY recipient_ein
)
SELECT
    t.recipient_ein,
    tr.train_funders,
    tr.train_funder_count,
    t.test_funders,
    t.test_funder_count
FROM test_funders t
JOIN training_funders tr ON t.recipient_ein = tr.recipient_ein;
```

---

## Success Metrics

### Primary Metrics

| Metric | Definition | Formula |
|--------|------------|---------|
| **Hit Rate@K** | Did ANY actual 2023-24 funder appear in top K recommendations? | # nonprofits with ≥1 hit / total nonprofits |
| **Recall@K** | What fraction of actual 2023-24 funders appear in top K? | Avg(# hits in top K / # actual funders) |
| **MRR** | Mean Reciprocal Rank of first correct match | Avg(1 / rank of first hit) |

### K Values Tested

- **K=50**: Represents a focused recommendation list
- **K=100**: Represents a broader discovery set

### Random Baseline Calculation

With 143,184 total foundations and avg 7.9 test funders per nonprofit:

- Random Hit Rate@50 ≈ 0.27%
- Random Hit Rate@100 ≈ 0.53%
- Random Recall@50 ≈ 0.27%
- Random Recall@100 ≈ 0.55%
- Random MRR ≈ 0.000055

**Interpretation:** Any algorithm significantly above these baselines is demonstrating predictive power.

---

## Signal Definitions

### 1. Collaborative Filtering

**Logic:** Foundations that funded similar nonprofits (shared recipients = similarity).

```
For test nonprofit X with training funders F1, F2, F3:
1. Find OTHER nonprofits also funded by F1, F2, F3 (siblings)
2. Find what OTHER foundations funded those siblings
3. Rank by: how many "sibling" nonprofits did this foundation fund?
```

**Strengths:** Captures implicit relationships; works across sectors.

### 2. NTEE Sector Match

**Logic:** Foundations tend to fund within sectors.

```
1. Compute foundation's historical sector distribution (NTEE broad codes)
2. Rank foundations by their preference for the nonprofit's sector
```

**Strengths:** Simple, interpretable; works even with limited history.

### 3. Geographic Match

**Logic:** Foundations prefer local grantees (same state).

```
1. Match foundation state to nonprofit state
2. Within same state, rank by foundation assets (capacity)
3. Out-of-state foundations ranked lower
```

**Strengths:** Very fast to compute; captures local giving bias.

### 4. Semantic Similarity

**Logic:** Grant purpose embeddings capture thematic alignment.

```
1. Compute nonprofit's grant profile (avg embedding of received grants)
2. Compute foundation's grant profile (avg embedding of made grants)
3. Rank by cosine similarity
```

**Strengths:** Captures nuanced thematic matching; works across sectors.
**Limitations:** Computationally expensive; requires embeddings.

---

## Validation Methodology

### Testing Protocol

1. For each test nonprofit:
   a. Use ONLY training period data (2016-2022) to rank foundations
   b. Exclude known funders from ranking (test discovery of NEW funders)
   c. Generate top 100 recommendations
   d. Check against actual 2023-2024 funders

2. Aggregate metrics across all test nonprofits

### Sample Sizes

| Signal | Sample Size | Rationale |
|--------|-------------|-----------|
| Geographic | 200 | Fast computation |
| Collaborative | 200 | Moderate complexity |
| NTEE Sector | 200 | Fast computation |
| Semantic | 100 | High computational cost |

---

## The "New vs Known" Challenge

**Note:** We validate on relationships that formed in 2023-2024, but customers want to discover UNKNOWN foundations.

**Why this validation still works:**
- If our algorithm can "rediscover" relationships that formed in 2023-2024 using only 2013-2022 data, it can also find NEW foundations the nonprofit hasn't discovered yet
- A foundation that funded similar orgs is a good candidate regardless of whether they've funded this specific org
- High recall on test set indicates the algorithm surfaces relevant matches

---

## Quality Checks

Before trusting results, verify:

1. **Test Set Sanity**
   - Number of test nonprofits is reasonable (expect 1,000+)
   - Train/test funders are computed correctly
   - Spot check random nonprofits manually

2. **Baseline Sanity**
   - Random baseline is extremely low (<1%)
   - Best signals outperform random by at least 10x

3. **Signal Sanity**
   - Semantic: similarity scores in [0,1] range
   - Collaborative: only works for nonprofits WITH historical funders
   - Geographic: geo_match is binary (0 or 1)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-20 | 1.0 | Initial framework specification |
