# PROMPT: Audit and Clean Up .claude Folder

**Date:** 2025-01-02
**Executor:** Claude Code CLI
**Priority:** Medium - Do after current report generation completes

---

## Objective

Review the `.claude` folder and recommend cleanup to optimize for all current use cases:

1. **Report Generation** - Building monthly grant reports using Pipeline V2 scripts with enrichment caching
2. **Software Development** - Improving matching algorithms, pipeline scripts, database, and infrastructure
3. **Sales Support (Nonprofits)** - Prospect enrichment, foundation research, outreach prep
4. **Marketing** - Writing LinkedIn posts, social media content, website copy
5. **Progress Tracking** - Logging time, tracking goals, session summaries
6. **Client Feedback & Iteration** - Processing beta feedback, updating profiles, identifying improvements
7. **B2B Sales (Foundation Management Companies)** - Research, call prep, pipeline tracking for B2B channel
8. **Operations Tracking** - Client onboarding, payments, delivery schedule, capacity planning

The `.claude` folder should support all of these efficiently without conflicting instructions.

---

## Current State

The `.claude` folder contains files from various development phases (Nov-Dec 2025). Some may be outdated, redundant, or conflicting with current workflow.

**Known contents:**
- `CLAUDE.md` - Main instructions file (updated Dec 31)
- `SKILL_foundation_scraper.md` - New skill for enrichment research (Jan 1)
- `SIMPLIFIED_AGENT_TEAM_v2 2025-12-4.md` - Agent definitions
- Multiple guide files (CONTEXT_TRACKING, STATE_PERSISTENCE, TEAM_COLLABORATION, etc.)
- `SESSION_STATUS.md` - From Nov 27 (likely stale)
- Folders: agents, commands, guides, hooks, mcp, memory, research, scripts, state, templates

---

## Tasks

### Task 1: Inventory Current Files

List all files and folders in `.claude` with:
- Filename
- Last modified date
- Size
- Brief description of contents/purpose

### Task 2: Assess Relevance

For each file/folder, categorize as:

| Category | Meaning | Action |
|----------|---------|--------|
| **KEEP** | Still relevant, actively used | Leave in place |
| **UPDATE** | Needed but outdated | Revise contents |
| **ARCHIVE** | Historical, no longer needed | Move to `.claude/archive/` |
| **DELETE** | Redundant or broken | Remove |

**Assessment criteria:**
- Does this support one of the five use cases (reports, dev, sales, marketing, tracking)?
- Is the information current?
- Does it conflict with other files?
- Is it referenced by CLAUDE.md or other active files?

### Task 3: Review CLAUDE.md

Read `CLAUDE.md` and assess:
1. Does it reflect the current pipeline (01-08 scripts + enrichment)?
2. Does it reference the Foundation Scraper skill?
3. Are agent definitions current?
4. Is there outdated information that could confuse execution?

**Deliverable:** List of specific updates needed for CLAUDE.md

### Task 4: Review Agent Definitions

Check `agents/` folder and `SIMPLIFIED_AGENT_TEAM_v2` file:
1. Which agents are needed for each use case?
2. Are there redundant agents that could be merged?
3. Are any agents missing (e.g., Writer for marketing)?
4. Are agent instructions aligned with current workflows?

**Proposed agent coverage:**

| Use Case | Agents Needed |
|----------|---------------|
| Report Generation | Scout, Builder, Reviewer |
| Software Dev | Builder, Data Engineer, Reviewer |
| Sales Support (Nonprofits) | Scout, Analyst |
| Marketing | Writer (new?), Reviewer |
| Progress Tracking | Reporter |
| Client Feedback | Analyst, Reporter |
| B2B Sales (Foundation Mgmt) | Scout, Analyst |
| Operations Tracking | Reporter |

**Deliverable:** Recommended agent structure covering all use cases, noting any gaps

### Task 5: Recommendations Summary

Provide a summary table:

| File/Folder | Current State | Recommendation | Reason |
|-------------|---------------|----------------|--------|
| CLAUDE.md | Dec 31 | UPDATE | Add enrichment workflow |
| SESSION_STATUS.md | Nov 27 | ARCHIVE | Stale |
| ... | ... | ... | ... |

---

## Constraints

- **Do not make changes yet** - Show recommendations first and get approval
- **Preserve history** - Archive rather than delete when uncertain
- **Support all use cases** - Don't over-optimize for one use case at expense of others
- **Keep it lean** - Fewer, clearer files are better than many overlapping ones

---

## Context: All Use Cases

### Use Case 1: Report Generation

```
1. Load client profile (01_load_client.py)
   - Includes specific_ask_text and grant_type_preference

2. Score foundations (02_score_foundations.py)
   - Returns top 20 matched foundations

3. Check enrichment cache (03_check_enrichment.py)
   - Identifies which foundations need research

4. Research foundations [SKILL: Foundation Scraper]
   - Scrape websites for enrichment data
   - Store in database via 03b_store_enrichment.py

5. Filter by viability (04_filter_viable.py)
   - Apply viability tiers (READY/CONDITIONAL/WATCH/SKIP)

6. Assemble opportunities (05_assemble_opportunities.py)
7. Generate narratives (06_generate_narratives.py)
8. Build report data (07_build_report_data.py)
9. Render report (08_render_report.py)
10. Convert to DOCX (09_convert_to_docx.py)
```

### Use Case 2: Software Development

- Improving matching algorithms
- Database schema changes
- Pipeline script updates
- Bug fixes
- New feature development

**Key agents:** Builder, Data Engineer, Reviewer

### Use Case 3: Sales Support

- Prospect research (enriching nonprofit leads)
- Foundation research for B2B outreach
- Call prep briefs
- Follow-up tracking

**Key agents:** Scout, Analyst

### Use Case 4: Marketing

- LinkedIn posts (aim for 3x/week)
- Website copy updates
- Email sequences
- Case studies from client feedback

**Key agents:** Writer (may need to define)

### Use Case 5: Progress Tracking

- Session summaries
- Weekly progress reports
- Goal tracking
- Time logging

**Key agents:** Reporter

### Use Case 6: Client Feedback & Iteration

- Process feedback from beta calls
- Update client profiles based on learnings
- Track which report formats work for which client types
- Identify product improvements from feedback patterns

**Key agents:** Analyst, Reporter

### Use Case 7: B2B Sales (Foundation Management Companies)

- Research foundation management companies (Whittier Trust, etc.)
- Prep for calls with contacts like Jesse Ostroff
- Different value prop than nonprofit sales
- Track B2B pipeline separately

**Key agents:** Scout, Analyst

### Use Case 8: Operations Tracking

- Client onboarding status
- Payment tracking
- Report delivery schedule
- Monthly capacity planning (20 reports/month target)

**Key agents:** Reporter

---

## Output Format

After completing the audit, provide:

1. **Summary table** of all files with recommendations
2. **Specific changes** needed for CLAUDE.md (bullet points)
3. **Agent structure** recommendation (which to keep/update/remove)
4. **Proposed folder structure** for cleaned-up `.claude`

---

## After Approval

Once recommendations are approved:

1. Create `.claude/archive/` folder
2. Move archived files
3. Update CLAUDE.md with approved changes
4. Update agent definitions if needed
5. Verify no broken references

---

*Prompt prepared 2025-01-02. Run after current report generation completes.*
