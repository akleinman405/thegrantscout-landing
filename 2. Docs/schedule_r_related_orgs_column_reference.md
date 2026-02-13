# schedule_r_related_orgs -- Column Reference

**Table:** `f990_2025.schedule_r_related_orgs`
**Granularity:** One row per related organization from Schedule R
**Total rows:** 850,773
**Unique EINs:** 72,098
**Source:** 990 Schedule R XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 850,773 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 850,773 | 100.0% | FK to nonprofit_returns.id |
| `filer_ein` | VARCHAR | 850,773 | 100.0% | EIN of the filing organization |
| `tax_year` | INTEGER | 850,773 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 850,773 | 100.0% | When this row was inserted into our DB |

## Related Org Identity

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `schedule_part` | VARCHAR | 850,773 | 100.0% | Which part of Schedule R (II, III, or IV) |
| `related_org_name` | TEXT | 850,769 | 100.0% | Name of the related organization |
| `related_org_ein` | VARCHAR | 811,636 | 95.4% | EIN of the related organization |
| `related_org_state` | VARCHAR | 823,251 | 96.8% | State code of the related organization |

## Relationship Details

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `exempt_code_section` | TEXT | 535,342 | 62.9% | IRC exempt code section of related org |
| `public_charity_status` | TEXT | 493,579 | 58.0% | Public charity status of related org |
| `direct_controlling_name` | TEXT | 417,385 | 49.1% | Name of directly controlling entity |
| `relationship_type` | TEXT | 263,253 | 30.9% | Type of relationship (e.g., parent, subsidiary) |
