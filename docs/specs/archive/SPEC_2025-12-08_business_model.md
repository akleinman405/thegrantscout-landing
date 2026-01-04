# SPEC: BUSINESS_MODEL.md

**Document Type:** SPEC
**Purpose:** Revenue model and how we landed on it
**Date:** 2025-12-08

---

## 1. Model Overview

### Business Model Structure
TheGrantScout operates on a **monthly subscription model** with report-based delivery.

**What the Customer Gets Each Month:**
- Personalized PDF report (10-15 pages)
- 5-10 matched opportunities OR 5 matched foundations
- Funder intelligence and positioning strategies
- Contact information and application details
- Deadline tracking and action timelines
- Email brief with "If you only do one thing this week" action

### Current Pricing Tiers

| Tier | Price | Target Customer | Description |
|------|-------|-----------------|-------------|
| **Founding Member** | $99/month | Early adopters, BG2+ | Beta-validated rate, includes feedback commitment |
| **Standard** (planned) | $100-150/month | Mid-market nonprofits ($500K-$3M budget) | Full monthly report + support |
| **Premium** (future) | $200-300/month | Larger nonprofits needing more customization | Enhanced research, more foundations, concierge support |

### Report Delivery Format
- **Primary:** Monthly PDF report emailed to client
- **Supplementary:** Email brief with urgent actions
- **Optional:** Excel tracker for deadline management
- **Future:** Web dashboard access (planned)

---

## 2. Pricing Evolution

### Initial Pricing Ideas Considered

**Option A: Per-Report Pricing ($250-500 per report)**
- Pros: Simple, no commitment required
- Cons: Unpredictable revenue, high per-transaction friction
- Status: REJECTED - clients prefer predictable costs

**Option B: Tiered Annual Plans ($1,200-$6,000/year)**
- Pros: Larger commitments, better retention
- Cons: High upfront cost for smaller nonprofits
- Status: DEFERRED - may introduce annual option with discount later

**Option C: Monthly Subscription ($99-150/month)**
- Pros: Low barrier to entry, predictable revenue, monthly feedback loops
- Cons: Lower total commitment than annual
- Status: SELECTED as primary model

**Option D: Freemium with Premium Features**
- Pros: Large top-of-funnel
- Cons: Requires significant automation infrastructure
- Status: DEFERRED until automation built

### How We Arrived at $100/mo Founding Rate

**Competitive Analysis Informed the Range:**
- GrantWatch: $249/year ($21/month equivalent) - too low for our value
- Instrumentl: $1,000+/month ($12K+/year) - premium enterprise pricing
- Market gap: Quality matching at $100-200/month (50-70% less than Instrumentl)

**Beta Feedback Validated the Price:**
- Mariam (SNS) asked about pricing: "~$100/mo" was mentioned, **she didn't object**
- Terry (VetsBoats) call: Alec mentioned "$99 a month" as initial user price, Terry's reaction was **positive** ("sounds pretty good")
- No pushback or price objection from any beta participant

**Value Justification:**
- One successful grant = $25,000-$500,000+ in funding
- $100/month = $1,200/year investment
- ROI: Even 1 small grant win = 20-100x return on subscription

### Beta Feedback on Pricing

**Mariam (SNS) - Direct Pricing Discussion:**
- Asked about pricing during feedback call
- $100/mo mentioned, no objection
- Also asked about grant writing concierge tier (interest in premium)

**Terry (VetsBoats) - Initial User Price Reaction:**
- Alec: "Right now, we're doing it for 99 a month"
- Terry: "That sounds pretty good... I'd like to have Matt talk with you"
- No price negotiation or objection

**Andy (RHF):**
- No direct pricing discussion
- Valued organization/compilation aspect
- Implied willingness to pay for "having it all in one place"

**Consuelo (PSMF):**
- No direct pricing discussion
- Focus was on report format (foundation-focused vs. opportunity-focused)
- Spent "an hour today and then two hours yesterday with the current report" - indicating high engagement value

---

## 3. Unit Economics

### Cost to Serve One Client

