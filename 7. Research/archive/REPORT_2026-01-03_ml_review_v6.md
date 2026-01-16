# ML Engineering Review: Grant Matching V6

**Reviewer:** ML Engineer (Claude Code)
**Date:** 2026-01-03
**Reviewed:** V6 training data generation and model design
**Status:** CRITICAL ISSUES IDENTIFIED - DO NOT TRAIN UNTIL FIXED

---

## Executive Summary

V6 has made excellent progress removing feature leakage and adding semantic similarity. However, **there are 4 critical ML issues that will invalidate results if not fixed:**

1. **CRITICAL:** No negatives in validation/test sets (0 negatives in 2023-2024)
2. **CRITICAL:** Temporal leakage in `f_funded_new_recently` feature
3. **HIGH:** 99.8% correlation between `f_openness_score` and `f_first_time_rate`
4. **MEDIUM:** Semantic similarity approach may not generalize to cold-start

---

## Issue 1: Missing Negatives in Validation/Test (CRITICAL)

### Problem

Looking at `SQL_2025-01-02_v5_training_data_fast.sql` line 142-148:

```sql
-- Negatives (assign random tax year)
SELECT
    foundation_ein,
    recipient_ein,
    2017 + (RANDOM() * 5)::int as tax_year,  -- ← ONLY assigns 2017-2022!
    label,
    sample_type
FROM stg_v5_negatives;
```

This assigns negatives **only to years 2017-2022** (random integer 0-5 added to 2017).

Result:
- **2023 validation:** 94,597 positives, **0 negatives**
- **2024 test:** 11,894 positives, **0 negatives**

### Why This is Critical

1. **Invalid metrics:** AUC on all-positive data is meaningless (model can predict 1.0 for everything and get "perfect" score)
2. **No false positive rate:** Cannot measure specificity, precision, or calibration
3. **Overfitting undetected:** Model could memorize training data patterns and you wouldn't know

### Root Cause

Your positive examples are **actual grants with real tax years** (2017-2024), but negatives are **synthetic pairs with assigned years** restricted to training range.

### ML-Correct Solutions

**Option A: Stratified Random Split (RECOMMENDED)**

Abandon temporal split entirely. Use random 70/15/15 split stratified by label.

**Pros:**
- Standard ML practice for i.i.d. data
- Ensures balanced classes in all splits
- Simpler to implement

