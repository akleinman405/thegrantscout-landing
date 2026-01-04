#!/usr/bin/env python3
"""
Script 07: Build Report Data

Combines opportunities and narratives into the final report data structure,
adds metadata and timeline, and prepares everything for rendering.

Usage:
    python scripts/07_build_report_data.py --client "PSMF"
    python scripts/07_build_report_data.py --client "PSMF" --week 1
    python scripts/07_build_report_data.py --client "PSMF" --week 5
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.paths import get_run_dir, load_client_registry, setup_logging


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(data: dict, path: Path):
    """Save data to JSON file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def build_client_dict(client: dict) -> dict:
    """Extract relevant client fields for report."""
    return {
        "organization_name": client.get("organization_name", ""),
        "short_name": client.get("short_name", ""),
        "ein": client.get("ein", ""),
        "email": client.get("email", ""),
        "state": client.get("state", ""),
        "city": client.get("city", ""),
        "org_type": client.get("org_type", ""),
        "budget": client.get("budget", ""),
        "budget_numeric": client.get("budget_numeric", 0),
        "grant_size_target": client.get("grant_size_target", ""),
        "program_areas": client.get("program_areas", []),
        "populations_served": client.get("populations_served", []),
        "geographic_scope": client.get("geographic_scope", ""),
        "ntee_code": client.get("ntee_code", ""),
        "mission_statement": client.get("mission_statement", "")
    }


def build_timeline(opportunities: list, start_date: date) -> list:
    """
    Build 8-week action timeline.
    Distributes next_steps across weeks intelligently.
    """
    timeline = []

    for week_num in range(1, 9):
        week_start = start_date + timedelta(weeks=week_num - 1)
        week_end = week_start + timedelta(days=6)

        week_data = {
            "week": week_num,
            "date_start": week_start.isoformat(),
            "date_end": week_end.isoformat(),
            "tasks": []
        }

        # Week 1-2: Research and LOI drafting
        if week_num == 1:
            week_data["focus"] = "Research & Prioritization"
            # Add research tasks from top opportunities
            for opp in opportunities[:3]:
                for step in opp.get("next_steps", []):
                    if "research" in step.get("action", "").lower():
                        week_data["tasks"].append({
                            "foundation": opp["foundation_name"],
                            "action": step["action"],
                            "owner": step.get("owner", "TBD")
                        })
            # If no research tasks found, add generic ones
            if not week_data["tasks"]:
                for opp in opportunities[:3]:
                    week_data["tasks"].append({
                        "foundation": opp["foundation_name"],
                        "action": f"Research {opp['foundation_name']}'s recent grants and priorities",
                        "owner": "Development Director"
                    })

        elif week_num == 2:
            week_data["focus"] = "LOI Drafting"
            for opp in opportunities[:2]:
                week_data["tasks"].append({
                    "foundation": opp["foundation_name"],
                    "action": f"Draft Letter of Inquiry for {opp['foundation_name']}",
                    "owner": "Grant Writer"
                })

        elif week_num == 3:
            week_data["focus"] = "Submissions & Outreach"
            for opp in opportunities[:2]:
                week_data["tasks"].append({
                    "foundation": opp["foundation_name"],
                    "action": f"Submit LOI to {opp['foundation_name']}",
                    "owner": "Development Director"
                })

        elif week_num == 4:
            week_data["focus"] = "Follow-up & Next Batch"
            week_data["tasks"].append({
                "foundation": "All",
                "action": "Follow up on submitted LOIs",
                "owner": "Development Director"
            })
            # Start on opportunities 3-5
            for opp in opportunities[2:4]:
                week_data["tasks"].append({
                    "foundation": opp["foundation_name"],
                    "action": f"Research {opp['foundation_name']}",
                    "owner": "Development Team"
                })

        elif week_num in [5, 6]:
            week_data["focus"] = "Secondary Opportunities"
            for opp in opportunities[2:5]:
                week_data["tasks"].append({
                    "foundation": opp["foundation_name"],
                    "action": f"Prepare application materials for {opp['foundation_name']}",
                    "owner": "Grant Writer"
                })

        elif week_num == 7:
            week_data["focus"] = "Review & Adjust"
            week_data["tasks"].append({
                "foundation": "All",
                "action": "Review responses and adjust strategy",
                "owner": "Development Director"
            })

        elif week_num == 8:
            week_data["focus"] = "Planning Next Cycle"
            week_data["tasks"].append({
                "foundation": "All",
                "action": "Prepare for next report cycle",
                "owner": "Development Team"
            })

        timeline.append(week_data)

    return timeline


def extract_urgent_actions(opportunities: list) -> list:
    """
    Extract the most urgent actions across all opportunities.
    Returns top 5 actions sorted by deadline.
    """
    all_actions = []

    for opp in opportunities:
        for step in opp.get("next_steps", []):
            all_actions.append({
                "foundation": opp["foundation_name"],
                "action": step.get("action", ""),
                "deadline": step.get("deadline", ""),
                "owner": step.get("owner", "TBD")
            })

    # Sort by deadline
    all_actions.sort(key=lambda x: x.get("deadline", "9999-99-99"))

    # Return top 5 soonest
    return all_actions[:5]


