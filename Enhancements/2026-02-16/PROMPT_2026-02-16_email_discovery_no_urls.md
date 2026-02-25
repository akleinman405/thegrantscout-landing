# PROMPT: Research Email/Contact Discovery for Orgs WITHOUT Websites

**Date:** 2026-02-16
**Agent:** Claude Code CLI (multi-agent)
**Type:** Research + analysis
**Part:** 3 of 3 — Foundation Reachability Research (URL Discovery → Email from URLs → Email without URLs)

---

## Start in Planning Mode

Before doing any research, agents should first:
1. Read this prompt carefully
2. Deliberate with each other on whether the scope, questions, and structure are right
3. Recommend any changes to the prompt (missing angles, wrong assumptions, better framing)
4. Present the agreed-upon research plan for my approval before proceeding

## Pre-Research Baseline Estimates (Required Before External Research)

Before searching anything, agents must segment the ~124K foundations without URLs using IRS data we already have. Estimate:

- % bank/trust company managed (look for institutional names in officer fields)
- % family-run (residential mailing address, 1-2 officers with same last name)
- % community foundation affiliated
- % likely dormant (no grants in recent years, minimal assets)
- % likely reachable via any realistic means
- % fundamentally unreachable

These are hypotheses. They will be revised after research.

## Pre-Mortem

Before research, agents should also answer:
- Why might this entire effort fail?
- What % of these orgs are simply not contactable at scale?
- Are we chasing orgs that don't want to be found?

## Kill Criteria (Define Before Research)

Agents must propose objective rules for which orgs to skip entirely:
- Asset threshold below which it's not worth pursuing?
- Grant volume threshold (e.g., no grants in last 3 years)?
- Years since last 990-PF filing?
- Address type heuristic (PO box at a bank = managed by bank, skip individual pursuit)?

These become filters in our database, not just research conclusions.

## Problem

This is the hardest bucket. After URL discovery and web scraping, a large portion of orgs will still have NO website and NO email:

- **~124K foundations** (86%) have no discoverable website through IRS data or search
- Many of these are small family foundations, donor-advised funds, or bank-managed trusts — they may genuinely not have a website or public email
- A smaller but still significant portion of nonprofits also lack websites
- For these orgs, we can't scrape because there's nothing to scrape

What we DO have for these orgs (from IRS filings):
- EIN (tax ID)
- Legal name (and sometimes DBA)
- Mailing address (city, state, zip)
- Officer/trustee names and titles (from 990-PF Part VIII)
- Bank/trust company names (for managed foundations)
- Total assets and grant amounts
- Historical grant recipients and amounts

## What We Need

Research how to find contact information for orgs that have no web presence. This is a fundamentally different problem from scraping — it's about data enrichment from non-web sources and understanding which orgs are even reachable.

**Both pipelines are for sales outreach:**

- **Foundation sales outreach** — We sell a B2B capacity-building service to foundations ($50/month per grantee nonprofit, 10-grantee minimum). We need to reach whoever manages grantee services or capacity-building — typically a program officer, trustee, or ED. For bank-managed foundations, the contact may be a trust officer at the bank.
- **Nonprofit sales outreach** — We sell grant matching subscriptions directly to nonprofits ($99/month). We need to reach whoever manages fundraising or grant seeking — typically an ED, development director, or grants manager.

**Critically: "contact" does not mean only email.** For orgs without websites, the best contact method may not be email. Agents should evaluate all reachability channels:
- Email (if discoverable through non-web means)
- Phone (from address + name lookups)
- Trustee office / bank trust department contact
- Attorney-of-record contact
- Community foundation directory listing
- LinkedIn profile of officers
- Physical mail (certified or standard)

## Agent Assignments

Use at least 2 agents working in parallel:

