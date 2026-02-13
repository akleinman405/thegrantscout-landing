# SESSION STATE: VetsBoats First Report Build - 2026-02-06

**Last Updated:** 2026-02-06
**Purpose:** Preserve context across sessions for VetsBoats (Wooden Boats for Veterans) first monthly grant report
**Status:** In Progress — Checkpoint 4 next
**Plan File:** `5. Runs/VetsBoats/2026-02-06/PLAN_2026-02-06_vetsboats_report_build.md`
**Conversation Transcripts:** `/Users/aleckleinman/.claude/projects/-Users-aleckleinman-Documents-TheGrantScout/` (JSONL files — raw but complete)

---

## CURRENT STATUS - WHERE WE ARE

### Current Step
**Checkpoint 4: Enrichment & Final Selection.** Research the top 17 foundations (web + DB verification) to find the best 5 for the report.

The next session should:
1. Read this file and the plan file
2. Run the enrichment research on 17 foundations with the expanded verification protocol (see "Enrichment Protocol" section below)
3. Present findings at Checkpoint 4 pause for Alec's review
4. Then proceed to Checkpoints 5 (report assembly) and 6 (final delivery)

### Remaining Steps
1. **Checkpoint 4:** Enrichment research on 17 foundations → categorize READY/CONDITIONAL/WATCH/SKIP → select final 5
2. **Checkpoint 5:** Draft report using template, calculate funder snapshots, write positioning strategies
3. **Checkpoint 6:** Final polish, quality checks, Word export, prospect pipeline CSV

---

## What's Done

### Checkpoint 1: Client Profile & Identity Verification (COMPLETE)
- VetsBoats identity fully verified (EIN 464194065, Sausalito CA, 501(c)(3) private operating foundation)
- Client profile constructed from sales call + online research (no questionnaire available)
- **dim_clients INSERT executed** — VetsBoats is ID 8 in the database
- 11 matching keywords selected and tested
- 3-option target_grant_purpose defined (narrow/medium/broad)
- Pre-call brief errors caught and corrected (3 funders debunked: Goodfellow, JPMorgan, BMS were grants to "Center for Wooden Boats" not VetsBoats)
- Known funders confirmed: Tahoe Maritime (943073894), Henry Mayo Newhall (946073084), Sidney Stern (956495222), Charis Fund (946077619), Bonnell Cove (133556721)
- **File:** `CHECKPOINT_1_client_profile.md`

### Checkpoint 2: Sibling Discovery & Grant Landscape (COMPLETE)
- 33 siblings loaded (28 original from Jan 16 + 5 new: Sail to Prevail, Team Paradise, Freedom Waters, Sailing Angels, Raider Sailing)
- 347 grants from 144 unique foundations populated into `calc_client_sibling_grants`
- Keyword matching: 26 grants matched
- Semantic similarity: 340 grants scored using 3-option Max-of-3 (all-MiniLM-L6-v2)
- 47 target grants identified (keyword OR semantic >= 0.55) from 19 foundations
- **File:** `LOG_2026-02-06_checkpoint2_siblings_grants.md`

### Checkpoint 3: Foundation Scoring & Prospect Ranking (COMPLETE)
- 144 foundations scored in `calc_client_foundation_scores` (known funders excluded)
- Tiered: 4 Tier A, 26 Tier B, 8 Tier B-, 13 Tier C, 93 Tier D-E
- Full ranked list exported
- **File:** `DATA_2026-02-06_foundation_scores.csv`

### Agent QA Review (COMPLETE)
- Two agents reviewed the enrichment plan and surfaced critical issues
- Major finding: 990-PF eligibility is the #1 risk — many funders restrict to public charities
- Expanded verification protocol defined (see below)

---

## What's Not Started
- Checkpoint 4: Foundation enrichment research (17 foundations)
- Checkpoint 5: Report assembly
- Checkpoint 6: Final delivery + quality checks
- Retrospective

---

