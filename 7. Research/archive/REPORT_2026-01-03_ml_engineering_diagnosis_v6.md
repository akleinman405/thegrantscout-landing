# ML Engineering Diagnosis: V6 Size Bias Problem

**Date:** 2026-01-03
**Role:** ML Engineer
**Issue:** Model dominated by organization size, not useful for smaller clients
**Status:** ROOT CAUSE IDENTIFIED - Recommending architectural changes

---

## Executive Summary

**The Problem:** V6 learned "big organizations get grants" which is TRUE but not USEFUL for helping smaller nonprofits find fundable opportunities.

**Root Cause:** Training data reflects reality (large orgs get more grants), but business goal is different (help small orgs find gettable grants).

**Solution:** Need to reframe the ML problem from "predict who gets funded" to "predict gettability for organizations of this size."

**Expected AUC Tradeoff:** 0.98 → 0.82-0.88 (but much more useful for business)

---

## 1. Why the Model Learned Organization Size

### The Evidence

| Size Bucket | % Funded in Training Data |
|-------------|---------------------------|
| Tiny (<$100K) | 33.8% |
| Small ($100K-$1M) | 40.4% |
| Medium ($1M-$10M) | 64.0% |
| Large (>$10M) | 69.6% |

**V6 Results:**
- Top predictor: `r_total_revenue` (+4.07)
- Semantic similarity: -0.31 (WRONG SIGN!)
- The model essentially learned: `P(funding) ≈ 0.34 + 0.41 × log(revenue)`

### Why This Happened (Statistically)

**1. Strong Signal in Ground Truth**
- Training on historical grants (2017-2022)
- Large orgs genuinely DO get funded more often
- The pattern is real, not noise
- Model learned the easiest, strongest pattern first

**2. Weak Competing Signals**
- Semantic similarity computed on sector averages (diluted signal)
- Geographic/sector matches are weaker than size effect
- LASSO penalized weaker features to zero

**3. Positive Sampling Bias**
- Positives = actual grants (mix of all sizes, skewed toward large)
- Negatives = random foundation-nonprofit pairs (also skewed toward large orgs existing in DB)
- Model never sees "small org successfully got grant from foundation that usually funds large orgs"

### The Statistical Paradox

**Model is statistically correct but strategically wrong:**

```
P(foundation funds org) = HIGH if org is large  ✓ TRUE
P(foundation WOULD fund small org | small org applies) = ??? ✗ UNANSWERED
```

The model learned Question 1, but clients need Question 2.

---

## 2. Why Semantic Similarity Got Wrong Sign

### The Implementation (from PY_2025-01-02_v6_export_training.py)

```python
def get_semantic_sim(row):
    fein = row['foundation_ein']
    ntee = row['r_ntee_broad']  # ← SECTOR CODE, not actual mission

    if fein not in foundation_embeddings:
        return 0.0
    if ntee not in sector_embeddings:  # ← SECTOR AVERAGE, not org-specific
        return 0.0

    return cosine_similarity(
        foundation_embeddings[fein],  # Avg of foundation's grant purposes
        sector_embeddings[ntee]       # Avg of all orgs in sector
    )
```

### Why It's Negative (-0.31)

**Hypothesis 1: Sector Averages Wash Out Signal**

Large, well-established orgs tend to have:
- Generic missions (broad sector average)
- Low semantic similarity to specialized foundation niches
- But they get funded anyway (brand reputation, relationships)

Small, specialized orgs tend to have:
- Specific missions (high similarity to niche foundations)
- But fewer resources to apply everywhere
- Sample under-represented in training data

**Hypothesis 2: Confounding with Size**

```
High semantic similarity → Specialized org → Likely small → Lower funding rate
Low semantic similarity → Generic org → Likely large → Higher funding rate
```

Model sees correlation: `semantic_sim ↓ → funding ↑` and encodes it.

**Hypothesis 3: Train/Serve Skew**

At training: Compare foundation to **sector average embedding**
At scoring: Will compare foundation to **specific client mission embedding**

Sector averages are artificial constructs. Real client embeddings will be more specific and higher-similarity than what the model saw in training.

### The Fix

