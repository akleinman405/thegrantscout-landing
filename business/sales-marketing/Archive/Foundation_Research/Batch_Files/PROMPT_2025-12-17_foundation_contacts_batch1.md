# PROMPT: Foundation Contact Research — Batch 1 of 3

**Date:** 2025-12-17  
**For:** Claude Code CLI  
**Batch:** Foundations 1-34

---

## Standards

**FIRST:** Review `CLAUDE.md` for project conventions before starting.

**Output location:** Save all outputs in the same folder as this prompt.

---

## Situation

Researching program-level contacts at 100 foundations for B2B outreach. This is Batch 1 of 3 — research foundations 1-34 from the list below.

**Goal:** Find the right person to call (VP Programs, Director of Grants, Chief Strategy Officer, etc.) with their LinkedIn and contact info.

---

## Your 34 Foundations

| # | EIN | Foundation |
|---|-----|------------|
| 1 | 453611066 | AARON'S FOUNDATION INC |
| 2 | 920166198 | Alaska Airlines Foundation |
| 3 | 953294377 | ALBERT AND ELAINE BORCHARD |
| 4 | 131623877 | ALFRED P SLOAN FOUNDATION |
| 5 | 943019660 | ALLETTA MORRIS MCBEAN CHARITABLE TRUST |
| 6 | 330340635 | ALLIANCE HEALTHCARE FOUNDATION |
| 7 | 844571035 | ALLY CHARITABLE FOUNDATION |
| 8 | 131623879 | ALTMAN FOUNDATION |
| 9 | 541759773 | AMERICAN WOODMARK FOUNDATION INC |
| 10 | 953367511 | ANN JACKSON FAMILY FOUNDATION |
| 11 | 952114455 | ANN PEPPERS FOUNDATION |
| 12 | 742132676 | Anschutz Family Foundation |
| 13 | 843049720 | ARCONIC CHARITABLE FOUNDATION II |
| 14 | 383332791 | ARCUS FOUNDATION |
| 15 | 134200689 | AVANGRID FOUNDATION INC |
| 16 | 350882856 | BALL BROTHERS FOUNDATION |
| 17 | 141810419 | BANK OF GREENE COUNTY |
| 18 | 386151026 | BARSTOW FOUNDATION |
| 19 | 262667384 | BCM Foundation |
| 20 | 943345967 | BELLA VISTA FOUNDATION |
| 21 | 043365869 | BERKSHIRE BANK FOUNDATION INC |
| 22 | 330046140 | BESS J HODGES FOUNDATION |
| 23 | 383853264 | BISSELL Pet Foundation |
| 24 | 941196182 | BOTHIN FOUNDATION |
| 25 | 262992045 | BRITTINGHAM FAMILY FOUNDATION |
| 26 | 821511283 | CARESTAR FOUNDATION |
| 27 | 746078530 | Carl C Anderson Sr and Marie Jo Anderson |
| 28 | 131628151 | CARNEGIE CORPORATION OF NEW YORK |
| 29 | 381211227 | CHARLES STEWART MOTT FOUNDATION |
| 30 | 562582815 | CITIZENS PHILANTHROPIC FOUNDATION INC |
| 31 | 251086799 | CLAUDE WORTHINGTON BENEDUM FOUNDATION |
| 32 | 061057387 | CONNECTICUT HEALTH FOUNDATION INC |
| 33 | 943100217 | CONRAD N HILTON FOUNDATION |
| 34 | 680208980 | Dean and Margaret Lesher Foundation |

---

## Research Process

For each foundation:

### Step 1: Find Website
- Search "[Foundation Name] foundation" 
- Verify it's the right org (check EIN if possible)

### Step 2: Find Staff/Team Page
- Look for "About > Team" or "About > Staff" or "Our People"
- Screenshot or note the URL

### Step 3: Identify Best Contact
**Target titles (priority order):**
1. VP/Director of Programs
2. Chief Strategy/Impact Officer  
3. Director of Grants Management
4. Program Officer
5. Executive Director (if small foundation with no program staff)

### Step 4: Get Contact Details
- LinkedIn URL (search "[Name] [Foundation]")
- Phone (usually foundation main number from website)
- Email (from website, or infer pattern like firstname@foundation.org)

### Step 5: Document Sources
Note where you found each piece of data.

---

## Output

**File:** `OUTPUT_2025-12-17_foundation_contacts_batch1.csv`

**Columns:**
```
batch,foundation_name,ein,contact_name,contact_title,linkedin_url,phone,phone_source,email,email_source,website,notes
```

**Example row:**
```
1,AARON'S FOUNDATION INC,453611066,Jane Smith,Director of Programs,https://linkedin.com/in/janesmith,555-123-4567,website contact page,jsmith@aaronsfoundation.org,inferred from pattern,https://aaronsfoundation.org,Corporate foundation - Aaron's Inc
```

---

## Quality Standards

- If no program-level contact found, use ED/President but note "No program staff found"
- If website is broken/missing, note "Website not found" and try LinkedIn search
- If foundation appears inactive, flag it
- Phone number = main foundation line is fine (we'll ask for contact by name)
- Spend ~3-5 minutes max per foundation

---

## When Done

Save output in the same folder as this prompt file.

Then notify that Batch 1 is complete.