**Research Agent(s):** Search the internet for:
- How do prospect researchers find contact info for small/private foundations with no web presence?
- State charity registry databases — which states have searchable databases with contact emails? (e.g., NY Charities Bureau, CA Registry of Charitable Trusts)
- IRS BMF (Business Master File) — does it contain any contact info beyond what's in 990-PF filings?
- ProPublica Nonprofit Explorer, Open990, Cause IQ — do these aggregate contact data beyond IRS filings?
- Foundation directories (Foundation Directory Online/Candid, GrantStation) — what contact data do they have, and is any accessible without expensive subscriptions?
- Bank/trust company foundation management — how do grantseekers typically contact bank-managed foundations? Is there a pattern or standard workflow?
- LinkedIn as a data source — can officer names from IRS data be matched to LinkedIn profiles to find current org affiliations and contact info?
- Phone-first approaches — IRS filings have addresses. Are there bulk phone lookup APIs that work from address + name?
- Community foundation directories — many small foundations are affiliated with community foundations that publish directories
- Donor-advised fund sponsors (Fidelity Charitable, Schwab Charitable, etc.) — is there any way to reach advisors?
- USPS address validation + business lookup — can we determine if a mailing address is a home, office, bank, or law firm?
- Any nonprofit data cooperatives, shared databases, or industry datasets?

**Analysis Agent:** Once research is gathered:
- Segment the 124K foundations into reachable categories (bank-managed, family, community-affiliated, etc.) — update the pre-research estimates with data
- For each approach: realistic coverage estimate, cost per org enriched, effort, legal risk
- Evaluate contactability by channel (email vs phone vs mail vs trustee vs LinkedIn)
- Identify which orgs are fundamentally unreachable (DAFs, dormant foundations, etc.) — knowing what to skip is valuable
- Evaluate foundation vs nonprofit differently
- Consider: is it worth pursuing some of these orgs at all? What's the business value threshold?

## Agents Should Deliberate

After individual research, agents should:
- Challenge each other on realistic coverage estimates (don't be optimistic about reaching family foundations at home addresses)
- Debate: breadth (try to reach all 124K) vs depth (focus on the subset most likely to be active grantmakers who also offer capacity-building to grantees)
- Discuss the bank/trust managed foundation angle — this could be a high-leverage shortcut if we can identify which foundations are managed by which institutions
- Consider what data we could add to our database even if we can't get an email (phone, trustee company, affiliated community foundation, contact method)
- Converge on a realistic recommendation

## Output

A single research report with:

1. **Executive Summary** — 5 bullet insights, 3 recommended actions, 1 "don't pursue" recommendation
2. **Revised segmentation** — update pre-research estimates with data. How many orgs per category? How many are reachable?
3. **Kill criteria recommendation** — proposed database filters for orgs not worth pursuing, with thresholds and rationale
4. **Data enrichment approaches** — for each:
   - What it is, how it works
   - Which org segment it covers
   - Contact channel (email / phone / mail / trustee / LinkedIn)
   - Estimated coverage gain
   - Cost per org enriched
   - Implementation effort
   - Legal/TOS considerations
   - Data freshness
5. **Foundation sales outreach recommendations** (ranked — focused on reaching decision-makers for B2B capacity-building pitch)
6. **Nonprofit sales outreach recommendations** (ranked — focused on reaching ED/development staff for subscription pitch)
7. **Orgs to deprioritize** — which segments aren't worth pursuing and why, with specific filter criteria
8. **Combined roadmap** — implementation order
9. **A/B Testing Plan** — for the top 2-3 recommended approaches:
   - Sample size to test on
   - Success metric (contacts found, response rate if applicable)
   - Stop condition
   - Cost ceiling for the test
10. **What we still don't know**

Save to `Enhancements/2026-02-16/REPORT_2026-02-16_no_url_contact_discovery_research.md`

## Constraints

- Bootstrapped startup — free/cheap first
- We have: IRS 990-PF data (EIN, name, address, officers, grants, assets), PostgreSQL, Python
- Be honest about what's unreachable — knowing which orgs to skip saves time too
- The business value varies: a foundation giving $5M/year in grants is worth spending $5 to find contact info for. A dormant foundation with $50K in assets is not.
- Recommend, don't just list
