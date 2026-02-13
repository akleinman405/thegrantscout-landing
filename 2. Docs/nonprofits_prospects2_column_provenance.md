# nonprofits_prospects2 — Column Provenance

**Schema:** `f990_2025`
**Table:** `nonprofits_prospects2`
**Source Table:** `f990_2025.nonprofit_returns` (IRS Form 990 and 990-EZ e-file data)
**Grain:** One row per unique EIN (nonprofit organization)
**Row Count:** 673,381
**Created:** 2026-02-11

## How "Most Recent" Is Determined

For each EIN, rows in `nonprofit_returns` are ranked by `tax_year DESC, tax_period_end DESC, id DESC`. The top-ranked row is used as the primary source for most fields.

For fields marked **"most recent non-null"**, a separate ranking is applied that filters out rows where the field is NULL or empty before selecting the top-ranked row. This ensures that if the most recent return is missing a value (e.g., no website), we fall back to an earlier year where it was populated.

## Column Reference

| Column | Type | Source | Selection Logic |
|--------|------|--------|-----------------|
| `id` | INTEGER | Generated | `ROW_NUMBER() OVER (ORDER BY ein)` — synthetic sequential ID |
| `ein` | VARCHAR | `nonprofit_returns.ein` | Partition key — one row per unique EIN |
| `organization_name` | TEXT | `nonprofit_returns.organization_name` | From most recent return |
| `most_recent_tax_year` | INTEGER | `nonprofit_returns.tax_year` | From most recent return |
| `most_recent_tax_period_begin` | DATE | `nonprofit_returns.tax_period_begin` | From most recent return |
| `most_recent_tax_period_end` | DATE | `nonprofit_returns.tax_period_end` | From most recent return |
| `most_recent_form_type` | VARCHAR | `nonprofit_returns.form_type` | From most recent return. Values: `990` or `990EZ` |
| `address_line1` | TEXT | `nonprofit_returns.address_line1` | **Most recent non-null** — falls back to earlier years if latest is empty |
| `address_line2` | TEXT | `nonprofit_returns.address_line2` | From the same row as `address_line1` (most recent non-null address row) |
| `city` | TEXT | `nonprofit_returns.city` | From the same row as `address_line1` (most recent non-null address row) |
| `state` | VARCHAR | `nonprofit_returns.state` | From the same row as `address_line1` (most recent non-null address row) |
| `zip` | VARCHAR | `nonprofit_returns.zip` | From the same row as `address_line1` (most recent non-null address row) |
| `phone` | VARCHAR | `nonprofit_returns.phone` | **Most recent non-null** |
| `website` | TEXT | `nonprofit_returns.website` | **Most recent non-null** |
| `mission_description` | TEXT | `nonprofit_returns.mission_description` | **Most recent non-null** — present on both 990 and 990-EZ forms |
| `program_1_desc` | TEXT | `nonprofit_returns.program_1_desc` | From most recent return. Primarily populated for Form 990 filers (Part III) |
| `program_2_desc` | TEXT | `nonprofit_returns.program_2_desc` | From most recent return |
| `program_3_desc` | TEXT | `nonprofit_returns.program_3_desc` | From most recent return |
| `program_1_expense_amt` | NUMERIC | `nonprofit_returns.program_1_expense_amt` | From most recent return |
| `program_2_expense_amt` | NUMERIC | `nonprofit_returns.program_2_expense_amt` | From most recent return |
| `program_3_expense_amt` | NUMERIC | `nonprofit_returns.program_3_expense_amt` | From most recent return |
| `ntee_code` | VARCHAR | `nonprofit_returns.ntee_code` | From most recent return. National Taxonomy of Exempt Entities code |
| `total_employees_cnt` | INTEGER | `nonprofit_returns.total_employees_cnt` | From most recent return. Primarily populated for Form 990 filers |
| `total_volunteers_cnt` | INTEGER | `nonprofit_returns.total_volunteers_cnt` | From most recent return |
| `org_description` | TEXT | `nonprofit_returns.activity_description` OR `nonprofit_returns.primary_exempt_purpose` | **Most recent non-null**, combining two form-specific fields: `activity_description` (Form 990, Part III Line 1) and `primary_exempt_purpose` (Form 990-EZ, Part III). Uses `COALESCE(activity_description, primary_exempt_purpose)` from the most recent return where either is non-null. |

