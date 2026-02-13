# pf_returns -- Column Reference

**Table:** `f990_2025.pf_returns`
**Granularity:** One row per 990-PF filing (multiple rows per foundation across tax years)
**Total rows:** 638,698
**Unique foundations (EINs):** 143,184
**Tax years:** 2016-2024
**Source:** IRS 990-PF XML filings + post-import enrichment on 3 fields

---

## Record Metadata

| Column | Type | Foundations | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 143,184 | 100% | Auto-generated primary key |
| `ein` | VARCHAR | 143,184 | 100% | Employer Identification Number (9-digit, no dashes) |
| `business_name` | TEXT | 143,184 | 100% | Foundation's legal name as filed |
| `tax_year` | INTEGER | 143,184 | 100% | Tax year this return covers (e.g., 2023) |
| `tax_period_begin` | DATE | 143,184 | 100% | Start date of the fiscal year |
| `tax_period_end` | DATE | 143,184 | 100% | End date of the fiscal year |
| `source_file` | TEXT | 143,184 | 100% | Path to the IRS XML file this was parsed from |
| `return_timestamp` | TIMESTAMP | 143,184 | 100% | When the return was filed/submitted to IRS |
| `object_id` | VARCHAR | 143,184 | 100% | IRS internal identifier for this specific filing |
| `created_at` | TIMESTAMP | 143,184 | 100% | When this row was inserted into our DB |
| `updated_at` | TIMESTAMP | 143,184 | 100% | When this row was last modified |

## Contact Info (990-PF Header)

| Column | Type | Foundations | % | Meaning |
|--------|------|---:|---:|---------|
| `address_line1` | TEXT | 143,184 | 100% | Foundation's mailing address, line 1 |
| `address_line2` | TEXT | 0 | 0% | Suite/floor/PO Box, line 2 (never populated) |
| `city` | TEXT | 143,184 | 100% | City |
| `state` | VARCHAR | 143,145 | 100% | State code (2-letter) |
| `zip` | VARCHAR | 143,172 | 100% | ZIP code |
| `country` | TEXT | 143,184 | 100% | Country (usually US) |
| `phone_num` | VARCHAR | 138,009 | 96.4% | Main phone number. Partially enriched (96% XML, 4% propagated) |
| `email_address_txt` | TEXT | 0 | 0% | Email address (never populated in this table) |
| `website_url` | TEXT | 130,796 | 91.4% | Foundation website. Heavily enriched (29% XML, rest scraped) |

## Foundation Classification (Part VII-A)

| Column | Type | Foundations | % | Meaning |
|--------|------|---:|---:|---------|
| `private_operating_foundation_ind` | BOOLEAN | 143,184 | 100% | Is this a private OPERATING foundation? (runs programs, not just grants) |
| `exempt_operating_foundations_ind` | BOOLEAN | 143,184 | 100% | Has IRS ruling as exempt operating foundation? |
| `grants_to_organizations_ind` | BOOLEAN | 143,184 | 100% | Does this foundation make grants to organizations? |
| `grants_to_individuals_ind` | BOOLEAN | 143,184 | 100% | Does this foundation make grants to individuals? |
| `only_contri_to_preselected_ind` | BOOLEAN | 143,184 | 100% | Only gives to preselected recipients? FALSE = accepts applications |
| `foreign_activities_ind` | BOOLEAN | 143,184 | 100% | Conducts activities outside the US? |
| `contributing_manager_nm` | TEXT | 57,118 | 39.9% | Name of the foundation manager (Part VIII, substantial contributor) |
| `formation_yr` | INTEGER | 0 | 0% | Year the foundation was legally formed (never populated) |

## Financials (Part I / Balance Sheet)

| Column | Type | Foundations | % | Meaning |
|--------|------|---:|---:|---------|
| `total_revenue_amt` | NUMERIC | 143,184 | 100% | Total revenue (investment income + contributions + other) |
| `total_expenses_amt` | NUMERIC | 143,184 | 100% | Total expenses (grants + admin + other) |
| `total_assets_eoy_amt` | NUMERIC | 143,184 | 100% | Total assets at end of year (the main "size" metric) |
| `total_assets_boy_amt` | NUMERIC | 138,733 | 96.9% | Total assets at beginning of year |
| `fmv_assets_eoy_amt` | NUMERIC | 143,184 | 100% | Fair market value of assets at end of year |
| `net_assets_eoy_amt` | NUMERIC | 143,184 | 100% | Net assets (assets minus liabilities) at end of year |
| `net_assets_boy_amt` | NUMERIC | 137,119 | 95.8% | Net assets at beginning of year |
| `total_liabilities_eoy_amt` | NUMERIC | 143,184 | 100% | Total liabilities at end of year |
| `excess_revenue_over_expenses_amt` | NUMERIC | 143,184 | 100% | Revenue minus expenses (surplus or deficit) |
| `contributions_received_amt` | NUMERIC | 89,517 | 62.5% | Contributions and gifts received this year |
| `investment_income_amt` | NUMERIC | 143,184 | 100% | Income from investments (dividends, interest, capital gains) |

