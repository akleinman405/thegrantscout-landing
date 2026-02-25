# PROMPT: Cold Email Strategy Research → Prospect Profile Data Requirements

**Date:** 2026-02-16
**Agent:** Claude Code CLI (multi-agent)
**Type:** Research + analysis + data architecture
**Pipeline Phase:** 3 (Build Prospect Profiles) + 4 (Write Emails) — strategy foundation
**Anchor KPI:** Positive reply rate (not opens, not total replies — positive replies that lead to conversations)

---

## Start in Planning Mode

Before doing any research, agents should first:
1. Read this prompt carefully
2. Deliberate with each other on whether the scope, questions, and structure are right
3. Recommend any changes to the prompt (missing angles, wrong assumptions, better framing)
4. Present the agreed-upon research plan for my approval before proceeding

## Why Backwards

We are NOT starting with "what data do we have." We are starting with "what makes cold email actually convert" and working backwards to "what data do we need to collect." Strategy drives data requirements, not the other way around.

## Context

TheGrantScout is an AI-powered grant matching service. We're building a cold email pipeline to sell to two buyer types:

**Nonprofit buyers ($99/month subscription):**
- We help them discover new foundation funding opportunities
- Buyer is typically ED, development director, or grants manager
- Pain point: lost government funding, limited staff to research funders, missing opportunities they don't know about

**Foundation buyers ($50/month per grantee, 10-grantee minimum):**
- We help their grantees find additional/replacement funding as a capacity-building service
- Buyer is typically program officer, grants manager, or ED
- Pain point: grantees struggling after federal funding cuts, want to support grantee sustainability

**What we already have in our database:**
- IRS 990-PF data: 143K foundations, 8.3M historical grants, 670K nonprofits
- Grant relationships: which foundations funded which nonprofits, amounts, years
- Government funding data: which nonprofits report government grants, dependency %, dollar amounts
- Federal funding cuts research: 30+ events, 10 sectors, vulnerability scores (26,257 highly vulnerable orgs)
- Officer names and titles (from IRS filings — quality varies)
- Website scrape data: mission statements, staff names/titles, emails
- NTEE codes, budget sizes, geographic data

## Phase 1: Cold Email Strategy Research

### 1A: "Give First" Strategy — Does It Work in Cold Email?

