# PROMPT_06b: Phase 6b - AI Integration & Iteration

**Date:** 2025-12-27
**Phase:** 6b
**Agent:** Dev Team
**Estimated Time:** 4-5 hours
**Depends On:** PROMPT_06a (Prompt Templates) complete

---

## Objective

Integrate AI prompt templates with Claude API and create the narrative generation pipeline. Test and iterate on output quality.

---

## Context

Phase 6a created 5 prompt templates. This phase:
1. Builds the Python integration with Claude API
2. Creates fallback templates for API failures
3. Tests output quality and iterates on prompts

---

## Tasks

### Task 1: Create `ai/narratives.py`

Main narrative generation module.

```python
import anthropic
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import json

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
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        
        # Load templates
        self.templates = {
            'why_this_fits': load_prompt_template('why_this_fits'),
            'positioning_strategy': load_prompt_template('positioning_strategy'),
            'next_steps': load_prompt_template('next_steps'),
            'key_strengths': load_prompt_template('key_strengths'),
            'one_thing': load_prompt_template('one_thing')
        }
    
    def generate(self, template_name: str, context: dict, max_tokens: int = 500) -> str:
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
    
    def generate_next_steps(self, opportunity: dict) -> list[dict]:
        """Generate Next Steps as list of action items."""
        context = build_next_steps_context(opportunity)
        response = self.generate('next_steps', context, max_tokens=800)
        return parse_next_steps_response(response)
    
    def generate_key_strengths(self, client: dict, opportunities: list[dict]) -> list[str]:
        """Generate Key Strengths for executive summary."""
        context = build_key_strengths_context(client, opportunities)
        response = self.generate('key_strengths', context)
        return parse_key_strengths_response(response)
    
    def generate_one_thing(self, opportunities: list[dict]) -> str:
        """Generate One Thing This Week statement."""
        context = build_one_thing_context(opportunities)
        return self.generate('one_thing', context, max_tokens=100)


def build_why_this_fits_context(client: dict, opportunity: dict) -> dict:
    """Build context dict for Why This Fits template."""
    snapshot = opportunity.get('funder_snapshot', {})
    comparable = opportunity.get('comparable_grant')
    
    comparable_text = "No comparable grant identified."
    if comparable:
        comparable_text = f"{comparable['recipient_name']} received ${comparable['grant_amount']:,.0f} for {comparable['grant_purpose']} ({comparable['grant_year']})"
    
    return {
        'client_name': client.get('organization_name', ''),
        'client_mission': client.get('mission_statement', ''),
        'client_programs': ', '.join(client.get('program_areas', [])),
        'client_city': client.get('city', ''),
        'client_state': client.get('state', ''),
        'client_budget': client.get('budget', ''),
        
        'foundation_name': opportunity.get('foundation_name', ''),
        'annual_giving': snapshot.get('annual_giving_total', 0),
        'grant_count': snapshot.get('annual_giving_count', 0),
        'median_grant': snapshot.get('typical_grant_median', 0),
        'min_grant': snapshot.get('typical_grant_min', 0),
        'max_grant': snapshot.get('typical_grant_max', 0),
        'top_state': snapshot.get('geographic_top_state', ''),
        'top_state_pct': snapshot.get('geographic_top_state_pct', 0),
        'in_state_pct': snapshot.get('geographic_in_state_pct', 0),
        'general_support_pct': snapshot.get('giving_style_general_pct', 0),
        'program_specific_pct': snapshot.get('giving_style_program_pct', 0),
        'funding_trend': snapshot.get('funding_trend_direction', 'Stable'),
        
        'comparable_grant_text': comparable_text,
        'deadline': opportunity.get('deadline', 'Not specified')
    }


def build_positioning_context(client: dict, opportunity: dict) -> dict:
    """Build context dict for Positioning Strategy template."""
    snapshot = opportunity.get('funder_snapshot', {})
    connections = opportunity.get('potential_connections', [])
    
    connections_text = "No connections identified."
    if connections:
        connections_text = '\n'.join([f"- {c['connection_type']}: {c['description']}" for c in connections])
    
    return {
        'annual_giving': snapshot.get('annual_giving_total', 0),
        'grant_count': snapshot.get('annual_giving_count', 0),
        'median_grant': snapshot.get('typical_grant_median', 0),
        'min_grant': snapshot.get('typical_grant_min', 0),
        'max_grant': snapshot.get('typical_grant_max', 0),
        'top_state': snapshot.get('geographic_top_state', ''),
        'top_state_pct': snapshot.get('geographic_top_state_pct', 0),
        'in_state_pct': snapshot.get('geographic_in_state_pct', 0),
        'repeat_rate': snapshot.get('repeat_funding_rate', 0),
        'general_support_pct': snapshot.get('giving_style_general_pct', 0),
        'program_specific_pct': snapshot.get('giving_style_program_pct', 0),
        'budget_min': snapshot.get('recipient_budget_min', 0),
        'budget_max': snapshot.get('recipient_budget_max', 0),
        'primary_sector': snapshot.get('recipient_primary_sector', 'Various'),
        'funding_trend': snapshot.get('funding_trend_direction', 'Stable'),
        'trend_change_pct': snapshot.get('funding_trend_change_pct', 0),
        
        'client_city': client.get('city', ''),
        'client_state': client.get('state', ''),
        'client_budget': client.get('budget', ''),
        'client_strengths': ', '.join(client.get('program_areas', [])),
        
        'connections_text': connections_text
    }


def build_next_steps_context(opportunity: dict) -> dict:
    """Build context dict for Next Steps template."""
    from datetime import date
    
    requirements = opportunity.get('application_requirements', [])
    requirements_list = '\n'.join([f"- {r}" for r in requirements]) if requirements else "Not specified"
    
    return {
        'foundation_name': opportunity.get('foundation_name', ''),
        'deadline': opportunity.get('deadline', 'Rolling'),
        'contact_name': opportunity.get('contact_name', 'Not available'),
        'contact_email': opportunity.get('contact_email', 'Not available'),
        'prior_relationship': opportunity.get('prior_relationship', 'None'),
        'requirements_list': requirements_list,
        'today': date.today().strftime('%B %d, %Y')
    }


def build_key_strengths_context(client: dict, opportunities: list[dict]) -> dict:
    """Build context dict for Key Strengths template."""
    opp_summary = []
    for opp in opportunities:
        snapshot = opp.get('funder_snapshot', {})
        opp_summary.append(f"- {opp['foundation_name']}: {snapshot.get('geographic_top_state', 'N/A')} focus, ${snapshot.get('typical_grant_median', 0):,.0f} typical grant")
    
    return {
        'client_name': client.get('organization_name', ''),
        'client_city': client.get('city', ''),
        'client_state': client.get('state', ''),
        'client_programs': ', '.join(client.get('program_areas', [])),
        'client_budget': client.get('budget', ''),
        'opportunities_summary': '\n'.join(opp_summary)
    }


def build_one_thing_context(opportunities: list[dict]) -> dict:
    """Build context dict for One Thing template."""
    opp_list = []
    for opp in opportunities:
        opp_list.append(f"- {opp['foundation_name']}: Deadline {opp.get('deadline', 'Not specified')}, Contact: {opp.get('contact_name', 'N/A')}")
    
    return {
        'opportunities_with_deadlines': '\n'.join(opp_list)
    }


def parse_next_steps_response(response: str) -> list[dict]:
    """Parse Next Steps JSON response."""
    # Handle markdown code blocks
    if '```json' in response:
        response = response.split('```json')[1].split('```')[0]
    elif '```' in response:
        response = response.split('```')[1].split('```')[0]
    
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        # Fallback: return generic steps
        return [
            {"action": "Review application requirements", "deadline": "This week", "owner": "Grants Manager"},
            {"action": "Draft initial proposal outline", "deadline": "Next week", "owner": "Grants Manager"}
        ]


