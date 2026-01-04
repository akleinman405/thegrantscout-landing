#!/usr/bin/env python3
"""
02_score_foundations_v6.1.py - Score foundations using V6.1 model with semantic similarity

KEY CHANGES FROM V5:
1. Adds semantic similarity using foundation and recipient embeddings
2. Uses V6.1 coefficients (size-matched training, balanced by revenue)
3. Includes match_semantic_similarity feature

Usage:
    python scripts/02_score_foundations_v6.1.py --client "PSMF" --top-k 100
"""
import argparse
import json
import logging
import math
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import numpy as np
import pandas as pd

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils import query_df, get_run_dir, get_latest_run_dir, CONFIG_DIR, LOGS_DIR


# State codes used in model (must match coefficients)
STATE_CODES = ['NY', 'CA', 'TX', 'IL', 'FL', 'PA', 'MA', 'DE', 'NJ', 'MI']

# NTEE broad categories used in model
NTEE_CODES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# Caches (loaded once per run)
_foundation_sector_dist_cache: Dict[str, Dict[str, float]] = {}
_foundation_state_dist_cache: Dict[str, Dict[str, float]] = {}
_foundation_hhi_cache: Dict[str, float] = {}
_foundation_embeddings_cache: Dict[str, np.ndarray] = {}
_recipient_embeddings_cache: Dict[str, np.ndarray] = {}
_sector_avg_embeddings_cache: Dict[str, np.ndarray] = {}


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


def load_foundation_embeddings(logger: logging.Logger) -> None:
    """Load foundation average embeddings for semantic similarity."""
    global _foundation_embeddings_cache

    query = """
    SELECT foundation_ein, avg_embedding
    FROM f990_2025.calc_foundation_avg_embedding
    WHERE avg_embedding IS NOT NULL
    """
    df = query_df(query, {})

    for _, row in df.iterrows():
        ein = row['foundation_ein']
        emb = np.array(row['avg_embedding'])
        _foundation_embeddings_cache[ein] = emb

    logger.info(f"Loaded {len(_foundation_embeddings_cache)} foundation embeddings")


def load_recipient_embeddings(logger: logging.Logger) -> None:
    """Load recipient mission embeddings (68% coverage)."""
    global _recipient_embeddings_cache

    query = """
    SELECT ein, mission_embedding
    FROM f990_2025.emb_nonprofit_missions
    WHERE mission_embedding IS NOT NULL
    """
    df = query_df(query, {})

    for _, row in df.iterrows():
        ein = row['ein']
        emb = np.array(row['mission_embedding'])
        _recipient_embeddings_cache[ein] = emb

    logger.info(f"Loaded {len(_recipient_embeddings_cache)} recipient embeddings")