**Option A: Use Actual Recipient Embeddings** (BEST if available)

```sql
-- Check coverage first:
SELECT
    COUNT(DISTINCT r.recipient_ein) as total_recipients,
    COUNT(DISTINCT nme.ein) as with_mission_text,
    ROUND(100.0 * COUNT(DISTINCT nme.ein) / COUNT(DISTINCT r.recipient_ein), 1) as pct
FROM training_data_v6 r
LEFT JOIN f990_2025.nonprofit_mission_embeddings nme ON r.recipient_ein = nme.ein;
```

If >50% coverage, modify SQL training data generation:

```sql
-- In SQL_2025-01-02_v6_training_data.sql
-- Add actual recipient embeddings (not sector averages)
LEFT JOIN f990_2025.nonprofit_mission_embeddings nme
    ON tp.recipient_ein = nme.ein
```

Then compute similarity in Python:

```python
# Use actual embedding if available, else fall back to sector average
def get_semantic_sim(row):
    fein = row['foundation_ein']
    rein = row['recipient_ein']
    ntee = row['r_ntee_broad']

    if fein not in foundation_embeddings:
        return 0.0

    # Prefer actual recipient embedding
    if rein in recipient_embeddings:
        recip_emb = recipient_embeddings[rein]
    elif ntee in sector_embeddings:
        recip_emb = sector_embeddings[ntee]
    else:
        return 0.0

    return cosine_similarity(foundation_embeddings[fein], recip_emb)
```

**Option B: Create Synthetic Recipient Missions**

For recipients without mission text:

```python
# Generate synthetic mission from available data
def create_synthetic_mission(row):
    org_name = row['recipient_name']
    ntee_desc = NTEE_DESCRIPTIONS[row['r_ntee_broad']]  # Human-readable
    state = row['r_state']

    return f"{org_name} is a {ntee_desc} organization serving {state}."

# Embed synthetic missions
recipient_embeddings[ein] = model.encode(create_synthetic_mission(row))
```

This gives you something more specific than pure sector average.

**Option C: Drop Semantic Similarity Entirely**

If it's giving wrong sign and being zeroed out by LASSO anyway, remove it. Focus on:
- Geographic match (proven positive)
- Sector match (proven positive)
- Foundation openness (proven positive)

---

## 3. ML Solutions to the Size Bias Problem

### Approach A: Remove Revenue Features Entirely

**Implementation:**
```python
# In PY_2025-01-02_v6_export_training.py
# Comment out lines with revenue features
features_to_drop = ['r_total_revenue', 'r_log_total_revenue', 'r_revenue_per_employee']
df = df.drop(columns=features_to_drop, errors='ignore')
```

**Pros:**
- Forces model to learn other patterns
- Levels playing field across org sizes
- Simple to implement

