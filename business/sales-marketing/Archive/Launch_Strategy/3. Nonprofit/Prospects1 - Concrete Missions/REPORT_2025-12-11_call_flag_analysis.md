# Call Flag Analysis Report

**Date:** 2025-12-11
**Analysis:** Correlation between prospect flags and cold call outcomes

---

## Executive Summary

We analyzed 49 cold calls against prospect flags from our database to identify which attributes predict successful outreach. **Key finding: Sector (Education/Human Services) is the strongest predictor of both reaching decision makers (7.2x lift) and generating interest (3.6x lift).** ICP score showed no clear correlation with outcomes.

### Top Predictive Flags

| Flag | Lift for Talking to Person | Lift for Interest |
|------|---------------------------|-------------------|
| reach_sector_e_p (E/P sectors) | 2.57x | 3.60x |
| reach_revenue_1m_2m ($1M-$2M) | 1.68x | ∞ (all interest here) |
| has_no_biz_dev (no dev staff) | 1.74x | 0.14x (negative!) |
| received_capacity_grant | 1.54x | 0.77x |

---

## 1. Match Summary

| Metric | Count |
|--------|-------|
| Total calls with outcome data | 49 |
| Matched to prospects table | 46 (94%) |
| Not found in database | 3 |

**Unmatched EINs:** 770376995, 462730379 (PSMF - beta client), 870800728

---

## 2. Overall Metrics (Baseline)

| Outcome | Count | Rate |
|---------|-------|------|
| Left voicemail | 43 | 88% |
| Talked to someone | 14 | 29% |
| Reached decision maker | 4 | 8% |
| Showed interest (Yes/Maybe) | 3 | 6% |

---

## 3. Flag Analysis

### 3.1 Impact on Talking to a Person

| Flag | Flag=1 Rate | Flag=0 Rate | Lift | n (Flag=1) |
|------|-------------|-------------|------|------------|
| **reach_sector_e_p** | 50.0% | 19.4% | **2.57x** | 10 |
| **has_no_biz_dev** | 31.6% | 18.2% | **1.74x** | 38 |
| **reach_revenue_1m_2m** | 32.0% | 19.0% | **1.68x** | 25 |
| received_capacity_grant | 30.8% | 20.0% | 1.54x | 26 |
| reach_grant_dep_75 | 28.1% | 21.4% | 1.31x | 32 |
| has_concrete_mission | 28.6% | 25.6% | 1.11x | 7 |
| reach_employees_1_10 | 16.7% | 27.5% | 0.61x | 6 |
| **new_to_foundations** | 13.3% | 32.3% | **0.41x** | 15 |
| fiscal_year_end_soon | 0.0% | 27.9% | 0.00x | 3 |

**Key insight:** Organizations **new to foundations** were actually LESS likely to answer (0.41x). Established grantees are more responsive.

### 3.2 Impact on Reaching Decision Maker

| Flag | Flag=1 Rate | Flag=0 Rate | Lift | n (Flag=1) |
|------|-------------|-------------|------|------------|
| **reach_sector_e_p** | 20.0% | 2.8% | **7.20x** | 10 |
| **reach_employees_1_10** | 16.7% | 5.0% | **3.33x** | 6 |
| reach_revenue_1m_2m | 8.0% | 4.8% | 1.68x | 25 |
| new_to_foundations | 6.7% | 6.5% | 1.03x | 15 |
| **has_no_biz_dev** | 5.3% | 18.2% | **0.29x** | 38 |

**Key insight:** Small orgs (1-10 employees) and E/P sector orgs are much more likely to get you to a decision maker. But orgs without biz dev staff are harder to convert once reached.

### 3.3 Impact on Showing Interest

| Flag | Flag=1 Rate | Flag=0 Rate | Lift | n (Flag=1) |
|------|-------------|-------------|------|------------|
| **reach_employees_1_10** | 16.7% | 2.5% | **6.67x** | 6 |
| **reach_sector_e_p** | 10.0% | 2.8% | **3.60x** | 10 |
| new_to_foundations | 6.7% | 3.2% | 2.07x | 15 |
| reach_revenue_1m_2m | 8.0% | 0.0% | ∞ | 25 |
| **has_no_biz_dev** | 2.6% | 18.2% | **0.14x** | 38 |

**Critical finding:** Organizations WITHOUT business development staff are much easier to reach but 7x LESS likely to show interest. This suggests they may not be actively seeking grant support.

---

## 4. Best Flag Combinations

| Combination | n | Talked Rate | DM Rate | Interest Rate |
|-------------|---|-------------|---------|---------------|
| **Sector E/P + Revenue $1-2M** | 5 | **60%** | 20% | 20% |
| Capacity Grant + Sector E/P | 6 | 50% | 17% | 17% |
| Sector E/P + Small Staff | 3 | 33% | 33% | 33% |
| *Baseline (all calls)* | 46 | 26% | 7% | 4% |

