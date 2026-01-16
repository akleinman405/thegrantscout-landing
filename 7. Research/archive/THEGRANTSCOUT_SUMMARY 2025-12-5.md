# TheGrantScout: Product Summary

**Purpose:** Comprehensive context document for Research Team, Dev Team, and project planning. Tracks current status, learnings, and open questions.

**Last Updated:** December 5, 2025

---

## 1. What We Do

TheGrantScout helps nonprofits find foundations and grant opportunities most likely to want to fund them. We surface funders they didn't already know about and provide comprehensive information to maximize their chances of success.

**Core Promise:** "Your mission deserves funding. We'll help you find it."

**Value Proposition:**
- Discovery of new funding sources (not just reminders of known ones)
- Comprehensive funder intelligence in one organized place
- Positioning strategies based on foundation giving patterns
- Time savings on research that would take weeks manually

---

## 2. The Data Advantage

### Database Metrics

| Metric | Value |
|--------|-------|
| Foundations analyzed | 85,470 |
| Historical grants | 1,624,501 |
| Years of data | 8 (2016-2024) |
| Data source | IRS Form 990-PF filings |

### F990 2025 Import Status

**Status:** COMPLETE (December 2, 2025)

| Component | Details |
|-----------|---------|
| Source files | 8 ZIP files (~2 GB total) |
| Schema | f990_2025 (6 tables) |
| Form types | 990-PF, 990, 990-EZ |
| Next step | Validate data fields, build matching tables |

---

## 3. Core Methodology

### How Matching Works

**Workflow (MVP):**
1. Nonprofit profile submitted via questionnaire
2. Match nonprofit to foundations using 10-signal scoring
3. Score foundations on "openness to new grantees" 
4. Scrape matched foundations' websites for current opportunities
5. Supplement with federal/state opportunities database (reduces scraping effort)
6. Generate report with funder intelligence and positioning strategies

### 10-Signal Scoring Algorithm

| Signal | Points | Description |
|--------|--------|-------------|
| Prior Relationship | 40 | Has foundation funded this nonprofit before? |
| Geographic Match | 15 | In-state funding preference (3-5x more likely) |
| Grant Size Alignment | 12 | Does typical grant size match nonprofit's ask? |
| Repeat Funding Rate | 10 | Does foundation favor existing grantees? |
| Portfolio Concentration | 8 | How focused is foundation on specific sectors? |
| Purpose Text Match | 5 | Semantic similarity to past grant purposes |
| Recipient Validation | 4 | Foundation's grantee quality patterns |
| Foundation Size | 3 | Capacity to fund at requested level |
| Regional Proximity | 2 | Cross-state giving corridors |
| Grant Frequency | 1 | Active vs. sporadic grantmaker |

**Total Possible Score:** 100 points

### Openness Scoring

Foundations are scored on likelihood to fund NEW grantees (not just existing relationships). This addresses the need for discovery, not just relationship-based matching.

**Factors:**
- % of grants to first-time recipients
- Whether foundation accepts unsolicited applications
- Application process transparency
- Recent grantee diversity

---

## 4. Project Timeline

| Date | Milestone |
|------|-----------|
| Nov 1, 2025 | Selected as Tier 1 opportunity |
| Nov 15-17 | Project kickoff, F990 data discovered, scope expansion |
| Nov 21 | Beta Group 1 questionnaires collected |
| Nov 22-23 | BG1 Report 1 delivered (100% manual research) |
| Nov 24 | SNS feedback received (errors found) |
| Nov 25 | Horizons National zoom call (BG2 prospect) |
| Nov 30 | Round 2 recommendations document completed |
| Dec 2 | F990 2025 import complete, website landing page built |
| Dec 3 | PSMF feedback call (foundation-focused pivot) |
| Dec 4 | Terry Moran/VetsBoats call; Matt Gettleman identified as decision maker; follow-up sent |
| Dec 5 | Website copy finalized (monthly PDF report emphasis); Ka Ulukoa report held pending Bank of Hawaii deadline fix; CLAUDE.md naming conventions established |

---

## 5. Current Status

### Beta Group 1 (Forms Completed - 5 Organizations)

*Source: 3 from cold calls, 2 from cold emails*

