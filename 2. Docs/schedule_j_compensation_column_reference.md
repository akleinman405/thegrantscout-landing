# schedule_j_compensation -- Column Reference

**Table:** `f990_2025.schedule_j_compensation`
**Granularity:** One row per highly-compensated person from Schedule J
**Total rows:** 286,308
**Unique EINs:** 71,188
**Source:** 990 Schedule J Part II XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 286,308 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 286,308 | 100.0% | FK to nonprofit_returns.id |
| `ein` | VARCHAR | 286,308 | 100.0% | Employer Identification Number |
| `tax_year` | INTEGER | 286,308 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 286,308 | 100.0% | When this row was inserted into our DB |

## Person Info

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `person_nm` | TEXT | 286,308 | 100.0% | Name of the compensated person |
| `title_txt` | TEXT | 280,373 | 97.9% | Title/position of the compensated person |

## Compensation Breakdown

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `base_compensation_org_amt` | NUMERIC | 272,001 | 95.0% | Base compensation from the filing organization |
| `bonus_filing_org_amt` | NUMERIC | 23,522 | 8.2% | Bonus and incentive compensation from filing org |
| `other_compensation_org_amt` | NUMERIC | 244,280 | 85.3% | Other reportable compensation from filing org |
| `deferred_comp_org_amt` | NUMERIC | 257,807 | 90.0% | Deferred compensation from filing org |
| `nontaxable_benefits_amt` | NUMERIC | 258,807 | 90.4% | Nontaxable benefits (e.g., health insurance, housing) |
| `total_compensation_org_amt` | NUMERIC | 272,142 | 95.1% | Total compensation from the filing organization |
| `comp_reported_related_org_amt` | NUMERIC | 0 | 0% | Compensation reported by related organizations |

---

## Dead Columns (never populated)

These columns exist but have zero data across all 286,308 rows:

- `comp_reported_related_org_amt` -- Compensation reported by related organizations
