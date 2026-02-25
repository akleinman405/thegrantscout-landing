# SKILL: Additional Funders Companion Document

**Purpose:** Generate a companion document listing secondary foundation leads beyond the top 5 profiled in the main grant report.

---

## Overview

This skill produces a supplementary document that accompanies the main monthly grant report. It lists 10-20 additional foundations that scored well but didn't make the top 5, giving the client a broader pipeline for future months.

This document is lighter than the main report: no deep profiles, no action plans. It provides enough information for the client to decide which foundations to research further.

### When to Use

- After generating a main grant report (grant-report skill)
- When the client has 15+ viable foundations and wants a broader view
- When a client asks "what else do you have?"

### When NOT to Use

- As a standalone document (always pair with a main report)
- For the top 5 foundations (those go in the main report)
- When fewer than 10 additional foundations are viable

---

## Required Inputs

| Input | Required | Source | Notes |
|---|---|---|---|
| Scored foundations list | Yes | Pipeline scoring output | Beyond the top 5 already profiled |
| Client profile | Yes | Main report inputs | Same client info used for the main report |
| Funder snapshots | Optional | `pull_funder_snapshots.py` | Run for additional EINs if needed |

---

## Process Steps

### Step 1: Read Inputs

- Read the input JSON (client profile + additional funders list)
- Print summary: client name, N funder names
- Validate: all have EINs, none overlap with top 5 in main report

### Step 2: Write the Document

Follow the format in `references/format_guide.md`. Group foundations into tiers:

- **Tier A: Strong Fit** - High model score, strong geographic/sector match
- **Tier B: Good Fit** - Moderate score, partial match on geography or sector
- **Tier C: Worth Watching** - Lower score but notable for specific reasons

For each foundation, gather (from database or snapshot script):
- Name, EIN, state, city
- Total assets
- Annual giving (average)
- Median grant size
- Geographic relevance (% in client's state)
- Most recent grant year
- One comparable grantee if available

Save draft to `Enhancements/[DATE]/REPORT_[DATE]_[client]_additional_funders.md`

### STOP: Review Draft

Tell Alec the document is ready for review at the file path above.

**Wait for Alec to approve or request edits.** Apply any edits.

### Step 3: Finalize

1. Save final version to `Enhancements/[DATE]/REPORT_[DATE]_[client]_additional_funders.md`

2. Convert to .docx if the client prefers Word format:
   ```bash
   python3 "0. Tools/md_to_docx.py" -i additional_funders.md -o additional_funders.docx
   ```

3. Save alongside the main report in `5. Runs/{Client}/{date}/`

4. Write session report using `references/session_report_template.md`:
   Save to `Enhancements/[DATE]/REPORT_[DATE]_[client]_additional_funders_session.md`

---

## Writing Guidelines

- Keep entries brief: 2-3 lines per foundation max
- Focus on WHY this foundation is relevant (sector, geography, grant size)
- Include one comparable grantee per foundation if available
- No application process details (save that for when they move to the main report)
- Dollar amounts formatted as $X,XXX or $X.XM

---

## Quality Checklist

- [ ] No overlap with top 5 in main report
- [ ] No foundations from client's known funders list
- [ ] All foundations active (grants in past 3 years)
- [ ] Tier assignments match the data (don't inflate)
- [ ] At least 10 foundations listed (or explain why fewer)
- [ ] Dollar amounts formatted consistently
- [ ] Session report written

---

## Reference Files

- **Format guide:** `references/format_guide.md`
- **Session report template:** `references/session_report_template.md`
- **Snapshot script:** `../grant-report/scripts/pull_funder_snapshots.py`

---

*Skill version 1.1 - Updated 2026-02-21 (added pause gate + session report)*
