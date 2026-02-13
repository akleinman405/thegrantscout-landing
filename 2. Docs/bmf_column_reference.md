# bmf -- Column Reference

**Table:** `f990_2025.bmf`
**Granularity:** One row per exempt organization (EIN is primary key)
**Total rows:** 1,935,635
**Source:** IRS Exempt Organizations Business Master File (EO BMF), 4 regional files (eo1-eo4)
**As of:** February 2026

---

## Organization Identity

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `ein` | VARCHAR(20) | 1,935,635 | 100% | Employer Identification Number (9-digit, no dashes). Primary key. |
| `name` | TEXT | 1,935,635 | 100% | Legal name of exempt organization |
| `sort_name` | TEXT | 415,722 | 21.5% | Secondary/sort name (often inverted: "Red Cross, American") |
| `ico` | TEXT | 1,242,531 | 64.2% | In Care Of name (contact person at organization address) |

## Address

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `street` | TEXT | 1,935,635 | 100% | Street address or PO Box |
| `city` | TEXT | 1,935,635 | 100% | City |
| `state` | VARCHAR(2) | 1,934,272 | 99.9% | State code (2-letter). Includes DC, PR, territories. |
| `zip` | VARCHAR(10) | 1,935,635 | 100% | ZIP code (5-digit or ZIP+4) |

## Tax Exemption Classification

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `subsection` | VARCHAR(5) | 1,935,635 | 100% | IRC subsection code. 03 = 501(c)(3), 04 = 501(c)(4), 05 = 501(c)(5), etc. |
| `foundation` | VARCHAR(5) | 1,935,635 | 100% | Foundation status code for 501(c)(3) orgs. See code table below. |
| `deductibility` | VARCHAR(5) | 1,935,635 | 100% | Contribution deductibility: 1 = deductible, 2 = by treaty, 0 = not deductible, 4 = date-dependent |
| `status` | VARCHAR(5) | 1,935,635 | 100% | Exempt status: 01 = unconditional, 02 = conditional, 12 = revoked, 25 = terminated |
| `ruling` | VARCHAR(6) | 1,935,635 | 100% | IRS ruling/determination date (YYYYMM). 1,923,999 have a meaningful date (not 000000). |

### Foundation Code Values

| Code | Count | Meaning |
|------|------:|---------|
| 00 | 325,331 | Non-501(c)(3) organization (field not applicable) |
| 02 | 310 | Private operating foundation exempt from excise taxes |
| 03 | 9,086 | Private operating foundation (other) |
| 04 | 124,802 | Private non-operating foundation |
| 10 | 290,055 | Church (170(b)(1)(A)(i)) |
| 11 | 24,124 | School (170(b)(1)(A)(ii)) |
| 12 | 5,808 | Hospital or cooperative hospital service org (170(b)(1)(A)(iii)) |
| 13 | 1,297 | Organization operated for benefit of a college/university |
| 14 | 541 | Governmental unit (170(b)(1)(A)(v)) |
| 15 | 658,420 | Organization receiving > 1/3 support from public (509(a)(1)) |
| 16 | 470,916 | Organization receiving > 1/3 from public or operated for benefit (509(a)(2)) |
| 17 | 15,380 | Organization publicly supported by IRS determination |
| 21 | 5,470 | Supporting organization Type I (509(a)(3)) |
| 22 | 2,073 | Supporting organization Type II (509(a)(3)) |
| 23 | 1,318 | Supporting organization Type III functionally integrated |
| 24 | 704 | Supporting organization Type III other |

### Subsection Code Values

| Code | Count | Meaning |
|------|------:|---------|
| 03 | 1,610,053 | 501(c)(3) - Charitable, educational, religious, scientific |
| 04 | 69,191 | 501(c)(4) - Civic leagues, social welfare |
| 05 | 43,472 | 501(c)(5) - Labor, agricultural, horticultural orgs |
| 06 | 57,647 | 501(c)(6) - Business leagues, chambers of commerce |
| 07 | 46,686 | 501(c)(7) - Social and recreational clubs |
| 08 | 34,956 | 501(c)(8) - Fraternal beneficiary societies |
| 10 | 14,365 | 501(c)(10) - Domestic fraternal societies |
| 13 | 9,688 | 501(c)(13) - Cemetery companies |
| 19 | 24,740 | 501(c)(19) - Veterans organizations |
| 92 | 5,830 | 527 - Political organizations |

