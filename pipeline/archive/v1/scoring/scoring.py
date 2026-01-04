"""
Grant scoring module using LASSO logistic regression model.

Scores foundation-recipient pairs to predict match probability.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from config.database import query_df
from .features import (
    calculate_features,
    get_foundation_features,
    get_recipient_features,
    compute_match_features,
    get_all_foundation_features_batch,
    STATE_CODES,
    NTEE_CODES,
    SIZE_BUCKETS
)

# Load model parameters
CONFIG_DIR = Path(__file__).parent.parent / "config"

with open(CONFIG_DIR / "coefficients.json") as f:
    MODEL_CONFIG = json.load(f)

with open(CONFIG_DIR / "scaling.json") as f:
    SCALING_PARAMS = json.load(f)

INTERCEPT = MODEL_CONFIG["intercept"]
COEFFICIENTS = MODEL_CONFIG["coefficients"]


@dataclass
class MatchScore:
    """Represents a foundation match score for a recipient."""
    foundation_ein: str
    foundation_name: str
    match_score: float  # 0-100 score
    match_probability: float  # Raw logistic probability
    match_rank: int
    same_state: bool
    foundation_state: str


def scale_feature(value: float, feature_name: str) -> float:
    """
    Apply z-score scaling to a feature value.

    Args:
        value: Raw feature value
        feature_name: Name of feature for lookup

    Returns:
        Scaled value (z-score normalized)
    """
    if feature_name not in SCALING_PARAMS:
        return value

    params = SCALING_PARAMS[feature_name]
    mean = params.get('mean', 0)
    sd = params.get('sd', 1)

    if sd == 0:
        return 0

    return (value - mean) / sd


def logistic(z: float) -> float:
    """Logistic sigmoid function."""
    if z < -500:
        return 0.0
    if z > 500:
        return 1.0
    return 1 / (1 + np.exp(-z))


class GrantScorer:
    """
    Score foundation-recipient pairs using trained LASSO model.

    The model predicts the probability that a foundation will fund a recipient
    based on 59 features including foundation characteristics, recipient
    characteristics, and match features.
    """

    def __init__(self):
        """Initialize scorer with model parameters."""
        self.intercept = INTERCEPT
        self.coefficients = COEFFICIENTS
        self.scaling = SCALING_PARAMS

    def score_pair(self, foundation_ein: str, recipient_ein: str) -> float:
        """
        Score a single foundation-recipient pair.

        Args:
            foundation_ein: Foundation EIN
            recipient_ein: Recipient EIN

        Returns:
            Match probability (0-1)
        """
        features = calculate_features(foundation_ein, recipient_ein)

        if features is None:
            return 0.0

        return self._compute_probability(features)

    def _compute_probability(self, features: dict) -> float:
        """Compute match probability from features dict."""
        # Scale features and compute linear predictor
        z = self.intercept

        for feature_name, coef in self.coefficients.items():
            if feature_name in features:
                raw_value = features[feature_name]
                scaled_value = scale_feature(raw_value, feature_name)
                z += coef * scaled_value

        return logistic(z)

    def score_nonprofit(
        self,
        recipient_ein: str,
        top_k: int = 50,
        exclude_prior_funders: bool = True,
        min_assets: int = 100000,
        require_grants_to_orgs: bool = True
    ) -> pd.DataFrame:
        """
        Score all eligible foundations for a recipient and return top matches.

        Args:
            recipient_ein: Recipient EIN to score
            top_k: Number of top matches to return
            exclude_prior_funders: If True, exclude foundations that have previously funded this recipient
            min_assets: Minimum foundation assets to consider
            require_grants_to_orgs: If True, only consider foundations that make grants to organizations

        Returns:
            DataFrame with columns: foundation_ein, foundation_name, match_score,
            match_probability, match_rank, same_state, foundation_state
        """
        # Get recipient features
        r_features = get_recipient_features(recipient_ein)
        if r_features is None:
            raise ValueError(f"Recipient not found: {recipient_ein}")

        recipient_state = r_features.get('_state', '')

        # Build exclusion list if needed
        exclusions = set()
        if exclude_prior_funders:
            prior_query = """
            SELECT DISTINCT foundation_ein
            FROM f990_2025.fact_grants
            WHERE recipient_ein = %(ein)s
            """
            prior_df = query_df(prior_query, {'ein': recipient_ein})
            exclusions = set(prior_df['foundation_ein'].tolist())

        # Get all eligible foundations
        foundations = self._get_eligible_foundations(
            min_assets=min_assets,
            require_grants_to_orgs=require_grants_to_orgs,
            exclusions=exclusions
        )

        if foundations.empty:
            return pd.DataFrame(columns=[
                'foundation_ein', 'foundation_name', 'match_score',
                'match_probability', 'match_rank', 'same_state', 'foundation_state'
            ])

        # Score each foundation
        scores = []
        for _, f_row in foundations.iterrows():
            # Build foundation features from row
            f_features = self._row_to_features(f_row)

            # Compute match features
            m_features = compute_match_features(f_features, r_features)

            # Combine all features
            all_features = {}
            for key, value in f_features.items():
                if not key.startswith('_'):
                    all_features[key] = value
            for key, value in r_features.items():
                if not key.startswith('_'):
                    all_features[key] = value
            all_features.update(m_features)

            # Score
            prob = self._compute_probability(all_features)
            same_state = f_features.get('_state', '') == recipient_state

            scores.append({
                'foundation_ein': f_row['ein'],
                'foundation_name': f_row.get('name', ''),
                'match_probability': prob,
                'match_score': round(prob * 100, 1),
                'same_state': same_state,
                'foundation_state': f_features.get('_state', '')
            })

        # Create DataFrame and sort
        result = pd.DataFrame(scores)
        result = result.sort_values('match_score', ascending=False)
        result = result.head(top_k)
        result['match_rank'] = range(1, len(result) + 1)

        return result.reset_index(drop=True)

    def _get_eligible_foundations(
        self,
        min_assets: int = 100000,
        require_grants_to_orgs: bool = True,
        exclusions: set = None
    ) -> pd.DataFrame:
        """Get all foundations eligible for scoring."""
        exclusions = exclusions or set()

        # Use batch function to get all foundation features
        df = get_all_foundation_features_batch()

        # Apply filters
        if min_assets > 0:
            df = df[df['f_assets'] >= min_assets]

        # TODO: Add grants_to_orgs filter if needed

        # Apply exclusions
        if exclusions:
            df = df[~df['ein'].isin(exclusions)]

        return df

    def _row_to_features(self, row: pd.Series) -> dict:
        """Convert DataFrame row to features dict."""
        features = {}

        # Numeric features
        numeric_cols = [
            'f_assets', 'f_total_giving', 'f_total_grants', 'f_avg_grant',
            'f_median_grant', 'f_repeat_rate', 'f_in_state_pct', 'f_states_funded',
            'f_sectors_funded', 'f_openness_score', 'f_accepts_apps', 'f_payout_rate',
            'f_officer_count', 'f_has_paid_staff', 'f_years_active', 'f_foundation_age',
            'f_grant_cv', 'f_primary_sector_pct'
        ]

        for col in numeric_cols:
            if col in row.index:
                features[col] = row[col] if pd.notna(row[col]) else 0.0

        # State one-hot features
        for state in STATE_CODES:
            col = f'f_state_{state}'
            if col in row.index:
                features[col] = row[col]
            else:
                features[col] = 1.0 if row.get('state', '') == state else 0.0

        # Store state for match calculation
        features['_state'] = row.get('state', '')

        return features


# Convenience function
def score_nonprofit(
    recipient_ein: str,
    top_k: int = 50,
    exclude_prior_funders: bool = True
) -> pd.DataFrame:
    """
    Score foundations for a recipient nonprofit.

    Convenience function that creates a GrantScorer instance.

    Args:
        recipient_ein: Recipient EIN
        top_k: Number of top matches to return
        exclude_prior_funders: Whether to exclude prior funders

    Returns:
        DataFrame with top matches
    """
    scorer = GrantScorer()
    return scorer.score_nonprofit(
        recipient_ein=recipient_ein,
        top_k=top_k,
        exclude_prior_funders=exclude_prior_funders
    )
