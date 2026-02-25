# PROMPT: Email Prompt Engineering — How to Get AI to Write Great Cold Emails at Scale

**Date:** 2026-02-16
**Agent:** Claude Code CLI (multi-agent)
**Type:** Research + prompt design + pipeline architecture
**Pipeline Phase:** 4 (Write Emails)
**Prerequisite:** Run AFTER the cold email strategy + prospect profile prompt. This prompt uses those outputs.
**Anchor KPI:** Positive reply rate

---

## Start in Planning Mode

Before doing any research, agents should first:
1. Read this prompt carefully
2. Read the output from the strategy/profile research: `Enhancements/2026-02-16/REPORT_2026-02-16_cold_email_strategy_and_profiles.md`
3. Deliberate with each other on whether the scope, questions, and structure are right
4. Recommend any changes to the prompt (missing angles, wrong assumptions, better framing)
5. Present the agreed-upon research plan for my approval before proceeding

## Problem

We need to generate hundreds or thousands of personalized cold emails using AI (Claude via API or Claude Code). Each email will be powered by a structured prospect profile (built in the previous phase). The challenge is making every email feel:

- **Researched** — references specific, accurate details about the recipient's org
- **Human** — doesn't sound like AI wrote it, no corporate buzzwords, no filler
- **Relevant** — clear why we're reaching out to THEM specifically
- **Valuable** — gives them something useful (named funders, specific insights) not just a sales pitch
- **Brief** — respects their time, gets to the point
- **Actionable** — clear next step that's low-friction (not "schedule a demo")
- **Generous** — the "give first" angles mean some emails are literally offering a free resource, not selling

We need a repeatable pipeline: profile in → quality email out, at scale, with quality control.

## Phase 1: Research — What Works for AI-Written Outreach

**Research Agent(s):** Search the internet for:

**AI email generation best practices:**
- How are companies using LLMs (Claude, GPT, etc.) to write personalized cold emails at scale?
- What prompt engineering techniques produce the most natural-sounding outreach?
- How do you avoid the "AI voice" — the telltale patterns that make AI emails obvious?
- What's the right balance of templated structure vs freeform generation?
- Few-shot prompting vs detailed system prompts — what works best for email?
- How do you prompt for the "give first" tone — generous, peer-to-peer, not transactional?

**Deliverability and spam:**
- What spam trigger phrases should we avoid? (Especially around crisis/urgency language)
- Link density impact on deliverability
- Plain text vs HTML — which performs better for cold outreach and why?
- Email length vs spam scoring — is there a sweet spot?
- Does government funding "crisis language" (cuts, lost funding, struggling) trigger spam filters?
- How do AI-generated emails score on spam detection tools? Any known patterns to avoid?

**Quality control at scale:**
- How do you review hundreds of AI-generated emails before sending?
- AI-as-reviewer: can a second AI pass catch quality issues? What does that prompt look like?
- What scoring rubrics work for email quality? (personalization depth, accuracy, tone, length, CTA clarity)
- Human-in-the-loop approaches — where does human review add most value?
- How do you catch hallucinated or inaccurate data points before they go out?

**Prompt architecture:**
- Single mega-prompt vs chained prompts (draft → review → revise)?
- How to structure the prospect profile data in the prompt for best results?
- System prompt vs user prompt — where do style guidelines go?
- Temperature and model selection for email generation
- How to maintain voice consistency across hundreds of emails while varying content?

**Nonprofit/foundation-specific tone:**
- What tone works for nonprofit outreach? (Peers, not vendors. Helpful, not salesy.)
- How do you reference someone's mission or work without sounding like you copy-pasted their website?
- How to reference government funding cuts without being alarmist or exploitative?
- How to mention specific grantees in foundation emails respectfully?
- How to frame "here's a free resource" without it feeling like a lead magnet trap?

**Checkpoint: Present research findings for approval before Phase 2.**

## Phase 2: Design the Email Writing Pipeline

After research is approved, agents design the full pipeline:

### 2A: Pipeline Architecture

Map the end-to-end flow from prospect profile to sent email:

1. **Input preparation** — How does the prospect profile get formatted for the prompt? JSON? Structured text? What fields are mandatory vs optional?
2. **Profile depth check** — Before generating, classify the profile: rich (many data points), moderate, thin. This determines which email template/angle to use.
3. **Email generation** — The core prompt(s).
4. **Quality review** — A second AI pass.
5. **Revision** — If review flags issues, how does the email get revised?
6. **Human review queue** — Which emails need human eyes?
7. **Batch processing** — How to generate 100-500 emails in a session efficiently

### 2B: Hard Accuracy Controls

**This is non-negotiable.** A personalized email with wrong information destroys credibility and reputation.

The pipeline MUST enforce:
- **Every factual claim in the email must map to a specific field in the prospect profile.** The generator cannot add external facts, statistics, or details that aren't in the profile.
- **The review agent must verify field-to-text alignment.** For each factual claim, the reviewer checks: is this in the profile? Is it stated accurately? Is the data point current?
- **The generator is explicitly forbidden from "improving" the data** — no rounding numbers, no inferring details, no filling gaps with plausible-sounding information.
- **If a data point seems wrong or inconsistent, flag it — don't use it.**

### 2C: Personalization Depth Rules

Not every email should be maximally personalized. Design a tiered system:

**Tier 1 — Rich profile (15+ data points):**
Full personalization. Reference specific grants, funding sources, grantees, sector details.

**Tier 2 — Moderate profile (8-14 data points):**
Moderate personalization. Reference sector, geography, org type. Don't stretch thin data.

