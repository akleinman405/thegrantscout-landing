# pf_revenue_expenses -- Column Reference

**Table:** `f990_2025.pf_revenue_expenses`
**Granularity:** One row per revenue/expense line item from 990-PF Part I
**Total rows:** 1,353,353
**Unique EINs:** 119,229
**Source:** 990-PF Part I XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 1,353,353 | 100.0% | Auto-generated primary key |
| `pf_return_id` | INTEGER | 1,353,353 | 100.0% | FK to pf_returns.id |
| `ein` | VARCHAR | 1,353,353 | 100.0% | Foundation EIN |
| `tax_year` | INTEGER | 1,353,353 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 1,353,353 | 100.0% | When this row was inserted into our DB |

## Line Item Data

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `line_item` | VARCHAR | 1,353,353 | 100.0% | Revenue/expense line item code (e.g., contributions, dividends, comp_officers) |
| `rev_and_expenses_amt` | NUMERIC | 1,176,380 | 86.9% | Revenue and expenses per books amount (Column A) |
| `net_invst_incm_amt` | NUMERIC | 884,652 | 65.4% | Net investment income amount (Column B) |
| `adj_net_incm_amt` | NUMERIC | 296,092 | 21.9% | Adjusted net income amount (Column C) |
| `dsbrs_chrtbl_amt` | NUMERIC | 718,611 | 53.1% | Disbursements for charitable purposes amount (Column D) |
