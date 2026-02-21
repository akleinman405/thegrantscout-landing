# SKILL: Grant Report Generation

**Purpose:** Generate monthly grant opportunity reports for nonprofit clients using database-backed funder snapshots and a standardized template.

---

## Overview

This skill produces a **monthly grant opportunities report** for a nonprofit client. It combines structured data from PostgreSQL (funder snapshots) with enrichment research and narrative writing to deliver a client-ready document.

The report profiles 5 foundations with detailed fit evidence, application instructions, contacts, and a monthly action plan.

### When to Use

- Monthly report generation for an active client
- One-off grant opportunity report for a prospect or pilot
- Refreshing a previous report with updated data

### When NOT to Use

- Client viability checks (use `SKILL_client_viability_check.md` instead)
- Foundation scraping/enrichment (use `SKILL_foundation_scraper.md` instead)
- Additional funders companion document (use `additional-funders` skill instead)

---

## Required Inputs

| Input | Required | Source | Notes |
|---|---|---|---|
| Client profile JSON | Yes | `4. Pipeline/config/clients/` or user | Must include name, EIN, state, NTEE, revenue |
| Foundation list | Yes | Pipeline scoring output or user | 5 foundation EINs with names |
| Enrichment dossiers | Yes | Foundation Scraper skill or user | Website research, contacts, application process |

---

## Process Steps

### Step 1: Pull Funder Snapshots (Automated)

Run the snapshot script to extract structured data from PostgreSQL:

```bash
python3 .claude/skills/grant-report/scripts/pull_funder_snapshots.py input.json --output snapshots.json
```

**Input JSON format:**

```json
{
    "client": {
        "name": "Organization Name",
        "ein": "123456789",
        "state": "CA",
        "ntee_code": "X20",
        "annual_revenue": 5000000
    },
    "foundations": [
        {"ein": "941234567", "name": "Example Foundation"},
        {"ein": "952345678", "name": "Another Foundation"}
    ]
}
```

**Output:** JSON file with per-foundation metrics:
- Annual giving, grant count, median grant, grant range
- Geographic concentration (% in client's state)
- Repeat funding rate
- Giving trend (Growing/Stable/Declining with % change)
- Giving style (general support vs. program-specific)
- Comparable grantees (up to 5 recent, in-state preferred)
- Officers/directors (most recent year)
- Application info (deadlines, restrictions, contacts) for private foundations

### Step 2: Merge Enrichment Dossiers

Combine snapshot data with enrichment research gathered via Foundation Scraper or manual research:

- **Website research:** Application process details, program areas, recent news
- **Contact information:** Staff names, titles, emails, phone numbers
- **Application process:** Portal URLs, LOI requirements, deadlines, form details
- **Board members:** Key names and backgrounds

For each foundation, classify as one of:
- **LOI-Ready** - Accepts unsolicited Letters of Inquiry
- **Open Application** - Has formal application process
- **Upcoming Deadline** - Application deadline approaching
- **Cultivation** - Invitation-only or relationship-required
- **RFP-Based** - Only funds via specific RFPs (include only if open RFP matches)

### Step 3: Generate Report

Use the template at `references/report_template.md` to structure the report.

**Required sections for every report:**

1. **If You Only Have 5 Hours** - Single highest-ROI action
2. **This Month's Focus** - Priority order table with time estimates
3. **Foundation Types Explained** - Only include types present in this report
4. **Top 5 at a Glance** - Summary table with fit scores
5. **Foundation Profiles** (x5) - Each includes:
   - Why This Foundation (2-3 sentences)
   - Fit Evidence table (grants to sector, geography, org size, comparable grantee)
   - Funder Snapshot metrics table
   - How to Apply section (type-specific)
   - Contacts table (at least 2 per foundation)
   - Potential Connections
   - Positioning Strategy
   - Action Steps with time estimates
6. **Monthly Action Plan** - Week-by-week breakdown
7. **Quick Reference** - All contacts, application summary, time summary

### Step 4: Output

1. Write the report as markdown (source of truth):
   `REPORT_YYYY-MM-DD.N_{client}_grant_report.md`

2. Convert to client deliverable formats:
   ```bash
   python3 "0. Tools/md_to_docx.py" -i report.md -o report.docx
   python3 "0. Tools/md_to_pdf.py" -i report.md -o report.pdf
   ```

3. Save all outputs to: `5. Runs/{Client}/{date}/`

---

## Writing Guidelines

**Voice:** Write as "TheGrantScout Research Team" - professional, knowledgeable, direct.

**Tone rules:**
- No jargon the client wouldn't know
- No em dashes (use commas, periods, colons instead)
- No hedging ("might", "could potentially") - be direct about fit
- Dollar amounts formatted as $X,XXX or $X.XM
- Explain WHY, not just WHAT (e.g., "They've funded 12 orgs like yours" not "They make grants")

**Data integrity:**
- Every metric in Funder Snapshot must come from the snapshot JSON or enrichment
- Never fabricate grant amounts, contact info, or deadlines
- If data is missing, say so (e.g., "Contact information not publicly available")
- Comparable grantee names must match database records exactly

**Formatting (for PDF output):**
- Blank line required before tables, bullet lists, and numbered lists
- Blank line required between consecutive bold metadata lines
- No code blocks in the client-facing portion (use tables or bullets instead)
- Use `<div class="page-break"></div>` for page breaks
- Website URLs as markdown links for clickable PDFs

---

## Quality Checklist

Before delivering:

- [ ] All 5 foundations have complete Funder Snapshot tables
- [ ] All Fit Evidence tables cite specific grant counts and amounts from data
- [ ] Comparable grantees verified against database (name, amount, year)
- [ ] No foundations from client's known funders list (check `dim_clients.known_funders`)
- [ ] All foundations active (grants in past 3 years)
- [ ] All deadlines are current (not expired)
- [ ] At least 2 contacts per foundation (or noted as unavailable)
- [ ] Dollar amounts formatted consistently
- [ ] No duplicate foundations
- [ ] Week-by-week action plan adds up to total time estimate
- [ ] All links verified working
- [ ] Both .md and .docx/.pdf produced

---

## Reference Files

- **Report template:** `references/report_template.md` (v6)
- **Snapshot script:** `scripts/pull_funder_snapshots.py`
- **Branding:** `0. Tools/branding.py`
- **Converters:** `0. Tools/md_to_docx.py`, `0. Tools/md_to_pdf.py`

---

*Skill version 1.0 - Created 2026-02-21*
