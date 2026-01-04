"""
Snapshot caching layer.

Caches FunderSnapshot objects to avoid repeated database queries.
"""
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from config.settings import CACHE_DIR, CACHE_TTL_DAYS
from .snapshot import FunderSnapshot


class SnapshotCache:
    """File-based cache for FunderSnapshot objects."""

    def __init__(self, cache_dir: str = None, ttl_days: int = None):
        """
        Initialize cache.

        Args:
            cache_dir: Directory for cache files
            ttl_days: Cache TTL in days
        """
        self.cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR / "snapshots"
        self.ttl_days = ttl_days if ttl_days is not None else CACHE_TTL_DAYS
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, foundation_ein: str) -> str:
        """Generate cache key for a foundation."""
        return f"snapshot_{foundation_ein}.json"

    def _cache_path(self, foundation_ein: str) -> Path:
        """Get cache file path for a foundation."""
        return self.cache_dir / self._cache_key(foundation_ein)

    def get(self, foundation_ein: str) -> Optional[FunderSnapshot]:
        """
        Get cached snapshot if valid.

        Args:
            foundation_ein: Foundation EIN

        Returns:
            FunderSnapshot if cached and not expired, else None
        """
        path = self._cache_path(foundation_ein)

        if not path.exists():
            return None

        # Check TTL
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        if datetime.now() - mtime > timedelta(days=self.ttl_days):
            path.unlink()  # Delete expired cache
            return None

        # Load cached data
        try:
            with open(path) as f:
                data = json.load(f)
            return self._dict_to_snapshot(data)
        except (json.JSONDecodeError, KeyError):
            path.unlink()  # Delete corrupt cache
            return None

    def set(self, foundation_ein: str, snapshot: FunderSnapshot) -> None:
        """
        Cache a snapshot.

        Args:
            foundation_ein: Foundation EIN
            snapshot: FunderSnapshot to cache
        """
        path = self._cache_path(foundation_ein)

        data = snapshot.to_dict()
        data['_cached_at'] = datetime.now().isoformat()

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def invalidate(self, foundation_ein: str) -> bool:
        """
        Invalidate (delete) a cached snapshot.

        Args:
            foundation_ein: Foundation EIN

        Returns:
            True if cache existed and was deleted
        """
        path = self._cache_path(foundation_ein)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear_all(self) -> int:
        """
        Clear all cached snapshots.

        Returns:
            Number of cache entries deleted
        """
        count = 0
        for path in self.cache_dir.glob("snapshot_*.json"):
            path.unlink()
            count += 1
        return count

    def stats(self) -> dict:
        """Get cache statistics."""
        files = list(self.cache_dir.glob("snapshot_*.json"))
        total_size = sum(f.stat().st_size for f in files)

        return {
            'entries': len(files),
            'total_size_bytes': total_size,
            'cache_dir': str(self.cache_dir),
            'ttl_days': self.ttl_days
        }

    def _dict_to_snapshot(self, data: dict) -> FunderSnapshot:
        """Convert cached dict back to FunderSnapshot."""
        # Extract nested values
        annual = data.get('annual_giving', {})
        typical = data.get('typical_grant', {})
        geo = data.get('geographic_focus', {})
        repeat = data.get('repeat_funding', {})
        style = data.get('giving_style', {})
        profile = data.get('recipient_profile', {})
        trend = data.get('funding_trend', {})
        comparable = data.get('comparable_grant', {})

        return FunderSnapshot(
            foundation_ein=data['foundation_ein'],
            foundation_name=data.get('foundation_name', ''),

            annual_giving_total=annual.get('total', 0),
            annual_giving_count=annual.get('count', 0),
            annual_giving_year=annual.get('year', 0),

            typical_grant_median=typical.get('median', 0),
            typical_grant_min=typical.get('min', 0),
            typical_grant_max=typical.get('max', 0),
            typical_grant_avg=typical.get('avg', 0),

            geographic_top_state=geo.get('top_state', ''),
            geographic_top_state_pct=geo.get('top_state_pct', 0),
            geographic_in_state_pct=geo.get('in_state_pct', 0),
            geographic_foundation_state=geo.get('foundation_state', ''),

            repeat_funding_unique=repeat.get('unique_recipients', 0),
            repeat_funding_repeat=repeat.get('repeat_recipients', 0),
            repeat_funding_rate=repeat.get('rate', 0),

            giving_style_general_pct=style.get('general_support_pct', 0.5),
            giving_style_program_pct=style.get('program_specific_pct', 0.5),

            recipient_budget_min=profile.get('budget_min', 0),
            recipient_budget_max=profile.get('budget_max', 0),
            recipient_budget_median=profile.get('budget_median', 0),
            recipient_primary_sector=profile.get('primary_sector', ''),
            recipient_primary_sector_pct=profile.get('primary_sector_pct', 0),

            funding_trend_direction=trend.get('direction', 'Stable'),
            funding_trend_change_pct=trend.get('change_pct', 0),
            funding_trend_oldest_year=trend.get('oldest_year', 0),
            funding_trend_newest_year=trend.get('newest_year', 0),

            comparable_grant_recipient=comparable.get('recipient_name', ''),
            comparable_grant_amount=comparable.get('amount', 0),
            comparable_grant_purpose=comparable.get('purpose', ''),
            comparable_grant_year=comparable.get('year', 0)
        )


# Global cache instance
_cache = None


def get_cache() -> SnapshotCache:
    """Get global cache instance."""
    global _cache
    if _cache is None:
        _cache = SnapshotCache()
    return _cache
