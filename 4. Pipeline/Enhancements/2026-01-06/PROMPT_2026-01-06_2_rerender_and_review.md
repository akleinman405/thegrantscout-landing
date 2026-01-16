# PROMPT_2026-01-06_2: Re-Render Reports and Manual Review

**Date:** 2026-01-06
**Priority:** High - blocking client delivery

---

## Situation

The build plan (BUILD_PLAN_2026-01-06_v2) has been implemented:
- Narrative merge bug fixed in `07_build_report_data.py`
- Pool expanded to 500
- Curated snapshot script created (`02b_add_foundation.py`)
- Exclusion list support added
- Enrichment tracking template created

The 5 client reports (PSMF, RHF, SNS, HN, FCSD) were generated before the narrative merge fix. They currently have empty/generic narrative text and need to be re-rendered.

---

## Tasks

### Task 1: Re-Render All 5 Reports

For each client (PSMF, RHF, SNS, HN, FCSD):

```bash
python scripts/07_build_report_data.py --client "{CLIENT}"
python scripts/08_render_report.py --client "{CLIENT}"
python scripts/09_convert_to_docx.py --client "{CLIENT}"
```

Confirm narrative merge is working by checking console output shows successful merges (not 0).

---

### Task 2: Manual Review Each Report

Review each rendered report against these criteria:

**A. Geographic Fit**
- Do the foundations fund the client's actual location?
- Flag any mismatches (e.g., San Diego client getting Northern California foundations)

**B. Goal Alignment**
- Does the client have specific goals (grant type, project focus, funding amount)?
- Do the recommended foundations match those goals?
- For multi-priority clients (FCSD: bakery + building), are both priorities addressed?

**C. Known Funder Check**
- Based on questionnaire responses, would the client likely already know about these foundations?
- Flag any "obvious" matches that provide no discovery value

**D. Narrative Quality**
- Did narratives render (not empty)?
- Are "Why This Fits" sections specific to the client, not generic?
- Do "Next Steps" include actionable information (deadlines, contacts, application process)?

**E. Foundation Viability**
- Are all foundations open to applications (not invitation-only)?
- Do grant sizes match client capacity?

---

### Task 3: Report Findings

Create `REPORT_2026-01-06_3_report_review_findings.md` with:

**Per-client summary table:**
| Client | Narratives Rendered? | Geographic Fit | Goal Alignment | Discovery Value | Ready to Send? |
|--------|---------------------|----------------|----------------|-----------------|----------------|
| PSMF | Yes/No | Good/Issues | Good/Issues | Good/Issues | Yes/No |
| ... | | | | | |

**For each client with issues:**
- What's wrong
- Specific foundations to swap out (if any)
- What would fix it

**Overall assessment:**
- How many reports are ready to send as-is?
- How many need fixes?
- What fixes are needed?

---

## Outputs

1. Re-rendered reports for all 5 clients (steps 07-09)
2. `REPORT_2026-01-06_3_report_review_findings.md` with review results
3. Clear recommendation: which reports are ready, which need work

---

## Notes

- Previous QA scored these reports 5.6/10 average alignment
- Known issues from previous review:
  - FCSD: Geographic mismatch (San Diego vs Aptos)
  - HN: National org got CT-only foundations
  - RHF: Initially got 0 opportunities (fixed with curated foundations)
- Focus on "is this ready to send to a paying client?" not perfection

---

*Created 2026-01-06*