| Cost Component | Current (Manual) | Target (Hybrid) |
|----------------|------------------|-----------------|
| **Research Time** | 40+ hours | <25 hours |
| **Researcher Cost** (at $50/hr) | $2,000 | $1,250 |
| **Compute/API Costs** | ~$5/month | ~$10/month |
| **Infrastructure** | ~$2/month | ~$5/month |
| **QA/Review** | 4-6 hours ($200-300) | 2-3 hours ($100-150) |
| **Total Cost per Client** | ~$2,200/month | ~$1,400/month |

**Note:** Current manual model is unsustainable. Hybrid automation is required for positive unit economics.

### Margin Targets

| Scenario | Revenue | COGS | Gross Margin |
|----------|---------|------|--------------|
| **Current (Manual)** | $99 | ~$2,200 | -2,100% (unsustainable) |
| **Target (Hybrid - 70% automated)** | $125 | ~$40 | 68% |
| **Scale (500+ clients)** | $125 | ~$25 | 80% |

### Break-Even Analysis

**At $125/month per client, with Hybrid Model:**
- Fixed costs (team, infrastructure): ~$25,000/month
- Variable cost per client: ~$40/month
- Contribution margin: $85/client/month
- Break-even: ~295 clients

**Path to Break-Even:**
- Month 3: 30 clients ($3,750 MRR)
- Month 6: 60 clients ($7,500 MRR)
- Month 12: 150 clients ($18,750 MRR)
- Month 18: 300 clients ($37,500 MRR) - at break-even

### Scalability Considerations

**Current Blockers:**
- 100% manual research = cannot scale beyond 5-10 clients
- 40+ hours per organization research time
- High dependency on researcher capacity

**Automation Requirements for Scale:**
- Automated matching engine (Tier 1-2 matching)
- Current grants scraping pipeline (500+ opportunities)
- Standardized report generation
- Target: 70% automated, 30% manual validation

**Scale Targets:**

| Stage | Clients | Team Size | Revenue |
|-------|---------|-----------|---------|
| Beta | 3-6 | 1 | <$1K |
| Pilot | 15-30 | 2-3 | $1.5K-$3K |
| Growth | 60-100 | 4-5 | $6K-$10K |
| Scale | 200-500 | 6-8 | $20K-$50K |
| Mature | 500-1,000 | 8-12 | $50K-$100K |

---

## 4. Customer Acquisition

### Cold Call Results

| Metric | Value | % |
|--------|-------|---|
| Total Prospects | 200 | 100% |
| Prospects Called | 50 | 25% |
| Conversations | 14 | 28% connection rate |
| Decision Makers Reached | 4 | 8% |
| Interested (Yes/Maybe) | 3 | **6% interest rate** |
| BG1 Members from Calls | 3 | - |
| Remaining to Call | 150 | 75% |

**Key Insight:** Cold calls significantly outperform cold email (6% vs 0.23% interest rate). Calls require 12.5 calls per decision maker reached, 17 calls per interested prospect.

### Cold Email Results

| Metric | Value | % |
|--------|-------|---|
| Total Sent | 1,844 | 100% |
| Delivered | 1,731 | 93.9% |
| Bounced | 113 | 6.1% |
| Positive Replies | 4 | **0.23% response rate** |
| BG1 Members from Email | 2 | - |
| BG2 Members from Email | 1 | - |

**Benchmarks:**
- Deliverability: 93.9% (Good - industry avg ~85%)
- Response Rate: 0.23% (Low - cold email avg ~1-5%)

### Conversion Funnel

```
COLD CALLS:
Prospects: 200
    ↓ 25% contacted
Called: 50
    ↓ 28% connected
Conversations: 14
    ↓ 29% reached DM
Decision Makers: 4
    ↓ 75% interested
Interested: 3 (6% of called)
    ↓ TBD
Beta Users: 3

COLD EMAIL:
Sent: 1,844
    ↓ 93.9% delivered
Delivered: 1,731
    ↓ 0.23% replied
Interested: 4
    ↓ TBD
Beta Users: 3
```

### CAC Estimates

**Current (Beta - Manual Outreach):**
- Hours spent on outreach: ~40 hours
- Cost (at $50/hr equivalent): $2,000
- Beta users acquired: 6
- CAC: ~$333 per beta user

