#!/usr/bin/env python3
"""
PY_2025-01-03_v6_export_training_fixed.py
Export V6 training data with semantic similarity - FIXED VERSION

FIXES from statistical review:
1. REMOVED: f_funded_new_recently (temporal leakage)
2. REMOVED: f_first_time_rate (99.8% correlated with openness_score)
3. REMOVED: f_one_time_rate (86% correlated with openness_score)
4. CHANGED: Use 'split' column (random 80/10/10) instead of tax_year

Usage:
    python3 scripts/python/PY_2025-01-03_v6_export_training_fixed.py

Output:
    outputs/v6/train.csv
    outputs/v6/validation.csv
    outputs/v6/test.csv
"""

import os
import sys
import math
import numpy as np
from pathlib import Path
from datetime import datetime

import pandas as pd
import psycopg2

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'thegrantscout',
    'user': 'postgres',
    'password': 'kmalec21'
}

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'outputs' / 'v6'


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}")


def connect_db():
    """Connect to PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)


def export_training_data():
    """Export training data from database."""
    log("Connecting to database...")
    conn = connect_db()

    log("Querying training_data_v6...")

    query = """
    SELECT
        foundation_ein,
        recipient_ein,
        tax_year,
        label,
        sample_type,
        split,

        -- Foundation features
        f_assets,
        f_total_grants,
        f_avg_grant,
        f_median_grant,
        f_repeat_rate,
        f_openness_score,
        f_in_state_pct,
        f_states_funded,
        f_sectors_funded,
        f_years_active,
        f_foundation_age,
        f_payout_rate,
        f_officer_count,
        f_has_paid_staff,
        f_grant_cv,
        f_primary_sector_pct,
        f_state,
        f_pct_capital,
        f_pct_operating,
        f_pct_program,
        f_sector_hhi,
        f_is_accessible,
        f_is_small,
        f_is_growing,
        f_is_declining,
        f_is_recently_active,

        -- Recipient features (V6: reduced set)
        r_total_revenue,
        r_state,
        r_ntee_broad,
        r_org_age,
        r_is_emerging,

        -- Match features
        match_same_state,
        match_sector_pct,
        match_state_pct,
        match_capital_pct,
        match_same_region,
        match_same_division,
        f_has_embedding

    FROM f990_2025.training_data_v6
    """

    df = pd.read_sql(query, conn)
    conn.close()

    log(f"Loaded {len(df):,} rows")

    return df


def load_foundation_embeddings():
    """Load foundation average embeddings for semantic similarity."""
    log("Loading foundation embeddings...")
    conn = connect_db()

    query = """
    SELECT foundation_ein, avg_embedding
    FROM f990_2025.calc_foundation_avg_embedding
    WHERE avg_embedding IS NOT NULL
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # Convert to dict for fast lookup
    embeddings = {}
    for _, row in df.iterrows():
        embeddings[row['foundation_ein']] = np.array(row['avg_embedding'])

    log(f"Loaded {len(embeddings)} foundation embeddings")
    return embeddings


def load_sector_avg_embeddings():
    """Compute average embedding per NTEE sector (as proxy for recipient embedding).

    PostgreSQL can't AVG arrays directly, so we load all embeddings and compute in Python.
    """
    log("Computing sector average embeddings...")
    conn = connect_db()

    # Get foundation-to-sector mapping
    # Note: sector_pct is stored as decimal (0-1), not percentage (0-100)
    query = """
    WITH foundation_sectors AS (
        SELECT DISTINCT foundation_ein, ntee_broad
        FROM f990_2025.stg_foundation_sector_dist
        WHERE sector_pct >= 0.20
    )
    SELECT
        fs.ntee_broad,
        fs.foundation_ein,
        fae.avg_embedding
    FROM foundation_sectors fs
    JOIN f990_2025.calc_foundation_avg_embedding fae ON fs.foundation_ein = fae.foundation_ein
    WHERE fae.avg_embedding IS NOT NULL
    """

    try:
        df = pd.read_sql(query, conn)
        conn.close()

        # Group by sector and compute mean embedding in Python
        sector_embeddings = {}
        for ntee in df['ntee_broad'].unique():
            sector_df = df[df['ntee_broad'] == ntee]
            embeddings_list = [np.array(e) for e in sector_df['avg_embedding'].values]
            if embeddings_list:
                # Stack and take mean
                stacked = np.vstack(embeddings_list)
                avg_emb = np.mean(stacked, axis=0)
                # Normalize to unit vector
                norm = np.linalg.norm(avg_emb)
                if norm > 0:
                    avg_emb = avg_emb / norm
                sector_embeddings[ntee] = avg_emb

        log(f"Computed {len(sector_embeddings)} sector average embeddings")
        return sector_embeddings

    except Exception as e:
        log(f"Warning: Could not load sector embeddings: {e}")
        conn.close()
        return {}


