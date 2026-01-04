# Lessons Learned: Prospects Table Build Session
## 2025-12-10

---

## Session Overview

Built the `f990_2025.prospects` table from scratch, populated it with 74,144 qualifying nonprofits, calculated ICP scores, and added reachability flags.

---

## What Worked Well

### 1. Schema Exploration First
- Started by listing all tables in the schema before writing any INSERT queries
- Discovered that `nonprofit_returns` had NULL NTEE codes, but `irs_bmf` had them
- This prevented a broken query and wasted time

### 2. Incremental Approach
- Added columns, then populated, then calculated derived fields
- Each step was verifiable before moving to the next
- Made debugging straightforward

### 3. Source Table Documentation
- Documented which tables were used as sources
- Important for reproducibility and future maintenance:
  - `nonprofit_returns` → base nonprofit data
  - `irs_bmf` → NTEE codes
  - `pf_grants` → foundation grant history

### 4. Using Python + psycopg2 vs psql
- `psql` wasn't available in the WSL2 environment
- Python with psycopg2 worked seamlessly
- Allowed for programmatic report generation

---

## Data Quality Insights

### NTEE Code Gaps
- 20.6% of prospects have no NTEE code (blank in irs_bmf)
- 1.7% have NULL sector
- **Implication:** Can't rely solely on sector-based filtering

### Reachability Flag Results
- `reach_form_990` = 100% (all prospects file Form 990 by definition of our inclusion criteria)
- This flag is redundant—could be removed
- Only 290 prospects (0.4%) meet ALL reachability criteria
- Most restrictive filter: `reach_sector_e_p` at 18.7%

### Foundation Grant Coverage
- 57.9% of prospects have at least one foundation grant in our database
- This is higher than expected—good for relationship-based outreach

---

## Schema Design Notes

### What Could Be Improved

1. **Redundant Columns**
   - `reach_form_990` is always 1 given our inclusion criteria
   - Could be removed to simplify

2. **Denormalization Trade-offs**
   - We stored derived values (revenue_band, grant_dep_band) directly
   - Pros: Fast queries, simple reporting
   - Cons: Must remember to recalculate if source data updates

3. **Beta Client Connection String**
   - Currently stores free text ("Shares 3 funder(s) with PSMF")
   - Could be normalized to a separate junction table for more complex analysis

### Indexes Created
- `idx_prospects_score` (icp_score DESC)
- `idx_prospects_tier` (priority_tier)
- `idx_prospects_status` (outreach_status)
- `idx_prospects_state` (state)
- `idx_prospects_sector` (sector)

These cover the most common query patterns for outreach workflows.

---

## Key Statistics to Remember

| Metric | Value |
|--------|-------|
| Total prospects | 74,144 |
| Tier 1 (ICP ≥10) | 6,862 (9.3%) |
| Tier 2 (ICP 6-9) | 51,134 (69.0%) |
| Tier 3 (ICP <6) | 16,148 (21.8%) |
| With all reach flags | 290 (0.4%) |
| With beta connections | 20,362 (27.5%) |
| Max ICP score possible | 12 |
| Max ICP score achieved | 12 (377 prospects) |

---

## Recommendations for Next Steps

1. **Remove `reach_form_990`** - It's always 1, provides no discriminatory value

2. **Consider loosening reachability criteria** - Only 290 prospects meet all 6 flags; perhaps require 4 or 5 instead

3. **Enrich contact data** - The `contact_email`, `contact_phone` fields are empty; external enrichment needed

4. **Add index on `reach_all_flags`** for fast filtering:
   ```sql
   CREATE INDEX idx_prospects_reachable ON f990_2025.prospects(reach_all_flags) WHERE reach_all_flags = 1;
   ```

5. **Automate updates** - If nonprofit_returns data refreshes, the prospects table needs recalculation

---

## Files Created This Session

| File | Purpose |
|------|---------|
| `REPORT_2025-12-10_prospects_table_summary.md` | Full summary of prospects table build |
| `OUTPUT_2025-12-10_prospects_table_ddl.sql` | SQL DDL for table creation |
| `REPORT_2025-12-10_reachability_flags_summary.md` | Reachability flag analysis |
| `LESSONS_2025-12-10_prospects_table_session.md` | This file |

---

*Session completed: 2025-12-10*