def load_sector_avg_embeddings(logger: logging.Logger) -> None:
    """Load sector average embeddings as fallback."""
    global _sector_avg_embeddings_cache

    # Compute sector averages from foundation embeddings
    query = """
    WITH foundation_sectors AS (
        SELECT DISTINCT foundation_ein, ntee_broad
        FROM f990_2025.stg_foundation_sector_dist
        WHERE sector_pct >= 0.20
    )
    SELECT
        fs.ntee_broad,
        array_agg(fae.avg_embedding) as embeddings
    FROM foundation_sectors fs
    JOIN f990_2025.calc_foundation_avg_embedding fae ON fs.foundation_ein = fae.foundation_ein
    WHERE fae.avg_embedding IS NOT NULL
    GROUP BY fs.ntee_broad
    """
    try:
        df = query_df(query, {})

        for _, row in df.iterrows():
            ntee = row['ntee_broad'] or ''
            embeddings_list = [np.array(e) for e in row['embeddings'] if e is not None]
            if embeddings_list:
                stacked = np.vstack(embeddings_list)
                avg_emb = np.mean(stacked, axis=0)
                norm = np.linalg.norm(avg_emb)
                if norm > 0:
                    avg_emb = avg_emb / norm
                _sector_avg_embeddings_cache[ntee] = avg_emb

        logger.info(f"Computed {len(_sector_avg_embeddings_cache)} sector average embeddings")
    except Exception as e:
        logger.warning(f"Could not load sector embeddings: {e}")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    if a is None or b is None:
        return 0.0
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def get_semantic_similarity(foundation_ein: str, recipient_ein: str, recipient_ntee: str) -> float:
    """
    Compute semantic similarity between foundation and recipient.

    Uses actual recipient embedding if available (68% coverage),
    falls back to sector average if not.
    """
    f_emb = _foundation_embeddings_cache.get(foundation_ein)
    if f_emb is None:
        return 0.0

    # Try actual recipient embedding first
    r_emb = _recipient_embeddings_cache.get(recipient_ein)
    if r_emb is not None:
        return cosine_similarity(f_emb, r_emb)

    # Fallback to sector average
    ntee_broad = (recipient_ntee or '')[:1]
    s_emb = _sector_avg_embeddings_cache.get(ntee_broad)
    if s_emb is not None:
        return cosine_similarity(f_emb, s_emb)

    return 0.0


def get_sector_match_pct(foundation_ein: str, recipient_ntee: str) -> float:
    """Get % of foundation's grants in recipient's sector."""
    if not recipient_ntee:
        return 0.5

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
    return _foundation_hhi_cache.get(foundation_ein, 0.05)