def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    if a is None or b is None:
        return 0.0
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def add_derived_features(df, foundation_embeddings, sector_embeddings):
    """Add log-transformed, interaction, and semantic features."""
    log("Adding derived features...")

    # =========================================================================
    # Log-transformed features (foundation)
    # =========================================================================
    df['f_log_assets'] = df['f_assets'].apply(lambda x: math.log1p(max(x or 0, 0)))
    df['f_log_total_grants'] = df['f_total_grants'].apply(lambda x: math.log1p(max(x or 0, 0)))
    df['f_log_avg_grant'] = df['f_avg_grant'].apply(lambda x: math.log1p(max(x or 0, 0)))
    df['f_log_median_grant'] = df['f_median_grant'].apply(lambda x: math.log1p(max(x or 0, 0)))

    # Grants per year
    df['f_grants_per_year'] = df['f_total_grants'] / df['f_years_active'].replace(0, 1)
    df['f_log_grants_per_year'] = df['f_grants_per_year'].apply(lambda x: math.log1p(max(x or 0, 0)))

    # =========================================================================
    # Log-transformed features (recipient) - V6: only revenue
    # =========================================================================
    df['r_log_total_revenue'] = df['r_total_revenue'].apply(lambda x: math.log1p(max(x or 0, 0)))

    # Log org age
    df['r_log_org_age'] = df['r_org_age'].apply(lambda x: math.log1p(max(x or 0, 0)))

    # =========================================================================
    # Interaction terms
    # =========================================================================
    df['match_state_x_geo_conc'] = df['match_state_pct'] * (1 - df['f_in_state_pct'].fillna(0.5))
    df['match_sector_x_sector_hhi'] = df['match_sector_pct'] * df['f_sector_hhi'].fillna(0.05)

    # =========================================================================
    # Grant size alignment (using median grant as proxy for "typical ask")
    # =========================================================================
    df['match_grant_size_ratio'] = df.apply(
        lambda row: math.log(max(row['r_total_revenue'] or 1, 1) /
                            max(row['f_median_grant'] or 10000, 1))
        if row['r_total_revenue'] and row['f_median_grant'] else 0,
        axis=1
    )

    # Is recipient budget in "reasonable" range for this foundation's grants?
    df['match_budget_in_range'] = df.apply(
        lambda row: 1.0 if (row['r_total_revenue'] and row['f_avg_grant'] and
                          10 <= (row['r_total_revenue'] / max(row['f_avg_grant'], 1)) <= 100)
                    else 0.5 if (row['r_total_revenue'] and row['f_avg_grant'] and
                                5 <= (row['r_total_revenue'] / max(row['f_avg_grant'], 1)) <= 200)
                    else 0.0,
        axis=1
    )

    # =========================================================================
    # Semantic similarity (foundation embedding vs sector average)
    # =========================================================================
    log("Computing semantic similarity...")

    def get_semantic_sim(row):
        fein = row['foundation_ein']
        ntee = row['r_ntee_broad']

        if fein not in foundation_embeddings:
            return 0.0
        if ntee not in sector_embeddings:
            return 0.0

        return cosine_similarity(
            foundation_embeddings[fein],
            sector_embeddings[ntee]
        )

    if foundation_embeddings and sector_embeddings:
        df['match_semantic_similarity'] = df.apply(get_semantic_sim, axis=1)
    else:
        log("Warning: No embeddings available, setting semantic similarity to 0")
        df['match_semantic_similarity'] = 0.0

    log(f"Semantic similarity stats: mean={df['match_semantic_similarity'].mean():.3f}, "
        f"std={df['match_semantic_similarity'].std():.3f}")

    return df