| Organization | Sector | Geography | Status | Feedback Summary |
|--------------|--------|-----------|--------|------------------|
| Senior Network Services (SNS) | Senior services | California | Report 1 delivered | Errors found (wrong grant name, expired deadline, broken link). Already working on some opps. Asked about pricing (~$100/mo confirmed) and grant writing tier. Mariam suggested annual calendar with selective alerts. |
| Patient Safety Movement Foundation (PSMF) | Healthcare education | National/Global | Report 1 delivered, feedback call completed | Wants foundation-focused reports (~5 foundations), not opportunity-focused. Fellowship Program as funding target. Prefers LOI prospecting strategy. Interested in political/family foundation connections. Multi-mission org needs special handling. |
| Retirement Housing Foundation (RHF) | Senior housing | Multi-state | Report 1 delivered | Andy: Info organized in one place was helpful even though he already knew about the opportunities. Validates "calendar manager" customer type. |
| Ka Ulukoa | Youth athletics | Hawaii | Report 1 delivered | Report 2 reviewed but held pending Bank of Hawaii deadline fix before sending |
| Arborbrook Christian Academy (ACA) | K-12 athletics | North Carolina | Report 1 delivered | Awaiting detailed feedback |

### Beta Group 2 (Forms Completed - 1 Organization)

*Source: Cold email*

| Organization | Contact | Details | Status |
|--------------|---------|---------|--------|
| Horizons National | Alex Hof (PA) | Out-of-school K-8 programs, 6-week summer program, $43M decentralized network across multiple geographies. Wants foundation prospecting + direct fundraising. Looking for hyperlocal funding in communities where sites are located. | Form filled Nov 11, ready for report |

### Sales Pipeline (Interested - Not Yet Onboarded)

| Organization | Contact | Decision Maker | Source | Status | Notes |
|--------------|---------|----------------|--------|--------|-------|
| VetsBoats Foundation | Terry Moran | Matt Gettleman (Dir of Development) | LinkedIn | Interested | Dec 4 call completed. Sent website, sample report, Top 500 list. National expansion focus. Awaiting Matt's response. |

### BG1 Report 2 Plans

Testing two report approaches:
- **Opportunity-focused:** Current grant opportunities with deadlines, requirements, positioning
- **Foundation-focused:** Foundation profiles for relationship building, LOI prospecting (per PSMF request)

Will compare feedback to determine which approach (or hybrid) works best for different customer types.

**Note:** Ka Ulukoa Report 2 held pending resolution of Bank of Hawaii deadline issue (passed deadline with vague "contact for 2026" solution not acceptable for client-facing document).

---

## 6. Technical Infrastructure

### Full Database Schema

**Existing Tables (Production):**

| Table | Records | Purpose |
|-------|---------|---------|
| f990_foundations | 85,470 | Foundation profiles - name, EIN, state, assets, giving capacity |
| f990_grants | 1,624,501 | Historical grant records - amounts, purposes, recipients |
| nonprofits | ~10 | Beta user profiles from questionnaire |
| current_opportunities | ~42 | Scraped/discovered active grants (needs expansion) |
| matches | TBD | Generated match results with scores |
| foundation_intelligence | TBD | Enriched profiles (openness scores, patterns, giving style) |

**New F990 2025 Schema:**

| Table | Purpose |
|-------|---------|
| pf_returns | Private foundation returns (990-PF) - financials, grant capacity, application info |
| nonprofit_returns | Nonprofit returns (990, 990-EZ) - org info, programs, classification |
| pf_grants | Grant records from 990-PF Part XV - amounts, purposes, recipients |
| officers | Board members and officers from all form types |
| schedule_a | Charity classifications (509(a) status, public charity type) |
| import_log | ETL tracking - success/failure counts, timestamps |

### How Tables Work Together (Semi-Automated Flow)

```
1. INTAKE
   nonprofits table ← Questionnaire data (mission, geography, budget, sectors)

2. FOUNDATION MATCHING
   f990_foundations + f990_grants → 10-signal scoring algorithm
   → foundation_intelligence (enriched with openness scores)
   → matches table (ranked foundations per nonprofit)

3. OPPORTUNITY GATHERING
   Top matched foundations → Website scraping for current RFPs
   + current_opportunities table (federal/state grants)
   → Validated opportunities with deadlines

4. REPORT GENERATION
   matches + foundation_intelligence + current_opportunities
   → Funder Snapshots (8 metrics per foundation)
   → Positioning strategies
   → PDF/Excel reports
```

