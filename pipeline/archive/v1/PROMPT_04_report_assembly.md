# PROMPT_04: Phase 4 - Report Data Assembly

**Date:** 2025-12-27
**Phase:** 4
**Agent:** Dev Team
**Estimated Time:** 4-5 hours
**Depends On:** PROMPT_02 (Scoring) + PROMPT_03b (Enrichment) complete

---

## Objective

Create the data assembly layer that combines scoring results, funder enrichment, and client data into a structured report data object.

---

## Context

At this point we have:
- **Scoring:** `score_nonprofit()` returns top N foundations
- **Enrichment:** `get_funder_snapshot()` returns foundation intelligence

This phase combines them with client data to create the complete data structure needed for report generation.

---

## Tasks

### Task 1: Create `schemas/report_schema.json`

Define the complete schema for report data.

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "GrantScoutReport",
    "type": "object",
    "required": ["client", "report_meta", "opportunities"],
    "properties": {
        "client": {
            "type": "object",
            "properties": {
                "organization_name": {"type": "string"},
                "ein": {"type": ["string", "null"]},
                "email": {"type": "string"},
                "state": {"type": "string"},
                "city": {"type": ["string", "null"]},
                "budget": {"type": "string"},
                "budget_numeric": {"type": ["number", "null"]},
                "grant_size_target": {"type": "string"},
                "org_type": {"type": "string"},
                "program_areas": {"type": "array", "items": {"type": "string"}},
                "populations_served": {"type": "array", "items": {"type": "string"}},
                "geographic_scope": {"type": "string"},
                "ntee_code": {"type": ["string", "null"]},
                "mission_statement": {"type": "string"},
                "prior_funders": {"type": "array", "items": {"type": "string"}},
                "notes": {"type": ["string", "null"]}
            }
        },
        "report_meta": {
            "type": "object",
            "properties": {
                "week_number": {"type": "integer"},
                "report_date": {"type": "string", "format": "date"},
                "urgent_count": {"type": "integer"},
                "urgent_nearest_date": {"type": ["string", "null"]},
                "total_potential_funding_min": {"type": "number"},
                "total_potential_funding_max": {"type": "number"}
            }
        },
        "opportunities": {
            "type": "array",
            "items": {"$ref": "#/definitions/opportunity"},
            "minItems": 5,
            "maxItems": 5
        },
        "executive_summary": {
            "type": "object",
            "properties": {
                "one_thing": {"type": "string"},
                "urgent_actions": {"type": "array"},
                "funding_scenarios": {"type": "object"},
                "key_strengths": {"type": "array", "items": {"type": "string"}}
            }
        },
        "timeline": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "week": {"type": "integer"},
                    "dates": {"type": "string"},
                    "focus": {"type": "string"},
                    "milestones": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    },
    "definitions": {
        "opportunity": {
            "type": "object",
            "properties": {
                "rank": {"type": "integer"},
                "foundation_ein": {"type": "string"},
                "foundation_name": {"type": "string"},
                "match_score": {"type": "number"},
                "match_probability": {"type": "number"},
                
                "funder_snapshot": {"type": "object"},
                "comparable_grant": {"type": ["object", "null"]},
                "potential_connections": {"type": "array"},
                
                "amount_min": {"type": ["number", "null"]},
                "amount_max": {"type": ["number", "null"]},
                "deadline": {"type": ["string", "null"]},
                "portal_url": {"type": ["string", "null"]},
                "contact_name": {"type": ["string", "null"]},
                "contact_email": {"type": ["string", "null"]},
                "contact_phone": {"type": ["string", "null"]},
                "application_requirements": {"type": "array", "items": {"type": "string"}},
                
                "why_this_fits": {"type": ["string", "null"]},
                "positioning_strategy": {"type": ["string", "null"]},
                "next_steps": {"type": "array"},
                
                "status": {"type": "string", "enum": ["URGENT", "HIGH", "MEDIUM"]},
                "effort": {"type": "string", "enum": ["Low", "Medium", "High"]},
                "fit_score": {"type": "integer", "minimum": 1, "maximum": 10}
            }
        }
    }
}
```

### Task 2: Create `loaders/questionnaire.py`

Load and parse client questionnaire data.

```python
import pandas as pd
from pathlib import Path
from typing import Optional, Union
from dataclasses import dataclass

@dataclass
class ClientProfile:
    """Parsed client questionnaire data."""
    organization_name: str
    ein: Optional[str]
    email: str
    state: str
    city: Optional[str]
    budget: str
    budget_numeric: Optional[float]
    grant_size_target: str
    org_type: str
    program_areas: list[str]
    populations_served: list[str]
    geographic_scope: str
    ntee_code: Optional[str]
    mission_statement: str
    prior_funders: list[str]
    notes: Optional[str]


