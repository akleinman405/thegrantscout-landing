# PROMPT 1 of 4: VetsBoats Public Charity Discovery — Candidate Identification

**Date:** 2026-02-21  
**Type:** Database queries + ranking  
**Schema:** f990_2025  
**Client:** VetsBoats Foundation (EIN 464194065, "Wooden Boats for Veterans")  
**Next:** PROMPT 2 (targeted crawl of approved candidates)

---

## Situation

VetsBoats is a private foundation serving veterans through adaptive sailing in the SF Bay Area. We've completed 3 batches of deep crawls across 53 private foundations (17% actionable rate, 83% ineligible due to PF status).

Our `schedule_i_grants` table contains 997K grants from 48K public charity grantmakers (2019-2023) that we haven't used for matching. This is a separate funder universe from the 990-PF data. We're also carrying forward the best PF leads from the deep crawl work.

This prompt identifies and ranks ALL candidates. Alec will review and approve which ones to research before Prompt 2.

---

## Tasks

### 1. Query Schedule I for peer org funders

Find all public charity grantmakers that funded VetsBoats' peer orgs but NOT VetsBoats itself.

**Peer orgs (search by EIN first, fall back to name ILIKE):**
- Achieve Tahoe / Disabled Sports Eastern Sierra (check both names)
- Treasure Island Sailing Center (TISC)
- BAADS (Bay Area Association of Disabled Sailors)
- Judd Goldman Adaptive Sailing Foundation
- Sail to Prevail
- Warrior Sailing Program

**Exclude VetsBoats' known funders from results:**
```sql
-- Find filers who grant to peers but not to VetsBoats
SELECT DISTINCT s.filer_ein, s.filer_name, s.recipient_name, s.amount, s.purpose, s.tax_year
FROM f990_2025.schedule_i_grants s
WHERE (recipient matches peer org via EIN or ILIKE)
AND s.filer_ein NOT IN (
  SELECT filer_ein FROM f990_2025.schedule_i_grants 
  WHERE recipient_ein = '464194065' 
  OR recipient_name ILIKE '%wooden boats%' 
  OR recipient_name ILIKE '%vetsboats%'
)
ORDER BY s.amount DESC;
```

### 2. Query Schedule I for keyword matches

Find public charities making grants with relevant purpose text. Focus on grants $5,000+ from 2022-2023.

Keyword combinations:
- veteran/veterans + sailing/boats/maritime/adaptive/recreation
- disabled/disability + sailing/adaptive sports/recreation
- adaptive sailing
- therapeutic sailing/recreation + veteran

### 3. Filter and deduplicate

**Remove known funders:**
- Tahoe Maritime Foundation, Henry Mayo Newhall Foundation, Sidney Stern Memorial Trust, Charis Fund, Bonnell Cove Foundation, SVCF, American Online Giving Foundation

**Flag DAF platforms separately (not actionable leads):**
- Fidelity Investments Charitable Gift Fund
- Schwab Charitable Fund
- National Philanthropic Trust
- Vanguard Charitable Endowment Program
- Morgan Stanley Global Impact Funding Trust
- Network for Good
- Mightycause
- TisBest Philanthropy
- Benevity
- AmazonSmile

**Remove obvious geographic mismatches** (East Coast community foundations with no CA grants).

Deduplicate by filer_ein. Combine peer-org and keyword results.

### 4. Add PF leads from deep crawl work

Include these confirmed PF leads (already researched — do NOT re-crawl):
- Kim & Harold Louie Family Foundation (STRONG_FIT, rolling LOI)
- Charles H. Stout Foundation (STRONG_FIT, June 15 deadline)
- Kovler Family Foundation (POSSIBLE_FIT, mid-Nov deadline)
- Howard Family Foundation (POSSIBLE_FIT, bank-managed)
- Hutton Family Foundation (RELATIONSHIP_TARGET, preselected)
- Jerome Mirza Foundation (RELATIONSHIP_TARGET, preselected)

Mark these as "PF — ALREADY RESEARCHED" so they're not sent to the crawl step.

### 5. Enrich all candidates with DB data

For each unique public charity grantmaker, pull from DB:
- All grants to peer orgs (recipient, amount, year, purpose)
- Any other grants with veteran/disability/sailing/adaptive keywords
- Total grantmaking volume (sum of all schedule_i_grants for that filer)
- From `nonprofit_returns`: revenue, assets, website, mission description, state

### 6. Rank and output candidate list

**Ranking priority:**
1. Funds multiple VetsBoats peers (strongest signal)
2. Funds one peer + has veteran/adaptive keywords in other grants
3. Funds one peer org at significant amount ($10K+)
4. Keyword match only but strong thematic fit
5. PF leads from deep crawl (already ranked)

---

## Output

| File | Description |
|------|-------------|
| DATA_2026-02-21_vetsboats_pc_candidates_ranked.md | Ranked candidate list for Alec to review |
| DATA_2026-02-21_vetsboats_pc_query_results.json | Raw query results |
| DATA_2026-02-21_vetsboats_daf_signals.md | DAF platform activity on peer orgs (separate) |

### Format for candidate list

For each candidate, one block:

```
## Rank X: [Org Name] (EIN, State)
- **Source:** Peer funder / Keyword match / Both
- **Peer grants:** [which peers, amounts, years]
- **Keyword grants:** [relevant purpose text matches]
- **Total grantmaking:** $X (Y grants, 2022-2023)
- **From DB:** Revenue $X, Assets $X, Website, Mission snippet
- **Category:** Direct fit / Strong adjacent / Community foundation / PF (already researched)
- **Status:** RESEARCH (needs crawl) / ALREADY RESEARCHED (PF lead) / SKIP (DAF/geographic)
```

### STOP HERE

Do not proceed to web research. Alec will review this list and respond with:
- Which candidates to research (approve/skip)
- Any reordering
- Any candidates to add from his own knowledge