### What's Built vs. Still Needed

| Component | Status |
|-----------|--------|
| F990 2025 import | ✅ Complete |
| Foundation profiles (85K) | ✅ Complete |
| Historical grants (1.6M) | ✅ Complete |
| Matching algorithm code | ✅ Built (needs optimization) |
| Foundation intelligence table | ⏳ Needs population |
| Openness scoring | ⏳ Needs implementation |
| Website scraping pipeline | ⏳ Needs building |
| Current opportunities expansion | ⏳ 42 → 500+ needed |
| Report generation automation | ⏳ Currently manual |

### Tools & Stack

- **Database:** PostgreSQL
- **Backend:** Python (matching algorithm, scrapers)
- **Website:** Next.js 14, TypeScript, Tailwind CSS
- **Email:** Brevo API (planned)
- **Hosting:** TBD (Railway, Vercel options)
- **Agent Workflow:** CLAUDE.md naming conventions for Claude Code CLI

**Document Naming Convention (CLAUDE.md):**
- Format: `DOCTYPE_taskname_YYYY-MM-DD.V.ext`
- Doctypes: PROMPT (input), SPEC (requirements), REPORT (analysis output), STATUS (snapshot), GUIDE (how-to), DELIVERABLE (client-facing), CODE (scripts), INDEX (navigation)

---

## 7. What We Deliver

### Report Structure

**Email Brief (1 page):**
- Subject line with urgent deadlines
- "If you only do one thing this week" action
- Top 5 opportunities table (funder, amount, deadline, effort, fit)
- Immediate action items

**PDF Report (10-15 pages):**
- Executive summary with funding scenarios
- This Week's Top 5 table
- Per-opportunity deep dives:
  - Why This Fits (3-4 sentences)
  - Key Details (amount, deadline, portal, contact)
  - Funder Snapshot (8 metrics from F990 data)
  - Potential Connections (board overlap, shared network)
  - Positioning Strategy (data-driven recommendations)
  - Next Steps (specific actions with owners/deadlines)
- 8-week timeline
- Quick reference (all contacts and portals)

### Funder Snapshot Metrics

| Metric | Source |
|--------|--------|
| Annual Giving | f990_grants aggregation |
| Typical Grant | Median, min, max from history |
| Geographic Focus | % in-state, top states |
| Repeat Funding Rate | % recipients funded 2+ times |
| Giving Style | % general support vs. program-specific |
| Recipient Profile | Typical budget size, sector focus |
| Funding Trend | Growing/stable/declining over 3 years |
| Comparable Grant | Similar org that received funding |

### How BG1 Report 1 Was Made

- **100% manual research** (no automated matching)
- 20-30 page comprehensive PDFs
- 40+ hours per organization
- Research team used web search + F990 data + foundation websites
- Included positioning strategies, timelines, contact info, document checklists

### Report Types Being Tested (BG1 Report 2)

| Type | Focus | Best For |
|------|-------|----------|
| Opportunity-focused | Active grants with deadlines | Orgs ready to apply now |
| Foundation-focused | Foundation profiles for prospecting | Orgs building relationships, preferring LOI approach |

---

## 8. Outreach

### LinkedIn

| Metric | Value |
|--------|-------|
| Activity | Free giveaway posts offering grant matching |
| Results | TBD - tracking engagement |
| Next Steps | Continue engagement, track conversions to questionnaire |

### Cold Calls

| Metric | Value |
|--------|-------|
| Total prospects | 200 |
| Called | 50 (25%) |
| Conversations | 14 (28% connection rate) |
| Decision makers reached | 4 (8%) |
| Interested (Yes/Maybe) | 3 (6% interest rate) |
| BG1 members from calls | 3 |

**Pipeline:**
- 150 prospects remaining to call
- 10 requested follow-up emails

**Next Steps:**
- Complete call list
- Send follow-up emails to 10 who requested info

### Email Campaigns

| Metric | Value |
|--------|-------|
| Total sent (grant_alerts) | 1,395 |
| Delivered | 93.9% (good - industry avg ~85%) |
| Positive replies | 4 (0.23% - low vs. 1-5% industry avg) |
| BG1 members from email | 2 |
| BG2 members from email | 1 |