def load_questionnaire(
    path: Union[str, Path] = None,
    organization_name: str = None
) -> ClientProfile:
    """
    Load client profile from questionnaire CSV.
    
    Args:
        path: Path to questionnaire CSV (default: data/questionnaires/*.csv)
        organization_name: Filter to specific organization
        
    Returns:
        ClientProfile object
    """
    pass


def parse_budget_string(budget_str: str) -> Optional[float]:
    """
    Parse budget string to numeric value.
    
    Examples:
        "$100,000 - $500,000" -> 300000 (midpoint)
        "Under $100,000" -> 50000
        "$1 million - $5 million" -> 3000000
    """
    pass


def parse_list_field(value: str, delimiter: str = ';') -> list[str]:
    """Parse semicolon-separated list into list of strings."""
    pass


def get_all_clients(path: Union[str, Path] = None) -> list[ClientProfile]:
    """Load all clients from questionnaire."""
    pass
```

**Column Mapping (from actual questionnaire):**

| CSV Column | ClientProfile Field |
|------------|---------------------|
| Organization Name | organization_name |
| Email Address (The one you want us to send...) | email |
| Organization Type | org_type |
| Where is your organization headquartered? | state |
| What City is your organization located in? | city |
| Your most recent annual budget... | budget |
| What size grants are you typically looking for? | grant_size_target |
| What are your organization's primary program areas? | program_areas |
| Select all populations your organization primarily serves | populations_served |
| What geographic range does your organization serve? | geographic_scope |
| If you know your IRS NTEE classification code... | ntee_code |
| In 1-2 sentences, what does your organization do? | mission_statement |
| Which funders have you received grants from... | prior_funders |
| Anything else we should know... | notes |

### Task 3: Create `loaders/client_data.py`

Enrich client profile with database data (if EIN available).

```python
from typing import Optional
from .questionnaire import ClientProfile

@dataclass
class EnrichedClient(ClientProfile):
    """Client profile enriched with database data."""
    # From database (if EIN found)
    db_assets: Optional[float] = None
    db_revenue: Optional[float] = None
    db_employees: Optional[int] = None
    db_ntee: Optional[str] = None
    db_mission: Optional[str] = None
    db_founding_year: Optional[int] = None
    
    # Prior funding from our database
    db_prior_funders: list[str] = None  # EINs of foundations that funded this org
    db_total_grants_received: Optional[int] = None


def enrich_client(client: ClientProfile) -> EnrichedClient:
    """
    Enrich client profile with database data.
    
    Args:
        client: Parsed questionnaire data
        
    Returns:
        EnrichedClient with additional database fields
    """
    pass


def find_client_ein(organization_name: str, state: str) -> Optional[str]:
    """
    Try to find client's EIN by name and state.
    
    Uses fuzzy matching against nonprofit database.
    """
    pass


def get_client_prior_funders(client_ein: str) -> list[str]:
    """Get list of foundation EINs that have funded this client."""
    pass
```

### Task 4: Create `assembly/report_data.py`

Main assembly function.

```python
from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional
import json

from scoring.scoring import GrantScorer
from enrichment import get_funder_snapshot, find_comparable_grant, find_connections
from loaders.questionnaire import load_questionnaire, ClientProfile
from loaders.client_data import enrich_client, get_client_prior_funders


@dataclass
class ReportData:
    """Complete data structure for report generation."""
    client: dict
    report_meta: dict
    opportunities: list[dict]
    executive_summary: dict
    timeline: list[dict]
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self, path: str = None) -> str:
        """Export to JSON."""
        data = self.to_dict()
        if path:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        return json.dumps(data, indent=2, default=str)
    
    @classmethod
    def from_json(cls, path: str) -> 'ReportData':
        """Load from JSON."""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)


