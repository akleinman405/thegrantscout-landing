# PROMPT: Execute .claude Folder Cleanup + Create Report Generation SOP

**Date:** 2025-01-02
**Executor:** Claude Code CLI
**Input:** REPORT_2026-01-02.1_claude_folder_audit.md

---

## Objective

Execute the approved cleanup from the audit report, with two additions:
1. **Preserve documentation SOPs** (PROMPT, REPORT, SPEC, LESSONS_LEARNED naming conventions and standards)
2. **Create new SOP** for Report Generation using Pipeline V2

---

## Part 1: Execute Cleanup

### Step 1: Create Archive Structure

```bash
mkdir -p .claude/archive/2025-11-27_agent_system
```

### Step 2: Archive Files (Don't Delete)

Move all Nov 27 agent system files to archive:

```bash
# Agent definitions
mv .claude/agents .claude/archive/2025-11-27_agent_system/

# Guide files
mv .claude/guides .claude/archive/2025-11-27_agent_system/
mv .claude/SESSION_STATUS.md .claude/archive/2025-11-27_agent_system/
mv .claude/QUICK_REFERENCE.md .claude/archive/2025-11-27_agent_system/
mv .claude/SYSTEM_OVERVIEW.md .claude/archive/2025-11-27_agent_system/
mv .claude/TEAM_COLLABORATION_GUIDE.md .claude/archive/2025-11-27_agent_system/
mv .claude/TEAM_INVOCATION_GUIDE.md .claude/archive/2025-11-27_agent_system/
mv .claude/MULTI_BUILDER_GUIDE.md .claude/archive/2025-11-27_agent_system/
mv .claude/CONTEXT_TRACKING_GUIDE.md .claude/archive/2025-11-27_agent_system/
mv .claude/STATE_PERSISTENCE_GUIDE.md .claude/archive/2025-11-27_agent_system/

# Historical decision doc
mv ".claude/SIMPLIFIED_AGENT_TEAM_v2 2025-12-4.md" .claude/archive/
```

### Step 3: Delete Stale Files

```bash
rm -rf .claude/state
rm -rf .claude/memory
rm -rf .claude/scripts
rm -rf .claude/commands
rm -rf .claude/research
rm -rf .claude/cdfi_research
rm -f .claude/mailbox.jsonl
rm -f .claude/check-status.sh
```

### Step 4: Verify Preserved Files

Confirm these still exist after cleanup:

| File/Folder | Purpose | Status |
|-------------|---------|--------|
| CLAUDE.md | Core instructions | Should exist |
| SKILL_foundation_scraper.md | Enrichment skill | Should exist |
| rules/clients.md | Beta client info | Should exist |
| rules/database.md | DB conventions | Should exist |
| rules/naming.md | Doc naming standards | Should exist |
| rules/reports.md | Report quality criteria | Should exist |
| templates/ | Project templates | Should exist |
| mcp/postgres/ | DB connection config | Should exist |
| hooks/ | Future hooks | Should exist |
| 1. Enhancements/ | Historical reference | Should exist |

---

## Part 2: Verify/Update Documentation SOPs

### Check rules/naming.md

Confirm it contains the document type standards:

| Prefix | Purpose | Example |
|--------|---------|---------|
| PROMPT_ | Instructions for Claude Code CLI | PROMPT_2025-01-02_build_reports.md |
| REPORT_ | Session summaries, findings | REPORT_2025-01-02_audit_results.md |
| SPEC_ | Specifications, designs | SPEC_2025-01-02_enrichment_schema.md |
| OUTPUT_ | Generated artifacts | OUTPUT_2025-01-02_client_report.md |
| LESSONS_ | Lessons learned | LESSONS_2025-01-02_pipeline_issues.md |
| SOP_ | Standard operating procedures | SOP_2025-01-02_report_generation.md |

**If SOP_ prefix is not documented, add it.**

### Check rules/reports.md

Confirm it contains report quality criteria. If not, note what's missing.

---

## Part 3: Update CLAUDE.md

### Add "Use Cases" Section (near top)

```markdown
## Use Cases

Claude Code CLI supports these workflows for TheGrantScout:

1. **Report Generation** - Monthly grant opportunity reports using Pipeline V2
2. **Software Development** - Algorithm improvements, pipeline scripts, database work
3. **Sales Support (Nonprofits)** - Prospect enrichment, outreach prep
4. **Marketing** - LinkedIn posts, website copy, email sequences
5. **Progress Tracking** - Session summaries, goal tracking, time logging
6. **Client Feedback** - Process beta feedback, update profiles
7. **B2B Sales** - Foundation management company research and outreach
8. **Operations** - Client onboarding, payments, delivery tracking

See `SOP_report_generation.md` for detailed report workflow.
```

### Add "Pipeline V2" Section

```markdown
## Report Generation Pipeline (V2)

Location: `Pipeline v2/scripts/`

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| 01_load_client.py | Load client profile | Questionnaire | 01_client.json |
| 02_score_foundations.py | Match foundations | Client profile | 02_scored_foundations.csv |
| 03_check_enrichment.py | Check cache | Scored foundations | 03_enrichment_status.json |
| 03b_store_enrichment.py | Store research | Enrichment data | DB: foundation_enrichment |
| 04_filter_viable.py | Apply viability | Enrichment | 04_viable_foundations.json |
| 05_assemble_opportunities.py | Build opportunities | Viable foundations | 05_opportunities.json |
| 06_generate_narratives.py | Create positioning | Opportunities | 06_narratives.json |
| 07_build_report_data.py | Structure report | Narratives | 07_report_data.json |
| 08_render_report.py | Generate markdown | Report data | 08_report.md |
| 09_convert_to_docx.py | Export to Word | Markdown | 08_report.docx |

See `SOP_report_generation.md` for full workflow with quality checkpoints.
```

### Add "Skills" Section

```markdown
## Skills

| Skill | Purpose | Location |
|-------|---------|----------|
| Foundation Scraper | Extract enrichment data from foundation websites | SKILL_foundation_scraper.md |
```

### Remove Outdated Content

Remove or update any references to:
- 16-agent system
- Router, mailbox, task graphs
- Multi-builder coordination
- Agent invocation patterns

---

## Part 4: Create Report Generation SOP

Create new file: `.claude/SOP_report_generation.md`

```markdown
# SOP: Monthly Report Generation

**Version:** 1.0
**Created:** 2025-01-02
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
2. Adjusted score (original × viability multiplier)
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

*SOP Version 1.0 - Created 2025-01-02*
```

---

## Part 5: Final Verification

After all changes:

1. **Show updated folder structure:**
   ```bash
   find .claude -type f -name "*.md" | head -20
   ```

2. **Show updated CLAUDE.md** - Display full contents for review

3. **Confirm SOP created** - Show first 50 lines of SOP_report_generation.md

4. **Verify no broken references** - Search for any references to deleted files

---

## Deliverables

1. Clean `.claude` folder with archive
2. Updated `CLAUDE.md` with use cases, Pipeline V2, skills
3. New `SOP_report_generation.md` with full workflow
4. Updated `rules/naming.md` with SOP_ prefix (if needed)

---

*Execute with checkpoints. Show CLAUDE.md and SOP contents before finalizing.*
