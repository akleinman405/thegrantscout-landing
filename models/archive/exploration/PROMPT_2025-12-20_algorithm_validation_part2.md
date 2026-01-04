# PROMPT: Matching Algorithm Validation - Part 2: Optimize & Finalize

**Date:** 2025-12-20
**For:** Claude Code CLI
**Schema:** f990_2025
**Prerequisite:** Part 1 complete (baseline results exist)

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

Part 1 established:
- Test set of nonprofits with train/test split (2013-2022 / 2023-2024)
- Baseline metrics for each signal in isolation
- Random baseline for comparison

**Goal:** Find optimal signal weights, validate on real clients, and produce final algorithm spec with defensible accuracy claims.

**Part 1 Finding:** Semantic similarity underperformed (4x random vs 52x for collaborative). Hypothesis: generic grant purposes ("general support", "charitable purposes") add noise to embeddings.

---

## Task 1: Semantic Signal Investigation

Before combining signals, test whether filtering generic grants improves semantic matching.

### 1A: Analyze Grant Purpose Quality

```sql
-- What % of grants have generic/short purposes?
SELECT 
    CASE 
        WHEN purpose_text IS NULL OR purpose_text = '' THEN 'empty'
        WHEN purpose_text ~* 'general.*(support|operating|purpose)' THEN 'generic'
        WHEN purpose_text ~* '^(charitable|contribution|grant|donation)' THEN 'generic'
        WHEN length(purpose_text) < 30 THEN 'too_short'
        ELSE 'specific'
    END as purpose_quality,
    COUNT(*) as grants,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM f990_2025.fact_grants
GROUP BY 1
ORDER BY grants DESC;
```

### 1B: Re-run Semantic with Filtered Grants

Test semantic similarity using ONLY specific grant purposes (exclude generic/short).

```sql
-- Create filtered grant embeddings view
-- Only include grants with meaningful purpose text
CREATE OR REPLACE VIEW f990_2025.filtered_grant_embeddings AS
SELECT ge.*
FROM f990_2025.grant_embeddings ge
JOIN f990_2025.fact_grants fg ON ge.grant_id = fg.id
WHERE fg.purpose_text IS NOT NULL
  AND length(fg.purpose_text) >= 50
  AND fg.purpose_text !~* 'general.*(support|operating|purpose)'
  AND fg.purpose_text !~* '^(charitable|contribution|grant|donation)';

-- Check: how many grants remain after filtering?
SELECT COUNT(*) as filtered_grants,
       (SELECT COUNT(*) FROM f990_2025.grant_embeddings) as total_grants,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM f990_2025.grant_embeddings), 1) as pct_remaining
FROM f990_2025.filtered_grant_embeddings;
```

### 1C: Compare Filtered vs Unfiltered Semantic

Run semantic matching on same sample of test nonprofits, compare:

| Version | Hit Rate@100 | vs Random | Improvement |
|---------|--------------|-----------|-------------|
| Unfiltered (Part 1) | 2.00% | 4x | baseline |
| Filtered (specific only) | ?% | ?x | ? |

**If filtered semantic improves significantly (>15x random):** Include filtered semantic in combination tests.
**If no improvement:** Deprioritize semantic signal; focus on collaborative + NTEE + geographic.

### 1D: Document Findings

Record:
- % of grants filtered out
- Impact on semantic performance
- Recommendation for whether to include semantic in final algorithm

---

## Task 2: Combination Tests

Test weighted combinations of signals to find optimal blend.

### 2A: Load Baseline Results

```sql
-- Verify Part 1 outputs exist
SELECT 'semantic' as signal, COUNT(*) FROM f990_2025.validation_semantic_results
UNION ALL
SELECT 'collaborative', COUNT(*) FROM f990_2025.validation_collaborative_results
UNION ALL
SELECT 'geographic', COUNT(*) FROM f990_2025.validation_geographic_results;
```

### 2B: Normalize Scores

Each signal has different scales. Normalize to 0-1 before combining.

