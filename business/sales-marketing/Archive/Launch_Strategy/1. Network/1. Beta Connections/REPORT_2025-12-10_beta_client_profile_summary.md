# Beta Client Profile Summary

**Date:** 2025-12-10
**Purpose:** Analyze F990 data for beta clients + VetsBoats to define ICP targeting criteria

---

## Executive Summary

Analysis of 7 beta clients (8 records including duplicate) found in the F990 database reveals a diverse group of nonprofits ranging from $365K to $42M in revenue. Excluding the outlier (RHF at $42M), the core profile is:

- **Revenue:** $1.3M - $3.4M (recommended target: $1.6M - $2.7M)
- **Grant Dependency:** Wide range (0.2% - 100%), with median at 94%
- **Employees:** 0 - 82 (median: 8)
- **Geography:** Mostly California (4/7), plus CT, NC, HI

**Key Finding:** VetsBoats Foundation (first paying client) found in grants data with EIN 464194065, receiving $43,500 in foundation grants from 3 funders.

---

## Beta Clients Found in Database

| Organization | EIN | Group | State | Revenue | Grant Dep % | Employees |
|--------------|-----|-------|-------|---------|-------------|-----------|
| Retirement Housing Foundation | 952249495 | BG1 | CA | $42,118,324 | 45.3% | 78 |
| Horizons National | 061468129 | BG2 | CT | $3,409,631 | 95.6% | 19 |
| Arborbrook Christian Academy | 202707577 | BG1 | NC | $2,705,662 | 15.8% | 82 |
| Friendship Circle SD | 203472700 | BG2 | CA | $2,690,324 | 94.1% | 8 |
| Senior Network Services | 942259716 | BG1 | CA | $1,956,265 | 94.9% | 26 |
| Ka Ulukoa | 260542078 | BG1 | HI | $1,308,763 | 0.2% | 0 |
| Patient Safety Movement Foundation | 462730379 | BG1 | CA | $365,177 | 100.0% | 4 |

**Not Found:** VetsBoats Foundation (464194065) not in nonprofit_returns table, but found in pf_grants as grant recipient.

---

## Summary Statistics

### All Orgs (n=7 unique)

| Metric | Min | Median | Max |
|--------|-----|--------|-----|
| Revenue | $365,177 | $2,690,324 | $42,118,324 |
| Expenses | $771,056 | $2,036,635 | $26,718,964 |
| Assets | $89,728 | $2,106,556 | $226,932,871 |
| Employees | 0 | 8 | 82 |
| Volunteers | 0 | 26 | 466 |
| Grant Dependency | 0.2% | 94.1% | 100.0% |

### Excluding RHF (n=6) - More Representative ICP

| Metric | Min | Median | Max |
|--------|-----|--------|-----|
| Revenue | $365,177 | $2,323,264 | $3,409,631 |
| Employees | 0 | 13.5 | 82 |
| Grant Dependency | 0.2% | 94.5% | 100.0% |

---

## Foundation Grants Received

Beta clients have received grants from private foundations tracked in F990-PF data:

| Organization | Total Grants | Unique Funders | Total Amount | Years Active |
|--------------|--------------|----------------|--------------|--------------|
| Horizons National | 16 | 11 | $626,960 | 2022-2024 |
| VetsBoats Foundation | 3 | 3 | $43,500 | 2023 |
| Arborbrook Christian Academy | 3 | 2 | $6,050 | 2022-2023 |
| Senior Network Services | 2 | 1 | $1,000 | 2022-2023 |
| Patient Safety Movement Foundation | 1 | 1 | $50,000 | 2021 |
| Friendship Circle SD | 1 | 1 | $20 | 2022 |
| Ka Ulukoa | 0 | 0 | $0 | — |
| Retirement Housing Foundation | 0 | 0 | $0 | — |

**Insight:** Most beta clients have minimal foundation grant history (0-3 grants). Horizons National is the exception with 16 grants. This suggests our target market may be nonprofits that are **new to foundation fundraising** or underserved by traditional grant sources.

---

## Revenue Trends (2019-2024)

