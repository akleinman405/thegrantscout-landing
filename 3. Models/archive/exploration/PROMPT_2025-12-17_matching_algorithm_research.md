# PROMPT: Matching Algorithm Research & Validation Framework

**Date:** 2025-12-17  
**For:** Research Team  
**Priority:** High - blocks algorithm build

---

## Situation

We're building a foundation-nonprofit matching algorithm. We have:
- 8.3M grants from 143K foundations to 264K recipients
- 100% semantic embedding coverage (grant purposes, missions)
- 43% of grants have recipient EIN (will improve to ~80%+ soon)
- Current algorithm spec uses intuition-based weights, not validated

**Problem:** We can't claim the algorithm "predicts which foundations are most likely to fund a nonprofit" without proving it.

**Goal:** Design and execute a rigorous validation framework so we can make defensible accuracy claims.

---

## Tasks

### Phase 1: Research Methods (2-3 hours)

Before building anything, research best practices for this type of problem.

#### 1A: Recommendation System Approaches

Research and summarize (with pros/cons for our use case):

- **Collaborative Filtering**
  - User-based vs. item-based
  - Matrix factorization (SVD, ALS)
  - Implicit vs. explicit feedback
  
- **Content-Based Filtering**
  - TF-IDF, BM25
  - Semantic embeddings (what we have)
  - Feature engineering approaches

- **Hybrid Methods**
  - Weighted combinations
  - Switching/cascading
  - Feature augmentation

- **Graph-Based Methods**
  - Bipartite graph matching
  - Network analysis (shared funders = edges)
  - Graph neural networks (probably overkill)

#### 1B: Evaluation Metrics for Recommenders

Research standard metrics and which apply to our case:

- Precision@K, Recall@K, F1@K
- Mean Average Precision (MAP)
- Normalized Discounted Cumulative Gain (NDCG)
- Hit Rate / Success@K
- Mean Reciprocal Rank (MRR)
- AUC-ROC for binary classification
- Coverage and diversity metrics

**Key question:** What metric best captures "did we recommend a foundation that actually funded this type of work"?

#### 1C: Cold Start Problem

Research approaches for:
- New nonprofits with no funding history (content-only matching)
- Foundations with sparse grant data
- How to blend signals when some are missing

#### 1D: Similar Systems

Find any published research or case studies on:
- Grant matching algorithms
- Donor-nonprofit matching
- Any philanthropic sector recommendation systems
- Analogous domains (job matching, academic collaboration prediction)

**Output:** `REPORT_2025-12-17_matching_methods_research.md` with findings organized by section above.

---

### Phase 2: Design Validation Framework (2-3 hours)

#### 2A: Create Holdout Test Set

Design methodology to create ground truth:

```
Option A: Time-based split
- Training: 2016-2022 grants
- Test: 2023-2024 grants
- Question: Can we predict 2023-2024 grants from earlier patterns?

Option B: Random holdout
- Randomly hold out 20% of foundation-recipient pairs
- Question: Can we "rediscover" known relationships?

Option C: Leave-one-out by foundation
- For each foundation, hide one recipient
- Question: Can we rank the hidden recipient highly?
```

