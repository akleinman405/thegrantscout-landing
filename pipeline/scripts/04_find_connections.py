#!/usr/bin/env python3
"""
Script 04: Find Connections

Finds potential relationship angles between the client and each scored foundation.
This helps personalize outreach and identify warm introduction paths.

Usage:
    python scripts/04_find_connections.py --client "PSMF"
    python scripts/04_find_connections.py --client "Patient Safety Movement Foundation"
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Set

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.paths import get_run_dir, load_client_registry, setup_logging
from scripts.utils.db import query_df

# NTEE sector names
NTEE_NAMES = {
    "A": "Arts & Culture",
    "B": "Education",
    "C": "Environment",
    "D": "Animal-Related",
    "E": "Healthcare",
    "F": "Mental Health",
    "G": "Disease/Disorder",
    "H": "Medical Research",
    "I": "Crime/Legal",
    "J": "Employment",
    "K": "Food/Agriculture",
    "L": "Housing",
    "M": "Public Safety",
    "N": "Recreation/Sports",
    "O": "Youth Development",
    "P": "Human Services",
    "Q": "International",
    "R": "Civil Rights",
    "S": "Community Development",
    "T": "Philanthropy",
    "U": "Science/Tech",
    "V": "Social Science",
    "W": "Public Policy",
    "X": "Religion",
    "Y": "Mutual Benefit",
    "Z": "Unknown",
}

# Adjacent states mapping
ADJACENT_STATES = {
    "AL": ["FL", "GA", "MS", "TN"],
    "AK": [],
    "AZ": ["CA", "CO", "NM", "NV", "UT"],
    "AR": ["LA", "MO", "MS", "OK", "TN", "TX"],
    "CA": ["AZ", "NV", "OR"],
    "CO": ["AZ", "KS", "NE", "NM", "OK", "UT", "WY"],
    "CT": ["MA", "NY", "RI"],
    "DE": ["MD", "NJ", "PA"],
    "FL": ["AL", "GA"],
    "GA": ["AL", "FL", "NC", "SC", "TN"],
    "HI": [],
    "ID": ["MT", "NV", "OR", "UT", "WA", "WY"],
    "IL": ["IN", "IA", "KY", "MO", "WI"],
    "IN": ["IL", "KY", "MI", "OH"],
    "IA": ["IL", "MN", "MO", "NE", "SD", "WI"],
    "KS": ["CO", "MO", "NE", "OK"],
    "KY": ["IL", "IN", "MO", "OH", "TN", "VA", "WV"],
    "LA": ["AR", "MS", "TX"],
    "ME": ["NH"],
    "MD": ["DE", "PA", "VA", "WV", "DC"],
    "MA": ["CT", "NH", "NY", "RI", "VT"],
    "MI": ["IN", "OH", "WI"],
    "MN": ["IA", "ND", "SD", "WI"],
    "MS": ["AL", "AR", "LA", "TN"],
    "MO": ["AR", "IL", "IA", "KS", "KY", "NE", "OK", "TN"],
    "MT": ["ID", "ND", "SD", "WY"],
    "NE": ["CO", "IA", "KS", "MO", "SD", "WY"],
    "NV": ["AZ", "CA", "ID", "OR", "UT"],
    "NH": ["MA", "ME", "VT"],
    "NJ": ["DE", "NY", "PA"],
    "NM": ["AZ", "CO", "OK", "TX", "UT"],
    "NY": ["CT", "MA", "NJ", "PA", "VT"],
    "NC": ["GA", "SC", "TN", "VA"],
    "ND": ["MN", "MT", "SD"],
    "OH": ["IN", "KY", "MI", "PA", "WV"],
    "OK": ["AR", "CO", "KS", "MO", "NM", "TX"],
    "OR": ["CA", "ID", "NV", "WA"],
    "PA": ["DE", "MD", "NJ", "NY", "OH", "WV"],
    "RI": ["CT", "MA"],
    "SC": ["GA", "NC"],
    "SD": ["IA", "MN", "MT", "ND", "NE", "WY"],
    "TN": ["AL", "AR", "GA", "KY", "MO", "MS", "NC", "VA"],
    "TX": ["AR", "LA", "NM", "OK"],
    "UT": ["AZ", "CO", "ID", "NV", "NM", "WY"],
    "VT": ["MA", "NH", "NY"],
    "VA": ["KY", "MD", "NC", "TN", "WV", "DC"],
    "WA": ["ID", "OR"],
    "WV": ["KY", "MD", "OH", "PA", "VA"],
    "WI": ["IL", "IA", "MI", "MN"],
    "WY": ["CO", "ID", "MT", "NE", "SD", "UT"],
    "DC": ["MD", "VA"],
}


def normalize_name(name: str) -> str:
    """Normalize name for comparison (lowercase, remove titles, etc.)"""
    if not name:
        return ""
    name = name.lower().strip()
    # Remove common titles
    for title in ["dr.", "dr ", "mr.", "mr ", "ms.", "ms ", "mrs.", "mrs ", "jr.", "jr", "sr.", "sr", "iii", "ii", "iv"]:
        name = name.replace(title, "")
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    # Normalize whitespace
    name = ' '.join(name.split())
    return name


def are_adjacent_states(state1: str, state2: str) -> bool:
    """Check if two states are adjacent."""
    if not state1 or not state2:
        return False
    return state2 in ADJACENT_STATES.get(state1, []) or state1 in ADJACENT_STATES.get(state2, [])


def find_board_overlap(foundation_ein: str, client_officers: Set[str]) -> List[Dict]:
    """Find overlapping board members between foundation and client."""
    if not client_officers:
        return []

    sql = """
    SELECT person_nm as person_name
    FROM f990_2025.officers
    WHERE ein = %(ein)s
    """
    try:
        foundation_officers = query_df(sql, {"ein": foundation_ein})
    except Exception:
        return []

    connections = []
    for _, row in foundation_officers.iterrows():
        person_name = row.get("person_name", "")
        if not person_name:
            continue
        normalized = normalize_name(person_name)
        if normalized and normalized in client_officers:
            connections.append({
                "type": "board_overlap",
                "description": f"{person_name} serves on both boards",
                "strength": "strong",
                "person": person_name,
            })

    return connections


def find_shared_funders(foundation_ein: str, client_ein: str) -> List[Dict]:
    """Find foundations that fund both the client and this foundation's grantees."""
    if not client_ein:
        return []

    sql = """
    WITH client_funders AS (
        SELECT DISTINCT foundation_ein
        FROM f990_2025.fact_grants
        WHERE recipient_ein = %(client_ein)s
    ),
    foundation_grantees AS (
        SELECT DISTINCT recipient_ein
        FROM f990_2025.fact_grants
        WHERE foundation_ein = %(foundation_ein)s
    ),
    shared AS (
        SELECT DISTINCT cf.foundation_ein, f.name as funder_name
        FROM client_funders cf
        JOIN f990_2025.fact_grants g ON cf.foundation_ein = g.foundation_ein
        JOIN foundation_grantees fg ON g.recipient_ein = fg.recipient_ein
        JOIN f990_2025.dim_foundations f ON cf.foundation_ein = f.ein
        WHERE cf.foundation_ein != %(foundation_ein)s
        LIMIT 3
    )
    SELECT * FROM shared
    """

    try:
        shared = query_df(sql, {"client_ein": client_ein, "foundation_ein": foundation_ein})
    except Exception:
        return []

    connections = []
    for _, row in shared.iterrows():
        funder_name = row.get("funder_name", "Unknown")
        connections.append({
            "type": "shared_funder",
            "description": f"{funder_name} has funded both you and their grantees",
            "strength": "moderate",
            "funder_name": funder_name,
            "funder_ein": row.get("foundation_ein", ""),
        })

    return connections