def assemble_report_data(
    client_identifier: str,  # Organization name or EIN
    questionnaire_path: str = None,
    top_k: int = 5,
    exclude_prior_funders: bool = True,
    week_number: int = None
) -> ReportData:
    """
    Assemble complete report data for a client.
    
    Args:
        client_identifier: Organization name or EIN
        questionnaire_path: Path to questionnaire CSV
        top_k: Number of opportunities to include
        exclude_prior_funders: If True, don't recommend foundations that already fund client
        week_number: Week number for report (default: auto-calculate)
        
    Returns:
        ReportData object ready for rendering
    """
    # 1. Load client data
    client = load_questionnaire(questionnaire_path, client_identifier)
    enriched_client = enrich_client(client)
    
    # 2. Score and get top foundations
    scorer = GrantScorer()
    prior_funders = get_client_prior_funders(enriched_client.ein) if enriched_client.ein else []
    matches = scorer.score_nonprofit(
        recipient_ein=enriched_client.ein,
        top_k=top_k * 2,  # Get extra in case some are filtered
        exclude_prior_funders=exclude_prior_funders
    )
    
    # 3. Build opportunities
    opportunities = []
    for i, match in matches.head(top_k).iterrows():
        opp = build_opportunity(
            rank=len(opportunities) + 1,
            match=match,
            client=enriched_client
        )
        opportunities.append(opp)
    
    # 4. Build report metadata
    report_meta = build_report_meta(opportunities, week_number)
    
    # 5. Build executive summary (placeholders for AI)
    executive_summary = build_executive_summary_placeholder(opportunities, enriched_client)
    
    # 6. Build timeline
    timeline = build_timeline_placeholder(opportunities)
    
    return ReportData(
        client=enriched_client_to_dict(enriched_client),
        report_meta=report_meta,
        opportunities=opportunities,
        executive_summary=executive_summary,
        timeline=timeline
    )


def build_opportunity(rank: int, match: pd.Series, client: EnrichedClient) -> dict:
    """
    Build opportunity data structure for one foundation.
    
    Combines scoring data with enrichment.
    """
    foundation_ein = match['foundation_ein']
    
    # Get enrichment data
    snapshot = get_funder_snapshot(foundation_ein)
    comparable = find_comparable_grant(
        foundation_ein=foundation_ein,
        client_state=client.state,
        client_ntee=client.ntee_code
    )
    connections = find_connections(
        foundation_ein=foundation_ein,
        client_ein=client.ein
    )
    
    # Calculate derived fields
    fit_score = calculate_fit_score(match['match_probability'])
    effort = estimate_effort(snapshot)
    status = determine_status(deadline=None)  # Will be filled by scraper
    
    return {
        'rank': rank,
        'foundation_ein': foundation_ein,
        'foundation_name': match.get('foundation_name', snapshot.foundation_name),
        'match_score': round(match['match_score'], 1),
        'match_probability': round(match['match_probability'], 3),
        
        'funder_snapshot': snapshot.to_dict() if snapshot else None,
        'comparable_grant': comparable.__dict__ if comparable else None,
        'potential_connections': [c.__dict__ for c in connections],
        
        # Placeholders - filled by scraper (Phase 5)
        'amount_min': snapshot.typical_grant_min if snapshot else None,
        'amount_max': snapshot.typical_grant_max if snapshot else None,
        'deadline': None,
        'portal_url': None,
        'contact_name': None,
        'contact_email': None,
        'contact_phone': None,
        'application_requirements': [],
        
        # Placeholders - filled by AI (Phase 6)
        'why_this_fits': None,
        'positioning_strategy': None,
        'next_steps': [],
        
        'status': status,
        'effort': effort,
        'fit_score': fit_score
    }


def calculate_fit_score(probability: float) -> int:
    """Convert probability (0-1) to fit score (1-10)."""
    return max(1, min(10, round(probability * 10)))


def estimate_effort(snapshot) -> str:
    """Estimate application effort based on foundation characteristics."""
    if not snapshot:
        return 'Medium'
    
    # Small foundations tend to have simpler applications
    if snapshot.annual_giving_count < 20:
        return 'Low'
    elif snapshot.annual_giving_count > 100:
        return 'High'
    else:
        return 'Medium'


def determine_status(deadline: str = None) -> str:
    """Determine opportunity status based on deadline."""
    if not deadline:
        return 'MEDIUM'
    
    # Parse deadline and compare to today
    # URGENT if < 30 days, HIGH if < 60 days
    # ... implementation
    return 'MEDIUM'


def build_report_meta(opportunities: list[dict], week_number: int = None) -> dict:
    """Build report metadata."""
    today = date.today()
    
    # Calculate week number if not provided
    if week_number is None:
        week_number = today.isocalendar()[1]
    
    # Calculate funding range
    funding_min = sum(o.get('amount_min', 0) or 0 for o in opportunities)
    funding_max = sum(o.get('amount_max', 0) or 0 for o in opportunities)
    
    # Count urgent
    urgent = [o for o in opportunities if o.get('status') == 'URGENT']
    
    return {
        'week_number': week_number,
        'report_date': today.isoformat(),
        'urgent_count': len(urgent),
        'urgent_nearest_date': None,  # Will be filled after scraping
        'total_potential_funding_min': funding_min,
        'total_potential_funding_max': funding_max
    }


