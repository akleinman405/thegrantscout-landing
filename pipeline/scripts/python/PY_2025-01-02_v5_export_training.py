#!/usr/bin/env python3
"""
PY_2025-01-02_v5_export_training.py
Export V5 training data from PostgreSQL to CSV for R training.

Usage:
    python3 scripts/python/PY_2025-01-02_v5_export_training.py

Output:
    outputs/v5/training_data_v5.csv
    outputs/v5/train.csv (2017-2022)
    outputs/v5/validation.csv (2023)
    outputs/v5/test.csv (2024)
"""

import os
import sys
import math
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
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'outputs' / 'v5'


def connect_db():
    """Connect to PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)


def export_training_data():
    """Export training data from database."""
    print(f"[{datetime.now():%H:%M:%S}] Connecting to database...")
    conn = connect_db()

    print(f"[{datetime.now():%H:%M:%S}] Querying training_data_v5...")

    query = """
    SELECT
        foundation_ein,
        recipient_ein,
        tax_year,
        label,
        sample_type,

        -- Foundation features (raw)
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

        -- Recipient features (raw)
        r_total_revenue,
        r_assets,
        r_employee_count,
        r_state,
        r_ntee_broad,
        r_size_bucket,
        r_total_grants,
        r_total_funders,
        r_total_funding,

        -- Match features
        match_same_state,
        match_sector_pct,
        match_state_pct,
        match_capital_pct

    FROM f990_2025.training_data_v5
    """

    df = pd.read_sql(query, conn)
    conn.close()

    print(f"[{datetime.now():%H:%M:%S}] Loaded {len(df):,} rows")

    return df


def add_derived_features(df):
    """Add log-transformed and interaction features."""
    print(f"[{datetime.now():%H:%M:%S}] Adding derived features...")

    # Log-transformed features (foundation)
    df['f_log_assets'] = df['f_assets'].apply(lambda x: math.log1p(max(x or 0, 0)))
    df['f_log_total_grants'] = df['f_total_grants'].apply(lambda x: math.log1p(max(x or 0, 0)))
    df['f_log_avg_grant'] = df['f_avg_grant'].apply(lambda x: math.log1p(max(x or 0, 0)))
    df['f_log_median_grant'] = df['f_median_grant'].apply(lambda x: math.log1p(max(x or 0, 0)))

    # Grants per year
    df['f_grants_per_year'] = df['f_total_grants'] / df['f_years_active'].replace(0, 1)
    df['f_log_grants_per_year'] = df['f_grants_per_year'].apply(lambda x: math.log1p(max(x or 0, 0)))

    # Log-transformed features (recipient)
    df['r_log_total_revenue'] = df['r_total_revenue'].apply(lambda x: math.log1p(max(x or 0, 0)))
    df['r_log_assets'] = df['r_assets'].apply(lambda x: math.log1p(max(x or 0, 0)))

    # Grant size ratio: log(f_median / r_avg_funding)
    df['match_grant_size_ratio'] = df.apply(
        lambda row: math.log(max(row['f_median_grant'] or 1, 1) /
                            max((row['r_total_funding'] / max(row['r_total_grants'], 1)) if row['r_total_grants'] > 0 else 10000, 1))
        if row['f_median_grant'] else 0,
        axis=1
    )

    # Interaction terms (for LASSO)
    df['match_state_x_geo_conc'] = df['match_state_pct'] * (1 - df['f_in_state_pct'].fillna(0.5))
    df['match_sector_x_sector_hhi'] = df['match_sector_pct'] * df['f_sector_hhi'].fillna(0.05)

    # Budget in range: is recipient budget reasonable for this foundation's typical grants?
    df['match_budget_in_range'] = df.apply(
        lambda row: 1.0 if (row['r_total_revenue'] and row['f_avg_grant'] and
                          10 <= (row['r_total_revenue'] / max(row['f_avg_grant'], 1)) <= 100)
                    else 0.5 if (row['r_total_revenue'] and row['f_avg_grant'] and
                                5 <= (row['r_total_revenue'] / max(row['f_avg_grant'], 1)) <= 200)
                    else 0.0,
        axis=1
    )

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


def create_size_dummies(df, column='r_size_bucket'):
    """Create one-hot encoding for size buckets."""
    sizes = ['TINY', 'SMALL', 'MEDIUM', 'LARGE']

    for size in sizes:
        df[f'r_size_{size}'] = (df[column] == size).astype(int)

    df['r_size_UNKNOWN'] = (df[column].isna() | (df[column] == '')).astype(int)

    return df


def impute_missing(df):
    """Fill missing values with reasonable defaults."""
    print(f"[{datetime.now():%H:%M:%S}] Imputing missing values...")

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

    # Recipient features
    df['r_total_revenue'] = df['r_total_revenue'].fillna(df['r_total_revenue'].median())
    df['r_assets'] = df['r_assets'].fillna(0)
    df['r_employee_count'] = df['r_employee_count'].fillna(10)
    df['r_total_grants'] = df['r_total_grants'].fillna(0)
    df['r_total_funders'] = df['r_total_funders'].fillna(0)
    df['r_total_funding'] = df['r_total_funding'].fillna(0)

    # Match features
    df['match_sector_pct'] = df['match_sector_pct'].fillna(0)
    df['match_state_pct'] = df['match_state_pct'].fillna(0)

    return df


def main():
    """Main export pipeline."""
    print("=" * 60)
    print("V5 Training Data Export")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Export from database
    df = export_training_data()

    # Impute missing values
    df = impute_missing(df)

    # Add derived features
    df = add_derived_features(df)

    # Create categorical dummies
    df = create_state_dummies(df, 'f_state', 'f_state')
    df = create_state_dummies(df, 'r_state', 'r_state')
    df = create_ntee_dummies(df)
    df = create_size_dummies(df)

    # Select features for training (exclude IDs and raw categoricals)
    exclude_cols = ['foundation_ein', 'recipient_ein', 'sample_type',
                   'f_state', 'r_state', 'r_ntee_broad', 'r_size_bucket']
    feature_cols = [c for c in df.columns if c not in exclude_cols]

    df_features = df[feature_cols]

    print(f"[{datetime.now():%H:%M:%S}] Final dataset: {len(df_features):,} rows, {len(feature_cols)} columns")

    # Split by year
    train = df_features[df_features['tax_year'] <= 2022]
    validation = df_features[df_features['tax_year'] == 2023]
    test = df_features[df_features['tax_year'] == 2024]

    print(f"\nSplits:")
    print(f"  Train (2017-2022):   {len(train):,} rows ({train['label'].mean()*100:.1f}% positive)")
    print(f"  Validation (2023):   {len(validation):,} rows ({validation['label'].mean()*100:.1f}% positive)")
    print(f"  Test (2024):         {len(test):,} rows ({test['label'].mean()*100:.1f}% positive)")

    # Save files
    print(f"\n[{datetime.now():%H:%M:%S}] Saving CSV files...")

    df_features.to_csv(OUTPUT_DIR / 'training_data_v5.csv', index=False)
    train.to_csv(OUTPUT_DIR / 'train.csv', index=False)
    validation.to_csv(OUTPUT_DIR / 'validation.csv', index=False)
    test.to_csv(OUTPUT_DIR / 'test.csv', index=False)

    # Save feature list
    with open(OUTPUT_DIR / 'feature_list.txt', 'w') as f:
        for col in feature_cols:
            if col not in ['tax_year', 'label']:
                f.write(col + '\n')

    print(f"\n[{datetime.now():%H:%M:%S}] Done!")
    print(f"\nOutput files:")
    print(f"  {OUTPUT_DIR / 'training_data_v5.csv'}")
    print(f"  {OUTPUT_DIR / 'train.csv'}")
    print(f"  {OUTPUT_DIR / 'validation.csv'}")
    print(f"  {OUTPUT_DIR / 'test.csv'}")
    print(f"  {OUTPUT_DIR / 'feature_list.txt'}")


if __name__ == '__main__':
    main()