## Decisions Made

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| 11 keywords (specific + "veteran fishing") | Broader "veteran program" (1,000+ hits) | Only 21% overlap between broad/narrow foundations — 79% noise |
| 3-option Max-of-3 semantic scoring | Single target_grant_purpose | Catches wider range of relevant grants |
| $20K-$750K sibling budget range | $27K-$685K (standard 0.2x-5x) | Catches Judd Goldman ($678K), borderline orgs |
| Exclude all 5 known funders | Only exclude 3 DB-confirmed | Alec confirmed Charis + Bonnell Cove as past funders |
| $5K-$50K grant size seeking | Wider range | DB shows first grants from sweet-spot foundations = $3K-$5K median |
| Keep Freedom Waters as sibling | Exclude (above $750K in recent year) | Alec override — strong mission alignment |
| Skip detailed play-by-play logs going forward | Continue blow-by-blow logging | Conversation transcripts (JSONL) capture everything; write concise checkpoint summaries instead |

---

## What Was Tried (Failed Approaches)

| Approach | Why It Failed | Lesson |
|----------|--------------|--------|
| MCP postgres tool for queries with SQL comments | `--` comments cause "Only SELECT queries" error | Use psql via Bash tool instead |
| MCP postgres after an error | Transaction enters "aborted" state, all queries fail | Switch to psql via Bash for all queries |
| target_grant_reason as VARCHAR(20) | "keyword+semantic_narrow" exceeds 20 chars | Use abbreviated codes: "kw+sem", "keyword", "semantic" |
| Pre-call brief data as source of truth | 3 funders were misattributed (Center for Wooden Boats confusion) | Always verify external claims against DB by EIN |
| Broad "veteran program" keywords | Would add 276 irrelevant foundations (79% noise) | Specific keywords outperform broad ones for niche orgs |

---

## Files Created This Session

| File | Path | Description |
|------|------|-------------|
| CHECKPOINT_1_client_profile.md | 5. Runs/VetsBoats/2026-02-06/ | Full client profile with all dim_clients fields |
| PLAN_2026-02-06_vetsboats_report_build.md | 5. Runs/VetsBoats/2026-02-06/ | 6-checkpoint implementation plan |
| LOG_2026-02-06_vetsboats_build_activity.md | 5. Runs/VetsBoats/2026-02-06/ | Checkpoint 1 detailed activity log |
| LOG_2026-02-06_checkpoint2_siblings_grants.md | 5. Runs/VetsBoats/2026-02-06/ | Checkpoint 2 activity log |
| DATA_2026-02-06_full_review.csv | 5. Runs/VetsBoats/2026-02-06/ | 347 grants, 23 columns — comprehensive review CSV |
| DATA_2026-02-06_foundation_scores.csv | 5. Runs/VetsBoats/2026-02-06/ | 144 foundations ranked with tiers |
| semantic_scoring.py | scratchpad (temp) | Python script for 3-option semantic scoring |

---

## Database Changes Made

| Table | Action | Details |
|-------|--------|---------|
| `f990_2025.dim_clients` | INSERT | VetsBoats as ID 8 (ein=464194065, 11 keywords, 5 known funders, $20K-$750K range) |
| `f990_2025.calc_client_siblings` | INSERT | 33 siblings for client_ein=464194065 |
| `f990_2025.calc_client_sibling_grants` | INSERT + UPDATE | 347 grants populated, keyword_match and semantic_similarity scored, is_target_grant set |
| `f990_2025.calc_client_foundation_scores` | INSERT | 144 foundations scored with tiers and eligibility flags |

---

## The 17 Foundations to Research in Checkpoint 4

### Tier A — Top Prospects (open + geo + target grants + $1M+ assets)
| # | Foundation | EIN | State | Assets | Target Grants | Total Giving |
|---|-----------|-----|-------|--------|---------------|-------------|
| 1 | Albert & Ethel Herzstein | 746070484 | TX | $127M | 2 | $122K |
| 2 | Jim Moran Foundation | 651058044 | FL | $252M | 1 | $20K |
| 3 | Harry S Cameron Foundation | 746073312 | TX | $30M | 1 | $5K |
| 4 | Sparks Foundation | 237029788 | TN | $6.4M | 1 | $500 |