```sql
-- Create normalized scores table
CREATE TABLE f990_2025.validation_normalized_scores AS
SELECT 
    recipient_ein,
    foundation_ein,
    -- Min-max normalization per nonprofit
    (semantic_score - MIN(semantic_score) OVER (PARTITION BY recipient_ein)) /
    NULLIF(MAX(semantic_score) OVER (PARTITION BY recipient_ein) - 
           MIN(semantic_score) OVER (PARTITION BY recipient_ein), 0) as semantic_norm,
    -- Repeat for other signals...
    collaborative_score,
    geographic_score,
    sector_score
FROM (
    -- Join all signal results
    SELECT 
        s.recipient_ein,
        s.foundation_ein,
        s.similarity as semantic_score,
        COALESCE(c.sibling_count, 0) as collaborative_score,
        COALESCE(g.geo_match, 0) as geographic_score,
        COALESCE(n.sector_match, 0) as sector_score
    FROM f990_2025.validation_semantic_results s
    LEFT JOIN f990_2025.validation_collaborative_results c 
        ON s.recipient_ein = c.recipient_ein AND s.foundation_ein = c.foundation_ein
    LEFT JOIN f990_2025.validation_geographic_results g
        ON s.recipient_ein = g.recipient_ein AND s.foundation_ein = g.foundation_ein
    -- Add sector join if available
) combined;
```

### 2C: Test Weight Configurations

Test these combinations:

| Config | Semantic | Collaborative | Geographic | Sector | Rationale |
|--------|----------|---------------|------------|--------|-----------|
| Equal | 0.25 | 0.25 | 0.25 | 0.25 | Baseline blend |
| Semantic-heavy | 0.50 | 0.25 | 0.15 | 0.10 | Trust embeddings |
| Collab-heavy | 0.25 | 0.50 | 0.15 | 0.10 | Trust network effects |
| Current spec | 0.30 | 0.25 | 0.20 | 0.15 | Existing intuition |
| Drop worst | Exclude lowest-performing signal from Part 1 |

```sql
-- Function to calculate combined score
CREATE OR REPLACE FUNCTION f990_2025.calc_combined_score(
    semantic float, collab float, geo float, sector float,
    w_semantic float, w_collab float, w_geo float, w_sector float
) RETURNS float AS $$
    SELECT semantic * w_semantic + collab * w_collab + geo * w_geo + sector * w_sector;
$$ LANGUAGE SQL;

-- Test each configuration
WITH config_1 AS (
    SELECT 
        recipient_ein,
        foundation_ein,
        f990_2025.calc_combined_score(
            semantic_norm, collaborative_norm, geographic_norm, sector_norm,
            0.25, 0.25, 0.25, 0.25  -- Equal weights
        ) as combined_score
    FROM f990_2025.validation_normalized_scores
),
ranked AS (
    SELECT 
        recipient_ein,
        foundation_ein,
        combined_score,
        ROW_NUMBER() OVER (PARTITION BY recipient_ein ORDER BY combined_score DESC) as rank
    FROM config_1
)
-- Calculate metrics for this config
SELECT 
    'equal_weights' as config,
    AVG(CASE WHEN has_hit_50 THEN 1.0 ELSE 0.0 END) as hit_rate_50,
    AVG(CASE WHEN has_hit_100 THEN 1.0 ELSE 0.0 END) as hit_rate_100,
    AVG(recall_50) as recall_50,
    AVG(recall_100) as recall_100,
    AVG(mrr) as mrr
FROM (
    SELECT 
        r.recipient_ein,
        MAX(CASE WHEN r.rank <= 50 AND r.foundation_ein = ANY(t.test_funders) THEN 1 ELSE 0 END) as has_hit_50,
        MAX(CASE WHEN r.rank <= 100 AND r.foundation_ein = ANY(t.test_funders) THEN 1 ELSE 0 END) as has_hit_100,
        -- Recall calculations
        COUNT(CASE WHEN r.rank <= 50 AND r.foundation_ein = ANY(t.test_funders) THEN 1 END)::float / 
            NULLIF(array_length(t.test_funders, 1), 0) as recall_50,
        COUNT(CASE WHEN r.rank <= 100 AND r.foundation_ein = ANY(t.test_funders) THEN 1 END)::float / 
            NULLIF(array_length(t.test_funders, 1), 0) as recall_100,
        -- MRR: 1/rank of first hit
        1.0 / MIN(CASE WHEN r.foundation_ein = ANY(t.test_funders) THEN r.rank END) as mrr
    FROM ranked r
    JOIN f990_2025.validation_test_nonprofits t ON r.recipient_ein = t.recipient_ein
    GROUP BY r.recipient_ein, t.test_funders
) per_nonprofit;

-- Repeat for each weight configuration
```

