# PROMPT: Build Client Viability Check Skill

**Date:** 2026-02-20
**Prompt Number:** 4
**Type:** Skill Development

---

## Situation

We just ran a viability assessment for Proclaim Aviation (PROMPT/REPORT_2026-02-20.3). It worked but was massively overbuilt — 7 dimensions, weighted scorecard, 400-line report. The core question is simple: **"Does our database have enough foundation matches to deliver useful monthly reports for this nonprofit?"** We don't need to assess grant capacity, accreditation, peer benchmarks, or do actual matching. We just need to check if the pool is big enough.

We want to extract the useful parts into a reusable skill file that Claude Code can run in 5-10 minutes for any incoming prospect.

## Reference Files

- `Enhancements/2026-02-20/REPORT_2026-02-20.3_proclaim_aviation_viability_assessment.md` — the overbuilt assessment (study what queries were useful vs. overkill)
- `Enhancements/2026-02-20/PROMPT_2026-02-20.3_proclaim_aviation_viability_assessment.md` — the original prompt
- `/mnt/skills/` — review existing SKILL.md files for format conventions

## Tasks

### Task 1: Research (do NOT write anything yet)
- Read the Proclaim report and identify which queries/dimensions actually answered the core viability question vs. which were nice-to-know extras
- Review 2-3 SKILL.md files in /mnt/skills/ to understand the expected format and structure
- Check the f990_2025 schema for the key tables/columns the queries would need

### Task 2: Draft Proposed Skill Design
Write `REPORT_2026-02-20_4_viability_skill_proposal.md` containing:
- Which dimensions from the Proclaim assessment to KEEP vs. CUT
- The 3 core checks the skill should perform:
  1. **Eligible Foundation Pool Size** — foundations matching sector + geography + accepts_applications + minimum assets/grant history
  2. **Sibling Funder Signals** — orgs doing similar work and how many production-ready funders they have
  3. **Monthly Report Sustainability** — can we deliver 5 fresh opportunities/month for 12 months without running dry?
- Proposed thresholds (e.g., 50+ = GO, 20-49 = CONDITIONAL, <20 = NO GO)
- Parameterized SQL templates for each check (inputs: EIN, NTEE code, state, annual revenue)
- The proposed SKILL.md content

### Task 3: STOP and present the proposal for my review
- Do NOT create the final skill file yet
- Show me the proposal and wait for approval/feedback

### Task 4: After approval, create the skill file
- Write the final `SKILL.md` to the agreed location
- Include clear instructions, SQL templates, input/output spec, and thresholds

## Expected Outputs

| File | Naming | Description |
|------|--------|-------------|
| Research + Proposal | `REPORT_2026-02-20_4_viability_skill_proposal.md` | Analysis of what to keep/cut + full skill draft |
| Final Skill (after approval) | `SKILL.md` in appropriate skills directory | The reusable viability check skill |

## Key Constraints

- The skill should take 5-10 minutes to run, not 30+
- Inputs: EIN, NTEE code, state, annual revenue (all available before a sales call)
- Output: GO / CONDITIONAL / NO GO with pool size numbers and a 1-paragraph summary
- No weighted scorecards, no peer benchmarks, no grant capacity assessment
- Use f990_2025 schema exclusively
- Production filters: has_grant_history, assets >= $100K, unique_recipients >= 5, accepts_applications = TRUE
- Auto-filter corporate matching programs from co-funder/sibling results

---

*Prompt by Aleck Kleinman, 2026-02-20*
