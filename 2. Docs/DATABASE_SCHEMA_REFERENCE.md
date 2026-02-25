# DATABASE_SCHEMA_REFERENCE

**Schema:** f990_2025
**Database:** thegrantscout (localhost:5432)
**Last Updated:** 2026-02-25

A human-readable overview of all tables, materialized views, and views in the f990_2025 schema.

---

## Table of Contents

1. [Core Data](#core-data)
2. [Dimension Tables](#dimension-tables)
3. [Fact Tables](#fact-tables)
4. [Calculated Tables](#calculated-tables)
5. [Prospect Tables](#prospect-tables)
6. [Email Pipeline](#email-pipeline)
7. [Web Scraping](#web-scraping)
8. [Reference Tables](#reference-tables)
9. [Staging / ETL](#staging--etl)
10. [Materialized Views](#materialized-views)
11. [Views](#views)

---

## Core Data

IRS tax return filings and their associated schedule data, parsed from XML.

### pf_returns
- **Rows:** 638,082
- **Purpose:** Private foundation 990-PF tax return filings, one row per filing per tax year.
- **Primary Key:** `id` (serial)
- **Key Columns:** `ein`, `business_name`, `state`, `tax_year`, `total_assets_eoy_amt`, `total_grant_paid_amt`, `grants_to_organizations_ind`, `only_contri_to_preselected_ind`, `website_url`, `phone_num`
- **Foreign Keys:** None outbound. Referenced by `pf_grants.return_id`, `officers.pf_return_id`, `pf_balance_sheet.pf_return_id`, `pf_capital_gains.pf_return_id`, `pf_investments.pf_return_id`, `pf_revenue_expenses.pf_return_id`.
- **Column Reference:** `pf_returns_column_reference.md`

### pf_grants
- **Rows:** 1,758,527
- **Purpose:** Raw individual grant records from 990-PF Schedule I (Part XV), one row per grant.
- **Primary Key:** `id` (serial)
- **Key Columns:** `filer_ein`, `tax_year`, `recipient_ein`, `recipient_name`, `recipient_state`, `amount`, `purpose`, `is_individual`
- **Foreign Keys:** `return_id` -> `pf_returns.id` (CASCADE delete)

### nonprofit_returns
- **Rows:** 2,956,959
- **Purpose:** 990 and 990-EZ nonprofit tax return filings, one row per filing per tax year.
- **Primary Key:** `id` (serial)
- **Key Columns:** `ein`, `organization_name`, `tax_year`, `form_type`, `state`, `total_revenue`, `total_expenses`, `net_assets_eoy`, `net_assets_boy`, `mission_description`, `program_1_desc`
- **Foreign Keys:** None outbound. Referenced by `officers.np_return_id`, `schedule_a.np_return_id`, `schedule_i_grants.np_return_id`, and other schedule tables.
- **Column Reference:** `nonprofit_returns_column_reference.md`

### officers
- **Rows:** 26,281,615
- **Purpose:** Board members, officers, trustees, and key employees from all form types.
- **Primary Key:** `id` (serial)
- **Key Columns:** `ein`, `tax_year`, `form_type`, `person_nm`, `title_txt`, `compensation_amt`, `is_officer`, `is_director`, `is_trustee`, `is_key_employee`
- **Foreign Keys:** `pf_return_id` -> `pf_returns.id`, `np_return_id` -> `nonprofit_returns.id`
- **Column Reference:** `officers_column_reference.md`

### contractors
- **Rows:** 107,020
- **Purpose:** Independent contractors paid >$100K, from 990 Part VII Section B and 990-PF Part VIII.
- **Primary Key:** `id` (serial)
- **Key Columns:** `ein`, `tax_year`, `contractor_name`, `service_desc`, `compensation_amt`
- **Foreign Keys:** `np_return_id` -> `nonprofit_returns.id`, `pf_return_id` -> `pf_returns.id`
- **Column Reference:** `contractors_column_reference.md`

### Schedule Tables

| Table | Rows | Purpose | PK | Key Columns |
|-------|-----:|---------|-----|-------------|
| schedule_a | 574,037 | Charity classification (509(a) status) | id | ein, tax_year, church_ind, school_ind, hospital_ind, public_charity_509a1_ind |
| schedule_d_endowments | 36,936 | Endowment fund details | id | ein, tax_year, endowment_boy_amt, contributions_amt |
| schedule_f_grants | 81,561 | Foreign grants (990 Schedule F) | id | filer_ein, tax_year, region, cash_grant_amt |
| schedule_i_grants | 996,940 | Grants to orgs/individuals (990 Schedule I) | id | filer_ein, tax_year, recipient_ein, recipient_name, amount, purpose |
| schedule_j_compensation | 286,308 | Executive compensation details | id | ein, tax_year, person_nm, base_compensation_org_amt |
| schedule_o_narratives | 2,950,168 | Supplemental explanations (Schedule O) | id | ein, tax_year, form_and_line_ref, explanation_txt |
| schedule_r_related_orgs | 850,773 | Related organizations (Schedule R) | id | filer_ein, tax_year, related_org_name, related_org_ein |

### Financial Detail Tables

| Table | Rows | Purpose | PK | Key Columns |
|-------|-----:|---------|-----|-------------|
| pf_balance_sheet | 679,634 | 990-PF balance sheet line items | id | ein, tax_year, line_item, boy_amt, eoy_amt, eoy_fmv_amt |
| pf_capital_gains | 3,740,163 | 990-PF capital gains/losses | id | ein, tax_year, property_desc, gross_sales_price_amt |
| pf_investments | 1,844,771 | 990-PF investment holdings | id | ein, tax_year, investment_type, description, fmv_eoy_amt |
| pf_revenue_expenses | 1,353,353 | 990-PF revenue/expense line items | id | ein, tax_year, line_item, rev_and_expenses_amt |
| np_balance_sheet | 2,717,584 | 990 balance sheet line items | id | ein, tax_year, line_item, boy_amt, eoy_amt |
| np_functional_expenses | 360,191 | 990 Part IX functional expense breakdown | id | ein, tax_year, grants_to_domestic_orgs_amt, other_salaries_wages_amt |

---

## Dimension Tables

Canonical identity tables with one row per entity.

### dim_foundations
- **Rows:** 143,184
- **Purpose:** Master table of unique private foundations, one row per foundation EIN.
- **Primary Key:** `ein`
- **Key Columns:** `ein`, `name`, `state`, `city`, `ntee_code`, `ntee_broad`, `accepts_applications`, `grants_to_orgs`, `assets`, `last_return_year`
- **Foreign Keys:** Referenced by `fact_grants.foundation_ein`, `calc_foundation_profiles.ein`, `calc_foundation_features.ein`
- **Column Reference:** `dim_foundations_column_reference.md`

### dim_recipients
- **Rows:** 1,652,766
- **Purpose:** Master table of unique grant recipients matched to EINs.
- **Primary Key:** `ein`
- **Key Columns:** `ein`, `name`, `state`, `city`, `ntee_code`, `ntee_broad`, `name_variants`, `first_funded_year`, `last_funded_year`
- **Foreign Keys:** Referenced by `fact_grants.recipient_ein`, `calc_recipient_features.ein`
- **Column Reference:** `dim_recipients_column_reference.md`

### dim_clients
- **Rows:** 8
- **Purpose:** TheGrantScout client organizations for grant matching and report generation.
- **Primary Key:** `id` (serial)
- **Key Columns:** `id`, `name`, `ein`, `state`, `sector_ntee`, `mission_text`, `project_need_text`, `known_funders`, `recipient_ein`, `status`
- **Foreign Keys:** `recipient_ein` -> `dim_recipients.ein`. Referenced by `fact_foundation_client_scores.client_ein`, `calc_client_*` tables.
- **Column Reference:** `dim_clients_column_reference.md`

---

## Fact Tables

Transactional records and computed scores.

### fact_grants
- **Rows:** 8,310,650
- **Purpose:** Cleaned and EIN-matched grant records, one row per grant.
- **Primary Key:** `id` (serial)
- **Key Columns:** `foundation_ein`, `recipient_ein`, `amount`, `purpose_text`, `tax_year`, `is_first_time`, `recipient_match_confidence`
- **Foreign Keys:** `foundation_ein` -> `dim_foundations.ein`, `recipient_ein` -> `dim_recipients.ein`
- **Column Reference:** `fact_grants_column_reference.md`
- **IMPORTANT:** Column is `foundation_ein` (NOT filer_ein), column is `purpose_text` (NOT purpose).

### fact_foundation_client_scores
- **Rows:** 12,652
- **Purpose:** LASSO V6.1 model scores pairing each eligible foundation with each client.
- **Primary Key:** (`foundation_ein`, `client_ein`) composite
- **Key Columns:** `foundation_ein`, `client_ein`, `lasso_score`, `probability`, `semantic_similarity`, `model_version`
- **Foreign Keys:** `foundation_ein` -> `dim_foundations.ein`, `client_ein` -> `dim_clients.ein`
- **Column Reference:** `fact_foundation_client_scores_column_reference.md`

---

## Calculated Tables

Pre-computed aggregations and ML features.

### calc_foundation_profiles
- **Rows:** 143,184
- **Purpose:** Aggregated giving metrics and behavior profiles for every foundation.
- **Primary Key:** `ein`
- **Key Columns:** `ein`, `has_grant_history`, `total_grants_5yr`, `total_giving_5yr`, `unique_recipients_5yr`, `median_grant`, `openness_score`, `repeat_rate`, `giving_trend`
- **Foreign Keys:** `ein` -> `dim_foundations.ein`
- **Column Reference:** `calc_foundation_profiles_column_reference.md`

### calc_foundation_features
- **Rows:** 143,184
- **Purpose:** Comprehensive feature vectors (95 columns) for LASSO model training and scoring.
- **Primary Key:** `ein`
- **Key Columns:** `ein`, `name`, `state`, `ntee_code`, `accepts_applications`, `dim_assets`, `openness_score`, `repeat_rate`, `median_grant` (+ 85 more feature columns)
- **Foreign Keys:** `ein` -> `dim_foundations.ein`

### calc_client_foundation_scores
- **Rows:** 4,816
- **Purpose:** Sibling-based foundation scoring: how many client siblings a foundation has funded.
- **Primary Key:** None (composite on `client_ein`, `foundation_ein`)
- **Key Columns:** `client_ein`, `foundation_ein`, `foundation_name`, `siblings_funded`, `grants_to_siblings`, `total_amount_to_siblings`, `median_grant_size_to_siblings`

### calc_client_siblings
- **Rows:** 2,100
- **Purpose:** Organizations similar to each client (budget-matched, same sector/state) for sibling analysis.
- **Primary Key:** None (composite on `client_ein`, `sibling_ein`)
- **Key Columns:** `client_ein`, `sibling_ein`, `similarity`, `client_budget`, `sibling_budget`, `budget_ratio`

### calc_client_sibling_funders
- **Rows:** 168
- **Purpose:** Foundations that fund client siblings, aggregated per foundation-client pair.
- **Primary Key:** None (composite on `client_ein`, `foundation_ein`)
- **Key Columns:** `client_ein`, `foundation_ein`, `siblings_funded`, `total_grants`, `total_amount`, `avg_grant`

### calc_client_sibling_grants
- **Rows:** 13,389
- **Purpose:** Individual grants from foundations to client siblings, used for proof-of-fit evidence.
- **Primary Key:** None
- **Key Columns:** `client_ein`, `foundation_ein`, `sibling_ein`, `grant_id`, `amount`, `tax_year`, `purpose_text`

### calc_client_proof_of_fit_grants
- **Rows:** 25
- **Purpose:** Curated grant examples demonstrating foundation-client fit for report narratives.
- **Primary Key:** `id` (serial)
- **Key Columns:** `client_ein`, `foundation_ein`, `recipient_name`, `amount`, `purpose_text`, `tax_year`, `fit_reason`

### calc_client_foundation_recommendations
- **Rows:** 5
- **Purpose:** Final ranked foundation recommendations per client, used in report generation.
- **Primary Key:** `id` (serial)
- **Key Columns:** `client_ein`, `foundation_ein`, `rank`, `fit_score`, `eligibility_status`, `annual_giving`, `grant_count`

### calc_recipient_features
- **Rows:** 1,652,766
- **Purpose:** Comprehensive recipient feature vectors (74 columns) for analysis and ML.
- **Primary Key:** `ein`
- **Key Columns:** `ein`, `name`, `state`, `ntee_code`, `total_funders`, `total_grants`, `total_funding_received`

---

## Prospect Tables

Enriched prospect records for sales outreach, combining IRS data with BMF and officer information.

### foundation_prospects2 (fp2)
- **Rows:** 143,184
- **Purpose:** Canonical foundation prospect table with 990-PF data, BMF enrichment, and contact info.
- **Primary Key:** `id` (serial), unique on `ein`
- **Key Columns:** `ein`, `foundation_name`, `state`, `total_assets_eoy_amt`, `total_grant_paid_amt`, `website_url`, `app_contact_email`, `only_contri_to_preselected_ind`, `bmf_ntee_cd`
- **Foreign Keys:** `ein` references `dim_foundations.ein` (logical, not enforced)
- **Column Reference:** `foundation_prospects2_column_reference.md`

### nonprofits_prospects2 (np2)
- **Rows:** 673,381
- **Purpose:** Canonical nonprofit prospect table with 990/990-EZ data, BMF enrichment, officer names, and email campaign fields.
- **Primary Key:** `id`
- **Key Columns:** `ein`, `organization_name`, `state`, `most_recent_tax_year`, `mission_description`, `contact_email`, `contact_first_name`, `email_quality_tier`, `email_priority_score`, `ed_ceo_name`
- **Column Reference:** `nonprofits_prospects2_column_reference.docx`

### foundation_enrichment
- **Rows:** 374
- **Purpose:** Manually researched foundation application details (deadlines, URLs, contacts) cached for report generation.
- **Primary Key:** `id` (serial)
- **Key Columns:** `ein`, `accepts_unsolicited`, `application_type`, `application_url`, `current_deadline`, `contact_name`, `contact_email`

### research_events
- **Rows:** 273
- **Purpose:** Fundraising/networking events data for prospect enrichment and outreach timing.
- **Primary Key:** `event_id`
- **Key Columns:** `source`, `org_name_raw`, `event_name`, `event_date`, `event_state`, `matched_ein`, `is_active`

---

## Email Pipeline

Tables supporting the cold email outreach pipeline.

### campaign_prospect_status
- **Rows:** 3,185
- **Purpose:** Email campaign tracking: send history, replies, bounces, and errors per prospect.
- **Primary Key:** `id` (serial)
- **Key Columns:** `ein`, `email`, `org_name`, `org_type`, `vertical`, `campaign_status`, `replied`, `bounced`, `unsubscribed`
- **Column Reference:** `campaign_prospect_status_column_reference.md`

### cohort_foundation_lists (v1)
- **Rows:** 13,002
- **Purpose:** Version 1 foundation lists per state-sector cohort for email personalization.
- **Primary Key:** None (composite on `cohort_id`, `foundation_rank`)
- **Key Columns:** `cohort_id`, `state`, `ntee_sector`, `foundation_ein`, `foundation_name`, `total_giving_5yr`, `median_grant`

### cohort_foundation_lists_v2
- **Rows:** 21,667
- **Purpose:** Version 2 foundation lists with composite email_fit_score and example grant matches.
- **Primary Key:** None (composite on `state`, `ntee_sector`, `foundation_rank`)
- **Key Columns:** `state`, `ntee_sector`, `foundation_ein`, `foundation_name`, `email_fit_score`, `geo_tier`, `example_recipient_name`, `example_grant_amount`, `giving_trend`

### cohort_viability
- **Rows:** 882
- **Purpose:** State-sector cohort viability assessment: whether enough foundations exist for a credible email.
- **Primary Key:** None (composite on `state`, `ntee_sector`)
- **Key Columns:** `state`, `ntee_sector`, `sector_label`, `foundation_count`, `prospect_count`, `viable`, `display_count`, `display_text`

### ref_foundation_email_exclusions
- **Rows:** 45
- **Purpose:** Foundations excluded from email campaigns (invitation-only, geographic monopolies, patient assistance, micro-grant DAFs).
- **Primary Key:** `foundation_ein`
- **Key Columns:** `foundation_ein`, `foundation_name`, `exclusion_reason`, `exclusion_category`, `notes`

---

## Web Scraping

Tables storing website scraping results for contact and metadata enrichment.

### org_url_enrichment
- **Rows:** 813,698
- **Purpose:** URL enrichment and scrape pipeline tracking for both foundations and nonprofits.
- **Primary Key:** `ein`
- **Key Columns:** `ein`, `org_type`, `website_raw`, `website_clean`, `url_validated`, `scrape_status`, `scrape_pages_fetched`, `verification_score`, `app_contact_email`

### web_pages
- **Rows:** 267,734
- **Purpose:** Metadata for fetched HTML pages (HTML content stored on disk in gzip cache).
- **Primary Key:** `id` (serial)
- **Key Columns:** `ein`, `url`, `page_type`, `http_status`, `html_size_bytes`, `fetched_at`

### web_emails
- **Rows:** 103,773
- **Purpose:** All emails extracted from organization websites, one row per unique email per org.
- **Primary Key:** `id` (serial), unique on (`ein`, `email`)
- **Key Columns:** `ein`, `email`, `email_type`, `domain_matches_website`, `person_name`, `confidence`, `mx_valid`

### web_staff
- **Rows:** 0 (not yet populated)
- **Purpose:** Staff members extracted from team/leadership/board pages on websites.
- **Primary Key:** `id` (serial)
- **Key Columns:** `ein`, `person_name`, `title`, `email`, `staff_type`, `extraction_confidence`

### web_org_metadata
- **Rows:** 0 (not yet populated)
- **Purpose:** Organization metadata extracted from websites (meta tags, social URLs, mission text).
- **Primary Key:** `ein`
- **Key Columns:** `ein`, `meta_description`, `mission_text`, `twitter_url`, `linkedin_url`, `cms_platform`

---

## Reference Tables

Static or slowly-changing lookup data.

### bmf
- **Rows:** 1,935,635
- **Purpose:** IRS Business Master File -- reference data for all tax-exempt organizations.
- **Primary Key:** `ein`
- **Key Columns:** `ein`, `name`, `state`, `ntee_cd`, `subsection`, `foundation`, `asset_amt`, `income_amt`, `status`
- **Column Reference:** `bmf_column_reference.md`

### ref_state_regions
- **Rows:** 51
- **Purpose:** Maps state codes to Census regions and divisions.
- **Primary Key:** `state_code`
- **Key Columns:** `state_code`, `region`, `division`

### ref_org_aliases
- **Rows:** 150
- **Purpose:** Manual alias-to-EIN mappings for organizations with common abbreviations or name variants.
- **Primary Key:** None (unique on `alias`)
- **Key Columns:** `alias`, `ein`

### ref_recipient_alias_mappings
- **Rows:** 129
- **Purpose:** Verified recipient name-to-canonical-EIN mappings for grant matching.
- **Primary Key:** None (composite on `alias_name`, `alias_state`)
- **Key Columns:** `alias_name`, `alias_state`, `canonical_ein`, `canonical_name`, `source`, `verified_date`

---

## Staging / ETL

Import tracking and intermediate processing tables.

### import_log
- **Rows:** 748,311
- **Purpose:** ETL run tracking: each row records a single XML file import attempt.
- **Primary Key:** `id` (serial)
- **Key Columns:** `import_run_id`, `started_at`, `completed_at`, `source_file`, `form_type`, `tax_year`, `records_processed`, `records_success`, `status`

### stg_foundation_sector_dist
- **Rows:** 588,064
- **Purpose:** Pre-computed foundation grant distribution by NTEE sector.
- **Primary Key:** None (composite on `foundation_ein`, `ntee_broad`)
- **Key Columns:** `foundation_ein`, `ntee_broad`, `grant_count`, `total_grants`, `sector_pct`

### stg_foundation_state_dist
- **Rows:** 527,598
- **Purpose:** Pre-computed foundation grant distribution by recipient state.
- **Primary Key:** None (composite on `foundation_ein`, `recipient_state`)
- **Key Columns:** `foundation_ein`, `recipient_state`, `grant_count`, `total_grants`, `state_pct`

---

## Materialized Views

Pre-computed views refreshed on demand.

### web_best_email
- **Rows:** 9,844
- **Purpose:** Best email per organization, ranked by domain match, MX validity, email type, and confidence. Only includes emails where syntax_valid = TRUE AND domain_matches_website = TRUE.
- **Key Columns:** `ein`, `email`, `email_type`, `person_name`, `person_title`, `confidence`, `mx_valid`

### mv_foundation_geo_relevance
- **Rows:** 425,794
- **Purpose:** Foundation geographic relevance by state, with tiering (primary/secondary/tertiary/incidental). Used for email cohort building.
- **Key Columns:** `foundation_ein`, `state`, `state_pct`, `grant_count`, `state_giving_dollars`, `geo_tier`, `is_national_funder`
- **Refresh:** `REFRESH MATERIALIZED VIEW CONCURRENTLY f990_2025.mv_foundation_geo_relevance;`

---

## Views

Virtual views computed on the fly from underlying tables.

| View | Purpose | Underlying Tables |
|------|---------|-------------------|
| `grant_purpose_quality` | Classifies each grant's purpose_text quality (specific, generic_general, too_short, empty, reference_only) | fact_grants |
| `vw_foundation_summary` | Foundation summary with application status label from pf_returns | pf_returns |
| `sales_prospects` | Unified sales prospect list combining nonprofit and foundation prospects | grantscout_campaign.nonprofit_prospects, grantscout_campaign.foundation_prospects |
| `prospects_with_events` | Nonprofit prospects joined with upcoming active research events | grantscout_campaign.nonprofit_prospects, research_events |
| `v_campaign_prospects` | Enriched campaign prospect view for outreach management | campaign_prospect_status (+ enrichment) |
| `v_email_preflight_prospect_quality` | Pre-flight QC: prospect data quality checks before email send | nonprofits_prospects2 |
| `v_email_preflight_example_quality` | Pre-flight QC: validates example grant matches in cohort foundation lists | cohort_foundation_lists_v2 |
| `v_email_preflight_overcitation` | Pre-flight QC: flags foundations appearing in too many cohorts | cohort_foundation_lists_v2 |
| `v_suppress_list` | Email suppression list (bounced, unsubscribed, errored addresses) | campaign_prospect_status |
| `v_suppress_list_by_ein` | EIN-level suppression list for organizations already contacted | campaign_prospect_status |

---

## Backup Tables

| Table | Purpose |
|-------|---------|
| `_bak_sales_foundation_prospects` | Backup of legacy foundation prospect data |
| `_bak_sales_nonprofit_prospects` | Backup of legacy nonprofit prospect data |

---

## Quick Reference: Table Counts

| Category | Table | Rows |
|----------|-------|-----:|
| Core | pf_returns | 638,082 |
| Core | pf_grants | 1,758,527 |
| Core | nonprofit_returns | 2,956,959 |
| Core | officers | 26,281,615 |
| Core | contractors | 107,020 |
| Dimension | dim_foundations | 143,184 |
| Dimension | dim_recipients | 1,652,766 |
| Dimension | dim_clients | 8 |
| Fact | fact_grants | 8,310,650 |
| Fact | fact_foundation_client_scores | 12,652 |
| Calculated | calc_foundation_profiles | 143,184 |
| Calculated | calc_foundation_features | 143,184 |
| Calculated | calc_recipient_features | 1,652,766 |
| Calculated | calc_client_foundation_scores | 4,816 |
| Calculated | calc_client_siblings | 2,100 |
| Calculated | calc_client_sibling_funders | 168 |
| Calculated | calc_client_sibling_grants | 13,389 |
| Calculated | calc_client_proof_of_fit_grants | 25 |
| Calculated | calc_client_foundation_recommendations | 5 |
| Prospect | foundation_prospects2 | 143,184 |
| Prospect | nonprofits_prospects2 | 673,381 |
| Prospect | foundation_enrichment | 374 |
| Prospect | research_events | 273 |
| Email | campaign_prospect_status | 3,185 |
| Email | cohort_foundation_lists | 13,002 |
| Email | cohort_foundation_lists_v2 | 21,667 |
| Email | cohort_viability | 882 |
| Email | ref_foundation_email_exclusions | 45 |
| Web | org_url_enrichment | 813,698 |
| Web | web_pages | 267,734 |
| Web | web_emails | 103,773 |
| Web | web_staff | 0 |
| Web | web_org_metadata | 0 |
| Reference | bmf | 1,935,635 |
| Reference | ref_state_regions | 51 |
| Reference | ref_org_aliases | 150 |
| Reference | ref_recipient_alias_mappings | 129 |
| Staging | import_log | 748,311 |
| Staging | stg_foundation_sector_dist | 588,064 |
| Staging | stg_foundation_state_dist | 527,598 |
| Schedule | schedule_a | 574,037 |
| Schedule | schedule_d_endowments | 36,936 |
| Schedule | schedule_f_grants | 81,561 |
| Schedule | schedule_i_grants | 996,940 |
| Schedule | schedule_j_compensation | 286,308 |
| Schedule | schedule_o_narratives | 2,950,168 |
| Schedule | schedule_r_related_orgs | 850,773 |
| Financial | pf_balance_sheet | 679,634 |
| Financial | pf_capital_gains | 3,740,163 |
| Financial | pf_investments | 1,844,771 |
| Financial | pf_revenue_expenses | 1,353,353 |
| Financial | np_balance_sheet | 2,717,584 |
| Financial | np_functional_expenses | 360,191 |
| Matview | web_best_email | 9,844 |
| Matview | mv_foundation_geo_relevance | 425,794 |
