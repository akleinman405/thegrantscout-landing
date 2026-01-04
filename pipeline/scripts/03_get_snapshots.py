#!/usr/bin/env python3
"""
Script 03: Get Funder Snapshots

Runs 8 SQL queries per foundation to build rich funder intelligence snapshots.

Usage:
    python scripts/03_get_snapshots.py --client "PSMF"
    python scripts/03_get_snapshots.py --client "PSMF" --limit 20
    python scripts/03_get_snapshots.py --client "PSMF" --skip-cache
"""

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.paths import get_run_dir, load_client_registry, setup_logging
from scripts.utils.db import query_df

# Constants
PIPELINE_ROOT = Path(__file__).parent.parent
SQL_DIR = PIPELINE_ROOT / "sql"

# Garbage values to filter from comparable grants
GARBAGE_RECIPIENTS = [
    "SEE ATTACHED SCHEDULE",
    "SEE STATEMENT",
    "SEE ATTACHED",
    "VARIOUS",
    "VARIOUS INDIVIDUALS",
    "MULTIPLE RECIPIENTS",
    "SEE SCHEDULE",
    "INDIVIDUAL PATIENT PROGRAMS",
    "",
]

# Garbage values to filter from contact/URL fields
GARBAGE_VALUES = ["N/A", "NONE", "0", "N A", "NA", ""]


def load_sql_templates() -> dict:
    """Load all SQL templates from sql/ directory."""
    templates = {}
    for sql_file in SQL_DIR.glob("*.sql"):
        templates[sql_file.stem] = sql_file.read_text()
    return templates


def get_annual_giving(ein: str, sql: str) -> dict:
    """Query 1: Annual giving for most recent year."""
    try:
        df = query_df(sql, {"foundation_ein": ein})
        if df.empty:
            return {"total": 0, "count": 0, "year": None}
        row = df.iloc[0]
        return {
            "total": float(row.get("total_giving", 0) or 0),
            "count": int(row.get("grant_count", 0) or 0),
            "year": int(row.get("tax_year")) if pd.notna(row.get("tax_year")) else None,
        }
    except Exception as e:
        logging.debug(f"annual_giving error for {ein}: {e}")
        return {"total": 0, "count": 0, "year": None}


def get_typical_grant(ein: str, sql: str) -> dict:
    """Query 2: Typical grant statistics."""
    try:
        df = query_df(sql, {"foundation_ein": ein})
        if df.empty:
            return {"median": 0, "min": 0, "max": 0, "avg": 0}
        row = df.iloc[0]
        return {
            "median": float(row.get("median_grant", 0) or 0),
            "min": float(row.get("min_grant", 0) or 0),
            "max": min(float(row.get("max_grant", 0) or 0), 10000000),  # Cap at $10M
            "avg": float(row.get("avg_grant", 0) or 0),
        }
    except Exception as e:
        logging.debug(f"typical_grant error for {ein}: {e}")
        return {"median": 0, "min": 0, "max": 0, "avg": 0}


def get_geographic_focus(ein: str, sql: str) -> dict:
    """Query 3: Geographic focus - top state and in-state percentage."""
    try:
        df = query_df(sql, {"foundation_ein": ein})
        if df.empty:
            return {"top_state": None, "top_state_pct": 0, "in_state_pct": 0, "foundation_state": None}
        row = df.iloc[0]
        return {
            "top_state": row.get("top_state"),
            "top_state_pct": round(float(row.get("top_state_pct", 0) or 0), 3),
            "in_state_pct": round(float(row.get("in_state_pct", 0) or 0), 3),
            "foundation_state": row.get("foundation_state"),
        }
    except Exception as e:
        logging.debug(f"geographic_focus error for {ein}: {e}")
        return {"top_state": None, "top_state_pct": 0, "in_state_pct": 0, "foundation_state": None}


def get_repeat_funding(ein: str, sql: str) -> dict:
    """Query 4: Repeat funding rate."""
    try:
        df = query_df(sql, {"foundation_ein": ein})
        if df.empty:
            return {"unique": 0, "repeat": 0, "rate": 0}
        row = df.iloc[0]
        unique = int(row.get("unique_recipients", 0) or 0)
        repeat = int(row.get("repeat_recipients", 0) or 0)
        rate = float(row.get("repeat_rate", 0) or 0)
        return {
            "unique": unique,
            "repeat": repeat,
            "rate": round(rate, 3),
        }
    except Exception as e:
        logging.debug(f"repeat_funding error for {ein}: {e}")
        return {"unique": 0, "repeat": 0, "rate": 0}


