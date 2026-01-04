# SKILL: Foundation Website Scraper

**Purpose:** Extract standardized enrichment data from private foundation websites to populate the `foundation_enrichment` database table.

---

## Overview

When researching a foundation for grant matching, you need to extract specific fields from their website. This skill provides consistent instructions for finding and formatting this data.

## Required Output Fields

| Field | Type | Description | Where to Look |
|-------|------|-------------|---------------|
| `accepts_unsolicited` | boolean | Do they accept applications from unknown orgs? | Guidelines, FAQ, "How to Apply" |
| `application_type` | enum | How do they accept applications? | Guidelines, "How to Apply" |
| `application_url` | string | Direct link to apply/submit | "Apply" button, Guidelines |
| `current_deadline` | date | Next deadline if any | RFP page, Guidelines, News |
| `deadline_notes` | string | Context about timing | Guidelines |
| `contact_name` | string | Program officer or grants contact | Staff page, Contact page |
| `contact_title` | string | Their role | Staff page |
| `contact_email` | string | Direct email | Staff page, Contact page |
| `contact_phone` | string | Phone if available | Contact page |
| `program_priorities` | text | What they say they fund | About, Focus Areas, Guidelines |
| `geographic_focus` | text | Geographic restrictions | Guidelines, About |
| `grant_range_stated` | string | Grant size range as stated | Guidelines, FAQ |
| `application_requirements` | text | What they ask for | Guidelines, "How to Apply" |
| `red_flags` | array | Concerns identified | Throughout |
| `enrichment_source` | string | Primary URL used | N/A |

---

## application_type Values

Use exactly one of these values:

| Value | When to Use |
|-------|-------------|
| `open` | Accept applications anytime, no specific process |
| `loi` | Require letter of inquiry first |
| `rfp_periodic` | Issue specific RFPs with deadlines |
| `rfp_rolling` | Accept proposals on rolling basis with periodic review |
| `invite_only` | Only fund orgs they already know or invite |
| `unknown` | Can't determine from website |

---

## Red Flags to Identify

Add to `red_flags` array if found:

| Flag | Trigger |
|------|---------|
| `no_unsolicited` | Explicitly states "do not accept unsolicited proposals" |
| `invite_only_strict` | "Grants by invitation only" with no exceptions noted |
| `no_public_process` | No grants page, no guidelines, no application info |
| `possibly_dormant` | Website not updated in 2+ years, or last grants are old |
| `mission_mismatch` | Their stated priorities don't match client at all |
| `geographic_mismatch` | Explicit geographic restriction excluding client |
| `budget_mismatch` | Only fund orgs much larger/smaller than client |
| `sector_mismatch` | Don't fund client's sector based on explicit statement |
| `program_only` | Explicitly state they don't fund capital/facilities (for capital-seeking clients) |
| `capital_only` | Explicitly state they only fund capital (for program-seeking clients) |

---

## Scraping Process

### Step 1: Find the Foundation Website

**If not in database:**
1. Search: `"{foundation_name}" foundation grants`
2. Look for official .org or .com domain
3. Verify EIN matches if shown on site
4. Avoid: Charity navigator profiles, GuideStar, news articles

### Step 2: Locate Key Pages

Navigate to find these pages (may have different names):

| Target | Common Names |
|--------|--------------|
| Grants page | "Grants", "Grantmaking", "What We Fund", "Our Work" |
| Guidelines | "Guidelines", "How to Apply", "Application Process", "For Grantseekers" |
| Staff page | "Team", "Staff", "About Us", "Leadership" |
| Contact page | "Contact", "Contact Us", "Get in Touch" |
| News/RFPs | "News", "Announcements", "Current Opportunities", "RFPs" |

### Step 3: Extract accepts_unsolicited

**Look for explicit statements:**

| Statement | Value |
|-----------|-------|
| "We accept letters of inquiry" | `true` |
| "Submit a proposal through our portal" | `true` |
| "We welcome applications from..." | `true` |
| "We do not accept unsolicited proposals" | `false` |
| "Grants are by invitation only" | `false` |
| "We identify grantees through our own research" | `false` |
| No grants page or application info | `null` (unknown) |

**If ambiguous:** Set to `null` and note in `enrichment_notes`

### Step 4: Extract application_type

**Decision tree:**

1. Do they mention "letter of inquiry" or "LOI"? → `loi`
2. Do they post specific RFPs with deadlines? → `rfp_periodic`
3. Do they say "rolling basis" or "reviewed quarterly"? → `rfp_rolling`
4. Do they have an open application form/portal? → `open`
5. Do they say invitation only? → `invite_only`
6. Can't tell? → `unknown`

### Step 5: Extract Deadlines

**Look for:**
- Specific dates: "Applications due March 15, 2026"
- Cycles: "We review LOIs quarterly in March, June, September, December"
- Rolling: "Applications reviewed on a rolling basis"

**Format:**
- `current_deadline`: Next specific date (YYYY-MM-DD) or `null`
- `deadline_notes`: Context like "Annual deadline, typically spring" or "Rolling review"

### Step 6: Extract Contact Information

**Priority order:**
1. Named program officer on grants/guidelines page
2. Grants contact on contact page
3. Executive director if small foundation
4. General contact email if nothing else

**Format:**
- `contact_name`: "Jane Smith" (no titles in name field)
- `contact_title`: "Program Officer" or "Director of Grantmaking"
- `contact_email`: Direct email, not info@ if possible
- `contact_source`: URL where found (for verification later)

### Step 7: Extract Program Priorities

