# PROMPT: VetsBoats Hard-Filtered Foundation Shortlist

**Date:** 2026-02-20
**Target:** Claude Code CLI
**Priority:** URGENT — output needed today for client delivery
**Scope:** Single query + CSV export. No schema changes, no migrations.

---

## Situation

We sent VetsBoats (EIN 273960435) a report on Feb 6 that included foundations with eligibility problems — some don't fund private foundations, some had wrong geography, some were preselected-only. We need to regenerate the shortlist with hard filters applied FIRST, so every foundation on the list is pre-vetted before Alec manually checks websites.

VetsBoats is a **private foundation** based in California. This is the #1 constraint — most foundations either explicitly exclude PFs or have never funded one. Only foundations with PROVEN PF-to-PF giving should make the list.

---

## Task

Produce three files:
1. **PRIMARY:** An HTML review file with clickable website links and visual filter badges — `REVIEW_2026-02-20_vetsboats_prospects.html`
2. A CSV with the full data — `DATA_2026-02-20_vetsboats_hardfiltered_prospects.csv`
3. A summary report with SQL used and funnel stats — `REPORT_2026-02-20_vetsboats_shortlist_summary.md`

Every foundation in the output must pass ALL THREE hard filters (near-misses in a separate section).

---

## The Three Hard Filters

Every foundation in the output must pass ALL of these:

### Filter 1: Open to Applicants
The foundation does NOT restrict to preselected grantees only.

```sql
-- Use the MOST RECENT filing per foundation
-- only_contri_to_preselected_ind = FALSE (or NULL) on their latest return
-- grants_to_organizations_ind = TRUE on their latest return
```

Use a window function or subquery to get each foundation's most recent pf_returns row. Don't just check one year — a foundation might have flipped this flag between filings.

### Filter 2: Geographic — Gives in California
The foundation has made at least 1 grant to a California recipient, OR is headquartered in CA and gives nationally.

