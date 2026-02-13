# np_balance_sheet -- Column Reference

**Table:** `f990_2025.np_balance_sheet`
**Granularity:** One row per balance sheet line item from 990/990-EZ Part X
**Total rows:** 2,717,584
**Unique EINs:** 333,995
**Source:** 990/990-EZ Part X XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 2,717,584 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 2,717,584 | 100.0% | FK to nonprofit_returns.id |
| `ein` | VARCHAR | 2,717,584 | 100.0% | Employer Identification Number |
| `tax_year` | INTEGER | 2,717,584 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 2,717,584 | 100.0% | When this row was inserted into our DB |

## Balance Sheet Data

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `line_item` | VARCHAR | 2,717,584 | 100.0% | Balance sheet line item code (e.g., cash, investments, payables) |
| `boy_amt` | NUMERIC | 2,491,450 | 91.7% | Beginning-of-year amount |
| `eoy_amt` | NUMERIC | 2,662,598 | 98.0% | End-of-year amount |
