# SESSION STATE: Friendship Circle SD Report Build - 2026-01-16

**Last Updated:** 2026-01-16 16:45
**Purpose:** Preserve context for Friendship Circle foundation matching report

---

## CURRENT STATUS

Building foundation matching report for **Friendship Circle San Diego** following the step-by-step guide. Currently at **Phase 3.3** (scoring) and about to do **Phase 3.4** (eligibility enrichment).

---

## CLIENT PROFILE

| Field | Value |
|-------|-------|
| **Name** | Friendship Circle SD INC. |
| **EIN** | 203472700 |
| **Location** | San Diego County, California (Encinitas) |
| **Budget (IRS 2023)** | $2,690,324 revenue / $5,212,943 assets |
| **Budget Variance** | RED (questionnaire said $500K-$1M) |
| **NTEE Code** | P30 (Children & Youth Services) |
| **Grant Size Seeking** | $25,000 - $100,000 |
| **Key Project** | Vocational training bakery (~$100K need) |
| **Staff** | 8 employees, 75 volunteers |
| **Email** | rabbiyossi@friendshipsd.org |

### Mission
"We promote Friendships between people with and without special needs by providing recreational, educational, social and vocational experiences in an inclusive environment."

### Target Grant Purpose
"Vocational training program operating a bakery social enterprise that provides employment skills and job placement for adults with developmental disabilities in San Diego County"

### Matching Keywords (stored in dim_clients)
```
disability, special needs, vocational, employment, job training,
inclusion, developmental, jewish, recreation, social enterprise
```

---

## COMPLETED PHASES

### Phase 1: Pre-Flight Setup ✅
- Client loaded in dim_clients (id=7)
- EIN verified: 203472700
- IRS financials populated: database_revenue=$2,690,324, database_assets=$5,212,943
- Budget variance flagged: RED
- Run folder created: `5. Runs/friendship_circle_sd/2026-01-16/`

### Phase 2: Client Understanding ✅
- Mission comparison: Questionnaire version selected (more specific about vocational)
- 10 keywords identified and stored
- Target grant purpose created and stored
- Data quality issues flagged (budget variance, staff mismatch)

### Phase 3.1.1: Find Siblings ✅
- **102 siblings** found
- Parameters: similarity >= 0.72, budget 0.2x-5x ($538K-$13.5M)
- Quality verified: 87% strong matches
- Stored in: `calc_client_siblings` WHERE client_ein = '203472700'

### Phase 3.2.1: Populate Sibling Grants ✅
- **1,460 grants** from **554 foundations** to 77 siblings
- Years: 2018-2024
- Purpose quality: 77.5% VALID, 14.2% GENERIC, 8.4% TOO_SHORT
- Stored in: `calc_client_sibling_grants`

### Phase 3.2.2: Generate Semantic Similarity ✅
- Ran TWICE: original specific purpose + broader framing
- Broader framing: "Programs serving people with disabilities including employment training, vocational services, job placement, recreation, social inclusion, and community integration for adults with special needs"
- Results: 65 grants >= 0.55 similarity (up from 4 with original)
- Max similarity: 0.740

### Phase 3.2.3: Update Keyword Matches ✅
- 91 grants matched keywords (8.0%)

### Phase 3.2.4: Update Target Grant Flags ✅
- Used **AND** approach (semantic >= 0.55 AND keyword_match)
- **61 target grants** from **38 foundations**

### Phase 3.3.1: Aggregate Foundation Scores ✅
- **554 foundations** scored
- **38 with target grants**
- **9 with gold standard grants** (target + first-time + CA geography)
- LASSO scoring: NOT YET RUN

---

## KEY DATA TABLES

| Table | Records | Query |
|-------|---------|-------|
| calc_client_siblings | 102 | WHERE client_ein = '203472700' |
| calc_client_sibling_grants | 1,460 | WHERE client_ein = '203472700' |
| calc_client_foundation_scores | 554 | WHERE client_ein = '203472700' |

---

## TOP PROSPECTS (GOLD STANDARD)

9 foundations gave TARGET grants to FIRST-TIME recipients in CALIFORNIA:

| Foundation | State | Gold | Assets | Notes |
|------------|-------|------|--------|-------|
| **Liora & Levy Gerzberg** | CA | 2 | $1.5M | Jewish family foundation - best fit |
| **Windsong Trust** | CA | 1 | $429M | Huge assets, gave $1.5M to siblings |
| **Sheila Dave & Sherry Gold** | CA | 1 | $68M | Large CA foundation |
| **Stanley W Ekstrom** | CA | 1 | $54M | CA foundation |
| **Oak Tree Charitable** | CA | 1 | $7.5M | CA foundation |
| Russell J Salvatore | NY | 1 | $2.9M | Out of state |
| Valleycare Medical | CA | 1 | $398K | Healthcare focus |
| Cabrerizo Family | FL | 1 | $4K | Small |
| Ethel and Nathan Cohen | CA | 1 | $0 | Minimal assets |

---

## NEXT STEPS

### Phase 3.4: Enrich Foundation Scores (PENDING)
Need to verify for top ~20-38 foundations:
- **geo_eligible**: Does foundation fund California?
- **open_to_applicants**: Not invite-only?
- **client_eligible**: Does FC meet foundation requirements?
- **eligibility_notes**: Specific restrictions
- **has_active_opportunities**: Current RFPs?
- **opportunity_notes**: Application details

### Phase 3.5: Select Final 5 Foundations (PENDING)

### Optional: Run LASSO Scoring
Script location: `/Users/aleckleinman/Documents/TheGrantScout/9. Pipeline Legacy (Large CSVs)/Pipeline v2/scripts/02_score_foundations_v6.1.py`

---

## KEY LEARNINGS (from PSMF)

1. **Verify eligibility EARLY** - Most major foundations are invite-only
2. **Match on PROGRAM TYPE** - "vocational/workforce" not just "disability"
3. **Local geography is advantage** - FC is county-wide (unlike PSMF's global scope)
4. **Broader semantic framing works** - 65 vs 4 target grants with broader framing
5. **Gold standard = strongest signal** - Target + First-time + Geography

---

## DIFFERENCES FROM PSMF

| Factor | PSMF | Friendship Circle |
|--------|------|-------------------|
| Geography | Global (48 countries) | Local (San Diego County) |
| Budget | $1M+ | $2.69M |
| Challenge | Global scope conflicts | Simpler - local nonprofit |
| Siblings found | 91 | 102 |
| Target grants | TBD (narrow target) | 61 (after broader framing) |
| Gold standard | TBD | 9 |

---

## DATABASE QUERIES

```sql
-- Get all siblings
SELECT * FROM f990_2025.calc_client_siblings WHERE client_ein = '203472700';

-- Get target grants
SELECT * FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = '203472700' AND is_target_grant = TRUE;

-- Get foundation scores
SELECT * FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = '203472700' ORDER BY gold_standard_grants DESC, target_grants_to_siblings DESC;

-- Get gold standard foundations
SELECT * FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = '203472700' AND gold_standard_grants > 0;
```

---

*Last updated: 2026-01-16 16:45*
