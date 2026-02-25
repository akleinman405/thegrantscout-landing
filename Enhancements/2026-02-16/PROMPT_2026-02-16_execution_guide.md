# PROMPT: Email Campaign Execution Guide (Interactive HTML)

**Date:** 2026-02-16
**For:** Claude Code CLI
**Schema:** f990_2025

---

## Situation

We've completed extensive research on our cold email campaign (4 reports, 20 angles evaluated, schema audit, email migration). Now we need to turn all of this into a clear, readable execution guide that Alec can work through phase by phase.

**Budget: $0** (except Anthropic API for writing emails). No paid tools — no Trestle, no Smartlead, no commercial enrichment APIs. Use existing Gmail accounts + existing Python campaign scripts.

## Source Reports (read ALL before building the guide)

1. `REPORT_2026-02-16_11_email_campaign_master.md` — 6-phase pipeline, 20 key decisions, tool recommendations, budget
2. `REPORT_2026-02-16_cold_email_strategy_and_profiles.md` — Give-first strategy, benchmarks, ethics framework, prospect profile DDL/SQL, angle-specific queries, email templates
3. `REPORT_2026-02-16_12_cold_email_angle_catalog.md` — 20 angles rated on 4 dimensions, SQL-verified feasibility, top 3 per buyer type
4. `REPORT_2026-02-16_schema_audit.md` — 59-table inventory, canonical coverage numbers, Steps 1-3 executed
5. `REPORT_2026-02-16_email_migration.md` — Steps 4-6 executed, all emails consolidated, campaign history preserved

## Current State (after migration)

| Asset | Count | Notes |
|-------|-------|-------|
| Foundation valid emails (fp2) | 8,712 | Never been emailed by us |
| Nonprofit emails (np2) | 6,372 | 1,392 already emailed Nov-Dec 2025 |
| Nonprofit emails NOT yet contacted | ~4,980 | Available for new campaign |
| Bounced addresses (suppress list) | 113 | In campaign_prospect_status |
| Replied (positive) | 5 | Beta leads from prior campaign |
| Grants in fact_grants | ~8.3M | For generating personalized data |
| Foundation profiles (calc_foundation_profiles) | 143,184 | Giving analytics, trends, openness |
| Campaign scripts | 4 | send_initial_outreach.py, send_followup.py, campaign_tracker.py, export_bounces.py |

## Key Research Findings to Present

### Angle Rankings (from catalog)

**Top nonprofit angles:**
1. Peer Funder Discovery (14/15) — "5 foundations fund your peers but not you" — 451K targetable
2. New Funders Entering Your Space (13/15) — "3 foundations started funding your sector this year" — 400K targetable  
3. Lapsed Funder Re-engagement (13/15) — "Foundation X hasn't funded you since 2020" — 81K targetable

**Top foundation angles:**
1. New Grantee Discovery (13/15) — "5 orgs match your giving pattern" — 69K targetable
2. Grantee Portfolio Health (12/15) — "27% of your grantees saw revenue decline" — 13K targetable
3. Co-Funder Network Map (11/15) — "You and Foundation X share 4,926 grantees" — 3.4K targetable

**Government funding cuts angle scored LAST (7/15).** Highest ethical risk, can't name specific programs from DB, ambulance-chaser perception. Use as context in follow-ups only, never first touch.

### Email Strategy (from benchmarks)

- Plain text, 50-80 words, 0-1 links, no tracking pixels, no HTML
- 3-touch sequence: Day 0 (value), Day 3 (new data), Day 10 (breakup + different value)
- Cohorts under 50 get 2.76x reply rate vs 1,000+ blasts
- Segment by state + NTEE sector + budget band
- Timeline hooks ("3 new foundations started...") get 10% reply vs 4.4% for problem hooks
- "Give first" value IN the email body — real names, real amounts, verifiable
- Tuesday-Wednesday, 9-11 AM recipient local time
- Domain warm-up: start 10-20/day, ramp over 4-6 weeks

### Ethics Framework (7 rules)

1. Lead with solution, not wound
2. Never reference specific cuts unless recipient did first
3. Make value unconditional (useful whether or not they subscribe)
4. Price the same as before the crisis
5. Acknowledge context with restraint ("current funding environment")
6. Pass the "worst day" test
7. Offer to help even if they can't pay

