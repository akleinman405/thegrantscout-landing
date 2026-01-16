# Action Plan: Fix V6 Size Bias

**Date:** 2026-01-03
**Problem:** Model learned "big orgs get grants" (true but not useful)
**Solution:** Size-matched negative sampling + feature interactions
**Timeline:** 1-2 days
**Expected Result:** AUC 0.82-0.88, fair to small orgs

---

## Quick Diagnosis

**Current V6 Issue:**
- Top predictor: `r_total_revenue` (+4.07) - org size
- Semantic similarity: -0.31 (WRONG SIGN)
- Model is 98% accurate but recommends only large foundations to small clients

**Root Cause:**
- Training data: Large orgs get 69.6% of grants, tiny orgs get 33.8%
- Model learned shortcut: `P(funding) ≈ f(revenue)`
- Semantic similarity uses sector averages (diluted signal, wrong sign)

**Business Impact:**
- Useless for smaller clients (your target market!)
- Will recommend Gates Foundation to $50K food bank

---

## Recommended Solution: Size-Matched Negatives ⭐

**Approach:** Generate negatives with SAME size distribution as positives.

**Why This Works:**
- Removes size shortcut (balanced classes per size bucket)
- Preserves legitimate size-alignment signal
- Forces model to learn openness, geography, sector patterns
- Single unified model (simple deployment)

**Expected AUC:** 0.82-0.88 overall, 0.78-0.84 for small orgs

---

## Implementation Steps

### Step 1: Check Data Coverage (15 min)

```sql
-- Check if you have actual recipient embeddings
SELECT
    COUNT(DISTINCT tp.recipient_ein) as total_recipients,
    COUNT(DISTINCT nme.ein) as with_mission_text,
    ROUND(100.0 * COUNT(DISTINCT nme.ein) / COUNT(DISTINCT tp.recipient_ein), 1) as pct_coverage
FROM f990_2025.training_data_v6 tp
LEFT JOIN f990_2025.nonprofit_mission_embeddings nme ON tp.recipient_ein = nme.ein;
```

**Decision:**
- If >50% coverage → Use actual embeddings (Step 2a)
- If <50% coverage → Use synthetic missions (Step 2b)

---

### Step 2a: Fix Semantic Similarity (Actual Embeddings) (30 min)

**Modify `PY_2025-01-02_v6_export_training.py` lines 266-278:**

```python
def get_semantic_sim(row):
    fein = row['foundation_ein']
    rein = row['recipient_ein']
    ntee = row['r_ntee_broad']

    if fein not in foundation_embeddings:
        return 0.0

    # FIXED: Prefer actual recipient embedding over sector average
    if rein in recipient_embeddings:
        recip_emb = recipient_embeddings[rein]
    elif ntee in sector_embeddings:
        recip_emb = sector_embeddings[ntee]
    else:
        return 0.0

    return cosine_similarity(foundation_embeddings[fein], recip_emb)
```

**Add recipient embeddings loading (after line 230):**

```python
# Load recipient mission embeddings
print("Loading recipient mission embeddings...")
recipient_embeddings = {}
cur.execute("""
    SELECT ein, mission_embedding_v
    FROM f990_2025.nonprofit_mission_embeddings
    WHERE mission_embedding_v IS NOT NULL
""")
for row in cur.fetchall():
    recipient_embeddings[row[0]] = np.array(row[1])
print(f"  Loaded {len(recipient_embeddings):,} recipient embeddings")
```

---

### Step 2b: Fix Semantic Similarity (Synthetic Missions) (45 min)

**If low coverage, create synthetic missions:**

