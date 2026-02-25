# officers Column Reference

**Schema:** f990_2025
**Table:** officers
**Rows:** 26,281,615
**Description:** Board members, officers, trustees, and key employees from all IRS form types (990, 990-EZ, 990-PF), one row per person per filing.

---

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Auto-incrementing primary key |
| pf_return_id | integer | YES | Foreign key to pf_returns.id (populated when source is a 990-PF filing) |
| np_return_id | integer | YES | Foreign key to nonprofit_returns.id (populated when source is a 990 or 990-EZ filing) |
| ein | character varying(20) | NO | EIN of the organization this person is associated with |
| tax_year | integer | YES | Tax year of the filing |
| form_type | character varying(20) | YES | IRS form type: '990', '990EZ', or '990PF' |
| person_nm | text | YES | Person's full name as reported on the filing |
| title_txt | text | YES | Title or position (e.g. "President", "Trustee", "Executive Director") |
| average_hours_per_week | numeric | YES | Average hours per week devoted to the organization |
| compensation_amt | numeric | YES | Total compensation from this organization (dollars with cents) |
| is_officer | boolean | YES | Person holds an officer position. Default: false. |
| is_director | boolean | YES | Person is a director. Default: false. |
| is_trustee | boolean | YES | Person is a trustee. Default: false. |
| is_key_employee | boolean | YES | Person is a key employee (compensation > $150K or top 20). Default: false. |
| is_highest_compensated | boolean | YES | Person is among the 5 highest compensated employees. Default: false. |
| is_former | boolean | YES | Person is a former officer/director/key employee. Default: false. |
| created_at | timestamp without time zone | YES | When this row was inserted. Default: CURRENT_TIMESTAMP. |
| address_line1 | text | YES | Person's address line 1 (rarely populated) |
| employee_benefit_amt | numeric | YES | Employee benefits and deferred compensation (990 Part VII) |
| expense_account_amt | numeric | YES | Expense account and other allowances (990 Part VII) |
| reportable_comp_from_rltd_org_amt | numeric | YES | Reportable compensation from related organizations |
| other_compensation_amt | numeric | YES | Other compensation from the organization and related orgs |
| individual_trustee_or_director_ind | boolean | YES | Is an individual trustee or director (as opposed to institutional) |

---

## Primary Key
- `id` -- Auto-incrementing integer

## Foreign Keys
- `pf_return_id` -> `pf_returns.id` -- Links to the 990-PF filing (NULL for 990/990-EZ)
- `np_return_id` -> `nonprofit_returns.id` -- Links to the 990/990-EZ filing (NULL for 990-PF)

## Indexes
- See database for current indexes

## Notes
- This is one of the largest tables in the database (26M+ rows). Queries should filter by `ein` and/or `tax_year` to avoid full scans.
- Exactly one of `pf_return_id` or `np_return_id` will be populated per row, depending on the source form type.
- The same person may appear multiple times across tax years (one row per filing). To get current officers, filter to the most recent `tax_year` for each `ein`.
- The boolean role columns (`is_officer`, `is_director`, `is_trustee`, `is_key_employee`, `is_highest_compensated`, `is_former`) default to false. A person can have multiple roles simultaneously (e.g. is_officer = TRUE AND is_director = TRUE).
- `compensation_amt` is the primary compensation field. The additional fields (`employee_benefit_amt`, `expense_account_amt`, etc.) are from 990 Part VII and are less consistently populated.
- Name formatting varies widely across filings (e.g. "JOHN SMITH", "Smith, John", "John A. Smith"). No normalization is applied.
