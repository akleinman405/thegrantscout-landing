# TheGrantScout Report Section Definitions

## Purpose

This document provides detailed specifications for each section of the Weekly Grant Opportunities Report and Email Brief. Use this as a reference when generating reports to ensure consistency, accuracy, and appropriate depth.

---

## Document Overview

| Document | Purpose | Target Length | Audience |
|----------|---------|---------------|----------|
| **Email Brief** | Quick summary to drive action | 1 page (~400 words) | Executive Director, Development Director |
| **Weekly Report** | Detailed intelligence for grant pursuit | 10-15 pages | Grants Manager, Program Staff |

---

## Email Brief Sections

### Subject Line

**Purpose:** Drive opens, communicate urgency  
**Format:** `Week [X]: Your Top 5 Grant Opportunities - [URGENT flag if applicable]`  
**Length:** Under 60 characters ideal  
**Include URGENT flag when:** Any deadline is within 30 days  

**Examples:**
- `Week 3: Your Top 5 Grant Opportunities - URGENT: NIOSH Due Dec 12`
- `Week 5: Your Top 5 Grant Opportunities`

---

### Opening Paragraph

**Purpose:** Orient reader, highlight most critical action  
**Length:** 2-3 sentences  
**Must include:**
1. "If you only do one thing this week" statement
2. Count of opportunities
3. Any urgent deadlines with specific dates

**Example:**
> Welcome to your Week 3 grant opportunity brief from TheGrantScout. **If you only do one thing this week:** Contact NIOSH program officer by November 25. This week's report highlights five opportunities, with one urgent deadline: NIOSH R13 closes December 12.

---

### This Week's 5 Opportunities Table

**Purpose:** Scannable overview of all opportunities  
**Columns:**
| Column | Description | Example Values |
|--------|-------------|----------------|
| # | Priority rank 1-5 | 1, 2, 3, 4, 5 |
| Funder | Foundation/agency name | "Commonwealth Fund" |
| Amount | Funding range | "$50,000 - $200,000" |
| Deadline | Date or "Rolling" | "Dec 12, 2025" or "Rolling" |
| Effort | Application complexity | Low / Med / High |
| Why This Week | One phrase justification | "URGENT deadline" / "Strong 9/10 fit" |

**Effort definitions:**
- **Low:** LOI only, simple 2-5 page application, no complex attachments
- **Medium:** Standard proposal (10-20 pages), budget required, 2-3 attachments
- **High:** Federal grant package, multi-part application, biosketches, data management plans

---

### Immediate Actions

**Purpose:** Prioritized to-do list  
**Format:** Checkbox list with deadlines and actions  
**Length:** 4-5 items max  
**Prioritize by:** Deadline urgency, then strategic importance  

**Example:**
```
- [ ] **By December 12:** Submit NIOSH R13 application
- [ ] **By November 30:** Register for Commonwealth Fund portal
- [ ] **This Week:** Sign up for Macy Foundation mailing list
```

---

### Feedback Request (Beta Period Only)

**Purpose:** Collect input to improve reports  
**Length:** 3-4 lines  
**Include:** Specific questions about opportunity relevance and report usefulness

---

## Weekly Report Sections

### Header Block

**Purpose:** Quick reference metadata  
**Required fields:**
- Organization Name
- Week Number
- Report Date
- Urgent Deadlines count + nearest date
- Total Potential Funding range

**Total Potential Funding calculation:** Sum of maximum amounts for all 5 opportunities. Use range if amounts vary significantly.

---

### If You Only Do One Thing This Week

**Purpose:** Single most critical action for busy executives  
**Length:** Exactly 1 sentence  
**Format:** Blockquote  
**Selection criteria:** Choose the action with:
1. Nearest hard deadline, OR
2. Highest strategic impact if no urgent deadlines

**Good example:**
> **Contact NIOSH program officer by November 25 to discuss your December 12 application.**

**Bad example (too vague):**
> **Start working on your grant applications.**

---

### Executive Summary - Urgent Actions Table

**Purpose:** Prioritized action items with accountability  
**Columns:** Priority (1-3), Action, Deadline, Contact/Owner  
**Length:** 3 rows maximum  
**Selection criteria:** Include only actions needed in next 14 days

---

### Executive Summary - Funding Scenarios

**Purpose:** Set realistic expectations for success  
**Three rows:**
| Scenario | Definition | Calculation |
|----------|------------|-------------|
| Conservative | 1-2 wins, lowest amounts | Sum of 2 smallest minimums |
| Moderate | 2-3 wins, mid amounts | Sum of 3 median amounts |
| Ambitious | 4-5 wins, higher amounts | Sum of 4-5 maximums |

---

### Executive Summary - Key Strengths

**Purpose:** Remind client of their competitive advantages for THIS WEEK's opportunities  
**Length:** 3 bullet points, 1 sentence each  
**Must be specific to:** The intersection of client's strengths AND this week's funders' preferences