**Cons:**
- Throws away real information
- Some foundation-org size alignment is legitimate (operating foundation with $50K budget probably won't fund $10M org)
- May hurt AUC significantly

**Expected AUC:** 0.78-0.84 (moderate drop)

**Recommendation:** ❌ **Not recommended.** Size mismatch IS a real signal for some foundations.

---

### Approach B: Size-Stratified Models

Train separate models for each size bucket:

**Implementation:**
```python
# In training script
size_buckets = {
    'tiny': df[df['r_total_revenue'] < 100_000],
    'small': df[(df['r_total_revenue'] >= 100_000) & (df['r_total_revenue'] < 1_000_000)],
    'medium': df[(df['r_total_revenue'] >= 1_000_000) & (df['r_total_revenue'] < 10_000_000)],
    'large': df[df['r_total_revenue'] >= 10_000_000]
}

models = {}
for size, subset in size_buckets.items():
    # Train LASSO on this size bucket only
    X = subset[non_revenue_features]  # Exclude revenue from features
    y = subset['label']
    models[size] = cv.glmnet(X, y, ...)

# At scoring time, select model based on client size
```

**Pros:**
- Each model learns patterns relevant to that size cohort
- Can discover "small-org-specific" fundability signals
- Revenue no longer dominates (it's implicit in model selection)

**Cons:**
- Need 4x the training effort
- Small-org model has fewer positive examples (data scarcity)
- Complexity in deployment (which model to use?)
- Hard to compare across models

**Expected AUC per bucket:**
- Tiny: 0.72-0.78 (limited data)
- Small: 0.78-0.84
- Medium: 0.82-0.88
- Large: 0.85-0.90 (most data)

**Recommendation:** ⚠️ **Worth testing** if you have enough data in each bucket. Check first:

```sql
-- Verify sufficient positives per size bucket
SELECT
    CASE
        WHEN r_total_revenue < 100000 THEN 'tiny'
        WHEN r_total_revenue < 1000000 THEN 'small'
        WHEN r_total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket,
    label,
    COUNT(*)
FROM f990_2025.training_data_v6
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Minimum requirement:** >10,000 positives per bucket. If any bucket has <10K positives, don't use this approach.

---

### Approach C: Size-Matched Negative Sampling ⭐ **RECOMMENDED**

**The Core Idea:** When generating negatives, match the size distribution of positives.

**Current Problem:**
- Positives: Mix of sizes, skewed toward large (reflects reality)
- Negatives: Random pairs, ALSO skewed toward large (because DB has more large orgs)
- Model learns: "Large org → more likely positive"

**Solution:** Oversample small-org negatives to match small-org positive rate.

**Implementation:**

```sql
-- In negative sampling (modify SQL_2025-01-03.1_fix_v6_validation_negatives.sql)

-- Step 1: Get size distribution of POSITIVES
CREATE TEMP TABLE positive_size_dist AS
SELECT
    CASE
        WHEN nr.total_revenue < 100000 THEN 'tiny'
        WHEN nr.total_revenue < 1000000 THEN 'small'
        WHEN nr.total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket,
    COUNT(*) as n_positives
FROM f990_2025.fact_grants fg
JOIN f990_2025.nonprofit_returns nr ON fg.recipient_ein = nr.ein
WHERE fg.tax_year BETWEEN 2017 AND 2022
GROUP BY 1;

-- Step 2: Generate negatives with SAME size distribution
-- For each size bucket, sample proportionally
WITH negative_candidates AS (
    SELECT
        f.ein as foundation_ein,
        nr.ein as recipient_ein,
        CASE
            WHEN nr.total_revenue < 100000 THEN 'tiny'
            WHEN nr.total_revenue < 1000000 THEN 'small'
            WHEN nr.total_revenue < 10000000 THEN 'medium'
            ELSE 'large'
        END as size_bucket,
        ROW_NUMBER() OVER (
            PARTITION BY CASE
                WHEN nr.total_revenue < 100000 THEN 'tiny'
                WHEN nr.total_revenue < 1000000 THEN 'small'
                WHEN nr.total_revenue < 10000000 THEN 'medium'
                ELSE 'large'
            END
            ORDER BY RANDOM()
        ) as rn
    FROM f990_2025.dim_foundations f
    CROSS JOIN f990_2025.nonprofit_returns nr
    WHERE NOT EXISTS (
        SELECT 1 FROM f990_2025.fact_grants fg
        WHERE fg.foundation_ein = f.ein
        AND fg.recipient_ein = nr.ein
    )
)
SELECT
    nc.foundation_ein,
    nc.recipient_ein,
    0 as label,
    'negative_size_matched' as sample_type
FROM negative_candidates nc
JOIN positive_size_dist psd ON nc.size_bucket = psd.size_bucket
WHERE nc.rn <= psd.n_positives  -- Sample same count as positives for this size
;
```

**Result:** Training data with size-balanced classes.

**Pros:**
- Model can't use size as a shortcut (equal representation)
- Learns genuine affinity patterns at each size level
- Still allows size as a feature (for legitimate size-alignment matching)
- Minimal code changes
- Works with single unified model

**Cons:**
- Negatives are artificial (but so are all negatives in this problem)
- May slightly reduce AUC on overall dataset (but that's OK - we WANT to ignore size)

**Expected AUC:** 0.82-0.88 (similar to size-stratified but simpler)

**Why This is Best:**
1. **Addresses root cause:** Removes size shortcut while preserving size-alignment signal
2. **Simple deployment:** Single model, standard scoring pipeline
3. **Generalizes well:** Small clients get fair shake
4. **Honest metrics:** If AUC drops, it's because model isn't relying on size crutch

---

### Approach D: Sample Weighting (Inverse Propensity Weighting)

Weight training samples to balance size representation.

**Implementation:**

```R
# In R_2025-01-02_lasso_v6.R

# Calculate size-bucket-specific weights
size_bucket <- cut(train$r_total_revenue,
                   breaks = c(0, 1e5, 1e6, 1e7, Inf),
                   labels = c("tiny", "small", "medium", "large"))

# Count positives per size bucket
size_pos_counts <- table(size_bucket[train$label == 1])

# Inverse propensity weights (upweight underrepresented sizes)
weights <- rep(1, nrow(train))
for (size in names(size_pos_counts)) {
    idx <- size_bucket == size & train$label == 1
    weights[idx] <- 1 / size_pos_counts[size]  # Inverse frequency
}

# Normalize weights to sum to N
weights <- weights * (nrow(train) / sum(weights))

# Train weighted LASSO
cv_fit <- cv.glmnet(
    X_train_scaled, y_train,
    family = "binomial",
    alpha = 1,
    weights = weights,  # ← Add this
    nfolds = 5,
    type.measure = "auc"
)
```

**Pros:**
- Easy to implement (just add `weights=` parameter)
- Keeps all data (no subsampling)
- Can fine-tune weight ratios

**Cons:**
- Weights can make optimization unstable
- Hard to choose exact weighting scheme (linear? log? sqrt?)
- May still learn size patterns (just less strongly)

**Expected AUC:** 0.84-0.89

**Recommendation:** ⚠️ **Alternative to Approach C.** Try this if negative resampling is too complex.

---

### Approach E: Feature Interaction - Size × Openness

**The Insight:** Revenue is predictive, BUT its effect should be moderated by foundation openness.

Create interaction features:

**Implementation:**

```python
# In PY_2025-01-02_v6_export_training.py add_derived_features()

# Interaction: Does foundation's first-time rate vary by org size?
# High first_time_rate + small org → strong positive signal
df['interaction_openness_x_small'] = (
    df['f_first_time_rate'] * (df['r_total_revenue'] < 500_000).astype(int)
)

# Interaction: Does foundation fund orgs of this size?
# Compare recipient revenue to foundation's median grant recipient size
df['match_revenue_alignment'] = np.where(
    df['r_total_revenue'].between(
        df['f_median_recipient_revenue'] * 0.5,  # ±50% of foundation's typical grantee
        df['f_median_recipient_revenue'] * 2.0
    ),
    1,
    0
)

# Interaction: Semantic similarity matters MORE for small orgs (less brand reputation)
df['interaction_semantic_x_small'] = (
    df['match_semantic_similarity'] * (df['r_total_revenue'] < 1_000_000).astype(int)
)
```

**Add foundation feature: typical grantee size**

```sql
-- In SQL_2025-01-02_v6_training_data.sql
-- Add to foundation features section

-- Foundation's median recipient revenue (from historical grants)
LEFT JOIN LATERAL (
    SELECT
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY nr.total_revenue) as median_recipient_revenue
    FROM f990_2025.fact_grants fg
    JOIN f990_2025.nonprofit_returns nr ON fg.recipient_ein = nr.ein
    WHERE fg.foundation_ein = tp.foundation_ein
        AND fg.tax_year BETWEEN (tp.tax_year - 3) AND (tp.tax_year - 1)
) med_recip ON TRUE
```

**Pros:**
- Captures nuance: "Revenue matters differently depending on foundation type"
- Allows model to learn: "Small org + open foundation = good match"
- Doesn't remove base revenue feature (preserves legitimate signal)

**Cons:**
- Adds complexity (more features)
- Interactions can be noisy
- Requires domain knowledge to design good interactions

**Expected AUC:** 0.86-0.90 (best of both worlds)

**Recommendation:** ✅ **Use in combination with Approach C.** Size-matched sampling + smart interactions.

---

## 4. Expected AUC Tradeoffs (Summary)

| Approach | Expected AUC | Pros | Cons | Recommendation |
|----------|--------------|------|------|----------------|
| **Current V6** | 0.98 | High AUC | Useless for small orgs | ❌ Don't use |
| **A: Remove revenue** | 0.78-0.84 | Simple, fair | Loses real signal | ❌ Too aggressive |
| **B: Size-stratified models** | 0.72-0.90 | Tailored to size | Complex, data-hungry | ⚠️ If you have data |
| **C: Size-matched negatives** ⭐ | 0.82-0.88 | Removes shortcut, simple | Artificial negatives | ✅ **RECOMMENDED** |
| **D: Sample weighting** | 0.84-0.89 | Easy to implement | Optimization instability | ⚠️ Alternative to C |
| **E: Feature interactions** | 0.86-0.90 | Captures nuance | Requires domain knowledge | ✅ **Combine with C** |

---

## 5. Concrete Recommendations

### Phase 1: Fix Critical Bugs (Do This First)

**From previous ML review:**

1. ✅ Fix validation/test negatives (no negatives in 2023-2024)
2. ✅ Fix temporal leakage in `f_funded_new_recently`
3. ✅ Drop `f_openness_score` (99.8% correlated with `f_first_time_rate`)

**Result:** V6 will train correctly but still have size bias.

---

### Phase 2: Implement Size-Matched Sampling ⭐

**Goal:** Remove size shortcut while preserving size-alignment signal.

**Steps:**

1. **Analyze current size distribution** (30 min)

```sql
-- Check positive size distribution
SELECT
    CASE
        WHEN nr.total_revenue < 100000 THEN 'tiny (<$100K)'
        WHEN nr.total_revenue < 1000000 THEN 'small ($100K-$1M)'
        WHEN nr.total_revenue < 10000000 THEN 'medium ($1M-$10M)'
        ELSE 'large (>$10M)'
    END as size_bucket,
    COUNT(*) as n_positives,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM f990_2025.fact_grants fg
JOIN f990_2025.nonprofit_returns nr ON fg.recipient_ein = nr.ein
WHERE fg.tax_year BETWEEN 2017 AND 2022
GROUP BY 1
ORDER BY
    CASE
        WHEN nr.total_revenue < 100000 THEN 1
        WHEN nr.total_revenue < 1000000 THEN 2
        WHEN nr.total_revenue < 10000000 THEN 3
        ELSE 4
    END;
```

2. **Create size-matched negatives** (1 hour)

```sql
-- See full SQL in Approach C above
-- Key: Match negative size distribution to positive size distribution
```

3. **Verify balance** (10 min)

```sql
-- After regenerating training_data_v6:
SELECT
    CASE
        WHEN r_total_revenue < 100000 THEN 'tiny'
        WHEN r_total_revenue < 1000000 THEN 'small'
        WHEN r_total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket,
    label,
    COUNT(*) as n,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY label), 1) as pct_of_label