def parse_key_strengths_response(response: str) -> list[str]:
    """Parse Key Strengths response into list."""
    lines = response.strip().split('\n')
    strengths = []
    for line in lines:
        if line.strip() and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('**')):
            strengths.append(line.strip().lstrip('123.').strip())
    return strengths[:3]  # Ensure max 3
```

### Task 2: Create `ai/fallbacks.py`

Fallback templates when API fails or for dry-run mode.

```python
from datetime import date, timedelta

def fallback_why_this_fits(client: dict, opportunity: dict) -> str:
    """Generate fallback Why This Fits text."""
    snapshot = opportunity.get('funder_snapshot', {})
    
    return f"{opportunity['foundation_name']} has given ${snapshot.get('annual_giving_total', 0):,.0f} " \
           f"across {snapshot.get('annual_giving_count', 0)} grants in the most recent year. " \
           f"Their focus on {snapshot.get('geographic_top_state', 'multiple states')} aligns with your location. " \
           f"Review their giving patterns and recent grants to identify specific alignment with your programs."


def fallback_positioning_strategy(client: dict, opportunity: dict) -> str:
    """Generate fallback Positioning Strategy text."""
    snapshot = opportunity.get('funder_snapshot', {})
    
    median = snapshot.get('typical_grant_median', 0)
    general_pct = snapshot.get('giving_style_general_pct', 0.5)
    
    style = "general operating support" if general_pct > 0.5 else "program-specific funding"
    
    return f"Consider framing your request as {style} based on their giving patterns. " \
           f"A request in the ${median * 0.8:,.0f}-${median * 1.2:,.0f} range aligns with their typical grants. " \
           f"Emphasize your {client.get('state', '')} presence if applicable."


