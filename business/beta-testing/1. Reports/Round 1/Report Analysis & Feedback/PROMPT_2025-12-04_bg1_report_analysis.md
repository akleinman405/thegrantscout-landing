# Research Team Prompt: BG1 Report Analysis & Example Report Creation

**Date:** December 4, 2025

---

## File Paths

**BG1 Reports :**
```
"C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\Research Team Finds Opportunities\Week1 Beta Reports\Final Reports (WORD)"
```

**Report Template Info:**
```
C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\Research Team Finds Opportunities\Week2 Beta Reports\Report Templates
```

**Database Access Info:**
```
C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\Postgresql Info.txt
```

**Output Folder:**
```
C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\Research Team Finds Opportunities\Week1 Beta Reports\Report Analysis & Feedback
```

---

## Objective

Review all 5 Beta Group 1 reports, analyze strengths and weaknesses against our report framework, select the strongest candidate(for an example, not necessarily for the intended nonprofit(ex psmf)), and produce a fully polished example report ready for the website and to send to hot leads as an example.

---

## Inputs

**Reports to review:**
1. PSMF (Patient Safety Movement Foundation)
2. RHF (Retirement Housing Foundation)
3. SNS (Senior Network Services)
4. Ka Ulukoa
5. ACA (Arborbrook Christian Academy)

**Framework documents:**
- `REPORT_SECTION_DEFINITIONS.md`
- `WEEKLY_REPORT_TEMPLATE.md`

**Feedback received:**
- SNS: Errors found (wrong grant name, expired deadline, broken link)
- RHF: Andy said info was organized but he already knew about the opportunities
- PSMF: Wants foundation-focused reports, not opportunity-focused

---

## Task 1: Report Analysis

For each of the 5 reports, evaluate against the framework and answer:

**Strengths:**
- Which sections are well-executed?
- What formatting/structure works well?
- Which opportunities are well-researched?

**Weaknesses:**
- What sections are missing or incomplete vs. the template?
- Where is data thin or unverified?
- What positioning advice is generic vs. data-backed?

**Specific issues:**
- Are Funder Snapshots complete (all 8 metrics)?
- Are positioning strategies tied to specific data points?
- Are deadlines verified and current?
- Are comparable grants real and sourced?

---

## Task 2: Ranking & Selection

Rank all 5 reports from strongest to weakest. Select the strongest candidate for the example report based on:
- Completeness
- Data quality
- Opportunity diversity (mix of federal, foundation, deadline urgency)
- Presentation quality

Provide 2-3 sentence justification for your selection.

---

## Task 3: Create Polished Example Report

Take the selected report and upgrade it to a fully polished example report. ---*****USE THE TEMPLATE(path given at top of this prompt)*****

**Requirements:**
- Include ALL 5 opportunities (do not drop any)
- Every opportunity must have the complete structure from the template:
  - Why This Fits (3-4 sentences)
  - Key Details table
  - Funder Snapshot (all 8 metrics, data-backed)
  - Potential Connections
  - Application Requirements
  - Positioning Strategy (must reference Funder Snapshot data)
  - Next Steps table
- Executive Summary fully populated
- 8-Week Timeline complete
- Quick Reference section complete
- Ensure positioning advice is specific, not generic

**Use multiple research agents as necessary to:**
- Look up current deadline status for each opportunity
- Verify funder contact information
- Find comparable grants from the database
- Calculate Funder Snapshot metrics from F990 data
- Research any missing application requirements
- Verify board/officer information for connections

---

## CRITICAL: URL & Opportunity Verification

**All URLs must be manually tested before including in the final example report.**

For every URL in the report:
1. Visit the URL
2. Confirm it loads correctly (no 404s, no redirects to dead pages)
3. Confirm it points to the correct page (grant program, application portal, etc.)
4. If a URL is broken, find the correct current URL or remove the opportunity

**All opportunities must be current and open.**

For every opportunity in the final example report:
1. Verify the deadline has NOT passed
2. Verify the grant program is still active and accepting applications
3. Verify funding amounts are still accurate
4. If an opportunity is expired or closed, replace it with a current opportunity in the same category

**Document your verification:**
- Create a URL verification log showing each URL tested and result
- Note any opportunities that were replaced and why

---

## Outputs

**Output 1: Analysis Document**
- 1-2 page summary
- Table ranking all 5 reports with scores
- Bullet lists of common strengths and weaknesses
- Justification for selected report

**Output 2: URL Verification Log**
- Table of all URLs tested
- Status (Working / Broken / Replaced)
- Notes on any issues found

**Output 3: Polished Example Report**
- Full report following WEEKLY_REPORT_TEMPLATE.md exactly
- All 5 opportunities fully fleshed out
- ALL URLs verified working
- ALL opportunities verified current and open
- 10-15 pages target length
- Ready for website use (may need anonymization afterward)

Save all outputs to the Output Folder specified above.

---

## Quality Checklist (from REPORT_SECTION_DEFINITIONS.md)

Before finalizing the example report, verify:

- [ ] All 5 opportunities are currently accepting applications (VERIFIED - not assumed)
- [ ] All URLs manually tested and working
- [ ] Deadlines are accurate and verified (not past)
- [ ] Funding amounts match current program guidelines
- [ ] Funder Snapshot metrics are calculated from actual database queries
- [ ] Comparable grants are real (verify org name and amount exist in database)
- [ ] Positioning strategy references specific Funder Snapshot data points
- [ ] Contact information is current (verify emails/URLs work)
- [ ] No "About [Org]" section—client knows their own organization
- [ ] Timeline is realistic given stated deadlines
- [ ] Total report length is 10-15 pages

---

## Deadline

Complete analysis and polished example report ASAP for website launch.

---

*Note: If the selected report needs significant additions, prioritize quality over speed. The example report will be used to sell the service—it must be excellent. Broken URLs or expired opportunities will immediately undermine credibility.*
