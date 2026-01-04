# BUILD PLAN: Report Generation Pipeline (v2)

**Created:** 2025-12-26
**Updated:** 2025-12-26
**Goal:** Automated pipeline from client EIN → finished Word doc report
**Target:** Production-ready for 50 clients by January 2026

---

## Overview

```
Client EIN + Questionnaire
        ↓
[Phase 0] Infrastructure Setup → DB connections, API keys, logging
        ↓
[Phase 1] Model Validation → Confirm LASSO model is usable
        ↓
[Phase 2] Scoring Function → Top 50 foundations ranked
        ↓
[Phase 3] DB Enrichment Queries → Funder Snapshots (cached)
        ↓
[Phase 4] Report Data Assembly → Structured table with all fields
        ↓
[Phase 5] Just-in-Time Scraper → Fill gaps (deadlines, contacts, URLs)
        ↓
[Phase 6] AI Narrative Generation → Why This Fits, Positioning Strategy
        ↓
[Phase 7] MD Assembly → Complete markdown report
        ↓
[Phase 8] Word Doc Conversion → Branded deliverable
        ↓
[Phase 9] Testing & Validation → Quality checks, client feedback
```

---

## Phase 0: Infrastructure Setup

**Status:** NEW - Required foundation for all other phases

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 0.1 | Create project structure | Directory layout | 30 min |
| 0.2 | Database connection config | `config/database.py` | 1 hr |
| 0.3 | API key management (Anthropic) | `config/secrets.py` + .env | 30 min |
| 0.4 | Logging setup | `utils/logging.py` | 1 hr |
| 0.5 | Output directory structure | `outputs/`, `cache/`, `logs/` | 15 min |
| 0.6 | Questionnaire data loader | `loaders/questionnaire.py` | 1.5 hr |
| 0.7 | Create requirements.txt | Dependencies | 15 min |

### Project Structure

```
thegrantscout-pipeline/
├── config/
│   ├── database.py          # DB connection settings
│   ├── secrets.py           # API keys (reads from .env)
│   ├── coefficients.json    # LASSO model coefficients
│   └── scaling.json         # Feature scaling parameters
├── loaders/
│   ├── questionnaire.py     # Load client questionnaire data
│   └── client_data.py       # Client EIN → full profile
├── scoring/
│   ├── scoring.py           # Main scoring function
│   └── features.py          # Feature calculator
├── enrichment/
│   ├── db_queries.py        # SQL query templates
│   ├── funder_snapshot.py   # Build funder snapshots
│   └── cache.py             # Caching layer
├── scraper/
│   ├── scraper.py           # Foundation website scraper
│   ├── extractors.py        # Field-specific extractors
│   └── fallback.py          # Manual entry fallback
├── ai/
│   ├── narratives.py        # AI generation functions
│   └── prompts/             # Prompt templates
│       ├── why_this_fits.txt
│       ├── positioning.txt
│       ├── next_steps.txt
│       └── executive_summary.txt
├── rendering/
│   ├── md_renderer.py       # Markdown assembly
│   └── templates/
│       └── report_template.md
├── outputs/
│   ├── reports/             # Generated reports
│   ├── cache/               # Cached funder snapshots
│   └── logs/                # Execution logs
├── tests/
│   ├── test_scoring.py
│   ├── test_enrichment.py
│   └── test_pipeline.py
├── generate_report.py       # Main CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

### Database Connection Config

```python
# config/database.py
import os
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

# Connection pool for efficiency
pool = None

def init_pool():
    global pool
    pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_NAME', 'thegrantscout'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )

@contextmanager
def get_connection():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

def query_df(sql: str, params: dict = None) -> pd.DataFrame:
    """Execute query and return DataFrame."""
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=params)
```

### Questionnaire Data Loader

```python
# loaders/questionnaire.py
import pandas as pd
from pathlib import Path

QUESTIONNAIRE_PATH = Path("data/Grant_Alerts_Questionnaire.csv")

def load_questionnaire(ein: str = None) -> dict:
    """
    Load client questionnaire data.
    
    Returns dict with:
    - organization_name
    - email
    - org_type
    - location (state, city)
    - budget
    - grant_size_target
    - program_areas (list)
    - populations_served (list)
    - geographic_scope
    - ntee_code
    - mission_statement
    - prior_funders (list)
    - notes
    """
    df = pd.read_csv(QUESTIONNAIRE_PATH)
    
    # Map column names to clean keys
    column_map = {
        'Organization Name': 'organization_name',
        'Email Address (The one you want us to send matched grant opportunities to)': 'email',
        'Organization Type': 'org_type',
        'Where is your organization headquartered?': 'state',
        'What City is your organization located in?': 'city',
        'Your most recent annual budget.': 'budget',
        'What size grants are you typically looking for?': 'grant_size_target',
        'What are your organization\'s primary program areas?': 'program_areas',
        'Select all populations your organization primarily serves': 'populations_served',
        'What geographic range does your organization serve?': 'geographic_scope',
        'If you know your IRS NTEE classification code': 'ntee_code',
        'In 1-2 sentences, what does your organization do?': 'mission_statement',
        'Which funders have you received grants from within the last year?': 'prior_funders',
        'Anything else we should know': 'notes'
    }
    
    df = df.rename(columns=column_map)
    
    if ein:
        # Filter by EIN if provided
        row = df[df['ein'] == ein].iloc[0]
    else:
        # Return all as list of dicts
        return df.to_dict('records')
    
    # Parse list fields
    result = row.to_dict()
    for field in ['program_areas', 'populations_served', 'prior_funders']:
        if pd.notna(result.get(field)):
            result[field] = [x.strip() for x in str(result[field]).split(';')]
        else:
            result[field] = []
    
    return result
```

### Environment File

```bash
# .env.example
DB_HOST=localhost
DB_PORT=5432
DB_NAME=thegrantscout
DB_USER=postgres
DB_PASSWORD=your_password_here

ANTHROPIC_API_KEY=your_api_key_here

LOG_LEVEL=INFO
CACHE_TTL_DAYS=7
```

---

## Phase 1: Model Validation ✓ IN PROGRESS

**Status:** LASSO v2 script ready to run

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 1.1 | Run LASSO v2 script in RStudio | Model outputs in `r_lasso_output_v2/` | 15 min |
| 1.2 | Review metrics (AUC, precision, recall) | Decision: adopt or iterate | 30 min |
| 1.3 | Examine non-zero coefficients | Which features matter? | 30 min |
| 1.4 | Compare to v1 results | Confirm data fixes helped | 30 min |
| 1.5 | Export coefficients to JSON | `config/coefficients.json` | 15 min |
| 1.6 | Export scaling params to JSON | `config/scaling.json` | 15 min |
| 1.7 | Decision gate | Go/no-go on LASSO model | — |

### Success Criteria
- AUC > 0.70 (realistic expectation after fixing data issues)
- Coefficients make intuitive sense (same_state positive, openness positive, etc.)
- Hit rate @ 20 > random baseline
- No single feature dominates (unlike v1's r_has_features)

### Decision Points
- If AUC < 0.65: revisit feature engineering, consider adding semantic similarity
- If AUC 0.65-0.70: proceed with caution, plan iteration
- If AUC > 0.70: adopt model, move to Phase 2

### Coefficient Export Script

```r
# Run after LASSO training completes
library(jsonlite)

# Load results
coefs <- fread("r_lasso_output_v2/coefficients_nonzero_v2.csv")
scaling <- fread("r_lasso_output_v2/scaling_parameters_v2.csv")

# Export to JSON for Python
coef_list <- setNames(as.list(coefs$coefficient), coefs$feature)
write_json(coef_list, "../config/coefficients.json", pretty = TRUE)

scaling_list <- list(
    means = setNames(as.list(scaling$mean), scaling$feature),
    sds = setNames(as.list(scaling$sd), scaling$feature)
)
write_json(scaling_list, "../config/scaling.json", pretty = TRUE)
```

---

## Phase 2: Scoring Function

**Dependency:** Phase 1 complete with acceptable metrics

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 2.1 | Create feature calculator | `scoring/features.py` | 3 hr |
| 2.2 | Load LASSO coefficients + scaling | Config loader | 30 min |
| 2.3 | Build single-pair scorer | Function | 1 hr |
| 2.4 | Build batch scorer (nonprofit → all foundations) | Function | 2 hr |
| 2.5 | Add known funder exclusion | Filter function | 30 min |
| 2.6 | Add ranking + top-K selection | Function | 30 min |
| 2.7 | Unit tests | `tests/test_scoring.py` | 1.5 hr |
| 2.8 | Test on beta clients | Validation report | 2 hr |

### Scoring Function Spec

```python
# scoring/scoring.py
import pandas as pd
import numpy as np
from typing import Optional
import json

