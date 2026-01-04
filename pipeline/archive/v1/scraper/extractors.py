"""
AI-powered extraction from scraped foundation website content.

Uses Claude API to parse grant application information from raw text.
"""
import anthropic
import json
from typing import Optional
from dataclasses import dataclass, field, asdict

from .scraper import ScrapedContent


@dataclass
class ExtractedFoundationData:
    """Structured data extracted from foundation website."""
    accepts_applications: Optional[bool] = None
    application_deadline: Optional[str] = None
    application_url: Optional[str] = None
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    application_requirements: list = field(default_factory=list)
    grant_amount_range: Optional[str] = None
    geographic_restrictions: Optional[str] = None
    sector_focus: Optional[str] = None
    extraction_confidence: float = 0.0
    extraction_notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


def build_extraction_prompt(raw_text: str, client_context: dict = None) -> str:
    """
    Build the extraction prompt for Claude.

    Args:
        raw_text: Raw text from website
        client_context: Optional context about the client for better matching

    Returns:
        Formatted prompt string
    """
    # Truncate if too long
    max_chars = 15000
    if len(raw_text) > max_chars:
        raw_text = raw_text[:max_chars] + "\n\n[Content truncated...]"

    context_section = ""
    if client_context:
        context_section = f"""
CLIENT CONTEXT (for relevance assessment):
- Organization: {client_context.get('organization_name', 'Unknown')}
- Focus Areas: {', '.join(client_context.get('program_areas', []))}
- Location: {client_context.get('state', 'Unknown')}

"""

    prompt = f"""You are extracting grant application information from a foundation website.

{context_section}WEBSITE CONTENT:
{raw_text}

Extract the following information. If not found, use null.

Respond in JSON format ONLY (no markdown, no explanation):
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

Be conservative - only extract information that is clearly stated. If the website is unclear about whether they accept applications, set accepts_applications to null.
"""

    return prompt


def parse_extraction_response(response_text: str) -> ExtractedFoundationData:
    """
    Parse Claude's JSON response into dataclass.

    Args:
        response_text: Raw response from Claude

    Returns:
        ExtractedFoundationData instance
    """
    # Clean up response - remove markdown code blocks if present
    clean_text = response_text.strip()

    if '```json' in clean_text:
        clean_text = clean_text.split('```json')[1].split('```')[0]
    elif '```' in clean_text:
        clean_text = clean_text.split('```')[1].split('```')[0]

    try:
        data = json.loads(clean_text.strip())
    except json.JSONDecodeError as e:
        # Return empty extraction with error note
        return ExtractedFoundationData(
            extraction_confidence=0.0,
            extraction_notes=f"Failed to parse JSON response: {str(e)}"
        )

    # Handle application_requirements - ensure it's a list
    requirements = data.get('application_requirements', [])
    if requirements is None:
        requirements = []
    elif isinstance(requirements, str):
        requirements = [requirements]

    return ExtractedFoundationData(
        accepts_applications=data.get('accepts_applications'),
        application_deadline=data.get('application_deadline'),
        application_url=data.get('application_url'),
        contact_name=data.get('contact_name'),
        contact_title=data.get('contact_title'),
        contact_email=data.get('contact_email'),
        contact_phone=data.get('contact_phone'),
        application_requirements=requirements,
        grant_amount_range=data.get('grant_amount_range'),
        geographic_restrictions=data.get('geographic_restrictions'),
        sector_focus=data.get('sector_focus'),
        extraction_confidence=float(data.get('extraction_confidence', 0.0)),
        extraction_notes=data.get('extraction_notes', '')
    )


def extract_foundation_data(
    scraped_content: ScrapedContent,
    client_context: dict = None
) -> ExtractedFoundationData:
    """
    Use Claude to extract structured data from raw website content.

    Args:
        scraped_content: ScrapedContent from scraper
        client_context: Optional client context for relevance

    Returns:
        ExtractedFoundationData with parsed information
    """
    if not scraped_content.success or not scraped_content.raw_text:
        return ExtractedFoundationData(
            extraction_confidence=0.0,
            extraction_notes=scraped_content.error_message or "No content to extract"
        )

    try:
        client = anthropic.Anthropic()

        prompt = build_extraction_prompt(scraped_content.raw_text, client_context)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        return parse_extraction_response(response.content[0].text)

    except anthropic.APIError as e:
        return ExtractedFoundationData(
            extraction_confidence=0.0,
            extraction_notes=f"API error: {str(e)}"
        )

    except Exception as e:
        return ExtractedFoundationData(
            extraction_confidence=0.0,
            extraction_notes=f"Extraction failed: {str(e)}"
        )


def create_empty_extraction(error_message: str = "") -> ExtractedFoundationData:
    """
    Create empty extraction result with error message.

    Args:
        error_message: Description of why extraction failed

    Returns:
        Empty ExtractedFoundationData
    """
    return ExtractedFoundationData(
        extraction_confidence=0.0,
        extraction_notes=error_message or "No data extracted"
    )
