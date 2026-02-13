# schedule_d_endowments -- Column Reference

**Table:** `f990_2025.schedule_d_endowments`
**Granularity:** One row per organization's endowment data from Schedule D Part V
**Total rows:** 36,936
**Unique EINs:** 34,935
**Source:** 990 Schedule D Part V XML filings

---

## Record Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `id` | INTEGER | 36,936 | 100.0% | Auto-generated primary key |
| `np_return_id` | INTEGER | 36,936 | 100.0% | FK to nonprofit_returns.id |
| `ein` | VARCHAR | 36,936 | 100.0% | Employer Identification Number |
| `tax_year` | INTEGER | 36,936 | 100.0% | Tax year of the filing |
| `created_at` | TIMESTAMP | 36,936 | 100.0% | When this row was inserted into our DB |

## Current Year Endowment

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `endowment_boy_amt` | NUMERIC | 34,989 | 94.7% | Endowment balance at beginning of current year |
| `contributions_amt` | NUMERIC | 18,807 | 50.9% | Contributions to endowment during current year |
| `investment_earnings_amt` | NUMERIC | 30,622 | 82.9% | Net investment earnings/losses during current year |
| `grants_or_scholarships_amt` | NUMERIC | 8,824 | 23.9% | Grants or scholarships paid from endowment |
| `other_expenditures_amt` | NUMERIC | 15,987 | 43.3% | Other expenditures from endowment |
| `admin_expenses_amt` | NUMERIC | 12,431 | 33.7% | Administrative expenses charged to endowment |
| `endowment_eoy_amt` | NUMERIC | 35,529 | 96.2% | Endowment balance at end of current year |

## Endowment Composition

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `board_designated_pct` | NUMERIC | 20,625 | 55.8% | Percentage that is board-designated (quasi-endowment) |
| `perm_restricted_pct` | NUMERIC | 23,437 | 63.5% | Percentage that is permanently restricted |
| `temp_restricted_pct` | NUMERIC | 17,139 | 46.4% | Percentage that is temporarily restricted |

## Year -1 Endowment

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `yr1_endowment_boy_amt` | NUMERIC | 0 | 0% | Year -1: endowment beginning balance |
| `yr1_contributions_amt` | NUMERIC | 0 | 0% | Year -1: contributions |
| `yr1_investment_earnings_amt` | NUMERIC | 0 | 0% | Year -1: investment earnings/losses |
| `yr1_grants_or_scholarships_amt` | NUMERIC | 0 | 0% | Year -1: grants or scholarships |
| `yr1_other_expenditures_amt` | NUMERIC | 0 | 0% | Year -1: other expenditures |
| `yr1_admin_expenses_amt` | NUMERIC | 0 | 0% | Year -1: admin expenses |
| `yr1_endowment_eoy_amt` | NUMERIC | 0 | 0% | Year -1: endowment ending balance |

## Year -2 Endowment

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `yr2_endowment_boy_amt` | NUMERIC | 0 | 0% | Year -2: endowment beginning balance |
| `yr2_contributions_amt` | NUMERIC | 0 | 0% | Year -2: contributions |
| `yr2_investment_earnings_amt` | NUMERIC | 0 | 0% | Year -2: investment earnings/losses |
| `yr2_grants_or_scholarships_amt` | NUMERIC | 0 | 0% | Year -2: grants or scholarships |
| `yr2_other_expenditures_amt` | NUMERIC | 0 | 0% | Year -2: other expenditures |
| `yr2_admin_expenses_amt` | NUMERIC | 0 | 0% | Year -2: admin expenses |
| `yr2_endowment_eoy_amt` | NUMERIC | 0 | 0% | Year -2: endowment ending balance |