### Tier B — Open + Geo, strongest indicators (no target grants but fund siblings)
| # | Foundation | EIN | State | Assets | Total Giving | Median Grant |
|---|-----------|-----|-------|--------|-------------|-------------|
| 5 | Alletta Morris McBean | 943019660 | CA | $20M | $125K | $125K |
| 6 | Liberty Mutual Foundation | 141893520 | MA | $47M | $100K | $25K |
| 7 | Frederick Henry Prince Trust | 366009208 | IL | $112M | $50K | $10K |
| 8 | Enterprise Holdings Foundation | 431262762 | MO | $545M | $5K | $5K |
| 9 | 1687 Foundation | 263882051 | TX | $162M | $5K | $5K |
| 10 | Dr P Phillips Foundation | 596135403 | FL | $45M | $5K | $5K |
| 11 | Virginia Wellington Cabot | 046728351 | MA | $43M | $15K | $15K |
| 12 | Kovler Family Foundation | 366152744 | IL | $35M | $13K | $5K |
| 13 | Diebold Foundation | 341757351 | OH | $7M | $25K | $25K |
| 14 | Bill Simpson Foundation | 843992087 | IN | $18M | $10K | $10K |

### Tier C — Preselected but strongest fit signals (cultivation targets)
| # | Foundation | EIN | State | Assets | Target Grants |
|---|-----------|-----|-------|--------|---------------|
| 15 | Van Beuren Charitable | 222773769 | NY | $343M | 5 |
| 16 | John & Daria Barry Foundation | 461550110 | FL | $477M | 4 |
| 17 | San Francisco Challenge | 943242538 | CA | $2.1M | 5 |

---

## Enrichment Protocol (Expanded — from agent QA review)

### For each of the 17 foundations, gather:

**From the web:**
- Website URL (verify it loads)
- Application process (portal, LOI, full proposal, invitation-only)
- Current deadlines (with YEAR verification — flag if year not confirmed)
- Program areas / funding priorities
- Geographic restrictions (specific county/city lists)
- Grant size range (stated)
- Contact info (program officer name, email, phone)
- Board/staff names (for Matt Goettelman connection paths)
- Staffing requirements (paid staff required?)
- Budget minimum/maximum requirements
- Audit requirements
- Organization type restrictions — **CRITICAL: look for "public charity," "509(a)," "not a private foundation" language**
- Multi-year funding availability
- Reporting burden

**From the database:**
```sql
-- 1. Has this foundation ever funded a private foundation (990-PF filer)?
SELECT fg.recipient_name, fg.recipient_ein, fg.amount, fg.tax_year
FROM f990_2025.fact_grants fg
JOIN f990_2025.pf_returns pr ON fg.recipient_ein = pr.ein
WHERE fg.foundation_ein = '[EIN]'
ORDER BY fg.tax_year DESC LIMIT 10;

-- 2. Geographic distribution
SELECT recipient_state, COUNT(*), SUM(amount)
FROM f990_2025.fact_grants WHERE foundation_ein = '[EIN]'
GROUP BY recipient_state ORDER BY COUNT(*) DESC;

-- 3. Typical grantee size
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY nr.total_revenue) as median_grantee_rev
FROM f990_2025.fact_grants fg
JOIN f990_2025.nonprofit_returns nr ON fg.recipient_ein = nr.ein
WHERE fg.foundation_ein = '[EIN]' AND fg.tax_year >= 2020;

-- 4. Recent grant activity
SELECT recipient_name, amount, purpose_text, tax_year
FROM f990_2025.fact_grants WHERE foundation_ein = '[EIN]'
ORDER BY tax_year DESC LIMIT 20;
```

### Categorize each foundation:
- **READY** — accepting apps, VetsBoats qualifies, no red flags
- **CONDITIONAL** — unclear on 990-PF eligibility or other issue
- **WATCH** — invitation-only but strong fit (cultivation target for future)
- **SKIP** — geographic mismatch, wrong sector, dormant, 990-PF excluded, or red flag

### Hard Gates (must pass ALL to be READY):
- [ ] 990-PF eligible (not restricted to public charities, OR has funded PFs before)
- [ ] No budget minimum above $137K
- [ ] No paid staff requirement
- [ ] Geographic scope includes Marin County, CA
- [ ] Active grants in past 3 years
- [ ] Accepts unsolicited applications

