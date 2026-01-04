# Database Schema & Structure

## Overview

TheGrantScout uses PostgreSQL for storing IRS Form 990 data. The primary schema is `f990_2025`, designed for importing and analyzing IRS Form 990, 990-PF, and 990-EZ data from 2025 TEOS XML files.

---

## Connection Information

**File Location:** `1. Database/Postgresql Info.txt`

**Structure (do not include credentials in documentation):**
```
HOST=<host_ip>
PORT=5432
DATABASE=postgres
USERNAME=<username>
PASSWORD=<password>
```

**Common Connection Pattern (Python/psycopg2):**
```python
import psycopg2

# Load from config.yaml or Postgresql Info.txt
db_conn = psycopg2.connect(
    host=config['database']['host'],
    port=config['database']['port'],
    database=config['database']['database'],
    user=config['database']['username'],
    password=config['database']['password']
)
db_conn.autocommit = False
```

---

## Schema: f990_2025

### Table 1: pf_returns (Private Foundation Returns)

**Purpose:** Stores Form 990-PF data for private foundations - the primary source for grant-making foundations.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `ein` | VARCHAR(20) | Employer Identification Number (NOT NULL) |
| `business_name` | TEXT | Foundation name |
| `tax_year` | INTEGER | Tax year of filing |
| `tax_period_begin` | DATE | Start of tax period |
| `tax_period_end` | DATE | End of tax period |
| `source_file` | TEXT | Original XML file path |
| `return_timestamp` | TIMESTAMP | When return was filed |
| `object_id` | VARCHAR(100) | IRS object identifier |
| `address_line1` | TEXT | Street address |
| `address_line2` | TEXT | Address line 2 |
| `city` | TEXT | City |
| `state` | VARCHAR(50) | State code |
| `zip` | VARCHAR(20) | ZIP code |
| `country` | TEXT | Country |
| `phone_num` | VARCHAR(50) | Phone number |
| `email_address_txt` | TEXT | Email address |
| `website_url` | TEXT | Website URL |
| `contributing_manager_nm` | TEXT | Contributing manager name |
| `private_operating_foundation_ind` | BOOLEAN | Is private operating foundation |
| `exempt_operating_foundations_ind` | BOOLEAN | Is exempt operating foundation |
| `grants_to_organizations_ind` | BOOLEAN | Makes grants to organizations |
| `grants_to_individuals_ind` | BOOLEAN | Makes grants to individuals |
| `total_revenue_amt` | NUMERIC(15,2) | Total revenue |
| `total_expenses_amt` | NUMERIC(15,2) | Total expenses |
| `total_assets_boy_amt` | NUMERIC(15,2) | Total assets beginning of year |
| `total_assets_eoy_amt` | NUMERIC(15,2) | Total assets end of year |
| `net_assets_boy_amt` | NUMERIC(15,2) | Net assets beginning of year |
| `net_assets_eoy_amt` | NUMERIC(15,2) | Net assets end of year |
| `contributions_received_amt` | NUMERIC(15,2) | Contributions received |
| `investment_income_amt` | NUMERIC(15,2) | Investment income |
| `distributable_as_adjusted_amt` | NUMERIC(15,2) | Distributable amount (adjusted) |
| `qualifying_distributions_amt` | NUMERIC(15,2) | Qualifying distributions |
| `total_grant_paid_amt` | NUMERIC(15,2) | Total grants paid |
| `total_grant_approved_future_amt` | NUMERIC(15,2) | Grants approved for future |
| `undistributed_income_cy_amt` | NUMERIC(15,2) | Undistributed income current year |
| `undistributed_income_py_ind` | BOOLEAN | Has undistributed prior year income |
| `only_contri_to_preselected_ind` | BOOLEAN | **Key Filter:** Only gives to preselected recipients |
| `application_submission_info` | JSONB | Application submission details |
| `mission_desc` | TEXT | Mission description |
| `activity_or_mission_desc` | TEXT | Activity/mission description |
| `primary_exempt_purpose` | TEXT | Primary exempt purpose |
| `activity_code_1` | VARCHAR(20) | NTEE activity code 1 |
| `activity_code_2` | VARCHAR(20) | NTEE activity code 2 |
| `activity_code_3` | VARCHAR(20) | NTEE activity code 3 |
| `foreign_activities_ind` | BOOLEAN | Has foreign activities |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Record update timestamp |