## Indexes

| Index Name | Column(s) | Unique |
|------------|-----------|--------|
| `idx_np2_ein` | `ein` | Yes |
| `idx_np2_id` | `id` | Yes |

## IRS Form Context

- **Form 990** — Filed by larger nonprofits (generally revenue > $200K or assets > $500K). Provides `activity_description`, program details, and employee counts.
- **Form 990-EZ** — Filed by smaller nonprofits (revenue < $200K and assets < $500K). Provides `primary_exempt_purpose` instead of `activity_description`. Program expense fields are typically not populated.
- Both forms include mission description, address, phone, website, and NTEE code.

## BMF Enrichment Columns (added 2026-02-11)

These columns are populated from `f990_2025.bmf` (IRS Business Master File) by joining on EIN. 604,428 of 673,381 EINs (89.8%) were found in the BMF. The remaining 68,953 have NULL in all BMF columns.

| Column | Type | Populated | % | Source | Meaning |
|--------|------|----------|---|--------|---------|
| `bmf_status` | VARCHAR(5) | 604,428 | 89.8% | `bmf.status` | Exempt org status. 01 = active, 02 = conditional, 12 = revoked, 25 = terminated. NULL = not in BMF. |
| `bmf_ico` | TEXT | 369,722 | 54.9% | `bmf.ico` | In Care Of name (contact person at org). |
| `bmf_subsection` | VARCHAR(5) | 604,428 | 89.8% | `bmf.subsection` | IRC subsection code. See code tables below. |
| `bmf_foundation` | VARCHAR(5) | 604,428 | 89.8% | `bmf.foundation` | Foundation status code. See code tables below. |
| `bmf_deductibility` | VARCHAR(5) | 604,428 | 89.8% | `bmf.deductibility` | Contribution deductibility code. See code tables below. |
| `bmf_ruling` | VARCHAR(6) | 604,428 | 89.8% | `bmf.ruling` | IRS ruling/determination date (YYYYMM format). |
| `bmf_ntee_cd` | VARCHAR(10) | 450,409 | 66.9% | `bmf.ntee_cd` | NTEE code from BMF (compare with `ntee_code` from 990 filing). See code tables below. |
| `bmf_org_type` | VARCHAR(5) | 604,428 | 89.8% | `bmf.organization` | Legal form. See code tables below. |
| `bmf_affiliation` | VARCHAR(5) | 604,428 | 89.8% | `bmf.affiliation` | Organizational relationship. See code tables below. |
| `bmf_group_code` | VARCHAR(10) | 604,428 | 89.8% | `bmf.group_code` | Group exemption number. 0000 = not part of a group. |
| `bmf_classification` | VARCHAR(10) | 604,428 | 89.8% | `bmf.classification` | Legacy IRS classification codes. |
| `bmf_activity` | VARCHAR(10) | 604,428 | 89.8% | `bmf.activity` | Legacy activity codes (up to 3 three-digit codes). Superseded by NTEE. |

## Field Completeness

| Field | Populated | % |
|-------|----------|---|
| address_line1 | 672,786 | 99.9% |
| phone | 673,381 | 100% |
| website | 578,028 | 85.8% |
| mission_description | 673,381 | 100% |
| org_description | 673,381 | 100% |
| ntee_code | 452,209 | 67.2% |
| total_employees_cnt | 389,134 | 57.8% |
| bmf_status | 604,428 | 89.8% |
| bmf_ntee_cd | 450,409 | 66.9% |
| bmf_ico | 369,722 | 54.9% |

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
