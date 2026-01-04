#!/usr/bin/env python3
"""
Script 06: Generate Narratives

Calls Claude API to generate personalized narratives for each opportunity:
- "Why This Fits" explanation
- "Positioning Strategy" advice
- "Next Steps" action items
Also generates executive summary content.

Usage:
    python scripts/06_generate_narratives.py --client "PSMF"
    python scripts/06_generate_narratives.py --client "PSMF" --dry-run
    python scripts/06_generate_narratives.py --client "PSMF" --model claude-3-5-sonnet-20241022
"""

import argparse
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.paths import (
    TEMPLATES_DIR,
    get_run_dir,
    load_client_registry,
    setup_logging,
)

# Try to import anthropic
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(data: dict, path: Path):
    """Save data to JSON file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def validate_opportunities_data(opportunities: list, client: dict) -> list:
    """
    Check data quality before generating narratives.
    Returns list of warnings.
    """
    warnings = []

    # Parse client's target grant size
    target_str = client.get("grant_size_target", "")
    target_min = 0
    if "$25,000" in target_str or "25,000" in target_str:
        target_min = 25000
    elif "$10,000" in target_str or "10,000" in target_str:
        target_min = 10000
    elif "$50,000" in target_str or "50,000" in target_str:
        target_min = 50000
    elif "$100,000" in target_str or "100,000" in target_str:
        target_min = 100000

    for opp in opportunities:
        name = opp.get("foundation_name", "Unknown")[:40]
        snapshot = opp.get("funder_snapshot", {})

        # Check for comparable grant
        if not opp.get("comparable_grant"):
            warnings.append(f"{name}: No comparable grant - narrative will be generic")

        # Check median grant vs client target
        median = snapshot.get("typical_grant", {}).get("median", 0)
        if target_min and median < target_min * 0.25:
            warnings.append(f"{name}: Median grant ${median:,.0f} far below target ${target_min:,.0f}")

        # Check for connections
        if not opp.get("connections"):
            warnings.append(f"{name}: No relationship connections found")

        # Check for annual giving data
        annual_total = snapshot.get("annual_giving", {}).get("total", 0)
        if annual_total == 0:
            warnings.append(f"{name}: No annual giving data")

    return warnings


def load_prompt_template(name: str) -> str:
    """Load prompt template from templates/prompts/"""
    template_path = TEMPLATES_DIR / "prompts" / f"{name}.txt"
    if template_path.exists():
        return template_path.read_text()
    else:
        print(f"WARNING: Template not found: {template_path}")
        return ""


def build_opportunity_context(opp: dict, client: dict) -> dict:
    """Build template variables for an opportunity."""
    snapshot = opp.get("funder_snapshot", {})
    annual = snapshot.get("annual_giving", {})
    typical = snapshot.get("typical_grant", {})
    geographic = snapshot.get("geographic_focus", {})
    giving_style = snapshot.get("giving_style", {})
    trend = snapshot.get("funding_trend", {})
    recipient_profile = snapshot.get("recipient_profile", {})
    repeat_funding = snapshot.get("repeat_funding", {})
    comparable = opp.get("comparable_grant") or {}

    # Format comparable grant text
    if comparable and comparable.get("amount", 0) > 0:
        comparable_text = (
            f"{comparable.get('recipient', 'Similar organization')} received "
            f"${comparable.get('amount', 0):,.0f} in {comparable.get('year', 'recent year')} "
            f"for: {comparable.get('purpose', 'general support')}"
        )
    else:
        comparable_text = "No directly comparable grant found, but foundation funds similar organizations."

    # Format connections text
    connections_text = ""
    for conn in opp.get("connections", []):
        connections_text += f"- {conn.get('description', '')}\n"
    if not connections_text:
        connections_text = "No direct connections identified yet."

    return {
        # Client info
        "client_name": client.get("organization_name", ""),
        "client_mission": client.get("mission_statement", ""),
        "client_programs": ", ".join(client.get("program_areas", [])),
        "client_populations": ", ".join(client.get("populations_served", [])),
        "client_city": client.get("city", ""),
        "client_state": client.get("state", ""),
        "client_budget": client.get("budget", ""),
        "client_budget_numeric": client.get("budget_numeric", 0),
        "client_strengths": ", ".join(client.get("program_areas", [])[:3]),

        # Foundation info
        "foundation_name": opp.get("foundation_name", ""),
        "foundation_state": opp.get("foundation_state", ""),
        "foundation_ein": opp.get("foundation_ein", ""),

        # Giving data
        "annual_giving": annual.get("total", 0),
        "grant_count": annual.get("count", 0),
        "median_grant": typical.get("median", 0),
        "min_grant": typical.get("min", 0),
        "max_grant": typical.get("max", 0),

        # Geographic
        "top_state": geographic.get("top_state", ""),
        "top_state_pct": geographic.get("top_state_pct", 0),
        "in_state_pct": geographic.get("in_state_pct", 0),
        "same_state": "Yes" if opp.get("same_state") else "No",

        # Style
        "general_support_pct": giving_style.get("general_pct", 0),
        "program_specific_pct": giving_style.get("program_pct", 0),

        # Repeat funding
        "repeat_rate": repeat_funding.get("rate", 0),

        # Recipient profile
        "budget_min": recipient_profile.get("budget_min", 0),
        "budget_max": recipient_profile.get("budget_max", 0),
        "primary_sector": recipient_profile.get("primary_sector", ""),

        # Trend
        "funding_trend": trend.get("direction", "Stable"),
        "trend_change_pct": trend.get("change_pct", 0),

        # Comparable
        "comparable_grant_text": comparable_text,

        # Connections
        "connections_text": connections_text,

        # Amount range
        "amount_min": opp.get("amount_min", 0),
        "amount_max": opp.get("amount_max", 0),

        # Status
        "fit_score": opp.get("fit_score", 5),
        "effort": opp.get("effort", "Medium"),
        "deadline": opp.get("deadline", "Rolling"),

        # Contact (from enrichment if available)
        "contact_name": opp.get("contact_name", ""),
        "contact_email": opp.get("contact_email", ""),
        "contact_phone": opp.get("contact_phone", ""),
        "portal_url": opp.get("portal_url", ""),
        "prior_relationship": "None identified",
        "requirements_list": "Standard LOI and proposal required.",

        # Viability data (from 05c filter)
        "viability_tier": opp.get("viability", {}).get("tier", "unknown"),
        "viability_reason": opp.get("viability", {}).get("tier_reason", ""),
        "viability_multiplier": opp.get("viability", {}).get("multiplier", 1.0),
        "adjusted_score": opp.get("viability", {}).get("adjusted_score", opp.get("fit_score", 5)),
        "unsolicited_status": opp.get("viability", {}).get("unsolicited_status", "unknown"),
        "red_flags": opp.get("viability", {}).get("red_flags", []),
        "foundation_priorities": opp.get("foundation_priorities", []),

        # Today's date
        "today": date.today().isoformat()
    }


def call_claude(anthropic_client, prompt: str, model: str, max_tokens: int = 1000) -> str:
    """Call Claude API and return response text."""
    try:
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"API error: {e}")
        return ""


# ============================================================================
# Fallback templates (for dry-run mode)
# ============================================================================

def fallback_why_this_fits(ctx: dict) -> str:
    """Template-based fallback for Why This Fits."""
    parts = []

    # Mission alignment
    parts.append(
        f"{ctx['foundation_name']} has a track record of supporting organizations "
        f"like {ctx['client_name']}."
    )

    # Geographic
    if ctx.get("same_state") == "Yes":
        parts.append(
            f"As a {ctx['foundation_state']}-based foundation with {ctx['in_state_pct']:.0%} "
            f"in-state giving, they prioritize local organizations."
        )
    elif ctx.get("top_state") == ctx.get("client_state"):
        parts.append(
            f"Their top funding state is {ctx['top_state']} ({ctx['top_state_pct']:.0%} of grants), "
            f"matching your location."
        )

    # Comparable grant
    if "received $" in ctx.get("comparable_grant_text", ""):
        parts.append(f"Notably, {ctx['comparable_grant_text']}")

    # Trend
    if ctx.get("funding_trend") == "Growing":
        parts.append("Their giving has been increasing, suggesting capacity for new grantees.")

    # Add viability context if available
    viability_tier = ctx.get("viability_tier", "unknown")
    if viability_tier == "watch":
        parts.append("**Note:** This foundation does not accept unsolicited proposals. Monitor for RFPs or seek a warm introduction.")
    elif viability_tier == "conditional":
        unsolicited = ctx.get("unsolicited_status", "")
        if unsolicited == "conditional":
            parts.append("**Note:** This foundation uses an RFP-based process. Check their website for open opportunities.")
        else:
            parts.append("**Note:** Verify application process before outreach.")

    return " ".join(parts)


def fallback_positioning(ctx: dict) -> str:
    """Template-based fallback for positioning strategy."""
    parts = []

    # Add viability-aware intro for WATCH tier
    viability_tier = ctx.get("viability_tier", "unknown")
    if viability_tier == "watch":
        parts.append(
            "**Approach with caution:** This foundation does not accept unsolicited proposals. "
            "Focus on relationship-building through networking or board connections before formal outreach."
        )
        return " ".join(parts)  # Return early for watch tier

    # General vs program
    general_pct = ctx.get("general_support_pct", 0)
    if general_pct > 0.5:
        parts.append(
            f"Lead with an unrestricted operating support request—{general_pct:.0%} of their grants "
            f"are general support."
        )
    else:
        parts.append(
            f"Frame your request around a specific program or initiative, as this foundation favors "
            f"program-specific grants ({ctx.get('program_specific_pct', 0):.0%})."
        )

    # Amount recommendation
    median = ctx.get("median_grant", 0)
    if median > 0:
        suggested_min = int(median * 0.8)
        suggested_max = int(median * 1.5)
        parts.append(f"Consider requesting ${suggested_min:,} - ${suggested_max:,} based on their ${median:,.0f} median grant.")

    # Geographic angle
    if ctx.get("same_state") == "Yes":
        parts.append(f"Emphasize your local {ctx['client_state']} presence and community impact.")

    # Repeat funding
    repeat_rate = ctx.get("repeat_rate", 0)
    if repeat_rate > 0.5:
        parts.append(f"With a {repeat_rate:.0%} repeat funding rate, plan for multi-year relationship building.")

    # Add portal URL if available
    portal_url = ctx.get("portal_url", "")
    if portal_url and portal_url not in ["null", "None", ""]:
        parts.append(f"Apply via: {portal_url}")

    return " ".join(parts)


def fallback_next_steps(ctx: dict) -> list:
    """Template-based fallback for next steps."""
    today = date.today()
    viability_tier = ctx.get("viability_tier", "unknown")
    foundation_deadline = ctx.get("deadline", "Rolling")

    # Different steps based on viability tier
    if viability_tier == "watch":
        # For WATCH tier: focus on relationship building, not direct application
        steps = [
            {
                "action": "Identify board or staff connections who could provide introduction",
                "deadline": (today + timedelta(days=14)).isoformat(),
                "owner": "Executive Director"
            },
            {
                "action": f"Add {ctx['foundation_name']} to monitoring list for future RFPs",
                "deadline": (today + timedelta(days=7)).isoformat(),
                "owner": "Development Director"
            },
            {
                "action": "Research foundation's invitation process and past grantee profiles",
                "deadline": (today + timedelta(days=21)).isoformat(),
                "owner": "Grant Writer"
            }
        ]
        return steps

    # Standard steps for READY and CONDITIONAL tiers
    steps = [
        {
            "action": f"Research {ctx['foundation_name']}'s recent grants and stated priorities",
            "deadline": (today + timedelta(days=7)).isoformat(),
            "owner": "Development Director"
        },
        {
            "action": "Draft Letter of Inquiry highlighting alignment with foundation priorities",
            "deadline": (today + timedelta(days=14)).isoformat(),
            "owner": "Grant Writer"
        },
        {
            "action": "Identify potential board or staff connections for warm introduction",
            "deadline": (today + timedelta(days=10)).isoformat(),
            "owner": "Executive Director"
        }
    ]

    # Add specific deadline step if we have one
    if foundation_deadline and foundation_deadline != "Rolling" and "20" in str(foundation_deadline):
        steps.insert(0, {
            "action": f"Submit application by foundation deadline: {foundation_deadline}",
            "deadline": foundation_deadline,
            "owner": "Grant Writer"
        })

    # Add contact step if contact info available
    if ctx.get("contact_email"):
        steps.insert(0, {
            "action": f"Email {ctx['contact_name'] or 'program officer'} to introduce organization",
            "deadline": (today + timedelta(days=5)).isoformat(),
            "owner": "Development Director"
        })
    elif ctx.get("contact_phone"):
        steps.insert(0, {
            "action": f"Call {ctx['foundation_name']} at {ctx['contact_phone']} to inquire about application process",
            "deadline": (today + timedelta(days=5)).isoformat(),
            "owner": "Development Director"
        })

    # Add portal step if available
    portal_url = ctx.get("portal_url", "")
    if portal_url and portal_url not in ["null", "None", ""]:
        steps.append({
            "action": f"Create account on application portal: {portal_url}",
            "deadline": (today + timedelta(days=7)).isoformat(),
            "owner": "Development Director"
        })

    return steps


def fallback_key_strengths(ctx: dict, opps: list) -> list:
    """Template-based key strengths."""
    strengths = []

    # Count viability tiers
    ready_count = sum(1 for o in opps if o.get("viability", {}).get("tier") == "ready")
    conditional_count = sum(1 for o in opps if o.get("viability", {}).get("tier") == "conditional")
    watch_count = sum(1 for o in opps if o.get("viability", {}).get("tier") == "watch")

    same_state_count = sum(1 for o in opps if o.get("same_state"))
    high_priority_count = sum(1 for o in opps if o.get("status") == "HIGH")
    total_min = sum(o.get("amount_min", 0) for o in opps)
    total_max = sum(o.get("amount_max", 0) for o in opps)

    # Viability-based strength (most important)
    if ready_count > 0:
        strengths.append(
            f"**Ready to Apply:** {ready_count} foundation(s) actively accepting applications "
            f"with clear processes."
        )
    elif conditional_count > 0:
        strengths.append(
            f"**Actionable Opportunities:** {conditional_count} foundation(s) may accept applications "
            f"pending verification."
        )

    if same_state_count > 0:
        strengths.append(
            f"**Geographic Advantage:** {same_state_count} of {len(opps)} opportunities "
            f"are in-state funders who prioritize local organizations."
        )

    if high_priority_count > 0:
        strengths.append(
            f"**Strong Matches:** {high_priority_count} opportunities rated HIGH priority "
            f"based on alignment analysis."
        )

    # Funding potential (for READY + CONDITIONAL only)
    actionable_opps = [o for o in opps if o.get("viability", {}).get("tier") in ["ready", "conditional", "unknown"]]
    if actionable_opps:
        actionable_min = sum(o.get("amount_min", 0) for o in actionable_opps)
        actionable_max = sum(o.get("amount_max", 0) for o in actionable_opps)
        strengths.append(
            f"**Funding Potential:** ${actionable_min:,.0f} - ${actionable_max:,.0f} from actionable opportunities."
        )
    else:
        strengths.append(
            f"**Funding Potential:** ${total_min:,.0f} - ${total_max:,.0f} potential "
            f"across all opportunities."
        )

    return strengths[:3]


def fallback_one_thing(ctx: dict, opps: list) -> str:
    """Template-based one thing."""
    if not opps:
        return "**This week's priority:** Review the opportunities in this report and identify your top target."

    # Find the best READY tier opportunity first
    ready_opps = [o for o in opps if o.get("viability", {}).get("tier") == "ready"]
    if ready_opps:
        top = ready_opps[0]
        deadline = top.get("deadline", "Rolling")
        if deadline and deadline != "Rolling" and "20" in str(deadline):
            return f"**This week's priority:** Apply to {top['foundation_name']} before {deadline} deadline."
        portal = top.get("portal_url", "")
        if portal:
            return f"**This week's priority:** Start application for {top['foundation_name']} via their online portal."
        return f"**This week's priority:** Contact {top['foundation_name']} to begin application process."

    # Fall back to CONDITIONAL tier
    conditional_opps = [o for o in opps if o.get("viability", {}).get("tier") == "conditional"]
    if conditional_opps:
        top = conditional_opps[0]
        return f"**This week's priority:** Verify application process for {top['foundation_name']} before proceeding."

    # All WATCH tier - focus on relationship building
    top = opps[0]
    return f"**This week's priority:** Identify connections to {top['foundation_name']} for potential introduction."


def parse_next_steps_text(response: str, ctx: dict) -> list:
    """Try to parse next steps from text response if JSON parsing fails."""
    # Return fallback if response is empty or unparseable
    return fallback_next_steps(ctx)


def parse_bullets(response: str) -> list:
    """Parse bullet points from response."""
    lines = response.strip().split("\n")
    bullets = []
    for line in lines:
        line = line.strip()
        if line and (line.startswith("-") or line.startswith("*") or line[0].isdigit()):
            # Remove leading bullet/number
            if line.startswith("-") or line.startswith("*"):
                line = line[1:].strip()
            elif line[0].isdigit():
                # Remove "1. " or "1) "
                if ". " in line[:4]:
                    line = line.split(". ", 1)[1]
                elif ") " in line[:4]:
                    line = line.split(") ", 1)[1]
            if line:
                bullets.append(line)
    return bullets if bullets else [response]


# ============================================================================
# Narrative generation functions
# ============================================================================

def generate_why_this_fits(
    anthropic_client, context: dict, template: str, model: str, dry_run: bool
) -> str:
    """Generate 'Why This Fits' narrative."""
    if dry_run:
        return fallback_why_this_fits(context)

    try:
        prompt = template.format(**context)
        return call_claude(anthropic_client, prompt, model, max_tokens=500)
    except KeyError as e:
        print(f"  Template formatting error (why_this_fits): {e}")
        return fallback_why_this_fits(context)


def generate_positioning_strategy(
    anthropic_client, context: dict, template: str, model: str, dry_run: bool
) -> str:
    """Generate positioning strategy."""
    if dry_run:
        return fallback_positioning(context)

    try:
        prompt = template.format(**context)
        return call_claude(anthropic_client, prompt, model, max_tokens=500)
    except KeyError as e:
        print(f"  Template formatting error (positioning_strategy): {e}")
        return fallback_positioning(context)


def generate_next_steps(
    anthropic_client, context: dict, template: str, model: str, dry_run: bool
) -> list:
    """Generate next steps as list of {action, deadline, owner}."""
    if dry_run:
        return fallback_next_steps(context)

    try:
        prompt = template.format(**context)
        response = call_claude(anthropic_client, prompt, model, max_tokens=500)

        # Parse JSON response
        try:
            steps = json.loads(response)
            if isinstance(steps, list):
                return steps
        except json.JSONDecodeError:
            pass

        # Try to extract from markdown code block
        if "```json" in response:
            json_part = response.split("```json")[1].split("```")[0]
            try:
                steps = json.loads(json_part)
                if isinstance(steps, list):
                    return steps
            except json.JSONDecodeError:
                pass

        return parse_next_steps_text(response, context)

    except KeyError as e:
        print(f"  Template formatting error (next_steps): {e}")
        return fallback_next_steps(context)


def calculate_funding_scenarios(opportunities: list) -> dict:
    """Calculate conservative/moderate/ambitious funding scenarios."""
    if not opportunities:
        return {"conservative": 0, "moderate": 0, "ambitious": 0}

    # Conservative: Sum of amount_min for top 2
    conservative = sum(o.get("amount_min", 0) for o in opportunities[:2])

    # Moderate: Sum of midpoint for top 3
    moderate = sum(
        (o.get("amount_min", 0) + o.get("amount_max", 0)) / 2
        for o in opportunities[:3]
    )

    # Ambitious: Sum of amount_max for all
    ambitious = sum(o.get("amount_max", 0) for o in opportunities)

    return {
        "conservative": int(conservative),
        "moderate": int(moderate),
        "ambitious": int(ambitious)
    }


def generate_executive_summary(
    anthropic_client, client: dict, opportunities: list, templates: dict, model: str, dry_run: bool
) -> dict:
    """Generate executive summary narratives."""

    # Build opportunities summary for key_strengths template
    opp_lines = []
    for i, o in enumerate(opportunities):
        snap = o.get("funder_snapshot", {})
        annual = snap.get("annual_giving", {})
        opp_lines.append(
            f"{i+1}. {o['foundation_name']} - ${annual.get('total', 0):,.0f} annual giving, "
            f"status={o.get('status', 'MEDIUM')}, {o.get('foundation_state', 'N/A')}"
        )
    opportunities_summary = "\n".join(opp_lines)

    # Build opportunities with deadlines for one_thing template
    opp_deadlines = []
    for o in opportunities:
        opp_deadlines.append(f"- {o['foundation_name']}: Deadline={o.get('deadline', 'Rolling')}, Status={o.get('status', 'MEDIUM')}")
    opportunities_with_deadlines = "\n".join(opp_deadlines)

    context = {
        "client_name": client.get("organization_name", ""),
        "client_city": client.get("city", ""),
        "client_state": client.get("state", ""),
        "client_programs": ", ".join(client.get("program_areas", [])),
        "client_budget": client.get("budget", ""),
        "num_opportunities": len(opportunities),
        "top_foundation": opportunities[0]["foundation_name"] if opportunities else "",
        "high_priority_count": sum(1 for o in opportunities if o.get("status") == "HIGH"),
        "total_potential_min": sum(o.get("amount_min", 0) for o in opportunities),
        "total_potential_max": sum(o.get("amount_max", 0) for o in opportunities),
        "same_state_count": sum(1 for o in opportunities if o.get("same_state")),
        "opportunities_summary": opportunities_summary,
        "opportunities_with_deadlines": opportunities_with_deadlines,
        "today": date.today().isoformat()
    }

    # Key strengths (3 bullets)
    if dry_run:
        key_strengths = fallback_key_strengths(context, opportunities)
    else:
        try:
            prompt = templates["key_strengths"].format(**context)
            response = call_claude(anthropic_client, prompt, model, max_tokens=400)
            key_strengths = parse_bullets(response)
        except (KeyError, Exception) as e:
            print(f"  Key strengths API error: {e}")
            key_strengths = fallback_key_strengths(context, opportunities)

    # One thing (single priority)
    if dry_run:
        one_thing = fallback_one_thing(context, opportunities)
    else:
        try:
            prompt = templates["one_thing"].format(**context)
            one_thing = call_claude(anthropic_client, prompt, model, max_tokens=150)
        except (KeyError, Exception) as e:
            print(f"  One thing API error: {e}")
            one_thing = fallback_one_thing(context, opportunities)

    # Funding scenarios (calculated, not AI)
    scenarios = calculate_funding_scenarios(opportunities)

    # Urgent actions from high-priority next steps
    urgent_actions = []

    return {
        "key_strengths": key_strengths,
        "one_thing": one_thing,
        "urgent_actions": urgent_actions,
        "funding_scenarios": scenarios
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate personalized narratives for grant opportunities"
    )
    parser.add_argument("--client", required=True, help="Client name or short_name")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Skip API calls, use template fallbacks"
    )
    parser.add_argument(
        "--model", default="claude-3-5-sonnet-20241022",
        help="Claude model to use"
    )
    parser.add_argument(
        "--date", default=date.today().isoformat(),
        help="Run date (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    # Find client
    registry = load_client_registry()
    client_entry = None
    for c in registry.get("clients", []):
        if (c["name"].lower() == args.client.lower() or
            c.get("short_name", "").lower() == args.client.lower()):
            client_entry = c
            break

    if not client_entry:
        print(f"ERROR: Client '{args.client}' not found in registry")
        sys.exit(1)

    client_name = client_entry["name"].replace(" ", "_")

    # Set up logging
    logger = setup_logging(client_name, "06_generate_narratives")
    logger.info(f"[06_generate_narratives] Starting for {client_entry['name']}")

    # Check API setup
    dry_run = args.dry_run
    anthropic_client = None

    if not dry_run:
        if not HAS_ANTHROPIC:
            print("WARNING: anthropic library not installed. Using --dry-run mode.")
            dry_run = True
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("WARNING: ANTHROPIC_API_KEY not set. Using --dry-run mode.")
                dry_run = True
            else:
                anthropic_client = Anthropic(api_key=api_key)

    mode = "dry-run (fallbacks)" if dry_run else f"API ({args.model})"
    logger.info(f"[06_generate_narratives] Mode: {mode}")
    print(f"\nGenerating narratives in {mode} mode...")

    # Find run directory
    run_dir = get_run_dir(client_name, args.date)
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)

    # Load inputs
    client_file = run_dir / "01_client.json"

    # Prefer filtered opportunities (05c) if available, fall back to 05
    filtered_file = run_dir / "05c_filtered.json"
    opportunities_file = run_dir / "05_opportunities.json"

    if filtered_file.exists():
        opportunities_file = filtered_file
        print(f"Using viability-filtered opportunities: {filtered_file.name}")
    else:
        print(f"Note: No 05c_filtered.json found, using 05_opportunities.json")
        print(f"  Run 05c_viability_filter.py first for better results.")

    for f in [client_file, opportunities_file]:
        if not f.exists():
            print(f"ERROR: Required file not found: {f}")
            sys.exit(1)

    client_profile = load_json(client_file)
    opportunities = load_json(opportunities_file)

    logger.info(f"Loaded {len(opportunities)} opportunities")
    print(f"Client: {client_profile.get('organization_name', 'Unknown')}")
    print(f"Opportunities: {len(opportunities)}")

    # Validate data quality before generating narratives
    print("\nValidating data quality...")
    data_warnings = validate_opportunities_data(opportunities, client_profile)

    if data_warnings:
        print("\n" + "="*60)
        print("DATA QUALITY WARNINGS")
        print("="*60)
        for w in data_warnings:
            print(f"  - {w}")
        print("="*60)
        print("\nProceeding with narrative generation, but output may be generic.")
        print("Consider re-running with different filters or more foundations.\n")

        for w in data_warnings:
            logger.warning(f"Data quality: {w}")
    else:
        print("Data quality: OK")

    # Load prompt templates
    templates = {
        "why_this_fits": load_prompt_template("why_this_fits"),
        "positioning_strategy": load_prompt_template("positioning_strategy"),
        "next_steps": load_prompt_template("next_steps"),
        "key_strengths": load_prompt_template("key_strengths"),
        "one_thing": load_prompt_template("one_thing")
    }

    # Generate narratives for each opportunity
    narratives = {"opportunities": [], "executive_summary": {}}
    api_calls = 0

    for i, opp in enumerate(opportunities):
        print(f"\n[{i+1}/{len(opportunities)}] {opp['foundation_name'][:50]}...")
        logger.info(f"Generating narratives for [{i+1}/{len(opportunities)}] {opp['foundation_name']}")

        context = build_opportunity_context(opp, client_profile)

        opp_narratives = {
            "foundation_ein": opp["foundation_ein"],
            "foundation_name": opp["foundation_name"],
            "why_this_fits": generate_why_this_fits(
                anthropic_client, context, templates["why_this_fits"], args.model, dry_run
            ),
            "positioning_strategy": generate_positioning_strategy(
                anthropic_client, context, templates["positioning_strategy"], args.model, dry_run
            ),
            "next_steps": generate_next_steps(
                anthropic_client, context, templates["next_steps"], args.model, dry_run
            )
        }

        narratives["opportunities"].append(opp_narratives)

        if not dry_run:
            api_calls += 3
            # Rate limiting
            time.sleep(1)

    # Generate executive summary
    print("\nGenerating executive summary...")
    logger.info("Generating executive summary")

    narratives["executive_summary"] = generate_executive_summary(
        anthropic_client, client_profile, opportunities, templates, args.model, dry_run
    )

    if not dry_run:
        api_calls += 2

    # Save output
    output_file = run_dir / "06_narratives.json"
    save_json(narratives, output_file)

    logger.info(f"[06_generate_narratives] Saved to {output_file}")
    if not dry_run:
        logger.info(f"[06_generate_narratives] API calls made: {api_calls}")

    # Summary
    print(f"\n{'='*60}")
    print("Narratives generated!")
    print(f"{'='*60}")
    print(f"Client: {client_profile.get('organization_name', 'Unknown')}")
    print(f"Opportunities processed: {len(opportunities)}")
    print(f"Mode: {mode}")
    if not dry_run:
        print(f"API calls: {api_calls}")

    print(f"\nExecutive Summary:")
    exec_sum = narratives["executive_summary"]
    print(f"  Key strengths: {len(exec_sum.get('key_strengths', []))} items")
    print(f"  One thing: {exec_sum.get('one_thing', '')[:60]}...")
    print(f"  Funding scenarios:")
    scenarios = exec_sum.get("funding_scenarios", {})
    print(f"    Conservative: ${scenarios.get('conservative', 0):,}")
    print(f"    Moderate: ${scenarios.get('moderate', 0):,}")
    print(f"    Ambitious: ${scenarios.get('ambitious', 0):,}")

    print(f"\nOutput: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