### 2D: Results Table

| Config | Hit@50 | Hit@100 | Recall@50 | Recall@100 | MRR | Notes |
|--------|--------|---------|-----------|------------|-----|-------|
| Equal weights | | | | | | |
| Semantic-heavy | | | | | | |
| Collab-heavy | | | | | | |
| Current spec | | | | | | |
| Best single signal | | | | | | From Part 1 |

**Select best configuration** based on Hit Rate@50 (primary) and MRR (secondary).

---

## Task 3: Real Client Validation

Test on actual beta clients with known funders.

### 3A: Load Client Data

```sql
-- Check dim_clients table structure
SELECT * FROM f990_2025.dim_clients LIMIT 5;

-- Get clients with known_funders populated
SELECT 
    id, 
    name, 
    ein,
    known_funders,
    array_length(known_funders, 1) as num_known_funders
FROM f990_2025.dim_clients
WHERE known_funders IS NOT NULL;
```

### 3B: Run Algorithm for Each Client

```sql
-- For each client, generate top 100 recommendations using best weights from Task 1
-- Then check: do known_funders appear in the list?

WITH client_recs AS (
    -- Generate recommendations for client using optimal weights
    SELECT 
        c.id as client_id,
        c.name as client_name,
        c.known_funders,
        f.ein as foundation_ein,
        -- Combined score with optimal weights (fill in from Task 1)
        (semantic_score * 0.XX + collab_score * 0.XX + geo_score * 0.XX) as score,
        ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY combined_score DESC) as rank
    FROM f990_2025.dim_clients c
    CROSS JOIN f990_2025.dim_foundations f
    -- Join to get scores (adapt based on actual table structure)
),
client_hits AS (
    SELECT 
        client_id,
        client_name,
        array_length(known_funders, 1) as num_known,
        COUNT(CASE WHEN rank <= 50 AND foundation_ein = ANY(known_funders) THEN 1 END) as hits_in_50,
        COUNT(CASE WHEN rank <= 100 AND foundation_ein = ANY(known_funders) THEN 1 END) as hits_in_100,
        MIN(CASE WHEN foundation_ein = ANY(known_funders) THEN rank END) as first_hit_rank,
        array_agg(foundation_ein ORDER BY rank) FILTER (WHERE rank <= 10) as top_10_recs
    FROM client_recs
    GROUP BY client_id, client_name, known_funders
)
SELECT 
    client_name,
    num_known as known_funders,
    hits_in_50,
    hits_in_100,
    ROUND(100.0 * hits_in_50 / num_known, 1) as recall_50_pct,
    ROUND(100.0 * hits_in_100 / num_known, 1) as recall_100_pct,
    first_hit_rank,
    top_10_recs
FROM client_hits
ORDER BY client_name;
```

### 3C: Client Validation Summary

| Client | Known Funders | Hits in Top 50 | Hits in Top 100 | First Hit Rank |
|--------|---------------|----------------|-----------------|----------------|
| PSMF | | | | |
| RHF | | | | |
| SNS | | | | |
| VetsBoats | | | | |
| ... | | | | |

**Qualitative check:** Review top 10 recommendations for 2-3 clients. Do they make sense even if not in known_funders? (These are the "new discovery" recommendations we actually sell.)

---

## Task 4: Segment Analysis

Does algorithm perform differently for different nonprofit types?

### 4A: By Nonprofit Size (Revenue)

