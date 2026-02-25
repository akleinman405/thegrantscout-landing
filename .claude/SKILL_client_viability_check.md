# SKILL: Client Viability Check

**Purpose:** Determine whether TheGrantScout's database has enough foundation matches to sustain monthly grant reports for a prospective nonprofit client.

---

## Overview

Before onboarding a new client, run this viability check to answer one question: **"Does our DB have enough foundation matches to deliver useful monthly reports?"**

This skill produces a **GO / CONDITIONAL / NO GO** verdict in 5-10 minutes using 3 focused checks. It replaces the full 7-dimension viability assessment (which took 30+ minutes and mostly answered questions that don't gate viability).

### When to Use

- Before a sales call with a new nonprofit prospect
- When a prospect fills out the intake questionnaire
- When evaluating a new market segment (run against a representative org)

### When NOT to Use

- For existing clients (use the report pipeline instead)
- For foundation prospects (this skill is nonprofit-only)
- For detailed competitive analysis (this is a go/no-go gate, not a strategy document)

---

## Required Inputs

| Input | Required | Source | Notes |
|---|---|---|---|
| NTEE code | Yes | User or Step 0 lookup | First letter extracted as sector (e.g., "X" from "X20") |
| State | Yes | User or Step 0 lookup | 2-letter code |
| Annual revenue | Yes | User or Step 0 lookup | For peer revenue filtering |
| EIN | Optional | User | Enables Step 0 auto-fill; skip if unknown |
| Geographic scope | Optional | User | `state` (default), `regional`, `national` |
| Organization name | Optional | User | For report header and summary text |

---

## Process Steps

### Step 0: EIN Lookup (if EIN provided)

**Time:** < 1 second. **Purpose:** Auto-populate inputs, catch existing clients.

**0A. Check if already a client:**

```sql
SELECT id, name, ein, state, sector_ntee, status
FROM f990_2025.dim_clients
WHERE ein = '{ein}'
LIMIT 1
```

If found: **STOP.** Output: "Already a client (ID {id}, status: {status}). Use report pipeline instead."

**0B. Lookup in dim_recipients:**

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

If found: auto-fill name, state, ntee_code, ntee_broad. Note existing_funder_count as bonus intel for the summary.

**0C. Lookup in nonprofit_returns (latest year):**

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

If found: auto-fill total_revenue, organization_name (if not already set), mission_description (for context). Use `tax_year` to note data recency.

**After Step 0:** Confirm all required inputs are populated. If any are missing, ask the user to provide them before continuing.

---

### Check 1: Cohort Pool Size (instant)

**Time:** < 1 second. **Purpose:** Instant context from pre-computed data.

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

**Processing:**
- Apply **0.85 haircut** to `foundation_count` (cohort_viability uses looser filters than production)
- Adjusted count = `FLOOR(foundation_count * 0.85)`
- If no row returned: adjusted count = 0 (this state+sector combo has no coverage)
- Record `sector_label` for use in the summary

**For national orgs** (geographic_scope = 'national'), use this instead:

```sql
SELECT COUNT(DISTINCT fg.foundation_ein) AS national_foundation_count
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

No haircut needed for the national variant (it applies production filters directly).

---

### Check 2: Sibling Funder Network (primary signal)

**Time:** 5-15 seconds. **Purpose:** Find production-ready foundations that fund similar organizations.

This is the most important check. It answers: "How many real, contactable foundations fund orgs like this one?"

**2A. Find peer organizations:**

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
      AND dr.ein <> '{target_ein}'
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

**Parameter substitution:**
- `{ntee_broad}` = first letter of NTEE code (e.g., "X" from "X20")
- `{revenue_min}` = annual_revenue * 0.25
- `{revenue_max}` = annual_revenue * 4.0
- `{target_ein}` = the prospect's EIN (or '0000000000' if no EIN provided)

**Fallback cascade** (if < 5 peers found):
1. **Fallback A:** Remove the revenue filter (`AND nr.total_revenue BETWEEN...`). Keep sector + state.
2. **Fallback B:** Remove state filter too (`AND dr.state = '{state}'`). Sector-only, nationwide.
3. **Fallback C:** If still < 5 peers, proceed with whatever is available. Note in output.

Record which fallback was used (or "none") for the summary.

**2B. Find production-ready foundations from peers:**

```sql
WITH peer_eins AS (
    SELECT ein FROM (VALUES
        ('{peer_ein_1}'), ('{peer_ein_2}'), ('{peer_ein_3}'),
        ('{peer_ein_4}'), ('{peer_ein_5}'), ('{peer_ein_6}'),
        ('{peer_ein_7}'), ('{peer_ein_8}'), ('{peer_ein_9}'),
        ('{peer_ein_10}')
    ) AS t(ein)
    WHERE ein IS NOT NULL
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

**From results, extract:**
- `check_2_pool` = total row count (production-ready foundations)
- `top_3` = first 3 rows (for "Name 3" output)
- `peers_funded` on each row shows how many of the 10 peers that foundation funds

---

### Check 3: Sustainability Projection (computed)

**Time:** 0 seconds (pure math). **Purpose:** Translate pool size into months of report coverage.

```
pool_size         = check_2_pool
report_ready      = FLOOR(pool_size * 0.30)
months_coverage   = FLOOR(report_ready / 5)
foundations_year   = 60  (5/report * 12 reports)
```

| Metric | Formula | Example (pool=118) |
|---|---|---|
| Production-ready pool | Check 2 count | 118 |
| Report-ready estimate | pool * 0.30 | 35 |
| Months of coverage | report_ready / 5 | 7 |
| Annual need | 5/report * 12 | 60 |

---

## Verdict Thresholds

Apply to **Check 2 production-filtered count** (the primary signal):

| Verdict | Check 2 Pool | Report-Ready (30%) | Sustainability | Action |
|---|---|---|---|---|
| **GO** | 50+ | 15+ | 12+ months | Proceed with onboarding |
| **CONDITIONAL** | 20-49 | 6-14 | 4-9 months | Onboard with caveats (see guidance) |
| **NO GO** | < 20 | < 6 | < 4 months | Decline or pilot only |

### Decision Matrix (when Check 1 and Check 2 conflict)

Check 2 is the primary signal. Check 1 provides context only.

| Check 1 (Cohort) | Check 2 (Siblings) | Verdict | Note |
|---|---|---|---|
| 50+ | 50+ | **GO** | Strong on both signals |
| 50+ | 20-49 | **CONDITIONAL** | Broad pool exists but production filters reduce it |
| 50+ | < 20 | **CONDITIONAL** | Investigate why sibling funders fail filters |
| 20-49 | 30+ | **CONDITIONAL** | State pool thin but sibling network compensates |
| < 20 | 50+ | **GO** | Sibling network overrides thin local pool |
| < 20 | < 20 | **NO GO** | Both signals weak |

---

## CONDITIONAL Prescriptive Guidance

When the verdict is CONDITIONAL, auto-select one of these templates based on the data pattern:

| Pattern | How to Detect | Guidance Template |
|---|---|---|
| Thin state, strong siblings | Check 1 < 30, Check 2 >= 20 | "State pool is thin ({check_1_adj}), but national funders from sibling network ({check_2_pool}) compensate. Recommend Foundation-Focused report format." |
| Thin sector, strong state | Check 1 >= 30, Check 2 20-35 | "Sector pool is niche, but {state} has a strong foundation base. Cross-sector funders are the opportunity." |
| Both thin | Check 1 < 30, Check 2 20-35 | "Both state and sector pools are thin. Recommend 3-month pilot before annual commitment." |
| Adequate pool, low quality | Check 2 >= 30, median_grant < 10000 | "Pool adequate ({check_2_pool}), but median grant ${median_grant}. Set expectations for $5K-$15K grants." |

If none match precisely, use the closest fit.

---

## Output Format

### Console Output

Print this directly in the conversation:

```
VERDICT: {GO | CONDITIONAL | NO GO}

Pool Size: {check_2_pool} production-ready foundations
  - Cohort pool (state+sector): {check_1_adj} (adjusted from {check_1_raw})
  - Sibling network pool: {check_2_pool} (from {peer_count} peer orgs)
  - Estimated report-ready: {report_ready} (~30% of production pool)

Top Foundations:
  1. {name} - ${median_grant} median grant, funds {peers_funded} peers
  2. {name} - ${median_grant} median grant, funds {peers_funded} peers
  3. {name} - ${median_grant} median grant, funds {peers_funded} peers

Summary: "{check_2_pool} production-ready foundations match {org_name}'s
profile ({sector_label} sector, {state}). {insight}. {caveat}.
Comparable foundations include {fdn_1}, {fdn_2}, and {fdn_3}."
```

### Report File

Also produce a short report (50-80 lines) saved as:

```
REPORT_YYYY-MM-DD.N_{org_name_snake}_viability.md
```

Location: same folder as the prompt, or `Enhancements/{date}/` if verbal instruction.

Report structure:

```markdown
# Viability Check: {Organization Name}

**Date:** YYYY-MM-DD
**Prompt:** Client viability check for {org_name}
**Status:** Complete
**Owner:** Aleck Kleinman

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | YYYY-MM-DD | Claude Code | Initial viability check |

---

## Verdict: {GO | CONDITIONAL | NO GO}

**{check_2_pool}** production-ready foundations match {org_name}'s profile
({sector_label} sector, {state}).

## Inputs

| Field | Value | Source |
|---|---|---|
| Organization | {name} | {user / dim_recipients / nonprofit_returns} |
| EIN | {ein or "Not provided"} | {source} |
| State | {state} | {source} |
| NTEE | {ntee_code} ({sector_label}) | {source} |
| Revenue | ${revenue} | {source} |
| Scope | {state/regional/national} | {source} |

## Check 1: Cohort Pool

- **Raw count:** {foundation_count} ({state} + {sector_label})
- **Adjusted (0.85x):** {adjusted}
- **Avg foundation giving:** ${avg_giving}
- **Cohort viable flag:** {yes/no}

## Check 2: Sibling Funder Network

- **Peers found:** {N} (fallback: {none/A/B})
- **Distinct foundations (unfiltered):** {N}
- **Production-ready (filtered):** {check_2_pool}
- **Median grant (top 3 avg):** ${N}

| # | Foundation | State | Median Grant | Peers Funded | Trend |
|---|---|---|---|---|---|
| 1 | {name} | {ST} | ${N} | {N} | {trend} |
| 2 | {name} | {ST} | ${N} | {N} | {trend} |
| 3 | {name} | {ST} | ${N} | {N} | {trend} |

## Check 3: Sustainability

- **Report-ready estimate:** {N} (30% of {check_2_pool})
- **Months of coverage:** {N} (at 5 foundations/report)
- **Annual need:** 60

## Summary

{The one-paragraph summary from console output.}

## Notes

{Any caveats: fallbacks used, data gaps, thin peer data, etc.}

---

*Generated by Claude Code on YYYY-MM-DD*
```

---

## Edge Cases

| Scenario | Handling |
|---|---|
| **National org** | Check 1: use national variant SQL (sector-wide, deduplicated). Check 2: drop state from peer search (go straight to Fallback B). |
| **Multi-sector org** | Use primary NTEE. Note in summary if secondary sector exists. |
| **US Territories** (VI, GU, PR, AS, MP) | Likely NO GO. Flag: "Territory-based orgs have limited foundation coverage in IRS data." |
| **No NTEE code** | Cannot run. Ask user to look up on Candid/GuideStar. |
| **Existing client** | Step 0 catches this. Stop immediately. |
| **EIN not in DB** | Step 0 returns nothing. All inputs from user. Note: "No IRS filing data found; inputs are user-provided." |
| **Zero peers** (all fallbacks exhausted) | NO GO with note: "No comparable organizations found in IRS grant data." |
| **< 5 peers** | Proceed with available data. Note: "Limited peer data ({N} orgs). Pool estimate may be less reliable." |
| **No EIN provided** | Skip Step 0 entirely. All inputs from user. Set target_ein = '0000000000' in Check 2A. |

---

## SQL Execution Strategy

1. Attempt all queries via **MCP postgres tool** first (fastest for single queries)
2. If ANY MCP query fails or returns an "aborted" error, switch ALL remaining queries to **psql via Bash**
3. Retain results from successful prior checks; do not re-execute them
4. **No SQL comments** (`--`) in MCP queries (triggers "Only SELECT" error)
5. All queries use deterministic `ORDER BY` with EIN tiebreaker
6. Use `<>` instead of `!=` in SQL (shell escaping issue with `!` in Bash/psql)

**psql fallback template:**
```bash
psql -h localhost -p 5432 -U postgres -d thegrantscout -t -A -F '|' -c "
{sql_query}
"
```

---

## Quality Checklist

Before delivering results:

- [ ] All 3 checks completed (or failures noted)
- [ ] Verdict matches threshold table (not manually overridden)
- [ ] Top 3 foundations have real names and non-null median grants
- [ ] Report-ready estimate uses 30% factor (not raw pool)
- [ ] Summary paragraph reads naturally and includes org name, sector, state
- [ ] CONDITIONAL verdicts include prescriptive guidance template
- [ ] Edge cases handled (national scope, fallbacks, thin data noted)
- [ ] Report file follows CLAUDE.md naming convention

---

## Future Enhancements

- **Screen mode:** Batch Check 1 only for rapid prospect list triage (no sibling analysis). Input: CSV of prospects. Output: GO/CONDITIONAL/NO GO column.
- **viability_assessments table:** Store all results in DB for historical tracking, sales pipeline analytics, and win/loss correlation.
- **Auto-trigger:** When a new row appears in dim_clients, auto-run viability check and flag if NO GO.

---

*Skill version 1.0 - Created 2026-02-20*
