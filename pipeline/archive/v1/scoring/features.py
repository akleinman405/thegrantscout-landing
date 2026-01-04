"""
Feature calculator for grant matching model.

Computes all 59 features for foundation-recipient pairs using pre-computed tables.
"""
import json
from pathlib import Path
from typing import Optional

import pandas as pd

from config.database import query_df

# Load imputation values
CONFIG_DIR = Path(__file__).parent.parent / "config"
with open(CONFIG_DIR / "imputation.json") as f:
    IMPUTATION_VALUES = json.load(f)

# State codes used in model
STATE_CODES = ['NY', 'CA', 'TX', 'IL', 'FL', 'PA', 'MA', 'DE', 'NJ', 'MI']

# NTEE broad categories used in model
NTEE_CODES = ['', 'B', 'P', 'A', 'E', 'X', 'D', 'T', 'Q']

# Size buckets used in model
SIZE_BUCKETS = ['TINY', 'SMALL', 'MEDIUM', 'LARGE', '']


def get_foundation_features(foundation_ein: str) -> Optional[dict]:
    """
    Get pre-computed foundation features from database.

    Args:
        foundation_ein: Foundation EIN

    Returns:
        Dict with all f_* features, or None if not found
    """
    query = """
    SELECT
        ein,
        state,
        assets::float as f_assets,
        total_giving::float as f_total_giving,
        total_grants_all_time::float as f_total_grants,
        avg_grant_amount::float as f_avg_grant,
        median_grant::float as f_median_grant,
        COALESCE(repeat_rate::float, 0.5) as f_repeat_rate,
        COALESCE(in_state_grant_pct::float, 0.5) as f_in_state_pct,
        COALESCE(states_funded::float, 1) as f_states_funded,
        COALESCE(sectors_funded::float, 1) as f_sectors_funded,
        COALESCE(openness_score::float, 0.5) as f_openness_score,
        CASE WHEN accepts_applications THEN 1.0 ELSE 0.0 END as f_accepts_apps,
        COALESCE(payout_rate::float, 0.05) as f_payout_rate,
        COALESCE(officer_count::float, 4) as f_officer_count,
        CASE WHEN has_paid_staff THEN 1.0 ELSE 0.0 END as f_has_paid_staff,
        COALESCE(years_active::float, 5) as f_years_active,
        COALESCE(foundation_age::float, 6) as f_foundation_age,
        COALESCE(grant_amount_cv::float, 3) as f_grant_cv,
        COALESCE(primary_sector_pct::float, 0.3) as f_primary_sector_pct
    FROM f990_2025.calc_foundation_features
    WHERE ein = %(ein)s
    """

    df = query_df(query, {'ein': foundation_ein})

    if df.empty:
        return None

    row = df.iloc[0]
    features = row.to_dict()

    # Add state one-hot features
    foundation_state = features.pop('ein', None) or ''
    foundation_state = row.get('state', '') or ''
    for state in STATE_CODES:
        features[f'f_state_{state}'] = 1.0 if foundation_state == state else 0.0

    # Apply imputation for any remaining NaN
    for key, value in features.items():
        if pd.isna(value) and key in IMPUTATION_VALUES:
            features[key] = IMPUTATION_VALUES[key]
        elif pd.isna(value):
            features[key] = 0.0

    # Store state for match feature calculation
    features['_state'] = foundation_state

    return features


