# PROMPT: Foundation Contact Research — Batch 3 of 3

**Date:** 2025-12-17  
**For:** Claude Code CLI  
**Batch:** Foundations 68-100

---

## Standards

**FIRST:** Review `CLAUDE.md` for project conventions before starting.

**Output location:** Save all outputs in the same folder as this prompt.

---

## Situation

Researching program-level contacts at 100 foundations for B2B outreach. This is Batch 3 of 3 — research foundations 68-100 from the list below.

**Goal:** Find the right person to call (VP Programs, Director of Grants, Chief Strategy Officer, etc.) with their LinkedIn and contact info.

---

## Your 33 Foundations

| # | EIN | Foundation |
|---|-----|------------|
| 68 | 770559337 | JW & HM GOODMAN FAMILY CHARITABLE |
| 69 | 591885997 | KOCH FOUNDATION |
| 70 | 941624987 | KORET FOUNDATION |
| 71 | 680237238 | LEO M SHORTINO FAMILY FOUNDATION |
| 72 | 061479957 | LIBERTY BANK FOUNDATION INC |
| 73 | 141893520 | LIBERTY MUTUAL FOUNDATION INC |
| 74 | 350868122 | LILLY ENDOWMENT INC |
| 75 | 366108775 | LLOYD A FRY FOUNDATION |
| 76 | 351813228 | Lumina Foundation for Education Inc |
| 77 | 237456468 | M J MURDOCK CHARITABLE TRUST |
| 78 | 043722125 | Majestic Realty Foundation |
| 79 | 756015322 | Meadows Foundation Inc |
| 80 | 930806316 | MEYER MEMORIAL TRUST |
| 81 | 364336415 | Michael & Susan Dell Foundation |
| 82 | 363556764 | MIDCONTINENT FOUNDATION |
| 83 | 521700855 | MITSUBISHI ELECTRIC AMERICA FOUNDATION |
| 84 | 466854005 | MONTANA HEALTHCARE FOUNDATION |
| 85 | 830590263 | MOTHER CABRINI HEALTH FOUNDATION INC |
| 86 | 942601172 | Nancy Buck Ransom Foundation |
| 87 | 135626345 | NEW YORK FOUNDATION |
| 88 | 300127892 | NEW YORK STATE HEALTH FDN |
| 89 | 562453619 | NEWALLIANCE FOUNDATION INC |
| 90 | 356644088 | Nina Mason Pulliam Charitable Trust |
| 91 | 386083080 | OLESON FOUNDATION |
| 92 | 137029285 | OPEN SOCIETY INSTITUTE |
| 93 | 436203035 | OPPENSTEIN BROTHERS FOUNDATION |
| 94 | 416019050 | OTTO BREMER TRUST |
| 95 | 822797338 | PD Jackson Family Foundation |
| 96 | 951661675 | PFAFFINGER FOUNDATION |
| 97 | 870643877 | Philanthropy International |
| 98 | 900653262 | PHYLLIS C WATTIS FOUNDATION |
| 99 | 223125880 | PSEG FOUNDATION INC |
| 100 | 540597601 | Public Welfare Foundation Inc |

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

**File:** `OUTPUT_2025-12-17_foundation_contacts_batch3.csv`

**Columns:**
```
batch,foundation_name,ein,contact_name,contact_title,linkedin_url,phone,phone_source,email,email_source,website,notes
```

**Example row:**
```
3,KORET FOUNDATION,941624987,Sarah Johnson,Program Director,https://linkedin.com/in/sarahjohnson,415-882-7740,website,sjohnson@koretfoundation.org,inferred,https://koretfoundation.org,SF Bay Area focus
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

Then notify that Batch 3 is complete.