This is a core strategic question. On social media and content marketing, the "give massive value first, sell later" approach (think Brooke Castillo, Alex Hormozi — lead with a free resource that's genuinely useful, build trust, then offer) drives engagement and conversion. But those contexts are different:
- Social media: person opts in by following or responding to a public post
- Content marketing: person finds you via search or referral
- Cold email: you're interrupting someone's inbox uninvited

**Research specifically:**
- Does the "lead with free value" approach translate to cold email, or does the uninvited nature change the dynamic?
- Are there case studies of cold email campaigns that led with genuinely useful free content and converted well?
- What's the psychology difference between "I found something useful for you" in an inbox vs on social media?
- Does offering something free in a cold email increase trust or increase suspicion? ("What's the catch?")
- What makes a cold email freebie feel generous vs feel like a lead magnet trap?
- Is there research on nonprofit/foundation recipients specifically — are they more or less receptive to free resources from unknown senders?

### 1B: Brainstorm "Give First" Angles

We've brainstormed some initial angles. Agents should evaluate these AND generate additional ones we haven't thought of. For each angle, assess: how useful is it to the recipient, how easy is it for us to produce at scale, and does it naturally lead to our paid service?

**Our initial angles for nonprofits:**
- "We're putting together a list of the top foundations funding nonprofits in [your state/sector]. Want a copy?" — simple, useful, easy to produce from our data, natural upsell when we deliver it
- "We noticed you were receiving funding from [specific government program] that's been cut. We found a few foundations worth looking into: [Name A], [Name B], [Name C]." — specific, shows research, gives immediate value
- Benchmark data: "Nonprofits your size in [sector] typically receive grants from X foundations — here's how your funding profile compares"

**Our initial angles for foundations:**
- "Three of your grantees — [Org A], [Org B], [Org C] — recently lost federal funding from [program]. We put together a brief on replacement funding options for them."
- "We're researching which foundation grantees were most impacted by recent federal cuts in [sector]. Would a summary of your grantees' exposure be useful?"

**Agents should brainstorm at least 5 additional angles for each buyer type.** Think about:
- What can we generate from our existing data that would be genuinely useful?
- What would a nonprofit ED actually forward to their board?
- What would a foundation program officer actually read vs delete?
- What free thing is so good it makes them think "if this is free, what's the paid version like?"
- Are there angles that don't reference funding cuts at all? (The cuts angle has a shelf life)
- Are there angles based on positive opportunity rather than crisis? ("We found 12 foundations that started funding [sector] orgs in the last 2 years")

### 1C: General Cold Email Best Practices

**Research Agent(s):** Search the internet for:

**General cold email mechanics:**
- What positive reply rates should we target? What do top performers achieve for B2B cold outreach?
- What subject line strategies work? (Especially for nonprofit/foundation recipients)
- Optimal email length for cold outreach
- How many touchpoints before giving up? What follow-up cadence works?
- What kills cold emails? Common mistakes that get deleted or spam-filtered

**Personalization research:**
- What level of personalization actually moves the needle? (Name only vs role-specific vs org-specific vs situation-specific)
- Is there a personalization ceiling where it starts feeling creepy or invasive rather than thoughtful?
- At what point does a cold email feel like "they did their homework" vs "they're surveilling me"?
- For foundations specifically: does referencing their grantees by name feel helpful or intrusive?
- What's the "personalization comfort band" — specific enough to feel relevant, not so specific it feels assembled by a machine?

**Nonprofit/foundation-specific cold email:**
- How do SaaS companies successfully sell to nonprofits via cold email?
- How do grant consultants and fundraising tools acquire nonprofit clients?
- What messaging resonates with nonprofit EDs/development directors?
- What messaging resonates with foundation program officers?
- Case studies or teardowns of successful nonprofit cold outreach campaigns?
- Unique sensitivities: nonprofits are skeptical of vendors, foundations get pitched constantly

### 1D: Ethical Line Deliberation

The government funding cuts angle is powerful and timely. But it references a crisis affecting real organizations.

**Agents must explicitly debate:**
- When does urgency become exploitation?
- When does referencing lost funding feel manipulative vs helpful?
- Is there a difference between "we can help you through this" and "we noticed you're struggling"?
- How would a nonprofit ED feel receiving this email on their worst funding day?
- What's the line between showing you understand their situation and profiting from their pain?
- Are there framings that feel like solidarity rather than sales?

**This matters for reputation.** The nonprofit world is small and connected. One tone-deaf email campaign can create lasting damage.

**Checkpoint: Present all strategy findings for approval before Phase 2.**

## Phase 2: Data Requirements (Driven by Strategy)

After strategy research is approved, agents map backwards:

**Analysis Agent(s):**

For each email angle and personalization signal identified in Phase 1:
- What specific data point does it require?
- Do we already have it in our database? (Which table/field?)
- If not, where could we get it? (External source, enrichment, scraping)
- How fresh does it need to be?
- How accurate does it need to be? (A wrong data point is worse than no data point)

**Minimum viable profile vs gold standard:**
- What's the minimum data that produces a good email for each angle?
- What's the gold standard if we had unlimited enrichment?
- Where's the 80/20 line?
- At what point does profile complexity slow down launch beyond the funding cuts window?

Organize into a prospect profile schema:

**Per-contact fields:**
- Person-level: name, title, email, source, confidence
- Org-level: what do we need about their organization?
- Hook-level: what situation-specific data powers the email angle?
- Foundation-specific: grantee impact data, capacity-building signals
- Nonprofit-specific: funding vulnerability, named alternative funders
- Free-value-specific: what data powers the free resource we're offering?

For each field:
- Source (which table or external source)
- Have it? (yes / partial / no)
- Quality (clean / needs work / unreliable)
- Priority (must-have for email / nice-to-have / skip)

**Checkpoint: Present data requirements and gap analysis for approval before finalizing.**

## Phase 3: Prospect Profile Spec

After data requirements are approved, produce:

1. **Prospect profile table schema** — DDL-ready for PostgreSQL. One row per outreach target. Include every field needed to generate a personalized email.
2. **Data assembly queries** — SQL or pseudocode showing how to populate the profile from existing tables (grants, officers, org_url_enrichment, web_emails, web_staff, etc.)
3. **Gap list** — fields we need but don't have, with recommended enrichment approach and effort estimate
4. **Foundation email data assembly** — how to look up a foundation's grantees, identify which lost federal funding, and package that into the profile
5. **Nonprofit email data assembly** — how to look up a nonprofit's funding history, identify vulnerability, find replacement funders, and package that into the profile
6. **Free resource data assembly** — how to generate the "give first" deliverable (state-level foundation lists, sector funding profiles, grantee impact briefs) from existing data
7. **"Minimum viable angle" recommendation** — if we could only use ONE angle for the first 90 days, which one and why?

## Output

A single report with:

1. **Executive Summary** — 5 key insights, 3 recommended actions, 1 "don't pursue" recommendation
2. **"Give First" strategy assessment** — does it work in cold email? How to adapt it? Which angles test best conceptually?
3. **Cold Email Strategy Brief** — what works, what doesn't, recommended angles (ranked), personalization comfort band, target metrics
4. **Ethical line guidance** — where the line is, recommended framings, what to avoid
5. **Angle catalog** — all angles (ours + agent-generated) rated on: usefulness to recipient, ease of production, natural upsell path, ethical risk
6. **Data Requirements Map** — every data point needed, where it comes from, what we have vs don't have
7. **Prospect Profile Spec** — table schema, assembly queries, gap list
8. **A/B Testing Plan** — for the top 3-4 email angles:
   - Sample size
   - Success metric (positive reply rate)
   - Stop condition
   - What data quality level is needed for the test
   - How to measure "give first" conversion (freebie requested → paid conversion)

Save to `Enhancements/2026-02-16/REPORT_2026-02-16_cold_email_strategy_and_profiles.md`

## Constraints

- We're bootstrapped. The email pipeline needs to work at scale with AI-generated content, not hand-written emails.
- Accuracy matters more than completeness. A wrong data point in a personalized email destroys credibility. If we're not confident in a data point, don't use it.
- Both buyer types (nonprofit and foundation) need separate angle strategies. Don't merge them.
- The government funding cuts angle is timely right now. Factor in that this urgency has a shelf life — also brainstorm angles that work regardless of political climate.
- The prospect profiles will be fed to an AI to write emails — so the schema needs to be structured for prompt consumption, not just human reading.
- Anchor everything to positive reply rate. Opens don't matter. Total replies include "stop emailing me." We want conversations.
