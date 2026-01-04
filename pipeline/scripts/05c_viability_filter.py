#!/usr/bin/env python3
"""
Script 05c: Viability Filter

Merges web research enrichment data with opportunities and applies viability
filtering to ensure only actionable foundations are included in client reports.

Viability Tiers:
  - READY: Accepts unsolicited applications, has clear process
  - CONDITIONAL: May accept applications, requires relationship/connection
  - WATCH: RFP-only or invitation-only, monitor for opportunities
  - SKIP: Mission mismatch, inactive, or explicitly closed

Usage:
    python scripts/05c_viability_filter.py --client "PSMF"
    python scripts/05c_viability_filter.py --client "PSMF" --strict
    python scripts/05c_viability_filter.py --client "PSMF" --keep-all
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.paths import get_run_dir, load_client_registry, setup_logging


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(data, path: Path):
    """Save data to JSON file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================================
# Viability Assessment
# ============================================================================

def assess_unsolicited_policy(enrichment: dict) -> Tuple[str, str]:
    """
    Check if foundation accepts unsolicited proposals.

    Returns: (status, reason)
        status: 'open', 'conditional', 'closed', 'unknown'
    """
    how_to_apply = enrichment.get("how_to_apply", {})

    # Check for explicit barriers
    if how_to_apply.get("critical_barrier"):
        barrier_type = how_to_apply.get("barrier_type", "Policy")
        return "closed", f"{barrier_type}: Does not accept unsolicited proposals"

    # Check process description
    process = (how_to_apply.get("process") or "").upper()

    # Explicit rejection indicators
    rejection_phrases = [
        "NOT ACCEPT",
        "DOES NOT ACCEPT",
        "NO UNSOLICITED",
        "INVITATION ONLY",
        "BY INVITATION",
        "RFP-ONLY",
        "RFP ONLY",
        "UNSOLICITED PROPOSALS NOT ACCEPTED",
    ]

    for phrase in rejection_phrases:
        if phrase in process:
            return "closed", "Foundation does not accept unsolicited proposals"

    # Check for RFP-based process
    if "RFP" in process and ("ONLY" in process or "MUST" in process or "RESPOND" in process):
        return "conditional", "RFP-based only - must wait for specific solicitations"

    # Check for unknown/unclear process
    if "UNKNOWN" in process or not process or process == "N/A":
        return "unknown", "Application process unclear - contact foundation"

    # Has portal = likely open
    if how_to_apply.get("portal_url"):
        return "open", "Online application available"

    # Default: assume potentially open
    return "unknown", "Contact foundation to verify application process"


def assess_fit_rating(enrichment: dict) -> Tuple[str, List[str]]:
    """
    Extract fit assessment from enrichment.

    Returns: (rating, red_flags)
        rating: 'strong', 'moderate', 'weak', 'unknown'
    """
    fit = enrichment.get("fit_assessment", {})

    rating = (fit.get("rating") or "unknown").lower()
    red_flags = fit.get("red_flags", [])

    # Normalize rating
    if rating in ["strong", "good", "high"]:
        rating = "strong"
    elif rating in ["moderate", "medium", "possible"]:
        rating = "moderate"
    elif rating in ["weak", "poor", "low"]:
        rating = "weak"
    else:
        rating = "unknown"

    return rating, red_flags


def extract_deadline(enrichment: dict) -> Optional[str]:
    """Extract specific deadline from enrichment if available."""
    deadlines = enrichment.get("deadlines", {})

    # Check for specific dates
    dates = deadlines.get("dates", [])
    for d in dates:
        # Skip generic values
        if d and not any(x in str(d).lower() for x in ["rolling", "none", "unknown", "check", "quarterly"]):
            return str(d)

    # Check current opportunities
    for opp in enrichment.get("current_opportunities", []):
        deadline = opp.get("deadline", "")
        if deadline and not any(x in str(deadline).lower() for x in ["rolling", "none", "unknown", "closed"]):
            return str(deadline)

    return None


