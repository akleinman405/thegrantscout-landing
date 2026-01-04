# Lessons Learned: Additional Prospect Flags

**Date:** 2025-12-11
**Task:** Add 5 new flags to prospects table for outreach targeting

---

## 1. What Worked Well

### Efficient Approach for Large Tables
- The officers table has 18.3 million rows - direct LIKE queries were too slow
- Using `INNER JOIN` to prospects first, then filtering, reduced query time from timeout to ~5 minutes
- CTE (WITH clause) approach cleaner than subqueries for multi-step updates

### Flag Design Decisions
- Using SMALLINT (0/1) instead of BOOLEAN for most flags - easier for SUM aggregations
- Three-value `has_biz_dev_staff` (yes/no/uncertain) captures nuance when officer data is missing
- Converting text field (`beta_client_connection`) to binary flag simplifies filtering while preserving original data

### Fiscal Year Logic
- Simplified to month-based logic (Dec/Jan) rather than exact day calculations
- 57% of prospects have Dec/Jan FY ends - good for year-end campaign timing
- Could extend to include Feb for "60-day" window if needed

---

## 2. What Was Harder Than Expected

### Officers Table Scale
- 18,362,896 rows made simple LIKE queries impractical
- No index on `title_txt` column - full table scans required
- Solution: Filter to relevant EINs first via JOIN, then apply title matching

### Development Title Matching
- Many variations: "Director of Development", "VP Development", "Development Officer"
- Had to be careful with `%develop%` - catches "software develop" (false positive)
- Could improve with more specific patterns or title standardization

### Understanding the Fundraising Score Scope
- `likely_active_fundraiser` only meaningful for prime prospects (642)
- Set to 0 for all 73,928 non-prime prospects since score wasn't calculated for them
- This is correct behavior but worth documenting

---

## 3. What I Wish I Knew Going In

### Table Relationships
1. `prospects` is a materialized view/snapshot - safe to add columns
2. `officers` table covers both 990 and 990-PF filers - larger than expected
3. Fiscal year data requires JOIN to `nonprofit_returns` table

### Data Quirks
1. `beta_client_connection` contains "Same state as beta clients" for 16K+ records - not actually a shared funder
2. Should potentially filter out state-only matches for `shares_funder_with_beta`
3. Many officers with truncated titles (e.g., "EXECUTIVE DI", "VICE PRESIDE")

### Performance Tips
- Always check table sizes before writing queries
- Use `EXPLAIN ANALYZE` in psycopg2 for query optimization
- Background process tracking helps for long-running queries

---

## 4. Recommendations for Future

### Index Recommendations
If officer title queries become common, consider:
```sql
CREATE INDEX idx_officers_title_lower
ON f990_2025.officers (LOWER(title_txt));
```

### Flag Improvements
1. **Refine `shares_funder_with_beta`** - exclude "Same state" matches:
   ```sql
   WHERE beta_client_connection LIKE 'Shares%funder%'
   ```

2. **Add development keywords** - Consider:
   - "annual giving"
   - "planned giving"
   - "stewardship"
   - "resource development"

3. **Time-based fiscal_year_end_soon** - Make dynamic:
   ```sql
   -- Calculate based on current date, not hardcoded months
   WHERE EXTRACT(MONTH FROM tax_period_end) IN (
       EXTRACT(MONTH FROM CURRENT_DATE),
       EXTRACT(MONTH FROM CURRENT_DATE + INTERVAL '1 month'),
       EXTRACT(MONTH FROM CURRENT_DATE + INTERVAL '2 months')
   )
   ```

### Targeting Suggestions
1. **Start with multi-flag prospects** - Those hitting 3+ flags are best candidates
2. **Segment by employee count** - Small orgs (1-10) likely need help most
3. **Use "no biz dev" as pain point** - These orgs lack dedicated fundraising capacity

---

## 5. Technical Notes

### Connection Pattern
```python
import psycopg2
conn = psycopg2.connect(
    host='172.26.16.1',
    port=5432,
    database='postgres',
    user='postgres',
    password='kmalec21'
)
```

### Columns Added to prospects Table
| Column | Type | Default |
|--------|------|---------|
| likely_active_fundraiser | SMALLINT | 0 |
| fiscal_year_end_soon | SMALLINT | 0 |
| has_biz_dev_staff | VARCHAR(10) | 'uncertain' |
| new_to_foundations | SMALLINT | 0 |
| shares_funder_with_beta | SMALLINT | 0 |

### Query Timing
- Flag 1 (likely_active_fundraiser): <1 second
- Flag 2 (fiscal_year_end_soon): ~30 seconds
- Flag 3 (has_biz_dev_staff): ~5 minutes (due to officers table)
- Flag 4 (new_to_foundations): <1 second
- Flag 5 (shares_funder_with_beta): <1 second

---

## 6. Success Criteria Assessment

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| All 5 columns added | Yes | Yes | MET |
| Summary stats for each flag | Yes | Yes | MET |
| Cross-tab showing overlap | Yes | Yes | MET |
| Count of prime prospects with flags | Yes | Yes | MET |
| Report file created | Yes | Yes | MET |
| Lessons learned file created | Yes | Yes | MET |

---

*Lessons documented: 2025-12-11*
