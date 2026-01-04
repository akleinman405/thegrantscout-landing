# PROMPT_05: Phase 5 - Foundation Data Gathering

**Date:** 2025-12-27
**Phase:** 5
**Agent:** Dev Team
**Estimated Time:** 5-6 hours
**Depends On:** PROMPT_04 (Report Assembly) complete

---

## Objective

Create a system to gather missing foundation data (deadlines, contacts, application requirements) from foundation websites using scraping + AI extraction.

---

## Context

After Phase 4, we have report data with these gaps:
- `deadline` - Application deadline
- `portal_url` - Application portal URL
- `contact_name`, `contact_email`, `contact_phone` - Program officer contact
- `application_requirements` - List of required documents

These must be scraped from foundation websites and parsed using AI.

---

## Approach

**Two-step process:**
1. **Scrape:** Fetch raw HTML/text from foundation website
2. **Extract:** Use Claude API to parse relevant fields from raw content

**Why AI extraction?** Foundation websites have wildly different structures. AI can handle varied formats without custom code per foundation.

---

## Tasks

### Task 1: Create `scraper/scraper.py`

Main scraper module.

```python
import requests
from bs4 import BeautifulSoup
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

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
        foundation_ein: EIN (for caching)
        
    Returns:
        ScrapedContent with raw HTML and text
    """
    pass


def find_foundation_url(foundation_name: str) -> Optional[str]:
    """
    Find foundation's website URL if not in database.
    
    Strategies:
    1. Check database for stored URL
    2. Search common patterns
    """
    pass


def fetch_page(url: str, timeout: int = 10) -> tuple[str, str]:
    """
    Fetch page content.
    
    Returns:
        (raw_html, raw_text) tuple
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; GrantScout/1.0; +https://thegrantscout.com)'
    }
    
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()
    
    raw_text = soup.get_text(separator='\n', strip=True)
    
    return response.text, raw_text


def find_grants_page(base_url: str) -> Optional[str]:
    """
    Try to find the grants/grantmaking page on a foundation site.
    
    Common patterns:
    - /grants, /grantmaking, /apply, /for-grantseekers
    """
    pass
```

### Task 2: Create `scraper/extractors.py`

AI-powered extraction from raw content.

```python
import anthropic
from typing import Optional
from dataclasses import dataclass

@dataclass
class ExtractedFoundationData:
    """Structured data extracted from foundation website."""
    accepts_applications: bool
    application_deadline: Optional[str]
    application_url: Optional[str]
    contact_name: Optional[str]
    contact_title: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    application_requirements: list[str]
    grant_amount_range: Optional[str]
    geographic_restrictions: Optional[str]
    sector_focus: Optional[str]
    extraction_confidence: float
    extraction_notes: str


def extract_foundation_data(
    scraped_content: ScrapedContent,
    client_context: dict = None
) -> ExtractedFoundationData:
    """
    Use Claude to extract structured data from raw website content.
    """
    client = anthropic.Anthropic()
    
    prompt = build_extraction_prompt(scraped_content.raw_text, client_context)
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return parse_extraction_response(response.content[0].text)


def build_extraction_prompt(raw_text: str, client_context: dict = None) -> str:
    """Build the extraction prompt."""
    
    max_chars = 15000
    if len(raw_text) > max_chars:
        raw_text = raw_text[:max_chars] + "\n\n[Content truncated...]"
    
    prompt = f"""You are extracting grant application information from a foundation website.

WEBSITE CONTENT:
{raw_text}

Extract the following information. If not found, use null.

Respond in JSON format:
{{
    "accepts_applications": true/false/null,
    "application_deadline": "date string or 'Rolling' or 'By invitation only' or null",
    "application_url": "URL string or null",
    "contact_name": "Name or null",
    "contact_title": "Title or null", 
    "contact_email": "email@domain.com or null",
    "contact_phone": "phone number or null",
    "application_requirements": ["requirement 1", "requirement 2", ...],
    "grant_amount_range": "$X - $Y or null",
    "geographic_restrictions": "description or null",
    "sector_focus": "areas of focus or null",
    "extraction_confidence": 0.0-1.0,
    "extraction_notes": "any caveats or uncertainties"
}}

Be conservative - only extract information that is clearly stated.
"""
    
    return prompt


def parse_extraction_response(response_text: str) -> ExtractedFoundationData:
    """Parse Claude's JSON response into dataclass."""
    import json
    
    if '```json' in response_text:
        response_text = response_text.split('```json')[1].split('```')[0]
    elif '```' in response_text:
        response_text = response_text.split('```')[1].split('```')[0]
    
    data = json.loads(response_text.strip())
    
    return ExtractedFoundationData(**data)
```

### Task 3: Create `scraper/cache.py`

Cache for scraped and extracted data.

```python
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Optional

