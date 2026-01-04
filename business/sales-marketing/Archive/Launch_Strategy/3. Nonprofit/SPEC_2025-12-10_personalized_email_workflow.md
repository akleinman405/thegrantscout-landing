# Personalized Email Outreach Workflow
**Date:** 2025-12-10
**Purpose:** Efficient system for Claude Code to write personalized emails to prospects from database

---

## The Challenge

True personalization requires research per org — that's slow. Sending generic emails gets ignored. Solution: **tiered approach** that matches effort to prospect value.

---

## Tiered Personalization Model

| Tier | Prospects | Personalization Level | Time per Email | Daily Volume |
|------|-----------|----------------------|----------------|--------------|
| **1** | Top 10 by score | Full research (website, news, mission) | 5-10 min | 5-10 |
| **2** | Next 50 | Template + mission/sector reference | 1-2 min | 20-50 |
| **3** | Rest | Mail merge (name, org, sector, location) | Seconds | 100+ |

**Daily total:** 90-140 emails, with top 10 highly personalized

---

## Tier 1: High-Touch Research

**When:** Top prospects, highest ICP scores, warmest angles

**Process:**
1. Query top 10 prospects not yet contacted
2. For each org, Claude:
   - Fetches website (about page, mission, programs)
   - Searches news ("[org name] grant" or "[org name] expansion")
   - Pulls F990 data (grants received, revenue trend, funders)
   - Checks for any beta client connection (shared funder, geography, sector)
3. Generate truly personalized email with specific hooks
4. Output as draft for human review
5. Mark status = "drafted"

**Personalization hooks:**
- "I saw your [specific program] serving [population] in [city]"
- "Congratulations on the recent grant from [Foundation]"
- "Your growth from $X to $Y suggests you're expanding — finding new funders is probably top of mind"
- "We helped [beta client] who works in [similar sector] — thought this might be relevant"

**Example Tier 1 Email:**
```
Subject: Grant discovery for [Org Name]

Hi [Name],

I came across [Org Name]'s work providing [specific program] to [population] in [City]. Your growth over the past few years caught my attention.

I run TheGrantScout — we help nonprofits discover foundation funding they don't know about. We analyze IRS 990 data to find foundations that fund similar work but aren't on your radar yet.

I noticed you've received grants from [Foundation X] and [Foundation Y]. Based on your profile, there are likely 10-15 other foundations that fund [sector] work in [state] that you haven't approached.

Worth 15 minutes to see if this could help?

Best,
Alec
```

---

## Tier 2: Template + Variables

**When:** Good prospects, solid ICP fit, but not worth full research

**Process:**
1. Query next 50 prospects (by score, not yet contacted)
2. Pull from database:
   - org_name, contact_name, contact_title
   - sector, state, city
   - mission statement (from 990 or enrichment)
   - num_foundation_grants, notable funder (if any)
   - revenue, revenue_trend
3. Claude selects best template based on sector/angle
4. Fills variables + adds one custom sentence
5. Batch output as CSV or email queue

**Template Types:**

**Template A: Healthcare (NTEE E)**
```
Subject: Foundation funding for [org_name]

Hi [contact_name],

Healthcare nonprofits like [org_name] often miss foundation funding because there's no time to research who's giving to similar organizations.

We help by matching nonprofits with foundations based on actual giving patterns — not just keyword searches. [One custom sentence about their specific work or location].

Would a list of 10 foundations funding healthcare work in [state] be useful?

Alec
```

**Template B: Human Services (NTEE P)**
```
Subject: Finding funders for [org_name]

Hi [contact_name],

I work with human services nonprofits to find foundation funding they don't know about.

Most organizations know maybe 20% of the foundations that could fund their work. We close that gap using IRS 990 data to find matches based on giving history, geography, and program focus. [One custom sentence].

Worth a quick conversation?

Alec
```

**Template C: Few Grants Received**
```
Subject: Foundation funding opportunities for [org_name]

Hi [contact_name],

I noticed [org_name] hasn't received many foundation grants — which often means there's untapped opportunity.

We specialize in helping nonprofits find foundation funding sources they don't know about. Based on your work in [sector] serving [population], there are likely foundations already funding similar organizations. [One custom sentence].

Would it be helpful to see what's out there?

Alec
```

**Template D: Growing Revenue**
```
Subject: Funding to support [org_name]'s growth

Hi [contact_name],

[org_name]'s growth over the past few years suggests you're expanding your impact. Finding new funders to support that growth is probably on your radar.

We help nonprofits discover foundation funding sources they don't know about — using IRS 990 data to match you with foundations already funding similar work. [One custom sentence].

15 minutes to see if this could help?

Alec
```

**Template E: Geographic/Beta Client Angle**
```
Subject: Grant discovery — worked with [beta_client] in [state]

Hi [contact_name],

We recently helped [beta_client_name] in [state] identify new foundation funding opportunities. Given [org_name]'s similar focus on [sector], thought this might be relevant.

We analyze IRS 990 data to find foundations that fund similar work — not the obvious ones, but hidden matches based on giving patterns. [One custom sentence].

Worth a conversation?

Alec
```

---

## Tier 3: Mail Merge

