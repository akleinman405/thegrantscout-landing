# Schema Reference — f990_2025

**Verified:** 2026-02-25 | **Host:** localhost:5432 | **Database:** thegrantscout

---

## COLUMN GOTCHAS (read before writing SQL)

| Wrong | Right | Table | Notes |
|-------|-------|-------|-------|
| `filer_ein` | `foundation_ein` | fact_grants | pf_grants uses filer_ein; fact_grants uses foundation_ein |
| `purpose` | `purpose_text` | fact_grants | pf_grants uses purpose; fact_grants uses purpose_text |
| `mission_statement` | `mission_text` | dim_clients | Was renamed; mission_description is in nonprofit_returns |
| `project_description` | `project_need_text` | dim_clients | Was renamed |
| `business_name` | `name` | dim_foundations | pf_returns uses business_name; dim_foundations uses name |
| `organization_name` | `name` | dim_recipients | nonprofit_returns uses organization_name; dim_recipients uses name |
| `website_address_txt` | `website_url` | pf_returns | Column was renamed during import |
| `net_assets` | `net_assets_eoy_amt` | pf_returns | Separate BOY/EOY columns, no single net_assets |
| `amount` (integer) | `amount` (bigint) | fact_grants | bigint not numeric — no cents |
| `ntee_code` (varchar) | Check length | varies | varchar(10) in most tables, varchar(4) in some |

---

## COMMON JOINS

```sql
-- Grants → Foundation details
fact_grants fg JOIN dim_foundations df ON fg.foundation_ein = df.ein

-- Grants → Recipient details
fact_grants fg JOIN dim_recipients dr ON fg.recipient_ein = dr.ein

-- Raw grants → Return filing
pf_grants pg JOIN pf_returns pr ON pg.return_id = pr.id

-- Foundation profiles
dim_foundations df JOIN calc_foundation_profiles cfp ON df.ein = cfp.ein

-- Client scoring
fact_foundation_client_scores fcs JOIN dim_foundations df ON fcs.foundation_ein = df.ein

-- Client siblings → their funders
calc_client_siblings cs JOIN calc_client_sibling_funders csf
  ON cs.client_ein = csf.client_ein

-- Foundation prospect enrichment
foundation_prospects2 fp2 JOIN foundation_enrichment fe ON fp2.ein = fe.ein

-- Officers from 990-PF filing
officers o JOIN pf_returns pr ON o.pf_return_id = pr.id

-- Officers from 990 filing
officers o JOIN nonprofit_returns nr ON o.np_return_id = nr.id

-- Best contact email for foundation
foundation_prospects2 fp2 JOIN web_best_email wbe ON fp2.ein = wbe.ein

-- Geographic relevance
mv_foundation_geo_relevance mgr WHERE mgr.state = 'CA' AND mgr.geo_tier = 'primary'
```

---

## HIGH-USE TABLES

### fact_grants (8.3M rows)
Cleaned grant records. **Use this for grant analysis, not pf_grants.**
`id` PK | `foundation_ein` FK→dim_foundations | `recipient_ein` FK→dim_recipients | `recipient_name_raw` | `recipient_state` | `recipient_city` | `amount` bigint | `purpose_text` varchar(1000) | `purpose_type` | `tax_year` int NOT NULL | `is_first_time` bool | `recipient_match_confidence` | `source` | `created_at`

### dim_foundations (143K rows)
One row per foundation. PK: `ein` varchar(10).
`name` | `state` | `city` | `ntee_code` | `ntee_broad` | `accepts_applications` bool | `grants_to_orgs` bool | `assets` bigint | `last_return_year` int | `created_at` | `updated_at`

### dim_recipients (1.65M rows)
One row per grant recipient. PK: `ein` varchar(10).
`name` | `state` | `city` | `ntee_code` | `ntee_broad` | `name_variants` text[] | `first_funded_year` | `last_funded_year` | `created_at` | `updated_at`

