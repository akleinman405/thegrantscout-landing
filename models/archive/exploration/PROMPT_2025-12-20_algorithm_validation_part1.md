# PROMPT: Matching Algorithm Validation - Part 1: Framework & Baselines

**Date:** 2025-12-20
**For:** Claude Code CLI
**Schema:** f990_2025

---

## Instructions

Work continuously until all tasks are complete. Take your time and do thorough, high-quality work. After completing each major task, pause to validate your own results before moving on:
- Check that row counts and statistics make sense
- Verify SQL logic is correct
- Confirm outputs match expected formats
- If something looks wrong, investigate and fix before proceeding

When you complete all tasks, do a final review of all outputs and flag any concerns or anomalies.

---

## Situation

We're validating a foundation-nonprofit matching algorithm. Current state:
- 8.3M grants from 143K foundations to 264K recipients
- 55.8% of grants have recipient EIN (enables collaborative filtering)
- 100% semantic embedding coverage in `grant_embeddings` table
- Current algorithm uses intuition-based weights — need empirical validation

**Goal:** Create a validation framework and establish baseline performance for each signal type so we can make defensible accuracy claims.

---

## Task 1: Create Holdout Test Set

Use **time-based split** — this best simulates real use (predicting future grants from past patterns).

### 1A: Define Train/Test Split

```sql
-- Training set: 2013-2022 grants
-- Test set: 2023-2024 grants (most recent, best data quality)

-- First, understand the data distribution
SELECT tax_year, COUNT(*) as grant_count,
       COUNT(DISTINCT foundation_ein) as foundations,
       COUNT(DISTINCT recipient_ein) FILTER (WHERE recipient_ein IS NOT NULL) as recipients_with_ein
FROM f990_2025.fact_grants
GROUP BY tax_year
ORDER BY tax_year;
```

### 1B: Create Test Set of Nonprofits

Select nonprofits that:
1. Have recipient_ein populated
2. Received grants in BOTH periods (so we can test prediction)
3. Have 3+ funders in training period (enough signal for collaborative filtering)

```sql
-- Find nonprofits with grants in both periods
CREATE TABLE f990_2025.validation_test_nonprofits AS
WITH training_funders AS (
    SELECT recipient_ein, array_agg(DISTINCT foundation_ein) as train_funders,
           COUNT(DISTINCT foundation_ein) as train_funder_count
    FROM f990_2025.fact_grants
    WHERE tax_year <= 2022 AND recipient_ein IS NOT NULL
    GROUP BY recipient_ein
    HAVING COUNT(DISTINCT foundation_ein) >= 3
),
test_funders AS (
    SELECT recipient_ein, array_agg(DISTINCT foundation_ein) as test_funders,
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

-- Report: How many test nonprofits do we have?
SELECT COUNT(*) as test_nonprofits,
       AVG(train_funder_count) as avg_train_funders,
       AVG(test_funder_count) as avg_test_funders
FROM f990_2025.validation_test_nonprofits;
```

**Target:** At least 1,000 test nonprofits with 3+ training funders each.

### 1C: Document the "New vs Known" Challenge

Note: We validate on KNOWN relationships but customers want UNKNOWN foundations. The bridge:
- If our algorithm can "rediscover" relationships that formed in 2023-2024 using only 2013-2022 data, it can also find NEW foundations the nonprofit hasn't discovered yet.
- A foundation that funded similar orgs is a good candidate regardless of whether they've funded this specific org.

---

## Task 2: Define Success Metrics

### Primary Metrics

