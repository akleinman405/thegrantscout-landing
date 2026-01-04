"""
Funder Snapshot data access layer.

Provides Python wrappers for the SQL queries that compute 8 snapshot metrics.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json

import pandas as pd

from config.database import query_df

# SQL directory
SQL_DIR = Path(__file__).parent / "sql"


@dataclass
class FunderSnapshot:
    """Complete Funder Snapshot data for a foundation."""

    foundation_ein: str
    foundation_name: str = ""

    # 1. Annual Giving
    annual_giving_total: float = 0
    annual_giving_count: int = 0
    annual_giving_year: int = 0

    # 2. Typical Grant
    typical_grant_median: float = 0
    typical_grant_min: float = 0
    typical_grant_max: float = 0
    typical_grant_avg: float = 0

    # 3. Geographic Focus
    geographic_top_state: str = ""
    geographic_top_state_pct: float = 0
    geographic_in_state_pct: float = 0
    geographic_foundation_state: str = ""

    # 4. Repeat Funding
    repeat_funding_unique: int = 0
    repeat_funding_repeat: int = 0
    repeat_funding_rate: float = 0

    # 5. Giving Style
    giving_style_general_pct: float = 0.5
    giving_style_program_pct: float = 0.5

    # 6. Recipient Profile
    recipient_budget_min: float = 0
    recipient_budget_max: float = 0
    recipient_budget_median: float = 0
    recipient_primary_sector: str = ""
    recipient_primary_sector_pct: float = 0

    # 7. Funding Trend
    funding_trend_direction: str = "Stable"
    funding_trend_change_pct: float = 0
    funding_trend_oldest_year: int = 0
    funding_trend_newest_year: int = 0

    # 8. Comparable Grant
    comparable_grant_recipient: str = ""
    comparable_grant_amount: float = 0
    comparable_grant_purpose: str = ""
    comparable_grant_year: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'foundation_ein': self.foundation_ein,
            'foundation_name': self.foundation_name,
            'annual_giving': {
                'total': self.annual_giving_total,
                'count': self.annual_giving_count,
                'year': self.annual_giving_year
            },
            'typical_grant': {
                'median': self.typical_grant_median,
                'min': self.typical_grant_min,
                'max': self.typical_grant_max,
                'avg': self.typical_grant_avg
            },
            'geographic_focus': {
                'top_state': self.geographic_top_state,
                'top_state_pct': self.geographic_top_state_pct,
                'in_state_pct': self.geographic_in_state_pct,
                'foundation_state': self.geographic_foundation_state
            },
            'repeat_funding': {
                'unique_recipients': self.repeat_funding_unique,
                'repeat_recipients': self.repeat_funding_repeat,
                'rate': self.repeat_funding_rate
            },
            'giving_style': {
                'general_support_pct': self.giving_style_general_pct,
                'program_specific_pct': self.giving_style_program_pct
            },
            'recipient_profile': {
                'budget_min': self.recipient_budget_min,
                'budget_max': self.recipient_budget_max,
                'budget_median': self.recipient_budget_median,
                'primary_sector': self.recipient_primary_sector,
                'primary_sector_pct': self.recipient_primary_sector_pct
            },
            'funding_trend': {
                'direction': self.funding_trend_direction,
                'change_pct': self.funding_trend_change_pct,
                'oldest_year': self.funding_trend_oldest_year,
                'newest_year': self.funding_trend_newest_year
            },
            'comparable_grant': {
                'recipient_name': self.comparable_grant_recipient,
                'amount': self.comparable_grant_amount,
                'purpose': self.comparable_grant_purpose,
                'year': self.comparable_grant_year
            }
        }


def _load_sql(name: str) -> str:
    """Load SQL query from file."""
    with open(SQL_DIR / f"{name}.sql") as f:
        return f.read()


def get_annual_giving(foundation_ein: str) -> dict:
    """Get annual giving metrics for a foundation."""
    query = _load_sql("annual_giving")
    df = query_df(query, {'foundation_ein': foundation_ein})

    if df.empty:
        return {'total': 0, 'count': 0, 'year': 0}

    row = df.iloc[0]
    return {
        'total': float(row.get('total_giving', 0) or 0),
        'count': int(row.get('grant_count', 0) or 0),
        'year': int(row.get('tax_year', 0) or 0)
    }


def get_typical_grant(foundation_ein: str) -> dict:
    """Get typical grant metrics for a foundation."""
    query = _load_sql("typical_grant")
    df = query_df(query, {'foundation_ein': foundation_ein})

    if df.empty:
        return {'median': 0, 'min': 0, 'max': 0, 'avg': 0}

    row = df.iloc[0]
    return {
        'median': float(row.get('median_grant', 0) or 0),
        'min': float(row.get('min_grant', 0) or 0),
        'max': float(row.get('max_grant', 0) or 0),
        'avg': float(row.get('avg_grant', 0) or 0)
    }


def get_geographic_focus(foundation_ein: str) -> dict:
    """Get geographic focus metrics for a foundation."""
    query = _load_sql("geographic_focus")
    df = query_df(query, {'foundation_ein': foundation_ein})

    if df.empty:
        return {
            'top_state': '',
            'top_state_pct': 0,
            'in_state_pct': 0,
            'foundation_state': ''
        }

    row = df.iloc[0]
    return {
        'top_state': str(row.get('top_state', '') or ''),
        'top_state_pct': float(row.get('top_state_pct', 0) or 0),
        'in_state_pct': float(row.get('in_state_pct', 0) or 0),
        'foundation_state': str(row.get('foundation_state', '') or '')
    }


def get_repeat_funding(foundation_ein: str) -> dict:
    """Get repeat funding metrics for a foundation."""
    query = _load_sql("repeat_funding")
    df = query_df(query, {'foundation_ein': foundation_ein})

    if df.empty:
        return {'unique': 0, 'repeat': 0, 'rate': 0}

    row = df.iloc[0]
    return {
        'unique': int(row.get('unique_recipients', 0) or 0),
        'repeat': int(row.get('repeat_recipients', 0) or 0),
        'rate': float(row.get('repeat_rate', 0) or 0)
    }


def get_giving_style(foundation_ein: str) -> dict:
    """Get giving style metrics for a foundation."""
    query = _load_sql("giving_style")
    df = query_df(query, {'foundation_ein': foundation_ein})

    if df.empty:
        return {'general_pct': 0.5, 'program_pct': 0.5}

    row = df.iloc[0]
    general_pct = float(row.get('general_support_pct', 0.5) or 0.5)
    return {
        'general_pct': general_pct,
        'program_pct': 1 - general_pct
    }


def get_recipient_profile(foundation_ein: str) -> dict:
    """Get recipient profile metrics for a foundation."""
    query = _load_sql("recipient_profile")
    df = query_df(query, {'foundation_ein': foundation_ein})

    if df.empty:
        return {
            'budget_min': 0,
            'budget_max': 0,
            'budget_median': 0,
            'primary_sector': '',
            'primary_sector_pct': 0
        }

    row = df.iloc[0]
    return {
        'budget_min': float(row.get('typical_budget_min', 0) or 0),
        'budget_max': float(row.get('typical_budget_max', 0) or 0),
        'budget_median': float(row.get('median_budget', 0) or 0),
        'primary_sector': str(row.get('primary_sector', '') or ''),
        'primary_sector_pct': float(row.get('primary_sector_pct', 0) or 0)
    }


def get_funding_trend(foundation_ein: str) -> dict:
    """Get funding trend metrics for a foundation."""
    query = _load_sql("funding_trend")
    df = query_df(query, {'foundation_ein': foundation_ein})

    if df.empty:
        return {
            'direction': 'Stable',
            'change_pct': 0,
            'oldest_year': 0,
            'newest_year': 0
        }

    row = df.iloc[0]
    return {
        'direction': str(row.get('trend', 'Stable') or 'Stable'),
        'change_pct': float(row.get('change_pct', 0) or 0),
        'oldest_year': int(row.get('oldest_year', 0) or 0),
        'newest_year': int(row.get('newest_year', 0) or 0)
    }


def get_comparable_grant(
    foundation_ein: str,
    client_state: str,
    client_ntee: str
) -> dict:
    """Get comparable grant for positioning."""
    query = _load_sql("comparable_grant")
    df = query_df(query, {
        'foundation_ein': foundation_ein,
        'client_state': client_state,
        'client_ntee': client_ntee
    })

    if df.empty:
        return {
            'recipient_name': '',
            'amount': 0,
            'purpose': '',
            'year': 0
        }

    row = df.iloc[0]
    return {
        'recipient_name': str(row.get('recipient_name', '') or ''),
        'amount': float(row.get('grant_amount', 0) or 0),
        'purpose': str(row.get('grant_purpose', '') or ''),
        'year': int(row.get('grant_year', 0) or 0)
    }


def get_funder_snapshot(
    foundation_ein: str,
    client_state: str = '',
    client_ntee: str = ''
) -> FunderSnapshot:
    """
    Get complete Funder Snapshot for a foundation.

    Combines all 8 metrics into a single object.

    Args:
        foundation_ein: Foundation EIN
        client_state: Client's state (for comparable grant)
        client_ntee: Client's NTEE code (for comparable grant)

    Returns:
        FunderSnapshot with all metrics populated
    """
    # Get foundation name
    name_df = query_df(
        "SELECT name FROM f990_2025.dim_foundations WHERE ein = %(ein)s",
        {'ein': foundation_ein}
    )
    foundation_name = name_df.iloc[0]['name'] if not name_df.empty else ''

    # Get all metrics
    annual = get_annual_giving(foundation_ein)
    typical = get_typical_grant(foundation_ein)
    geo = get_geographic_focus(foundation_ein)
    repeat = get_repeat_funding(foundation_ein)
    style = get_giving_style(foundation_ein)
    profile = get_recipient_profile(foundation_ein)
    trend = get_funding_trend(foundation_ein)
    comparable = get_comparable_grant(foundation_ein, client_state, client_ntee)

    return FunderSnapshot(
        foundation_ein=foundation_ein,
        foundation_name=foundation_name,

        annual_giving_total=annual['total'],
        annual_giving_count=annual['count'],
        annual_giving_year=annual['year'],

        typical_grant_median=typical['median'],
        typical_grant_min=typical['min'],
        typical_grant_max=typical['max'],
        typical_grant_avg=typical['avg'],

        geographic_top_state=geo['top_state'],
        geographic_top_state_pct=geo['top_state_pct'],
        geographic_in_state_pct=geo['in_state_pct'],
        geographic_foundation_state=geo['foundation_state'],

        repeat_funding_unique=repeat['unique'],
        repeat_funding_repeat=repeat['repeat'],
        repeat_funding_rate=repeat['rate'],

        giving_style_general_pct=style['general_pct'],
        giving_style_program_pct=style['program_pct'],

        recipient_budget_min=profile['budget_min'],
        recipient_budget_max=profile['budget_max'],
        recipient_budget_median=profile['budget_median'],
        recipient_primary_sector=profile['primary_sector'],
        recipient_primary_sector_pct=profile['primary_sector_pct'],

        funding_trend_direction=trend['direction'],
        funding_trend_change_pct=trend['change_pct'],
        funding_trend_oldest_year=trend['oldest_year'],
        funding_trend_newest_year=trend['newest_year'],

        comparable_grant_recipient=comparable['recipient_name'],
        comparable_grant_amount=comparable['amount'],
        comparable_grant_purpose=comparable['purpose'],
        comparable_grant_year=comparable['year']
    )
