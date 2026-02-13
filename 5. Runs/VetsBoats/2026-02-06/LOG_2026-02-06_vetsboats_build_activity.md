# VetsBoats Report Build — Full Activity Log (Real-Time)

**Date:** 2026-02-06
**Client:** Wooden Boats for Veterans (dba VetsBoats), EIN 46-4194065
**Purpose:** Play-by-play record of every action, thought, query, search, and decision during the full report build. Written as if you're watching over my shoulder in real time.

---

## SESSION START — ~[T+0:00]

Alec provides a detailed implementation plan with 6 checkpoints. VetsBoats is the first paying customer. The plan references prior research from Jan 16 (siblings, foundation analysis) and critical files (sales call, pre-call brief, report template).

**My first thought:** This is a complex build with a lot of moving parts. The plan calls for manual execution of the pipeline since VetsBoats lacks embeddings and a dim_clients entry. I need to start by reading all the source files to get context, then verify identity in the database and online.

**Strategy:** Read all 6 critical files in parallel (saves time vs sequential), then fire off DB queries and a web verification agent simultaneously.

---

## CHECKPOINT 1: Client Profile & Identity Verification

### Step 1: Read All Source Files [parallel, T+0:01]

I fire off 6 Read tool calls simultaneously:

**File 1: Sales call transcript** (`Call with Terry 2025-12-4.md`)
- It's a raw voice transcription (not cleaned up). Terry is the founder, Navy veteran.
- Key intel extracted:
  - Started 12 years ago sailing veterans on his own boat in SF Bay
  - "I could see people relaxing... feeling more at peace being more mindful"
  - Became 501c3, built network with VA departments in Bay Area
  - **Going national:** Chapters in Cape Cod, Ohio, looking at San Diego next
  - Looking for at-risk veterans specifically, targeting suicide prevention
  - **$500K fundraising goal** next year to hire staff
  - Currently raising $150-250K/year, Terry is the grant writer himself
  - "Just brought in a new director of development" — Matt, focusing on corporate sponsorships
  - Terry calls Matt "Matt Gettleman" [sic — will need to verify spelling]
  - Alec pitched the $99/mo monthly report subscription
  - Terry was receptive: "That could be something we'd be very interested in"
  - Terry mentioned "mindfulness based sailing therapy" — a specific study

  **My thinking:** This is a classic small-but-ambitious nonprofit. All-volunteer, founder doing everything, wants to 5x fundraising. The "director of development" title is interesting — need to verify if Matt is actual staff or advisory. The $500K goal is aggressive for an org at $137K revenue.

**File 2: Pre-call brief** (`VetsBoats_Foundation_Pre-Call_Brief_2025-12-04.md`)
- Very thorough research document. 355 lines.
- **EIN confirmed:** 46-4194065
- **Files 990-PF as private operating foundation** — this is unusual and important
- Financial data through FY2024: Revenue $136,943, Expenses $186,050, Net Assets $279,349
- **$300K debt** from LENDonate refinancing (4% interest, 12-month term)
- **Past grants listed:** SVCF $30K, American Online Giving $24K, Sidney Stern $3.5K, Goodfellow $60K, JPMorgan $8.5K, BMS $2.5K

  **My thinking:** Wait — Goodfellow $60K seems big for a $137K org. And JPMorgan $8.5K? These numbers need to be cross-referenced against our DB. I'm suspicious some of these might be misattributed.

- **Database prospect tiers listed:** Schmidt Family Foundation, Alletta Morris McBean, Saw Island, Koret Foundation, Arthur Blank, Cohen Veterans Network — these were identified in Dec 2025 before I had siblings
- **Capacity concerns:** No dedicated development staff, no grant management infrastructure

**File 3: Sibling analysis** (`REPORT_2026-01-16.1_vetsboats-sibling-analysis.md`)
- 28 siblings found using keyword search (not embeddings — VetsBoats not in nonprofit_returns)
- Budget range: $20K-$700K (0.15x-5x of $137K revenue)
- Tier 1 (19 orgs): Veteran sailing/therapy (4), Veteran water recreation (13), Wooden boat programs (2)
- Tier 2 (9 orgs): Veteran outdoor therapy
- Notable siblings: Judd Goldman Adaptive Sailing ($678K), Veteran Sailing Inc ($183K), Wooden Boat Foundation ($557K)

  **My thinking:** Good sibling set. The sailing-specific ones (Judd Goldman, Veteran Sailing Inc, Tantillo, Sailing Heals) are the highest-quality siblings. The water recreation ones (fishing, rowing, kayak) are decent but more distant. I'll use these as-is and maybe add a few if I find gaps.

**File 4: Foundation analysis** (`REPORT_2026-01-16.2_vetsboats-foundation-analysis.md`)
- 67 foundations funding the 28 siblings
- 6 grants to VetsBoats directly found: Tahoe Maritime $25K, Henry Mayo Newhall $15K, Charis $5K, Bonnell Cove $5K+$2.5K, Sidney Stern $3.5K
- Foundation types: 63% private, 21% family, 7% charitable, 6% corporate
- Most are $1M-$50M assets
- Only 2 CA foundations in the sibling funder set — **big opportunity gap**

  **My thinking:** The 67 sibling funders are a good starting population. But I need to verify the "past funders" list carefully. The Charis and Bonnell Cove claims will need DB verification.

**File 5: clients.json**
- VetsBoats is listed: `{"name": "Wooden Boats For Veterans", "short_name": "VetsBoats", "ein": "464194065", "active": true, "notes": "Not in questionnaire - manual add for report"}`
- Good — already in config, just not in dim_clients table.

**File 6: Report template** (`TEMPLATE_2026-02-02_monthly_grant_report.md`)
- 371 lines. Structured report with: "If You Only Have 5 Hours", Priority table, Foundation Types Explained, Top 5 at a Glance, 5 Foundation Profiles (each with: Why This Foundation, Fit Evidence, Funder Snapshot, How to Apply, Contacts, Positioning Strategy, Action Steps), Monthly Action Plan, Quick Reference.
- Each profile needs: LOI process details, contacts table, potential connections, positioning strategy, step-by-step action items
- Template includes timeline explanation section at end

  **My thinking:** This template is comprehensive. The "Funder Snapshot" requires 6 computed metrics per foundation. The "Contacts" section requires actual names/emails/phones from web research. The "How to Apply" section requires website verification. This is where the bulk of Checkpoint 4 work will be.

---

### Step 2: Database Checks [parallel, T+0:03]

I fire off 6 SQL queries simultaneously. Some hit errors (the MCP postgres tool has a quirk where SQL comments with `--` cause parsing failures, and when one query in a batch fails, sibling queries abort too). I recover and re-run.

