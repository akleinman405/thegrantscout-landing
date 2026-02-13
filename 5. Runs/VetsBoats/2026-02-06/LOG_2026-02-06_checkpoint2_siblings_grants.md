# VetsBoats Report Build — Checkpoint 2 Activity Log

**Date:** 2026-02-06
**Phase:** Checkpoint 2 — Sibling Discovery & Grant Landscape
**Client:** Wooden Boats for Veterans (dba VetsBoats), EIN 46-4194065

---

## SESSION START — Checkpoint 2 [T+0:00]

**Context:** Checkpoint 1 is complete. All 5 decisions finalized by Alec:
1. Keywords: 11 total (original 10 + "veteran fishing")
2. target_grant_purpose: 3-option Max-of-3 semantic scoring
3. Budget range: $20K-$750K
4. Known funders: Exclude all 5 (Tahoe Maritime, Henry Mayo Newhall, Sidney Stern, Charis Fund, Bonnell Cove)
5. Grant size seeking: $5K-$50K

**dim_clients INSERT executed successfully:** VetsBoats is now ID 8 in dim_clients. Verified: 5 known funders, 11 keywords, $20K-$750K budget range, active status.

---

### Step 1: Load 28 Known Siblings [T+0:01]

**Source:** `5. Runs/VetsBoats/2026-01-16/REPORT_2026-01-16.1_vetsboats-sibling-analysis.md`

**Schema check:** Examined `calc_client_siblings` columns: client_ein, sibling_ein, similarity, client_budget, sibling_budget, budget_ratio, model_version, computed_at.

**Pattern check:** Looked at how SNS (942259716) siblings are stored to match format. Found they use `all-MiniLM-L6-v2` as model_version and have numeric similarity scores. Since our siblings are keyword-based (not embedding-based), I used `keyword_tier_v1` as model_version and tiered similarity scores:
- Tier 1 Veteran Sailing/Therapy: 0.90 (closest match)
- Tier 1 Veteran Water Recreation: 0.80
- Tier 1 Wooden Boat Programs: 0.75
- Tier 2 Veteran Outdoor Therapy: 0.65

**Query:**
```sql
INSERT INTO f990_2025.calc_client_siblings (client_ein, sibling_ein, similarity, client_budget, sibling_budget, budget_ratio, model_version, computed_at)
VALUES
('464194065', '363832321', 0.90, 136943, 678208, 4.95, 'keyword_tier_v1', NOW()),
... [28 rows total]
```

**Result:** INSERT 0 28 — all 28 siblings loaded successfully.

**My thinking:** Using tiered similarity scores lets us weight siblings in downstream scoring — a veteran sailing org (0.90) is more relevant than a veteran outdoor therapy org (0.65) for VetsBoats' specific programs. This is a reasonable proxy for what embedding-based similarity would produce.

---

### Step 2: Search for Additional Siblings [T+0:03]

**First search — expanded budget range ($700K-$750K):**
```sql
SELECT ein, organization_name, state, city, total_revenue
FROM f990_2025.nonprofit_returns
WHERE total_revenue BETWEEN 700000 AND 750000
AND (organization_name ILIKE '%veteran%sail%' OR ...)
```
**Result:** 0 rows. No new siblings in the expanded range.

**Second search — organizations from grant purpose text analysis:**
In Checkpoint 1, Step 11, I found 54 grants with sailing+veteran/therapeutic language. Several were to organizations NOT in our sibling list. I searched for these by name patterns:

```sql
SELECT ein, organization_name, state, city, total_revenue
FROM f990_2025.nonprofit_returns
WHERE total_revenue BETWEEN 20000 AND 750000
AND (
    organization_name ILIKE '%sail%prevail%' OR '%veteran%deck%' OR '%call%sea%'
    OR '%freedom%water%' OR '%sail%angel%' OR '%raider%sail%'
    OR '%hudson%river%sail%' OR '%team%paradise%sail%' OR '%chesapeake%boat%'
    OR '%rocking%boat%'
)
AND ein NOT IN (SELECT sibling_ein FROM f990_2025.calc_client_siblings WHERE client_ein = '464194065')
```

**Result:** 29 rows (multiple years per org). Found 6 unique organizations:

