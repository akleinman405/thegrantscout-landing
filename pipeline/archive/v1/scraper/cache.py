"""
Cache for scraped and extracted foundation data.

Stores data to avoid repeated scraping and API calls.
"""
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Optional

from .scraper import ScrapedContent
from .extractors import ExtractedFoundationData


class ScraperCache:
    """Cache for scraped foundation data."""

    def __init__(
        self,
        cache_dir: str = "data/cache/scraper",
        ttl_days: int = 30
    ):
        """
        Initialize cache.

        Args:
            cache_dir: Directory for cache files
            ttl_days: Time-to-live in days
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(days=ttl_days)

        # Sub-directories for different cache types
        self.scraped_dir = self.cache_dir / "scraped"
        self.extracted_dir = self.cache_dir / "extracted"
        self.scraped_dir.mkdir(exist_ok=True)
        self.extracted_dir.mkdir(exist_ok=True)

    def _is_valid(self, cache_file: Path) -> bool:
        """Check if cache file is still valid (not expired)."""
        if not cache_file.exists():
            return False

        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        return datetime.now() - mtime < self.ttl

    def _get_cache_path(self, cache_type: str, foundation_ein: str) -> Path:
        """Get cache file path for an EIN."""
        ein_clean = foundation_ein.replace('-', '')
        if cache_type == 'scraped':
            return self.scraped_dir / f"{ein_clean}.json"
        else:
            return self.extracted_dir / f"{ein_clean}.json"

    def get_scraped(self, foundation_ein: str) -> Optional[ScrapedContent]:
        """
        Get cached scraped content.

        Args:
            foundation_ein: Foundation EIN

        Returns:
            ScrapedContent if found and valid, None otherwise
        """
        cache_path = self._get_cache_path('scraped', foundation_ein)

        if not self._is_valid(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return ScrapedContent(
                foundation_ein=data['foundation_ein'],
                foundation_name=data['foundation_name'],
                url=data['url'],
                raw_html=data.get('raw_html', ''),
                raw_text=data.get('raw_text', ''),
                page_title=data.get('page_title', ''),
                scrape_timestamp=datetime.fromisoformat(data['scrape_timestamp']),
                success=data['success'],
                error_message=data.get('error_message')
            )

        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def set_scraped(self, content: ScrapedContent) -> None:
        """
        Cache scraped content.

        Args:
            content: ScrapedContent to cache
        """
        if not content.foundation_ein:
            return

        cache_path = self._get_cache_path('scraped', content.foundation_ein)

        data = {
            'foundation_ein': content.foundation_ein,
            'foundation_name': content.foundation_name,
            'url': content.url,
            'raw_text': content.raw_text,  # Don't cache raw_html (too large)
            'page_title': content.page_title,
            'scrape_timestamp': content.scrape_timestamp.isoformat(),
            'success': content.success,
            'error_message': content.error_message
        }

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def get_extracted(self, foundation_ein: str) -> Optional[ExtractedFoundationData]:
        """
        Get cached extracted data.

        Args:
            foundation_ein: Foundation EIN

        Returns:
            ExtractedFoundationData if found and valid, None otherwise
        """
        cache_path = self._get_cache_path('extracted', foundation_ein)

        if not self._is_valid(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return ExtractedFoundationData(
                accepts_applications=data.get('accepts_applications'),
                application_deadline=data.get('application_deadline'),
                application_url=data.get('application_url'),
                contact_name=data.get('contact_name'),
                contact_title=data.get('contact_title'),
                contact_email=data.get('contact_email'),
                contact_phone=data.get('contact_phone'),
                application_requirements=data.get('application_requirements', []),
                grant_amount_range=data.get('grant_amount_range'),
                geographic_restrictions=data.get('geographic_restrictions'),
                sector_focus=data.get('sector_focus'),
                extraction_confidence=data.get('extraction_confidence', 0.0),
                extraction_notes=data.get('extraction_notes', '')
            )

        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def set_extracted(
        self,
        foundation_ein: str,
        data: ExtractedFoundationData
    ) -> None:
        """
        Cache extracted data.

        Args:
            foundation_ein: Foundation EIN
            data: ExtractedFoundationData to cache
        """
        if not foundation_ein:
            return

        cache_path = self._get_cache_path('extracted', foundation_ein)

        cache_data = {
            'foundation_ein': foundation_ein,
            'cached_at': datetime.now().isoformat(),
            'accepts_applications': data.accepts_applications,
            'application_deadline': data.application_deadline,
            'application_url': data.application_url,
            'contact_name': data.contact_name,
            'contact_title': data.contact_title,
            'contact_email': data.contact_email,
            'contact_phone': data.contact_phone,
            'application_requirements': data.application_requirements,
            'grant_amount_range': data.grant_amount_range,
            'geographic_restrictions': data.geographic_restrictions,
            'sector_focus': data.sector_focus,
            'extraction_confidence': data.extraction_confidence,
            'extraction_notes': data.extraction_notes
        }

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)

    def clear(self, foundation_ein: str = None) -> int:
        """
        Clear cache entries.

        Args:
            foundation_ein: Specific EIN to clear, or None for all

        Returns:
            Number of entries cleared
        """
        cleared = 0

        if foundation_ein:
            # Clear specific EIN
            for cache_type in ['scraped', 'extracted']:
                cache_path = self._get_cache_path(cache_type, foundation_ein)
                if cache_path.exists():
                    cache_path.unlink()
                    cleared += 1
        else:
            # Clear all
            for cache_path in self.scraped_dir.glob("*.json"):
                cache_path.unlink()
                cleared += 1
            for cache_path in self.extracted_dir.glob("*.json"):
                cache_path.unlink()
                cleared += 1

        return cleared

    def stats(self) -> dict:
        """Get cache statistics."""
        scraped_count = len(list(self.scraped_dir.glob("*.json")))
        extracted_count = len(list(self.extracted_dir.glob("*.json")))

        return {
            'scraped_count': scraped_count,
            'extracted_count': extracted_count,
            'cache_dir': str(self.cache_dir),
            'ttl_days': self.ttl.days
        }