**Query 1: `SELECT * FROM f990_2025.dim_clients WHERE ein = '464194065'`**
- **Result:** 0 rows. VetsBoats is NOT in dim_clients.
- **But I got something useful:** The empty result showed me all 39 column names and types in the schema. This is critical for building the INSERT later.
- Columns include: name, ein, state, city, sector_ntee, sector_broad, org_type, budget_tier, budget_min, budget_max, grant_size_seeking, grant_size_min, grant_size_max, grant_capacity, mission_text, project_need_text, project_type, project_keywords, populations_served, geographic_scope, known_funders, recipient_ein, email, status, matching_grant_keywords, excluded_keywords, budget_target_min, budget_target_max, database_revenue, database_assets, budget_variance_flag, client_data_quality, quality_flags, timeframe, questionnaire_date, questionnaire_version, target_grant_purpose

**Query 2: `SELECT ... FROM f990_2025.nonprofit_returns WHERE ein = '464194065'`**
- **Result:** 0 rows. Confirmed — VetsBoats is NOT in nonprofit_returns.
- **Why this matters:** The pipeline normally relies on nonprofit_returns for mission text and revenue. We'll have to populate these fields manually from external sources.
- **Why they're not here:** They file 990-PF (private foundation form), not 990 or 990-EZ. And they may also file 990-N (e-postcard) for some years. Our nonprofit_returns table only has 990/990-EZ data.

**Query 3: `SELECT ... FROM f990_2025.pf_returns WHERE ein = '464194065'`**
- First attempt failed: I used `total_revenue` instead of `total_revenue_amt`. Checked the column list via psql, found the correct name.
- **Result:** 5 rows! Years 2018-2023 (missing 2021 and 2024).

  **Interpreting the results:**
  - `only_contri_to_preselected_ind = TRUE` for ALL years — this threw me for a second. In our normal pipeline, this flag means "only gives to preselected grantees" and we use it to filter OUT foundations that won't accept cold applications. But here, VetsBoats IS a private foundation, and this flag means THEY only contribute to preselected entities — which is irrelevant because they don't make grants at all (`grants_to_organizations_ind = FALSE`).
  - `private_operating_foundation_ind` is TRUE only for 2018, FALSE after. This suggests they changed their classification.
  - Revenue trend: $7.7K → $66.7K → $52.6K → $389K → $278.7K. That 2022 spike to $389K then decline to $278K (and external data shows $137K for FY2024) tells a story of a growth push that they couldn't sustain.
  - Assets: $69K → $113K → $125K → $94K → $352K. The jump from $94K (2022) to $352K (2023) while revenue was declining is interesting — maybe they received Clover or other boat assets.

**Query 4: Grants TO VetsBoats** (`fact_grants WHERE recipient_ein = '464194065'`)
- **Result:** 3 grants, all from tax year 2023:
  1. Tahoe Maritime Foundation — $25,000 — "GENERAL PURPOSE CONTRIBUTION"
  2. Henry Mayo Newhall Foundation — $15,000 — "TO PROVIDE VETERANS WITH SAILING OUTINGS AND LESSONS AS A WAY TO PROVIDE EMOTIONAL SUPPORT AND HEALING"
  3. Sidney Stern Memorial Trust — $3,500 — "GENERAL OPERATING"

  **My thinking:** Only $43.5K total in our DB. The pre-call brief listed $126K+ in historical grants. Big discrepancy. Need to figure out what's real vs. misattributed.

  The Henry Mayo Newhall purpose text is gold — "veterans with sailing outings and lessons as a way to provide emotional support and healing" — this is EXACTLY the kind of language I need for the target_grant_purpose.

**Query 5: dim_recipients check**
- **Result:** Found! `WOODEN BOATS FOR VETERANS`, CA, SAUSALITO, NTEE W99, first_funded_year 2023, last_funded_year 2023. Also has name variants: `["WOODEN BOATS FOR VETERANS", "WOODEN BOATS FOR VETERANS FOUNDATION"]`.
- Good — they're in the recipients table, which means fact_grants has picked them up.

**Query 6: Broader name search** (searching `dr.name ILIKE '%wooden boats%'`)
- **Result:** 43 rows — but scanning through, the vast majority are for "CENTER FOR WOODEN BOATS" (EIN not 464194065, located in Washington state). Only 3 match VetsBoats (the same 3 from Query 4).

  **This is the smoking gun for the pre-call brief errors.** The pre-call brief listed Goodfellow Fund ($60K), JPMorgan Chase ($8.5K), Bristol-Myers Squibb ($2.5K) as VetsBoats funders. But in the DB, these grants went to "CENTER FOR WOODEN BOATS" — a completely different organization in Washington state! The name similarity ("Wooden Boats for Veterans" vs "Center for Wooden Boats") apparently confused whoever prepared the pre-call research.

  I can see specifically:
  - Goodfellow Fund → Center for Wooden Boats: $28.5K (2019), $30K (2020), $30K (2021), $10K (2023) = $98.5K total
  - JPMorgan Chase → Center for Wooden Boats: $1.05K (2018), $2.5K (2020), $5K (2021), $500 (2022), $3.9K (2023)
  - Bristol-Myers Squibb → Center for Wooden Boats: $2.52K (2020)

---

### Step 3: Verify Questionable Funders [T+0:08]

**Query 7: Goodfellow Fund grants to VetsBoats EIN specifically**
```sql
SELECT ... WHERE fg.foundation_ein = '912000453' AND fg.recipient_ein = '464194065'
```
- **Result:** 0 rows. Confirmed — Goodfellow has never funded VetsBoats. Pre-call brief was wrong.

**Query 8: Charis Fund grants to VetsBoats EIN**
```sql
SELECT ... WHERE fg.foundation_ein = '946077619' AND fg.recipient_ein = '464194065'
```
- **Result:** 0 rows.
- Also searched Charis Fund grants to any veteran/wooden org: Found grants to "VETERAN RITES INC" ($5K 2022, $3K 2021) — not VetsBoats.

  **My thinking:** The pre-call brief may have sourced the Charis Fund grant from GuideStar or Candid, which sometimes has different data than what's in 990-PF filings. Or it could be from a year not in our DB. I'll flag it as "unconfirmed" — it's possible they did get a grant, just not visible to us.

**Query 9: Bonnell Cove Foundation — all grants**
```sql
SELECT ... WHERE fg.foundation_ein = '133556721' ORDER BY tax_year DESC LIMIT 30
```
- **Result:** 30 rows showing maritime/environmental focus — "SAFETY AT SEA", "ENVIRONMENTAL". Recipients include Call of the Sea, Center for Coastal Studies, Rocking the Boat, Billion Oyster Project, Maine Island Trail, etc.
- No VetsBoats in the list. Bonnell Cove is clearly a maritime environmental funder, not a veteran services funder. But "Safety at Sea" IS relevant to VetsBoats' programs.

  **My thinking:** Bonnell Cove is actually a great prospect for VetsBoats' wooden boat restoration and sailing safety programs, even though we can't confirm past funding. I'll keep them in mind for the foundation scoring phase.