class ScraperCache:
    """Cache for scraped foundation data."""
    
    def __init__(self, cache_dir: str = "data/cache/scraper", ttl_days: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(days=ttl_days)
    
    def get_scraped(self, foundation_ein: str) -> Optional[ScrapedContent]:
        """Get cached scraped content."""
        pass
    
    def set_scraped(self, content: ScrapedContent) -> None:
        """Cache scraped content."""
        pass
    
    def get_extracted(self, foundation_ein: str) -> Optional[ExtractedFoundationData]:
        """Get cached extracted data."""
        pass
    
    def set_extracted(self, foundation_ein: str, data: ExtractedFoundationData) -> None:
        """Cache extracted data."""
        pass
```

### Task 4: Create `scraper/fallback.py`

Fallback for when scraping fails.

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass 
class ManualEntryTemplate:
    """Template for manual data entry when scraping fails."""
    foundation_ein: str
    foundation_name: str
    website_url: Optional[str]
    scrape_error: str
    fields_needed: list[str]
    
    def to_markdown(self) -> str:
        """Generate markdown template for manual entry."""
        return f"""## Manual Entry Needed: {self.foundation_name}

**EIN:** {self.foundation_ein}
**Website:** {self.website_url or 'Not found'}
**Scrape Error:** {self.scrape_error}

### Fields to Complete:

- [ ] Application Deadline: _______________
- [ ] Application URL: _______________
- [ ] Contact Name: _______________
- [ ] Contact Email: _______________
- [ ] Contact Phone: _______________
- [ ] Application Requirements:
  - [ ] _______________
- [ ] Accepts Applications: Yes / No / By Invitation
"""


def create_fallback(
    foundation_ein: str,
    foundation_name: str,
    website_url: str = None,
    error: str = "Scrape failed"
) -> ManualEntryTemplate:
    """Create a manual entry template when scraping fails."""
    return ManualEntryTemplate(
        foundation_ein=foundation_ein,
        foundation_name=foundation_name,
        website_url=website_url,
        scrape_error=error,
        fields_needed=['deadline', 'contact', 'requirements']
    )
```

### Task 5: Create Main Gathering Function

```python
# In scraper/__init__.py

def gather_foundation_data(
    foundation_ein: str,
    foundation_name: str,
    website_url: str = None,
    use_cache: bool = True
) -> tuple[ExtractedFoundationData, bool]:
    """
    Gather foundation data from website.
    
    Returns:
        (ExtractedFoundationData, success: bool)
    """
    cache = ScraperCache()
    
    if use_cache:
        cached = cache.get_extracted(foundation_ein)
        if cached:
            return cached, True
    
    try:
        scraped = scrape_foundation_website(
            foundation_name=foundation_name,
            website_url=website_url,
            foundation_ein=foundation_ein
        )
        
        if not scraped.success:
            return create_empty_extraction(scraped.error_message), False
        
        extracted = extract_foundation_data(scraped)
        cache.set_extracted(foundation_ein, extracted)
        
        return extracted, True
        
    except Exception as e:
        return create_empty_extraction(str(e)), False


def gather_for_report(opportunities: list[dict]) -> tuple[list[dict], list[ManualEntryTemplate]]:
    """
    Gather data for all opportunities in a report.
    
    Returns:
        (updated_opportunities, fallback_templates)
    """
    fallbacks = []
    
    for opp in opportunities:
        extracted, success = gather_foundation_data(
            foundation_ein=opp['foundation_ein'],
            foundation_name=opp['foundation_name'],
            website_url=opp.get('portal_url')
        )
        
        if success:
            opp['deadline'] = extracted.application_deadline
            opp['portal_url'] = extracted.application_url or opp.get('portal_url')
            opp['contact_name'] = extracted.contact_name
            opp['contact_email'] = extracted.contact_email
            opp['contact_phone'] = extracted.contact_phone
            opp['application_requirements'] = extracted.application_requirements
        else:
            fallbacks.append(create_fallback(
                foundation_ein=opp['foundation_ein'],
                foundation_name=opp['foundation_name'],
                website_url=opp.get('portal_url'),
                error=extracted.extraction_notes
            ))
    
    return opportunities, fallbacks
```

---

## Output Files

| File | Description |
|------|-------------|
| `scraper/__init__.py` | Package init with exports |
| `scraper/scraper.py` | Website scraping |
| `scraper/extractors.py` | AI extraction |
| `scraper/cache.py` | Caching layer |
| `scraper/fallback.py` | Manual entry fallback |

---

## Done Criteria

- [ ] `scrape_foundation_website()` fetches content from URLs
- [ ] `extract_foundation_data()` calls Claude API and parses response
- [ ] Cache stores and retrieves data
- [ ] Fallback templates generated for failed scrapes
- [ ] `gather_for_report()` updates opportunities list
- [ ] Works on 8/10 test foundation websites

---

## Verification Tests

### Test 1: Basic Scrape
```python
from scraper import scrape_foundation_website

content = scrape_foundation_website(
    foundation_name="Ford Foundation",
    website_url="https://www.fordfoundation.org/work/our-grants/"
)
print(f"Success: {content.success}")
print(f"Text length: {len(content.raw_text)} chars")
```

### Test 2: AI Extraction
```python
from scraper import scrape_foundation_website, extract_foundation_data

content = scrape_foundation_website("Sample Foundation", "https://example.org/grants")
extracted = extract_foundation_data(content)
print(f"Deadline: {extracted.application_deadline}")
print(f"Contact: {extracted.contact_email}")
```

### Test 3: Batch for Report
```python
from scraper import gather_for_report

opportunities = [...]  # Mock opportunities
updated, fallbacks = gather_for_report(opportunities)
print(f"Fallbacks needed: {len(fallbacks)}")
```

---

## Notes

### Rate Limiting
- Add 1-2 second delay between requests
- Use polite User-Agent string

### AI Extraction Costs
~$0.01 per foundation at Sonnet pricing. For 5 foundations: ~$0.05 per report.

---

## Handoff

After completion:
1. Test on 10 diverse foundation websites
2. Document success rate
3. PM reviews before proceeding to PROMPT_06a

---

*Next: PROMPT_06a (AI Prompt Templates)*
