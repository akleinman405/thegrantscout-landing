# Claude Code CLI Prompt
## Generate Targeted Prospect Call List

---

## Context & Goal

**Situation:** We've built 16+ flags on our prospects table (74,144 nonprofits). Based on call data analysis, we know Sector E/P + Revenue $1-2M predicts success. We also want to target orgs without dedicated development staff (they need our help), with concrete missions, and signs of active fundraising need.

**Goal:** Generate a CSV call list of prospects matching our ideal criteria, enriched with contact info for cold calling.

**Database:** PostgreSQL, schema `f990_2025`, Windows machine, Python/psycopg2.

---

## Output Requirements

1. **All outputs in same folder as this prompt**
2. **Use naming convention:** DOCTYPE_YYYY-MM-DD_description.ext
3. **Required deliverables:**
   - `DATA_2025-12-12_prospect_call_list.csv` — The call list
   - `REPORT_2025-12-12_prospect_call_list.md` — Summary of what was pulled
   - `LESSONS_2025-12-12_prospect_call_list.md` — What you learned

---

## Filter Criteria

Pull prospects matching ALL of these:

| Criterion | Column/Logic |
|-----------|--------------|
| No biz dev staff | `has_biz_dev_staff = 'no'` |
| 0-3 employees | `employee_count BETWEEN 0 AND 3` |
| Sector E or P | `sector IN ('E', 'P')` |
| Revenue $1M-$2M | `total_revenue BETWEEN 1000000 AND 2000000` |
| Likely active fundraiser | `likely_active_fundraiser = 1` |
| 0-3 foundation funders | `num_unique_funders <= 3` OR `num_foundation_grants <= 3` |
| High grant dependency | `grant_dependency_pct >= 75` |
| Stagnant/declining YoY | `yoy_revenue_growth <= 10` (flat or declining) |
| Has website | `website IS NOT NULL AND website != ''` |
| Concrete mission | `has_concrete_mission = 1` |

---

## SQL Query

```sql
-- Step 1: Get matching prospects
SELECT 
    p.ein,
    p.org_name,
    p.city,
    p.state,
    p.zip,
    p.website,
    p.phone,
    p.mission_statement,
    p.sector,
    p.employee_count,
    p.total_revenue,
    p.grant_dependency_pct,
    p.yoy_revenue_growth,
    p.num_foundation_grants,
    p.num_unique_funders,
    p.icp_score,
    p.fundraising_likelihood_score
FROM f990_2025.prospects p
WHERE p.has_biz_dev_staff = 'no'
  AND p.employee_count BETWEEN 0 AND 3
  AND p.sector IN ('E', 'P')
  AND p.total_revenue BETWEEN 1000000 AND 2000000
  AND p.likely_active_fundraiser = 1
  AND (p.num_unique_funders <= 3 OR p.num_foundation_grants <= 3)
  AND p.grant_dependency_pct >= 75
  AND (p.yoy_revenue_growth <= 10 OR p.yoy_revenue_growth IS NULL)
  AND p.website IS NOT NULL AND p.website != ''
  AND p.has_concrete_mission = 1
ORDER BY p.icp_score DESC, p.fundraising_likelihood_score DESC;
```

---

## Step 2: Enrich with Officer/Contact Info

Get CEO/Executive Director/Founder from officers table:

```sql
-- Find the top officer for each prospect
SELECT 
    o.ein,
    o.person_name,
    o.title_txt
FROM f990_2025.officers o
WHERE o.ein IN ([LIST_OF_EINS_FROM_STEP_1])
  AND (
    LOWER(o.title_txt) LIKE '%executive director%'
    OR LOWER(o.title_txt) LIKE '%ceo%'
    OR LOWER(o.title_txt) LIKE '%chief executive%'
    OR LOWER(o.title_txt) LIKE '%president%'
    OR LOWER(o.title_txt) LIKE '%founder%'
    OR LOWER(o.title_txt) LIKE '%director%'
  )
ORDER BY 
    CASE 
        WHEN LOWER(o.title_txt) LIKE '%ceo%' THEN 1
        WHEN LOWER(o.title_txt) LIKE '%chief executive%' THEN 2
        WHEN LOWER(o.title_txt) LIKE '%executive director%' THEN 3
        WHEN LOWER(o.title_txt) LIKE '%founder%' THEN 4
        WHEN LOWER(o.title_txt) LIKE '%president%' THEN 5
        ELSE 6
    END;
```

Then join to get one contact per org (take the highest-ranked title).

---

## Step 3: Build Final CSV

Combine prospect data + officer contact into final CSV with these columns:

| Column | Source |
|--------|--------|
| ein | prospects |
| org_name | prospects |
| city | prospects |
| state | prospects |
| zip | prospects |
| phone | prospects |
| website | prospects |
| mission_statement | prospects |
| contact_name | officers (CEO/ED/Founder) |
| contact_title | officers |
| sector | prospects |
| employee_count | prospects |
| total_revenue | prospects |
| grant_dependency_pct | prospects |
| yoy_revenue_growth | prospects |
| num_foundation_grants | prospects |
| icp_score | prospects |
| fundraising_likelihood_score | prospects |

---

## Step 4: Handle Edge Cases

1. **No phone number:** Leave blank, note in report how many are missing
2. **No officer found:** Leave contact_name/contact_title blank
3. **Multiple officers match:** Take highest priority title (CEO > ED > President > Founder)
4. **Mission too long:** Truncate to 500 chars for CSV readability

---

## Step 5: If Count is Too Low

If the strict criteria return <20 prospects, try relaxing in this order:

1. First: Remove `yoy_revenue_growth <= 10` filter
2. Second: Expand to `employee_count BETWEEN 0 AND 10`
3. Third: Expand revenue to `BETWEEN 500000 AND 3500000`
4. Fourth: Remove `likely_active_fundraiser = 1`

Document which filters were relaxed and final count.

---

---

## Deliverables

### DATA_2025-12-12_prospect_call_list.csv

CSV with all columns listed above, sorted by priority.

### REPORT_2025-12-12_prospect_call_list.md

1. **Total prospects matching criteria**
2. **Filter summary** — Which criteria were applied, any relaxed?
3. **Missing data summary:**
   - How many missing phone?
   - How many missing contact name?
   - How many missing mission?
4. **Distribution:**
   - By state
   - By sector (E vs P)
   - By ICP score
5. **Top 10 preview** — Show first 10 rows as sample
6. **Recommendations** — Any observations about the list?

### LESSONS_2025-12-12_prospect_call_list.md

1. What worked well?
2. What was harder than expected?
3. What do you wish you knew going in?
4. Any data quality issues discovered?

---

## Success Criteria

- [ ] CSV generated with all required columns
- [ ] Contact name populated for majority of records
- [ ] Phone populated where available
- [ ] Report documents filter logic and data quality
- [ ] Lessons learned file created

---

*Prompt: PROMPT_2025-12-12_prospect_call_list.md*
