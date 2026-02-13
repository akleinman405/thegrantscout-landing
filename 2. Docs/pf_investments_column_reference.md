# pf_investments -- Column Reference

**Table:** `f990_2025.pf_investments`
**Granularity:** One row per investment holding from 990-PF Part II
**Total rows:** 1,844,771
**Unique EINs:** 69,686
**Source:** 990-PF Part II XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 1,844,771 | 100.0% | Auto-generated primary key |
| `pf_return_id` | INTEGER | 1,844,771 | 100.0% | FK to pf_returns.id |
| `ein` | VARCHAR | 1,844,771 | 100.0% | Foundation EIN |
| `tax_year` | INTEGER | 1,844,771 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 1,844,771 | 100.0% | When this row was inserted into our DB |

## Investment Details

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `investment_type` | VARCHAR | 1,844,771 | 100.0% | Category: corporate_stock, corporate_bond, govt_obligations, land_buildings, etc. |
| `description` | TEXT | 1,844,771 | 100.0% | Description of the specific investment holding |
| `book_value_eoy_amt` | NUMERIC | 1,205,479 | 65.3% | Book value at end of year |
| `fmv_eoy_amt` | NUMERIC | 1,576,595 | 85.5% | Fair market value at end of year |