**Projected (Scaled - Automated + Sales):**
- Email automation cost: ~$100/month
- Sales time per closed client: 2-3 hours
- Marketing content: ~$200/month
- Target CAC: <$500 per paying client

### What Messaging Worked

**Effective (from calls and positive responses):**
- "Predict which foundations are most likely to fund you"
- "Data analytics + AI on IRS Form 990 data"
- "Monthly reports with actionable to-do lists"
- "Find opportunities you didn't know about"
- "$99/month for personalized grant matching"

**Less Effective:**
- Generic "grant writing help" positioning
- Features without ROI context
- Long-form email without clear CTA

---

## 5. Revenue Projections

### 30/60/90 Day Targets

| Timeframe | Clients | MRR | Cumulative Revenue |
|-----------|---------|-----|-------------------|
| Day 30 | 6-10 | $600-$1,000 | $600-$1,000 |
| Day 60 | 15-25 | $1,500-$2,500 | $2,700-$4,500 |
| Day 90 | 30-40 | $3,000-$4,000 | $7,200-$11,000 |

### Path to Sustainability

| Milestone | Clients | MRR | Timeline |
|-----------|---------|-----|----------|
| Beta Complete | 6 | $0 | Done (Dec 2025) |
| First Paying | 1 | $99 | Dec 2025 |
| Validation | 15 | $1,500 | Jan 2026 |
| Product-Market Fit | 50 | $5,000 | Mar 2026 |
| Sustainability | 150 | $15,000 | Jun 2026 |
| Break-Even | 300 | $30,000 | Dec 2026 |
| Scale | 500+ | $50,000+ | 2027 |

### Assumptions Behind Projections

**Conversion Assumptions:**
- Cold call interest rate: 6% (validated)
- Cold email response rate: 0.5% (improved with iteration)
- Beta → Paid conversion: 50%
- Trial → Paid conversion: 30%
- Monthly churn: 5%
- Annual retention: 80%

**Operational Assumptions:**
- Hybrid automation built by Feb 2026
- Research time drops to <25 hours by Mar 2026
- Current opportunities database reaches 500+ by Feb 2026
- QA pass rate improves to 70%+ by Feb 2026

**Market Assumptions:**
- No major competitor price drops
- Continued nonprofit sector growth
- Foundation giving remains stable or grows

---

## 6. Model Iterations Considered

### Annual Calendar Model (Mariam's Suggestion)

**What it was:**
- Instead of weekly/monthly reports, provide an annual grant calendar
- 3 strategic alerts per year (vs. 12 monthly reports)
- Focus on major deadlines and relationship-building moments

**Why we considered it:**
- Mariam (SNS) suggested this: "the way you broke down the work ensures no action is overlooked"
- Experienced grant writers don't need weekly reports - they need strategic reminders
- Reduces operational burden (3 deep dives vs. 12 lighter reports)

**Why rejected/deferred:**
- Works for "Calendar Manager" customer type but not "Niche Seekers" or "Relationship Builders"
- Harder to charge monthly subscription for 3 annual deliverables
- May offer as premium annual tier later
- Status: **DEFERRED** - may introduce as annual plan option ($800-1,000/year with 3 deep reports)

### Per-Report Pricing

**What it was:**
- Charge $250-500 per report instead of monthly subscription
- Client requests reports as needed
- Higher per-unit price, lower commitment

**Why we considered it:**
- Simple to understand and price
- No ongoing obligation for either party
- Some consultants charge $1,000+ per comprehensive report

**Why rejected:**
- Unpredictable revenue stream
- Higher friction per transaction
- Clients may delay purchases
- Doesn't build recurring relationship
- Status: **REJECTED** - subscription provides better economics and relationship

### Concierge/Grant Writing Tier

**What it was:**
- Premium tier that includes actual grant writing assistance
- Not just matching and intelligence, but draft proposals
- $300-500/month or per-project pricing

**Why we considered it:**
- Mariam (SNS) directly asked: "Asked about grant writing concierge tier"
- Natural upsell from matching service
- Higher margins per client
- Some clients have time constraints, not just knowledge gaps

