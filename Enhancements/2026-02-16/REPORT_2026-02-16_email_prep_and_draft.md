# Report: Fix, Prep, and Draft 20 Nonprofit Emails

**Date:** 2026-02-16
**Prompt:** PROMPT_2026-02-16_fix_prep_draft_emails.md
**Status:** Complete
**Owner:** Claude Code

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial version |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Part A: Import Outreach History](#part-a-import-outreach-history)
3. [Part B: Database Prep](#part-b-database-prep)
4. [Part C: Draft 20 Emails](#part-c-draft-20-emails)
5. [Previous Cohort Collision Check](#previous-cohort-collision-check)
6. [Files Created/Modified](#files-createdmodified)
7. [Notes](#notes)

---

## Executive Summary

Imported 227 outreach records from Calls-2.xlsx into campaign_prospect_status. Built cohort infrastructure: 882 state+sector combos with 13,002 foundation list entries, 864 viable cohorts. Extracted contact first names for 5,606 of 6,372 emailable prospects (88%). After suppression, 4,990 prospects are ready to email. Selected and drafted 20 nonprofit emails across 16 states and 7 sectors using the give-first approach. Confirmed 4 of 10 previous foundation emails would have collided with phone contacts.

---

## Part A: Import Outreach History

### A1: Schema Changes

| Change | Result |
|--------|--------|
| Make `email` nullable | Done (was NOT NULL) |
| Add `notes` column | Done (TEXT) |
| Replace unique constraint with partial index | Done: `UNIQUE (email, vertical) WHERE email IS NOT NULL` |

### A1b-f: Import Results

| Sheet | Description | Rows Imported | Skipped (dup) |
|-------|-------------|---------------|---------------|
| Calls | Main outreach log | 129 | 6 |
| Sheet2 | Researched foundations | 6 | (overlap with Calls) |
| Sheet3 | Contact enrichment | 5 fp2 emails updated | N/A (not CPS rows) |
| Sheet4 | Contacts without email | 92 | (some overlap) |
| Sheet5 | Priority foundations | 0 | 50 (all covered by prior sheets) |
| Sheet1 | Outcome labels | SKIPPED | N/A |
| Sheet6 | EIN rank list | SKIPPED | N/A |
| **TOTAL** | | **227 added** | **80 skipped** |

### Suppress List Totals (Post-Import)

| Metric | Count |
|--------|-------|
| Cold-call records | 227 |
| Unique EINs (cold-call) | 132 |
| Unique emails (cold-call) | 66 |
| ALL campaign records | 2,063 |
| ALL unique EINs | 1,517 |
| ALL unique emails | 1,902 |

### Campaign Status Breakdown (Cold Calls)

| Status | Count |
|--------|-------|
| queued | 145 |
| contacted | 80 |
| replied | 2 |

### A2: Previous Cohort Artifacts

- `EMAILS_2026-02-16_first_cohort_CA.md` exists with 10 foundation + 10 nonprofit emails (wrong framing, superseded)
- No cohort/suppress tables existed prior to this session
- No send script was created previously

---

## Part B: Database Prep

### B1: Clean fp2 Junk Emails

**Result:** 0 rows affected (fp2 emails were already clean)

### B2: Contact First Names

| Metric | Count |
|--------|-------|
| Total emailable prospects | 6,372 |
| Real name extracted (from all_officers) | 5,550 |
| Real name extracted (from ed_ceo_name fallback) | 56 |
| Fallback to "there" | 766 |
| **Coverage rate** | **88%** |

Top 10 first names: David (86), John (76), Michael (63), James (58), Jennifer (55), Amy (51), Robert (47), Brian (44), Mark (43), Mary (42)

**Known issue:** Names stored last-name-first (e.g., "Simmons Dawn M") will extract the wrong name. One instance found and excluded from email selection (Front Porch Arts Collective, EIN 853300505).

### B3: Cohort Foundation Lists

| Metric | Value |
|--------|-------|
| Total state+sector combos | 882 |
| Total foundation list rows | 13,002 |
| Foundations per combo | Up to 15 (top 15 by 5yr giving) |
| All have accepts_applications = true | Yes |
| Example grants included | Yes (one per foundation) |

**Top 10 Cohorts by True Foundation Count:**

| State | Sector | Label | True Foundation Count |
|-------|--------|-------|---------------------|
| NY | B | Education | 2,880 |
| CA | B | Education | 2,322 |
| NY | Q | International | 2,099 |
| MA | B | Education | 1,920 |
| NY | A | Arts & Culture | 1,784 |
| NY | P | Human Services | 1,754 |
| PA | B | Education | 1,747 |
| CA | P | Human Services | 1,655 |
| TX | B | Education | 1,430 |
| CA | T | Philanthropy | 1,359 |

### 5 Sample Foundation Lists

**NY Human Services (1,754 foundations):**

| Rank | Foundation | 5yr Giving | Median Grant | Example Recipient |
|------|-----------|-----------|-------------|------------------|
| 1 | Edna McConnell Clark Foundation | $688M | $25M | Blue Meridian Partners |
| 2 | Lilly Endowment | $109M | $8K | National Urban League |
| 3 | Mother Cabrini Health Foundation | $77M | $139K | Good Shepherd Services |

**MI Human Services (588 foundations):**

| Rank | Foundation | 5yr Giving | Median Grant | Example Recipient |
|------|-----------|-----------|-------------|------------------|
| 1 | WK Kellogg Foundation | $31M | $75K | YMCA of Greater Grand Rapids |
| 2 | Julia Burke Foundation | $11M | $2M | Pope Francis Center |
| 3 | Ronda E Stryker Foundation | $11M | $55K | LIFT Foundation |

**HI Environment (111 foundations):**

| Rank | Foundation | 5yr Giving | Median Grant | Example Recipient |
|------|-----------|-----------|-------------|------------------|
| 1 | Marisla Foundation | $1.2M | $80K | National Tropical Botanical Garden |
| 2 | Schmidt Family Foundation | $1.1M | $140K | Kuaaina Ulu Auamo |
| 3 | Harold KL Castle Foundation | $946K | $30K | Hawaii Conservation Alliance |

**IL Housing (275 foundations):**

| Rank | Foundation | 5yr Giving | Median Grant | Example Recipient |
|------|-----------|-----------|-------------|------------------|
| 1 | Polk Bros Foundation | $5.7M | $55K | Center for Housing and Health |
| 2 | Arie and Ida Crown Memorial | $5.3M | $100K | Sarah's Circle |
| 3 | Bank of America Charitable | $2.5M | $250 | Resurrection Project |

**ME Human Services (207 foundations):**

| Rank | Foundation | 5yr Giving | Median Grant | Example Recipient |
|------|-----------|-----------|-------------|------------------|
| 1 | John T Gorman Foundation | $4.0M | $20K | Preble Street |
| 2 | Elmina B Sewall Foundation | $2.7M | $20K | ProsperityME |
| 3 | Maine Health Access Foundation | $2.0M | $20K | New England Arab American Org |

### B4: Cohort Viability

| Viable? | Cohorts | Prospects |
|---------|---------|-----------|
| Yes | 864 | 4,957 |
| No | 18 | 19 |

**Foundation count distribution (viable cohorts):**

| Tier | Cohorts | Prospects |
|------|---------|-----------|
| 200+ foundations | 321 | 3,684 |
| 100-199 | 228 | 769 |
| 50-99 | 163 | 295 |
| 10-49 | 152 | 209 |

### B5: Priority Scores

| Score | Count | Description |
|-------|-------|-------------|
| 8 | 7 | Maximum score |
| 7 | 19 | Very high priority |
| 6 | 1,087 | High priority |
| 5 | 2,143 | Good candidates |
| 4 | 1,458 | Moderate |
| 3 | 666 | Lower priority |
| 2 | 684 | Low |
| 1 | 300 | Minimal |
| 0 | 8 | No scoring factors |

**Scoring components:**
- +3 if cohort has 100+ foundations, +2 if 50-99, +1 if 10-49
- +2 if revenue $500K-$2M, +1 if $2M-$5M
- +2 if government funding >50%, +1 if 20-50%
- +1 if fewer than 5 existing foundation grants

### B6: Suppress Lists

| View | Records |
|------|---------|
| v_suppress_list (by email) | 1,869 unique emails |
| v_suppress_list_by_ein (by EIN) | 1,443 unique EINs |

**Suppression impact on emailable prospects:**

| Metric | Count |
|--------|-------|
| Total emailable (np2 with contact_email) | 6,372 |
| Suppressed by email match | 1,276 |
| Suppressed by EIN match | 1,349 |
| **Ready to email** | **4,990** |

**Fully qualified candidates** (ready + viable cohort + real name + NTEE): **3,428**

---

## Part C: Draft 20 Emails

### Selection Criteria Applied
- contact_email IS NOT NULL and contains @
- Not in v_suppress_list (by email)
- Not in v_suppress_list_by_ein (by EIN)
- email_cohort_viable = TRUE
- contact_first_name != 'there' (has real name)
- ntee_code IS NOT NULL
- mission_description IS NOT NULL and not "SEE SCHEDULE O"
- One prospect per state+sector combo (for diversity)
- Ordered by email_priority_score DESC, foundation_count DESC

### The 20 Selected Prospects

| # | Name | Organization | State | Sector | Score | Foundations |
|---|------|-------------|-------|--------|-------|-------------|
| 1 | Shirley | Street Corner Resources | NY | Human Services | 8 | 1,754 |
| 2 | Cynthia | Celandine Life-Prep Academy | FL | Education | 8 | 1,200 |
| 3 | Walkiria | Centro de Apoyo Familiar | MA | Human Services | 8 | 825 |
| 4 | Alexia | Family Connection-Communities In | GA | Human Services | 8 | 504 |
| 5 | Jason | Northwest Side CDC | IL | Housing | 8 | 275 |
| 6 | Erika | Refugee Development Center | MI | Human Services | 7 | 588 |
| 7 | Ashley | Disability Resource Center | NC | Human Services | 7 | 478 |
| 8 | Sarah | Emergency Support Shelter | WA | Human Services | 7 | 433 |
| 9 | Rena | GA Partnership for Telehealth | GA | Health | 7 | 325 |
| 10 | Barbara | Adoptive & Foster Families of ME | ME | Human Services | 7 | 207 |
| 11 | Kenneth | West Sound Treatment Center | WA | Mental Health | 7 | 137 |
| 12 | Andrea | Hawaii Wildfire Management | HI | Environment | 7 | 111 |
| 13 | Ken | Operation Rapid Response | KS | Housing | 7 | 67 |
| 14 | Felicia | Sojourner House | MA | Housing | 7 | 402 |
| 15 | Mark | Watkins Glen Motor Racing Research | NY | Arts & Culture | 6 | 1,784 |
| 16 | Al | Variety the Children's | TX | Human Services | 6 | 1,222 |
| 17 | Pamela | Workforce Services Unlimited | OH | Education | 6 | 1,258 |
| 18 | Tomas | EnrichLA | CA | Environment | 6 | 975 |
| 19 | Kacey | Westport Weston Cooperative Nursery | CT | Education | 6 | 1,012 |
| 20 | Andrea | Respective Solutions Group | PA | Human Services | 6 | 1,015 |

### Diversity Metrics
- **States:** 16 unique (NY, FL, MA, GA, IL, MI, NC, WA, ME, HI, KS, TX, OH, CA, CT, PA)
- **Sectors:** 7 unique (Human Services, Education, Housing, Health, Mental Health, Environment, Arts & Culture)
- **Max per state:** 2 (NY, MA, GA, WA)
- **Max per sector:** 9 (Human Services, the dominant nonprofit sector)

### Foundations Selected Per Email

| # | Foundation 1 | Foundation 2 | Why Selected |
|---|-------------|-------------|-------------|
| 1 | Mother Cabrini Health Foundation | Lilly Endowment | NYC human services, youth focus |
| 2 | Knight Foundation | Lennar Foundation | FL education, community focus |
| 3 | Cummings Foundation | Fidelity Foundation | MA human services, community orgs |
| 4 | Joseph B Whitehead Foundation | James M Cox Foundation | GA-focused family services |
| 5 | Polk Bros Foundation | Arie and Ida Crown Memorial | Chicago housing/community |
| 6 | WK Kellogg Foundation | Ronda E Stryker Foundation | MI community, refugee-adjacent |
| 7 | Duke Endowment | Dogwood Health Trust | NC human services, DV support |
| 8 | MJ Murdock Charitable Trust | Satterberg Foundation | WA/Pacific NW human services |
| 9 | Robert W Woodruff Foundation | J Bulow Campbell Foundation | GA health, rural health |
| 10 | John T Gorman Foundation | Elmina B Sewall Foundation | ME-specific, family services |
| 11 | MJ Murdock Charitable Trust | Medina Foundation | WA behavioral health |
| 12 | Harold KL Castle Foundation | Marisla Foundation | HI environment, conservation |
| 13 | Sunderland Foundation | Earl Bane Foundation | KS housing/shelter |
| 14 | Liberty Mutual Foundation | Eastern Bank Foundation | MA housing, family shelter |
| 15 | Ford Foundation | Andrew W Mellon Foundation | NY arts/culture, preservation |
| 16 | Houston Endowment | Rees-Jones Foundation | TX children's services |
| 17 | Knight Foundation | Austin E Knowlton Foundation | OH education, workforce |
| 18 | Packard Foundation | Hewlett Foundation | CA environment |
| 19 | Lilly Endowment | Andrew W Mellon Foundation | CT education |
| 20 | William Penn Foundation | Hillman Family Foundations | PA youth services |

### Data Quality Notes
- All 20 prospects have real first names extracted from officer data
- All 20 have non-empty mission descriptions
- One prospect (Sojourner House, MA) has a PA-domain email (sjhpa.org) despite MA state. Could be a data quality issue.
- Some cohort top foundations are very large (Gates, Mellon, Ford) relative to prospect org size. The full list contains more appropriately sized funders.
- Watkins Glen Motor Racing Research (arts/culture) is a niche museum; large arts foundations may not be realistic but demonstrate the sector's funding depth.

---

## Previous Cohort Collision Check

4 of 10 foundation emails from the previous cohort (EMAILS_2026-02-16_first_cohort_CA.md) would have gone to organizations we already contacted by phone:

| Previous Email | Foundation | Collision Type |
|---------------|-----------|---------------|
| stear@pricephilanthropies.org | Price Philanthropies Foundation | Already contacted (phone) |
| mroach@ncousa.com | O.L. Halsell Foundation | Already contacted (phone) |
| palmer.jackson@gmail.com | Ann Jackson Family Foundation | Already contacted (phone) |
| COMMUNITYARTS@ZFF.ORG | Zellerbach Family Foundation | In pipeline (queued) |

**All 4 are now in the suppress list.** The new email cohort (20 nonprofits) has zero collisions with Calls-2.xlsx contacts.

The previous cohort also used the wrong framing:
- Old: "I analyze foundation giving using public 990 data" + signed "Alec Kleinman, TheGrantScout"
- New: Give-first approach, no company mention, signed just "Alec"

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| import_calls.py | Enhancements/2026-02-16/ | Python script to import Calls-2.xlsx |
| build_cohorts_v2.sql | Enhancements/2026-02-16/ | SQL to build cohort foundation lists |
| EMAILS_2026-02-16_nonprofit_cohort_1.md | Enhancements/2026-02-16/ | 20 drafted emails with metadata |
| EMAIL_BATCH_2026-02-16_nonprofit_1.csv | Enhancements/2026-02-16/ | CSV for sender script |
| REPORT_2026-02-16_email_prep_and_draft.md | Enhancements/2026-02-16/ | This report |

### Database Objects Created/Modified

| Object | Type | Description |
|--------|------|-------------|
| campaign_prospect_status | ALTER TABLE | email nullable, notes column added |
| campaign_prospect_status | 227 rows | Cold call outreach history |
| foundation_prospects2 | 5 rows | Contact emails enriched from Sheet3 |
| nonprofits_prospects2 | ALTER TABLE | contact_first_name, cohort columns added |
| cohort_foundation_lists | NEW TABLE | 13,002 rows (top 15 per state+sector) |
| cohort_viability | NEW TABLE | 882 rows (864 viable) |
| v_suppress_list | NEW VIEW | Email-based suppress list (1,869 emails) |
| v_suppress_list_by_ein | NEW VIEW | EIN-based suppress list (1,443 EINs) |

---

## Notes

### What Went Well
- Bulk SQL approach for cohort foundation lists ran in seconds (vs. per-combo approach that was projected to take hours)
- 88% first-name coverage from all_officers JSONB
- 4,990 prospects ready to email after suppression (large addressable pool)
- Previous cohort collisions are now prevented by suppress list

### Recommendations
1. **Send batch 1 first** (5 emails, score 8) and monitor deliverability before scaling
2. **Fix last-name-first names**: Query all_officers for patterns like "LastName FirstName" to catch more cases like "Simmons Dawn M"
3. **Verify Sojourner House state**: Email domain suggests PA, not MA
4. **For cohorts with 200+ foundations**, consider only listing top 50-100 in the free list (otherwise it's overwhelming)
5. **Track replies in campaign_prospect_status** to measure conversion and refine selection criteria

### Next Steps
- Adapt/create send script to process EMAIL_BATCH CSV
- After initial results, draft foundation cohort emails (separate angle)
- Build A/B testing infrastructure for subject lines

---

*Generated by Claude Code on 2026-02-16*
