"""
Report data assembly module.

Combines client data, scoring, and enrichment into a complete report structure.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import json

from loaders import (
    ClientProfile,
    load_questionnaire,
    enrich_client,
    get_client_officers,
    lookup_client_by_ein
)
from scoring import GrantScorer
from enrichment import (
    get_funder_snapshot,
    find_connections,
    FunderSnapshot,
    Connection
)


@dataclass
class Opportunity:
    """A single grant opportunity in the report."""
    rank: int
    foundation_ein: str
    foundation_name: str

    # Match info
    match_score: float
    match_probability: float
    same_state: bool
    foundation_state: str

    # Funder snapshot
    funder_snapshot: Dict[str, Any] = field(default_factory=dict)

    # Comparable grant
    comparable_grant: Optional[Dict[str, Any]] = None

    # Connections
    potential_connections: List[Dict[str, Any]] = field(default_factory=list)

    # Amount estimate (from typical grant)
    amount_min: float = 0
    amount_max: float = 0

    # Deadline and status (placeholder - populated by scraping)
    deadline: str = "Rolling"
    status: str = "HIGH"  # HIGH, MEDIUM, LOW
    effort: str = "Medium"  # Low, Medium, High
    fit_score: int = 8  # 1-10

    # Application info (placeholder - populated by scraping)
    portal_url: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    application_requirements: List[str] = field(default_factory=list)

    # AI narratives (placeholder - populated by AI)
    why_this_fits: str = ""
    positioning_strategy: str = ""
    next_steps: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'rank': self.rank,
            'foundation_ein': self.foundation_ein,
            'foundation_name': self.foundation_name,
            'match_score': self.match_score,
            'match_probability': self.match_probability,
            'same_state': self.same_state,
            'foundation_state': self.foundation_state,
            'funder_snapshot': self.funder_snapshot,
            'comparable_grant': self.comparable_grant,
            'potential_connections': self.potential_connections,
            'amount_min': self.amount_min,
            'amount_max': self.amount_max,
            'deadline': self.deadline,
            'status': self.status,
            'effort': self.effort,
            'fit_score': self.fit_score,
            'portal_url': self.portal_url,
            'contact_name': self.contact_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'application_requirements': self.application_requirements,
            'why_this_fits': self.why_this_fits,
            'positioning_strategy': self.positioning_strategy,
            'next_steps': self.next_steps
        }


@dataclass
class ReportData:
    """Complete report data structure."""

    # Client info
    client: Dict[str, Any] = field(default_factory=dict)

    # Report metadata
    report_meta: Dict[str, Any] = field(default_factory=dict)

    # Opportunities (top 5)
    opportunities: List[Opportunity] = field(default_factory=list)

    # Executive summary (populated by AI)
    executive_summary: Dict[str, Any] = field(default_factory=dict)

    # Timeline (8 weeks)
    timeline: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'client': self.client,
            'report_meta': self.report_meta,
            'opportunities': [opp.to_dict() for opp in self.opportunities],
            'executive_summary': self.executive_summary,
            'timeline': self.timeline
        }

    def to_json(self, path: str) -> None:
        """Save to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


def calculate_effort(snapshot: Dict) -> str:
    """Estimate application effort based on foundation characteristics."""
    # Higher repeat rate = easier to get funded if you're already in
    repeat_rate = snapshot.get('repeat_funding', {}).get('rate', 0)

    # Higher general support = less work to apply
    general_pct = snapshot.get('giving_style', {}).get('general_support_pct', 0.5)

    if general_pct > 0.6 and repeat_rate > 0.4:
        return "Low"
    elif general_pct < 0.4 or repeat_rate > 0.7:
        return "High"
    else:
        return "Medium"


def calculate_fit_score(
    match_score: float,
    same_state: bool,
    snapshot: Dict,
    client_budget: float
) -> int:
    """Calculate 1-10 fit score."""
    score = match_score / 10  # Start with 0-10 from match

    # Bonus for same state
    if same_state:
        score += 0.5

    # Check budget alignment
    budget_min = snapshot.get('recipient_profile', {}).get('budget_min', 0)
    budget_max = snapshot.get('recipient_profile', {}).get('budget_max', 0)

    if budget_min > 0 and budget_max > 0:
        if budget_min <= client_budget <= budget_max:
            score += 0.5  # Budget in range
        elif client_budget < budget_min * 0.5 or client_budget > budget_max * 2:
            score -= 1  # Way outside range

    return max(1, min(10, int(round(score))))


