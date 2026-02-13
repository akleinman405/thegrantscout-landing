# foundation_prospects2 -- Column Reference

**Schema:** `f990_2025`
**Table:** `foundation_prospects2`
**Source Tables:** `f990_2025.pf_returns` (IRS Form 990-PF e-file data) + `f990_2025.bmf` (IRS Business Master File)
**Grain:** One row per unique EIN (private foundation)
**Row Count:** 143,184
**Created:** 2026-02-11

## How "Most Recent" Is Determined

For each EIN, rows in `pf_returns` are ranked by `tax_year DESC, id DESC`. The top-ranked row is used for most fields.

For fields marked **"most recent non-null"**, rows where the field is NULL or empty are filtered out before selecting the top-ranked row. This recovers values that may have been present in earlier filings but missing from the latest.

---

## Column Reference

### Identity & Address (from pf_returns)

| Column | Type | Populated | % | Source | Selection Logic |
|--------|------|----------|---|--------|-----------------|
| `id` | INTEGER | 143,184 | 100% | Generated | Serial PK (starts at 77348 due to shared sequence) |
| `ein` | VARCHAR(20) | 143,184 | 100% | `pf_returns.ein` | Partition key, one row per unique EIN |
| `foundation_name` | TEXT | 143,184 | 100% | `pf_returns.business_name` | From most recent return |
| `address_line1` | TEXT | 143,184 | 100% | `pf_returns.address_line1` | From most recent return |
| `address_line2` | TEXT | 0 | 0% | `pf_returns.address_line2` | Dead column in source (never populated) |
| `city` | TEXT | 143,184 | 100% | `pf_returns.city` | From most recent return |
| `state` | VARCHAR(50) | 143,184 | 100% | `pf_returns.state` | From most recent return |
| `zip` | VARCHAR(20) | 143,184 | 100% | `pf_returns.zip` | From most recent return |

### Filing & Application Info (from pf_returns)

| Column | Type | Populated | % | Source | Selection Logic |
|--------|------|----------|---|--------|-----------------|
| `last_filing_year` | INTEGER | 143,184 | 100% | `MAX(tax_year)` | Latest tax year with a filing |
| `app_submission_deadlines` | TEXT | 33,066 | 23.1% | `pf_returns.app_submission_deadlines` | **Most recent non-null** |
| `app_restrictions` | TEXT | 33,171 | 23.2% | `pf_returns.app_restrictions` | **Most recent non-null** |
| `app_form_requirements` | TEXT | 33,301 | 23.3% | `pf_returns.app_form_requirements` | **Most recent non-null** |
| `app_contact_name` | TEXT | 35,162 | 24.6% | `pf_returns.app_contact_name` | **Most recent non-null** |
| `app_contact_phone` | VARCHAR(50) | 33,619 | 23.5% | `pf_returns.app_contact_phone` | **Most recent non-null** |
| `phone_num` | VARCHAR(50) | 138,009 | 96.4% | `pf_returns.phone_num` | **Most recent non-null** |

### Mission, Financials & Classification (from pf_returns)

| Column | Type | Populated | % | Source | Selection Logic |
|--------|------|----------|---|--------|-----------------|
| `activity_or_mission_desc` | TEXT | 115,205 | 80.5% | `pf_returns.activity_or_mission_desc` | **Most recent non-null** |
| `total_grant_paid_amt` | NUMERIC | 118,467 | 82.7% | `pf_returns.total_grant_paid_amt` | From most recent return |
| `total_assets_eoy_amt` | NUMERIC | 143,184 | 100% | `pf_returns.total_assets_eoy_amt` | From most recent return |
| `grants_to_organizations_ind` | BOOLEAN | 143,184 | 100% | `pf_returns.grants_to_organizations_ind` | From most recent return |
| `only_contri_to_preselected_ind` | BOOLEAN | 143,184 | 100% | `pf_returns.only_contri_to_preselected_ind` | From most recent return. FALSE = accepts applications. |
| `private_operating_foundation_ind` | BOOLEAN | 143,184 | 100% | `pf_returns.private_operating_foundation_ind` | From most recent return |
| `grants_to_individuals_ind` | BOOLEAN | 143,184 | 100% | `pf_returns.grants_to_individuals_ind` | From most recent return |
| `website_url` | TEXT | 21,234 | 14.8% | `pf_returns.website_url` | **Most recent non-null** |

