# SESSION STATE: PSMF Funder Research - 2026-01-16

**Last Updated:** 2026-01-16 (pre-autocompact)
**Purpose:** Preserve context across compactions for PSMF foundation search

---

## CURRENT STATUS - WHERE WE ARE

### Guide Location: **Phase 3.5 → Phase 4 Transition (Modified Approach)**

The original pipeline (sibling-based matching) FAILED for PSMF because their "siblings" don't receive foundation grants. We **pivoted to relationship-building approach**.

### Current Step: **Building Final 5-Foundation Report**

We selected 5 foundations and stored them in the database:
```sql
-- Table: f990_2025.calc_client_foundation_recommendations
-- Client EIN: 462730379 (PSMF)
-- 5 foundations inserted with ranks 1-5
```

| Rank | Foundation | EIN | Type | Status |
|------|------------|-----|------|--------|
| 1 | Josiah Macy Jr. | 135596895 | LOI-Ready | Open - Rolling |
| 2 | Commonwealth Fund | 131635260 | LOI-Ready | Open - Rolling |
| 3 | W.K. Kellogg | 381359264 | LOI-Ready | Open - Rolling |
| 4 | John A. Hartford | 131667057 | Cultivation | Invite-only |
| 5 | Schooner Foundation | 043347626 | Cultivation | Invite-only |

### Next Step: Calculate Funder Snapshot Metrics
Query was interrupted. Need to run:
- Annual Giving (total $ and grant count)
- Typical Grant (median, min, max)
- Geographic Focus
- Repeat Funding Rate
- Giving Style
- Funding Trend

### Remaining Steps (from todo list):
1. ✅ Select 5 foundations - DONE
2. ⏳ Calculate Funder Snapshot metrics - IN PROGRESS
3. ⏳ Research detailed contacts
4. ⏳ Document application process details
5. ⏳ Write positioning strategies
6. ⏳ Create action plans
7. ⏳ Assemble final report using template

---

## ORIGINAL PROBLEM (Why We Pivoted)

PSMF is "structurally unique" - their peers (state PSOs) don't rely on foundation grants, so sibling-based matching failed. Solution: Match on PROGRAM TYPE (fellowship) not CAUSE AREA (patient safety).

---

## KEY PSMF FACTS

| Field | Value |
|-------|-------|
| **EIN** | 462730379 |
| **Name** | Patient Safety Movement Foundation |
| **Location** | Irvine, California |
| **Founded** | 2012 by Joe Kiani (Masimo CEO) |
| **Budget** | ~$1M+ |
| **Tax Status** | 501(c)(3) |

### Priority Program: Kiani Fellowship
- 12-month global health professional training program
- Virtual monthly sessions
- Trains healthcare professionals from 48+ countries
- Focus on patient safety leadership
- Fellows from Argentina, Sudan, Lebanon, Uganda, Pakistan, Indonesia, Kenya, Malaysia, Australia, etc.

### The Challenge
PSMF's **global scope** conflicts with most US foundations' **US-only** restrictions.

---

## EXISTING FUNDERS (Already Funded PSMF - Exclude)

| Foundation | EIN | Amount | Year |
|------------|-----|--------|------|
| Masimo Foundation for Ethics | 010956020 | $1,000,000 | 2020 |
| Nima Taghavi Foundation | 203959759 | $50,000 | 2021 |

---

## KEY FINDING: Most Foundations Are Invite-Only