def create_state_dummies(df, column, prefix, top_n=10):
    """Create one-hot encoding for top N states."""
    top_states = df[column].value_counts().head(top_n).index.tolist()

    for state in top_states:
        df[f'{prefix}_{state}'] = (df[column] == state).astype(int)

    # Other states
    df[f'{prefix}_OTHER'] = (~df[column].isin(top_states)).astype(int)

    return df


def create_ntee_dummies(df, column='r_ntee_broad'):
    """Create one-hot encoding for NTEE codes."""
    ntee_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    for code in ntee_codes:
        df[f'r_ntee_{code}'] = (df[column] == code).astype(int)

    df['r_ntee_UNKNOWN'] = (df[column].isna() | (df[column] == '')).astype(int)

    return df


def impute_missing(df):
    """Fill missing values with reasonable defaults."""
    log("Imputing missing values...")

    # Foundation features
    df['f_assets'] = df['f_assets'].fillna(df['f_assets'].median())
    df['f_total_grants'] = df['f_total_grants'].fillna(0)
    df['f_avg_grant'] = df['f_avg_grant'].fillna(df['f_avg_grant'].median())
    df['f_median_grant'] = df['f_median_grant'].fillna(df['f_median_grant'].median())
    df['f_repeat_rate'] = df['f_repeat_rate'].fillna(0.5)
    df['f_openness_score'] = df['f_openness_score'].fillna(0.5)
    df['f_in_state_pct'] = df['f_in_state_pct'].fillna(0.5)
    df['f_states_funded'] = df['f_states_funded'].fillna(1)
    df['f_sectors_funded'] = df['f_sectors_funded'].fillna(1)
    df['f_years_active'] = df['f_years_active'].fillna(5)
    df['f_foundation_age'] = df['f_foundation_age'].fillna(10)
    df['f_payout_rate'] = df['f_payout_rate'].fillna(0.05)
    df['f_officer_count'] = df['f_officer_count'].fillna(4)
    df['f_has_paid_staff'] = df['f_has_paid_staff'].fillna(0)
    df['f_grant_cv'] = df['f_grant_cv'].fillna(3)
    df['f_primary_sector_pct'] = df['f_primary_sector_pct'].fillna(0.3)
    df['f_sector_hhi'] = df['f_sector_hhi'].fillna(0.05)
    df['f_is_accessible'] = df['f_is_accessible'].fillna(0)
    df['f_is_small'] = df['f_is_small'].fillna(0)
    df['f_is_growing'] = df['f_is_growing'].fillna(0)
    df['f_is_declining'] = df['f_is_declining'].fillna(0)
    df['f_is_recently_active'] = df['f_is_recently_active'].fillna(0)

    # Recipient features (V6: simplified)
    df['r_total_revenue'] = df['r_total_revenue'].fillna(df['r_total_revenue'].median())
    df['r_org_age'] = df['r_org_age'].fillna(10)
    df['r_is_emerging'] = df['r_is_emerging'].fillna(0)

    # Match features
    df['match_sector_pct'] = df['match_sector_pct'].fillna(0)
    df['match_state_pct'] = df['match_state_pct'].fillna(0)
    df['match_same_region'] = df['match_same_region'].fillna(0)
    df['match_same_division'] = df['match_same_division'].fillna(0)
    df['match_semantic_similarity'] = df['match_semantic_similarity'].fillna(0)

    # Derived features (created in add_derived_features)
    for col in ['f_log_assets', 'f_log_total_grants', 'f_log_avg_grant', 'f_log_median_grant',
                'f_grants_per_year', 'f_log_grants_per_year', 'r_log_total_revenue', 'r_log_org_age',
                'match_state_x_geo_conc', 'match_sector_x_sector_hhi', 'match_grant_size_ratio',
                'match_budget_in_range']:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    return df