def extract_verified_contact(enrichment: dict) -> dict:
    """Extract verified contact information from enrichment."""
    contact = enrichment.get("contact", {})

    result = {
        "website": None,
        "website_verified": False,
        "email": None,
        "phone": None,
        "program_officer": None,
        "program_officer_title": None,
        "portal_url": None,
    }

    # Website
    website = contact.get("website") or contact.get("website_verified")
    if website and website not in ["null", "None", "N/A"]:
        result["website"] = website
        result["website_verified"] = contact.get("website_verified", False)

    # Email
    email = contact.get("email") or contact.get("program_officer_email")
    if email and "@" in str(email):
        result["email"] = email

    # Phone
    phone = contact.get("phone")
    if phone:
        result["phone"] = str(phone)

    # Program officer
    po = contact.get("program_officer")
    if po and po not in ["None", "Not identified", "N/A", "null"]:
        result["program_officer"] = po
        result["program_officer_title"] = contact.get("program_officer_title")

    # Portal
    portal = enrichment.get("how_to_apply", {}).get("portal_url")
    if portal and portal not in ["null", "None", "N/A"]:
        result["portal_url"] = portal

    return result


def calculate_viability_tier(
    unsolicited_status: str,
    fit_rating: str,
    red_flags: List[str],
    has_deadline: bool
) -> Tuple[str, float, str]:
    """
    Calculate viability tier and multiplier.

    Returns: (tier, multiplier, reason)
        tier: 'ready', 'conditional', 'watch', 'skip'
        multiplier: 0.0 to 1.0
    """

    # SKIP tier: Definite exclusions
    if fit_rating == "weak" and len(red_flags) >= 3:
        return "skip", 0.0, "Multiple red flags and weak fit assessment"

    # Check for mission mismatch in red flags
    mission_mismatch_phrases = [
        "mission",
        "focus",
        "not relevant",
        "does not align",
        "geographic restriction",
        "not in target",
    ]

    has_mission_mismatch = any(
        any(phrase in flag.lower() for phrase in mission_mismatch_phrases)
        for flag in red_flags
    )

    if has_mission_mismatch and fit_rating == "weak":
        return "skip", 0.0, "Mission or geographic mismatch"

    # WATCH tier: Closed to unsolicited but might have opportunities
    if unsolicited_status == "closed":
        if fit_rating == "strong":
            return "watch", 0.3, "Strong fit but does not accept unsolicited proposals - requires relationship"
        else:
            return "watch", 0.2, "Does not accept unsolicited proposals"

    # CONDITIONAL tier: RFP-only or unclear
    if unsolicited_status == "conditional":
        if fit_rating in ["strong", "moderate"]:
            return "conditional", 0.6, "RFP-based - monitor for open opportunities"
        else:
            return "watch", 0.4, "RFP-based with uncertain fit"

    if unsolicited_status == "unknown":
        if fit_rating == "strong":
            return "conditional", 0.7, "Application process unclear - strong fit warrants inquiry"
        elif fit_rating == "moderate":
            return "conditional", 0.5, "Application process unclear - contact to verify"
        else:
            return "watch", 0.3, "Unclear process and uncertain fit"

    # READY tier: Open to applications
    if unsolicited_status == "open":
        if fit_rating == "strong":
            multiplier = 1.0
            if has_deadline:
                return "ready", 1.0, "Strong fit with clear deadline"
            return "ready", 0.95, "Strong fit with open application"
        elif fit_rating == "moderate":
            return "ready", 0.85, "Moderate fit with open application"
        elif fit_rating == "weak":
            return "conditional", 0.5, "Open to applications but weak fit - consider carefully"
        else:
            return "ready", 0.8, "Open to applications"

    # Default
    return "conditional", 0.5, "Viability uncertain"


