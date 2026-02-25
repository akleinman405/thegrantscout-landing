# f990_2025 Data Dictionary

**Last Updated:** 2026-02-25
**Schema:** f990_2025
**Total Tables:** 57 (tables) + 2 materialized views + 10 views

---

## Table of Contents

1. [Core Data Tables](#core-data-tables)
2. [Dimension Tables](#dimension-tables)
3. [Fact Tables](#fact-tables)
4. [Calculated Tables](#calculated-tables)
5. [Embedding Tables](#embedding-tables)
6. [Staging Tables](#staging-tables)
7. [Reference Tables](#reference-tables)
8. [Other Tables](#other-tables)

---

## Core Data Tables

### pf_returns
Private foundation 990-PF tax return filings.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| ein | varchar(20) | NO | Employer Identification Number |
| business_name | text | YES | Foundation name |
| tax_year | integer | YES | Tax year of filing |
| tax_period_begin | date | YES | Start of tax period |
| tax_period_end | date | YES | End of tax period |
| source_file | text | YES | Original XML file path |
| return_timestamp | timestamp | YES | When return was filed |
| object_id | varchar(100) | YES | IRS object identifier |
| address_line1 | text | YES | Street address |
| city | text | YES | City |
| state | varchar(50) | YES | State code |
| zip | varchar(20) | YES | ZIP code |
| total_assets_boy_amt | numeric(15,2) | YES | Total assets beginning of year |
| total_assets_eoy_amt | numeric(15,2) | YES | Total assets end of year |
| grants_to_organizations_ind | boolean | YES | Makes grants to organizations? |
| only_contri_to_preselected_ind | boolean | YES | Only contributes to preselected? |
| website_url | text | YES | Foundation website URL |
| email_address_txt | text | YES | Email address |
| phone_num | text | YES | Phone number |
| mission_desc | text | YES | Mission description |
| app_contact_name | text | YES | Application contact name |
| app_contact_phone | text | YES | Application contact phone |
| app_contact_email | text | YES | Application contact email |
| app_submission_deadlines | text | YES | Application deadlines |
| app_restrictions | text | YES | Application restrictions |
| app_form_requirements | text | YES | Application form requirements |
| ntee_code | varchar(10) | YES | NTEE classification code |
| private_operating_foundation_ind | boolean | YES | Is private operating foundation? |
| *...and ~50 more columns (94 total)* |

### pf_grants
Individual grant records from 990-PF Schedule I.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| return_id | integer | YES | FK to pf_returns.id |
| filer_ein | varchar(20) | NO | Foundation EIN |
| tax_year | integer | YES | Grant tax year |
| recipient_ein | varchar(20) | YES | Recipient EIN (if known) |
| recipient_name | text | YES | Recipient organization name |
| recipient_city | text | YES | Recipient city |
| recipient_state | varchar(50) | YES | Recipient state |
| recipient_zip | varchar(20) | YES | Recipient ZIP |
| is_individual | boolean | YES | Grant to individual? |
| amount | numeric(15,2) | YES | Grant amount in dollars |
| purpose | text | YES | Grant purpose description |
| relationship | text | YES | Relationship to foundation |

### nonprofit_returns
990 and 990-EZ nonprofit tax return filings.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| ein | varchar(20) | NO | Employer Identification Number |
| organization_name | text | YES | Organization name |
| tax_year | integer | YES | Tax year |
| form_type | varchar(20) | YES | 990 or 990-EZ |
| city | text | YES | City |
| state | varchar(50) | YES | State |
| total_revenue | numeric(15,2) | YES | Total revenue |
| total_expenses | numeric(15,2) | YES | Total expenses |
| total_assets_eoy | numeric(15,2) | YES | Total assets end of year |
| total_assets_boy | numeric(15,2) | YES | Total assets beginning of year |
| net_assets_eoy | numeric(15,2) | YES | Net assets end of year |
| net_assets_boy | numeric(15,2) | YES | Net assets beginning of year |
| mission_description | text | YES | Mission statement |
| program_1_desc | text | YES | Program 1 description |
| program_2_desc | text | YES | Program 2 description |
| program_3_desc | text | YES | Program 3 description |
| program_1_expense_amt | numeric(15,2) | YES | Program 1 expenses |
| ntee_code | varchar(10) | YES | NTEE code |
| total_employees_cnt | integer | YES | Total employees |
| total_volunteers_cnt | integer | YES | Total volunteers |
| website | text | YES | Website URL |
| phone | text | YES | Phone number |
| *...and ~50 more columns (91 total)* |

### officers
Board members, officers, and key employees from all form types.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| pf_return_id | integer | YES | FK to pf_returns.id |
| np_return_id | integer | YES | FK to nonprofit_returns.id |
| ein | varchar(20) | NO | Organization EIN |
| tax_year | integer | YES | Tax year |
| form_type | varchar(20) | YES | Form type (990, 990-PF, etc.) |
| person_nm | text | YES | Person name |
| title_txt | text | YES | Title/position |
| average_hours_per_week | numeric(5,2) | YES | Hours per week |
| compensation_amt | numeric(15,2) | YES | Compensation amount |
| is_officer | boolean | YES | Is officer? |
| is_director | boolean | YES | Is director? |
| is_trustee | boolean | YES | Is trustee? |
| is_key_employee | boolean | YES | Is key employee? |

### schedule_a
Schedule A charity classification information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| np_return_id | integer | YES | FK to nonprofit_returns.id |
| ein | varchar(20) | NO | Organization EIN |
| tax_year | integer | YES | Tax year |
| church_ind | boolean | YES | Is a church? |
| school_ind | boolean | YES | Is a school? |
| hospital_ind | boolean | YES | Is a hospital? |
| public_charity_509a1_ind | boolean | YES | 509(a)(1) public charity? |
| public_charity_509a2_ind | boolean | YES | 509(a)(2) public charity? |
| supporting_org_509a3_ind | boolean | YES | 509(a)(3) supporting org? |

---

## Dimension Tables

### dim_foundations
Master table of unique private foundations.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(10) | NO | Primary key - Foundation EIN |
| name | varchar(255) | NO | Foundation name |
| state | varchar(50) | YES | State code |
| city | varchar(100) | YES | City |
| ntee_code | varchar(10) | YES | NTEE classification code |
| ntee_broad | varchar(100) | YES | Broad NTEE category |
| accepts_applications | boolean | YES | Open to grant applications? |
| grants_to_orgs | boolean | YES | Makes grants to organizations? |
| assets | bigint | YES | Total assets |
| last_return_year | integer | YES | Most recent tax year filed |
| created_at | timestamp | YES | Record created timestamp |
| updated_at | timestamp | YES | Record updated timestamp |

### dim_recipients
Master table of unique grant recipients (matched to EINs).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(10) | NO | Primary key - Recipient EIN |
| name | varchar(255) | NO | Canonical organization name |
| state | varchar(50) | YES | State code |
| city | varchar(100) | YES | City |
| ntee_code | varchar(10) | YES | NTEE classification code |
| ntee_broad | varchar(100) | YES | Broad NTEE category |
| name_variants | text[] | YES | Array of known name variants |
| first_funded_year | integer | YES | First year received grant |
| last_funded_year | integer | YES | Last year received grant |
| created_at | timestamp | YES | Record created timestamp |
| updated_at | timestamp | YES | Record updated timestamp |

### dim_clients
TheGrantScout client organizations.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| name | varchar(255) | NO | Client organization name |
| ein | varchar(20) | YES | Client EIN |
| state | varchar(50) | NO | State |
| city | varchar(1000) | YES | City |
| sector_ntee | varchar(100) | YES | NTEE code |
| sector_broad | varchar(255) | YES | Broad sector description |
| org_type | varchar(100) | YES | Organization type |
| budget_tier | varchar(100) | YES | Budget size tier |
| grant_size_seeking | varchar(100) | YES | Target grant size |
| grant_size_min | numeric | YES | Minimum grant size seeking |
| grant_size_max | numeric | YES | Maximum grant size seeking |
| grant_capacity | text | YES | Grant writing capacity |
| mission_text | text | YES | Mission statement |
| project_need_text | text | YES | Current project/need description |
| project_type | text | YES | Project type classification |
| project_keywords | text | YES | Keywords for matching |
| populations_served | text | YES | Target populations |
| geographic_scope | text | YES | Geographic service area |
| known_funders | text[] | YES | Array of known funder EINs |
| recipient_ein | varchar(20) | YES | FK to dim_recipients.ein |
| email | text | YES | Contact email |
| status | varchar(50) | YES | Client status |
| matching_grant_keywords | text | YES | Keywords for grant matching |
| excluded_keywords | text | YES | Keywords to exclude |
| target_grant_purpose | text | YES | Target grant purpose text |
| database_revenue | numeric | YES | Revenue from DB lookup |
| database_assets | numeric | YES | Assets from DB lookup |
| *...and 8 more columns (40 total)* |

---

## Fact Tables

### fact_grants
Cleaned and matched grant transaction records.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| foundation_ein | varchar(10) | NO | FK to dim_foundations.ein |
| recipient_ein | varchar(10) | YES | FK to dim_recipients.ein |
| recipient_name_raw | varchar(255) | YES | Original recipient name |
| recipient_state | varchar(50) | YES | Recipient state |
| recipient_city | varchar(100) | YES | Recipient city |
| amount | bigint | YES | Grant amount in dollars |
| purpose_text | varchar(1000) | YES | Grant purpose description |
| purpose_type | varchar(50) | YES | Categorized purpose type |
| tax_year | integer | NO | Tax year of grant |
| is_first_time | boolean | YES | First grant to this recipient? |
| recipient_match_confidence | varchar(20) | YES | EIN match confidence level |
| source | varchar(50) | YES | Data source |
| created_at | timestamp | YES | Record created timestamp |

---

## Calculated Tables

### calc_foundation_profiles
Aggregated foundation giving profiles.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(10) | NO | Primary key - Foundation EIN |
| has_grant_history | boolean | YES | Has grants in database? |
| total_grants_all_time | integer | YES | Total grants ever made |
| total_grants_5yr | integer | YES | Grants in last 5 years |
| total_giving_5yr | bigint | YES | Total $ given in 5 years |
| unique_recipients_5yr | integer | YES | Unique recipients in 5 years |
| last_active_year | integer | YES | Most recent grant year |
| median_grant | bigint | YES | Median grant amount |
| avg_grant | bigint | YES | Average grant amount |
| grant_range_min | bigint | YES | Minimum grant amount |
| grant_range_max | bigint | YES | Maximum grant amount |
| openness_score | numeric(3,2) | YES | Score 0-1 for new recipients |
| repeat_rate | numeric(3,2) | YES | Rate of repeat funding |
| geographic_focus | jsonb | YES | Geographic giving patterns |
| sector_focus | jsonb | YES | NTEE sector focus |

### calc_foundation_features
Comprehensive features for ML model training.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(10) | YES | Foundation EIN |
| name | varchar(255) | YES | Foundation name |
| state | varchar(50) | YES | State |
| ntee_code | varchar(10) | YES | NTEE code |
| accepts_applications | boolean | YES | Open to applications? |
| dim_assets | bigint | YES | Total assets |
| openness_score | numeric | YES | Openness score |
| repeat_rate | numeric | YES | Repeat funding rate |
| median_grant | bigint | YES | Median grant size |
| *...and 80+ feature columns* |

### calc_recipient_features
Comprehensive recipient features for ML model training.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(10) | YES | Recipient EIN |
| name | varchar(255) | YES | Organization name |
| state | varchar(50) | YES | State |
| ntee_code | varchar(10) | YES | NTEE code |
| total_funders | integer | YES | Total unique funders |
| total_grants | integer | YES | Total grants received |
| total_funding_received | bigint | YES | Total $ received |
| *...and 59+ feature columns* |

### calc_client_siblings (2,100 rows)
Similar organizations per client for funder discovery.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| client_ein | varchar | NO | Client EIN (PK part) |
| sibling_ein | varchar | NO | Similar org EIN (PK part) |
| similarity | numeric | YES | Similarity score |
| client_budget | numeric | YES | Client budget |
| sibling_budget | numeric | YES | Sibling budget |
| budget_ratio | numeric | YES | Budget ratio |
| model_version | varchar | YES | Model version |
| computed_at | timestamp | YES | When computed |

### calc_client_sibling_funders (168 rows)
Foundations that fund client siblings.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| client_ein | varchar | NO | Client EIN (PK part) |
| foundation_ein | varchar | NO | Foundation EIN (PK part) |
| siblings_funded | integer | YES | Number of siblings funded |
| total_grants | integer | YES | Total grants to siblings |
| total_amount | numeric | YES | Total amount to siblings |
| avg_grant | numeric | YES | Average grant size |
| most_recent_year | integer | YES | Most recent grant year |
| computed_at | timestamp | YES | When computed |

### calc_client_sibling_grants (13,389 rows)
Individual grants to client siblings with analysis.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| client_ein | varchar | NO | Client EIN (PK part) |
| foundation_ein | varchar | NO | Foundation EIN |
| sibling_ein | varchar | NO | Sibling EIN |
| grant_id | integer | NO | Grant ID (PK part) |
| amount | bigint | YES | Grant amount |
| tax_year | integer | YES | Tax year |
| recipient_state | varchar | YES | Recipient state |
| purpose_text | varchar | YES | Grant purpose |
| is_first_grant | boolean | YES | First grant to this recipient? |
| purpose_quality | varchar | YES | Purpose text quality |
| keyword_match | boolean | YES | Matches client keywords? |
| semantic_similarity | numeric | YES | Semantic similarity score |
| is_target_grant | boolean | YES | Meets target criteria? |
| target_grant_reason | text | YES | Why it's a target grant |
| computed_at | timestamp | YES | When computed |

### calc_client_foundation_scores (4,816 rows)
Enriched client-foundation scoring with eligibility analysis.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| client_ein | varchar | NO | Client EIN (PK part) |
| foundation_ein | varchar | NO | Foundation EIN (PK part) |
| client_name | varchar | YES | Client name |
| foundation_name | varchar | YES | Foundation name |
| foundation_state | varchar | YES | Foundation state |
| foundation_total_assets | numeric | YES | Foundation assets |
| siblings_funded | integer | YES | Siblings funded by this foundation |
| grants_to_siblings | integer | YES | Grants to client siblings |
| total_amount_to_siblings | numeric | YES | Total amount to siblings |
| lasso_score | numeric | YES | LASSO model score |
| geo_eligible | boolean | YES | Geographic eligibility |
| open_to_applicants | boolean | YES | Accepts applications? |
| client_eligible | boolean | YES | Overall client eligibility |
| eligibility_notes | text | YES | Eligibility notes |

### calc_client_proof_of_fit_grants (25 rows)
Best proof-of-fit grants per recommendation.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| client_ein | varchar | YES | Client EIN |
| foundation_ein | varchar | YES | Foundation EIN |
| grant_id | integer | YES | Reference grant ID |
| amount | numeric | YES | Grant amount |
| purpose_text | text | YES | Grant purpose |
| recipient_name | text | YES | Recipient name |
| fit_reason | text | YES | Why this grant shows fit |

### calc_client_foundation_recommendations (5 rows)
Final top-N foundation recommendations per client.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| client_ein | varchar | NO | Client EIN |
| foundation_ein | varchar | NO | Foundation EIN |
| rank | integer | YES | Recommendation rank |
| score | numeric | YES | Combined score |
| recommendation_notes | text | YES | Why recommended |

---

## Email Pipeline Tables

### campaign_prospect_status (3,185 rows)
Email campaign tracking and status.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| ein | varchar | YES | Organization EIN |
| email | varchar | YES | Contact email |
| org_name | varchar | YES | Organization name |
| org_type | varchar | YES | Organization type |
| vertical | varchar | YES | Campaign vertical |
| campaign_status | varchar | YES | Current status |
| initial_sent_at | timestamp | YES | When initial email sent |
| initial_status | varchar | YES | Initial send status |
| replied | boolean | YES | Has replied? |
| bounced | boolean | YES | Has bounced? |
| unsubscribed | boolean | YES | Has unsubscribed? |
| *...and 16 more columns (29 total)* |

### cohort_foundation_lists_v2 (21,667 rows)
Foundation-cohort matches with composite fit scores.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| state | varchar | NO | State code |
| ntee_sector | varchar | NO | NTEE sector |
| foundation_rank | integer | NO | Rank within cohort |
| foundation_ein | varchar | NO | Foundation EIN |
| foundation_name | varchar | YES | Foundation name |
| email_fit_score | numeric | YES | Composite email fit score |
| geo_tier | varchar | YES | Geographic relevance tier |
| *...and 24 more columns (32 total)* |

### cohort_viability (882 rows)
State-sector cohort viability flags.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| state | varchar | NO | State code (PK part) |
| ntee_sector | varchar | NO | NTEE sector (PK part) |
| foundation_count | integer | YES | Foundations matching |
| prospect_count | integer | YES | Prospects matching |
| viable | boolean | YES | Is cohort viable? |
| display_count | integer | YES | Capped display count |
| display_text | text | YES | Formatted display text |

### ref_foundation_email_exclusions (45 rows)
Foundations excluded from email campaigns.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| foundation_ein | varchar | NO | Primary key |
| exclusion_reason | text | YES | Why excluded |
| category | varchar | YES | Exclusion category |

### foundation_enrichment (374 rows)
Manual/scraped enrichment data for foundations.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| ein | varchar | NO | Foundation EIN (UNIQUE) |
| accepts_unsolicited | boolean | YES | Accepts unsolicited proposals? |
| application_type | varchar | YES | Application type |
| application_url | varchar | YES | Application URL |
| current_deadline | text | YES | Current deadline |
| contact_name | varchar | YES | Contact name |
| contact_email | varchar | YES | Contact email |
| program_priorities | text | YES | Program priorities |
| geographic_focus | text | YES | Geographic focus |
| viability_multiplier | numeric | YES | Viability scoring multiplier |
| *...and 12 more columns (24 total)* |

---

## Embedding Tables (ARCHIVED 2026-01-04)

### emb_grant_purposes
384-dimensional embeddings of grant purpose text.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| grant_id | integer | NO | PK, FK to fact_grants.id |
| purpose_embedding | float[] | NO | 384-dim float array |
| model_name | varchar(100) | YES | Model used (all-MiniLM-L6-v2) |
| created_at | timestamp | YES | When embedding was created |
| purpose_embedding_v | vector(384) | YES | pgvector format |

### emb_nonprofit_missions
384-dimensional embeddings of nonprofit mission statements.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(20) | NO | Primary key - Organization EIN |
| mission_embedding | float[] | NO | 384-dim float array |
| source_text_length | integer | YES | Length of source text |
| model_name | varchar(100) | YES | Model used |
| created_at | timestamp | YES | When created |
| mission_embedding_v | vector(384) | YES | pgvector format |

### emb_programs
384-dimensional embeddings of program descriptions.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| ein | varchar(20) | NO | Organization EIN |
| program_number | integer | NO | Program number (1, 2, 3) |
| program_embedding | float[] | NO | 384-dim float array |
| model_name | varchar(100) | YES | Model used |
| program_embedding_v | vector(384) | YES | pgvector format |

### emb_prospects
384-dimensional embeddings of prospect mission statements.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(20) | NO | Primary key - Prospect EIN |
| mission_embedding | float[] | NO | 384-dim float array |
| source_text_length | integer | YES | Length of source text |
| model_name | varchar(100) | YES | Model used |
| mission_embedding_v | vector(384) | YES | pgvector format |

### emb_clients
384-dimensional embeddings of client mission/project text.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| client_id | integer | NO | PK, FK to dim_clients.id |
| mission_embedding | float[] | YES | Mission text embedding |
| project_embedding | float[] | YES | Project text embedding |
| combined_embedding | float[] | YES | Combined embedding |
| model_name | varchar(100) | YES | Model used |
| mission_embedding_v | vector(384) | YES | pgvector format |
| project_embedding_v | vector(384) | YES | pgvector format |
| combined_embedding_v | vector(384) | YES | pgvector format |

---

## Staging / ETL Tables

### import_log (748,311 rows)
ETL run tracking and statistics.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| import_run_id | uuid | YES | Unique run identifier |
| started_at | timestamp | YES | Run start time |
| completed_at | timestamp | YES | Run end time |
| source_file | text | YES | Source file path |
| form_type | varchar(20) | YES | Form type processed |
| tax_year | integer | YES | Tax year processed |
| records_processed | integer | YES | Total records attempted |
| records_success | integer | YES | Successful records |
| records_failed | integer | YES | Failed records |
| error_message | text | YES | Error details |
| status | varchar(50) | YES | Run status |

### stg_foundation_state_dist / stg_foundation_sector_dist
Staging tables for geographic and sector distribution. Used by mv_foundation_geo_relevance.

---

## Reference Tables

### bmf (1,935,635 rows)
IRS Business Master File - nonprofit reference data. PK: `ein`.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar | NO | Primary key - EIN |
| name | text | NO | Organization name |
| ico | text | YES | In care of name |
| street | text | YES | Street address |
| city | text | YES | City |
| state | varchar | YES | State |
| zip | varchar | YES | ZIP code |
| ntee_cd | varchar | YES | NTEE code |
| subsection | varchar | YES | IRS subsection |
| foundation | integer | YES | Foundation type code |
| deductibility | integer | YES | Deductibility code |
| classification | varchar | YES | Classification code |
| ruling | varchar | YES | Ruling date |
| affiliation | varchar | YES | Affiliation code |
| organization | varchar | YES | Organization code |
| status | varchar | YES | BMF status |
| asset_cd | varchar | YES | Asset code |
| asset_amt | bigint | YES | Asset amount |
| income_cd | varchar | YES | Income code |
| income_amt | bigint | YES | Income amount |
| revenue_amt | bigint | YES | Revenue amount |
| sort_name | text | YES | Sort name |

### ref_state_regions (51 rows)
State to region mapping. PK: `state_code`.

### ref_org_aliases
Manual organization alias mappings.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| alias | text | NO | Alias name |
| ein | varchar(20) | YES | Mapped EIN |

### ref_recipient_alias_mappings
Recipient canonical name mappings.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| alias_name | text | NO | Alias name |
| alias_state | varchar(2) | NO | Alias state |
| canonical_ein | varchar(20) | YES | Canonical EIN |
| canonical_name | text | YES | Canonical name |
| source | text | YES | Mapping source |
| verified_date | date | YES | Verification date |

---

## Prospect Tables

### foundation_prospects2 (143,184 rows)
Flattened foundation master table for prospecting. PK: `id`, UNIQUE: `ein`.
See `foundation_prospects2_column_reference.md` for full 38-column listing.

### nonprofits_prospects2 (673,381 rows)
Flattened nonprofit master for email campaigns. PK: `id`, UNIQUE: `ein`.
Includes email quality columns: `email_quality_tier`, `email_quality_flags`, `verification_status`.

### research_events (273 rows)
Fundraising event data for prospecting. PK: `event_id`.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| event_id | integer | NO | Primary key |
| source | varchar(50) | YES | Data source |
| source_event_id | varchar | YES | External event ID |
| org_name_raw | varchar(500) | YES | Organization name |
| event_name | varchar(500) | YES | Event name |
| event_date | date | YES | Event date |
| event_city | varchar(100) | YES | Event city |
| event_state | varchar(2) | YES | Event state |
| event_url | varchar(1000) | YES | Event URL |
| matched_ein | varchar(20) | YES | Matched organization EIN |

### org_url_enrichment (813,698 rows)
URL enrichment and scrape tracking. PK: `ein`.
Key columns: `scrape_status` (pending/fetched/extracted/failed/blocked), `scrape_pages_fetched`, `scrape_started_at`, `scrape_completed_at`, `scrape_error`.

---

## Web Scraping Tables

### web_pages
Metadata for fetched HTML pages (HTML stored on disk in gzip cache).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | serial | NO | Primary key |
| ein | varchar(20) | NO | Organization EIN |
| url | text | NO | Page URL |
| page_type | varchar(30) | YES | Page type: homepage/contact/about/team/leadership/grants |
| http_status | smallint | YES | HTTP status code |
| html_hash | varchar(64) | YES | SHA-256 hash of HTML content |
| html_size_bytes | integer | YES | Size of HTML in bytes |
| fetched_at | timestamp | NO | When page was fetched |

### web_emails
All emails extracted from organization websites, one row per unique email per org.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | serial | NO | Primary key |
| ein | varchar(20) | NO | Organization EIN |
| email | varchar(255) | NO | Email address |
| email_type | varchar(20) | NO | Classification: general/role/person |
| email_domain | varchar(255) | YES | Email domain part |
| domain_matches_website | boolean | YES | Does email domain match org website? |
| person_name | text | YES | Associated person name (when email_type='person') |
| person_title | text | YES | Associated person title |
| source_url | text | YES | URL where email was found |
| source_page_type | varchar(30) | YES | Page type where found |
| extraction_method | varchar(30) | YES | How email was extracted: regex/mailto/cfemail/at_dot/json_ld |
| confidence | numeric(3,2) | YES | Confidence score 0.00-1.00 |
| syntax_valid | boolean | YES | Email syntax is valid? |
| mx_valid | boolean | YES | Domain has valid MX records? |
| validated_at | timestamp | YES | When validation was performed |
| extracted_at | timestamp | NO | When email was extracted |

UNIQUE constraint on (ein, email).

### web_org_metadata
Organization metadata extracted from websites.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(20) | NO | Primary key - Organization EIN |
| meta_description | text | YES | HTML meta description tag |
| og_description | text | YES | OpenGraph description |
| mission_text | text | YES | Mission statement text from website |
| twitter_url | text | YES | Twitter/X profile URL |
| linkedin_url | text | YES | LinkedIn company page URL |
| facebook_url | text | YES | Facebook page URL |
| instagram_url | text | YES | Instagram profile URL |
| youtube_url | text | YES | YouTube channel URL |
| phone_numbers | text[] | YES | Array of discovered phone numbers |
| physical_address | text | YES | Physical address from website |
| has_cloudflare | boolean | YES | Site uses Cloudflare? |
| has_js_rendering | boolean | YES | Site uses JS frameworks (React/Vue/Angular)? |
| cms_platform | varchar(50) | YES | Detected CMS: wordpress/squarespace/wix/etc. |
| json_ld_types | text[] | YES | JSON-LD @type values found |
| extracted_at | timestamp | NO | When metadata was extracted |

### web_staff
Staff members extracted from team/leadership/board pages.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | serial | NO | Primary key |
| ein | varchar(20) | NO | Organization EIN |
| person_name | text | NO | Person's name |
| title | text | YES | Job title |
| email | varchar(255) | YES | Person's email (if found) |
| phone | varchar(50) | YES | Person's phone (if found) |
| staff_type | varchar(30) | YES | Classification: board/executive/staff/leadership/advisory |
| source_url | text | YES | URL where person was found |
| source_page_type | varchar(30) | YES | Page type where found |
| extraction_confidence | numeric(3,2) | YES | Extraction confidence 0.00-1.00 |
| extracted_at | timestamp | NO | When staff was extracted |

### web_best_email (Materialized View)
Best email per organization, ranked by domain match, MX validity, email type, and confidence.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(20) | NO | Organization EIN |
| email | varchar(255) | NO | Best email address |
| email_type | varchar(20) | NO | Email classification |
| person_name | text | YES | Associated person name |
| person_title | text | YES | Associated person title |
| confidence | numeric(3,2) | YES | Confidence score |
| mx_valid | boolean | YES | MX record validity |
| rank | bigint | YES | Always 1 (best per org) |

Only includes emails where syntax_valid=TRUE AND domain_matches_website=TRUE.

---

## Data Quality Notes

### EIN Format
- Always VARCHAR, not integer (preserve leading zeros)
- No dashes: `123456789` not `12-3456789`
- Length: 9 characters for standard EINs, 10 with check digit

### Common NULL Patterns
- `purpose_text` in fact_grants: ~15% NULL
- `recipient_ein` in fact_grants: ~20% NULL (unmatched recipients)
- `ntee_code` varies by table: 60-80% populated

### Embedding Tables
- ARCHIVED 2026-01-04 to save 52GB disk space
- Backups at `1. Database/4. Semantic Embeddings/archive/`
- See `REPORT_2026-01-04.1_embeddings_archived.md` for restore instructions

---

## Materialized Views

### web_best_email (9,844 rows)
Best email per organization. Only includes emails where syntax_valid=TRUE AND domain_matches_website=TRUE.
Refresh: `REFRESH MATERIALIZED VIEW f990_2025.web_best_email;`

### mv_foundation_geo_relevance (425,794 rows)
Foundation geographic giving relevance by state with tier classification (primary/secondary/tertiary/incidental).
Refresh: `REFRESH MATERIALIZED VIEW CONCURRENTLY f990_2025.mv_foundation_geo_relevance;`

---

## Views

| View | Purpose |
|------|---------|
| vw_foundation_summary | Simplified foundation summary from pf_returns |
| sales_prospects | Union of NP + FDN prospects for CRM |
| v_campaign_prospects | Campaign status joined with prospect details |
| v_suppress_list | Emails to suppress (bounced/replied/unsubscribed) |
| v_suppress_list_by_ein | EINs to suppress from outreach |
| v_email_preflight_overcitation | QC: foundations cited in too many cohorts |
| v_email_preflight_example_quality | QC: example grant quality check |
| v_email_preflight_prospect_quality | QC: prospect data quality check |
| grant_purpose_quality | Purpose text quality classification |
| prospects_with_events | Prospects joined with fundraising events |

---

## Public Schema

### global_bounce_list (276 rows)
Email addresses that have bounced. PK: `email`. Used across all campaigns.

---

*Last verified against live database: 2026-02-25*