---

## Key Data Findings

- VetsBoats has only 3 confirmed grants in our DB (all 2023): Tahoe Maritime $25K, Henry Mayo Newhall $15K, Sidney Stern $3.5K
- Pre-call brief contained 3 major errors (Goodfellow/JPMorgan/BMS grants were to "Center for Wooden Boats" WA, not VetsBoats)
- **VetsBoats classification CONFIRMED (2026-02-06 session 2):**
  - Files **990-PF** (private foundation return) — does NOT appear in nonprofit_returns (990/990-EZ)
  - **IRS BMF foundation code 03** = "Private operating foundation (other)" per Charity Navigator
  - **BUT:** 990-PF filings show `private_operating_foundation_ind = TRUE` only in **2018**; marked **FALSE** in 2019, 2020, 2022, 2023
  - This means VetsBoats may no longer qualify as a private operating foundation (failed income/assets/endowment/support test) or it's a filing error
  - **Bottom line: VetsBoats is a private foundation, NOT a public charity** — this is the #1 eligibility risk for funder matching
  - **Bonnell Cove paradox explained:** Their guidelines say "public charities only" yet they funded VetsBoats — suggests foundations don't always enforce stated restrictions, OR Bonnell Cove made an exception
  - **Recommendation for Terry:** (1) Provide IRS determination letter, (2) Clarify if the FALSE on operating foundation box since 2019 is intentional or a filing error, (3) Consider re-qualifying as operating foundation if lapsed
- `only_contri_to_preselected_ind = TRUE` on VetsBoats' own filing is irrelevant (describes their grantmaking, not their eligibility as recipient)
- First grants from $10M-$50M foundations: median $5K, subsequent median $10K (50% ratio)
- Semantic threshold of 0.55 cleanly separates relevant from irrelevant grants (100% of keyword matches also scored >= 0.55)
- Only 4 foundations pass all filters (open + geo + target grants + assets) — report will likely need some Tier B foundations too
- Bonnell Cove paradox: their guidelines say "public charities only" yet they funded VetsBoats — suggests either VetsBoats' classification is different than assumed OR foundations don't always enforce stated restrictions

---

## Blockers

| Blocker | Severity | Workaround |
|---------|----------|------------|
| VetsBoats is a **private foundation** (confirmed) — NOT a public charity | HIGH | BMF shows code 03 (private operating foundation) but 990-PF filings since 2019 mark operating foundation as FALSE. Either way, it's a PF not a public charity. Must check each prospect foundation's 990-PF eligibility language AND whether they've funded other PFs. Recommend Terry provide IRS determination letter and clarify operating foundation status. |
| Only 4 Tier A prospects | MEDIUM | Supplement with best Tier B foundations that pass enrichment verification. Tier B has 26 foundations, several with strong indicators. |
| No questionnaire from client | LOW | Profile constructed from sales call + online research. Good enough for report but note as data quality flag. |

---

## Key People

| Person | Role | Notes |
|--------|------|-------|
| Terry Moran | Founder & ED, VetsBoats | Navy F-14 pilot, primary grant writer, all-volunteer org |
| Matt Goettelman | Advisory Board Member | Former West Point, Goldman Sachs — connection path for foundation boards |
| Alec | TheGrantScout | Reviewing at each checkpoint, making final decisions |

---

## Process Notes for Next Session

1. **Don't re-do Checkpoints 1-3** — all DB tables are populated and ready
2. **Skip detailed play-by-play logging** — conversation transcripts capture everything. Write concise checkpoint summaries instead.
3. **Export a comprehensive CSV after enrichment** (like DATA_2026-02-06_full_review.csv) so Alec can manually review
4. **The 990-PF check is the most important new addition** — run it for every foundation before recommending
5. **MCP postgres tool is unreliable** — use `psql` via Bash tool directly (PGPASSWORD=kmalec21)
6. **Alec prefers to review data himself** — provide browsable files, not just summaries

---

*Generated by Claude Code on 2026-02-06*