### BMF Enrichment Columns (from bmf, added 2026-02-11)

Populated from `f990_2025.bmf` by joining on EIN. 123,117 of 143,184 EINs (86.0%) were found in the BMF. The remaining 20,067 have NULL in all BMF columns.

| Column | Type | Populated | % | Source | Meaning |
|--------|------|----------|---|--------|---------|
| `bmf_status` | VARCHAR(5) | 123,117 | 86.0% | `bmf.status` | Exempt org status. 01 = active, 12 = revoked, 25 = terminated. NULL = not in BMF. |
| `bmf_ico` | TEXT | 91,051 | 63.6% | `bmf.ico` | In Care Of name (contact person at org). |
| `bmf_subsection` | VARCHAR(5) | 123,117 | 86.0% | `bmf.subsection` | IRC subsection code. See code tables below. |
| `bmf_foundation` | VARCHAR(5) | 123,117 | 86.0% | `bmf.foundation` | Foundation status code. See code tables below. |
| `bmf_deductibility` | VARCHAR(5) | 123,117 | 86.0% | `bmf.deductibility` | Contribution deductibility code. See code tables below. |
| `bmf_ruling` | VARCHAR(6) | 123,117 | 86.0% | `bmf.ruling` | IRS ruling/determination date (YYYYMM). |
| `bmf_ntee_cd` | VARCHAR(10) | 91,582 | 64.0% | `bmf.ntee_cd` | NTEE code. See code tables below. |
| `bmf_org_type` | VARCHAR(5) | 123,117 | 86.0% | `bmf.organization` | Legal form. See code tables below. |
| `bmf_affiliation` | VARCHAR(5) | 123,117 | 86.0% | `bmf.affiliation` | Organizational relationship. See code tables below. |
| `bmf_group_code` | VARCHAR(10) | 123,117 | 86.0% | `bmf.group_code` | Group exemption number. 0000 = not part of a group. |
| `bmf_classification` | VARCHAR(10) | 123,117 | 86.0% | `bmf.classification` | Legacy IRS classification codes. |
| `bmf_activity` | VARCHAR(10) | 123,117 | 86.0% | `bmf.activity` | Legacy activity codes (up to 3 three-digit codes). Superseded by NTEE. |

---

## Field Completeness Summary

| Field | Populated | % |
|-------|----------|---|
| ein | 143,184 | 100% |
| foundation_name | 143,184 | 100% |
| total_assets_eoy_amt | 143,184 | 100% |
| phone_num | 138,009 | 96.4% |
| bmf_status | 123,117 | 86.0% |
| total_grant_paid_amt | 118,467 | 82.7% |
| activity_or_mission_desc | 115,205 | 80.5% |
| bmf_ntee_cd | 91,582 | 64.0% |
| bmf_ico | 91,051 | 63.6% |
| app_contact_name | 35,162 | 24.6% |
| app_form_requirements | 33,301 | 23.3% |
| website_url | 21,234 | 14.8% |

---

## BMF Code Tables

### Subsection Codes (bmf_subsection)

