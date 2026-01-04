"""
Questionnaire data loader.

Loads and parses client questionnaire responses from CSV files.
"""
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from config.settings import QUESTIONNAIRE_DIR, BETA_QUESTIONNAIRE_DIR


@dataclass
class ClientProfile:
    """Parsed client profile from questionnaire."""
    organization_name: str
    email: str = ""
    ein: str = ""  # May be looked up later

    # Location
    state: str = ""
    city: str = ""

    # Organization info
    org_type: str = ""
    budget: str = ""
    budget_numeric: float = 0
    grant_size_target: str = ""
    grant_capacity: str = ""

    # Program focus
    program_areas: List[str] = field(default_factory=list)
    populations_served: List[str] = field(default_factory=list)
    geographic_scope: str = ""
    ntee_code: str = ""

    # Mission
    mission_statement: str = ""

    # Prior funders (to exclude)
    prior_funders: List[str] = field(default_factory=list)

    # Notes
    timeframe: str = ""
    notes: str = ""


def parse_budget(budget_str: str) -> float:
    """Parse budget string to numeric value (midpoint of range)."""
    budget_str = budget_str.lower().strip()

    if 'over' in budget_str and '$1,000,000' in budget_str:
        return 2000000
    elif '$10m' in budget_str or '$10,000,000' in budget_str:
        return 25000000
    elif '$5m' in budget_str:
        return 7500000
    elif '$1m' in budget_str:
        return 2500000
    elif '$500,000' in budget_str:
        return 750000
    elif '$100,000' in budget_str:
        return 300000
    else:
        return 500000  # Default


def parse_state(state_str: str) -> str:
    """Parse state from location string."""
    if not state_str:
        return ""

    # Extract first state if multiple
    state = state_str.split(';')[0].strip()

    # State name to abbreviation mapping
    state_abbr = {
        'california': 'CA', 'hawaii': 'HI', 'north carolina': 'NC',
        'connecticut': 'CT', 'new york': 'NY', 'texas': 'TX',
        'florida': 'FL', 'georgia': 'GA', 'illinois': 'IL',
        'massachusetts': 'MA', 'new jersey': 'NJ', 'pennsylvania': 'PA',
        'colorado': 'CO', 'delaware': 'DE', 'indiana': 'IN',
        'maryland': 'MD', 'missouri': 'MO', 'new mexico': 'NM',
        'south carolina': 'SC', 'tennessee': 'TN', 'utah': 'UT',
        'virginia': 'VA'
    }

    state_lower = state.lower()
    if state_lower in state_abbr:
        return state_abbr[state_lower]
    elif len(state) == 2:
        return state.upper()
    else:
        return state


def parse_list(value: str, delimiter: str = ';') -> List[str]:
    """Parse semicolon-delimited list."""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter) if item.strip()]


def get_column(row: dict, *patterns: str) -> str:
    """Get column value using partial pattern matching."""
    for key in row.keys():
        for pattern in patterns:
            if pattern.lower() in key.lower():
                return row.get(key, '')
    return ''


def load_questionnaire(
    path: str = None,
    organization_name: str = None
) -> Optional[ClientProfile]:
    """
    Load client profile from questionnaire CSV.

    Args:
        path: Path to questionnaire CSV (default: look in data/questionnaires)
        organization_name: Organization name to find

    Returns:
        ClientProfile if found, None otherwise
    """
    # Find questionnaire file
    if path:
        csv_path = Path(path)
    else:
        # Look in default locations
        for dir_path in [QUESTIONNAIRE_DIR, BETA_QUESTIONNAIRE_DIR]:
            if not dir_path.exists():
                continue
            for csv_file in dir_path.glob("*.csv"):
                csv_path = csv_file
                break
            else:
                continue
            break
        else:
            return None

    # Read CSV - handle various encodings
    with open(csv_path, encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            org_name = row.get('Organization Name', '').strip()

            # Match by name (case-insensitive partial match)
            if organization_name:
                if organization_name.lower() not in org_name.lower():
                    continue

            # Parse the row using flexible column matching
            return ClientProfile(
                organization_name=org_name,
                email=get_column(row, 'email address', 'email'),
                ein=row.get('EIN', '').strip(),
                state=parse_state(get_column(row, 'headquartered')),
                city=get_column(row, 'what city'),
                org_type=get_column(row, 'organization type'),
                budget=get_column(row, 'annual budget'),
                budget_numeric=parse_budget(get_column(row, 'annual budget')),
                grant_size_target=get_column(row, 'size grants'),
                grant_capacity=get_column(row, 'grant management capacity'),
                program_areas=parse_list(get_column(row, 'program areas')),
                populations_served=parse_list(get_column(row, 'populations')),
                geographic_scope=get_column(row, 'geographic range'),
                ntee_code=get_column(row, 'ntee'),
                mission_statement=get_column(row, 'what does your organization do'),
                prior_funders=parse_list(get_column(row, 'funders have you received')),
                timeframe=get_column(row, 'timeframes'),
                notes=get_column(row, 'anything else')
            )

    return None


def get_all_clients(path: str = None) -> List[ClientProfile]:
    """Load all clients from questionnaire."""
    profiles = []

    # Find questionnaire file
    if path:
        csv_path = Path(path)
    else:
        for dir_path in [QUESTIONNAIRE_DIR, BETA_QUESTIONNAIRE_DIR]:
            if not dir_path.exists():
                continue
            for csv_file in dir_path.glob("*.csv"):
                csv_path = csv_file
                break
            else:
                continue
            break
        else:
            return []

    # Read CSV - handle various encodings
    with open(csv_path, encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            org_name = row.get('Organization Name', '').strip()
            if not org_name:
                continue

            profiles.append(ClientProfile(
                organization_name=org_name,
                email=get_column(row, 'email address', 'email'),
                ein=row.get('EIN', '').strip(),
                state=parse_state(get_column(row, 'headquartered')),
                city=get_column(row, 'what city'),
                org_type=get_column(row, 'organization type'),
                budget=get_column(row, 'annual budget'),
                budget_numeric=parse_budget(get_column(row, 'annual budget')),
                grant_size_target=get_column(row, 'size grants'),
                grant_capacity=get_column(row, 'grant management capacity'),
                program_areas=parse_list(get_column(row, 'program areas')),
                populations_served=parse_list(get_column(row, 'populations')),
                geographic_scope=get_column(row, 'geographic range'),
                ntee_code=get_column(row, 'ntee'),
                mission_statement=get_column(row, 'what does your organization do'),
                prior_funders=parse_list(get_column(row, 'funders have you received')),
                timeframe=get_column(row, 'timeframes'),
                notes=get_column(row, 'anything else')
            ))

    return profiles
