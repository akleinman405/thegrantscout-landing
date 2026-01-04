#!/usr/bin/env python3
"""
02b_grant_type_filter.py - Post-scoring filter to boost foundations based on grant type alignment

This filter addresses the issue where the LASSO model scores large national foundations
highest regardless of whether they fund the specific grant type the client needs.

For clients with capital/facility needs, this boosts foundations that have history of
funding capital/building/facility projects.

Usage:
    python scripts/02b_grant_type_filter.py --client "Ka Ulukoa"
"""
import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils import query_df, get_run_dir, get_latest_run_dir, CONFIG_DIR, LOGS_DIR


# Grant type to keyword mapping
GRANT_TYPE_KEYWORDS = {
    'capital_facility': ['facility', 'building', 'construction', 'capital', 'equipment', 'renovation', 'land', 'property'],
    'capital_housing': ['housing', 'affordable housing', 'senior housing', 'multifamily', 'construction', 'development', 'building'],
    'program_athletics': ['athletics', 'sports', 'youth athletics', 'equipment', 'fields', 'gymnasium'],
    'program_disability': ['disability', 'special needs', 'vocational', 'employment', 'training'],
    'program': ['education', 'healthcare', 'patient safety', 'training', 'fellowship'],
}


def get_foundation_grant_type_score(ein: str, keywords: list) -> dict:
    """
    Calculate how many grants from this foundation match the desired keywords.
    Returns dict with total_grants, matching_grants, and match_pct.
    """
    if not keywords:
        return {'total_grants': 0, 'matching_grants': 0, 'match_pct': 0.0}

    # Build the SQL pattern
    pattern = '|'.join(keywords)

    query = """
    SELECT
        COUNT(*) as total_grants,
        SUM(CASE WHEN LOWER(purpose_text) SIMILAR TO %(pattern)s THEN 1 ELSE 0 END) as matching_grants
    FROM f990_2025.fact_grants
    WHERE foundation_ein = %(ein)s
    """

    df = query_df(query, {'ein': str(ein), 'pattern': f'%({pattern})%'})

    if df.empty:
        return {'total_grants': 0, 'matching_grants': 0, 'match_pct': 0.0}

    total = int(df['total_grants'].iloc[0] or 0)
    matching = int(df['matching_grants'].iloc[0] or 0)
    match_pct = (matching / total * 100) if total > 0 else 0.0

    return {
        'total_grants': total,
        'matching_grants': matching,
        'match_pct': match_pct
    }


def get_state_giving_history(ein: str, state: str) -> dict:
    """Check if foundation has given to organizations in the client's state."""
    query = """
    SELECT
        COUNT(*) as total_grants,
        SUM(CASE WHEN recipient_state = %(state)s THEN 1 ELSE 0 END) as state_grants
    FROM f990_2025.fact_grants
    WHERE foundation_ein = %(ein)s
    """

    df = query_df(query, {'ein': str(ein), 'state': state})

    if df.empty:
        return {'total_grants': 0, 'state_grants': 0, 'state_pct': 0.0}

    total = int(df['total_grants'].iloc[0] or 0)
    state_grants = int(df['state_grants'].iloc[0] or 0)
    state_pct = (state_grants / total * 100) if total > 0 else 0.0

    return {
        'total_grants': total,
        'state_grants': state_grants,
        'state_pct': state_pct
    }


def calculate_adjusted_score(row: pd.Series, grant_type_info: dict, state_info: dict,
                            grant_type_weight: float = 0.3, state_weight: float = 0.2) -> float:
    """
    Calculate adjusted score combining original match score with grant type and state alignment.

    Formula:
    adjusted_score = original_score * (1 - grant_type_weight - state_weight)
                   + grant_type_match_pct * grant_type_weight
                   + state_match_pct * state_weight
    """
    original_score = row['match_score']

    # Normalize grant type match (cap at 20% match = 100 points)
    grant_type_score = min(grant_type_info['match_pct'] * 5, 100)  # 20% match = 100

    # Normalize state match (cap at 10% in-state = 100 points)
    state_score = min(state_info['state_pct'] * 10, 100)  # 10% in-state = 100

    # Calculate weighted average
    adjusted = (original_score * (1 - grant_type_weight - state_weight)
               + grant_type_score * grant_type_weight
               + state_score * state_weight)

    return round(adjusted, 1)


