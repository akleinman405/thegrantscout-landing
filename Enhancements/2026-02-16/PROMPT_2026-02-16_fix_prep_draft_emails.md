# PROMPT: Fix, Prep, and Draft 20 Nonprofit Emails

**Date:** 2026-02-16
**For:** Claude Code CLI
**Schema:** f990_2025

---

## Situation

A previous prompt ran prematurely — it selected a first cohort and drafted 20 emails (10 foundation, 10 nonprofit) before the database was properly prepped. Several problems:

1. **4 of 10 foundation emails were to orgs we already contacted** (O.L. Halsell, Price Philanthropies, Ann Jackson, Zellerbach). Our call/outreach history in Calls-2.xlsx was never imported.
2. **The email framing was wrong.** The emails used a cold data-analyst pitch ("I analyze foundation giving using public 990 data"). We want a different approach (described below).
3. **We're starting with nonprofits only.** Skip foundations for now.

This prompt: (A) imports all outreach history, (B) does the database prep steps that should have happened first, (C) drafts 20 nonprofit emails with the correct framing.

---

## PART A: Import Outreach History & Fix Collisions

### A1: Import Calls-2.xlsx

File: `Calls-2.xlsx` (in uploads or at `C:\TheGrantScout\4. Sales & Marketing\Calls-2.xlsx`)

This spreadsheet has 7 sheets with all our outreach history. Import into campaign_prospect_status so we never email someone we've already contacted.

**Sheet: "Calls" (main — 135 contacts)**
Columns: Org (B), Priority (C), Date Contacted (D), Phone (E), Contact (F), Title (G), Email (H), State (I), EIN (L), Rating (M), Org Type (R), Outcome (S), Call Notes (T)

Import every row where Org is not null. Map fields:
- `email` → column H (may be null)
- `ein` → column L (may be null — match by org name to fp2/np2 if missing)
- `organization_name` → column B
- `vertical` → 'cold_call'
- `campaign_status` → map from Outcome column:
  - "1. Not Contacted" → 'queued'
  - "2. VM" → 'contacted'
  - "3. Talked to Someone" → 'contacted'
  - "4. Reached Decision Maker" → 'contacted'
  - "5. Interested" → 'replied'
  - NULL → 'queued'
- `initial_sent_at` → Date Contacted column
- `notes` → Call Notes column
- `org_type` → Org Type column

**Sheet: "Sheet2" (17 researched foundations)**
Columns: Org (B), Researched (C), Date_Contacted (D), Rating (E), Why_Rating (F), Pitch_Angle (G), State (H), EIN (I), Contact_Email (P)

These are foundations with deep research. Import any NOT already in campaign_prospect_status from the Calls sheet import.

**Sheet: "Sheet3" (84 foundation contacts)**
Columns: foundation name (B), contact name (E), contact title (F), contact email (G), contact phone (H), contact linkedin (I), ein (J)

These are contact records, not outreach events. Import as supplementary contact data — update fp2.app_contact_email where we have a better email, and add to foundation_enrichment if useful. Do NOT create campaign_prospect_status rows unless the foundation also appears in the Calls sheet.

**Sheet: "Sheet4" (105 other contacts)**
Columns: Org name (C), Phone (E), Contact name (F), Title (G), State (I), EIN (K), Org Type (O), Segment (P)

Import into campaign_prospect_status where not already present.

**Sheet: "Sheet5" (49 priority foundations)**
Columns: Rating (B), Foundation Name (C), State (D), Contact Name (H), Contact Title (I), Email (J), Phone (K), EIN (P)

Import into campaign_prospect_status where not already present. These are high-priority researched foundations.

**After import, report:**
- Total records added to campaign_prospect_status
- Total unique EINs now in suppress list
- Total unique emails now in suppress list
- Any EIN/org matching issues

### A2: Discard the Previous First Cohort