def merge_enrichment_into_opportunity(opp: dict, enrichment: dict) -> dict:
    """
    Merge enrichment data into opportunity record.
    Returns enriched opportunity.
    """
    # Assess viability factors
    unsolicited_status, unsolicited_reason = assess_unsolicited_policy(enrichment)
    fit_rating, red_flags = assess_fit_rating(enrichment)
    specific_deadline = extract_deadline(enrichment)
    verified_contact = extract_verified_contact(enrichment)

    # Calculate tier
    tier, multiplier, tier_reason = calculate_viability_tier(
        unsolicited_status,
        fit_rating,
        red_flags,
        bool(specific_deadline)
    )

    # Calculate adjusted score
    original_fit = opp.get("fit_score", 5)
    adjusted_score = round(original_fit * multiplier, 1)

    # Build viability data
    viability = {
        "tier": tier,
        "tier_reason": tier_reason,
        "multiplier": multiplier,
        "adjusted_score": adjusted_score,
        "unsolicited_status": unsolicited_status,
        "unsolicited_reason": unsolicited_reason,
        "fit_rating_enriched": fit_rating,
        "red_flags": red_flags[:5],  # Limit to top 5
        "recommendation": enrichment.get("fit_assessment", {}).get("recommendation", ""),
    }

    # Update opportunity with enrichment data
    enriched = opp.copy()
    enriched["viability"] = viability

    # Update deadline if specific one found
    if specific_deadline:
        enriched["deadline"] = specific_deadline
        enriched["deadline_source"] = "enrichment"

    # Update contact with verified info
    if verified_contact.get("website"):
        enriched["portal_url"] = verified_contact.get("portal_url") or verified_contact.get("website")
    if verified_contact.get("phone"):
        enriched["contact_phone"] = verified_contact["phone"]
    if verified_contact.get("email"):
        enriched["contact_email"] = verified_contact["email"]
    if verified_contact.get("program_officer"):
        enriched["contact_name"] = verified_contact["program_officer"]

    # Add current opportunities from enrichment
    current_opps = enrichment.get("current_opportunities", [])
    if current_opps:
        enriched["current_opportunities"] = current_opps

    # Add priorities from enrichment
    priorities = enrichment.get("current_priorities", [])
    if priorities:
        enriched["foundation_priorities"] = priorities[:5]

    return enriched


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Apply viability filter to opportunities using enrichment data"
    )
    parser.add_argument("--client", required=True, help="Client name or short_name")
    parser.add_argument(
        "--strict", action="store_true",
        help="Exclude WATCH and SKIP tier foundations entirely"
    )
    parser.add_argument(
        "--keep-all", action="store_true",
        help="Keep all foundations but add viability data (no filtering)"
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
    logger = setup_logging(client_name, "05c_viability_filter")
    logger.info(f"[05c_viability_filter] Starting for {client_entry['name']}")

    # Find run directory
    run_dir = get_run_dir(client_name, args.date)
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)

    # Load opportunities
    opportunities_file = run_dir / "05_opportunities.json"
    if not opportunities_file.exists():
        print(f"ERROR: Opportunities file not found: {opportunities_file}")
        sys.exit(1)

    opportunities = load_json(opportunities_file)
    logger.info(f"Loaded {len(opportunities)} opportunities")

    # Load enrichment data (optional)
    enrichment_file = run_dir / "05b_enrichment.json"
    enrichment_by_ein = {}

    if enrichment_file.exists():
        enrichment_data = load_json(enrichment_file)

        # Index by EIN
        # Handle different enrichment structures
        foundations = enrichment_data.get("foundations", []) or enrichment_data.get("enrichments", [])
        for f in foundations:
            ein = str(f.get("foundation_ein", ""))
            if ein:
                enrichment_by_ein[ein] = f

        logger.info(f"Loaded enrichment for {len(enrichment_by_ein)} foundations")
        print(f"\nLoaded enrichment data for {len(enrichment_by_ein)} foundations")
    else:
        logger.warning(f"No enrichment file found: {enrichment_file}")
        print(f"\nWARNING: No enrichment file found. Run web research first.")
        print(f"Expected: {enrichment_file}")
        print("Proceeding with basic viability assessment...\n")

    # Process each opportunity
    print(f"\nProcessing {len(opportunities)} opportunities...")
    print("=" * 70)

    enriched_opportunities = []
    tier_counts = {"ready": 0, "conditional": 0, "watch": 0, "skip": 0, "no_enrichment": 0}

    for opp in opportunities:
        ein = str(opp.get("foundation_ein", ""))
        name = opp.get("foundation_name", "Unknown")[:45]

        enrichment = enrichment_by_ein.get(ein, {})

        if enrichment:
            enriched = merge_enrichment_into_opportunity(opp, enrichment)
            tier = enriched["viability"]["tier"]
            tier_counts[tier] += 1

            # Log result
            mult = enriched["viability"]["multiplier"]
            reason = enriched["viability"]["tier_reason"][:50]
            logger.info(f"{name}: {tier.upper()} (×{mult}) - {reason}")
            print(f"  {name}")
            print(f"    → {tier.upper()} (×{mult:.1f}) - {reason}")
        else:
            # No enrichment data - add basic viability structure
            enriched = opp.copy()
            enriched["viability"] = {
                "tier": "conditional",
                "tier_reason": "No enrichment data available - requires verification",
                "multiplier": 0.7,
                "adjusted_score": round(opp.get("fit_score", 5) * 0.7, 1),
                "unsolicited_status": "unknown",
                "unsolicited_reason": "Not researched",
                "fit_rating_enriched": "unknown",
                "red_flags": [],
                "recommendation": "Contact foundation to verify application process",
            }
            tier_counts["no_enrichment"] += 1
            logger.info(f"{name}: NO ENRICHMENT - marked conditional")
            print(f"  {name}")
            print(f"    → CONDITIONAL (no enrichment data)")

        enriched_opportunities.append(enriched)

    print("=" * 70)

    # Apply filtering based on mode
    if args.strict:
        # Exclude WATCH and SKIP tiers
        filtered = [o for o in enriched_opportunities if o["viability"]["tier"] in ["ready", "conditional"]]
        logger.info(f"Strict mode: Kept {len(filtered)} of {len(enriched_opportunities)} opportunities")
    elif args.keep_all:
        # Keep all, just add viability data
        filtered = enriched_opportunities
        logger.info(f"Keep-all mode: All {len(filtered)} opportunities retained")
    else:
        # Default: Exclude SKIP tier only
        filtered = [o for o in enriched_opportunities if o["viability"]["tier"] != "skip"]
        logger.info(f"Default mode: Kept {len(filtered)} of {len(enriched_opportunities)} opportunities")

    # Re-sort by adjusted score
    filtered.sort(key=lambda x: (
        {"ready": 0, "conditional": 1, "watch": 2, "skip": 3}.get(x["viability"]["tier"], 4),
        -x["viability"]["adjusted_score"],
        -x.get("fit_score", 0)
    ))

    # Update ranks
    for i, opp in enumerate(filtered):
        opp["rank"] = i + 1

    # Save output
    output_file = run_dir / "05c_filtered.json"
    save_json(filtered, output_file)

    logger.info(f"[05c_viability_filter] Saved {len(filtered)} opportunities to {output_file}")

    # Summary
    print(f"\n{'=' * 70}")
    print("Viability Filter Complete!")
    print(f"{'=' * 70}")
    print(f"Client: {client_entry['name']}")
    print(f"\nTier Distribution:")
    print(f"  READY:       {tier_counts['ready']}")
    print(f"  CONDITIONAL: {tier_counts['conditional']}")
    print(f"  WATCH:       {tier_counts['watch']}")
    print(f"  SKIP:        {tier_counts['skip']}")
    if tier_counts['no_enrichment'] > 0:
        print(f"  (No enrichment: {tier_counts['no_enrichment']})")

    print(f"\nFiltering Result:")
    print(f"  Input:  {len(opportunities)} opportunities")
    print(f"  Output: {len(filtered)} opportunities")
    excluded = len(opportunities) - len(filtered)
    if excluded > 0:
        print(f"  Excluded: {excluded} (SKIP tier)")

    print(f"\nFinal Ranking (by viability-adjusted score):")
    for opp in filtered[:7]:
        v = opp["viability"]
        deadline = opp.get("deadline", "Rolling")
        print(f"  {opp['rank']}. {opp['foundation_name'][:40]}")
        print(f"     {v['tier'].upper()} | Adj. Score: {v['adjusted_score']:.1f} | Deadline: {deadline}")

    if len(filtered) > 7:
        print(f"  ... and {len(filtered) - 7} more")

    print(f"\nOutput: {output_file}")
    print(f"{'=' * 70}")

    # Provide guidance on next steps
    print(f"\n📋 Next Steps:")
    if tier_counts['ready'] > 0:
        print(f"  ✅ {tier_counts['ready']} foundations are READY for outreach")
    if tier_counts['conditional'] > 0:
        print(f"  ⚠️  {tier_counts['conditional']} foundations need verification before outreach")
    if tier_counts['watch'] > 0:
        print(f"  👀 {tier_counts['watch']} foundations are WATCH-only (monitor for RFPs)")
    if tier_counts['skip'] > 0:
        print(f"  ❌ {tier_counts['skip']} foundations excluded (poor fit or closed)")

    print(f"\nTo regenerate reports with viability data:")
    print(f"  1. Update 06_generate_narratives.py to read 05c_filtered.json")
    print(f"  2. Or manually review 05c_filtered.json and adjust")


if __name__ == "__main__":
    main()
