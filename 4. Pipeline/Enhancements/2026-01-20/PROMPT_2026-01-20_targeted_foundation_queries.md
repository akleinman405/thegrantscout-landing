# PROMPT: Find Foundation Matches for Beta Clients

**Date:** 2026-01-20
**Owner:** Claude Code CLI

---

## Background

We're building foundation matching reports for nonprofit clients. Our standard pipeline finds foundations that funded "sibling" organizations (similar nonprofits). However, this approach failed for some clients because it didn't filter by geography - foundations that only fund Michigan showed up as matches for California nonprofits.

We need to fill gaps for certain clients using a simpler, more direct approach: find foundations that have actually given grants in the client's state/region for the client's cause area.

**This is a two-phase process:**
- **Phase 1 (this prompt):** Database queries to generate an UNVETTED list of candidates
- **Phase 2 (separate, manual):** Research each foundation one at a time via web search

---

## Current Status Summary

| Client | Status | Matches Needed |
|--------|--------|----------------|
| RHF | ✅ Ready | 0 - pick top 5 from existing list |
| Horizons | ⚠️ Reframe | 0 - but list is mostly existing funders |
| SNS | ❌ Rebuild | 5 - entire list was geographically disqualified |
| Friendship Circle | ⚠️ Need more | 2-3 more |
| PSMF | ⚠️ Need more | 2-3 more |

---

## What We Learned

1. **Geographic filtering is essential.** A foundation's headquarters state doesn't matter - what matters is where they've actually given grants.

2. **The IRS `only_contri_to_preselected_ind` field is NOT always accurate.** It's a useful initial filter, but many foundations marked as "open" actually say "by invitation only" on their website. **Web verification is required.**

3. **Grant purpose text** tells us what the foundation actually funds. Keywords in purpose text are more reliable than foundation mission statements.

4. **Multiple grants = pattern.** One grant could be an outlier. 2+ grants in the same cause area shows intentional funding.

---

## The Five Clients

### Client 1: RHF (Retirement Housing Foundation)
**Location:** Headquartered in California, but NATIONAL operations
**Properties in:** Clark County NV (Las Vegas, Henderson), DeKalb County GA (Stone Mountain), Phoenix AZ, Riverside CA, Utah
**Budget:** $10M - $50M (IRS shows $42M)
**Grant size seeking:** Over $500,000 (major grants)
**Grant capacity:** Part-time grant staff (<20 hrs/week)

**What they do:** 
> "Low Income Housing to Seniors and Families, but primarily Seniors"

**Populations served:** Seniors 65+, low-income individuals

**Why they're using our service:** Looking for gap financing for future multifamily projects in specific areas: DeKalb County GA, Clark County NV, Utah, Phoenix AZ, Riverside CA

**Program areas:** Housing & Homelessness

**Matches needed:** 0 - already have 8-9 viable, just pick top 5
**Current status:** ✅ READY - strong list from Phase A/B

**Search keywords (if needed):** affordable housing, senior housing, low-income housing, multifamily, elderly housing, supportive housing

---

### Client 2: Horizons National Student Enrichment Program
**Location:** Connecticut HQ, but operates in 21 states (71 sites)
**Cities:** Boston, New Haven, NYC, Philadelphia, Atlanta, Chicago, San Diego, Denver, and 30+ more
**Budget:** $1M - $5M (IRS shows $3.4M)
**Grant size seeking:** $25,000 - $100,000 (medium grants)
**Grant capacity:** Multiple grant staff (2+ FTE)

**What they do:**
> "Horizons is a tuition-free, multi-year academic and enrichment program for students from under-resourced communities who lack access to expanded learning opportunities. In 2025, Horizons programs served over 7,500 students at 71 sites across 21 states."

**Populations served:** Children (0-12), youth (13-17), low-income, rural and urban communities

**Why they're using our service:** National network seeking foundations to support summer learning enrichment for K-8 students from under-resourced communities.