**Why rejected/deferred:**
- Significantly different service (writing vs. research)
- Higher liability and time commitment
- Requires different skill set (grant writers vs. researchers)
- Would delay core product development
- Status: **DEFERRED** - Phase 2 expansion after core model validated

### Foundation-Focused vs. Opportunity-Focused Reports

**What it was:**
Two distinct report approaches:
1. **Opportunity-focused:** Current grants with deadlines, requirements, positioning (for orgs ready to apply now)
2. **Foundation-focused:** Foundation profiles for relationship building, LOI prospecting (for orgs building relationships)

**Why we considered it:**
- Consuelo (PSMF) explicitly requested foundation-focused approach
- "Prefers ~5 foundations with relationship-building info"
- "Prefers LOI/inquiry format over formal applications"
- Different customer types have different needs

**Current decision:**
- **Testing both approaches** in BG1 Report 2
- May offer as client preference toggle
- Status: **IN TESTING** - will standardize based on feedback

---

## 7. Customer Types and Pricing Implications

### Three Customer Types Identified

| Type | Characteristics | What They Want | Price Sensitivity |
|------|-----------------|----------------|-------------------|
| **Calendar Managers** | Experienced grant writers, know most opportunities | Organization, reminders, nothing overlooked | Lower - already have processes, value efficiency |
| **Niche Seekers** | Looking outside usual sources | Discovery of new/unexpected funders | Medium - value depends on discovery quality |
| **Relationship Builders** | Prefer prospecting over formal applications | Foundation profiles, LOI strategy, networking info | Higher - willing to pay for relationship intelligence |

### Pricing Implications by Customer Type

**Calendar Managers (Andy, Mariam):**
- Would pay $75-100/month for organization and reminders
- May prefer annual calendar model
- Potential tier: "Essentials" at $75/month

**Niche Seekers (Ka Ulukoa):**
- Would pay $100-150/month for discovery value
- Need geographic and sector-specific matching
- Potential tier: "Standard" at $125/month

**Relationship Builders (Consuelo):**
- Would pay $150-200/month for foundation intelligence
- Value board connections, giving patterns, networking info
- Potential tier: "Premium" at $175/month

---

## 8. Source Files

### Outreach Data
- `/mnt/c/TheGrantScout/4. Sales & Marketing/OUTREACH_PIPELINE_REPORT.md`

### Beta Feedback
- `/mnt/c/TheGrantScout/2. Beta Testing/2. Feedback/DATA_2025-12-03_feedback_andy_rhf.txt`
- `/mnt/c/TheGrantScout/2. Beta Testing/2. Feedback/DATA_2025-12-03_feedback_consuelo_psmf.txt`
- `/mnt/c/TheGrantScout/2. Beta Testing/2. Feedback/REPORT_2025-12-03_feedback_consuelo_psmf_summary.md`

### Pricing Discussions
- `/mnt/c/TheGrantScout/THEGRANTSCOUT_SUMMARY 2025-12-5.md` (Sections 10-11)
- `/mnt/c/TheGrantScout/2. Beta Testing/1. Reports/Project Analysis/Project Analysis 1 2025-11-30/REPORT_2025-11-30.6_round2_recommendations.md` (Section: GAP 9 - No Defined Pricing Model)

### Call Transcripts
- `/mnt/c/TheGrantScout/4. Sales & Marketing/Sales Calls/2025-12-4 VetsBoats/Call with Terry 2025-12-4.md`

---

## Appendix: Key Quotes

**Mariam (SNS) on value:**
> "The way you broke down the work ensures no action is overlooked."

**Andy (RHF) on organization:**
> "Info organized in one place was valuable even though he already knew the opportunities."

**Consuelo (PSMF) on foundation approach:**
> "Wants ~5 foundations with relationship-building info"
> "Prefers LOI/inquiry format over formal applications"

**Terry (VetsBoats) on pricing:**
> [After hearing "$99 a month"]: "Sounds pretty good... I'd like to have Matt talk with you."

---

*Document Prepared: December 8, 2025*
*Status: SPEC - Living Document*
*Last Updated: 2025-12-08*
