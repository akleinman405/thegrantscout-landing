# dim_foundations Column Reference

**Schema:** f990_2025
**Table:** dim_foundations
**Rows:** 143,184
**Description:** Master dimension table of unique private foundations, one row per foundation EIN.

---

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | character varying(10) | NO | Employer Identification Number (9-digit, no dashes). Primary key. |
| name | character varying(255) | NO | Foundation's legal name (canonical, from most recent filing) |
| state | character varying(50) | YES | State code (2-letter, e.g. CA, NY) |
| city | character varying(100) | YES | City from most recent filing |
| ntee_code | character varying(10) | YES | NTEE classification code from IRS BMF (e.g. T20, T30) |
| ntee_broad | character varying(100) | YES | Broad NTEE category label (e.g. "Philanthropy, Voluntarism and Grantmaking") |
| accepts_applications | boolean | YES | Foundation is open to unsolicited grant applications. Derived from only_contri_to_preselected_ind = FALSE on pf_returns. Default: true. |
| grants_to_orgs | boolean | YES | Foundation makes grants to organizations (vs. only individuals). Default: true. |
| assets | bigint | YES | Total assets end-of-year from most recent filing (dollars, no cents) |
| last_return_year | integer | YES | Most recent tax year with a 990-PF filing in the database |
| created_at | timestamp without time zone | YES | When this row was first inserted. Default: now(). |
| updated_at | timestamp without time zone | YES | When this row was last modified. Default: now(). |

---

## Primary Key
- `ein` -- Foundation EIN, 9-digit VARCHAR with leading zeros preserved

## Foreign Keys
- None outbound. Referenced by:
  - `fact_grants.foundation_ein` -> `dim_foundations.ein`
  - `calc_foundation_profiles.ein` -> `dim_foundations.ein`
  - `calc_foundation_features.ein` -> `dim_foundations.ein`

## Indexes
- See database for current indexes

## Notes
- EINs are VARCHAR to preserve leading zeros. Never cast to integer.
- The `accepts_applications` and `grants_to_orgs` columns default to TRUE, so NULL should be treated as TRUE.
- The `assets` column is bigint (whole dollars), not numeric with cents.
- Use the production filter `accepts_applications = TRUE AND grants_to_orgs = TRUE` to find grantmaking foundations open to applications.
- This table is the canonical source for foundation identity. Join to `calc_foundation_profiles` for giving metrics and to `pf_returns` for filing-level detail.