def validate_report_data(report_data: dict) -> list:
    """
    Validate report data is complete.
    Returns list of warnings.
    """
    warnings = []

    # Check client
    if not report_data.get("client", {}).get("organization_name"):
        warnings.append("Missing client organization name")

    # Check opportunities
    opps = report_data.get("opportunities", [])
    if len(opps) < 5:
        warnings.append(f"Only {len(opps)} opportunities (expected 5)")

    for i, opp in enumerate(opps):
        if not opp.get("why_this_fits"):
            warnings.append(f"Opportunity {i+1} missing 'why_this_fits' narrative")
        if not opp.get("positioning_strategy"):
            warnings.append(f"Opportunity {i+1} missing 'positioning_strategy'")
        if not opp.get("next_steps"):
            warnings.append(f"Opportunity {i+1} missing 'next_steps'")
        if not opp.get("funder_snapshot"):
            warnings.append(f"Opportunity {i+1} missing funder snapshot")

    # Check executive summary
    exec_sum = report_data.get("executive_summary", {})
    if not exec_sum.get("key_strengths"):
        warnings.append("Missing executive summary key strengths")
    if not exec_sum.get("one_thing"):
        warnings.append("Missing executive summary 'one thing'")

    return warnings


def main():
    parser = argparse.ArgumentParser(
        description="Build final report data structure from opportunities and narratives"
    )
    parser.add_argument("--client", required=True, help="Client name or short_name")
    parser.add_argument(
        "--week", type=int, default=None,
        help="Week number (auto-calculates from date if not specified)"
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
    logger = setup_logging(client_name, "07_build_report_data")
    logger.info(f"[07_build_report_data] Starting for {client_entry['name']}")

    # Find run directory
    run_dir = get_run_dir(client_name, args.date)
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)

    # Load inputs
    client_file = run_dir / "01_client.json"
    opportunities_file = run_dir / "05_opportunities.json"
    narratives_file = run_dir / "06_narratives.json"

    for f in [client_file, opportunities_file, narratives_file]:
        if not f.exists():
            print(f"ERROR: Required file not found: {f}")
            sys.exit(1)

    client = load_json(client_file)
    opportunities = load_json(opportunities_file)
    narratives = load_json(narratives_file)

    logger.info(f"Loaded client profile")
    logger.info(f"Loaded {len(opportunities)} opportunities")
    logger.info(f"Loaded narratives for {len(narratives.get('opportunities', []))} opportunities")

    print(f"\nBuilding report data...")
    print(f"Client: {client.get('organization_name', 'Unknown')}")
    print(f"Opportunities: {len(opportunities)}")

    # Index narratives by EIN for easy lookup
    narrative_map = {
        n["foundation_ein"]: n
        for n in narratives.get("opportunities", [])
    }

    # Merge narratives into opportunities
    for opp in opportunities:
        ein = opp["foundation_ein"]
        narr = narrative_map.get(ein, {})

        # Merge narrative fields
        opp["why_this_fits"] = narr.get("why_this_fits", "")
        opp["positioning_strategy"] = narr.get("positioning_strategy", "")
        opp["next_steps"] = narr.get("next_steps", [])

    logger.info(f"Merged narratives into opportunities")
    print(f"Merged narratives into {len(opportunities)} opportunities")

    # Build report metadata
    today = date.today()

    # Week number - either specified or calculated
    week_number = args.week
    if week_number is None:
        week_number = today.isocalendar()[1]

    # Date range for this report
    date_range_start = today
    date_range_end = today + timedelta(days=6)

    report_meta = {
        "week_number": week_number,
        "report_date": today.isoformat(),
        "date_range_start": date_range_start.isoformat(),
        "date_range_end": date_range_end.isoformat(),
        "generated_at": datetime.now().isoformat(),
        "pipeline_version": "2.0"
    }

    logger.info(f"Built report metadata (Week {week_number})")
    print(f"Report week: {week_number}")

    # Build 8-week timeline
    timeline = build_timeline(opportunities, today)
    logger.info(f"Built 8-week timeline")
    print(f"Built {len(timeline)}-week timeline")

    # Extract urgent actions
    urgent_actions = extract_urgent_actions(opportunities)
    logger.info(f"Extracted {len(urgent_actions)} urgent actions")
    print(f"Extracted {len(urgent_actions)} urgent actions")

    # Build the complete report data structure
    report_data = {
        "client": build_client_dict(client),
        "report_meta": report_meta,
        "opportunities": opportunities,
        "executive_summary": narratives.get("executive_summary", {}),
        "timeline": timeline,
        "urgent_actions": urgent_actions
    }

    # Add urgent_actions to executive_summary as well
    report_data["executive_summary"]["urgent_actions"] = urgent_actions

    # Validate
    warnings = validate_report_data(report_data)
    logger.info(f"Validation: {len(warnings)} warnings")

    if warnings:
        print(f"\nValidation warnings:")
        for w in warnings:
            print(f"  - {w}")
            logger.warning(f"Validation: {w}")

    # Save output
    output_file = run_dir / "07_report_data.json"
    save_json(report_data, output_file)

    logger.info(f"[07_build_report_data] Saved to {output_file}")

    # Summary
    print(f"\n{'='*60}")
    print("Report data built!")
    print(f"{'='*60}")
    print(f"Client: {report_data['client']['organization_name']}")
    print(f"Report week: {report_meta['week_number']}")
    print(f"Date range: {report_meta['date_range_start']} to {report_meta['date_range_end']}")
    print(f"Opportunities: {len(opportunities)}")
    print(f"Timeline weeks: {len(timeline)}")
    print(f"Urgent actions: {len(urgent_actions)}")

    # Show executive summary stats
    exec_sum = report_data.get("executive_summary", {})
    scenarios = exec_sum.get("funding_scenarios", {})
    print(f"\nFunding scenarios:")
    print(f"  Conservative: ${scenarios.get('conservative', 0):,}")
    print(f"  Moderate: ${scenarios.get('moderate', 0):,}")
    print(f"  Ambitious: ${scenarios.get('ambitious', 0):,}")

    if warnings:
        print(f"\nWarnings: {len(warnings)}")

    print(f"\nOutput: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
