"""
Markdown renderer for grant reports.

Assembles all report data into formatted markdown.
"""
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import re

TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_template(name: str) -> str:
    """Load a template file."""
    path = TEMPLATES_DIR / f"{name}.md"
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def escape_markdown(text: str) -> str:
    """Escape special markdown characters in table cells."""
    if not text:
        return ""
    text = str(text)
    text = text.replace('|', '\\|')
    return text


def format_currency(amount: float, abbreviate: bool = False) -> str:
    """Format amount as currency."""
    if not amount or amount == 0:
        return "—"
    if abbreviate and amount >= 1000000:
        return f"${amount / 1000000:.1f}M"
    elif abbreviate and amount >= 1000:
        return f"${amount / 1000:.0f}K"
    else:
        return f"${amount:,.0f}"


class ReportRenderer:
    """Render report data to markdown."""

    def __init__(self):
        """Load templates from files."""
        self.report_template = load_template('report_template')
        self.opportunity_template = load_template('opportunity_template')

    def render(self, report_data: Dict[str, Any]) -> str:
        """
        Render complete report to markdown.

        Args:
            report_data: Complete report data dict

        Returns:
            Formatted markdown string
        """
        client = report_data.get('client', {})
        meta = report_data.get('report_meta', {})
        opportunities = report_data.get('opportunities', [])
        exec_summary = report_data.get('executive_summary', {})
        timeline = report_data.get('timeline', [])

        # Render opportunity sections
        opp_sections = []
        for opp in opportunities:
            opp_md = self._render_opportunity(opp)
            opp_sections.append(opp_md)

        # Calculate funding scenarios
        scenarios = self._calculate_funding_scenarios(opportunities)

        # Format key strengths
        key_strengths = exec_summary.get('key_strengths', [])
        key_strengths_md = '\n'.join([f"- {s}" for s in key_strengths])

        # Format date range
        start_date = meta.get('date_range_start', date.today().isoformat())
        end_date = meta.get('date_range_end', (date.today() + timedelta(days=7)).isoformat())
        date_range = f"{self._format_date(start_date)} - {self._format_date(end_date)}"

        # Count total action items
        action_count = sum(len(opp.get('next_steps', [])) for opp in opportunities)

        # Fill in the template
        md = self.report_template.format(
            client_name=client.get('organization_name', 'Client'),
            week_number=meta.get('week_number', 1),
            date_range=date_range,
            one_thing=exec_summary.get('one_thing', 'Review this week\'s opportunities and prioritize.'),
            funding_range=f"{format_currency(scenarios['min'])} - {format_currency(scenarios['max'])}",
            action_item_count=action_count,
            key_strengths=key_strengths_md,
            urgent_actions_rows=self._format_urgent_actions_table(opportunities),
            conservative_amount=format_currency(scenarios['conservative']),
            moderate_amount=format_currency(scenarios['moderate']),
            ambitious_amount=format_currency(scenarios['ambitious']),
            top5_rows=self._format_top_5_table(opportunities),
            opportunity_sections='\n\n'.join(opp_sections),
            timeline_rows=self._format_timeline_table(timeline),
            contacts_rows=self._format_contacts_table(opportunities),
            portals_rows=self._format_portals_table(opportunities),
            generated_date=datetime.now().strftime('%B %d, %Y'),
            next_report_date=self._calculate_next_report_date(meta.get('report_date'))
        )

        return md

    def render_to_file(self, report_data: Dict[str, Any], output_path: str) -> str:
        """Render and save to file."""
        md = self.render(report_data)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)

        return output_path

    def _render_opportunity(self, opp: Dict[str, Any]) -> str:
        """Render a single opportunity section."""
        snapshot = opp.get('funder_snapshot', {})

        # Get or generate narratives
        why_fits = opp.get('why_this_fits', 'See funder snapshot for alignment details.')
        positioning = opp.get('positioning_strategy', 'Review funder snapshot to develop positioning.')
        next_steps = opp.get('next_steps', [])

        # Format connections section
        connections = opp.get('potential_connections', [])
        if connections:
            conn_rows = []
            for c in connections:
                conn_rows.append(f"| {escape_markdown(c.get('connection_type', 'Connection'))} | {escape_markdown(c.get('description', ''))} | {c.get('strength', 'Medium')} |")
            connections_section = "| Type | Description | Strength |\n|------|-------------|----------|\n" + '\n'.join(conn_rows)
        else:
            connections_section = "*No direct connections identified. Consider building relationships through events or shared networks.*"

        # Format requirements section
        requirements = opp.get('application_requirements', [])
        if requirements:
            requirements_section = '\n'.join([f"- {escape_markdown(r)}" for r in requirements])
        else:
            requirements_section = "*Requirements not specified. Check foundation website for application details.*"

        # Format next steps table
        next_steps_rows = []
        for step in next_steps:
            next_steps_rows.append(
                f"| {escape_markdown(step.get('action', ''))} | {step.get('deadline', '—')} | {step.get('owner', '—')} |"
            )
        next_steps_md = '\n'.join(next_steps_rows) if next_steps_rows else "| Review opportunity details | This week | Grants Manager |"

        # Status badge
        status = opp.get('status', 'MEDIUM')
        status_badges = {
            'HIGH': '**[HIGH PRIORITY]**',
            'MEDIUM': '[MEDIUM]',
            'LOW': '[LOW]'
        }
        status_badge = status_badges.get(status, '[REVIEW]')

        return self.opportunity_template.format(
            rank=opp.get('rank', 1),
            foundation_name=opp.get('foundation_name', 'Foundation'),
            status_badge=status_badge,
            deadline=opp.get('deadline', 'Not specified'),
            fit_score=opp.get('fit_score', 5),
            effort=opp.get('effort', 'Medium'),
            why_this_fits=why_fits,
            foundation_ein=opp.get('foundation_ein', '—'),
            foundation_state=opp.get('foundation_state', '—'),
            amount_range=self._format_amount_range(opp),
            same_state='Yes' if opp.get('same_state') else 'No',
            match_score=f"{opp.get('match_score', 0):.0f}",
            annual_giving=self._format_annual_giving(snapshot),
            typical_grant=self._format_typical_grant(snapshot),
            geographic_focus=self._format_geographic(snapshot),
            repeat_funding=self._format_repeat_rate(snapshot),
            giving_style=self._format_giving_style(snapshot),
            recipient_profile=self._format_recipient_profile(snapshot),
            funding_trend=self._format_funding_trend(snapshot),
            comparable_grant=self._format_comparable_grant(opp),
            connections_section=connections_section,
            requirements_section=requirements_section,
            positioning_strategy=positioning,
            next_steps_rows=next_steps_md
        )

    # Formatting helpers
    def _format_amount_range(self, opp: Dict) -> str:
        """Format amount range from min/max."""
        min_amt = opp.get('amount_min', 0)
        max_amt = opp.get('amount_max', 0)
        if min_amt and max_amt:
            return f"{format_currency(min_amt)} - {format_currency(max_amt)}"
        elif max_amt:
            return f"Up to {format_currency(max_amt)}"
        elif min_amt:
            return f"From {format_currency(min_amt)}"
        return "—"

    def _format_contact(self, opp: Dict) -> str:
        """Format contact info string."""
        parts = []
        if opp.get('contact_name'):
            parts.append(opp['contact_name'])
        if opp.get('contact_email'):
            parts.append(opp['contact_email'])
        if opp.get('contact_phone'):
            parts.append(opp['contact_phone'])
        return ', '.join(parts) if parts else '—'

    def _format_annual_giving(self, snapshot: Dict) -> str:
        """Format annual giving from snapshot."""
        annual = snapshot.get('annual_giving', {})
        total = annual.get('total', 0)
        count = annual.get('count', 0)
        if total and count:
            return f"{format_currency(total, abbreviate=True)} across {count} grants"
        return "—"

    def _format_typical_grant(self, snapshot: Dict) -> str:
        """Format typical grant from snapshot."""
        typical = snapshot.get('typical_grant', {})
        median = typical.get('median', 0)
        min_amt = typical.get('min', 0)
        max_amt = typical.get('max', 0)
        if median:
            return f"{format_currency(median)} median (range: {format_currency(min_amt)} - {format_currency(max_amt)})"
        return "—"

    def _format_geographic(self, snapshot: Dict) -> str:
        """Format geographic focus from snapshot."""
        geo = snapshot.get('geographic_focus', {})
        top_state = geo.get('top_state', '')
        top_pct = geo.get('top_state_pct', 0)
        in_state_pct = geo.get('in_state_pct', 0)
        if top_state and top_pct:
            return f"{top_state} ({top_pct:.0%}), {in_state_pct:.0%} in-state overall"
        return "—"

    def _format_repeat_rate(self, snapshot: Dict) -> str:
        """Format repeat funding rate."""
        repeat = snapshot.get('repeat_funding', {})
        rate = repeat.get('rate', 0)
        if rate:
            return f"{rate:.0%} of recipients funded 2+ times"
        return "—"

    def _format_giving_style(self, snapshot: Dict) -> str:
        """Format giving style from snapshot."""
        style = snapshot.get('giving_style', {})
        general = style.get('general_support_pct', 0)
        if general:
            program = 1 - general
            return f"{general:.0%} general support / {program:.0%} program-specific"
        return "—"

    def _format_recipient_profile(self, snapshot: Dict) -> str:
        """Format recipient profile from snapshot."""
        profile = snapshot.get('recipient_profile', {})
        budget_min = profile.get('budget_min', 0)
        budget_max = profile.get('budget_max', 0)
        sector = profile.get('primary_sector', '')
        parts = []
        if budget_min and budget_max:
            parts.append(f"{format_currency(budget_min, True)}-{format_currency(budget_max, True)} budget")
        if sector:
            parts.append(f"{sector} focus")
        return ', '.join(parts) if parts else "—"

    def _format_funding_trend(self, snapshot: Dict) -> str:
        """Format funding trend from snapshot."""
        trend = snapshot.get('funding_trend', {})
        direction = trend.get('direction', '')
        change = trend.get('change_pct', 0)
        if direction:
            if change:
                return f"{direction} ({change:+.0%} over 3 years)"
            return direction
        return "—"

    def _format_comparable_grant(self, opp: Dict) -> str:
        """Format comparable grant info."""
        comparable = opp.get('comparable_grant')
        if not comparable:
            return "No comparable grant identified"
        name = comparable.get('recipient_name', 'Organization')
        amount = comparable.get('amount', 0)
        purpose = comparable.get('purpose_text', '')[:80]
        year = comparable.get('tax_year', '')
        return f"{escape_markdown(name)} received {format_currency(amount)} for {escape_markdown(purpose)} ({year})"

    def _format_date(self, date_str: str) -> str:
        """Format date string for display."""
        try:
            if isinstance(date_str, str):
                d = date.fromisoformat(date_str)
            else:
                d = date_str
            return d.strftime('%B %d, %Y')
        except:
            return date_str

    # Table formatters
    def _format_top_5_table(self, opportunities: List[Dict]) -> str:
        """Generate markdown table rows for Top 5."""
        rows = []
        for opp in opportunities:
            rows.append(
                f"| {opp.get('rank', '')} | {escape_markdown(opp.get('foundation_name', ''))} | "
                f"{self._format_amount_range(opp)} | {opp.get('deadline', '—')} | "
                f"{opp.get('fit_score', '')}/10 | {opp.get('effort', '')} | {opp.get('status', 'REVIEW')} |"
            )
        return '\n'.join(rows)

    def _format_urgent_actions_table(self, opportunities: List[Dict]) -> str:
        """Generate urgent actions table rows."""
        rows = []
        priority = 1
        for opp in opportunities[:3]:  # Top 3 most urgent
            next_steps = opp.get('next_steps', [])
            if next_steps:
                step = next_steps[0]
                rows.append(
                    f"| {priority} | {escape_markdown(step.get('action', 'Review opportunity'))} | "
                    f"{step.get('deadline', 'This week')} | {escape_markdown(opp.get('foundation_name', ''))} |"
                )
                priority += 1
        return '\n'.join(rows) if rows else "| 1 | Review this week's opportunities | This week | All |"

    def _format_timeline_table(self, timeline: List[Dict]) -> str:
        """Generate 8-week timeline rows."""
        rows = []
        for week in timeline:
            week_num = week.get('week', '')
            week_date = self._format_date(week.get('date', ''))
            tasks = week.get('tasks', [])
            tasks_str = '; '.join(tasks) if tasks else 'TBD'
            rows.append(f"| Week {week_num} | {week_date} | {escape_markdown(tasks_str)} |")
        return '\n'.join(rows) if rows else "| Week 1 | TBD | Review opportunities |"

    def _format_contacts_table(self, opportunities: List[Dict]) -> str:
        """Generate quick reference contacts table."""
        rows = []
        for opp in opportunities:
            name = opp.get('contact_name', '—')
            email = opp.get('contact_email', '—')
            phone = opp.get('contact_phone', '—')
            rows.append(
                f"| {escape_markdown(opp.get('foundation_name', ''))} | "
                f"{escape_markdown(name)} | {escape_markdown(email)} | {escape_markdown(phone)} |"
            )
        return '\n'.join(rows)

    def _format_portals_table(self, opportunities: List[Dict]) -> str:
        """Generate quick reference portals table."""
        rows = []
        for opp in opportunities:
            portal = opp.get('portal_url', '—')
            if portal and portal != '—':
                portal = f"[Link]({portal})"
            rows.append(
                f"| {escape_markdown(opp.get('foundation_name', ''))} | {portal} |"
            )
        return '\n'.join(rows)

    # Calculation helpers
    def _calculate_funding_scenarios(self, opportunities: List[Dict]) -> Dict:
        """Calculate conservative/moderate/ambitious funding ranges."""
        amounts = []
        for opp in opportunities:
            min_amt = opp.get('amount_min', 0)
            max_amt = opp.get('amount_max', 0)
            if min_amt:
                amounts.append(min_amt)
            if max_amt:
                amounts.append(max_amt)

        if not amounts:
            return {
                'min': 25000,
                'max': 250000,
                'conservative': 25000,
                'moderate': 75000,
                'ambitious': 150000
            }

        amounts.sort()
        min_amt = amounts[0] if amounts else 25000
        max_amt = amounts[-1] if amounts else 100000

        return {
            'min': min_amt,
            'max': max_amt,
            'conservative': min_amt,
            'moderate': sum(amounts[:3]) / min(3, len(amounts)) if amounts else 50000,
            'ambitious': sum(amounts) / len(amounts) * 2 if amounts else 150000
        }

    def _calculate_next_report_date(self, current_date: str) -> str:
        """Calculate next report date (7 days out)."""
        try:
            if isinstance(current_date, str):
                d = date.fromisoformat(current_date)
            else:
                d = current_date or date.today()
            next_date = d + timedelta(days=7)
            return next_date.strftime('%B %d, %Y')
        except:
            return "Next week"