```python
# In PY_2025-01-02_v6_export_training.py after loading data

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# NTEE descriptions (simplified - expand as needed)
NTEE_DESC = {
    'A': 'arts and culture',
    'B': 'education',
    'E': 'health',
    'F': 'mental health',
    'H': 'healthcare',
    'K': 'food and agriculture',
    'L': 'housing',
    'N': 'youth development',
    'P': 'human services',
    # ... add more
}

def create_synthetic_mission(row):
    """Generate synthetic mission from org name + NTEE + state"""
    org_name = row.get('recipient_name', 'This organization')
    ntee = row['r_ntee_broad']
    state = row['r_state']

    ntee_desc = NTEE_DESC.get(ntee, 'nonprofit')

    return f"{org_name} is a {ntee_desc} organization serving {state}."

# Generate embeddings for recipients without actual missions
print("Generating synthetic mission embeddings...")
recipient_embeddings = {}
for idx, row in df_features.iterrows():
    rein = row['recipient_ein']
    if rein not in recipient_embeddings:
        synthetic_mission = create_synthetic_mission(row)
        recipient_embeddings[rein] = model.encode(synthetic_mission)

print(f"  Generated {len(recipient_embeddings):,} synthetic embeddings")
```

---

### Step 3: Analyze Size Distribution (15 min)

```sql
-- Get current size distribution of positives
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
JOIN f990_2025.nonprofit_returns nr
    ON fg.recipient_ein = nr.ein
    AND nr.tax_year = fg.tax_year
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

**Save the output** - you'll use these percentages in Step 4.

---

### Step 4: Implement Size-Matched Negative Sampling (1 hour)

**Create new file: `SQL_2025-01-03_v6_size_matched_negatives.sql`**

```sql
-- Size-Matched Negative Sampling for V6
-- Generates negatives with same size distribution as positives

BEGIN;

-- Step 1: Get size distribution of positives (2017-2022 training period)
DROP TABLE IF EXISTS temp_positive_size_dist;
CREATE TEMP TABLE temp_positive_size_dist AS
SELECT
    CASE
        WHEN nr.total_revenue < 100000 THEN 'tiny'
        WHEN nr.total_revenue < 1000000 THEN 'small'
        WHEN nr.total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket,
    COUNT(*) as n_positives
FROM f990_2025.fact_grants fg
JOIN f990_2025.nonprofit_returns nr
    ON fg.recipient_ein = nr.ein
    AND ABS(nr.tax_year - fg.tax_year) <= 1  -- Match by close tax year
WHERE fg.tax_year BETWEEN 2017 AND 2022
GROUP BY 1;

