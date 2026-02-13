# pf_balance_sheet -- Column Reference

**Table:** `f990_2025.pf_balance_sheet`
**Granularity:** One row per balance sheet line item from 990-PF Part II
**Total rows:** 679,634
**Unique EINs:** 119,229
**Source:** 990-PF Part II XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 679,634 | 100.0% | Auto-generated primary key |
| `pf_return_id` | INTEGER | 679,634 | 100.0% | FK to pf_returns.id |
| `ein` | VARCHAR | 679,634 | 100.0% | Foundation EIN |
| `tax_year` | INTEGER | 679,634 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 679,634 | 100.0% | When this row was inserted into our DB |

## Balance Sheet Data

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `line_item` | VARCHAR | 679,634 | 100.0% | Balance sheet line item code (e.g., cash, investments, payables) |
| `boy_amt` | NUMERIC | 570,413 | 83.9% | Beginning-of-year book value amount |
| `eoy_amt` | NUMERIC | 667,169 | 98.2% | End-of-year book value amount |
| `eoy_fmv_amt` | NUMERIC | 301,234 | 44.3% | End-of-year fair market value amount |
