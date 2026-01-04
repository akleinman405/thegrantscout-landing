#!/usr/bin/env python3
"""
Script 03: Check Enrichment Status

Checks which foundations have cached enrichment data in the database,
identifies gaps needing research, and flags stale data for verification.

Usage:
    python scripts/03_check_enrichment.py --client "PSMF"
    python scripts/03_check_enrichment.py --client "PSMF" --top 20
    python scripts/03_check_enrichment.py --client "PSMF" --full-refresh-days 90 --verify-days 30
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.paths import get_run_dir, load_client_registry, setup_logging

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "thegrantscout",
    "user": "postgres",
    "password": "kmalec21"
}


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG)


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(data, path: Path):
    """Save data to JSON file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get_enrichment_status(
    ein: str,
    conn,
    full_refresh_days: int = 90,
    verify_days: int = 30
) -> Tuple[str, Optional[dict]]:
    """
    Check enrichment status for a foundation.

    Returns: (status, enrichment_data)
        status: 'READY', 'NEEDS_FULL_ENRICHMENT', 'NEEDS_VERIFICATION'
    """
    now = datetime.now()

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT *
            FROM f990_2025.foundation_enrichment
            WHERE ein = %s
        """, (ein,))
        row = cur.fetchone()

    if not row:
        return "NEEDS_FULL_ENRICHMENT", None

    enrichment = dict(row)
    last_enriched = enrichment.get("last_enriched")
    last_verified = enrichment.get("last_verified")

    # Check if full enrichment is stale
    if last_enriched:
        days_since_enrichment = (now - last_enriched).days
        if days_since_enrichment > full_refresh_days:
            return "NEEDS_FULL_ENRICHMENT", enrichment
    else:
        return "NEEDS_FULL_ENRICHMENT", enrichment

    # Check if verification is stale
    if last_verified:
        days_since_verification = (now - last_verified).days
        if days_since_verification > verify_days:
            return "NEEDS_VERIFICATION", enrichment
    else:
        # Has enrichment but never verified - needs verification
        return "NEEDS_VERIFICATION", enrichment

    return "READY", enrichment


def get_foundation_website(ein: str, conn) -> Optional[str]:
    """Try to find foundation website from database."""
    with conn.cursor() as cur:
        # Check pf_returns for website
        cur.execute("""
            SELECT website_url
            FROM f990_2025.pf_returns
            WHERE ein = %s
            AND website_url IS NOT NULL
            AND website_url NOT IN ('', 'N/A', 'NONE', '0')
            ORDER BY tax_year DESC
            LIMIT 1
        """, (ein,))
        row = cur.fetchone()
        if row and row[0]:
            website = row[0]
            if not website.startswith("http"):
                website = "https://" + website
            return website
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Check enrichment status for scored foundations"
    )
    parser.add_argument("--client", required=True, help="Client name or short_name")
    parser.add_argument("--top", type=int, default=20, help="Number of top foundations to check")
    parser.add_argument(
        "--full-refresh-days", type=int, default=90,
        help="Days before requiring full re-enrichment"
    )
    parser.add_argument(
        "--verify-days", type=int, default=30,
        help="Days before requiring verification"
    )
    parser.add_argument(
        "--date", default=date.today().isoformat(),
        help="Run date (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    # Find client
    registry = load_client_registry()
    client_entry = None
    for c in registry.get("clients", []):
        if (c["name"].lower() == args.client.lower() or
            c.get("short_name", "").lower() == args.client.lower()):
            client_entry = c
            break

    if not client_entry:
        print(f"ERROR: Client '{args.client}' not found in registry")
        sys.exit(1)

    client_name = client_entry["name"].replace(" ", "_")

    # Set up logging
    logger = setup_logging(client_name, "03_check_enrichment")
    logger.info(f"[03_check_enrichment] Starting for {client_entry['name']}")

    # Find run directory
    run_dir = get_run_dir(client_name, args.date)
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)

    # Load scored foundations
    scores_file = run_dir / "02_scored_foundations.csv"
    if not scores_file.exists():
        print(f"ERROR: Scores file not found: {scores_file}")
        sys.exit(1)

    scores_df = pd.read_csv(scores_file, dtype={"foundation_ein": str})

    # Get top N foundations
    top_foundations = scores_df.head(args.top)
    logger.info(f"Checking enrichment for top {len(top_foundations)} foundations")

    print(f"\nChecking enrichment status...")
    print(f"  Client: {client_entry['name']}")
    print(f"  Foundations to check: {len(top_foundations)}")
    print(f"  Full refresh threshold: {args.full_refresh_days} days")
    print(f"  Verification threshold: {args.verify_days} days")
    print("=" * 70)

    # Check each foundation
    conn = get_db_connection()
    results = {
        "client": client_entry["name"],
        "check_date": datetime.now().isoformat(),
        "thresholds": {
            "full_refresh_days": args.full_refresh_days,
            "verify_days": args.verify_days
        },
        "summary": {
            "total": len(top_foundations),
            "ready": 0,
            "needs_full_enrichment": 0,
            "needs_verification": 0
        },
        "foundations": []
    }

    status_counts = {"READY": 0, "NEEDS_FULL_ENRICHMENT": 0, "NEEDS_VERIFICATION": 0}

    for _, row in top_foundations.iterrows():
        ein = str(row["foundation_ein"])
        name = row["foundation_name"][:45]

        status, enrichment = get_enrichment_status(
            ein, conn,
            full_refresh_days=args.full_refresh_days,
            verify_days=args.verify_days
        )

        status_counts[status] += 1

        # Get website for foundations needing enrichment
        website = None
        if status in ["NEEDS_FULL_ENRICHMENT", "NEEDS_VERIFICATION"]:
            website = get_foundation_website(ein, conn)

        foundation_result = {
            "ein": ein,
            "name": row["foundation_name"],
            "state": row.get("foundation_state", ""),
            "match_score": float(row["match_score"]),
            "status": status,
            "website": website,
            "enrichment": enrichment
        }

        results["foundations"].append(foundation_result)

        # Log result
        status_icon = {"READY": "✅", "NEEDS_FULL_ENRICHMENT": "🔴", "NEEDS_VERIFICATION": "🟡"}
        logger.info(f"{status_icon[status]} {name}: {status}")
        print(f"  {status_icon[status]} {name}")
        print(f"      Status: {status}")
        if website:
            print(f"      Website: {website}")
        if enrichment and enrichment.get("last_enriched"):
            days_ago = (datetime.now() - enrichment["last_enriched"]).days
            print(f"      Last enriched: {days_ago} days ago")

    conn.close()

    # Update summary
    results["summary"]["ready"] = status_counts["READY"]
    results["summary"]["needs_full_enrichment"] = status_counts["NEEDS_FULL_ENRICHMENT"]
    results["summary"]["needs_verification"] = status_counts["NEEDS_VERIFICATION"]

    # Save output
    output_file = run_dir / "03_enrichment_status.json"
    save_json(results, output_file)

    logger.info(f"[03_check_enrichment] Saved to {output_file}")

    # Summary
    print("=" * 70)
    print("Enrichment Status Summary")
    print("=" * 70)
    print(f"  ✅ READY:                 {status_counts['READY']}")
    print(f"  🔴 NEEDS_FULL_ENRICHMENT: {status_counts['NEEDS_FULL_ENRICHMENT']}")
    print(f"  🟡 NEEDS_VERIFICATION:    {status_counts['NEEDS_VERIFICATION']}")
    print("=" * 70)

    # Guidance
    if status_counts["NEEDS_FULL_ENRICHMENT"] > 0:
        print(f"\n🔴 {status_counts['NEEDS_FULL_ENRICHMENT']} foundations need web research:")
        for f in results["foundations"]:
            if f["status"] == "NEEDS_FULL_ENRICHMENT":
                print(f"   - {f['name'][:40]}")
                if f["website"]:
                    print(f"     Website: {f['website']}")
        print("\nNext: Research these foundations and run 03b_store_enrichment.py")

    elif status_counts["NEEDS_VERIFICATION"] > 0:
        print(f"\n🟡 {status_counts['NEEDS_VERIFICATION']} foundations need verification:")
        for f in results["foundations"]:
            if f["status"] == "NEEDS_VERIFICATION":
                print(f"   - {f['name'][:40]}")
        print("\nNext: Verify contact info and deadlines, then update via 03b_store_enrichment.py")

    else:
        print("\n✅ All foundations have fresh enrichment data!")
        print("Next: Run 04_filter_viable.py to calculate viability tiers")

    print(f"\nOutput: {output_file}")


if __name__ == "__main__":
    main()