**Pipeline:**
- 1,391 pending follow-up (no reply yet)

**Next Steps:**
- Design follow-up sequence for non-responders
- Test different subject lines
- Consider phone follow-up for email non-responders

---

## 9. Website Status

### Completed

- Landing page built (Next.js 14, TypeScript, Tailwind CSS)
- Mobile optimizations (touch targets, typography)
- Responsive design
- Hero, How It Works, Features, Pricing, FAQ, CTA sections
- Form UI coded
- Copy finalized (Dec 5) - clarified monthly PDF report delivery format

### Still Needed

| Item | Priority |
|------|----------|
| Form API connection for CTA button | High |
| Mobile header fix (words cut off, too busy) | High |
| Example reports page | Medium |

---

## 10. Key Learnings

### Three Customer Types Identified

| Type | Characteristics | What They Want | Example |
|------|-----------------|----------------|---------|
| Calendar Managers | Experienced grant writers, already know most opportunities | Organization, reminders, nothing overlooked | Andy (RHF), Mariam (SNS) |
| Niche Seekers | Looking for opportunities outside their usual sources | Discovery of new/unexpected funders | Ka Ulukoa (Hawaii-specific) |
| Relationship Builders | Prefer prospecting over formal applications | Foundation profiles, LOI strategy, networking info | Consuelo (PSMF) |

### Key Feedback Insights

**From Mariam (SNS):**
- Experienced grant writers need reminders too - "the way you broke down the work ensures no action is overlooked"
- Suggested annual calendar with selective alerts (3 alerts/year vs. weekly)
- Only 1 of 5 opportunities was truly new to her
- Asked about grant writing concierge tier

**From Andy (RHF):**
- Info organized in one place was valuable even though he already knew the opportunities
- Validates the "calendar manager" use case

**From Consuelo (PSMF):**
- Multi-mission organizations need foundation-first approach
- Prefers LOI/inquiry format over formal applications
- Wants ~5 foundations with relationship-building info
- Fellowship Program is the priority funding target
- Interested in political/family foundation connections

### Report Quality Issues Found

- Wrong grant name (CSNSGP = Security, not Nutrition/Services)
- Expired deadline included (AAA RFP from Jan 2025)
- Broken link (NCOA grants page)
- Low discovery value for experienced grant writers

**Implication:** Need stronger QA process and hard filters before scoring.

---

## 11. What We Need to Learn Before Converting Clients

### Critical Questions to Answer Through Beta

| Question | Signal So Far | How to Answer |
|----------|---------------|---------------|
| **What's the right price?** | ~$100/mo mentioned, Mariam didn't object | Ask directly, test willingness to pay |
| **What's most valuable?** | Organization/reminders (Andy), positioning strategies (Mariam), foundation prospecting (Consuelo) | Compare feedback across customer types |
| **Bare minimum before first sale?** | TBD | Identify which features are must-have vs. nice-to-have |
| **How to get first client?** | Cold calls (6%) > cold email (0.23%) | Continue calls, refine pitch |
| **Report frequency/depth?** | Mariam: annual calendar + 3 alerts; Consuelo: ~5 foundations | Test both approaches |
| **Who is target client?** | Mid-market nonprofits without dedicated grant staff? | Analyze which beta orgs engage most |
| **Which client type prefers which report?** | Calendar managers want organization; relationship builders want prospecting | BG1 Report 2 A/B test |
| **How many beta testers before charging?** | Currently 5 in BG1, 1 in BG2 | Enough to validate format and pricing |

### What We DON'T Need Before Selling

- Proof that grants were won (takes 6-12 months)
- Perfect matching algorithm (iterate with paying customers)
- 100% database completion
- Fully automated system

### Recommended Approach

Set "founding member" price (~$100/mo) based on competitor research + beta feedback + gut. Convert BG2 or new leads to paid at discounted rate. Work closely with paying clients to iterate in real-time. This gets revenue + feedback simultaneously.

---

## 12. Goals & Milestones

### Immediate (This Week)

- [x] Follow up with Terry (sent Dec 4)
- [x] Establish document naming conventions (CLAUDE.md)
- [x] Finalize website copy
- [ ] Fix Ka Ulukoa report (Bank of Hawaii deadline issue)
- [ ] Validate F990 2025 data fields are complete
- [ ] Build matching tables infrastructure
- [ ] Deliver BG1 Report 2 (testing opp-focused vs foundation-focused)
- [ ] Send Horizons National their first report

