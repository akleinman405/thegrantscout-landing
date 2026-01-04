"""
Fallback handling for when scraping fails.

Generates templates for manual data entry.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class ManualEntryTemplate:
    """Template for manual data entry when scraping fails."""
    foundation_ein: str
    foundation_name: str
    website_url: Optional[str] = None
    scrape_error: str = ""
    fields_needed: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_markdown(self) -> str:
        """Generate markdown template for manual entry."""
        website_display = self.website_url or 'Not found'

        return f"""## Manual Entry Needed: {self.foundation_name}

**EIN:** {self.foundation_ein}
**Website:** {website_display}
**Scrape Error:** {self.scrape_error}
**Created:** {self.created_at.strftime('%Y-%m-%d %H:%M')}

### Fields to Complete:

- [ ] Accepts Applications: Yes / No / By Invitation Only
- [ ] Application Deadline: _______________
- [ ] Application URL: _______________
- [ ] Contact Name: _______________
- [ ] Contact Title: _______________
- [ ] Contact Email: _______________
- [ ] Contact Phone: _______________
- [ ] Grant Amount Range: _______________
- [ ] Geographic Restrictions: _______________
- [ ] Sector Focus: _______________
- [ ] Application Requirements:
  - [ ] _______________
  - [ ] _______________
  - [ ] _______________

### Notes:

_______________

---
"""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'foundation_ein': self.foundation_ein,
            'foundation_name': self.foundation_name,
            'website_url': self.website_url,
            'scrape_error': self.scrape_error,
            'fields_needed': self.fields_needed,
            'created_at': self.created_at.isoformat()
        }


def create_fallback(
    foundation_ein: str,
    foundation_name: str,
    website_url: str = None,
    error: str = "Scrape failed"
) -> ManualEntryTemplate:
    """
    Create a manual entry template when scraping fails.

    Args:
        foundation_ein: Foundation EIN
        foundation_name: Foundation name
        website_url: Website URL (if known)
        error: Error description

    Returns:
        ManualEntryTemplate instance
    """
    return ManualEntryTemplate(
        foundation_ein=foundation_ein,
        foundation_name=foundation_name,
        website_url=website_url,
        scrape_error=error,
        fields_needed=[
            'accepts_applications',
            'application_deadline',
            'application_url',
            'contact_name',
            'contact_email',
            'contact_phone',
            'application_requirements'
        ]
    )


def save_fallbacks_to_markdown(
    fallbacks: List[ManualEntryTemplate],
    output_path: str
) -> None:
    """
    Save multiple fallback templates to a markdown file.

    Args:
        fallbacks: List of ManualEntryTemplate instances
        output_path: Path to save markdown file
    """
    if not fallbacks:
        return

    content = f"""# Manual Entry Required

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Foundations needing manual entry:** {len(fallbacks)}

---

"""
    for template in fallbacks:
        content += template.to_markdown() + "\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def load_manual_entries(markdown_path: str) -> dict:
    """
    Parse completed manual entry markdown file.

    This is a placeholder for parsing manually filled templates.
    In practice, you might want to use a different format (JSON, CSV)
    for easier parsing.

    Args:
        markdown_path: Path to filled markdown file

    Returns:
        Dictionary mapping EINs to extracted data
    """
    # This would need custom parsing based on your workflow
    # For now, return empty dict as placeholder
    return {}