def get_recipient_features(recipient_ein: str) -> Optional[dict]:
    """
    Get/compute recipient features from database.

    Note: This excludes r_total_grants, r_total_funders, etc. per ablation model.

    Args:
        recipient_ein: Recipient EIN

    Returns:
        Dict with all r_* features, or None if not found
    """
    query = """
    SELECT
        ein,
        state,
        ntee_broad,
        size_bucket,
        assets::float as r_assets,
        total_revenue::float as r_total_revenue,
        COALESCE(employee_count::float, 20) as r_employee_count,
        COALESCE(mission_length::float, 150) as r_mission_length,
        CASE WHEN has_mission_embedding THEN 1.0 ELSE 0.0 END as r_has_embedding,
        COALESCE(avg_grant_received::float, 10000) as r_avg_grant
    FROM f990_2025.calc_recipient_features
    WHERE ein = %(ein)s
    """

    df = query_df(query, {'ein': recipient_ein})

    if df.empty:
        # Try nonprofit_returns as fallback
        return get_recipient_features_fallback(recipient_ein)

    row = df.iloc[0]
    features = {}

    # Core numeric features
    features['r_assets'] = row.get('r_assets', 0) or 0
    features['r_total_revenue'] = row.get('r_total_revenue', 0) or 0
    features['r_employee_count'] = row.get('r_employee_count', 20) or 20
    features['r_mission_length'] = row.get('r_mission_length', 150) or 150
    features['r_has_embedding'] = row.get('r_has_embedding', 0) or 0
    features['r_avg_grant'] = row.get('r_avg_grant', 10000) or 10000

    # State one-hot features
    recipient_state = row.get('state', '') or ''
    for state in STATE_CODES:
        features[f'r_state_{state}'] = 1.0 if recipient_state == state else 0.0
    features['r_state_'] = 1.0 if recipient_state not in STATE_CODES else 0.0

    # NTEE one-hot features
    ntee_broad = (row.get('ntee_broad', '') or '')[:1]  # First letter
    for ntee in NTEE_CODES:
        if ntee == '':
            features['r_ntee_'] = 1.0 if not ntee_broad else 0.0
        else:
            features[f'r_ntee_{ntee}'] = 1.0 if ntee_broad == ntee else 0.0

    # Size bucket one-hot features
    size = (row.get('size_bucket', '') or '').upper()
    for bucket in SIZE_BUCKETS:
        if bucket == '':
            features['r_size_'] = 1.0 if not size else 0.0
        else:
            features[f'r_size_{bucket}'] = 1.0 if size == bucket else 0.0

    # Store state for match feature calculation
    features['_state'] = recipient_state

    # Apply imputation
    for key, value in features.items():
        if pd.isna(value) and key in IMPUTATION_VALUES:
            features[key] = IMPUTATION_VALUES[key]
        elif pd.isna(value):
            features[key] = 0.0

    return features


def get_recipient_features_fallback(recipient_ein: str) -> Optional[dict]:
    """Fallback to nonprofit_returns if not in calc_recipient_features."""
    query = """
    SELECT
        ein,
        state,
        ntee_code,
        total_revenue::float as r_total_revenue,
        total_assets::float as r_assets,
        COALESCE(employee_count::float, 20) as r_employee_count,
        COALESCE(LENGTH(mission_description)::float, 150) as r_mission_length
    FROM f990_2025.nonprofit_returns
    WHERE ein = %(ein)s
    ORDER BY tax_year DESC
    LIMIT 1
    """

    df = query_df(query, {'ein': recipient_ein})

    if df.empty:
        return None

    row = df.iloc[0]
    features = {}

    # Core numeric features with defaults
    features['r_assets'] = row.get('r_assets', 0) or 0
    features['r_total_revenue'] = row.get('r_total_revenue', 0) or 0
    features['r_employee_count'] = row.get('r_employee_count', 20) or 20
    features['r_mission_length'] = row.get('r_mission_length', 150) or 150
    features['r_has_embedding'] = 0.0  # Unknown
    features['r_avg_grant'] = 10000  # Default

    # State one-hot
    recipient_state = row.get('state', '') or ''
    for state in STATE_CODES:
        features[f'r_state_{state}'] = 1.0 if recipient_state == state else 0.0
    features['r_state_'] = 1.0 if recipient_state not in STATE_CODES else 0.0

    # NTEE one-hot
    ntee_code = (row.get('ntee_code', '') or '')[:1]
    for ntee in NTEE_CODES:
        if ntee == '':
            features['r_ntee_'] = 1.0 if not ntee_code else 0.0
        else:
            features[f'r_ntee_{ntee}'] = 1.0 if ntee_code == ntee else 0.0

    # Size bucket - calculate from assets
    assets = features['r_assets']
    if assets < 500000:
        size = 'TINY'
    elif assets < 2000000:
        size = 'SMALL'
    elif assets < 10000000:
        size = 'MEDIUM'
    elif assets < 100000000:
        size = 'LARGE'
    else:
        size = 'LARGE'

    for bucket in SIZE_BUCKETS:
        if bucket == '':
            features['r_size_'] = 0.0
        else:
            features[f'r_size_{bucket}'] = 1.0 if size == bucket else 0.0

    features['_state'] = recipient_state

    return features