**Existing funders:** Richard D. Donchian Foundation, Henry E. Niles Foundation, J.C. Kellogg Foundation, Hilda and Preston Davis Foundation, Scoob Trust Foundation, Louis Calder Foundation, Horace W. Goldsmith Foundation

**Program areas:** Education & Youth Development

**Matches needed:** 0 - but note that current list is mostly EXISTING funders of Horizons affiliates
**Current status:** ⚠️ REFRAME - 7 of 9 candidates already fund Horizons chapters. Useful for stewardship, but not "new discovery." May want to find truly NEW prospects.

**Search keywords (if needed):** summer learning, academic enrichment, youth education, after-school, K-8, underserved students, expanded learning

---

### Client 3: SNS (Senior Network Services)
**Location:** Soquel, California (serves multiple counties)
**Budget:** $1M - $5M
**Grant size seeking:** $100,000 - $500,000 (large grants)
**Grant capacity:** Full-time grant staff (1 FTE)
**Timeframe:** FY2026-2028

**What they do:** 
> "Our mission is to provide senior citizens and people with disabilities with information, guidance and assistance in coordinating existing resources to promote independence and lead the highest quality of life."

**Populations served:** Seniors 65+, people with disabilities, low-income, rural communities, homeless individuals

**Why they're using our service:** Looking for large grants ($100K-$500K) to support senior services and case management across multiple California counties. Open to partnerships and contract opportunities.

**Program areas:** Social Services, Healthcare & Mental Health

**Matches needed:** 5 foundations
**Current status:** ❌ NEEDS REBUILD - entire previous list was geographically disqualified (all out-of-state)

**Search keywords:** senior, elderly, aging, older adult, meals on wheels, case management, independent living, disability

---

### Client 4: Friendship Circle SD
**Location:** San Diego, California (county-wide)
**Budget:** ~$2.7M (IRS) - questionnaire said $500K-$1M
**Grant size seeking:** $25,000 - $100,000 (medium grants)
**Grant capacity:** No dedicated grant staff (volunteers)
**Timeframe:** 2026

**What they do:**
> "We promote Friendships between people with and without special needs by providing recreational, educational, social and vocational experiences in an inclusive environment."

**Populations served:** Children, youth, young adults, adults, seniors - all with disabilities/special needs

**Why they're using our service:** 
- **Priority project:** Vocational training bakery (~$100K need) that employs people with special needs
- **Future project:** Community center/building for families and volunteers

**Existing funders:** Jewish Federation, Walmart

**Program areas:** Education & Youth Development, Social Services, Arts & Culture, Healthcare & Mental Health

**Matches needed:** 2-3 more foundations
**Current status:** ⚠️ NEEDS MORE - only 2-3 viable (Ekstrom, Gloria Estefan, maybe Umpqua)

**Search keywords:** disability, special needs, developmental, inclusion, vocational, employment, job training, autism, recreation, Jewish

---

### Client 5: PSMF (Patient Safety Movement Foundation)
**Location:** Irvine, California (but programs are GLOBAL)
**Budget:** Over $1M
**Grant size seeking:** $25,000 - $100,000 (medium grants)
**Grant capacity:** No dedicated grant staff (volunteers)
**Timeframe:** Maximum one year

**What they do:**
> "We protect patients because everyone will be a patient one day, and preventable harm can be reduced through proper training. Through our fellowship program for clinicians from low- and middle-income countries, we screened more than 1,000 applicants and trained 47 fellows who are now applying their skills to reduce preventable harm in their hospitals. An estimated 26,200 patients each year will benefit."

**Key program:** Kiani Fellowship - 12-month virtual training for healthcare professionals from 48 countries

**Why they're using our service:** Looking for foundations that fund healthcare education and clinical training. Challenge is that most US foundations only fund domestic programs, but PSMF's fellowship serves global participants.

**Program areas:** Healthcare & Mental Health, Research & Innovation, Education

**Matches needed:** 2-3 more foundations
**Current status:** ⚠️ NEEDS MORE - only 2-3 viable (Josiah Macy Jr, Commonwealth Fund, Hartford is invite-only)

