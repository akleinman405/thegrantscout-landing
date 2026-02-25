# Cold Email Strategy Research + Prospect Profile Spec

**Date:** 2026-02-16
**Prompt:** PROMPT_2026-02-16_cold_email_strategy_and_profiles.md
**Status:** Complete
**Owner:** Aleck Kleinman

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial version: 3-agent parallel research + synthesis |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. ["Give First" Strategy Assessment](#2-give-first-strategy-assessment)
3. [Cold Email Strategy Brief](#3-cold-email-strategy-brief)
4. [Ethical Line Guidance](#4-ethical-line-guidance)
5. [Angle Catalog](#5-angle-catalog)
6. [Data Requirements Map](#6-data-requirements-map)
7. [Prospect Profile Spec](#7-prospect-profile-spec)
8. [A/B Testing Plan](#8-ab-testing-plan)
9. [Files Created/Modified](#files-createdmodified)
10. [Notes](#notes)

---

## 1. Executive Summary

### 5 Key Insights

1. **"Give first" works in cold email, but only when bespoke.** Generic freebies trigger suspicion. Personalized foundation matches with real names and verifiable dollar amounts trigger reciprocity and demonstrate competence. Personalized cold emails achieve 10-25% reply rates vs. 1-5% for generic approaches. The email itself must contain the value, not offer to send it later.

2. **Peer Funder Discovery is the #1 angle for nonprofits.** "We found 47 foundations that fund organizations like yours but have never funded you. Here are the top 5." It scored 14/15 on our composite rating (highest of 20 angles evaluated). The data exists for 451,823 nonprofits, it is fully SQL-automatable, the upsell is natural ("subscribe for the full 47"), and there is zero ethical risk.

3. **The government funding cuts angle should NOT lead.** It ranked 20th of 20 angles (composite score: 7). Highest ethical risk. We cannot name specific federal programs from our database (only aggregate government_grants_amt). The crisis framing risks ambulance-chaser perception in a small, connected sector. Use it as context in follow-up emails after the prospect engages, never in the first touch.

4. **Email availability is the binding constraint.** Nonprofits: zero email addresses in np2. Foundations: 10,092 emails (7.1%). Phone coverage is strong (96.4% for foundations, 100% for nonprofits), but our pipeline is designed for email. The enrichment pipeline (Trestle reverse phone at $0.07/query, Candid at $1,200/year) must run before campaigns can scale.

5. **Small cohorts (under 50 prospects) get 2.76x the reply rate of mass blasts.** Segment by state + NTEE sector + budget band. Send Tuesday-Wednesday, 9-11 AM local time. Plain text, 50-80 words, zero images, 0-1 links. Three-touch sequence (Day 0, 3, 10). Never send more than 3 emails.

### 3 Recommended Actions

1. **Immediate (Week 1):** Run the enrichment pipeline. Backfill app_contact_email to fp2 (10,092 foundation emails). Begin Trestle reverse phone pilot (1,000 records, ~$70) to validate email match rates.

2. **First 90 days:** Launch A/B tests with the top 3 nonprofit angles (Peer Funder Discovery, New Funders Entering Your Space, Lapsed Funder Re-engagement) and top 2 foundation angles (New Grantee Discovery, Grantee Portfolio Health). Start with 50-prospect cohorts per angle. Target: 5%+ positive reply rate.

3. **Parallel track:** Build the prospect profile views (Section 7 DDL) so the AI email generator has structured context. Pre-compute angle-specific data for the top 5,000 prospects per angle.

### 1 "Don't Pursue" Recommendation

**Do not lead with the government funding cuts angle in cold email.** Reserve it for warm follow-ups and content marketing. The ethical risk, data limitations (cannot name specific programs), and shelf life make it a poor first-touch strategy. The Peer Funder Discovery angle achieves the same goal (connecting vulnerable nonprofits with alternative funders) without referencing the crisis.

---

## 2. "Give First" Strategy Assessment

### Does "Give First" Work in Cold Email?

**Yes, but it requires fundamental adaptation from social media/content marketing.**

The core mechanism, reciprocity, functions even with strangers. Cialdini's research confirms that unsolicited favors create felt obligation. A 2007 study (Gamberini) found users who received content before being asked submitted higher-quality data than those asked upfront. But cold email introduces a consent gap: social media followers opted in; cold email recipients did not. This consent gap transforms the psychology.

### Evidence FOR

| Finding | Impact | Source |
|---------|--------|--------|
| MailShake case study: value-first approach achieved 30% reply rate from 206 prospects | 6x typical cold email reply rate | MailShake |
| SaaS startup: 400 value-first emails via Smartlead booked 61 demos (15.25% conversion) | Demonstrates scale viability | Floworks |
| Personalized cold emails: 20-40% open rates, 10-25% response rates | 5-10x generic approach | Martal Group, Digital Bloom |
| Hyper-personalized emails hitting 40-60% reply rates in 2025-2026 | Top performers pulling further ahead | SalesHandy |
| Nonprofits lead all sectors with reply rates exceeding 16.5% | Sector-specific advantage for TGS | Martal Group |
| Email marketing in nonprofit sector returns $36 per $1 spent | Higher ROI than most sectors | Bloomerang |

### Evidence AGAINST

| Finding | Impact | Mitigation |
|---------|--------|------------|
| Nielsen Norman Group: requests from unknown senders create suspicion | Generic freebies backfire | Make value bespoke, not broadcast |
| "Reciprocity anxiety": uninvited favors create unwanted obligation | Rich unsolicited gifts increase suspicion | Share an insight (2-3 bullets), not a deliverable (20-page report) |
| Commercial intent detectors: brain pathways that spot sales pitches | Lead magnets feel like traps | Make value unconditional and immediately verifiable |
| Nonprofit EDs receive 40+ vendor emails daily | Default behavior is ignore/delete | Stand out with personalized, sector-specific data |
| Phishing attacks targeting nonprofits increasing | Trust in unknown senders eroding | Plain text from a real person's name, not "TheGrantScout Team" |

### 5 Adaptation Principles

**Principle 1: Bespoke beats broadcast.** Do not send a generic "Guide to Foundation Funding." Send: "I found 3 foundations that gave $50K+ to organizations like yours in the past 2 years. Here are their names." The personalization must reference their specific state, sector, and situation.

**Principle 2: Give the insight, not the deliverable.** Share enough to be genuinely useful, not so much there is nothing left to discuss. Name 2-3 specific foundations with recent grant amounts. Do not include contact info, application deadlines, or positioning strategy. That is the paid product.

**Principle 3: Value must be immediately verifiable.** The recipient must be able to confirm the insight is real within 30 seconds. Use real foundation names, real grant amounts, real NTEE codes. Every claim must be checkable by Googling the foundation name.

**Principle 4: Keep it under 125 words.** Research consistently shows that concise, credible emails under 125 words outperform longer messages. Do not attach a 20-page report. Share 2-3 bullet points and offer to share more.

**Principle 5: Follow up with new value, not reminders.** Each of 3 follow-ups should contain a new foundation match, sector trend, or data point. Never send "just checking in." Follow-ups with new value improve reply rates by 20%.

### Nonprofit/Foundation-Specific Considerations

Trust violations hurt nonprofits disproportionately. University of Queensland research found that while consumers trust nonprofits more than commercial organizations, trust drops more sharply when a nonprofit-adjacent entity violates trust vs. a purely commercial one. Higher baseline receptivity, higher reputational stakes.

The sector runs on word of mouth. One ED sharing a tone-deaf email screenshot on LinkedIn can poison an entire subsector. Foundation program officers operate behind institutional firewalls and have sophisticated pitch filters. Our "give first" approach must demonstrate deep portfolio knowledge, not product features.

---

## 3. Cold Email Strategy Brief

### Benchmark Summary (2025-2026)

| Metric | Average | Good | Top 10% | Source |
|--------|---------|------|---------|--------|
| Open rate | 27.7% | 45%+ | 50%+ | Snovio, Martal |
| Reply rate (all) | 3.4-5.1% | 5.5-10% | 10.7%+ | Instantly 2026 |
| Positive reply % | 48-53% of replies | 61-65% | 65%+ | Digital Bloom |
| Positive reply rate | ~1.7% | ~4% | ~6.5% | Calculated |
| Meeting/booking rate | 0.69% | 1.25-1.86% | 2.34% | Digital Bloom |
| Bounce rate | 7-8% | Under 3% | Under 2% | Instantly 2026 |

**TGS target: 5%+ positive reply rate** (above "good," approaching top 10%). Achievable with L3 personalization + small cohorts + nonprofit sector advantage.

### Hook Type Performance

| Hook Type | Reply Rate | Positive Reply % | Meeting Rate | vs. Baseline |
|-----------|-----------|-------------------|-------------|--------------|
| Timeline ("Since you recently...") | 10.01% | 65.36% | 2.34% | 2.3x |
| Numbers ("X% of orgs like yours...") | 8.57% | 61.76% | 1.86% | 1.95x |
| Social proof ("Org X achieved...") | 6.53% | 53.44% | 1.25% | 1.49x |
| Problem ("Struggling with...") | 4.39% | 48.30% | 0.69% | Baseline |

**TGS implication:** Use timeline hooks ("3 new foundations started funding [sector] in [state] this year") and numbers hooks ("47 foundations fund your peers but not you"). Avoid problem hooks ("struggling with funding"). The data directly supports our angle ranking.

### Subject Line Rules

| Rule | Evidence |
|------|----------|
| 4-7 words (30-40 characters) | Under 40 chars = 37% higher open rates |
| Include recipient's first name | 43% reply rate lift |
| Lowercase, no punctuation tricks | ALL CAPS and !! trigger spam filters |
| Reference something specific | Industry-specific = 73% more opens |
| Questions outperform statements | 21% higher open rate |
| Include numbers when relevant | 113% increase using numbers |

**TGS subject line templates (nonprofit):**

- "{FirstName}, 5 foundations matching {OrgName}"
- "3 new funders for [sector] nonprofits in [state]"
- "[Foundation Name] hasn't funded you since 2020"

**TGS subject line templates (foundation):**

- "{FirstName}, a question about {FoundationName}'s grantees"
- "5 organizations matching your giving pattern"

### Email Structure

| Element | Specification |
|---------|--------------|
| Format | Plain text only (HTML bounces 652% more) |
| Total words | 50-80 (sweet spot from Instantly 2026) |
| Links | 0-1 maximum |
| Images | None |
| Signature | Minimal plain text (rich signatures reduce replies 23%) |
| Tracking pixels | Avoid (10-15% lower reply rates) |

**Template:**

```
[PERSONALIZED HOOK - 1 sentence, 10-15 words]
References something specific from their grant history.

[VALUE BRIDGE - 1-2 sentences, 20-30 words]
The actual insight: 2-3 foundation names with amounts.

[SOFT CTA - 1 sentence, 10-15 words]
"Worth a quick look?" or "Would the full list help?"

Name
TheGrantScout
```

### 3-Touch Cadence

| Touch | Day | Content | Expected Impact |
|-------|-----|---------|-----------------|
| Email 1 | Day 0 | Initial hook + 2-3 foundation matches | 58% of all replies |
| Email 2 | Day 3 | New angle or additional data point | +60% cumulative lift |
| Email 3 | Day 10 | Ultra-short breakup + different value | 93% of total replies captured |

**Do not send Touch 4+.** Beyond 3 emails, unsubscribes exceed new replies.

**Timing:** Tuesday-Wednesday, 9-11 AM recipient's local time. Consistent daily send volume (erratic patterns flag spam filters).

### Personalization Framework

| Level | What It Includes | Reply Rate Lift | TGS Use |
|-------|-----------------|----------------|---------|
| L0: None | Generic blast | Baseline (3.4%) | Never |
| L1: Merge tags | First name, company name | +5-15% | Minimum |
| L2: Role/industry | Title, sector reference | +20-25% | Good |
| L3: Situation-specific | Recent event, specific data point | +25-35% | **Target** |
| L4: Deep research | Custom analysis, peer comparison | +35-52% | Premium prospects only |

**TGS operates at L3** for standard outreach (state, NTEE sector, specific grant data from their 990) and L4 for high-value foundation prospects (portfolio analysis, co-funder map).

**The personalization comfort band:** Reference what a knowledgeable peer in the sector would naturally know. Our edge is 990 data and grant history, which is public record and feels like domain expertise, not stalking.

| Feels Helpful | Feels Creepy |
|---------------|-------------|
| "You fund 23 youth development orgs in CA" | "I saw you were at the NCFP conference" |
| "Your peer org received a $50K grant from X" | "Your ED makes $85K and your budget gap is $200K" |
| "Orgs like yours in Hawaii struggle to find local funders" | "I noticed you liked a LinkedIn post about grantee sustainability" |

### Segmentation Multiplier

Campaigns targeting cohorts under 50 achieve 5.8% reply rates vs. 2.1% for blasts of 1,000+, a 2.76x multiplier (Digital Bloom 2025). Segment by: state + NTEE sector + budget band. Example: "California youth development orgs with $500K-$2M revenue."

### Top 10 Things That Destroy Cold Emails

| # | Mistake | Impact |
|---|---------|--------|
| 1 | No SPF/DKIM/DMARC | Rejected outright by Gmail/Yahoo since Nov 2025 |
| 2 | Sending from primary domain | Domain reputation damage affects all company email |
| 3 | HTML formatting, images, rich signatures | 652% higher bounce rate |
| 4 | Tracking pixels | 10-15% lower reply rates |
| 5 | Multiple links | Triggers phishing detection |
| 6 | Spam trigger words: "free," "guarantee," "act now" | 67% more likely to hit spam |
| 7 | Erratic send volume | Mimics bot behavior |
| 8 | Skipping domain warm-up | Need 4-6 weeks at 5-10/day ramping |
| 9 | Emails over 150 words | 52% booking rate at 120 words vs. 20% at 300+ |
| 10 | Selling in the first touch | Cold emails open conversations, not close deals |

---

## 4. Ethical Line Guidance

### The Ambulance Driver Framework

Michael Smith (cybersecurity vendor) distinguishes between "ambulance chasers" and "ambulance drivers":

- **Ambulance chasers** see a crisis and rush to sell. They show up with a bill of materials. They use the crisis as leverage.
- **Ambulance drivers** see a crisis and pull over to check if anyone needs help. They do not push. If everybody is OK, that is a good thing. They ask before they offer.

Nonprofit EDs maintain blacklists of vendors perceived as profiting from crises. Once on the blacklist, recovery is extremely difficult. TheGrantScout's email should feel like pulling over to offer help, not chasing the ambulance.

### 7 Rules for Crisis Outreach

**Rule 1: Lead with the solution, not the wound.** Open with what you can offer, not what they lost. "We identified 5 foundations actively funding [sector] organizations in [state]" is fundamentally different from "We know your federal funding was just cut."

**Rule 2: Never reference specific cuts unless the recipient did first.** Do not say "We saw that HHS terminated your grant." Even if public, it feels like surveillance. Present opportunity, not diagnosis.

**Rule 3: Make the value unconditional.** The free insight should be useful whether or not they subscribe. Do not gate it behind a demo or reply. The email body contains the actionable insight.

**Rule 4: Price the service the same as before the crisis.** Do not create "crisis pricing." TheGrantScout's $99/month was set before the cuts. Maintaining that price signals non-exploitation.

**Rule 5: Acknowledge context with restraint.** Appropriate: "the current funding environment" or "changes in federal grant programs." Not appropriate: dramatize, catastrophize, or use emotional language.

**Rule 6: Pass the "worst day" test.** If the recipient reads this email on the day they laid off half their staff, does it feel like solidarity or sales? If any doubt, revise.

**Rule 7: Offer to help even if they cannot pay.** "If budget is a concern right now, reply and we will share what we can at no cost." Both ethical and strategic.

### What NOT to Say

**The Voyeur:** "We noticed your organization lost $2.3M in federal funding when HHS terminated DEI-related grants. That must be devastating." Fails Rules 1, 2, 6.

**The Fear Amplifier:** "With $863B in Medicaid cuts, nonprofits like yours face an existential threat. The organizations that survive will be the ones that diversify NOW." Fails Rules 3, 5, 6.

**The Data Stalker:** "Our analysis shows that [Org Name] receives 73% of revenue from government sources and has only 1 foundation grant on record. That's a critical vulnerability." Fails Rules 1, 2.

**The Guilt Trip:** "26,257 nonprofits are in the same situation. Most will wait too long to act. Will you join our subscribers who are already finding new funders?" Fails Rules 2, 3, 6.

### What TO Say

**The Specific Gift:**
> Subject: 3 foundations funding [sector] work in [state]
>
> Hi [Name], I research foundation funding patterns for nonprofits. In looking at [state]'s [sector] landscape, I found three foundations that gave $50K+ grants to organizations similar to [Org Name] in the past two years:
> - [Foundation A]: $75K to [similar org] for [purpose]
> - [Foundation B]: $60K to [similar org] for [purpose]
> - [Foundation C]: $52K to [similar org] for [purpose]
>
> I can share more detail on their application processes if useful. No obligation.

**The Sector Context:**
> Subject: Foundation funding trends in [sector]
>
> Hi [Name], Foundation giving to [sector] nonprofits in [state] totaled $[X]M in 2024, up [X]% from 2022. Several foundations have expanded their [sector] portfolios recently.
>
> I pulled together a short list of the most active funders in your area. Happy to share it, just reply.

**The Community Builder:**
> Subject: [Sector] foundation funding, free resource
>
> Hi [Name], We have been tracking which private foundations are most actively funding [sector] work in [state/region]. Given how much the funding landscape is shifting, we thought this might be useful.
>
> Top 5 foundations by grant volume in your sector:
> [1-line summary each: name, total giving, focus area]
>
> We publish these analyses monthly. Happy to add you to the list, no strings.

### Reputation Risk Assessment

**Risk level: Moderate, manageable with discipline.**

| Factor | Assessment |
|--------|-----------|
| Sector size | Small, interconnected. Word of mouth dominant. |
| Brand maturity | New, unknown. Less benefit of the doubt. |
| Crisis sensitivity | Ongoing. Organizations currently laying off staff. |
| Product relevance | Genuinely relevant (unlike "web hosting company emailing about COVID") |
| Price point | $99/month is modest, not exploitative |
| Data advantage | Real and verifiable, not manufactured |

**Safeguards:** Review every email against the 7-rule framework. Start with 50-100 emails. Monitor for negative sentiment. If >5% of replies are negative, pause and revise. Never use "crisis" in subject lines. Build public credibility in parallel (free LinkedIn content, sector reports).

---

## 5. Angle Catalog

### Full Ranked Catalog (20 Angles)

All angles rated on 4 dimensions. Composite = (Data + Scalability + Upsell) - Ethical Risk.

| Rank | # | Angle Name | Buyer | Data | Scale | Upsell | Ethics | Composite |
|------|---|-----------|-------|------|-------|--------|--------|-----------|
| 1 | 6 | **Peer Funder Discovery** | NP | 5 | 5 | 5 | 1 | **14** |
| 2 | 1 | State/Sector Foundation List | NP | 5 | 5 | 4 | 1 | 13 |
| 3 | 7 | New Funders Entering Your Space | NP | 5 | 5 | 4 | 1 | 13 |
| 4 | 8 | Lapsed Funder Re-engagement | NP | 4 | 5 | 5 | 1 | 13 |
| 5 | 9 | Rising Star Funders | NP | 5 | 5 | 4 | 1 | 13 |
| 6 | 20 | New Grantee Discovery | FDN | 5 | 4 | 5 | 1 | 13 |
| 7 | 3 | Benchmark Data | NP | 4 | 5 | 5 | 2 | 12 |
| 8 | 10 | Underserved Org Alert | NP | 4 | 5 | 5 | 2 | 12 |
| 9 | 14 | Grantee Portfolio Health | FDN | 5 | 4 | 5 | 2 | 12 |
| 10 | 13 | Co-Funder Network Map | FDN | 5 | 3 | 4 | 1 | 11 |
| 11 | 15 | Peer Foundation Benchmarking | FDN | 5 | 5 | 3 | 2 | 11 |
| 12 | 16 | Sector Trend Report | FDN | 4 | 5 | 3 | 1 | 11 |
| 13 | 18 | Grantee Overlap / Shared Grantees | FDN | 5 | 3 | 4 | 1 | 11 |
| 14 | 19 | Concentration Risk Alert | FDN | 5 | 5 | 3 | 3 | 10 |
| 15 | 11 | Foundation Deadline Calendar | NP | 3 | 3 | 4 | 1 | 9 |
| 16 | 12 | Board Connection Finder | NP | 4 | 2 | 5 | 2 | 9 |
| 17 | 5 | Grantee Exposure Summary | FDN | 4 | 4 | 4 | 3 | 9 |
| 18 | 4 | Grantee Impact Brief | FDN | 3 | 3 | 5 | 3 | 8 |
| 19 | 17 | Gap Analysis | FDN | 4 | 3 | 3 | 2 | 8 |
| 20 | 2 | Government Funding Cut Alert | NP | 3 | 3 | 5 | 4 | 7 |

### Top 3 Nonprofit Angles (First 90 Days)

#### #1: Peer Funder Discovery (Composite: 14)

**Pitch:** "We found 47 foundations that fund organizations like yours in [state] but have never funded you. Here are the top 5."

**Why #1:** Highest composite score. 451,823 targetable nonprofits. Pure SQL automation. Directly demonstrates our core value proposition: surfacing funders they did not know about. Zero ethical risk.

**"Give first" deliverable:** 5 foundations that fund their peers but not them. Each entry: foundation name, state, median grant, 5-year giving, giving trend.

**Data pipeline:** Single SQL query per nonprofit. Batch-feasible for thousands in a single run.

```sql
SELECT fp.foundation_name, fp.state, cp.median_grant, cp.total_giving_5yr, cp.giving_trend
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_recipients dr ON fg.recipient_ein = dr.ein
JOIN f990_2025.foundation_prospects2 fp ON fg.foundation_ein = fp.ein
JOIN f990_2025.calc_foundation_profiles cp ON fp.ein = cp.ein
WHERE LEFT(dr.ntee_code, 1) = '[NP_SECTOR]' AND dr.state = '[NP_STATE]'
  AND fg.tax_year >= 2020 AND cp.accepts_applications = true
  AND fg.foundation_ein NOT IN (
    SELECT foundation_ein FROM f990_2025.fact_grants WHERE recipient_ein = '[NP_EIN]'
  )
ORDER BY cp.total_giving_5yr DESC LIMIT 5;
```

#### #2: New Funders Entering Your Space (Composite: 13)

**Pitch:** "3 new foundations started funding [sector] organizations in [state] this year."

**Why #2:** Forward-looking and positive. 116,089 new sector-entrant pairs since 2022. Creates urgency without crisis framing: "They're building their portfolios, so they're more open to new grantees."

**"Give first" deliverable:** 3 foundations that made first grants in the recipient's sector/state since 2022, with amounts, purposes, and giving trend.

#### #3: Lapsed Funder Re-engagement (Composite: 13)

**Pitch:** "[Foundation X] hasn't funded you since 2020. Here's what they're funding now."

**Why #3:** Most personalized angle. References real foundations the nonprofit has actual history with. 81,136 targetable nonprofits with 2+ lapsed funders. Cannot be ignored because it touches their own grant record.

**"Give first" deliverable:** 2-3 lapsed funders with last funded year, total received historically, current giving trend, and 3 recent grants from each.

### Top 3 Foundation Angles (First 90 Days)

#### #1: New Grantee Discovery (Composite: 13)

**Pitch:** "5 organizations matching your giving pattern that aren't on your radar yet."

**Why #1:** This IS our product for foundations. The sample directly demonstrates the paid offering. 69,674 foundations with $500K+ in 5-year giving. The simplified SQL version works for "give first" samples; full LASSO model produces better results.

#### #2: Grantee Portfolio Health Dashboard (Composite: 12)

**Pitch:** "27% of your grantees saw revenue decline last year. Here's a health summary."

**Why #2:** Novel intelligence no foundation currently has. Verified 86.5% grantee match rate for large foundations. Creates problem awareness that our service directly solves.

#### #3: Co-Funder Network Map (Composite: 11)

**Pitch:** "Your top 5 co-funders (foundations funding the same organizations you do)."

**Why #3:** Intelligence genuinely hard to get elsewhere. Verified with real data: one test foundation had 4,926 shared grantees with its top co-funder. Pre-computing for top 5,000 foundations is feasible.

### Angles to Avoid or Defer

| Angle | Why |
|-------|-----|
| Government Funding Cut Alert (#2) | Lowest composite (7). Highest ethical risk. Cannot name specific programs. Shelf life limited. |
| Foundation Deadline Calendar (#11) | Only 7,291 parseable deadlines (5%). High stale-data risk. |
| Board Connection Finder (#12) | 25M records to cross-reference. Computationally prohibitive for batch. |
| Gap Analysis (#17) | Prescriptive tone risks alienating foundations. Better for warm leads. |
| Grantee Impact Brief (#4) | Requires full matching pipeline per grantee. Labor-intensive per lead. |

---

## 6. Data Requirements Map

### Master Data Asset Inventory

| Asset | Records | Email Coverage | Key Use |
|-------|---------|---------------|---------|
| foundation_prospects2 (fp2) | 143,184 | 10,092 (7.1%) | Master foundation table |
| nonprofits_prospects2 (np2) | 673,381 | 0 (0%) | Master nonprofit table |
| fact_grants | 8,310,650 | N/A | Powers every "give first" angle |
| calc_foundation_profiles | 143,184 | N/A | Foundation analytics (trends, openness, sectors) |
| nonprofit_returns | 2,956,959 filings | N/A | Government vulnerability, revenue data |
| officers | 26,281,615 | N/A | Contact name inference |
| org_url_enrichment | 813,698 | N/A | URL validation pipeline |

### Per-Angle Data Requirements

#### Angle 6: Peer Funder Discovery (NP #1)

| Field | Source | Have It? | Quality | Priority |
|-------|--------|----------|---------|----------|
| Recipient NTEE code | np2.ntee_code | Partial (67.2%) | Clean | Must-have |
| Recipient state | np2.state | Yes (99.9%) | Clean | Must-have |
| Recipient EIN | np2.ein | Yes (100%) | Clean | Must-have |
| Foundation name | fp2.foundation_name | Yes (100%) | Clean | Must-have |
| Median grant | calc_foundation_profiles.median_grant | Yes (78.6%) | Clean | Must-have |
| 5yr giving total | calc_foundation_profiles.total_giving_5yr | Yes (78.6%) | Clean | Must-have |
| Giving trend | calc_foundation_profiles.giving_trend | Yes (78.6%) | Clean | Nice-to-have |
| Accepts applications | calc_foundation_profiles.accepts_applications | Yes (100%) | Clean | Must-have |
| **Recipient email** | **Not in np2** | **No** | **N/A** | **Must-have (blocking)** |
| Recipient contact name | np2.ed_ceo_name | Partial (21.2%) | Needs cleaning | Must-have |

#### Angle 7: New Funders Entering Your Space (NP #2)

| Field | Source | Have It? | Quality | Priority |
|-------|--------|----------|---------|----------|
| Foundation first grant in sector/state | fact_grants + dim_recipients | Yes (derivable) | Clean | Must-have |
| Grant purpose text | fact_grants.purpose_text | Yes (99.9%) | Clean | Nice-to-have |
| Foundation giving trend | calc_foundation_profiles.giving_trend | Yes (78.6%) | Clean | Must-have |
| **Recipient email** | **Not in np2** | **No** | **N/A** | **Must-have (blocking)** |

#### Angle 8: Lapsed Funder Re-engagement (NP #3)

| Field | Source | Have It? | Quality | Priority |
|-------|--------|----------|---------|----------|
| Prior funding history | fact_grants (recipient_ein match) | Yes | Clean | Must-have |
| Last funded year | fact_grants.tax_year | Yes | Clean | Must-have |
| Lapsed funder's current grants | fact_grants (recent) | Yes | Clean | Must-have |
| Foundation giving trend | calc_foundation_profiles | Yes | Clean | Must-have |
| **Recipient email** | **Not in np2** | **No** | **N/A** | **Must-have (blocking)** |

#### Angle 20: New Grantee Discovery (FDN #1)

| Field | Source | Have It? | Quality | Priority |
|-------|--------|----------|---------|----------|
| Foundation sector_focus | calc_foundation_profiles.sector_focus (JSONB) | Yes (70.2%) | Clean | Must-have |
| Foundation geographic_focus | calc_foundation_profiles.geographic_focus (JSONB) | Yes (70.2%) | Clean | Must-have |
| Existing grantee list | fact_grants | Yes | Clean | Must-have |
| Nonprofit mission | np2.mission_description | Yes (100%) | Clean | Must-have |
| Nonprofit revenue | nonprofit_returns.total_revenue | Yes | Clean | Must-have |
| **Foundation email** | **fp2.app_contact_email** | **Partial (7.1%)** | **Clean** | **Must-have (blocking)** |
| Foundation contact name | fp2.contact_name | Yes (98.1%) | Needs cleaning (77% ALL CAPS) | Must-have |

#### Angle 14: Grantee Portfolio Health (FDN #2)

| Field | Source | Have It? | Quality | Priority |
|-------|--------|----------|---------|----------|
| Foundation grantee list | fact_grants | Yes | Clean | Must-have |
| Grantee multi-year revenue | nonprofit_returns (2021 + 2023) | Yes (86.5% match) | Clean | Must-have |
| Grantee government_grants_amt | nonprofit_returns | Yes | Clean | Must-have |
| **Foundation email** | **fp2.app_contact_email** | **Partial (7.1%)** | **Clean** | **Must-have (blocking)** |

### Gap Analysis Summary

| Gap | Impact | Remediation | Cost | Timeline |
|-----|--------|-------------|------|----------|
| **NP email: 0%** | Cannot email nonprofits at all | Website scraping (85.9% have URLs) + Hunter.io enrichment | $5,000-$10,000 | 4-6 weeks |
| **FDN email: 7.1%** | Can only email 10,092 of 143K foundations | Trestle reverse phone ($6,420) + Candid ($1,200/yr) | $7,620 | 2-4 weeks |
| NP contact name: 21.2% | Limits personalization to "Hi there" for 79% | Officers table has 92.6% via np2.all_officers JSONB | $0 (data exists) | 1 day SQL |
| NP NTEE: 67.2% | 33% of NPs cannot be sector-matched | BMF table has 91,582 foundations; NP coverage is the gap | NLP on mission text | 1-2 weeks |
| FDN contact name quality | 77% ALL CAPS in officers table | Title-case conversion script | $0 | 1 hour |
| Govt program specificity | Cannot name which federal program was cut | Import 26,257 vulnerability scores from research files | $0 (data exists as files) | 1 day |
| Grant dates | Only tax_year, no exact dates | IRS filing limitation; cannot improve | N/A | N/A |

### Enrichment Cost Summary (from prior research)

| Method | Cost | Expected Contacts | Cost Per Contact |
|--------|------|-------------------|-----------------|
| Trestle reverse phone (85.6K queries) | $6,420 | 25,000-35,000 emails | $0.20-$0.28 |
| Candid subscription (annual) | $1,200 | 5,000-15,000 contacts | $0.08-$0.24 |
| Smarty address classification | $300 | Segmentation only | N/A |
| Apollo pilot (1,000 records) | $100 | 100-250 emails | $0.40-$1.00 |
| Physical mail (2,000 pieces) | $2,000 | 100-200 contacts | $10-$20 |
| **Total** | **$10,020** | **30,000-50,000** | **$0.21-$0.35** |

---

## 7. Prospect Profile Spec

### Design Principle

The prospect profile is consumed by an AI to generate personalized emails. It must be a flat, denormalized structure with clear field names that can be dropped into a prompt template. The AI needs: who they are, what they do, what their situation is, and what specific "give first" data powers the email.

### 7A. ALTER TABLE Statements (Extend fp2 and np2)

#### Foundation Prospects (fp2)

```sql
-- New columns for email campaign support
ALTER TABLE f990_2025.foundation_prospects2
  ADD COLUMN IF NOT EXISTS email_source VARCHAR(30),
  ADD COLUMN IF NOT EXISTS email_validated BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS email_validated_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS contact_name_clean TEXT,
  ADD COLUMN IF NOT EXISTS outreach_channel VARCHAR(20),
  ADD COLUMN IF NOT EXISTS outreach_priority INTEGER;

-- Backfill contact_name_clean (title-case from ALL CAPS)
UPDATE f990_2025.foundation_prospects2
SET contact_name_clean = INITCAP(LOWER(contact_name))
WHERE contact_name IS NOT NULL AND contact_name = UPPER(contact_name);

-- Set outreach channel based on available contact data
UPDATE f990_2025.foundation_prospects2
SET outreach_channel = CASE
  WHEN app_contact_email IS NOT NULL AND app_contact_email <> '' THEN 'email'
  WHEN app_contact_phone IS NOT NULL AND app_contact_phone <> '' THEN 'phone'
  WHEN phone_num IS NOT NULL AND phone_num <> '' THEN 'phone'
  ELSE 'mail'
END;

-- Set outreach priority based on data quality + foundation viability
UPDATE f990_2025.foundation_prospects2 fp2
SET outreach_priority = CASE
  WHEN fp2.app_contact_email IS NOT NULL
    AND cfp.has_grant_history AND cfp.accepts_applications
    AND cfp.total_giving_5yr > 500000 THEN 1
  WHEN cfp.has_grant_history AND cfp.accepts_applications
    AND cfp.total_giving_5yr > 100000 THEN 2
  WHEN cfp.has_grant_history AND cfp.total_giving_5yr > 50000 THEN 3
  ELSE 4
END
FROM f990_2025.calc_foundation_profiles cfp
WHERE fp2.ein = cfp.ein;
```

#### Nonprofit Prospects (np2)

```sql
-- New columns for email campaign support
ALTER TABLE f990_2025.nonprofits_prospects2
  ADD COLUMN IF NOT EXISTS contact_email VARCHAR(255),
  ADD COLUMN IF NOT EXISTS email_source VARCHAR(30),
  ADD COLUMN IF NOT EXISTS email_validated BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS email_validated_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS contact_name_clean TEXT,
  ADD COLUMN IF NOT EXISTS govt_grants_amt NUMERIC(15,2),
  ADD COLUMN IF NOT EXISTS govt_dependency_pct NUMERIC(5,2),
  ADD COLUMN IF NOT EXISTS total_revenue_latest NUMERIC(15,2),
  ADD COLUMN IF NOT EXISTS foundation_grant_count INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS lapsed_funder_count INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS peer_funder_count INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS outreach_channel VARCHAR(20),
  ADD COLUMN IF NOT EXISTS outreach_priority INTEGER;

-- Backfill contact name from ed_ceo_name (title-case)
UPDATE f990_2025.nonprofits_prospects2
SET contact_name_clean = INITCAP(LOWER(ed_ceo_name))
WHERE ed_ceo_name IS NOT NULL AND ed_ceo_name = UPPER(ed_ceo_name);

-- Backfill government grants data from most recent filing
UPDATE f990_2025.nonprofits_prospects2 np2
SET govt_grants_amt = sub.government_grants_amt,
    total_revenue_latest = sub.total_revenue,
    govt_dependency_pct = CASE
      WHEN sub.total_revenue > 0 THEN
        ROUND(sub.government_grants_amt::numeric / sub.total_revenue * 100, 1)
      ELSE NULL
    END
FROM (
  SELECT DISTINCT ON (ein) ein, government_grants_amt, total_revenue
  FROM f990_2025.nonprofit_returns
  WHERE government_grants_amt IS NOT NULL AND total_revenue > 0
  ORDER BY ein, tax_year DESC NULLS LAST
) sub
WHERE np2.ein = sub.ein;

-- Backfill foundation grant count
UPDATE f990_2025.nonprofits_prospects2 np2
SET foundation_grant_count = sub.cnt
FROM (
  SELECT recipient_ein, COUNT(DISTINCT foundation_ein) as cnt
  FROM f990_2025.fact_grants
  WHERE tax_year >= 2020
  GROUP BY recipient_ein
) sub
WHERE np2.ein = sub.recipient_ein;

-- Backfill lapsed funder count
UPDATE f990_2025.nonprofits_prospects2 np2
SET lapsed_funder_count = sub.cnt
FROM (
  SELECT fg1.recipient_ein, COUNT(DISTINCT fg1.foundation_ein) as cnt
  FROM f990_2025.fact_grants fg1
  WHERE fg1.tax_year BETWEEN 2018 AND 2020
    AND NOT EXISTS (
      SELECT 1 FROM f990_2025.fact_grants fg2
      WHERE fg2.foundation_ein = fg1.foundation_ein
        AND fg2.recipient_ein = fg1.recipient_ein
        AND fg2.tax_year >= 2022
    )
  GROUP BY fg1.recipient_ein
) sub
WHERE np2.ein = sub.recipient_ein;

-- Backfill peer funder count (foundations funding same sector/state, not this NP)
UPDATE f990_2025.nonprofits_prospects2 np2
SET peer_funder_count = sub.cnt
FROM (
  SELECT np.ein, COUNT(DISTINCT fg.foundation_ein) as cnt
  FROM f990_2025.nonprofits_prospects2 np
  JOIN f990_2025.fact_grants fg ON TRUE
  JOIN f990_2025.dim_recipients dr ON fg.recipient_ein = dr.ein
  JOIN f990_2025.calc_foundation_profiles cp ON fg.foundation_ein = cp.ein
  WHERE LEFT(dr.ntee_code, 1) = LEFT(np.ntee_code, 1)
    AND dr.state = np.state
    AND fg.tax_year >= 2020
    AND cp.accepts_applications = true
    AND fg.foundation_ein NOT IN (
      SELECT foundation_ein FROM f990_2025.fact_grants WHERE recipient_ein = np.ein
    )
  GROUP BY np.ein
) sub
WHERE np2.ein = sub.ein;

-- Set outreach channel
UPDATE f990_2025.nonprofits_prospects2
SET outreach_channel = CASE
  WHEN contact_email IS NOT NULL AND contact_email <> '' THEN 'email'
  WHEN website IS NOT NULL AND website <> '' THEN 'web_scrape_needed'
  WHEN phone IS NOT NULL AND phone <> '' THEN 'phone'
  ELSE 'mail'
END;
```

### 7B. AI-Consumable Email Context Views

#### Nonprofit Prospect View

```sql
CREATE OR REPLACE VIEW f990_2025.vw_np_email_context AS
SELECT
  -- Identity
  np.ein,
  np.organization_name,
  COALESCE(np.contact_name_clean, np.ed_ceo_name, 'there') as contact_first_name,
  np.state,
  np.city,

  -- Org profile
  np.mission_description,
  np.program_1_desc,
  LEFT(np.ntee_code, 1) as ntee_sector,
  np.total_revenue_latest,
  np.total_employees_cnt,

  -- Hook data
  np.govt_grants_amt,
  np.govt_dependency_pct,
  np.foundation_grant_count,
  np.lapsed_funder_count,
  np.peer_funder_count,

  -- Contact
  np.contact_email,
  np.phone,
  np.website,
  np.outreach_channel,
  np.outreach_priority,

  -- Angle eligibility flags
  CASE WHEN np.peer_funder_count > 0 THEN TRUE ELSE FALSE END as eligible_peer_funder,
  CASE WHEN np.lapsed_funder_count >= 2 THEN TRUE ELSE FALSE END as eligible_lapsed_funder,
  CASE WHEN np.foundation_grant_count = 0
    AND np.total_revenue_latest > 500000 THEN TRUE ELSE FALSE END as eligible_underserved,
  CASE WHEN np.govt_dependency_pct > 30 THEN TRUE ELSE FALSE END as eligible_govt_vulnerable

FROM f990_2025.nonprofits_prospects2 np
WHERE np.outreach_channel = 'email'
  AND np.contact_email IS NOT NULL;
```

#### Foundation Prospect View

```sql
CREATE OR REPLACE VIEW f990_2025.vw_fdn_email_context AS
SELECT
  -- Identity
  fp.ein,
  fp.foundation_name,
  COALESCE(fp.contact_name_clean, fp.app_contact_name, fp.contact_name, 'there') as contact_first_name,
  fp.contact_title,
  fp.state,
  fp.city,

  -- Org profile
  fp.activity_or_mission_desc,
  LEFT(fp.bmf_ntee_cd, 1) as ntee_sector,
  fp.total_assets_eoy_amt,
  fp.total_grant_paid_amt,

  -- Giving analytics
  cfp.total_giving_5yr,
  cfp.median_grant,
  cfp.unique_recipients_5yr,
  cfp.giving_trend,
  cfp.trend_pct_change,
  cfp.openness_score,
  cfp.repeat_rate,
  cfp.new_recipients_5yr,
  cfp.accepts_applications,

  -- Contact
  fp.app_contact_email,
  fp.app_contact_phone,
  fp.phone_num,
  fp.website_url,
  fp.outreach_channel,
  fp.outreach_priority,

  -- Angle eligibility flags
  CASE WHEN cfp.unique_recipients_5yr >= 10 THEN TRUE ELSE FALSE END as eligible_new_grantee,
  CASE WHEN cfp.unique_recipients_5yr >= 20 THEN TRUE ELSE FALSE END as eligible_portfolio_health,
  CASE WHEN cfp.unique_recipients_5yr >= 50 THEN TRUE ELSE FALSE END as eligible_cofunder_map

FROM f990_2025.foundation_prospects2 fp
JOIN f990_2025.calc_foundation_profiles cfp ON fp.ein = cfp.ein
WHERE fp.outreach_channel = 'email'
  AND fp.app_contact_email IS NOT NULL
  AND cfp.has_grant_history = true;
```

### 7C. Angle-Specific Data Assembly Queries

#### Peer Funder Discovery (Angle 6) -- per nonprofit

```sql
-- Returns 5 foundations that fund peers but not this nonprofit
SELECT
  fp.foundation_name,
  fp.state as fdn_state,
  cfp.median_grant,
  cfp.total_giving_5yr,
  cfp.giving_trend,
  cfp.openness_score
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_recipients dr ON fg.recipient_ein = dr.ein
JOIN f990_2025.foundation_prospects2 fp ON fg.foundation_ein = fp.ein
JOIN f990_2025.calc_foundation_profiles cfp ON fp.ein = cfp.ein
WHERE LEFT(dr.ntee_code, 1) = :np_sector
  AND dr.state = :np_state
  AND fg.tax_year >= 2020
  AND cfp.accepts_applications = true
  AND cfp.total_giving_5yr > 100000
  AND fg.foundation_ein NOT IN (
    SELECT foundation_ein FROM f990_2025.fact_grants
    WHERE recipient_ein = :np_ein
  )
GROUP BY fp.foundation_name, fp.state, cfp.median_grant,
  cfp.total_giving_5yr, cfp.giving_trend, cfp.openness_score
ORDER BY cfp.total_giving_5yr DESC
LIMIT 5;
```

#### Lapsed Funder Re-engagement (Angle 8) -- per nonprofit

```sql
-- Returns lapsed funders with their current activity
WITH lapsed AS (
  SELECT fg.foundation_ein, MAX(fg.tax_year) as last_funded_year,
    SUM(fg.amount) as total_received
  FROM f990_2025.fact_grants fg
  WHERE fg.recipient_ein = :np_ein
    AND fg.tax_year BETWEEN 2018 AND 2020
    AND NOT EXISTS (
      SELECT 1 FROM f990_2025.fact_grants fg2
      WHERE fg2.foundation_ein = fg.foundation_ein
        AND fg2.recipient_ein = fg.recipient_ein
        AND fg2.tax_year >= 2022
    )
  GROUP BY fg.foundation_ein
)
SELECT
  fp.foundation_name,
  l.last_funded_year,
  l.total_received,
  cfp.giving_trend,
  cfp.total_giving_5yr as current_5yr_giving,
  (SELECT fg3.recipient_ein || ': $' || fg3.amount || ' (' || fg3.purpose_text || ')'
   FROM f990_2025.fact_grants fg3
   LEFT JOIN f990_2025.nonprofit_returns nr ON fg3.recipient_ein = nr.ein
   WHERE fg3.foundation_ein = l.foundation_ein AND fg3.tax_year >= 2022
   ORDER BY fg3.amount DESC LIMIT 1
  ) as recent_grant_example
FROM lapsed l
JOIN f990_2025.foundation_prospects2 fp ON l.foundation_ein = fp.ein
JOIN f990_2025.calc_foundation_profiles cfp ON l.foundation_ein = cfp.ein
ORDER BY l.total_received DESC
LIMIT 3;
```

#### New Grantee Discovery (Angle 20) -- per foundation

```sql
-- Returns 5 nonprofits matching the foundation's pattern
SELECT
  np.organization_name,
  np.state,
  LEFT(np.mission_description, 200) as mission_snippet,
  nr.total_revenue,
  LEFT(np.ntee_code, 1) as sector
FROM f990_2025.nonprofits_prospects2 np
JOIN f990_2025.nonprofit_returns nr ON np.ein = nr.ein
  AND nr.tax_year >= 2021
WHERE LEFT(np.ntee_code, 1) IN (
    SELECT key FROM f990_2025.calc_foundation_profiles,
    jsonb_each_text(sector_focus)
    WHERE ein = :fdn_ein AND value::numeric > 0.1
  )
  AND np.state IN (
    SELECT key FROM f990_2025.calc_foundation_profiles,
    jsonb_each_text(geographic_focus)
    WHERE ein = :fdn_ein AND value::numeric > 0.1
  )
  AND np.ein NOT IN (
    SELECT recipient_ein FROM f990_2025.fact_grants
    WHERE foundation_ein = :fdn_ein
  )
  AND nr.total_revenue > 100000
ORDER BY nr.total_revenue DESC
LIMIT 5;
```

#### Grantee Portfolio Health (Angle 14) -- per foundation

```sql
-- Returns portfolio health summary
SELECT
  CASE
    WHEN nr2.total_revenue > nr1.total_revenue * 1.1 THEN 'growing'
    WHEN nr2.total_revenue < nr1.total_revenue * 0.9 THEN 'declining'
    ELSE 'stable'
  END as revenue_trend,
  COUNT(*) as grantee_count,
  ROUND(AVG(nr2.total_revenue)::numeric, 0) as avg_revenue,
  COUNT(CASE WHEN nr2.government_grants_amt > 0 THEN 1 END) as govt_funded_count,
  ROUND(AVG(CASE WHEN nr2.government_grants_amt > 0 THEN
    nr2.government_grants_amt::numeric / NULLIF(nr2.total_revenue, 0) * 100
  END), 1) as avg_govt_dependency_pct
FROM f990_2025.fact_grants fg
JOIN f990_2025.nonprofit_returns nr1 ON fg.recipient_ein = nr1.ein AND nr1.tax_year = 2021
JOIN f990_2025.nonprofit_returns nr2 ON fg.recipient_ein = nr2.ein AND nr2.tax_year = 2023
WHERE fg.foundation_ein = :fdn_ein AND fg.tax_year >= 2021
GROUP BY revenue_trend;
```

### 7D. Gap List with Effort/Cost Estimates

| # | Gap | Needed For | Remediation | Effort | Cost | Priority |
|---|-----|-----------|-------------|--------|------|----------|
| 1 | **NP email addresses** | All NP angles | Website scraping (85.9% have URLs) + Hunter.io for domain-based lookup | 4-6 weeks | $5,000-$10,000 | P0 (blocking) |
| 2 | **FDN email addresses** | All FDN angles | Trestle reverse phone (96.4% have phone) + Candid subscription | 2-4 weeks | $7,620 | P0 (blocking) |
| 3 | NP contact name (79% missing) | Email personalization | Extract from np2.all_officers JSONB (92.6% populated) | 1 day | $0 | P1 |
| 4 | FDN contact name quality | Email personalization | INITCAP(LOWER()) on 77% ALL CAPS names | 1 hour | $0 | P1 |
| 5 | NP NTEE code (33% missing) | Sector-based angle matching | NLP on mission_description to infer NTEE | 1-2 weeks | $0 (compute) | P2 |
| 6 | Govt program specificity | Crisis-based angles only | Import vulnerability scores from research files | 1 day | $0 | P3 (deferred) |
| 7 | Email validation | Deliverability | MillionVerifier at $0.003/email or ZeroBounce at $0.008/email | Ongoing | $300-$800 | P1 |
| 8 | Domain warm-up | Email deliverability | 4-6 week ramp on dedicated sending domains | 4-6 weeks | $50-$100/domain | P0 (blocking) |

### 7E. Minimum Viable Angle Recommendation

**If we could only use ONE angle for the first 90 days: Peer Funder Discovery (Angle 6) for nonprofits.**

Rationale:

- **Data availability:** 5/5. All required fields exist in current tables. Zero enrichment needed for the "give first" content itself (the foundation list). The only enrichment needed is the recipient's email address.
- **Scalability:** 5/5. One SQL query per prospect, batch-feasible for thousands. No NLP, no pipeline execution, no manual research.
- **Upsell:** 5/5. "Here are 5 of 47 foundations" is the most natural teaser-to-paid conversion in the catalog.
- **Ethical risk:** 1/5. Purely positive, opportunity-focused. Works regardless of political climate.
- **Addressable market:** 451,823 nonprofits with identifiable peers (state + NTEE sector).
- **Speed to launch:** Once NP emails are obtained, this angle can be live within days.

For foundations, the minimum viable angle is **New Grantee Discovery (Angle 20)**, but it is constrained by the 7.1% email availability rate. Phone outreach or physical mail may be the initial channel for foundation prospects while the email enrichment pipeline runs.

---

## 8. A/B Testing Plan

### Test Design Principles

- **Anchor KPI:** Positive reply rate (replies that express interest or request more information, excluding "unsubscribe," "not interested," "stop emailing me")
- **Minimum sample size:** 50 per variant per angle (based on 5% expected positive reply rate, 80% power, 5% significance level)
- **Statistical framework:** Two-proportion z-test. Minimum detectable effect: 5 percentage points (e.g., 3% vs. 8%)

### Test 1: Nonprofit Angle A/B (Peer Funder Discovery vs. New Funders)

| Parameter | Value |
|-----------|-------|
| Angle A | Peer Funder Discovery (#6): "5 foundations that fund your peers but not you" |
| Angle B | New Funders Entering Your Space (#7): "3 new foundations started funding [sector] in [state]" |
| Cohort | California Education nonprofits, $500K-$5M revenue |
| Sample size | 100 per angle (200 total) |
| Sending cadence | 3-touch sequence (Day 0, 3, 10) |
| Subject line | Angle A: "{FirstName}, 5 foundations funding [sector] in CA (that haven't funded you)" / Angle B: "3 new foundations just started funding [sector] in CA" |
| Personalization level | L3 (state, sector, specific foundation names with amounts) |
| Success metric | Positive reply rate after 3 touches |
| Target | 5%+ positive reply rate for winning angle |
| Stop condition | If bounce rate exceeds 5% in first 50 sends, pause and verify list quality. If spam complaint rate exceeds 0.3%, stop immediately. |
| Duration | 14 days from first send |

### Test 2: Nonprofit Personalization Level A/B

| Parameter | Value |
|-----------|-------|
| Angle | Winning angle from Test 1 |
| Variant A | L2 personalization: sector + state only ("foundations funding education nonprofits in California") |
| Variant B | L3 personalization: specific grant data ("Foundation X gave $75K to [similar org] for [purpose]") |
| Cohort | Same profile as Test 1, different state (NY Education, $500K-$5M) |
| Sample size | 100 per variant (200 total) |
| Success metric | Positive reply rate |
| Target | Quantify the reply rate lift from L2 to L3 personalization |
| Duration | 14 days |

### Test 3: Foundation Angle Test

| Parameter | Value |
|-----------|-------|
| Angle A | New Grantee Discovery (#20): "5 organizations matching your giving pattern" |
| Angle B | Grantee Portfolio Health (#14): "27% of your grantees saw revenue decline" |
| Cohort | Foundations with 20+ grantees, $1M+ in 5yr giving, has email (app_contact_email not null) |
| Sample size | 50 per angle (100 total, constrained by email availability) |
| Personalization level | L4 (specific grantee names, portfolio-level statistics) |
| Success metric | Positive reply rate |
| Target | 3%+ positive reply rate (foundations are harder to reach) |
| Stop condition | If bounce rate exceeds 3%, pause. If any reply indicates the email was unwelcome or inappropriate, review tone immediately. |
| Duration | 21 days (longer because foundation response times are slower) |

### Test 4: "Give First" Conversion Tracking

| Parameter | Value |
|-----------|-------|
| Scope | All positive replies from Tests 1-3 |
| Tracking | Every positive reply is tagged with: angle, personalization level, "give first" deliverable type |
| Conversion funnel | Positive reply -> Free resource requested -> Follow-up conversation -> Trial/demo -> Paid subscription |
| Measurement period | 60 days from first positive reply |
| Key question | Which angle produces positive replies that actually convert to paid subscriptions? A high-reply, low-conversion angle is worse than a moderate-reply, high-conversion angle. |

### Deliverability Prerequisites (Must Complete Before Tests)

| Prerequisite | Status | Action |
|-------------|--------|--------|
| Dedicated sending domain (not thegrantscout.com) | Not started | Register 2-3 domains (e.g., tgs-insights.com) |
| SPF/DKIM/DMARC on sending domains | Not started | Configure DNS records |
| Domain warm-up (4-6 weeks, 5-10/day ramp) | Not started | Start immediately, delay testing by 4-6 weeks |
| Email list validation (MillionVerifier) | Not started | Validate all emails before first send |
| Unsubscribe mechanism | Not started | Required by CAN-SPAM |
| Physical address in email footer | Not started | Required by CAN-SPAM |

### 90-Day Testing Timeline

| Week | Activity |
|------|----------|
| 1-2 | Domain registration, DNS configuration, list building |
| 2-6 | Domain warm-up (5-10 emails/day, ramp gradually) |
| 4-6 | Email enrichment (Trestle pilot, website scraping) |
| 6 | Email validation (MillionVerifier) |
| 7-8 | **Test 1: NP Angle A/B** (200 emails) |
| 9-10 | **Test 2: NP Personalization A/B** (200 emails) |
| 9-11 | **Test 3: Foundation Angle Test** (100 emails) |
| 7-13 | **Test 4: Conversion tracking** (ongoing) |
| 13 | Results analysis, angle selection for scale |

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| REPORT_2026-02-16_cold_email_strategy_and_profiles.md | Enhancements/2026-02-16/ | This report |
| PROMPT_2026-02-16_cold_email_strategy_and_profiles.md | Enhancements/2026-02-16/ | Source prompt |

---

## Notes

### Research Methodology

Three research agents were launched in parallel:
1. **Agent 1 (Give First + Ethics):** Web research on reciprocity psychology, value-first cold email case studies, crisis marketing ethics, nonprofit vendor reputation dynamics. 16 sources cited.
2. **Agent 2 (Cold Email Mechanics):** Web research on 2025-2026 benchmark data from Instantly, Snovio, Martal, Digital Bloom, SalesHandy, and others. 14 sources cited.
3. **Agent 3 (Angle Brainstorming + Data Feasibility):** Database queries against production tables (fp2, np2, fact_grants, calc_foundation_profiles, nonprofit_returns, officers). All angle ratings verified against real data counts.

### Data Verification Notes

All database numbers in this report were verified via SQL queries against the production thegrantscout database on 2026-02-16:
- fp2: 143,184 rows, 38 columns
- np2: 673,381 rows, 47 columns
- fact_grants: 8,310,650 rows
- calc_foundation_profiles: 143,184 rows (112,520 with grant history)
- nonprofit_returns: 2,956,959 filings (97,782 with govt grants > 0)
- officers: 26,281,615 rows (355,165 distinct foundation officers since 2021)

### Key Decisions Made in This Report

1. **Peer Funder Discovery over Government Cuts** as the lead angle. Data availability, ethical risk, and shelf life all favor Peer Funder Discovery.
2. **ALTER TABLE fp2/np2** (extend existing tables) rather than creating new prospect profile tables. Avoids schema proliferation.
3. **CREATE VIEW** for AI email context rather than materialized tables. Views stay current; materialized views would need refresh schedules.
4. **3-touch maximum cadence.** Beyond 3 emails, unsubscribes exceed new replies per Digital Bloom 2025 data.
5. **L3 personalization as the target level.** L4 (deep research) is reserved for high-value foundation prospects. L2 (role/industry) is the minimum acceptable.

### Benchmark Data Caveat

Most benchmark reports (Instantly, Snovio, Martal) are produced by cold email tool vendors with incentives to present optimistic figures. The Digital Bloom 2025 analysis is the most methodologically transparent, drawn from 24,000+ campaigns with hook-type breakdowns. No published benchmarks exist specifically for "SaaS selling to nonprofits" or "foundation program officer" reply rates. Nonprofit-specific recommendations are synthesized from general B2B data plus sector knowledge.

### Source Reports Referenced

| Report | Key Data Used |
|--------|--------------|
| REPORT_2026-02-16_schema_audit.md | Table inventory, canonical coverage numbers, URL tier definitions |
| REPORT_2026-02-16.6_enrichment_tools_contact_discovery_research.md | Enrichment costs (Trestle, Candid, Smarty, Apollo) |
| REPORT_2026-02-16.11_email_campaign_master.md | Foundation universe numbers, contact coverage, production pipeline |

---

*Generated by Claude Code on 2026-02-16*