**Recommend which approach** and why. Consider:
- We care about NEW matches (nonprofits finding foundations they don't know)
- But we validate on KNOWN relationships (the only ground truth we have)
- How do we bridge this gap?

#### 2B: Define Success Metrics

Propose specific metrics with targets:

| Metric | Definition | Target | Why This Target |
|--------|------------|--------|-----------------|
| Precision@10 | Of top 10 recs, how many are actual funders? | ? | ? |
| Recall@100 | Of all actual funders, how many in top 100? | ? | ? |
| MRR | Average reciprocal rank of first correct match | ? | ? |

**Important:** For a nonprofit with 5 known funders among 143K foundations:
- Random baseline Precision@10 = 0.00003 (essentially 0)
- Any score above this is "better than random"
- What's a meaningful threshold for "good"?

#### 2C: Design Signal Tests

Plan experiments to test each signal's predictive power:

| Signal | Test Approach | Hypothesis |
|--------|---------------|------------|
| Semantic similarity | Rank foundations by embedding distance only | Top 100 should contain actual funders at rate >> random |
| Collaborative (shared funders) | Foundations that funded similar orgs | Should predict future funding |
| Geographic match | State alignment | Local foundations more likely to fund local |
| Sector match | NTEE alignment | Sector-focused foundations fund that sector |
| Openness score | Filter by openness | High-openness foundations should have more diverse recipients |
| Grant size fit | Match grant size to org budget | Better fit = higher likelihood |
| Recency | Weight recent grants higher | Recent patterns more predictive than old |

**Output:** `SPEC_2025-12-17_validation_framework.md` with detailed methodology.

---

### Phase 3: Execute Baseline Tests (3-4 hours)

Run initial experiments to establish baselines.

#### 3A: Random Baseline

```sql
-- For each test nonprofit, what's the probability of randomly 
-- selecting one of their actual funders in top K?
```

Calculate expected Precision@K for K = 10, 50, 100, 500 under random selection.

#### 3B: Single-Signal Tests

Test each signal in isolation:

**Semantic-only matching:**
```sql
-- For nonprofit X, rank all foundations by:
-- AVG similarity of foundation's grants to nonprofit's mission embedding
-- Measure: where do actual funders rank?
```

**Collaborative-only matching:**
```sql
-- For nonprofit X with known funders F1, F2, F3:
-- Find other nonprofits funded by F1, F2, F3
-- Their other funders become candidates
-- Measure: do these predict X's other funders?
```

**Geographic-only, Sector-only, etc.**

#### 3C: Combination Tests

Test weighted combinations:
- Equal weights
- Heavy semantic (0.5 semantic, 0.1 each other)
- Heavy collaborative (0.5 collab, 0.1 each other)
- Current spec weights (0.30/0.25/0.20/0.10/0.10/0.05)

#### 3D: Statistical Significance

- Run tests on multiple sample sets
- Calculate confidence intervals
- Determine if differences between approaches are significant

**Output:** `REPORT_2025-12-17_baseline_experiments.md` with:
- Results tables for each test
- Statistical analysis
- Preliminary conclusions on signal value

---

### Phase 4: Optimize & Recommend (2-3 hours)

#### 4A: Weight Optimization

If simple weighted combination works well:
- Grid search over weight combinations
- Or use logistic regression to learn weights from data
- Cross-validate to avoid overfitting

#### 4B: Threshold Analysis

- At what score threshold do we have confidence in a recommendation?
- Precision-recall tradeoff curves
- Recommended cutoffs for "high confidence" vs "worth exploring"

#### 4C: Segment Analysis

Does algorithm perform differently for:
- Large vs small nonprofits?
- Different sectors (health vs education vs arts)?
- National vs local organizations?
- Nonprofits with many vs few known funders?

#### 4D: Final Recommendations

Deliver:
1. **Recommended algorithm** (method + weights)
2. **Defensible accuracy claim** (e.g., "Precision@50 = 12%, which is 400x better than random")
3. **Known limitations** (where it works well vs poorly)
4. **Improvement roadmap** (what would make it better)

**Output:** `SPEC_2025-12-17_matching_algorithm_final.md`

---

## Deliverables Summary

| File | Contents |
|------|----------|
| `REPORT_2025-12-17_matching_methods_research.md` | Literature review, method comparisons |
| `SPEC_2025-12-17_validation_framework.md` | Test design, metrics, methodology |
| `REPORT_2025-12-17_baseline_experiments.md` | Experiment results, statistical analysis |
| `SPEC_2025-12-17_matching_algorithm_final.md` | Final algorithm spec with validated weights |

---

## Key Questions to Answer

1. **What method works best for our data?** (collaborative vs semantic vs hybrid)
2. **What accuracy can we defensibly claim?** (with confidence intervals)
3. **What are the optimal signal weights?** (empirically derived, not guessed)
4. **Where does the algorithm fail?** (so we know limitations)
5. **How do we explain this to customers?** (simple, credible claim)

---

## Database Reference

**Schema:** f990_2025

**Key tables:**
- `fact_grants` - 8.3M grants (foundation_ein, recipient_ein, amount, purpose_text, tax_year)
- `grant_embeddings` - semantic vectors for all grants
- `dim_foundations` - 143K foundations
- `dim_recipients` - 264K recipients
- `calc_foundation_profiles` - pre-computed foundation metrics
- `calc_recipient_profiles` - pre-computed recipient metrics including funder_eins array
- `dim_clients` - 7 test clients with known funders
- `client_embeddings` - mission/project embeddings for clients

**Key fields for validation:**
- `fact_grants.recipient_ein` - links grant to recipient (43% populated, improving)
- `calc_recipient_profiles.funder_eins` - array of foundations that have funded this recipient
- `client_embeddings.combined_embedding` - vector for similarity matching

---

## Notes

- Recipient EIN coverage improving from 43% to ~80%+ (in progress)
- 2023-2024 data is most complete and recent
- Patient assistance foundations should be excluded (drug value, not real grants)
- Focus on foundations with 5+ grants (93,816 foundations) for pattern reliability