def get_giving_style(ein: str, sql: str) -> dict:
    """Query 5: General vs program-specific support."""
    try:
        df = query_df(sql, {"foundation_ein": ein})
        if df.empty:
            return {"general_pct": 0.5, "program_pct": 0.5}
        row = df.iloc[0]
        general_pct = float(row.get("general_support_pct", 0.5) or 0.5)
        return {
            "general_pct": round(general_pct, 3),
            "program_pct": round(1 - general_pct, 3),
        }
    except Exception as e:
        logging.debug(f"giving_style error for {ein}: {e}")
        return {"general_pct": 0.5, "program_pct": 0.5}


def get_recipient_profile(ein: str, sql: str) -> dict:
    """Query 6: Typical recipient profile."""
    try:
        df = query_df(sql, {"foundation_ein": ein})
        if df.empty:
            return {"budget_min": 0, "budget_max": 0, "budget_median": 0, "primary_sector": None, "primary_sector_pct": 0}
        row = df.iloc[0]
        return {
            "budget_min": int(row.get("typical_budget_min", 0) or 0),
            "budget_max": int(row.get("typical_budget_max", 0) or 0),
            "budget_median": int(row.get("median_budget", 0) or 0),
            "primary_sector": row.get("primary_sector"),
            "primary_sector_pct": round(float(row.get("primary_sector_pct", 0) or 0), 3),
        }
    except Exception as e:
        logging.debug(f"recipient_profile error for {ein}: {e}")
        return {"budget_min": 0, "budget_max": 0, "budget_median": 0, "primary_sector": None, "primary_sector_pct": 0}


def get_funding_trend(ein: str, sql: str) -> dict:
    """Query 7: 3-year funding trend."""
    try:
        df = query_df(sql, {"foundation_ein": ein})
        if df.empty:
            return {"direction": "Unknown", "change_pct": 0, "oldest_year": None, "newest_year": None}
        row = df.iloc[0]
        return {
            "direction": row.get("trend", "Stable"),
            "change_pct": round(float(row.get("change_pct", 0) or 0), 3),
            "oldest_year": int(row.get("oldest_year")) if pd.notna(row.get("oldest_year")) else None,
            "newest_year": int(row.get("newest_year")) if pd.notna(row.get("newest_year")) else None,
        }
    except Exception as e:
        logging.debug(f"funding_trend error for {ein}: {e}")
        return {"direction": "Unknown", "change_pct": 0, "oldest_year": None, "newest_year": None}


def get_comparable_grant(ein: str, sql: str, client_state: str, client_ntee: str) -> Optional[dict]:
    """Query 8: Find a comparable grant to a similar organization."""
    try:
        df = query_df(sql, {
            "foundation_ein": ein,
            "client_state": client_state,
            "client_ntee": client_ntee[:1] if client_ntee else "",
        })
        if df.empty:
            return None
        row = df.iloc[0]
        recipient = row.get("recipient_name", "")
        purpose = row.get("grant_purpose") or ""
        amount = float(row.get("grant_amount", 0) or 0)
        year = int(row.get("grant_year")) if pd.notna(row.get("grant_year")) else None

        # If recipient is garbage but we have meaningful purpose, show purpose-only
        if not recipient or recipient.upper().strip() in GARBAGE_RECIPIENTS:
            if purpose and len(purpose) > 20:
                return {
                    "recipient": "[Various recipients]",
                    "amount": amount,
                    "purpose": purpose,
                    "year": year,
                }
            return None

        return {
            "recipient": recipient,
            "amount": amount,
            "purpose": purpose,
            "year": year,
        }
    except Exception as e:
        logging.debug(f"comparable_grant error for {ein}: {e}")
        return None


def clean_value(value: str) -> Optional[str]:
    """Clean a value, returning None if it's garbage."""
    if not value:
        return None
    cleaned = str(value).strip()
    if cleaned.upper() in GARBAGE_VALUES:
        return None
    return cleaned