-- Step 2: Clear existing negatives (we'll regenerate)
DELETE FROM f990_2025.stg_v5_training_pairs WHERE label = 0;

-- Step 3: Generate size-matched negatives for TRAINING (2017-2022)
INSERT INTO f990_2025.stg_v5_training_pairs (
    foundation_ein, recipient_ein, tax_year, label, sample_type
)
WITH
-- Get all foundations that made grants 2017-2022
active_foundations AS (
    SELECT DISTINCT foundation_ein
    FROM f990_2025.fact_grants
    WHERE tax_year BETWEEN 2017 AND 2022
),
-- Get all nonprofits by size bucket (using most recent revenue)
nonprofits_by_size AS (
    SELECT DISTINCT ON (nr.ein)
        nr.ein as recipient_ein,
        CASE
            WHEN nr.total_revenue < 100000 THEN 'tiny'
            WHEN nr.total_revenue < 1000000 THEN 'small'
            WHEN nr.total_revenue < 10000000 THEN 'medium'
            ELSE 'large'
        END as size_bucket,
        nr.total_revenue
    FROM f990_2025.nonprofit_returns nr
    WHERE nr.tax_year BETWEEN 2015 AND 2022
        AND nr.total_revenue IS NOT NULL
    ORDER BY nr.ein, nr.tax_year DESC
),
-- Generate negative candidates (foundation × nonprofit pairs)
negative_candidates AS (
    SELECT
        f.foundation_ein,
        n.recipient_ein,
        n.size_bucket,
        2017 + (RANDOM() * 5)::int as tax_year,  -- Random year 2017-2022
        ROW_NUMBER() OVER (
            PARTITION BY n.size_bucket
            ORDER BY RANDOM()
        ) as rn
    FROM active_foundations f
    CROSS JOIN nonprofits_by_size n
    WHERE NOT EXISTS (
        -- Exclude actual grants
        SELECT 1
        FROM f990_2025.fact_grants fg
        WHERE fg.foundation_ein = f.foundation_ein
            AND fg.recipient_ein = n.recipient_ein
    )
)
-- Sample negatives proportional to positive size distribution
SELECT
    nc.foundation_ein,
    nc.recipient_ein,
    nc.tax_year,
    0 as label,
    'negative_size_matched' as sample_type
FROM negative_candidates nc
JOIN temp_positive_size_dist psd ON nc.size_bucket = psd.size_bucket
WHERE nc.rn <= psd.n_positives  -- Match count of positives per size bucket
;

-- Step 4: Generate size-matched negatives for VALIDATION (2023)
INSERT INTO f990_2025.stg_v5_training_pairs (
    foundation_ein, recipient_ein, tax_year, label, sample_type
)
WITH
val_positive_dist AS (
    SELECT
        CASE
            WHEN nr.total_revenue < 100000 THEN 'tiny'
            WHEN nr.total_revenue < 1000000 THEN 'small'
            WHEN nr.total_revenue < 10000000 THEN 'medium'
            ELSE 'large'
        END as size_bucket,
        COUNT(*) as n_positives
    FROM f990_2025.fact_grants fg
    JOIN f990_2025.nonprofit_returns nr
        ON fg.recipient_ein = nr.ein
        AND ABS(nr.tax_year - fg.tax_year) <= 1
    WHERE fg.tax_year = 2023
    GROUP BY 1
),
active_foundations_2023 AS (
    SELECT DISTINCT foundation_ein
    FROM f990_2025.fact_grants
    WHERE tax_year = 2023
),
nonprofits_by_size AS (
    SELECT DISTINCT ON (nr.ein)
        nr.ein as recipient_ein,
        CASE
            WHEN nr.total_revenue < 100000 THEN 'tiny'
            WHEN nr.total_revenue < 1000000 THEN 'small'
            WHEN nr.total_revenue < 10000000 THEN 'medium'
            ELSE 'large'
        END as size_bucket
    FROM f990_2025.nonprofit_returns nr
    WHERE nr.tax_year BETWEEN 2020 AND 2023
        AND nr.total_revenue IS NOT NULL
    ORDER BY nr.ein, nr.tax_year DESC
),
negative_candidates AS (
    SELECT
        f.foundation_ein,
        n.recipient_ein,
        n.size_bucket,
        2023 as tax_year,
        ROW_NUMBER() OVER (
            PARTITION BY n.size_bucket
            ORDER BY RANDOM()
        ) as rn
    FROM active_foundations_2023 f
    CROSS JOIN nonprofits_by_size n
    WHERE NOT EXISTS (
        SELECT 1 FROM f990_2025.fact_grants fg
        WHERE fg.foundation_ein = f.foundation_ein
            AND fg.recipient_ein = n.recipient_ein
    )
)
SELECT
    nc.foundation_ein,
    nc.recipient_ein,
    nc.tax_year,
    0 as label,
    'negative_size_matched_val' as sample_type
FROM negative_candidates nc
JOIN val_positive_dist psd ON nc.size_bucket = psd.size_bucket
WHERE nc.rn <= psd.n_positives * 5  -- 5x negatives to match reality (more negatives than positives)
;

-- Step 5: Repeat for TEST (2024)
INSERT INTO f990_2025.stg_v5_training_pairs (
    foundation_ein, recipient_ein, tax_year, label, sample_type
)
WITH
test_positive_dist AS (
    SELECT
        CASE
            WHEN nr.total_revenue < 100000 THEN 'tiny'
            WHEN nr.total_revenue < 1000000 THEN 'small'
            WHEN nr.total_revenue < 10000000 THEN 'medium'
            ELSE 'large'
        END as size_bucket,
        COUNT(*) as n_positives
    FROM f990_2025.fact_grants fg
    JOIN f990_2025.nonprofit_returns nr
        ON fg.recipient_ein = nr.ein
        AND ABS(nr.tax_year - fg.tax_year) <= 1
    WHERE fg.tax_year = 2024
    GROUP BY 1
),
active_foundations_2024 AS (
    SELECT DISTINCT foundation_ein
    FROM f990_2025.fact_grants
    WHERE tax_year = 2024
),
nonprofits_by_size AS (
    SELECT DISTINCT ON (nr.ein)
        nr.ein as recipient_ein,
        CASE
            WHEN nr.total_revenue < 100000 THEN 'tiny'
            WHEN nr.total_revenue < 1000000 THEN 'small'
            WHEN nr.total_revenue < 10000000 THEN 'medium'
            ELSE 'large'
        END as size_bucket
    FROM f990_2025.nonprofit_returns nr
    WHERE nr.tax_year BETWEEN 2021 AND 2024
        AND nr.total_revenue IS NOT NULL
    ORDER BY nr.ein, nr.tax_year DESC
),
negative_candidates AS (
    SELECT
        f.foundation_ein,
        n.recipient_ein,
        n.size_bucket,
        2024 as tax_year,
        ROW_NUMBER() OVER (
            PARTITION BY n.size_bucket
            ORDER BY RANDOM()
        ) as rn
    FROM active_foundations_2024 f
    CROSS JOIN nonprofits_by_size n
    WHERE NOT EXISTS (
        SELECT 1 FROM f990_2025.fact_grants fg
        WHERE fg.foundation_ein = f.foundation_ein
            AND fg.recipient_ein = n.recipient_ein
    )
)
SELECT
    nc.foundation_ein,
    nc.recipient_ein,
    nc.tax_year,
    0 as label,
    'negative_size_matched_test' as sample_type
FROM negative_candidates nc
JOIN test_positive_dist psd ON nc.size_bucket = psd.size_bucket
WHERE nc.rn <= psd.n_positives * 8  -- 8x negatives for test set
;

COMMIT;

-- Verification query
SELECT
    CASE WHEN tax_year <= 2022 THEN 'Train'
         WHEN tax_year = 2023 THEN 'Val'
         ELSE 'Test' END as split,
    label,
    COUNT(*) as n,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY
        CASE WHEN tax_year <= 2022 THEN 'Train'
             WHEN tax_year = 2023 THEN 'Val'
             ELSE 'Test' END
    ), 1) as pct
