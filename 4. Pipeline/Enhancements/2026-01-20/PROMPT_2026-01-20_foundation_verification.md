# PROMPT: Foundation Candidate Verification for Beta Clients

**Date:** 2026-01-20
**Owner:** Claude Code CLI
**Est. Duration:** 60-90 minutes

---

## Situation Summary

We have 5 beta clients who need foundation matching reports. Phase 1-3 database work is complete. We now need to:
1. Pull the strongest foundation candidates from the database with supporting evidence
2. Create a polished Excel workbook showing WHY each foundation is a good match
3. Verify each foundation via web research (accepts applications, geographic eligibility, etc.)
4. Document all sources used

**Clients:**
| Client | EIN | Open+Target Count | Notes |
|--------|-----|-------------------|-------|
| PSMF | 462730379 | 0 (special case) | 5 already selected in `calc_client_foundation_recommendations` |
| RHF | 952137342 | 51 | Pull top 15 |
| SNS | 953422137 | 27 | Pull top 15 |
| Horizons | 061640692 | 9 | Pull all 9 |
| Friendship Circle | 203472700 | 10 | Pull all 10 |

---

## Phase A: Database Extraction & Excel Creation

### Step A.1: Pull Foundation Candidates

For each client (except PSMF), run this query to get top candidates:

```sql
WITH latest_pf AS (
    SELECT DISTINCT ON (ein)
        ein,
        only_contri_to_preselected_ind,
        total_assets_eoy_amt as pf_assets,
        website_url
    FROM f990_2025.pf_returns
    ORDER BY ein, tax_year DESC
),
foundation_geo AS (
    SELECT 
        foundation_ein,
        array_agg(DISTINCT recipient_state ORDER BY recipient_state) as funded_states,
        COUNT(DISTINCT recipient_state) as state_count
    FROM f990_2025.fact_grants
    WHERE recipient_state IS NOT NULL 
      AND LENGTH(recipient_state) = 2
    GROUP BY foundation_ein
),
foundation_stats AS (
    SELECT
        foundation_ein,
        COUNT(*) as total_grants,
        SUM(amount) as total_giving,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median_grant,
        MIN(amount) as min_grant,
        MAX(amount) as max_grant,
        MAX(tax_year) as most_recent_year
    FROM f990_2025.fact_grants
    WHERE amount > 0
    GROUP BY foundation_ein
)
SELECT
    cfs.foundation_ein,
    cfs.foundation_name,
    cfs.foundation_state,
    COALESCE(lp.pf_assets, cfs.foundation_total_assets) as assets,
    cfs.target_grants_to_siblings,
    cfs.total_grants_to_siblings,
    cfs.gold_standard_grants,
    COALESCE(lp.only_contri_to_preselected_ind, FALSE) as irs_invite_only,
    lp.website_url,
    fg.funded_states,
    fg.state_count as states_funded_count,
    fs.total_grants as all_time_grants,
    fs.total_giving as all_time_giving,
    fs.median_grant,
    fs.min_grant,
    fs.max_grant,
    fs.most_recent_year
FROM f990_2025.calc_client_foundation_scores cfs
LEFT JOIN latest_pf lp ON lp.ein = cfs.foundation_ein
LEFT JOIN foundation_geo fg ON fg.foundation_ein = cfs.foundation_ein
LEFT JOIN foundation_stats fs ON fs.foundation_ein = cfs.foundation_ein
WHERE cfs.client_ein = '{CLIENT_EIN}'
  AND cfs.target_grants_to_siblings > 0
  AND COALESCE(lp.only_contri_to_preselected_ind, FALSE) = FALSE
ORDER BY cfs.gold_standard_grants DESC, cfs.target_grants_to_siblings DESC, fs.median_grant DESC
LIMIT 15;
```

For PSMF, pull from existing recommendations:
```sql
SELECT * FROM f990_2025.calc_client_foundation_recommendations
WHERE client_ein = '462730379';
```

### Step A.2: Pull Target Grant Examples

For each foundation candidate, pull 3-5 target grants as proof of fit:

```sql
SELECT
    g.foundation_ein,
    df.name as foundation_name,
    g.sibling_ein as recipient_ein,
    dr.name as recipient_name,
    g.recipient_state,
    g.amount,
    g.purpose_text,
    g.tax_year,
    g.semantic_similarity,
    g.keyword_match
FROM f990_2025.calc_client_sibling_grants g
JOIN f990_2025.dim_foundations df ON df.ein = g.foundation_ein
JOIN f990_2025.dim_recipients dr ON dr.ein = g.sibling_ein
WHERE g.client_ein = '{CLIENT_EIN}'
  AND g.foundation_ein = '{FOUNDATION_EIN}'
  AND g.is_target_grant = TRUE
ORDER BY g.semantic_similarity DESC, g.amount DESC
LIMIT 5;
```

### Step A.3: Create Excel Workbook

**File:** `EXCEL_2026-01-20_foundation_candidates.xlsx`

**Structure:**
- Tab 1: `Summary` - All clients, top 5 foundations each, key metrics
- Tab 2: `RHF` - All 15 candidates with full details
- Tab 3: `SNS` - All 15 candidates with full details
- Tab 4: `Horizons` - All 9 candidates with full details
- Tab 5: `Friendship Circle` - All 10 candidates with full details
- Tab 6: `PSMF` - Existing 5 selections with full details
- Tab 7: `Target Grant Examples` - All proof-of-fit grants by foundation