## Grantmaking (Part XV / Distribution)

| Column | Type | Foundations | % | Meaning |
|--------|------|---:|---:|---------|
| `total_grant_paid_amt` | NUMERIC | 124,782 | 87.1% | Total grants paid during this year |
| `qualifying_distributions_amt` | NUMERIC | 133,860 | 93.5% | Total qualifying distributions (grants + program expenses toward 5% payout) |
| `distributable_as_adjusted_amt` | NUMERIC | 133,636 | 93.3% | Amount foundation is required to distribute (5% rule) |
| `min_investment_return_amt` | NUMERIC | 140,683 | 98.3% | Minimum investment return (5% of avg FMV of assets) |
| `undistributed_income_cy_amt` | NUMERIC | 134,030 | 93.6% | Undistributed income for current year (how much they still owe) |
| `undistributed_income_py_ind` | BOOLEAN | 143,184 | 100% | Has undistributed income from prior years? (penalty risk) |
| `total_grant_approved_future_amt` | NUMERIC | 66,552 | 46.5% | Grants approved but not yet paid (committed for future) |
| `grants_payable_eoy_amt` | NUMERIC | 13,373 | 9.3% | Outstanding grant obligations at year end |

## Application Process (Part XV - Supplementary Info)

| Column | Type | Foundations | % | Meaning |
|--------|------|---:|---:|---------|
| `application_submission_info` | JSONB | 35,385 | 24.7% | Structured contact: `{name, phone, email, address}` |
| `app_contact_name` | TEXT | 35,162 | 24.6% | Contact person for applications (same data as JSONB `name`) |
| `app_contact_phone` | VARCHAR | 33,619 | 23.5% | Contact phone for applications (same data as JSONB `phone`) |
| `app_form_requirements` | TEXT | 33,301 | 23.3% | How to apply ("LETTER", "WRITTEN REQUEST", "ONLINE", etc.) |
| `app_restrictions` | TEXT | 33,171 | 23.2% | Restrictions on who can apply (geographic, sector, etc.) |
| `app_submission_deadlines` | TEXT | 33,066 | 23.1% | When applications are due ("APRIL 1", "ROLLING", "NONE", etc.) |
| `app_contact_email` | TEXT | 10,092 | 7.0% | Contact email for applications (same data as JSONB `email`) |

## Mission / Purpose (Part IX-A)

| Column | Type | Foundations | % | Meaning |
|--------|------|---:|---:|---------|
| `activity_or_mission_desc` | TEXT | 115,205 | 80.5% | Description of activities or mission |
| `mission_desc` | TEXT | 0 | 0% | Mission statement (never populated -- use `activity_or_mission_desc`) |
| `primary_exempt_purpose` | TEXT | 0 | 0% | Primary exempt purpose (never populated) |
| `activity_code_1` | VARCHAR | 0 | 0% | IRS activity code #1 (never populated) |
| `activity_code_2` | VARCHAR | 0 | 0% | IRS activity code #2 (never populated) |
| `activity_code_3` | VARCHAR | 0 | 0% | IRS activity code #3 (never populated) |

## Enriched Fields (added post-import)

| Column | Type | Foundations | % | Meaning |
|--------|------|---:|---:|---------|
| `ntee_code` | VARCHAR | 90,868 | 63.5% | NTEE classification code (e.g., "T20") |
| `ntee_source` | VARCHAR | 122,430 | 85.5% | Source of NTEE code (always `irs_bmf`) |
| `ntee_enriched_at` | TIMESTAMP | 122,430 | 85.5% | When NTEE lookup was done |
| `url_source` | VARCHAR | 124,814 | 87.2% | How website URL was found (xml, scraped, invalid, propagated) |
| `url_enriched_at` | TIMESTAMP | 124,814 | 87.2% | When URL enrichment was done |
| `url_validated` | BOOLEAN | 124,814 | 87.2% | Whether the URL was checked and found working |
| `phone_source` | VARCHAR | 117,703 | 82.2% | How phone was obtained (xml or propagated) |
| `phone_enriched_at` | TIMESTAMP | 117,703 | 82.2% | When phone enrichment was done |
| `phone_validated` | BOOLEAN | 117,703 | 82.2% | Whether phone number was verified |

---

## Dead Columns (never populated)

These columns exist in the schema but have zero data across all 638K rows:

- `address_line2` -- Suite/floor info (apparently not parsed from XML)
- `email_address_txt` -- Foundation email (not available in 990-PF XML)
- `formation_yr` -- Year formed (not parsed)
- `mission_desc` -- Mission statement (use `activity_or_mission_desc` instead)
- `primary_exempt_purpose` -- Exempt purpose text
- `activity_code_1/2/3` -- IRS activity codes