**Key Indexes:**
- `idx_pf_returns_ein` - EIN lookup
- `idx_pf_returns_state` - State filtering
- `idx_pf_returns_grants_to_orgs` - Filter for org grantmakers (WHERE TRUE)
- `idx_pf_returns_only_preselected` - Filter for open applications (WHERE FALSE)
- `idx_pf_returns_distributable` - Filter by grant capacity

---

### Table 2: nonprofit_returns (Form 990 & 990-EZ)

**Purpose:** Stores nonprofit organization returns - potential grant recipients and general nonprofit data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `ein` | VARCHAR(20) | Employer Identification Number (NOT NULL) |
| `organization_name` | TEXT | Organization name |
| `tax_year` | INTEGER | Tax year of filing |
| `tax_period_begin` | DATE | Start of tax period |
| `tax_period_end` | DATE | End of tax period |
| `form_type` | VARCHAR(20) | '990' or '990EZ' |
| `source_file` | TEXT | Original XML file path |
| `object_id` | VARCHAR(100) | IRS object identifier |
| `address_line1` | TEXT | Street address |
| `city` | TEXT | City |
| `state` | VARCHAR(50) | State code |
| `zip` | VARCHAR(20) | ZIP code |
| `country` | TEXT | Country |
| `phone` | VARCHAR(50) | Phone number |
| `website` | TEXT | Website URL |
| `total_revenue` | NUMERIC(15,2) | Total revenue |
| `total_expenses` | NUMERIC(15,2) | Total expenses |
| `total_assets_boy` | NUMERIC(15,2) | Total assets beginning of year |
| `total_assets_eoy` | NUMERIC(15,2) | Total assets end of year |
| `net_assets_boy` | NUMERIC(15,2) | Net assets beginning of year |
| `net_assets_eoy` | NUMERIC(15,2) | Net assets end of year |
| `contributions_grants` | NUMERIC(15,2) | Contributions and grants received |
| `program_service_revenue` | NUMERIC(15,2) | Program service revenue |
| `investment_income` | NUMERIC(15,2) | Investment income |
| `mission_description` | TEXT | Mission description |
| `activity_description` | TEXT | Activity description |
| `primary_exempt_purpose` | TEXT | Primary exempt purpose |
| `program_1_desc` | TEXT | Program 1 description |
| `program_2_desc` | TEXT | Program 2 description |
| `program_3_desc` | TEXT | Program 3 description |
| `program_1_expense_amt` | NUMERIC(15,2) | Program 1 expenses |
| `program_2_expense_amt` | NUMERIC(15,2) | Program 2 expenses |
| `program_3_expense_amt` | NUMERIC(15,2) | Program 3 expenses |
| `program_1_revenue_amt` | NUMERIC(15,2) | Program 1 revenue |
| `activity_code_1` | VARCHAR(20) | NTEE activity code 1 |
| `activity_code_2` | VARCHAR(20) | NTEE activity code 2 |
| `activity_code_3` | VARCHAR(20) | NTEE activity code 3 |
| `ntee_code` | VARCHAR(10) | NTEE classification code |
| `ruling_date` | DATE | IRS ruling date |
| `foreign_activities_ind` | BOOLEAN | Has foreign activities |
| `voting_members_governing_body_cnt` | INTEGER | Voting board members |
| `voting_members_independent_cnt` | INTEGER | Independent voting members |
| `total_employees_cnt` | INTEGER | Total employees |
| `total_volunteers_cnt` | INTEGER | Total volunteers |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Record update timestamp |

**Key Indexes:**
- `idx_nonprofit_returns_ein` - EIN lookup
- `idx_nonprofit_returns_state` - State filtering
- `idx_nonprofit_returns_form_type` - Form type filtering
- `idx_nonprofit_returns_ntee` - NTEE code filtering

---

### Table 3: pf_grants (Grant Records)