FROM f990_2025.training_data_v6
WHERE tax_year BETWEEN 2017 AND 2022  -- Training set only
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Expected result:**

```
size_bucket | label | n       | pct_of_label
------------|-------|---------|-------------
tiny        | 0     | 120,000 | 15.0%        ← Should match positives
tiny        | 1     | 120,000 | 15.0%
small       | 0     | 280,000 | 35.0%
small       | 1     | 280,000 | 35.0%
medium      | 0     | 320,000 | 40.0%
medium      | 1     | 320,000 | 40.0%
large       | 0     | 80,000  | 10.0%
large       | 1     | 80,000  | 10.0%
```

4. **Re-train V6** (1 hour)

```bash
# Re-export training data with size-balanced negatives
python3 PY_2025-01-02_v6_export_training.py

# Train model
Rscript R_2025-01-02_lasso_v6.R
```

5. **Validate coefficients** (15 min)

Check that:
- ✅ `r_total_revenue` coefficient is smaller (not dominant)
- ✅ `f_first_time_rate` coefficient is positive and significant
- ✅ `match_semantic_similarity` coefficient is positive (after fixing embedding issue)

**Expected V6.1 results:**

```
Top 10 coefficients:
1. f_first_time_rate              +1.82  ← Foundation openness (was +0.54)
2. match_state_pct                +1.45  ← Geographic match (was +1.71)
3. match_sector_pct               +0.98  ← Sector match (was +0.48)
4. r_total_revenue                +0.62  ← Still matters, but not dominant
5. f_is_accessible                +0.54
6. match_semantic_similarity      +0.48  ← Should be positive now
7. f_sector_hhi                   -0.41  ← Concentrated foundations harder
...
```

