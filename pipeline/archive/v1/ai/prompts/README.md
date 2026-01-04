# AI Prompt Templates

This directory contains prompt templates for generating AI narratives in grant reports.

## Prompts

### 1. `why_this_fits.txt`
**Purpose:** Explain why a foundation matches the client.

**Required Variables:**
| Variable | Description | Format |
|----------|-------------|--------|
| `client_name` | Organization name | string |
| `client_mission` | Mission statement | string |
| `client_programs` | Comma-separated programs | string |
| `client_city` | City | string |
| `client_state` | State (2-letter) | string |
| `client_budget` | Budget description | string |
| `foundation_name` | Foundation name | string |
| `annual_giving` | Total annual giving | float |
| `grant_count` | Number of grants | int |
| `median_grant` | Median grant amount | float |
| `min_grant` | Minimum grant | float |
| `max_grant` | Maximum grant | float |
| `top_state` | Top state for giving | string |
| `top_state_pct` | Percentage to top state | float (0-1) |
| `in_state_pct` | Percentage in-state | float (0-1) |
| `general_support_pct` | Pct general support | float (0-1) |
| `program_specific_pct` | Pct program-specific | float (0-1) |
| `funding_trend` | "Growing"/"Stable"/"Declining" | string |
| `comparable_grant_text` | Description of similar grant | string |
| `deadline` | Application deadline | string |

**Output:** 3-4 sentences

---

### 2. `positioning_strategy.txt`
**Purpose:** Actionable advice on framing the application.

**Required Variables:**
All variables from `why_this_fits.txt` plus:
| Variable | Description | Format |
|----------|-------------|--------|
| `repeat_rate` | Repeat funding rate | float (0-1) |
| `budget_min` | Min recipient budget | float |
| `budget_max` | Max recipient budget | float |
| `primary_sector` | Primary funding sector | string |
| `trend_change_pct` | 3-year trend change | float (-1 to +1) |
| `client_strengths` | Client strengths | string |
| `connections_text` | Description of connections | string |

**Output:** 3-4 sentences

---

### 3. `next_steps.txt`
**Purpose:** Generate actionable next steps with deadlines.

**Required Variables:**
| Variable | Description | Format |
|----------|-------------|--------|
| `foundation_name` | Foundation name | string |
| `deadline` | Application deadline | string |
| `contact_name` | Program officer name | string |
| `contact_email` | Program officer email | string |
| `prior_relationship` | Relationship status | string |
| `requirements_list` | Bulleted requirements | string |
| `today` | Current date | YYYY-MM-DD |

**Output:** JSON array of 3-5 steps with action/deadline/owner

---

### 4. `key_strengths.txt`
**Purpose:** Executive summary key strengths.

**Required Variables:**
| Variable | Description | Format |
|----------|-------------|--------|
| `client_name` | Organization name | string |
| `client_city` | City | string |
| `client_state` | State | string |
| `client_programs` | Programs | string |
| `client_budget` | Budget | string |
| `opportunities_summary` | Summary of all 5 opps | string |

**Output:** Exactly 3 bullet points

---

### 5. `one_thing.txt`
**Purpose:** Single most critical action.

**Required Variables:**
| Variable | Description | Format |
|----------|-------------|--------|
| `opportunities_with_deadlines` | All opps with deadlines | string |
| `today` | Current date | YYYY-MM-DD |

**Output:** Single sentence, bolded

---

## Usage

```python
from pathlib import Path

def load_prompt(name: str) -> str:
    """Load prompt template by name."""
    path = Path(__file__).parent / f"{name}.txt"
    return path.read_text()

# Example
template = load_prompt("why_this_fits")
prompt = template.format(
    client_name="Oakland Youth Services",
    client_mission="Empowering youth through education...",
    # ... other variables
)
```

## Variable Formatting

For numbers:
- Currency: `{amount:,.0f}` → "45,000"
- Percentage: `{rate:.0%}` → "78%"
- Signed percentage: `{change:+.0%}` → "+12%" or "-5%"

## Quality Guidelines

Good outputs:
- Reference specific data points
- Use actual numbers from context
- Avoid generic phrases
- Match specified length

Bad outputs:
- Generic advice that could apply to anyone
- Missing data references
- Wrong length
- Phrases like "would be a good fit"
