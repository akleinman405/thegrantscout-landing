# Reachability Flags Summary Report
## REPORT_2025-12-10_reachability_flags_summary.md

---

## Executive Summary

Added 7 reachability flag columns to `f990_2025.prospects` table to identify high-reachability prospects.

## Flag Distribution

**Total Prospects:** 74,144

| Flag | Count | % of Total | Description |
|------|-------|------------|-------------|
| `reach_employees_1_10` | 23,571 | 31.8% | 1-10 employees (small team, reachable) |
| `reach_revenue_1m_2m` | 22,977 | 31.0% | $1M-$2M revenue (sweet spot) |
| `reach_form_990` | 74,144 | 100.0% | Files Form 990 (more established) |
| `reach_sector_e_p` | 13,881 | 18.7% | Health (E) or Human Services (P) |
| `reach_grant_dep_75` | 48,545 | 65.5% | ≥75% grant dependent |
| `reach_more_employees_than_volunteers` | 26,887 | 36.3% | Professional staff > volunteers |
| **`reach_all_flags`** | **290** | **0.4%** | **All criteria met** |

## Distribution by Number of Flags Met

| Flags Met | Count | % of Total |
|-----------|-------|------------|
| 6 | 290 | 0.4% |
| 5 | 3,904 | 5.3% |
| 4 | 14,822 | 20.0% |
| 3 | 25,895 | 34.9% |
| 2 | 22,539 | 30.4% |
| 1 | 6,694 | 9.0% |

## Top 20 Prospects with All Flags

| EIN | Organization | State | Sector | Revenue | Employees | ICP Score |
|-----|--------------|-------|--------|---------|-----------|-----------|
| 800291226 | Indian Child and Family Preservatio | CA | P | $1.1M | 7 | 12 |
| 331070775 | CHANGING PEOPLES LIVES INC | CA | P | $1.3M | 10 | 12 |
| 453957719 | INNOVATIVE HEALTH SOLUTIONS | CA | E | $1.2M | 6 | 12 |
| 454436246 | GRACE SOCIAL AND MEDICAL SERVICES I | CA | P | $1.0M | 8 | 12 |
| 461434482 | CALIFORNIA COMMUNITY ACTION | CA | P | $1.5M | 7 | 12 |
| 461816160 | NEW ERA FFA | CA | P | $1.7M | 7 | 12 |
| 472296503 | ST LUKES FAMILY MEDICAL GROUP | CA | E | $1.6M | 6 | 12 |
| 770617600 | Avante-Garde Foster Family Services | CA | P | $1.0M | 7 | 12 |
| 810688043 | PWT United Inc | CA | P | $1.5M | 8 | 12 |
| 823723957 | 4EVERGREEN FOSTER FAMILY AGENCY INC | CA | P | $1.8M | 6 | 12 |
| 862688341 | NATIVE SOLUTIONS FAMILY GUIDANCE CE | CA | P | $1.7M | 5 | 12 |
| 942882426 | ROUNDHOUSE COUNCIL INC | CA | P | $1.4M | 7 | 12 |
| 800875187 | RETRAINING THE VILLAGE | CA | P | $1.3M | 7 | 12 |
| 814700851 | AFRICAN ADVOCACY NETWORK | CA | P | $1.8M | 10 | 12 |
| 953842560 | KOREAN AMERICAN FEDERATION OF LA | CA | P | $1.8M | 8 | 12 |
| 853173347 | THE VICTORIA PROJECT INC | CA | E | $1.4M | 5 | 12 |
| 954648247 | Fathers and Mothers Who Care | CA | P | $1.0M | 7 | 12 |
| 834275967 | PRIME WELLNESS COMMUNITY | CA | E | $1.2M | 10 | 12 |
| 200015196 | DEAFHOPE | CA | P | $1.1M | 7 | 12 |
| 720949444 | MAMOU HEALTH RESOURCES INC | LA | E | $1.9M | 10 | 11 |

## Reachability by Priority Tier

| Tier | With All Flags | Total | % Reachable |
|------|----------------|-------|-------------|
| Tier 1 (High touch) | 196 | 6,862 | 2.9% |
| Tier 2 (Template) | 94 | 51,134 | 0.2% |
| Tier 3 (Mail merge) | 0 | 16,148 | 0.0% |

## ICP Score by Reachability

| Group | Avg ICP | Min | Max |
|-------|---------|-----|-----|
| Not all flags | 6.9 | 1 | 12 |
| All flags | 9.9 | 7 | 12 |

---

## Column Definitions

| Column | Logic |
|--------|-------|
| `reach_employees_1_10` | `employee_count BETWEEN 1 AND 10` |
| `reach_revenue_1m_2m` | `total_revenue BETWEEN 1000000 AND 2000000` |
| `reach_form_990` | `form_type = '990'` |
| `reach_sector_e_p` | `sector IN ('E', 'P')` |
| `reach_grant_dep_75` | `grant_dependency_pct >= 75` |
| `reach_more_employees_than_volunteers` | `employee_count > COALESCE(volunteer_count, 0)` |
| `reach_all_flags` | All above = 1 |

---

*Generated: 2025-12-10*