| EIN | Organization | State | Most Recent Rev | Mission Alignment |
|-----|-------------|-------|-----------------|-------------------|
| 050399703 | Sail to Prevail | RI | $621,503 (2023) | EXCELLENT — therapeutic sailing for disabled + wounded military |
| 202663905 | Team Paradise Sailing | FL | $127,172 (2024) | GOOD — sailing for disabled, veterans, underserved |
| 204513735 | Freedom Waters Foundation | FL | $673,720 (varies) | GOOD — boating for disabled, veterans, youth at risk |
| 453186110 | Sailing Angels Foundation | TX | $101,136 (2024) | MODERATE — adaptive sailing for disabled (no veteran focus) |
| 933706958 | Raider Sailing Foundation | WA | $108,950 (2023) | EXCELLENT — combat veteran sailing adventures |
| 710682761 | Freedom Water Association | AR | $603,464 (2023) | NONE — water utility in rural Arkansas. FALSE POSITIVE. |

**Mission verification query:**
```sql
SELECT ein, organization_name, mission_description, state, city, MAX(total_revenue)
FROM f990_2025.nonprofit_returns
WHERE ein IN ('204513735', '050399703', '710682761', '202663905', '453186110', '933706958')
GROUP BY ein, organization_name, mission_description, state, city
```

**Key mission texts found:**
- **Sail to Prevail:** "Our national disabled sailing program teaches children and adults with disabilities to overcome adversity through therapeutic sailing... Wounded U.S. military personnel also take part through dedicated programs."
- **Raider Sailing Foundation:** "To empower combat veterans through transformative experiences that rekindle the camaraderie and purpose found in close-knit teams. Through dynamic sailing adventures, we facilitate the reintegration of teams of veterans into a supportive community."
- **Team Paradise:** "Changing lives by inspiring and empowering disabled and underserved communities, US Veterans and others through recreational, educational and healing programs that motivate and engage participants in the sport of sailing."
- **Freedom Waters:** "To provide boating opportunities and marine related education for people with disabilities, veterans, and youth at risk."
- **Sailing Angels:** "Introduce sailing in the form of recreation, exercise, and education to children and adults with physical and developmental disabilities."

**Budget filtering decision:**
- Freedom Waters' most recent year (2024) shows $1.55M — above $750K cap
- BUT earlier years range $550K-$673K, within range
- Alec explicitly requested keeping Freedom Waters — overriding the budget filter
- Used $673,720 (most recent in-range year) for the insert

**Initial decision was to exclude Freedom Waters as too large. Alec overrode this — "keep freedom waters."**

**Inserted 5 new siblings:**

```sql
INSERT INTO f990_2025.calc_client_siblings VALUES
('464194065', '050399703', 0.90, 136943, 621503, 4.54, 'keyword_tier_v1', NOW()),  -- Sail to Prevail
('464194065', '202663905', 0.85, 136943, 127172, 0.93, 'keyword_tier_v1', NOW()),  -- Team Paradise
('464194065', '204513735', 0.85, 136943, 673720, 4.92, 'keyword_tier_v1', NOW()),  -- Freedom Waters
('464194065', '453186110', 0.75, 136943, 101136, 0.74, 'keyword_tier_v1', NOW()),  -- Sailing Angels
('464194065', '933706958', 0.95, 136943, 108950, 0.80, 'keyword_tier_v1', NOW());  -- Raider Sailing
```

**Result:** INSERT 0 5. Now 33 siblings total.

**Similarity scores rationale:**
- Raider Sailing (0.95): combat veteran sailing — closest possible match to VetsBoats
- Sail to Prevail (0.90): therapeutic sailing + military — same tier as our Tier 1 Veteran Sailing
- Team Paradise (0.85): sailing for vets + disabled — slightly broader focus
- Freedom Waters (0.85): boating for vets + disabled + youth — broader but strong fit
- Sailing Angels (0.75): adaptive sailing, no veteran focus — similar to Wooden Boat Programs tier

---

### Step 3: Populate All Grants to Siblings [T+0:06]