def main():
    """Main export pipeline."""
    print("=" * 60)
    print("V6 Training Data Export (FIXED)")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load foundation embeddings
    try:
        foundation_embeddings = load_foundation_embeddings()
    except Exception as e:
        log(f"Warning: Could not load foundation embeddings: {e}")
        foundation_embeddings = {}

    # Load sector average embeddings
    try:
        sector_embeddings = load_sector_avg_embeddings()
    except Exception as e:
        log(f"Warning: Could not load sector embeddings: {e}")
        sector_embeddings = {}

    # Export from database
    df = export_training_data()

    # Add derived features FIRST (creates match_semantic_similarity)
    df = add_derived_features(df, foundation_embeddings, sector_embeddings)

    # Then impute missing values (including match_semantic_similarity)
    df = impute_missing(df)

    # Create categorical dummies
    df = create_state_dummies(df, 'f_state', 'f_state')
    df = create_state_dummies(df, 'r_state', 'r_state')
    df = create_ntee_dummies(df)

    # Select features for training (exclude IDs and raw categoricals)
    exclude_cols = ['foundation_ein', 'recipient_ein', 'sample_type', 'split',
                   'f_state', 'r_state', 'r_ntee_broad', 'tax_year']
    feature_cols = [c for c in df.columns if c not in exclude_cols]

    df_features = df[feature_cols + ['split']]  # Keep split for splitting

    log(f"Final dataset: {len(df_features):,} rows, {len(feature_cols)} columns")

    # Split by random 'split' column (not tax_year!)
    train = df_features[df_features['split'] == 'train'].drop('split', axis=1)
    validation = df_features[df_features['split'] == 'validation'].drop('split', axis=1)
    test = df_features[df_features['split'] == 'test'].drop('split', axis=1)

    print(f"\nSplits (Random 80/10/10):")
    print(f"  Train:      {len(train):,} rows ({train['label'].mean()*100:.1f}% positive)")
    print(f"  Validation: {len(validation):,} rows ({validation['label'].mean()*100:.1f}% positive)")
    print(f"  Test:       {len(test):,} rows ({test['label'].mean()*100:.1f}% positive)")

    # Verify both classes in all splits
    for name, split_df in [('Train', train), ('Validation', validation), ('Test', test)]:
        pos = (split_df['label'] == 1).sum()
        neg = (split_df['label'] == 0).sum()
        if pos == 0 or neg == 0:
            log(f"ERROR: {name} split missing a class! Positives: {pos}, Negatives: {neg}")
        else:
            log(f"OK: {name} has both classes (Pos: {pos:,}, Neg: {neg:,})")

    # Save files
    log("Saving CSV files...")

    train.to_csv(OUTPUT_DIR / 'train.csv', index=False)
    validation.to_csv(OUTPUT_DIR / 'validation.csv', index=False)
    test.to_csv(OUTPUT_DIR / 'test.csv', index=False)

    # Save feature list
    feature_list = [c for c in feature_cols if c != 'label']
    with open(OUTPUT_DIR / 'feature_list.txt', 'w') as f:
        for col in feature_list:
            f.write(col + '\n')

    log("Done!")
    print(f"\nOutput files:")
    print(f"  {OUTPUT_DIR / 'train.csv'}")
    print(f"  {OUTPUT_DIR / 'validation.csv'}")
    print(f"  {OUTPUT_DIR / 'test.csv'}")
    print(f"  {OUTPUT_DIR / 'feature_list.txt'}")

    # Print feature comparison to V5
    print("\n" + "=" * 60)
    print("V6 vs V5 Feature Changes:")
    print("=" * 60)
    print("\nREMOVED from V5 (leakage/multicollinearity):")
    print("  - r_total_grants (leakage, +4.18 coefficient)")
    print("  - r_total_funders (leakage)")
    print("  - r_total_funding (leakage)")
    print("  - r_assets (multicollinear)")
    print("  - r_employee_count (multicollinear)")
    print("  - r_size_* dummies (redundant)")

    print("\nREMOVED from V6 draft (statistical review):")
    print("  - f_funded_new_recently (temporal leakage)")
    print("  - f_first_time_rate (99.8% correlated with openness_score)")
    print("  - f_one_time_rate (86% correlated with openness_score)")

    print("\nADDED in V6:")
    print("  - match_semantic_similarity")
    print("  - r_org_age, r_log_org_age")
    print("  - r_is_emerging")
    print("  - f_is_accessible")
    print("  - f_is_small")
    print("  - f_is_growing, f_is_declining")
    print("  - f_is_recently_active")
    print("  - match_same_region, match_same_division")

    print("\nSPLIT CHANGE:")
    print("  - OLD: Temporal (train <=2022, val 2023, test 2024)")
    print("  - NEW: Random 80/10/10 (fixes missing negatives in val/test)")


if __name__ == '__main__':
    main()