---

### Step 4: Online Verification [launched in parallel with DB queries, T+0:03]

I launched a general-purpose subagent to verify VetsBoats' identity online. The agent searched:
- "Wooden Boats for Veterans EIN 46-4194065"
- ProPublica Nonprofit Explorer
- GuideStar/Candid
- Charity Navigator
- Cause IQ
- vetsboats.org
- Archdiocese of San Francisco article about VetsBoats
- LinkedIn for Matt Goettelman
- VetsBoats team page
- The Org (org chart site)
- findCRA

**Agent returned a comprehensive 7-section report. Key findings I'm processing:**

1. **Address is different from what I expected.** Pre-call brief said "100 South St" but ProPublica/Charity Navigator show "1001 Bridgeway Street, Suite 608". The Bridgeway address appears more current.

2. **NTEE code conflict:** ProPublica says W99, Cause IQ says T20. The W99 is the IRS-assigned code meaning "Public, Society Benefit - Multipurpose N.E.C." which is a catch-all. T20 just reflects private foundation filing. Neither is great for matching — ideally they'd be coded under P (Human Services) or something veteran-specific.

3. **Matt Goettelman correction — THIS IS IMPORTANT.**
   - Terry on the call said "we just brought in a new director of development" named Matt
   - Online verification shows: Matt Goettelman's actual title is **Advisory Board Member**
   - He's a former West Point cadet, Goldman Sachs guy, advises family offices and foundations
   - He's NOT paid staff and NOT a "Director of Development"
   - Correct spelling: **Goettelman** (not "Gettleman" as Terry said on the call)
   - This matters because the plan assumed Matt would be executing the report's action plans. If he's just advisory board, he may not be the one doing the work.

4. **Programs are more extensive than I thought:**
   - Wheelchair Regatta Support (partnership with Pacific Yacht Club Association)
   - Veteran Benefits Navigation (connecting to VA resources)
   - Monthly training camps in Sausalito, Emeryville, San Francisco, Richmond, Coyote Point
   - Advisory board includes a VA psychologist, 2 recreational therapists, 4 social workers — this is actually a more clinical/structured program than I expected

5. **Expansion plans updated:** Website now says San Diego CA, Galveston TX, Springfield OH, Annapolis MD. The sales call from Dec 2025 said Cape Cod and Ohio. Galveston and Annapolis are new targets.

6. **Impact numbers clarified:** Website says 2,500+ veterans and families since founding (up from the "600+" in the pre-call brief). The 200+ number is for a single season (2023).

7. **The 990-PF filing is a RED FLAG for grant seeking.** The agent flagged that VetsBoats' `only_contri_to_preselected_ind = TRUE` flag will show up in our pipeline's filtering. But this flag is on THEIR filing (as a private foundation), not a funder's filing. We need to be careful not to confuse VetsBoats-the-private-foundation with VetsBoats-the-grant-seeker.

8. **Cash position is dire:** Only $9,349 in cash/investments on the most recent filing, despite $279K in total assets. Most of those assets must be boats (Clover alone is probably worth a significant amount). They are asset-rich, cash-poor.

---

### Step 5: Keyword Hit Testing [T+0:05]

**Rationale:** I need to define `matching_grant_keywords` — these are terms I'll search for in `fact_grants.purpose_text` to flag "target grants" (grants that look like something VetsBoats would receive). If a foundation has made target grants to siblings, that's a strong signal they'd fund VetsBoats.

**First batch — 12 keywords tested:**

| Hits | Keyword | My Assessment |
|------|---------|---------------|
| 348 | PTSD | Good — specific enough. Core to VetsBoats' mission. |
| 103 | sailing program | Good — captures sailing-focused grants |
| 97 | veteran mental health | Good — relevant and not too broad |
| 56 | veteran wellness | Good — aligned with therapeutic mission |
| 44 | maritime heritage | Decent — captures wooden boat/preservation angle |
| 35 | veteran outdoor | Good — captures outdoor recreation therapy |
| 27 | sailing education | Good — captures sail training programs |
| 26 | adaptive sailing | Good — closely related org type |
| 5 | therapeutic sailing | Very specific — but only 5 hits. That's okay — when it matches, it's a STRONG signal. |
| 4 | boat restoration | Very specific — same logic as above |
| 3 | sailing therapy | Very specific — 3 hits is fine |
| 2 | veteran sailing | Extremely specific — only 2 grants in the entire DB mention this exact phrase. Perfect precision, low recall. |

**My thinking:** The highly specific keywords (2-5 hits) are actually the most valuable for identifying truly aligned foundations. If a foundation has given a grant for "therapeutic sailing" or "veteran sailing", that's a near-perfect match for VetsBoats. The broader keywords (97-348 hits) help cast a wider net but will produce more false positives.

**Second batch — 12 more keywords tested:**

| Hits | Keyword | My Assessment |
|------|---------|---------------|
| 1,105 | veteran program | Too broad — literally every veteran-serving grant. Would match VA hospitals, job training, housing... |
| 1,041 | veteran service | Same problem — too broad |
| 1,018 | veteran support | Same |
| 849 | military veteran | Same — just means "mentions veterans" |
| 305 | veteran healing | Interesting — "healing" is more specific than "program/service/support" |
| 297 | mindfulness | Surprisingly many hits. But includes yoga studios, meditation centers — lots of false positives for VetsBoats |
| 133 | veteran trauma | Clinical — includes PTSD treatment centers, medical research. More distant from VetsBoats. |
| 66 | veteran suicide | Too clinical — VetsBoats doesn't position as suicide prevention (even though that's an underlying motivation) |
| 41 | boat building | Good — captures boat restoration/construction programs |
| 39 | sailing instruction | Good — captures sail training |
| 18 | veteran recreation | Good — recreation-based therapy |
| 11 | wooden boat | Very relevant — low hits but high precision |

**Decision on keyword set:**

I'm going with 10 keywords that balance specificity and coverage:
1. `veteran sailing` (2 hits) — ultra-specific, high signal
2. `therapeutic sailing` (5 hits) — very specific, high signal
3. `adaptive sailing` (26 hits) — closely related, good signal
4. `sailing program` (103 hits) — moderate breadth
5. `veteran wellness` (56 hits) — moderate breadth, relevant
6. `veteran outdoor` (35 hits) — captures outdoor therapy
7. `boat restoration` (4 hits) — specific to their programs
8. `wooden boat` (11 hits) — specific to their identity
9. `maritime heritage` (44 hits) — captures preservation angle
10. `PTSD veteran` (need to test this exact combo, but "PTSD" alone has 348 hits)

