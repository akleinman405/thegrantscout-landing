# schedule_a -- Column Reference

**Table:** `f990_2025.schedule_a`
**Granularity:** One row per 990 filing (public charity status and support test)
**Total rows:** 574,037
**Unique EINs:** 527,952
**Source:** 990 Schedule A XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 574,037 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 574,037 | 100.0% | FK to nonprofit_returns.id |
| `ein` | VARCHAR | 574,037 | 100.0% | Employer Identification Number |
| `tax_year` | INTEGER | 574,037 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 574,037 | 100.0% | When this row was inserted into our DB |

## Organization Type

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `church_ind` | BOOLEAN | 574,037 | 100.0% | Organization is a church (170(b)(1)(A)(i)) |
| `school_ind` | BOOLEAN | 574,037 | 100.0% | Organization is a school (170(b)(1)(A)(ii)) |
| `hospital_ind` | BOOLEAN | 574,037 | 100.0% | Organization is a hospital (170(b)(1)(A)(iii)) |
| `medical_research_org_ind` | BOOLEAN | 360,191 | 62.7% | Medical research org (170(b)(1)(A)(iii)) |
| `college_org_ind` | BOOLEAN | 360,191 | 62.7% | College/university support org (170(b)(1)(A)(iv)) |
| `governmental_unit_ind` | BOOLEAN | 360,191 | 62.7% | Governmental unit (170(b)(1)(A)(v)) |
| `public_safety_org_ind` | BOOLEAN | 360,191 | 62.7% | Public safety testing org (509(a)(4)) |
| `community_trust_ind` | BOOLEAN | 360,191 | 62.7% | Community trust (170(b)(1)(A)(vi)) |

## Public Charity Status

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `public_charity_509a1_ind` | BOOLEAN | 574,037 | 100.0% | Publicly supported charity under 509(a)(1) |
| `public_charity_509a2_ind` | BOOLEAN | 574,037 | 100.0% | Publicly supported charity under 509(a)(2) |
| `supporting_org_509a3_ind` | BOOLEAN | 360,191 | 62.7% | Supporting organization under 509(a)(3) |
| `supporting_org_type1_ind` | BOOLEAN | 360,191 | 62.7% | Supporting org Type I (operated/supervised by) |
| `supporting_org_type2_ind` | BOOLEAN | 360,191 | 62.7% | Supporting org Type II (supervised/controlled with) |
| `supporting_org_type3_func_int_ind` | BOOLEAN | 360,191 | 62.7% | Supporting org Type III functionally integrated |
| `supporting_org_type3_non_func_int_ind` | BOOLEAN | 360,191 | 62.7% | Supporting org Type III non-functionally integrated |

## Public Support Test

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `public_support_cy170_pct` | NUMERIC | 133,576 | 23.3% | Public support percentage (170 test, current year) |
| `public_support_total_amt` | NUMERIC | 128,294 | 22.3% | Total public support amount |
