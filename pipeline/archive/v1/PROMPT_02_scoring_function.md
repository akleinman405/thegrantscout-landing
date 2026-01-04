# PROMPT_02: Phase 2 - Scoring Function

**Date:** 2025-12-27
**Phase:** 2
**Agent:** Dev Team
**Estimated Time:** 4-5 hours
**Depends On:** PROMPT_01 (Infrastructure) complete

---

## Objective

Build the scoring function that takes a nonprofit EIN and returns ranked foundation matches using the LASSO model coefficients.

---

## Context

**Model:** LASSO Logistic Regression (V3-Ablation)
- AUC: 0.910
- 56 non-zero coefficients
- Trained on 3.45M foundation-recipient pairs

**Key Insight:** Model predicts probability of a grant match. Higher score = more likely match.

---

## Input Files

| File | Location | Description |
|------|----------|-------------|
| Coefficients | `Take 2/outputs/v3/r_lasso_output_v3_ablation/coefficients_nonzero.csv` | 56 feature weights |
| Scaling Params | `Take 2/outputs/v3/r_lasso_output_v3_ablation/scaling_parameters.csv` | Mean/SD for standardization |
| Imputation Values | `Take 2/outputs/v3/r_lasso_output_v3_ablation/imputation_values.csv` | Median values for NA handling |
| Feature List | `Take 2/outputs/v3/r_lasso_output_v3_ablation/feature_list_ablation.txt` | 59 features used |

**Note:** The "Take 2" folder is at:
`/Users/aleckleinman/Documents/TheGrantScout/1. Database/5. Matching Algorithm/Logistic Regression Modeling/Take 2`

---

## Tasks

### Task 1: Export Model Parameters to JSON

Convert R CSV outputs to JSON format for Python.

**Create `config/coefficients.json`:**
```json
{
    "intercept": -1.234,
    "coefficients": {
        "f_total_grants": 1.85,
        "match_same_state": 1.57,
        "f_repeat_rate": -0.92,
        ...
    }
}
```

**Create `config/scaling.json`:**
```json
{
    "f_total_grants": {"mean": 123.45, "sd": 456.78},
    "match_same_state": {"mean": 0.15, "sd": 0.36},
    ...
}
```

**Create `config/imputation.json`:**
```json
{
    "f_total_grants": 50,
    "r_assets": 100000,
    ...
}
```

### Task 2: Create `scoring/features.py`

Feature calculator that computes all features for a foundation-nonprofit pair.

**Required Functions:**

```python
def get_foundation_features(foundation_ein: str) -> dict:
    """
    Get pre-computed foundation features from database.
    
    Returns dict with keys like:
    - f_total_grants
    - f_avg_grant
    - f_repeat_rate
    - f_in_state_pct
    - f_openness_score
    - f_state_CA, f_state_NY, etc.
    - ... (all f_* features)
    """

def get_recipient_features(recipient_ein: str) -> dict:
    """
    Get/compute recipient features from database.
    
    Returns dict with keys like:
    - r_assets
    - r_employee_count
    - r_total_revenue
    - r_state_CA, r_state_NY, etc.
    - r_ntee_A, r_ntee_B, etc.
    - r_size_SMALL, r_size_MEDIUM, etc.
    - ... (all r_* features, EXCLUDING r_total_grants family)
    """

def compute_match_features(foundation_ein: str, recipient_ein: str) -> dict:
    """
    Compute match features between foundation and recipient.
    
    Returns dict with keys like:
    - match_same_state (1 if same state, 0 otherwise)
    """

def calculate_features(foundation_ein: str, recipient_ein: str) -> dict:
    """
    Calculate all features for a foundation-recipient pair.
    
    Combines foundation, recipient, and match features.
    Handles missing values using imputation.
    
    Returns dict with all 59 features.
    """
```

**Database Queries Needed:**

Foundation features come from `f990_2025.dim_foundations` and aggregations of `f990_2025.fact_grants`.

Recipient features come from `f990_2025.dim_recipients` joined with nonprofit returns.

Match features are computed from foundation and recipient data.

### Task 3: Create `scoring/scoring.py`

Main scoring module.

**Required Class/Functions:**

```python
class GrantScorer:
    def __init__(self, 
                 coefficients_path: str = "config/coefficients.json",
                 scaling_path: str = "config/scaling.json",
                 imputation_path: str = "config/imputation.json"):
        """Load model parameters."""
        
    def score_pair(self, foundation_ein: str, recipient_ein: str) -> float:
        """
        Score a single foundation-recipient pair.
        
        Returns probability (0-1) of match.
        """
        
    def score_nonprofit(self, 
                        recipient_ein: str, 
                        top_k: int = 50,
                        exclude_prior_funders: bool = True) -> pd.DataFrame:
        """
        Score all foundations for a given nonprofit.
        
        Args:
            recipient_ein: The nonprofit's EIN
            top_k: Number of top matches to return
            exclude_prior_funders: If True, exclude foundations that have 
                                   already funded this nonprofit
        
        Returns DataFrame with columns:
            - foundation_ein
            - foundation_name
            - match_score (0-100 scale)
            - match_probability (0-1 scale)
            - match_rank (1 to top_k)
        """
```