**Search keywords:** healthcare education, medical training, clinical fellowship, health professional development, patient safety, quality improvement, global health

---

## PHASE 1: Database Screening (This Prompt)

### Your Task

For each client, query the database to find 15-20 foundation candidates that meet these criteria:

1. **Have actually given grants** in the relevant geography (California for SNS/FC, national OK for PSMF)
2. **For the relevant cause area** (based on grant purpose text keywords)
3. **IRS indicator suggests they accept applications** (FALSE or NULL) - *Note: this will be verified in Phase 2*
4. **Have meaningful capacity** (assets > $500K for FC/PSMF, assets > $1M for SNS since they want larger grants)
5. **Are recently active** (grants in 2020 or later)
6. **Show a pattern** (2+ grants in the cause area preferred)

**Important:** This is an UNVETTED list. The IRS "accepts applications" field is not reliable. Phase 2 will verify each foundation via web research.

---

### Phase 1 Output

**File:** `REPORT_2026-01-20_phase1_foundation_candidates.md`

For each client, provide a numbered list of foundation candidates with:
- Foundation Name
- EIN
- Foundation State
- Assets
- # of Relevant CA Grants (or national for PSMF)
- Grant size range
- IRS Open Indicator
- Website (if in database)
- 2-3 sample grants as evidence (Recipient: $Amount for "Purpose" - Year)

Example format:
```
### SNS Candidates (15 foundations)

1. **Example Senior Foundation**
   - EIN: 123456789
   - State: CA | Assets: $15M
   - CA Senior Grants: 8 | Grant Range: $10K - $75K
   - IRS Open: TRUE | Website: www.example.org
   - Evidence:
     - Riverside Senior Center: $50K for "meals and transportation for elderly" (2022)
     - Inland Empire AAA: $35K for "senior case management services" (2023)
     - Corona Senior Services: $25K for "independent living program" (2021)

2. **Another Foundation**
   ...
```

---

## PHASE 2: Web Verification (Separate - Manual)

After Phase 1, I will ask you to research foundations one at a time.

**When I say:** "Research [Foundation Name] for [Client]"

**You will:**
1. Search the web for the foundation's website and grantmaking information
2. Answer these specific questions:
   - **Do they accept unsolicited applications?** (Yes / No / By invitation only / Unclear)
   - **What is their stated geographic focus?** (Specific states/regions, or national)
   - **What are their stated funding priorities?** (Quote from website)
   - **What are their eligibility requirements?** (Budget minimums, years in operation, etc.)
   - **What is their application process?** (LOI, online portal, written request, deadlines)
   - **Does the client appear to be eligible?** (Yes / No / Maybe - with reasoning)
3. Provide all source URLs used
4. Give a final recommendation: **PURSUE** / **SKIP** / **NEEDS MORE INFO**

---

## Database Notes

- Use schema `f990_2025`
- Key tables: `fact_grants`, `pf_returns`, `dim_foundations`
- Grant geography is in `fact_grants.recipient_state`
- Grant purpose is in `fact_grants.purpose_text`
- IRS open indicator is in `pf_returns.only_contri_to_preselected_ind` (use as initial filter only - NOT reliable)
- Get most recent 990-PF data by ordering by tax_year DESC

---

## Phase 1 Process

**Run queries for these clients:**

1. **Query for SNS** - California recipients + senior/aging keywords + assets > $1M (they want large grants)
2. **Query for Friendship Circle** - California recipients + disability keywords + assets > $500K
3. **Query for PSMF** - Any state + healthcare education keywords + assets > $1M

**Optional (if requested):**
4. **Query for Horizons** - National + summer learning/youth education keywords (to find NEW prospects, not existing funders)
5. **Query for RHF** - Multi-state + affordable housing keywords (if they want alternatives to current list)

For each foundation found, pull 2-3 sample grants as evidence of fit. Compile into the markdown report format above. Save to `/mnt/user-data/outputs/`.

**Do NOT do web research yet.** Just produce the database-filtered candidate list.

---

*End of Phase 1 prompt*
