# SESSION STATE: VetsBoats Report Review SOP & Execution - 2026-02-06

**Last Updated:** 2026-02-06
**Purpose:** Preserve context for the Report Review SOP creation and its first execution against VetsBoats
**Status:** Review Complete — Report Needs Revisions

---

## CURRENT STATUS - WHERE WE ARE

### Current Step
The VetsBoats report **failed review** (70.66/100, 1 CRITICAL error, 3 hard gate failures). The next session should:

1. **Fix the report** at `5. Runs/VetsBoats/2026-02-06/REPORT_2026-02-06_vetsboats_grant_report.md` using the error list in `REPORT_2026-02-06.3_vetsboats_report_review.md`
2. **Re-run the review SOP** after fixes to verify PASS

### Remaining Steps
1. **Fix CRITICAL + HIGH errors** in the VetsBoats report (see priority list below)
2. **Re-run review SOP** against corrected report — target score >= 90 with 0 CRITICAL
3. **Regenerate .docx** from corrected markdown
4. **Investigate systemic issue**: All 5 giving trends and 4 repeat rates were wrong — suggests report generation pipeline is not pulling from `calc_foundation_profiles` for these fields

---

## What's Done

### SOP Creation
- Created `.claude/SOP_report_review.md` — 44-test, 5-gate, 4-agent review protocol (v1.0)
- Added cross-reference to `.claude/SOP_report_generation.md` Phase 5
- SOP includes: Error Taxonomy (C/H/M/L), Agent Architecture, 5 Gate definitions, Hard Gate Thresholds, Scoring System, Error Resolution Workflow, Review Report Template, SQL Query Library (11 queries)

### Review Execution
- Ran full review against VetsBoats report using 3 parallel agents (Gates 1, 2, 4) + manual analysis (Gates 3, 5)
- Produced review report: `5. Runs/VetsBoats/2026-02-06/REPORT_2026-02-06.3_vetsboats_report_review.md`
- **Verdict: FAIL (70.66/100)** — 30/44 tests passed, 14 failed

### Foundation Research (Prior Session — Context Carried Over)
- 9 foundation research agents completed (Herzstein, Enterprise Holdings, Kovler, Bill Simpson, Jim Moran, Harry Cameron, 1687 Foundation, Dr P Phillips, Diebold)
- VetsBoats report built and delivered as draft

## What's Partially Done
- **VetsBoats report corrections** — errors identified but not yet fixed
- **Pipeline investigation** — trend/repeat-rate data mismatch identified but root cause not diagnosed

## What's Not Started
- Fix all errors in VetsBoats report
- Re-run review SOP post-fix
- Regenerate .docx
- Root cause analysis of trend/repeat-rate systemic errors

---