def main():
    parser = argparse.ArgumentParser(description='Apply grant type filter to scored foundations')
    parser.add_argument('--client', type=str, required=True, help='Client name or short name')
    parser.add_argument('--top-k', type=int, default=50, help='Number of foundations to output')
    parser.add_argument('--date', type=str, help='Run date (YYYY-MM-DD)')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Find run directory
    run_date = date.fromisoformat(args.date) if args.date else date.today()
    run_dir = get_run_dir(args.client.replace(' ', '_'), run_date)
    if not run_dir.exists():
        run_dir = get_latest_run_dir(args.client.replace(' ', '_'))

    if not run_dir or not (run_dir / '02_scored_foundations.csv').exists():
        print(f"ERROR: No scored foundations found for {args.client}")
        sys.exit(1)

    # Load client data
    client_file = run_dir / '01_client.json'
    with open(client_file) as f:
        client = json.load(f)

    grant_type = client.get('grant_type_preference', 'program_general')
    keywords = client.get('grant_type_keywords', GRANT_TYPE_KEYWORDS.get(grant_type, []))
    client_state = client.get('state', '')

    logger.info(f"Client: {client['organization_name']}")
    logger.info(f"Grant type: {grant_type}")
    logger.info(f"Keywords: {keywords}")
    logger.info(f"State: {client_state}")

    # Load scored foundations
    scored_df = pd.read_csv(run_dir / '02_scored_foundations.csv')
    logger.info(f"Loaded {len(scored_df)} scored foundations")

    # Skip if grant type is generic (program_general)
    if grant_type in ['program_general', 'program']:
        logger.info("Generic grant type - skipping filter, using original scores")
        scored_df.to_csv(run_dir / '02b_filtered_foundations.csv', index=False)
        return

    # Calculate adjusted scores
    results = []
    for idx, row in scored_df.iterrows():
        ein = str(row['foundation_ein'])  # Ensure EIN is string for DB queries

        # Get grant type alignment
        grant_type_info = get_foundation_grant_type_score(ein, keywords)

        # Get state alignment
        state_info = get_state_giving_history(ein, client_state) if client_state else {'state_pct': 0}

        # Calculate adjusted score
        adjusted_score = calculate_adjusted_score(row, grant_type_info, state_info)

        results.append({
            **row.to_dict(),
            'original_score': row['match_score'],
            'adjusted_score': adjusted_score,
            'grant_type_match_pct': grant_type_info['match_pct'],
            'grant_type_grants': grant_type_info['matching_grants'],
            'state_match_pct': state_info.get('state_pct', 0),
        })

    # Create DataFrame and sort by adjusted score
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values('adjusted_score', ascending=False).head(args.top_k)
    result_df['adjusted_rank'] = range(1, len(result_df) + 1)

    # Save results
    output_file = run_dir / '02b_filtered_foundations.csv'
    result_df.to_csv(output_file, index=False)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Grant Type Filter Applied")
    print(f"{'='*60}")
    print(f"Client: {client['organization_name']}")
    print(f"Grant type: {grant_type}")
    print(f"\nTop 10 after filtering:")
    for _, row in result_df.head(10).iterrows():
        gt_match = f"GT:{row['grant_type_match_pct']:.1f}%" if row['grant_type_match_pct'] > 0 else ""
        state_match = f"ST:{row['state_match_pct']:.1f}%" if row['state_match_pct'] > 0 else ""
        boost_info = f"[{gt_match} {state_match}]".strip() if gt_match or state_match else ""
        print(f"  {int(row['adjusted_rank'])}. {row['foundation_name'][:40]} - {row['adjusted_score']:.1f}% {boost_info}")

    print(f"\nOutput: {output_file}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
