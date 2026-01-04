# Prospect Call List Report
**Date:** 2025-12-12
**Output:** DATA_2025-12-12_prospect_call_list.csv

---

## Executive Summary

Generated a targeted call list of **27 prospects** matching ideal customer profile criteria for cold outreach. Prospects are small nonprofits (0-3 employees) in sectors E (Healthcare/Education) and P (Human Services) with $1-2M revenue, high grant dependency, and limited foundation relationships.

---

## Filter Summary

### Applied Filters

| Criterion | Filter Applied |
|-----------|----------------|
| No biz dev staff | `has_biz_dev_staff = 'no'` |
| 0-3 employees | `employee_count BETWEEN 0 AND 3` |
| Sector E or P | `sector IN ('E', 'P')` |
| Revenue $1M-$2M | `total_revenue BETWEEN 1000000 AND 2000000` |
| 0-3 foundation funders | `num_unique_funders <= 3 OR num_foundation_grants <= 3` |
| High grant dependency | `grant_dependency_pct >= 75` |
| Has website | `website IS NOT NULL AND website != ''` |
| Concrete mission | `has_concrete_mission = 1` |

### Filters Relaxed

Two filters were removed due to insufficient results:

1. **`likely_active_fundraiser = 1`** — Only 216 prospects in entire database match this flag; combined with other filters, resulted in 2 matches.
2. **`yoy_revenue_growth <= 10`** — Further reduced count from 27 to 16, below the 20-prospect threshold.

**Rationale:** The `likely_active_fundraiser` flag is extremely restrictive (0.3% of prospects). Removing it while keeping other filters still yields high-quality prospects who need foundation funding support.

---

## Missing Data Summary

| Field | Missing | Populated | Notes |
|-------|---------|-----------|-------|
| Phone | 27/27 (100%) | 0/27 | Phone numbers not in source data |
| Contact Name | 2/27 (7%) | 25/27 | Enriched from officers table |
| Mission Statement | 0/27 (0%) | 27/27 | All have concrete missions |

**Note:** Phone numbers will need to be sourced externally (website lookup, LinkedIn, etc.).

---

## Distribution

### By State

| State | Count |
|-------|-------|
| WA | 4 |
| FL | 3 |
| CA | 2 |
| DC | 2 |
| GA | 2 |
| TX | 2 |
| AK, AL, AR, IL, IN, KY, MA, NC, NY, PA, SD, WV | 1 each |

**Geographic spread:** 18 states represented, with concentration in WA (15%) and FL (11%).

### By Sector

| Sector | Count | % |
|--------|-------|---|
| P - Human Services | 21 | 78% |
| E - Healthcare/Education | 6 | 22% |

### ICP Score Distribution

| Metric | Value |
|--------|-------|
| Mean | 9.9 |
| Min | 8 |
| Max | 11 |
| Std Dev | 0.6 |

All prospects have high ICP scores (8-11), indicating strong fit with target profile.

### Revenue Distribution

| Metric | Amount |
|--------|--------|
| Minimum | $1,006,377 |
| Maximum | $1,798,993 |
| Mean | $1,353,413 |

---

## Top 10 Preview

| Organization | State | Sector | Revenue | Contact | ICP |
|-------------|-------|--------|---------|---------|-----|
| Tulare County Hope for the Homeless Inc | CA | P | $1,052,271 | Bob Link | 11 |
| Hmong Youth and Parents United | CA | P | $1,023,111 | Mai Yang Thor | 11 |
| Children of Restaurant Employees | GA | P | $1,153,213 | Larry McGinn | 10 |
| Animal Wellness Action | DC | P | $1,574,991 | William Marty Irby Jr | 10 |
| Serenity Hospice and Home Found | IL | E | $1,254,970 | Lynette Knodle | 10 |
| Howard Hanna Children's Free Care Fund | PA | E | $1,127,808 | (Missing) | 10 |
| Hibiscus Children's Center | FL | P | $1,070,130 | Matt Markley | 10 |
| Somerset Senior Living at Harrison | AR | E | $1,187,982 | Cathy Abatangle | 10 |
| Providence Hospice & Home Care | WA | E | $1,704,383 | Dr Jim Congdon | 10 |
| Veterans Relief Network Inc | IN | P | $1,301,100 | Helen Ignas | 10 |

---

## Recommendations

1. **Phone Number Sourcing:** All 27 prospects are missing phone numbers. Recommend using website contact pages or LinkedIn to source before calling.

2. **Priority Order:** List is sorted by ICP score (descending). The top 2 prospects (Tulare County Hope for the Homeless, Hmong Youth and Parents United) have ICP score of 11 — start there.

3. **Mission-Based Personalization:** All prospects have concrete missions. Use mission statement in CSV for call personalization.

4. **Washington & Florida Focus:** 7 of 27 prospects (26%) are in WA/FL. Consider a regional calling campaign if time zone coordination helps.

5. **Consider Expanding Criteria:** To increase list size, consider:
   - Expanding employee count to 0-10 (adds ~200 prospects)
   - Expanding revenue to $500K-$3.5M (adds more)
   - Note: These relaxations should be tested incrementally

---

*Generated: 2025-12-12*