```sql
-- Split test nonprofits by revenue tier
WITH nonprofit_tiers AS (
    SELECT 
        t.recipient_ein,
        CASE 
            WHEN r.total_revenue < 500000 THEN 'small'
            WHEN r.total_revenue < 2000000 THEN 'medium'
            ELSE 'large'
        END as size_tier
    FROM f990_2025.validation_test_nonprofits t
    LEFT JOIN f990_2025.dim_recipients r ON r.ein = t.recipient_ein
)
-- Calculate metrics by tier
SELECT 
    size_tier,
    COUNT(*) as num_nonprofits,
    AVG(hit_rate_50) as avg_hit_rate_50,
    AVG(recall_100) as avg_recall_100
FROM nonprofit_tiers nt
JOIN validation_results vr ON nt.recipient_ein = vr.recipient_ein
GROUP BY size_tier;
```

### 4B: By Number of Historical Funders

```sql
-- Nonprofits with more history should match better (more collaborative signal)
SELECT 
    CASE 
        WHEN train_funder_count <= 5 THEN '3-5 funders'
        WHEN train_funder_count <= 10 THEN '6-10 funders'
        ELSE '10+ funders'
    END as funder_tier,
    COUNT(*) as num_nonprofits,
    AVG(hit_rate_50) as avg_hit_rate_50,
    AVG(recall_100) as avg_recall_100
FROM f990_2025.validation_test_nonprofits t
JOIN validation_results vr ON t.recipient_ein = vr.recipient_ein
GROUP BY 1;
```

### 4C: Cold Start Performance

For nonprofits with NO historical funders (new orgs), algorithm relies only on content signals.

```sql
-- Find nonprofits with 2023-24 grants but NO 2013-2022 grants
-- These simulate "new customers" with no funding history
WITH cold_start_nonprofits AS (
    SELECT DISTINCT recipient_ein
    FROM f990_2025.fact_grants
    WHERE tax_year >= 2023 AND recipient_ein IS NOT NULL
    AND recipient_ein NOT IN (
        SELECT DISTINCT recipient_ein 
        FROM f990_2025.fact_grants 
        WHERE tax_year <= 2022 AND recipient_ein IS NOT NULL
    )
)
-- Run semantic-only matching for these
-- Report performance vs nonprofits WITH history
```

**Key question:** How much worse is semantic-only vs hybrid? This tells us what new customers can expect.

---

## Task 5: Threshold Analysis

At what score do we have confidence in a recommendation?

### 5A: Score Distribution by Outcome

```sql
-- Compare score distributions: actual funders vs non-funders
SELECT 
    CASE WHEN is_actual_funder THEN 'Actual Funder' ELSE 'Non-Funder' END as category,
    percentile_cont(0.25) WITHIN GROUP (ORDER BY combined_score) as p25,
    percentile_cont(0.50) WITHIN GROUP (ORDER BY combined_score) as median,
    percentile_cont(0.75) WITHIN GROUP (ORDER BY combined_score) as p75,
    percentile_cont(0.90) WITHIN GROUP (ORDER BY combined_score) as p90
FROM (
    SELECT 
        combined_score,
        foundation_ein = ANY(test_funders) as is_actual_funder
    FROM f990_2025.validation_normalized_scores s
    JOIN f990_2025.validation_test_nonprofits t ON s.recipient_ein = t.recipient_ein
) scored
GROUP BY 1;
```

### 5B: Precision-Recall at Different Thresholds

```sql
-- If we only show recommendations above threshold X, what's precision?
WITH thresholds AS (
    SELECT generate_series(0.3, 0.8, 0.05) as threshold
)
SELECT 
    t.threshold,
    COUNT(CASE WHEN s.combined_score >= t.threshold AND is_actual THEN 1 END) as true_positives,
    COUNT(CASE WHEN s.combined_score >= t.threshold AND NOT is_actual THEN 1 END) as false_positives,
    COUNT(CASE WHEN s.combined_score >= t.threshold AND is_actual THEN 1 END)::float /
        NULLIF(COUNT(CASE WHEN s.combined_score >= t.threshold THEN 1 END), 0) as precision,
    COUNT(CASE WHEN s.combined_score >= t.threshold AND is_actual THEN 1 END)::float /
        NULLIF(COUNT(CASE WHEN is_actual THEN 1 END), 0) as recall
FROM thresholds t
CROSS JOIN (
    SELECT combined_score, foundation_ein = ANY(test_funders) as is_actual
    FROM validation_scores_with_labels
) s
GROUP BY t.threshold
ORDER BY t.threshold;
```

