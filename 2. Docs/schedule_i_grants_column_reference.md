# schedule_i_grants -- Column Reference

**Table:** `f990_2025.schedule_i_grants`
**Granularity:** One row per grant from 990 Schedule I (grants to domestic orgs/individuals)
**Total rows:** 996,940
**Unique EINs:** 48,069
**Source:** 990/990-EZ Schedule I XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 996,940 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 996,940 | 100.0% | FK to nonprofit_returns.id |
| `filer_ein` | VARCHAR | 996,940 | 100.0% | EIN of the granting organization |
| `tax_year` | INTEGER | 996,940 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 996,940 | 100.0% | When this row was inserted into our DB |

## Recipient Info

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `recipient_ein` | VARCHAR | 935,772 | 93.9% | EIN of the grant recipient (if available) |
| `recipient_name` | TEXT | 996,776 | 100.0% | Name of the grant recipient |
| `recipient_city` | TEXT | 982,341 | 98.5% | City of the grant recipient |
| `recipient_state` | VARCHAR | 982,341 | 98.5% | State code of the grant recipient (2-letter) |
| `recipient_zip` | VARCHAR | 982,341 | 98.5% | ZIP code of the grant recipient |

## Grant Details

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `irc_section` | TEXT | 878,576 | 88.1% | IRC section under which recipient is exempt (e.g., 501(c)(3)) |
| `amount` | NUMERIC | 986,277 | 98.9% | Cash grant amount in dollars |
| `noncash_amount` | NUMERIC | 623,509 | 62.5% | Non-cash assistance amount in dollars |
| `purpose` | TEXT | 963,023 | 96.6% | Purpose or description of the grant |
| `grant_type` | TEXT | 0 | 0% | Type of grant (e.g., cash, non-cash) |

---

## Dead Columns (never populated)

These columns exist but have zero data across all 996,940 rows:

- `grant_type` -- Type of grant (e.g., cash, non-cash)
