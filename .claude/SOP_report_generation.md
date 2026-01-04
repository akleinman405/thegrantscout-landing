# SOP: Monthly Report Generation

**Version:** 1.0
**Created:** 2026-01-02
**Purpose:** Standard procedure for generating monthly grant opportunity reports

---

## Overview

This SOP covers generating grant opportunity reports for TheGrantScout clients using Pipeline V2 scripts and the foundation enrichment system.

**Time estimate:** 1-2 hours per client (depending on cache hits)
**Output:** Client-ready report (markdown + docx)

---

## Prerequisites

Before starting:
- [ ] Client has completed questionnaire
- [ ] Client profile exists or can be created
- [ ] Database connection working (`psql` to f990_2025)
- [ ] Pipeline V2 scripts available in `Pipeline v2/scripts/`

---

## Workflow

### Phase 1: Client Setup

**Script:** `01_load_client.py`

1. Load client from questionnaire data
2. Verify these fields are populated:
   - `specific_ask_text` - What they're specifically looking for
   - `grant_type_preference` - Capital, program, general, etc.
   - `target_grant_size` - Their preferred grant range
   - `geographic_scope` - Where they operate

**Quality Check:**
- [ ] Client profile has specific_ask_text
- [ ] Grant type preference makes sense for their ask

**Output:** `runs/{client}/YYYY-MM/01_client.json`

---

### Phase 2: Foundation Scoring

**Script:** `02_score_foundations.py`

1. Run 10-signal matching algorithm
2. Generate top 20 scored foundations

**Quality Check:**
- [ ] Review top 10 foundations - do they make sense for this client?
- [ ] For capital-seeking clients: Are capital funders appearing?
- [ ] For geographic-specific clients: Are local funders appearing?

**If poor matches:** Check client profile, may need to adjust parameters.

**Output:** `runs/{client}/YYYY-MM/02_scored_foundations.csv`

---

### Phase 3: Enrichment Check

**Script:** `03_check_enrichment.py`

1. Check database for cached enrichment data
2. Identify foundations needing research

**Output:** `runs/{client}/YYYY-MM/03_enrichment_status.json`

Categories:
- `READY` - Have fresh data, proceed
- `NEEDS_FULL_ENRICHMENT` - No data or >90 days old
- `NEEDS_VERIFICATION` - Have data but contacts >30 days old

---

### Phase 4: Foundation Research

**Skill:** `SKILL_foundation_scraper.md`

For each foundation needing enrichment:

1. Find foundation website
2. Extract fields per skill instructions:
   - accepts_unsolicited
   - application_type
   - application_url
   - current_deadline
   - contact_name, contact_email
   - program_priorities
   - geographic_focus
   - grant_range_stated
   - application_requirements
   - red_flags
3. Store via `03b_store_enrichment.py`

**Quality Check:**
- [ ] Each enrichment record has accepts_unsolicited value
- [ ] Red flags identified where appropriate
- [ ] Contact info captured where available

**Output:** Database records in `foundation_enrichment` table

---

### Phase 5: Viability Filtering

**Script:** `04_filter_viable.py`

1. Calculate viability tier for each foundation:
   - **READY** - Clear path to apply (multiplier 0.85-1.0)
   - **CONDITIONAL** - Possible but needs verification (0.5-0.7)
   - **WATCH** - Relationship building only (0.2-0.3)
   - **SKIP** - Exclude from report (0.0)

2. Apply multipliers to adjust scores

**Quality Check:**
- [ ] At least 5 foundations are READY or CONDITIONAL
- [ ] If <5 viable, pull next batch and repeat Phase 3-4
- [ ] Review SKIP foundations - are exclusions correct?

**Output:** `runs/{client}/YYYY-MM/04_viable_foundations.json`

---

### Phase 6: Select Final 5

From viable foundations, select top 5 based on:
1. Viability tier (READY > CONDITIONAL > WATCH)
2. Adjusted score (original x viability multiplier)
3. Alignment with client's specific_ask_text
4. Grant type match

**Quality Check (CRITICAL):**
- [ ] Each foundation actually matches client's needs
- [ ] Mix of tiers is appropriate
- [ ] No red flags missed
- [ ] For multi-priority clients (e.g., Friendship Circle): mix covers both priorities

**STOP AND REVIEW** - Get approval before proceeding to narratives.

---

### Phase 7: Assemble & Generate

**Scripts:** `05_assemble_opportunities.py`, `06_generate_narratives.py`

1. Assemble opportunity objects with all data
2. Generate positioning narratives for each foundation

**Quality Check:**
- [ ] Narratives reference client's specific ask
- [ ] Action types are appropriate (Apply Now / Send LOI / Build Relationship)
- [ ] Deadlines are accurate and not passed

**Outputs:**
- `runs/{client}/YYYY-MM/05_opportunities.json`
- `runs/{client}/YYYY-MM/06_narratives.json`

---

### Phase 8: Build Report

**Scripts:** `07_build_report_data.py`, `08_render_report.py`, `09_convert_to_docx.py`

1. Structure report data
2. Render to markdown
3. Convert to Word document

**Final Quality Check:**
- [ ] Report has 5 foundations (or explanation if fewer)
- [ ] All deadlines are future dates
- [ ] Contact info present where available
- [ ] Client's specific ask reflected in recommendations
- [ ] No broken URLs
- [ ] Grammar/formatting clean

**Outputs:**
- `runs/{client}/YYYY-MM/07_report_data.json`
- `runs/{client}/YYYY-MM/08_report.md`
- `runs/{client}/YYYY-MM/08_report.docx`

---

## Batch Processing (Multiple Clients)

When generating reports for multiple clients:

1. **Group by similarity:**
   - Program-focused clients together
   - Capital-seeking clients together
   - Geographic clusters together

2. **Leverage cache:** Run enrichment-heavy clients first to populate cache for others

3. **Parallel execution:** Can run 2-3 clients simultaneously in different terminals (watch for DB write conflicts)

4. **Quality gates:** Still review each client's final 5 before generating narratives

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| <5 viable foundations | Narrow niche or strict viability | Expand to top 30-50, consider WATCH tier |
| Poor matches | Client profile incomplete | Review specific_ask_text and grant_type_preference |
| Stale enrichment | Cache >90 days | Re-run Phase 4 research |
| Missing contacts | Foundation website sparse | Note in report, check LinkedIn |
| Passed deadlines | Data not refreshed | Verify deadlines before finalizing |

---

## Output Locations

All outputs saved to: `Pipeline v2/runs/{client_name}/YYYY-MM/`

Final deliverables:
- `08_report.md` - Markdown version
- `08_report.docx` - Word version for client

---

## Monthly Schedule

| Day | Task |
|-----|------|
| 25th-30th | Generate reports for all clients |
| 1st | Send reports to clients |
| 2nd-5th | Follow-up calls for feedback |

---

*SOP Version 1.0 - Created 2026-01-02*