| Metric | Definition | Formula |
|--------|------------|---------|
| **Hit Rate@K** | Did ANY actual 2023-24 funder appear in top K recommendations? | # nonprofits with ≥1 hit / total nonprofits |
| **Recall@K** | What fraction of actual 2023-24 funders appear in top K? | Avg(# hits in top K / # actual funders) |
| **MRR** | Average reciprocal rank of first correct match | Avg(1 / rank of first hit) |

### Baseline Calculation

**Random baseline for context:**
- 143K foundations total
- Average nonprofit has ~5 actual funders among 143K
- Random Recall@100 = 100/143,000 × 5 ≈ 0.0035 (0.35%)
- Random Hit Rate@100 ≈ 1 - (142,995/143,000)^100 ≈ 0.35%

Any score significantly above this is "better than random."

### Meaningful Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Hit Rate@50 | >20% | 1 in 5 nonprofits finds actual funder in top 50 |
| Recall@100 | >5% | Find 5% of actual funders in top 100 (14x random) |
| MRR | >0.02 | First hit typically in top 50 |

---

## Task 3: Calculate Random Baseline

```sql
-- For each test nonprofit, simulate random selection
-- Calculate expected hit rate under random

WITH test_stats AS (
    SELECT 
        recipient_ein,
        array_length(test_funders, 1) as num_actual_funders,
        (SELECT COUNT(DISTINCT ein) FROM f990_2025.dim_foundations) as total_foundations
    FROM f990_2025.validation_test_nonprofits
)
SELECT 
    AVG(num_actual_funders) as avg_actual_funders,
    AVG(total_foundations) as total_foundations,
    -- Probability of hitting at least one funder in random K selections
    -- P(hit) ≈ 1 - (1 - num_funders/total)^K
    AVG(1 - POWER(1 - num_actual_funders::float/total_foundations, 50)) as random_hitrate_50,
    AVG(1 - POWER(1 - num_actual_funders::float/total_foundations, 100)) as random_hitrate_100
FROM test_stats;
```

---

## Task 4: Single-Signal Tests

Test each signal in isolation to understand its predictive power.

### 4A: Semantic Similarity Only

For each test nonprofit, rank foundations by semantic similarity to their mission/grants.

```sql
-- Approach: 
-- 1. Get nonprofit's historical grant embeddings (from grants they received 2013-2022)
-- 2. For each foundation, get their grant embeddings
-- 3. Compute average similarity
-- 4. Rank foundations by similarity
-- 5. Check where actual 2023-24 funders rank

-- Sample test on 100 nonprofits first (full test takes longer)
-- Use cosine similarity: 1 - (embedding <=> other_embedding)

-- NOTE: Adapt based on actual embedding table structure
-- grant_embeddings likely has: grant_id, embedding vector
-- Need to join to fact_grants to get foundation_ein and recipient_ein
```

**Output needed:**
- For each test nonprofit: ranked list of top 500 foundations
- Calculate: Hit Rate@50, Hit Rate@100, Recall@50, Recall@100, MRR
- Store results in: `f990_2025.validation_semantic_results`

### 4B: Collaborative Filtering Only

Foundations that funded similar nonprofits (shared recipients = similarity).

```sql
-- For test nonprofit X with training funders F1, F2, F3:
-- 1. Find OTHER nonprofits also funded by F1, F2, F3
-- 2. Find what OTHER foundations funded those nonprofits
-- 3. Rank by: how many "sibling" nonprofits did this foundation fund?

WITH nonprofit_siblings AS (
    -- Nonprofits that share funders with test nonprofit
    SELECT 
        t.recipient_ein as test_nonprofit,
        g.recipient_ein as sibling_nonprofit,
        COUNT(DISTINCT g.foundation_ein) as shared_funders
    FROM f990_2025.validation_test_nonprofits t
    JOIN f990_2025.fact_grants g 
        ON g.foundation_ein = ANY(t.train_funders)
        AND g.recipient_ein != t.recipient_ein
        AND g.tax_year <= 2022
        AND g.recipient_ein IS NOT NULL
    GROUP BY t.recipient_ein, g.recipient_ein
    HAVING COUNT(DISTINCT g.foundation_ein) >= 2  -- At least 2 shared funders
),
candidate_foundations AS (
    -- Foundations that funded sibling nonprofits
    SELECT 
        s.test_nonprofit,
        g.foundation_ein,
        COUNT(DISTINCT s.sibling_nonprofit) as sibling_count,
        SUM(s.shared_funders) as total_shared_signal
    FROM nonprofit_siblings s
    JOIN f990_2025.fact_grants g 
        ON g.recipient_ein = s.sibling_nonprofit
        AND g.tax_year <= 2022
    -- Exclude foundations already in training set
    JOIN f990_2025.validation_test_nonprofits t 
        ON t.recipient_ein = s.test_nonprofit
        AND NOT (g.foundation_ein = ANY(t.train_funders))
    GROUP BY s.test_nonprofit, g.foundation_ein
)
SELECT * FROM candidate_foundations
ORDER BY test_nonprofit, sibling_count DESC;
```

**Output needed:**
- Same metrics as semantic test
- Store in: `f990_2025.validation_collaborative_results`

### 4C: Geographic Match Only

Foundations prefer local grantees (same state).

```sql
-- Rank foundations by geographic match
-- 1 = same state, 0 = different state
-- Within same state, rank by total giving (larger = more capacity)

WITH nonprofit_states AS (
    SELECT DISTINCT 
        t.recipient_ein,
        r.state as nonprofit_state
    FROM f990_2025.validation_test_nonprofits t
    JOIN f990_2025.dim_recipients r ON r.ein = t.recipient_ein
),
foundation_states AS (
    SELECT 
        ein as foundation_ein,
        state as foundation_state,
        total_giving
    FROM f990_2025.dim_foundations
)
SELECT 
    n.recipient_ein,
    f.foundation_ein,
    CASE WHEN n.nonprofit_state = f.foundation_state THEN 1 ELSE 0 END as geo_match,
    f.total_giving
FROM nonprofit_states n
CROSS JOIN foundation_states f
ORDER BY n.recipient_ein, geo_match DESC, f.total_giving DESC;
```

**Output needed:**
- Same metrics
- Store in: `f990_2025.validation_geographic_results`

### 4D: NTEE Sector Match Only

Foundations tend to fund within sectors.

```sql
-- Match foundation's historical sector focus to nonprofit's sector
-- Foundation sector = mode of NTEE codes they've funded
-- Nonprofit sector = their NTEE code from IRS BMF

-- This requires NTEE data - check if available in dim_recipients or nonprofit_returns
```

---

## Task 5: Summarize Baseline Results

Create summary table:

| Signal | Hit Rate@50 | Hit Rate@100 | Recall@50 | Recall@100 | MRR | vs Random |
|--------|-------------|--------------|-----------|------------|-----|-----------|
| Random Baseline | X% | X% | X% | X% | X | 1x |
| Semantic Only | X% | X% | X% | X% | X | Xx |
| Collaborative Only | X% | X% | X% | X% | X | Xx |
| Geographic Only | X% | X% | X% | X% | X | Xx |
| Sector Only | X% | X% | X% | X% | X | Xx |

---

## Validation Checkpoint

Before finalizing, verify your work:

1. **Test Set Sanity Check**
   - Does the number of test nonprofits make sense? (expect 1,000+)
   - Are train_funders and test_funders arrays non-overlapping as expected?
   - Do a spot check: pick 3 random nonprofits and manually verify their funders

2. **Baseline Sanity Check**
   - Is random baseline extremely low? (should be <1%)
   - Do the metrics calculate correctly? Run a manual example.

3. **Signal Test Validation**
   - For semantic: are similarity scores in expected range (0-1)?
   - For collaborative: do results exist only for nonprofits WITH historical funders?
   - For geographic: is the geo_match flag binary (0 or 1)?
   - Compare top-ranked foundations for one test nonprofit across signals — do they differ as expected?

4. **Results Cross-Check**
   - Does the best single signal outperform random by at least 10x?
   - If not, investigate — something may be wrong with the test setup

Flag any anomalies in your final report.

---

## Deliverables

| File | Contents |
|------|----------|
| `SPEC_2025-12-20_validation_framework.md` | Test set definition, metrics, methodology |
| `REPORT_2025-12-20_baseline_results.md` | Results table, analysis, which signals work |
| `f990_2025.validation_test_nonprofits` | Test set table |
| `f990_2025.validation_*_results` | Raw results for each signal test |

---

## Key Questions to Answer

1. **How many test nonprofits qualify?** (target: 1,000+)
2. **Which single signal performs best?** (likely semantic or collaborative)
3. **How much better than random is each signal?**
4. **Are any signals useless?** (not worth including in final algorithm)
5. **What's the upper bound?** (best single signal sets ceiling for hybrid)

---

## Notes

- Start with sample of 100 nonprofits for quick iteration, then run full test
- Semantic similarity computation is expensive — may need batching
- Collaborative filtering only works for nonprofits WITH historical funders (55.8% of grants)
- Geographic and sector are fast to compute
- Save all intermediate results — Part 2 will use them for optimization