**Pre-count query:**
```sql
SELECT COUNT(*) as total_grants, COUNT(DISTINCT fg.foundation_ein) as unique_foundations
FROM f990_2025.fact_grants fg
JOIN f990_2025.calc_client_siblings cs ON fg.recipient_ein = cs.sibling_ein
WHERE cs.client_ein = '464194065'
```
**Result:** 342 grants from 139 unique foundations (before Freedom Waters).

**Main INSERT query — 342 grants (before Freedom Waters):**

Built a complex INSERT with inline keyword matching for all 11 keywords:

```sql
INSERT INTO f990_2025.calc_client_sibling_grants (
    client_ein, foundation_ein, sibling_ein, grant_id, amount, tax_year,
    recipient_state, purpose_text, is_first_grant, purpose_quality,
    keyword_match, semantic_similarity, is_target_grant, target_grant_reason, computed_at
)
SELECT
    '464194065',
    fg.foundation_ein, fg.recipient_ein, fg.id, fg.amount, fg.tax_year,
    fg.recipient_state, fg.purpose_text,
    (fg.tax_year = first_yr.first_year) as is_first_grant,
    CASE
        WHEN fg.purpose_text IS NULL OR '' THEN 'none'
        WHEN LENGTH(fg.purpose_text) < 20 THEN 'low'
        WHEN LENGTH(fg.purpose_text) < 50 THEN 'medium'
        ELSE 'high'
    END as purpose_quality,
    CASE WHEN purpose_text ILIKE '%veteran%sail%' OR '%therapeutic%sail%'
        OR '%adaptive%sail%' OR '%sailing%program%' OR '%veteran%wellness%'
        OR '%veteran%outdoor%' OR '%boat%restor%' OR '%wooden%boat%'
        OR '%maritime%heritage%' OR '%PTSD%veteran%' OR '%veteran%PTSD%'
        OR '%veteran%fish%'
    THEN TRUE ELSE FALSE END as keyword_match,
    NULL, FALSE, NULL, NOW()
FROM f990_2025.fact_grants fg
JOIN f990_2025.calc_client_siblings cs ON fg.recipient_ein = cs.sibling_ein
    AND cs.client_ein = '464194065'
LEFT JOIN (...first_year subquery...) first_yr ON ...
```

**Result:** INSERT 0 342.

**Then added Freedom Waters grants separately:** INSERT 0 5.

**Final counts:**
| Metric | Value |
|--------|-------|
| Total grants | 347 |
| Unique foundations | 144 |
| Siblings with grants | 24 (out of 33) |
| Keyword matches | 26 |
| High-quality purpose texts | 41 |

**My thinking:** 24 out of 33 siblings have grants in our DB. The 9 without grants are likely very small orgs that only receive grants from community foundations or government sources (not private foundations in our data). 26 keyword matches is a solid start — semantic scoring will likely add more target grants.

---

### Step 4: Semantic Similarity Scoring [T+0:10]

**Approach:** 3-option Max-of-3 semantic scoring using sentence-transformers (all-MiniLM-L6-v2)

**Target grant purpose texts used:**
- **Narrow:** "To provide veterans with sailing outings and lessons as a way to provide emotional support and healing through mindfulness-based therapeutic sailing" (148 chars)
- **Medium:** "Therapeutic sailing programs for military veterans suffering from PTSD and traumatic injuries, including adaptive sailing, sail training, and wooden boat restoration to support veteran well-being and healing" (207 chars)
- **Broad:** "Outdoor recreation therapy programs for military veterans, including therapeutic sailing, boat restoration, and mindfulness-based wellness programs supporting veterans with PTSD" (177 chars)

**Script:** Wrote `semantic_scoring.py` in scratchpad directory. Process:
1. Load all-MiniLM-L6-v2 model
2. Encode all 3 target texts
3. Fetch all 340 grants with non-empty purpose text (7 have no purpose)
4. Encode all grant texts in batches of 64
5. Calculate cosine similarity of each grant against all 3 targets
6. Take MAX score across the 3 targets for each grant
7. Update calc_client_sibling_grants with the max score
8. Set is_target_grant = TRUE where keyword_match OR semantic >= 0.55

**First run error:** `psycopg2.errors.StringDataRightTruncation: value too long for type character varying(20)` — the target_grant_reason column is VARCHAR(20) and I was trying to write longer strings like "keyword+semantic_narrow". Fixed by using abbreviated codes ("kw+sem", "keyword", "semantic") and separating the update logic.