def assemble_report_data(
    client_identifier: str,
    questionnaire_path: str = None,
    top_k: int = 5,
    week_number: int = None
) -> ReportData:
    """
    Assemble complete report data for a client.

    Args:
        client_identifier: Organization name or EIN
        questionnaire_path: Optional path to questionnaire CSV
        top_k: Number of top matches to include
        week_number: Week number for report header

    Returns:
        ReportData with all sections populated
    """
    # Load client data
    if len(client_identifier) == 9 and client_identifier.isdigit():
        # It's an EIN
        client = lookup_client_by_ein(client_identifier)
        if not client:
            raise ValueError(f"Client not found by EIN: {client_identifier}")
    else:
        # It's a name
        client = load_questionnaire(questionnaire_path, client_identifier)
        if not client:
            raise ValueError(f"Client not found: {client_identifier}")

    # Enrich client data
    client = enrich_client(client)

    # Get client officers for connection finding
    client_officers = get_client_officers(client.ein) if client.ein else []

    # Score foundations
    scorer = GrantScorer()

    if client.ein:
        # Use EIN for scoring
        matches = scorer.score_nonprofit(
            recipient_ein=client.ein,
            top_k=top_k * 2,  # Get extra for filtering
            exclude_prior_funders=True
        )
    else:
        # Can't score without EIN - would need alternative approach
        raise ValueError(f"Cannot score client without EIN: {client.organization_name}")

    # Take top K
    matches = matches.head(top_k)

    # Build opportunities
    opportunities = []
    for idx, match_row in matches.iterrows():
        rank = match_row['match_rank']
        f_ein = match_row['foundation_ein']
        f_name = match_row.get('foundation_name', '')

        # Get funder snapshot
        snapshot = get_funder_snapshot(
            f_ein,
            client_state=client.state,
            client_ntee=client.ntee_code[:1] if client.ntee_code else ''
        )
        snapshot_dict = snapshot.to_dict()

        # Get connections
        connections = find_connections(
            foundation_ein=f_ein,
            client_ein=client.ein,
            client_state=client.state,
            client_ntee=client.ntee_code,
            client_officers=client_officers
        )

        # Build opportunity
        opp = Opportunity(
            rank=rank,
            foundation_ein=f_ein,
            foundation_name=f_name or snapshot.foundation_name,
            match_score=match_row['match_score'],
            match_probability=match_row['match_probability'],
            same_state=match_row['same_state'],
            foundation_state=match_row['foundation_state'],
            funder_snapshot=snapshot_dict,
            comparable_grant=snapshot_dict.get('comparable_grant'),
            potential_connections=[{
                'connection_type': c.connection_type,
                'description': c.description,
                'strength': c.strength
            } for c in connections],
            amount_min=snapshot.typical_grant_min,
            amount_max=snapshot.typical_grant_max,
            effort=calculate_effort(snapshot_dict),
            fit_score=calculate_fit_score(
                match_row['match_score'],
                match_row['same_state'],
                snapshot_dict,
                client.budget_numeric
            )
        )
        opportunities.append(opp)

    # Build report metadata
    today = date.today()
    if week_number is None:
        # Calculate week number (weeks since start of year, or could be report sequence)
        week_number = today.isocalendar()[1]

    report_meta = {
        'week_number': week_number,
        'report_date': today.isoformat(),
        'date_range_start': today.isoformat(),
        'date_range_end': (today.replace(day=today.day + 7)).isoformat() if today.day <= 24 else today.isoformat(),
        'generated_at': datetime.now().isoformat()
    }

    # Build client dict
    client_dict = {
        'organization_name': client.organization_name,
        'ein': client.ein,
        'email': client.email,
        'state': client.state,
        'city': client.city,
        'org_type': client.org_type,
        'budget': client.budget,
        'budget_numeric': client.budget_numeric,
        'grant_size_target': client.grant_size_target,
        'program_areas': client.program_areas,
        'populations_served': client.populations_served,
        'geographic_scope': client.geographic_scope,
        'ntee_code': client.ntee_code,
        'mission_statement': client.mission_statement
    }

    # Build timeline (8 weeks placeholder)
    timeline = []
    for i in range(8):
        timeline.append({
            'week': i + 1,
            'date': today.replace(day=min(28, today.day + i * 7)).isoformat(),
            'tasks': []
        })

    # Executive summary (placeholder - populated by AI)
    executive_summary = {
        'key_strengths': [],
        'one_thing': '',
        'urgent_actions': [],
        'funding_scenarios': {
            'conservative': 0,
            'moderate': 0,
            'ambitious': 0
        }
    }

    return ReportData(
        client=client_dict,
        report_meta=report_meta,
        opportunities=opportunities,
        executive_summary=executive_summary,
        timeline=timeline
    )
