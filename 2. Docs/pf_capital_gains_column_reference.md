# pf_capital_gains -- Column Reference

**Table:** `f990_2025.pf_capital_gains`
**Granularity:** One row per capital gain/loss line item from 990-PF Part IV
**Total rows:** 3,740,163
**Unique EINs:** 66,848
**Source:** 990-PF Part IV XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 3,740,163 | 100.0% | Auto-generated primary key |
| `pf_return_id` | INTEGER | 3,740,163 | 100.0% | FK to pf_returns.id |
| `ein` | VARCHAR | 3,740,163 | 100.0% | Foundation EIN |
| `tax_year` | INTEGER | 3,740,163 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 3,740,163 | 100.0% | When this row was inserted into our DB |

## Property Details

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `property_desc` | TEXT | 3,739,535 | 100.0% | Description of the property sold (e.g., stock name, real estate) |
| `how_acquired_cd` | VARCHAR | 1,947,758 | 52.1% | How property was acquired: P=Purchase, D=Donation |
| `date_acquired` | DATE | 1,963,624 | 52.5% | Date property was acquired |
| `date_sold` | DATE | 2,119,296 | 56.7% | Date property was sold |

## Financial

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `gross_sales_price_amt` | NUMERIC | 2,182,134 | 58.3% | Gross sales price of the property |
| `cost_or_other_basis_amt` | NUMERIC | 2,153,409 | 57.6% | Cost or other basis of the property |
| `gain_or_loss_amt` | NUMERIC | 3,629,630 | 97.0% | Net capital gain or loss (sales price minus basis) |