def find_geographic_connection(foundation_state: str, client_state: str) -> List[Dict]:
    """Assess geographic connection strength."""
    if not foundation_state or not client_state:
        return []

    connections = []

    if foundation_state == client_state:
        connections.append({
            "type": "geographic",
            "description": f"Both based in {client_state}",
            "strength": "strong",
        })
    elif are_adjacent_states(foundation_state, client_state):
        connections.append({
            "type": "geographic",
            "description": f"Foundation in {foundation_state}, adjacent to your {client_state}",
            "strength": "moderate",
        })

    return connections


def find_sector_alignment(foundation_ein: str, client_ntee: str) -> List[Dict]:
    """Check if foundation funds client's sector."""
    if not client_ntee:
        return []

    sql = """
    WITH sector_distribution AS (
        SELECT
            LEFT(r.ntee_code, 1) as sector,
            COUNT(*) as grant_count
        FROM f990_2025.fact_grants g
        JOIN f990_2025.dim_recipients r ON g.recipient_ein = r.ein
        WHERE g.foundation_ein = %(ein)s
          AND r.ntee_code IS NOT NULL
          AND r.ntee_code != ''
        GROUP BY LEFT(r.ntee_code, 1)
    ),
    total AS (
        SELECT SUM(grant_count) as total FROM sector_distribution
    )
    SELECT
        sd.sector,
        sd.grant_count,
        sd.grant_count * 1.0 / NULLIF(t.total, 0) as pct
    FROM sector_distribution sd
    CROSS JOIN total t
    WHERE sd.sector = %(ntee)s
    """

    try:
        result = query_df(sql, {"ein": foundation_ein, "ntee": client_ntee})
    except Exception:
        return []

    connections = []
    if not result.empty:
        pct = float(result.iloc[0].get("pct", 0) or 0)
        sector_name = NTEE_NAMES.get(client_ntee, client_ntee)

        if pct >= 0.3:
            connections.append({
                "type": "sector_alignment",
                "description": f"Foundation funds {pct:.0%} {sector_name} organizations",
                "strength": "strong",
                "sector": client_ntee,
                "percentage": round(pct, 3),
            })
        elif pct >= 0.1:
            connections.append({
                "type": "sector_alignment",
                "description": f"Foundation funds {pct:.0%} {sector_name} organizations",
                "strength": "moderate",
                "sector": client_ntee,
                "percentage": round(pct, 3),
            })

    return connections


