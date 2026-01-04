"""
Potential connections finder.

Identifies potential connections between client and foundation.
"""
from dataclasses import dataclass
from typing import List, Optional

from config.database import query_df


@dataclass
class Connection:
    """Represents a potential connection between client and foundation."""
    connection_type: str  # 'board_overlap', 'shared_funder', 'network'
    description: str
    strength: str  # 'strong', 'moderate', 'weak'
    source: str = ""


def find_board_overlap(
    foundation_ein: str,
    client_officers: List[str]
) -> List[Connection]:
    """
    Find overlapping board members between foundation and client.

    Args:
        foundation_ein: Foundation EIN
        client_officers: List of client officer names

    Returns:
        List of Connection objects for overlaps
    """
    if not client_officers:
        return []

    # Get foundation officers
    query = """
    SELECT DISTINCT person_nm
    FROM f990_2025.officers
    WHERE ein = %(ein)s
    """
    df = query_df(query, {'ein': foundation_ein})

    if df.empty:
        return []

    foundation_officers = set(df['person_nm'].str.upper().tolist())
    client_officers_upper = set(name.upper() for name in client_officers)

    # Find overlaps
    overlaps = foundation_officers & client_officers_upper

    connections = []
    for name in overlaps:
        connections.append(Connection(
            connection_type='board_overlap',
            description=f"{name} serves on both boards",
            strength='strong',
            source='officer_records'
        ))

    return connections


def find_shared_funders(
    foundation_ein: str,
    client_ein: str
) -> List[Connection]:
    """
    Find other foundations that have funded both this foundation and the client.

    Args:
        foundation_ein: Foundation EIN to check
        client_ein: Client EIN

    Returns:
        List of Connection objects for shared funders
    """
    query = """
    WITH foundation_funders AS (
        SELECT DISTINCT foundation_ein
        FROM f990_2025.fact_grants
        WHERE recipient_ein = %(foundation_ein)s
    ),
    client_funders AS (
        SELECT DISTINCT foundation_ein
        FROM f990_2025.fact_grants
        WHERE recipient_ein = %(client_ein)s
    )
    SELECT
        ff.foundation_ein,
        df.name as funder_name
    FROM foundation_funders ff
    INNER JOIN client_funders cf ON ff.foundation_ein = cf.foundation_ein
    LEFT JOIN f990_2025.dim_foundations df ON ff.foundation_ein = df.ein
    LIMIT 5
    """
    df = query_df(query, {
        'foundation_ein': foundation_ein,
        'client_ein': client_ein
    })

    connections = []
    for _, row in df.iterrows():
        connections.append(Connection(
            connection_type='shared_funder',
            description=f"Both funded by {row.get('funder_name', 'another foundation')}",
            strength='moderate',
            source='grant_records'
        ))

    return connections


def find_geographic_proximity(
    foundation_state: str,
    client_state: str,
    client_city: str = ""
) -> List[Connection]:
    """
    Find geographic connections.

    Args:
        foundation_state: Foundation's state
        client_state: Client's state
        client_city: Client's city

    Returns:
        List of Connection objects
    """
    connections = []

    if foundation_state and client_state:
        if foundation_state == client_state:
            connections.append(Connection(
                connection_type='geographic',
                description=f"Foundation is based in {foundation_state}, same as your organization",
                strength='moderate',
                source='location'
            ))

    return connections


def find_sector_alignment(
    foundation_ein: str,
    client_ntee: str
) -> List[Connection]:
    """
    Find sector alignment connections.

    Args:
        foundation_ein: Foundation EIN
        client_ntee: Client's NTEE code

    Returns:
        List of Connection objects
    """
    if not client_ntee:
        return []

    # Get foundation's primary funded sector
    query = """
    SELECT
        dr.ntee_broad,
        COUNT(*) as grant_count
    FROM f990_2025.fact_grants fg
    JOIN f990_2025.dim_recipients dr ON fg.recipient_ein = dr.ein
    WHERE fg.foundation_ein = %(foundation_ein)s
      AND dr.ntee_broad IS NOT NULL
      AND dr.ntee_broad != ''
    GROUP BY dr.ntee_broad
    ORDER BY grant_count DESC
    LIMIT 1
    """
    df = query_df(query, {'foundation_ein': foundation_ein})

    connections = []
    if not df.empty:
        top_sector = df.iloc[0]['ntee_broad']
        client_sector = client_ntee[0] if client_ntee else ''

        if top_sector == client_sector:
            connections.append(Connection(
                connection_type='sector_alignment',
                description=f"Foundation primarily funds {top_sector} sector organizations",
                strength='moderate',
                source='grant_history'
            ))

    return connections


def find_connections(
    foundation_ein: str,
    client_ein: str = "",
    client_state: str = "",
    client_ntee: str = "",
    client_officers: List[str] = None
) -> List[Connection]:
    """
    Find all potential connections between client and foundation.

    Args:
        foundation_ein: Foundation EIN
        client_ein: Client EIN (optional)
        client_state: Client's state (optional)
        client_ntee: Client's NTEE code (optional)
        client_officers: List of client officer names (optional)

    Returns:
        List of all Connection objects found
    """
    connections = []

    # Board overlap
    if client_officers:
        connections.extend(find_board_overlap(foundation_ein, client_officers))

    # Shared funders
    if client_ein:
        connections.extend(find_shared_funders(foundation_ein, client_ein))

    # Geographic proximity
    # Get foundation state
    state_df = query_df(
        "SELECT state FROM f990_2025.dim_foundations WHERE ein = %(ein)s",
        {'ein': foundation_ein}
    )
    if not state_df.empty:
        foundation_state = state_df.iloc[0]['state']
        connections.extend(find_geographic_proximity(foundation_state, client_state))

    # Sector alignment
    if client_ntee:
        connections.extend(find_sector_alignment(foundation_ein, client_ntee))

    return connections
