# Prospect Call List v2 Report
**Date:** 2025-12-12

---

## Executive Summary

Generated a prospect call list of **600 prospects** with simplified filters, enriched with phone numbers from nonprofit_returns and contact names from officers table. Additionally, checked 74 websites for active fundraising and identified **21 organizations with current/upcoming fundraising events**.

---

## Deliverables

| File | Description |
|------|-------------|
| `DATA_2025-12-12_prospect_call_list_v2.csv` | Full 600 prospects with phone enrichment |
| `DATA_2025-12-12_prospect_call_list_v2_with_fundraising.csv` | Same + `current_fundraising` column (1/0/blank) |

---

## Filter Summary

| Criterion | Filter Applied |
|-----------|----------------|
| Sector | `sector IN ('E', 'P')` |
| Employees | `employee_count BETWEEN 0 AND 3` |
| Revenue | `total_revenue BETWEEN 1000000 AND 2000000` |
| Grant Dependency | `grant_dependency_pct >= 75` |
| Foundation Grants | `num_foundation_grants <= 3` |

**Result:** 600 prospects (164 sector E, 436 sector P)

---

## Data Enrichment

### Phone Numbers
- **Source:** `f990_2025.nonprofit_returns` (most recent tax year)
- **Result:** 600/600 (100%) have phone numbers

### Contact Names
- **Source:** `f990_2025.officers` table with title priority ranking
- **Priority:** CEO > Chief Executive > Executive Director > Founder > President > Director
- **Result:** 546/600 (91%) have contact names

### Fundraising Events
- **Method:** 3 parallel agents checked 74 websites with valid URLs
- **Checked:** First 100 prospects, filtered to 74 with valid URLs
- **Result:** 21 organizations have active/upcoming fundraising

---

## Organizations with Active Fundraising (21)

| Organization | State | Contact | Fundraising Activity |
|-------------|-------|---------|---------------------|
| Medical Ministries International | CA | Ralph Handly OD | Gala event, Adopt-A-Box program |
| The David Foster Foundation | CA | Michael Ravenhill | Aeroplan Miles, Sponsor a Family |
| Children's Oncology Support Fund | CA | Thomas Pierce | Donate Today campaign, corporate giving |
| 4 Kids 2 Kids | CA | Lorie Vos | Active Toy Drive |
| POPS Foundation | CA | Kenneth Yeung | Charity concerts (June 2025) |
| Kern Medical Center Foundation | CA | — | 18th Annual Toy Drive/Car Show |
| New Yorkers for Local Businesses | CA | Roy Iraci | eFundraising campaign |
| Donate Life California | CA | Jim Martin | Run Walk event |
| Home Preservation & Prevention Inc | CA | Katherine Peoples McGill | Wildfire Relief Fund |
| Mercy Medical Center Merced Foundation | CA | Jacob McDougal | "Gratitude For Impact" year-end appeal, Golf Classic 2025 |
| Friends of the Children - Coachella Valley | CA | Karrie Schaaf | "Triple Your Support" year-end campaign |
| Firefighter Cancer Support Network | CA | Lisa Marie Raggio | 5 Alarm 5K races, golf tournaments |
| Karimu International Help Foundation | CA | Marianne Kent-Stoll | 6 campaigns for healthcare/education |
| NTNU Heritage Foundation | CA | Ching-Lai Huoh | Anniversary Presentation campaign |
| Korean American Community Foundation | CA | So Yong Park | 2026 HANA Gala, monthly giving |
| Mercy Coalition of West Sacramento | CA | — | Impact100 grant, Mosaic City Breakfast |
| Camp Laurel Foundation | CA | Margot Anderson | "DREAM IT. DO IT. Summit" |
| F C Cancer Foundation | CA | John McGuinness | 5k Walk (Mar 2025), Golf Tournament 2025 |
| Matthew 10 International Ministry | TN | Dr Pete Sulack | "The Harvest" monthly program |
| Water Street Health Services | PA | John Crowley | Holiday giving campaign |
| Boca West Community Charitable | FL | Pamela Weinroth | Raffle, Golf Challenge, Bikes for Tikes |

---

## Data Quality Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total prospects | 600 | 100% |
| With phone | 600 | 100% |
| With contact name | 546 | 91% |
| With website | 518 | 86% |
| Websites checked | 74 | — |
| Active fundraising found | 21 | 28% of checked |
| Not checked (blank) | 526 | — |

---

## Distribution

### By Sector
| Sector | Count | % |
|--------|-------|---|
| P - Human Services | 436 | 73% |
| E - Healthcare/Education | 164 | 27% |

### By State (Top 10)
| State | Count |
|-------|-------|
| CA | 229 |
| TX | 39 |
| FL | 37 |
| NY | 24 |
| PA | 22 |
| OH | 17 |
| IL | 16 |
| WA | 15 |
| NC | 14 |
| MI | 13 |

---

## Recommendations

1. **Prioritize Fundraising Orgs:** The 21 organizations with active fundraising are warmer leads — they're actively seeking donations and may be more receptive to funding strategy help.

2. **California Concentration:** 17 of 21 fundraising orgs (81%) are in California. Consider a CA-focused calling campaign.

3. **Year-End Timing:** Many orgs have year-end giving campaigns active now — good timing for outreach about grant diversification.

4. **Missing Contacts:** 54 prospects (9%) lack contact names. These may need LinkedIn lookup before calling.

---

*Generated: 2025-12-12*