def setup_logging(client_name: str) -> logging.Logger:
    """Set up logging for this run."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = client_name.replace(" ", "_")[:20]
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_{safe_name}.log"

    logger = logging.getLogger('02_score_foundations_v61')
    logger.setLevel(logging.INFO)
    logger.handlers = []

    fh = logging.FileHandler(log_file, mode='a')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)

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
        run_dir = get_run_dir(client_name, date.today())
        if (run_dir / "01_client.json").exists():
            return run_dir

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
    """Find full client name from identifier."""
    registry = load_clients_registry()
    identifier_lower = identifier.lower()

    for client in registry.get('clients', []):
        if client['name'].lower() == identifier_lower:
            return client['name']
        if client.get('short_name', '').lower() == identifier_lower:
            return client['name']

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

    query = """
    SELECT *
    FROM f990_2025.calc_recipient_features
    WHERE ein = %(ein)s
    """
    df = query_df(query, {'ein': ein})

    if not df.empty:
        row = df.iloc[0]
        logger.info("Found recipient in calc_recipient_features")
        return build_recipient_features_from_row(row, ein)

    logger.info("Recipient not in calc_recipient_features, using client data")
    return build_recipient_features_from_client(client_data, ein)


def build_recipient_features_from_row(row: pd.Series, ein: str) -> Dict:
    """Build recipient feature dict from database row."""
    features = {}

    features['r_total_revenue'] = float(row.get('total_revenue', 0) or 0)
    features['r_org_age'] = float(row.get('org_age_years', 0) or 0)
    features['r_is_emerging'] = 1.0 if features['r_org_age'] < 5 else 0.0

    # Log-transformed
    features['r_log_total_revenue'] = math.log1p(max(features['r_total_revenue'], 0))
    features['r_log_org_age'] = math.log1p(max(features['r_org_age'], 0))

    # State one-hot
    state = row.get('state', '') or ''
    for s in STATE_CODES:
        features[f'r_state_{s}'] = 1.0 if state == s else 0.0
    features['r_state_OTHER'] = 1.0 if state not in STATE_CODES else 0.0

    # NTEE one-hot
    ntee = (row.get('ntee_broad', '') or '')[:1]
    for n in NTEE_CODES:
        features[f'r_ntee_{n}'] = 1.0 if ntee == n else 0.0
    features['r_ntee_UNKNOWN'] = 1.0 if not ntee else 0.0

    # Store for match features
    features['_state'] = state
    features['_ntee'] = ntee
    features['_ein'] = ein

    return features


def build_recipient_features_from_client(client: dict, ein: str) -> Dict:
    """Build recipient features from client JSON data."""
    features = {}

    features['r_total_revenue'] = float(client.get('total_revenue', 0) or client.get('budget_numeric', 0) or 0)
    features['r_org_age'] = float(client.get('org_age', 10) or 10)
    features['r_is_emerging'] = 1.0 if features['r_org_age'] < 5 else 0.0

    # Log-transformed
    features['r_log_total_revenue'] = math.log1p(max(features['r_total_revenue'], 0))
    features['r_log_org_age'] = math.log1p(max(features['r_org_age'], 0))

    # State one-hot
    state = client.get('state', '') or ''
    for s in STATE_CODES:
        features[f'r_state_{s}'] = 1.0 if state == s else 0.0
    features['r_state_OTHER'] = 1.0 if state not in STATE_CODES else 0.0

    # NTEE one-hot
    ntee = (client.get('ntee_code', '') or '')[:1]
    for n in NTEE_CODES:
        features[f'r_ntee_{n}'] = 1.0 if ntee == n else 0.0
    features['r_ntee_UNKNOWN'] = 1.0 if not ntee else 0.0

    # Store for match features
    features['_state'] = state
    features['_ntee'] = ntee
    features['_ein'] = ein

    return features


def get_all_foundation_features(min_assets: int, logger: logging.Logger, min_recipients: int = 5) -> pd.DataFrame:
    """
    Batch load all foundation features meeting criteria.

    Args:
        min_assets: Minimum foundation assets
        logger: Logger instance
        min_recipients: Minimum unique recipients to exclude "captive" foundations
                       that only give to 1-2 orgs (default: 5)
    """

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
        preselected_only,
        payout_rate,
        officer_count,
        has_paid_staff,
        years_active,
        foundation_age,
        grant_amount_cv,
        primary_sector_pct,
        has_grant_history,
        giving_trend,
        last_grant_year,
        unique_recipients_all_time
    FROM f990_2025.calc_foundation_features
    WHERE has_grant_history = TRUE
      AND assets >= %(min_assets)s
      AND unique_recipients_all_time >= %(min_recipients)s
      AND (grants_to_orgs = TRUE OR accepts_applications = TRUE)
      AND (preselected_only = FALSE OR preselected_only IS NULL)
    """

    df = query_df(query, {'min_assets': min_assets, 'min_recipients': min_recipients})
    logger.info(f"Loaded {len(df)} foundations (assets >= ${min_assets:,}, >= {min_recipients} recipients, open to applications)")

    return df