def compute_match_features(foundation_features: dict, recipient_features: dict) -> dict:
    """
    Compute match features between foundation and recipient.

    Args:
        foundation_features: Dict from get_foundation_features()
        recipient_features: Dict from get_recipient_features()

    Returns:
        Dict with match_* features
    """
    f_state = foundation_features.get('_state', '')
    r_state = recipient_features.get('_state', '')

    return {
        'match_same_state': 1.0 if f_state and r_state and f_state == r_state else 0.0
    }


def calculate_features(foundation_ein: str, recipient_ein: str) -> Optional[dict]:
    """
    Calculate all features for a foundation-recipient pair.

    Combines foundation, recipient, and match features.
    Handles missing values using imputation.

    Args:
        foundation_ein: Foundation EIN
        recipient_ein: Recipient EIN

    Returns:
        Dict with all 59 features, or None if either party not found
    """
    # Get foundation features
    f_features = get_foundation_features(foundation_ein)
    if f_features is None:
        return None

    # Get recipient features
    r_features = get_recipient_features(recipient_ein)
    if r_features is None:
        return None

    # Compute match features
    m_features = compute_match_features(f_features, r_features)

    # Combine all features
    all_features = {}

    # Add foundation features (exclude internal _state)
    for key, value in f_features.items():
        if not key.startswith('_'):
            all_features[key] = value

    # Add recipient features (exclude internal _state)
    for key, value in r_features.items():
        if not key.startswith('_'):
            all_features[key] = value

    # Add match features
    all_features.update(m_features)

    return all_features


def get_all_foundation_features_batch() -> pd.DataFrame:
    """
    Get all foundation features for batch scoring.

    Returns DataFrame with one row per foundation, all f_* features as columns.
    """
    query = """
    SELECT
        ein,
        name,
        state,
        assets::float as f_assets,
        total_giving::float as f_total_giving,
        total_grants_all_time::float as f_total_grants,
        avg_grant_amount::float as f_avg_grant,
        median_grant::float as f_median_grant,
        COALESCE(repeat_rate::float, 0.5) as f_repeat_rate,
        COALESCE(in_state_grant_pct::float, 0.5) as f_in_state_pct,
        COALESCE(states_funded::float, 1) as f_states_funded,
        COALESCE(sectors_funded::float, 1) as f_sectors_funded,
        COALESCE(openness_score::float, 0.5) as f_openness_score,
        CASE WHEN accepts_applications THEN 1.0 ELSE 0.0 END as f_accepts_apps,
        COALESCE(payout_rate::float, 0.05) as f_payout_rate,
        COALESCE(officer_count::float, 4) as f_officer_count,
        CASE WHEN has_paid_staff THEN 1.0 ELSE 0.0 END as f_has_paid_staff,
        COALESCE(years_active::float, 5) as f_years_active,
        COALESCE(foundation_age::float, 6) as f_foundation_age,
        COALESCE(grant_amount_cv::float, 3) as f_grant_cv,
        COALESCE(primary_sector_pct::float, 0.3) as f_primary_sector_pct
    FROM f990_2025.calc_foundation_features
    WHERE has_grant_history = TRUE
    """

    df = query_df(query)

    # Add state one-hot columns
    for state in STATE_CODES:
        df[f'f_state_{state}'] = (df['state'] == state).astype(float)

    # Fill NaN with imputation values
    for col in df.columns:
        if col in IMPUTATION_VALUES:
            df[col] = df[col].fillna(IMPUTATION_VALUES[col])
        elif df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)

    return df
