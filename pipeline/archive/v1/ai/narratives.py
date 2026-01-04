"""
AI narrative generation for grant reports.

Uses Claude API to generate customized narrative sections.
"""
import anthropic
from pathlib import Path
from typing import Optional, List, Dict
from datetime import date
import json
import os

from .fallbacks import (
    fallback_why_this_fits,
    fallback_positioning_strategy,
    fallback_next_steps,
    fallback_key_strengths,
    fallback_one_thing
)

# Load prompt templates
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt_template(name: str) -> str:
    """Load a prompt template from file."""
    path = PROMPTS_DIR / f"{name}.txt"
    with open(path) as f:
        return f.read()


class NarrativeGenerator:
    """Generate AI narratives for grant reports."""

    def __init__(self, api_key: str = None):
        """
        Initialize generator.

        Args:
            api_key: Anthropic API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"

        # Load templates
        self.templates = {
            'why_this_fits': load_prompt_template('why_this_fits'),
            'positioning_strategy': load_prompt_template('positioning_strategy'),
            'next_steps': load_prompt_template('next_steps'),
            'key_strengths': load_prompt_template('key_strengths'),
            'one_thing': load_prompt_template('one_thing')
        }

    def generate(
        self,
        template_name: str,
        context: dict,
        max_tokens: int = 500
    ) -> str:
        """
        Generate narrative using template and context.

        Args:
            template_name: Name of template to use
            context: Dict of variables to fill in template
            max_tokens: Max output tokens

        Returns:
            Generated text
        """
        template = self.templates[template_name]
        prompt = template.format(**context)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def generate_why_this_fits(self, client: dict, opportunity: dict) -> str:
        """Generate Why This Fits section."""
        context = build_why_this_fits_context(client, opportunity)
        return self.generate('why_this_fits', context)

    def generate_positioning_strategy(self, client: dict, opportunity: dict) -> str:
        """Generate Positioning Strategy section."""
        context = build_positioning_context(client, opportunity)
        return self.generate('positioning_strategy', context)

    def generate_next_steps(self, opportunity: dict) -> List[Dict[str, str]]:
        """Generate Next Steps as list of action items."""
        context = build_next_steps_context(opportunity)
        response = self.generate('next_steps', context, max_tokens=800)
        return parse_next_steps_response(response)

    def generate_key_strengths(
        self,
        client: dict,
        opportunities: List[dict]
    ) -> List[str]:
        """Generate Key Strengths for executive summary."""
        context = build_key_strengths_context(client, opportunities)
        response = self.generate('key_strengths', context)
        return parse_key_strengths_response(response)

    def generate_one_thing(self, opportunities: List[dict]) -> str:
        """Generate One Thing This Week statement."""
        context = build_one_thing_context(opportunities)
        return self.generate('one_thing', context, max_tokens=100)


def build_why_this_fits_context(client: dict, opportunity: dict) -> dict:
    """Build context dict for Why This Fits template."""
    snapshot = opportunity.get('funder_snapshot', {})
    comparable = opportunity.get('comparable_grant')

    comparable_text = "No comparable grant identified."
    if comparable:
        comparable_text = f"{comparable.get('recipient_name', 'An organization')} received ${comparable.get('amount', 0):,.0f} for {comparable.get('purpose_text', 'similar work')[:100]} ({comparable.get('tax_year', 'recent year')})"

    # Extract snapshot values
    annual = snapshot.get('annual_giving', {})
    typical = snapshot.get('typical_grant', {})
    geo = snapshot.get('geographic_focus', {})
    style = snapshot.get('giving_style', {})
    trend = snapshot.get('funding_trend', {})

    return {
        'client_name': client.get('organization_name', ''),
        'client_mission': client.get('mission_statement', '')[:500],
        'client_programs': ', '.join(client.get('program_areas', [])[:5]),
        'client_city': client.get('city', ''),
        'client_state': client.get('state', ''),
        'client_budget': client.get('budget', ''),

        'foundation_name': opportunity.get('foundation_name', ''),
        'annual_giving': annual.get('total', 0),
        'grant_count': annual.get('count', 0),
        'median_grant': typical.get('median', 0),
        'min_grant': typical.get('min', 0),
        'max_grant': typical.get('max', 0),
        'top_state': geo.get('top_state', 'Various'),
        'top_state_pct': geo.get('top_state_pct', 0),
        'in_state_pct': geo.get('in_state_pct', 0),
        'general_support_pct': style.get('general_support_pct', 0.5),
        'program_specific_pct': 1 - style.get('general_support_pct', 0.5),
        'funding_trend': trend.get('direction', 'Stable'),

        'comparable_grant_text': comparable_text,
        'deadline': opportunity.get('deadline', 'Not specified')
    }


def build_positioning_context(client: dict, opportunity: dict) -> dict:
    """Build context dict for Positioning Strategy template."""
    snapshot = opportunity.get('funder_snapshot', {})
    connections = opportunity.get('potential_connections', [])

    connections_text = "No connections identified."
    if connections:
        connections_text = '\n'.join([
            f"- {c.get('connection_type', 'Connection')}: {c.get('description', '')}"
            for c in connections
        ])

    # Extract snapshot values
    annual = snapshot.get('annual_giving', {})
    typical = snapshot.get('typical_grant', {})
    geo = snapshot.get('geographic_focus', {})
    repeat = snapshot.get('repeat_funding', {})
    style = snapshot.get('giving_style', {})
    recipient = snapshot.get('recipient_profile', {})
    trend = snapshot.get('funding_trend', {})

    return {
        'annual_giving': annual.get('total', 0),
        'grant_count': annual.get('count', 0),
        'median_grant': typical.get('median', 0),
        'min_grant': typical.get('min', 0),
        'max_grant': typical.get('max', 0),
        'top_state': geo.get('top_state', 'Various'),
        'top_state_pct': geo.get('top_state_pct', 0),
        'in_state_pct': geo.get('in_state_pct', 0),
        'repeat_rate': repeat.get('rate', 0),
        'general_support_pct': style.get('general_support_pct', 0.5),
        'program_specific_pct': 1 - style.get('general_support_pct', 0.5),
        'budget_min': recipient.get('budget_min', 0),
        'budget_max': recipient.get('budget_max', 0),
        'primary_sector': recipient.get('primary_sector', 'Various'),
        'funding_trend': trend.get('direction', 'Stable'),
        'trend_change_pct': trend.get('change_pct', 0),

        'client_city': client.get('city', ''),
        'client_state': client.get('state', ''),
        'client_budget': client.get('budget', ''),
        'client_strengths': ', '.join(client.get('program_areas', [])[:3]),

        'connections_text': connections_text
    }


def build_next_steps_context(opportunity: dict) -> dict:
    """Build context dict for Next Steps template."""
    requirements = opportunity.get('application_requirements', [])
    requirements_list = '\n'.join([f"- {r}" for r in requirements]) if requirements else "Not specified"

    return {
        'foundation_name': opportunity.get('foundation_name', ''),
        'deadline': opportunity.get('deadline', 'Rolling'),
        'contact_name': opportunity.get('contact_name', 'Not available'),
        'contact_email': opportunity.get('contact_email', 'Not available'),
        'prior_relationship': 'None',  # Could be enhanced
        'requirements_list': requirements_list,
        'today': date.today().strftime('%B %d, %Y')
    }


def build_key_strengths_context(client: dict, opportunities: List[dict]) -> dict:
    """Build context dict for Key Strengths template."""
    opp_summary = []
    for opp in opportunities:
        snapshot = opp.get('funder_snapshot', {})
        geo = snapshot.get('geographic_focus', {})
        typical = snapshot.get('typical_grant', {})
        opp_summary.append(
            f"- {opp.get('foundation_name', 'Foundation')}: "
            f"{geo.get('top_state', 'N/A')} focus, "
            f"${typical.get('median', 0):,.0f} typical grant"
        )

    return {
        'client_name': client.get('organization_name', ''),
        'client_city': client.get('city', ''),
        'client_state': client.get('state', ''),
        'client_programs': ', '.join(client.get('program_areas', [])[:5]),
        'client_budget': client.get('budget', ''),
        'opportunities_summary': '\n'.join(opp_summary)
    }


def build_one_thing_context(opportunities: List[dict]) -> dict:
    """Build context dict for One Thing template."""
    opp_list = []
    for opp in opportunities:
        opp_list.append(
            f"- {opp.get('foundation_name', 'Foundation')}: "
            f"Deadline {opp.get('deadline', 'Not specified')}, "
            f"Contact: {opp.get('contact_name', 'N/A')}"
        )

    return {
        'opportunities_with_deadlines': '\n'.join(opp_list),
        'today': date.today().strftime('%B %d, %Y')
    }


def parse_next_steps_response(response: str) -> List[Dict[str, str]]:
    """Parse Next Steps JSON response."""
    # Handle markdown code blocks
    clean = response.strip()
    if '```json' in clean:
        clean = clean.split('```json')[1].split('```')[0]
    elif '```' in clean:
        clean = clean.split('```')[1].split('```')[0]

    try:
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        # Fallback: return generic steps
        return [
            {"action": "Review application requirements", "deadline": "This week", "owner": "Grants Manager"},
            {"action": "Draft initial proposal outline", "deadline": "Next week", "owner": "Grants Manager"}
        ]


def parse_key_strengths_response(response: str) -> List[str]:
    """Parse Key Strengths response into list."""
    lines = response.strip().split('\n')
    strengths = []
    for line in lines:
        line = line.strip()
        if line and (
            line.startswith('1.') or
            line.startswith('2.') or
            line.startswith('3.') or
            line.startswith('**')
        ):
            # Remove leading numbers
            clean = line.lstrip('123.').strip()
            strengths.append(clean)
    return strengths[:3]  # Ensure max 3


def generate_all_narratives(
    client: dict,
    opportunities: List[dict],
    use_fallbacks: bool = False
) -> dict:
    """
    Generate all narrative sections for a report.

    Args:
        client: Client profile dict
        opportunities: List of opportunity dicts
        use_fallbacks: If True, use fallbacks instead of API

    Returns:
        Dict with all generated narratives
    """
    if use_fallbacks:
        return generate_all_fallbacks(client, opportunities)

    try:
        generator = NarrativeGenerator()
    except ValueError:
        # No API key - use fallbacks
        return generate_all_fallbacks(client, opportunities)

    # Generate per-opportunity narratives
    for opp in opportunities:
        try:
            opp['why_this_fits'] = generator.generate_why_this_fits(client, opp)
            opp['positioning_strategy'] = generator.generate_positioning_strategy(client, opp)
            opp['next_steps'] = generator.generate_next_steps(opp)
        except Exception as e:
            # Fall back on error
            opp['why_this_fits'] = fallback_why_this_fits(client, opp)
            opp['positioning_strategy'] = fallback_positioning_strategy(client, opp)
            opp['next_steps'] = fallback_next_steps(opp)

    # Generate executive summary narratives
    try:
        key_strengths = generator.generate_key_strengths(client, opportunities)
        one_thing = generator.generate_one_thing(opportunities)
    except Exception:
        key_strengths = fallback_key_strengths(client, opportunities)
        one_thing = fallback_one_thing(opportunities)

    return {
        'opportunities': opportunities,
        'executive_summary': {
            'key_strengths': key_strengths,
            'one_thing': one_thing
        }
    }


def generate_all_fallbacks(client: dict, opportunities: List[dict]) -> dict:
    """Generate all narratives using fallbacks only (no API)."""
    for opp in opportunities:
        opp['why_this_fits'] = fallback_why_this_fits(client, opp)
        opp['positioning_strategy'] = fallback_positioning_strategy(client, opp)
        opp['next_steps'] = fallback_next_steps(opp)

    return {
        'opportunities': opportunities,
        'executive_summary': {
            'key_strengths': fallback_key_strengths(client, opportunities),
            'one_thing': fallback_one_thing(opportunities)
        }
    }
