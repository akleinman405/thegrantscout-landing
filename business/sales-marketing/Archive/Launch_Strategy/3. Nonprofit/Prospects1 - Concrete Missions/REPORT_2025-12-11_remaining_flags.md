# Report: Additional Prospect Flags

**Date:** 2025-12-11
**Task:** Add 5 new flags to prospects table for outreach targeting

---

## Executive Summary

Successfully added 5 new flags to the prospects table (74,144 nonprofits), enabling flexible filtering for outreach campaigns. All flags are now available for mix-and-match targeting.

**Key Findings:**
- 216 prospects (0.3%) are "likely active fundraisers" (score >= 6)
- 42,447 prospects (57.2%) have fiscal year ending soon (Dec/Jan)
- 3,270 prospects (4.4%) have identified business development staff
- 31,205 prospects (42.1%) are new to foundation funding
- 20,362 prospects (27.5%) share funders with beta clients

---

## 1. Flags Added

| Column | Type | Description | Source Logic |
|--------|------|-------------|--------------|
| `likely_active_fundraiser` | SMALLINT (0/1) | High probability of active fundraising | `fundraising_likelihood_score >= 6` |
| `fiscal_year_end_soon` | SMALLINT (0/1) | FY ends Dec or Jan (prime giving season) | `tax_period_end` month IN (12, 1) |
| `has_biz_dev_staff` | VARCHAR(10) | Development/fundraising staff on 990 | Officer title keyword matching |
| `new_to_foundations` | SMALLINT (0/1) | Zero foundation grants in database | `num_foundation_grants = 0 OR NULL` |
| `shares_funder_with_beta` | SMALLINT (0/1) | Has common funder with beta clients | `beta_client_connection IS NOT NULL` |

---

## 2. Summary Statistics

### Overall Distribution (All 74,144 Prospects)

| Flag | Value | Count | Percentage |
|------|-------|-------|------------|
| `likely_active_fundraiser` | 1 | 216 | 0.3% |
| `fiscal_year_end_soon` | 1 | 42,447 | 57.2% |
| `has_biz_dev_staff` | yes | 3,270 | 4.4% |
| `has_biz_dev_staff` | no | 66,306 | 89.4% |
| `has_biz_dev_staff` | uncertain | 4,568 | 6.2% |
| `new_to_foundations` | 1 | 31,205 | 42.1% |
| `shares_funder_with_beta` | 1 | 20,362 | 27.5% |

### By Concrete Mission Flag

| Mission | Total | ActiveFund | FY Soon | BizDev=Yes | New2Found | SharedBeta |
|---------|-------|------------|---------|------------|-----------|------------|
| Yes | 7,277 | 216 | 3,885 | 268 | 2,860 | 2,147 |
| No | 66,867 | 0 | 38,562 | 3,002 | 28,345 | 18,215 |

**Note:** `likely_active_fundraiser` only applies to prospects with `has_concrete_mission = 1` AND `received_capacity_grant = 1` AND `icp_score >= 8`.

### By ICP Score Bucket

| ICP Bucket | Total | ActiveFund | FY Soon | New2Found |
|------------|-------|------------|---------|-----------|
| 8+ (Prime) | 29,621 | 216 | 16,098 | 16,690 |
| 6-7 (Good) | 28,375 | 0 | 16,938 | 12,207 |
| 4-5 (Med) | 12,758 | 0 | 7,464 | 2,308 |
| 0-3 (Low) | 3,390 | 0 | 1,947 | 0 |

---

## 3. Cross-Tab Analysis

### Prime Prospects (Concrete + Capacity Grant + ICP 8+)

| Segment | Count |
|---------|-------|
| Base: Prime Prospects | 642 |
| + likely_active_fundraiser | 216 (33.6%) |
| + fiscal_year_end_soon | 318 (49.5%) |
| + NO biz dev staff | 589 (91.7%) |
| + new_to_foundations | 75 (11.7%) |
| + shares_funder_with_beta | 224 (34.9%) |

### Key Targeting Combinations

| Combination | Count |
|-------------|-------|
| FY soon + NO biz dev + small staff (1-3 employees) | 284 |
| Prime + FY soon + NO biz dev + small staff | 20 |
| New to foundations + concrete mission | 2,860 |
| Likely fundraiser + FY soon | 176 |
| Shares beta funder + concrete mission | 2,147 |

---

## 4. Ideal Target Segments

### Segment A: "Hot Prospects" (Highest Priority)
**Criteria:** Prime + ActiveFund + FY Soon + SharedBeta
**Description:** Prime prospects who are likely active fundraisers, have fiscal year ending soon, and share funders with beta clients
**Estimated Count:** ~100-150

### Segment B: "Low-Hanging Fruit" (No Competition)
**Criteria:** Prime + FY Soon + NO biz dev staff + small team
**Description:** Prospects without dedicated development staff who need help during year-end push
**Count:** 20

### Segment C: "New to Foundations" (Education Play)
**Criteria:** Concrete mission + new_to_foundations + ICP 6+
**Description:** Organizations that haven't yet tapped foundation funding
**Count:** ~2,800+

### Segment D: "Warm Referral" (Beta Network)
**Criteria:** Concrete mission + shares_funder_with_beta
**Description:** Prospects connected to beta client funders
**Count:** 2,147