I'm excluding the 1,000+ hit keywords because at that volume, the signal-to-noise ratio is too low. A foundation that gave a grant for "veteran program" could be funding job training, housing, medical care — anything. I want foundations that fund *sailing/outdoor/therapeutic* programs for veterans specifically.

---

### Step 6: Reference Existing Clients [T+0:12]

**Query:** Check how SNS and Ka Ulukoa are configured in dim_clients to model the INSERT.
```sql
SELECT name, ein, state, city, sector_ntee, ..., matching_grant_keywords[1:5], target_grant_purpose
FROM f990_2025.dim_clients WHERE ein IN ('942259716', '260542078')
```
- SNS (Senior Network Services): Keywords like "senior services", "aging services", "elderly care", "senior center", "case management". Target purpose: "Information, guidance and case management services for seniors and people with disabilities to maintain independence"
- Ka Ulukoa: Keywords like "youth athletics", "youth sports", "athletic training". Target purpose: "Youth athletic training and competition programs developing student athletes..."

**My thinking:** Good reference points. My keywords and target purpose should follow this pattern — specific enough to distinguish VetsBoats from generic veteran programs, but broad enough to capture relevant foundations.

---

### Step 7: Check Existing Pipeline Tables [T+0:13]

Checked schemas for `calc_client_siblings`, `calc_client_sibling_grants`, `calc_client_foundation_scores` — got all column definitions.

Also checked which clients already have siblings loaded:
```sql
SELECT DISTINCT client_ein FROM f990_2025.calc_client_siblings
```
Result: 7 clients loaded (061468129, 202707577, 203472700, 260542078, 462730379, 942259716, 952249495). VetsBoats (464194065) is NOT yet loaded.

---

### Step 8: Compile Checkpoint 1 Deliverable [T+0:15]