### dim_clients (8 rows)
TGS client organizations. PK: `id` serial.
`name` | `ein` | `state` | `city` | `sector_ntee` | `sector_broad` | `org_type` | `budget_tier` | `budget_min`/`budget_max` | `grant_size_seeking`/`_min`/`_max` | `grant_capacity` | `mission_text` | `project_need_text` | `project_type` | `project_keywords` | `populations_served` | `geographic_scope` | `known_funders` text[] | `recipient_ein` FK→dim_recipients | `email` | `status` | `matching_grant_keywords` | `excluded_keywords` | `target_grant_purpose` | `database_revenue`/`_assets` | `budget_variance_flag` | `client_data_quality` | `quality_flags` | `timeframe` | `questionnaire_date`/`_version` | `created_at` | `updated_at`

### pf_returns (638K rows)
990-PF filings, one row per filing year. PK: `id`. 94 columns.
Key: `ein` | `business_name` | `tax_year` | `state` | `total_assets_eoy_amt` numeric(15,2) | `grants_to_organizations_ind` bool | `only_contri_to_preselected_ind` bool | `website_url` | `email_address_txt` | `phone_num` | `application_submission_info` | `mission_desc` | `app_contact_name`/`_phone`/`_email` | `app_submission_deadlines` | `app_restrictions` | `app_form_requirements` | `total_grant_paid_amt` | `total_revenue_amt` | `qualifying_distributions_amt` | `ntee_code` | `ntee_source` | `private_operating_foundation_ind`

### pf_grants (1.76M rows)
Raw grant records from 990-PF. PK: `id`. FK: `return_id`→pf_returns.
`filer_ein` | `tax_year` | `recipient_ein` | `recipient_name` | `recipient_city`/`_state`/`_zip`/`_country` | `is_individual` bool | `amount` numeric(15,2) | `purpose` text | `relationship` | `recipient_foundation_status` | `grant_status`

### nonprofit_returns (2.96M rows)
990/990-EZ filings. PK: `id`. 91 columns.
Key: `ein` | `organization_name` | `tax_year` | `form_type` | `state` | `total_revenue`/`_expenses` numeric(15,2) | `total_assets_eoy`/`_boy` | `net_assets_eoy`/`_boy` | `mission_description` | `program_1_desc`/`_2_desc`/`_3_desc` | `program_1_expense_amt` | `ntee_code` | `total_employees_cnt` | `total_volunteers_cnt` | `website` | `phone`

### officers (26.3M rows)
Board/officers/key employees from all forms. PK: `id`.
`pf_return_id` FK→pf_returns | `np_return_id` FK→nonprofit_returns | `ein` | `tax_year` | `form_type` | `person_nm` | `title_txt` | `average_hours_per_week` | `compensation_amt` | `is_officer`/`is_director`/`is_trustee`/`is_key_employee`/`is_highest_compensated`/`is_former` bool | `employee_benefit_amt` | `expense_account_amt`

### calc_foundation_profiles (143K rows)
Aggregated giving metrics. PK: `ein` FK→dim_foundations.
`has_grant_history` | `total_grants_all_time`/`_5yr` | `total_giving_5yr` | `unique_recipients_5yr` | `last_active_year` | `median_grant`/`avg_grant` | `grant_range_min`/`_max` | `openness_score` numeric(3,2) | `repeat_rate` | `new_recipients_5yr` | `geographic_focus` jsonb | `sector_focus` jsonb | `project_types` | `typical_recipient_size` | `giving_trend` | `trend_pct_change` | `accepts_applications` | `calculated_at`