**Recommend:** Threshold for "high confidence" matches (show in report) vs "worth exploring" (show as secondary).

---

## Task 6: Final Recommendations

### 6A: Optimal Algorithm Specification

Based on experiments, document:

```yaml
algorithm:
  name: "TheGrantScout Matching Algorithm v1.0"
  method: "Weighted Hybrid (Semantic + Collaborative + Geographic + Sector)"
  
  weights:
    semantic_similarity: 0.XX  # From Task 1 (if improved) or deprioritize
    collaborative_filtering: 0.XX  # From Task 2
    geographic_match: 0.XX
    sector_match: 0.XX
    
  thresholds:
    high_confidence: 0.XX  # Show in main report
    worth_exploring: 0.XX  # Show as secondary
    minimum: 0.XX  # Below this, don't show
    
  performance:
    hit_rate_50: XX%
    recall_100: XX%
    mrr: 0.XX
    vs_random: XXx better
```

### 6B: Defensible Accuracy Claim

Write 1-2 sentences for marketing:

> "TheGrantScout's matching algorithm identifies foundations [X]x more accurately than random search, successfully surfacing actual funders in the top 50 recommendations for [Y]% of nonprofits tested."

### 6C: Known Limitations

Document where algorithm performs poorly:
- Cold start (new nonprofits with no history): Performance = X%
- Generic missions: Performance = X%
- Niche sectors with few foundations: Performance = X%

### 6D: Improvement Roadmap

What would make it better?
1. More EIN coverage (currently 55.8%)
2. Add grant size matching signal
3. Add foundation "openness" signal (% new grantees)
4. Recency weighting (recent grants weighted higher)

---

## Validation Checkpoint

Before finalizing, verify your work:

1. **Semantic Investigation Check**
   - What % of grants were filtered out?
   - Did filtered semantic improve meaningfully (>15x random)?
   - Is the decision to include/exclude semantic in combination tests justified?

2. **Combination Test Validation**
   - Do different weight configs produce meaningfully different results?
   - Does the best combo outperform the best single signal? (If not, investigate)
   - Is the winning config stable? (Re-run on different sample to confirm)

3. **Client Validation Sanity Check**
   - For clients with known_funders, do ANY appear in top 100?
   - If zero hits for a client, investigate — is their data correct in dim_clients?
   - Do the top 10 recommendations for each client make intuitive sense?

4. **Threshold Validation**
   - Is there clear separation between funder and non-funder score distributions?
   - Does the recommended threshold balance precision vs recall appropriately?

5. **Final Spec Review**
   - Are the weights and thresholds internally consistent?
   - Is the accuracy claim supported by the data?
   - Are limitations clearly documented?

6. **Cross-Check with Part 1**
   - Do Part 2 results align with Part 1 baselines?
   - Any unexpected discrepancies?

Flag any anomalies or concerns in your final report.

---

## Deliverables

| File | Contents |
|------|----------|
| `REPORT_2025-12-20_semantic_investigation.md` | Filtered vs unfiltered semantic results |
| `SPEC_2025-12-20_matching_algorithm_final.md` | Final algorithm with validated weights |
| `REPORT_2025-12-20_optimization_results.md` | All experiment results, analysis |
| `REPORT_2025-12-20_client_validation.md` | Beta client test results |
| SQL tables | `validation_normalized_scores`, combination results |

---

## Key Questions Answered

1. **Does filtering generic grants improve semantic?** → Task 1 results
2. **What are optimal weights?** → From Task 2 experiments
3. **What accuracy can we claim?** → Hit Rate@50 = X%, Yx better than random
4. **Does it work for real clients?** → Task 3 results
5. **Where does it fail?** → Task 4 segment analysis
6. **What score = "good match"?** → Task 5 threshold analysis

---

## Success Criteria

- [ ] Optimal weights empirically determined (not guessed)
- [ ] Hit Rate@50 > 20% (or document why lower is acceptable)
- [ ] At least 5/7 beta clients have known funders in top 100
- [ ] Clear accuracy claim for marketing
- [ ] Known limitations documented
- [ ] Final algorithm spec ready for production implementation