**Purpose:** Individual grant records from Form 990-PF Part XV - shows who foundations have funded.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `return_id` | INTEGER | FK to pf_returns(id), CASCADE delete |
| `filer_ein` | VARCHAR(20) | Funder's EIN (NOT NULL) |
| `tax_year` | INTEGER | Tax year of grant |
| `recipient_ein` | VARCHAR(20) | Recipient's EIN (may be NULL for individuals) |
| `recipient_name` | TEXT | Recipient organization/individual name |
| `recipient_address_line1` | TEXT | Recipient street address |
| `recipient_city` | TEXT | Recipient city |
| `recipient_state` | VARCHAR(50) | Recipient state |
| `recipient_zip` | VARCHAR(20) | Recipient ZIP |
| `recipient_country` | TEXT | Recipient country |
| `is_individual` | BOOLEAN | Grant to individual (vs organization) |
| `amount` | NUMERIC(15,2) | Grant amount in dollars |
| `purpose` | TEXT | Grant purpose description |
| `relationship` | TEXT | Relationship to foundation |
| `created_at` | TIMESTAMP | Record creation timestamp |

**Key Indexes:**
- `idx_pf_grants_return_id` - Join to parent return
- `idx_pf_grants_filer_ein` - Lookup by funder
- `idx_pf_grants_recipient_ein` - Lookup by recipient
- `idx_pf_grants_amount` - Filter by grant size
- `idx_pf_grants_recipient_state` - Geographic filtering

**Foreign Keys:**
- `return_id` -> `pf_returns(id)` ON DELETE CASCADE

---

### Table 4: officers

**Purpose:** Officers, directors, and trustees from all form types.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `pf_return_id` | INTEGER | FK to pf_returns(id), NULL if nonprofit |
| `np_return_id` | INTEGER | FK to nonprofit_returns(id), NULL if PF |
| `ein` | VARCHAR(20) | Organization's EIN (NOT NULL) |
| `tax_year` | INTEGER | Tax year |
| `form_type` | VARCHAR(20) | '990PF', '990', or '990EZ' |
| `person_nm` | TEXT | Person's name |
| `title_txt` | TEXT | Title/position |
| `average_hours_per_week` | NUMERIC(5,2) | Average hours worked |
| `compensation_amt` | NUMERIC(15,2) | Compensation amount |
| `is_officer` | BOOLEAN | Is an officer |
| `is_director` | BOOLEAN | Is a director |
| `is_trustee` | BOOLEAN | Is a trustee |
| `is_key_employee` | BOOLEAN | Is a key employee |
| `is_highest_compensated` | BOOLEAN | Is highest compensated |
| `is_former` | BOOLEAN | Is former officer/director |
| `created_at` | TIMESTAMP | Record creation timestamp |

**Constraints:**
- `chk_officer_return` - Must reference EITHER pf_return_id OR np_return_id (not both, not neither)

**Foreign Keys:**
- `pf_return_id` -> `pf_returns(id)` ON DELETE CASCADE
- `np_return_id` -> `nonprofit_returns(id)` ON DELETE CASCADE

---

### Table 5: schedule_a (Charity Classifications)

**Purpose:** Schedule A charity type classifications for 509(a) status.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `np_return_id` | INTEGER | FK to nonprofit_returns(id) |
| `ein` | VARCHAR(20) | Organization's EIN (NOT NULL) |
| `tax_year` | INTEGER | Tax year |
| `church_ind` | BOOLEAN | Is a church |
| `school_ind` | BOOLEAN | Is a school |
| `hospital_ind` | BOOLEAN | Is a hospital |
| `medical_research_org_ind` | BOOLEAN | Is medical research org |
| `college_org_ind` | BOOLEAN | Is a college/university |
| `governmental_unit_ind` | BOOLEAN | Is a governmental unit |
| `public_charity_509a1_ind` | BOOLEAN | Is 509(a)(1) public charity |
| `public_charity_509a2_ind` | BOOLEAN | Is 509(a)(2) public charity |
| `supporting_org_509a3_ind` | BOOLEAN | Is 509(a)(3) supporting org |
| `supporting_org_type1_ind` | BOOLEAN | Type I supporting org |
| `supporting_org_type2_ind` | BOOLEAN | Type II supporting org |
| `supporting_org_type3_func_int_ind` | BOOLEAN | Type III functionally integrated |
| `supporting_org_type3_non_func_int_ind` | BOOLEAN | Type III non-functionally integrated |
| `community_trust_ind` | BOOLEAN | Is a community trust |
| `public_safety_org_ind` | BOOLEAN | Is a public safety org |
| `created_at` | TIMESTAMP | Record creation timestamp |