### foundation_prospects2 (143K rows, "fp2")
Flattened foundation master table for prospecting. PK: `id`, UNIQUE: `ein`.
`foundation_name` | `address_line1`/`_line2` | `city`/`state`/`zip` | `last_filing_year` | `app_submission_deadlines` | `app_restrictions` | `app_form_requirements` | `app_contact_name`/`_phone`/`_email` | `phone_num` | `activity_or_mission_desc` | `total_grant_paid_amt` | `total_assets_eoy_amt` | `grants_to_organizations_ind`/`only_contri_to_preselected_ind`/`private_operating_foundation_ind`/`grants_to_individuals_ind` | `website_url` | `bmf_status`/`_ico`/`_subsection`/`_foundation`/`_deductibility`/`_ruling`/`_ntee_cd`/`_org_type`/`_affiliation`/`_group_code`/`_classification`/`_activity` | `contact_name`/`_title`

### nonprofits_prospects2 (673K rows, "np2")
Flattened nonprofit master for email campaigns. PK: `id`, UNIQUE: `ein`.
`organization_name` | `most_recent_tax_year` | `city`/`state`/`zip` | `phone`/`website` | `mission_description` | `program_1_desc`/`_2_desc`/`_3_desc` | `ntee_code` | `total_employees_cnt`/`_volunteers_cnt` | `org_description` | `bmf_*` (12 BMF cols) | `ed_ceo_name`/`_title` | `president_name`/`_title` | `treasurer_name` | `vp_name`/`_title` | `chair_name`/`_title` | `all_officers` | `contact_email` | `contact_first_name` | `email_cohort_state`/`_sector` | `email_cohort_viable` | `email_priority_score` | `email_quality_tier` | `email_quality_flags` | `verification_status` | `verified_at`

### fact_foundation_client_scores (12.7K rows)
LASSO model scores per foundation-client pair. PK: (`foundation_ein`, `client_ein`).
`lasso_score` | `probability` | `semantic_similarity` | `model_version` | `calculated_at`

### calc_client_foundation_scores (4.8K rows)
Enriched client-foundation analysis. PK: (`client_ein`, `foundation_ein`).
`client_name`/`_state` | `foundation_name`/`_state`/`_total_assets` | `siblings_funded` | `grants_to_siblings` | `total_amount_to_siblings` | `median_grant_size_to_siblings` | `target_grants_to_siblings`/`_first_grants`/`_geo_grants` | `gold_standard_grants` | `most_recent_grant_year`/`_target_year` | `lasso_score` | `geo_eligible`/`open_to_applicants`/`client_eligible` bool | `eligibility_notes` | `has_active_opportunities` | `opportunity_notes`

### bmf (1.94M rows)
IRS Business Master File. PK: `ein`.
`name` | `ico` | `street`/`city`/`state`/`zip` | `group_code` | `subsection` | `affiliation` | `classification` | `ruling` | `deductibility` | `foundation` | `activity` | `organization` | `status` | `tax_period` | `asset_cd`/`_amt` | `income_cd`/`_amt` | `revenue_amt` | `ntee_cd` | `sort_name` | `source_file`

---

## EMAIL PIPELINE TABLES

### campaign_prospect_status (3.2K rows)
Email campaign tracking. PK: `id`.
`ein` | `email` | `org_name` | `org_type` | `vertical` | `campaign_status` | `initial_sent_at`/`_status`/`_subject`/`_sender` | `followup_sent_at`/`_status`/`_sender` | `replied`/`replied_at`/`reply_notes` | `bounced`/`bounced_at`/`bounce_reason` | `send_error`/`error_message`/`error_at` | `unsubscribed`/`unsubscribed_at` | `source_file` | `notes`

### cohort_foundation_lists_v2 (21.7K rows)
Foundation-cohort matches with fit scores. No PK. Logical key: (state, ntee_sector, foundation_rank).
`state` | `ntee_sector`/`sector_label` | `foundation_rank` | `foundation_ein`/`_name` | `total_giving_5yr` | `median_grant` | `unique_recipients`/`recent_recipients` | `last_active_year` | `assets` | `state_pct` | `geo_score`/`size_fit_score`/`openness_score`/`recency_score`/`volume_score` | `mega_penalty` | `email_fit_score` | `geo_tier` | `is_national_funder` | `accepts_applications` | `example_recipient_*` (name, ein, amount, purpose, year, match_tier, revenue) | `giving_trend`

