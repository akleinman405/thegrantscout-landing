# dim_clients Column Reference

**Schema:** f990_2025
**Table:** dim_clients
**Rows:** 8
**Description:** TheGrantScout client organizations used for grant matching and report generation.

---

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Auto-incrementing primary key |
| name | character varying(255) | NO | Client organization name |
| ein | character varying(20) | YES | Client's Employer Identification Number |
| state | character varying(50) | NO | Client's home state (2-letter code) |
| city | character varying(1000) | YES | Client's city |
| sector_ntee | character varying(100) | YES | NTEE code describing the client's sector |
| sector_broad | character varying(255) | YES | Broad sector description (e.g. "Human Services") |
| org_type | character varying(100) | YES | Organization type. Default: '501c3'. |
| budget_tier | character varying(100) | YES | Budget size tier label (e.g. "Under $1M", "$1M-$5M") |
| budget_min | integer | YES | Lower bound of budget range (dollars) |
| budget_max | integer | YES | Upper bound of budget range (dollars) |
| grant_size_seeking | character varying(100) | YES | Target grant size range label |
| grant_size_min | integer | YES | Minimum grant size sought (dollars) |
| grant_size_max | integer | YES | Maximum grant size sought (dollars) |
| grant_capacity | character varying(100) | YES | Client's grant management capacity level |
| mission_text | text | YES | Client's mission statement (used for semantic matching) |
| project_need_text | text | YES | Description of the current project or funding need |
| project_type | character varying(50) | YES | Type of project (e.g. "program", "capital", "general") |
| project_keywords | text[] (ARRAY) | YES | Keywords describing the project for grant purpose matching |
| populations_served | text[] (ARRAY) | YES | Target populations (e.g. "veterans", "youth", "seniors") |
| geographic_scope | character varying(100) | YES | Geographic scope of programs (e.g. "local", "state", "national") |
| known_funders | text[] (ARRAY) | YES | Array of EINs for foundations the client already has relationships with (excluded from reports) |
| recipient_ein | character varying(10) | YES | Client's EIN in dim_recipients (for matching as a grant recipient) |
| email | character varying(255) | YES | Primary contact email for the client |
| status | character varying(20) | YES | Client status. Default: 'active'. |
| created_at | timestamp without time zone | YES | When this row was first inserted. Default: now(). |
| updated_at | timestamp without time zone | YES | When this row was last modified. Default: now(). |
| matching_grant_keywords | text[] (ARRAY) | YES | Keywords that indicate a grant purpose is relevant to this client |
| excluded_keywords | text[] (ARRAY) | YES | Keywords that indicate a grant purpose is NOT relevant (false positive filter) |
| budget_target_min | integer | YES | Minimum foundation budget for matching (filters out too-small funders) |
| budget_target_max | integer | YES | Maximum foundation budget for matching |
| database_revenue | numeric | YES | Client's total revenue as found in database filings |
| database_assets | numeric | YES | Client's total assets as found in database filings |
| budget_variance_flag | character varying(20) | YES | Flag when questionnaire budget differs significantly from database financials |
| client_data_quality | character varying(20) | YES | Overall data quality assessment (e.g. "good", "partial", "poor") |
| quality_flags | text[] (ARRAY) | YES | Array of specific data quality issues identified |
| timeframe | character varying(255) | YES | Client's funding timeframe or urgency |
| questionnaire_date | date | YES | Date the client intake questionnaire was completed |
| questionnaire_version | character varying(50) | YES | Version of the intake questionnaire used |
| target_grant_purpose | text | YES | Narrative description of the target grant purpose for matching |

---

## Primary Key
- `id` -- Auto-incrementing integer

## Foreign Keys
- `recipient_ein` -> `dim_recipients.ein` -- Links client to their recipient record for prior funding lookup
- Referenced by:
  - `fact_foundation_client_scores.client_ein` -> `dim_clients.ein`
  - `calc_client_siblings.client_ein` -> `dim_clients.ein`
  - `calc_client_sibling_funders.client_ein` -> `dim_clients.ein`

## Indexes
- See database for current indexes

## Notes
- The `known_funders` array contains EINs of foundations the client already knows. These MUST be excluded from grant reports to ensure discovery value.
- The `mission_text` and `project_need_text` fields are the source text for semantic embedding (stored separately in emb_clients, currently archived).
- `recipient_ein` links the client to `dim_recipients` so the pipeline can look up their prior grant history.
- Budget fields come from two sources: questionnaire (budget_tier, budget_min, budget_max) and database (database_revenue, database_assets). The `budget_variance_flag` highlights discrepancies.
- Only 8 rows as of February 2026. This is a small, manually-maintained table populated from client intake questionnaires.
