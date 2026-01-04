# Capacity Grant Field Analysis Report
**Generated:** 2025-12-10

---

## Executive Summary

Added 6 new capacity-building grant fields to the prospects table. **31,928 prospects (43.1%)** have received capacity grants (general operating, general support, or unrestricted funding).

**Key Findings:**
- 128,332 unique organizations in the database received capacity grants
- 31,928 of these matched to prospects in our table
- Average capacity grant amount: $40,704
- 25 "prime prospects" have high ICP, full reachability, AND recent capacity grants

---

## 1. Capacity Grant Coverage

| Received Capacity Grant | Count | Percent |
|------------------------|-------|---------|
| No | 42,216 | 56.9% |
| Yes | 31,928 | 43.1% |

---

## 2. Capacity Grant Amount Distribution

| Amount Band | Count |
|-------------|-------|
| <$10K | 16,447 |
| $10K-$25K | 5,848 |
| $25K-$50K | 3,508 |
| $50K-$100K | 2,666 |
| >$100K | 3,459 |

**Note:** Over half of capacity grants are under $10K, but 3,459 prospects received capacity grants of $100K+.

---

## 3. Capacity Grant as Percent of Revenue

| Percent of Revenue | Count |
|-------------------|-------|
| <1% | 19,596 |
| 1-5% | 8,071 |
| 5-10% | 2,180 |
| 10-25% | 1,509 |
| >25% | 572 |

**Note:** Most capacity grants represent less than 1% of nonprofit revenue, indicating these are supplemental rather than core funding.

---

## 4. Top 20 Prospects with Recent Capacity Grants

| EIN | Organization | State | Sector | Revenue | Grant Date | Grant Amount | % Rev | Funder | ICP | Reach |
|-----|-------------|-------|--------|---------|------------|--------------|-------|--------|-----|-------|
| 946182681 | Association for Education | CA | B | $1,070,505 | 2024-12-31 | $200 | N/A | JPMORGAN CHASE FOUND | 12 | 0 |
| 942598256 | LIVE VIOLENCE FREE | CA | P | $2,538,460 | 2024-12-31 | $3,000 | 0.1% | Schiller Foundation | 12 | 0 |
| 941156357 | Womens Division Christian | CA | P | $2,588,486 | 2024-12-31 | $50 | N/A | JPMORGAN CHASE FOUND | 12 | 0 |
| 680218781 | PLOWSHARES PEACE & JUSTICE | CA | P | $1,197,806 | 2024-12-31 | $2,000 | 0.2% | KAUFMAN FAMILY FOUND | 12 | 0 |
| 472341475 | TORAH EDUCATION OF AMERICA | NJ | B | $2,705,743 | 2024-12-31 | $50 | N/A | THE ZEV AND SUSAN MU | 11 | 0 |
| 263658409 | KAKENYA CENTER FOR EXCELL | VA | B | $2,100,044 | 2024-12-31 | $1,250 | 0.1% | PINKI AND DENNIS MEA | 11 | 0 |
| 461737255 | SERVE 6 8 | CO | P | $3,337,820 | 2024-12-31 | $500 | N/A | First Interstate Ban | 11 | 0 |
| 410696493 | YOUNG WOMEN'S CHRISTIAN A | MN | P | $1,419,082 | 2024-12-31 | $100,000 | 7.0% | ORDEAN FOUNDATION | 11 | 0 |
| 470823383 | MERRICK COUNTY CHILD CARE | NE | N | $1,452,312 | 2024-12-31 | $5,000 | 0.3% | DINSDALE FAMILY FOUN | 11 | 0 |
| 272023911 | ERIK HITE FOUNDATION INC | AZ | P | $1,395,813 | 2024-12-31 | $49,765 | 3.6% | GATES FAMILY FOUNDAT | 11 | 0 |
| 440562039 | ALPHA PHI OMEGA NATIONAL | MO | B | $2,188,464 | 2024-12-31 | $650 | N/A | JPMORGAN CHASE FOUND | 11 | 0 |
| 454307513 | AL HADI INITIATIVES | TX | B | $1,232,797 | 2024-12-31 | $2,000 | 0.2% | JPMORGAN CHASE FOUND | 11 | 0 |
| 351148259 | FAMILY SERVICE OF BARTHOL | IN | P | $1,164,011 | 2024-12-31 | $2,861 | 0.2% | BUCHANAN-CLEMENTS FO | 11 | 0 |
| 262895165 | ANGELS FOSTER FAMILY NETW | OK | P | $1,785,393 | 2024-12-31 | $4,000 | 0.2% | The Magnolia Charita | 11 | 0 |
| 391247541 | WALKER'S POINT YOUTH AND | WI | P | $1,226,811 | 2024-12-31 | $10,000 | 0.8% | PETROVIC GUBIN FOUND | 11 | 0 |
| 271799465 | TENNESSEE CHARTER SCHOOL | TN | B | $1,075,128 | 2024-12-31 | $50,000 | 4.7% | DEVINE-MAJORS FOUNDA | 11 | 0 |
| 470605938 | Bright Horizons Resources | NE | P | $3,178,737 | 2024-12-31 | $1,000 | N/A | First Interstate Ban | 11 | 0 |
| 452465260 | FRIENDS OF THE MANDARIN S | CA | B | $2,284,992 | 2024-12-31 | $750 | N/A | JPMORGAN CHASE FOUND | 11 | 0 |
| 271458930 | COMMUNITIES OF ROOTED BRI | WA | B | $1,260,784 | 2024-12-31 | $3,000 | 0.2% | KAWABE MEMORIAL FUND | 11 | 0 |
| 311482374 | THE COLUMBUS JEWISH DAY S | OH | B | $2,507,915 | 2024-12-31 | $290 | N/A | JPMORGAN CHASE FOUND | 11 | 0 |

