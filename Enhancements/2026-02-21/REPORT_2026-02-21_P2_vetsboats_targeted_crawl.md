# Report: VetsBoats Targeted Crawl for Opportunity Leads

**Date:** 2026-02-21

**Prompt:** PROMPT_2026-02-21_P2_opportunity_research_v2.md

**Status:** Complete

**Owner:** Claude Code

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-21 | Claude Code | Initial version |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Candidate Results](#candidate-results)
3. [Files Created](#files-createdmodified)
4. [Notes](#notes)

---

## Executive Summary

Conducted targeted web crawl and structured extraction for 5 Alec-approved candidates from the PROMPT 1 Schedule I discovery. Used 5 parallel research agents (one per candidate) to maximize throughput.

**Results:**

| Metric | Count |
|--------|-------|
| Candidates researched | 5 |
| Possible (pending eligibility check) | 2 |
| No Go (explicitly disqualified) | 1 |
| Skip (not a grantmaker or wrong geography) | 2 |

**Verdicts:**

| Foundation | Verdict | Blocking Issue |
|-----------|---------|----------------|
| Christopher Reeve Foundation | **POSSIBLE** | PF eligibility unknown; must serve paralysis population; deadline March 12 |
| Orange County Community Foundation | **NO GO** | PFs explicitly ineligible + OC-only geography |
| Bob Woodruff Foundation | **POSSIBLE** | Requires 990/990-EZ filing (not 990-PF); highest program fit |
| SRAlab | **SKIP** | Hospital, not a grantmaker; Judd Goldman is referral partnership |
| Tahoe Fund | **SKIP** | Tahoe Basin only + environmental mission |

**Key Finding:** VetsBoats' private foundation status (990-PF filer) is the recurring eligibility barrier across Schedule I-sourced public charity funders. Both "Possible" candidates require direct confirmation that 990-PF filers can apply. The 4 PF leads from prior research do not have this barrier.

**Combined candidate pool for final 5 selection:**
1. Kim & Harold Louie Family Foundation (STRONG_FIT, rolling LOI)
2. Charles H. Stout Foundation (STRONG_FIT, June 15 deadline)
3. Kovler Family Foundation (POSSIBLE_FIT, mid-Nov deadline)
4. Howard Family Foundation (POSSIBLE_FIT, bank-managed)
5. Christopher Reeve Foundation (POSSIBLE, pending PF eligibility)
6. Bob Woodruff Foundation (POSSIBLE, pending 990-PF eligibility)

---

## Candidate Results

### 1. Christopher Reeve Foundation (POSSIBLE)

- **EIN:** 222939536 (public charity, NJ)
- **Program:** Quality of Life (QOL) Grants, $5K-$25K (Tier 1), up to $100K (Tier 5, prior grantees only)
- **Application:** Open now via Grant Interface portal. **Deadline: March 12, 2026.**
- **Cycle:** Semi-annual (spring + fall)
- **Contact:** Alena Sherman, Dir. Grant Administration, QOL@Reeve.org
- **PF Eligible:** Unknown. GrantsBuddy.com lists PFs as ineligible; Reeve's own materials say "501(c)(3)" without distinguishing. Needs direct confirmation.
- **Critical Requirement:** Must serve people with **paralysis** (SCI, stroke, MS, etc.). Veterans get special consideration but paralysis focus is mandatory.
- **Bay Area Precedent:** BORP received QOL grant for adaptive sports in the Bay Area.

### 2. Orange County Community Foundation (NO GO)

- **EIN:** 330378778 (public charity, CA)
- **Disqualifiers:** (1) FAQ explicitly states "Organizations with a Private Foundation designation are currently not eligible." (2) OC-only geography.
- **Side Note:** TK Foundation Youth Sailing (administered through OCCF) has broader geography but likely same PF barrier. Only relevant if VetsBoats has youth programs.

### 3. Bob Woodruff Foundation (POSSIBLE)

- **EIN:** 261441650 (public charity, NY). NOTE: Prompt listed 237047543; actual EIN is 261441650.
- **Program:** Charitable Investments, $5K-$500K (avg ~$100K), rolling applications
- **Application:** Open year-round via Blackbaud YourCause portal
- **Contact:** grants@bobwoodrufffoundation.org, 877-784-7268
- **PF Eligible:** Likely no. Requires "filed a 990EZ or 990 for last two fiscal years" (excludes 990-PF). May be shorthand. Needs direct confirmation.
- **Programmatic Fit:** Highest of all 5. Core mission is veterans. Adaptive sports funded as "Quality of Life." Move United and Disabled Sports USA are major grantees. Water sports explicitly included.
- **Budget Threshold:** Requires $50K+ gross receipts for 2 years. Needs VetsBoats financial verification.

### 4. SRAlab (SKIP)

- **EIN:** 362256036 (hospital, IL)
- **Finding:** Not a grantmaker. $447M-revenue research hospital. "Grants" are research subcontracts to universities. Judd Goldman Adaptive Sailing connection is a clinical referral partnership, not funding. JGASF raises its own money from Chicago-area family foundations.

### 5. Tahoe Fund (SKIP)

- **EIN:** 010974628 (public charity, CA/NV)
- **Finding:** Strictly Lake Tahoe Basin environmental fund. 2026 call for projects already closed. Zero geographic or programmatic overlap with VetsBoats.

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| DATA_2026-02-21_vetsboats_targeted_crawl.json | Enhancements/2026-02-21/ | Structured extraction for all 5 candidates |
| DATA_2026-02-21_vetsboats_opportunity_cards.md | Enhancements/2026-02-21/ | Formatted cards for Alec's review |
| REPORT_2026-02-21_P2_vetsboats_targeted_crawl.md | Enhancements/2026-02-21/ | This report |

---

## Notes

1. **Private foundation status is the dominant barrier** for Schedule I-sourced leads. Public charity funders commonly require 990/990-EZ filing or explicitly exclude private foundations. The PF leads from prior crawl (Louie, Stout, Kovler, Howard) are all private foundations themselves and do not have this barrier.

2. **Two action items for Alec before final selection:**
   - Email QOL@Reeve.org to ask if private operating foundations are eligible for QOL grants
   - Email grants@bobwoodrufffoundation.org or test BWF's portal eligibility quiz with EIN 464194065

3. **Reeve Foundation deadline is imminent** (March 12, 2026). If pursuing, PF eligibility must be confirmed within days.

4. **BWF EIN mismatch:** The EIN from the discovery prompt (237047543) does not match BWF's actual EIN (261441650). The original EIN may have been a data quality issue in the Schedule I source.

---

*Generated by Claude Code on 2026-02-21*
