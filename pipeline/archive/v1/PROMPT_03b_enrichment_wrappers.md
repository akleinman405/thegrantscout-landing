# PROMPT_03b: Phase 3b - Enrichment Python Wrappers

**Date:** 2025-12-27
**Phase:** 3b
**Agent:** Dev Team
**Estimated Time:** 4-5 hours
**Depends On:** PROMPT_03a (SQL Queries) complete

---

## Objective

Create Python modules that wrap the SQL queries and provide clean interfaces for retrieving funder intelligence.

---

## Context

Phase 3a created 8 SQL query templates. This phase wraps them in Python functions with:
- Caching to avoid redundant queries
- Error handling
- Clean data structures

---

## Tasks

### Task 1: Create `enrichment/funder_snapshot.py`

Main module for getting all funder metrics.

```python
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FunderSnapshot:
    """All metrics for a foundation."""
    foundation_ein: str
    foundation_name: str
    
    # Annual Giving
    annual_giving_total: float
    annual_giving_count: int
    annual_giving_year: int
    
    # Typical Grant
    typical_grant_median: float
    typical_grant_min: float
    typical_grant_max: float
    
    # Geographic Focus
    geographic_top_state: str
    geographic_top_state_pct: float
    geographic_in_state_pct: float
    
    # Repeat Funding
    repeat_funding_rate: float
    unique_recipients: int
    
    # Giving Style
    giving_style_general_pct: float
    giving_style_program_pct: float
    
    # Recipient Profile
    recipient_budget_min: Optional[float]
    recipient_budget_max: Optional[float]
    recipient_primary_sector: Optional[str]
    
    # Funding Trend
    funding_trend_direction: str  # 'Growing', 'Stable', 'Declining'
    funding_trend_change_pct: float
    
    # Metadata
    snapshot_date: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        pass
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FunderSnapshot':
        """Create from dictionary (for cache loading)."""
        pass


def get_funder_snapshot(foundation_ein: str, use_cache: bool = True) -> FunderSnapshot:
    """
    Get complete funder snapshot for a foundation.
    
    Args:
        foundation_ein: The foundation's EIN
        use_cache: If True, use cached data if available and fresh
        
    Returns:
        FunderSnapshot with all metrics
    """
    pass


def get_funder_snapshots_batch(foundation_eins: list[str]) -> dict[str, FunderSnapshot]:
    """
    Get snapshots for multiple foundations efficiently.
    
    Args:
        foundation_eins: List of EINs
        
    Returns:
        Dict mapping EIN to FunderSnapshot
    """
    pass
```

**Implementation Notes:**
- Load SQL templates from `enrichment/sql/` folder
- Execute queries using `config.database.query_df()`
- Handle NULL/missing data gracefully
- Return None for metrics that can't be calculated

### Task 2: Create `enrichment/cache.py`

Caching layer for funder snapshots.

```python
from pathlib import Path
from datetime import datetime, timedelta
import json

class SnapshotCache:
    """Cache for funder snapshots."""
    
    def __init__(self, cache_dir: str = "data/cache", ttl_days: int = 7):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_days: Time-to-live in days
        """
        pass
    
    def get(self, foundation_ein: str) -> Optional[FunderSnapshot]:
        """
        Get cached snapshot if exists and fresh.
        
        Returns None if not cached or expired.
        """
        pass
    
    def set(self, foundation_ein: str, snapshot: FunderSnapshot) -> None:
        """Store snapshot in cache."""
        pass
    
    def invalidate(self, foundation_ein: str) -> None:
        """Remove snapshot from cache."""
        pass
    
    def clear_all(self) -> None:
        """Clear entire cache."""
        pass
    
    def get_stats(self) -> dict:
        """Return cache statistics (hits, misses, size)."""
        pass
```

**Cache Storage Options:**
1. **JSON files:** One file per foundation EIN in `data/cache/snapshots/`
2. **SQLite:** Single database file with snapshots table
3. **In-memory with pickle backup:** Fast but needs persistence

