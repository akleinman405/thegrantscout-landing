#!/usr/bin/env python3
"""
01_load_client.py - Load and enrich client data

Usage:
    python scripts/01_load_client.py --client "Patient Safety Movement Foundation"
    python scripts/01_load_client.py --client "PSMF"
    python scripts/01_load_client.py --ein "474667797"
    python scripts/01_load_client.py --client "PSMF" --questionnaire ./custom.csv
"""
import argparse
import csv
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils import query_df, get_run_dir, CONFIG_DIR, DATA_DIR, LOGS_DIR


# State name to abbreviation mapping
STATE_ABBR = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
    'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
    'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
    'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
    'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
    'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
    'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
    'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
    'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
    'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
    'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC'
}


def setup_logging(client_name: str) -> logging.Logger:
    """Set up logging for this run."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = client_name.replace(" ", "_")[:20]
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_{safe_name}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def parse_budget(budget_str: str) -> float:
    """
    Parse budget string to numeric midpoint.

    Examples:
        "$100,000 - $500,000" -> 300000
        "$1M - $5M" -> 3000000
        "Under $100K" -> 50000
        "Over $10M" -> 15000000
    """
    if not budget_str:
        return 0.0

    budget_str = budget_str.lower().strip()

    # Handle "over" cases
    if 'over' in budget_str:
        if '$10m' in budget_str or '10,000,000' in budget_str:
            return 15000000.0
        if '$1,000,000' in budget_str or '$1m' in budget_str:
            return 2000000.0
        if '$500,000' in budget_str or '$500k' in budget_str:
            return 750000.0

    # Handle "under" cases
    if 'under' in budget_str:
        if '$100' in budget_str:
            return 50000.0
        if '$500' in budget_str:
            return 250000.0

    # Handle range patterns like "$1M - $5M" or "$100,000 - $500,000"
    if '-' in budget_str:
        # Extract numbers
        numbers = re.findall(r'\$?([\d,]+(?:\.\d+)?)\s*([kmb])?', budget_str)
        if len(numbers) >= 2:
            def parse_number(match):
                num_str, suffix = match
                num = float(num_str.replace(',', ''))
                multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000}
                return num * multipliers.get(suffix, 1)

            low = parse_number(numbers[0])
            high = parse_number(numbers[1])
            return (low + high) / 2

    # Fallback patterns
    if '$10m' in budget_str:
        return 25000000.0
    if '$5m' in budget_str:
        return 7500000.0
    if '$1m' in budget_str:
        return 2500000.0
    if '$500' in budget_str and ('k' in budget_str or '000' in budget_str):
        return 750000.0
    if '$100' in budget_str and ('k' in budget_str or '000' in budget_str):
        return 300000.0

    return 500000.0  # Default


def parse_state(location_str: str) -> str:
    """
    Extract 2-letter state code from location string.

    Examples:
        "California" -> "CA"
        "CA" -> "CA"
        "Los Angeles, CA" -> "CA"
        "California;" -> "CA"
    """
    if not location_str:
        return ""

    # Clean up
    location = location_str.strip().rstrip(';').split(';')[0].strip()

    # Already a 2-letter code?
    if len(location) == 2 and location.upper() in STATE_ABBR.values():
        return location.upper()

    # Check for state name
    location_lower = location.lower()
    if location_lower in STATE_ABBR:
        return STATE_ABBR[location_lower]

    # Check if it's in the format "City, ST"
    parts = location.split(',')
    if len(parts) >= 2:
        state_part = parts[-1].strip()
        if len(state_part) == 2:
            return state_part.upper()
        if state_part.lower() in STATE_ABBR:
            return STATE_ABBR[state_part.lower()]

    return location[:2].upper() if len(location) >= 2 else ""


def parse_list(value: str, delimiter: str = ';') -> List[str]:
    """Parse semicolon-delimited string to list."""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter) if item.strip()]


def get_column(row: dict, *patterns: str) -> str:
    """Get column value using partial pattern matching."""
    for key in row.keys():
        for pattern in patterns:
            if pattern.lower() in key.lower():
                return row.get(key, '') or ''
    return ''


def load_clients_registry() -> Dict:
    """Load client registry from config/clients.json."""
    clients_file = CONFIG_DIR / "clients.json"
    if not clients_file.exists():
        return {"clients": []}

    with open(clients_file) as f:
        return json.load(f)


def load_grant_type_preferences() -> Dict:
    """Load grant type preferences from config/grant_type_preferences.json."""
    prefs_file = CONFIG_DIR / "grant_type_preferences.json"
    if not prefs_file.exists():
        return {}

    with open(prefs_file) as f:
        return json.load(f)


def get_grant_type_config(org_name: str, logger: logging.Logger) -> Dict:
    """Get grant type preference and keywords for an organization."""
    prefs = load_grant_type_preferences()

    # Try exact match first
    if org_name in prefs:
        logger.info(f"Found grant type config for: {org_name}")
        return prefs[org_name]

    # Try partial match (case-insensitive)
    org_lower = org_name.lower()
    for key, value in prefs.items():
        if org_lower in key.lower() or key.lower() in org_lower:
            logger.info(f"Found grant type config via partial match: {key}")
            return value

    # Default
    logger.info(f"No grant type config found for: {org_name}, using defaults")
    return {
        'grant_type_preference': 'program_general',
        'grant_type_keywords': [],
        'specific_ask_text': ''
    }


def find_client_in_registry(identifier: str) -> Optional[Dict]:
    """Find client in registry by name or short_name."""
    registry = load_clients_registry()
    identifier_lower = identifier.lower()

    for client in registry.get('clients', []):
        if client['name'].lower() == identifier_lower:
            return client
        if client.get('short_name', '').lower() == identifier_lower:
            return client

    return None


def load_questionnaire(questionnaire_path: Path, client_name: str) -> Optional[Dict]:
    """Load client data from questionnaire CSV."""
    if not questionnaire_path.exists():
        return None

    with open(questionnaire_path, encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    client_lower = client_name.lower()

    # Find matching row
    for row in rows:
        org_name = row.get('Organization Name', '').strip()
        if org_name and client_lower in org_name.lower():
            return row

    return None


def get_available_clients(questionnaire_path: Path) -> List[str]:
    """Get list of available client names from questionnaire."""
    if not questionnaire_path.exists():
        return []

    with open(questionnaire_path, encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        return [row.get('Organization Name', '').strip() for row in reader if row.get('Organization Name')]


def lookup_ein_by_name(org_name: str, logger: logging.Logger) -> str:
    """Query nonprofit_returns for EIN by organization name."""
    logger.info(f"Looking up EIN for: {org_name}")

    query = """
    SELECT ein, organization_name
    FROM f990_2025.nonprofit_returns
    WHERE LOWER(organization_name) LIKE %(name_pattern)s
    ORDER BY tax_year DESC
    LIMIT 5
    """

    df = query_df(query, {'name_pattern': f"%{org_name.lower()}%"})

    if df.empty:
        logger.warning(f"No EIN found for: {org_name}")
        return ""

    # Return first match
    ein = df.iloc[0]['ein']
    found_name = df.iloc[0]['organization_name']
    logger.info(f"Found EIN {ein} for: {found_name}")
    return ein


def get_ntee_code(ein: str, logger: logging.Logger) -> str:
    """Get NTEE code from ref_irs_bmf."""
    if not ein:
        return ""

    query = """
    SELECT ntee_cd
    FROM f990_2025.ref_irs_bmf
    WHERE ein = %(ein)s
    LIMIT 1
    """

    df = query_df(query, {'ein': ein})

    if df.empty:
        logger.info(f"No NTEE code found in BMF for EIN: {ein}")
        return ""

    ntee = df.iloc[0]['ntee_cd'] or ""
    logger.info(f"Found NTEE code: {ntee}")
    return ntee


def get_financials(ein: str, logger: logging.Logger) -> Dict:
    """Get revenue, assets, employees from nonprofit_returns."""
    if not ein:
        return {'assets': 0.0, 'total_revenue': 0.0, 'employee_count': 0}

    query = """
    SELECT
        total_revenue,
        total_assets_eoy,
        total_employees_cnt
    FROM f990_2025.nonprofit_returns
    WHERE ein = %(ein)s
    ORDER BY tax_year DESC
    LIMIT 1
    """

    df = query_df(query, {'ein': ein})

    if df.empty:
        logger.info(f"No financial data found for EIN: {ein}")
        return {'assets': 0.0, 'total_revenue': 0.0, 'employee_count': 0}

    row = df.iloc[0]
    financials = {
        'assets': float(row.get('total_assets_eoy', 0) or 0),
        'total_revenue': float(row.get('total_revenue', 0) or 0),
        'employee_count': int(row.get('total_employees_cnt', 0) or 0)
    }
    logger.info(f"Found financials: revenue=${financials['total_revenue']:,.0f}, assets=${financials['assets']:,.0f}")
    return financials


def get_officers(ein: str, logger: logging.Logger) -> List[str]:
    """Get officer names from officers table."""
    if not ein:
        return []

    query = """
    SELECT DISTINCT person_nm
    FROM f990_2025.officers
    WHERE ein = %(ein)s
    ORDER BY person_nm
    """

    df = query_df(query, {'ein': ein})

    if df.empty:
        logger.info(f"No officers found for EIN: {ein}")
        return []

    officers = df['person_nm'].tolist()
    logger.info(f"Found {len(officers)} officers")
    return officers


def main():
    parser = argparse.ArgumentParser(description='Load and enrich client data')
    parser.add_argument('--client', type=str, help='Client name or short name')
    parser.add_argument('--ein', type=str, help='Client EIN')
    parser.add_argument('--questionnaire', type=str, help='Path to questionnaire CSV')

    args = parser.parse_args()

    if not args.client and not args.ein:
        parser.error("Either --client or --ein is required")

    # Determine questionnaire path
    if args.questionnaire:
        questionnaire_path = Path(args.questionnaire)
    else:
        questionnaire_dir = DATA_DIR / "questionnaires"
        csv_files = list(questionnaire_dir.glob("*.csv"))
        if not csv_files:
            print("ERROR: No questionnaire CSV files found in data/questionnaires/")
            sys.exit(1)
        questionnaire_path = csv_files[0]

    # Set up client identifier
    client_identifier = args.client or args.ein

    # Set up logging
    logger = setup_logging(client_identifier)
    logger.info(f"Starting client load for: {client_identifier}")
    logger.info(f"Using questionnaire: {questionnaire_path}")

    # Check registry first
    registry_client = None
    if args.client:
        registry_client = find_client_in_registry(args.client)
        if registry_client:
            logger.info(f"Found client in registry: {registry_client['name']}")

    # Load questionnaire data
    search_name = registry_client['name'] if registry_client else client_identifier
    questionnaire_row = load_questionnaire(questionnaire_path, search_name)

    if not questionnaire_row and args.ein:
        # Try to find by EIN in questionnaire
        logger.info("Searching questionnaire by EIN...")
        with open(questionnaire_path, encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('EIN', '').strip() == args.ein:
                    questionnaire_row = row
                    break

    if not questionnaire_row:
        print(f"\nERROR: Client not found in questionnaire: {search_name}")
        print("\nAvailable clients:")
        for name in get_available_clients(questionnaire_path):
            print(f"  - {name}")
        sys.exit(1)

    logger.info(f"Found client in questionnaire: {questionnaire_row.get('Organization Name', '')}")

    # Parse questionnaire fields
    org_name = questionnaire_row.get('Organization Name', '').strip()

    # Get EIN - priority: registry > questionnaire > lookup
    ein = ""
    if registry_client and registry_client.get('ein'):
        ein = registry_client['ein']
        logger.info(f"Using EIN from registry: {ein}")
    elif questionnaire_row.get('EIN', '').strip():
        ein = questionnaire_row['EIN'].strip()
        logger.info(f"Using EIN from questionnaire: {ein}")

    # Parse other fields
    email = get_column(questionnaire_row, 'email address', 'email').strip()
    state = parse_state(get_column(questionnaire_row, 'headquartered', 'State'))
    city = get_column(questionnaire_row, 'what city', 'located in').strip()
    org_type = get_column(questionnaire_row, 'organization type').strip()
    budget_str = get_column(questionnaire_row, 'annual budget').strip()
    budget_numeric = parse_budget(budget_str)
    grant_size_target = get_column(questionnaire_row, 'size grants', 'looking for').strip()
    grant_capacity = get_column(questionnaire_row, 'grant management capacity').strip()
    program_areas = parse_list(get_column(questionnaire_row, 'program areas'))
    populations_served = parse_list(get_column(questionnaire_row, 'populations'))
    geographic_scope = get_column(questionnaire_row, 'geographic range').strip()
    ntee_code = get_column(questionnaire_row, 'ntee').strip()
    mission_statement = get_column(questionnaire_row, 'what does your organization do', '1-2 sentences').strip()
    prior_funders = parse_list(get_column(questionnaire_row, 'funders have you received'))
    timeframe = get_column(questionnaire_row, 'timeframe').strip()
    notes = get_column(questionnaire_row, 'anything else').strip()

    # Clean up NTEE code (may have prefix text)
    if ntee_code:
        # Extract code from strings like "NTEE code, primary B00: Education"
        ntee_match = re.search(r'([A-Z]\d{2})', ntee_code.upper())
        if ntee_match:
            ntee_code = ntee_match.group(1)

    # Database enrichment
    logger.info("Starting database enrichment...")

    # Look up EIN if still missing
    if not ein:
        ein = lookup_ein_by_name(org_name, logger)

    # Get NTEE from BMF database (authoritative source) - prefer over questionnaire
    questionnaire_ntee = ntee_code  # Save questionnaire value
    if ein:
        bmf_ntee = get_ntee_code(ein, logger)
        if bmf_ntee:
            ntee_code = bmf_ntee
            if questionnaire_ntee and questionnaire_ntee != bmf_ntee:
                logger.info(f"Using BMF NTEE ({bmf_ntee}) over questionnaire NTEE ({questionnaire_ntee})")

    # Get state from database if not in questionnaire
    if not state and ein:
        state_query = """
        SELECT state FROM f990_2025.nonprofit_returns
        WHERE ein = %(ein)s AND state IS NOT NULL
        ORDER BY tax_year DESC LIMIT 1
        """
        state_df = query_df(state_query, {'ein': ein})
        if not state_df.empty:
            state = state_df.iloc[0]['state']
            logger.info(f"Got state from database: {state}")

    # Get financials
    financials = get_financials(ein, logger)

    # Get officers
    officers = get_officers(ein, logger)

    # Get grant type preferences (NEW)
    grant_type_config = get_grant_type_config(org_name, logger)

    # Build output
    client_data = {
        'organization_name': org_name,
        'short_name': registry_client['short_name'] if registry_client else '',
        'ein': ein,
        'email': email,
        'state': state,
        'city': city,
        'org_type': org_type,
        'budget': budget_str,
        'budget_numeric': budget_numeric,
        'grant_size_target': grant_size_target,
        'grant_capacity': grant_capacity,
        'program_areas': program_areas,
        'populations_served': populations_served,
        'geographic_scope': geographic_scope,
        'ntee_code': ntee_code,
        'mission_statement': mission_statement,
        'prior_funders': prior_funders,
        'timeframe': timeframe,
        'notes': notes,
        'officers': officers,
        'assets': financials['assets'],
        'total_revenue': financials['total_revenue'],
        'employee_count': financials['employee_count'],
        # NEW: Grant type preferences
        'grant_type_preference': grant_type_config.get('grant_type_preference', 'program_general'),
        'grant_type_keywords': grant_type_config.get('grant_type_keywords', []),
        'specific_ask_text': grant_type_config.get('specific_ask_text', notes),
        'loaded_at': datetime.now().isoformat()
    }

    # Save output
    run_dir = get_run_dir(org_name)
    output_file = run_dir / "01_client.json"

    with open(output_file, 'w') as f:
        json.dump(client_data, f, indent=2)

    logger.info(f"Saved client data to: {output_file}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Client loaded successfully!")
    print(f"{'='*60}")
    print(f"Organization: {org_name}")
    print(f"EIN: {ein or '(not found)'}")
    print(f"State: {state}")
    print(f"Budget: {budget_str} (${budget_numeric:,.0f})")
    print(f"NTEE: {ntee_code or '(not found)'}")
    print(f"Officers: {len(officers)}")
    print(f"Grant Type: {client_data['grant_type_preference']}")
    print(f"Specific Ask: {client_data['specific_ask_text'][:80]}..." if len(client_data['specific_ask_text']) > 80 else f"Specific Ask: {client_data['specific_ask_text']}")
    print(f"Mission: {mission_statement[:100]}..." if len(mission_statement) > 100 else f"Mission: {mission_statement}")
    print(f"\nOutput: {output_file}")
    print(f"{'='*60}\n")

    return client_data


if __name__ == '__main__':
    main()