| Code | Meaning |
|------|---------|
| 03 | 501(c)(3) - Charitable, educational, religious, scientific. Eligible for tax-deductible donations. |
| 04 | 501(c)(4) - Civic leagues, social welfare orgs. Example: Sierra Club, NRA. |
| 05 | 501(c)(5) - Labor, agricultural, horticultural orgs. Example: AFL-CIO locals, farm bureaus. |
| 06 | 501(c)(6) - Business leagues, chambers of commerce. Example: local Chamber of Commerce. |
| 07 | 501(c)(7) - Social and recreational clubs. Example: country clubs, yacht clubs. |
| 08 | 501(c)(8) - Fraternal beneficiary societies. Example: Knights of Columbus, Elks lodges. |
| 09 | 501(c)(9) - Voluntary employees beneficiary associations (VEBAs). |
| 10 | 501(c)(10) - Domestic fraternal societies. |
| 12 | 501(c)(12) - Benevolent life insurance, mutual telephone/electric companies. |
| 13 | 501(c)(13) - Cemetery companies. |
| 14 | 501(c)(14) - Credit unions, mutual reserve funds. |
| 19 | 501(c)(19) - Veterans organizations. Example: VFW, American Legion. |
| 25 | 501(c)(25) - Title holding corps for multiple exempt orgs. |
| 92 | 527 - Political organizations. Campaign committees, PACs. |

### Foundation Codes (bmf_foundation)

| Code | Meaning |
|------|---------|
| 00 | Not a 501(c)(3) organization (field not applicable). |
| 02 | Private operating foundation exempt from excise taxes on net investment income. |
| 03 | Private operating foundation (all other). |
| 04 | Private non-operating foundation (the classic grantmaking PF). |
| 10 | Church (170(b)(1)(A)(i)). |
| 11 | School (170(b)(1)(A)(ii)). |
| 12 | Hospital or cooperative hospital service org (170(b)(1)(A)(iii)). |
| 13 | Org operated for benefit of a college or university (170(b)(1)(A)(iv)). |
| 14 | Governmental unit (170(b)(1)(A)(v)). |
| 15 | Publicly supported org receiving >1/3 from contributions (509(a)(1)). Example: United Way, Salvation Army. |
| 16 | Publicly supported org receiving >1/3 from gross receipts (509(a)(2)). Example: YMCA, museum gift shops. |
| 17 | Organization determined publicly supported by IRS (alternative test). |
| 21 | Supporting organization Type I (509(a)(3)). Operated/supervised by supported org. |
| 22 | Supporting organization Type II (509(a)(3)). Supervised or controlled in connection with. |
| 23 | Supporting organization Type III functionally integrated (509(a)(3)). |
| 24 | Supporting organization Type III other (509(a)(3)). |

### Status Codes (bmf_status)

| Code | Meaning |
|------|---------|
| 01 | Unconditional Exemption. Active and in good standing. |
| 02 | Conditional Exemption. Exempt with conditions or limitations. |
| 12 | Revoked. Usually for failure to file 3 consecutive years (auto-revocation). |
| 25 | Terminated. Voluntarily gave up exempt status or IRS terminated it. |
| NULL | Not found in current BMF. Likely dissolved, merged, or foreign org. |

### Deductibility Codes (bmf_deductibility)

| Code | Meaning |
|------|---------|
| 1 | Contributions are deductible. Standard charitable deduction. |
| 2 | Contributions deductible by treaty or election. Limited deductibility. |
| 0 | Contributions are NOT deductible. Example: social clubs, business leagues. |
| 4 | Deductibility depends on date of gift. |

### Organization Type Codes (bmf_org_type)

| Code | Meaning |
|------|---------|
| 1 | Corporation. Most common form for nonprofits. |
| 2 | Trust. Common for private foundations. |
| 3 | Co-operative. Member-owned organizations. |
| 4 | Partnership. Rare for exempt orgs. |
| 5 | Association. Unincorporated membership orgs. Example: many churches, VFW posts. |
| 6 | Other. |
| 0 | Not specified or unknown. |

### Affiliation Codes (bmf_affiliation)

