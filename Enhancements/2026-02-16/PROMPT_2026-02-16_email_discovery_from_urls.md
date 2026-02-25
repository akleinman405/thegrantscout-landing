# PROMPT: Research Better Email Discovery From URLs

**Date:** 2026-02-16
**Agent:** Claude Code CLI (multi-agent)
**Type:** Research + analysis
**Part:** 2 of 3 — Foundation Reachability Research (URL Discovery → Email from URLs → Email without URLs)

---

## Start in Planning Mode

Before doing any research, agents should first:
1. Read this prompt carefully
2. Deliberate with each other on whether the scope, questions, and structure are right
3. Recommend any changes to the prompt (missing angles, wrong assumptions, better framing)
4. Present the agreed-upon research plan for my approval before proceeding

## Pre-Research Baseline Estimates (Required Before External Research)

Before searching anything, agents must estimate from first principles:

- Current yield is 15-30%. Break that down:
  - What % of zero-yield sites are JS-rendered (recoverable with Playwright)?
  - What % have contact forms only (no email on page)?
  - What % have emails but our extraction missed them?
  - What % are genuinely email-less sites?
- What is the realistic ceiling yield after all improvements? (50%? 65%? 80%?)
- For pattern inference (officer name + domain → guessed email): what's a realistic accuracy rate?
- What % of nonprofit domains are catch-all? (This caps how much verification can help)

These are hypotheses. They will be revised after research.

## Pre-Mortem

Before research, agents should also answer:
- Why might yield improvements plateau quickly?
- What are the ceiling constraints on email discovery from websites?
- Where does adding more extraction methods hit diminishing returns?

## Problem

We have ~242K orgs with validated live URLs (14K foundations + 228K nonprofits). Our current scraper (scripts 04-07) extracts emails from these websites but only yields 15-30%. That means 70-85% of sites we visit give us nothing.

Current scraper capabilities:
- Fetches homepage + up to 4 internal pages (contact, about, team, leadership, grants)
- 5 extraction methods: mailto links, Cloudflare decode, JSON-LD, AT/DOT obfuscation, regex
- Email classification: general (info@), role (grants@), person (first.last@)
- Confidence scoring 0.00-1.00
- MX + syntax validation
- Materialized view picks best email per org

Current gaps identified (from prior analysis):
- No JS rendering (Playwright) — ~15-20% of sites need it
- Confidence scoring collapses into narrow 0.55-0.65 band
- No SMTP verification or catch-all detection
- No email pattern inference (officer name + domain → guessed email → verify)
- Officer cross-reference with IRS data not built yet (77% ALL CAPS, truncated titles)
- Foundation vs nonprofit email priorities differ but use same ranking

Reference file for full details: `Enhancements/2026-02-13/OUTPUT_2026-02-13.4_email_scraper_analysis.md`

## What We Need

Research how to significantly improve email yield from orgs that HAVE websites — both by improving our scraper AND by using non-scraping approaches that leverage the URL/domain we already know.

**Both pipelines are for sales outreach — but to different buyer types:**

- **Foundation sales pipeline** — We sell a B2B capacity-building service to foundations ($50/month per grantee nonprofit, 10-grantee minimum). We need to reach the person at the foundation who manages grantee services or capacity-building programs — typically a program officer, grants manager, or ED. Not grants@ inboxes (those receive applications). We need decision-maker contacts.
- **Nonprofit sales pipeline** — We sell grant matching subscriptions directly to nonprofits ($99/month). We need to reach whoever manages fundraising or grant seeking — typically an ED, development director, or grants manager. Person-name emails are ideal; general contact emails are fallback.

**These are different optimization problems:** foundation outreach targets a different role, different page types (grantmaking pages, staff directories), and different email patterns than nonprofit outreach.

## Agent Assignments

Use at least 2 agents working in parallel:

**Research Agent(s):** Search the internet for:
- How do email discovery tools (Hunter.io, Snov.io, Apollo.io, RocketReach, Clearbit, Voila Norbert, etc.) find emails given a domain? What's their methodology?
- What's the state of the art for email pattern inference (first.last@domain, f.last@domain, etc.)? How accurate is it?
- Are there free/cheap APIs or open source tools for email discovery given a domain name?
- Best practices for improving web scraper email yield — what pages, patterns, or techniques do we miss?
- How do nonprofit-specific tools (Bloomerang, DonorPerfect, Instrumentl, etc.) source contact data?
- SMTP verification best practices at scale — self-hosted (Reacher) vs commercial APIs, cost per verification, accuracy tradeoffs
- Catch-all domain detection — how prevalent, how to handle
- What do professional prospect researchers do that automated tools miss?

**Analysis Agent:** Once research is gathered:
- Evaluate each approach separately for foundations vs nonprofits (different buyer roles, different page types, different email patterns)
- Score on: yield improvement estimate, cost, implementation effort, legal/TOS risk, accuracy
- **For each method, estimate false positive / bounce risk:**
  - Expected false positive rate
  - Bounce risk if used for outreach
  - Reputation impact on sending domains
  - Is a 10% yield gain worth it if bounce rate goes up 5%?
- Identify the compounding effect — which approaches layer well together? Map the full pipeline: JS render → scrape → pattern infer → SMTP verify → rank. Identify diminishing returns and stopping points.
- Map to our existing pipeline: what plugs into scripts 04-07 vs what's a new parallel track?
- Consider the economics: we charge $99/month (nonprofit) and $50/month per grantee (foundation B2B). Bulk API costs need to make sense at our scale.

## Agents Should Deliberate

After individual research, agents should:
- Challenge each other on yield estimates and false positive rates
- Debate: improve the scraper vs add parallel email discovery tracks vs both?
- Separate what works for foundations (need decision-makers, not application inboxes) vs nonprofits (need ED/development staff)
- Identify what needs real-world A/B testing vs what's clearly worth doing
- Converge on a ranked recommendation for each org type

## Output

A single research report with:

1. **Executive Summary** — 5 bullet insights, 3 recommended actions, 1 "don't pursue" recommendation
2. **Revised ceiling estimate** — update pre-research baseline. What's the realistic max yield per pipeline?
3. **Scraper improvement approaches** — things that make scripts 04-07 better:
   - What it is, how it works
   - Estimated yield improvement
   - Expected false positive / bounce rate
   - Implementation effort
   - Foundation relevance vs nonprofit relevance
4. **Non-scraping email discovery approaches** — parallel tracks using domain/name data:
   - What it is, how it works
   - Estimated coverage gain
   - Cost at our scale (~12K foundation domains, ~228K nonprofit domains)
   - Accuracy / deliverability expectations
   - False positive rate and bounce risk
   - Legal/TOS considerations
5. **Validation improvements** — approaches to improve email deliverability after discovery:
   - SMTP verification options and costs
   - Catch-all handling
   - Freshness/decay management
6. **Foundation sales pipeline recommendation** (ranked, with rationale — focused on reaching decision-makers)
7. **Nonprofit sales pipeline recommendation** (ranked, with rationale — focused on reaching ED/development staff)
8. **Compounding model** — how approaches layer, where diminishing returns hit
9. **A/B Testing Plan** — for the top 2-3 recommended approaches:
   - Sample size to test on
   - Success metric (yield %, bounce rate, deliverability)
   - Stop condition
   - Cost ceiling for the test
10. **What we still don't know**

Save to `Enhancements/2026-02-16/REPORT_2026-02-16_email_discovery_research.md`

## Constraints

- Bootstrapped startup — free/cheap first, paid APIs only if ROI is clear
- We already have: IRS officer names for all 143K foundations, working scraper, 242K live URLs, PostgreSQL + Python stack
- Don't re-discover what's already in our scraper analysis — go beyond it
- Deliverability matters as much as yield. A method that increases bounce rate is net negative for outreach.
- Recommend, don't just list