FROM f990_2025.stg_v5_training_pairs
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Run it:**
```bash
PGPASSWORD=kmalec21 psql -h localhost -U postgres -d thegrantscout \
  -f SQL_2025-01-03_v6_size_matched_negatives.sql
```

---

### Step 5: Add Feature Interactions (Optional, 30 min)

**Modify `PY_2025-01-02_v6_export_training.py` in `add_derived_features()`:**

```python
def add_derived_features(df):
    """Add engineered features"""
    print("\nAdding derived features...")

    # ... existing features ...

    # NEW: Revenue alignment (is org similar size to foundation's typical grantee?)
    # Note: This requires adding f_median_recipient_revenue to SQL query first
    if 'f_median_recipient_revenue' in df.columns:
        df['match_revenue_alignment'] = np.where(
            df['r_total_revenue'].between(
                df['f_median_recipient_revenue'] * 0.5,
                df['f_median_recipient_revenue'] * 2.0
            ),
            1,
            0
        )
        print("  Added: match_revenue_alignment")

    # NEW: Openness × small org interaction
    # High openness + small org = strong positive signal
    if 'f_first_time_rate' in df.columns:
        df['interaction_openness_x_small'] = (
            df['f_first_time_rate'] * (df['r_total_revenue'] < 500_000).astype(int)
        )
        print("  Added: interaction_openness_x_small")

    # NEW: Semantic similarity × small org interaction
    # Similarity matters more for small orgs (less brand recognition)
    if 'match_semantic_similarity' in df.columns:
        df['interaction_semantic_x_small'] = (
            df['match_semantic_similarity'] * (df['r_total_revenue'] < 1_000_000).astype(int)
        )
        print("  Added: interaction_semantic_x_small")

    return df
```