def build_executive_summary_placeholder(opportunities: list, client) -> dict:
    """Create placeholder for executive summary (filled by AI)."""
    return {
        'one_thing': None,  # AI generates
        'urgent_actions': [],  # AI generates based on deadlines
        'funding_scenarios': {
            'conservative': {'opportunities': '1-2', 'funding': None},
            'moderate': {'opportunities': '2-3', 'funding': None},
            'ambitious': {'opportunities': '4-5', 'funding': None}
        },
        'key_strengths': []  # AI generates
    }


def build_timeline_placeholder(opportunities: list) -> list[dict]:
    """Create 8-week timeline placeholder."""
    from datetime import timedelta
    today = date.today()
    
    timeline = []
    for week in range(1, 9):
        week_start = today + timedelta(weeks=week-1)
        week_end = week_start + timedelta(days=6)
        
        timeline.append({
            'week': week,
            'dates': f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}",
            'focus': None,  # AI fills
            'milestones': []  # AI fills
        })
    
    return timeline
```

---

## Output Files

| File | Description |
|------|-------------|
| `schemas/report_schema.json` | JSON schema for validation |
| `loaders/__init__.py` | Package init |
| `loaders/questionnaire.py` | Questionnaire parser |
| `loaders/client_data.py` | Client enrichment |
| `assembly/__init__.py` | Package init |
| `assembly/report_data.py` | Main assembly |

---

## Done Criteria

- [ ] Schema defines all required fields
- [ ] Questionnaire loader parses all columns correctly
- [ ] Budget string parsing works for all formats
- [ ] Client enrichment retrieves database data
- [ ] `assemble_report_data()` returns complete structure
- [ ] All 5 opportunities have funder snapshots
- [ ] Comparable grants found for most opportunities
- [ ] Report data exports to valid JSON

---

## Verification Tests

### Test 1: Questionnaire Loading
```python
from loaders.questionnaire import load_questionnaire, get_all_clients

clients = get_all_clients('data/questionnaires/Grant_Alerts_Questionnaire.csv')
print(f"Loaded {len(clients)} clients")

for client in clients[:3]:
    print(f"  - {client.organization_name} ({client.state})")
    print(f"    Budget: {client.budget}")
    print(f"    Programs: {client.program_areas}")
```

### Test 2: Budget Parsing
```python
from loaders.questionnaire import parse_budget_string

test_cases = [
    "$100,000 - $500,000",
    "Under $100,000",
    "$1 million - $5 million",
    "$500,000 - $1 million"
]

for budget in test_cases:
    numeric = parse_budget_string(budget)
    print(f"{budget} -> ${numeric:,.0f}")
```

### Test 3: Full Assembly
```python
from assembly.report_data import assemble_report_data

report = assemble_report_data(
    client_identifier="Sample Nonprofit",  # Use real name from questionnaire
    questionnaire_path="data/questionnaires/Grant_Alerts_Questionnaire.csv"
)

print(f"Client: {report.client['organization_name']}")
print(f"Report date: {report.report_meta['report_date']}")
print(f"Opportunities: {len(report.opportunities)}")

for opp in report.opportunities:
    print(f"  {opp['rank']}. {opp['foundation_name']} (Score: {opp['match_score']})")
```

### Test 4: JSON Export
```python
from assembly.report_data import assemble_report_data

report = assemble_report_data("Sample Nonprofit")
report.to_json("outputs/test_report_data.json")

# Validate against schema
import jsonschema
with open('schemas/report_schema.json') as f:
    schema = json.load(f)
    
jsonschema.validate(report.to_dict(), schema)
print("Schema validation passed!")
```

---

## Notes

### Missing Data Handling

When data is unavailable:
- Use None for optional fields
- Use empty list [] for list fields
- Use placeholder strings for required text fields

### Performance

Assembly should complete in < 60 seconds for one client (5 opportunities):
- Scoring: ~30 sec
- Enrichment: ~20 sec (with cold cache)
- Assembly: ~5 sec

### Placeholders for Later Phases

These fields are populated by later phases:
- `deadline`, `portal_url`, `contact_*`: Phase 5 (Scraper)
- `why_this_fits`, `positioning_strategy`, `next_steps`: Phase 6 (AI)
- `executive_summary`, `timeline`: Phase 6 (AI)

---

## Handoff

After completion:
1. Run assembly on 3 different clients
2. Export JSON and validate against schema
3. Note any fields consistently missing
4. PM reviews before proceeding to PROMPT_05

---

*Next: PROMPT_05 (Foundation Data Gathering)*
