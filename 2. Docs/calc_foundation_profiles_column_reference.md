# calc_foundation_profiles Column Reference

**Schema:** f990_2025
**Table:** calc_foundation_profiles
**Rows:** 143,184
**Description:** Aggregated giving metrics and behavior profiles for every foundation, one row per foundation EIN. Pre-computed from fact_grants for pipeline performance.

---

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | character varying(10) | NO | Foundation EIN. Primary key. |
| has_grant_history | boolean | YES | TRUE if this foundation has any grants in fact_grants. Used as a production filter. |
| total_grants_all_time | integer | YES | Total number of grants ever made (all years in database) |
| total_grants_5yr | integer | YES | Number of grants in the most recent 5 tax years |
| total_giving_5yr | bigint | YES | Total dollar amount given in the most recent 5 tax years |
| unique_recipients_5yr | integer | YES | Number of distinct recipients funded in the most recent 5 tax years. Production filter: >= 5 excludes captive trusts. |
| last_active_year | integer | YES | Most recent tax year with a grant in the database |
| median_grant | bigint | YES | Median grant amount across all grants (whole dollars) |
| avg_grant | bigint | YES | Average (mean) grant amount across all grants (whole dollars) |
| grant_range_min | bigint | YES | Smallest grant amount on record |
| grant_range_max | bigint | YES | Largest grant amount on record |
| openness_score | numeric | YES | Score from 0 to 1 measuring willingness to fund new recipients. Higher = more open. Based on ratio of first-time recipients to total recipients. |
| repeat_rate | numeric | YES | Rate of repeat funding (0 to 1). Fraction of recipients who received grants in 2+ years. |
| new_recipients_5yr | integer | YES | Number of first-time recipients in the most recent 5 tax years |
| geographic_focus | jsonb | YES | JSON object describing geographic giving patterns. Contains state-level distribution of grants. |
| sector_focus | jsonb | YES | JSON object describing NTEE sector giving patterns. Contains sector-level distribution of grants. |
| project_types | jsonb | YES | JSON object describing types of projects funded (e.g. general support, program, capital) |
| typical_recipient_size | character varying(20) | YES | Size category of typical recipient (e.g. "small", "medium", "large") based on recipient revenue |
| giving_trend | character varying(20) | YES | Trend direction: "growing", "stable", or "declining" based on 3-year comparison |
| trend_pct_change | double precision | YES | Percentage change in giving comparing recent period to earlier period |
| accepts_applications | boolean | YES | Whether the foundation accepts unsolicited applications (mirrors dim_foundations) |
| calculated_at | timestamp without time zone | YES | When these metrics were last computed. Default: now(). |

---

## Primary Key
- `ein` -- Foundation EIN, 9-digit VARCHAR with leading zeros preserved

## Foreign Keys
- `ein` -> `dim_foundations.ein` -- One-to-one relationship with dim_foundations

## Indexes
- See database for current indexes

## Notes
- This table has exactly the same number of rows as `dim_foundations` (143,184). Every foundation gets a profile row, even if `has_grant_history` is FALSE.
- The "5yr" columns refer to the most recent 5 tax years available in the database (approximately 2020-2024).
- `openness_score` and `repeat_rate` are key signals in the LASSO V6.1 scoring model.
- `geographic_focus` and `sector_focus` are JSONB columns. Example geographic_focus: `{"CA": 0.45, "NY": 0.20, "TX": 0.10, ...}`. Example sector_focus: `{"P": 0.30, "B": 0.25, ...}` where letters are NTEE major group codes.
- `giving_trend` is derived from `trend_pct_change`. Thresholds: growing > +10%, declining < -10%, otherwise stable.
- Production filters use multiple columns from this table: `has_grant_history = TRUE`, `unique_recipients_5yr >= 5`, combined with `dim_foundations.assets >= 100000` and `dim_foundations.accepts_applications = TRUE`.
