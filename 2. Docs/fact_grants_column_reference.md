# fact_grants Column Reference

**Schema:** f990_2025
**Table:** fact_grants
**Rows:** 8,310,650
**Description:** Cleaned and EIN-matched grant transaction records, one row per grant from a foundation to a recipient in a given tax year.

---

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Auto-incrementing primary key |
| foundation_ein | character varying(10) | NO | Granting foundation's EIN. Foreign key to dim_foundations.ein. |
| recipient_ein | character varying(10) | YES | Recipient organization's EIN. NULL when recipient could not be matched (~20% of rows). Foreign key to dim_recipients.ein. |
| recipient_name_raw | character varying(255) | YES | Original recipient name as it appeared on the 990-PF filing |
| recipient_state | character varying(50) | YES | Recipient's state code (2-letter) |
| recipient_city | character varying(100) | YES | Recipient's city |
| amount | bigint | YES | Grant amount in whole dollars. NULL means not reported. |
| purpose_text | character varying(1000) | YES | Grant purpose description from 990-PF Part XV. ~15% NULL. |
| purpose_type | character varying(50) | YES | Categorized purpose type (e.g. "general support", "program", "capital") |
| tax_year | integer | NO | Tax year this grant was reported on (the filing year, not necessarily the payment year) |
| is_first_time | boolean | YES | TRUE if this is the first grant from this foundation to this recipient in the database |
| recipient_match_confidence | character varying(20) | YES | Confidence level of the EIN match (e.g. "high", "medium", "low") |
| source | character varying(50) | YES | Data source identifier (e.g. "pf_grants_v1") |
| created_at | timestamp without time zone | YES | When this row was inserted. Default: now(). |

---

## Primary Key
- `id` -- Auto-incrementing integer

## Foreign Keys
- `foundation_ein` -> `dim_foundations.ein` -- The granting foundation
- `recipient_ein` -> `dim_recipients.ein` -- The grant recipient (NULL when unmatched)

## Indexes
- See database for current indexes

## Notes
- **CRITICAL:** The foundation column is `foundation_ein`, NOT `filer_ein`. The raw `pf_grants` table uses `filer_ein`, but `fact_grants` was renamed to `foundation_ein` for clarity. Always use `foundation_ein` when joining to `dim_foundations`.
- **CRITICAL:** The purpose column is `purpose_text`, NOT `purpose`. The raw `pf_grants` table uses `purpose`, but `fact_grants` uses `purpose_text`.
- EINs are VARCHAR with leading zeros preserved. Never cast to integer or add dashes.
- The `amount` column is bigint (whole dollars), not numeric with cents.
- `tax_year` is more reliable than grant dates for temporal analysis, since grant dates are often NULL in IRS data.
- Approximately 20% of rows have NULL `recipient_ein` because the recipient could not be matched to a known EIN via name/state fuzzy matching.
- Approximately 15% of rows have NULL `purpose_text` because the foundation did not report a grant purpose.
- This table is derived from `pf_grants` with cleaning, deduplication, and EIN matching applied.
- Use `tax_year` for filtering by time period. Data covers 2016-2024.
