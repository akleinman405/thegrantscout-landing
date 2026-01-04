"""Scraper package for TheGrantScout Pipeline."""
from .scraper import (
    ScrapedContent,
    scrape_foundation_website,
    find_foundation_url,
    find_grants_page,
    fetch_page
)
from .extractors import (
    ExtractedFoundationData,
    extract_foundation_data,
    build_extraction_prompt,
    parse_extraction_response,
    create_empty_extraction
)
from .cache import ScraperCache
from .fallback import (
    ManualEntryTemplate,
    create_fallback,
    save_fallbacks_to_markdown
)

from typing import Tuple, List


def gather_foundation_data(
    foundation_ein: str,
    foundation_name: str,
    website_url: str = None,
    use_cache: bool = True,
    client_context: dict = None
) -> Tuple[ExtractedFoundationData, bool]:
    """
    Gather foundation data from website.

    Args:
        foundation_ein: Foundation EIN
        foundation_name: Foundation name
        website_url: Website URL (optional)
        use_cache: Whether to use cache
        client_context: Client context for relevance assessment

    Returns:
        (ExtractedFoundationData, success: bool)
    """
    cache = ScraperCache()

    # Check cache first
    if use_cache:
        cached = cache.get_extracted(foundation_ein)
        if cached:
            return cached, True

    try:
        # Scrape website
        scraped = scrape_foundation_website(
            foundation_name=foundation_name,
            website_url=website_url,
            foundation_ein=foundation_ein
        )

        # Cache scraped content
        if scraped.success:
            cache.set_scraped(scraped)

        if not scraped.success:
            return create_empty_extraction(scraped.error_message), False

        # Extract data using AI
        extracted = extract_foundation_data(scraped, client_context)

        # Cache extracted data
        if extracted.extraction_confidence > 0:
            cache.set_extracted(foundation_ein, extracted)

        return extracted, extracted.extraction_confidence > 0

    except Exception as e:
        return create_empty_extraction(str(e)), False


def gather_for_report(
    opportunities: List[dict],
    client_context: dict = None,
    use_cache: bool = True
) -> Tuple[List[dict], List[ManualEntryTemplate]]:
    """
    Gather data for all opportunities in a report.

    Args:
        opportunities: List of opportunity dictionaries
        client_context: Client context for relevance
        use_cache: Whether to use cache

    Returns:
        (updated_opportunities, fallback_templates)
    """
    fallbacks = []

    for opp in opportunities:
        extracted, success = gather_foundation_data(
            foundation_ein=opp.get('foundation_ein', ''),
            foundation_name=opp.get('foundation_name', ''),
            website_url=opp.get('portal_url'),
            use_cache=use_cache,
            client_context=client_context
        )

        if success and extracted.extraction_confidence > 0.3:
            # Update opportunity with extracted data
            if extracted.application_deadline:
                opp['deadline'] = extracted.application_deadline
            if extracted.application_url:
                opp['portal_url'] = extracted.application_url
            if extracted.contact_name:
                opp['contact_name'] = extracted.contact_name
            if extracted.contact_email:
                opp['contact_email'] = extracted.contact_email
            if extracted.contact_phone:
                opp['contact_phone'] = extracted.contact_phone
            if extracted.application_requirements:
                opp['application_requirements'] = extracted.application_requirements
        else:
            # Create fallback for manual entry
            fallbacks.append(create_fallback(
                foundation_ein=opp.get('foundation_ein', ''),
                foundation_name=opp.get('foundation_name', ''),
                website_url=opp.get('portal_url'),
                error=extracted.extraction_notes if extracted else "Extraction failed"
            ))

    return opportunities, fallbacks


__all__ = [
    # Scraper
    'ScrapedContent',
    'scrape_foundation_website',
    'find_foundation_url',
    'find_grants_page',
    'fetch_page',

    # Extractors
    'ExtractedFoundationData',
    'extract_foundation_data',
    'build_extraction_prompt',
    'parse_extraction_response',
    'create_empty_extraction',

    # Cache
    'ScraperCache',

    # Fallback
    'ManualEntryTemplate',
    'create_fallback',
    'save_fallbacks_to_markdown',

    # Main functions
    'gather_foundation_data',
    'gather_for_report'
]
