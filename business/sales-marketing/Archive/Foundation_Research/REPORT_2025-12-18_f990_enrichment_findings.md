# F990 Data Enrichment Findings Report

**Date:** 2025-12-18
**Purpose:** Enrich foundation management company contacts with 990 filing data

---

## Executive Summary

Queried the f990_2025 database to enrich contact data with phone numbers, EINs, asset sizes, and grant activity. **15 of 41 target companies** were found in 990 filings, representing the community foundations, DAF sponsors, and fiscal sponsors in our list.

**Key Finding:** Dedicated foundation managers (Foundation Source, Sterling, etc.) are for-profit service companies and do NOT file 990s. They are not in our database. Community foundations and fiscal sponsors DO file 990s and appear as **grant recipients** from private foundations.

---

## Organizations Found in 990 Data

| Organization | EIN | Phone (990) | Assets | Grants Received (2022+) | Capacity Grants |
|-------------|-----|-------------|--------|------------------------|-----------------|
| Fidelity Charitable Gift Fund | 110303001 | 800-952-4438 | $56.7B | 176 | 45 |
| Schwab Charitable (DAFgiving360) | 311640316 | 800-746-6216 | $41.1B | 3 | 0 |
| National Philanthropic Trust | 237825575 | 215-277-3010 | $28.2B | 11 | 2 |
| Vanguard Charitable | 232888152 | 888-383-4483 | $17.0B | 28 | 7 |
| Silicon Valley Community Foundation | 205205488 | 650-450-5400 | $10.4B | 139 | 32 |
| Chicago Community Trust | 362167000 | 312-616-8000 | $6.0B | 67 | 24 |
| Foundation for the Carolinas | 566047886 | 704-973-4500 | $3.5B | 192 | 94 |
| Cleveland Foundation | 340714588 | 216-861-3810 | $2.9B | 61 | 16 |
| California Community Foundation | 953510055 | 213-413-4130 | $2.1B | 249 | 39 |
| Marin Community Foundation | 943007979 | 415-464-2500 | $1.1B | 34 | 5 |
| Rockefeller Philanthropy Advisors | 133615533 | 212-812-4330 | $912M | 614 | 42 |
| New Venture Fund | 205806345 | 202-595-1061 | $768M | 1,071 | 111 |
| Tides Foundation | 510198509 | 415-561-6400 | $646M | 567 | 96 |
| Bridgespan Group | 311625487 | 617-572-2833 | $204M | 32 | 2 |
| Fractured Atlas | 113451703 | 212-277-8020 | $31M | 453 | 84 |

---

## Organizations NOT in 990 Data (For-Profit or Not Required to File)

These companies are for-profit service providers or trust companies that don't file Form 990:

| Company | Type | Reason Not in 990 |
|---------|------|-------------------|
| Foundation Source | Dedicated Manager | For-profit service company |
| Pacific Foundation Services | Dedicated Manager | For-profit (acquired by Foundation Source) |
| Sterling Foundation Management | Dedicated Manager | For-profit service company |
| Crewe Foundation Services | Dedicated Manager | For-profit service company |
| BlueStone Services | Outsourced Admin | For-profit (KatzAbosch subsidiary) |
| Foundation Group | Compliance Services | For-profit service company |
| Bessemer Trust | Multi-Family Office | For-profit trust company |
| Glenmede Trust | Trust Company | For-profit trust company |
| Fiduciary Trust Company | Trust Company | For-profit trust company |
| Arden Trust Company | Trust Company | For-profit trust company |
| Third Plateau | Consulting | For-profit consulting firm |
| CCS Fundraising | Consulting | For-profit consulting firm |
| Armanino | CPA Firm | For-profit accounting firm |
| GHJ Advisors | CPA Firm | For-profit accounting firm |
| Plante Moran | CPA Firm | For-profit accounting firm |
| J.P. Morgan Private Bank | Bank | For-profit financial institution |
| Goldman Sachs Ayco | Bank | For-profit financial institution |
| UBS | Bank | For-profit financial institution |

---

## Key Insights

### 1. Grant Activity Shows Market Position

The organizations receiving the most grants from private foundations are likely also:
- **Receiving DAF contributions** from private foundations
- **Well-networked** in the philanthropy ecosystem
- **Trusted partners** for foundation giving

**Top 5 by grants received (2022+):**
1. New Venture Fund: 1,071 grants ($573M)
2. Rockefeller Philanthropy Advisors: 614 grants ($569M)
3. Tides Foundation: 567 grants ($159M)
4. Fractured Atlas: 453 grants ($23M)
5. California Community Foundation: 249 grants ($61M)

### 2. Capacity/GOS Grants Indicate Trust Level

Organizations receiving capacity-building or general operating support grants are viewed as trusted partners:

**Top 5 by capacity grants:**
1. New Venture Fund: 111 capacity grants
2. Tides Foundation: 96 capacity grants
3. Foundation for the Carolinas: 94 capacity grants
4. Fractured Atlas: 84 capacity grants
5. Fidelity Charitable: 45 capacity grants

### 3. Phone Numbers Are Reliable

990-reported phone numbers are official organization contacts, more reliable than web-scraped or inferred emails. These have been added to the enriched CSV.

---

## Lessons Learned

### What Worked
1. **Community foundations and fiscal sponsors have rich 990 data** - phone, assets, grants, all available
2. **Grant receipt data shows ecosystem connections** - who funds whom reveals relationships
3. **Capacity grant analysis** adds a trust/relationship indicator

### Limitations
1. **For-profit foundation managers have NO 990 data** - Foundation Source, Sterling, etc. are invisible in IRS data
2. **Foundation management relationships are NOT captured** - We can't tell from 990 data which foundations are managed by which service providers
3. **Trust companies and banks file different forms** - Not in 990 universe

### Data Quality Notes
1. Phone numbers in 990s are sometimes outdated (organization moves, number changes)
2. Some organizations have multiple 990 filings with different phone numbers
3. Asset values reflect fiscal year-end, may be 1-2 years old

---

## Recommendations for Sales Outreach

### Tier 1 Priority (Have 990 data + verified phones)
Use 990 phone numbers as secondary contact method:
- Community Foundations (6 orgs with direct lines)
- DAF Sponsors (4 orgs with toll-free numbers)
- Fiscal Sponsors (3 orgs with verified phones)

### Tier 2 Priority (No 990 data - use web research)
Continue with LinkedIn and website-based outreach:
- Dedicated foundation managers
- Trust companies
- CPA firms

### Cross-Reference Opportunity
The organizations receiving the most foundation grants are likely TheGrantScout's future partners:
- They see grant activity data
- They work with grantees who need our product
- They could refer/recommend our service

---

## Appendix: Column Definitions Added to CSV

| Column | Description |
|--------|-------------|
| ein_990 | IRS EIN from 990 filing |
| phone_990 | Phone number from 990 filing (10 digits, no formatting) |
| assets_990 | Total assets from most recent 990 |
| grants_received_2022plus | Number of grants received from private foundations (2022+) |
| unique_funders | Number of distinct private foundations that funded them |
| capacity_grants_received | Grants with capacity/GOS/unrestricted purpose text |

---

*Generated 2025-12-18 for TheGrantScout*