**Good example:**
> **Proven Precedent:** Mid-Pacific School received $200,000 from Atherton for track facilities in 2024—direct model for your application.

**Bad example (generic):**
> **Strong Mission:** Your organization does good work.

---

### This Week's Top 5 Table

**Purpose:** Master reference for all opportunities  
**Columns:**
| Column | Source | Notes |
|--------|--------|-------|
| # | Assignment | Rank by priority (deadline + fit) |
| Funder | Opportunity research | Official foundation/agency name |
| Amount | 990-PF or website | Format as range "$X - $Y" |
| Deadline | Website/990-PF Part XIV | Specific date or "Rolling" |
| Fit | Matching algorithm | Score 1-10 based on mission, geography, size, history |
| Effort | Application analysis | Low/Med/High per definitions above |
| Status | Priority assessment | URGENT (<30 days) / HIGH / MEDIUM |

---

### Why Not This Week

**Purpose:** Show filtering rigor, manage expectations  
**Length:** 1-2 sentences  
**Must state:** How many reviewed, why excluded  
**Common exclusion reasons:**
- Deadlines too far out (>90 days)
- Funding amount misalignment
- Geographic restrictions
- Sector mismatch
- Foundation not accepting unsolicited proposals

---

## Opportunity Deep Dive Sections

### Why This Fits

**Purpose:** Justify inclusion, build confidence  
**Length:** 3-4 sentences maximum  
**Must address:**
1. Mission/program alignment (1 sentence)
2. Precedent or comparable grants if available (1 sentence)
3. Why NOW—timing rationale (1 sentence)

**Data sources:**
- Client questionnaire (mission, programs)
- f990_grants (comparable grants)
- Opportunity deadline

---

### Key Details Table

**Purpose:** Essential logistics at a glance  
**Required fields:**

| Field | Source | Format |
|-------|--------|--------|
| Amount | 990-PF, website | "$X - $Y" or "Up to $X" |
| Deadline | Website, 990-PF Part XIV | "Month DD, YYYY" or "Rolling" |
| Portal | Website | Full URL |
| Contact | 990-PF Part XIV, website | "Name, email, phone" |
| Prior Relationship | Client history, database | "None" / "Applied YYYY" / "Received $X in YYYY" / "Board connection: [Name]" |

---

### Funder Snapshot

**Purpose:** Data-driven intelligence on funder behavior  
**Length:** 8-row table  
**All metrics derived from F990 database queries**

| Metric | Query/Calculation | Format | Notes |
|--------|-------------------|--------|-------|
| **Annual Giving** | SUM(grant_amount) WHERE foundation_ein = X, GROUP BY tax_year, most recent year | "$X.XM across XX grants" | Use most recent complete tax year |
| **Typical Grant** | MEDIAN(grant_amount), MIN, MAX for foundation | "$XX,000 median (range: $X,000 - $XXX,000)" | Helps client size their ask |
| **Geographic Focus** | COUNT by recipient_state / total COUNT | "[XX]% [State], [XX]% in-state overall" | In-state = same state as foundation |
| **Repeat Funding Rate** | COUNT recipients with 2+ grants / total unique recipients | "[XX]% of recipients funded 2+ times" | Higher = values relationships |
| **Giving Style** | Categorize grant_purpose: "general/operating/unrestricted" vs "program/project/specific" | "[XX]% general support / [XX]% program-specific" | Based on keyword matching in purpose field |
| **Recipient Profile** | Join recipient EIN to IRS BMF for budget, NTEE | "Typically $[X-X]M budget, [sector] focus" | If EIN not available, describe from grant list |
| **Funding Trend** | Compare total_giving across 3 years | "Growing/Stable/Declining ([X]% change over 3 years)" | Growing = >10% increase, Declining = >10% decrease |
| **Comparable Grant** | Find grant to similar org (same state, similar NTEE, similar size) | "[Org Name] received $[XX,000] for [purpose] ([Year])" | Most recent, most similar to client |

**Giving Style categorization keywords:**
- General support: "general", "operating", "unrestricted", "charitable", "support"
- Program-specific: "program", "project", "for [specific purpose]", named initiatives

**Important limitation:** 91.9% of grant purposes are under 50 characters. Do not oversell "language analysis"—stick to simple categorization.

---

### Potential Connections

**Purpose:** Surface relationship advantages  
**Length:** 1-3 rows  
**Connection types:**

| Type | Definition | How to Find |
|------|------------|-------------|
| **Direct Board Overlap** | Person serves on both client board and funder board | Match f990_officers (funder) against client board list |
| **Shared Network** | Client board member serves on board of org that funder has funded | Client board → their other boards → funder's grantees |
| **Prior Funder Contact** | Client has received funding from this funder before | historical_grants WHERE recipient matches client |
| **None Identified** | No connections found | Default if no matches |

**Matching methodology:**
- Use fuzzy matching (Jaro-Winkler, threshold 0.90+)
- Match on: First name + Last name + State/City
- Flag matches 0.80-0.90 as "Possible match - verify"
- Common names (John Smith) require additional verification