**Summarize in 1-3 sentences:**
- What sectors/causes do they fund?
- Any specific initiatives or focus areas?
- What do they say they're looking for?

**Example:**
> "Education and youth development, with emphasis on college access for first-generation students. Recently launched initiative on STEM education in rural communities."

### Step 8: Extract Geographic Focus

**Look for:**
- State/region restrictions: "We fund only in California"
- City focus: "Grants limited to San Francisco Bay Area"
- National: "We fund nationally" or no geographic mention
- International: Note if they fund outside US

### Step 9: Extract Grant Size

**Capture as stated on site:**
- Range: "$10,000 - $50,000"
- Average: "Average grant size is $25,000"
- Maximum: "Grants up to $100,000"

**Don't infer** from 990 data here - this field is what they SAY on website

### Step 10: Extract Application Requirements

**Summarize what they ask for:**
- LOI length/format
- Required attachments (budget, 501c3 letter, etc.)
- Online portal vs. email submission
- Any unusual requirements

**Example:**
> "2-page LOI via online portal. Requires: project budget, org budget, 501(c)(3) letter, list of board members. Full proposals by invitation only."

---

## Output Format

After scraping, format as JSON for `03b_store_enrichment.py`:

```json
{
  "ein": "123456789",
  "accepts_unsolicited": true,
  "application_type": "loi",
  "application_url": "https://examplefoundation.org/apply",
  "current_deadline": null,
  "deadline_notes": "LOIs reviewed quarterly (Mar, Jun, Sep, Dec)",
  "contact_name": "Sarah Johnson",
  "contact_title": "Director of Grantmaking",
  "contact_email": "sjohnson@examplefoundation.org",
  "contact_phone": "(555) 123-4567",
  "contact_source": "https://examplefoundation.org/team",
  "program_priorities": "Youth education and STEM access in underserved communities. Focus on college readiness and first-generation students.",
  "geographic_focus": "San Francisco Bay Area, with occasional national grants for replicable models",
  "grant_range_stated": "$15,000 - $50,000 for new grantees; up to $100,000 for renewals",
  "application_requirements": "2-page LOI with org background, project description, budget summary, and outcomes framework. Submit via online portal.",
  "red_flags": [],
  "enrichment_source": "https://examplefoundation.org/grants",
  "enrichment_notes": "Clear guidelines, very transparent process. Good fit for education-focused clients."
}
```

---

## Special Cases

### No Website Found

```json
{
  "ein": "123456789",
  "accepts_unsolicited": null,
  "application_type": "unknown",
  "red_flags": ["no_public_process"],
  "enrichment_notes": "No foundation website found. May operate privately or through fiscal sponsor."
}
```

### Website Exists But No Grants Info

```json
{
  "ein": "123456789",
  "accepts_unsolicited": null,
  "application_type": "unknown",
  "program_priorities": "Based on About page: focuses on arts and education",
  "red_flags": ["no_public_process"],
  "enrichment_notes": "Website exists but no grants/application information. May be invite-only or family foundation."
}
```

### Explicitly Invite-Only

```json
{
  "ein": "123456789",
  "accepts_unsolicited": false,
  "application_type": "invite_only",
  "program_priorities": "Healthcare and medical research",
  "red_flags": ["invite_only_strict", "no_unsolicited"],
  "enrichment_notes": "States 'We do not accept unsolicited proposals. All grants are initiated by the foundation.' Consider for relationship-building only."
}
```

### Foundation with Active RFP

```json
{
  "ein": "123456789",
  "accepts_unsolicited": true,
  "application_type": "rfp_periodic",
  "application_url": "https://foundation.org/2026-rfp",
  "current_deadline": "2026-03-15",
  "deadline_notes": "2026 Community Impact RFP open now. Annual cycle.",
  "red_flags": [],
  "enrichment_notes": "Active RFP! Deadline March 15, 2026. Good fit for community development clients."
}
```

---

## Client-Specific Considerations

### For Capital/Facility-Seeking Clients

When researching for clients wanting capital grants (Ka Ulukoa, RHF, Friendship Circle building):

**Additional things to look for:**
- Do they mention "capital grants", "building", "facilities", "equipment"?
- Do they explicitly exclude capital? ("We do not fund capital projects")
- Have they funded construction/renovation in the past? (Check 990 grant purposes)

**Add red flag if:**
- `program_only`: States "We fund programs only, not capital or equipment"

### For Program-Seeking Clients

**Add red flag if:**
- `capital_only`: States "We only fund capital projects" or "No program/operating support"

---

## Quality Checklist

Before submitting enrichment data:

- [ ] `accepts_unsolicited` has a value (true/false/null)
- [ ] `application_type` uses exact enum value
- [ ] `contact_email` is valid email format if present
- [ ] `current_deadline` is future date or null
- [ ] `red_flags` is array (empty array if none)
- [ ] `enrichment_source` is the actual URL you used
- [ ] All text fields are concise (priorities < 500 chars)

---

## Storing Results

After completing research, store via:

```bash
python scripts/03b_store_enrichment.py --file enrichment_batch.json
```

Or for single foundation:

```bash
python scripts/03b_store_enrichment.py \
  --ein 123456789 \
  --accepts-unsolicited true \
  --application-type loi \
  --contact-name "Jane Smith" \
  --contact-email "jane@foundation.org" \
  --program-priorities "Youth education, STEM" \
  --enrichment-source "https://foundation.org/grants"
```

---

*Skill version 1.0 - Created 2025-01-01*
