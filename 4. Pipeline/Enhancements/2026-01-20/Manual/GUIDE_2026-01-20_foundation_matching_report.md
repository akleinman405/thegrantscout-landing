# TheGrantScout: Foundation Matching Report Guide

**Version:** 5.0
**Date:** 2026-01-20
**Status:** Production Ready
**Replaces:** GUIDE_2026-01-13_PSMF_report_step_by_step.md and GUIDE_2026-01-16_phase3_foundation_discovery.md

---

## Table of Contents

1. [Overview](#1-overview)
2. [Key Concepts & Lessons Learned](#2-key-concepts--lessons-learned)
3. [Phase 1: Client Intake & Setup](#3-phase-1-client-intake--setup)
4. [Phase 2: Client Understanding](#4-phase-2-client-understanding)
5. [Phase 3: Foundation Discovery (Database)](#5-phase-3-foundation-discovery-database)
6. [Phase 4: Foundation Verification (Web Research)](#6-phase-4-foundation-verification-web-research)
7. [Phase 5: Report Assembly](#7-phase-5-report-assembly)
8. [Phase 6: Quality Review & Delivery](#8-phase-6-quality-review--delivery)
9. [Edge Cases by Nonprofit Type](#9-edge-cases-by-nonprofit-type)
10. [Troubleshooting](#10-troubleshooting)
11. [Reference: Database Schema](#11-reference-database-schema)

---

## 1. Overview

### What We Deliver

A monthly PDF report with 5 curated foundation opportunities, including:
- Why the foundation is a fit (evidence from past grants)
- Funder snapshot (giving patterns, typical grant size, focus areas)
- Positioning strategy (how to frame the ask)
- Action plan (specific next steps, contacts, deadlines)

### The Core Methodology

**The Question We Answer:** "Which foundations have funded organizations like yours, for work like yours, in places like yours?"

**The Algorithm:**
1. Find "siblings" (similar nonprofits by mission and budget)
2. Find grants to those siblings that match client's work
3. Filter by geography (foundations that actually fund client's region)
4. Filter by accessibility (foundations that accept applications)
5. Verify via web research (eligibility, process, fit)
6. Select top 5 and build the case

### Critical Lessons Learned

| Lesson | Impact |
|--------|--------|
| **Geographic filtering is essential** | Siblings can be anywhere; must filter by where foundation actually gives grants |
| **IRS "open to applications" is unreliable** | ~30% of "open" foundations say "invite only" on their website |
| **Verify BEFORE investing effort** | Don't score 500 foundations then discover 78% are invite-only |
| **Broader semantic framing works** | Narrow target purposes yield few matches; iterate to sector-level if needed |
| **Match on PROGRAM TYPE, not just cause** | PSMF couldn't find "patient safety funders" but could find "fellowship funders" |

---

## 2. Key Concepts & Lessons Learned

### Terminology

| Term | Definition |
|------|------------|
| **Sibling** | Nonprofit with similar mission (cosine similarity ≥ 0.50) and comparable budget (0.2x - 5x) |
| **Target Grant** | Grant whose purpose matches client's work (keyword match OR semantic similarity ≥ 0.55) |
| **Gold Standard** | Target grant + first-time recipient + geographic match |
| **Tier A** | Open to applications (verified via website) |
| **Tier B** | Relationship-required (high fit but needs introduction) |
| **Tier C** | Dormant, captive, or closed |

### Why the Sibling Approach Works (and When It Doesn't)

**Works well for:**
- Mid-sized nonprofits in mainstream sectors (housing, education, senior services, youth)
- Organizations with many comparable peers who receive foundation grants
- Local/regional nonprofits with clear geographic focus

**Struggles with:**
- **Structurally unique organizations** - Peers don't receive foundation grants (PSMF's peers are government-funded)
- **Narrow intersections** - Jewish + disability = tiny funder pool
- **Global scope** - Most US foundations fund domestically only
- **Generic missions** - Match too many siblings, diluting signal

### The Geographic Filtering Problem

**What went wrong:** The sibling algorithm found foundations that funded similar nonprofits. But those siblings could be in Michigan, Colorado, Florida - anywhere. A Michigan foundation showed up as a "match" for a California nonprofit because it funded a Michigan senior center (which was a sibling).

**The fix:** Filter foundations by where they've **actually given grants**, not where they're headquartered.

### The Accessibility Problem

**What went wrong:** 78% of "gold standard" foundations were invite-only. We spent hours identifying perfect-fit foundations that couldn't be approached.

**The fix:** 
1. Use IRS indicator as initial filter (necessary but not sufficient)
2. Verify via website BEFORE investing in deep research
3. Classify as Tier A/B/C early, process accordingly

---

## 3. Phase 1: Client Intake & Setup

**Goal:** Gather all client information and set up the run.

### Step 1.1: Load Questionnaire Data

From questionnaire, extract:
- Organization name and EIN
- Location (city, state, service area)
- Budget (questionnaire value)
- Grant size seeking
- Grant management capacity
- Program areas
- Populations served
- Geographic range (local/regional/national/international)
- Mission statement
- Specific project needs
- Timeframe
- Existing funders (to exclude)
- Special requests

Store in `dim_clients` table.

### Step 1.2: Look Up IRS Data

From database, get:
- Verified EIN
- IRS-reported revenue and assets
- IRS mission statement
- NTEE code
- State

Compare questionnaire budget to IRS budget:
- **GREEN:** Within 50% variance
- **YELLOW:** 50-100% variance
- **RED:** >100% variance (flag for review)

### Step 1.3: Create Run Folder

```
5. Runs/{client_name}/{date}/
├── inputs/
├── phase3_candidates/
├── phase4_verification/
├── phase5_report/
└── SESSION_STATE.md
```

### Step 1.4: Create Session State File

Document current status, key decisions, and next steps. Update throughout the process.

### Quality Checks
- [ ] Client exists in dim_clients with all required fields
- [ ] EIN verified (9 digits, matches IRS records)
- [ ] Budget variance flagged if applicable
- [ ] Run folder created
- [ ] Session state initialized

---

## 4. Phase 2: Client Understanding

**Goal:** Understand what the client actually needs so we find the right foundations.

### Step 2.1: Review Client Profile

Read questionnaire carefully. Note:
- What specific project/program needs funding?
- What size grants do they want?
- What's their capacity to manage grants?
- Any geographic constraints?
- Any existing funders to exclude?

### Step 2.2: Classify Nonprofit Type

| Type | Characteristics | Implications |
|------|-----------------|--------------|
| **Local/Community** | Single city/county | Filter foundations by grants to that specific geography |
| **Regional** | Multi-county or state | Filter by state-level geography |
| **National** | Multi-state operations | National foundations OK; filter out hyper-local |
| **International** | Global programs | Very limited pool; may need alternative approach |
| **Identity-Based** | Jewish, faith, ethnic, LGBTQ+ | Include identity-specific funders; accept smaller pools |
| **Niche Sector** | Arts, environment, health research | Include sector-specific foundation databases |

### Step 2.3: Create Target Grant Purpose

Write 1-2 sentences describing what a matching grant would fund.

**Template:**
> "[Program type] providing [services] to [target population] in [geography]"

**Examples:**
- SNS: "Senior services including case management, meals, transportation, and independent living support for elderly and disabled individuals in California"
- Friendship Circle: "Programs serving people with disabilities including vocational training, employment services, recreation, and social inclusion in San Diego County"
- PSMF: "Healthcare education and clinical training programs including fellowships for medical professionals"

**Lesson:** Start specific, but be ready to broaden if < 20 grants match.

### Step 2.4: Define Matching Keywords

List 8-15 keywords that should appear in matching grant purposes:

**Example (SNS):**
```
senior, elderly, aging, older adult, meals on wheels, 
case management, independent living, disability, 
transportation, home care
```

### Step 2.5: Identify Exclusions

- Existing funders (from questionnaire)
- Prior funders (query database for grants to client's EIN)
- Known ineligible foundations

### Quality Checks
- [ ] Nonprofit type classification is accurate
- [ ] Target grant purpose is specific enough to be meaningful
- [ ] Target grant purpose is broad enough to find 20+ matches
- [ ] Keywords cover program type AND population
- [ ] Exclusions documented

---

## 5. Phase 3: Foundation Discovery (Database)

**Goal:** Generate an UNVETTED list of foundation candidates using database queries.

### Step 3.1: Choose Discovery Approach

**Option A: Sibling-Based (Standard)**
Best for: Mainstream sectors with many comparable nonprofits

1. Find siblings (similar mission + comparable budget)
2. Find grants to siblings
3. Filter for target grants (keyword OR semantic match)
4. Filter by geography (grants to client's state)
5. Filter by IRS open indicator
6. Rank by target grant count

**Option B: Direct Query (Fallback)**
Best for: Local nonprofits, niche sectors, or when sibling approach fails

1. Query grants directly by:
   - Recipient state = client's state
   - Purpose keywords match client's work
   - Foundation assets > minimum threshold
   - IRS open indicator = TRUE/NULL
2. Group by foundation
3. Rank by relevant grant count

### Step 3.2: Apply Geographic Filter

**Critical:** Filter by where foundation has ACTUALLY given grants, not foundation HQ state.

```sql
-- Find foundations that have given grants to California
WHERE recipient_state = 'CA'
```

For national clients (RHF, Horizons), filter by states where they operate.

### Step 3.3: Apply Accessibility Filter

Use IRS indicator as initial filter:
```sql
WHERE only_contri_to_preselected_ind = FALSE 
   OR only_contri_to_preselected_ind IS NULL
```

**Remember:** This is NOT reliable. ~30% will turn out to be invite-only. That's OK - we verify in Phase 4.

### Step 3.4: Apply Capacity Filter

Match foundation capacity to client's grant size needs:

| Client Seeking | Foundation Assets Minimum |
|----------------|---------------------------|
| < $25K | $500K |
| $25K - $100K | $1M |
| $100K - $500K | $5M |
| > $500K | $25M |

### Step 3.5: Pull Evidence Grants

For each foundation candidate, pull 2-3 sample grants that demonstrate fit:
- Recipient name
- Amount
- Purpose text
- Year

### Step 3.6: Generate Candidate List

Output: 15-20 foundation candidates per client with:
- Foundation name, EIN, state, assets
- # of relevant grants
- Grant size range
- IRS open indicator
- Website (if available)
- 2-3 sample grants as evidence

**This is an UNVETTED list.** Phase 4 will verify each one.

### Quality Checks
- [ ] Geographic filter applied correctly
- [ ] At least 15 candidates per client
- [ ] Each candidate has 2+ relevant grants
- [ ] Evidence grants are actually relevant (spot-check)
- [ ] No existing/prior funders in list

---

## 6. Phase 4: Foundation Verification (Web Research)

**Goal:** Verify each candidate via web research. This is done ONE FOUNDATION AT A TIME.

### Step 4.1: Prioritize Candidates

Order by:
1. # of relevant grants (more = stronger signal)
2. Asset size (higher = more capacity)
3. Recency (recent grants = still active)

### Step 4.2: Research Each Foundation

For each foundation, search the web and answer:

**Question 1: Do they accept unsolicited applications?**
- Look for: "How to apply", "Grant guidelines", "Application process"
- Red flags: "By invitation only", "Does not accept unsolicited requests", "Pre-selected grantees"
- Answer: Yes / No / Unclear

**Question 2: What is their stated geographic focus?**
- Look for: Specific states, regions, "local", "national"
- Does client's location qualify?
- Answer: Specific restriction or "National/No restriction"

**Question 3: What are their funding priorities?**
- Look for: "What we fund", "Focus areas", "Priorities"
- Does client's work align?
- Quote relevant language from website

**Question 4: What are their eligibility requirements?**
- Budget minimums/maximums
- Years in operation
- 501(c)(3) status
- Geographic requirements
- Population requirements
- Does client qualify?

**Question 5: What is their application process?**
- LOI, online portal, written request, phone call?
- Deadlines (rolling or fixed)?
- Contact information?

**Question 6: Final Assessment**
- **PURSUE:** Accepts applications, client eligible, good fit
- **TIER B:** High fit but invite-only (include in relationship section)
- **SKIP:** Geographic mismatch, wrong focus, client ineligible

### Step 4.3: Document Sources

For EVERY claim, record the URL:
```
Foundation: Example Foundation
Claim: Accepts applications via online portal
URL: https://example.org/apply
Date: 2026-01-20
```

### Step 4.4: Update Candidate Status

After researching each foundation, update status:
- Verification Status: Verified Open / Invite Only / Needs Review
- Geographic Eligible: Yes / No
- Client Eligible: Yes / No / Maybe
- Recommendation: PURSUE / TIER B / SKIP
- Notes: Key findings

### Quality Checks
- [ ] At least 8 foundations verified as PURSUE
- [ ] All PURSUE foundations have confirmed application process
- [ ] All geographic restrictions documented
- [ ] All eligibility requirements documented
- [ ] All claims have source URLs

---

## 7. Phase 5: Report Assembly

**Goal:** Build the final report with 5 foundation opportunities.

### Step 5.1: Select Final 5

From verified candidates, select top 5 based on:
1. Verified open to applications
2. Client is eligible
3. Strong fit (target grants as evidence)
4. Appropriate grant size
5. Active (recent grants)

Consider including 1-2 Tier B (relationship-required) if Tier A pool is thin.

### Step 5.2: Calculate Funder Snapshot Metrics

For each selected foundation, calculate:
- **Annual Giving:** Total grants per year (3-year average)
- **Typical Grant:** Median grant size
- **Grant Range:** Min - Max
- **Geographic Focus:** Top states funded
- **Repeat Funding Rate:** % of grantees funded multiple times
- **Giving Trend:** Increasing / Stable / Decreasing

### Step 5.3: Find Proof-of-Fit Grants

For each foundation, find 3-5 grants that prove they fund work like client's:
- Similar program type
- Similar population
- Similar geography
- Appropriate grant size

### Step 5.4: Write Positioning Strategy

For each foundation, explain:
- Why client is a fit (cite specific evidence)
- How to frame the ask
- What angle to emphasize
- Potential concerns and how to address

### Step 5.5: Write Action Plan

For each foundation, provide:
- Specific next steps
- Contact information (if available)
- Deadline (if applicable)
- Application process summary
- Recommended ask amount

### Step 5.6: Assemble Report

Use report template. Include:
1. Cover page
2. Executive summary
3. 5 foundation profiles (1-2 pages each)
4. Appendix: Methodology note

---

## 8. Phase 6: Quality Review & Delivery

### Step 6.1: Content Review

- [ ] All 5 foundations are appropriate matches
- [ ] Proof-of-fit grants are actually relevant
- [ ] Positioning strategies are specific, not generic
- [ ] Action plans have concrete next steps
- [ ] No factual errors

### Step 6.2: Format Review

- [ ] Professional formatting
- [ ] Consistent styling
- [ ] No typos
- [ ] Links work (if applicable)

### Step 6.3: Final Check

- [ ] Client's specific project/need addressed
- [ ] Geographic constraints respected
- [ ] Grant size range appropriate
- [ ] Existing funders excluded

### Step 6.4: Deliver

- Export as PDF
- Send to client email
- Log delivery in tracking system

---

## 9. Edge Cases by Nonprofit Type

### Local/Community Nonprofits (e.g., Friendship Circle)

**Challenges:**
- Smaller pool of foundations funding specific geography
- National foundations may not fund local orgs

**Adjustments:**
- Include local community foundation (always Tier A)
- Lower minimum candidate threshold to 8
- Weight geographic match heavily
- Include regional family foundations even if "invite-only" (Tier B)

### National Nonprofits (e.g., RHF, Horizons)

**Challenges:**
- Need foundations that fund multiple states
- Hyper-local foundations are noise

**Adjustments:**
- Filter out foundations that only fund one state
- Include corporate foundations
- De-emphasize geographic match in scoring
- Consider federated funders (United Way network)

### Identity-Based Missions (e.g., Friendship Circle - Jewish + disability)

**Challenges:**
- Narrow intersection = tiny funder pool
- Identity-specific funders may be invite-only

**Adjustments:**
- Include identity-specific foundation databases
- Accept smaller candidate pools (8-10 vs 15-20)
- Auto-promote identity-aligned Tier B to report
- Consider both identity AND cause area separately

### International/Global Programs (e.g., PSMF)

**Challenges:**
- Most US foundations fund domestically only
- "Global health" is rare focus area

**Adjustments:**
- Match on PROGRAM TYPE (e.g., "fellowship") not cause area
- Look for foundations with explicit global focus
- Consider framing: "US-based curriculum development" for global delivery
- Include Tier B with relationship-building paths
- May need alternative approach entirely

### Startup Nonprofits (< 3 years old)

**Challenges:**
- Many foundations require track record
- Limited grant history to analyze

**Adjustments:**
- De-prioritize foundations requiring 3+ years
- Boost community foundations and "emerging org" programs
- Emphasize Tier B relationships
- Consider fiscal sponsor network

---

## 10. Troubleshooting

### Problem: Too Few Candidates After Geographic Filter

**Symptoms:** < 10 foundations found after filtering by client's state

**Solutions:**
1. Expand to neighboring states
2. Include foundations with no state restriction
3. For local clients: Add community foundation manually
4. Switch to direct query approach (not sibling-based)

### Problem: Semantic Similarity Too Narrow

**Symptoms:** < 20 grants with similarity ≥ 0.55

**Solution:** Broaden target grant purpose to sector level:
- Before: "Vocational training bakery for adults with disabilities"
- After: "Programs serving people with disabilities including employment, vocational training, recreation, and community inclusion"

### Problem: IRS Indicator Contradicts Website

**Symptoms:** IRS says open, website says invite-only (or vice versa)

**Solution:** Trust the website. Update verification notes. If IRS says closed but website shows open application, verify carefully - may have recently changed.

### Problem: All Candidates Are Invite-Only

**Symptoms:** After web verification, 0 Tier A candidates

**Solutions:**
1. Broaden search (different keywords, wider geography)
2. Include high-fit Tier B in report with relationship-building guidance
3. Research community foundations (often open)
4. Consider corporate foundation programs (often more accessible)

### Problem: Client's Peers Don't Receive Foundation Grants

**Symptoms:** Sibling approach yields few grants (e.g., PSMF)

**Solution:** Pivot to program-type matching:
1. Identify client's PROGRAM TYPE (e.g., "fellowship", "training program")
2. Query foundations that fund that program type regardless of cause area
3. Accept that cause-area match may be weaker

---

## 11. Reference: Database Schema

### Key Tables

| Table | Purpose |
|-------|---------|
| `dim_clients` | Client profiles from questionnaire |
| `fact_grants` | All grants from 990-PF data |
| `pf_returns` | Foundation 990-PF return data (includes `only_contri_to_preselected_ind`) |
| `dim_foundations` | Foundation profiles |
| `dim_recipients` | Grant recipient profiles |
| `emb_nonprofit_missions` | Mission embeddings for similarity search |
| `calc_client_siblings` | Computed siblings per client |
| `calc_client_sibling_grants` | Grants to siblings with flags |
| `calc_client_foundation_scores` | Foundation scores per client |

### Key Fields

| Field | Table | Description |
|-------|-------|-------------|
| `recipient_state` | fact_grants | State where grant was given (use for geographic filter) |
| `purpose_text` | fact_grants | Grant purpose description |
| `only_contri_to_preselected_ind` | pf_returns | IRS indicator for invite-only (unreliable) |
| `total_assets_eoy_amt` | pf_returns | Foundation assets |
| `website_url` | pf_returns | Foundation website |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 5.0 | 2026-01-20 | Major revision: Added Phase 4 web verification, geographic filtering lessons, two-phase approach, edge cases |
| 4.0 | 2026-01-16 | Added Phase 3.0 semantic framing, tier classification, troubleshooting |
| 3.0 | 2026-01-13 | Original PSMF step-by-step guide |

---

*Guide created 2026-01-20 based on learnings from PSMF, Friendship Circle, SNS, RHF, and Horizons*
