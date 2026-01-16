# V6 Size Bias - One Page Summary

**Date:** 2026-01-03
**Reviewer:** ML Engineer
**Status:** 🔴 CRITICAL - Model is statistically correct but strategically wrong

---

## The Problem

**V6 learned "big organizations get grants" which is TRUE but USELESS for helping small nonprofits.**

```
Current V6 Results:
- Test AUC: 0.9795 (suspiciously high)
- Top predictor: r_total_revenue (+4.07)
- Semantic similarity: -0.31 (WRONG SIGN!)

Size Distribution Reality:
- Tiny orgs (<$100K):    33.8% get grants
- Small orgs ($100K-$1M): 40.4% get grants
- Medium orgs ($1M-$10M): 64.0% get grants
- Large orgs (>$10M):     69.6% get grants

Model learned: P(funding) ≈ 0.34 + 0.41 × log(revenue)
```

**Business Impact:** Will recommend Gates Foundation to $50K food bank. Useless for your target customers (small nonprofits).

---

## Root Cause (3 Issues)

### 1. Training Data Reflects Reality, Not Business Goal

- Positives = actual grants (skewed toward large orgs)
- Negatives = random pairs (also skewed toward large orgs in DB)
- Model took the easy path: learn size pattern first
- Other signals (semantic similarity, openness) too weak/noisy to compete

### 2. Semantic Similarity Has Wrong Sign (-0.31)

**Current implementation:**
```python
# Compares foundation to SECTOR AVERAGE (not actual org)
similarity = cosine(foundation_embedding, sector_avg_embedding)
```

**Why it's negative:**
- Large generic orgs → low similarity → high funding (brand reputation)
- Small specialized orgs → high similarity → low funding (fewer resources to apply)
- Model learned correlation ≠ causation

### 3. Train/Serve Skew

- Training: Use sector averages (generic, diluted)
- Production: Will use client mission (specific, focused)
- Model will under-predict at inference time

---

## Recommended Solution: Size-Matched Negative Sampling

**Approach:** Generate negatives with SAME size distribution as positives.

**Why This Works:**
- Removes size as a shortcut (equal representation per size bucket)
- Forces model to learn openness, geography, sector patterns
- Preserves legitimate size-alignment signal (some foundations only fund large orgs)
- Single unified model (simple deployment)

**Implementation:**
```sql
-- Instead of random negatives, sample proportional to positive distribution
-- If 35% of positives are small orgs, generate 35% small-org negatives
```

**Expected Result:**
- Overall AUC: 0.82-0.88 (down from 0.98, but honest)
- Small org AUC: 0.78-0.84 (up from 0.65, THIS IS THE GOAL)
- Top coefficient: f_first_time_rate (+1.8) not r_total_revenue (+4.07)

---

## Action Items (1-2 Days)

| # | Task | Time | Priority |
|---|------|------|----------|
| 1 | Check if you have actual recipient mission embeddings (vs sector averages) | 15 min | 🔴 CRITICAL |
| 2 | Fix semantic similarity to use actual embeddings | 30 min | 🔴 CRITICAL |
| 3 | Implement size-matched negative sampling SQL | 1 hour | 🔴 CRITICAL |
| 4 | Rebuild training data with balanced negatives | 30 min | 🔴 CRITICAL |
| 5 | Re-train V6.1 | 1 hour | 🔴 CRITICAL |
| 6 | Validate on Ka Ulukoa (real client test) | 30 min | 🟡 HIGH |
| 7 | Add feature interactions (openness × small org) | 30 min | 🟢 OPTIONAL |

**Total critical path:** 3-4 hours

---

## Expected AUC Tradeoffs

| Approach | Overall AUC | Small Org AUC | Complexity | Recommendation |
|----------|-------------|---------------|------------|----------------|
| **Current V6** | 0.98 | 0.65 | Low | ❌ Useless for small clients |
| **Remove revenue entirely** | 0.78-0.84 | 0.75-0.82 | Low | ❌ Throws away real signal |
| **Size-matched negatives** ⭐ | 0.82-0.88 | 0.78-0.84 | Medium | ✅ **BEST** |
| **Sample weighting** | 0.84-0.89 | 0.80-0.86 | Low | ⚠️ Alternative if time-constrained |
| **Size-stratified models** | Varies | Varies | High | ⚠️ Only if >10K positives per size |

---

## Success Criteria

✅ **Small org AUC ≥ 0.78** (2x better than random, useful for ranking)
✅ **Small org AUC within 0.05 of overall AUC** (no systematic bias)
✅ **Top coefficients are actionable:**
   - f_first_time_rate: +1.5 to +2.0 (foundation openness)
   - match_state_pct: +1.0 to +1.5 (geographic match)
   - match_semantic_similarity: +0.3 to +0.8 (mission alignment)
   - r_total_revenue: +0.5 to +0.8 (NOT +4.07!)

✅ **Real client validation:**
   - Ka Ulukoa: ≥2 of 3 known funders rank in top 50
   - Small client test: Top 20 are NOT all mega-foundations

---

## Why Lower AUC is Actually Better

**V6 (0.98 AUC) = Overfitted to size**
- Technically accurate but strategically useless
- Won't help small clients (your target market)
- Learned "big orgs get grants" not "gettable opportunities"

**V6.1 (0.85 AUC) = Honest gettability model**
- Fair to all org sizes
- Learns genuine affinity patterns
- Production use case is **ranking top 100**, not binary classification
- Precision@100 > 0.60 is success

**Remember:** You're not predicting "will this org get a grant?" You're answering "which foundations should this org approach?" Different problems!

---

## Files Created

| File | Purpose |
|------|---------|
| `REPORT_2026-01-03_ml_engineering_diagnosis_v6.md` | Full 30-page analysis (read this for details) |
| `ACTION_PLAN_2026-01-03_v6_size_bias_fix.md` | Step-by-step implementation guide |
| `SUMMARY_2026-01-03_v6_size_bias_one_pager.md` | This executive summary |

---

## Bottom Line

**Current V6 is like a college admissions model that learned "rich kids get into Harvard."**
**TRUE, but not helpful for a poor student asking "where should I apply?"**

**V6.1 will learn "which colleges accept students like you" - lower overall accuracy, but actually useful.**

**Question:** Ready to implement size-matched sampling? Check embedding coverage first (15 min query).
