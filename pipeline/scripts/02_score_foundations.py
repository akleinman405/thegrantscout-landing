#!/usr/bin/env python3
"""
02_score_foundations.py - Score all foundations against a client

Usage:
    python scripts/02_score_foundations.py --client "Patient Safety Movement Foundation"
    python scripts/02_score_foundations.py --client "PSMF" --top-k 100
    python scripts/02_score_foundations.py --client "PSMF" --min-assets 500000
"""
import argparse
import json
import logging
import math
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import pandas as pd

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils import query_df, get_run_dir, get_latest_run_dir, CONFIG_DIR, LOGS_DIR


# State codes used in model (must match coefficients)
STATE_CODES = ['NY', 'CA', 'TX', 'IL', 'FL', 'PA', 'MA', 'DE', 'NJ', 'MI']

# NTEE broad categories used in model
NTEE_CODES = ['', 'B', 'P', 'A', 'E', 'X', 'D', 'T', 'Q']

# Size buckets
SIZE_BUCKETS = ['TINY', 'SMALL', 'MEDIUM', 'LARGE', '']

# Cache for foundation distributions (loaded once per run)
_foundation_sector_dist_cache: Dict[str, Dict[str, float]] = {}
_foundation_state_dist_cache: Dict[str, Dict[str, float]] = {}
_foundation_hhi_cache: Dict[str, float] = {}


def load_foundation_distributions(logger: logging.Logger) -> None:
    """Load foundation sector and state distributions from staging tables."""
    global _foundation_sector_dist_cache, _foundation_state_dist_cache, _foundation_hhi_cache

    # Load sector distributions
    sector_query = """
    SELECT foundation_ein, ntee_broad, sector_pct
    FROM f990_2025.stg_foundation_sector_dist
    """
    sector_df = query_df(sector_query, {})

    for _, row in sector_df.iterrows():
        ein = row['foundation_ein']
        ntee = row['ntee_broad'] or ''
        pct = float(row['sector_pct'] or 0)

        if ein not in _foundation_sector_dist_cache:
            _foundation_sector_dist_cache[ein] = {}
        _foundation_sector_dist_cache[ein][ntee] = pct

    logger.info(f"Loaded sector distributions for {len(_foundation_sector_dist_cache)} foundations")

    # Load state distributions
    state_query = """
    SELECT foundation_ein, recipient_state, state_pct
    FROM f990_2025.stg_foundation_state_dist
    """
    state_df = query_df(state_query, {})

    for _, row in state_df.iterrows():
        ein = row['foundation_ein']
        state = row['recipient_state'] or ''
        pct = float(row['state_pct'] or 0)

        if ein not in _foundation_state_dist_cache:
            _foundation_state_dist_cache[ein] = {}
        _foundation_state_dist_cache[ein][state] = pct

    logger.info(f"Loaded state distributions for {len(_foundation_state_dist_cache)} foundations")

    # Load HHI values
    hhi_query = """
    SELECT foundation_ein, sector_hhi
    FROM f990_2025.stg_foundation_sector_hhi
    """
    hhi_df = query_df(hhi_query, {})

    for _, row in hhi_df.iterrows():
        ein = row['foundation_ein']
        hhi = float(row['sector_hhi'] or 0)
        _foundation_hhi_cache[ein] = hhi

    logger.info(f"Loaded HHI values for {len(_foundation_hhi_cache)} foundations")


def get_sector_match_pct(foundation_ein: str, recipient_ntee: str) -> float:
    """Get % of foundation's grants in recipient's sector."""
    if not recipient_ntee:
        return 0.5  # Default for unknown NTEE

    ntee_broad = recipient_ntee[:1] if recipient_ntee else ''

    if foundation_ein not in _foundation_sector_dist_cache:
        return 0.0

    return _foundation_sector_dist_cache[foundation_ein].get(ntee_broad, 0.0)


def get_state_match_pct(foundation_ein: str, recipient_state: str) -> float:
    """Get % of foundation's grants in recipient's state."""
    if not recipient_state:
        return 0.0

    if foundation_ein not in _foundation_state_dist_cache:
        return 0.0

    return _foundation_state_dist_cache[foundation_ein].get(recipient_state, 0.0)


def get_foundation_hhi(foundation_ein: str) -> float:
    """Get sector concentration HHI for foundation."""
    return _foundation_hhi_cache.get(foundation_ein, 0.05)  # Default median