def fallback_next_steps(opportunity: dict) -> list[dict]:
    """Generate fallback Next Steps."""
    today = date.today()
    
    return [
        {
            "action": f"Research {opportunity['foundation_name']} recent grants and priorities",
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


def fallback_key_strengths(client: dict, opportunities: list[dict]) -> list[str]:
    """Generate fallback Key Strengths."""
    return [
        f"**Local Presence:** Your {client.get('state', '')} location aligns with multiple funders' geographic focus.",
        f"**Program Relevance:** Your work in {client.get('program_areas', ['your focus area'])[0] if client.get('program_areas') else 'your focus area'} matches funder priorities.",
        f"**Organizational Capacity:** Your {client.get('budget', 'budget')} positions you well for the typical grant sizes of this week's opportunities."
    ]


def fallback_one_thing(opportunities: list[dict]) -> str:
    """Generate fallback One Thing statement."""
    # Find opportunity with nearest deadline
    urgent = None
    for opp in opportunities:
        if opp.get('deadline') and opp['deadline'] != 'Rolling':
            if urgent is None:
                urgent = opp
            # Simple comparison - could be improved
    
    if urgent:
        return f"**Begin preparing your application to {urgent['foundation_name']} before their {urgent['deadline']} deadline.**"
    else:
        return f"**Research {opportunities[0]['foundation_name']} this week to assess fit and begin outreach.**"
```

### Task 3: Create Batch Generation Function

```python
# Add to ai/narratives.py

def generate_all_narratives(
    client: dict,
    opportunities: list[dict],
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
    
    generator = NarrativeGenerator()
    
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


def generate_all_fallbacks(client: dict, opportunities: list[dict]) -> dict:
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
```

---

## Output Files

| File | Description |
|------|-------------|
| `ai/__init__.py` | Package init |
| `ai/narratives.py` | Main generation module |
| `ai/fallbacks.py` | Fallback templates |

---

## Done Criteria

- [ ] `NarrativeGenerator` class works with Claude API
- [ ] All 5 narrative types generate successfully
- [ ] Fallbacks work when `use_fallbacks=True`
- [ ] API errors gracefully fall back
- [ ] Generated text is specific (references data)
- [ ] Generated text is appropriate length

---

## Verification Tests

### Test 1: Single Narrative
```python
from ai.narratives import NarrativeGenerator

generator = NarrativeGenerator()

# Mock data
client = {
    'organization_name': 'Sample Nonprofit',
    'mission_statement': 'We provide education services...',
    'state': 'CA',
    'city': 'Oakland',
    'budget': '$500,000 - $1 million',
    'program_areas': ['Education', 'Youth Development']
}

opportunity = {
    'foundation_name': 'Sample Foundation',
    'funder_snapshot': {
        'annual_giving_total': 2500000,
        'annual_giving_count': 45,
        'typical_grant_median': 45000,
        # ... other metrics
    }
}

result = generator.generate_why_this_fits(client, opportunity)
print(result)
```

### Test 2: Batch Generation
```python
from ai.narratives import generate_all_narratives

result = generate_all_narratives(client, opportunities, use_fallbacks=False)

print("Key Strengths:")
for s in result['executive_summary']['key_strengths']:
    print(f"  - {s}")

print(f"\nOne Thing: {result['executive_summary']['one_thing']}")
```

### Test 3: Fallback Mode
```python
from ai.narratives import generate_all_narratives

result = generate_all_narratives(client, opportunities, use_fallbacks=True)

# Should work without API key
print(result['opportunities'][0]['why_this_fits'])
```

### Test 4: Quality Check
```python
# For each generated narrative, check:
# 1. Contains specific numbers from funder snapshot
# 2. Mentions foundation name
# 3. Is 3-4 sentences (not too long)
# 4. Does not contain generic phrases like "good fit"
```

---

## Notes

### API Costs

Per report (5 opportunities):
- 5 × why_this_fits: ~2500 tokens
- 5 × positioning: ~2500 tokens
- 5 × next_steps: ~2500 tokens
- 1 × key_strengths: ~500 tokens
- 1 × one_thing: ~200 tokens

Total: ~8200 tokens per report ≈ $0.08-0.12 at Sonnet pricing

### Quality Iteration

If outputs are too generic:
1. Add more specific examples to prompts
2. Add "Do NOT use phrases like..." instructions
3. Increase required data references

---

## Handoff

After completion:
1. Generate narratives for 3 sample clients
2. Review output quality with checklist
3. Note any patterns of generic output
4. PM reviews before proceeding to PROMPT_07

---

*Next: PROMPT_07 (MD Assembly)*