| Code | Meaning |
|------|---------|
| 3 | Independent. Not part of a group exemption. The majority of orgs. |
| 9 | Subordinate. Part of a group exemption. Example: local Girl Scout council. |
| 1 | Central organization (group ruling). The parent holding the group exemption. |
| 6 | Central org NOT included in its own group return. |
| 0 | Not specified. |
| 2 | Intermediate org (group return). Files a group return including subordinates. |
| 8 | Central org whose group exemption has been revoked. |
| 7 | Intermediate org (not filing group return). |

### NTEE Major Categories (first letter of bmf_ntee_cd)

| Letter | Category | Examples |
|--------|----------|----------|
| A | Arts, Culture, Humanities | A20 = Museums, A60 = Performing Arts |
| B | Education | B20 = Elementary/Secondary, B40 = Higher Ed |
| C | Environment | C20 = Pollution Abatement, C30 = Natural Resources |
| D | Animal-Related | D20 = Animal Protection, D30 = Wildlife |
| E | Health Care | E20 = Hospitals, E40 = Reproductive Health |
| F | Mental Health & Crisis | F20 = Substance Abuse, F30 = Mental Health |
| G | Diseases & Disorders | G20 = Birth Defects, G40 = Cancer |
| H | Medical Research | H20 = Birth Defects Research |
| I | Crime & Legal | I20 = Crime Prevention, I40 = Rehabilitation |
| J | Employment | J20 = Job Training, J30 = Vocational Rehab |
| K | Food, Agriculture, Nutrition | K20 = Food Banks, K30 = Agriculture |
| L | Housing & Shelter | L20 = Housing Development, L40 = Homeless Services |
| M | Public Safety & Disaster | M20 = Disaster Preparedness, M40 = Search/Rescue |
| N | Recreation & Sports | N20 = Camps, N60 = Amateur Sports |
| O | Youth Development | O20 = Youth Centers, O40 = Scouting |
| P | Human Services (Multipurpose) | P20 = Multipurpose Service, P80 = Emergency Assistance |
| Q | International Affairs | Q20 = International Understanding |
| R | Civil Rights & Social Action | R20 = Intergroup Relations, R60 = Civil Liberties |
| S | Community Improvement | S20 = Community Coalitions, S40 = Business & Industry |
| T | Philanthropy & Grantmaking | T20 = Private Foundations, T30 = Public Foundations |
| U | Science & Technology | U20 = General Science, U40 = Engineering |
| V | Social Science | V20 = Social Science Research |
| W | Public/Society Benefit | W20 = Government & Public Admin |
| X | Religion-Related | X20 = Christian, X30 = Jewish |
| Y | Mutual & Membership Benefit | Y20 = Insurance, Y40 = Pensions |
| Z | Unknown / Unclassified | |

### Asset/Income Size Codes (for reference when querying BMF directly)

| Code | Range |
|------|-------|
| 0 | $0 or not reported |
| 1 | $1 to $10,000 |
| 2 | $10,000 to $25,000 |
| 3 | $25,000 to $100,000 |
| 4 | $100,000 to $500,000 |
| 5 | $500,000 to $1,000,000 |
| 6 | $1,000,000 to $5,000,000 |
| 7 | $5,000,000 to $10,000,000 |
| 8 | $10,000,000 to $50,000,000 |
| 9 | $50,000,000+ |

### Filing Requirement Codes (for reference when querying BMF directly)

| Code | Meaning |
|------|---------|
| 01 | Form 990 required. Gross receipts >= $200K or assets >= $500K. |
| 02 | Form 990 or 990-EZ. Gross receipts < $200K and assets < $500K. |
| 03 | Form 990-PF required (private foundations). |
| 06 | Not required to file. Churches, government agencies. |
| 00 | Form 990-N (e-Postcard) eligible. Gross receipts <= $50K. |
| 07 | Section 4947(a)(1) nonexempt charitable trust treated as PF. |
| 13 | Section 4947(a)(1) nonexempt charitable trust not treated as PF. |
| 14 | Not required to file (other exemptions). |

---

*Generated by Claude Code on 2026-02-11*
