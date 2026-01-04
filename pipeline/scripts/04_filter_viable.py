#!/usr/bin/env python3
"""
Script 04: Filter Viable Foundations

Reads scored foundations and applies viability filtering using enrichment data
from the database. Calculates viability tiers and adjusted scores.

Viability Tiers:
  - READY: Accepts unsolicited applications, has clear process (multiplier: 0.85-1.0)
  - CONDITIONAL: May accept applications, requires verification (multiplier: 0.5-0.7)
  - WATCH: RFP-only or invitation-only, monitor for opportunities (multiplier: 0.2-0.3)
  - SKIP: Mission mismatch, inactive, or explicitly closed (multiplier: 0.0)

Usage:
    python scripts/04_filter_viable.py --client "PSMF"
    python scripts/04_filter_viable.py --client "PSMF" --top 20
    python scripts/04_filter_viable.py --client "PSMF" --include-watch
"""

import argparse
import json
import sys
from datetime import date, datetime
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


def save_json(data, path: Path):
    """Save data to JSON file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ============================================================================
# Enrichment Retrieval
# ============================================================================

def get_enrichment_from_db(ein: str, conn) -> Optional[dict]:
    """
    Retrieve enrichment data for a foundation from database.

    Returns: enrichment dict or None if not found
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT *
            FROM f990_2025.foundation_enrichment
            WHERE ein = %s
        """, (ein,))
        row = cur.fetchone()

    if row:
        return dict(row)
    return None


def get_foundation_website(ein: str, conn) -> Optional[str]:
    """Try to find foundation website from pf_returns."""
    with conn.cursor() as cur:
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


# ============================================================================
# Viability Calculation
# ============================================================================

def calculate_viability_tier(enrichment: Optional[dict]) -> Tuple[str, float, str]:
    """
    Calculate viability tier from database enrichment record.

    Returns: (tier, multiplier, reason)
    """
    if not enrichment:
        return "conditional", 0.7, "No enrichment data - requires web research"

    # Use cached multiplier if available
    if enrichment.get("viability_multiplier") is not None:
        multiplier = float(enrichment["viability_multiplier"])

        # Determine tier from multiplier
        if multiplier == 0.0:
            return "skip", 0.0, "Excluded based on enrichment data"
        elif multiplier >= 0.85:
            return "ready", multiplier, get_ready_reason(enrichment)
        elif multiplier >= 0.5:
            return "conditional", multiplier, get_conditional_reason(enrichment)
        else:
            return "watch", multiplier, get_watch_reason(enrichment)

    # Calculate from enrichment fields
    red_flags = enrichment.get("red_flags", []) or []
    if isinstance(red_flags, str):
        red_flags = [red_flags]

    accepts_unsolicited = enrichment.get("accepts_unsolicited")
    application_type = enrichment.get("application_type", "unknown")
    has_deadline = enrichment.get("current_deadline") is not None

    # SKIP tier conditions
    if "mission_mismatch" in red_flags:
        return "skip", 0.0, "Mission or geographic mismatch"
    if application_type == "invite_only":
        return "skip", 0.0, "Invitation-only - does not accept unsolicited proposals"
    if len(red_flags) >= 3:
        return "skip", 0.0, "Multiple red flags indicate poor fit"

    # READY tier conditions
    if accepts_unsolicited is True:
        if application_type in ("open", "loi"):
            if has_deadline:
                return "ready", 1.0, "Accepts applications with clear deadline"
            return "ready", 0.95, "Accepts applications (LOI or open)"
        if application_type == "rfp_periodic" and has_deadline:
            return "ready", 1.0, "Active RFP with deadline"
        if application_type == "rfp_rolling":
            return "ready", 0.90, "Rolling RFP - accepts proposals"

    # CONDITIONAL tier conditions
    if application_type == "unknown":
        return "conditional", 0.6, "Application process unclear - verify before outreach"
    if accepts_unsolicited is None:
        return "conditional", 0.5, "Unsolicited policy unknown - research needed"

    # WATCH tier - closed but worth monitoring
    if accepts_unsolicited is False:
        if application_type == "rfp_periodic":
            return "watch", 0.3, "RFP-only - monitor for future opportunities"
        return "watch", 0.2, "Does not accept unsolicited proposals"

    # Default
    return "conditional", 0.5, "Viability requires verification"


def get_ready_reason(enrichment: dict) -> str:
    """Generate reason string for READY tier."""
    app_type = enrichment.get("application_type", "unknown")
    deadline = enrichment.get("current_deadline")

    if deadline:
        return f"Accepts applications - deadline: {deadline}"
    elif app_type == "loi":
        return "Accepts Letters of Inquiry"
    elif app_type == "open":
        return "Open application process"
    elif app_type == "rfp_rolling":
        return "Rolling RFP - proposals accepted"
    else:
        return "Accepts unsolicited applications"


def get_conditional_reason(enrichment: dict) -> str:
    """Generate reason string for CONDITIONAL tier."""
    app_type = enrichment.get("application_type", "unknown")

    if app_type == "unknown":
        return "Application process unclear - contact to verify"
    elif enrichment.get("accepts_unsolicited") is None:
        return "Unsolicited policy unclear - research required"
    else:
        return "May accept applications - verify before outreach"


def get_watch_reason(enrichment: dict) -> str:
    """Generate reason string for WATCH tier."""
    app_type = enrichment.get("application_type", "unknown")

    if app_type == "rfp_periodic":
        return "RFP-only - monitor for announced opportunities"
    elif app_type == "invite_only":
        return "Invitation-only - build relationship before proposal"
    else:
        return "Does not accept unsolicited proposals - requires connection"


def build_viable_foundation(
    row: pd.Series,
    enrichment: Optional[dict],
    tier: str,
    multiplier: float,
    reason: str,
    website: Optional[str],
    rank: int
) -> dict:
    """Build a viable foundation record with all relevant data."""

    original_score = float(row["match_score"])
    adjusted_score = round(original_score * multiplier, 2)

    foundation = {
        "rank": rank,
        "foundation_ein": str(row["foundation_ein"]),
        "foundation_name": row["foundation_name"],
        "foundation_state": row.get("foundation_state", ""),
        "foundation_city": row.get("foundation_city", ""),

        # Scoring
        "match_score": original_score,
        "adjusted_score": adjusted_score,

        # Viability
        "viability": {
            "tier": tier,
            "multiplier": multiplier,
            "reason": reason,
        },

        # Enrichment data (if available)
        "enrichment": None,

        # Contact info
        "website": website,
        "contact_name": None,
        "contact_email": None,
        "contact_phone": None,
        "application_url": None,

        # Deadline
        "deadline": None,
        "deadline_notes": None,
    }

    # Add enrichment details if available
    if enrichment:
        foundation["enrichment"] = {
            "accepts_unsolicited": enrichment.get("accepts_unsolicited"),
            "application_type": enrichment.get("application_type"),
            "red_flags": enrichment.get("red_flags", []),
            "program_priorities": enrichment.get("program_priorities"),
            "geographic_focus": enrichment.get("geographic_focus"),
            "grant_range_stated": enrichment.get("grant_range_stated"),
            "last_enriched": str(enrichment.get("last_enriched")) if enrichment.get("last_enriched") else None,
            "enrichment_source": enrichment.get("enrichment_source"),
            "enrichment_notes": enrichment.get("enrichment_notes"),
        }

        # Contact info from enrichment
        foundation["contact_name"] = enrichment.get("contact_name")
        foundation["contact_email"] = enrichment.get("contact_email")
        foundation["contact_phone"] = enrichment.get("contact_phone")
        foundation["application_url"] = enrichment.get("application_url")

        # Deadline from enrichment
        foundation["deadline"] = str(enrichment.get("current_deadline")) if enrichment.get("current_deadline") else None
        foundation["deadline_notes"] = enrichment.get("deadline_notes")

    return foundation


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Filter foundations by viability using database enrichment"
    )
    parser.add_argument("--client", required=True, help="Client name or short_name")
    parser.add_argument("--top", type=int, default=20, help="Number of top foundations to process")
    parser.add_argument(
        "--include-watch", action="store_true",
        help="Include WATCH tier foundations in output (default: exclude)"
    )
    parser.add_argument(
        "--include-skip", action="store_true",
        help="Include SKIP tier foundations in output (default: exclude)"
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
    logger = setup_logging(client_name, "04_filter_viable")
    logger.info(f"[04_filter_viable] Starting for {client_entry['name']}")

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
    top_foundations = scores_df.head(args.top)

    logger.info(f"Processing top {len(top_foundations)} foundations")

    print(f"\nViability Filtering")
    print(f"=" * 70)
    print(f"Client: {client_entry['name']}")
    print(f"Foundations to process: {len(top_foundations)}")
    print(f"=" * 70)

    # Connect to database
    conn = get_db_connection()

    # Process each foundation
    viable_foundations = []
    tier_counts = {"ready": 0, "conditional": 0, "watch": 0, "skip": 0}

    for _, row in top_foundations.iterrows():
        ein = str(row["foundation_ein"])
        name = row["foundation_name"][:45]

        # Get enrichment from database
        enrichment = get_enrichment_from_db(ein, conn)

        # Get website if not in enrichment
        website = None
        if enrichment and enrichment.get("enrichment_source"):
            website = enrichment.get("enrichment_source")
        else:
            website = get_foundation_website(ein, conn)

        # Calculate viability
        tier, multiplier, reason = calculate_viability_tier(enrichment)
        tier_counts[tier] += 1

        # Log result
        enriched_flag = "DB" if enrichment else "none"
        logger.info(f"{name}: {tier.upper()} (x{multiplier:.2f}) [{enriched_flag}] - {reason}")

        status_icons = {"ready": "✅", "conditional": "🟡", "watch": "👀", "skip": "❌"}
        print(f"  {status_icons[tier]} {name}")
        print(f"      {tier.upper()} (x{multiplier:.2f}) - {reason}")

        # Build foundation record (rank will be set after filtering)
        foundation = build_viable_foundation(
            row, enrichment, tier, multiplier, reason, website, rank=0
        )
        viable_foundations.append(foundation)

    conn.close()

    print("=" * 70)

    # Filter based on tier
    if args.include_skip:
        filtered = viable_foundations
    elif args.include_watch:
        filtered = [f for f in viable_foundations if f["viability"]["tier"] != "skip"]
    else:
        # Default: exclude WATCH and SKIP
        filtered = [f for f in viable_foundations if f["viability"]["tier"] in ["ready", "conditional"]]

    # Sort by tier priority, then adjusted score
    tier_order = {"ready": 0, "conditional": 1, "watch": 2, "skip": 3}
    filtered.sort(key=lambda x: (
        tier_order.get(x["viability"]["tier"], 4),
        -x["adjusted_score"]
    ))

    # Assign ranks
    for i, f in enumerate(filtered):
        f["rank"] = i + 1

    # Prepare output
    output = {
        "client": client_entry["name"],
        "client_short_name": client_entry.get("short_name", ""),
        "run_date": args.date,
        "filter_date": datetime.now().isoformat(),
        "settings": {
            "top_n_processed": args.top,
            "include_watch": args.include_watch,
            "include_skip": args.include_skip,
        },
        "summary": {
            "total_processed": len(viable_foundations),
            "total_output": len(filtered),
            "tier_counts": tier_counts,
            "excluded": len(viable_foundations) - len(filtered),
        },
        "foundations": filtered
    }

    # Save output
    output_file = run_dir / "04_viable_foundations.json"
    save_json(output, output_file)

    logger.info(f"[04_filter_viable] Saved {len(filtered)} foundations to {output_file}")

    # Summary
    print(f"\n{'=' * 70}")
    print("Viability Filter Complete!")
    print(f"{'=' * 70}")

    print(f"\nTier Distribution (of {len(viable_foundations)} processed):")
    print(f"  ✅ READY:       {tier_counts['ready']}")
    print(f"  🟡 CONDITIONAL: {tier_counts['conditional']}")
    print(f"  👀 WATCH:       {tier_counts['watch']}")
    print(f"  ❌ SKIP:        {tier_counts['skip']}")

    print(f"\nOutput Summary:")
    print(f"  Total processed: {len(viable_foundations)}")
    print(f"  Total output:    {len(filtered)}")
    print(f"  Excluded:        {len(viable_foundations) - len(filtered)}")

    # Show top results
    print(f"\nTop Viable Foundations:")
    for f in filtered[:7]:
        v = f["viability"]
        deadline = f.get("deadline") or "Rolling/Unknown"
        print(f"  {f['rank']}. {f['foundation_name'][:40]}")
        print(f"     {v['tier'].upper()} | Score: {f['adjusted_score']:.1f} | Deadline: {deadline}")

    if len(filtered) > 7:
        print(f"  ... and {len(filtered) - 7} more")

    print(f"\nOutput: {output_file}")
    print(f"{'=' * 70}")

    # Guidance
    print(f"\n📋 Next Steps:")

    no_enrichment = sum(1 for f in viable_foundations if f["enrichment"] is None)
    if no_enrichment > 0:
        print(f"  ⚠️  {no_enrichment} foundations need web research:")
        print(f"     Run: python scripts/03_check_enrichment.py --client {args.client}")
        print(f"     Then: Enrich and store with 03b_store_enrichment.py")

    if tier_counts['ready'] > 0 or tier_counts['conditional'] > 0:
        print(f"\n  ✅ Ready for report generation:")
        print(f"     Run: python scripts/05_assemble_opportunities.py --client {args.client}")


if __name__ == "__main__":
    main()