**When:** Broad outreach, testing response rates, filling pipeline

**Process:**
1. Query remaining prospects in target segment
2. Simple variable replacement: {name}, {org}, {city}, {sector}
3. No custom research
4. Send via email script
5. Track opens/replies — high responders get upgraded to Tier 1

**Template:**
```
Subject: Foundation funding for {org_name}

Hi {contact_name},

I help {sector} nonprofits in {state} find foundation funding they don't know about.

Most organizations know maybe 20% of the foundations that could fund their work. We use IRS 990 data to find the other 80%.

Would a list of matched foundations be helpful for {org_name}?

Alec
```

---

## Database Schema to Support This

### Additions to prospects table:

```sql
-- Enrichment fields
website TEXT,
mission_statement TEXT,
contact_name TEXT,
contact_title TEXT,
contact_email TEXT,
contact_phone TEXT,

-- Research cache (for Tier 1)
website_about_text TEXT,
recent_news TEXT,
notable_funder TEXT,
beta_client_connection TEXT,  -- "Same funder as Horizons" or "Same sector as SNS"

-- Personalization fields
personalization_tier INT,        -- 1, 2, or 3
personalization_hook TEXT,       -- "Congratulations on Ford Foundation grant"
email_template_id TEXT,          -- template_healthcare, template_human_services, etc.
custom_sentence TEXT,            -- One custom line for Tier 2
email_draft TEXT,                -- Full generated draft

-- Tracking
outreach_status TEXT,            -- not_contacted, drafted, sent, opened, replied, bounced, converted
email_sent_date DATE,
email_opened BOOLEAN,
email_replied BOOLEAN,
reply_sentiment TEXT,            -- positive, negative, unsubscribe
next_followup_date DATE,
notes TEXT
```

---

## Daily Workflow

| Time | Action | Volume | Output |
|------|--------|--------|--------|
| **Morning** | Pull top 10 Tier 1 prospects | 10 | Prospect list with org details |
| | Claude researches each (website, news, F990) | 10 | Research notes per org |
| | Claude writes personalized emails | 10 | Email drafts |
| | You review and send | 10 | High-quality emails out |
| **Midday** | Pull next 30-50 Tier 2 prospects | 30-50 | Prospect list |
| | Claude selects template + fills variables | 30-50 | Email drafts |
| | Quick review, send | 30-50 | Mid-quality emails out |
| **Background** | Tier 3 drip runs automatically | 50-100 | Basic emails via script |
| **End of Day** | Check replies, update statuses | — | Pipeline updated |

---

## Claude Code Prompt Structure

### Tier 1 Prompt (run daily):
```
1. Connect to database
2. Query top 10 prospects WHERE:
   - outreach_status = 'not_contacted'
   - icp_score >= 7
   - contact_email IS NOT NULL
   ORDER BY icp_score DESC, priority_tier ASC
   LIMIT 10

3. For each prospect:
   a. Fetch website (web_fetch tool)
   b. Search news (web_search: "[org name] grant OR award OR expansion")
   c. Pull F990 grant history
   d. Check for beta client connection (shared funder, same state, same sector)
   e. Generate personalized email
   f. Save draft to email_draft column
   g. Update outreach_status = 'drafted'

4. Output: 10 email drafts for review
```

### Tier 2 Prompt (run daily):
```
1. Connect to database
2. Query next 50 prospects WHERE:
   - outreach_status = 'not_contacted'
   - icp_score >= 4
   - contact_email IS NOT NULL
   ORDER BY icp_score DESC
   LIMIT 50

3. For each prospect:
   a. Select template based on sector + angle
   b. Fill variables from database
   c. Generate one custom sentence based on mission/location
   d. Save to email_draft column
   e. Update personalization_tier = 2

4. Output: CSV of 50 emails ready to send
```

---

## Questions to Resolve

| Question | Options |
|----------|---------|
| **Where do contact emails come from?** | Email finding script? Hunter.io? Manual? |
| **Where do missions come from?** | Already in 990 data? Scrape from websites? |
| **Review before send?** | All tiers? Just Tier 1? Trust Tier 2/3? |
| **Sending method?** | Existing email campaign script? Brevo? Gmail? |
| **Followup automation?** | Auto-send followup if no reply in 5 days? |
| **Response handling?** | Manual check or integrate inbox? |

---

## Expected Results

| Tier | Daily Volume | Expected Response Rate | Replies/Day |
|------|--------------|------------------------|-------------|
| 1 | 10 | 10-15% | 1-2 |
| 2 | 40 | 3-5% | 1-2 |
| 3 | 100 | 1-2% | 1-2 |
| **Total** | **150** | — | **3-6** |

At 3-6 replies/day, with 20-30% converting to calls, that's **1-2 calls/day** from email alone.

---

## Summary

The key insight: **Not all prospects deserve equal effort.** 

- Top prospects get full research and custom emails
- Good prospects get smart templates
- Everyone else gets basic outreach

The database enables this by storing enrichment, templates, and tracking in one place. Claude Code handles the research and writing. You handle review and relationships.

---

*Document: SPEC_2025-12-10_personalized_email_workflow.md*