---

## 5. Prime Prospects (High ICP + Reachable + Capacity Grant)

**Total Prime Prospects:** 25

These are prospects with:
- ICP Score >= 10
- reach_all_flags = 1 (fully reachable)
- received_capacity_grant = 1

---

## 6. Capacity Grant Keywords Used

Grants were identified using purpose text containing these keywords:
- capacity
- general operating
- general support
- operating support
- organizational development
- infrastructure
- unrestricted

---

## 7. New Columns Added to Prospects Table

| Column | Type | Description |
|--------|------|-------------|
| capacity_grant_date | DATE | Date of most recent capacity grant (year-end) |
| capacity_grant_amount | NUMERIC | Amount of most recent capacity grant |
| capacity_grant_funder_ein | VARCHAR(20) | EIN of funder who gave capacity grant |
| capacity_grant_funder_name | TEXT | Name of funder who gave capacity grant |
| capacity_grant_pct_of_revenue | NUMERIC | Grant amount as % of nonprofit's revenue |
| received_capacity_grant | SMALLINT | Flag: 1 if received capacity grant, 0 if not |

---

## 8. Summary Statistics

- **Total Prospects:** 74,144
- **With Capacity Grant:** 31,928 (43.1%)
- **Average Grant Amount:** $40,703.55
- **Max Grant Amount:** $10,443,318.00
- **Min Grant Amount:** $-200.00 (likely data error or refund)

---

## Usage Notes

### Query Examples

**Find prospects with recent capacity grants:**
```sql
SELECT * FROM f990_2025.prospects
WHERE received_capacity_grant = 1
  AND capacity_grant_date >= '2023-01-01'
ORDER BY capacity_grant_amount DESC;
```

**Find prime prospects (high ICP + reachable + capacity grant):**
```sql
SELECT * FROM f990_2025.prospects
WHERE icp_score >= 10
  AND reach_all_flags = 1
  AND received_capacity_grant = 1
ORDER BY icp_score DESC, capacity_grant_amount DESC;
```

**Analyze by grant amount tier:**
```sql
SELECT
    CASE
        WHEN capacity_grant_amount < 10000 THEN '<$10K'
        WHEN capacity_grant_amount < 50000 THEN '$10K-$50K'
        ELSE '$50K+'
    END as tier,
    COUNT(*) as count,
    AVG(icp_score) as avg_icp
FROM f990_2025.prospects
WHERE received_capacity_grant = 1
GROUP BY 1;
```

---

## Technical Notes

- Data sourced from `f990_2025.pf_grants` table
- Funder names retrieved via JOIN to `f990_2025.pf_returns`
- Most recent grant selected using `ROW_NUMBER()` window function ordered by tax_year DESC, amount DESC
- Percent of revenue calculated as: `(grant_amount / total_revenue) * 100`

---

*Report generated from PROMPT_2025-12-10_capacity_grant_fields.md*