**Scoring Logic:**

1. Get all foundation EINs from database
2. For each foundation:
   - Calculate features
   - Standardize using scaling parameters
   - Apply logistic regression: `score = sigmoid(intercept + sum(coef * feature))`
3. Sort by score descending
4. Return top K

**Performance Consideration:**

Computing features for 143K foundations is expensive. Options:
- Pre-compute foundation features in database table
- Cache foundation features on first load
- Batch SQL queries instead of one-by-one

Recommend: Pre-compute foundation features in a materialized view or table.

### Task 4: Create Foundation Features Table (SQL)

Create a table with pre-computed foundation features to speed up scoring.

```sql
CREATE TABLE IF NOT EXISTS f990_2025.foundation_features AS
SELECT 
    foundation_ein,
    -- f_* features calculated here
    ...
FROM f990_2025.dim_foundations f
LEFT JOIN (
    -- aggregations from fact_grants
) g ON f.ein = g.foundation_ein;

CREATE INDEX idx_foundation_features_ein ON f990_2025.foundation_features(foundation_ein);
```

### Task 5: Test Scoring Function

**Test Cases:**

1. **Known good match:** Pick a foundation-recipient pair that exists in fact_grants. Score should be high (>0.5).

2. **Known bad match:** Pick a foundation that only funds in California and a recipient in New York. Score should be lower.

3. **Top-K ranking:** For a sample nonprofit, get top 50 matches. Verify:
   - Results are sorted by score
   - No duplicates
   - Prior funders excluded (if flag set)

4. **Performance:** Score one nonprofit in < 30 seconds.

---

## Output Files

| File | Description |
|------|-------------|
| `config/coefficients.json` | Model coefficients |
| `config/scaling.json` | Feature scaling parameters |
| `config/imputation.json` | NA imputation values |
| `scoring/features.py` | Feature calculator |
| `scoring/scoring.py` | Scoring module |
| SQL script for foundation_features table | Pre-computed features |

---

## Done Criteria

- [ ] `config/coefficients.json` contains intercept + 56 coefficients
- [ ] `config/scaling.json` contains mean/sd for all features
- [ ] `config/imputation.json` contains imputation values
- [ ] `scoring/features.py` calculates all 59 features
- [ ] `scoring/scoring.py` `GrantScorer` class works
- [ ] `score_nonprofit()` returns DataFrame with correct columns
- [ ] Scoring completes in < 30 seconds for one nonprofit
- [ ] Foundation features table created in database

---

## Verification Tests

### Test 1: Config Files Valid
```python
import json
with open('config/coefficients.json') as f:
    coefs = json.load(f)
    print(f"Intercept: {coefs['intercept']}")
    print(f"Num coefficients: {len(coefs['coefficients'])}")
    assert len(coefs['coefficients']) == 56
```

### Test 2: Feature Calculation
```python
from scoring.features import calculate_features

# Use a known foundation and recipient from database
features = calculate_features('FOUNDATION_EIN', 'RECIPIENT_EIN')
print(f"Num features: {len(features)}")
assert len(features) == 59
```

### Test 3: Single Pair Scoring
```python
from scoring.scoring import GrantScorer

scorer = GrantScorer()
prob = scorer.score_pair('FOUNDATION_EIN', 'RECIPIENT_EIN')
print(f"Match probability: {prob:.3f}")
assert 0 <= prob <= 1
```

### Test 4: Top-K Ranking
```python
from scoring.scoring import GrantScorer

scorer = GrantScorer()
results = scorer.score_nonprofit('RECIPIENT_EIN', top_k=10)
print(results)
assert len(results) == 10
assert 'match_score' in results.columns
assert 'match_rank' in results.columns
assert results['match_rank'].tolist() == list(range(1, 11))
```

### Test 5: Performance
```python
import time
from scoring.scoring import GrantScorer

scorer = GrantScorer()
start = time.time()
results = scorer.score_nonprofit('RECIPIENT_EIN', top_k=50)
elapsed = time.time() - start
print(f"Scoring time: {elapsed:.1f} seconds")
assert elapsed < 30
```

---

## Notes

### Features EXCLUDED (Ablation Model)

The ablation model excludes these recipient history features:
- r_total_grants
- r_total_funders
- r_total_funding
- r_funding_trend
- r_funder_states

Do NOT include these in feature calculation.

### Feature Standardization

Before applying coefficients, standardize each feature:
```python
standardized = (raw_value - mean) / sd
```

Use values from `scaling.json`.

### Sigmoid Function

```python
def sigmoid(x):
    return 1 / (1 + np.exp(-x))
```

### Score Scaling

Model outputs probability (0-1). For user display, convert to 0-100 scale:
```python
match_score = match_probability * 100
```

---

## Handoff

After completion:
1. Run all verification tests
2. Document any foundations/recipients used for testing
3. Note performance characteristics
4. PM reviews before proceeding to PROMPT_03a

---

*Next: PROMPT_03a (Funder Snapshot SQL)*