---

### Phase 3: Add Feature Interactions (Optional)

**Goal:** Capture "small org + open foundation = high gettability" patterns.

**Steps:**

1. **Add to SQL training data generation** (30 min)

```sql
-- In SQL_2025-01-02_v6_training_data.sql
-- Add foundation median recipient revenue (see Approach E above)
```

2. **Add to Python feature engineering** (30 min)

```python
# In PY_2025-01-02_v6_export_training.py add_derived_features()

# Revenue alignment (is org's budget similar to foundation's typical grantee?)
df['match_revenue_alignment'] = np.where(
    df['r_total_revenue'].between(
        df['f_median_recipient_revenue'] * 0.5,
        df['f_median_recipient_revenue'] * 2.0
    ),
    1,
    0
)

# Openness × small org interaction
df['interaction_openness_x_small'] = (
    df['f_first_time_rate'] * (df['r_total_revenue'] < 500_000).astype(int)
)

# Semantic similarity matters more for small orgs (less brand recognition)
df['interaction_semantic_x_small'] = (
    df['match_semantic_similarity'] * (df['r_total_revenue'] < 1_000_000).astype(int)
)
```

3. **Re-train and evaluate** (1 hour)

**Expected improvement:** +0.02 to +0.05 AUC, better ranking for small orgs.