def build_foundation_features(row: pd.Series) -> Dict:
    """Build foundation feature dict from database row."""
    features = {}

    # Core features matching V6.1 training
    features['f_assets'] = float(row.get('assets', 0) or 0)
    features['f_total_grants'] = float(row.get('total_grants_all_time', 0) or 0)
    features['f_avg_grant'] = float(row.get('avg_grant_amount', 0) or 0)
    features['f_median_grant'] = float(row.get('median_grant', 0) or 0)
    features['f_repeat_rate'] = float(row.get('repeat_rate', 0.5) or 0.5)
    features['f_openness_score'] = float(row.get('openness_score', 0.5) or 0.5)
    features['f_in_state_pct'] = float(row.get('in_state_grant_pct', 0.5) or 0.5)
    features['f_states_funded'] = float(row.get('states_funded', 1) or 1)
    features['f_sectors_funded'] = float(row.get('sectors_funded', 1) or 1)
    features['f_years_active'] = float(row.get('years_active', 5) or 5)
    features['f_foundation_age'] = float(row.get('foundation_age', 10) or 10)
    features['f_payout_rate'] = float(row.get('payout_rate', 0.05) or 0.05)
    features['f_officer_count'] = float(row.get('officer_count', 4) or 4)
    features['f_has_paid_staff'] = 1.0 if row.get('has_paid_staff') else 0.0
    features['f_grant_cv'] = float(row.get('grant_amount_cv', 3) or 3)
    features['f_primary_sector_pct'] = float(row.get('primary_sector_pct', 0.3) or 0.3)

    # Sector concentration HHI
    ein = row.get('ein', '') or ''
    features['f_sector_hhi'] = get_foundation_hhi(ein)

    # Boolean flags
    accepts = row.get('accepts_applications', False)
    preselected = row.get('preselected_only', True)
    features['f_is_accessible'] = 1.0 if accepts and not preselected else 0.0
    features['f_is_small'] = 1.0 if features['f_assets'] < 10000000 else 0.0
    features['f_is_growing'] = 1.0 if row.get('giving_trend') == 'growing' else 0.0
    features['f_is_declining'] = 1.0 if row.get('giving_trend') == 'declining' else 0.0
    features['f_is_recently_active'] = 1.0 if (row.get('last_grant_year') or 0) >= 2022 else 0.0

    # Log-transformed features
    features['f_log_assets'] = math.log1p(max(features['f_assets'], 0))
    features['f_log_total_grants'] = math.log1p(max(features['f_total_grants'], 0))
    features['f_log_avg_grant'] = math.log1p(max(features['f_avg_grant'], 0))
    features['f_log_median_grant'] = math.log1p(max(features['f_median_grant'], 0))

    # Grants per year
    years_active = max(features['f_years_active'], 1)
    grants_per_year = features['f_total_grants'] / years_active
    features['f_grants_per_year'] = grants_per_year
    features['f_log_grants_per_year'] = math.log1p(max(grants_per_year, 0))

    # State one-hot
    state = row.get('state', '') or ''
    for s in STATE_CODES:
        features[f'f_state_{s}'] = 1.0 if state == s else 0.0
    features['f_state_OTHER'] = 1.0 if state not in STATE_CODES else 0.0

    # Embedding flag
    features['f_has_embedding'] = 1.0 if ein in _foundation_embeddings_cache else 0.0

    # Store for match features
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
) -> tuple:
    """
    Calculate match score using V6.1 LASSO model.

    Returns tuple: (logit, probability, semantic_similarity)

    NOTE: We return the raw logit for ranking because probabilities saturate
    near 1.0 for most foundation-client pairs. The logit provides better
    discrimination for ranking purposes.
    """

    f_state = foundation_features.get('_state', '')
    r_state = recipient_features.get('_state', '')
    f_ein = foundation_features.get('_ein', '')
    r_ein = recipient_features.get('_ein', '')
    r_ntee = recipient_features.get('_ntee', '')

    # V6.1: Semantic similarity using actual embeddings
    semantic_sim = get_semantic_similarity(f_ein, r_ein, r_ntee)

    # Match features
    match_features = {
        'match_same_state': 1.0 if f_state and r_state and f_state == r_state else 0.0,
        'match_sector_pct': get_sector_match_pct(f_ein, r_ntee),
        'match_state_pct': get_state_match_pct(f_ein, r_state),
        'match_semantic_similarity': semantic_sim,
    }

    # Grant size ratio
    f_median = foundation_features.get('f_median_grant', 0) or 0
    r_revenue = recipient_features.get('r_total_revenue', 0) or 0
    if f_median > 0 and r_revenue > 0:
        match_features['match_grant_size_ratio'] = math.log(max(r_revenue, 1) / max(f_median, 1))
    else:
        match_features['match_grant_size_ratio'] = 0.0

    # Budget in range
    f_avg = foundation_features.get('f_avg_grant', 0) or 0
    if r_revenue > 0 and f_avg > 0:
        ratio = r_revenue / f_avg
        if 10 <= ratio <= 100:
            match_features['match_budget_in_range'] = 1.0
        elif 5 <= ratio <= 200:
            match_features['match_budget_in_range'] = 0.5
        else:
            match_features['match_budget_in_range'] = 0.0
    else:
        match_features['match_budget_in_range'] = 0.5

    # Interaction terms (from V6.1 training)
    match_features['match_state_x_geo_conc'] = (
        match_features['match_state_pct'] *
        (1 - foundation_features.get('f_in_state_pct', 0.5))
    )
    match_features['match_sector_x_sector_hhi'] = (
        match_features['match_sector_pct'] *
        foundation_features.get('f_sector_hhi', 0.05)
    )

    # Combine all features
    all_features = {}
    for key, value in foundation_features.items():
        if not key.startswith('_'):
            all_features[key] = value
    for key, value in recipient_features.items():
        if not key.startswith('_'):
            all_features[key] = value
    all_features.update(match_features)

    # Scale features and compute logit
    intercept = coefficients.get('intercept', 0)
    coefs = coefficients.get('coefficients', {})

    logit = intercept
    for feature_name, coef in coefs.items():
        if feature_name in all_features:
            raw_value = all_features[feature_name]
            scaled_value = scale_feature(raw_value, feature_name, scaling)
            logit += coef * scaled_value

    # Apply sigmoid for probability (for display)
    if logit < -500:
        probability = 0.0
    elif logit > 500:
        probability = 1.0
    else:
        probability = 1 / (1 + math.exp(-logit))

    return (logit, probability, semantic_sim)


