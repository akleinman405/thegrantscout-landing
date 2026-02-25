# Client Viability Check Skill: Design Proposal

**Date:** 2026-02-20
**Prompt:** PROMPT_2026-02-20_4_viability_skill_build.md
**Status:** Complete
**Owner:** Aleck Kleinman

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-20 | Claude Code | Initial proposal from plan |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What to Keep vs. Cut from Proclaim Assessment](#what-to-keep-vs-cut-from-proclaim-assessment)
3. [Skill Design: Step 0 + 3 Checks](#skill-design-step-0--3-checks)
4. [SQL Templates](#sql-templates)
5. [Verdict Thresholds and Decision Matrix](#verdict-thresholds-and-decision-matrix)
6. [CONDITIONAL Prescriptive Guidance](#conditional-prescriptive-guidance)
7. [Output Format](#output-format)
8. [Edge Cases](#edge-cases)
9. [Files Created/Modified](#files-createdmodified)
10. [Notes](#notes)

---

## Executive Summary

The Proclaim Aviation viability assessment (REPORT_2026-02-20.3) took 30+ minutes and produced 538 lines across 7 dimensions. Only 2 dimensions (D3: Sibling Analysis, D4: Foundation Overlap) actually answered the core question: "Does our DB have enough foundation matches to sustain monthly reports?"

This proposal designs a reusable skill that delivers a **GO / CONDITIONAL / NO GO** verdict in 5-10 minutes using 3 focused checks against pre-computed and live data. The skill requires only 4 inputs (NTEE, state, revenue, and optionally EIN) and produces a short report with pool sizes, top 3 foundations, and a one-paragraph summary.

---

## What to Keep vs. Cut from Proclaim Assessment

| Proclaim Dimension | Verdict | Reason |
|---|---|---|
| D3: Sibling Organization Analysis | **KEEP** (streamlined) | Finds peer orgs, proves niche has foundation interest |
| D4: Foundation Overlap from Siblings | **KEEP** (core) | Produces THE number: production-ready foundations |
| D1: Sector Foundation Pool | **CUT** | Every sector has thousands; doesn't differentiate |
| D2: Geography Pool | **REPLACE** with cohort_viability lookup | Pre-computed, instant, same answer |
| D5: Peer Comparison | **CUT** | Psychological comfort, not a viability gate |
| D6: Known Funder Network | **CUT** | Overlaps with D4; discovery method not viability gate |
| D7: Email Cohort Positioning | **CUT** | Technical infrastructure check, not viability |

**Result:** 7 dimensions reduced to 3 checks. Estimated time: 5-10 minutes (vs. 30+).

---

## Skill Design: Step 0 + 3 Checks

### Step 0: EIN Lookup (if EIN provided, < 1 second)

When an EIN is provided, auto-populate inputs from the database:

1. Check `dim_clients` first: if the EIN matches an existing client, stop immediately ("Already a client, ID {N}")
2. Check `dim_recipients`: get state, ntee_code, name. Note existing funder count as bonus intel.
3. Check `nonprofit_returns` (latest tax_year): get total_revenue, mission_description, organization_name

This eliminates manual data entry for orgs already in our DB.

### Check 1: Cohort Pool Size (instant, < 1 second)

Lookup `f990_2025.cohort_viability` for the org's state + NTEE sector letter.

- 882 pre-computed combos covering all state/sector intersections
- Returns `foundation_count` (pre-filtered: accepts applications + sector + state match)
- If combo not found, pool is effectively 0
- For **national orgs**: query sector-wide foundation count across all states (deduplicated)
- Apply **0.85 haircut** to the raw count (cohort_viability uses looser filters than production)

This check provides instant context but is NOT the primary verdict driver.

### Check 2: Sibling Funder Network (5-15 seconds)

This is the primary signal. It answers: "How many production-ready foundations fund orgs like this one?"

**Process:**
1. Find 10 peer orgs from `dim_recipients` (same NTEE broad sector + state), joined with `nonprofit_returns` for revenue filtering (0.25x to 4x of target revenue)
2. **Order peers by funder count DESC** before LIMIT 10 (data review showed 9.5x more results vs. random selection)
3. For those peers, find all distinct foundations from `fact_grants` (tax_year >= 2019)
4. Apply production filters via `calc_foundation_profiles`:
   - `has_grant_history = TRUE`
   - Assets >= $100K (via `pf_returns.total_assets_eoy_amt`)
   - `unique_recipients_5yr >= 5`
   - `accepts_applications = TRUE`
5. Return: count of production-ready foundations + top 3 by median grant size

**Fallback cascade** if < 5 peers found:
- Drop revenue filter (keep sector + state)
- If still < 5: broaden to sector-only (drop state)
- Report what's available and note fallback used

### Check 3: Sustainability Projection (computed, no query)

Pure math based on Check 2 results:

- **Pool estimate** = Check 2 count (production-filtered)
- **Delivery model:** 5 foundations/report, ~12 reports/year = 60 unique foundations needed
- **Enrichment attrition:** ~30% of production-filtered pool survives to report-ready
- **Effective report-ready estimate** = pool * 0.30
- **Months of coverage** = (report-ready estimate / 5)

---

## SQL Templates

### Step 0A: Check Existing Client

```sql
SELECT id, name, ein, state, sector_ntee, status
FROM f990_2025.dim_clients
WHERE ein = '{ein}'
LIMIT 1
```

### Step 0B: Lookup in dim_recipients

```sql
SELECT
    dr.ein,
    dr.name,
    dr.state,
    dr.ntee_code,
    dr.ntee_broad,
    COUNT(DISTINCT fg.foundation_ein) AS existing_funder_count
FROM f990_2025.dim_recipients dr
LEFT JOIN f990_2025.fact_grants fg
    ON fg.recipient_ein = dr.ein
    AND fg.tax_year >= 2019
WHERE dr.ein = '{ein}'
GROUP BY dr.ein, dr.name, dr.state, dr.ntee_code, dr.ntee_broad
```

### Step 0C: Lookup in nonprofit_returns (latest year)

```sql
SELECT
    ein,
    organization_name,
    state,
    ntee_code,
    total_revenue,
    mission_description,
    tax_year
FROM f990_2025.nonprofit_returns
WHERE ein = '{ein}'
ORDER BY tax_year DESC
LIMIT 1
```

### Check 1: Cohort Pool Lookup

```sql
SELECT
    state,
    ntee_sector,
    sector_label,
    foundation_count,
    prospect_count,
    avg_foundation_giving,
    viable,
    display_count,
    display_text
FROM f990_2025.cohort_viability
WHERE state = '{state}'
  AND ntee_sector = '{ntee_sector}'
```

### Check 1 (National variant): Sector-wide deduplicated count

```sql
SELECT COUNT(DISTINCT foundation_ein) AS national_foundation_count
FROM f990_2025.fact_grants fg
JOIN f990_2025.calc_foundation_profiles cfp ON cfp.ein = fg.foundation_ein
JOIN f990_2025.dim_recipients dr ON dr.ein = fg.recipient_ein
JOIN f990_2025.pf_returns pr ON pr.ein = fg.foundation_ein
WHERE LEFT(dr.ntee_code, 1) = '{ntee_sector}'
  AND fg.tax_year >= 2019
  AND cfp.has_grant_history = TRUE
  AND pr.total_assets_eoy_amt >= 100000
  AND cfp.unique_recipients_5yr >= 5
  AND cfp.accepts_applications = TRUE
```

### Check 2A: Find Peer Organizations

```sql
WITH peer_candidates AS (
    SELECT
        dr.ein,
        dr.name,
        dr.state,
        dr.ntee_code,
        nr.total_revenue,
        COUNT(DISTINCT fg.foundation_ein) AS funder_count
    FROM f990_2025.dim_recipients dr
    JOIN f990_2025.nonprofit_returns nr
        ON nr.ein = dr.ein
    JOIN f990_2025.fact_grants fg
        ON fg.recipient_ein = dr.ein
        AND fg.tax_year >= 2019
    WHERE dr.ntee_broad = '{ntee_broad}'
      AND dr.state = '{state}'
      AND dr.ein != '{target_ein}'
      AND nr.tax_year = (
          SELECT MAX(nr2.tax_year)
          FROM f990_2025.nonprofit_returns nr2
          WHERE nr2.ein = nr.ein
      )
      AND nr.total_revenue BETWEEN {revenue_min} AND {revenue_max}
    GROUP BY dr.ein, dr.name, dr.state, dr.ntee_code, nr.total_revenue
)
SELECT * FROM peer_candidates
ORDER BY funder_count DESC, ein
LIMIT 10
```

**Parameter notes:**
- `{ntee_broad}` = first letter of NTEE code (e.g., "X" from "X20")
- `{revenue_min}` = target_revenue * 0.25
- `{revenue_max}` = target_revenue * 4.0
- `{target_ein}` = the prospect's EIN (exclude self from peers)

### Check 2B: Find Production-Ready Foundations from Peers

```sql
WITH peer_eins AS (
    {check_2a_query_as_subquery}
),
peer_funders AS (
    SELECT DISTINCT fg.foundation_ein
    FROM f990_2025.fact_grants fg
    WHERE fg.recipient_ein IN (SELECT ein FROM peer_eins)
      AND fg.tax_year >= 2019
)
SELECT
    pf.foundation_ein AS ein,
    df.name AS foundation_name,
    df.state AS foundation_state,
    cfp.median_grant,
    cfp.total_giving_5yr,
    cfp.unique_recipients_5yr,
    cfp.giving_trend,
    COUNT(DISTINCT fg2.recipient_ein) AS peers_funded
FROM peer_funders pf
JOIN f990_2025.dim_foundations df ON df.ein = pf.foundation_ein
JOIN f990_2025.calc_foundation_profiles cfp ON cfp.ein = pf.foundation_ein
JOIN f990_2025.pf_returns pr ON pr.ein = pf.foundation_ein
LEFT JOIN f990_2025.fact_grants fg2
    ON fg2.foundation_ein = pf.foundation_ein
    AND fg2.recipient_ein IN (SELECT ein FROM peer_eins)
    AND fg2.tax_year >= 2019
WHERE cfp.has_grant_history = TRUE
  AND pr.total_assets_eoy_amt >= 100000
  AND cfp.unique_recipients_5yr >= 5
  AND cfp.accepts_applications = TRUE
GROUP BY pf.foundation_ein, df.name, df.state,
         cfp.median_grant, cfp.total_giving_5yr,
         cfp.unique_recipients_5yr, cfp.giving_trend
ORDER BY cfp.median_grant DESC NULLS LAST, pf.foundation_ein
```

### Check 2 Fallback A: Drop revenue filter

Same as Check 2A but remove the `AND nr.total_revenue BETWEEN...` clause.

### Check 2 Fallback B: Drop state filter (sector-only)

Same as Check 2A but remove `AND dr.state = '{state}'` and the revenue clause.

---

## Verdict Thresholds and Decision Matrix

### Primary Thresholds (applied to Check 2 production-filtered count)

| Verdict | Check 2 Pool | Report-Ready Est. (30%) | Sustainability |
|---|---|---|---|
| **GO** | 50+ | 15+ | 12+ months at 5/report |
| **CONDITIONAL** | 20-49 | 6-14 | 4-9 months; note constraints |
| **NO GO** | < 20 | < 6 | Cannot sustain quarterly delivery |

**Distribution estimate:** 80.7% of state+sector combos = GO, 13.8% = CONDITIONAL, 5.4% = NO GO.

### Decision Matrix (when Check 1 and Check 2 conflict)

| Check 1 (Cohort) | Check 2 (Siblings) | Verdict | Note |
|---|---|---|---|
| 50+ | 50+ | **GO** | Strong on both signals |
| 50+ | 20-49 | **CONDITIONAL** | Broad pool exists but production filters reduce it |
| 50+ | < 20 | **CONDITIONAL** | Investigate why sibling funders fail filters |
| 20-49 | 30+ | **CONDITIONAL** | State pool thin but sibling network compensates |
| < 20 | 50+ | **GO** | Sibling network overrides thin local pool |
| < 20 | < 20 | **NO GO** | Both signals weak |

**Resolution rule: Check 2 is the primary signal.** Check 1 provides context only. When they conflict, Check 2 wins except when Check 2 is borderline (20-49) and Check 1 is strong (50+), which upgrades the confidence of the CONDITIONAL.

---

## CONDITIONAL Prescriptive Guidance

The summary auto-selects one template based on the data pattern:

| Pattern | Template |
|---|---|
| Thin state, strong siblings | "State pool is thin ({N}), but national funders from sibling network ({K}) compensate. Recommend Foundation-Focused report format." |
| Thin sector, strong state | "Sector pool is niche, but {state} has a strong foundation base. Cross-sector funders are the opportunity." |
| Both thin | "Both state and sector pools are thin. Recommend 3-month pilot before annual commitment." |
| Adequate pool, low quality | "Pool adequate ({N}), but median grant ${X}. Set expectations for $5K-$15K grants." |

---

## Output Format

### Console Output

```
VERDICT: GO | CONDITIONAL | NO GO

Pool Size: {N} production-ready foundations
  - Cohort pool (state+sector): {M} (adjusted)
  - Sibling network pool: {K} (from {S} peer orgs)
  - Estimated report-ready: {R} (~30% of production pool)

Top Foundations:
  1. {Foundation Name} - ${median_grant} median grant, funds {N} peers
  2. {Foundation Name} - ${median_grant} median grant, funds {N} peers
  3. {Foundation Name} - ${median_grant} median grant, funds {N} peers

Summary: "{Pool_size} production-ready foundations match {org_name}'s profile
({sector_label} sector, {state}). {Check_2_insight}. {Conditional_caveat}.
Comparable foundations include {fdn_1}, {fdn_2}, and {fdn_3}."
```

### Report File (50-80 lines)

A short report following CLAUDE.md structure is also saved to `Enhancements/{date}/` or `5. Runs/{client}/{date}/`:

```
REPORT_YYYY-MM-DD.N_{org_name_snake}_viability.md
```

Contains: Executive Summary (verdict + pool numbers), Check 1-3 results with key data points, Top 3 foundations table, the summary paragraph, and notes/caveats.

---

## Edge Cases

| Scenario | Handling |
|---|---|
| **National org** (geographic_scope = 'national') | Check 1: use national variant SQL (sector-wide, deduplicated). Check 2: drop state from peer search. |
| **Multi-sector org** | Use primary NTEE. Note in summary if secondary sector would yield different result. |
| **US Territories** (VI, GU, PR, AS, MP) | Likely NO GO due to thin data. Flag explicitly: "Territory-based orgs have limited foundation coverage in IRS data." |
| **No NTEE code available** | Require user to provide one. Suggest looking up on GuideStar/Candid. Cannot run without sector. |
| **Existing client** | Step 0 catches this. Stop with: "Already a client (ID {N}). Use report pipeline instead." |
| **EIN not in DB** | Step 0 returns nothing. All inputs must come from user. Note: "No IRS filing data found; inputs are user-provided." |
| **Zero peers found** (even after fallbacks) | Report as NO GO with note: "No comparable organizations found in IRS grant data. This sector/geography combination has minimal foundation coverage." |
| **< 5 peers found** | Report available count. Note: "Limited peer data ({N} orgs). Pool estimate may be less reliable." |

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| This report | `Enhancements/2026-02-20/REPORT_2026-02-20_4_viability_skill_proposal.md` | Skill design proposal |
| Skill file (pending) | `.claude/SKILL_client_viability_check.md` | Reusable skill (after approval) |
| CLAUDE.md update (pending) | `.claude/CLAUDE.md` | Add skill to Skills table |

---

## Notes

**Verification results (all 3 dry-runs passed):**

| Test Case | Check 1 | Check 2 | Verdict | Expected | Match? |
|---|---|---|---|---|---|
| Proclaim Aviation (MN, X, $2.5M) | 130 adjusted | 169 production-ready | **GO** | GO | Yes |
| VI + Civil Rights ($500K) | 1 (not viable) | 0 sector-specific | **NO GO** | NO GO | Yes |
| National Environmental (DC, C, $5M) | 4,483 national | 1,365 production-ready | **GO** | GO | Yes |

**Key findings from verification:**
- National variant correctly yields 5x more foundations than state-only (4,483 vs 902)
- Fallback cascade triggered all 3 levels for VI (zero peers at state level)
- MCP postgres timed out on national query (large join); psql fallback worked
- Use `<>` instead of `!=` in SQL for psql/Bash shell compatibility

**Future enhancements:**
- **Screen mode:** Batch Check 1 only for rapid prospect list triage (no sibling analysis)
- **viability_assessments table:** Store results for historical tracking and sales pipeline analytics
- **Auto-populate from CRM:** If prospect intake form captures EIN, auto-trigger viability check

**Design decisions:**
- Check 2 orders peers by funder_count DESC (not random) because Proclaim data showed 9.5x more foundation results vs. random peer selection
- 0.85 haircut on Check 1 because cohort_viability uses looser filters than the 4-filter production chain
- 30% enrichment attrition is based on observed rates from VetsBoats and Proclaim report generation

---

*Generated by Claude Code on 2026-02-20*