---

### Phase 4: Enhanced Evaluation Metrics

**Goal:** Measure model performance specifically for small clients.

**Add to R script:**

```R
# In R_2025-01-02_lasso_v6.R after test set evaluation

# ============================================================================
# Small Org Performance Analysis
# ============================================================================

cat("\n", rep("=", 60), "\n", sep = "")
cat("SMALL ORG PERFORMANCE (Revenue < $1M)\n")
cat(rep("=", 60), "\n", sep = "")

# Filter to small orgs
test_small <- test[test$r_total_revenue < 1e6, ]
pred_small <- pred_test[test$r_total_revenue < 1e6]
y_small <- y_test[test$r_total_revenue < 1e6]

if (nrow(test_small) > 100) {
    roc_small <- roc(y_small, as.vector(pred_small), quiet = TRUE)
    cat(sprintf("  Small org test samples: %s\n", format(nrow(test_small), big.mark = ",")))
    cat(sprintf("  Small org AUC: %.4f\n", auc(roc_small)))

    # Precision at top 100
    small_ranked <- order(pred_small, decreasing = TRUE)
    precision_at_100 <- mean(y_small[small_ranked[1:min(100, length(small_ranked))]])
    cat(sprintf("  Precision@100: %.4f\n", precision_at_100))
} else {
    cat("  Not enough small org samples for evaluation\n")
}

# Compare to large orgs
cat("\n", rep("=", 60), "\n", sep = "")
cat("LARGE ORG PERFORMANCE (Revenue > $10M)\n")
cat(rep("=", 60), "\n", sep = "")

test_large <- test[test$r_total_revenue > 1e7, ]
pred_large <- pred_test[test$r_total_revenue > 1e7]
y_large <- y_test[test$r_total_revenue > 1e7]

if (nrow(test_large) > 100) {
    roc_large <- roc(y_large, as.vector(pred_large), quiet = TRUE)
    cat(sprintf("  Large org test samples: %s\n", format(nrow(test_large), big.mark = ",")))
    cat(sprintf("  Large org AUC: %.4f\n", auc(roc_large)))

    precision_at_100_large <- mean(y_large[order(pred_large, decreasing = TRUE)[1:min(100, length(y_large))]])
    cat(sprintf("  Precision@100: %.4f\n", precision_at_100_large))
}

cat("\n*** SUCCESS IF: Small org AUC within 0.05 of large org AUC ***\n")
```

---

## 6. Timeline and Expected Results

