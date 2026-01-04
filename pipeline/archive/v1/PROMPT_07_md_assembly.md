# PROMPT_07: Phase 7 - MD Assembly

**Date:** 2025-12-27
**Phase:** 7
**Agent:** Dev Team
**Estimated Time:** 3-4 hours
**Depends On:** PROMPT_06b (AI Integration) complete

---

## Objective

Create the markdown rendering system that assembles all report data into a formatted markdown document ready for Word conversion.

---

## Context

At this point we have:
- Assembled report data (Phase 4)
- Scraped foundation info (Phase 5)
- AI-generated narratives (Phase 6)

This phase combines everything into a formatted markdown report.

**Reference:** `SPEC_2025-12-01_weekly_report_template.md`

---

## Tasks

### Task 1: Create `rendering/templates/report_template.md`

Create the main template file with placeholders. Use `{variable_name}` syntax for all dynamic content.

The template should match the structure in `SPEC_2025-12-01_weekly_report_template.md` exactly, including:
- Header with client name, week number, dates
- "If You Only Do One Thing" section
- Executive Summary (urgent actions, funding scenarios, key strengths)
- Top 5 table
- 5 opportunity detail sections
- 8-week timeline
- Quick reference (contacts, portals)
- Footer

### Task 2: Create `rendering/templates/opportunity_template.md`

Separate template for each opportunity section:
- Rank and foundation name header
- Status badge and deadline
- Why This Fits narrative
- Key Details table
- Funder Snapshot table (8 metrics)
- Potential Connections table
- Application Requirements list
- Positioning Strategy narrative
- Next Steps table

### Task 3: Create `rendering/md_renderer.py`

Main rendering module with these functions:

```python
class ReportRenderer:
    """Render report data to markdown."""
    
    def __init__(self):
        """Load templates from files."""
        pass
    
    def render(self, report_data: dict) -> str:
        """
        Render complete report to markdown.
        
        Args:
            report_data: Complete report data dict (from Phase 4 + 5 + 6)
            
        Returns:
            Formatted markdown string
        """
        pass
    
    def render_to_file(self, report_data: dict, output_path: str) -> str:
        """Render and save to file."""
        pass
```

**Helper methods needed:**

```python
# Formatting helpers
def _format_amount_range(self, opp: dict) -> str:
    """Format '$50,000 - $100,000' from min/max."""
    pass

def _format_contact(self, opp: dict) -> str:
    """Format 'Name, email, phone' string."""
    pass

def _format_annual_giving(self, opp: dict) -> str:
    """Format '$2.5M across 45 grants' from snapshot."""
    pass

def _format_typical_grant(self, opp: dict) -> str:
    """Format '$45,000 median (range: $5,000 - $150,000)'."""
    pass

def _format_geographic(self, opp: dict) -> str:
    """Format 'CA (78%), 82% in-state overall'."""
    pass

def _format_repeat_rate(self, opp: dict) -> str:
    """Format '34% of recipients funded 2+ times'."""
    pass

def _format_giving_style(self, opp: dict) -> str:
    """Format '62% general support / 38% program-specific'."""
    pass

def _format_funding_trend(self, opp: dict) -> str:
    """Format 'Growing (+15% over 3 years)'."""
    pass

def _format_comparable_grant(self, opp: dict) -> str:
    """Format 'Org Name received $50,000 for purpose (2023)'."""
    pass

# Table formatters
def _format_top_5_table(self, opportunities: list) -> str:
    """Generate markdown table rows for Top 5."""
    pass

def _format_urgent_actions_table(self, opportunities: list) -> str:
    """Generate urgent actions table rows."""
    pass

def _format_connections_table(self, opp: dict) -> str:
    """Generate connections table rows."""
    pass

def _format_next_steps_table(self, opp: dict) -> str:
    """Generate next steps table rows."""
    pass

def _format_timeline_table(self, timeline: list) -> str:
    """Generate 8-week timeline rows."""
    pass

def _format_contacts_table(self, opportunities: list) -> str:
    """Generate quick reference contacts table."""
    pass

def _format_portals_table(self, opportunities: list) -> str:
    """Generate quick reference portals table."""
    pass

# Calculation helpers
def _calculate_funding_scenarios(self, opportunities: list) -> dict:
    """Calculate conservative/moderate/ambitious funding ranges."""
    pass

def _calculate_next_report_date(self, current_date: str) -> str:
    """Calculate next report date (7 days out)."""
    pass
```

### Task 4: Create `rendering/__init__.py`

Export main functions:

```python
from .md_renderer import ReportRenderer

__all__ = ['ReportRenderer']
```

---

## Output Files

| File | Description |
|------|-------------|
| `rendering/__init__.py` | Package init |
| `rendering/md_renderer.py` | Main renderer |
| `rendering/templates/report_template.md` | Main template |
| `rendering/templates/opportunity_template.md` | Opportunity section template |

---

## Done Criteria

- [ ] Templates created matching spec
- [ ] `ReportRenderer.render()` returns valid markdown
- [ ] All tables properly formatted
- [ ] All numeric values formatted with commas, dollar signs
- [ ] Percentages formatted consistently
- [ ] Dates formatted consistently
- [ ] Output renders correctly in markdown viewer
- [ ] No placeholder variables left unfilled

---

## Verification Tests

### Test 1: Basic Render
```python
from rendering import ReportRenderer
from assembly.report_data import assemble_report_data

# Get sample report data
report_data = assemble_report_data("Sample Client")

# Render to markdown
renderer = ReportRenderer()
md = renderer.render(report_data)

# Check for key sections
assert "# Sample Client" in md
assert "## If You Only Do One Thing This Week" in md
assert "## Executive Summary" in md
assert "## Opportunity #1" in md
assert "## 8-Week Timeline" in md
```

### Test 2: Table Formatting
```python
md = renderer.render(report_data)

# Check tables have proper structure
assert "| # | Funder | Amount | Deadline | Fit | Effort | Status |" in md
assert "|---|--------|--------|----------|-----|--------|--------|" in md
```

### Test 3: No Unfilled Placeholders
```python
md = renderer.render(report_data)

# Check no raw placeholders remain
assert "{" not in md or "```" in md  # Allow code blocks
```

### Test 4: Save to File
```python
renderer.render_to_file(report_data, "outputs/test_report.md")

# Verify file exists and is readable
with open("outputs/test_report.md") as f:
    content = f.read()
    assert len(content) > 1000
```

### Test 5: Visual Inspection
```python
# Open outputs/test_report.md in a markdown viewer
# Check:
# - Headers render properly
# - Tables align correctly
# - No broken formatting
```

---

## Notes

### Markdown Table Alignment

All tables must have proper alignment rows:
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Value 1  | Value 2  |
```

### Handling Missing Data

For optional fields that may be None:
- Use "Not available" or "—" instead of empty cells
- Don't show rows for completely missing sections

### Character Escaping

Escape special markdown characters in user-provided text:
- `|` in table cells → `\|`
- `*` and `_` → `\*` and `\_`

---

## Handoff

After completion:
1. Render report for 2 sample clients
2. Review markdown in viewer
3. Check for formatting issues
4. PM reviews before proceeding to PROMPT_08

---

*Next: PROMPT_08 (End-to-End Pipeline)*
