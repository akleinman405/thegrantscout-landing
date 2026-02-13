# SOP: Report Review for Agent Teams

**Version:** 1.0
**Created:** 2026-02-06
**Purpose:** Systematic quality verification of grant opportunity reports before client delivery. Designed for execution by a team of 4 parallel agents with specific test suites and pass/fail gates.

---

## Table of Contents

1. [Overview & When to Use](#overview--when-to-use)
2. [Error Taxonomy](#error-taxonomy)
3. [Agent Team Architecture](#agent-team-architecture)
4. [Pre-Review Setup](#pre-review-setup)
5. [Gate 1: Data Integrity](#gate-1-data-integrity)
6. [Gate 2: Contact & Web Verification](#gate-2-contact--web-verification)
7. [Gate 3: Internal Consistency](#gate-3-internal-consistency)
8. [Gate 4: Client Fit](#gate-4-client-fit)
9. [Gate 5: Formatting & Completeness](#gate-5-formatting--completeness)
10. [Hard Gate Thresholds](#hard-gate-thresholds)
11. [Scoring System & Pass/Fail Matrix](#scoring-system--passfail-matrix)
12. [Error Resolution Workflow](#error-resolution-workflow)
13. [Review Report Template](#review-report-template)
14. [SQL Query Library](#sql-query-library)

---

## 1. Overview & When to Use

### When to Run This Review

Run the full review SOP before delivering ANY client-facing grant report. This includes:

- Monthly grant opportunity reports (the primary use case)
- Foundation-focused relationship-building reports
- Ad hoc grant research deliverables with foundation profiles

### What This SOP Catches

This SOP was developed after real errors in production reports:

| Error | Client | Impact | Gate That Catches It |
|-------|--------|--------|---------------------|
| Dollar amounts in priority table ("$1.4M" / "$50K") contradicted foundation profile ("$1.96M" / "$200K") | VetsBoats | Client sees conflicting numbers, loses trust | Gate 3: Internal Consistency |
| Grants attributed to client were actually to a different org with a similar name ("Center for Wooden Boats" WA, not VetsBoats CA) | VetsBoats pre-call brief | Wrong funder history presented; embarrassment in client meeting | Gate 1: Data Integrity |
| 4 of 5 opportunities were foundations client already knew | SNS | No discovery value — client said "only 1 of 5 was truly new" | Gate 4: Client Fit |

### Review Scope

The review covers:
- The markdown report file (`.md`)
- Supporting data files in the run folder (`DATA_*.csv`, checkpoint files)
- Database records for all EINs mentioned in the report
- Live web verification of contacts and links

---

## 2. Error Taxonomy

Every error found during review is classified by severity. Severity determines whether the report can ship.

### CRITICAL (Report cannot ship)

| Code | Error | Example |
|------|-------|---------|
| C-01 | Known funder included in report | SNS report included foundation client already has relationship with |
| C-02 | EIN does not exist in database | Typo in EIN, foundation not in our 143K records |
| C-03 | Foundation inactive 3+ years | Last grant in 2020 or earlier — possibly defunct |
| C-04 | Dollar amount contradiction within report | Barry priority table says "$50K" but profile section says "$200K" |
| C-05 | Grant attribution to wrong organization | Pre-call brief attributed JPMorgan grant to VetsBoats; actual recipient was Center for Wooden Boats (WA) |
| C-06 | Expired deadline presented as current | "Apply by March 2025" in a February 2026 report |

### HIGH (Must fix before delivery)

| Code | Error | Example |
|------|-------|---------|
| H-01 | No verified contact info for a foundation | Profile lists foundation but no email, phone, or contact name |
| H-02 | Geographic mismatch | Foundation only funds New England; client is in California |
| H-03 | Foundation restricts against client's org type | "Public charities only" but client is a private foundation |
| H-04 | Broken or invalid URL | Application link returns 404 |
| H-05 | Grant amounts don't match database | Report says "$80,000 grant" but DB shows $8,000 |

### MEDIUM (Fix if time permits)

| Code | Error | Example |
|------|-------|---------|
| M-01 | Inconsistent formatting of dollar amounts | Mix of "$50K" and "$50,000" styles |
| M-02 | Missing section from report template | No "Potential Connections" table for a foundation |
| M-03 | Fit score not justified by evidence | Score 8/10 but fit evidence is thin |
| M-04 | Vague positioning strategy | "Apply for a grant" instead of specific approach |

### LOW (Note for future improvement)

| Code | Error | Example |
|------|-------|---------|
| L-01 | Spelling or grammar error | "Fundation" instead of "Foundation" |
| L-02 | Inconsistent capitalization | "loi" vs "LOI" |
| L-03 | Redundant information across sections | Same sentence appears in "Why This Foundation" and "Positioning Strategy" |

---

## 3. Agent Team Architecture

### Team Composition

| Agent | Name | Gate(s) | Tools Required | Runs When |
|-------|------|---------|----------------|-----------|
| Agent 1 | Data Integrity | Gate 1 | Database (SQL), file reader | Parallel — immediately |
| Agent 2 | Contact & Web | Gate 2 | Web fetch, DNS lookup | Parallel — immediately |
| Agent 3 | Client Fit | Gate 4 | Database (SQL), client profile | Parallel — immediately |
| Agent 4 | Consistency & Format | Gates 3 + 5 | Text parsing, report template | Sequential — after Agents 1-3 complete |

### Execution Flow

```
┌─────────────────────────────────────────────────┐
│              PRE-REVIEW SETUP                    │
│  Extract EINs, load client profile, verify DB   │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ Agent 1  │ │ Agent 2  │ │ Agent 3  │
   │ Data     │ │ Contact  │ │ Client   │
   │ Integrity│ │ & Web    │ │ Fit      │
   │ Gate 1   │ │ Gate 2   │ │ Gate 4   │
   └────┬─────┘ └────┬─────┘ └────┬─────┘
        │             │            │
        └─────────────┼────────────┘
                      ▼
              ┌──────────────┐
              │   Agent 4    │
              │ Consistency  │
              │ & Format     │
              │ Gates 3 + 5  │
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │   SCORING    │
              │  & VERDICT   │
              └──────────────┘
```

**Why Agent 4 runs last:** Gate 3 (Internal Consistency) cross-references facts verified by Agents 1 and 3. It needs to know which dollar amounts are correct (from DB) before it can flag contradictions within the report text.

---

## 4. Pre-Review Setup

Before any agent begins, the coordinating process must prepare the review context.

### 4.1 Required Inputs

| Input | Source | Example |
|-------|--------|---------|
| Report file path | Run folder | `5. Runs/VetsBoats/2026-02-06/REPORT_2026-02-06_vetsboats_grant_report.md` |
| Client name/ID | dim_clients | `VetsBoats` / ID 8 |
| Run folder path | Convention | `5. Runs/VetsBoats/2026-02-06/` |

### 4.2 Extract Foundation EINs

Parse the report to extract all foundation EINs mentioned. If EINs are not in the report text, look them up by foundation name:

```sql
SELECT ein, name
FROM f990_2025.dim_foundations
WHERE name ILIKE '%foundation_name%';
```

Store the EIN list — every subsequent agent needs it.

### 4.3 Load Client Profile

```sql
SELECT name, ein, state, sector_ntee, known_funders, matching_grant_keywords,
       budget_min, budget_max, grant_size_min, grant_size_max,
       geographic_scope, org_type, project_type
FROM f990_2025.dim_clients
WHERE name ILIKE '%client_name%';
```

### 4.4 Verify Database Connectivity

Run a simple test query before launching agents:

```sql
SELECT COUNT(*) FROM f990_2025.dim_foundations;
```

Expected: ~143,184. If this fails, agents cannot run Gates 1 or 4.

---

## 5. Gate 1: Data Integrity

**Agent:** Agent 1 (Data Integrity)
**Tools:** Database SQL queries
**Tests:** 10

Verifies that every factual claim in the report is backed by database records.

### Test DI-01: All EINs Exist in Database

**Severity:** CRITICAL (C-02)
**Pass criteria:** Every foundation EIN in the report returns a row from `dim_foundations`.

```sql
SELECT ein, name FROM f990_2025.dim_foundations
WHERE ein IN ('EIN1', 'EIN2', ...);
```

**Pass:** Row count = number of EINs in report.
**Fail:** Any EIN missing → CRITICAL error C-02.

### Test DI-02: All Foundations Active Within 3 Years

**Severity:** CRITICAL (C-03)
**Pass criteria:** Every foundation has at least one grant with `tax_year >= 2022` (for a 2026 report).

```sql
SELECT foundation_ein, MAX(tax_year) as last_active_year
FROM f990_2025.fact_grants
WHERE foundation_ein IN ('EIN1', 'EIN2', ...)
GROUP BY foundation_ein;
```

**Pass:** All `last_active_year >= 2022`.
**Fail:** Any foundation with `last_active_year < 2022` → CRITICAL error C-03.

### Test DI-03: Grant Amounts Match Database

**Severity:** HIGH (H-05) or CRITICAL (C-05)
**Pass criteria:** Every specific grant amount cited in the report (e.g., "gave $80,000 to CRAB") matches a record in `fact_grants` within 5% tolerance.

For each cited grant, query:

```sql
SELECT recipient_name_raw, amount, tax_year, purpose_text
FROM f990_2025.fact_grants
WHERE foundation_ein = 'FOUNDATION_EIN'
  AND amount BETWEEN CITED_AMOUNT * 0.95 AND CITED_AMOUNT * 1.05
ORDER BY tax_year DESC;
```

**Pass:** Matching record found for each cited grant.
**Fail — HIGH (H-05):** Amount exists but differs by >5% (e.g., report says $80K, DB says $75K).
**Fail — CRITICAL (C-05):** No matching grant exists at all — possible attribution to wrong org.

> **Real example:** VetsBoats pre-call brief attributed a Goodfellow Fund grant to VetsBoats. The actual recipient was "Center for Wooden Boats" in Washington state — a completely different organization. Always verify `recipient_name_raw` contains the CLIENT's name or known aliases.

### Test DI-04: Grant Recipients Match Client (Not Lookalikes)

**Severity:** CRITICAL (C-05)
**Pass criteria:** When the report says "Foundation X gave $Y to [Client]", the `recipient_name_raw` in the database actually refers to the client, not a similarly-named organization.

```sql
SELECT recipient_name_raw, recipient_state, recipient_ein, amount, tax_year
FROM f990_2025.fact_grants
WHERE foundation_ein = 'FOUNDATION_EIN'
  AND (recipient_name_raw ILIKE '%client_name%' OR recipient_ein = 'CLIENT_EIN')
ORDER BY tax_year DESC;
```

**Pass:** `recipient_state` matches client's state AND `recipient_name_raw` is unambiguous match.
**Fail:** Different state or name is a different org (e.g., "Center for Wooden Boats" WA vs "VetsBoats" CA) → CRITICAL error C-05.

### Test DI-05: Foundation Assets Match Database

**Severity:** HIGH (H-05)
**Pass criteria:** Asset figures cited in the report (e.g., "$477M assets") match the most recent `total_assets_eoy_amt` from `pf_returns` within 10% tolerance.

```sql
SELECT ein, total_assets_eoy_amt, tax_year
FROM f990_2025.pf_returns
WHERE ein = 'FOUNDATION_EIN'
ORDER BY tax_year DESC
LIMIT 1;
```

**Pass:** Reported figure within 10% of DB value.
**Fail:** Discrepancy >10% → HIGH error H-05.

### Test DI-06: Annual Giving Figures Match Database

**Severity:** HIGH (H-05)
**Pass criteria:** "Annual giving" or "total giving" figures in Funder Snapshot match aggregated `fact_grants`.

```sql
SELECT SUM(amount) as total_giving, COUNT(*) as grant_count
FROM f990_2025.fact_grants
WHERE foundation_ein = 'FOUNDATION_EIN'
  AND tax_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 1;
```

**Pass:** Within 15% of reported figure (some rounding acceptable).
**Fail:** Discrepancy >15% → HIGH error H-05.

### Test DI-07: Median/Typical Grant Matches Database

**Severity:** MEDIUM (M-03)
**Pass criteria:** "Typical grant" or "median grant" figures match `calc_foundation_profiles.median_grant`.

```sql
SELECT median_grant, avg_grant, grant_range_min, grant_range_max
FROM f990_2025.calc_foundation_profiles
WHERE ein = 'FOUNDATION_EIN';
```

**Pass:** Within 20% of `median_grant`.
**Fail:** Discrepancy >20% → MEDIUM error M-03.

### Test DI-08: Geographic Focus Matches Database

**Severity:** MEDIUM (M-03)
**Pass criteria:** Geographic focus percentage in Funder Snapshot (e.g., "85% Rhode Island") aligns with `calc_foundation_profiles.geographic_focus`.

```sql
SELECT geographic_focus
FROM f990_2025.calc_foundation_profiles
WHERE ein = 'FOUNDATION_EIN';
```

**Pass:** Reported state % within 10 percentage points of calculated value.
**Fail:** Discrepancy >10pp → MEDIUM error M-03.

### Test DI-09: Repeat Funding Rate Matches Database

**Severity:** MEDIUM (M-03)
**Pass criteria:** Repeat funding rate in Funder Snapshot matches `calc_foundation_profiles.repeat_rate`.

```sql
SELECT repeat_rate
FROM f990_2025.calc_foundation_profiles
WHERE ein = 'FOUNDATION_EIN';
```

**Pass:** Within 5 percentage points.
**Fail:** Discrepancy >5pp → MEDIUM error M-03.

### Test DI-10: Giving Trend Direction Matches Database

**Severity:** MEDIUM (M-03)
**Pass criteria:** "Growing/Stable/Declining" label matches `calc_foundation_profiles.giving_trend`.

```sql
SELECT giving_trend, trend_pct_change
FROM f990_2025.calc_foundation_profiles
WHERE ein = 'FOUNDATION_EIN';
```

**Pass:** Direction matches (Growing/Stable/Declining).
**Fail:** Direction contradicts → MEDIUM error M-03.

---

## 6. Gate 2: Contact & Web Verification

**Agent:** Agent 2 (Contact & Web)
**Tools:** Web fetch, DNS lookup, email pattern validation
**Tests:** 8

Verifies that contact information and web links are valid and current.

### Test CW-01: Foundation Websites Resolve

**Severity:** HIGH (H-04)
**Pass criteria:** Every foundation URL in the report returns HTTP 200 (or 301/302 redirect to a live page).

Fetch each URL. Record status code.

**Pass:** 2xx or 3xx status.
**Fail:** 4xx or 5xx → HIGH error H-04. Note: also flag if domain is parked or for sale.

### Test CW-02: Application URLs Resolve

**Severity:** HIGH (H-04)
**Pass criteria:** Every application/guidelines URL returns a live page with grant-related content.

Fetch each application URL. Verify page contains grant-related terms ("apply", "guidelines", "proposal", "LOI", "letter of inquiry").

**Pass:** Live page with grant content.
**Fail:** Dead link or irrelevant page → HIGH error H-04.

### Test CW-03: Email Addresses Have Valid Format

**Severity:** HIGH (H-01)
**Pass criteria:** Every email address matches standard format: `name@domain.tld`.

Validate regex pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

**Pass:** Valid format.
**Fail:** Invalid format → HIGH error H-01.

### Test CW-04: Email Domains Have MX Records

**Severity:** HIGH (H-01)
**Pass criteria:** The domain of each email address has valid MX records (can receive email).

For each email domain, check DNS MX records.

**Pass:** MX records exist.
**Fail:** No MX records (domain can't receive email) → HIGH error H-01.

### Test CW-05: Phone Numbers Have Valid Format

**Severity:** MEDIUM (M-02)
**Pass criteria:** Phone numbers are formatted consistently and have 10+ digits.

**Pass:** Valid US phone format with area code.
**Fail:** Missing area code, wrong digit count → MEDIUM error M-02.

### Test CW-06: Contact Names Appear on Foundation Website

**Severity:** MEDIUM (M-02)
**Pass criteria:** Named contacts can be found on the foundation's website (staff page, about page, or team page).

Fetch the foundation's staff/team page. Search for contact name.

**Pass:** Name found on website.
**Fail:** Name not found → MEDIUM error M-02. May indicate outdated contact or wrong person.

### Test CW-07: Deadline Dates Are in the Future

**Severity:** CRITICAL (C-06)
**Pass criteria:** Every deadline date mentioned in the report is AFTER the report date.

Parse all date mentions in deadline fields. Compare to report date.

**Pass:** All deadlines are future dates (or "rolling"/"ongoing").
**Fail:** Any past deadline → CRITICAL error C-06.

### Test CW-08: Foundation Website Content Matches Report Claims

**Severity:** HIGH (H-02)
**Pass criteria:** Key claims about application process (e.g., "accepts LOIs", "invite only", "application window Jan-Apr") are confirmed by the foundation's website.

Fetch the foundation's grants/guidelines page. Verify:
- Application type matches report
- Geographic restrictions match report
- Program priorities match report

**Pass:** Website confirms report claims.
**Fail:** Website contradicts report → HIGH error H-02 or H-03.

---

## 7. Gate 3: Internal Consistency

**Agent:** Agent 4 (Consistency & Format) — runs AFTER Agents 1-3
**Tools:** Text parsing, cross-reference against Agent 1 & 3 results
**Tests:** 9

Verifies that the report is internally consistent — numbers, names, and claims don't contradict each other across sections.

### Test IC-01: Priority Table Amounts Match Foundation Profiles

**Severity:** CRITICAL (C-04)
**Pass criteria:** Dollar amounts in the priority table (Section: "This Month's Focus") match the corresponding foundation profile sections.

Parse the priority table for each foundation's dollar references. Parse each foundation profile for the same metrics. Compare.

**Pass:** All amounts match or are clearly different metrics (e.g., "typical grant" vs "total giving").
**Fail:** Same metric reported differently → CRITICAL error C-04.

> **Real example:** VetsBoats report priority table for Barry Foundation said "$1.4M veteran grants + $50K Sail to Prevail." The actual profile section documented "$1.96M veteran grants" and "Sail to Prevail $200K." The priority table had stale or rounded numbers that contradicted the detailed profile.

### Test IC-02: "At a Glance" Table Matches Profiles

**Severity:** CRITICAL (C-04)
**Pass criteria:** The "Top 5 Foundations at a Glance" table's Typical Grant ranges match what appears in each foundation's Funder Snapshot.

Parse the At a Glance table. Parse each Funder Snapshot. Compare grant ranges.

**Pass:** Ranges are identical or one is a subset of the other.
**Fail:** Contradictory ranges → CRITICAL error C-04.

### Test IC-03: Foundation Names Are Consistent Throughout

**Severity:** LOW (L-01)
**Pass criteria:** Each foundation is referred to by the same name in every section. No partial names, abbreviations, or misspellings that differ across sections.

Collect all name references per foundation. Compare for consistency.

**Pass:** Same name used everywhere (abbreviations OK if introduced).
**Fail:** Inconsistent names → LOW error L-01.

### Test IC-04: Fit Scores Match Fit Evidence

**Severity:** MEDIUM (M-03)
**Pass criteria:** Foundations with higher fit scores have demonstrably stronger fit evidence than those with lower scores.

For each foundation, count: matching grants found, geographic alignment, sector alignment, org size alignment. Verify scores reflect this evidence.

**Pass:** Higher-scored foundations have more/stronger evidence.
**Fail:** High score with weak evidence or low score with strong evidence → MEDIUM error M-03.

### Test IC-05: Contact Info Is Consistent Across Sections

**Severity:** MEDIUM (M-02)
**Pass criteria:** Contact names, emails, and phones that appear in both the foundation profile AND the Quick Reference section are identical.

Parse contacts from each foundation profile's Contacts table. Parse the Quick Reference "All Contacts" table. Compare.

**Pass:** All matching.
**Fail:** Discrepancy → MEDIUM error M-02.

### Test IC-06: Foundation Types Are Consistent

**Severity:** MEDIUM (M-02)
**Pass criteria:** The foundation type (LOI-Ready, Open Application, Cultivation, etc.) is the same in the priority table, At a Glance table, and the profile header.

Parse type from each location. Compare per foundation.

**Pass:** Identical across all mentions.
**Fail:** Different types for same foundation → MEDIUM error M-02.

### Test IC-07: Action Steps Reference Correct Foundation Numbers

**Severity:** MEDIUM (M-02)
**Pass criteria:** Cross-references like "Barry #4 Step 2" or "shared with Barry Foundation (#4)" point to the correct rank number.

Parse all `#N` references. Verify they match the actual ranking in the priority table.

**Pass:** All cross-references are correct.
**Fail:** Wrong number → MEDIUM error M-02.

### Test IC-08: Time Estimates Sum Correctly

**Severity:** LOW (L-03)
**Pass criteria:** Per-foundation time estimates in the priority table sum to match the "Total This Month" figure in the Monthly Action Plan.

Sum time from priority table. Compare to stated total.

**Pass:** Within 1 hour of stated total.
**Fail:** Discrepancy >1 hour → LOW error L-03.

### Test IC-09: Week-by-Week Plan Covers All 5 Foundations

**Severity:** MEDIUM (M-02)
**Pass criteria:** Every foundation in the Top 5 appears at least once in the week-by-week breakdown.

Parse the weekly plan table. Check each foundation is mentioned.

**Pass:** All 5 present.
**Fail:** Missing foundation → MEDIUM error M-02.

---

## 8. Gate 4: Client Fit

**Agent:** Agent 3 (Client Fit)
**Tools:** Database SQL, client profile from dim_clients
**Tests:** 7

Verifies that every foundation in the report is appropriate for THIS specific client.

### Test CF-01: No Known Funders in Report

**Severity:** CRITICAL (C-01)
**Pass criteria:** None of the report's foundation EINs appear in the client's `known_funders` array.

```sql
SELECT known_funders
FROM f990_2025.dim_clients
WHERE name ILIKE '%client_name%';
```

Compare each report EIN against the `known_funders` array.

**Pass:** Zero overlap.
**Fail:** Any match → CRITICAL error C-01.

> **Real example:** SNS beta feedback: "Only 1 of 5 was truly new to her." Four foundations were already known to the client. This is the #1 value-destroyer for our reports.

### Test CF-02: Foundations Fund Client's Geographic Area

**Severity:** HIGH (H-02)
**Pass criteria:** Every foundation has granted to organizations in the client's state within the last 5 years.

```sql
SELECT foundation_ein, COUNT(*) as grants_in_state
FROM f990_2025.fact_grants
WHERE foundation_ein IN ('EIN1', 'EIN2', ...)
  AND recipient_state = 'CLIENT_STATE'
  AND tax_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 5
GROUP BY foundation_ein;
```

**Pass:** Each foundation has >=1 grant in client's state.
**Fail:** Zero grants in client's state → HIGH error H-02. Exception: national foundations with explicit "we fund nationally" on website.

### Test CF-03: Foundations Fund Client's Sector

**Severity:** HIGH (H-02)
**Pass criteria:** Every foundation has made grants with purpose text matching the client's sector keywords.

```sql
SELECT foundation_ein, COUNT(*) as matching_grants
FROM f990_2025.fact_grants
WHERE foundation_ein IN ('EIN1', 'EIN2', ...)
  AND purpose_text ILIKE ANY(
    SELECT UNNEST(matching_grant_keywords)
    FROM f990_2025.dim_clients WHERE name ILIKE '%client_name%'
  )
GROUP BY foundation_ein;
```

**Pass:** Each foundation has >=1 matching grant.
**Fail:** Zero matching grants → HIGH error H-02. Note: may still be valid if foundation's website shows sector alignment — flag for manual review.

### Test CF-04: Grant Sizes Appropriate for Client

**Severity:** MEDIUM (M-03)
**Pass criteria:** Each foundation's median grant is within a reasonable range for the client's grant size target.

```sql
SELECT cfp.ein, cfp.median_grant, dc.grant_size_min, dc.grant_size_max
FROM f990_2025.calc_foundation_profiles cfp
CROSS JOIN f990_2025.dim_clients dc
WHERE dc.name ILIKE '%client_name%'
  AND cfp.ein IN ('EIN1', 'EIN2', ...);
```

**Pass:** Foundation's `median_grant` is between 0.25x and 4x the client's `grant_size_min` to `grant_size_max` range.
**Fail:** Median grant wildly outside client's range → MEDIUM error M-03.

### Test CF-05: No Org-Type Restrictions Against Client

**Severity:** HIGH (H-03)
**Pass criteria:** No foundation in the report has stated restrictions that exclude the client's organization type.

This test uses web research results from Agent 2 (Gate 2, Test CW-08). For clients classified as private foundations (like VetsBoats), check whether foundation guidelines say "public charities only" or "no private foundations."

**Pass:** No exclusionary restrictions found, OR foundation has demonstrated grants to client's org type.
**Fail:** Explicit restriction against client's org type → HIGH error H-03.

### Test CF-06: Client's Primary Priority Addressed

**Severity:** HIGH (H-02)
**Pass criteria:** At least 3 of 5 foundations have grants matching the client's primary funding priority.

Review each foundation's fit evidence. Count how many address the primary priority stated in `dim_clients.project_need_text` or `target_grant_purpose`.

**Pass:** >=3 of 5 foundations align with primary priority.
**Fail:** <3 → HIGH error H-02.

### Test CF-07: Cultivation Foundations Have Clear Path

**Severity:** MEDIUM (M-04)
**Pass criteria:** Every foundation marked as "Cultivation" type has a specific, named connection path (not just "build relationship").

Parse the "How to Approach" section for each Cultivation foundation. Check for:
- A named person or organization as the connection
- A specific action (not generic "network" or "attend events")

**Pass:** Each Cultivation foundation has a named intermediary or specific connection path.
**Fail:** Vague cultivation path → MEDIUM error M-04.

---

## 9. Gate 5: Formatting & Completeness

**Agent:** Agent 4 (Consistency & Format) — runs alongside Gate 3
**Tools:** Text parsing, template comparison
**Tests:** 10

Verifies that the report follows the template structure and formatting standards.

### Test FC-01: All Template Sections Present

**Severity:** MEDIUM (M-02)
**Pass criteria:** Report contains all required top-level sections from the template.

Required sections (from `TEMPLATE_2026-02-02_monthly_grant_report.md`):
1. Title + metadata (Report Date, Report Period, Foundations Profiled, Total Potential Funding)
2. Table of Contents
3. "If You Only Have 5 Hours This Month"
4. "This Month's Focus" (priority table + time allocation)
5. "Foundation Types Explained"
6. "Top 5 Foundations at a Glance"
7. "Foundation Profiles" (5 profiles)
8. "Monthly Action Plan" (week-by-week + waiting + dependencies)
9. "Quick Reference" (all contacts + application summary + time summary)

**Pass:** All 9 sections present.
**Fail:** Missing section → MEDIUM error M-02.

### Test FC-02: Each Foundation Profile Has Required Subsections

**Severity:** MEDIUM (M-02)
**Pass criteria:** Each of the 5 foundation profiles contains all required subsections.

Required per profile:
- Type + Time Investment + Potential Award header
- "Why This Foundation"
- "Fit Evidence" table
- "Funder Snapshot" table
- Application/approach section (varies by type)
- "Contacts" table
- "Potential Connections" table
- "Positioning Strategy"
- "Action Steps" table

**Pass:** All subsections present for each foundation.
**Fail:** Missing subsection → MEDIUM error M-02. Note which foundation and which subsection.

### Test FC-03: Dollar Amounts Formatted Consistently

**Severity:** MEDIUM (M-01)
**Pass criteria:** All dollar amounts use the same format convention throughout the report.

Acceptable formats:
- Full: `$25,000` / `$1,960,000`
- Abbreviated: `$25K` / `$1.96M`
- Range: `$25,000 - $100,000` or `$25K-$100K`

**Pass:** One consistent format used (or clear pattern: abbreviated in tables, full in prose).
**Fail:** Inconsistent mixing without pattern → MEDIUM error M-01.

### Test FC-04: Exactly 5 Foundation Profiles

**Severity:** MEDIUM (M-02)
**Pass criteria:** Report contains exactly 5 numbered foundation profiles.

Count `### #N:` headers.

**Pass:** Exactly 5.
**Fail:** More or fewer → MEDIUM error M-02.

### Test FC-05: Page Breaks Between Sections

**Severity:** LOW (L-03)
**Pass criteria:** `<!-- PAGE_BREAK -->` markers appear between major sections (for Word conversion).

**Pass:** Page breaks present between each major section.
**Fail:** Missing page breaks → LOW error L-03.

### Test FC-06: Fit Scores Present and Within Range

**Severity:** MEDIUM (M-02)
**Pass criteria:** Every foundation in the At a Glance table has a fit score between 1/10 and 10/10.

**Pass:** All scores present and in range.
**Fail:** Missing score or out of range → MEDIUM error M-02.

### Test FC-07: Time Estimates Present for All Foundations

**Severity:** MEDIUM (M-02)
**Pass criteria:** Every foundation has a time estimate in the priority table and in its Action Steps section.

**Pass:** Time estimates present in both locations for all 5.
**Fail:** Missing time estimate → MEDIUM error M-02.

### Test FC-08: Quick Reference Tables Complete

**Severity:** MEDIUM (M-02)
**Pass criteria:** Quick Reference section contains all three tables: All Contacts, Application Summary, and Time Summary — each with an entry for all 5 foundations.

**Pass:** All three tables present, each with 5 entries.
**Fail:** Missing table or incomplete entries → MEDIUM error M-02.

### Test FC-09: No Placeholder Text Remaining

**Severity:** HIGH (H-01)
**Pass criteria:** Report contains no template placeholder text (brackets like `[Foundation Name]`, `[X hours]`, `[Type]`).

Search for patterns: `\[.*?\]` that look like unfilled placeholders (exclude legitimate markdown links).

**Pass:** No placeholder text found.
**Fail:** Placeholder text remaining → HIGH error H-01.

### Test FC-10: Data Sources Section Present

**Severity:** LOW (L-03)
**Pass criteria:** Report ends with a Data Sources section citing IRS 990-PF filings and other sources used.

**Pass:** Data Sources section present.
**Fail:** Missing → LOW error L-03.

---

## 10. Hard Gate Thresholds

These are absolute minimums. If ANY hard gate fails, the report **cannot ship** regardless of overall score.

| Hard Gate | Threshold | Rationale |
|-----------|-----------|-----------|
| Known funders in report | **0** | #1 value-destroyer. Client already knows these foundations. |
| Expired deadlines | **0** | Unprofessional; wastes client time. |
| Invalid EINs | **0** | Foundation doesn't exist; cannot be researched. |
| Inactive foundations (3+ years) | **0** | Possibly defunct; client can't apply. |
| Dollar amount contradictions within report | **0** | Destroys credibility; client sees conflicting numbers. |
| Grant misattributions (wrong org) | **0** | Embarrassing; shows we didn't verify our data. |
| Verified contact emails | **>= 3** | Client needs actionable contacts for at least 3 of 5 foundations. |
| Verified contact phones | **>= 3** | Alternative contact channel for at least 3 foundations. |
| Verified contact names | **>= 3** | Personalization for outreach. |
| Foundations with geographic match | **5 of 5** | Every foundation must plausibly fund client's area. |

---

## 11. Scoring System & Pass/Fail Matrix

### Weighted Composite Score

| Gate | Weight | Max Points | What It Measures |
|------|--------|------------|------------------|
| Gate 1: Data Integrity | 35% | 35 | Facts match the database |
| Gate 2: Contact & Web | 25% | 25 | Links work, contacts are real |
| Gate 3: Internal Consistency | 20% | 20 | Report doesn't contradict itself |
| Gate 4: Client Fit | 15% | 15 | Foundations match THIS client |
| Gate 5: Formatting & Completeness | 5% | 5 | Follows template, no placeholders |
| **Total** | **100%** | **100** | |

### Per-Gate Scoring

Within each gate, the score is calculated as:

```
Gate Score = (Tests Passed / Total Tests) × Gate Max Points
```

Severity-based deductions apply when a test fails:
- **CRITICAL failure:** That test contributes 0 points AND triggers hard gate check
- **HIGH failure:** That test contributes 0 points
- **MEDIUM failure:** That test contributes 50% of its points
- **LOW failure:** That test contributes 75% of its points

### Pass/Fail Verdicts

| Verdict | Criteria | Action |
|---------|----------|--------|
| **PASS** | Score >= 90 AND 0 CRITICAL errors | Ship the report |
| **PASS WITH NOTES** | Score >= 80 AND 0 CRITICAL errors AND <= 2 HIGH errors | Fix HIGH errors, then ship |
| **REVISE** | Score >= 60 OR any HIGH errors > 2 | Fix errors, re-run review |
| **FAIL** | Score < 60 OR any CRITICAL error | Major rework required |

**Absolute rule:** Any CRITICAL error = automatic FAIL regardless of score.

---

## 12. Error Resolution Workflow

When errors are found, resolve them in this priority order:

### Step 1: Fix All CRITICAL Errors

CRITICAL errors must be fixed before any other work. Resolution approach by error code:

| Code | Resolution |
|------|------------|
| C-01 (known funder) | Remove foundation from report. Replace with next-best-scored foundation from pipeline. Re-run full review on replacement. |
| C-02 (invalid EIN) | Look up correct EIN. If foundation doesn't exist in DB, replace with different foundation. |
| C-03 (inactive foundation) | Replace with active foundation from pipeline. |
| C-04 (dollar contradiction) | Identify correct value from database (Gate 1 results). Update ALL mentions in report to match. |
| C-05 (wrong org attribution) | Remove the misattributed grant. Find correct grants from database. If no valid grants exist for this foundation-client pair, consider replacing the foundation. |
| C-06 (expired deadline) | Update to current deadline from foundation website. If no current deadline, change foundation type to "Rolling" or note "check website for current dates." |

### Step 2: Fix All HIGH Errors

| Code | Resolution |
|------|------------|
| H-01 (no contact info) | Research foundation website for contacts. If truly unavailable, note "Contact via general inquiry" with foundation's main phone/email. |
| H-02 (geographic mismatch) | Verify on foundation website. If confirmed mismatch, replace foundation. If website shows broader scope, add evidence to report. |
| H-03 (org type restriction) | Verify restriction. If confirmed, replace foundation. If ambiguous, add advisory note (like the VetsBoats private foundation advisory). |
| H-04 (broken URL) | Find current URL. If site is down, remove URL and note "website temporarily unavailable." |
| H-05 (amount mismatch) | Correct to database value. Update all sections that reference this amount. |

### Step 3: Fix MEDIUM Errors (If Time Permits)

Address in order of visibility to client. Formatting inconsistencies in the priority table and At a Glance sections are highest priority since clients see those first.

### Step 4: Re-Run Review

After fixing CRITICAL and HIGH errors, re-run the full review. Do NOT ship until the report achieves PASS or PASS WITH NOTES.

---

## 13. Review Report Template

After completing all gates, produce a review report in this format:

```markdown
# Report Review: [Client Name] [Report Date]

**Review Date:** YYYY-MM-DD
**Reviewer:** Agent Team
**Report File:** [path to report]
**Verdict:** PASS | PASS WITH NOTES | REVISE | FAIL

---

## Score Summary

| Gate | Score | Max | Tests Passed | Tests Failed |
|------|-------|-----|--------------|--------------|
| Gate 1: Data Integrity | XX | 35 | X/10 | X |
| Gate 2: Contact & Web | XX | 25 | X/8 | X |
| Gate 3: Internal Consistency | XX | 20 | X/9 | X |
| Gate 4: Client Fit | XX | 15 | X/7 | X |
| Gate 5: Formatting & Completeness | XX | 5 | X/10 | X |
| **TOTAL** | **XX** | **100** | **X/44** | **X** |

## Hard Gate Check

| Hard Gate | Result | Status |
|-----------|--------|--------|
| Known funders: 0 | [X found] | PASS/FAIL |
| Expired deadlines: 0 | [X found] | PASS/FAIL |
| Invalid EINs: 0 | [X found] | PASS/FAIL |
| Inactive foundations: 0 | [X found] | PASS/FAIL |
| Dollar contradictions: 0 | [X found] | PASS/FAIL |
| Grant misattributions: 0 | [X found] | PASS/FAIL |
| Verified emails >= 3 | [X verified] | PASS/FAIL |
| Verified phones >= 3 | [X verified] | PASS/FAIL |
| Verified contact names >= 3 | [X verified] | PASS/FAIL |
| Geographic match: 5/5 | [X/5 match] | PASS/FAIL |

## Errors Found

### CRITICAL
| Code | Test | Foundation | Details |
|------|------|------------|---------|
| C-XX | [Test ID] | [Foundation Name] | [Description] |

### HIGH
| Code | Test | Foundation | Details |
|------|------|------------|---------|
| H-XX | [Test ID] | [Foundation Name] | [Description] |

### MEDIUM
| Code | Test | Foundation | Details |
|------|------|------------|---------|

### LOW
| Code | Test | Foundation | Details |
|------|------|------------|---------|

## Recommendations

1. [Specific fix for each CRITICAL/HIGH error]
2. ...

---

*Review completed by Agent Team on YYYY-MM-DD*
```

---

## 14. SQL Query Library

Reusable parameterized queries for review agents. All queries use schema prefix `f990_2025.` and verified column names.

### Q1: Validate Foundation EINs Exist

```sql
SELECT ein, name, state, assets, last_return_year
FROM f990_2025.dim_foundations
WHERE ein IN ('{ein_1}', '{ein_2}', '{ein_3}', '{ein_4}', '{ein_5}');
```

**Expected:** 5 rows (one per foundation).

### Q2: Check Foundation Activity (Last Active Year)

```sql
SELECT foundation_ein,
       MAX(tax_year) AS last_active_year,
       COUNT(*) AS total_grants,
       SUM(amount) AS total_giving
FROM f990_2025.fact_grants
WHERE foundation_ein IN ('{ein_1}', '{ein_2}', '{ein_3}', '{ein_4}', '{ein_5}')
GROUP BY foundation_ein
ORDER BY last_active_year DESC;
```

**Expected:** All `last_active_year >= 2022`.

### Q3: Verify Specific Grant Amount

```sql
SELECT foundation_ein, recipient_name_raw, recipient_state, recipient_ein,
       amount, tax_year, purpose_text
FROM f990_2025.fact_grants
WHERE foundation_ein = '{foundation_ein}'
  AND amount BETWEEN {cited_amount} * 0.95 AND {cited_amount} * 1.05
ORDER BY tax_year DESC
LIMIT 10;
```

**Use:** For each specific grant amount cited in the report (e.g., "$80,000 to CRAB").

### Q4: Verify Grant Recipient Is Client (Not Lookalike)

```sql
SELECT foundation_ein, recipient_name_raw, recipient_state, recipient_ein,
       amount, tax_year, purpose_text
FROM f990_2025.fact_grants
WHERE foundation_ein = '{foundation_ein}'
  AND (
    recipient_name_raw ILIKE '%{client_name}%'
    OR recipient_ein = '{client_ein}'
  )
ORDER BY tax_year DESC;
```

**Use:** When report claims "Foundation X previously funded [Client]."

### Q5: Get Foundation Assets (Most Recent)

```sql
SELECT ein, business_name, total_assets_eoy_amt, tax_year
FROM f990_2025.pf_returns
WHERE ein = '{foundation_ein}'
ORDER BY tax_year DESC
LIMIT 1;
```

**Use:** Verify asset figures like "$477M assets."

### Q6: Get Foundation Profile Metrics

```sql
SELECT ein, median_grant, avg_grant, grant_range_min, grant_range_max,
       repeat_rate, geographic_focus, sector_focus, giving_trend,
       trend_pct_change, total_grants_5yr, total_giving_5yr,
       unique_recipients_5yr, last_active_year
FROM f990_2025.calc_foundation_profiles
WHERE ein = '{foundation_ein}';
```

**Use:** Verify Funder Snapshot metrics (median grant, repeat rate, geographic focus, giving trend).

### Q7: Get Client Known Funders

```sql
SELECT name, known_funders
FROM f990_2025.dim_clients
WHERE name ILIKE '%{client_name}%';
```

**Use:** Check report foundations against known funders list. Zero overlap required.

### Q8: Check Foundation Grants in Client's State

```sql
SELECT foundation_ein, COUNT(*) AS grants_in_state,
       SUM(amount) AS total_in_state
FROM f990_2025.fact_grants
WHERE foundation_ein IN ('{ein_1}', '{ein_2}', '{ein_3}', '{ein_4}', '{ein_5}')
  AND recipient_state = '{client_state}'
  AND tax_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 5
GROUP BY foundation_ein;
```

**Use:** Verify geographic match (Gate 4, Test CF-02).

### Q9: Check Foundation Grants Matching Client Keywords

```sql
SELECT foundation_ein, COUNT(*) AS matching_grants,
       SUM(amount) AS matching_total
FROM f990_2025.fact_grants
WHERE foundation_ein IN ('{ein_1}', '{ein_2}', '{ein_3}', '{ein_4}', '{ein_5}')
  AND purpose_text ILIKE ANY(ARRAY['{keyword_1}', '{keyword_2}', '{keyword_3}'])
GROUP BY foundation_ein;
```

**Use:** Verify sector match (Gate 4, Test CF-03). Keywords come from `dim_clients.matching_grant_keywords`.

### Q10: Get Annual Giving for a Foundation

```sql
SELECT tax_year, COUNT(*) AS grant_count, SUM(amount) AS annual_giving
FROM f990_2025.fact_grants
WHERE foundation_ein = '{foundation_ein}'
  AND tax_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 3
GROUP BY tax_year
ORDER BY tax_year DESC;
```

**Use:** Verify "Annual Giving" figures in Funder Snapshot.

### Q11: Get Full Client Profile for Review

```sql
SELECT name, ein, state, city, sector_ntee, sector_broad, org_type,
       budget_min, budget_max, grant_size_min, grant_size_max,
       mission_text, project_need_text, project_type,
       matching_grant_keywords, known_funders, geographic_scope,
       target_grant_purpose
FROM f990_2025.dim_clients
WHERE name ILIKE '%{client_name}%';
```

**Use:** Pre-review setup — load all client fields needed across Gates 1-4.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-06 | Initial version. 5 gates, 44 tests, 4-agent architecture. |

---

*SOP Version 1.0 — Created 2026-02-06*
*Developed from error analysis of VetsBoats (Feb 2026) and SNS (Beta Group 1) reports.*