| Phase | Time | Expected AUC | Small Org AUC | Notes |
|-------|------|--------------|---------------|-------|
| **Current V6** | - | 0.98 | 0.65 | Biased toward large orgs |
| **Phase 1: Bug fixes** | 2 hours | 0.88-0.92 | 0.70-0.75 | Removes leakage |
| **Phase 2: Size-matched sampling** | 3 hours | 0.82-0.88 | 0.78-0.84 | Fair to small orgs ✅ |
| **Phase 3: Interactions** | 2 hours | 0.86-0.90 | 0.82-0.87 | Best of both worlds |

**Success Criteria:**

✅ **Small org AUC ≥ 0.78** (2x better than random, useful for ranking)
✅ **Small org AUC within 0.05 of overall AUC** (no systematic bias)
✅ **Top coefficients are actionable** (openness, geography, sector - not just size)
✅ **Semantic similarity is positive** (or zero if signal is weak)
✅ **Real client validation:** Ka Ulukoa's actual funders rank in top 50

---

## 7. Validation Plan: Real Client Tests

After re-training V6.1 (size-matched), test on real clients:

### Test 1: Ka Ulukoa (Small Org, Hawaii)

**Client Profile:**
- Revenue: ~$300K (small)
- Location: Hawaii
- Sector: Youth athletics (NTEE N20)

**Known Funders (Ground Truth):**
- Atherton Family Foundation
- Harold K.L. Castle Foundation
- Bank of Hawaii Foundation

**Test:**
```python
# Score all foundations for Ka Ulukoa profile
results = score_foundations(
    client_revenue=300_000,
    client_state='HI',
    client_sector='N20',
    client_mission_embedding=ka_ulukoa_embedding
)

# Check if known funders are in top 50
known_funders = ['237292730', '990042394', '996001055']  # EINs
for ein in known_funders:
    rank = results[results['ein'] == ein]['rank'].values[0]
    print(f"  {ein}: Rank {rank} {'✅' if rank <= 50 else '❌'}")
```

**Success:** ≥2 of 3 known funders in top 50.

### Test 2: PSMF (Medium-Large Org, National)

**Client Profile:**
- Revenue: ~$5M (medium)
- Location: CA (but national scope)
- Sector: Healthcare education

**Test:** Do top 50 recommendations include healthcare foundations open to national work?

### Test 3: Synthetic Small Org (Stress Test)

**Profile:**
- Revenue: $50K (tiny)
- Location: Rural Montana
- Sector: Environmental conservation

**Test:** Does model return ANY viable recommendations? (Should not return all large national foundations)

---

## 8. Long-Term: Consider Alternative Frameworks

If V6.1 still struggles, consider reframing the problem entirely:

### Alternative 1: Positive-Unlabeled (PU) Learning