---

### Application Requirements

**Purpose:** Checklist of what's needed  
**Format:** Bullet list, 5-8 items  
**Source:** Foundation website, 990-PF Part XIV, RFA/RFP document  
**Include:**
- Document types (LOI, full proposal, budget)
- Page limits
- Required attachments (501c3 letter, financials, board list)
- Specific forms or portals
- Registration requirements

---

### Positioning Strategy

**Purpose:** Actionable advice on how to frame the application  
**Length:** 3-4 sentences  
**MUST reference specific data from Funder Snapshot**

**Formula:**
1. Lead with giving style recommendation (sentence 1)
2. Suggest ask amount based on typical grant (sentence 2)
3. Address geographic or sector positioning (sentence 3)
4. Note any relationship leverage or timing considerations (sentence 4)

**Good example:**
> Emphasize general operating support—62% of their grants use this structure, and they rarely fund narrow project proposals. Their $45K median suggests requesting $40-50K; their largest grant was $150K but that went to a university. Highlight your California presence prominently; 78% of their giving stays in-state. If possible, mention your connection to [Org Name], which they've funded for 5 consecutive years.

**Bad example (generic, no data):**
> Write a strong proposal that aligns with their mission. Ask for an appropriate amount. Make sure to highlight your strengths.

---

### Next Steps Table

**Purpose:** Specific actions with accountability  
**Columns:** Action, Deadline, Owner  
**Length:** 3-5 rows per opportunity  
**Owner options:** Grants Manager, Program Director, ED, Finance, Development, Board

**Action specificity:** Use verbs + specific deliverables
- Good: "Draft 2-page LOI concept"
- Bad: "Work on application"

---

## 8-Week Timeline

**Purpose:** Multi-week planning across all opportunities  
**Format:** Table with Week, Dates, Focus, Key Milestones  
**Length:** 8 rows  

**Focus column:** Name the primary opportunity or activity for that week  
**Key Milestones:** 2-3 specific deliverables or deadlines

**Distribution logic:**
- Weeks 1-2: Urgent deadlines, immediate submissions
- Weeks 3-4: Secondary deadlines, LOI submissions
- Weeks 5-6: Longer-term preparation, relationship building
- Weeks 7-8: Pipeline development, monitoring

---

## Quick Reference Section

**Purpose:** All contact info and deadlines in one place  
**Tables:**
1. Contacts: Funder, Contact Name, Email, Phone
2. Portals & Deadlines: Funder, Portal URL, Deadline

**Source:** Compiled from all 5 opportunity deep dives

---

## Data Sources Reference

| Data Element | Primary Source | Backup Source | Database Table |
|--------------|----------------|---------------|----------------|
| Funder name, EIN | f990_foundations | Website | foundations |
| Grant amounts | f990_grants | Website | historical_grants |
| Grant purposes | f990_grants.grant_purpose | — | historical_grants |
| Geographic data | f990_grants.recipient_state | — | historical_grants |
| Board/officers | f990_officers | Website, 990-PF PDF | f990_officers |
| Contact info | 990-PF Part XIV | Website | foundations |
| Application process | Website | 990-PF Part XIV | foundations.application_process |
| Deadlines | Website | 990-PF Part XIV | current_grants.deadline |
| Recipient profile | IRS BMF via recipient EIN | Grant list analysis | irs_bmf |
| Client info | Questionnaire | Nonprofit's 990 | nonprofits |

---

## Quality Checklist

Before finalizing any report, verify:

- [ ] All 5 opportunities are currently accepting applications (not closed/paused)
- [ ] Deadlines are accurate and verified within past 7 days
- [ ] Funding amounts match current program guidelines
- [ ] Funder Snapshot metrics are calculated from actual database queries
- [ ] Comparable grants are real (verify org name and amount exist in database)
- [ ] Positioning strategy references specific Funder Snapshot data points
- [ ] Contact information is current (verify emails/URLs work)
- [ ] No "About [Org]" section—client knows their own organization
- [ ] Timeline is realistic given stated deadlines
- [ ] Total report length is 10-15 pages (not 50+)

---

## Common Errors to Avoid

1. **Generic positioning advice** — Always tie recommendations to specific Funder Snapshot data
2. **Unverified deadlines** — Confirm deadlines haven't changed since database was updated
3. **Overstating language analysis** — 91.9% of grant purposes are under 50 characters; don't claim sophisticated NLP insights
4. **Including "About [Org]" sections** — Wastes space telling client about themselves
5. **Day-by-day timelines** — Use week-by-week; nobody follows 60-day daily calendars
6. **False connections** — Only report board connections with 90%+ match confidence; flag others as "possible"
7. **Missing Funder Snapshot** — Every opportunity needs the full 8-metric snapshot
8. **Vague Next Steps** — "Work on application" is not actionable; "Draft 2-page LOI by Friday" is

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-01 | Initial definitions document |

---

*This document should be updated whenever report templates change or new data sources become available.*
