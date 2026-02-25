# PROMPT: Research Better URL Discovery Approaches for Foundations

**Date:** 2026-02-16
**Agent:** Claude Code CLI (multi-agent)
**Type:** Research + analysis
**Part:** 1 of 3 — Foundation Reachability Research (URL Discovery → Email from URLs → Email without URLs)

---

## Start in Planning Mode

Before doing any research, agents should first:
1. Read this prompt carefully
2. Deliberate with each other on whether the scope, questions, and structure are right
3. Recommend any changes to the prompt (missing angles, wrong assumptions, better framing)
4. Present the agreed-upon research plan for my approval before proceeding

## Pre-Research Baseline Estimates (Required Before External Research)

Before searching anything, agents must estimate from first principles using what we know from IRS data:

- What % of 143K foundations realistically should have a website? (Large staffed foundations vs family foundations vs bank-managed vs dormant)
- What % likely never will have a website?
- What is the theoretical max URL coverage we could achieve? (40%? 60%? 80%?)
- Do residential mailing addresses correlate with no website?
- Do bank/trust company addresses correlate with centralized trustee websites?
- Do law firm addresses correlate with zero public web presence?

These are hypotheses. They will be revised after research. The point is to reason before Googling.

## Pre-Mortem

Before research, agents should also answer:
- Why might this entire effort fail?
- What assumptions could be wrong?
- What ceiling constraints might make this not worth engineering time?

## Problem

Our current URL discovery pipeline only reaches ~14% of foundations:

- **143,184 foundations** in our database (from IRS 990-PF filings)
- **19,119 (13.4%)** have a website URL filed with the IRS
- **14,107 (9.9%)** of those URLs are actually alive after validation
- **Script 03 (DuckDuckGo search)** was built to find missing URLs but only tested on 100 foundations with a 25% hit rate
- That means **~86% of foundations have no discoverable website** through our current methods
- We had prior research on improving this but it was lost

This is a critical gap. Our product depends on having foundation contact info, and without URLs we can't scrape for emails, staff, or grant details.

## What We Need

Research how to dramatically improve foundation URL coverage. Find approaches we haven't considered. Think beyond just "search harder."

Prioritize bulk cross-dataset matching (EIN joins across public datasets) over per-org search-based discovery. Bulk matching scales; search doesn't.

## Agent Assignments

Use at least 2 agents working in parallel:

**Research Agent(s):** Search the internet for:
- How do Candid/GuideStar, Charity Navigator, Foundation Directory Online, GrantStation, and similar platforms source foundation data?
- What public datasets, APIs, or directories contain foundation URLs? (ProPublica Nonprofit Explorer, Open990, state charity registries, etc.)
- Are there bulk data sources (not just individual lookups) for nonprofit/foundation websites?
- EIN-based cross-dataset matching opportunities — evaluate joining on EIN across: ProPublica bulk datasets, state registry downloads, IRS BMF full file
- What do data enrichment companies (Clearbit, Hunter.io, ZoomInfo, etc.) do for org URL discovery at scale?
- How do nonprofit CRMs and prospect research tools solve this same problem?
- Any open source projects or academic research on nonprofit data enrichment?
- Domain inference without a standalone website: can we identify officer email domains from LinkedIn, bank trustee domains, community foundation domains, or law firm domains?

**Analysis Agent:** Once research is gathered:
- Evaluate each approach on: estimated coverage gain, cost, implementation effort, legal/TOS risk, data freshness
- Identify which approaches can be combined vs which overlap
- Flag approaches that could fill the gap for foundations specifically (small family foundations with no web presence are the hardest)
- Consider the 80/20: what combination of approaches gets us from 14% to 60%+ coverage fastest?

## Agents Should Deliberate

After individual research, agents should:
- Compare findings and challenge each other's assumptions
- Debate tradeoffs (e.g., paying for Candid API vs scraping state registries vs expanding search engines)
- Identify what they're uncertain about and what needs real-world testing
- Converge on a ranked recommendation

## Output

A single research report with:

1. **Executive Summary** — 5 bullet insights, 3 recommended actions, 1 "don't pursue" recommendation
2. **Revised ceiling estimate** — update the pre-research baseline with what was learned. What is the realistic max coverage?
3. **Approaches found** -- for each one:
   - What it is and how it works
   - Estimated coverage gain for our 143K foundations
   - Cost (free / cheap / expensive)
   - Implementation effort (hours/days)
   - Legal/TOS risk level
   - Data freshness (how current are the URLs?)
4. **Ranked recommendation** -- which approaches to pursue, in what order, with rationale
5. **Targets** -- realistic 30-day target, 90-day target, and theoretical max, with rationale
6. **What we still don't know** -- gaps that need testing or further research
7. **A/B Testing Plan** -- for the top 2-3 recommended approaches:
   - Sample size to test on
   - Success metric (coverage %, match accuracy)
   - Stop condition (when to abandon)
   - Cost ceiling for the test

Save to `Enhancements/2026-02-16/REPORT_2026-02-16_url_discovery_research.md`

## Constraints

- We're a bootstrapped startup. Free and cheap approaches get priority over expensive APIs.
- We already have IRS 990-PF data for all 143K foundations (EIN, name, address, officers, grants, assets).
- Our database is PostgreSQL. Our stack is Python.
- We have a working DuckDuckGo search script that can be adapted to other search approaches.
- Don't just list options -- actually recommend a path forward.
