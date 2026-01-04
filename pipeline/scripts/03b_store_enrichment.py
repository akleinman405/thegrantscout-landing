#!/usr/bin/env python3
"""
Script 03b: Store Enrichment Data

Stores foundation enrichment data in the database. Can accept data from:
1. A JSON file (batch import)
2. Command-line arguments (single foundation)
3. Interactive mode (guided entry)

Usage:
    # Import from JSON file
    python scripts/03b_store_enrichment.py --file enrichment_data.json

    # Single foundation via args
    python scripts/03b_store_enrichment.py --ein 123456789 --application-type loi --accepts-unsolicited

    # Migrate from old 05b_enrichment.json files
    python scripts/03b_store_enrichment.py --migrate-client PSMF
"""

import argparse
import json
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor, Json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.paths import get_run_dir, load_client_registry, setup_logging, RUNS_DIR

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


def calculate_viability_multiplier(enrichment: dict) -> float:
    """
    Calculate viability multiplier from enrichment data.

    Returns: 0.0 to 1.0
    """
    red_flags = enrichment.get("red_flags", []) or []
    if isinstance(red_flags, str):
        red_flags = [red_flags]

    accepts_unsolicited = enrichment.get("accepts_unsolicited")
    application_type = enrichment.get("application_type", "unknown")
    has_deadline = enrichment.get("current_deadline") is not None

    # Check for mission_mismatch in red flags (case insensitive)
    has_mission_mismatch = any(
        "mission_mismatch" in str(rf).lower() or "mission mismatch" in str(rf).lower()
        for rf in red_flags
    )

    # SKIP tier conditions (0.0) - only hard exclusions
    if has_mission_mismatch:
        return 0.0
    if application_type == "invite_only":
        return 0.0

    # READY tier conditions (0.85-1.0)
    if accepts_unsolicited is True:
        base_mult = 0.95
        if application_type in ("open", "loi"):
            base_mult = 1.0 if has_deadline else 0.95
        elif application_type == "rfp_periodic" and has_deadline:
            base_mult = 1.0
        elif application_type == "rfp_rolling":
            base_mult = 0.90

        # Reduce slightly for each red flag (but not to zero)
        penalty = min(len(red_flags) * 0.05, 0.15)  # Max 15% reduction
        return max(0.7, base_mult - penalty)

    # CONDITIONAL tier (0.5-0.7)
    if application_type == "unknown":
        return 0.6
    if accepts_unsolicited is None:
        # Unknown policy - penalize slightly for red flags
        base = 0.6
        penalty = min(len(red_flags) * 0.05, 0.1)
        return max(0.4, base - penalty)

    # WATCH tier (0.2-0.3) - closed to unsolicited
    if accepts_unsolicited is False:
        if application_type == "rfp_periodic":
            return 0.3  # Can still respond to RFPs
        return 0.2

    # Default
    return 0.5


