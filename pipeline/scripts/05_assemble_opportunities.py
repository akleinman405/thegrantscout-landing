#!/usr/bin/env python3
"""
Script 05: Assemble Opportunities

Combines scores, snapshots, and connections; applies quality filters;
calculates fit scores; and selects the final top opportunities for the report.

If 04_viable_foundations.json exists (from the viability filter), uses that
as the primary input and incorporates viability tier data.

Usage:
    python scripts/05_assemble_opportunities.py --client "PSMF"
    python scripts/05_assemble_opportunities.py --client "PSMF" --top 5
    python scripts/05_assemble_opportunities.py --client "PSMF" --top 10
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.paths import get_run_dir, load_client_registry, setup_logging


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def passes_quality_filters(opp: dict, client: dict, tier: str = "strict") -> Tuple[bool, str]:
    """
    Check if opportunity passes quality filters.
    Returns (passes, reason_if_failed)

    Tiers (in order of looseness):
    - "strict": All quality checks (prefer these)
    - "relaxed_median": Allow median up to $10M (for large foundations)
    - "relaxed_recency": Allow grants within 5 years instead of 3
    - "minimal": Only filter out obvious bad data (PAPs, no data, $0 grants)
    """
    snapshot = opp.get("snapshot", {})
    annual = snapshot.get("annual_giving", {})
    typical = snapshot.get("typical_grant", {})
    median = typical.get("median", 0)
    latest_year = annual.get("year")
    grant_count = annual.get("count", 0)

    # ============ ALWAYS APPLY (all tiers) ============

    # Hard filter: No grant amount data at all
    if median == 0:
        return False, "No grant amount data"

    # Hard filter: Patient assistance programs (billion-dollar medians)
    if median > 100000000:  # $100M - definitely a patient assistance program
        return False, f"Patient assistance program: ${median:,.0f} median"

    # Hard filter: Name-based patient assistance exclusion
    name = opp.get("foundation_name", "").upper()
    if any(x in name for x in ["PATIENT ASSISTANCE", "PATIENT ACCESS", "PAP INC"]):
        return False, "Patient assistance program (name match)"

    # Hard filter: DAF/employee matching (high volume + tiny median)
    if grant_count > 10000 and median < 2000:
        return False, f"Likely employee matching/DAF ({grant_count:,} grants, ${median:,.0f} median)"

    # ============ TIER: MINIMAL (only hard filters above) ============
    if tier == "minimal":
        # Clean up garbage comparable grants
        _clean_comparable_grant(opp)
        return True, ""

    # ============ TIER: RELAXED_RECENCY ============
    if tier in ["strict", "relaxed_median", "relaxed_recency"]:
        recency_threshold = 2019 if tier == "relaxed_recency" else 2021
        if latest_year is not None and latest_year < recency_threshold:
            return False, f"No recent grants (latest: {latest_year})"

    # ============ TIER: RELAXED_MEDIAN ============
    if tier in ["strict", "relaxed_median"]:
        median_cap = 10000000 if tier == "relaxed_median" else 5000000
        if median > median_cap:
            return False, f"Unrealistic median grant: ${median:,.0f}"

    # ============ TIER: STRICT ============
    if tier == "strict":
        # Median grant must be at least $5K (filters employee matching programs)
        if median < 5000:
            return False, f"Median grant too low: ${median:,.0f} (minimum: $5,000)"

        # Must have some grant history
        if grant_count < 5:
            return False, f"Too few grants: {grant_count}"

    # Clean up garbage comparable grants
    _clean_comparable_grant(opp)

    return True, ""


def _clean_comparable_grant(opp: dict) -> None:
    """Remove comparable grants with garbage recipient names."""
    comparable = opp.get("snapshot", {}).get("comparable_grant")
    if comparable:
        recipient = (comparable.get("recipient") or "").strip().upper()
        # Check for empty recipient
        if not recipient:
            opp["snapshot"]["comparable_grant"] = None
            return
        # Check for garbage patterns
        garbage_names = ["SEE ATTACHED", "SEE STATEMENT", "VARIOUS", "MULTIPLE"]
        if any(g in recipient for g in garbage_names):
            opp["snapshot"]["comparable_grant"] = None


def calculate_fit_score(opp: dict, client: dict) -> int:
    """
    Calculate 1-10 fit score based on multiple factors.
    """
    score = opp["match_score"] / 10  # Start with 0-10 from match

    snapshot = opp.get("snapshot", {})

    # Bonus: Same state (+1)
    if opp.get("same_state"):
        score += 1.0

    # Bonus: Strong connections (+0.5 per strong, +0.25 per moderate)
    for conn in opp.get("connections", []):
        if conn.get("strength") == "strong":
            score += 0.5
        elif conn.get("strength") == "moderate":
            score += 0.25

    # Bonus/Penalty: Budget alignment
    profile = snapshot.get("recipient_profile", {})
    budget_min = profile.get("budget_min", 0)
    budget_max = profile.get("budget_max", float("inf"))
    client_budget = client.get("budget_numeric", 0)

    if budget_min > 0 and budget_max > 0 and client_budget > 0:
        if budget_min <= client_budget <= budget_max:
            score += 0.5  # Budget in typical range
        elif client_budget < budget_min * 0.3 or client_budget > budget_max * 3:
            score -= 1.0  # Way outside typical range

    # Bonus: High general support (easier application)
    giving_style = snapshot.get("giving_style", {})
    if giving_style.get("general_pct", 0) > 0.5:
        score += 0.25

    # Penalty: No comparable grant (can't prove fit)
    comparable = opp.get("snapshot", {}).get("comparable_grant")
    if not comparable:
        score -= 1.5

    # Cap at 1-10
    return max(1, min(10, int(round(score))))


def calculate_effort(snapshot: dict) -> str:
    """
    Estimate application effort: Low, Medium, High
    """
    repeat_rate = snapshot.get("repeat_funding", {}).get("rate", 0)
    general_pct = snapshot.get("giving_style", {}).get("general_pct", 0.5)

    # Low effort: High general support + moderate repeat rate
    if general_pct > 0.6 and repeat_rate > 0.3:
        return "Low"

    # High effort: Program-specific focus or very high repeat rate (hard to break in)
    if general_pct < 0.3:
        return "High"
    if repeat_rate > 0.7:
        return "High"  # Very relationship-driven

    return "Medium"


def calculate_status(fit_score: int, effort: str) -> str:
    """
    Determine priority status: HIGH, MEDIUM, LOW
    """
    if fit_score >= 8 and effort != "High":
        return "HIGH"
    elif fit_score >= 6:
        return "MEDIUM"
    else:
        return "LOW"


def get_amount_range(snapshot: dict, client_budget: float) -> Tuple[float, float]:
    """
    Estimate likely grant amount range for this client.
    """
    typical = snapshot.get("typical_grant", {})
    median = typical.get("median", 0)
    min_grant = typical.get("min", 0)
    max_grant = typical.get("max", 0)

    # Use comparable grant if available
    comparable = snapshot.get("comparable_grant")
    if comparable and comparable.get("amount", 0) > 0:
        comp_amount = comparable["amount"]
        # Range around comparable: 50% to 150%
        return (comp_amount * 0.5, comp_amount * 1.5)

    # Otherwise use typical grant range, capped reasonably
    if median > 0:
        # Estimate: could get 50% to 200% of median
        amount_min = max(min_grant, median * 0.5)
        amount_max = min(max_grant, median * 2, 1000000)  # Cap at $1M
        return (amount_min, amount_max)

    # Fallback
    return (10000, 50000)


def ensure_geographic_diversity(opportunities: list, top_n: int = 5) -> list:
    """
    Ensure at least 1-2 same-state foundations in final selection.
    This helps clients see local options even if national foundations score higher.
    """
    same_state = [o for o in opportunities if o.get("same_state")]
    diff_state = [o for o in opportunities if not o.get("same_state")]

    if not same_state:
        # No same-state options, just return top N
        return opportunities[:top_n]

    if not diff_state:
        # All are same-state, just return top N
        return opportunities[:top_n]

    # Guarantee at least 1-2 same-state foundations
    num_same_state = min(2, len(same_state))
    num_other = top_n - num_same_state

    # Take top same-state + top other
    selected = same_state[:num_same_state] + diff_state[:num_other]

    # If we don't have enough, fill with more same-state or diff-state
    if len(selected) < top_n:
        remaining = top_n - len(selected)
        # First try more same_state
        extra_same = same_state[num_same_state:num_same_state + remaining]
        selected.extend(extra_same)
        remaining = top_n - len(selected)
        # Then try more diff_state if still needed
        if remaining > 0:
            extra_diff = diff_state[num_other:num_other + remaining]
            selected.extend(extra_diff)

    # Re-sort by fit_score to get proper ranking
    selected.sort(key=lambda x: (x["fit_score"], x["match_score"]), reverse=True)

    return selected


def main():
    parser = argparse.ArgumentParser(description="Assemble opportunities from scores, snapshots, and connections")
    parser.add_argument("--client", required=True, help="Client name or short_name")
    parser.add_argument("--top", type=int, default=5, help="Number of opportunities to select")
    parser.add_argument("--date", default=date.today().isoformat(), help="Run date (YYYY-MM-DD)")
    args = parser.parse_args()

    # Find client
    registry = load_client_registry()
    client_entry = None
    for c in registry.get("clients", []):
        if c["name"].lower() == args.client.lower() or c.get("short_name", "").lower() == args.client.lower():
            client_entry = c
            break

    if not client_entry:
        print(f"ERROR: Client '{args.client}' not found in registry")
        sys.exit(1)

    client_name = client_entry["name"].replace(" ", "_")

    # Set up logging
    logger = setup_logging(client_name, "05_assemble_opportunities")
    logger.info(f"[05_assemble_opportunities] Starting for {client_entry['name']}")

    # Find run directory
    run_dir = get_run_dir(client_name, args.date)
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)

    # Load all input files
    client_file = run_dir / "01_client.json"
    scores_file = run_dir / "02_scored_foundations.csv"
    snapshots_file = run_dir / "03_snapshots.json"
    connections_file = run_dir / "04_connections.json"
    viable_file = run_dir / "04_viable_foundations.json"

    # Check required files
    for f in [client_file, snapshots_file, connections_file]:
        if not f.exists():
            print(f"ERROR: Required file not found: {f}")
            sys.exit(1)

    # Load data
    client = load_json(client_file)
    snapshots_list = load_json(snapshots_file)
    connections = load_json(connections_file)

    # Index snapshots by EIN
    snapshots = {str(s["foundation_ein"]): s for s in snapshots_list}

    # Check for viability filter output (preferred input)
    use_viability = viable_file.exists()
    viable_data = None

    if use_viability:
        viable_data = load_json(viable_file)
        viable_foundations = viable_data.get("foundations", [])
        logger.info(f"Using viability-filtered foundations: {len(viable_foundations)}")
        print(f"\n✅ Found 04_viable_foundations.json - using viability data")
        print(f"  Viable foundations: {len(viable_foundations)}")
    else:
        # Fall back to scored foundations
        if not scores_file.exists():
            print(f"ERROR: Neither 04_viable_foundations.json nor 02_scored_foundations.csv found")
            sys.exit(1)
        scores_df = pd.read_csv(scores_file, dtype={"foundation_ein": str})
        logger.info(f"Loaded {len(scores_df)} scored foundations (no viability filter)")
        print(f"\n⚠️  No 04_viable_foundations.json - using scored foundations directly")
        print(f"  Scored foundations: {len(scores_df)}")

    logger.info(f"Loaded {len(snapshots)} snapshots")
    logger.info(f"Loaded connections for {len(connections)} foundations")

    print(f"  Snapshots: {len(snapshots)}")
    print(f"  Connections: {len(connections)}")

    # Join into single list - handle both viability-filtered and raw scores
    opportunities = []

    if use_viability:
        # Use viability-filtered foundations
        for vf in viable_foundations:
            ein = str(vf["foundation_ein"])
            opp = {
                "foundation_ein": ein,
                "foundation_name": vf["foundation_name"],
                "foundation_state": vf.get("foundation_state", ""),
                "match_score": float(vf.get("match_score", 0)),
                "adjusted_score": float(vf.get("adjusted_score", 0)),
                "match_probability": 0.0,  # Not available in viable format
                "same_state": False,  # Will check below
                "snapshot": snapshots.get(ein, {}),
                "connections": connections.get(ein, []),
                # Viability data from 04_filter_viable.py
                "viability": vf.get("viability", {}),
                "enrichment": vf.get("enrichment", {}),
                # Pre-filled contact info from enrichment
                "deadline": vf.get("deadline"),
                "deadline_notes": vf.get("deadline_notes"),
                "contact_name": vf.get("contact_name"),
                "contact_email": vf.get("contact_email"),
                "contact_phone": vf.get("contact_phone"),
                "application_url": vf.get("application_url"),
                "website": vf.get("website"),
            }
            # Check same_state
            opp["same_state"] = (opp["foundation_state"] == client.get("state", ""))
            opportunities.append(opp)
    else:
        # Fall back to raw scored foundations
        for _, row in scores_df.iterrows():
            ein = str(row["foundation_ein"])
            opp = {
                "foundation_ein": ein,
                "foundation_name": row["foundation_name"],
                "foundation_state": row.get("foundation_state", ""),
                "match_score": float(row["match_score"]),
                "adjusted_score": float(row["match_score"]),  # No adjustment without viability
                "match_probability": float(row["match_probability"]),
                "same_state": bool(row.get("same_state", False)),
                "snapshot": snapshots.get(ein, {}),
                "connections": connections.get(ein, []),
                "viability": {},  # No viability data
                "enrichment": {},
            }
            opportunities.append(opp)

    # Apply quality filters with progressive tiers to get exactly 5 foundations
    TARGET_COUNT = 5  # Always output exactly 5 foundations
    FILTER_TIERS = ["strict", "relaxed_median", "relaxed_recency", "minimal"]

    filtered = []
    filtered_out = []
    tier_counts = {tier: 0 for tier in FILTER_TIERS}

    # Track which opportunities have been selected and at what tier
    selected_eins = set()

    for tier in FILTER_TIERS:
        if len(filtered) >= TARGET_COUNT:
            break

        tier_added = 0
        for opp in opportunities:
            if opp["foundation_ein"] in selected_eins:
                continue  # Already selected at a stricter tier

            passes, reason = passes_quality_filters(opp, client, tier=tier)
            if passes:
                opp["quality_tier"] = tier  # Track which tier it passed at
                filtered.append(opp)
                selected_eins.add(opp["foundation_ein"])
                tier_added += 1

                if len(filtered) >= TARGET_COUNT:
                    break
            else:
                # Only log if this is the first (strictest) tier check
                if tier == "strict":
                    filtered_out.append({
                        "ein": opp["foundation_ein"],
                        "name": opp["foundation_name"],
                        "reason": reason
                    })

        tier_counts[tier] = tier_added
        if tier_added > 0:
            logger.info(f"Tier '{tier}': Added {tier_added} foundations (total: {len(filtered)})")

    # Log filtering results
    logger.info(f"Quality filtering: Passed={len(filtered)}, Failed={len(filtered_out)}")
    print(f"\nQuality filtering (target: {TARGET_COUNT}):")
    print(f"  Passed: {len(filtered)}")
    for tier, count in tier_counts.items():
        if count > 0:
            print(f"    - {tier}: {count}")
    print(f"  Failed (strict tier): {len(filtered_out)}")

    if filtered_out:
        print(f"\n  Sample filtered out (strict tier):")
        for f in filtered_out[:5]:
            print(f"    - {f['name'][:40]}: {f['reason']}")
            logger.info(f"  Filtered: {f['name']} - {f['reason']}")
        if len(filtered_out) > 5:
            print(f"    ... and {len(filtered_out) - 5} more")

    # Warn if we couldn't get 5
    if len(filtered) < TARGET_COUNT:
        logger.warning(f"Could only find {len(filtered)} foundations passing all filter tiers (target: {TARGET_COUNT})")
        print(f"\n  WARNING: Only {len(filtered)} foundations found (target: {TARGET_COUNT})")

    # Add calculated fields
    fit_scores = []
    for opp in filtered:
        snapshot = opp.get("snapshot", {})

        opp["fit_score"] = calculate_fit_score(opp, client)
        opp["effort"] = calculate_effort(snapshot)
        opp["status"] = calculate_status(opp["fit_score"], opp["effort"])

        amount_min, amount_max = get_amount_range(snapshot, client.get("budget_numeric", 0))
        opp["amount_min"] = amount_min
        opp["amount_max"] = amount_max

        # Extract comparable grant for easy access
        opp["comparable_grant"] = snapshot.get("comparable_grant")

        fit_scores.append(opp["fit_score"])

    if fit_scores:
        logger.info(f"Fit scores: min={min(fit_scores)}, max={max(fit_scores)}, avg={sum(fit_scores)/len(fit_scores):.1f}")

    # Sort by quality_tier (strict first), then fit_score, then match_score
    tier_priority = {"strict": 0, "relaxed_median": 1, "relaxed_recency": 2, "minimal": 3}
    filtered.sort(key=lambda x: (tier_priority.get(x.get("quality_tier", "minimal"), 4),
                                  -x["fit_score"], -x["match_score"]))

    # Take exactly 5 (or fewer if not available), with geographic diversity
    top_opportunities = ensure_geographic_diversity(filtered, TARGET_COUNT)

    # Assign final ranks
    for i, opp in enumerate(top_opportunities):
        opp["rank"] = i + 1

    # Build output structure
    output = []
    for opp in top_opportunities:
        # Get viability info
        viability = opp.get("viability") or {}
        enrichment = opp.get("enrichment") or {}

        output_entry = {
            "rank": opp["rank"],
            "foundation_ein": opp["foundation_ein"],
            "foundation_name": opp["foundation_name"],
            "foundation_state": opp["foundation_state"],
            "match_score": opp["match_score"],
            "adjusted_score": opp.get("adjusted_score", opp["match_score"]),
            "match_probability": opp.get("match_probability", 0.0),
            "same_state": opp["same_state"],
            "fit_score": opp["fit_score"],
            "effort": opp["effort"],
            "status": opp["status"],
            "quality_tier": opp.get("quality_tier", "strict"),
            "amount_min": opp["amount_min"],
            "amount_max": opp["amount_max"],
            "funder_snapshot": opp["snapshot"],
            "comparable_grant": opp["comparable_grant"],
            "connections": opp["connections"],
            # Viability data
            "viability": {
                "tier": viability.get("tier", "conditional"),
                "multiplier": viability.get("multiplier", 1.0),
                "reason": viability.get("reason", ""),
            },
            # Enrichment data
            "enrichment": {
                "accepts_unsolicited": enrichment.get("accepts_unsolicited"),
                "application_type": enrichment.get("application_type"),
                "red_flags": enrichment.get("red_flags", []),
                "program_priorities": enrichment.get("program_priorities"),
                "geographic_focus": enrichment.get("geographic_focus"),
                "last_enriched": enrichment.get("last_enriched"),
            },
            # Contact info (from enrichment if available)
            "deadline": opp.get("deadline") or "Rolling",
            "deadline_notes": opp.get("deadline_notes") or "",
            "portal_url": opp.get("application_url") or opp.get("website") or "",
            "contact_name": opp.get("contact_name") or "",
            "contact_email": opp.get("contact_email") or "",
            "contact_phone": opp.get("contact_phone") or "",
            "application_requirements": [],
            "why_this_fits": "",
            "positioning_strategy": "",
            "next_steps": [],
        }
        output.append(output_entry)

    # Save output
    output_file = run_dir / "05_opportunities.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    logger.info(f"[05_assemble_opportunities] Saved {len(output)} opportunities to {output_file}")

    # Summary
    print(f"\n{'='*60}")
    print("Opportunities assembled!")
    print(f"{'='*60}")
    print(f"Client: {client_entry['name']}")
    print(f"Opportunities selected: {len(output)} (target: {TARGET_COUNT})")
    print(f"\nTop {len(output)} opportunities:")
    for opp in output:
        state_marker = " (same state)" if opp["same_state"] else ""
        conn_count = len(opp["connections"])
        tier_marker = f" [{opp['quality_tier']}]" if opp.get('quality_tier') != 'strict' else ""

        # Viability info
        viability = opp.get("viability", {})
        v_tier = viability.get("tier", "unknown").upper()
        v_mult = viability.get("multiplier", 1.0)

        tier_icon = {"READY": "✅", "CONDITIONAL": "🟡", "WATCH": "👀", "SKIP": "❌"}.get(v_tier, "❓")

        print(f"  {opp['rank']}. {opp['foundation_name'][:40]}{tier_marker}")
        print(f"     {tier_icon} {v_tier} (x{v_mult:.1f}) | fit={opp['fit_score']}, effort={opp['effort']}{state_marker}")
        print(f"     amount: ${opp['amount_min']:,.0f} - ${opp['amount_max']:,.0f}")
        if opp.get("deadline") and opp["deadline"] != "Rolling":
            print(f"     deadline: {opp['deadline']}")
    print(f"\nOutput: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