Wrote comprehensive `CHECKPOINT_1_client_profile.md` with:
- Verified identity (all fields with sources)
- Financial profile (DB + external)
- Mission & programs
- Key people (with Matt Goettelman correction)
- Known past funders (with careful DB verification — caught 3 major errors in pre-call brief)
- Data quality flags (8 issues documented)
- Proposed keywords (10, with hit counts and rationale)
- Proposed target_grant_purpose (modeled on Henry Mayo Newhall's actual grant language)
- Full proposed dim_clients INSERT (all 39 fields)
- Discrepancies table (7 issues caught and resolved)
- 5 questions for Alec's review

Created run folder: `5. Runs/VetsBoats/2026-02-06/`

**Presented Checkpoint 1 to Alec. Awaiting review.**

---

---

## CHECKPOINT 1 FOLLOW-UP: Alec's 5 Research Questions

### Context
Alec reviewed Checkpoint 1 and asked 5 deep research questions instead of quick answers. He also:
- Asked me to save the plan as an MD file (done: `PLAN_2026-02-06_vetsboats_report_build.md`)
- Pointed out I should check VetsBoats' past names (smart idea — could explain funder confusion)
- Asked for the log to be much more detailed (this rewrite)
- Wanted all search terms and websites logged

### Step 9: VetsBoats Name History Check [T+0:20]

Alec's hunch: maybe VetsBoats had a prior name that would explain why the pre-call brief confused them with Center for Wooden Boats.

**Query: dim_recipients name_variants**
```sql
SELECT name, name_variants FROM f990_2025.dim_recipients WHERE ein = '464194065';
```
**Result:** Only two variants: "WOODEN BOATS FOR VETERANS" and "WOODEN BOATS FOR VETERANS FOUNDATION"

**Query: pf_returns business_name across years**
```sql
SELECT DISTINCT business_name, tax_year FROM f990_2025.pf_returns WHERE ein = '464194065' ORDER BY tax_year;
```
**Result:** Always "WOODEN BOATS FOR VETERANS" across all years (2018-2023). No name change.

**Query: All "wooden boat" recipients in the DB**
```sql
SELECT ein, name, name_variants FROM f990_2025.dim_recipients WHERE name ILIKE '%wooden%boat%' OR name ILIKE '%vetsboat%' OR name ILIKE '%vet%boat%'
```
**Result:** 18 orgs with "wooden boat" in the name. Key finding: **SPAULDING WOODEN BOAT CENTER** (EIN 753079357) is also in Sausalito — same city as VetsBoats. Could be a partner org worth noting. But no name that would explain the Center for Wooden Boats confusion.

**Conclusion:** The pre-call brief errors were NOT from a name change. They were simply from confusing "Wooden Boats for Veterans" (CA, EIN 464194065) with "CENTER FOR WOODEN BOATS" (WA, EIN 911061721) — two different orgs with similar names.

---

### Step 10: Q1 — Keyword Breadth Analysis [T+0:25]

**Alec's question:** Should we add broader "veteran program" keywords? Are the foundations that give to generic "veteran programs" also likely to fund sailing/outdoor/therapeutic programs, or are they typically narrower?

**Query: Overlap analysis**
```sql
WITH broad_veteran_foundations AS (
    SELECT DISTINCT foundation_ein FROM fact_grants WHERE purpose_text ILIKE '%veteran%program%' AND tax_year >= 2020
),
narrow_veteran_foundations AS (
    SELECT DISTINCT foundation_ein FROM fact_grants WHERE (purpose_text ILIKE '%veteran%sail%' OR '%veteran%outdoor%' OR '%veteran%wellness%' OR '%adaptive%sail%' OR '%therapeutic%sail%' etc.) AND tax_year >= 2020
)
SELECT COUNT broad, COUNT narrow, COUNT overlap
```

**Result:**
| Category | Count |
|----------|-------|
| Broad "veteran program" foundations | 350 |
| Narrow sailing/outdoor/therapeutic foundations | 290 |
| **Overlap (in both)** | **74** |

**My interpretation:** Only 74 out of 350 broad veteran foundations (21%) ALSO give narrow sailing/outdoor/therapeutic grants. That means **79% of "veteran program" foundations have NEVER funded anything related to sailing, outdoor therapy, or therapeutic recreation.** If we add the broad keyword, we'll pull in ~276 foundations that only fund generic veteran stuff (employment, housing, scholarships) — LOTS of noise.

But wait — 74 overlapping is actually a decent number. Let me see what those 74 look like vs. the 276 broad-only ones.

**Query: What do broad-ONLY foundations fund?**
```sql
-- Foundations that fund "veteran programs" but NOT sailing/outdoor/therapeutic
SELECT name, state, vet_grants, total_vet_giving, sample_purposes
FROM broad_only foundations JOIN fact_grants...
```

**Result (top 15 by total giving):**

| Foundation | State | Vet Grants | Total $ | What They Actually Fund |
|------------|-------|------------|---------|------------------------|
| Clark Charitable Foundation | MD | 20 | $25.2M | Transition programs, women veterans, housing |
| Bob & Renee Parsons Foundation | AZ | 4 | $10.5M | Veterans institute, retreats, general ops |
| Koret Foundation | CA | 37 | $3.8M | Bay Area veterans, career pipeline, scholarships, employment |
| Marna M Kuehne Foundation | WY | 44 | $2.4M | Fishing, gardening, legal aid, service officers |
| Prudential Foundation | NJ | 15 | $2.1M | Employment, tech training, equalpreneurship |
| Lilly Endowment | IN | 5 | $2.1M | Vietnam veterans book, job ready programs |
| Diana Davis Spencer Foundation | MD | 6 | $1.8M | Veterans conference, education, families |
| Shipley Foundation | MA | 8 | $1.5M | Legal services, housing, career transition |
| Harnish Foundation | WA | 13 | $1.4M | Home construction, fly fishing, wellness |
| Bobbie & Stanton Cook | IL | 6 | $1.2M | Medical school, assistance dogs, programming |

**My thinking:** Most of these are funding **employment, housing, education, legal services** for veterans — very different from VetsBoats' therapeutic sailing/outdoor recreation model. The exceptions are:
- **Marna M Kuehne Foundation** — "Veteran Fishing Program" is actually close to VetsBoats' model!
- **Harnish Foundation** — "veteran fly fishing trips" and "wellness services" — very relevant
- **Koret Foundation** — Already identified as a prospect, but their veteran grants are employment/scholarship-focused, not recreation

**VERDICT on Q1:** Adding "veteran program" would add ~276 mostly-irrelevant foundations. Not worth it. BUT I should check if specific terms like "veteran fishing" or "veteran fly fishing" would capture some of the closer-match foundations that the broad keyword catches.

---

### Step 11: Q2 — Real Grant Purpose Texts [T+0:30]

**Alec's question:** Can you find actual grant purpose texts in the DB that could work as our target_grant_purpose?

**Query: All grants with sailing + veteran/therapeutic/adaptive/heal/PTSD/therapy in purpose_text**
```sql
WHERE (purpose_text ILIKE '%sail%' AND purpose_text ILIKE '%veteran%')
   OR purpose_text ILIKE '%therapeutic%sail%'
   OR purpose_text ILIKE '%adaptive%sail%'
   OR (purpose_text ILIKE '%sail%' AND purpose_text ILIKE '%heal%')
   -- etc.
```

**Result: 54 grants found!** These are the actual grants in the IRS database that describe something similar to what VetsBoats does. The most relevant ones:

**PERFECT MATCHES (this IS what VetsBoats does):**
1. `"TO PROVIDE VETERANS WITH SAILING OUTINGS AND LESSONS AS A WAY TO PROVIDE EMOTIONAL SUPPORT AND HEALING"` — $15K, 2023, Henry Mayo Newhall Foundation → **WOODEN BOATS FOR VETERANS** (this is their own grant!)
2. `"PROVIDE COMBAT VETERANS TO RECONNECT, RELAX AND REDUCE STRESS WHILE SAILING"` — $5K, 2023, Ruth & Hal Launders Charitable → Raider Sailing Foundation
3. `"sailing therapy for veterans"` — $5K, 2023, Bozena & Josef Zelenda Foundation → Veterans On Deck
4. `"Sailing Rehab for Wounded Veterans"` — $5K, 2022, Zelenda Foundation → Veterans On Deck
5. `"FUNDS WILL ENABLE VETERANS TO EARN THEIR ASA 101 KEELBOAT & 103 COASTAL CRUISING CERTIFICATIONS"` — $10K, 2023 + 2022, Rock Harbor Foundation
6. `"SAILING CLINIC FOR VETERANS AND THE DISABLED"` — $4.2K, 2020, Phillips Charitable Foundation
7. `"PROVIDING TUITION FREE SAILING ADVENTURES TO YOUTH AND VETERANS"` — $3K, 2022, Corporate Creations Foundation

**STRONG ADJACENT MATCHES (therapeutic sailing, not veteran-specific):**
8. `"OVERCOMING ADVERSITY THROUGH THERAPEUTIC SAILING"` — $25-50K, 2019-2022, John & Daria Barry Foundation → Sail to Prevail
9. `"ADAPTIVE SAILING PROGRAM"` — $3-30K, multiple years, Van Beuren/JE Butler/Johnston/John & Denise Graves → Sail to Prevail, Hudson River Community Sailing, Team Paradise Sailing
10. `"SUPPORT THERAPEUTIC BENEFITS OF SAIL"` — $500, David R Lewis Family → Chesapeake Region Accessible Boating
11. `"TOWARDS SUPPORT OF SAILING ANGELS HYDROTHERAPY"` — $10-12K, Albert & Ethel Herzstein → Sailing Angels Foundation

**BROADER BUT RELEVANT:**
12. `"TO SUPPORT ORGANIZATION'S MISSION TO PROVIDE BOATING OPPORTUNITIES AND MARINE RELATED EDUCATION FOR PEOPLE WITH DISABILITIES, VETERANS, AND YOUTH AT RISK"` — $500, 2018, Sparks Foundation → Freedom Waters Foundation

**My thinking on target_grant_purpose:**

Option A (narrow, mirrors the actual VetsBoats grant):
> "To provide veterans with sailing outings and lessons as a way to provide emotional support and healing through mindfulness-based therapeutic sailing"

Option B (broader, captures more adjacent grants):
> "Therapeutic sailing programs for military veterans suffering from PTSD and traumatic injuries, including adaptive sailing, sail training, and wooden boat restoration to support veteran well-being and healing"

Option C (even broader, captures outdoor recreation therapy):
> "Outdoor recreation therapy programs for military veterans, including therapeutic sailing, boat restoration, and mindfulness-based wellness programs supporting veterans with PTSD"

**My recommendation:** Use Option B as the primary, but ALSO test Option A and C as alternatives during semantic scoring. This way we get three bites at the apple — narrow (catches exact matches), medium (catches adjacent programs), and broad (catches the outdoor therapy space).

**New question for Alec:** Should we actually use ALL THREE? We could run semantic similarity against each and take the MAX score, giving us the best of all worlds.

---

### Step 12: Q4 — VetsBoats Funding Deep Dive (Online) [T+0:35]

**Search 1:** `"Wooden Boats for Veterans" grant OR funding OR donation OR "supported by" OR sponsor`
- **Websites found:** LENDonate page, vetsboats.org, GuideStar profile, Bay Area Volunteer Info Center
- **Findings:** LENDonate refinancing campaign exists. Terry invested personal funds. Partnerships with ASA, Marine Institute, NW Center for Wooden Boat Building. No specific grant amounts beyond what we already knew.

**Search 2:** `VetsBoats foundation grant funding Sausalito`
- **Websites found:** vetsboats.org, SF Archdiocese article, GuideStar, findCRA, Tahoe Maritime Foundation page about VetsBoats, USVetConnect
- **Key finding:** Tahoe Maritime Foundation has a DEDICATED PAGE for VetsBoats at tahoemaritimefoundation.org/vetboats — strong relationship signal. Also: "In 2023, VetsBoats partnered with Call of the Sea Foundation and Silicon Valley Community Foundation"

**Search 3:** `site:vetsboats.org sponsors donors supporters partners`
- **Websites found:** vetsboats.org/foundation, /programs-1, /post/sail-with-vetsboats
- **Findings:** Philip Connolly is Board Member (LCOL USA Ret., CFO Vu Technologies Corp, Finance Officer American Legion Post 246). No public donor/sponsor list found on their site.

**Search 4:** `"Wooden Boats for Veterans" OR "VetsBoats" "Silicon Valley Community Foundation" OR "Charis Fund" OR "Bonnell Cove" grant`
- **Websites found:** svcf.org grants page, Inside Philanthropy, Instrumentl, InfluenceWatch
- **Findings:** SVCF average grants ~$30K. No specific confirmation of SVCF → VetsBoats grant in public search results. Charis Fund and Bonnell Cove not mentioned in connection with VetsBoats.

**WebFetch: tahoemaritimefoundation.org/vetboats**
- **Result:** Page rendered as Wix JavaScript — no content extractable. Would need to visit in browser.

**Known funders summary after online research:**

| Funder | Amount | Year | Confidence | Source |
|--------|--------|------|------------|--------|
| Tahoe Maritime Foundation | $25,000 | 2023 | CONFIRMED | IRS 990-PF |
| Henry Mayo Newhall Foundation | $15,000 | 2023 | CONFIRMED | IRS 990-PF |
| Sidney Stern Memorial Trust | $3,500 | 2023 | CONFIRMED | IRS 990-PF |
| SVCF | $30,000 | 2023 | PROBABLE | Multiple mentions, SVCF avg grant matches |
| American Online Giving Foundation | $5,054 | 2025 | PROBABLE | Cause IQ |
| Charis Fund | $5,000 | 2022 | UNCONFIRMED | Pre-call brief only |
| Bonnell Cove Foundation | $7,500 | 2022-23 | UNCONFIRMED | Pre-call brief only |
| ~~Goodfellow Fund~~ | ~~$60,000~~ | | DEBUNKED | Grants went to Center for Wooden Boats |
| ~~JPMorgan Chase~~ | ~~$8,550~~ | | DEBUNKED | Grants went to Center for Wooden Boats |
| ~~Bristol-Myers Squibb~~ | ~~$2,520~~ | | DEBUNKED | Grants went to Center for Wooden Boats |

---

### Step 13: Q5 — First-Time Grant Size Research [T+0:40]

**Web searches conducted:**
1. `first time grant size private foundation average median study 2024 2025` → GrantStation 2024/2025 reports, Instrumentl stats, Foundation Source
2. `Exponent Philanthropy small foundation first grant size "test grant" initial` → Grantmaking basics articles, seed funding concept
3. `Candid foundation grant size "first time" OR "new grantee" small nonprofit median 2024 2025 2026` → Candid grants data, Foundation 1000
4. `GrantStation "state of grantseeking" 2025 median grant size small nonprofit first grant` → 2025 State of Grantseeking report
5. `"foundation grant" "first year" OR "initial grant" OR "first grant" smaller renewal nonprofit study data` → General grant databases
6. `Instrumentl grant statistics 2025 average grant size small nonprofit under 250000 budget` → Instrumentl 2025 stats
7. `"Foundation Source" giving trends private foundation median grant size 2024 2025` → Foundation Source 2023 report

**External data collected:**

| Source | Finding |
|--------|---------|
| GrantStation 2025 State of Grantseeking | Small orgs: median total awards $24K, median largest individual award $10K |
| GrantStation 2024 | Median largest award from non-gov funders: $42,500 |
| GrantStation 2025 | Median largest individual award (all): $100K; average: $1.12M (heavily skewed) |
| Foundation Source 2023 | Median grant from smaller/mid-size foundations: constant YoY. Larger foundations: $10-13K range |
| Instrumentl 2025 | Median grant (all 501c3): $30K; Average: $550K (skewed) |
| Candid 2024-2025 | Median YoY change: +3.1%. Foundation 1000 captures grants >= $10K |

**Our own database analysis — THIS IS THE BEST DATA:**

**Query: Grant sizes to small nonprofits ($50K-$250K revenue) in our DB**
```sql
SELECT percentiles FROM fact_grants JOIN nonprofit_returns WHERE total_revenue BETWEEN 50000 AND 250000 AND tax_year >= 2020
```
**Result:** n=1,473,083 grants
| P25 | Median | P75 | Mean |
|-----|--------|-----|------|
| $570 | **$2,500** | $10,000 | $13,965 |

**Query: First-time vs repeat grants across ALL our clients' sibling data**
```sql
SELECT is_first_grant, percentiles FROM calc_client_sibling_grants GROUP BY client_ein, is_first_grant
```

**Result (aggregated across 7 clients):**

| Client | First Grant Median | Repeat Grant Median | Ratio |
|--------|-------------------|--------------------|----|
| Horizons National (061468129) | $5,000 | $10,000 | 2.0x |
| Arborbrook (202707577) | $2,500 | $5,000 | 2.0x |
| Friendship Circle (203472700) | $2,384 | $2,500 | 1.05x |
| Ka Ulukoa (260542078) | $2,500 | $3,000 | 1.2x |
| PSMF (462730379) | $2,000 | $2,500 | 1.25x |
| SNS (942259716) | $4,000 | $5,000 | 1.25x |
| RHF (952249495) | $5,000 | $10,000 | 2.0x |

**Key insight from our data:** First grants are typically **50-100% smaller** than repeat grants. The median first grant across clients is roughly **$2,500-$5,000**, and repeat grants are **$3,000-$10,000**.

For VetsBoats specifically (small org, $137K revenue), the most comparable clients are Ka Ulukoa ($2,500 first / $3,000 repeat) and PSMF ($2,000 / $2,500). But VetsBoats already received a $25K first grant from Tahoe Maritime and $15K from Henry Mayo Newhall — so they're performing ABOVE the median.

**My recommendation on grant size seeking:**
- Keep $5K-$50K as the "realistic ask" range
- VetsBoats' existing $3.5K-$25K grants validate this range
- For the $500K goal: need ~15-20 grants at $25K average, or 10 grants at $50K average
- First-time grants from NEW foundations: expect $5K-$15K initially, with potential to grow to $25K+ on renewal

**ADDITIONAL DATA — Background query completed (first grants by foundation asset size, n=1.95M first grants):**

| Foundation Size | First Grant Median | Subsequent Median | First as % of Sub | N |
|---|---|---|---|---|
| Under $1M | $1,366 | $2,000 | 68% | 504K |
| $1M-$10M | $3,000 | $3,500 | 86% | 681K |
| $10M-$50M | $5,000 | $10,000 | 50% | 361K |
| $50M-$100M | $6,250 | $5,000 | 125% (anomaly) | 112K |
| $100M+ | $10,000 | $25,000 | 40% | 290K |

**Insight:** $10M-$50M foundations (VetsBoats' sweet spot) give first grants that are literally HALF of subsequent grants. They genuinely "test" with smaller amounts. The $50M-$100M anomaly (first > subsequent) may reflect one-time project grants vs. smaller recurring operating support.

---

### Step 14: Q3 — Budget Range for Siblings [T+0:50]

**Alec's question:** $27K-$685K range, or widen for growth ambitions?

**My analysis:**
- Current VetsBoats revenue: $137K
- Standard range: 0.2x to 5x = $27K-$685K
- VetsBoats' GOAL is $500K revenue
- If we use the goal: 0.2x to 5x of $500K = $100K-$2.5M (way too broad, catches large established orgs)
- Compromise: use 0.15x of current to 5.5x of current = $20K-$750K

**My recommendation:** Widen slightly to **$20K-$750K**. The upper bound at $750K catches orgs like Judd Goldman Adaptive Sailing ($678K) which is already one of our best siblings. Going higher risks pulling in orgs that are structurally different from VetsBoats.

---

### Step 15: Q5 (Continued) — First-Time Grant Size Web Research [T+1:05, new session]

**Context:** Previous session (Step 13) analyzed our own DB data on first-time vs repeat grants. Alec wants external web sources to complement our internal data.

**Alec's decisions from review:**
- Q1: Approved — keep 10 specific keywords + add "veteran fishing" = 11 total
- Q2: Approved — use 3-option Max-of-3 semantic scoring (narrow/medium/broad)
- Q3: Approved — widen budget range to $20K-$750K
- Q4: Exclude ALL 5 confirmed funders (Charis Fund and Bonnell Cove confirmed by client as past funders). EINs: 943073894, 946073084, 956495222, 946077619, 133556721
- Q5: Do more web research on first-time grant sizes

**Web Search 1:** `first time grant award size private foundation new grantee 2025 2026 study data`
- **Sites returned:** thegrantportal.com, privatefoundationgrants.org, spencer.org, instrumentl.com/blog/grant-statistics-and-trends, americanafoundation.org, grantwritingandfunding.com, funraise.org, candid.org, foundationsource.com
- **Useful finding:** Candid survey — 53.9% of foundations expect 2025 giving same as 2024; 37.3% expect increase. Foundation Source: 71,000+ grants through Sept 2025, $1.6B total.
- **No specific first-time grantee data found in this search.**

**Web Search 2:** `foundation "test grant" "first grant" size small nonprofit initial funding amount research`
- **Sites returned:** thegrantportal.com, grantwatch.com, bankofamerica.com, foundationlist.org, fconline.foundationcenter.org, yawkeyfoundation.org, instrumentl.com, spmcf.org, fftc.org, nerdwallet.com
- **No specific data on test grant sizes.** General guidance only.

**Web Search 3:** `Exponent Philanthropy small foundation grantmaking trends 2025 2026 median grant size`
- **Sites returned:** exponentphilanthropy.org (2025 FOMR blog, due diligence blog, family foundation trends), candid.org, philanthropy.com, fundingforgood.org, grantassistant.ai, nonprofitquarterly.org, pnc.com
- **Key finding:** Exponent Philanthropy 2025 FOMR — average grant size = $74,981. But this is across ALL their members (assets $1M-$1B+), so heavily skewed by large grants. 75% of funders offer single-year operating grants; only 28% provide multiyear GOS.

**WebFetch 1:** instrumentl.com/blog/grant-statistics-and-trends
- **Result:** Article has extensive stats on grant writing timelines and success rates but NO specific data on grant sizes, median amounts, or first-time vs returning grantee amounts. Dead end.

**WebFetch 2:** exponentphilanthropy.org/blog/key-insights-from-the-2025-foundation-operations-management-report/
- **Result:** Average grant size $74,981. 62% streamlined applications, 58% simplified reporting, 65% collaborate with other funders. No first-time grantee data.

**WebFetch 3:** exponentphilanthropy.org/blog/grantmaking-due-diligence-organizational-budget-size/
- **Result:** Qualitative article about how foundations evaluate grantee budget size. Identifies 4 "blind spots" in budget-based decisions: restricted vs unrestricted funds, sector structures, capital types, anchoring bias. Mentions two example orgs with budgets of $5.9M and $375K but no specific grant-to-budget ratios or first-time data. Recommends "right-sizing guidelines" but gives no numbers.

**Web Search 4:** `GrantStation "state of grantseeking" 2025 2026 report median grant size first time applicant`
- **Sites returned:** grantstation.com (main page, 2025 PDF, 2024 report, 2023 report), grantprofessionals.org, instrumentl.com, writeepicgrants.com, grantassistant.ai, grantstation.com/benchmarker
- **Key finding:** GrantStation 2025 — median total awards: $24K for small orgs, $4.28M for extra-large orgs. 95% of orgs submitting 6+ applications received at least one award. All orgs submitting 31+ applications received funding.

**Web Search 5:** `Foundation Source private foundation giving report 2025 2026 median grant amount new grantee returning grantee statistics`
- **Sites returned:** foundationsource.com (2026 outlook, 2025 report PDF), candid.org, philanthropy.com, nonprofitpro.com, prnewswire.com, givingusa.org, foundationlist.org, irs.gov
- **Key finding from Foundation Source 2025 Report:** 1,136 foundations in study made 37,136 grants totaling $983.5M in 2024 (up from $943.9M in 2023). Average grants per foundation: 32 (up from 31). Average grant size: $26,417 (up from $26,109). No first-time grantee breakdown.

**Web Search 6:** `Candid foundation grants data 2025 new grantee "first grant" smaller initial amount pilot test`
- **Sites returned:** candid.org (multiple pages), fconline.foundationcenter.org, macfound.org
- **No specific first-time grantee data.** Candid processes ~3M grants/year representing $180B+, but data for a given year is complete ~2 years after year-end.

**WebFetch 4-6:** Attempted to fetch Foundation Source 2026 outlook press release, Foundation Source 2025 Report PDF, and GrantStation 2025 PDF.
- Foundation Source 2026 outlook: Page rendered as HTML structure, content truncated. No new data extracted.
- Foundation Source 2025 Report PDF: Returned raw PDF metadata (logo file?), no readable content.
- GrantStation 2025 PDF: Raw compressed PDF, not parseable.
- **All three dead ends for detailed stats.**

**Web Search 7:** `nonprofit "first time" foundation grant smaller amount "test grant" build relationship initial investment research study`
- **Sites returned:** learning.candid.org, exponentphilanthropy.org, candid.org/blogs, nonprofitmegaphone.com, grantstation.com, neonone.com, instrumentl.com, igxsolutions.com, fundsforngos.org
- **Key qualitative findings from Candid:**
  - For strong alignment + high capacity + NO relationship: ask for **40-60%** of what you'd ask with a relationship
  - For moderate alignment: ask for **10-40%**
  - Existing funders: can request **15-25% increase** on renewal
  - Family foundations "may decline a nonprofit's first or second request" as they learn about the org — persistence is expected

**Web Search 8:** `Foundation Source 2025 report private philanthropy average grant size median grant new grantee returning grantee statistics`
- **Sites returned:** Same Foundation Source pages, candid.org, instrumentl.com, nonprofitpro.com, givingusa.org
- **No new data beyond what was already found.**

**WebFetch 5:** candid.org/blogs/how-much-money-to-ask-for-grant-proposal-tips-for-success/
- **Key framework extracted:**
  - Strong alignment + high capacity + existing relationship → Ask for 70-90% of budget need
  - Strong alignment + high capacity + NO relationship → Ask for 40-60%
  - Moderate alignment + high capacity → Ask for 20-40%
  - Moderate alignment + moderate capacity → Ask for 10-20%
  - Existing funders → possible 15-25% increase on renewal
  - "Review Forms 990 from the last five years" for grant size patterns

**WebFetch 6:** instrumentl.com/blog/how-much-to-ask-for-in-a-grant — **THIS WAS THE BEST SOURCE**
- **CRITICAL DATA POINT:** "First-time applicants received a median of $15,000, while returning grantees received over $150,000 — a tenfold difference from the same foundation."
- **IMPORTANT CAVEAT I noticed:** This example is specifically from the **Ford Foundation** — one of the largest foundations in the world ($16B+ assets). This is NOT representative of the $1M-$50M foundations that are VetsBoats' sweet spot. Ford Foundation gives massive grants; their "small first grant" of $15K is still larger than many foundations' typical grants.
- **Other key advice:** "Most foundations stick to patterns in how they fund organizations. Their past giving is the best predictor of future giving." New grantees should compare past giving "specifically for new grantees" rather than overall foundation averages.
- **Funding by funder type — % of ask actually awarded:**
  - State/Local Government: 50%
  - Private Foundations: 32%
  - Association/Society Funders: 28%
  - Federal Agencies: 15%
  - Corporate Funders: 11%

**Web Search 9:** `Instrumentl "first time" grantee median $15000 returning grantee foundation grant size data study`
- Confirmed the $15K median for new grantees was specifically from **Ford Foundation** analysis. "New grantees were awarded a median of $15,000 by the Ford Foundation over the last 3 years."

**WebFetch 7:** writeepicgrants.com/291-the-2025-state-of-grantseekers-report-is-out/
- **Key stats:** 57% of respondents applied for more grants in 2024 and received more awards. Recurring grants = 10% of total. Only 1-2 people manage grantseeking in most orgs. Strong correlation between application volume and success.
- **No first-time grantee amount data.**

---

### Step 15 Summary: First-Time Grant Size — Combined Web + DB Evidence

**What the web says:**
| Source | Finding | Applicability to VetsBoats |
|--------|---------|---------------------------|
| Instrumentl/Ford Foundation | First-time median: $15K; returning: $150K (10x) | LOW — Ford is $16B+ foundation, not representative of $1M-$50M sweet spot |
| Candid | First-time applicants should ask for 40-60% of what they'd ask with a relationship | MODERATE — useful framing for positioning strategy |
| Foundation Source 2025 | Average grant size: $26,417 across 1,136 foundations ($1M-$1B assets) | MODERATE — gives overall benchmark |
| Exponent Philanthropy 2025 | Average grant size: $74,981 | LOW — skewed by large foundations |
| GrantStation 2025 | Small org median total awards: $24K/year from all grants | HIGH — directly comparable to VetsBoats' budget tier |
| Candid | Existing funders: can request 15-25% increase on renewal | HIGH — applies to relationship-building strategy |

**What our DB says (from Step 13, previous session):**
| Source | Finding | Applicability |
|--------|---------|---------------|
| Our DB: grants to $50K-$250K revenue orgs | Median grant: $2,500; P75: $10,000 | HIGHEST — our own data, same budget tier |
| Our DB: first vs repeat grants (7 clients) | First grants 50-100% smaller than repeat | HIGHEST — direct measurement |
| Our DB: $10M-$50M foundations | First grant median: $5,000; subsequent: $10,000 (50%) | HIGHEST — sweet spot foundation size |
| Our DB: $1M-$10M foundations | First grant median: $3,000; subsequent: $3,500 (86%) | HIGH — smaller foundations barely differentiate |

**SYNTHESIS for VetsBoats grant_size_seeking decision:**
- Our DB data is the most directly relevant: first grants from $1M-$50M foundations to small nonprofits → **$3,000-$5,000 median**
- BUT VetsBoats has already received $15K and $25K first grants — they're performing well above median
- Web data confirms the general pattern: first grants are smaller, 40-60% of established relationship level
- The GrantStation $24K/year total for small orgs is a useful ceiling for expected annual grant income from foundations
- **RECOMMENDATION CONFIRMED: $5K-$50K grant size seeking range is appropriate**
  - $5K = realistic first grant from $1M-$10M foundations
  - $50K = ambitious but achievable from $10M-$50M foundations with strong fit
  - VetsBoats' track record ($25K from Tahoe Maritime) validates the upper end

---

### Step 16: Finalize Checkpoint 1 Decisions & Execute dim_clients INSERT [T+1:20]

**All 5 decisions finalized by Alec:**

| # | Decision | Final Answer |
|---|----------|-------------|
| 1 | Keywords | 11 keywords: original 10 + "veteran fishing" |
| 2 | target_grant_purpose | 3-option Max-of-3 scoring (narrow/medium/broad) |
| 3 | Budget range | $20K-$750K |
| 4 | Known funders | Exclude all 5: Tahoe Maritime (943073894), Henry Mayo Newhall (946073084), Sidney Stern (956495222), Charis Fund (946077619), Bonnell Cove (133556721) |
| 5 | Grant size seeking | $5K-$50K confirmed |

**Executing dim_clients INSERT...**

---

## [Checkpoint 2 will be logged in a separate file: LOG_2026-02-06_checkpoint2_siblings_grants.md]