def upsert_enrichment(conn, enrichment: dict, enriched_by: str = "claude_code_cli") -> bool:
    """
    Insert or update enrichment record.

    Returns: True if successful
    """
    ein = str(enrichment.get("ein") or enrichment.get("foundation_ein", ""))
    if not ein:
        print(f"ERROR: No EIN provided in enrichment data")
        return False

    # Calculate viability multiplier
    multiplier = calculate_viability_multiplier(enrichment)

    # Prepare red_flags as JSONB
    red_flags = enrichment.get("red_flags", [])
    if isinstance(red_flags, str):
        red_flags = [red_flags]

    # Parse deadline if string
    current_deadline = enrichment.get("current_deadline")
    if isinstance(current_deadline, str) and current_deadline:
        # Try to parse various date formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"]:
            try:
                current_deadline = datetime.strptime(current_deadline, fmt).date()
                break
            except ValueError:
                continue
        else:
            current_deadline = None  # Couldn't parse

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO f990_2025.foundation_enrichment (
                ein,
                accepts_unsolicited,
                application_type,
                application_url,
                current_deadline,
                deadline_notes,
                contact_name,
                contact_title,
                contact_email,
                contact_phone,
                contact_source,
                program_priorities,
                geographic_focus,
                grant_range_stated,
                application_requirements,
                red_flags,
                enrichment_source,
                last_enriched,
                enriched_by,
                enrichment_notes,
                last_verified,
                verification_notes,
                viability_multiplier
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (ein) DO UPDATE SET
                accepts_unsolicited = EXCLUDED.accepts_unsolicited,
                application_type = EXCLUDED.application_type,
                application_url = EXCLUDED.application_url,
                current_deadline = EXCLUDED.current_deadline,
                deadline_notes = EXCLUDED.deadline_notes,
                contact_name = EXCLUDED.contact_name,
                contact_title = EXCLUDED.contact_title,
                contact_email = EXCLUDED.contact_email,
                contact_phone = EXCLUDED.contact_phone,
                contact_source = EXCLUDED.contact_source,
                program_priorities = EXCLUDED.program_priorities,
                geographic_focus = EXCLUDED.geographic_focus,
                grant_range_stated = EXCLUDED.grant_range_stated,
                application_requirements = EXCLUDED.application_requirements,
                red_flags = EXCLUDED.red_flags,
                enrichment_source = EXCLUDED.enrichment_source,
                last_enriched = EXCLUDED.last_enriched,
                enriched_by = EXCLUDED.enriched_by,
                enrichment_notes = EXCLUDED.enrichment_notes,
                last_verified = EXCLUDED.last_verified,
                verification_notes = EXCLUDED.verification_notes,
                viability_multiplier = EXCLUDED.viability_multiplier
        """, (
            ein,
            enrichment.get("accepts_unsolicited"),
            enrichment.get("application_type"),
            enrichment.get("application_url"),
            current_deadline,
            enrichment.get("deadline_notes"),
            enrichment.get("contact_name"),
            enrichment.get("contact_title"),
            enrichment.get("contact_email"),
            enrichment.get("contact_phone"),
            enrichment.get("contact_source"),
            enrichment.get("program_priorities"),
            enrichment.get("geographic_focus"),
            enrichment.get("grant_range_stated"),
            enrichment.get("application_requirements"),
            Json(red_flags),
            enrichment.get("enrichment_source"),
            datetime.now(),
            enriched_by,
            enrichment.get("enrichment_notes"),
            datetime.now(),  # Also set last_verified on new enrichment
            enrichment.get("verification_notes"),
            multiplier
        ))

    conn.commit()
    return True


def convert_old_enrichment(old_data: dict) -> dict:
    """
    Convert old 05b_enrichment.json format to new database format.
    """
    # Handle nested structure from old format
    how_to_apply = old_data.get("how_to_apply", {})
    contact = old_data.get("contact", {})
    deadlines = old_data.get("deadlines", {})
    fit = old_data.get("fit_assessment", {})

    # Determine application_type from old data
    process = (how_to_apply.get("process") or "").upper()
    if "NOT ACCEPT" in process or "DOES NOT ACCEPT" in process:
        accepts_unsolicited = False
        application_type = "invite_only"
    elif "RFP" in process:
        accepts_unsolicited = True
        application_type = "rfp_periodic"
    elif "LOI" in process or "LETTER" in process:
        accepts_unsolicited = True
        application_type = "loi"
    elif how_to_apply.get("portal_url"):
        accepts_unsolicited = True
        application_type = "open"
    else:
        accepts_unsolicited = None
        application_type = "unknown"

    # Extract deadline
    deadline_dates = deadlines.get("dates", [])
    current_deadline = None
    deadline_notes = deadlines.get("notes", "")

    for d in deadline_dates:
        if d and "20" in str(d):  # Has a year
            # Try to parse
            for fmt in ["%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"]:
                try:
                    current_deadline = datetime.strptime(str(d), fmt).date()
                    break
                except ValueError:
                    continue
            if current_deadline:
                break

    # Extract contact
    contact_name = contact.get("program_officer")
    contact_title = contact.get("program_officer_title")
    contact_email = contact.get("email")
    contact_phone = contact.get("phone")

    # Get red flags
    red_flags = fit.get("red_flags", [])

    # Map fit rating to notes
    fit_rating = fit.get("rating", "").lower()
    if fit_rating == "weak":
        if "mission_mismatch" not in [rf.lower().replace(" ", "_") for rf in red_flags]:
            # Check if any red flag suggests mission mismatch
            for rf in red_flags:
                if "mission" in rf.lower() or "focus" in rf.lower() or "not relevant" in rf.lower():
                    red_flags.append("mission_mismatch")
                    break

    # Normalize red flags
    normalized_flags = []
    for rf in red_flags:
        rf_lower = rf.lower()
        if "unsolicited" in rf_lower or "not accept" in rf_lower:
            normalized_flags.append("no_unsolicited")
        elif "mission" in rf_lower or "focus" in rf_lower:
            normalized_flags.append("mission_mismatch")
        elif "geographic" in rf_lower:
            normalized_flags.append("geographic_restriction")
        elif "small" in rf_lower or "grant" in rf_lower:
            normalized_flags.append("small_grants")
        elif "dormant" in rf_lower or "inactive" in rf_lower:
            normalized_flags.append("possibly_dormant")
        else:
            normalized_flags.append(rf[:50])  # Keep original if not recognized

    return {
        "ein": old_data.get("foundation_ein"),
        "accepts_unsolicited": accepts_unsolicited,
        "application_type": application_type,
        "application_url": how_to_apply.get("portal_url"),
        "current_deadline": current_deadline,
        "deadline_notes": deadline_notes or deadlines.get("type"),
        "contact_name": contact_name,
        "contact_title": contact_title,
        "contact_email": contact_email if contact_email and "@" in str(contact_email) else None,
        "contact_phone": str(contact_phone) if contact_phone else None,
        "contact_source": contact.get("website") or contact.get("website_verified"),
        "program_priorities": ", ".join(old_data.get("current_priorities", [])[:5]),
        "geographic_focus": old_data.get("geographic_focus"),
        "grant_range_stated": None,
        "application_requirements": how_to_apply.get("requirements") if isinstance(how_to_apply.get("requirements"), str) else "; ".join(how_to_apply.get("requirements", [])[:5]),
        "red_flags": list(set(normalized_flags))[:5],  # Dedupe and limit
        "enrichment_source": old_data.get("sources", [None])[0] if old_data.get("sources") else None,
        "enrichment_notes": fit.get("notes"),
        "verification_notes": f"Migrated from 05b_enrichment.json. Fit rating: {fit_rating}"
    }


def migrate_client_enrichment(client_short_name: str, run_date: str = None) -> int:
    """
    Migrate enrichment data from old 05b_enrichment.json files.

    Returns: Number of records migrated
    """
    # Find client
    registry = load_client_registry()
    client_entry = None
    for c in registry.get("clients", []):
        if (c["name"].lower() == client_short_name.lower() or
            c.get("short_name", "").lower() == client_short_name.lower()):
            client_entry = c
            break

    if not client_entry:
        print(f"ERROR: Client '{client_short_name}' not found")
        return 0

    client_name = client_entry["name"].replace(" ", "_")

    # Find enrichment file
    if run_date:
        run_dir = get_run_dir(client_name, run_date)
    else:
        # Find most recent run with enrichment file
        client_runs_dir = RUNS_DIR / client_name
        if not client_runs_dir.exists():
            print(f"ERROR: No runs found for {client_name}")
            return 0

        run_dirs = sorted(client_runs_dir.iterdir(), reverse=True)
        run_dir = None
        for rd in run_dirs:
            if (rd / "05b_enrichment.json").exists():
                run_dir = rd
                break

        if not run_dir:
            print(f"ERROR: No 05b_enrichment.json found for {client_name}")
            return 0

    enrichment_file = run_dir / "05b_enrichment.json"
    if not enrichment_file.exists():
        print(f"ERROR: File not found: {enrichment_file}")
        return 0

    print(f"Migrating enrichment from: {enrichment_file}")

    # Load and parse
    with open(enrichment_file) as f:
        data = json.load(f)

    # Handle different structures
    foundations = data.get("foundations", []) or data.get("enrichments", [])
    if not foundations:
        print(f"ERROR: No foundations found in {enrichment_file}")
        return 0

    # Migrate each foundation
    conn = get_db_connection()
    migrated = 0

    for old_enrichment in foundations:
        try:
            new_enrichment = convert_old_enrichment(old_enrichment)
            if upsert_enrichment(conn, new_enrichment, enriched_by="migration"):
                name = old_enrichment.get("foundation_name", old_enrichment.get("ein", "Unknown"))[:40]
                print(f"  ✅ Migrated: {name}")
                migrated += 1
        except Exception as e:
            name = old_enrichment.get("foundation_name", "Unknown")[:40]
            print(f"  ❌ Failed: {name} - {e}")

    conn.close()
    return migrated


def main():
    parser = argparse.ArgumentParser(
        description="Store foundation enrichment data in database"
    )

    # Input modes (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file", type=str, help="JSON file with enrichment data")
    input_group.add_argument("--migrate-client", type=str, help="Migrate from 05b_enrichment.json for client")
    input_group.add_argument("--ein", type=str, help="Single foundation EIN")

    # Single foundation fields
    parser.add_argument("--application-type", choices=["open", "loi", "rfp_periodic", "rfp_rolling", "invite_only", "unknown"])
    parser.add_argument("--accepts-unsolicited", action="store_true", default=None)
    parser.add_argument("--no-unsolicited", action="store_true")
    parser.add_argument("--application-url", type=str)
    parser.add_argument("--deadline", type=str, help="Current deadline (YYYY-MM-DD)")
    parser.add_argument("--contact-name", type=str)
    parser.add_argument("--contact-email", type=str)
    parser.add_argument("--contact-phone", type=str)
    parser.add_argument("--red-flags", type=str, help="Comma-separated red flags")
    parser.add_argument("--notes", type=str)

    # Migration options
    parser.add_argument("--run-date", type=str, help="Specific run date for migration (YYYY-MM-DD)")

    args = parser.parse_args()

    # Set up basic logging
    print("\n" + "=" * 70)
    print("Foundation Enrichment Storage")
    print("=" * 70)

    conn = get_db_connection()
    stored = 0

    if args.migrate_client:
        # Migration mode
        stored = migrate_client_enrichment(args.migrate_client, args.run_date)

    elif args.file:
        # Batch import from file
        with open(args.file) as f:
            data = json.load(f)

        # Handle list or dict with foundations key
        if isinstance(data, list):
            foundations = data
        else:
            foundations = data.get("foundations", [data])

        for enrichment in foundations:
            if upsert_enrichment(conn, enrichment):
                name = enrichment.get("foundation_name", enrichment.get("ein", "Unknown"))[:40]
                print(f"  ✅ Stored: {name}")
                stored += 1

    elif args.ein:
        # Single foundation mode
        enrichment = {
            "ein": args.ein,
            "application_type": args.application_type,
            "accepts_unsolicited": False if args.no_unsolicited else (True if args.accepts_unsolicited else None),
            "application_url": args.application_url,
            "current_deadline": args.deadline,
            "contact_name": args.contact_name,
            "contact_email": args.contact_email,
            "contact_phone": args.contact_phone,
            "red_flags": args.red_flags.split(",") if args.red_flags else [],
            "enrichment_notes": args.notes
        }

        if upsert_enrichment(conn, enrichment):
            print(f"  ✅ Stored enrichment for EIN: {args.ein}")
            stored = 1

    conn.close()

    # Summary
    print("=" * 70)
    print(f"Total records stored/updated: {stored}")
    print("=" * 70)

    if stored > 0:
        print("\nNext: Run 03_check_enrichment.py to verify status")
        print("      Then run 04_filter_viable.py to calculate viability tiers")


if __name__ == "__main__":
    main()