### Open to Applications
| Foundation | Status | Issue |
|------------|--------|-------|
| **Josiah Macy Jr.** | ✅ Rolling (President's Grants up to $25K) | US activities only |
| **Brinson Foundation** | ✅ LOI anytime | Healthcare Career Development |
| **Pfizer Foundation** | ✅ RFP-based | Must wait for relevant RFP |
| **Doctors Company** | ⏸️ PAUSED until mid-2026 | US projects only |

### Invite-Only (Cannot Apply)
- Skoll Foundation
- Rockefeller Foundation
- Ford Foundation
- MacArthur Foundation
- McGovern Foundation
- Schooner Foundation
- John A. Hartford Foundation

---

## REPORTS CREATED TODAY

1. `REPORT_2026-01-16.1_psmf_agent_analysis_and_plan.md` - 4-agent analysis of approach
2. `REPORT_2026-01-16.2_psmf_foundation_eligibility_assessment.md` - Eligibility research on 5 foundations
3. `REPORT_2026-01-16.3_psmf_database_search_eligible_foundations.md` - Database search for fellowship funders
4. `REPORT_2026-01-16.4_psmf_global_funders_search.md` - Global funder search
5. `REPORT_2026-01-16.5_psmf_funder_strategy_synthesis.md` - Final strategy synthesis
6. `DRAFT_2026-01-16_macy_application_concept.md` - Macy President's Grant application concept
7. `REPORT_2026-01-16.6_psmf_relationship_building_funders.md` - 5-funder relationship strategy
8. `REPORT_2026-01-16.7_psmf_15_funders_relationship_building.md` - 15-funder relationship strategy
9. `REPORT_2026-01-16.8_psmf_15_funders_eligibility_verification.md` - Eligibility verification (12 invite-only, 3 open)

## DATABASE CHANGES MADE

1. Created table: `f990_2025.calc_client_foundation_recommendations`
2. Inserted 5 foundation records for PSMF (client_ein = '462730379')

---

## COMPLETED ACTIONS (2026-01-16)

1. ✅ **Drafted Macy application concept** - President's Grant ($25K), framed as US-based curriculum development
2. ✅ **Researched introduction paths** to invite-only funders (IHI → Hartford, Partners in Health → Skoll)
3. ✅ **Agent brainstorm completed** - Corporate foundations, unconventional approaches, network leverage
4. ✅ **Final strategy synthesis** - 5 recommended foundations with multi-path approach

## NEXT ACTIONS FOR PSMF

1. **Review Macy application concept** - Internal approval needed
2. **Identify pilot partner schools** - 2-3 US health professions schools for curriculum pilot
3. **Submit Brinson Foundation LOI** - Healthcare Career Development framing
4. **Verify Masimo Foundation relationship** - Renewal? Introductions?

---

## KEY STRATEGIC INSIGHTS

1. **Match on PROGRAM TYPE, not CAUSE AREA** - Fellowship funders, not patient safety funders
2. **PSMF is "structurally unique"** - Global education platform, not typical patient safety org
3. **Two paths:**
   - Near-term: Apply to US-focused foundations with US-framed projects
   - Long-term: Build relationships with global foundations

---

## DATABASE QUERIES THAT WORKED

```sql
-- Find foundations funding global health education
SELECT foundation_ein, name, COUNT(*) as grants
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_foundations df ON fg.foundation_ein = df.ein
WHERE (LOWER(purpose_text) LIKE '%global%' OR LOWER(purpose_text) LIKE '%international%')
AND (LOWER(purpose_text) LIKE '%health%' OR LOWER(purpose_text) LIKE '%training%')
AND amount BETWEEN 50000 AND 1000000
AND tax_year >= 2020
GROUP BY foundation_ein, name
ORDER BY COUNT(*) DESC;

-- Find who funded IHI (PSMF's "cousin")
SELECT foundation_ein, name, amount, purpose_text
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_foundations df ON fg.foundation_ein = df.ein
WHERE LOWER(recipient_name_raw) LIKE '%institute for healthcare improvement%'
AND amount >= 50000;
```

---

## FILES IN THIS FOLDER

```
4. Pipeline/Enhancements/2026-01-13/
├── GUIDE_2026-01-13_PSMF_report_step_by_step.md
├── PSMF_organization_profile.md
├── PSMF_verified_siblings_v2.md
├── PROCESS_sibling_identification.md
├── REPORT_2026-01-13.1_psmf_build_log.md
├── REPORT_2026-01-13.2_sibling_quality_improvement.md
├── REPORT_2026-01-13.3_psmf_foundation_prospects.md
├── REPORT_2026-01-13.4_grant_matching_methodology.md
├── REPORT_2026-01-13.5_strategic_funder_discovery.md
├── REPORT_2026-01-16.1_psmf_agent_analysis_and_plan.md
├── REPORT_2026-01-16.2_psmf_foundation_eligibility_assessment.md
├── REPORT_2026-01-16.3_psmf_database_search_eligible_foundations.md
├── REPORT_2026-01-16.4_psmf_global_funders_search.md
├── SESSION_STATE_psmf_report.md (older session state)
└── SESSION_STATE_2026-01-16_psmf_funders.md (THIS FILE)
```

---

*Last updated: 2026-01-16*