**Cons:**
- Cannot claim "future prediction" capability
- Some 2024 grants in training may be similar to 2024 grants in test (but that's realistic)

**Implementation:**
```python
from sklearn.model_selection import train_test_split

# First split: 70% train, 30% temp
train, temp = train_test_split(df, test_size=0.3, stratify=df['label'], random_state=42)

# Second split: 15% val, 15% test
val, test = train_test_split(temp, test_size=0.5, stratify=temp['label'], random_state=42)
```

**Option B: Generate Negatives for 2023-2024**

Keep temporal split but create negatives for future years.

**Pros:**
- Maintains temporal validation story
- Tests true "predict future matches" capability

**Cons:**
- More complex
- Negatives in 2023-2024 are synthetic (positives are real grants)
- Need to be careful about what foundation/recipient features are available

**Implementation:**
```sql
-- In stg_v5_negatives, assign random year from FULL range
2017 + (RANDOM() * 7)::int as tax_year  -- 2017-2024 (8 years = 0-7)
```

**Option C: Positive-Unlabeled Learning**

Treat 2023-2024 as positive-only validation, use PU learning techniques.

**Pros:**
- Theoretically sound for one-class problems
- More realistic (you only observe actual grants, not "non-grants")

**Cons:**
- Complex to implement
- Requires PU-specific metrics
- Hard to explain to stakeholders

### My Recommendation

**Use Option A (random split)** for these reasons:

1. **Your problem is NOT truly temporal:** Foundation giving patterns don't change drastically year-to-year. A 2024 grant is similar to a 2022 grant from the same foundation.

2. **You're predicting affinity, not time-series:** You're not forecasting "will Foundation X increase giving in 2024?" You're predicting "does Foundation X have affinity for Nonprofit Y?" That's stable over time.

3. **Real-world usage:** When scoring a new client, you'll use the most recent foundation data available. There's no "predicting the future" - you're matching current nonprofits to current foundations.

4. **Simplicity:** Random split is standard, well-understood, and avoids the validation/test bug.

If you insist on temporal split, use **Option B** but be aware it's philosophically questionable for this use case.

---

## Issue 2: Temporal Leakage in `f_funded_new_recently` (CRITICAL)

### Problem

From `SQL_2025-01-02_v6_training_data.sql` line 218:

```sql
-- NEW: Foundation funded a new recipient in 2023-2024 (active openness signal)
CASE WHEN fnr.foundation_ein IS NOT NULL THEN 1 ELSE 0 END as f_funded_new_recently,
```

This feature is computed from `stg_foundations_funded_new_recently` (line 156-158):

```sql
CREATE TABLE stg_foundations_funded_new_recently AS
SELECT DISTINCT foundation_ein
FROM stg_first_time_grants
WHERE tax_year >= 2023;
```

**If you're testing on 2024 grants**, this feature uses **2024 data** to predict **2024 grants**. That's leakage.

### Why This is Critical

Example leakage scenario:
- Foundation X gives first-time grant to Org Y in **June 2024**
- This grant gets assigned to **test set** (tax_year = 2024, label = 1)
- Feature `f_funded_new_recently = 1` because Foundation X funded new org **in 2024**
- Model learns "if f_funded_new_recently=1, predict positive" and gets artificially high accuracy

### ML-Correct Solution

**Point-in-time feature computation:** For each sample, only use data **available before** that grant's tax year.

```sql
-- FIXED: Time-aware feature
CASE WHEN EXISTS (
    SELECT 1 FROM stg_first_time_grants ftg
    WHERE ftg.foundation_ein = tp.foundation_ein
      AND ftg.tax_year >= (tp.tax_year - 2)  -- Last 2 years BEFORE this sample
      AND ftg.tax_year < tp.tax_year          -- Strict inequality
) THEN 1 ELSE 0 END as f_funded_new_recently
```

**Alternative:** If using random split (Option A from Issue 1), this feature is less problematic because all years are mixed. But you should still use a **rolling window** (e.g., "funded new in last 2 years") rather than fixed cutoff.

---

## Issue 3: Correlation Between `f_openness_score` and `f_first_time_rate` (HIGH)

### Problem

You report **99.8% correlation** between these features. They're measuring the same thing:

- `f_openness_score`: Accepts applications AND not preselected_only
- `f_first_time_rate`: Historical % of grants to new recipients

Both answer "how open is this foundation to new applicants?"

### Why This Matters

1. **Multicollinearity:** LASSO will arbitrarily pick one or zero both out
2. **Coefficient instability:** Small data changes cause large coefficient swings
3. **Interpretation confusion:** Which one "really" matters?

### ML-Correct Solution

**Drop one explicitly.** My recommendation:

**KEEP: `f_first_time_rate`**
**DROP: `f_openness_score`**

**Rationale:**
- `f_first_time_rate` is **behavior-based** (what foundation actually does)
- `f_openness_score` is **self-reported** (what foundation says in Form 990)
- Behavior > words

```sql
-- REMOVE from training_data_v6:
-- cf.openness_score as f_openness_score,  ← DELETE THIS LINE
```

**Alternative:** Create a **composite feature**:

```sql
-- Combined openness signal (max of the two)
GREATEST(
    cf.openness_score,
    COALESCE(cf.first_time_rate, 0.3)
) as f_openness_combined
```

But I'd prefer the simple solution: drop `f_openness_score`.

---

## Issue 4: Semantic Similarity Generalization (MEDIUM)

### Problem

From `PY_2025-01-02_v6_export_training.py` lines 266-278:

```python
def get_semantic_sim(row):
    fein = row['foundation_ein']
    ntee = row['r_ntee_broad']

    if fein not in foundation_embeddings:
        return 0.0
    if ntee not in sector_embeddings:
        return 0.0

    return cosine_similarity(
        foundation_embeddings[fein],      # ← Foundation's avg grant embedding
        sector_embeddings[ntee]            # ← Sector's avg embedding
    )
```

**At training time:** You're comparing foundation embedding to **sector average**.

**At scoring time:** You'll compare foundation embedding to **client's actual mission** (much more specific).

### Why This Might Be a Problem

1. **Train/serve skew:** Model learns from sector averages but sees specific missions at inference
2. **Signal dilution:** Sector averages wash out specificity. "Healthcare" sector average is very generic.
3. **Missing variance:** All healthcare nonprofits get the same similarity score to a foundation

### Is This Actually Bad?

**Maybe not!** Here's the case for your approach:

**Pros:**
- You don't have mission statements for historical grant recipients (only NTEE codes)
- Sector average is a reasonable proxy
- At scoring time, client embedding will be MORE informative than sector average, so model may underestimate fit (conservative bias is OK)

**Cons:**
- Model may learn weak coefficient for semantic similarity because signal is noisy
- Calibration will be off (higher similarity at inference than training)

### ML-Correct Solutions

**Option A: Use Actual Recipient Embeddings (BEST)**

If you have mission statements or program descriptions for recipients, use those:

```sql
-- In training data, use actual recipient embedding
LEFT JOIN nonprofit_mission_embeddings nme ON tp.recipient_ein = nme.ein
```

Then at scoring time, use client mission embedding (train/serve consistency).

**Option B: Create "Synthetic Mission" for Recipients**

Generate synthetic mission text from NTEE code + org name:

```python
# For training data
recipient_synthetic_mission = f"{recipient_name} is a {ntee_description} organization"
recipient_embedding = model.encode(recipient_synthetic_mission)
```

This gives you something more specific than sector average.

**Option C: Keep Your Approach BUT Track It**

If you don't have recipient embeddings, your approach is pragmatic. Just:

1. **Flag it as approximation** in model docs
2. **Expect coefficient to be small** (noisy signal)
3. **Monitor at inference:** If `match_semantic_similarity` is much higher at scoring than in training data, model may under-predict

**My Recommendation:**

Check if `nonprofit_mission_embeddings` table has coverage for your recipients:

```sql
SELECT
    COUNT(*) as total_recipients,
    COUNT(nme.ein) as with_mission_embedding,
    ROUND(100.0 * COUNT(nme.ein) / COUNT(*), 1) as pct_coverage
FROM (SELECT DISTINCT recipient_ein FROM training_data_v6) r
LEFT JOIN nonprofit_mission_embeddings nme ON r.recipient_ein = nme.ein;
```

- **If >50% coverage:** Use actual embeddings (Option A)
- **If <50% coverage:** Use your sector average approach (Option C)

---

## Issue 5: Cold-Start Feature Availability (MEDIUM)

### Question You Asked

> For a cold-start problem (new client seeking foundations), what features matter most?

### Analysis

When a **brand new nonprofit** (never received grants) comes to you:

**Features they HAVE:**
- `r_total_revenue` (from 990)
- `r_state` (from address)
- `r_ntee_broad` (sector)
- `r_org_age` (from ruling date)
- Client mission embedding (from questionnaire)

**Features they DON'T have:**
- ~~`r_total_grants`~~ (you removed this - good!)
- ~~`r_total_funders`~~ (you removed this - good!)
- ~~`r_total_funding`~~ (you removed this - good!)

**V6 is well-designed for cold-start!** You've removed the problematic features.

**Most Important Features for Cold-Start:**

1. **`match_semantic_similarity`** - Does foundation fund orgs like this one?
2. **`match_sector_pct`** - Does foundation fund this sector?
3. **`match_state_pct`** - Does foundation fund this state?
4. **`f_openness_score` / `f_first_time_rate`** - Does foundation fund NEW orgs?
5. **`r_total_revenue`** - Does org size align with foundation's typical grant?

**Test this explicitly:**

After training, filter test set to only new orgs:

```python
# New orgs = first grant in dataset is in 2023-2024
new_orgs = test[test.groupby('recipient_ein')['tax_year'].transform('min') >= 2023]

# Evaluate model on just new orgs
auc_new_orgs = roc_auc_score(new_orgs['label'], new_orgs['predictions'])
print(f"AUC on new orgs only: {auc_new_orgs:.3f}")
```

**Expected:** AUC on new orgs should be 0.05-0.10 lower than overall AUC (they're harder to predict). If it's much worse, you have a problem.

---

## Expected AUC After Fixes

### V5 Results (With Leaky Features)

- Train AUC: ~0.98
- Validation AUC: 0.980
- Test AUC: 0.969

### V6 Expected (After Fixing Issues)

**Optimistic scenario (everything works):**
- AUC: 0.90-0.92
- Precision@100: 0.65-0.70 (65-70 of top 100 are true matches)

**Realistic scenario (semantic similarity helps modestly):**
- AUC: 0.88-0.90
- Precision@100: 0.60-0.65

**Pessimistic scenario (semantic similarity doesn't help):**
- AUC: 0.85-0.88
- Precision@100: 0.55-0.60

### Why Lower Than V5?

1. **Removed leaky features:** `r_total_grants` (+4.18) was your top predictor
2. **Harder problem:** Predicting affinity without knowing past funding history
3. **Less data:** Removed multicollinear features means fewer signals

### Is 0.88-0.90 AUC "Good Enough"?

**Yes, absolutely.** Here's why:

1. **Production context:** You're showing clients top 20-50 foundations. Even 0.85 AUC is useful if top-ranked foundations are good matches.

2. **Baseline comparison:** Random guessing AUC = 0.50. You'd be 40 points higher.

3. **Real-world validation:** If your model puts Ka Ulukoa's actual funders (Atherton, etc.) in top 50, it's working regardless of AUC.

**Focus on ranking metrics**, not just AUC:

- **Precision@20:** What % of your top 20 recommendations are actually good fits?
- **Recall@100:** Of all the foundations that WOULD fund this client, what % are in your top 100?
- **NDCG:** Normalized discounted cumulative gain (rewards putting best matches at the top)

---

## Recommendations for Training Pipeline

### 1. Data Splitting

```python
# In PY_2025-01-02_v6_export_training.py

# REPLACE lines 410-417 with:
from sklearn.model_selection import train_test_split

# Random stratified split (not temporal)
df_train, df_temp = train_test_split(
    df_features,
    test_size=0.3,
    stratify=df_features['label'],
    random_state=42
)

df_val, df_test = train_test_split(
    df_temp,
    test_size=0.5,
    stratify=df_temp['label'],
    random_state=42
)

print(f"\nSplits (random stratified):")
print(f"  Train (70%):        {len(df_train):,} rows ({df_train['label'].mean()*100:.1f}% positive)")
print(f"  Validation (15%):   {len(df_val):,} rows ({df_val['label'].mean()*100:.1f}% positive)")
print(f"  Test (15%):         {len(df_test):,} rows ({df_test['label'].mean()*100:.1f}% positive)")
```

### 2. Feature Cleanup

```python
# In add_derived_features(), ADD:

# Drop openness_score (99.8% correlated with first_time_rate)
df = df.drop(columns=['f_openness_score'], errors='ignore')
```

### 3. Temporal Leakage Fix

```sql
-- In SQL_2025-01-02_v6_training_data.sql line 218, REPLACE with:

-- FIXED: Recently active signal (look back 2 years from sample year)
-- This will be NULL for samples before 2019, which is fine (impute to 0.5)
cf.last_grant_year >= (tp.tax_year - 2)
  AND cf.last_grant_year < tp.tax_year as f_funded_new_recently_safe
```

But honestly, if you use random split (Recommendation #1), this feature becomes safe as-is.

### 4. Enhanced Evaluation

```R
# In R_2025-01-02_lasso_v6.R, ADD:

# Evaluate on new orgs only
test_with_history = test[test$r_org_age > 5, ]
test_new_orgs = test[test$r_org_age <= 5, ]

cat("\n=== Segmented Performance ===\n")
cat(sprintf("AUC (established orgs, age>5): %.3f\n",
            auc(test_with_history$label, predict(cv_model, test_with_history, s = "lambda.min"))))
cat(sprintf("AUC (new orgs, age<=5): %.3f\n",
            auc(test_new_orgs$label, predict(cv_model, test_new_orgs, s = "lambda.min"))))
```

### 5. Ablation Study

After V6 trains successfully, test whether new features help:

```R
# Train V6-baseline (V5 features only, no leakage)
features_baseline = c("f_assets", "f_repeat_rate", "match_state_pct", ...) # V5 features

# Train V6-full (V5 + semantic + new features)
features_full = c(features_baseline, "match_semantic_similarity", "f_is_accessible", ...)

# Compare AUCs
# If V6-full > V6-baseline by <0.02, new features didn't help much
```

---

## Summary of Action Items

**MUST FIX (blocking issues):**

1. ✅ **Change to random stratified split** (not temporal) to fix validation/test negatives
2. ✅ **Drop `f_openness_score`** (99.8% correlated with `f_first_time_rate`)

**SHOULD FIX (temporal leakage):**

3. ⚠️ If using random split, `f_funded_new_recently` is safe. If insisting on temporal split, fix it to be point-in-time.

**NICE TO HAVE (improvements):**

4. 📊 Add ranking metrics (Precision@K, NDCG) to evaluation
5. 🧪 Run ablation study to measure value of new features
6. 📈 Test explicitly on new orgs (age < 5 years) to validate cold-start performance

**VALIDATE:**

7. 🔍 Check coverage of `nonprofit_mission_embeddings` for actual recipient embeddings
8. 🎯 After training, run Ka Ulukoa test case (actual funders should rank in top 50)

---

## Expected Timeline

| Step | Time | Status |
|------|------|--------|
| Fix data splitting (random stratified) | 30 min | TO DO |
| Remove f_openness_score | 5 min | TO DO |
| Re-export training data | 10 min | TO DO |
| Train V6 model | 20 min | TO DO |
| Evaluate and compare to V5 | 15 min | TO DO |
| Run ablation study | 30 min | OPTIONAL |
| **Total (required)** | **1h 20m** | |

---

## Final Thoughts

You've done **excellent work** identifying and removing feature leakage. The semantic similarity addition is creative and should help.

The bugs I found (missing negatives, temporal leakage) are **easy to fix** but would have caused major headaches if you'd trained and deployed.

**Key insight:** Your problem is **not actually temporal**. Foundation giving patterns are relatively stable. Using random split is simpler, more standard, and avoids subtle bugs.

After fixes, I expect **V6 to have 0.88-0.92 AUC** with much better fairness to new nonprofits than V5.

---

**Questions? Let me know and I'll dive deeper into any section.**

*ML Review completed 2026-01-03 by Claude Code (Sonnet 4.5)*