**Fix applied:** Reset all scoring fields, simplified the update SQL, re-ran.

**Second run — SUCCESS:**

```
Loading sentence-transformers model...
Encoding 3 target grant purposes...
Scoring 340 grants with purpose text...
Encoding grant texts... [6 batches, ~2 seconds]
Calculating similarities...
Updating 340 grants in database...

=== RESULTS ===
Total grants scored: 340
Target grants (keyword OR semantic>=0.55): 47
  Keyword matches: 26
  Semantic matches (>=0.55): 47
  Both keyword + semantic: 26
Similarity stats: avg=0.2300, median=0.1655, max=0.7590, min=-0.0170
```

**Key insight:** ALL 26 keyword matches also scored >= 0.55 on semantic (100% overlap). Semantic added 21 additional target grants that keywords missed. Total target grants: 47.

**Similarity Distribution:**

| Bucket | Count | Notes |
|--------|-------|-------|
| 0.70+ | 5 | Extremely high — near-perfect matches |
| 0.55-0.69 | 42 | Strong matches — target grant territory |
| 0.40-0.54 | 11 | Moderate — potentially relevant but below threshold |
| 0.25-0.39 | 62 | Weak — somewhat related |
| <0.25 | 220 | Not related — general/operating grants |

**Top 10 Highest Scoring Grants:**

| Score | KW? | Amount | Year | Purpose Text |
|-------|-----|--------|------|-------------|
| 0.759 | YES | $5,000 | 2023 | PROVIDE COMBAT VETERANS TO RECONNECT, RELAX AND REDUCE STRESS WHILE SAILING |
| 0.713 | YES | $25,000 | 2020 | OVERCOMING ADVERSITY THROUGH THERAPEUTIC SAILING |
| 0.713 | YES | $25,000 | 2019 | OVERCOMING ADVERSITY THROUGH THERAPEUTIC SAILING |
| 0.713 | YES | $25,000 | 2021 | OVERCOMING ADVERSITY THROUGH THERAPEUTIC SAILING |
| 0.713 | YES | $50,000 | 2022 | OVERCOMING ADVERSITY THROUGH THERAPEUTIC SAILING |
| 0.669 | no | $5,000 | 2018 | DONATION TO USE THE SPORT OF SAILING AS A PLATFORM TO TEACH PEOPLE TO OVERCOME ADVERSITY... |
| 0.669 | no | $2,500 | 2019 | (same as above, different year) |
| 0.664 | no | $12,000 | 2022 | CONTRIBUTION FOR SAILING FOR CHILDREN AND TEENS WITH DISABILITIES |
| 0.664 | no | $15,000 | 2024 | (same — recurring grant) |
| 0.664 | no | $15,000 | 2023 | (same — recurring grant) |

**My thinking:** The 0.55 threshold feels right. The grants just above it are things like "SUPPORT THERAPEUTIC BENEFITS OF SAIL" (0.568) and "SAILING CLINIC FOR VETERANS AND THE DISABLED" (0.586). Below 0.55 we start seeing things like "YOUTH DEVELOPMENT" (0.42) and "GENERAL OPERATING SUPPORT" (0.33) which aren't specific enough.

The fact that all keyword matches also scored >= 0.55 is validating — it means our keyword list and semantic model are aligned.

---

### Step 5: Foundation-Level Analysis [T+0:15]

**Foundations with target grants — enrichment query:**

```sql
WITH target_foundations AS (
    SELECT foundation_ein, COUNT(*) total_grants,
        SUM(CASE WHEN is_target_grant ...) as target_grants, ...
    FROM calc_client_sibling_grants WHERE client_ein = '464194065'
    GROUP BY foundation_ein
)
SELECT ..., pf_returns assets/preselected, states_funded, ca_grants
FROM target_foundations
LEFT JOIN dim_foundations, pf_returns
WHERE target_grants > 0
```

**Result: 19 foundations with target grants**

