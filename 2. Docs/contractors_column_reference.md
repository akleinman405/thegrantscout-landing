# contractors -- Column Reference

**Table:** `f990_2025.contractors`
**Granularity:** One row per top contractor (highest-compensated, from 990/990-PF)
**Total rows:** 107,020
**Unique EINs:** 36,053
**Source:** 990 Part VII Section B / 990-PF Part VIII XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 107,020 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 107,020 | 100.0% | FK to nonprofit_returns.id (NULL if from 990-PF) |
| `pf_return_id` | INTEGER | 0 | 0% | FK to pf_returns.id (NULL if from 990/990-EZ) |
| `ein` | VARCHAR | 107,020 | 100.0% | EIN of the filing organization |
| `tax_year` | INTEGER | 107,020 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 107,020 | 100.0% | When this row was inserted into our DB |

## Contractor Info

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `contractor_name` | TEXT | 107,020 | 100.0% | Name of the contractor |
| `contractor_address` | TEXT | 104,334 | 97.5% | Address of the contractor |
| `contractor_state` | VARCHAR | 104,334 | 97.5% | State code of the contractor (2-letter) |

## Service Details

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `service_desc` | TEXT | 106,029 | 99.1% | Description of services provided |
| `compensation_amt` | NUMERIC | 106,224 | 99.3% | Total compensation paid to the contractor |

---

## Dead Columns (never populated)

These columns exist but have zero data across all 107,020 rows:

- `pf_return_id` -- FK to pf_returns.id (NULL if from 990/990-EZ)