def main():
    parser = argparse.ArgumentParser(description='Score foundations using V6.1 model')
    parser.add_argument('--client', type=str, required=True, help='Client name or short name')
    parser.add_argument('--top-k', type=int, default=50, help='Number of foundations to return')
    parser.add_argument('--min-assets', type=int, default=100000, help='Minimum foundation assets')
    parser.add_argument('--min-recipients', type=int, default=5, help='Minimum unique recipients (filters captive foundations)')
    parser.add_argument('--date', type=str, help='Run date (YYYY-MM-DD)')

    args = parser.parse_args()

    run_date = None
    if args.date:
        run_date = date.fromisoformat(args.date)

    client_name = find_client_name(args.client)
    if not client_name:
        print(f"ERROR: Could not find client: {args.client}")
        sys.exit(1)

    logger = setup_logging(client_name)
    logger.info(f"[02_score_foundations_v6.1] Starting for {client_name}")

    run_dir = find_client_run_dir(client_name, run_date)
    if not run_dir:
        print(f"ERROR: No run directory found for {client_name}")
        print("Make sure to run 01_load_client.py first")
        sys.exit(1)

    logger.info(f"Using run directory: {run_dir}")

    client_file = run_dir / "01_client.json"
    client = load_json(client_file)
    logger.info(f"Loaded client: {client.get('organization_name')}")

    ein = client.get('ein', '')
    if not ein:
        print("ERROR: Client has no EIN. Cannot score foundations.")
        sys.exit(1)

    logger.info(f"Client EIN: {ein}")

    # Load V6.1 model config
    model_dir = Path(__file__).parent.parent / "outputs" / "v6.1" / "model"
    if (model_dir / "coefficients.json").exists():
        coefficients = load_json(model_dir / "coefficients.json")
        scaling = load_json(model_dir / "scaling.json")
        logger.info("Loaded V6.1 model from outputs/v6.1/model")
    else:
        # Fall back to config directory
        coefficients = load_json(CONFIG_DIR / "coefficients.json")
        scaling = load_json(CONFIG_DIR / "scaling.json")
        logger.info("Loaded model from config (fallback)")

    imputation = load_json(CONFIG_DIR / "imputation.json")

    # Load distributions and embeddings
    print("Loading foundation distributions...")
    load_foundation_distributions(logger)

    print("Loading foundation embeddings...")
    load_foundation_embeddings(logger)

    print("Loading recipient embeddings...")
    load_recipient_embeddings(logger)

    print("Loading sector average embeddings...")
    load_sector_avg_embeddings(logger)

    # Get recipient features
    recipient_features = get_recipient_features(ein, client, logger)
    recipient_features = impute_missing(recipient_features, imputation)
    logger.info(f"Recipient features: {len([k for k in recipient_features if not k.startswith('_')])} features")

    # Get prior funder EINs to exclude
    prior_funders = client.get('prior_funders', [])
    prior_funder_eins = get_prior_funder_eins(prior_funders, logger)

    # Get existing funder EINs to exclude
    existing_funder_eins = get_existing_funder_eins(ein, logger)

    exclude_eins = prior_funder_eins | existing_funder_eins
    logger.info(f"Excluding {len(exclude_eins)} total funders")

    # Get all foundation features
    foundations_df = get_all_foundation_features(args.min_assets, logger, args.min_recipients)

    if foundations_df.empty:
        print("WARNING: No foundations found matching criteria")
        empty_df = pd.DataFrame(columns=[
            'foundation_ein', 'foundation_name', 'foundation_state',
            'match_score', 'match_probability', 'match_rank', 'same_state', 'semantic_sim'
        ])
        empty_df.to_csv(run_dir / "02_scored_foundations.csv", index=False)
        return

    # Score each foundation
    print(f"Scoring {len(foundations_df)} foundations with V6.1 model...")
    scores = []

    for idx, row in foundations_df.iterrows():
        f_ein = row['ein']

        if f_ein in exclude_eins:
            continue

        f_features = build_foundation_features(row)
        f_features = impute_missing(f_features, imputation)

        # Get logit, probability, and semantic similarity
        logit, probability, semantic_sim = score_pair(f_features, recipient_features, coefficients, scaling)

        same_state = f_features.get('_state', '') == recipient_features.get('_state', '')

        scores.append({
            'foundation_ein': f_ein,
            'foundation_name': row.get('name', ''),
            'foundation_state': row.get('state', ''),
            'match_logit': logit,
            'match_probability': probability,
            'match_score': round(logit, 2),  # Use logit as score for ranking
            'same_state': same_state,
            'semantic_sim': round(semantic_sim, 3)
        })

    # Sort by LOGIT descending (not probability, which saturates)
    scores.sort(key=lambda x: x['match_logit'], reverse=True)

    # Take top K
    top_scores = scores[:args.top_k]

    for i, score in enumerate(top_scores):
        score['match_rank'] = i + 1

    result_df = pd.DataFrame(top_scores)
    result_df = result_df[[
        'foundation_ein', 'foundation_name', 'foundation_state',
        'match_score', 'match_logit', 'match_probability', 'match_rank', 'same_state', 'semantic_sim'
    ]]

    output_file = run_dir / "02_scored_foundations.csv"
    result_df.to_csv(output_file, index=False)

    if top_scores:
        top_score = top_scores[0]
        logger.info(f"Top score: {top_score['match_score']} ({top_score['foundation_name']})")

    logger.info(f"Saved {len(top_scores)} foundations to {output_file}")

    print(f"\n{'='*60}")
    print(f"V6.1 Scoring complete!")
    print(f"{'='*60}")
    print(f"Client: {client.get('organization_name')}")
    print(f"EIN: {ein}")
    print(f"State: {client.get('state', 'Unknown')}")
    print(f"Foundations scored: {len(scores)}")
    print(f"Funders excluded: {len(exclude_eins)}")
    print(f"\nTop 5 matches:")
    for score in top_scores[:5]:
        state_marker = " (same state)" if score['same_state'] else ""
        print(f"  {score['match_rank']}. {score['foundation_name'][:40]} - {score['match_score']}% (sim: {score['semantic_sim']}){state_marker}")
    print(f"\nOutput: {output_file}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
