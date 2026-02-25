# dim_recipients Column Reference

**Schema:** f990_2025
**Table:** dim_recipients
**Rows:** 1,652,766
**Description:** Master dimension table of unique grant recipients matched to EINs, one row per recipient organization.

---

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | character varying(10) | NO | Employer Identification Number (9-digit, no dashes). Primary key. |
| name | character varying(255) | NO | Canonical organization name (most common variant or BMF name) |
| state | character varying(50) | YES | State code (2-letter) |
| city | character varying(100) | YES | City |
| ntee_code | character varying(10) | YES | NTEE classification code from IRS BMF |
| ntee_broad | character varying(100) | YES | Broad NTEE category label |
| name_variants | text[] (ARRAY) | YES | Array of known name variants for this organization across filings |
| first_funded_year | integer | YES | Earliest tax year this recipient received a grant in the database |
| last_funded_year | integer | YES | Most recent tax year this recipient received a grant |
| created_at | timestamp without time zone | YES | When this row was first inserted. Default: now(). |
| updated_at | timestamp without time zone | YES | When this row was last modified. Default: now(). |

---

## Primary Key
- `ein` -- Recipient EIN, 9-digit VARCHAR with leading zeros preserved

## Foreign Keys
- None outbound. Referenced by:
  - `fact_grants.recipient_ein` -> `dim_recipients.ein`
  - `calc_recipient_features.ein` -> `dim_recipients.ein`

## Indexes
- See database for current indexes

## Notes
- EINs are VARCHAR to preserve leading zeros. Never cast to integer.
- The `name_variants` array stores all known spellings/abbreviations of the organization name seen across grant filings. Useful for fuzzy matching.
- Not all grant recipients in `fact_grants` have a match in `dim_recipients`. Approximately 20% of fact_grants rows have NULL `recipient_ein` (unmatched recipients).
- This table covers both nonprofit and for-profit grant recipients. Use `ntee_code` to identify nonprofits.
- Join to `calc_recipient_features` for aggregated funding metrics.
