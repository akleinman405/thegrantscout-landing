# PROMPT: Find Whittier Trust Managed Foundations

**Date:** 2025-12-17  
**For:** Claude Code CLI  
**Database:** PostgreSQL, schema `f990_2025`

---

## Standards

**FIRST:** Review `CLAUDE.md` for project conventions before starting.

**Output location:** Save all outputs in the same folder as this prompt.

---

## Situation

Whittier Trust Company is a multi-family office that manages ~50-140 private foundations for wealthy families. They handle back-office admin (bookkeeping, grant agreements, compliance) while families focus on grantmaking.

We had a call with Pegine Grayson (Director of Philanthropic Services, retiring Dec 2025) who referred us to Jesse Ostroff. Before following up, we want to know which foundations Whittier manages — these are potential B2B targets.

**Key insight:** Foundations managed by Whittier often use Whittier's address as their mailing address on 990 filings.

---

## Whittier Trust Addresses to Search

**Primary (Pasadena HQ):**
- 177 E Colorado Blvd, Pasadena, CA 91105
- 177 East Colorado Boulevard
- Variations: "E Colorado", "E. Colorado", "East Colorado"
- Suite 500 or Suite 800

**Other offices (secondary search):**
- Newport Beach, CA
- San Francisco, CA  
- Menlo Park, CA
- Reno, NV
- Seattle, WA
- Portland, OR

---

## Tasks

### 1. Search by Address

Query foundations with addresses matching Whittier Trust locations:

```sql
-- Example approach - adjust based on actual schema
SELECT DISTINCT 
    foundation_ein,
    foundation_name,
    address_line_1,
    city,
    state,
    -- other relevant fields
FROM f990_2025.dim_foundations  -- or appropriate table
WHERE 
    LOWER(address_line_1) LIKE '%177%colorado%'
    OR LOWER(address_line_1) LIKE '%whittier%trust%'
ORDER BY foundation_name;
```

### 2. Search by Officer/Trustee Names

Look for Whittier Trust staff listed as officers on foundation 990s:

```sql
-- Search for known Whittier staff as foundation officers
WHERE officer_name ILIKE '%Pegine%Grayson%'
   OR officer_name ILIKE '%Jesse%Ostroff%'
   OR officer_name ILIKE '%Haley%Kirk%'
   OR officer_name ILIKE '%Whittier%Trust%'
```

### 3. Search by Known Foundation

We already know Ann Peppers Foundation is managed by Whittier. Use it to validate the search approach:
- EIN: 952114455
- Check what address is on file
- Use pattern to find similar foundations

### 4. For Each Foundation Found

Pull:
- Foundation name
- EIN
- Address on file
- Total assets (most recent year)
- Total grants paid (most recent year)
- Number of grantees (if available)
- Officers listed
- Tax year of filing

### 5. Cross-Reference with Our Foundation List

Check if any Whittier-managed foundations appear in:
- `DATA_2025-12-17_100_foundations_to_research.csv`
- `TABLE_2025-12-17_foundation_contacts_100.csv`

---

## Output

**File:** `REPORT_2025-12-17_whittier_trust_foundations.md`

### Sections:

**1. Summary**
- Total foundations found managed by Whittier Trust
- Total combined assets
- Total annual grantmaking

**2. Foundation List**

| Foundation Name | EIN | Assets | Annual Grants | Grantees | Address Match |
|-----------------|-----|--------|---------------|----------|---------------|

**3. Top Foundations by Assets**
Top 10 largest foundations managed by Whittier

**4. Top Foundations by Grantmaking**
Top 10 most active grantmakers

**5. Overlap with Our Target List**
Any foundations we already have on our outreach list

**6. Methodology Notes**
- Which address patterns matched
- Any limitations (missing data, old filings, etc.)
- Confidence level in the results

---

## Also Create CSV

**File:** `DATA_2025-12-17_whittier_trust_foundations.csv`

Columns:
```
foundation_name,ein,assets,annual_grants,grantee_count,address,city,state,tax_year,officers
```

---

## Notes

- Some foundations may use a family address, not Whittier's — we won't catch those
- Look for patterns: multiple foundations at same address = likely managed together
- If address search yields few results, try officer name search
- The Ann Peppers Foundation (EIN 952114455) is a known Whittier client — use as validation
