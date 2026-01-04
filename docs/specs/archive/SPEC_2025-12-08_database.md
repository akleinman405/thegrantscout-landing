# DATABASE_SPEC.md

**Document Type:** SPEC
**Purpose:** Final database architecture for TheGrantScout
**Date:** 2025-12-08
**Version:** 1.0

---

## Table of Contents

1. [Schema Overview](#1-schema-overview)
2. [Core Tables](#2-core-tables)
3. [Derived Tables](#3-derived-tables)
4. [Source Tables](#4-source-tables)
5. [Current State](#5-current-state)
6. [Build Tasks](#6-build-tasks)
7. [Source Files](#7-source-files)

---

## 1. Schema Overview

### Database Technology

| Component | Value |
|-----------|-------|
| **Database** | PostgreSQL 15+ |
| **Host** | 172.26.16.1 |
| **Port** | 5432 |
| **Database Name** | postgres |
| **Primary Schema** | f990_2025 |
| **Extensions** | pg_trgm (fuzzy matching), btree_gin (GIN indexes) |
| **Optional Future** | pgvector (semantic search - not yet implemented) |

### All Tables at a Glance

| Schema | Table | Purpose | Records | Status |
|--------|-------|---------|---------|--------|
| f990_2025 | pf_returns | Private foundation 990-PF filings | 42,855 | Populated |
| f990_2025 | pf_grants | Individual grant records | 440,868 | Populated |
| f990_2025 | nonprofit_returns | 990/990-EZ nonprofit filings | 220,245 | Populated |
| f990_2025 | officers | Board/officers from all forms | 41,641 | Populated |
| f990_2025 | schedule_a | Charity classifications | 220,245 | Populated |
| f990_2025 | import_log | ETL tracking | ~8 | Populated |
| public | foundations | Enriched foundation profiles | 85,470 | Populated |
| public | historical_grants | Processed grant history | 1,621,833 | Populated |
| public | current_grants | Active opportunities | 42 | Partial |
| public | nonprofits | Client nonprofit profiles | 4 | Partial |
| public | matches | Generated match results | 317 | Populated |
| public | board_members | Board overlap data | 0 | Empty |
| public | network_relationships | Foundation relationships | 0 | Empty |
| public | foundation_temporal_patterns | Giving cycle patterns | 0 | Empty |
| public | application_outcomes | Learning loop tracking | 0 | Empty |
| public | f990_foundations | Raw foundation source | 85,470 | Populated |
| public | f990_grants | Raw grants source | 1,624,501 | Populated |
| public | f990_officers | Raw officer data | 41,124 | Populated |
| public | irs_bmf | IRS Business Master File | 1,898,175 | Populated |

### Entity Relationship Diagram (ERD)

```
                            ┌─────────────────────┐
                            │    pf_returns       │
                            │   (42,855 rows)     │
                            │   Private Fndns     │
                            └─────────┬───────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │ 1:N                   │ 1:N                   │ 1:N
              ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │   pf_grants     │     │    officers     │     │  (No Schedule)  │
    │  (440,868 rows) │     │  (41,641 rows)  │     │                 │
    │  Grant Records  │     │  Board/Officers │     │                 │
    └─────────────────┘     └─────────────────┘     └─────────────────┘

                            ┌─────────────────────┐
                            │  nonprofit_returns  │
                            │  (220,245 rows)     │
                            │  990/990-EZ Orgs    │
                            └─────────┬───────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │ 1:N                   │ 1:1                   │
              ▼                       ▼                       │
    ┌─────────────────┐     ┌─────────────────┐              │
    │    officers     │     │   schedule_a    │              │
    │  (shared table) │     │  (220,245 rows) │              │
    │                 │     │  509(a) Status  │              │
    └─────────────────┘     └─────────────────┘              │


═══════════════════════════════════════════════════════════════════
                    PRODUCTION TABLES (PUBLIC SCHEMA)
═══════════════════════════════════════════════════════════════════

    ┌─────────────────┐                    ┌─────────────────┐
    │   foundations   │◄───────────────────│   nonprofits    │
    │  (85,470 rows)  │   Matched via      │   (4 rows)      │
    │  Enriched Fndns │   Scoring Algo     │  Client Profiles│
    └────────┬────────┘                    └────────┬────────┘
             │                                      │
             │ 1:N                                  │ 1:N
             ▼                                      ▼
    ┌─────────────────┐                    ┌─────────────────┐
    │historical_grants│                    │     matches     │
    │ (1.6M rows)     │                    │   (317 rows)    │
    │ Grant History   │◄───────────────────│ Score + Reason  │
    └─────────────────┘                    └─────────────────┘
                                                    │
                                                    ▼
                                           ┌─────────────────┐
                                           │ current_grants  │
                                           │   (42 rows)     │
                                           │ Active Opps     │
                                           └─────────────────┘
```

---

## 2. Core Tables

### 2.1 pf_returns (Private Foundation Returns)

**Purpose:** Stores Form 990-PF data for private foundations - the primary source for grant-making foundations.

**Schema:** f990_2025

**Row Count:** 42,855

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NO | Primary key |
| ein | VARCHAR(20) | NO | Employer Identification Number |
| business_name | TEXT | YES | Foundation name |
| tax_year | INTEGER | YES | Tax year of filing (2021-2024) |
| tax_period_begin | DATE | YES | Start of tax period |
| tax_period_end | DATE | YES | End of tax period |
| source_file | TEXT | YES | Original XML file path |
| return_timestamp | TIMESTAMP | YES | When return was filed |
| object_id | VARCHAR(100) | YES | IRS object identifier |
| address_line1 | TEXT | YES | Street address |
| address_line2 | TEXT | YES | Address line 2 |
| city | TEXT | YES | City |
| state | VARCHAR(50) | YES | State code |
| zip | VARCHAR(20) | YES | ZIP code |
| country | TEXT | YES | Country |
| phone_num | VARCHAR(50) | YES | Phone number |
| email_address_txt | TEXT | YES | Email address |
| website_url | TEXT | YES | Website URL |
| contributing_manager_nm | TEXT | YES | Contributing manager name |
| private_operating_foundation_ind | BOOLEAN | YES | Is private operating foundation |
| exempt_operating_foundations_ind | BOOLEAN | YES | Is exempt operating foundation |
| **grants_to_organizations_ind** | BOOLEAN | YES | **Makes grants to organizations** |
| grants_to_individuals_ind | BOOLEAN | YES | Makes grants to individuals |
| total_revenue_amt | NUMERIC(15,2) | YES | Total revenue |
| total_expenses_amt | NUMERIC(15,2) | YES | Total expenses |
| total_assets_boy_amt | NUMERIC(15,2) | YES | Total assets beginning of year |
| total_assets_eoy_amt | NUMERIC(15,2) | YES | Total assets end of year |
| net_assets_boy_amt | NUMERIC(15,2) | YES | Net assets beginning of year |
| net_assets_eoy_amt | NUMERIC(15,2) | YES | Net assets end of year |
| contributions_received_amt | NUMERIC(15,2) | YES | Contributions received |
| investment_income_amt | NUMERIC(15,2) | YES | Investment income |
| distributable_as_adjusted_amt | NUMERIC(15,2) | YES | Distributable amount (adjusted) |
| qualifying_distributions_amt | NUMERIC(15,2) | YES | Qualifying distributions |
| total_grant_paid_amt | NUMERIC(15,2) | YES | Total grants paid |
| total_grant_approved_future_amt | NUMERIC(15,2) | YES | Grants approved for future |
| undistributed_income_cy_amt | NUMERIC(15,2) | YES | Undistributed income current year |
| undistributed_income_py_ind | BOOLEAN | YES | Has undistributed prior year income |
| **only_contri_to_preselected_ind** | BOOLEAN | YES | **KEY: Only gives to preselected** |
| application_submission_info | JSONB | YES | Application submission details |
| mission_desc | TEXT | YES | Mission description |
| activity_or_mission_desc | TEXT | YES | Activity/mission description |
| primary_exempt_purpose | TEXT | YES | Primary exempt purpose |
| activity_code_1 | VARCHAR(20) | YES | NTEE activity code 1 |
| activity_code_2 | VARCHAR(20) | YES | NTEE activity code 2 |
| activity_code_3 | VARCHAR(20) | YES | NTEE activity code 3 |
| foreign_activities_ind | BOOLEAN | YES | Has foreign activities |
| created_at | TIMESTAMP | YES | Record creation timestamp |
| updated_at | TIMESTAMP | YES | Record update timestamp |

**Indexes:**
- `idx_pf_returns_ein` ON ein
- `idx_pf_returns_tax_year` ON tax_year
- `idx_pf_returns_state` ON state
- `idx_pf_returns_grants_to_orgs` ON grants_to_organizations_ind WHERE TRUE
- `idx_pf_returns_only_preselected` ON only_contri_to_preselected_ind WHERE FALSE
- `idx_pf_returns_distributable` ON distributable_as_adjusted_amt WHERE NOT NULL

**Constraints:** None beyond NOT NULL on ein

**Population Status:**
| Field | Populated | Rate |
|-------|-----------|------|
| total_assets_eoy_amt | 42,855 | 100% |
| total_grant_paid_amt | 31,416 | 73.3% |
| state | 42,833 | 99.9% |
| website_url | 34,124 | 79.6% (15.6% real URLs) |
| application_submission_info | 9,601 | 22.4% |
| only_contri_to_preselected_ind | 42,855 | 100% |

---

### 2.2 pf_grants (Grant Records)

**Purpose:** Individual grant records from Form 990-PF Part XV - shows who foundations have funded.

**Schema:** f990_2025

**Row Count:** 440,868

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NO | Primary key |
| return_id | INTEGER | YES | FK to pf_returns(id) |
| filer_ein | VARCHAR(20) | NO | Funder's EIN |
| tax_year | INTEGER | YES | Tax year of grant |
| recipient_ein | VARCHAR(20) | YES | Recipient's EIN (often NULL) |
| recipient_name | TEXT | YES | Recipient org/individual name |
| recipient_address_line1 | TEXT | YES | Recipient street address |
| recipient_city | TEXT | YES | Recipient city |
| recipient_state | VARCHAR(50) | YES | Recipient state |
| recipient_zip | VARCHAR(20) | YES | Recipient ZIP |
| recipient_country | TEXT | YES | Recipient country |
| is_individual | BOOLEAN | YES | Grant to individual (vs org) |
| amount | NUMERIC(15,2) | YES | Grant amount in dollars |
| purpose | TEXT | YES | Grant purpose description |
| relationship | TEXT | YES | Relationship to foundation |
| created_at | TIMESTAMP | YES | Record creation timestamp |

**Indexes:**
- `idx_pf_grants_return_id` ON return_id
- `idx_pf_grants_filer_ein` ON filer_ein
- `idx_pf_grants_recipient_ein` ON recipient_ein
- `idx_pf_grants_tax_year` ON tax_year
- `idx_pf_grants_amount` ON amount
- `idx_pf_grants_recipient_state` ON recipient_state

**Foreign Keys:**
- `return_id` -> `pf_returns(id)` ON DELETE CASCADE

**Constraints:** NOT NULL on filer_ein

**Population Status:**
| Field | Populated | Rate |
|-------|-----------|------|
| amount | 439,336 | 99.7% |
| recipient_name | 440,868 | 100% |
| recipient_state | 439,155 | 99.6% |
| purpose | 440,837 | 100% (after bug fix) |
| recipient_ein | 0 | 0% (needs enrichment) |

---

### 2.3 nonprofit_returns (Form 990 & 990-EZ)

**Purpose:** Stores nonprofit organization returns - potential grant recipients and general nonprofit data.

**Schema:** f990_2025

**Row Count:** 220,245

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NO | Primary key |
| ein | VARCHAR(20) | NO | Employer Identification Number |
| organization_name | TEXT | YES | Organization name |
| tax_year | INTEGER | YES | Tax year of filing |
| tax_period_begin | DATE | YES | Start of tax period |
| tax_period_end | DATE | YES | End of tax period |
| form_type | VARCHAR(20) | YES | '990' or '990EZ' |
| source_file | TEXT | YES | Original XML file path |
| object_id | VARCHAR(100) | YES | IRS object identifier |
| address_line1 | TEXT | YES | Street address |
| address_line2 | TEXT | YES | Address line 2 |
| city | TEXT | YES | City |
| state | VARCHAR(50) | YES | State code |
| zip | VARCHAR(20) | YES | ZIP code |
| country | TEXT | YES | Country |
| phone | VARCHAR(50) | YES | Phone number |
| website | TEXT | YES | Website URL |
| total_revenue | NUMERIC(15,2) | YES | Total revenue |
| total_expenses | NUMERIC(15,2) | YES | Total expenses |
| total_assets_boy | NUMERIC(15,2) | YES | Total assets BOY |
| total_assets_eoy | NUMERIC(15,2) | YES | Total assets EOY |
| net_assets_boy | NUMERIC(15,2) | YES | Net assets BOY |
| net_assets_eoy | NUMERIC(15,2) | YES | Net assets EOY |
| contributions_grants | NUMERIC(15,2) | YES | Contributions/grants received |
| program_service_revenue | NUMERIC(15,2) | YES | Program service revenue |
| investment_income | NUMERIC(15,2) | YES | Investment income |
| mission_description | TEXT | YES | Mission description |
| activity_description | TEXT | YES | Activity description |
| primary_exempt_purpose | TEXT | YES | Primary exempt purpose |
| program_1_desc | TEXT | YES | Program 1 description |
| program_2_desc | TEXT | YES | Program 2 description |
| program_3_desc | TEXT | YES | Program 3 description |
| program_1_expense_amt | NUMERIC(15,2) | YES | Program 1 expenses |
| program_2_expense_amt | NUMERIC(15,2) | YES | Program 2 expenses |
| program_3_expense_amt | NUMERIC(15,2) | YES | Program 3 expenses |
| program_1_revenue_amt | NUMERIC(15,2) | YES | Program 1 revenue |
| activity_code_1 | VARCHAR(20) | YES | NTEE activity code 1 |
| activity_code_2 | VARCHAR(20) | YES | NTEE activity code 2 |
| activity_code_3 | VARCHAR(20) | YES | NTEE activity code 3 |
| ntee_code | VARCHAR(10) | YES | NTEE classification code |
| ruling_date | DATE | YES | IRS ruling date |
| foreign_activities_ind | BOOLEAN | YES | Has foreign activities |
| voting_members_governing_body_cnt | INTEGER | YES | Voting board members |
| voting_members_independent_cnt | INTEGER | YES | Independent voting members |
| total_employees_cnt | INTEGER | YES | Total employees |
| total_volunteers_cnt | INTEGER | YES | Total volunteers |
| created_at | TIMESTAMP | YES | Record creation timestamp |
| updated_at | TIMESTAMP | YES | Record update timestamp |

**Indexes:**
- `idx_nonprofit_returns_ein` ON ein
- `idx_nonprofit_returns_tax_year` ON tax_year
- `idx_nonprofit_returns_state` ON state
- `idx_nonprofit_returns_form_type` ON form_type
- `idx_nonprofit_returns_ntee` ON ntee_code

---

### 2.4 officers

**Purpose:** Officers, directors, and trustees from all form types.

**Schema:** f990_2025

**Row Count:** 41,641

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NO | Primary key |
| pf_return_id | INTEGER | YES | FK to pf_returns(id) |
| np_return_id | INTEGER | YES | FK to nonprofit_returns(id) |
| ein | VARCHAR(20) | NO | Organization's EIN |
| tax_year | INTEGER | YES | Tax year |
| form_type | VARCHAR(20) | YES | '990PF', '990', or '990EZ' |
| person_nm | TEXT | YES | Person's name |
| title_txt | TEXT | YES | Title/position |
| average_hours_per_week | NUMERIC(5,2) | YES | Average hours worked |
| compensation_amt | NUMERIC(15,2) | YES | Compensation amount |
| is_officer | BOOLEAN | YES | Is an officer |
| is_director | BOOLEAN | YES | Is a director |
| is_trustee | BOOLEAN | YES | Is a trustee |
| is_key_employee | BOOLEAN | YES | Is a key employee |
| is_highest_compensated | BOOLEAN | YES | Is highest compensated |
| is_former | BOOLEAN | YES | Is former officer/director |
| created_at | TIMESTAMP | YES | Record creation timestamp |

**Constraints:**
- `chk_officer_return` - Must reference EITHER pf_return_id OR np_return_id (not both, not neither)

**Foreign Keys:**
- `pf_return_id` -> `pf_returns(id)` ON DELETE CASCADE
- `np_return_id` -> `nonprofit_returns(id)` ON DELETE CASCADE

---

### 2.5 schedule_a (Charity Classifications)

**Purpose:** Schedule A charity type classifications for 509(a) status.

**Schema:** f990_2025

**Row Count:** 220,245

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NO | Primary key |
| np_return_id | INTEGER | YES | FK to nonprofit_returns(id) |
| ein | VARCHAR(20) | NO | Organization's EIN |
| tax_year | INTEGER | YES | Tax year |
| church_ind | BOOLEAN | YES | Is a church |
| school_ind | BOOLEAN | YES | Is a school |
| hospital_ind | BOOLEAN | YES | Is a hospital |
| medical_research_org_ind | BOOLEAN | YES | Is medical research org |
| college_org_ind | BOOLEAN | YES | Is a college/university |
| governmental_unit_ind | BOOLEAN | YES | Is a governmental unit |
| public_charity_509a1_ind | BOOLEAN | YES | Is 509(a)(1) public charity |
| public_charity_509a2_ind | BOOLEAN | YES | Is 509(a)(2) public charity |
| supporting_org_509a3_ind | BOOLEAN | YES | Is 509(a)(3) supporting org |
| supporting_org_type1_ind | BOOLEAN | YES | Type I supporting org |
| supporting_org_type2_ind | BOOLEAN | YES | Type II supporting org |
| supporting_org_type3_func_int_ind | BOOLEAN | YES | Type III functionally integrated |
| supporting_org_type3_non_func_int_ind | BOOLEAN | YES | Type III non-functionally integrated |
| community_trust_ind | BOOLEAN | YES | Is a community trust |
| public_safety_org_ind | BOOLEAN | YES | Is a public safety org |
| created_at | TIMESTAMP | YES | Record creation timestamp |

**Foreign Keys:**
- `np_return_id` -> `nonprofit_returns(id)` ON DELETE CASCADE

---

### 2.6 import_log (ETL Tracking)

**Purpose:** Tracks import runs for debugging and audit purposes.

**Schema:** f990_2025

**Row Count:** ~8

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | SERIAL | NO | Primary key |
| import_run_id | UUID | NO | Unique identifier for import run |
| started_at | TIMESTAMP | YES | Import start time |
| completed_at | TIMESTAMP | YES | Import completion time |
| source_file | TEXT | YES | Source ZIP/XML file |
| form_type | VARCHAR(20) | YES | Form type processed |
| tax_year | INTEGER | YES | Tax year of data |
| records_processed | INTEGER | YES | Total records attempted |
| records_success | INTEGER | YES | Successfully imported |
| records_failed | INTEGER | YES | Failed to import |
| error_message | TEXT | YES | Error details if failed |
| status | VARCHAR(50) | YES | 'running', 'completed', 'failed', 'partial' |
| created_at | TIMESTAMP | YES | Record creation timestamp |

---

## 3. Derived Tables

### 3.1 foundations (Production Profile Table)

**Purpose:** Main foundation profiles table with enriched data for matching algorithms.

**Schema:** public (TheGrantScout)

**Row Count:** 85,470

**Source Tables:**
- f990_2025.pf_returns (primary)
- f990_foundations (historical)
- Web scraping enrichment

| Column | Type | Calculated/Source |
|--------|------|-------------------|
| id | INTEGER | Auto-increment |
| ein | VARCHAR(10) | Source: pf_returns.ein |
| name | VARCHAR(500) | Source: pf_returns.business_name |
| city | VARCHAR(100) | Source: pf_returns.city |
| state | VARCHAR(2) | Source: pf_returns.state |
| zip_code | VARCHAR(10) | Source: pf_returns.zip |
| website_url | TEXT | Source: pf_returns.website_url |
| assets | BIGINT | Source: pf_returns.total_assets_eoy_amt |
| total_giving | BIGINT | Source: pf_returns.total_grant_paid_amt |
| tax_year | INTEGER | Source: pf_returns.tax_year |
| openness_score | NUMERIC(5,2) | **Calculated:** See formula below |
| avg_grant_size | INTEGER | **Calculated:** AVG(historical_grants.amount) |
| median_grant_size | INTEGER | **Calculated:** MEDIAN(historical_grants.amount) |
| total_grants_count | INTEGER | **Calculated:** COUNT(historical_grants) |
| accepts_unsolicited | BOOLEAN | Derived: NOT only_contri_to_preselected_ind |
| size_category | VARCHAR(20) | **Calculated:** Based on assets |
| geographic_focus | VARCHAR(50) | **Calculated:** Mode of grant recipient states |
| intelligence_profile | JSONB | **Calculated:** Composite profile |

**Openness Score Formula (0-100):**
```
openness_score = (
    new_grantee_rate * 0.30 +      -- % grants to first-time recipients
    geographic_diversity * 0.25 +   -- Number of states funded (normalized)
    sector_diversity * 0.25 +       -- Number of NTEE categories (normalized)
    accessibility_indicators * 0.20 -- Public RFP, website, contact info
)
```

**Size Category Derivation:**
| Category | Asset Range |
|----------|-------------|
| Mega | > $1B |
| Large | $100M - $1B |
| Medium | $10M - $100M |
| Small | $1M - $10M |
| Micro | < $1M |

**Refresh Frequency:** On demand (currently manual)

---

### 3.2 historical_grants (Processed Grant History)

**Purpose:** Foundation giving patterns analysis, recipient discovery, and trend identification.

**Schema:** public (TheGrantScout)

**Row Count:** 1,621,833

**Source Tables:**
- f990_2025.pf_grants
- f990_grants (legacy)

| Column | Type | Source |
|--------|------|--------|
| id | INTEGER | Auto-increment |
| foundation_ein | VARCHAR(10) | Source: pf_grants.filer_ein |
| recipient_ein | VARCHAR(10) | Source: pf_grants.recipient_ein |
| recipient_name | VARCHAR(500) | Source: pf_grants.recipient_name |
| recipient_city | VARCHAR(100) | Source: pf_grants.recipient_city |
| recipient_state | VARCHAR(2) | Source: pf_grants.recipient_state |
| grant_amount | INTEGER | Source: pf_grants.amount |
| grant_date | DATE | Derived from tax_year |
| tax_year | INTEGER | Source: pf_grants.tax_year |
| grant_purpose | TEXT | Source: pf_grants.purpose |
| source | VARCHAR(50) | '990-PF' |

**Refresh Frequency:** Annual (IRS filing cycle)

---

### 3.3 matches (Generated Match Results)

**Purpose:** AI-generated foundation/grant matches for nonprofit organizations.

**Schema:** public (TheGrantScout)

**Row Count:** 317

**Source Tables:**
- foundations
- nonprofits
- historical_grants
- current_grants

| Column | Type | Calculated/Source |
|--------|------|-------------------|
| id | INTEGER | Auto-increment |
| nonprofit_ein | VARCHAR(10) | Input: Client nonprofit EIN |
| foundation_ein | VARCHAR(10) | Output: Matched foundation |
| match_score | NUMERIC(5,2) | **Calculated:** 10-signal algorithm |
| match_type | VARCHAR(50) | 'foundation' or 'current_opportunity' |
| match_reason | JSONB | **Calculated:** Score breakdown |
| score_components | JSONB | **Calculated:** Per-signal scores |
| relationship_tier | VARCHAR(50) | **Calculated:** Based on prior funding |
| funding_probability | INTEGER | **Calculated:** 0-100 estimate |
| expected_value | BIGINT | **Calculated:** probability × avg_grant_size |

**10-Signal Scoring Algorithm:**
| Signal | Points | Calculation |
|--------|--------|-------------|
| Prior Relationship | 40 | Has foundation funded this nonprofit before? |
| Geographic Match | 15 | In-state funding preference |
| Grant Size Alignment | 12 | Typical grant size matches ask? |
| Repeat Funding Rate | 10 | Foundation favors existing grantees? |
| Portfolio Concentration | 8 | How focused on specific sectors? |
| Purpose Text Match | 5 | Semantic similarity to past purposes |
| Recipient Validation | 4 | Foundation's grantee quality patterns |
| Foundation Size | 3 | Capacity to fund at requested level |
| Regional Proximity | 2 | Cross-state giving corridors |
| Grant Frequency | 1 | Active vs. sporadic grantmaker |

**Refresh Frequency:** On-demand per nonprofit

---

## 4. Source Tables

### 4.1 f990_2025 Schema Tables

These tables contain the raw IRS Form 990 data imported from 2025 TEOS XML files.

| Table | Purpose | Records | Feed Into |
|-------|---------|---------|-----------|
| pf_returns | Private foundation returns | 42,855 | foundations |
| pf_grants | Grant records | 440,868 | historical_grants |
| nonprofit_returns | 990/990-EZ filings | 220,245 | (reference data) |
| officers | Board/officer data | 41,641 | board_members (pending) |
| schedule_a | Charity classifications | 220,245 | (reference data) |
| import_log | ETL tracking | ~8 | (monitoring) |

**Import Source:**
- 8 ZIP files (~2 GB total)
- IRS TEOS XML files (2025 release)
- Tax years: 2021-2024 (weighted to 2023-2024)

**How Source Tables Feed Core Tables:**

```
pf_returns ──────────────────────────► foundations
    │                                      │
    │ enrichment: web scraping            │ calculated fields:
    │ + derived fields                    │ - openness_score
    │                                      │ - size_category
    ▼                                      │ - geographic_focus
pf_grants ───────────────────────────► historical_grants
    │                                      │
    │ aggregation + cleaning              │ + recipient_entity_id
    │                                      │
    ▼                                      ▼
officers ────────────────────────────► board_members (PENDING)
    │                                      │
    │ deduplication + name                │ network analysis
    │ normalization                       │
    │                                      ▼
    └──────────────────────────────────► network_relationships (PENDING)
```

### 4.2 IRS BMF Tables

**Purpose:** Reference data for organization lookups, EIN validation, NTEE code enrichment.

| Table | Records | Purpose |
|-------|---------|---------|
| irs_bmf | 1,898,175 | Master reference table |
| irs_bmf_eo1 | 270,505 | Partition 1 (duplicate) |
| irs_bmf_eo2 | 700,488 | Partition 2 (duplicate) |
| irs_bmf_eo3 | 922,562 | Partition 3 (duplicate) |
| irs_bmf_eo4 | 4,620 | Partition 4 (duplicate) |

**Note:** eo1-eo4 tables are duplicates of irs_bmf - candidates for deletion.

**Key Fields in irs_bmf:**
- ein (EIN lookup)
- name (Organization name)
- ntee_cd (NTEE classification)
- asset_amt (Asset amount)
- income_amt (Income amount)

---

## 5. Current State

### 5.1 Table Population Summary

| Table | Records | Status | Notes |
|-------|---------|--------|-------|
| f990_2025.pf_returns | 42,855 | COMPLETE | Tax years 2021-2024 |
| f990_2025.pf_grants | 440,868 | COMPLETE | Purpose text 100% after fix |
| f990_2025.nonprofit_returns | 220,245 | COMPLETE | 990 + 990-EZ forms |
| f990_2025.officers | 41,641 | COMPLETE | From all form types |
| f990_2025.schedule_a | 220,245 | COMPLETE | 509(a) classifications |
| foundations | 85,470 | NEEDS UPDATE | Merge with f990_2025 data |
| historical_grants | 1,621,833 | NEEDS UPDATE | Add 2024 grants |
| current_grants | 42 | PARTIAL | Needs expansion to 500+ |
| nonprofits | 4 | ACTIVE | Beta testers only |
| matches | 317 | ACTIVE | Generated matches |
| board_members | 0 | EMPTY | Awaiting population |
| network_relationships | 0 | EMPTY | Awaiting calculation |
| foundation_temporal_patterns | 0 | EMPTY | Awaiting analysis |
| application_outcomes | 0 | EMPTY | Future learning loop |

### 5.2 Data Quality Issues Known

| Issue | Impact | Status |
|-------|--------|--------|
| Grant purpose parser bug | 0% purpose text | FIXED (Dec 5) |
| Website URL placeholders | 79.6% have values but only 15.6% real | KNOWN |
| Recipient EINs missing | 0% in pf_grants | Needs enrichment |
| Grant dates sparse | Many NULL dates | Use tax_year instead |
| NTEE codes as text | Not array format in foundations | Needs migration |
| Duplicate BMF tables | eo1-eo4 duplicate irs_bmf | Candidates for deletion |

### 5.3 Recent Imports/Updates

| Date | Action | Result |
|------|--------|--------|
| Dec 3, 2025 | F990 2025 import | 262,450 records imported |
| Dec 5, 2025 | Grant purpose backfill | 440,837 purpose texts populated (100%) |

### 5.4 Import Statistics (Dec 3, 2025)

| Form Type | Records Imported |
|-----------|------------------|
| 990-PF | 42,574 |
| 990-EZ | 86,731 |
| 990 | 133,145 |
| **Total** | **262,450** |

**Failed:** 89,353 (mostly "Could not detect form type" - 990-T and other forms)

---

## 6. Build Tasks

### 6.1 SQL Migrations Needed

| Priority | Migration | Description |
|----------|-----------|-------------|
| HIGH | Update foundations from f990_2025 | Merge new 2025 data into production foundations table |
| HIGH | Add 2024 grants to historical_grants | Append pf_grants to historical_grants |
| MEDIUM | Convert ntee_codes to ARRAY | Migrate foundations.ntee_codes from TEXT to TEXT[] |
| MEDIUM | Add missing indexes | Add indexes to board_members, network_relationships |
| LOW | Delete duplicate BMF tables | Drop irs_bmf_eo1, eo2, eo3, eo4 |

**Migration Scripts Location:** `1. Database/F990-2025/3. Grant Scout Tables/`

### 6.2 Python Scripts Needed

| Priority | Script | Purpose |
|----------|--------|---------|
| HIGH | populate_foundation_intelligence.py | Calculate openness scores, size categories |
| HIGH | enrich_recipient_eins.py | Use ProPublica API to add recipient EINs |
| MEDIUM | populate_board_members.py | Dedupe/normalize officers into board_members |
| MEDIUM | calculate_temporal_patterns.py | Analyze quarterly giving patterns |
| LOW | clean_website_urls.py | Filter placeholder URLs |

### 6.3 Data Enrichment Tasks

| Task | Source | Priority |
|------|--------|----------|
| Recipient EIN matching | ProPublica Nonprofit Explorer API | HIGH |
| Foundation website scraping | Verified URLs from pf_returns | HIGH |
| Current opportunities expansion | Grants.gov, state portals, foundation sites | HIGH |
| NTEE code standardization | Cross-reference with irs_bmf | MEDIUM |
| Board overlap detection | Name matching across officers | MEDIUM |

### 6.4 Priority Order

```
Phase 1 (Immediate - This Week):
├── 1.1 Merge f990_2025.pf_returns → foundations
├── 1.2 Append f990_2025.pf_grants → historical_grants
└── 1.3 Calculate openness scores for all foundations

Phase 2 (Short Term - Next 2 Weeks):
├── 2.1 Recipient EIN enrichment
├── 2.2 Current opportunities expansion (42 → 500+)
└── 2.3 Website URL cleaning

Phase 3 (Medium Term - 30-60 Days):
├── 3.1 Board member deduplication
├── 3.2 Network relationship calculation
├── 3.3 Temporal pattern analysis
└── 3.4 Foundation intelligence profile population
```

---

## 7. Source Files

### 7.1 Documentation Files

| File | Path | Purpose |
|------|------|---------|
| DATA_DICTIONARY.md | `1. Database/DATA_DICTIONARY.md` | Complete field-level documentation |
| SCHEMA_SUMMARY.md | `.claude/Team Enhancements/Enhancements 2025-12-05/SCHEMA_SUMMARY.md` | Schema quick reference |
| OUTPUT_GOTCHAS.md | `.claude/Team Enhancements/Enhancements 2025-12-05/OUTPUT_GOTCHAS.md` | Known issues and fixes |
| Build Plan.md | `1. Database/Build Plan.md` | Database build roadmap |

### 7.2 Schema and Migration Files

| File | Path | Purpose |
|------|------|---------|
| schema.sql | `1. Database/F990-2025/1. Import/schema.sql` | F990 2025 schema DDL |
| config.yaml | `1. Database/F990-2025/1. Import/config.yaml` | Import configuration |

### 7.3 Import Scripts

| File | Path | Purpose |
|------|------|---------|
| import_f990.py | `1. Database/F990-2025/1. Import/import_f990.py` | Main import script |
| backfill_grant_purpose.py | `1. Database/F990-2025/1. Import/backfill_grant_purpose.py` | Grant purpose fix |
| validate.py | `1. Database/F990-2025/1. Import/validate.py` | Data validation |

### 7.4 Validation Reports

| File | Path | Purpose |
|------|------|---------|
| REPORT_2025-12-04_import_validation.md | `1. Database/F990-2025/2. Import review + fixes/` | Import validation findings |
| REPORT_2025-12-05_grant_purpose_bug.md | `1. Database/F990-2025/2. Import review + fixes/` | Grant purpose bug fix documentation |
| import_summary.json | `1. Database/F990-2025/1. Import/` | Import statistics |

### 7.5 Agent Documentation

| File | Path | Purpose |
|------|------|---------|
| data-engineer.md | `.claude/agents/data-engineer.md` | Data engineer agent spec |
| CLAUDE.md | `.claude/CLAUDE.md` | Project context for Claude Code |

---

## Appendix A: Data Conventions

### Amounts
- All monetary amounts: `NUMERIC(15,2)` (15 digits, 2 decimal places)
- Currency: USD (no conversion needed)
- NULL = not reported (distinct from 0)

### Dates
- Format: `YYYY-MM-DD` (ISO 8601)
- `tax_period_begin/end` define fiscal year
- Many grant_date values are NULL - use tax_year for temporal analysis

### Boolean Fields
- `TRUE`/`FALSE`/`NULL`
- NULL typically = "not applicable" or "not reported"
- **Key filter:** `only_contri_to_preselected_ind = FALSE` means open to applications

### EINs
- Stored as `VARCHAR(20)` to preserve leading zeros
- Format: 9 digits, no dashes (e.g., '123456789')
- Some legacy tables use `VARCHAR(9)` or `VARCHAR(10)`

### NULL Handling
- NULL = field not present in XML or not applicable
- Empty string ('') = field present but empty
- Use COALESCE or IS NOT NULL filters in queries

---

## Appendix B: Common Queries

### Find foundations accepting applications
```sql
SELECT ein, business_name, state, total_assets_eoy_amt
FROM f990_2025.pf_returns
WHERE grants_to_organizations_ind = TRUE
  AND (only_contri_to_preselected_ind = FALSE
       OR only_contri_to_preselected_ind IS NULL)
ORDER BY total_assets_eoy_amt DESC NULLS LAST;
```

### Get grant history for a foundation
```sql
SELECT recipient_name, recipient_state, amount, purpose, tax_year
FROM f990_2025.pf_grants
WHERE filer_ein = '123456789'
ORDER BY tax_year DESC, amount DESC;
```

### Check field population rates
```sql
SELECT
    'purpose' as field,
    COUNT(*) as total,
    COUNT(purpose) as populated,
    ROUND(100.0 * COUNT(purpose) / COUNT(*), 1) as pct
FROM f990_2025.pf_grants;
```

### Foundation grant totals by state
```sql
SELECT pf.state,
       COUNT(*) as foundation_count,
       SUM(pf.total_grant_paid_amt) as total_grants
FROM f990_2025.pf_returns pf
WHERE pf.grants_to_organizations_ind = TRUE
GROUP BY pf.state
ORDER BY total_grants DESC NULLS LAST;
```

---

**End of DATABASE_SPEC.md**

---

**Document Metadata:**
- Created: 2025-12-08
- Author: Claude Code (data-engineer agent)
- Database Version: PostgreSQL 15+
- Schema Version: f990_2025 (Dec 3, 2025)
- Total Tables Documented: 19+
- Total Data Volume: ~8M+ rows