### Profile Data Needed Per Prospect

**For foundation emails (New Grantee Discovery):**
- Foundation name, contact name, state, assets
- Top 2-3 sectors (from calc_foundation_profiles.sector_focus)
- Geographic focus
- 3-5 matching nonprofits they haven't funded (name, state, mission, revenue)

**For nonprofit emails (Peer Funder Discovery):**
- Nonprofit name, contact name, state, NTEE sector
- 3-5 foundations that fund peers but not them (name, median grant, 5yr giving, trend)

All data exists in the database. SQL queries are written in the strategy report (Section 7C).

### The Nightly Batch Process (proposed)

1. Each night: profile queries run for next day's cohort (~50 prospects, same state+sector+budget)
2. Anthropic API writes personalized emails using profile data
3. Next morning: emails sent via existing scripts during business hours (9-11 AM local)
4. Day 3 and Day 10 follow-ups auto-queued for non-repliers
5. Scale: start 10-20/day during warm-up, ramp to 50/day after 4 weeks

## Task: Build the HTML Execution Guide

Create a single HTML file: `EMAIL_CAMPAIGN_EXECUTION_GUIDE.html`

### Requirements

- **Clean, professional, readable** — this is a working document Alec will reference daily
- **Table of contents** with clickable links to each section
- **Collapsible sections** (use <details> tags) so it's not overwhelming
- **Decision points clearly marked** — highlight where Alec needs to make a choice before proceeding
- **Phase-by-phase structure** — each phase has: what we're doing, why, exact steps, expected results

### Structure

**Section 1: Current State Dashboard**
- What we have (emails, data, scripts, angles)
- What the research found (key numbers, top angles, benchmarks)
- Revenue math: nonprofit deals vs foundation deals

**Section 2: Decisions to Make**
Present each decision clearly with options and tradeoffs:
- Start with foundations, nonprofits, or both?
- Which angle(s) to lead with?
- First cohort criteria (largest by assets? accepts applications? capacity building history?)
- Sending volume and warm-up schedule
- Use existing Gmail scripts or set up something new?
- How to handle the 1,473 junk emails in fp2 (recommend cleanup)

**Section 3: Phase 1 — Build Prospect Profiles**
- Create the SQL views (vw_fdn_email_context, vw_np_email_context) — include the actual DDL from the strategy report
- Define cohort segmentation logic
- Run angle-specific data queries for first cohort
- Show example output: "here's what a foundation profile looks like before email writing"
- Include the actual SQL queries from the strategy report (Peer Funder Discovery, New Grantee Discovery, Lapsed Funder, Portfolio Health)

**Section 4: Phase 2 — Write Emails**
- Email structure (hook → value bridge → soft CTA, 50-80 words)
- Anthropic API prompt design for email generation
- Show example: profile data in → personalized email out
- Follow-up sequence design (touch 2 and 3 content)
- A/B test plan (which subject lines, which angles)
- Include the email templates from the strategy report (The Specific Gift, The Sector Context, etc.)
- Include the "what NOT to say" examples (The Voyeur, The Fear Amplifier, etc.)

**Section 5: Phase 3 — Send**
- Audit existing campaign scripts for compatibility
- Domain warm-up schedule (week by week)
- Cohort sending calendar
- Bounce/reply handling
- Suppression list management (113 bounces + future bounces)

**Section 6: Phase 4 — Systematize (Nightly Batch)**
- The automated pipeline: profile → write → queue → send → track
- Cron job / scheduled task setup
- Monitoring and alerts
- Scaling plan (when to increase volume, when to add angles)

**Section 7: Appendix**
- Full angle catalog (all 20, with scores)
- All SQL queries referenced
- Ethics framework (full 7 rules with examples)
- Email template library
- Benchmark data tables

### Design Notes

- Use a clean sans-serif font, good spacing
- Color-code: decisions in amber/yellow, actions in blue, warnings in red
- Make it printable (reasonable margins, no fixed widths)
- Include "estimated time" for each step
- Each phase should have a "done" checklist at the end

## Output

Save to: `EMAIL_CAMPAIGN_EXECUTION_GUIDE.html`
