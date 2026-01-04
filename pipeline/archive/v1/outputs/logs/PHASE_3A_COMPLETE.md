# Phase 3a: Funder Snapshot SQL - COMPLETE

**Date:** 2025-12-27
**Agent:** Dev Team

## Files Created

- `enrichment/sql/annual_giving.sql` - Total giving in most recent year
- `enrichment/sql/typical_grant.sql` - Median, min, max, avg grant amounts
- `enrichment/sql/geographic_focus.sql` - Top state and in-state percentage
- `enrichment/sql/repeat_funding.sql` - Percentage of repeat recipients
- `enrichment/sql/giving_style.sql` - General support vs program-specific
- `enrichment/sql/recipient_profile.sql` - Typical recipient budget and sector
- `enrichment/sql/funding_trend.sql` - 3-year giving trend
- `enrichment/sql/comparable_grant.sql` - Find similar grants for positioning

## Tests Run

Tested all 8 queries against foundation 200721133 (315,580 grants):

| Metric | Result |
|--------|--------|
| Annual Giving | $225.6M across 58,994 grants (2023) |
| Typical Grant | Median $300, Range $1-$5M |
| Geographic Focus | Top: CA (11.1%), In-state: 9.8% |
| Repeat Funding | 56.5% repeat rate |
| Giving Style | 80.3% general support |
| Funding Trend | Declining (-26.4%) |
| Comparable Grant | YEAR UP INC: $125,000 |

## Database Column Mappings

| Prompt Column | Actual Column |
|---------------|---------------|
| grant_amount | amount |
| grant_year | tax_year |
| grant_purpose | purpose_text |
| recipient_name | recipient_name_raw |

## Ready for Next Phase: Yes

---

*Next: PROMPT_03b (Enrichment Python Wrappers)*
