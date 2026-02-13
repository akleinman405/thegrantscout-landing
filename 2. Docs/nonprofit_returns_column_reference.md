# nonprofit_returns -- Column Reference

**Table:** `f990_2025.nonprofit_returns`
**Granularity:** One row per 990/990-EZ filing (multiple rows per nonprofit across tax years)
**Total rows:** 2,953,274
**Unique nonprofits (EINs):** 673,381
**Tax years:** 2016-2024
**Source:** IRS Form 990 and Form 990-EZ XML e-filings

---

## Record Metadata

| Column | Type | Nonprofits | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 673,381 | 100% | Auto-generated primary key |
| `ein` | VARCHAR | 673,381 | 100% | Employer Identification Number (9-digit, no dashes) |
| `organization_name` | TEXT | 673,381 | 100% | Nonprofit's legal name as filed |
| `tax_year` | INTEGER | 673,381 | 100% | Tax year this return covers (e.g., 2023) |
| `tax_period_begin` | DATE | 673,381 | 100% | Start date of the fiscal year |
| `tax_period_end` | DATE | 673,381 | 100% | End date of the fiscal year |
| `form_type` | VARCHAR | 673,381 | 100% | IRS form type: `990` (larger orgs, revenue >$200K) or `990EZ` (smaller orgs, revenue <$200K) |
| `source_file` | TEXT | 673,381 | 100% | Path to the IRS XML file this was parsed from |
| `object_id` | VARCHAR | 560,119 | 83.2% | IRS internal identifier for this specific filing |
| `created_at` | TIMESTAMP | 673,381 | 100% | When this row was inserted into our DB |
| `updated_at` | TIMESTAMP | 673,381 | 100% | When this row was last modified |

## Contact Info (990 Header)

| Column | Type | Nonprofits | % | Meaning |
|--------|------|---:|---:|---------|
| `address_line1` | TEXT | 672,786 | 99.9% | Nonprofit's mailing address, line 1 |
| `address_line2` | TEXT | 0 | 0% | Suite/floor/PO Box, line 2 (never populated) |
| `city` | TEXT | 672,786 | 99.9% | City |
| `state` | VARCHAR | 672,786 | 99.9% | State code (2-letter) |
| `zip` | VARCHAR | 672,786 | 99.9% | ZIP code |
| `country` | TEXT | 673,381 | 100% | Country (usually US) |
| `phone` | VARCHAR | 673,381 | 100% | Main phone number |
| `website` | TEXT | 578,028 | 85.8% | Organization website URL |

## Financials (Part I / Balance Sheet)

| Column | Type | Nonprofits | % | Meaning |
|--------|------|---:|---:|---------|
| `total_revenue` | NUMERIC | 668,551 | 99.3% | Total revenue from all sources |
| `total_expenses` | NUMERIC | 665,673 | 98.9% | Total expenses |
| `total_assets_boy` | NUMERIC | 402,488 | 59.8% | Total assets at beginning of year (990 only -- not on 990-EZ) |
| `total_assets_eoy` | NUMERIC | 412,797 | 61.3% | Total assets at end of year (990 only -- not on 990-EZ) |
| `net_assets_boy` | NUMERIC | 646,099 | 95.9% | Net assets at beginning of year |
| `net_assets_eoy` | NUMERIC | 665,951 | 98.9% | Net assets (assets minus liabilities) at end of year |
| `contributions_grants` | NUMERIC | 639,130 | 94.9% | Contributions, gifts, and grants received |
| `program_service_revenue` | NUMERIC | 557,793 | 82.8% | Revenue from program services (fees, contracts, etc.) |
| `investment_income` | NUMERIC | 564,174 | 83.8% | Income from investments (dividends, interest, capital gains) |

**Note:** `total_assets_boy` and `total_assets_eoy` have ~60% coverage because they are reported on the full Form 990 balance sheet but not on Form 990-EZ. The 990-EZ reports `net_assets` instead.

## Mission / Purpose / Programs (Part III)