**Winner:** Sector E/P + Revenue $1-2M delivers 2.3x the baseline talk rate and 5x the interest rate.

---

## 5. Who Showed Interest?

### Interested Organizations (3 total)

1. **BIKUR CHOLIM** (EIN: 954521980) - **Maybe**
   - Healthcare charity, 1 employee, $1M revenue
   - Sector E/P: ✓, Small staff: ✓, Grant-dependent: 88%
   - Notes: "Lucky - Director. Needs Review, how do they connect to it etc"

2. **ANAHEIM MEMORIAL MANOR** (EIN: 953618525) - **Yes**
   - RHF affiliate (senior housing), 0 employees, $1.4M revenue
   - New to foundations: ✓
   - Notes: "Sometimes they apply for public funding"

3. **PATIENT SAFETY MOVEMENT FOUNDATION** - **Maybe**
   - Not matched to database (beta client)
   - Notes: "Consuelo answered and said that michael wasn't available but that it sound interesting"

### Pattern: 2 of 3 interested orgs are in the E/P sector, small staff, and grant-dependent.

---

## 6. ICP Score Analysis

| ICP Score | n | Talked Rate | DM Reached | Interested |
|-----------|---|-------------|------------|------------|
| 4 | 1 | 0% | 0 | 0 |
| 5 | 2 | 50% | 0 | 0 |
| 6 | 2 | 0% | 0 | 0 |
| 7 | 7 | 29% | 0 | 0 |
| 8 | 3 | 33% | 1 | 1 |
| 9 | 18 | 22% | 2 | 1 |
| 10 | 4 | 25% | 0 | 0 |
| 11 | 3 | 33% | 0 | 0 |
| 12 | 6 | 33% | 0 | 0 |

**Finding:** ICP score does NOT predict cold call success. Interest came from ICP 8-9, not higher scores. This suggests ICP score may be optimized for other factors (email response, fit quality) rather than phone reachability.

---

## 7. Recommendations

### For Future Cold Call Targeting

1. **Prioritize Sector E/P (Education & Human Services)**
   - 2.6x more likely to talk to someone
   - 7.2x more likely to reach decision maker
   - These orgs tend to have leaner structures with accessible leadership

2. **Target $1M-$2M Revenue Range**
   - Large enough to have funding needs
   - Small enough to not have dedicated development staff gatekeeping
   - Combined with E/P sector: 60% talk rate, 20% interest rate

3. **Deprioritize "No Biz Dev Staff" as a Positive Signal**
   - Easier to reach (1.74x) but much harder to convert (0.14x)
   - Suggests these orgs aren't actively seeking grant support
   - Better to target orgs WITH some development capacity

4. **Don't Over-Weight "New to Foundations"**
   - Actually LESS likely to answer (0.41x lift)
   - Established grantees are more responsive
   - May still be worth targeting for fit reasons, but expect lower connection rates

5. **Ignore ICP Score for Phone Outreach**
   - No correlation with phone success
   - Use ICP for email/digital outreach instead

### Suggested Targeting Formula for Calls

**High priority (call first):**
- reach_sector_e_p = 1 AND reach_revenue_1m_2m = 1

**Medium priority:**
- reach_sector_e_p = 1 OR (received_capacity_grant = 1 AND reach_grant_dep_75 = 1)

**Lower priority for calls:**
- has_biz_dev_staff = 'no' (easier to reach but won't convert)
- new_to_foundations = 1 (won't answer)

---

## 8. Surprising Findings

1. **"No biz dev staff" is a trap** - These orgs answer more but convert less. They're not actively seeking grants.

2. **ICP score irrelevant for calls** - The score doesn't predict phone success at all. May need a separate "call likelihood" score.

3. **Established grantees answer more** - Counter-intuitive, but orgs already receiving foundation grants are MORE responsive, not less.

4. **Small sample caveat** - With only 49 calls and 3 interested parties, these findings are directional, not statistically significant. Would need 200+ calls to confirm.

---

## 9. Data Quality Notes

- **46/49 (94%)** calls matched to database
- **3 unmatched:** Two unknown EINs + PSMF (our beta client)
- **shares_funder_with_beta = 100%** for all called orgs (not discriminating)
- **likely_active_fundraiser = 0%** for all called orgs (flag not working or wrong segment)

---

## Deliverables

1. **This report:** `REPORT_2025-12-11_call_flag_analysis.md`
2. **Enriched data:** `DATA_2025-12-11_call_flag_enriched.csv` (49 rows, 35 columns)

---

*Analysis completed 2025-12-11*
