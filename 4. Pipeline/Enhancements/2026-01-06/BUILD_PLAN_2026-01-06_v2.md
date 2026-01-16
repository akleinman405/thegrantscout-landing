# Build Plan: Pipeline Improvements for Next Report Batch

**Date:** 2026-01-06
**Status:** Draft - Requesting Agent Team Feedback

---

## Goal

For each client, find foundations that:
1. Are likely to fund them (based on giving patterns, geography, sector)
2. Have a history of grants matching the client's specific goals (grant type, location, project focus)
3. Client doesn't already know about (ask them upfront)

Then gather all helpful info on those foundations for the report.

---

## Current Process

1. Client fills questionnaire (org info, goals, priorities)
2. Algorithm scores 12K foundations → outputs top 100
3. Generate snapshots (grant history, giving patterns)
4. Manual enrichment (websites, deadlines, contacts) - 2-4 hours
5. Filter to viable foundations
6. Assemble opportunities
7. Generate narratives
8. Render report

---

## What We Learned from Recent Reports

**5 clients processed (PSMF, RHF, SNS, HN, FCSD). Key issues:**

| Issue | Impact |
|-------|--------|
| No exclusion list | Surfaced foundations client already knew |
| Top 100 too narrow | Can't filter by specific goals without re-running |
| Curated foundations had no snapshots | Manual research got filtered out - RHF got 0 opportunities initially |
| Narratives didn't merge into report | Reports rendered with generic text |
| All enrichment manual | 2-4 hours per client |

---

## What to Build for Next Batch

### 1. Add Exclusion List to Questionnaire
Ask: "Which foundations have you applied to, received grants from, or are currently tracking?"

Exclude these from results.

**Effort:** 1 hour

---

### 2. Expand Scored Pool to 500
Currently outputs top 100. Expand to 500 so we can manually filter by client goals without re-running the algorithm.

**Effort:** 30 minutes

---

### 3. Fix Narrative Merge
`06_narratives.json` exists but never merges into `05_opportunities.json`. Reports render empty.

Create merge step so narratives actually appear in reports.

**Effort:** 2 hours

---

### 4. Curated Foundation Snapshot Script
When manual research finds good foundations not in the scored list, we need their snapshot data.

`03b_curate_foundations.py --eins "123456789,987654321"`

Generates snapshots for specific EINs so they can flow through the pipeline.

**Effort:** 3-4 hours

---

### 5. Enrichment Tracker
Log what we research manually: foundation, what we looked for, what we found, time spent.

After 20-30 foundations, patterns emerge → then automate.

**Effort:** 1 hour setup

---

## What to Track (To Inform Future Automation)

After each batch, review:

- Which goal filters did we apply most? (geography, grant type, sector, size)
- What enrichment data did we always look up? What was rarely useful?
- How often did curated foundations outperform scored ones?
- Did clients report the opportunities were new to them?
- What took the most time?

---

## Questions for Agent Team

1. **Exclusion list:** Sufficient to ask clients? Or should we also auto-pull their prior funders from 990 data?

2. **Pool size:** Is 500 right? Should we stratify differently (e.g., top 200 overall + top 100 by geography + top 100 by grant type)?

3. **Enrichment tracker:** What fields should we capture? Suggested: EIN, search goal, result, time, source URL, confidence.

4. **What are we missing?** Any obvious improvements not listed here?

5. **Risks:** What could go wrong with this approach?

---

## Timeline

**This week:** Build all 5 items

**Next 4-6 weeks:** Run 15-20 reports, track learnings

**Then:** Review patterns, decide what to automate

---

*Requesting feedback from agent team*