Options (use whichever is most reliable given what's in the DB):
- Check `mv_foundation_geo_relevance` for CA relevance
- Check `stg_foundation_state_dist` for CA giving
- Check `fact_grants` for grants where recipient state = 'CA'
- Check `calc_foundation_profiles` or `dim_foundations` for state info

Pick the approach that casts a reasonable net (we'd rather include a few marginal ones than miss good ones — Alec will verify manually).

### Filter 3: Has Made PF-to-PF Grants
This is the critical filter. The foundation has given at least 1 grant to another private foundation (not just public charities).

```sql
-- Join fact_grants to dim_foundations (or pf_returns) on recipient_ein
-- Where the RECIPIENT is also a private foundation (exists in pf_returns or dim_foundations)
-- Count these grants per funder
```

If recipient_ein coverage is too low to make this reliable, also check:
- `pf_grants` where recipient name matches known PFs
- Any field in pf_returns that indicates PF-to-PF giving patterns

Document which method you used and what the coverage limitations are.

---

## Candidate Pool

Combine foundations from TWO sources:

### Source A: Existing Sibling Analysis (143 foundations)
```sql
SELECT DISTINCT foundation_ein 
FROM f990_2025.calc_client_foundation_scores 
WHERE client_ein = '273960435';
```

### Source B: Veteran Keyword Search (125 foundations from Prompt 4)
If these were stored in a table, pull from there. If not, reproduce the search:
```sql
-- Foundations with grants containing veteran-related keywords in purpose text
-- Keywords: veteran, military, armed forces, service member, wounded warrior, 
--           adaptive sailing, therapeutic sailing, adaptive recreation
```

### Source C: Any Additional Foundations
If the hard filters surface foundations that weren't in either pool (e.g., a CA-based PF-to-PF funder that also funds veteran orgs but wasn't in the sibling set), include them. The goal is completeness.

---

## Output Columns

For each foundation that passes all 3 filters, include:

| Column | Source | Purpose |
|--------|--------|---------|
| foundation_ein | dim_foundations or pf_returns | Identifier |
| foundation_name | pf_returns (latest) | For Alec's review |
| state | pf_returns (latest) | HQ state |
| website_url | pf_returns (latest) | For manual website check |
| total_assets | pf_returns (latest, total_assets_eoy_amt or fmv_assets_eoy_amt) | Size indicator |
| annual_giving | calc_foundation_profiles or pf_returns | Approximate annual giving |
| total_grants_made | Count from fact_grants | Volume |
| pf_to_pf_grant_count | Count of grants to PF recipients | Key filter metric |
| pf_to_pf_total_amount | Sum of grants to PF recipients | Scale of PF giving |
| ca_grant_count | Grants to CA recipients | Geographic relevance |
| veteran_grant_count | Grants with veteran keywords in purpose | Mission relevance |
| veteran_grant_amount | Sum of veteran-purpose grants | Scale of veteran giving |
| target_grant_count | From calc_client_foundation_scores if available | Sibling relevance |
| open_to_applicants | Boolean | Confirmed open |
| latest_tax_year | pf_returns | Data freshness |
| source | 'sibling' / 'keyword' / 'both' / 'new' | How we found them |
| known_funder | Boolean | TRUE if in VetsBoats' 5 known funders (EXCLUDE from final list but show for reference) |

Sort by: `pf_to_pf_grant_count DESC, veteran_grant_count DESC, ca_grant_count DESC`

---

## Known Funders to Flag (but don't exclude from CSV — just mark them)

| EIN | Name |
|-----|------|
| 680400024 | Tahoe Maritime Museum Foundation |
| 953059828 | Henry Mayo Newhall Foundation |
| 956054953 | Sidney Stern Memorial Trust |
| 841849498 | Charis Fund |
| 843805975 | Bonnell Cove Foundation |

---

## HTML Review File (PRIMARY OUTPUT)

Create an interactive HTML file: `5. Runs/VetsBoats/2026-02-20/REVIEW_2026-02-20_vetsboats_prospects.html`

This is what Alec will actually use to review foundations and click through to websites. Design it as a single self-contained HTML file (inline CSS/JS, no external dependencies).

### Requirements:

**Layout:** One card per foundation, stacked vertically. Cards should be scannable — Alec needs to quickly see the key facts and click to the website.

**Each card contains:**
- Foundation name (large, bold)
- Website URL as a **clickable link that opens in a new tab**
- EIN
- State, total assets, annual giving (one line)
- **Mission/activity description** from `pf_returns.mission_desc` or `activity_or_mission_desc` (whichever is populated). If both exist, show the longer one.
- Hard filter results as visual badges:
  - ✅ Open to Applicants / ❌ Preselected Only
  - ✅ Gives in CA (X grants) / ❌ No CA Grants
  - ✅ Funds PFs (X grants, $Y total) / ❌ No PF Grants
- Key stats: PF-to-PF grant count + amount, CA grant count, veteran grant count + amount, target grant count (if from sibling analysis)
- Source tag: `sibling` / `keyword` / `both` / `new`
- If known funder: a prominent ⚠️ KNOWN FUNDER banner

**Sections:**
1. **Passed All 3 Filters** — green left border on cards
2. **Near Misses (passed 2 of 3)** — yellow left border, with a label showing which filter failed
3. **Funnel summary** at the top: total pool → passed F1 → passed F1+F2 → passed all 3

**Styling:** Clean, readable. Light background. Cards with slight shadow. Monospace for EINs/numbers. Nothing fancy — this is a working tool, not a client deliverable.

**Sort order within each section:** `pf_to_pf_grant_count DESC, veteran_grant_count DESC, ca_grant_count DESC`

---

## Also Produce

### Summary Stats
At the top of the report or in a separate summary file:
- How many foundations were in the candidate pool (Source A + B + C)
- How many passed Filter 1 (open to applicants)
- How many passed Filter 2 (CA geography)
- How many passed Filter 3 (PF-to-PF grants)
- How many passed ALL THREE
- Funnel: pool → F1 → F1+F2 → F1+F2+F3

### Data Quality Notes
- What percentage of grants have recipient_ein populated (affects Filter 3 reliability)
- Were there foundations that ALMOST passed but failed one filter? (e.g., strong veteran alignment but no confirmed PF grants — Alec might want to manually check these)
- Any limitations or caveats about the filters

### Near-Miss List
A separate section or second CSV tab with foundations that passed 2 of 3 filters. Label which filter they failed. These are Alec's "maybe check the website anyway" list.

---

## Rules

1. READ-ONLY — do not modify any tables
2. Use the LATEST filing per foundation for open_to_applicants and other return-level fields
3. Output goes to `5. Runs/VetsBoats/2026-02-20/`
4. HTML review file is the PRIMARY output — make sure it works standalone (open in browser, all links clickable): `5. Runs/VetsBoats/2026-02-20/REVIEW_2026-02-20_vetsboats_prospects.html`
5. Also save CSV and summary report: `5. Runs/VetsBoats/2026-02-20/DATA_2026-02-20_vetsboats_hardfiltered_prospects.csv` and `5. Runs/VetsBoats/2026-02-20/REPORT_2026-02-20_vetsboats_shortlist_summary.md`
5. If any query takes >30 seconds, note it and optimize or sample
6. Show your work — include the exact SQL used in the summary report so we can verify the logic