Recommend: JSON files for simplicity and debuggability.

**Cache Key Format:** `{foundation_ein}.json`

**Cache Entry Format:**
```json
{
    "foundation_ein": "123456789",
    "snapshot_date": "2025-12-27T10:30:00",
    "data": { ... FunderSnapshot fields ... }
}
```

### Task 3: Create `enrichment/comparable_grant.py`

Find comparable grants for positioning context.

```python
@dataclass
class ComparableGrant:
    """A grant to a similar organization."""
    recipient_name: str
    recipient_ein: Optional[str]
    grant_amount: float
    grant_purpose: str
    grant_year: int
    similarity_reason: str  # e.g., "Same state, similar sector"


def find_comparable_grant(
    foundation_ein: str,
    client_state: str,
    client_ntee: Optional[str] = None,
    client_budget: Optional[float] = None
) -> Optional[ComparableGrant]:
    """
    Find a grant to an organization similar to the client.
    
    Priority:
    1. Same state AND similar NTEE
    2. Same state
    3. Similar NTEE
    4. Any recent grant
    
    Args:
        foundation_ein: The foundation
        client_state: Client's state (2-letter code)
        client_ntee: Client's NTEE code (optional)
        client_budget: Client's annual budget (optional)
        
    Returns:
        ComparableGrant or None if no grants found
    """
    pass


def find_multiple_comparable_grants(
    foundation_ein: str,
    client_state: str,
    client_ntee: Optional[str] = None,
    limit: int = 3
) -> list[ComparableGrant]:
    """Find multiple comparable grants for richer context."""
    pass
```

### Task 4: Create `enrichment/connections.py`

Find potential connections between client and foundation.

```python
@dataclass
class Connection:
    """A potential connection to a foundation."""
    connection_type: str  # 'board_overlap', 'shared_funder', 'prior_grant', 'none'
    description: str
    confidence: float  # 0-1, how confident we are in the match
    details: dict  # Additional context


def find_connections(
    foundation_ein: str,
    client_ein: str,
    client_board_members: Optional[list[str]] = None
) -> list[Connection]:
    """
    Find connections between client and foundation.
    
    Checks:
    1. Prior grants from this foundation to client
    2. Board member overlap (if board list provided)
    3. Shared funders (other foundations that fund both)
    
    Args:
        foundation_ein: The foundation
        client_ein: The client nonprofit's EIN
        client_board_members: Optional list of board member names
        
    Returns:
        List of Connection objects (may be empty)
    """
    pass


def check_prior_relationship(foundation_ein: str, client_ein: str) -> Optional[Connection]:
    """Check if foundation has previously funded the client."""
    pass


def find_board_overlap(
    foundation_ein: str, 
    client_board_members: list[str]
) -> list[Connection]:
    """
    Find board members who serve on both boards.
    
    Uses fuzzy matching (Jaro-Winkler) for name comparison.
    Threshold: 0.90 for confident match, 0.80-0.90 for possible match.
    """
    pass
```

**Board Data Source:**
- Foundation officers from `f990_2025.pf_officers` or Part VIII of 990-PF
- Client board from questionnaire (if provided)

### Task 5: Create `enrichment/__init__.py`

Export main functions.

```python
from .funder_snapshot import get_funder_snapshot, get_funder_snapshots_batch, FunderSnapshot
from .cache import SnapshotCache
from .comparable_grant import find_comparable_grant, ComparableGrant
from .connections import find_connections, Connection

__all__ = [
    'get_funder_snapshot',
    'get_funder_snapshots_batch', 
    'FunderSnapshot',
    'SnapshotCache',
    'find_comparable_grant',
    'ComparableGrant',
    'find_connections',
    'Connection'
]
```

---

## Output Files

| File | Description |
|------|-------------|
| `enrichment/__init__.py` | Package exports |
| `enrichment/funder_snapshot.py` | Main snapshot retrieval |
| `enrichment/cache.py` | Caching layer |
| `enrichment/comparable_grant.py` | Find similar grants |
| `enrichment/connections.py` | Find relationships |