**Columns for client tabs:**

| Column | Description |
|--------|-------------|
| A: Foundation Name | From database |
| B: EIN | 9-digit |
| C: State | Foundation HQ state |
| D: Assets | Most recent from 990-PF |
| E: Target Grants | Count of grants matching client's work |
| F: Gold Standard | Target + first-time + geography match |
| G: Total Grants to Siblings | All grants to similar nonprofits |
| H: Median Grant | Typical grant size |
| I: Grant Range | Min - Max |
| J: States Funded | Top 3-5 states they give to |
| K: Most Recent Grant | Year |
| L: IRS Open | TRUE/FALSE from 990-PF |
| M: Website | From 990-PF if available |
| N: Sample Grant 1 | "Recipient: $Amount for Purpose (Year)" |
| O: Sample Grant 2 | Same format |
| P: Sample Grant 3 | Same format |
| Q: Verification Status | (blank - filled in Phase B) |
| R: Verification Notes | (blank - filled in Phase B) |

**Formatting:**
- Header row: Bold, freeze panes
- Currency columns: Format as currency
- Conditional formatting: Green for Gold Standard > 0, Yellow for IRS Open = FALSE
- Column widths: Auto-fit with max 50 for text columns
- Add data validation dropdowns for Verification Status (Verified Open, Invite Only, Needs Review)

---

## Phase B: Web Verification

### Step B.1: Research Each Foundation

For each foundation in the Excel (approximately 50-55 total), search the web to answer:

1. **Accepts Applications?** 
   - Search: "{Foundation Name} grant application" or "{Foundation Name} how to apply"
   - Look for: Application forms, LOI instructions, "by invitation only" language
   - Answer: Yes / No / Unclear

2. **Geographic Restrictions?**
   - Search: "{Foundation Name} grant guidelines" or "{Foundation Name} eligibility"
   - Look for: State/region restrictions, "local" language
   - Answer: List specific restrictions or "None stated"

3. **Focus Areas Match Client?**
   - Search: "{Foundation Name} funding priorities" or "{Foundation Name} what we fund"
   - Look for: Program areas, populations served
   - Answer: Strong match / Partial match / Weak match

4. **Eligibility Requirements?**
   - Look for: Budget minimums, years in operation, 501c3 requirement, other
   - Note anything that might disqualify the client

5. **Application Process?**
   - Deadlines, LOI vs full application, online portal, contact info
   - Note for action plan in report

### Step B.2: Document All Sources

For EVERY claim made, record the URL. Create a sources table:

| Foundation | Claim | URL | Date Accessed |
|------------|-------|-----|---------------|
| Example Foundation | Accepts applications via online portal | https://example.org/grants | 2026-01-20 |
| Example Foundation | Focus: education and youth development | https://example.org/about | 2026-01-20 |

### Step B.3: Update Excel

Add verification results to columns Q and R in each client tab.

---

## Outputs

### Output 1: Excel Workbook
**File:** `/mnt/user-data/outputs/EXCEL_2026-01-20_foundation_candidates.xlsx`

Must include:
- All tabs as specified
- Professional formatting
- Target grant examples as proof of fit
- Verification status and notes columns populated

### Output 2: Verification Report
**File:** `/mnt/user-data/outputs/REPORT_2026-01-20_foundation_verification.md`

Structure:
```markdown
# Foundation Verification Report

**Date:** 2026-01-20
**Clients:** PSMF, RHF, SNS, Horizons, Friendship Circle

## Summary

| Client | Candidates Reviewed | Verified Open | Invite Only | Unclear |
|--------|---------------------|---------------|-------------|---------|
| ... | ... | ... | ... | ... |

## Client: RHF

### Foundation 1: [Name]
- **EIN:** 
- **Accepts Applications:** Yes/No
- **Geographic Focus:** 
- **Focus Areas:** 
- **Eligibility Requirements:** 
- **Application Process:** 
- **Recommendation:** Include / Exclude / Tier B
- **Sources:**
  - [URL 1]
  - [URL 2]

### Foundation 2: [Name]
...

## Client: SNS
...

## Client: Horizons
...

## Client: Friendship Circle
...

## Client: PSMF
...

## All Sources

[Complete URL list with foundation and claim]
```

---

## Quality Checks

Before completing, verify:
- [ ] Excel has all 7 tabs with correct structure
- [ ] Every foundation has at least 2 target grant examples
- [ ] Web verification completed for all foundations
- [ ] Every verification claim has a source URL
- [ ] Verification Status column populated for all rows
- [ ] Report includes all sources used
- [ ] Files saved to `/mnt/user-data/outputs/`

---

## Notes

- Use the f990_2025 schema exclusively
- Client EINs: PSMF=462730379, RHF=952137342, SNS=953422137, Horizons=061640692, Friendship Circle=203472700
- If a foundation website cannot be found, note "No website found" and flag for manual review
- Prioritize foundations with Gold Standard grants > 0
- For PSMF, the 5 foundations are already selected - just verify and gather metrics

---

*Prompt created 2026-01-20*