def main():
    parser = argparse.ArgumentParser(description="Find connections between client and scored foundations")
    parser.add_argument("--client", required=True, help="Client name or short_name")
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
    logger = setup_logging(client_name, "04_find_connections")
    logger.info(f"[04_find_connections] Starting for {client_entry['name']}")

    # Find run directory
    run_dir = get_run_dir(client_name, args.date)
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)

    logger.info(f"Using run directory: {run_dir}")

    # Load client data
    client_file = run_dir / "01_client.json"
    if not client_file.exists():
        print(f"ERROR: Client file not found: {client_file}")
        sys.exit(1)

    with open(client_file) as f:
        client = json.load(f)

    # Extract client attributes
    client_ein = client.get("ein", "")
    client_state = client.get("state", "")
    client_ntee = (client.get("ntee_code", "") or "")[:1]  # Major category only

    # Build set of normalized client officer names
    client_officers_raw = client.get("officers", [])
    if isinstance(client_officers_raw, list) and client_officers_raw:
        # Handle both list of strings and list of dicts
        if isinstance(client_officers_raw[0], dict):
            client_officers = set(normalize_name(o.get("person_nm", "") or o.get("name", "")) for o in client_officers_raw)
        else:
            client_officers = set(normalize_name(n) for n in client_officers_raw)
    else:
        client_officers = set()

    # Remove empty strings
    client_officers.discard("")

    logger.info(f"Client EIN: {client_ein}, State: {client_state}, NTEE: {client_ntee}")
    logger.info(f"[04_find_connections] Client has {len(client_officers)} officers to check for board overlap")

    # Load scored foundations
    scored_file = run_dir / "02_scored_foundations.csv"
    if not scored_file.exists():
        print(f"ERROR: Scored foundations not found: {scored_file}")
        sys.exit(1)

    foundations_df = pd.read_csv(scored_file, dtype={"foundation_ein": str})

    logger.info(f"[04_find_connections] Processing {len(foundations_df)} foundations")
    print(f"\nProcessing {len(foundations_df)} foundations...")

    # Find connections for each foundation
    connections = {}
    stats = {"board_overlap": 0, "shared_funder": 0, "geographic": 0, "sector_alignment": 0}

    for i, (_, foundation) in enumerate(foundations_df.iterrows(), 1):
        f_ein = str(foundation["foundation_ein"])
        f_state = foundation.get("foundation_state", "")

        found_connections = []

        # Check each connection type
        board = find_board_overlap(f_ein, client_officers)
        found_connections.extend(board)
        stats["board_overlap"] += len(board)

        shared = find_shared_funders(f_ein, client_ein)
        found_connections.extend(shared)
        stats["shared_funder"] += len(shared)

        geo = find_geographic_connection(f_state, client_state)
        found_connections.extend(geo)
        stats["geographic"] += len(geo)

        sector = find_sector_alignment(f_ein, client_ntee)
        found_connections.extend(sector)
        stats["sector_alignment"] += len(sector)

        connections[f_ein] = found_connections

        # Log progress every 10 foundations
        if i % 10 == 0 or i == len(foundations_df):
            print(f"  [{i}/{len(foundations_df)}] {foundation['foundation_name'][:40]}")

    # Save output
    output_file = run_dir / "04_connections.json"
    with open(output_file, "w") as f:
        json.dump(connections, f, indent=2)

    logger.info(f"[04_find_connections] Found connections:")
    logger.info(f"  - Board overlap: {stats['board_overlap']}")
    logger.info(f"  - Shared funders: {stats['shared_funder']}")
    logger.info(f"  - Geographic: {stats['geographic']}")
    logger.info(f"  - Sector alignment: {stats['sector_alignment']}")
    logger.info(f"[04_find_connections] Saved connections to {output_file}")

    # Summary
    foundations_with_connections = sum(1 for c in connections.values() if c)
    total_connections = sum(len(c) for c in connections.values())

    print(f"\n{'='*60}")
    print("Connections found!")
    print(f"{'='*60}")
    print(f"Client: {client_entry['name']}")
    print(f"Foundations processed: {len(connections)}")
    print(f"Foundations with connections: {foundations_with_connections}")
    print(f"Total connections: {total_connections}")
    print(f"\nBy type:")
    print(f"  Board overlap: {stats['board_overlap']}")
    print(f"  Shared funders: {stats['shared_funder']}")
    print(f"  Geographic: {stats['geographic']}")
    print(f"  Sector alignment: {stats['sector_alignment']}")
    print(f"\nOutput: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