def get_foundation_contact(ein: str) -> dict:
    """Query 9: Get contact and application info from pf_returns."""
    sql = """
    SELECT
        website_url,
        phone_num,
        email_address_txt,
        app_contact_name,
        app_contact_phone,
        app_contact_email,
        app_submission_deadlines,
        app_restrictions,
        app_form_requirements
    FROM f990_2025.pf_returns
    WHERE ein = %(ein)s
    ORDER BY tax_year DESC
    LIMIT 1
    """
    try:
        df = query_df(sql, {"ein": ein})
        if df.empty:
            return {
                "website_url": None,
                "phone": None,
                "email": None,
                "app_contact_name": None,
                "app_contact_phone": None,
                "app_contact_email": None,
                "deadlines": None,
                "restrictions": None,
                "how_to_apply": None,
            }
        row = df.iloc[0]

        # Clean and normalize website URL
        website = clean_value(row.get("website_url"))
        if website and not website.lower().startswith(("http://", "https://")):
            website = f"https://{website}"

        return {
            "website_url": website,
            "phone": clean_value(row.get("phone_num")),
            "email": clean_value(row.get("email_address_txt")),
            "app_contact_name": clean_value(row.get("app_contact_name")),
            "app_contact_phone": clean_value(row.get("app_contact_phone")),
            "app_contact_email": clean_value(row.get("app_contact_email")),
            "deadlines": clean_value(row.get("app_submission_deadlines")),
            "restrictions": clean_value(row.get("app_restrictions")),
            "how_to_apply": clean_value(row.get("app_form_requirements")),
        }
    except Exception as e:
        logging.debug(f"foundation_contact error for {ein}: {e}")
        return {
            "website_url": None,
            "phone": None,
            "email": None,
            "app_contact_name": None,
            "app_contact_phone": None,
            "app_contact_email": None,
            "deadlines": None,
            "restrictions": None,
            "how_to_apply": None,
        }


def get_foundation_officers(ein: str) -> list:
    """Query 10: Get foundation officers/trustees from officers table."""
    sql = """
    SELECT DISTINCT ON (person_nm)
        person_nm as name,
        title_txt as title,
        compensation_amt as compensation
    FROM f990_2025.officers
    WHERE ein = %(ein)s
      AND form_type = '990PF'
      AND tax_year = (
          SELECT MAX(tax_year)
          FROM f990_2025.officers
          WHERE ein = %(ein)s AND form_type = '990PF'
      )
    ORDER BY person_nm, compensation_amt DESC NULLS LAST
    LIMIT 5
    """
    try:
        df = query_df(sql, {"ein": ein})
        if df.empty:
            return []

        officers = []
        for _, row in df.iterrows():
            name = row.get("name")
            if name:
                officers.append({
                    "name": name.title() if name.isupper() else name,
                    "title": row.get("title", "").title() if row.get("title", "").isupper() else row.get("title", ""),
                    "compensation": float(row.get("compensation", 0) or 0),
                })
        return officers
    except Exception as e:
        logging.debug(f"foundation_officers error for {ein}: {e}")
        return []


def build_snapshot(ein: str, sql_templates: dict, client_state: str, client_ntee: str) -> dict:
    """Build complete snapshot for a foundation."""
    snapshot = {
        "annual_giving": get_annual_giving(ein, sql_templates["annual_giving"]),
        "typical_grant": get_typical_grant(ein, sql_templates["typical_grant"]),
        "geographic_focus": get_geographic_focus(ein, sql_templates["geographic_focus"]),
        "repeat_funding": get_repeat_funding(ein, sql_templates["repeat_funding"]),
        "giving_style": get_giving_style(ein, sql_templates["giving_style"]),
        "recipient_profile": get_recipient_profile(ein, sql_templates["recipient_profile"]),
        "funding_trend": get_funding_trend(ein, sql_templates["funding_trend"]),
        "comparable_grant": get_comparable_grant(ein, sql_templates["comparable_grant"], client_state, client_ntee),
        # New: contact and application info from 990-PF
        "contact": get_foundation_contact(ein),
        # New: foundation officers/trustees
        "officers": get_foundation_officers(ein),
    }
    return snapshot


def clean_snapshot(snapshot: dict) -> dict:
    """Apply data quality filters to snapshot."""
    # Cap unrealistic grant amounts
    if snapshot.get("typical_grant"):
        tg = snapshot["typical_grant"]
        if tg.get("max", 0) > 10000000:
            tg["max"] = 10000000
        if tg.get("median", 0) > 5000000:
            tg["median"] = tg.get("avg", tg["median"])

    # Filter garbage comparable grants (already done in get_comparable_grant, but double-check)
    if snapshot.get("comparable_grant"):
        recipient = snapshot["comparable_grant"].get("recipient", "")
        if not recipient or recipient.upper().strip() in GARBAGE_RECIPIENTS:
            snapshot["comparable_grant"] = None

    return snapshot