## Year -3 Endowment

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `yr3_endowment_boy_amt` | NUMERIC | 0 | 0% | Year -3: endowment beginning balance |
| `yr3_contributions_amt` | NUMERIC | 0 | 0% | Year -3: contributions |
| `yr3_investment_earnings_amt` | NUMERIC | 0 | 0% | Year -3: investment earnings/losses |
| `yr3_grants_or_scholarships_amt` | NUMERIC | 0 | 0% | Year -3: grants or scholarships |
| `yr3_other_expenditures_amt` | NUMERIC | 0 | 0% | Year -3: other expenditures |
| `yr3_admin_expenses_amt` | NUMERIC | 0 | 0% | Year -3: admin expenses |
| `yr3_endowment_eoy_amt` | NUMERIC | 0 | 0% | Year -3: endowment ending balance |

## Year -4 Endowment

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `yr4_endowment_boy_amt` | NUMERIC | 0 | 0% | Year -4: endowment beginning balance |
| `yr4_contributions_amt` | NUMERIC | 0 | 0% | Year -4: contributions |
| `yr4_investment_earnings_amt` | NUMERIC | 0 | 0% | Year -4: investment earnings/losses |
| `yr4_grants_or_scholarships_amt` | NUMERIC | 0 | 0% | Year -4: grants or scholarships |
| `yr4_other_expenditures_amt` | NUMERIC | 0 | 0% | Year -4: other expenditures |
| `yr4_admin_expenses_amt` | NUMERIC | 0 | 0% | Year -4: admin expenses |
| `yr4_endowment_eoy_amt` | NUMERIC | 0 | 0% | Year -4: endowment ending balance |

## Donor Advised Funds

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `donor_advised_funds_cnt` | INTEGER | 0 | 0% | Number of donor advised funds |
| `donor_advised_funds_value_eoy` | NUMERIC | 2,063 | 5.6% | Aggregate value of donor advised funds at EOY |
| `donor_advised_funds_contri_amt` | NUMERIC | 1,857 | 5.0% | Total contributions to donor advised funds |
| `donor_advised_funds_grants_amt` | NUMERIC | 1,818 | 4.9% | Total grants from donor advised funds |

---

## Dead Columns (never populated)

These columns exist but have zero data across all 36,936 rows:

- `yr1_endowment_boy_amt` -- Year -1: endowment beginning balance
- `yr1_contributions_amt` -- Year -1: contributions
- `yr1_investment_earnings_amt` -- Year -1: investment earnings/losses
- `yr1_grants_or_scholarships_amt` -- Year -1: grants or scholarships
- `yr1_other_expenditures_amt` -- Year -1: other expenditures
- `yr1_admin_expenses_amt` -- Year -1: admin expenses
- `yr1_endowment_eoy_amt` -- Year -1: endowment ending balance
- `yr2_endowment_boy_amt` -- Year -2: endowment beginning balance
- `yr2_contributions_amt` -- Year -2: contributions
- `yr2_investment_earnings_amt` -- Year -2: investment earnings/losses
- `yr2_grants_or_scholarships_amt` -- Year -2: grants or scholarships
- `yr2_other_expenditures_amt` -- Year -2: other expenditures
- `yr2_admin_expenses_amt` -- Year -2: admin expenses
- `yr2_endowment_eoy_amt` -- Year -2: endowment ending balance
- `yr3_endowment_boy_amt` -- Year -3: endowment beginning balance
- `yr3_contributions_amt` -- Year -3: contributions
- `yr3_investment_earnings_amt` -- Year -3: investment earnings/losses
- `yr3_grants_or_scholarships_amt` -- Year -3: grants or scholarships
- `yr3_other_expenditures_amt` -- Year -3: other expenditures
- `yr3_admin_expenses_amt` -- Year -3: admin expenses
- `yr3_endowment_eoy_amt` -- Year -3: endowment ending balance
- `yr4_endowment_boy_amt` -- Year -4: endowment beginning balance
- `yr4_contributions_amt` -- Year -4: contributions
- `yr4_investment_earnings_amt` -- Year -4: investment earnings/losses
- `yr4_grants_or_scholarships_amt` -- Year -4: grants or scholarships
- `yr4_other_expenditures_amt` -- Year -4: other expenditures
- `yr4_admin_expenses_amt` -- Year -4: admin expenses
- `yr4_endowment_eoy_amt` -- Year -4: endowment ending balance
- `donor_advised_funds_cnt` -- Number of donor advised funds
