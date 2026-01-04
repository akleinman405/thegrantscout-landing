"""
Client data enrichment from database.

Supplements questionnaire data with database lookups.
"""
from typing import Optional

from config.database import query_df
from .questionnaire import ClientProfile


def enrich_client(client: ClientProfile) -> ClientProfile:
    """
    Enrich client profile with database lookups.

    Attempts to:
    1. Find EIN from nonprofit_returns
    2. Get additional financial data
    3. Validate NTEE code

    Args:
        client: ClientProfile from questionnaire

    Returns:
        Enriched ClientProfile
    """
    # Try to find EIN by name matching
    if not client.ein and client.organization_name:
        ein_query = """
        SELECT ein, organization_name, state, total_revenue, tax_year
        FROM f990_2025.nonprofit_returns
        WHERE LOWER(organization_name) LIKE %(name_pattern)s
        ORDER BY tax_year DESC
        LIMIT 1
        """
        df = query_df(ein_query, {
            'name_pattern': f"%{client.organization_name.lower()}%"
        })

        if not df.empty:
            client.ein = df.iloc[0]['ein']

            # Also update state if not set
            if not client.state and df.iloc[0]['state']:
                client.state = df.iloc[0]['state']

            # Update budget if we found better data
            if df.iloc[0]['total_revenue'] and df.iloc[0]['total_revenue'] > 0:
                client.budget_numeric = float(df.iloc[0]['total_revenue'])

    # Validate/update NTEE code
    if client.ein and not client.ntee_code:
        ntee_query = """
        SELECT ntee_code
        FROM f990_2025.ref_irs_bmf
        WHERE ein = %(ein)s
        LIMIT 1
        """
        df = query_df(ntee_query, {'ein': client.ein})
        if not df.empty and df.iloc[0]['ntee_code']:
            client.ntee_code = df.iloc[0]['ntee_code']

    return client


def get_client_officers(client_ein: str) -> list:
    """
    Get list of officers/board members for a client.

    Args:
        client_ein: Client EIN

    Returns:
        List of officer names
    """
    if not client_ein:
        return []

    query = """
    SELECT DISTINCT person_nm
    FROM f990_2025.officers
    WHERE ein = %(ein)s
    """
    df = query_df(query, {'ein': client_ein})

    return df['person_nm'].tolist() if not df.empty else []


def lookup_client_by_ein(ein: str) -> Optional[ClientProfile]:
    """
    Create ClientProfile from EIN lookup.

    Args:
        ein: EIN to look up

    Returns:
        ClientProfile if found
    """
    query = """
    SELECT
        ein,
        organization_name,
        state,
        city,
        total_revenue,
        mission_description,
        ntee_code
    FROM f990_2025.nonprofit_returns
    WHERE ein = %(ein)s
    ORDER BY tax_year DESC
    LIMIT 1
    """
    df = query_df(query, {'ein': ein})

    if df.empty:
        return None

    row = df.iloc[0]

    # Determine budget string from revenue
    revenue = float(row.get('total_revenue', 0) or 0)
    if revenue > 50000000:
        budget = "$50M+"
    elif revenue > 10000000:
        budget = "$10M - $50M"
    elif revenue > 5000000:
        budget = "$5M - $10M"
    elif revenue > 1000000:
        budget = "$1M - $5M"
    elif revenue > 500000:
        budget = "$500,000 - $1M"
    else:
        budget = "Under $500,000"

    return ClientProfile(
        organization_name=row.get('organization_name', ''),
        ein=ein,
        state=row.get('state', ''),
        city=row.get('city', ''),
        budget=budget,
        budget_numeric=revenue,
        ntee_code=row.get('ntee_code', ''),
        mission_statement=row.get('mission_description', '') or ''
    )
