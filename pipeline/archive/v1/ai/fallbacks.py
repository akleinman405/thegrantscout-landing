"""
Fallback templates for AI narratives.

Used when API fails or for dry-run mode.
"""
from datetime import date, timedelta
from typing import List, Dict


def fallback_why_this_fits(client: dict, opportunity: dict) -> str:
    """Generate fallback Why This Fits text."""
    snapshot = opportunity.get('funder_snapshot', {})

    return f"{opportunity.get('foundation_name', 'This foundation')} has given ${snapshot.get('annual_giving', {}).get('total', 0):,.0f} " \
           f"across {snapshot.get('annual_giving', {}).get('count', 0)} grants in the most recent year. " \
           f"Their focus on {snapshot.get('geographic_focus', {}).get('top_state', 'multiple states')} aligns with your location. " \
           f"Review their giving patterns and recent grants to identify specific alignment with your programs."


def fallback_positioning_strategy(client: dict, opportunity: dict) -> str:
    """Generate fallback Positioning Strategy text."""
    snapshot = opportunity.get('funder_snapshot', {})

    median = snapshot.get('typical_grant', {}).get('median', 0)
    general_pct = snapshot.get('giving_style', {}).get('general_support_pct', 0.5)

    style = "general operating support" if general_pct > 0.5 else "program-specific funding"

    return f"Consider framing your request as {style} based on their giving patterns. " \
           f"A request in the ${median * 0.8:,.0f}-${median * 1.2:,.0f} range aligns with their typical grants. " \
           f"Emphasize your {client.get('state', '')} presence if applicable."


def fallback_next_steps(opportunity: dict) -> List[Dict[str, str]]:
    """Generate fallback Next Steps."""
    today = date.today()
    foundation_name = opportunity.get('foundation_name', 'the foundation')

    return [
        {
            "action": f"Research {foundation_name} recent grants and priorities",
            "deadline": (today + timedelta(days=7)).strftime('%B %d'),
            "owner": "Grants Manager"
        },
        {
            "action": "Draft initial inquiry or LOI concept",
            "deadline": (today + timedelta(days=14)).strftime('%B %d'),
            "owner": "Grants Manager"
        },
        {
            "action": "Review draft with Executive Director",
            "deadline": (today + timedelta(days=21)).strftime('%B %d'),
            "owner": "ED"
        }
    ]


def fallback_key_strengths(client: dict, opportunities: List[dict]) -> List[str]:
    """Generate fallback Key Strengths."""
    program_area = client.get('program_areas', ['your focus area'])
    first_area = program_area[0] if program_area else 'your focus area'

    return [
        f"**Local Presence:** Your {client.get('state', '')} location aligns with multiple funders' geographic focus.",
        f"**Program Relevance:** Your work in {first_area} matches funder priorities.",
        f"**Organizational Capacity:** Your {client.get('budget', 'budget')} positions you well for the typical grant sizes of this week's opportunities."
    ]


def fallback_one_thing(opportunities: List[dict]) -> str:
    """Generate fallback One Thing statement."""
    if not opportunities:
        return "**Review this week's grant opportunities and prioritize based on deadlines and fit.**"

    # Find opportunity with nearest deadline
    urgent = None
    for opp in opportunities:
        deadline = opp.get('deadline', '')
        if deadline and deadline not in ('Rolling', 'Not specified', 'Unknown'):
            if urgent is None:
                urgent = opp

    if urgent:
        return f"**Begin preparing your application to {urgent['foundation_name']} before their {urgent['deadline']} deadline.**"
    else:
        return f"**Research {opportunities[0].get('foundation_name', 'the top foundation')} this week to assess fit and begin outreach.**"