def main():
    parser = argparse.ArgumentParser(description="Get funder snapshots for scored foundations")
    parser.add_argument("--client", required=True, help="Client name or short_name")
    parser.add_argument("--limit", type=int, default=50, help="Number of foundations to process")
    parser.add_argument("--date", default=date.today().isoformat(), help="Run date (YYYY-MM-DD)")
    parser.add_argument("--skip-cache", action="store_true", help="Re-run queries even if cached")
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
    logger = setup_logging(client_name, "03_get_snapshots")
    logger.info(f"[03_get_snapshots] Starting for {client_entry['name']}")

    # Find run directory
    run_dir = get_run_dir(client_name, args.date)
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)

    logger.info(f"Using run directory: {run_dir}")

    # Check for cached output
    output_file = run_dir / "03_snapshots.json"
    if output_file.exists() and not args.skip_cache:
        print(f"Output already exists: {output_file}")
        print("Use --skip-cache to regenerate")
        sys.exit(0)

    # Load client data
    client_file = run_dir / "01_client.json"
    if not client_file.exists():
        print(f"ERROR: Client file not found: {client_file}")
        print("Run script 01 first: python scripts/01_load_client.py --client '{}'".format(args.client))
        sys.exit(1)

    with open(client_file) as f:
        client = json.load(f)

    client_state = client.get("state", "")
    client_ntee = client.get("ntee_code", "")[:1] if client.get("ntee_code") else ""

    logger.info(f"Client state: {client_state}, NTEE: {client_ntee}")

    # Load scored foundations
    scored_file = run_dir / "02_scored_foundations.csv"
    if not scored_file.exists():
        print(f"ERROR: Scored foundations not found: {scored_file}")
        print("Run script 02 first: python scripts/02_score_foundations.py --client '{}'".format(args.client))
        sys.exit(1)

    foundations_df = pd.read_csv(scored_file, dtype={"foundation_ein": str})
    foundations = foundations_df.head(args.limit).to_dict("records")

    logger.info(f"[03_get_snapshots] Processing {len(foundations)} foundations")
    print(f"\nProcessing {len(foundations)} foundations...")

    # Load SQL templates
    sql_templates = load_sql_templates()
    logger.info(f"Loaded {len(sql_templates)} SQL templates")

    # Process each foundation
    snapshots = []
    garbage_count = 0

    for i, foundation in enumerate(foundations, 1):
        ein = str(foundation["foundation_ein"])  # Ensure string for SQL queries
        name = foundation["foundation_name"]

        # Build snapshot
        snapshot = build_snapshot(ein, sql_templates, client_state, client_ntee)
        snapshot = clean_snapshot(snapshot)

        # Add foundation identifiers
        snapshot["foundation_ein"] = ein
        snapshot["foundation_name"] = name
        snapshot["match_score"] = foundation.get("match_score", 0)
        snapshot["match_rank"] = foundation.get("match_rank", i)

        # Track garbage comparable grants
        if snapshot.get("comparable_grant") is None:
            garbage_count += 1

        snapshots.append(snapshot)

        # Log progress every 10 foundations
        if i % 10 == 0 or i == len(foundations):
            logger.info(f"[{i}/{len(foundations)}] Completed {name}")
            print(f"  [{i}/{len(foundations)}] {name}")

    # Save output
    with open(output_file, "w") as f:
        json.dump(snapshots, f, indent=2)

    logger.info(f"Data quality: {garbage_count} foundations had no comparable grants")
    logger.info(f"Saved {len(snapshots)} snapshots to {output_file}")

    # Print summary
    print(f"\n{'='*60}")
    print("Snapshots complete!")
    print(f"{'='*60}")
    print(f"Client: {client_entry['name']}")
    print(f"Foundations processed: {len(snapshots)}")
    print(f"No comparable grant: {garbage_count}")
    print(f"\nOutput: {output_file}")
    print(f"{'='*60}")

    # Show sample of first snapshot
    if snapshots:
        sample = snapshots[0]
        print(f"\nSample snapshot: {sample['foundation_name']}")
        print(f"  Annual giving: ${sample['annual_giving']['total']:,.0f} ({sample['annual_giving']['count']} grants)")
        print(f"  Typical grant: ${sample['typical_grant']['median']:,.0f} median")
        print(f"  Geographic: {sample['geographic_focus']['top_state']} ({sample['geographic_focus']['top_state_pct']:.1%})")
        print(f"  Repeat rate: {sample['repeat_funding']['rate']:.1%}")
        print(f"  Giving style: {sample['giving_style']['general_pct']:.0%} general support")
        print(f"  Funding trend: {sample['funding_trend']['direction']}")
        if sample.get("comparable_grant"):
            cg = sample["comparable_grant"]
            print(f"  Comparable: {cg['recipient'][:40]} - ${cg['amount']:,.0f}")
        # New: Show contact info summary
        contact = sample.get("contact", {})
        if contact.get("website_url"):
            print(f"  Website: {contact['website_url']}")
        if contact.get("phone"):
            print(f"  Phone: {contact['phone']}")
        if contact.get("app_contact_name"):
            print(f"  App Contact: {contact['app_contact_name']}")
        officers = sample.get("officers", [])
        if officers:
            print(f"  Officers: {len(officers)} found (e.g., {officers[0]['name']})")


if __name__ == "__main__":
    main()
