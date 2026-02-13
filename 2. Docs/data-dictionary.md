# f990_2025 Data Dictionary

**Last Updated:** 2026-02-13
**Schema:** f990_2025
**Total Tables:** 35 (including 1 materialized view)

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
| website_address_txt | text | YES | Foundation website URL |
| *...and 37 more columns* |

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
| net_assets | numeric(15,2) | YES | Net assets |
| mission_description | text | YES | Mission statement |
| program_service_desc_1 | text | YES | Program 1 description |
| program_service_desc_2 | text | YES | Program 2 description |
| program_service_desc_3 | text | YES | Program 3 description |
| *...and 33 more columns* |

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
| mission_statement | text | YES | Mission statement |
| project_description | text | YES | Current project description |
| known_funders | text[] | YES | Array of known funder EINs |

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

### calc_foundation_behavior
Foundation openness and behavior metrics.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| foundation_ein | varchar(10) | YES | Foundation EIN |
| total_grants_all_time | integer | YES | Total grants made |
| total_grants_5yr | integer | YES | Grants in last 5 years |
| unique_recipients_5yr | integer | YES | Unique recipients (5yr) |
| openness_score | numeric(3,2) | YES | Openness to new recipients |
| repeat_rate | numeric(3,2) | YES | Repeat funding rate |
| new_recipients_5yr | integer | YES | New recipients (5yr) |
| median_grant | bigint | YES | Median grant size |
| avg_grant | bigint | YES | Average grant size |
| giving_trend | varchar(20) | YES | Growing/stable/declining |
| trend_pct_change | double precision | YES | % change in giving |
| accepts_applications | boolean | YES | Open to applications? |
| avg_relationship_duration | numeric | YES | Avg years of funding |

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

### calc_foundation_primary_sector
Primary giving sector for each foundation.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| foundation_ein | varchar(10) | YES | Foundation EIN |
| primary_sector | text | YES | Primary NTEE sector |
| sector_grant_pct | double precision | YES | % of grants in sector |
| rank | bigint | YES | Sector rank (1=primary) |

### calc_recipient_profiles
Aggregated recipient funding profiles.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(10) | NO | Primary key - Recipient EIN |
| total_funders | integer | YES | Total unique funders |
| total_grants | integer | YES | Total grants received |
| total_funding_received | bigint | YES | Total $ received |
| avg_grant_received | bigint | YES | Average grant size |
| funder_eins | text[] | YES | Array of funder EINs |
| years_funded | integer[] | YES | Years with funding |
| first_funded_year | integer | YES | First funded year |
| last_funded_year | integer | YES | Last funded year |
| funding_consistency | varchar(20) | YES | Funding pattern |

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

### calc_recipient_prior_funders
Count of prior funders by recipient and year.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| recipient_ein | varchar(10) | YES | Recipient EIN |
| tax_year | integer | YES | Tax year |
| prior_funder_count | bigint | YES | Funders before this year |

### calc_recipient_prior_grants
Count of prior grants by recipient and year.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| recipient_ein | varchar(10) | YES | Recipient EIN |
| tax_year | integer | YES | Tax year |
| prior_grant_count | integer | YES | Grants before this year |
| prior_year_count | integer | YES | Years funded before this year |

---

## Embedding Tables

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

## Staging Tables

### stg_import_log
ETL run tracking and statistics.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| import_run_id | uuid | NO | Unique run identifier |
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

### stg_processed_xml_files
XML file processing status tracking.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Primary key |
| filename | text | NO | XML filename |
| zip_source | text | NO | Source ZIP file |
| import_run_id | uuid | YES | Associated import run |
| processed_at | timestamp | YES | When processed |
| form_type | varchar(20) | YES | Form type |
| tax_year | integer | YES | Tax year |
| status | varchar(20) | YES | Processing status |

---

## Reference Tables

### ref_irs_bmf
IRS Business Master File - nonprofit reference data.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(9) | NO | Primary key - EIN |
| name | text | NO | Organization name |
| city | text | YES | City |
| state | varchar(2) | YES | State |
| zip | varchar(10) | YES | ZIP code |
| ntee_cd | varchar(10) | YES | NTEE code |
| subsection | varchar(2) | YES | IRS subsection |
| foundation | integer | YES | Foundation type code |
| asset_amt | bigint | YES | Asset amount |
| income_amt | bigint | YES | Income amount |
| created_at | timestamp | YES | Record created |

### ref_org_name_lookup
Organization name normalization lookup.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(20) | NO | Organization EIN |
| raw_name | text | NO | Original name variant |
| normalized_name | text | NO | Normalized name |
| name_source | varchar(50) | YES | Source of this name |
| state | varchar(10) | YES | State |

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

## Other Tables

### prospects
Sales prospect list for TheGrantScout.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ein | varchar(9) | YES | Organization EIN |
| org_name | text | YES | Organization name |
| contact_name | text | YES | Contact person |
| contact_email | text | YES | Contact email |
| website | text | YES | Website URL |
| state | varchar(2) | YES | State |
| ntee_code | varchar(10) | YES | NTEE code |
| icp_score | integer | YES | Ideal customer profile score |
| *...and 63 more columns* |

### fundraising_events
Fundraising event data for prospecting.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| event_id | integer | NO | Primary key |
| source | varchar(50) | YES | Data source |
| org_name_raw | varchar(500) | YES | Organization name |
| event_name | varchar(500) | YES | Event name |
| event_date | date | YES | Event date |
| event_city | varchar(100) | YES | Event city |
| event_state | varchar(2) | YES | Event state |
| event_url | varchar(1000) | YES | Event URL |
| matched_ein | varchar(20) | YES | Matched organization EIN |
| match_confidence | smallint | YES | Match confidence (0-100) |

---

## Web Scraping Tables

### org_url_enrichment (scrape tracking columns)
Added columns for website scraping pipeline status tracking.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| scrape_status | varchar(20) | YES | Scraping pipeline status: pending/fetched/extracted/failed/blocked |
| scrape_pages_fetched | integer | YES | Number of pages successfully fetched |
| scrape_started_at | timestamp | YES | When scraping began for this org |
| scrape_completed_at | timestamp | YES | When scraping completed |
| scrape_error | text | YES | Error message if scrape_status = 'failed' |

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

### Embedding Columns
- `_v` suffix columns are pgvector format for similarity queries
- Base columns are float[] arrays for compatibility
- All use all-MiniLM-L6-v2 model (384 dimensions)