**Tier 3 — Thin profile (under 8 data points):**
Simple, honest email. "We help [org type] in [state] find foundation funding. Would a list of top funders in your sector be useful?" Do NOT fake specificity. A clean simple email beats a poorly personalized one.

**Personalization ceiling:** Research and define where personalization crosses from "thoughtful" to "creepy." Foundation outreach especially — referencing specific grantees by name with funding details could feel like surveillance. Define the comfort band.

### 2D: Prompt Drafts

For each combination of buyer type × angle × profile tier, draft:

**Email types (at minimum):**
- Nonprofit, "give first" angle (state/sector foundation list offer)
- Nonprofit, funding cuts angle (specific lost funding + named alternatives)
- Nonprofit, opportunity angle (new funders in their space)
- Nonprofit, thin profile fallback
- Foundation, grantee impact angle (specific grantees lost funding)
- Foundation, capacity-building offer (help your grantees find funding)
- Foundation, "give first" angle (grantee vulnerability brief offer)
- Foundation, thin profile fallback

**For each, draft:**
- The full system prompt (voice, constraints, anti-patterns, accuracy rules)
- The user prompt template (where profile data gets injected)
- 2-3 example outputs showing what "good" looks like at each tier
- The review prompt
- Scoring rubric

### 2E: Anti-Pattern Library

Compile a comprehensive list of specific phrases, patterns, and structures that make AI emails obvious or trigger spam filters. These go into the system prompt as explicit "never do this" instructions.

**AI voice tells (research and expand):**
- "I hope this email finds you well"
- "I came across your organization and was impressed by..."
- Starting with "I"
- Listing three adjectives in a row
- Generic mission statement paraphrasing
- "In today's challenging landscape..."
- "I wanted to reach out because..."
- Excessive hedging ("I thought you might perhaps be interested...")
- Over-explaining why you're emailing before getting to the point

**Spam triggers (research and expand):**
- Urgency language ("act now", "don't miss out")
- Crisis exploitation language
- Too many links
- ALL CAPS words
- Exclamation points
- "Free" in subject lines (context-dependent)

**Nonprofit-specific cringe:**
- Parroting their mission statement back to them
- "Your important work" / "your noble mission"
- Treating them as charity cases rather than peers
- Assuming they're desperate

**Checkpoint: Present pipeline design and draft prompts for approval before Phase 3.**

## Phase 3: Test Framework

### 3A: Small Batch Test

- Pick 10 nonprofits and 10 foundations with varying profile depths (some rich, some thin)
- Generate emails for each using the draft prompts
- Run through the review prompt
- Human review all 20
- Score each on: would I send this? Does anything feel wrong? Is it specific enough? Does the "give first" offer feel genuine?
- Compare: which angles produced the best emails? Which profile tier produced surprising quality?

### 3B: Accuracy Audit

- For every factual claim in the 20 test emails, trace it back to the prospect profile
- Flag any claim that doesn't match, was embellished, or was inferred
- This tests whether the accuracy controls actually work

### 3C: Iteration Protocol

- How do we improve prompts based on test results?
- What failure modes should we watch for?
- How many test rounds before scaling?

### 3D: Scale Test

- Generate 100 emails (mix of angles, buyer types, profile tiers)
- AI review all 100, human review random 20%
- Measure: consistency, quality variance, time per email, API cost per email
- Identify: which angle × tier combinations work best, which need more iteration

### 3E: KPI Targets

Define targets before testing so we have something to measure against:
- Target positive reply rate: ___% (agents should recommend based on Phase 1 research)
- Target "freebie requested" rate (for give-first angles): ___%
- Target freebie-to-paid conversion rate: ___%
- Acceptable bounce rate: under 2%
- Acceptable spam complaint rate: under 0.1%

## Output

A single report with:

1. **Executive Summary** — 5 key insights, 3 recommended actions, 1 "don't pursue" recommendation
2. **Research findings** — what works for AI email generation, give-first in cold email, deliverability
3. **Pipeline architecture** — flowchart from profile to sent email, including accuracy controls and tiering
4. **Personalization comfort band** — where the line is between thoughtful and creepy, with specific examples
5. **Draft prompts** — full system + user prompts for each email type × profile tier
6. **Anti-pattern library** — comprehensive list of AI tells + spam triggers + nonprofit cringe
7. **Review prompt + scoring rubric**
8. **Test framework** — small batch → accuracy audit → iteration → scale
9. **KPI targets** — recommended targets with rationale from research
10. **Cost estimate** — API cost per email at our likely model/token usage
11. **Open questions** — what needs real-world testing

Save to `Enhancements/2026-02-16/REPORT_2026-02-16_email_prompt_engineering.md`

## Constraints

- We use Claude (Anthropic API). Prompts should be optimized for Claude, not GPT.
- Accuracy above all. A personalized email with wrong information is worse than a generic one. The pipeline MUST have accuracy checks that actually work.
- The "give first" angles should feel genuinely generous — not like a lead magnet funnel. If the free resource isn't good enough to stand on its own, it's not good enough.
- We're not trying to trick anyone into thinking a human wrote each email. We're trying to write emails that are genuinely thoughtful, specific, and useful — at a scale a human couldn't achieve alone.
- Budget matters. If each email costs $0.50 in API calls, that's probably fine. If it costs $5.00, we need to optimize.
- The government funding cuts angle is timely NOW. But also design angles that work after the urgency fades.
- Don't just research — produce usable draft prompts we can test this week.
- Anchor everything to positive reply rate. That's our north star.