**Foreign Keys:**
- `np_return_id` -> `nonprofit_returns(id)` ON DELETE CASCADE

---

### Table 6: import_log (Import Tracking)

**Purpose:** Tracks import runs for debugging and audit purposes.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `import_run_id` | UUID | Unique identifier for import run (NOT NULL) |
| `started_at` | TIMESTAMP | Import start time |
| `completed_at` | TIMESTAMP | Import completion time |
| `source_file` | TEXT | Source ZIP/XML file |
| `form_type` | VARCHAR(20) | Form type processed |
| `tax_year` | INTEGER | Tax year of data |
| `records_processed` | INTEGER | Total records attempted |
| `records_success` | INTEGER | Successfully imported |
| `records_failed` | INTEGER | Failed to import |
| `error_message` | TEXT | Error details if failed |
| `status` | VARCHAR(50) | 'running', 'completed', 'failed', 'partial' |
| `created_at` | TIMESTAMP | Record creation timestamp |

---

## Views

### vw_grants_with_funder
Joins grants with funder details for easy querying.

### vw_foundation_summary
Foundation summary with application status derived field:
- 'Preselected Only' - only_contri_to_preselected_ind = TRUE
- 'Open to Applications' - grants_to_organizations_ind = TRUE
- 'Unknown' - neither flag set

---

## Data Conventions

### Amounts
- All monetary amounts stored as `NUMERIC(15,2)` (15 digits, 2 decimal places)
- Amounts in USD, no currency conversion needed
- NULL indicates amount not reported

### Dates
- Date format: `YYYY-MM-DD` (ISO 8601)
- `tax_period_begin` and `tax_period_end` define the fiscal year
- `ruling_date` is when IRS granted exempt status

### Boolean Fields
- `TRUE`/`FALSE`/`NULL`
- NULL typically means "not applicable" or "not reported"
- Key filter: `only_contri_to_preselected_ind = FALSE` means open to applications

### NULL Handling
- NULL = field not present in XML or not applicable
- Empty string (`''`) = field present but empty
- Most queries should handle NULLs with COALESCE or IS NOT NULL filters

### EINs
- Stored as VARCHAR(20) to preserve leading zeros
- Format: 9 digits, no dashes (e.g., '123456789')

---

## Relationship Diagram

```
pf_returns (1) ----< (N) pf_grants
     |
     +----< (N) officers

nonprofit_returns (1) ----< (N) officers
     |
     +----< (1) schedule_a
```

---

## Common Queries

### Find foundations accepting applications
```sql
SELECT ein, business_name, state, total_assets_eoy_amt
FROM f990_2025.pf_returns
WHERE grants_to_organizations_ind = TRUE
  AND (only_contri_to_preselected_ind = FALSE OR only_contri_to_preselected_ind IS NULL)
ORDER BY total_assets_eoy_amt DESC NULLS LAST;
```

### Get grant history for a recipient
```sql
SELECT filer_ein, recipient_name, amount, purpose, tax_year
FROM f990_2025.pf_grants
WHERE recipient_ein = '123456789'
ORDER BY tax_year DESC, amount DESC;
```

### Foundation grant totals by state
```sql
SELECT pf.state, COUNT(*) as foundation_count, SUM(pf.total_grant_paid_amt) as total_grants
FROM f990_2025.pf_returns pf
WHERE pf.grants_to_organizations_ind = TRUE
GROUP BY pf.state
ORDER BY total_grants DESC NULLS LAST;
```

---

## Configuration Files

### config.yaml (Import Settings)
Location: `1. Database/F990-2025/1. Import/config.yaml`

Key settings:
- `database`: Connection parameters
- `source_data.base_path`: Where ZIP files are located
- `processing.sample_size`: 0 for full import, N for testing
- `checkpointing.enabled`: Resume interrupted imports

### Import Script
Location: `1. Database/F990-2025/1. Import/import_f990.py`

Usage:
```bash
python import_f990.py                 # Full import
python import_f990.py --sample 5      # Test with 5 records
python import_f990.py --validate-only # Run validation only
```
