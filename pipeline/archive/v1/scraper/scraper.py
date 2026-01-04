"""
Website scraper for foundation grant information.

Fetches and parses foundation websites to extract grant-related content.
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
import re

from config.database import query_df


@dataclass
class ScrapedContent:
    """Raw scraped content from a foundation website."""
    foundation_ein: str
    foundation_name: str
    url: str
    raw_html: str
    raw_text: str
    page_title: str
    scrape_timestamp: datetime
    success: bool
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'foundation_ein': self.foundation_ein,
            'foundation_name': self.foundation_name,
            'url': self.url,
            'raw_html_length': len(self.raw_html),
            'raw_text_length': len(self.raw_text),
            'page_title': self.page_title,
            'scrape_timestamp': self.scrape_timestamp.isoformat(),
            'success': self.success,
            'error_message': self.error_message
        }


def fetch_page(url: str, timeout: int = 10) -> Tuple[str, str, str]:
    """
    Fetch page content.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        (raw_html, raw_text, page_title) tuple
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; GrantScout/1.0; +https://thegrantscout.com)'
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Get page title
    page_title = soup.title.string if soup.title else ''

    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript']):
        element.decompose()

    raw_text = soup.get_text(separator='\n', strip=True)

    return response.text, raw_text, page_title


def find_foundation_url(
    foundation_name: str,
    foundation_ein: str = None
) -> Optional[str]:
    """
    Find foundation's website URL if not in database.

    Strategies:
    1. Check database for stored URL
    2. Search common patterns

    Args:
        foundation_name: Foundation name
        foundation_ein: EIN (for database lookup)

    Returns:
        Website URL if found
    """
    # Strategy 1: Check database
    if foundation_ein:
        query = """
        SELECT website_url
        FROM f990_2025.pf_returns
        WHERE ein = %(ein)s
          AND website_url IS NOT NULL
          AND website_url != ''
          AND website_url NOT IN ('N/A', 'NONE', '0')
        ORDER BY tax_year DESC
        LIMIT 1
        """
        df = query_df(query, {'ein': foundation_ein})
        if not df.empty and df.iloc[0]['website_url']:
            url = df.iloc[0]['website_url']
            # Ensure URL has protocol
            if not url.startswith('http'):
                url = 'https://' + url
            return url

    # Strategy 2: Try common patterns (basic implementation)
    # Clean foundation name for URL guessing
    name_clean = foundation_name.lower()
    name_clean = re.sub(r'(foundation|fund|inc\.?|corp\.?|the)\s*', '', name_clean)
    name_clean = re.sub(r'[^a-z0-9\s]', '', name_clean)
    name_clean = name_clean.strip().replace(' ', '')

    if name_clean:
        # Try common patterns
        patterns = [
            f"https://www.{name_clean}foundation.org",
            f"https://www.{name_clean}.org",
            f"https://{name_clean}foundation.org",
        ]

        for url in patterns:
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return url
            except:
                continue

    return None


def find_grants_page(base_url: str) -> Optional[str]:
    """
    Try to find the grants/grantmaking page on a foundation site.

    Args:
        base_url: Foundation homepage URL

    Returns:
        Grants page URL if found
    """
    # Common grant page paths
    grant_paths = [
        '/grants',
        '/grantmaking',
        '/apply',
        '/for-grantseekers',
        '/for-nonprofits',
        '/grant-programs',
        '/apply-for-a-grant',
        '/how-to-apply',
        '/grant-application'
    ]

    # Normalize base URL
    base_url = base_url.rstrip('/')

    for path in grant_paths:
        try:
            test_url = base_url + path
            response = requests.head(test_url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return test_url
        except:
            continue

    return None


def scrape_foundation_website(
    foundation_name: str,
    website_url: str = None,
    foundation_ein: str = None
) -> ScrapedContent:
    """
    Scrape a foundation's website for grant information.

    Args:
        foundation_name: Foundation name (for URL finding if needed)
        website_url: Direct URL (if known)
        foundation_ein: EIN (for caching/lookup)

    Returns:
        ScrapedContent with raw HTML and text
    """
    timestamp = datetime.now()

    # Find URL if not provided
    if not website_url:
        website_url = find_foundation_url(foundation_name, foundation_ein)

    if not website_url:
        return ScrapedContent(
            foundation_ein=foundation_ein or '',
            foundation_name=foundation_name,
            url='',
            raw_html='',
            raw_text='',
            page_title='',
            scrape_timestamp=timestamp,
            success=False,
            error_message='Could not find foundation website URL'
        )

    try:
        # First try to find grants-specific page
        grants_url = find_grants_page(website_url)
        target_url = grants_url or website_url

        # Add polite delay
        time.sleep(1)

        raw_html, raw_text, page_title = fetch_page(target_url)

        return ScrapedContent(
            foundation_ein=foundation_ein or '',
            foundation_name=foundation_name,
            url=target_url,
            raw_html=raw_html,
            raw_text=raw_text,
            page_title=page_title,
            scrape_timestamp=timestamp,
            success=True
        )

    except requests.exceptions.Timeout:
        return ScrapedContent(
            foundation_ein=foundation_ein or '',
            foundation_name=foundation_name,
            url=website_url,
            raw_html='',
            raw_text='',
            page_title='',
            scrape_timestamp=timestamp,
            success=False,
            error_message='Request timed out'
        )

    except requests.exceptions.RequestException as e:
        return ScrapedContent(
            foundation_ein=foundation_ein or '',
            foundation_name=foundation_name,
            url=website_url,
            raw_html='',
            raw_text='',
            page_title='',
            scrape_timestamp=timestamp,
            success=False,
            error_message=f'Request failed: {str(e)}'
        )

    except Exception as e:
        return ScrapedContent(
            foundation_ein=foundation_ein or '',
            foundation_name=foundation_name,
            url=website_url,
            raw_html='',
            raw_text='',
            page_title='',
            scrape_timestamp=timestamp,
            success=False,
            error_message=f'Scraping failed: {str(e)}'
        )
