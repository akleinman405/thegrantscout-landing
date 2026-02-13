# np_functional_expenses -- Column Reference

**Table:** `f990_2025.np_functional_expenses`
**Granularity:** One row per filing with functional expense breakdowns (990 Part IX)
**Total rows:** 360,191
**Unique EINs:** 333,995
**Source:** 990 Part IX XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 360,191 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 360,191 | 100.0% | FK to nonprofit_returns.id |
| `ein` | VARCHAR | 360,191 | 100.0% | Employer Identification Number |
| `tax_year` | INTEGER | 360,191 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 360,191 | 100.0% | When this row was inserted into our DB |

## Grants

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `grants_to_domestic_orgs_amt` | NUMERIC | 138,190 | 38.4% | Grants to domestic organizations |
| `grants_to_domestic_individuals_amt` | NUMERIC | 120,032 | 33.3% | Grants to domestic individuals |
| `grants_to_foreign_orgs_amt` | NUMERIC | 90,047 | 25.0% | Grants to foreign organizations |

## Compensation

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `compensation_current_officers_amt` | NUMERIC | 200,438 | 55.6% | Compensation of current officers/directors/trustees |
| `compensation_disqualified_amt` | NUMERIC | 86,700 | 24.1% | Compensation to disqualified persons |
| `other_salaries_wages_amt` | NUMERIC | 241,545 | 67.1% | Other salaries and wages |
| `pension_plan_contributions_amt` | NUMERIC | 140,456 | 39.0% | Pension plan accruals and contributions |
| `other_employee_benefits_amt` | NUMERIC | 188,194 | 52.2% | Other employee benefits |
| `payroll_taxes_amt` | NUMERIC | 239,939 | 66.6% | Payroll taxes |

## Professional Fees

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `management_fees_amt` | NUMERIC | 120,265 | 33.4% | Management and general fees |
| `legal_fees_amt` | NUMERIC | 167,198 | 46.4% | Legal fees |
| `accounting_fees_amt` | NUMERIC | 282,231 | 78.4% | Accounting fees |
| `lobbying_fees_amt` | NUMERIC | 89,189 | 24.8% | Lobbying fees |
| `fundraising_fees_amt` | NUMERIC | 0 | 0% | Professional fundraising fees |
| `investment_mgmt_fees_amt` | NUMERIC | 120,723 | 33.5% | Investment management fees |

## Operations

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `advertising_promotion_amt` | NUMERIC | 219,496 | 60.9% | Advertising and promotion |
| `office_expenses_amt` | NUMERIC | 299,948 | 83.3% | Office expenses |
| `info_technology_amt` | NUMERIC | 174,406 | 48.4% | Information technology |
| `occupancy_amt` | NUMERIC | 248,265 | 68.9% | Occupancy expenses |
| `travel_amt` | NUMERIC | 212,560 | 59.0% | Travel |
| `conferences_amt` | NUMERIC | 180,340 | 50.1% | Conferences, conventions, and meetings |
| `interest_amt` | NUMERIC | 149,474 | 41.5% | Interest expense |
| `depreciation_amt` | NUMERIC | 236,982 | 65.8% | Depreciation, depletion, and amortization |
| `insurance_amt` | NUMERIC | 280,536 | 77.9% | Insurance |

## Totals

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `total_functional_expenses_amt` | NUMERIC | 360,191 | 100.0% | Total functional expenses (all categories) |
| `total_joint_costs_amt` | NUMERIC | 0 | 0% | Total joint costs (allocated across functions) |
| `total_program_services_amt` | NUMERIC | 340,010 | 94.4% | Total program services expenses |
| `total_management_general_amt` | NUMERIC | 339,229 | 94.2% | Total management and general expenses |
| `total_fundraising_amt` | NUMERIC | 337,944 | 93.8% | Total fundraising expenses |

---

## Dead Columns (never populated)

These columns exist but have zero data across all 360,191 rows:

- `fundraising_fees_amt` -- Professional fundraising fees
- `total_joint_costs_amt` -- Total joint costs (allocated across functions)