---

### Step 6: Rebuild Training Data (30 min)

```bash
# Rebuild SQL training table
PGPASSWORD=kmalec21 psql -h localhost -U postgres -d thegrantscout \
  -f "/Users/aleckleinman/Documents/TheGrantScout/5. TheGrantScout - Pipeline/Pipeline v2/scripts/sql/SQL_2025-01-02_v6_training_data.sql"

# Export to CSV
python3 "/Users/aleckleinman/Documents/TheGrantScout/5. TheGrantScout - Pipeline/Pipeline v2/scripts/python/PY_2025-01-02_v6_export_training.py"
```

**Verify splits have balanced size distributions:**
```sql
SELECT
    CASE WHEN tax_year <= 2022 THEN 'Train'
         WHEN tax_year = 2023 THEN 'Val'
         ELSE 'Test' END as split,
    CASE
        WHEN r_total_revenue < 100000 THEN 'tiny'
        WHEN r_total_revenue < 1000000 THEN 'small'
        WHEN r_total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket,
    label,
    COUNT(*) as n
FROM f990_2025.training_data_v6
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
```

**Expected result:** For each split and size bucket, positive/negative counts should be similar.

---

### Step 7: Re-train V6.1 (1 hour)

```bash
Rscript "/Users/aleckleinman/Documents/TheGrantScout/5. TheGrantScout - Pipeline/Pipeline v2/scripts/r/R_2025-01-02_lasso_v6.R"
```

**Check console output for:**

✅ Validation has negatives (not 100% positive)
✅ Test has negatives (not 100% positive)
✅ `r_total_revenue` coefficient is smaller (not dominant)
✅ `match_semantic_similarity` is positive (or zero)
✅ `f_first_time_rate` or `f_openness_score` is positive and significant

**Expected output:**
```
Top 10 Coefficients:
  1. f_first_time_rate              +1.82  ← Was +0.54, now top predictor ✅
  2. match_state_pct                +1.45  ← Still strong ✅
  3. match_sector_pct               +0.98  ← Still strong ✅
  4. r_total_revenue                +0.62  ← Was +4.07, now moderate ✅
  5. match_semantic_similarity      +0.48  ← Was -0.31, now positive ✅
  ...

Validation AUC: 0.8542  ← Down from 0.98, but honest
Test AUC: 0.8301        ← Realistic for production use
```

---

### Step 8: Validate on Real Clients (30 min)

**Create `PY_2025-01-03_validate_v6_real_clients.py`:**

```python
"""
Test V6.1 on real client cases
Check if known funders rank in top 50
"""

import psycopg2
import pandas as pd
import numpy as np
import json

# Load V6.1 model
with open('outputs/v6/model/coefficients.json') as f:
    model = json.load(f)
with open('outputs/v6/model/scaling.json') as f:
    scaling = json.load(f)

# Connect to DB
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='thegrantscout',
    user='postgres',
    password='kmalec21'
)

# Test Case 1: Ka Ulukoa (small org, Hawaii, youth athletics)
print("\n=== Test Case 1: Ka Ulukoa ===")
print("Client: $300K revenue, HI, youth athletics (NTEE N20)")
print("Known funders: Atherton Family Foundation, Harold K.L. Castle Foundation")

# Score all foundations for Ka Ulukoa profile
# (This would use your actual scoring pipeline - simplified here)
query = """
SELECT
    f.ein,
    f.name,
    -- Add all V6.1 features here
    ROW_NUMBER() OVER (ORDER BY <your scoring formula> DESC) as rank
FROM f990_2025.dim_foundations f
WHERE f.grants_to_organizations_ind = TRUE
    AND (f.only_contri_to_preselected_ind = FALSE OR f.only_contri_to_preselected_ind IS NULL)
LIMIT 100;
"""

# Check if known funders are in top 50
known_funders = {
    '237292730': 'Atherton Family Foundation',
    '990042394': 'Harold K.L. Castle Foundation',
    '996001055': 'Bank of Hawaii Foundation'
}

results = pd.read_sql(query, conn)
for ein, name in known_funders.items():
    if ein in results['ein'].values:
        rank = results[results['ein'] == ein]['rank'].values[0]
        status = '✅' if rank <= 50 else '❌'
        print(f"  {name}: Rank {rank} {status}")
    else:
        print(f"  {name}: Not in top 100 ❌")

# Test Case 2: PSMF (medium org, national healthcare)
print("\n=== Test Case 2: PSMF ===")
print("Client: $5M revenue, CA (national), healthcare education")
# ... similar test ...

conn.close()
```