from config.database import query_df
from scoring.features import calculate_features

class GrantScorer:
    def __init__(self, coefficients_path: str, scaling_path: str):
        with open(coefficients_path) as f:
            self.coefficients = json.load(f)
        with open(scaling_path) as f:
            scaling = json.load(f)
            self.means = scaling['means']
            self.sds = scaling['sds']
        
        self.intercept = self.coefficients.pop('(Intercept)', 0)
        self.feature_names = list(self.coefficients.keys())
    
    def score_pair(self, nonprofit_ein: str, foundation_ein: str) -> float:
        """Score a single nonprofit-foundation pair."""
        features = calculate_features(nonprofit_ein, foundation_ein)
        return self._apply_model(features)
    
    def score_nonprofit(
        self,
        nonprofit_ein: str,
        top_k: int = 50,
        exclude_known_funders: bool = True
    ) -> pd.DataFrame:
        """
        Score all foundations for a nonprofit, return top K.
        
        Output columns:
        - foundation_ein
        - foundation_name
        - match_score (0-100 scale)
        - match_rank (1 to K)
        - raw_score (log-odds)
        - probability (0-1)
        """
        # Get all foundations
        foundations = query_df("""
            SELECT ein, name, state, assets, total_giving
            FROM f990_2025.calc_foundation_features
            WHERE total_giving > 0
        """)
        
        # Exclude known funders if requested
        if exclude_known_funders:
            known = self._get_known_funders(nonprofit_ein)
            foundations = foundations[~foundations['ein'].isin(known)]
        
        # Calculate features for all pairs (vectorized)
        features_df = self._calculate_batch_features(nonprofit_ein, foundations)
        
        # Apply model
        features_df['raw_score'] = self._apply_model_batch(features_df)
        features_df['probability'] = 1 / (1 + np.exp(-features_df['raw_score']))
        features_df['match_score'] = (features_df['probability'] * 100).round(1)
        
        # Rank and select top K
        features_df = features_df.sort_values('match_score', ascending=False)
        features_df['match_rank'] = range(1, len(features_df) + 1)
        
        result = features_df.head(top_k)[[
            'ein', 'name', 'match_score', 'match_rank', 'raw_score', 'probability'
        ]].rename(columns={'ein': 'foundation_ein', 'name': 'foundation_name'})
        
        return result
    
    def _apply_model(self, features: dict) -> float:
        """Apply LASSO model to feature dict."""
        score = self.intercept
        for feat, coef in self.coefficients.items():
            if feat in features and features[feat] is not None:
                # Scale feature
                scaled = (features[feat] - self.means[feat]) / self.sds[feat]
                score += coef * scaled
        return score
    
    def _apply_model_batch(self, df: pd.DataFrame) -> np.ndarray:
        """Apply model to DataFrame of features."""
        scores = np.full(len(df), self.intercept)
        for feat, coef in self.coefficients.items():
            if feat in df.columns:
                scaled = (df[feat] - self.means[feat]) / self.sds[feat]
                scaled = scaled.fillna(0)  # Handle missing
                scores += coef * scaled.values
        return scores
    
    def _get_known_funders(self, nonprofit_ein: str) -> list:
        """Get foundations that have previously funded this nonprofit."""
        result = query_df("""
            SELECT DISTINCT foundation_ein
            FROM f990_2025.fact_grants
            WHERE recipient_ein = %(ein)s
        """, {'ein': nonprofit_ein})
        return result['foundation_ein'].tolist()
    
    def _calculate_batch_features(
        self, 
        nonprofit_ein: str, 
        foundations: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate features for nonprofit vs all foundations."""
        # Get nonprofit features once
        nonprofit = query_df("""
            SELECT * FROM f990_2025.calc_recipient_features
            WHERE ein = %(ein)s
        """, {'ein': nonprofit_ein})
        
        if len(nonprofit) == 0:
            raise ValueError(f"Nonprofit {nonprofit_ein} not found in features table")
        
        nonprofit = nonprofit.iloc[0]
        
        # Join with foundation features and calculate match features
        # ... (vectorized feature calculation)
        
        return foundations  # With features added
```

### Feature Calculator

```python
# scoring/features.py
from config.database import query_df

def calculate_features(nonprofit_ein: str, foundation_ein: str) -> dict:
    """
    Calculate all 33 features for a nonprofit-foundation pair.
    
    Returns dict with:
    - Foundation features (f_*)
    - Recipient features (r_*)
    - Match features (match_*)
    """
    # Get foundation features
    foundation = query_df("""
        SELECT * FROM f990_2025.calc_foundation_features
        WHERE ein = %(ein)s
    """, {'ein': foundation_ein})
    
    if len(foundation) == 0:
        raise ValueError(f"Foundation {foundation_ein} not found")
    foundation = foundation.iloc[0]
    
    # Get recipient features
    recipient = query_df("""
        SELECT * FROM f990_2025.calc_recipient_features
        WHERE ein = %(ein)s
    """, {'ein': nonprofit_ein})
    
    if len(recipient) == 0:
        raise ValueError(f"Nonprofit {nonprofit_ein} not found")
    recipient = recipient.iloc[0]
    
    # Build feature dict
    features = {}
    
    # Foundation features
    features['f_assets'] = foundation['assets']
    features['f_total_giving'] = foundation['total_giving']
    features['f_total_grants'] = foundation['total_grants_all_time']
    features['f_avg_grant'] = foundation['avg_grant_amount']
    features['f_median_grant'] = foundation['median_grant']
    features['f_repeat_rate'] = foundation['repeat_rate']
    features['f_in_state_pct'] = foundation['in_state_grant_pct']
    features['f_states_funded'] = foundation['states_funded']
    features['f_sectors_funded'] = foundation['sectors_funded']
    features['f_openness_score'] = foundation['openness_score']
    features['f_accepts_applications'] = float(foundation['accepts_applications'] or 0)
    features['f_payout_rate'] = foundation['payout_rate']
    features['f_officer_count'] = foundation['officer_count']
    features['f_has_paid_staff'] = float(foundation['has_paid_staff'] or 0)
    features['f_years_active'] = foundation['years_active']
    features['f_foundation_age'] = foundation['foundation_age']
    features['f_grant_cv'] = foundation['grant_amount_cv']
    features['f_sector_concentration'] = foundation['primary_sector_pct']
    
    # Recipient features
    features['r_total_grants'] = recipient['total_grants']
    features['r_total_funding'] = recipient['total_funding_received']
    features['r_total_funders'] = recipient['total_funders']
    features['r_avg_grant'] = recipient['avg_grant_received']
    features['r_revenue'] = recipient['total_revenue']
    features['r_assets'] = recipient['assets']
    features['r_employees'] = recipient['employee_count']
    features['r_mission_length'] = recipient['mission_length']
    features['r_funding_trend'] = recipient['funding_trend']
    features['r_funder_states'] = recipient['funder_states']
    features['r_has_embedding'] = float(recipient['has_mission_embedding'] or 0)
    
    # Match features
    features['match_same_state'] = 1 if foundation['state'] == recipient['state'] else 0
    features['match_same_sector'] = 1 if foundation['primary_sector'] == recipient['ntee_broad'] else 0
    
    # Log asset difference
    import math
    f_log_assets = math.log(foundation['assets']) if foundation['assets'] and foundation['assets'] > 0 else 0
    r_log_assets = math.log(recipient['assets']) if recipient['assets'] and recipient['assets'] > 0 else 0
    features['match_log_asset_diff'] = abs(f_log_assets - r_log_assets)
    
    # Grant size difference (normalized)
    if foundation['avg_grant_amount'] and recipient['avg_grant_received']:
        max_grant = max(foundation['avg_grant_amount'], recipient['avg_grant_received'])
        if max_grant > 0:
            features['match_grant_size_diff'] = abs(
                foundation['avg_grant_amount'] - recipient['avg_grant_received']
            ) / max_grant
        else:
            features['match_grant_size_diff'] = None
    else:
        features['match_grant_size_diff'] = None
    
    return features
```

### Test Cases

| Client | EIN | Notes |
|--------|-----|-------|
| VetsBoats Foundation | TBD | New paying client |
| Patient Safety Movement Foundation | 273236098 | Beta client with feedback |
| Senior Network Services | TBD | Beta client |
| Retirement Housing Foundation | TBD | Beta client |

---

## Phase 3: DB Enrichment Queries

**Dependency:** None (can run in parallel with Phase 2)

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 3.1 | SQL for Annual Giving metric | Query template | 30 min |
| 3.2 | SQL for Typical Grant (median, min, max) | Query template | 30 min |
| 3.3 | SQL for Geographic Focus | Query template | 30 min |
| 3.4 | SQL for Repeat Funding Rate | Query template | 45 min |
| 3.5 | SQL for Giving Style (general vs program) | Query template | 1 hr |
| 3.6 | SQL for Recipient Profile | Query template | 1 hr |
| 3.7 | SQL for Funding Trend (3-year) | Query template | 45 min |
| 3.8 | SQL for Comparable Grant finder | Query template | 1.5 hr |
| 3.9 | SQL for Potential Connections (board overlap) | Query template | 2 hr |
| 3.10 | Implement caching layer | `enrichment/cache.py` | 1.5 hr |
| 3.11 | Combine into single function | `get_funder_snapshot(ein)` | 1 hr |
| 3.12 | Unit tests | `tests/test_enrichment.py` | 1 hr |
| 3.13 | Test on 10 foundations | Validation | 1 hr |

### Caching Layer

```python
# enrichment/cache.py
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import os

CACHE_DIR = Path("outputs/cache")
CACHE_TTL_DAYS = int(os.getenv('CACHE_TTL_DAYS', 7))

def get_cache_path(key: str) -> Path:
    """Generate cache file path from key."""
    hash_key = hashlib.md5(key.encode()).hexdigest()[:12]
    return CACHE_DIR / f"{hash_key}.json"

def get_cached(key: str) -> Optional[dict]:
    """Get cached value if exists and not expired."""
    cache_path = get_cache_path(key)
    
    if not cache_path.exists():
        return None
    
    with open(cache_path) as f:
        cached = json.load(f)
    
    # Check expiry
    cached_at = datetime.fromisoformat(cached['cached_at'])
    if datetime.now() - cached_at > timedelta(days=CACHE_TTL_DAYS):
        cache_path.unlink()  # Delete expired
        return None
    
    return cached['data']

def set_cached(key: str, data: dict) -> None:
    """Cache a value."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    cache_path = get_cache_path(key)
    with open(cache_path, 'w') as f:
        json.dump({
            'key': key,
            'cached_at': datetime.now().isoformat(),
            'data': data
        }, f)

def cached(func):
    """Decorator for caching function results."""
    def wrapper(*args, **kwargs):
        # Build cache key from function name and args
        key = f"{func.__name__}:{':'.join(str(a) for a in args)}"
        
        cached_result = get_cached(key)
        if cached_result is not None:
            return cached_result
        
        result = func(*args, **kwargs)
        set_cached(key, result)
        return result
    
    return wrapper
```

### Funder Snapshot Function

```python
# enrichment/funder_snapshot.py
from enrichment.cache import cached
from enrichment.db_queries import (
    get_annual_giving,
    get_typical_grant,
    get_geographic_focus,
    get_repeat_rate,
    get_giving_style,
    get_recipient_profile,
    get_funding_trend,
    get_comparable_grant,
    get_potential_connections
)

@cached
def get_funder_snapshot(foundation_ein: str, client_ein: str = None) -> dict:
    """
    Build comprehensive funder snapshot for a foundation.
    
    Cached for 7 days by default.
    
    Args:
        foundation_ein: Foundation EIN
        client_ein: Optional client EIN for finding comparable grants
    
    Returns:
        Complete funder snapshot dict
    """
    snapshot = {
        "foundation_ein": foundation_ein,
        "foundation_name": None,  # Filled by first query
        "annual_giving": get_annual_giving(foundation_ein),
        "typical_grant": get_typical_grant(foundation_ein),
        "geographic_focus": get_geographic_focus(foundation_ein),
        "repeat_funding_rate": get_repeat_rate(foundation_ein),
        "giving_style": get_giving_style(foundation_ein),
        "recipient_profile": get_recipient_profile(foundation_ein),
        "funding_trend": get_funding_trend(foundation_ein),
        "comparable_grant": get_comparable_grant(foundation_ein, client_ein) if client_ein else None,
        "potential_connections": get_potential_connections(foundation_ein, client_ein) if client_ein else []
    }
    
    return snapshot
```

### Funder Snapshot Output Schema

```python
{
    "foundation_ein": "123456789",
    "foundation_name": "Example Foundation",
    "annual_giving": {
        "total": 2500000,
        "grant_count": 45,
        "year": 2023
    },
    "typical_grant": {
        "median": 45000,
        "min": 5000,
        "max": 150000,
        "p25": 20000,
        "p75": 75000
    },
    "geographic_focus": {
        "top_state": "CA",
        "top_state_pct": 0.78,
        "in_state_pct": 0.82,
        "states_funded": ["CA", "OR", "WA", "AZ"]
    },
    "repeat_funding_rate": 0.34,
    "giving_style": {
        "general_support_pct": 0.62,
        "program_specific_pct": 0.38,
        "keywords_found": ["general", "operating", "program"]
    },
    "recipient_profile": {
        "typical_budget_min": 500000,
        "typical_budget_max": 5000000,
        "median_budget": 1200000,
        "primary_sectors": ["Human Services", "Education"],
        "org_types": ["501c3"]
    },
    "funding_trend": {
        "direction": "Growing",  # Growing, Stable, Declining
        "three_year_change_pct": 0.15,
        "years": [2021, 2022, 2023],
        "amounts": [2100000, 2300000, 2500000]
    },
    "comparable_grant": {
        "recipient_name": "Similar Org",
        "recipient_ein": "987654321",
        "amount": 50000,
        "purpose": "General operating support",
        "year": 2023,
        "similarity_reason": "Same state, similar budget, human services"
    },
    "potential_connections": [
        {
            "type": "board_overlap",
            "name": "John Smith",
            "foundation_role": "Trustee",
            "client_connection": "Board member at partner org"
        }
    ]
}
```

### Giving Style Classification

```python
# enrichment/db_queries.py (partial)

GENERAL_SUPPORT_KEYWORDS = [
    'general', 'operating', 'unrestricted', 'charitable', 'support',
    'annual', 'core', 'operations', 'general purpose'
]

PROGRAM_SPECIFIC_KEYWORDS = [
    'program', 'project', 'initiative', 'capital', 'building',
    'equipment', 'specific', 'restricted', 'endowment'
]

def get_giving_style(foundation_ein: str) -> dict:
    """Analyze foundation's giving style from grant purposes."""
    grants = query_df("""
        SELECT purpose, amount
        FROM f990_2025.fact_grants
        WHERE foundation_ein = %(ein)s
          AND purpose IS NOT NULL
          AND purpose != ''
        ORDER BY tax_year DESC
        LIMIT 200
    """, {'ein': foundation_ein})
    
    if len(grants) == 0:
        return {"general_support_pct": None, "program_specific_pct": None}
    
    general_count = 0
    program_count = 0
    
    for purpose in grants['purpose'].str.lower():
        if any(kw in purpose for kw in GENERAL_SUPPORT_KEYWORDS):
            general_count += 1
        if any(kw in purpose for kw in PROGRAM_SPECIFIC_KEYWORDS):
            program_count += 1
    
    total = general_count + program_count
    if total == 0:
        return {"general_support_pct": None, "program_specific_pct": None}
    
    return {
        "general_support_pct": round(general_count / total, 2),
        "program_specific_pct": round(program_count / total, 2),
        "sample_size": len(grants)
    }
```

---

## Phase 4: Report Data Assembly

**Dependency:** Phase 2 + Phase 3 complete

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 4.1 | Define report_data schema | `schemas/report_schema.json` | 1 hr |
| 4.2 | Build assembly function | `assemble_report_data()` | 3 hr |
| 4.3 | Client data loader integration | Function | 1 hr |
| 4.4 | Identify fields requiring scrape | Gap list | 30 min |
| 4.5 | Identify fields requiring AI | AI field list | 30 min |
| 4.6 | Define graceful degradation rules | Error handling spec | 1 hr |
| 4.7 | Unit tests | `tests/test_assembly.py` | 1 hr |
| 4.8 | Test assembly on one client | Sample output | 1 hr |

### Report Data Schema

```python
report_data = {
    "client": {
        "name": str,
        "ein": str,
        "mission": str,  # from questionnaire
        "budget": int,
        "location": {
            "state": str,
            "city": str
        },
        "programs": list[str],
        "target_populations": list[str],
        "prior_funders": list[str],
        "ntee_code": str
    },
    "report_meta": {
        "report_id": str,  # UUID
        "week_number": int,
        "report_date": str,
        "generated_at": str,  # ISO timestamp
        "urgent_count": int,
        "total_potential_funding": str,
        "generation_errors": list[str]  # Track any issues
    },
    "opportunities": [
        {
            "rank": 1,
            "foundation_ein": str,
            "foundation_name": str,
            "match_score": float,
            "match_rank": int,
            
            # From DB (Funder Snapshot) - Phase 3
            "funder_snapshot": {...},
            
            # Needs scrape (or DB if available) - Phase 5
            "deadline": str,  # May be None
            "deadline_verified": bool,
            "portal_url": str,
            "contact_name": str,
            "contact_email": str,
            "contact_phone": str,
            "application_requirements": list[str],
            "scrape_status": str,  # "success", "partial", "failed", "skipped"
            
            # Needs AI generation - Phase 6
            "why_this_fits": str,
            "positioning_strategy": str,
            "next_steps": list[dict],
            "ai_status": str,  # "success", "failed", "fallback"
            
            # Calculated
            "status": str,  # URGENT/HIGH/MEDIUM
            "effort": str,  # Low/Med/High
            "fit_score": int,  # 1-10
            
            # Error tracking
            "errors": list[str]
        }
        # ... 4 more opportunities
    ],
    "executive_summary": {
        "one_thing": str,  # AI generated
        "key_strengths": list[str],
        "funding_scenarios": {
            "conservative": {"amount": int, "foundations": list},
            "moderate": {"amount": int, "foundations": list},
            "aggressive": {"amount": int, "foundations": list}
        }
    },
    "timeline": [
        {
            "week": 1,
            "date_range": str,
            "tasks": list[str],
            "focus_foundation": str
        }
        # ... 7 more weeks
    ]
}
```

### Field Source Map

| Field | Source | Phase | Required | Fallback |
|-------|--------|-------|----------|----------|
| foundation_name | DB | 3 | Yes | None |
| funder_snapshot.* | DB | 3 | Yes | Partial OK |
| comparable_grant | DB | 3 | No | "No comparable grant found" |
| potential_connections | DB | 3 | No | Empty list |
| deadline | Scrape | 5 | No | "Contact foundation" |
| portal_url | DB or Scrape | 5 | No | Foundation website |
| contact_* | DB or Scrape | 5 | No | "See foundation website" |
| application_requirements | Scrape | 5 | No | Generic list |
| why_this_fits | AI | 6 | Yes | Template fallback |
| positioning_strategy | AI | 6 | Yes | Template fallback |
| next_steps | AI | 6 | Yes | Generic steps |
| executive_summary | AI | 6 | Yes | Template fallback |

### Graceful Degradation Rules

```python
# report_data.py

FALLBACK_VALUES = {
    "deadline": "Contact foundation directly for current deadlines",
    "portal_url": None,  # Will use foundation website
    "contact_name": "Grants Administrator",
    "contact_email": None,
    "contact_phone": None,
    "application_requirements": [
        "Letter of inquiry or full proposal",
        "Organization budget",
        "Project budget (if applicable)",
        "501(c)(3) determination letter",
        "Board list"
    ],
    "why_this_fits": "This foundation's giving history suggests alignment with your mission. Review their recent grants for specific positioning guidance.",
    "positioning_strategy": "Focus on demonstrating clear outcomes and alignment with the foundation's stated priorities.",
    "next_steps": [
        {"action": "Research foundation website", "timeline": "Week 1"},
        {"action": "Identify any personal connections", "timeline": "Week 1"},
        {"action": "Prepare letter of inquiry", "timeline": "Week 2"},
        {"action": "Submit and follow up", "timeline": "Week 3"}
    ]
}

def apply_fallbacks(opportunity: dict) -> dict:
    """Apply fallback values for any missing fields."""
    for field, fallback in FALLBACK_VALUES.items():
        if opportunity.get(field) is None:
            opportunity[field] = fallback
            opportunity.setdefault('errors', []).append(f"Used fallback for {field}")
    return opportunity
```

---

## Phase 5: Just-in-Time Scraper

**Dependency:** Phase 4 complete (knows which foundations need scraping)

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 5.1 | Research foundation website patterns | Pattern doc | 2 hr |
| 5.2 | Build base scraper class | `scraper/scraper.py` | 3 hr |
| 5.3 | Deadline extractor | `scraper/extractors.py` | 2 hr |
| 5.4 | Contact info extractor | `scraper/extractors.py` | 2 hr |
| 5.5 | Application requirements extractor | `scraper/extractors.py` | 2 hr |
| 5.6 | Add rate limiting + retries | Robust scraper | 1 hr |
| 5.7 | Add proxy rotation (optional) | Anti-blocking | 2 hr |
| 5.8 | Manual entry fallback UI | `scraper/fallback.py` | 2 hr |
| 5.9 | Unit tests | `tests/test_scraper.py` | 1.5 hr |
| 5.10 | Test on 20 foundation websites | Validation report | 3 hr |

### Scraper Architecture

```python
# scraper/scraper.py
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import time
import random
from dataclasses import dataclass

@dataclass
class ScrapeResult:
    success: bool
    data: Dict
    errors: list
    source_url: str

class FoundationScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GrantResearchBot/1.0)'
        })
        self.rate_limit_seconds = 2
        self.max_retries = 3
    
    def scrape_foundation(self, ein: str, website_url: str = None) -> ScrapeResult:
        """
        Scrape foundation website for grant information.
        
        Returns structured data about deadlines, contacts, requirements.
        """
        errors = []
        data = {}
        
        # Get website URL from DB if not provided
        if not website_url:
            website_url = self._get_website_from_db(ein)
        
        if not website_url:
            return ScrapeResult(
                success=False,
                data={},
                errors=["No website URL found"],
                source_url=None
            )
        
        # Rate limiting
        time.sleep(self.rate_limit_seconds + random.random())
        
        try:
            # Fetch main page
            response = self._fetch_with_retry(website_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data
            data['deadline'] = self._extract_deadline(soup)
            data['contact_info'] = self._extract_contacts(soup)
            data['requirements'] = self._extract_requirements(soup)
            data['portal_url'] = self._find_application_portal(soup, website_url)
            
            # Try to find grants/apply page
            grants_url = self._find_grants_page(soup, website_url)
            if grants_url and grants_url != website_url:
                grants_response = self._fetch_with_retry(grants_url)
                grants_soup = BeautifulSoup(grants_response.text, 'html.parser')
                
                # Re-extract from grants page (may have better info)
                if not data['deadline']:
                    data['deadline'] = self._extract_deadline(grants_soup)
                if not data['requirements']:
                    data['requirements'] = self._extract_requirements(grants_soup)
            
            success = any(v for v in data.values() if v)
            
        except Exception as e:
            errors.append(str(e))
            success = False
        
        return ScrapeResult(
            success=success,
            data=data,
            errors=errors,
            source_url=website_url
        )
    
    def _fetch_with_retry(self, url: str) -> requests.Response:
        """Fetch URL with retries."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _extract_deadline(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract application deadline from page."""
        # Look for common deadline patterns
        deadline_keywords = ['deadline', 'due date', 'submit by', 'applications due']
        
        for keyword in deadline_keywords:
            # Search in text
            elements = soup.find_all(string=lambda t: t and keyword.lower() in t.lower())
            for el in elements:
                # Try to find a date nearby
                date = self._extract_date_near_element(el)
                if date:
                    return date
        
        return None
    
    def _extract_contacts(self, soup: BeautifulSoup) -> Dict:
        """Extract contact information."""
        contacts = {}
        
        # Email patterns
        import re
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', soup.get_text())
        if emails:
            contacts['email'] = emails[0]
        
        # Phone patterns
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', soup.get_text())
        if phones:
            contacts['phone'] = phones[0]
        
        # Look for contact name near email
        # ... (implementation)
        
        return contacts
    
    def _extract_requirements(self, soup: BeautifulSoup) -> list:
        """Extract application requirements."""
        requirements = []
        
        # Look for lists near "requirements", "submit", "application"
        keywords = ['requirement', 'submit', 'include', 'attach', 'provide']
        
        for keyword in keywords:
            elements = soup.find_all(['ul', 'ol'], string=lambda t: t and keyword.lower() in t.lower())
            for el in elements:
                items = el.find_all('li')
                requirements.extend([item.get_text().strip() for item in items])
        
        return list(set(requirements))[:10]  # Dedupe and limit
```

### Manual Entry Fallback

```python
# scraper/fallback.py
import json
from pathlib import Path

MANUAL_DATA_PATH = Path("data/manual_foundation_data.json")

def get_manual_data(ein: str) -> dict:
    """Get manually entered data for a foundation."""
    if not MANUAL_DATA_PATH.exists():
        return {}
    
    with open(MANUAL_DATA_PATH) as f:
        all_data = json.load(f)
    
    return all_data.get(ein, {})

def save_manual_data(ein: str, data: dict) -> None:
    """Save manually entered data."""
    if MANUAL_DATA_PATH.exists():
        with open(MANUAL_DATA_PATH) as f:
            all_data = json.load(f)
    else:
        all_data = {}
    
    all_data[ein] = data
    
    with open(MANUAL_DATA_PATH, 'w') as f:
        json.dump(all_data, f, indent=2)

def prompt_manual_entry(ein: str, foundation_name: str) -> dict:
    """
    CLI prompt for manual data entry.
    Used when scraping fails and data is needed.
    """
    print(f"\n=== Manual Entry Required ===")
    print(f"Foundation: {foundation_name} ({ein})")
    print(f"Please enter the following (press Enter to skip):\n")
    
    data = {}
    
    data['deadline'] = input("Application deadline: ").strip() or None
    data['portal_url'] = input("Application portal URL: ").strip() or None
    data['contact_name'] = input("Contact name: ").strip() or None
    data['contact_email'] = input("Contact email: ").strip() or None
    data['contact_phone'] = input("Contact phone: ").strip() or None
    
    req_input = input("Requirements (comma-separated): ").strip()
    data['requirements'] = [r.strip() for r in req_input.split(',')] if req_input else None
    
    if any(data.values()):
        save_manual_data(ein, data)
        print("Data saved.")
    
    return data
```

### Required vs Nice-to-Have Fields

| Field | Priority | If Missing |
|-------|----------|------------|
| deadline | Nice-to-have | Use fallback text |
| portal_url | Nice-to-have | Link to main website |
| contact_email | Nice-to-have | Use fallback text |
| contact_phone | Nice-to-have | Omit |
| requirements | Nice-to-have | Use generic list |

**Decision:** Scraping failures should NOT block report generation. Always use fallbacks.

---

## Phase 6: AI Narrative Generation

**Dependency:** Phase 4 + Phase 5 complete (all data assembled)

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 6.1 | Design prompt template structure | Template spec | 1 hr |
| 6.2 | Write "Why This Fits" prompt | `prompts/why_this_fits.txt` | 2 hr |
| 6.3 | Write "Positioning Strategy" prompt | `prompts/positioning.txt` | 2 hr |
| 6.4 | Write "Next Steps" prompt | `prompts/next_steps.txt` | 1.5 hr |
| 6.5 | Write "Executive Summary" prompt | `prompts/executive_summary.txt` | 2 hr |
| 6.6 | Write "One Thing" prompt | `prompts/one_thing.txt` | 1 hr |
| 6.7 | Build AI generation module | `ai/narratives.py` | 2 hr |
| 6.8 | Add fallback templates | `ai/fallbacks.py` | 1 hr |
| 6.9 | Add output validation | Ensure quality | 1 hr |
| 6.10 | Unit tests | `tests/test_ai.py` | 1 hr |
| 6.11 | Test on 5 foundations | Quality review | 2 hr |
| 6.12 | Iterate on prompts based on output | Refinement | 2 hr |

### Prompt Template: "Why This Fits"

```
You are writing the "Why This Fits" section for a grant opportunity report.

CLIENT PROFILE:
- Organization: {client_name}
- Mission: {client_mission}
- Location: {client_city}, {client_state}
- Annual Budget: {client_budget}
- Primary Programs: {client_programs}
- Populations Served: {client_populations}

FOUNDATION PROFILE:
- Name: {foundation_name}
- Annual Giving: ${annual_giving_total:,} across {grant_count} grants
- Typical Grant: ${typical_grant_median:,} (range: ${typical_grant_min:,} - ${typical_grant_max:,})
- Geographic Focus: {top_state} ({top_state_pct}% of grants), {in_state_pct}% in-state
- Primary Sectors: {primary_sectors}
- Giving Style: {general_support_pct}% general support / {program_specific_pct}% program-specific
- Repeat Funding Rate: {repeat_rate}%

COMPARABLE GRANT (if any):
{comparable_grant_details}

MATCH SCORE: {match_score}/100

Write 3-4 sentences explaining why this foundation is a good match for this client.

REQUIREMENTS:
1. Reference at least 2 specific data points from the foundation profile
2. Explain the alignment (geographic, programmatic, or budget)
3. If there's a comparable grant, mention it as precedent
4. Be specific and actionable, not generic
5. Do NOT start with "This foundation" - vary your opening

EXAMPLE OUTPUT:
"With 78% of grants staying in California and a focus on human services organizations, the Smith Foundation's giving pattern aligns well with your Bay Area-based work. Their median grant of $45,000 fits your target range, and their 2023 grant to Oakland Family Services for general operating support demonstrates willingness to fund organizations similar to yours. The foundation's 34% repeat funding rate suggests they value building long-term partnerships."
```

### Prompt Template: "Positioning Strategy"

```
You are writing the "Positioning Strategy" section for a grant opportunity report.

FUNDER SNAPSHOT:
- Foundation: {foundation_name}
- Annual Giving: ${annual_giving_total:,} ({grant_count} grants)
- Typical Grant: ${typical_grant_median:,} (range: ${typical_grant_min:,} - ${typical_grant_max:,})
- Geographic Focus: {in_state_pct}% in-state giving
- Giving Style: {general_support_pct}% general support / {program_specific_pct}% program-specific
- Repeat Funding Rate: {repeat_rate}%
- Recipient Profile: Typical budget ${typical_budget_min:,} - ${typical_budget_max:,}
- Funding Trend: {funding_trend_direction} ({three_year_change_pct}% over 3 years)

CLIENT CONTEXT:
- Organization: {client_name}
- Location: {client_city}, {client_state}
- Budget: ${client_budget:,}
- Key Strengths: {client_strengths}

POTENTIAL CONNECTIONS:
{connections_details}

Write 3-4 sentences of actionable positioning advice.

REQUIREMENTS:
1. Recommend a specific ask amount based on typical grant data
2. Advise on framing (general support vs program-specific) based on giving style
3. Address geographic positioning if client is out-of-state
4. Mention any connections to leverage
5. Be concrete and tactical, not vague

EXAMPLE OUTPUT:
"Request $40,000-50,000 for general operating support, aligning with their median grant size and preference for unrestricted giving (62% of grants). Since you're based in Oregon and they primarily fund in California, emphasize any California impact or partnerships in your proposal. Their growing giving trend (+15% over 3 years) suggests capacity for new grantees. If possible, leverage the connection through your board member Jane Smith, who serves on their advisory council."
```

### AI Generation Module

```python
# ai/narratives.py
import anthropic
from typing import Optional
import json
from pathlib import Path

from ai.fallbacks import FALLBACK_NARRATIVES

PROMPTS_DIR = Path("ai/prompts")

class NarrativeGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> dict:
        """Load all prompt templates."""
        prompts = {}
        for prompt_file in PROMPTS_DIR.glob("*.txt"):
            with open(prompt_file) as f:
                prompts[prompt_file.stem] = f.read()
        return prompts
    
    def generate(
        self,
        prompt_name: str,
        data: dict,
        max_tokens: int = 500
    ) -> tuple[str, str]:
        """
        Generate narrative using specified prompt.
        
        Returns:
            (narrative_text, status)
            status is "success", "failed", or "fallback"
        """
        if prompt_name not in self.prompts:
            raise ValueError(f"Unknown prompt: {prompt_name}")
        
        try:
            prompt = self.prompts[prompt_name].format(**data)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text.strip()
            
            # Basic validation
            if len(text) < 50:
                return FALLBACK_NARRATIVES.get(prompt_name, ""), "fallback"
            
            return text, "success"
            
        except Exception as e:
            print(f"AI generation failed: {e}")
            return FALLBACK_NARRATIVES.get(prompt_name, ""), "fallback"
    
    def generate_why_this_fits(self, opportunity: dict, client: dict) -> str:
        """Generate Why This Fits narrative."""
        data = self._prepare_why_this_fits_data(opportunity, client)
        text, status = self.generate("why_this_fits", data)
        return text
    
    def generate_positioning(self, opportunity: dict, client: dict) -> str:
        """Generate Positioning Strategy narrative."""
        data = self._prepare_positioning_data(opportunity, client)
        text, status = self.generate("positioning", data)
        return text
    
    def generate_next_steps(self, opportunity: dict) -> list:
        """Generate Next Steps list."""
        data = self._prepare_next_steps_data(opportunity)
        text, status = self.generate("next_steps", data, max_tokens=300)
        
        # Parse into structured list
        steps = self._parse_next_steps(text)
        return steps
    
    def generate_executive_summary(self, report_data: dict) -> dict:
        """Generate full executive summary."""
        data = self._prepare_executive_summary_data(report_data)
        
        one_thing, _ = self.generate("one_thing", data, max_tokens=100)
        summary, _ = self.generate("executive_summary", data, max_tokens=400)
        
        return {
            "one_thing": one_thing,
            "narrative": summary
        }
    
    def _prepare_why_this_fits_data(self, opp: dict, client: dict) -> dict:
        """Prepare data dict for why_this_fits prompt."""
        snapshot = opp.get('funder_snapshot', {})
        comparable = snapshot.get('comparable_grant', {})
        
        return {
            "client_name": client.get('name'),
            "client_mission": client.get('mission'),
            "client_city": client.get('location', {}).get('city'),
            "client_state": client.get('location', {}).get('state'),
            "client_budget": client.get('budget'),
            "client_programs": ", ".join(client.get('programs', [])),
            "client_populations": ", ".join(client.get('target_populations', [])),
            "foundation_name": opp.get('foundation_name'),
            "annual_giving_total": snapshot.get('annual_giving', {}).get('total', 0),
            "grant_count": snapshot.get('annual_giving', {}).get('grant_count', 0),
            "typical_grant_median": snapshot.get('typical_grant', {}).get('median', 0),
            "typical_grant_min": snapshot.get('typical_grant', {}).get('min', 0),
            "typical_grant_max": snapshot.get('typical_grant', {}).get('max', 0),
            "top_state": snapshot.get('geographic_focus', {}).get('top_state'),
            "top_state_pct": int((snapshot.get('geographic_focus', {}).get('top_state_pct', 0)) * 100),
            "in_state_pct": int((snapshot.get('geographic_focus', {}).get('in_state_pct', 0)) * 100),
            "primary_sectors": ", ".join(snapshot.get('recipient_profile', {}).get('primary_sectors', [])),
            "general_support_pct": int((snapshot.get('giving_style', {}).get('general_support_pct', 0)) * 100),
            "program_specific_pct": int((snapshot.get('giving_style', {}).get('program_specific_pct', 0)) * 100),
            "repeat_rate": int((snapshot.get('repeat_funding_rate', 0)) * 100),
            "comparable_grant_details": self._format_comparable_grant(comparable),
            "match_score": opp.get('match_score', 0)
        }
```

### Fallback Templates

```python
# ai/fallbacks.py

FALLBACK_NARRATIVES = {
    "why_this_fits": (
        "This foundation's giving history and focus areas suggest potential alignment "
        "with your organization's mission. Review their recent grants on the 990-PF "
        "for specific examples of similar organizations they've funded, and use those "
        "as models for your approach."
    ),
    
    "positioning": (
        "Focus your proposal on demonstrating clear, measurable outcomes aligned with "
        "this foundation's stated priorities. Request an amount within their typical "
        "grant range and emphasize your organization's track record and sustainability."
    ),
    
    "next_steps": [
        {"action": "Research foundation website and recent grants", "timeline": "Week 1", "owner": "Development Director"},
        {"action": "Identify any board or staff connections", "timeline": "Week 1", "owner": "ED"},
        {"action": "Draft letter of inquiry", "timeline": "Week 2", "owner": "Grant Writer"},
        {"action": "Submit LOI and follow up", "timeline": "Week 3", "owner": "Development Director"}
    ],
    
    "one_thing": (
        "Focus your energy this week on the highest-ranked opportunity that accepts "
        "unsolicited proposals."
    ),
    
    "executive_summary": (
        "This week's opportunities represent a mix of foundation types and giving styles. "
        "Prioritize foundations with upcoming deadlines and those where you have potential "
        "connections. The recommended approach balances quick wins with longer-term "
        "relationship building."
    )
}
```

### Cost Estimate

| Item | Calculation | Cost |
|------|-------------|------|
| Per opportunity | 5 AI calls × ~500 tokens | ~$0.02 |
| Per report | 5 opportunities + executive summary | ~$0.12 |
| 50 clients/month | 50 × $0.12 | ~$6/month |

---

## Phase 7: MD Assembly

**Dependency:** Phase 6 complete (all narratives generated)

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 7.1 | Build MD template renderer | `rendering/md_renderer.py` | 2 hr |
| 7.2 | Implement Header section | Template section | 30 min |
| 7.3 | Implement Executive Summary section | Template section | 1 hr |
| 7.4 | Implement Top 5 Table section | Template section | 1 hr |
| 7.5 | Implement Opportunity sections (×5) | Template section | 2 hr |
| 7.6 | Implement 8-Week Timeline section | Template section | 1 hr |
| 7.7 | Implement Quick Reference section | Template section | 30 min |
| 7.8 | Build full report assembler | Function | 1 hr |
| 7.9 | Unit tests | `tests/test_rendering.py` | 1 hr |
| 7.10 | Test output formatting | Visual review | 1 hr |

### MD Renderer

```python
# rendering/md_renderer.py
from pathlib import Path
from datetime import datetime
from typing import List

TEMPLATE_DIR = Path("rendering/templates")

def render_report_md(report_data: dict) -> str:
    """
    Render complete markdown report from report_data.
    """
    sections = [
        render_header(report_data),
        render_one_thing(report_data),
        render_executive_summary(report_data),
        render_top_5_table(report_data),
    ]
    
    # Add each opportunity section
    for opp in report_data['opportunities']:
        sections.append(render_opportunity(opp, report_data['client']))
    
    sections.extend([
        render_timeline(report_data),
        render_quick_reference(report_data),
        render_footer(report_data)
    ])
    
    return "\n\n---\n\n".join(sections)

def render_header(data: dict) -> str:
    """Render report header."""
    client = data['client']
    meta = data['report_meta']
    
    return f"""# Grant Opportunities Report

**Prepared for:** {client['name']}  
**Report Date:** {meta['report_date']}  
**Week:** {meta['week_number']}

**Total Potential Funding:** {meta['total_potential_funding']}  
**Urgent Opportunities:** {meta['urgent_count']}
"""

def render_one_thing(data: dict) -> str:
    """Render 'One Thing' section."""
    one_thing = data['executive_summary'].get('one_thing', '')
    
    return f"""## 🎯 If You Do One Thing This Week...

{one_thing}
"""

def render_executive_summary(data: dict) -> str:
    """Render executive summary section."""
    summary = data['executive_summary']
    
    strengths = "\n".join(f"- {s}" for s in summary.get('key_strengths', []))
    
    scenarios = summary.get('funding_scenarios', {})
    
    return f"""## Executive Summary

{summary.get('narrative', '')}

### Your Strengths This Week

{strengths}

### Funding Scenarios

| Scenario | Potential Funding | Foundations |
|----------|-------------------|-------------|
| Conservative | ${scenarios.get('conservative', {}).get('amount', 0):,} | {', '.join(scenarios.get('conservative', {}).get('foundations', []))} |
| Moderate | ${scenarios.get('moderate', {}).get('amount', 0):,} | {', '.join(scenarios.get('moderate', {}).get('foundations', []))} |
| Aggressive | ${scenarios.get('aggressive', {}).get('amount', 0):,} | {', '.join(scenarios.get('aggressive', {}).get('foundations', []))} |
"""

def render_top_5_table(data: dict) -> str:
    """Render top 5 opportunities summary table."""
    rows = []
    for opp in data['opportunities']:
        snapshot = opp.get('funder_snapshot', {})
        typical = snapshot.get('typical_grant', {})
        
        rows.append(
            f"| {opp['rank']} | {opp['foundation_name']} | "
            f"${typical.get('median', 0):,} | {opp.get('status', 'MEDIUM')} | "
            f"{opp.get('deadline', 'Rolling')} |"
        )
    
    table = "\n".join(rows)
    
    return f"""## Top 5 Opportunities at a Glance

| Rank | Foundation | Typical Grant | Status | Deadline |
|------|------------|---------------|--------|----------|
{table}
"""

def render_opportunity(opp: dict, client: dict) -> str:
    """Render single opportunity section."""
    snapshot = opp.get('funder_snapshot', {})
    typical = snapshot.get('typical_grant', {})
    geo = snapshot.get('geographic_focus', {})
    giving = snapshot.get('giving_style', {})
    
    # Format next steps
    steps = opp.get('next_steps', [])
    steps_md = "\n".join(
        f"- [ ] **{s.get('action')}** - {s.get('timeline')}"
        for s in steps
    )
    
    return f"""## {opp['rank']}. {opp['foundation_name']}

**Match Score:** {opp['match_score']}/100 | **Status:** {opp.get('status', 'MEDIUM')} | **Effort:** {opp.get('effort', 'Medium')}

### Funder Snapshot

| Metric | Value |
|--------|-------|
| Annual Giving | ${snapshot.get('annual_giving', {}).get('total', 0):,} |
| Typical Grant | ${typical.get('median', 0):,} (${typical.get('min', 0):,} - ${typical.get('max', 0):,}) |
| Geographic Focus | {geo.get('top_state', 'N/A')} ({int(geo.get('top_state_pct', 0) * 100)}%) |
| Giving Style | {int(giving.get('general_support_pct', 0) * 100)}% general / {int(giving.get('program_specific_pct', 0) * 100)}% program |
| Repeat Funding | {int(snapshot.get('repeat_funding_rate', 0) * 100)}% |

### Why This Fits

{opp.get('why_this_fits', '')}

### Positioning Strategy

{opp.get('positioning_strategy', '')}

### Next Steps

{steps_md}

### Contact Information

- **Website:** {opp.get('portal_url') or 'See foundation website'}
- **Contact:** {opp.get('contact_name', 'Grants Administrator')}
- **Email:** {opp.get('contact_email', 'N/A')}
- **Deadline:** {opp.get('deadline', 'Contact foundation')}
"""

def render_timeline(data: dict) -> str:
    """Render 8-week timeline."""
    timeline = data.get('timeline', [])
    
    rows = []
    for week in timeline:
        tasks = ", ".join(week.get('tasks', []))
        rows.append(
            f"| Week {week['week']} | {week.get('date_range', '')} | "
            f"{week.get('focus_foundation', '')} | {tasks} |"
        )
    
    table = "\n".join(rows)
    
    return f"""## 8-Week Action Timeline

| Week | Dates | Focus | Key Tasks |
|------|-------|-------|-----------|
{table}
"""

def render_quick_reference(data: dict) -> str:
    """Render quick reference section."""
    opps = data['opportunities']
    
    contacts = "\n".join(
        f"- **{o['foundation_name']}:** {o.get('contact_email', 'N/A')}"
        for o in opps
    )
    
    return f"""## Quick Reference

### Contact List

{contacts}

### Deadline Summary

| Foundation | Deadline | Status |
|------------|----------|--------|
{chr(10).join(f"| {o['foundation_name']} | {o.get('deadline', 'Rolling')} | {o.get('status', 'MEDIUM')} |" for o in opps)}
"""

def render_footer(data: dict) -> str:
    """Render report footer."""
    meta = data['report_meta']
    
    return f"""---

*Report generated by The Grant Scout on {meta.get('generated_at', datetime.now().isoformat())}*

*Questions? Contact support@thegrantscout.com*
"""
```

---

## Phase 8: End-to-End Pipeline

**Dependency:** All previous phases complete

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 8.1 | Build master pipeline script | `generate_report.py` | 3 hr |
| 8.2 | Add comprehensive logging | Structured logs | 1 hr |
| 8.3 | Add error handling + recovery | Robust script | 2 hr |
| 8.4 | Integrate Word doc conversion | Full pipeline | 1 hr |
| 8.5 | Add progress reporting | CLI output | 30 min |
| 8.6 | Add dry-run mode | Testing support | 30 min |
| 8.7 | Test on VetsBoats (new client) | First production report | 2 hr |
| 8.8 | Test on 3 beta clients | Validation | 3 hr |
| 8.9 | Document usage | README.md | 1 hr |

### Master Pipeline

```python
#!/usr/bin/env python3
"""
generate_report.py - Main entry point for report generation

Usage:
    python generate_report.py --ein 123456789 --questionnaire ./intake/client.json
    python generate_report.py --ein 123456789 --dry-run
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path
import json
import sys

from config.database import init_pool
from loaders.questionnaire import load_questionnaire
from scoring.scoring import GrantScorer
from enrichment.funder_snapshot import get_funder_snapshot
from scraper.scraper import FoundationScraper
from scraper.fallback import get_manual_data
from ai.narratives import NarrativeGenerator
from rendering.md_renderer import render_report_md
from report_data import assemble_report_data, apply_fallbacks

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'outputs/logs/report_{datetime.now():%Y%m%d_%H%M%S}.log')
    ]
)
logger = logging.getLogger(__name__)

def generate_report(
    client_ein: str,
    questionnaire_data: dict = None,
    output_dir: str = "outputs/reports/",
    dry_run: bool = False
) -> str:
    """
    Full pipeline: EIN → Word doc
    
    Args:
        client_ein: Client organization EIN
        questionnaire_data: Pre-loaded questionnaire dict (optional)
        output_dir: Where to save outputs
        dry_run: If True, skip AI and scraping
    
    Returns:
        Path to generated Word doc (or MD if conversion fails)
    """
    start_time = datetime.now()
    errors = []
    
    logger.info(f"Starting report generation for {client_ein}")
    
    # Initialize
    init_pool()
    scorer = GrantScorer("config/coefficients.json", "config/scaling.json")
    scraper = FoundationScraper()
    ai = NarrativeGenerator()
    
    # Step 1: Load client data
    logger.info("Loading client data...")
    if questionnaire_data:
        client = questionnaire_data
    else:
        client = load_questionnaire(client_ein)
    
    if not client:
        raise ValueError(f"No questionnaire data found for {client_ein}")
    
    # Step 2: Score foundations
    logger.info("Scoring foundations...")
    matches = scorer.score_nonprofit(client_ein, top_k=50, exclude_known_funders=True)
    top_5 = matches.head(5)
    logger.info(f"Top match: {top_5.iloc[0]['foundation_name']} (score: {top_5.iloc[0]['match_score']})")
    
    # Step 3: Get funder snapshots
    logger.info("Building funder snapshots...")
    opportunities = []
    for _, row in top_5.iterrows():
        logger.info(f"  Processing {row['foundation_name']}...")
        
        opp = {
            "rank": row['match_rank'],
            "foundation_ein": row['foundation_ein'],
            "foundation_name": row['foundation_name'],
            "match_score": row['match_score'],
            "errors": []
        }
        
        try:
            opp["funder_snapshot"] = get_funder_snapshot(
                row['foundation_ein'], 
                client_ein
            )
        except Exception as e:
            logger.warning(f"  Funder snapshot failed: {e}")
            opp["funder_snapshot"] = {}
            opp["errors"].append(f"Funder snapshot: {e}")
        
        opportunities.append(opp)
    
    # Step 4: Scrape missing data (or use fallbacks)
    if not dry_run:
        logger.info("Scraping foundation websites...")
        for opp in opportunities:
            # Check manual data first
            manual = get_manual_data(opp['foundation_ein'])
            if manual:
                opp.update(manual)
                opp['scrape_status'] = 'manual'
                continue
            
            # Try scraping
            try:
                result = scraper.scrape_foundation(opp['foundation_ein'])
                if result.success:
                    opp.update(result.data)
                    opp['scrape_status'] = 'success'
                else:
                    opp['scrape_status'] = 'failed'
                    opp['errors'].extend(result.errors)
            except Exception as e:
                logger.warning(f"  Scrape failed for {opp['foundation_name']}: {e}")
                opp['scrape_status'] = 'failed'
                opp['errors'].append(f"Scrape: {e}")
    else:
        logger.info("Dry run - skipping scraping")
        for opp in opportunities:
            opp['scrape_status'] = 'skipped'
    
    # Step 5: Generate AI narratives (or use fallbacks)
    if not dry_run:
        logger.info("Generating AI narratives...")
        for opp in opportunities:
            try:
                opp['why_this_fits'] = ai.generate_why_this_fits(opp, client)
                opp['positioning_strategy'] = ai.generate_positioning(opp, client)
                opp['next_steps'] = ai.generate_next_steps(opp)
                opp['ai_status'] = 'success'
            except Exception as e:
                logger.warning(f"  AI generation failed for {opp['foundation_name']}: {e}")
                opp['ai_status'] = 'failed'
                opp['errors'].append(f"AI: {e}")
    else:
        logger.info("Dry run - skipping AI generation")
        for opp in opportunities:
            opp['ai_status'] = 'skipped'
    
    # Step 6: Apply fallbacks for any missing data
    logger.info("Applying fallbacks...")
    for opp in opportunities:
        apply_fallbacks(opp)
    
    # Step 7: Assemble report data
    logger.info("Assembling report data...")
    report_data = assemble_report_data(client, opportunities)
    
    # Generate executive summary
    if not dry_run:
        try:
            report_data['executive_summary'] = ai.generate_executive_summary(report_data)
        except Exception as e:
            logger.warning(f"Executive summary generation failed: {e}")
            errors.append(f"Executive summary: {e}")
    
    report_data['report_meta']['generation_errors'] = errors
    
    # Step 8: Render to markdown
    logger.info("Rendering markdown...")
    md_content = render_report_md(report_data)
    
    # Save markdown
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    md_path = output_path / f"{client_ein}_{date_str}_report.md"
    
    with open(md_path, 'w') as f:
        f.write(md_content)
    
    logger.info(f"Saved markdown: {md_path}")
    
    # Step 9: Convert to Word (if not dry run)
    if not dry_run:
        try:
            from docx_converter import convert_md_to_docx
            docx_path = convert_md_to_docx(md_path)
            logger.info(f"Saved Word doc: {docx_path}")
            final_path = docx_path
        except Exception as e:
            logger.warning(f"Word conversion failed: {e}")
            errors.append(f"Word conversion: {e}")
            final_path = md_path
    else:
        final_path = md_path
    
    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"Report generation complete in {elapsed:.1f}s")
    logger.info(f"Output: {final_path}")
    
    if errors:
        logger.warning(f"Completed with {len(errors)} errors")
    
    return str(final_path)


def main():
    parser = argparse.ArgumentParser(description="Generate grant opportunities report")
    parser.add_argument("--ein", required=True, help="Client organization EIN")
    parser.add_argument("--questionnaire", help="Path to questionnaire JSON file")
    parser.add_argument("--output", default="outputs/reports/", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Skip AI and scraping")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load questionnaire if provided
    questionnaire_data = None
    if args.questionnaire:
        with open(args.questionnaire) as f:
            questionnaire_data = json.load(f)
    
    try:
        output_path = generate_report(
            client_ein=args.ein,
            questionnaire_data=questionnaire_data,
            output_dir=args.output,
            dry_run=args.dry_run
        )
        print(f"\n✓ Report generated: {output_path}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        print(f"\n✗ Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### CLI Interface

```bash
# Basic usage
python generate_report.py --ein 123456789

# With questionnaire file
python generate_report.py --ein 123456789 --questionnaire ./intake/vetsboats.json

# Dry run (no AI, no scraping)
python generate_report.py --ein 123456789 --dry-run

# Verbose output
python generate_report.py --ein 123456789 -v
```

---

## Phase 9: Testing & Validation

**Dependency:** Phase 8 complete

### Tasks

| # | Task | Output | Est. Time |
|---|------|--------|-----------|
| 9.1 | Write unit tests for scoring | `tests/test_scoring.py` | 2 hr |
| 9.2 | Write unit tests for enrichment | `tests/test_enrichment.py` | 2 hr |
| 9.3 | Write integration tests | `tests/test_pipeline.py` | 3 hr |
| 9.4 | Create test fixtures | Sample data | 1 hr |
| 9.5 | Run full pipeline on 5 clients | Validation reports | 3 hr |
| 9.6 | Quality review of outputs | Checklist | 2 hr |
| 9.7 | Client feedback collection | Feedback doc | 2 hr |
| 9.8 | Iterate based on feedback | Bug fixes | 4 hr |

### Test Strategy

```python
# tests/test_scoring.py
import pytest
from scoring.scoring import GrantScorer
from scoring.features import calculate_features

class TestScoring:
    @pytest.fixture
    def scorer(self):
        return GrantScorer("config/coefficients.json", "config/scaling.json")
    
    def test_score_pair_returns_float(self, scorer):
        score = scorer.score_pair("123456789", "987654321")
        assert isinstance(score, float)
    
    def test_score_nonprofit_returns_dataframe(self, scorer):
        results = scorer.score_nonprofit("123456789", top_k=10)
        assert len(results) == 10
        assert "match_score" in results.columns
        assert "match_rank" in results.columns
    
    def test_scores_are_bounded(self, scorer):
        results = scorer.score_nonprofit("123456789", top_k=50)
        assert results["match_score"].min() >= 0
        assert results["match_score"].max() <= 100
    
    def test_exclude_known_funders(self, scorer):
        with_exclusion = scorer.score_nonprofit("123456789", exclude_known_funders=True)
        without_exclusion = scorer.score_nonprofit("123456789", exclude_known_funders=False)
        assert len(without_exclusion) >= len(with_exclusion)


# tests/test_pipeline.py
import pytest
from pathlib import Path
from generate_report import generate_report

class TestPipeline:
    def test_dry_run_generates_markdown(self, tmp_path):
        output = generate_report(
            client_ein="123456789",
            output_dir=str(tmp_path),
            dry_run=True
        )
        assert Path(output).exists()
        assert output.endswith(".md")
    
    def test_report_has_required_sections(self, tmp_path):
        output = generate_report(
            client_ein="123456789",
            output_dir=str(tmp_path),
            dry_run=True
        )
        content = Path(output).read_text()
        assert "# Grant Opportunities Report" in content
        assert "## Executive Summary" in content
        assert "## Top 5 Opportunities" in content
```

### Quality Checklist

| Check | Criteria |
|-------|----------|
| Scoring | Top 5 foundations are reasonable matches |
| Data | All funder snapshots have key metrics |
| AI | Narratives reference specific data points |
| AI | No generic/boilerplate text |
| Formatting | Markdown renders correctly |
| Formatting | Word doc looks professional |
| Accuracy | Grant amounts are realistic |
| Accuracy | Geographic info is correct |
| Completeness | All 5 opportunities have all sections |

---

## Timeline Summary

| Phase | Description | Est. Time | Dependencies |
|-------|-------------|-----------|--------------|
| 0 | Infrastructure Setup | 5 hr | None |
| 1 | Model Validation | 3 hr | None |
| 2 | Scoring Function | 11 hr | Phase 1 |
| 3 | DB Enrichment Queries | 13 hr | None (parallel) |
| 4 | Report Data Assembly | 9 hr | Phase 2, 3 |
| 5 | Just-in-Time Scraper | 18 hr | Phase 4 |
| 6 | AI Narrative Generation | 17 hr | Phase 4, 5 |
| 7 | MD Assembly | 9 hr | Phase 6 |
| 8 | End-to-End Pipeline | 14 hr | All |
| 9 | Testing & Validation | 19 hr | Phase 8 |

**Total estimated: ~118 hours of dev work**

### Parallel Tracks

```
Week 1:     [Phase 0: Setup] → [Phase 1: Model]
            [Phase 3: DB Queries --------------------]

Week 2:     [Phase 2: Scoring ----------------------]
            [Phase 3: continued --------------------]

Week 3:     [Phase 4: Assembly]
            [Phase 5: Scraper ----------------------]

Week 4:     [Phase 5: continued]
            [Phase 6: AI Prompts -------------------]

Week 5:     [Phase 7: MD Assembly]
            [Phase 8: Pipeline ---------------------]

Week 6:     [Phase 9: Testing & Validation ---------]
```

**Realistic timeline: 5-6 weeks** with focused effort.

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LASSO model underperforms | Medium | High | Fall back to heuristic scoring; iterate on features |
| Foundation websites block scraping | High | Medium | Use rotating proxies; manual entry fallback; cache aggressively |
| AI narratives low quality | Medium | Medium | Iterate on prompts; add example outputs; human review initially |
| Deadline verification fails | High | Low | Flag unverified deadlines; use "Contact foundation" fallback |
| Pipeline too slow | Medium | Medium | Cache funder snapshots; batch AI calls; pre-compute features |
| API rate limits | Low | Medium | Add retry logic; queue requests; monitor usage |

---

## Quality Gates

### After Phase 1
- [ ] AUC > 0.70
- [ ] Coefficients interpretable
- [ ] No single feature dominates

### After Phase 4
- [ ] Report data schema complete
- [ ] Sample data assembly works for 3 clients
- [ ] All required fields populated or have fallbacks

### After Phase 6
- [ ] AI narratives reviewed and approved
- [ ] Narratives reference specific data (not generic)
- [ ] Fallback templates acceptable quality

### After Phase 8
- [ ] Full report generated for 5 clients
- [ ] Report matches quality of manual Research Team output
- [ ] Generation time < 5 minutes per report
- [ ] Error rate < 10% of fields

### After Phase 9
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Client feedback positive (3/3 beta clients)

---

## Files to Create

| Phase | Files |
|-------|-------|
| 0 | `config/database.py`, `config/secrets.py`, `loaders/questionnaire.py`, `.env`, `requirements.txt` |
| 2 | `scoring/scoring.py`, `scoring/features.py`, `config/coefficients.json`, `config/scaling.json` |
| 3 | `enrichment/db_queries.py`, `enrichment/funder_snapshot.py`, `enrichment/cache.py` |
| 4 | `report_data.py`, `schemas/report_schema.json` |
| 5 | `scraper/scraper.py`, `scraper/extractors.py`, `scraper/fallback.py` |
| 6 | `ai/narratives.py`, `ai/fallbacks.py`, `ai/prompts/*.txt` |
| 7 | `rendering/md_renderer.py`, `rendering/templates/report_template.md` |
| 8 | `generate_report.py`, `README.md` |
| 9 | `tests/test_*.py`, `tests/fixtures/*` |

---

## Dependencies (requirements.txt)

```
# Database
psycopg2-binary>=2.9.0

# Data processing
pandas>=2.0.0
numpy>=1.24.0

# AI
anthropic>=0.18.0

# Scraping
requests>=2.31.0
beautifulsoup4>=4.12.0

# Document generation
python-docx>=0.8.11

# Utilities
python-dotenv>=1.0.0

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
```

---

*Next step: Complete Phase 1 (run LASSO v2), then begin Phase 0 (infrastructure) + Phase 3 (DB queries) in parallel.*
