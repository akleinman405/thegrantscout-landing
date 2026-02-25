# PROMPT A: Create Report Generation Skills

**Date:** 2026-02-21  
**Type:** Skill creation  
**Schema:** f990_2025  
**Next:** Prompt B (run grant-report skill on VetsBoats — after Alec reviews)

---

## Situation

TheGrantScout generates monthly grant opportunity reports for nonprofit clients. The report follows a standard template (MONTHLY_GRANT_REPORT_TEMPLATE_v6.md in project knowledge). Currently we rewrite the report prompt from scratch every time. We need two reusable skills so any future client report can be generated consistently.

---

## Task 1: Create the `grant-report` skill

**Location:** `/mnt/skills/user/grant-report/`

### Structure

```
grant-report/
├── SKILL.md
├── scripts/
│   └── pull_funder_snapshots.py
└── references/
    └── report_template.md
```

### SKILL.md

Should instruct Claude to follow four steps:

**Step 1: Pull funder snapshot data from DB**

Run `scripts/pull_funder_snapshots.py` with foundation EINs. The script queries f990_2025 and computes:

- `annual_giving`: total giving per year (last 3-5 years)
- `grant_count`: number of grants per year
- `median_grant`: median grant amount
- `grant_range`: min-max grant amounts
- `geographic_pct`: % of grants in client's state, top 3 states
- `repeat_rate`: % of recipients funded 2+ times
- `giving_trend`: growing/stable/declining (% change over 3 years)
- `comparable_grantee`: most similar grantee to client (by mission/sector)
- `giving_style_pct`: % general support vs program-specific (from grant_purpose text)
- `contacts`: officers list
- `application_info`: deadlines, submission type, restrictions

For private foundations, query: `pf_returns`, `pf_grants`, `officers`
For public charities, query: `nonprofit_returns`, `schedule_i_grants`, `officers`

**Step 2: Merge dossier data with DB data**

The skill receives both structured dossier data (from prior research) and fresh DB-pulled snapshots. Merge into complete data package per foundation.

**Step 3: Generate the report**

Write the full report following the v6 template. Key sections:

1. "If You Only Have 5 Hours" box — single highest-ROI action
2. Priority table — all 5 ranked with type, why, time estimate
3. Time Allocation Guide — 5/10/15/20 hours
4. For each foundation:
   - Why This Fits (3-4 sentences)
   - Fit Evidence table
   - Funder Snapshot table (annual giving, typical grant, geographic focus, repeat rate, giving style, funding trend)
   - How to Apply (method, requirements, contact)
   - Positioning Strategy (referencing snapshot data)
   - Action Steps table (step-by-step with time estimates)
5. 8-Week Timeline
6. Quick Reference — contacts + portals/deadlines tables

**Step 4: Output** `REPORT_[DATE]_[client]_grant_opportunities.md`

**Formatting rules:**
- Client-facing. No internal jargon ("Schedule I", "990-PF data", "deep crawl", "LASSO")
- Write as "TheGrantScout Research Team"
- Prose paragraphs for narrative, tables for structured data
- Specific dollar amounts, dates, names — no vague language
- Every foundation ends with concrete next step

### scripts/pull_funder_snapshots.py

Python script that:
- Takes a JSON file path as input (client profile + foundation list with EINs and types)
- Connects to PostgreSQL f990_2025
- Runs appropriate queries for each foundation (PF vs PC)
- Computes all snapshot metrics listed above
- Outputs JSON with complete funder data
- Handles missing data gracefully (some foundations may have sparse records)

DB connection: `host=localhost, dbname=f990_2025, schema=f990_2025`
EIN fields are VARCHAR in all tables.

Key tables and relevant columns:

```sql
-- Private foundation returns
f990_2025.pf_returns: ein, tax_year, business_name, tot_grants_paid_amt, 
  num_grants_paid, total_assets_eoy_amt, total_revenue_amt,
  app_submission_type, app_deadlines, app_restrictions, app_form_requirements

-- Private foundation grants
f990_2025.pf_grants: filer_ein, recipient_name, recipient_ein, recipient_state,
  grant_amount, grant_purpose, tax_year

-- Public charity returns  
f990_2025.nonprofit_returns: ein, tax_year, organization_name, total_revenue,
  total_assets_eoy, total_grants_paid

-- Public charity grants (Schedule I)
f990_2025.schedule_i_grants: filer_ein, recipient_name, recipient_ein,
  recipient_state, grant_amount, grant_purpose, tax_year

-- Officers (both PF and PC)
f990_2025.officers: ein, person_nm, title_txt
```

### references/report_template.md

Read `MONTHLY_GRANT_REPORT_TEMPLATE_v6.md` from project knowledge and save a copy as the reference file. This is the template the skill follows when generating reports.

### Input format the skill expects

```json
{
  "client": {
    "name": "string",
    "ein": "string",
    "mission": "string",
    "org_type": "private_foundation | public_charity",
    "state": "string (2-letter)",
    "city": "string",
    "budget": "string",
    "sector_keywords": ["string"]
  },
  "foundations": [
    {
      "ein": "string",
      "name": "string",
      "type": "private_foundation | public_charity",
      "rank": 1,
      "category": "LOI-Ready | Open Application | Upcoming Deadline | Cultivation",
      "recommended_ask": "string",
      "deadline": "string",
      "application_method": "string",
      "application_url": "string or null",
      "dossier_notes": "string",
      "fit_evidence": "string",
      "positioning_notes": "string",
      "contacts": [{"name": "string", "title": "string", "email": "string", "phone": "string"}]
    }
  ]
}
```

---

## Task 2: Create the `additional-funders` skill

**Location:** `/mnt/skills/user/additional-funders/`

### Structure

```
additional-funders/
├── SKILL.md
└── references/
    └── format_guide.md
```

### SKILL.md

Simpler skill. No DB queries. Takes a list of additional leads and generates a lighter companion document.

For each funder, write:
- **Header:** Foundation name + location
- **Why:** 2-3 sentences on relevance (grant history, mission alignment, comparable grantees)
- **Caveat (if any):** 1 sentence on what needs confirmation
- **Next Step:** One specific action
- **Grant Range:** If known
- **Contact:** If known

**Formatting:**
- Client-facing, same tone as main report
- Short intro (2 sentences): "Beyond the 5 primary opportunities, we identified additional funders worth exploring. These require a preliminary step before a full application."
- Short closing (1-2 sentences): "Several of these could become primary opportunities once eligibility is confirmed."
- Write as "TheGrantScout Research Team"
- No internal jargon

**Output:** `REPORT_[DATE]_[client]_additional_funders.md`

### Input format

```json
{
  "client": {
    "name": "string",
    "ein": "string",
    "mission": "string",
    "org_type": "string",
    "state": "string"
  },
  "additional_funders": [
    {
      "ein": "string",
      "name": "string",
      "state": "string",
      "assets": "string",
      "why": "string",
      "caveat": "string or null",
      "next_step": "string",
      "contact": "string or null",
      "grant_range": "string or null"
    }
  ]
}
```

---

## Output

| File | Description |
|------|-------------|
| `/mnt/skills/user/grant-report/SKILL.md` | Grant report skill instructions |
| `/mnt/skills/user/grant-report/scripts/pull_funder_snapshots.py` | DB query script |
| `/mnt/skills/user/grant-report/references/report_template.md` | V6 template copy |
| `/mnt/skills/user/additional-funders/SKILL.md` | Additional funders skill |
| `/mnt/skills/user/additional-funders/references/format_guide.md` | Format reference |

## STOP HERE

Do not run the skills yet. Alec will review the skill files and approve before testing on VetsBoats data.
