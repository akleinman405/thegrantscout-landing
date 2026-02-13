# schedule_o_narratives -- Column Reference

**Table:** `f990_2025.schedule_o_narratives`
**Granularity:** One row per supplemental explanation from Schedule O
**Total rows:** 2,950,168
**Unique EINs:** 515,642
**Source:** 990/990-EZ Schedule O XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 2,950,168 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 2,950,168 | 100.0% | FK to nonprofit_returns.id |
| `ein` | VARCHAR | 2,950,168 | 100.0% | Employer Identification Number |
| `tax_year` | INTEGER | 2,950,168 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 2,950,168 | 100.0% | When this row was inserted into our DB |

## Narrative Content

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `form_and_line_ref` | TEXT | 2,950,168 | 100.0% | Form and line number this explanation refers to (e.g., "Form 990, Part III, Line 4d") |
| `explanation_txt` | TEXT | 2,950,168 | 100.0% | Full text of the supplemental explanation |