### Near-Term (Next 2 Weeks)

- [ ] Complete website (form API, mobile fixes, example reports)
- [ ] Finish remaining 150 cold calls
- [ ] Get BG1 feedback on Report 2 format
- [ ] Finalize pricing based on feedback
- [ ] Convert first paying client (founding member rate)
- [ ] Follow up with VetsBoats/Matt Gettleman

### Medium-Term (30-60 Days)

- [ ] 50+ clients target
- [ ] <5 minute match generation (vs. 40+ hours manual)
- [ ] 70%+ QA pass rate (vs. current ~50%)
- [ ] 500+ current opportunities in database
- [ ] Semi-automated report generation

---

## 13. Competitive Positioning

### The Market Gap

| Segment | Examples | Problem |
|---------|----------|---------|
| Premium ($1,000+/mo) | Instrumentl, Foundation Directory Online | Unaffordable for 80% of nonprofits |
| Budget ($249/year) | GrantWatch | Limited features, outdated interface, low discovery value |
| Free | Grants.gov | Federal only, no matching intelligence |

**TheGrantScout fills the middle:** High-quality matching at mid-market pricing (50-70% less than Instrumentl).

### Differentiators

1. **Research-informed hybrid approach** - Not pure algorithm (black box) or pure manual (doesn't scale)
2. **Openness intelligence** - Identify foundations likely to fund NEW grantees, not just existing relationships
3. **Explainable recommendations** - Every match includes "why this foundation"
4. **Actionable, not overwhelming** - 5-10 high-probability opportunities vs. thousands of maybes

### Key Stats for Marketing

| Claim | Source |
|-------|--------|
| 85,000+ foundations analyzed | IRS 990-PF database |
| 1.6M+ historical grants | 8 years of filings (2016-2024) |
| 97% filter efficiency | Hard filters eliminate impossible matches |

---

## 14. Open Questions

### Answered (Decisions Made)

| Question | Answer |
|----------|--------|
| Business model | Subscription service |
| Target pricing | ~$100/mo founding member rate |
| Report format direction | Testing opportunity vs. foundation-focused |
| Data source | IRS F990 filings (verified, comprehensive) |

### Still Open (Need More Signal)

| Question | Current Thinking | How to Resolve |
|----------|------------------|----------------|
| Opportunity-focused vs. foundation-focused? | Different customers want different things | BG1 Report 2 A/B test |
| Grant writing tier? | Mariam interested, could be premium upsell | Survey interest, estimate effort |
| How to handle multi-mission orgs? | Foundation-first approach (per PSMF) | Test with more complex orgs |
| Vertical vs. horizontal product? | Start horizontal, may specialize later | See which verticals engage most |
| Optimal automation level? | 70% automated + 30% manual validation | Iterate based on quality metrics |
| Annual calendar vs. weekly alerts? | May depend on customer type | Test both approaches |

### Future Research Questions (From Research Team)

**High Priority:**
1. What predicts foundation responsiveness to cold outreach?
2. Can we predict grant success rates for specific matches?
3. How do foundation giving patterns change over time?
4. What's the ROI of relationship-building vs. cold applications?

**Product Questions:**
5. Should we show poor matches with explanations (learning) or hide them (reduce noise)?
6. What's the value of grant tracking/management features?
7. Can we partner with grant writing consultants or compete with them?
8. Would foundations pay for pre-screened applicant pipeline? (two-sided marketplace)

---

## 15. Technical Reference

### Database Connection

```
Host: 172.26.16.1
Port: 5432
Database: postgres
User: postgres
```

### Key File Locations

| Item | Path |
|------|------|
| Matching algorithm | `/matching_algorithm.py` |
| Report templates | `/templates/` |
| F990 2025 import scripts | `/f990_2025_import/` |
| Website | `/thegrantscout-landing/` |

### Tools & Stack

- **Database:** PostgreSQL
- **Backend:** Python (matching algorithm, scrapers)
- **Website:** Next.js 14, TypeScript, Tailwind CSS
- **Email:** Brevo API (planned)
- **Hosting:** TBD (Railway, Vercel options)

---

*Last Updated: December 5, 2025*