## Decisions Made

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| 44 tests across 5 gates (expanded from plan's 28) | Stick with 28 | Each gate naturally had 7-10 specific tests; 44 provides comprehensive coverage |
| 4 agents: 3 parallel (Gates 1/2/4) + 1 sequential (Gates 3/5) | All sequential; all parallel | Gate 3 (Internal Consistency) needs verified facts from Gates 1+4 before cross-referencing |
| Weighted scoring: DI 35%, CW 25%, IC 20%, CF 15%, FC 5% | Equal weights | Data Integrity is most impactful on client trust; Formatting is least |
| Hard gate minimums: 3 emails, 3 phones, 3 names, 0 CRITICAL | Higher/lower thresholds | 3 of 5 = majority of foundations have actionable contacts; 0 CRITICAL is absolute |
| DI-10 severity = M-03 per SOP definition | Agent elevated some to C-02 | SOP specifically defines trend direction mismatch as MEDIUM; consistent application matters |
| Van Beuren NOT actually preselected-only | Trust 990-PF flag | Website shows open application portal at vbcfoundation.org — real-world practice overrides form filing |

---

## What Was Tried (Failed Approaches)

| Approach | Why It Failed | Lesson |
|----------|--------------|--------|
| MCP postgres tool for multi-query research | Enters "aborted" transaction state after any error — all subsequent queries fail | Use `PGPASSWORD=kmalec21 psql -h localhost -p 5432 -U postgres -d thegrantscout` via Bash instead |
| SQL comments in MCP queries | "Only SELECT queries" error | MCP tool treats `--` comments as non-SELECT |
| Trusting 990-PF `only_contri_to_preselected_ind` at face value | Van Beuren marks TRUE but accepts applications on their website | Always verify with web research — 990-PF flags can be wrong or outdated |

---

## Files Modified (Uncommitted)

| File | Status | Description |
|------|--------|-------------|
| `.claude/SOP_report_review.md` | **New** | Full 44-test review SOP for agent teams |
| `.claude/SOP_report_generation.md` | Modified | Added cross-reference to review SOP in Phase 5 |
| `5. Runs/VetsBoats/2026-02-06/REPORT_2026-02-06.3_vetsboats_report_review.md` | **New** | Review results: FAIL 70.66/100 |

---

## Reports Created

| File | Description |
|------|-------------|
| `.claude/SOP_report_review.md` | Review SOP v1.0 — 14 sections, 44 tests, 5 gates, 4-agent architecture |
| `5. Runs/VetsBoats/2026-02-06/REPORT_2026-02-06.3_vetsboats_report_review.md` | VetsBoats review: FAIL, 1 CRITICAL, 8 HIGH, 14 MEDIUM, 1 LOW error |

---

## Key Errors to Fix (Priority Order)

### CRITICAL (Must fix — automatic FAIL)
1. **Barry: Veterans Consortium $160K/$320K contradiction** — Line 446 says $160K, line 453 says $320K. DB confirms $320K. Fix line 446.

### HIGH (Must fix before delivery)
2. **Barry: Sail to Prevail $200K is fabricated** — DB max is $50K (2022). 4x overstatement. Fix all instances.
3. **Barry: Puppies Behind Bars $100K** — DB shows $75K. Fix to $75K.
4. **Van Beuren: Reclassify from "Cultivation" to "Open Application"** — Has website (vbcfoundation.org), application portal (apply.yourcausegrants.com), deadlines (Feb/Jul). February deadline is imminent.
5. **Van Beuren: Annual giving $8.9M/136 wrong** — DB shows ~$10.7M/163.
6. **Kovler: Zero sector alignment** — Consider replacing with better-aligned foundation.
7. **Bill Simpson: Zero purpose_text keyword matches** — Tangential CRAB match only. Strengthen justification.
8. **Only 2 of 5 match primary priority** — Need >= 3. Fixing Van Beuren helps.
9. **Add verified emails** — Only 2, need >= 3. Check vbcfoundation.org for staff emails.
10. **Add verified phones** — Only 1, need >= 3.

### MEDIUM (Fix if time permits)
11. **All 5 giving trends wrong** — Pull from `calc_foundation_profiles.giving_trend`
12. **4 of 5 repeat rates inflated** — Pull from `calc_foundation_profiles.repeat_rate`
13. **Van Beuren geographic 85% RI vs DB 50%** — Major overstatement
14. Various minor formatting/consistency issues

---

## Database Queries That Worked

```sql
-- Verify specific grant amounts for a foundation
SELECT foundation_ein, recipient_name_raw, amount, tax_year, purpose_text
FROM f990_2025.fact_grants
WHERE foundation_ein = '461550110'
  AND recipient_name_raw ILIKE '%sail to prevail%'
ORDER BY tax_year DESC;

-- Get foundation profile metrics (repeat rate, trend, geographic focus)
SELECT ein, repeat_rate, giving_trend, trend_pct_change, geographic_focus
FROM f990_2025.calc_foundation_profiles
WHERE ein IN ('843992087', '746070484', '366152744', '461550110', '222773769');

-- Check preselected-only status across all filing years
SELECT ein, business_name, only_contri_to_preselected_ind, tax_year
FROM f990_2025.pf_returns
WHERE ein = '222773769'
ORDER BY tax_year DESC;

-- Sector keyword alignment check
SELECT foundation_ein,
  SUM(CASE WHEN purpose_text ILIKE '%veteran%' OR purpose_text ILIKE '%military%' THEN 1 ELSE 0 END) as veteran_military,
  SUM(CASE WHEN purpose_text ILIKE '%sail%' OR purpose_text ILIKE '%boat%' THEN 1 ELSE 0 END) as sailing_boat
FROM f990_2025.fact_grants
WHERE foundation_ein IN ('843992087','746070484','366152744','461550110','222773769')
GROUP BY foundation_ein;

-- Check known funders overlap
SELECT known_funders FROM f990_2025.dim_clients WHERE name ILIKE '%vetsboats%';
```

---

## Key Data Findings

### VetsBoats Foundation EINs (for report)
| Foundation | EIN |
|-----------|-----|
| Bill Simpson Foundation | 843992087 |
| Albert & Ethel Herzstein | 746070484 |
| Kovler Family Foundation | 366152744 |
| John & Daria Barry Foundation | 461550110 |
| Van Beuren Charitable Foundation | 222773769 |

### Client: VetsBoats
- EIN: 464194065
- Client ID: 8 in dim_clients
- State: CA
- Known funders (5): 943073894, 946073084, 956495222, 946077619, 133556721
- Private foundation (990-PF filer) — #1 eligibility risk

### Systemic Pipeline Issue
- **All 5 giving trends are wrong** in the report. The report generation process appears to NOT pull from `calc_foundation_profiles.giving_trend`. Instead, trends appear to be AI-generated/hallucinated during narrative writing.
- **4 of 5 repeat rates are inflated** (7-20 percentage points above `calc_foundation_profiles.repeat_rate`). Same likely cause — generated rather than queried.
- **Root cause hypothesis:** The report generation pipeline (scripts 05-08) may not pass `calc_foundation_profiles` data through to the narrative generation step, forcing the LLM to estimate/hallucinate these statistics.

### Van Beuren Discovery
- 990-PF says `only_contri_to_preselected_ind = TRUE` across all years
- But vbcfoundation.org has a full grants section, online application portal, and published deadlines
- This means the 990-PF flag is UNRELIABLE for this foundation — web verification is essential
- **Lesson for pipeline:** Always cross-check preselected-only with web presence before classifying as "cultivation"

---

## Blockers (if any)

| Blocker | Severity | Workaround |
|---------|----------|------------|
| Trend/repeat-rate data not flowing from calc_foundation_profiles to report | HIGH | Manually correct from DB for now; diagnose pipeline root cause later |
| MCP postgres tool transaction abort issue | MED | Use psql via Bash with PGPASSWORD |
| Kovler has zero sector alignment | MED | Consider replacing with a better-aligned foundation from the scored pipeline |

---

*Generated by Claude Code on 2026-02-06*
