# schedule_f_grants -- Column Reference

**Table:** `f990_2025.schedule_f_grants`
**Granularity:** One row per foreign grant region from Schedule F Part I
**Total rows:** 81,561
**Unique EINs:** 9,227
**Source:** 990 Schedule F Part I XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 81,561 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 81,561 | 100.0% | FK to nonprofit_returns.id |
| `filer_ein` | VARCHAR | 81,561 | 100.0% | EIN of the granting organization |
| `tax_year` | INTEGER | 81,561 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 81,561 | 100.0% | When this row was inserted into our DB |

## Region Info

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `region` | TEXT | 79,320 | 97.3% | Geographic region of foreign activity (e.g., "Sub-Saharan Africa") |
| `recipient_cnt` | INTEGER | 0 | 0% | Number of recipients in this region |

## Grant Amounts

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `cash_grant_amt` | NUMERIC | 79,636 | 97.6% | Total cash grants to this region |
| `noncash_amt` | NUMERIC | 57,633 | 70.7% | Total non-cash assistance to this region |

## Activity Details

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `manner_of_cash` | TEXT | 70,683 | 86.7% | How cash was disbursed (e.g., wire transfer, check) |
| `activity_desc` | TEXT | 79,404 | 97.4% | Description of activities conducted in this region |

---

## Dead Columns (never populated)

These columns exist but have zero data across all 81,561 rows:

- `recipient_cnt` -- Number of recipients in this region
