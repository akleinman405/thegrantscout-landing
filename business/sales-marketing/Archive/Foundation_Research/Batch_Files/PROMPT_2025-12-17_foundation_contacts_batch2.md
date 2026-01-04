# PROMPT: Foundation Contact Research — Batch 2 of 3

**Date:** 2025-12-17  
**For:** Claude Code CLI  
**Batch:** Foundations 35-67

---

## Standards

**FIRST:** Review `CLAUDE.md` for project conventions before starting.

**Output location:** Save all outputs in the same folder as this prompt.

---

## Situation

Researching program-level contacts at 100 foundations for B2B outreach. This is Batch 2 of 3 — research foundations 35-67 from the list below.

**Goal:** Find the right person to call (VP Programs, Director of Grants, Chief Strategy Officer, etc.) with their LinkedIn and contact info.

---

## Your 33 Foundations

| # | EIN | Foundation |
|---|-----|------------|
| 35 | 416034786 | DELUXE CORPORATION FOUNDATION |
| 36 | 943086271 | DERMODY PROPERTIES FOUNDATION |
| 37 | 830590696 | DOGWOOD HEALTH TRUST |
| 38 | 472746460 | DOMINION ENERGY CHARITABLE FOUNDATION |
| 39 | 823691183 | DORIS DUKE CHARITABLE FOUNDATION INC |
| 40 | 366068724 | Dr Scholl Foundation |
| 41 | 912172351 | DRAPER RICHARDS KAPLAN FOUNDATION |
| 42 | 954856207 | DURFEE FOUNDATION |
| 43 | 510155772 | E RHODES AND LEONA B CARPENTER |
| 44 | 952500545 | EARL B & LORAINE H MILLER FOUNDATION |
| 45 | 461702755 | EDWARDS LIFESCIENCES FOUNDATION |
| 46 | 820548352 | ESL CHARITABLE FOUNDATION |
| 47 | 382143122 | ETHEL AND JAMES FLINN FOUNDATION |
| 48 | 436064859 | EWING MARION KAUFFMAN FOUNDATION |
| 49 | 452599017 | FARMINGTON BANK COMMUNITY |
| 50 | 300219424 | FAUQUIER HEALTH FOUNDATION |
| 51 | 046131201 | FIDELITY FOUNDATION |
| 52 | 943301999 | Firedoll Foundation |
| 53 | 421444870 | FRED MAYTAG FAMILY FOUNDATION |
| 54 | 581709417 | GEORGIA POWER FOUNDATION INC |
| 55 | 391577137 | GREEN BAY PACKERS FOUNDATION |
| 56 | 237376427 | Helen V Brach Foundation |
| 57 | 256065959 | HILLMAN FAMILY FOUNDATIONS |
| 58 | 953924667 | HONDA USA FOUNDATION |
| 59 | 746013920 | Houston Endowment Inc |
| 60 | 300527867 | INTREPID PHILANTHROPY FOUNDATION |
| 61 | 770229243 | JAMES S BOWER FOUNDATION |
| 62 | 237093598 | John D and Catherine T MacArthur Foundation |
| 63 | 866052431 | JOHN F LONG FOUNDATION INC |
| 64 | 953759369 | JOHN GOGIAN FAMILY FOUNDATION |
| 65 | 650464177 | JOHN S AND JAMES L KNIGHT FOUNDATION |
| 66 | 621322826 | JOHN TEMPLETON FOUNDATION |
| 67 | 776154307 | June G Outhwaite Charitable Trust |

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

**File:** `OUTPUT_2025-12-17_foundation_contacts_batch2.csv`

**Columns:**
```
batch,foundation_name,ein,contact_name,contact_title,linkedin_url,phone,phone_source,email,email_source,website,notes
```

**Example row:**
```
2,DELUXE CORPORATION FOUNDATION,416034786,John Doe,VP Community Relations,https://linkedin.com/in/johndoe,555-234-5678,website,jdoe@deluxe.com,website staff page,https://deluxe.com/foundation,Corporate foundation
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

Then notify that Batch 2 is complete.
