# Enrichment Tracking Guide

Track manual research on foundations to identify patterns for future automation.

## Purpose

When manually researching foundations for client reports, log:
1. **What** you searched for
2. **Where** you found it (or didn't)
3. **How long** it took

After 20-30 foundations, review to identify:
- Most commonly searched fields
- Fields that are easy to find vs. hard
- Data sources that are most reliable
- Fields that rarely produce useful results

## How to Use

1. Copy `enrichment_tracking_template.csv` to the client's run folder
2. Rename to `enrichment_log.csv`
3. Add a row for each field you research
4. Be honest about time and confidence

## Fields

| Field | Description | Example |
|-------|-------------|---------|
| foundation_ein | Foundation's EIN | 123456789 |
| foundation_name | Foundation name | The Ford Foundation |
| client_name | Which client this research was for | PSMF |
| search_goal | What you were looking for | application_deadline, contact_email, eligibility_budget |
| result_found | Did you find it? | yes, no, partial |
| result_value | What you found | March 15 2026, jane@foundation.org, Min $500K |
| source_url | Where you found it | https://fordfoundation.org/apply |
| confidence | How reliable is this info? | high, medium, low |
| time_minutes | How long did this take? | 5 |
| notes | Any additional context | Found on grants page, PSMF qualifies |
| date_researched | When you did this research | 2026-01-06 |
| eligibility_check | Which eligibility criterion (if applicable) | budget_requirement, org_type_requirement |
| eligibility_met | Does client meet this requirement? | YES, NO, UNCLEAR |

## Common Search Goals

Use these standard values for `search_goal`:

### Application & Contact Info
- `application_deadline` - When applications are due
- `application_url` - Link to apply or submit LOI
- `contact_email` - General or program officer email
- `contact_phone` - Phone number
- `program_officer` - Name of relevant program officer
- `accepts_unsolicited` - Do they accept applications?
- `loi_required` - Is an LOI required before full application?
- `funding_cycle` - When do they make decisions?

### Foundation Focus
- `giving_focus` - Current funding priorities
- `geographic_focus` - Where they fund
- `grant_range` - Typical grant sizes they make
- `recent_grants` - Recent grants in relevant area

### Eligibility Criteria (NEW - Added 2026-01-13)

**CRITICAL:** Check these BEFORE spending time on other research. If client doesn't meet eligibility → SKIP.

- `eligibility_budget` - Min/max recipient budget requirements
- `eligibility_org_type` - Required organization type (501c3, public charity, etc.)
- `eligibility_org_age` - Required years in operation
- `eligibility_geography` - Geographic restrictions beyond state level
- `eligibility_project_type` - Allowed project types (capital, program, general operating)
- `eligibility_grant_size` - Typical/max grant amount (is it meaningful for client?)
- `eligibility_other` - Any other disqualifying criteria

### Eligibility Check Values

For `eligibility_check` field, use:
- `budget_requirement`
- `org_type_requirement`
- `org_age_requirement`
- `geographic_restrictions`
- `project_type_restrictions`
- `grant_size_range`
- `other_restrictions`

For `eligibility_met` field, use:
- `YES` - Client meets this requirement
- `NO` - Client does NOT meet this requirement → **SKIP foundation**
- `UNCLEAR` - Requirement is ambiguous → **CONDITIONAL** status

## After 20-30 Entries

Run this analysis:

1. **Most searched fields:** What do we look up most often?
2. **Success rate by field:** Which fields are usually found?
3. **Time by field:** Which fields take longest?
4. **Source patterns:** Where do we find each field type?

This informs what to automate first (high frequency + high success + predictable source).

## Storage Location

- Template: `pipeline/templates/enrichment_tracking_template.csv`
- Per-run logs: `runs/{client}/{date}/enrichment_log.csv`
- Aggregated analysis: `runs/enrichment_analysis.csv` (combine all logs periodically)