def setup_logging(client_name: str) -> logging.Logger:
    """Set up logging for this run."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = client_name.replace(" ", "_")[:20]
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_{safe_name}.log"

    # Configure logging to append
    logger = logging.getLogger('02_score_foundations')
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers = []

    # File handler (append)
    fh = logging.FileHandler(log_file, mode='a')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

    return logger


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def find_client_run_dir(client_name: str, run_date: date = None) -> Optional[Path]:
    """Find the run directory for a client."""
    if run_date:
        run_dir = get_run_dir(client_name, run_date)
        if (run_dir / "01_client.json").exists():
            return run_dir
    else:
        # Try today first
        run_dir = get_run_dir(client_name, date.today())
        if (run_dir / "01_client.json").exists():
            return run_dir

        # Fall back to latest
        latest = get_latest_run_dir(client_name)
        if latest and (latest / "01_client.json").exists():
            return latest

    return None


def load_clients_registry() -> Dict:
    """Load client registry."""
    clients_file = CONFIG_DIR / "clients.json"
    if not clients_file.exists():
        return {"clients": []}
    with open(clients_file) as f:
        return json.load(f)


def find_client_name(identifier: str) -> Optional[str]:
    """Find full client name from identifier (name or short_name)."""
    registry = load_clients_registry()
    identifier_lower = identifier.lower()

    for client in registry.get('clients', []):
        if client['name'].lower() == identifier_lower:
            return client['name']
        if client.get('short_name', '').lower() == identifier_lower:
            return client['name']

    # Return as-is if not in registry (might be a direct name)
    return identifier


def get_prior_funder_eins(prior_funder_names: List[str], logger: logging.Logger) -> Set[str]:
    """Convert prior funder names to EINs by fuzzy matching."""
    if not prior_funder_names:
        return set()

    eins = set()
    for name in prior_funder_names:
        if not name:
            continue

        query = """
        SELECT ein
        FROM f990_2025.dim_foundations
        WHERE LOWER(name) LIKE %(pattern)s
        LIMIT 1
        """
        df = query_df(query, {'pattern': f"%{name.lower()}%"})

        if not df.empty:
            eins.add(df.iloc[0]['ein'])
            logger.info(f"Found prior funder: {name} -> {df.iloc[0]['ein']}")

    return eins


def get_existing_funder_eins(recipient_ein: str, logger: logging.Logger) -> Set[str]:
    """Get EINs of foundations that have already funded this recipient."""
    if not recipient_ein:
        return set()

    query = """
    SELECT DISTINCT foundation_ein
    FROM f990_2025.fact_grants
    WHERE recipient_ein = %(ein)s
    """
    df = query_df(query, {'ein': recipient_ein})

    if df.empty:
        logger.info(f"No existing funders found for EIN: {recipient_ein}")
        return set()

    eins = set(df['foundation_ein'].tolist())
    logger.info(f"Found {len(eins)} existing funders to exclude")
    return eins


def get_recipient_features(ein: str, client_data: dict, logger: logging.Logger) -> Optional[Dict]:
    """Get recipient features from database or compute from client data."""

    # Try calc_recipient_features first
    query = """
    SELECT *
    FROM f990_2025.calc_recipient_features
    WHERE ein = %(ein)s
    """
    df = query_df(query, {'ein': ein})

    if not df.empty:
        row = df.iloc[0]
        logger.info("Found recipient in calc_recipient_features")
        return build_recipient_features_from_row(row)

    # Fall back to client data
    logger.info("Recipient not in calc_recipient_features, using client data")
    return build_recipient_features_from_client(client_data)


def build_recipient_features_from_row(row: pd.Series) -> Dict:
    """Build recipient feature dict from database row."""
    features = {}

    # Numeric features
    features['r_total_revenue'] = float(row.get('total_revenue', 0) or 0)
    features['r_total_expenses'] = float(row.get('total_expenses', 0) or 0)
    features['r_assets'] = float(row.get('assets', 0) or 0)
    features['r_employee_count'] = float(row.get('employee_count', 0) or 0)
    features['r_mission_length'] = float(row.get('mission_length', 150) or 150)
    features['r_has_embedding'] = 1.0 if row.get('has_mission_embedding') else 0.0
    features['r_avg_grant'] = float(row.get('avg_grant_received', 10000) or 10000)

    # V4: High-coefficient recipient features from grant history
    features['r_total_grants'] = float(row.get('total_grants', 0) or 0)
    features['r_total_funders'] = float(row.get('total_funders', 0) or 0)
    features['r_total_funding'] = float(row.get('total_funding_received', 0) or 0)
    features['r_funder_states'] = float(row.get('funder_states', 0) or 0)
    features['r_funding_trend'] = float(row.get('funding_trend', 0) or 0)
    features['r_org_age'] = float(row.get('org_age_years', 0) or 0)

    # V4: Log-transformed recipient features
    features['r_log_total_revenue'] = math.log1p(max(features['r_total_revenue'], 0))
    features['r_log_assets'] = math.log1p(max(features['r_assets'], 0))
    features['r_log_avg_grant'] = math.log1p(max(features['r_avg_grant'], 0))

    # State one-hot
    state = row.get('state', '') or ''
    for s in STATE_CODES:
        features[f'r_state_{s}'] = 1.0 if state == s else 0.0
    features['r_state_'] = 1.0 if state not in STATE_CODES else 0.0

    # NTEE one-hot
    ntee = (row.get('ntee_broad', '') or '')[:1]
    for n in NTEE_CODES:
        if n == '':
            features['r_ntee_'] = 1.0 if not ntee else 0.0
        else:
            features[f'r_ntee_{n}'] = 1.0 if ntee == n else 0.0

    # Size one-hot
    size = (row.get('size_bucket', '') or '').upper()
    for bucket in SIZE_BUCKETS:
        if bucket == '':
            features['r_size_'] = 1.0 if not size else 0.0
        else:
            features[f'r_size_{bucket}'] = 1.0 if size == bucket else 0.0

    # Store state and NTEE for match features
    features['_state'] = state
    features['_ntee'] = ntee

    return features


def build_recipient_features_from_client(client: dict) -> Dict:
    """Build recipient features from client JSON data."""
    features = {}

    # Numeric features
    features['r_total_revenue'] = float(client.get('total_revenue', 0) or client.get('budget_numeric', 0) or 0)
    features['r_total_expenses'] = float(client.get('total_expenses', 0) or features['r_total_revenue'] * 0.95)
    features['r_assets'] = float(client.get('assets', 0) or 0)
    features['r_employee_count'] = float(client.get('employee_count', 20) or 20)
    features['r_mission_length'] = len(client.get('mission_statement', '')) or 150
    features['r_has_embedding'] = 0.0  # Unknown
    features['r_avg_grant'] = float(client.get('avg_grant_received', 10000) or 10000)

    # V4: High-coefficient recipient features (use imputation defaults for new clients)
    # These will be imputed if not provided
    features['r_total_grants'] = float(client.get('total_grants', 0) or 0)
    features['r_total_funders'] = float(client.get('total_funders', 0) or 0)
    features['r_total_funding'] = float(client.get('total_funding', 0) or 0)
    features['r_funder_states'] = float(client.get('funder_states', 0) or 0)
    features['r_funding_trend'] = float(client.get('funding_trend', 0) or 0)
    features['r_org_age'] = float(client.get('org_age', 0) or 0)

    # V4: Log-transformed recipient features
    features['r_log_total_revenue'] = math.log1p(max(features['r_total_revenue'], 0))
    features['r_log_assets'] = math.log1p(max(features['r_assets'], 0))
    features['r_log_avg_grant'] = math.log1p(max(features['r_avg_grant'], 0))

    # State one-hot
    state = client.get('state', '') or ''
    for s in STATE_CODES:
        features[f'r_state_{s}'] = 1.0 if state == s else 0.0
    features['r_state_'] = 1.0 if state not in STATE_CODES else 0.0

    # NTEE one-hot
    ntee = (client.get('ntee_code', '') or '')[:1]
    for n in NTEE_CODES:
        if n == '':
            features['r_ntee_'] = 1.0 if not ntee else 0.0
        else:
            features[f'r_ntee_{n}'] = 1.0 if ntee == n else 0.0

    # Size bucket from budget
    budget = features['r_total_revenue'] or client.get('budget_numeric', 0)
    if budget < 500000:
        size = 'TINY'
    elif budget < 2000000:
        size = 'SMALL'
    elif budget < 10000000:
        size = 'MEDIUM'
    else:
        size = 'LARGE'

    for bucket in SIZE_BUCKETS:
        if bucket == '':
            features['r_size_'] = 0.0
        else:
            features[f'r_size_{bucket}'] = 1.0 if size == bucket else 0.0

    # Store state and NTEE for match features
    features['_state'] = state
    features['_ntee'] = ntee

    return features


def get_all_foundation_features(min_assets: int, logger: logging.Logger) -> pd.DataFrame:
    """Batch load all foundation features meeting criteria."""

    query = """
    SELECT
        ein,
        name,
        state,
        assets,
        total_giving,
        total_grants_all_time,
        avg_grant_amount,
        median_grant,
        repeat_rate,
        in_state_grant_pct,
        states_funded,
        sectors_funded,
        openness_score,
        accepts_applications,
        payout_rate,
        officer_count,
        has_paid_staff,
        years_active,
        foundation_age,
        grant_amount_cv,
        primary_sector_pct,
        has_grant_history
    FROM f990_2025.calc_foundation_features
    WHERE has_grant_history = TRUE
      AND assets >= %(min_assets)s
      AND unique_recipients_all_time > 0
      AND (grants_to_orgs = TRUE OR accepts_applications = TRUE)
    """

    df = query_df(query, {'min_assets': min_assets})
    logger.info(f"Loaded {len(df)} foundations with assets >= ${min_assets:,}")

    return df


def build_foundation_features(row: pd.Series) -> Dict:
    """Build foundation feature dict from database row."""
    features = {}

    # Map database columns to model feature names
    features['f_assets'] = float(row.get('assets', 0) or 0)
    features['f_total_giving'] = float(row.get('total_giving', 0) or 0)
    features['f_total_grants'] = float(row.get('total_grants_all_time', 0) or 0)
    features['f_avg_grant'] = float(row.get('avg_grant_amount', 0) or 0)
    features['f_median_grant'] = float(row.get('median_grant', 0) or 0)
    features['f_repeat_rate'] = float(row.get('repeat_rate', 0.5) or 0.5)
    features['f_in_state_pct'] = float(row.get('in_state_grant_pct', 0.5) or 0.5)
    features['f_states_funded'] = float(row.get('states_funded', 1) or 1)
    features['f_sectors_funded'] = float(row.get('sectors_funded', 1) or 1)
    features['f_openness_score'] = float(row.get('openness_score', 0.5) or 0.5)
    features['f_accepts_apps'] = 1.0 if row.get('accepts_applications') else 0.0
    features['f_payout_rate'] = float(row.get('payout_rate', 0.05) or 0.05)
    features['f_officer_count'] = float(row.get('officer_count', 4) or 4)
    features['f_has_paid_staff'] = 1.0 if row.get('has_paid_staff') else 0.0
    features['f_years_active'] = float(row.get('years_active', 5) or 5)
    features['f_foundation_age'] = float(row.get('foundation_age', 6) or 6)
    features['f_grant_cv'] = float(row.get('grant_amount_cv', 3) or 3)
    features['f_primary_sector_pct'] = float(row.get('primary_sector_pct', 0.3) or 0.3)

    # V4: Log-transformed features (dampen extreme values)
    features['f_log_total_grants'] = math.log1p(max(features['f_total_grants'], 0))
    features['f_log_median_grant'] = math.log1p(max(features['f_median_grant'], 0))
    features['f_log_total_giving'] = math.log1p(max(features['f_total_giving'], 0))
    features['f_log_assets'] = math.log1p(max(features['f_assets'], 0))

    # V4: Grants per year (log-transformed)
    years_active = max(features['f_years_active'], 1)
    grants_per_year = features['f_total_grants'] / years_active
    features['f_log_grants_per_year'] = math.log1p(max(grants_per_year, 0))

    # V4: Sector concentration HHI (from staging table)
    ein = row.get('ein', '') or ''
    features['f_sector_hhi'] = get_foundation_hhi(ein)

    # State one-hot
    state = row.get('state', '') or ''
    for s in STATE_CODES:
        features[f'f_state_{s}'] = 1.0 if state == s else 0.0

    # Store state and EIN for match features
    features['_state'] = state
    features['_ein'] = ein

    return features


def impute_missing(features: Dict, imputation: Dict) -> Dict:
    """Fill missing values with imputation defaults."""
    for key, value in features.items():
        if key.startswith('_'):
            continue
        if value is None or (isinstance(value, float) and math.isnan(value)):
            if key in imputation:
                features[key] = imputation[key]
            else:
                features[key] = 0.0
    return features


def scale_feature(value: float, feature_name: str, scaling: Dict) -> float:
    """Apply z-score scaling to a feature value."""
    if feature_name not in scaling:
        return value

    params = scaling[feature_name]
    mean = params.get('mean', 0)
    sd = params.get('sd', 1)

    if sd == 0:
        return 0.0

    return (value - mean) / sd


def score_pair(
    foundation_features: Dict,
    recipient_features: Dict,
    coefficients: Dict,
    scaling: Dict
) -> float:
    """Calculate match probability using LASSO model."""

    # 1. Compute match features
    f_state = foundation_features.get('_state', '')
    r_state = recipient_features.get('_state', '')
    f_ein = foundation_features.get('_ein', '')
    r_ntee = recipient_features.get('_ntee', '')

    # V4: Enhanced match features
    match_features = {
        'match_same_state': 1.0 if f_state and r_state and f_state == r_state else 0.0,
        # Sector match: % of foundation's grants in recipient's sector
        'match_sector_pct': get_sector_match_pct(f_ein, r_ntee),
        # State match: % of foundation's grants in recipient's state
        'match_state_pct': get_state_match_pct(f_ein, r_state),
    }

    # Grant size ratio: log(f_median_grant / r_avg_grant)
    f_median = foundation_features.get('f_median_grant', 0) or 0
    r_avg = recipient_features.get('r_avg_grant', 0) or 0
    if f_median > 0 and r_avg > 0:
        match_features['match_grant_size_ratio'] = math.log(max(f_median, 1) / max(r_avg, 1))
    else:
        match_features['match_grant_size_ratio'] = 0.0

    # Budget in range: probability recipient budget is in foundation's typical range
    # Based on model training, this is computed from budget_min_typical and budget_max_typical
    # For now, use a simplified version based on revenue alignment
    r_revenue = recipient_features.get('r_total_revenue', 0) or 0
    f_avg_grant = foundation_features.get('f_avg_grant', 0) or 0
    if r_revenue > 0 and f_avg_grant > 0:
        # Typical recipients have revenue 10-100x of average grant
        ratio = r_revenue / f_avg_grant
        if 10 <= ratio <= 100:
            match_features['match_budget_in_range'] = 1.0
        elif 5 <= ratio <= 200:
            match_features['match_budget_in_range'] = 0.5
        else:
            match_features['match_budget_in_range'] = 0.0
    else:
        match_features['match_budget_in_range'] = 0.5  # Unknown

    # 2. Combine all features
    all_features = {}
    for key, value in foundation_features.items():
        if not key.startswith('_'):
            all_features[key] = value
    for key, value in recipient_features.items():
        if not key.startswith('_'):
            all_features[key] = value
    all_features.update(match_features)

    # 3. Scale features and compute logit
    intercept = coefficients.get('intercept', 0)
    coefs = coefficients.get('coefficients', {})

    logit = intercept
    for feature_name, coef in coefs.items():
        if feature_name in all_features:
            raw_value = all_features[feature_name]
            scaled_value = scale_feature(raw_value, feature_name, scaling)
            logit += coef * scaled_value

    # 4. Apply sigmoid
    if logit < -500:
        return 0.0
    if logit > 500:
        return 1.0
    probability = 1 / (1 + math.exp(-logit))

    return probability


def main():
    parser = argparse.ArgumentParser(description='Score foundations against a client')
    parser.add_argument('--client', type=str, required=True, help='Client name or short name')
    parser.add_argument('--top-k', type=int, default=50, help='Number of foundations to return')
    parser.add_argument('--min-assets', type=int, default=100000, help='Minimum foundation assets')
    parser.add_argument('--date', type=str, help='Run date (YYYY-MM-DD)')

    args = parser.parse_args()

    # Parse date if provided
    run_date = None
    if args.date:
        run_date = date.fromisoformat(args.date)

    # Find client name
    client_name = find_client_name(args.client)
    if not client_name:
        print(f"ERROR: Could not find client: {args.client}")
        sys.exit(1)

    # Set up logging
    logger = setup_logging(client_name)
    logger.info(f"[02_score_foundations] Starting for {client_name}")

    # Find run directory
    run_dir = find_client_run_dir(client_name, run_date)
    if not run_dir:
        print(f"ERROR: No run directory found for {client_name}")
        print("Make sure to run 01_load_client.py first")
        sys.exit(1)

    logger.info(f"Using run directory: {run_dir}")

    # Load client data
    client_file = run_dir / "01_client.json"
    client = load_json(client_file)
    logger.info(f"Loaded client: {client.get('organization_name')}")

    # Check for EIN
    ein = client.get('ein', '')
    if not ein:
        print("ERROR: Client has no EIN. Cannot score foundations.")
        print("Please ensure 01_client.json has a valid EIN.")
        sys.exit(1)

    logger.info(f"Client EIN: {ein}")

    # Load model config
    coefficients = load_json(CONFIG_DIR / "coefficients.json")
    scaling = load_json(CONFIG_DIR / "scaling.json")
    imputation = load_json(CONFIG_DIR / "imputation.json")
    logger.info("Loaded model configuration")

    # V4: Load foundation sector/state distributions for match features
    print("Loading foundation distributions...")
    load_foundation_distributions(logger)

    # Get recipient features
    recipient_features = get_recipient_features(ein, client, logger)
    recipient_features = impute_missing(recipient_features, imputation)
    logger.info(f"Recipient features: {len([k for k in recipient_features if not k.startswith('_')])} features")

    # Get prior funder EINs to exclude (from questionnaire)
    prior_funders = client.get('prior_funders', [])
    prior_funder_eins = get_prior_funder_eins(prior_funders, logger)

    # Get existing funder EINs to exclude (from database)
    existing_funder_eins = get_existing_funder_eins(ein, logger)

    # Combine both sets
    exclude_eins = prior_funder_eins | existing_funder_eins
    logger.info(f"Excluding {len(exclude_eins)} total funders ({len(prior_funder_eins)} from questionnaire, {len(existing_funder_eins)} from database)")

    # Get all foundation features
    foundations_df = get_all_foundation_features(args.min_assets, logger)

    if foundations_df.empty:
        print("WARNING: No foundations found matching criteria")
        # Create empty output
        empty_df = pd.DataFrame(columns=[
            'foundation_ein', 'foundation_name', 'foundation_state',
            'match_score', 'match_probability', 'match_rank', 'same_state'
        ])
        empty_df.to_csv(run_dir / "02_scored_foundations.csv", index=False)
        logger.info("Saved empty results")
        return

    # Score each foundation
    print(f"Scoring {len(foundations_df)} foundations...")
    scores = []

    for idx, row in foundations_df.iterrows():
        f_ein = row['ein']

        # Skip excluded funders (prior + existing)
        if f_ein in exclude_eins:
            continue

        # Build foundation features
        f_features = build_foundation_features(row)
        f_features = impute_missing(f_features, imputation)

        # Score
        probability = score_pair(f_features, recipient_features, coefficients, scaling)

        # Check if same state
        same_state = f_features.get('_state', '') == recipient_features.get('_state', '')

        scores.append({
            'foundation_ein': f_ein,
            'foundation_name': row.get('name', ''),
            'foundation_state': row.get('state', ''),
            'match_probability': probability,
            'match_score': round(probability * 100, 1),
            'same_state': same_state
        })

    # Sort by probability descending
    scores.sort(key=lambda x: x['match_probability'], reverse=True)

    # Take top K
    top_scores = scores[:args.top_k]

    # Add rank
    for i, score in enumerate(top_scores):
        score['match_rank'] = i + 1

    # Create DataFrame and save
    result_df = pd.DataFrame(top_scores)
    result_df = result_df[[
        'foundation_ein', 'foundation_name', 'foundation_state',
        'match_score', 'match_probability', 'match_rank', 'same_state'
    ]]

    output_file = run_dir / "02_scored_foundations.csv"
    result_df.to_csv(output_file, index=False)

    # Log results
    if top_scores:
        top_score = top_scores[0]
        logger.info(f"Top score: {top_score['match_score']} ({top_score['foundation_name']})")

    logger.info(f"Saved {len(top_scores)} foundations to {output_file}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Scoring complete!")
    print(f"{'='*60}")
    print(f"Client: {client.get('organization_name')}")
    print(f"EIN: {ein}")
    print(f"State: {client.get('state', 'Unknown')}")
    print(f"Foundations scored: {len(scores)}")
    print(f"Funders excluded: {len(exclude_eins)} ({len(prior_funder_eins)} prior, {len(existing_funder_eins)} existing)")
    print(f"\nTop 5 matches:")
    for score in top_scores[:5]:
        state_marker = " (same state)" if score['same_state'] else ""
        print(f"  {score['match_rank']}. {score['foundation_name'][:40]} - {score['match_score']}%{state_marker}")
    print(f"\nOutput: {output_file}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