| Organization | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | Trend |
|--------------|------|------|------|------|------|------|-------|
| RHF | $35.0M | — | $49.8M | $106.9M | $42.1M | — | Volatile |
| Horizons | — | $4.5M | — | $3.8M | $2.6M | $3.4M | Recovering |
| Arborbrook | $1.9M | $1.8M | $2.4M | $3.1M | $2.7M | — | Growing |
| Friendship Circle SD | — | $0.4M | $0.2M | $3.4M | $2.7M | — | Major growth |
| Senior Network Services | — | $1.2M | $0.8M | $1.3M | $2.0M | — | Growing |
| Ka Ulukoa | $0.3M | $0.03M | $0.4M | $0.9M | $1.3M | — | Strong growth |
| PSMF | $2.4M | $2.2M | $1.2M | $1.3M | $2.1M | $0.4M | Volatile |

**Growth Pattern:** Most beta clients show revenue growth over the past 3-5 years, suggesting they're in expansion mode and may need grant funding to support growth.

---

## Recommended ICP Range

Based on beta client analysis, excluding RHF as outlier:

### Primary Criteria (Must-Have)

| Attribute | Target Range | Rationale |
|-----------|--------------|-----------|
| **Revenue** | $1,000,000 - $3,500,000 | Core beta client range |
| **Form Type** | 990 or 990-EZ | Public charities |

### Secondary Criteria (Nice-to-Have)

| Attribute | Target Range | Rationale |
|-----------|--------------|-----------|
| Grant Dependency | 50% - 100% | Indicates need for grant funding |
| Employees | 5 - 50 | Has staff capacity |
| Foundation Grants | 0 - 5 | Underserved by foundations |
| Revenue Trend | Growing or stable | Can invest in services |

### Geography (Proven Markets)

- **Primary:** California (4 of 7 beta clients)
- **Secondary:** All U.S. states

### Sectors

NTEE codes not available in database for these orgs, but based on known sectors:
- E (Healthcare/Medical): PSMF
- B (Education): Horizons, Arborbrook
- P (Human Services): Senior Network Services
- N (Recreation/Sports): Ka Ulukoa, VetsBoats
- P (Human Services): Friendship Circle SD

---

## Key Questions Answered

### 1. What's the revenue range of converted orgs?
**$365K - $42M** (full range), **$1.3M - $3.4M** (excluding RHF outlier)

### 2. How many employees/volunteers do they have?
**Employees:** 0-82 (median 8)
**Volunteers:** 0-466 (median 26)

### 3. How grant-dependent are they?
**Wide range:** 0.2% to 100%, with **median 94%** - most are highly grant-dependent

### 4. How many foundation grants have they received?
**Range:** 0-16 grants
**Median:** 1-2 grants
**Most have minimal foundation funding history**

### 5. Are they growing or shrinking?
**Mostly growing** - 5 of 7 show upward revenue trends over past 3 years

### 6. What sectors (NTEE) are represented?
Education (B), Healthcare (E), Human Services (P), Recreation (N)

### 7. Is RHF an outlier we should exclude from ICP?
**Yes** - RHF at $42M revenue is 12x larger than the next largest beta client. Should be excluded from ICP targeting but represents an interesting "enterprise" segment.

---

## Database Query for ICP Prospects

```sql
-- Find nonprofits matching beta client ICP
SELECT
    ein,
    organization_name,
    state,
    total_revenue,
    contributions_grants,
    ROUND(100.0 * contributions_grants / NULLIF(total_revenue, 0), 1) as grant_dependency_pct,
    total_employees_cnt,
    total_volunteers_cnt
FROM f990_2025.nonprofit_returns
WHERE tax_year = 2023
  AND total_revenue BETWEEN 1000000 AND 3500000
  AND contributions_grants > 0
  AND ROUND(100.0 * contributions_grants / NULLIF(total_revenue, 0), 1) >= 50
  AND total_employees_cnt BETWEEN 5 AND 50
ORDER BY total_revenue DESC
LIMIT 1000;
```

---

## Deliverables

- [x] `DATA_2025-12-10_beta_client_profiles.csv` — Full comparison data
- [x] `REPORT_2025-12-10_beta_client_profile_summary.md` — This summary
- [x] `beta_client_profiling.py` — Python analysis script

---

*Generated: 2025-12-10*
*Prompt: PROMPT_2025-12-10_beta_client_profiling.md*