| Foundation | State | Assets | Open? | Target Grants | Total $ | CA Grants | States |
|-----------|-------|--------|-------|---------------|---------|-----------|--------|
| Lyn & Margaret Comfort | RI | $425K | NO | 6 | $3K | 0 | 7 |
| Van Beuren Charitable | NY | $343M | NO | 5 | $130K | 11 | 24 |
| Roy T Morgan Foundation | RI | $3M | YES | 5 | $78K | 0 | 2 |
| San Francisco Challenge | CA | $2.1M | NO | 5 | $50K | 34 | 3 |
| John D & K A Johnston | TX | $742K | NO | 5 | $21.5K | 1 | 3 |
| John and Daria Barry | FL | $477M | NO | 4 | $125K | 6 | 10 |
| Albert & Ethel Herzstein | TX | $127M | YES | 2 | $122K | 11 | 23 |
| Calf Island Foundation | CT | $172K | NO | 2 | $12.5K | 0 | 8 |
| Frank & Eileen Nugent | FL | $4.4M | YES | 2 | $10K | 0 | 4 |
| Arena Energy Foundation | TX | $70K | NO | 2 | $5K | 2 | 8 |
| Jim Moran Foundation | FL | $252M | YES | 1 | $20K | 0 | 10 |
| Donald Morris Charitable | OH | $13.4M | YES | 1 | $15K | 0 | 2 |
| Greathouse Foundation | TX | $10M | YES | 1 | $10K | 0 | 9 |
| Ruth & Hal Launders | VA | $49.5M | NO | 1 | $5K | 11 | 19 |
| Corinthians Endowment | PA | $196K | YES | 1 | $5K | 0 | 3 |
| Harry S Cameron Foundation | TX | $30.2M | YES | 1 | $5K | 1 | 14 |
| Cheryl & Ken Ellegard | AZ | $35K | NO | 1 | $1K | 4 | 6 |
| Sparks Foundation | TN | $6.4M | YES | 1 | $500 | 3 | 22 |
| Howell Family Charitable | MA | $1.4M | NO | 1 | $250 | 3 | 11 |

**Foundations funding 2+ siblings (ANY grants, not just target):**
- Bank of America Charitable (NC): 4 siblings, 5 grants, $3,200 — no target grants
- Xcel Energy Foundation (MN): 2 siblings, 3 grants, $135 — no target grants

**My thinking:** The multi-sibling signal is weak for VetsBoats because our siblings are niche orgs. The target grant signal is much stronger. The most promising foundations at first glance:

**Open to applications + meaningful assets + CA or national:**
1. Albert & Ethel Herzstein ($127M, TX, 11 CA grants, 23 states) — broad national reach
2. Harry S Cameron Foundation ($30M, TX, 14 states) — decent size
3. Greathouse Foundation ($10M, TX, 9 states) — mid-range
4. Sparks Foundation ($6.4M, TN, 22 states) — wide geographic spread
5. Donald Morris Charitable ($13.4M, OH, 2 states) — limited geography but good size

**Preselected-only but worth noting (cultivation targets):**
- Van Beuren Charitable ($343M, 24 states, 11 CA grants) — massive assets, national
- John and Daria Barry ($477M, 10 states, 6 CA grants) — massive, high target grants
- San Francisco Challenge ($2.1M, CA) — local CA foundation
- Ruth & Hal Launders ($49.5M, 19 states, 11 CA grants) — national reach

**NOTE:** These 19 foundations are only the ones from SIBLING grants. Checkpoint 3 will score ALL 144 foundations (and potentially the broader 12,653 open foundations) using the LASSO model signals.

---

## Checkpoint 2 Summary

| Metric | Value |
|--------|-------|
| **Total siblings** | 33 (28 original + 5 new) |
| **Siblings with grants in DB** | 24 |
| **Total grants to siblings** | 347 |
| **Unique foundations** | 144 |
| **Keyword-matched grants** | 26 |
| **Semantic-matched grants (>=0.55)** | 47 |
| **Target grants (keyword OR semantic)** | 47 |
| **Foundations with target grants** | 19 |
| **Open + target grants** | 9 |
| **Open + target + CA/national** | ~5-8 (needs verification in Checkpoint 3) |
| **Highest semantic score** | 0.759 ("combat veterans...sailing") |
| **Median semantic score** | 0.166 |
| **Semantic threshold used** | 0.55 |

---

*Log generated by Claude Code on 2026-02-06*