### cohort_viability (882 rows)
State-sector cohort viability flags. PK: (state, ntee_sector).
`sector_label` | `foundation_count` | `prospect_count` | `avg_foundation_giving` | `viable` bool | `display_count` | `display_text`

### ref_foundation_email_exclusions (45 rows)
Foundations excluded from email campaigns. PK: `foundation_ein`.

### web_emails (104K rows), web_pages (268K rows), web_best_email (9.8K rows MV), web_staff (0 rows), web_org_metadata (0 rows)
See `2. Docs/data-dictionary.md` for full column details.

### global_bounce_list (276 rows, public schema)
PK: `email`. Bounced email addresses excluded from all campaigns.

---

## CLIENT PIPELINE TABLES

| Table | Rows | Purpose |
|-------|------|---------|
| calc_client_siblings | 2,100 | Similar orgs per client (client_ein, sibling_ein, similarity) |
| calc_client_sibling_funders | 168 | Foundations that fund client siblings |
| calc_client_sibling_grants | 13.4K | Individual grants to client siblings with keyword/purpose analysis |
| calc_client_proof_of_fit_grants | 25 | Best proof-of-fit grants per recommendation |
| calc_client_foundation_recommendations | 5 | Final top-N recommendations per client |
| foundation_enrichment | 374 | Manual/scraped enrichment (deadlines, contacts, viability) |

---

## OTHER TABLES

| Table | Rows | Purpose |
|-------|------|---------|
| calc_foundation_features | 143K | ML feature matrix for foundations |
| calc_recipient_features | 1.65M | ML feature matrix for recipients |
| mv_foundation_geo_relevance | 426K | Materialized view: state giving %, geo_tier |
| stg_foundation_state_dist | — | State distribution staging |
| stg_foundation_sector_dist | — | Sector distribution staging |
| org_url_enrichment | 814K | URL enrichment status tracking |
| import_log | 748K | ETL run tracking |
| ref_state_regions | 51 | State → region mapping |
| ref_org_aliases | 150 | Manual org alias → EIN |
| ref_recipient_alias_mappings | 129 | Recipient name → canonical EIN |
| research_events | 273 | Fundraising events for prospecting |
| schedule_a/d/f/i/j/o/r | varies | IRS schedule child tables (FK→nonprofit_returns.id) |
| pf_balance_sheet/investments/revenue_expenses/capital_gains | varies | PF schedule tables (FK→pf_returns.id) |
| contractors | — | Contractor records (FK→pf_returns + nonprofit_returns) |

---

## VIEWS

| View | Purpose |
|------|---------|
| vw_foundation_summary | Simplified foundation summary from pf_returns |
| sales_prospects | Union of NP + FDN prospects for CRM |
| v_campaign_prospects | Campaign status joined with prospect details |
| v_suppress_list | Emails to suppress (bounced/replied/unsubscribed) |
| v_suppress_list_by_ein | EINs to suppress from outreach |
| v_email_preflight_* | QC views for email campaign preflight checks |
| grant_purpose_quality | Purpose text quality classification |
| prospects_with_events | Prospects joined with fundraising events |

---

## FILTER PATTERNS

```sql
-- Open to applications
(only_contri_to_preselected_ind = FALSE OR only_contri_to_preselected_ind IS NULL)

-- Active foundations (production filter)
WHERE has_grant_history = TRUE AND assets >= 100000
  AND unique_recipients_5yr >= 5 AND accepts_applications = TRUE

-- Valid website (exclude junk)
WHERE website_url IS NOT NULL
  AND website_url NOT IN ('N/A', 'NONE', '0', '')

-- Valid EIN (always VARCHAR, preserve leading zeros)
WHERE ein ~ '^\d{9}$'
```