| Column | Type | Nonprofits | % | Meaning |
|--------|------|---:|---:|---------|
| `mission_description` | TEXT | 673,381 | 100% | Brief mission statement -- present on both 990 and 990-EZ |
| `activity_description` | TEXT | 412,797 | 61.3% | Description of most significant activities. **Form 990 only** (Part III, Line 1). Not populated for 990-EZ filers. |
| `primary_exempt_purpose` | TEXT | 334,254 | 49.6% | Primary exempt purpose statement. **Form 990-EZ only** (Part III). Not populated for 990 filers. |
| `program_1_desc` | TEXT | 377,992 | 56.1% | Program service accomplishment #1 description (Part III, Line 4a). **Primarily 990 filers.** |
| `program_2_desc` | TEXT | 161,782 | 24.0% | Program service accomplishment #2 description (Part III, Line 4b) |
| `program_3_desc` | TEXT | 81,064 | 12.0% | Program service accomplishment #3 description (Part III, Line 4c) |
| `program_1_expense_amt` | NUMERIC | 295,044 | 43.8% | Expenses for program #1 |
| `program_2_expense_amt` | NUMERIC | 138,564 | 20.6% | Expenses for program #2 |
| `program_3_expense_amt` | NUMERIC | 70,443 | 10.5% | Expenses for program #3 |
| `program_1_revenue_amt` | NUMERIC | 185,875 | 27.6% | Revenue for program #1 |

**Key distinction:** `activity_description` (Form 990) and `primary_exempt_purpose` (Form 990-EZ) serve the same purpose -- describing what the nonprofit does -- but come from different form sections. An org will typically have one or the other depending on which form they file.

## Classification Codes

| Column | Type | Nonprofits | % | Meaning |
|--------|------|---:|---:|---------|
| `activity_code_1` | VARCHAR | 919 | 0.1% | IRS activity code #1 (rarely populated) |
| `activity_code_2` | VARCHAR | 281 | 0.0% | IRS activity code #2 (rarely populated) |
| `activity_code_3` | VARCHAR | 173 | 0.0% | IRS activity code #3 (rarely populated) |
| `ntee_code` | VARCHAR | 452,209 | 67.2% | National Taxonomy of Exempt Entities code (e.g., "B20" = elementary/secondary education) |
| `ruling_date` | DATE | 0 | 0% | Date IRS granted tax-exempt status (never populated) |

## Governance (Part VI)

| Column | Type | Nonprofits | % | Meaning |
|--------|------|---:|---:|---------|
| `foreign_activities_ind` | BOOLEAN | 673,381 | 100% | Does the org conduct activities outside the US? |
| `voting_members_governing_body_cnt` | INTEGER | 412,797 | 61.3% | Number of voting members on governing board. **Form 990 only.** |
| `voting_members_independent_cnt` | INTEGER | 412,797 | 61.3% | Number of independent voting members. **Form 990 only.** |
| `total_employees_cnt` | INTEGER | 412,797 | 61.3% | Total number of employees. **Form 990 only.** |
| `total_volunteers_cnt` | INTEGER | 322,949 | 48.0% | Total number of volunteers |

**Note:** Governance and employee count fields are only populated for Form 990 filers. 990-EZ does not require this level of reporting.

---

## Dead Columns (never populated)

These columns exist in the schema but have zero data across all 2.95M rows:

- `address_line2` -- Suite/floor info (not parsed from XML)
- `ruling_date` -- Date of IRS tax-exempt ruling (not parsed)

## Nearly Dead Columns (<1% populated)

- `activity_code_1/2/3` -- IRS activity codes (919 / 281 / 173 EINs respectively). These legacy codes are rarely filed in modern e-file returns.

---

## Form 990 vs 990-EZ Field Availability

| Field Category | Form 990 | Form 990-EZ |
|----------------|----------|-------------|
| Basic info (name, EIN, address, phone) | Yes | Yes |
| Mission description | Yes | Yes |
| Activity description | **Yes** | No |
| Primary exempt purpose | No | **Yes** |
| Program descriptions (1-3) | **Yes** | Limited |
| Total revenue / expenses | Yes | Yes |
| Total assets (BOY/EOY) | **Yes** | No |
| Net assets (BOY/EOY) | Yes | Yes |
| Employee / volunteer counts | **Yes** | Volunteers only (partial) |
| Voting board members | **Yes** | No |
| NTEE code | Yes | Yes |