The previous prompt created files and possibly database records for a 20-email cohort. Specifically:
- If any tables/views were created for that cohort, note them but don't drop (we may reuse the structure)
- The drafted emails in EMAILS_2026-02-16_first_cohort_CA.md should be ignored — we're replacing them
- If a `send_cohort.py` script was created, keep it (we'll adapt it later)

---

## PART B: Database Prep (Do These In Order)

### B1: Clean fp2 junk emails

```sql
UPDATE f990_2025.foundation_prospects2 
SET app_contact_email = NULL 
WHERE app_contact_email IS NOT NULL 
  AND app_contact_email NOT ILIKE '%@%';
```
Report count cleaned.

### B2: Extract Contact First Names from np2.all_officers

1. Examine 10-20 examples of the all_officers JSONB structure to understand format
2. Add `contact_first_name` VARCHAR(50) to np2 if not exists
3. UPDATE: For each nonprofit with contact_email, find the top officer (ED, Executive Director, CEO, President, Director — in priority order), extract first name, INITCAP(LOWER()) to fix ALL CAPS
4. Fall back to 'there' if no officer found
5. Only process rows that have contact_email (the ~6,372)
6. Report: how many got a real name vs 'there'?

### B3: Build Cohort Foundation Lists

Create table `f990_2025.cohort_foundation_lists` (if not exists):

```sql
CREATE TABLE IF NOT EXISTS f990_2025.cohort_foundation_lists (
    cohort_id SERIAL PRIMARY KEY,
    state VARCHAR(2) NOT NULL,
    ntee_sector VARCHAR(1) NOT NULL,
    sector_label VARCHAR(100),
    foundation_rank INTEGER,
    foundation_ein VARCHAR(20),
    foundation_name TEXT,
    total_giving_5yr NUMERIC,
    median_grant NUMERIC,
    giving_trend VARCHAR(20),
    accepts_applications BOOLEAN,
    example_recipient_name TEXT,
    example_grant_amount NUMERIC,
    example_grant_purpose TEXT,
    UNIQUE(state, ntee_sector, foundation_rank)
);
```

Populate: For each state+NTEE-first-letter combo that has emailable nonprofits in np2:
- Find foundations that gave to recipients in that state+sector in last 5 years
- Rank by total_giving_5yr DESC
- Top 15 per combo
- Include one real example grant per foundation (recipient name + amount)
- Only include foundations where accepts_applications = true OR openness_score >= 3
- Map NTEE first letter to human-readable label (A=Arts, B=Education, C=Environment, E=Health, I=Crime/Legal, J=Employment, K=Food/Agriculture, L=Housing, M=Public Safety, N=Recreation, O=Youth Development, P=Human Services, Q=International, R=Civil Rights, S=Community Improvement, T=Philanthropy, U=Science, V=Social Science, W=Public Policy, X=Religion, Y=Mutual/Membership, Z=Unknown)

### B4: Identify Viable Cohorts

Create `f990_2025.cohort_viability` (if not exists):

```sql
CREATE TABLE IF NOT EXISTS f990_2025.cohort_viability (
    state VARCHAR(2),
    ntee_sector VARCHAR(1),
    sector_label VARCHAR(100),
    foundation_count INTEGER,
    prospect_count INTEGER,
    avg_foundation_giving NUMERIC,
    viable BOOLEAN,
    PRIMARY KEY(state, ntee_sector)
);
```

Viable = foundation_count >= 10 AND prospect_count >= 1. Also note combos where foundation_count < 200 (we'd say "top 50 funders" instead of "top 200").

### B5: Tag Prospects with Cohort

Add to np2 (if not exists):
- `email_cohort_state` VARCHAR(2)
- `email_cohort_sector` VARCHAR(1)
- `email_cohort_viable` BOOLEAN
- `email_priority_score` INTEGER

Populate for the ~6,372 with emails. Priority score:
- +3 if cohort has 100+ foundations (great list)
- +2 if cohort has 50-99 foundations
- +1 if cohort has 10-49 foundations
- +2 if org revenue $500K-$2M (sweet spot)
- +1 if org revenue $2M-$5M
- +2 if government funding dependency > 50%
- +1 if government funding dependency 20-50%
- +1 if fewer than 5 existing foundation grants

### B6: Build Suppress List

Create view:
```sql
CREATE OR REPLACE VIEW f990_2025.v_suppress_list AS
SELECT DISTINCT email, 
    CASE 
        WHEN bounced THEN 'bounced'
        WHEN campaign_status = 'replied' THEN 'replied'
        WHEN campaign_status = 'unsubscribed' THEN 'unsubscribed'
        WHEN campaign_status IN ('contacted', 'sent') THEN 'already_contacted'
        ELSE 'other'
    END as reason
FROM f990_2025.campaign_prospect_status
WHERE bounced = TRUE 
   OR campaign_status IN ('replied', 'unsubscribed', 'contacted', 'sent');
```

Also suppress by EIN — if we called a foundation, don't email them even if the email address is different:
```sql
CREATE OR REPLACE VIEW f990_2025.v_suppress_list_by_ein AS
SELECT DISTINCT ein, organization_name, campaign_status, vertical
FROM f990_2025.campaign_prospect_status
WHERE ein IS NOT NULL
  AND campaign_status NOT IN ('queued');
```

Cross-reference: how many of our 6,372 np2 emails are suppressed (by email OR by EIN)?

Report final "ready to email" count.

---

## PART C: Draft 20 Nonprofit Emails

### Email Approach (FOLLOW THIS EXACTLY)

**The strategy:** We're offering a free list of the top foundations funding their sector in their state. The motivation is genuine — federal funding is getting cut and we want to help nonprofits find private alternatives. We drop 2-3 real foundation names in the email for credibility, then offer the full list free on reply.

**What the email should sound like:**
- A real person who cares about the problem, not a data analyst pitching a service
- Warm, brief, genuine — like texting a colleague a useful resource
- The "why" comes first: we're unhappy about what's happening with federal funding and trying to help
- The value is in the body: real foundation names with real dollar amounts
- The ask is low-friction: "want a copy?" — that's it, no demo, no call, no signup
- 50-80 words total
- Plain text, no formatting, no links, no images
- Do NOT mention TheGrantScout, 990 data, analyzing anything, or our product/service
- Do NOT say "I analyze" or "I study" or "I track" — these sound robotic and salesy
- Sign off with just "Alec" (no company name, no title — keep it personal)

**Email structure:**
1. **Why** (1 sentence) — Acknowledge the funding environment, say we're trying to help
2. **Value** (2-3 sentences) — Drop 2-3 foundation names with amounts that are specific to their state+sector. Include one detail per foundation (giving trend, median grant size, or that they accept applications)
3. **Offer** (1 sentence) — "We put together the full top [X] list for [sector] funders in [state]. Want a copy?"
4. **Sign-off** — Just "Alec"

**Example (this is the TONE and STRUCTURE to follow):**

> Hi Maria,
> 
> The past year has been tough on nonprofits that depend on federal funding. We've been putting together lists of private foundations by state and sector — trying to get useful info into the hands of people who need it.
> 
> A few California human services funders you might not know: Weingart Foundation gave $150K to transitional housing last year, and Ahmanson Foundation is growing their human services giving significantly.
> 
> We have the full top 200 list for free. Want a copy?
> 
> Alec

**IMPORTANT — what varies per email:**
- First name (from contact_first_name)
- State name
- Sector label (human-readable)
- 2-3 foundation names with one data point each (from cohort_foundation_lists)
- The number in "top X list" should match actual foundation_count for their cohort (if 87 foundations, say "top 87" not "top 200")

**IMPORTANT — what should vary in WORDING (not just merge tags):**
- The opening line about federal funding can be worded differently each time — don't use the exact same sentence 20 times
- The transition to foundation names can vary ("A few you might not know:", "Some that caught my eye:", "Here are a couple worth looking into:", etc.)
- The closing offer can vary ("Want a copy?", "Happy to send it over", "Interested?", "Just reply and I'll send it")
- Use the prospect's mission_description to inform which foundations you pick from the cohort list (pick the 2-3 most relevant to their specific work, not just the biggest)

### Cohort Selection for These 20

Select 20 nonprofits from np2 where:
- contact_email IS NOT NULL and valid
- NOT in v_suppress_list (by email) and NOT in v_suppress_list_by_ein (by EIN)
- email_cohort_viable = TRUE
- Has a real contact_first_name (not 'there')
- Prioritize by email_priority_score DESC
- Spread across at least 3-4 different states (don't send all 20 to California)
- Spread across at least 3-4 different sectors

For each prospect, pull their cohort's foundation list and pick the 2-3 most relevant foundations based on the nonprofit's NTEE code and mission_description.

### How to Draft the Emails

Do NOT use the Anthropic API to generate emails. Draft them yourself directly as a Claude Code agent. 

For each of the 20 prospects:
1. Look at their contact_first_name, org_name, state, sector_label, mission_description
2. Look at their cohort's foundation list (from cohort_foundation_lists) and pick the 2-3 foundations most relevant to this specific nonprofit's work
3. Write the email following the structure and tone described above — vary the wording naturally so no two emails read the same
4. Write a subject line (4-7 words, reference their state or sector, no clickbait)

### Output Files

Save ALL output files to the Enhancements folder (or working directory if that's how the project is structured).

**File 1:** `EMAILS_2026-02-16_nonprofit_cohort_1.md`
- For each email: To, Contact Name, Org Name, State, Sector, Subject Line, Email Body
- At the end: sending notes (recommended send order, subject line A/B test ideas)

**File 2:** `EMAIL_BATCH_2026-02-16_nonprofit_1.csv` with columns:
- email, first_name, org_name, state, sector, subject, body, cohort_state, cohort_sector, priority_score
(This is what the sender script will read)

**File 3:** The report specified in Part D below

---

## PART D: Final Report

Save as `REPORT_2026-02-16_email_prep_and_draft.md` (same location as other output files).

1. **Part A results:** Calls import counts, suppress list totals, any collisions found with previous cohort
2. **Part B results:** 
   - Junk emails cleaned
   - Contact name coverage
   - Cohort foundation lists: how many combos, total rows, top 20 cohorts by prospect count
   - 5 sample foundation lists (show what the email writer worked with)
   - Viable cohorts summary
   - Final "ready to email" count
3. **Part C results:**
   - The 20 selected prospects with their profile data
   - Which foundations were picked for each and why
   - Any data quality issues (thin cohorts, missing names, etc.)
4. **Previous cohort collision check:** List any of the 20 previously drafted emails that overlap with contacts in Calls-2.xlsx
