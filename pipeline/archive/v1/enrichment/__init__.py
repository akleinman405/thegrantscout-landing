"""Enrichment package for TheGrantScout Pipeline."""
from .snapshot import (
    FunderSnapshot,
    get_funder_snapshot,
    get_annual_giving,
    get_typical_grant,
    get_geographic_focus,
    get_repeat_funding,
    get_giving_style,
    get_recipient_profile,
    get_funding_trend,
    get_comparable_grant
)
from .cache import SnapshotCache, get_cache
from .connections import (
    Connection,
    find_connections,
    find_board_overlap,
    find_shared_funders,
    find_geographic_proximity,
    find_sector_alignment
)

__all__ = [
    'FunderSnapshot',
    'get_funder_snapshot',
    'get_annual_giving',
    'get_typical_grant',
    'get_geographic_focus',
    'get_repeat_funding',
    'get_giving_style',
    'get_recipient_profile',
    'get_funding_trend',
    'get_comparable_grant',
    'SnapshotCache',
    'get_cache',
    'Connection',
    'find_connections',
    'find_board_overlap',
    'find_shared_funders',
    'find_geographic_proximity',
    'find_sector_alignment'
]