**Run it:**
```bash
python3 PY_2025-01-03_validate_v6_real_clients.py
```

**Success criteria:**
- ✅ At least 2 of 3 Ka Ulukoa known funders in top 50
- ✅ Top 20 recommendations for small client are NOT all mega-foundations
- ✅ Small org recommendations have high `f_first_time_rate` (open foundations)

---

## Success Metrics

| Metric | V6 (Current) | V6.1 (Target) | Status |
|--------|--------------|---------------|--------|
| **Overall AUC** | 0.98 | 0.82-0.88 | Lower is OK (removing shortcuts) |
| **Small Org AUC** | 0.65 | 0.78-0.84 | 🎯 PRIMARY GOAL |
| **Top coefficient** | r_total_revenue (+4.07) | f_first_time_rate (+1.5 to +2.0) | Should change |
| **Semantic similarity coef** | -0.31 ❌ | +0.3 to +0.8 ✅ | Must fix |
| **Ka Ulukoa validation** | Unknown | ≥2 of 3 funders in top 50 | Real-world test |

---

## Timeline

| Task | Time | Owner |
|------|------|-------|
| Check embedding coverage | 15 min | You |
| Fix semantic similarity | 30 min | You |
| Analyze size distribution | 15 min | You |
| Create size-matched negatives SQL | 1 hour | You |
| Add feature interactions (optional) | 30 min | You |
| Rebuild training data | 30 min | Auto |
| Re-train V6.1 | 1 hour | Auto |
| Validate on real clients | 30 min | You |
| **Total** | **4-5 hours** | |

---

## Rollback Plan

If V6.1 performs worse than expected:

**Acceptable:**
- AUC drops to 0.82 (from 0.98) - expected, because we removed shortcuts
- Small org AUC improves to 0.80+ - THIS IS THE GOAL

**Not acceptable:**
- Small org AUC < 0.75 (worse than random + noise)
- Known funders rank below 100 for test clients
- All coefficients zeroed out by LASSO

**If not acceptable:**
1. Try Approach D instead (sample weighting, simpler)
2. Check if semantic similarity fix helped (compare with/without)
3. Consider removing revenue entirely for small-org-specific model

---

## Questions?

1. **Should I run the embedding coverage check first?** Yes, this determines Step 2a vs 2b.

2. **Can I skip feature interactions (Step 5)?** Yes, do it in Phase 2 if V6.1 base model works.

3. **What if I don't have time for all this?** Minimum viable fix:
   - Step 2 (fix semantic similarity)
   - Step 4 (size-matched negatives)
   - Step 6-7 (rebuild and retrain)
   - Skip Step 5 (interactions) and Step 8 (real client validation) for now

4. **How do I know if it worked?** Look for:
   - Small org AUC ≥ 0.78
   - Top coefficient is foundation openness (not org size)
   - Ka Ulukoa known funders rank in top 50

---

**Files Referenced:**
- Full analysis: `REPORT_2026-01-03_ml_engineering_diagnosis_v6.md`
- Previous review: `REPORT_2026-01-03_ml_review_v6.md`
- This action plan: `ACTION_PLAN_2026-01-03_v6_size_bias_fix.md`