---

## 5. Sample Queries

### Get "Hot Prospects"
```sql
SELECT ein, org_name, state, employee_count, icp_score, website
FROM f990_2025.prospects
WHERE has_concrete_mission = 1
  AND received_capacity_grant = 1
  AND icp_score >= 8
  AND likely_active_fundraiser = 1
  AND fiscal_year_end_soon = 1
  AND shares_funder_with_beta = 1
ORDER BY icp_score DESC, employee_count ASC;
```

### Get "No Development Staff" targets
```sql
SELECT ein, org_name, state, employee_count, icp_score, website
FROM f990_2025.prospects
WHERE has_concrete_mission = 1
  AND fiscal_year_end_soon = 1
  AND has_biz_dev_staff = 'no'
  AND employee_count BETWEEN 1 AND 10
ORDER BY icp_score DESC;
```

### Get "New to Foundations" targets
```sql
SELECT ein, org_name, state, employee_count, icp_score, website
FROM f990_2025.prospects
WHERE has_concrete_mission = 1
  AND new_to_foundations = 1
  AND icp_score >= 6
ORDER BY icp_score DESC, total_revenue DESC;
```

### Get "Beta Network" targets
```sql
SELECT ein, org_name, state, employee_count, icp_score,
       beta_client_connection, website
FROM f990_2025.prospects
WHERE has_concrete_mission = 1
  AND shares_funder_with_beta = 1
  AND icp_score >= 7
ORDER BY icp_score DESC;
```

---

## 6. Top 20 Prime Prospects (Multi-Flag)

| # | Organization | State | Emp | ICP | Flags |
|---|--------------|-------|-----|-----|-------|
| 1 | Childrens Oncology Support Fund | CA | 0 | 11 | ActiveFund, FY-Soon, SharedBeta |
| 2 | Men & Women United for Youth | NC | 46 | 11 | ActiveFund, FY-Soon, SharedBeta |
| 3 | South End Children's Cafe | NY | 13 | 11 | ActiveFund, FY-Soon, BizDev, SharedBeta |
| 4 | Firefighter Cancer Support Network | CA | 0 | 11 | ActiveFund, FY-Soon, BizDev, SharedBeta |
| 5 | Care for Special Needs Children | NY | 16 | 11 | ActiveFund, FY-Soon, SharedBeta |
| 6 | Youth & Family Counseling Agency | NY | 21 | 11 | ActiveFund, FY-Soon, SharedBeta |
| 7 | Global Children Foundation | CA | 1 | 11 | ActiveFund, FY-Soon, SharedBeta |
| 8 | Bethel Shelters | SC | 45 | 11 | ActiveFund, FY-Soon, SharedBeta |
| 9 | Committee for the Rescue | NY | 0 | 10 | ActiveFund, FY-Soon, SharedBeta |
| 10 | Madera Rescue Mission | CA | 13 | 10 | ActiveFund, FY-Soon, SharedBeta |
| 11 | Estrella Warbirds Museum | CA | 6 | 10 | ActiveFund, FY-Soon, SharedBeta |
| 12 | Homeless Action Sonoma | CA | 22 | 10 | ActiveFund, FY-Soon, SharedBeta |
| 13 | Youth Mentoring Action Network | CA | 8 | 9 | ActiveFund, FY-Soon, SharedBeta |
| 14 | Student Reach | CA | 1 | 9 | ActiveFund, FY-Soon, New2Found, SharedBeta |
| 15 | SF Fire Fighters Cancer | CA | 0 | 9 | ActiveFund, FY-Soon, SharedBeta |
| 16 | Children of the Immaculate Heart | CA | 31 | 9 | ActiveFund, FY-Soon, SharedBeta |
| 17 | Intl Senior Lawyers Project | NY | 7 | 9 | ActiveFund, FY-Soon, BizDev, SharedBeta |
| 18 | Jacob's Heart Children's Cancer | CA | 24 | 9 | ActiveFund, FY-Soon, BizDev, SharedBeta |
| 19 | For the Children | CA | 17 | 9 | ActiveFund, FY-Soon, SharedBeta |
| 20 | North American Islamic Shelter | CA | 0 | 9 | ActiveFund, FY-Soon, SharedBeta |

---

## 7. Schema Changes Applied

```sql
-- Flag 1
ALTER TABLE f990_2025.prospects
ADD COLUMN IF NOT EXISTS likely_active_fundraiser SMALLINT DEFAULT 0;

-- Flag 2
ALTER TABLE f990_2025.prospects
ADD COLUMN IF NOT EXISTS fiscal_year_end_soon SMALLINT DEFAULT 0;

-- Flag 3
ALTER TABLE f990_2025.prospects
ADD COLUMN IF NOT EXISTS has_biz_dev_staff VARCHAR(10) DEFAULT 'uncertain';

-- Flag 4
ALTER TABLE f990_2025.prospects
ADD COLUMN IF NOT EXISTS new_to_foundations SMALLINT DEFAULT 0;

-- Flag 5
ALTER TABLE f990_2025.prospects
ADD COLUMN IF NOT EXISTS shares_funder_with_beta SMALLINT DEFAULT 0;
```

---

*Report generated: 2025-12-11*
*Database: f990_2025 schema*
