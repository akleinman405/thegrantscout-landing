# PROMPT: $0-Budget Email Campaign Execution Plan

**Date:** 2026-02-16
**For:** Claude Code CLI
**Schema:** f990_2025

---

## Situation

We have three comprehensive research reports on our cold email campaign strategy. Now we need to turn them into a step-by-step execution plan that costs $0 (except Anthropic API for writing emails). No paid tools — no Trestle, no Smartlead, no commercial enrichment APIs.

## Source Reports (read all four before planning)

1. `REPORT_2026-02-16_11_email_campaign_master.md` — 6-phase pipeline master report
2. `REPORT_2026-02-16_cold_email_strategy_and_profiles.md` — Give-first strategy, benchmarks, ethics framework, prospect profile DDL, angle-specific SQL queries
3. `REPORT_2026-02-16_12_cold_email_angle_catalog.md` — 20 angles rated, SQL-verified data feasibility, top 3 per buyer type
4. `REPORT_2026-02-16_schema_audit.md` — 59-table inventory, canonical coverage numbers, Steps 1-3 executed (fp2 email column added, oue expanded, web_* tables created)

## Dependencies

- **Run PROMPT_2026-02-16_email_data_audit.md FIRST.** That prompt migrates old campaign emails into fp2/np2 and creates the campaign_prospect_status table. This plan assumes that migration is complete.

## Key Constraints

**$0 budget.** Only free methods:
- Foundation emails already in DB: 10,092 (fp2.app_contact_email)
- URL discovery: DuckDuckGo scraping, DNS domain guessing
- Email scraping: Improved web scraper on 14,107 foundations with validated URLs
- Pattern inference + SMTP verification: Guess emails from officer names + domains, verify free
- Nonprofit emails: Scrape from websites (57.8% of np2 have URLs)
- Sending: Existing Gmail accounts + existing campaign scripts (send_initial_outreach.py, send_followup.py, campaign_tracker.py, export_bounces.py) — NOT Smartlead
- Email content: Anthropic API via Claude Code to write personalized emails using angle catalog

**What we HAVE:**
- 143,184 foundations in fp2 (10,092 with email via app_contact_email — already backfilled per schema audit, 138,009 with phone, 14,107 with validated URLs)
- 673,381 nonprofits in np2 (0 emails currently — need column added, 100% phone, 57.8% URLs)
- org_url_enrichment table already expanded with contact columns (schema audit Step 2)
- web_* tables created (schema audit Step 3)
- 8.3M grants in fact_grants
- calc_foundation_profiles with giving analytics
- Existing email campaign scripts (Python + Gmail)
- 20 rated cold email angles with SQL queries
- Prospect profile DDL (views) ready to create
- Ethics framework and email templates

## Key Insights to Incorporate

These findings from the reports should inform the plan:

1. **Peer Funder Discovery is the #1 nonprofit angle** (scored 14/15). Government cuts angle scored 7/15 — use as follow-up context only, never first touch.
2. **New Grantee Discovery is the #1 foundation angle** (scored 13/15). "Here are 5 orgs matching your giving pattern that you haven't funded."
3. **Small cohorts (<50) get 2.76x reply rates** vs blasts of 1,000+. Segment by state + NTEE + budget.
4. **3-touch sequence** (Day 0, 3, 10). Each follow-up brings new value, never "just checking in."
5. **Plain text, 50-80 words, 0-1 links.** No tracking pixels, no HTML, no images.
6. **Timeline hooks > problem hooks** (10% reply rate vs 4.4%). "3 new foundations started funding [sector] in [state]" beats "struggling with funding?"
7. **L3 personalization** (situation-specific) using 990 data. Not just merge tags.
8. **7-rule crisis ethics framework** — lead with solution not wound, never reference specific cuts, make value unconditional.
9. **The "give first" value must be IN the email body** — real foundation names, real amounts. Don't gate behind a demo.
10. **Domain warm-up needed** — 4-6 weeks ramping from 5-10/day before full volume.

## Tasks

### 1. Review Reports
Read all three reports. Note any conflicts, gaps, or assumptions that don't hold under a $0 constraint.

### 2. Create Phase-by-Phase $0 Execution Plan

For EACH phase, provide:
- **What we're doing** (1-2 sentences)
- **Steps** (numbered, specific, actionable — "run this query" not "gather data")
- **Expected yield** (how many emails/URLs/contacts)
- **Dependencies** (what must be done first)
- **Time estimate**

#### Phase 1: Get More URLs ($0 methods only)
- DuckDuckGo scraping for foundations without URLs
- DNS domain guessing (foundationname.org, etc.)
- Re-validate failed URLs from existing data
- Mine buried URLs from application text fields

#### Phase 2: Get Emails ($0 methods only)
- Start with emails already in DB after migration (10,092 in fp2 + whatever the audit prompt adds from campaign tables and CSVs)
- Scrape emails from foundation websites (14,107 with validated URLs)
- Pattern inference from officer names + domain (e.g., jsmith@foundationdomain.org)
- SMTP verification of guessed emails (free)
- Scrape nonprofit emails from np2 websites (57.8% have URLs)
- Do NOT re-email anyone marked as bounced/unsubscribed in campaign_prospect_status

#### Phase 3: Build Prospect Profiles ($0)
- Create the two SQL views (vw_np_email_context, vw_fdn_email_context) from the DDL in the strategy report
- ALTER TABLE fp2/np2 to add campaign-support columns
- Run angle eligibility queries to tag prospects

#### Phase 4: Write Campaign Content ($0 except API)
- Build email templates per the top 3 angles (nonprofit + foundation)
- Create the SQL generators that produce per-prospect "give first" data
- Set up Anthropic API prompt to turn prospect context + angle data into personalized emails
- Write follow-up sequences (touch 2 and 3) with new value per touch

#### Phase 5: Send ($0 — use existing scripts)
- Audit existing send scripts (send_initial_outreach.py etc.) for compatibility
- Set up domain warm-up schedule using existing Gmail accounts
- Define cohort segmentation (state + NTEE + budget, <50 per cohort)
- Start soft launch: 10-20 emails/day to highest-quality foundation prospects

#### Phase 6: Track & Respond ($0)
- Use existing campaign_tracker.py and response_tracker
- Define response classification (positive, negative, OOO, bounce)
- Set up follow-up trigger logic

### 3. Identify What's Missing
- What can't we do at $0 that materially hurts the campaign?
- What's the realistic email volume ceiling without paid tools?
- Where should we spend money first IF budget opens up?

## Output

`PLAN_2026-02-16_email_campaign_execution.md` with:
- Phase-by-phase steps (numbered, specific)
- Realistic yield estimates for $0 methods
- Timeline (week-by-week for first 90 days)
- "First 5 things to do" summary at the top
- "Spend money here first" section at the bottom