---

## Done Criteria

- [ ] `get_funder_snapshot()` returns FunderSnapshot for any foundation EIN
- [ ] All 8 metrics populated (or None with reason if unavailable)
- [ ] Cache stores and retrieves snapshots correctly
- [ ] Cache respects TTL (expired entries not returned)
- [ ] `find_comparable_grant()` returns relevant grant
- [ ] `find_connections()` detects prior grants
- [ ] All functions handle missing data gracefully

---

## Verification Tests

### Test 1: Funder Snapshot
```python
from enrichment import get_funder_snapshot

# Use a well-known foundation
snapshot = get_funder_snapshot('SAMPLE_EIN')
print(f"Foundation: {snapshot.foundation_name}")
print(f"Annual giving: ${snapshot.annual_giving_total:,.0f}")
print(f"Typical grant: ${snapshot.typical_grant_median:,.0f}")
print(f"Top state: {snapshot.geographic_top_state} ({snapshot.geographic_top_state_pct:.0%})")
print(f"Repeat rate: {snapshot.repeat_funding_rate:.0%}")
print(f"Trend: {snapshot.funding_trend_direction}")
```

### Test 2: Cache
```python
from enrichment import get_funder_snapshot, SnapshotCache

cache = SnapshotCache()

# First call - should hit database
snapshot1 = get_funder_snapshot('SAMPLE_EIN', use_cache=True)
stats1 = cache.get_stats()
print(f"After first call - Hits: {stats1['hits']}, Misses: {stats1['misses']}")

# Second call - should hit cache
snapshot2 = get_funder_snapshot('SAMPLE_EIN', use_cache=True)
stats2 = cache.get_stats()
print(f"After second call - Hits: {stats2['hits']}, Misses: {stats2['misses']}")

assert stats2['hits'] == stats1['hits'] + 1
```

### Test 3: Comparable Grant
```python
from enrichment import find_comparable_grant

grant = find_comparable_grant(
    foundation_ein='SAMPLE_EIN',
    client_state='CA',
    client_ntee='B20'  # Education
)

if grant:
    print(f"Similar org: {grant.recipient_name}")
    print(f"Grant: ${grant.grant_amount:,.0f} for {grant.grant_purpose}")
    print(f"Reason: {grant.similarity_reason}")
else:
    print("No comparable grant found")
```

### Test 4: Connections
```python
from enrichment import find_connections

# Test with a known funder-recipient pair
connections = find_connections(
    foundation_ein='FUNDER_EIN',
    client_ein='RECIPIENT_EIN'
)

for conn in connections:
    print(f"Type: {conn.connection_type}")
    print(f"Description: {conn.description}")
```

### Test 5: Batch Performance
```python
import time
from enrichment import get_funder_snapshots_batch

# Get 10 foundation EINs
eins = ['EIN1', 'EIN2', ...]  # 10 EINs

start = time.time()
snapshots = get_funder_snapshots_batch(eins)
elapsed = time.time() - start

print(f"Batch of 10 snapshots: {elapsed:.1f} seconds")
assert elapsed < 60  # Should be under 1 minute
```

---

## Notes

### Error Handling

All functions should:
- Return None (not raise) for missing foundations
- Log warnings for data quality issues
- Provide meaningful error messages

### Data Quality

Some metrics may be unavailable:
- New foundations may have no trend data
- Small foundations may have few grants
- Recipient data may be incomplete

Handle gracefully with None values and document in FunderSnapshot.

### Performance

For report generation (5 foundations):
- With cold cache: ~30-60 seconds
- With warm cache: <1 second

---

## Handoff

After completion:
1. Run all verification tests
2. Test on 5 different foundations (varied sizes)
3. Verify cache works across sessions
4. PM reviews before proceeding to PROMPT_04

---

*Next: PROMPT_04 (Report Data Assembly)*