## Organization Structure

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `organization` | VARCHAR(5) | 1,935,635 | 100% | Organization type: 1 = corporation, 2 = trust, 3 = cooperative, 4 = partnership, 5 = association, 6 = other |
| `affiliation` | VARCHAR(5) | 1,935,635 | 100% | Affiliation code: 3 = independent, 9 = subordinate, 1 = central/parent, 6 = central (no group return) |
| `group_code` | VARCHAR(10) | 1,935,635 | 100% | Group exemption number. 0000 = no group (1,533,026 orgs). Non-zero = part of a group exemption. |
| `classification` | VARCHAR(10) | 1,935,635 | 100% | Classification codes (legacy). 1,934,746 have meaningful values. |
| `activity` | VARCHAR(10) | 1,935,635 | 100% | Activity codes (up to 3 three-digit codes). Legacy field, superseded by NTEE. 714,717 have meaningful values. |
| `ntee_cd` | VARCHAR(10) | 1,352,945 | 69.9% | NTEE code (e.g., "A20" = Museums, "B20" = Higher Ed, "T20" = Private Grantmaking). Critical for sector matching. |

## Financials

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `asset_amt` | NUMERIC(15,2) | 1,482,390 | 76.6% | Total assets from most recent Form 990 filing |
| `income_amt` | NUMERIC(15,2) | 1,482,390 | 76.6% | Gross income from most recent Form 990 filing |
| `revenue_amt` | NUMERIC(15,2) | 1,356,504 | 70.1% | Total revenue (Form 990 Line 12 or 990-EZ Line 9). Most reliable revenue figure. |
| `asset_cd` | VARCHAR(5) | 1,935,635 | 100% | Asset size code: 0 = $0, 1 = $1-$10K, 2 = $10K-$25K, 3 = $25K-$100K, 4 = $100K-$500K, 5 = $500K-$1M, 6 = $1M-$5M, 7 = $5M-$10M, 8 = $10M-$50M, 9 = $50M+ |
| `income_cd` | VARCHAR(5) | 1,935,635 | 100% | Income code (same ranges as asset_cd) |

## Filing Information

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `tax_period` | VARCHAR(6) | 1,502,230 | 77.6% | Most recent tax period end (YYYYMM). Recent = actively filing. |
| `filing_req_cd` | VARCHAR(5) | 1,935,635 | 100% | Filing requirement: 01 = 990, 02 = 990/990-EZ, 03 = 990-PF, 06 = not required, 00 = 990-N eligible |
| `pf_filing_req_cd` | VARCHAR(5) | 1,935,635 | 100% | PF filing: 0 = not required, 1 = 990-PF required, 2 = group return, 3 = 4947(a)(1) trust |
| `acct_pd` | VARCHAR(5) | 1,935,635 | 100% | Accounting period end month (01-12). 12 = calendar year filer. |

## Metadata

| Column | Type | Populated | % | Meaning |
|--------|------|---:|---:|---------|
| `source_file` | VARCHAR(10) | 1,935,635 | 100% | Which IRS EO BMF file this came from (eo1, eo2, eo3, eo4) |
| `created_at` | TIMESTAMP | 1,935,635 | 100% | When this row was inserted into our DB |

---

## Key Queries

### All 501(c)(3) public charities (active)
```sql
SELECT ein, name, state, ntee_cd, asset_amt
FROM f990_2025.bmf
WHERE subsection = '03'
  AND foundation NOT IN ('02','03','04')  -- exclude private foundations
  AND status = '01'
ORDER BY asset_amt DESC NULLS LAST;
```

### Private foundations only
```sql
SELECT ein, name, state, asset_amt
FROM f990_2025.bmf
WHERE foundation IN ('02','03','04')
  AND status = '01';
-- 134,198 rows (02 + 03 + 04)
```

### Cross-reference with pf_returns
```sql
SELECT b.ein, b.name, b.ntee_cd, b.state, b.asset_amt as bmf_assets
FROM f990_2025.bmf b
JOIN f990_2025.dim_foundations d ON b.ein = d.ein
WHERE b.status = '01';
```

---

## Summary Stats

| Metric | Value |
|--------|-------|
| Total organizations | 1,935,635 |
| 501(c)(3) orgs | 1,610,053 (83.2%) |
| Private foundations (02+03+04) | 134,198 (6.9%) |
| Active (status 01) | 1,927,507 (99.6%) |
| With NTEE code | 1,352,945 (69.9%) |
| With financial data | 1,482,390 (76.6%) |
| Unique states/territories | 62 |