**Framing:** You only observe successful grants (positives). Non-grants are "unlabeled" (maybe would fund, just haven't applied yet).

**Technique:** PU bagging (Liu et al. 2002)

**Pros:** More theoretically sound for this problem.
**Cons:** Complex, less interpretable.

### Alternative 2: Learning to Rank

**Framing:** Instead of binary classification, train a ranking model (LambdaMART, RankNet).

**Data:** For each client, rank foundations by likelihood of funding.

**Pros:** Optimizes directly for top-K recommendations.
**Cons:** Requires pair-wise training data.

### Alternative 3: Multi-Task Learning

**Tasks:**
1. Predict funding (main task)
2. Predict grant amount (auxiliary task)
3. Predict repeat funding (auxiliary task)

**Benefit:** Auxiliary tasks may help model learn better representations.

---

## 9. Summary of Answers to Your Questions

### Q1: Why is the model dominated by org size?

**A:** Training data reflects reality (large orgs get funded more). Model learned the easiest, strongest pattern. Competing signals (semantic similarity, openness) were weaker or noisy.

### Q2: Propose ML approaches for "gettability" model?

**A:** **Size-matched negative sampling** (Approach C) is best. Removes size shortcut while preserving legitimate size-alignment signal.

### Q3: Should we remove revenue entirely?

**A:** ❌ No. Revenue alignment IS meaningful (foundation funding $10K grants won't fund $10M org). Instead, balance the training data so model can't use revenue as a shortcut.

### Q4: Size-stratified models?

**A:** ⚠️ Worth trying IF you have >10K positives per size bucket. Check data first. More complex to deploy.

### Q5: Size-matched negative sampling?

**A:** ✅ **YES, recommended.** Generate negatives with same size distribution as positives. Forces model to learn other patterns.

### Q6: Weight smaller orgs higher in training?

**A:** ⚠️ Alternative to size-matched sampling. Use inverse propensity weighting. Simpler to implement but may be less effective.

### Q7: Something else?

**A:** ✅ **Feature interactions** (Approach E). Combine size-matched sampling with smart interactions like `openness × small_org`. Best of both worlds.

### Q8: Expected AUC tradeoff for each approach?

| Approach | AUC | Small Org AUC | Complexity |
|----------|-----|---------------|------------|
| Current | 0.98 | 0.65 | Low |
| Remove revenue | 0.78-0.84 | 0.75-0.82 | Low |
| Size-stratified | 0.72-0.90 | Varies | High |
| Size-matched negatives ⭐ | 0.82-0.88 | 0.78-0.84 | Medium |
| Sample weighting | 0.84-0.89 | 0.80-0.86 | Low |
| Interactions + size-matched | 0.86-0.90 | 0.82-0.87 | Medium |

### Q9: How should semantic similarity be computed?

**A:**
1. ✅ **Check coverage** of `nonprofit_mission_embeddings` for training recipients
2. ✅ **If >50% coverage:** Use actual recipient embeddings (not sector averages)
3. ✅ **If <50% coverage:** Generate synthetic mission text from org name + NTEE + state
4. ❌ **Don't use pure sector averages** - too generic, causes wrong sign

**Expected result:** Coefficient should be +0.3 to +0.8 (positive and moderate strength).

---

## 10. Files to Create/Modify

### SQL
- ✅ Modify `SQL_2025-01-02_v6_training_data.sql`
  - Add `f_median_recipient_revenue` feature
  - Ensure recipient revenue is available
- ✅ Create `SQL_2025-01-03_v6_size_matched_negatives.sql`
  - Implement size-matched negative sampling logic

### Python
- ✅ Modify `PY_2025-01-02_v6_export_training.py`
  - Fix semantic similarity (use actual recipient embeddings)
  - Add feature interactions (openness × small, semantic × small)
  - Add revenue alignment feature

### R
- ✅ Modify `R_2025-01-02_lasso_v6.R`
  - Add small org evaluation section
  - Add precision@K metrics
  - Add size-bucket comparison

### New Scripts
- ✅ Create `PY_2025-01-03_validate_real_clients.py`
  - Test Ka Ulukoa, PSMF, synthetic small org
  - Check if known funders rank in top 50

---

## Next Steps

**Immediate (Today):**
1. ✅ Check coverage of `nonprofit_mission_embeddings` for training data
2. ✅ Implement size-matched negative sampling SQL
3. ✅ Fix semantic similarity to use actual embeddings (if available)

**This Week:**
4. ✅ Re-train V6.1 with size-balanced data
5. ✅ Validate coefficients have expected signs
6. ✅ Test on Ka Ulukoa and PSMF real clients

**Next Week:**
7. ✅ Add feature interactions (if V6.1 performance is acceptable)
8. ✅ Deploy to production if real client validation passes

---

## Questions for You

1. **Do you have nonprofit_mission_embeddings for historical grant recipients?** Check coverage with query in Section 2.

2. **What's the minimum acceptable AUC for small orgs?** I'm targeting 0.78+, is that sufficient?

3. **Which approach do you prefer?**
   - **Size-matched negatives** (my recommendation, medium complexity)
   - **Sample weighting** (simpler, may be less effective)
   - **Size-stratified models** (complex, requires checking data)

4. **Should I prioritize AUC or Precision@100?** For production (showing top 100 foundations), Precision@100 matters more than global AUC.

---

**ML Engineering Review Complete**
**Status:** Recommendations provided, awaiting direction to implement
**Estimated Time to Fix:** 1-2 days
**Expected Result:** Fair, useful model for small nonprofits (the clients who need it most)
