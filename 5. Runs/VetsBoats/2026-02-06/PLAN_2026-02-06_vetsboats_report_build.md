# VetsBoats First Report — Implementation Plan

## Context

**Client:** Wooden Boats for Veterans (DBA VetsBoats), EIN 46-4194065, Sausalito CA
**Why:** VetsBoats just paid — this is their first report as a paying customer. Terry Moran (founder, Navy veteran) needs to scale fundraising from $150-250K/yr to $500K/yr to hire staff, expand nationally (Cape Cod, Ohio, San Diego), restore vessel Clover for Hawaii voyages, and service ~$300K debt.
**Deliverable:** Monthly grant report (2026-02-02 template) with 5 foundation profiles (prioritizing active opportunities) + a broader prospect pipeline for future months.

---

## Critical Files

| File | Purpose |
|------|---------|
| `6. Business/sales-marketing/Materials/Research/2025-12-4 VetsBoats/2025-12-04/Call with Terry 2025-12-4.md` | Sales call transcript — funding goals |
| `6. Business/sales-marketing/Materials/Research/2025-12-4 VetsBoats/2025-12-04/VetsBoats_Foundation_Pre-Call_Brief_2025-12-04.md` | Pre-call research — financials, programs |
| `5. Runs/VetsBoats/2026-01-16/REPORT_2026-01-16.1_vetsboats-sibling-analysis.md` | 28 siblings already identified |
| `5. Runs/VetsBoats/2026-01-16/REPORT_2026-01-16.2_vetsboats-foundation-analysis.md` | 67 sibling funders analyzed |
| `4. Pipeline/Enhancements/2026-02-02/TEMPLATE_2026-02-02_monthly_grant_report.md` | Report template to use |
| `4. Pipeline/Enhancements/2026-02-02/EXAMPLE_2026-02-02_horizons_grant_report.md` | Example of completed report |
| `4. Pipeline/process_client.py` | SQL/Python logic for Phases 3.1-3.3 (adapt, don't run directly) |
| `4. Pipeline/phases/` | TASK.md files for each phase |
| `4. Pipeline/config/clients.json` | VetsBoats already listed (EIN 464194065) |

---

## Special Constraints

1. **Not in nonprofit_returns** — VetsBoats likely files 990-N (small org) so no IRS financial data or mission in our DB
2. **No questionnaire** — Must manually construct profile from DB, online research, and sales call
3. **No embeddings** — `emb_nonprofit_missions` archived; use manual keyword-based sibling discovery (already done in prior research)
4. **process_client.py won't work as-is** — Requires embeddings + dim_clients entry; we'll execute phases manually via SQL/Python
5. **Known past funders to EXCLUDE:** Tahoe Maritime (943073894), Henry Mayo Newhall (946073084), Sidney Stern (956495222), Charis Fund, Bonnell Cove

---

## Step-by-Step Plan (with Review Checkpoints)

Each checkpoint is a **PAUSE** where we stop, I present what was done, why, and how it connects to the final goal. You review, ask questions, suggest changes, and approve before we continue.

---

### CHECKPOINT 1: Client Profile & Identity Verification
**Phases covered:** 1 (Pre-Flight) + 2 (Client Understanding)
**Goal:** Establish a verified, complete client record in the database

**What I'll do:**
1. **Verify VetsBoats identity online** — WebSearch to confirm EIN, NTEE code, legal name, state, city, revenue, mission against IRS Tax Exempt Org Search, Candid/GuideStar, ProPublica
2. **Construct the full client profile** from: verified online data + sales call with Terry + prior research
3. **INSERT into dim_clients** with all fields populated
4. **Create run folder** at `5. Runs/VetsBoats/2026-02-06/`
5. **Define 8-12 matching_grant_keywords** — test each against `fact_grants.purpose_text` to confirm they appear in real grant language
6. **Craft target_grant_purpose** — 1-2 sentences in IRS filing style describing what a grant TO VetsBoats would say
7. **Flag data quality issues** (no IRS record, no questionnaire, manual revenue)

**What I'll present at the checkpoint:**
- The full client profile (every field and its source)
- Any discrepancies found between sources
- The keyword list with hit counts from the database
- The target_grant_purpose and reasoning
- Data quality flags and what they mean for downstream steps

**Why this matters:** Everything downstream (sibling matching, keyword filtering, semantic scoring) depends on getting the mission, keywords, and target_grant_purpose right. Bad inputs here = bad foundation matches later.

**You'll decide:** Are the keywords right? Does the target_grant_purpose capture what Terry wants funding for? Any fields need adjustment?

### >>> PAUSE — Review & Discuss <<<

---

### CHECKPOINT 2: Sibling Discovery & Grant Landscape
**Phases covered:** 3.1 (Siblings) + 3.2 (Grant Population & Flagging)
**Goal:** Map the funding landscape — who funds orgs like VetsBoats?

**What I'll do:**
1. **Insert 28 known siblings** from prior 2026-01-16 research into `calc_client_siblings`
2. **Search for additional siblings** via keyword search in `nonprofit_returns` (budget filter: $27K-$685K)
3. **Populate all grants to siblings** into `calc_client_sibling_grants` (expected: ~167+ grants)
4. **Run semantic similarity scoring** — Python script using sentence_transformers to compare each grant purpose to target_grant_purpose
5. **Run keyword matching** — flag grants whose purpose matches our keywords
6. **Set target grant flags** — is_target_grant = keyword OR semantic >= 0.55

**What I'll present at the checkpoint:**
- Final sibling count (28 + any new) and summary by tier
- Total grants found and breakdown: how many are target grants, keyword matches, semantic matches
- Distribution of semantic similarity scores
- Sample of highest-scoring target grants (so you can gut-check relevance)
- Any surprises or concerns (e.g., too few target grants, unexpected keyword matches)

**Why this matters:** Target grants are the signal that tells us "this foundation funds work like VetsBoats'." If we have too few, the foundation scoring will be weak. If we have false positives, we'll recommend wrong foundations.

**You'll decide:** Do the target grants look right? Should we adjust the semantic threshold or keywords? Are there sibling orgs we missed or should remove?

### >>> PAUSE — Review & Discuss <<<

---

### CHECKPOINT 3: Foundation Scoring & Prospect Ranking
**Phases covered:** 3.3 (Foundation Scoring) + initial 3.4 (Ranking)
**Goal:** Produce a ranked list of foundation prospects

**What I'll do:**
1. **Aggregate grant data to foundation level** — INSERT into `calc_client_foundation_scores`
2. **Set open_to_applicants and geo_eligible** from IRS data
3. **Generate summary stats** — total foundations, how many open + with target grants, asset distribution
4. **Rank and present the top 20** ordered by target grants, gold standard grants, and total amount

**What I'll present at the checkpoint:**
- Summary table: total foundations scored, how many open, how many with target grants
- Top 20 ranked foundations with key metrics (name, state, assets, siblings funded, target grants, open/closed)
- The full scored list exported as CSV (for your reference)
- Known past funders flagged (to exclude from report but potentially include in "existing relationships" section)
- Recommended foundations to research first (and why)

**Why this matters:** This is where we decide which foundations to invest research time in. The ranking determines the quality of the final report. Getting the right 5 is more important than getting 15 mediocre ones.

**You'll decide:** Do the top foundations look promising? Any you want to add/remove? Which should we prioritize for deep research? Should we adjust scoring criteria?

### >>> PAUSE — Review & Discuss <<<

---

### CHECKPOINT 4: Enrichment & Final Selection
**Phases covered:** 3.4 (Enrichment) + 3.5 (Final Selection)
**Goal:** Verify top prospects and select the 5 for the report

**What I'll do:**
1. **Quick eligibility screen** on top 15-20 foundations — check websites for application info, geographic eligibility, program fit
2. **Categorize each:** READY (accepting apps, good fit) / CONDITIONAL (unclear) / WATCH (invitation-only but strong fit) / SKIP (red flags)
3. **Deep enrichment on the 5 best READY foundations** — contacts, deadlines, application requirements, URLs
4. **Build prospect pipeline CSV** — ALL viable foundations tiered for future months
5. **Select final 5** for this report, prioritizing active opportunities

**What I'll present at the checkpoint:**
- Eligibility screen results for each researched foundation
- The 5 selected foundations with enrichment details (contacts, deadlines, how to apply)
- The full prospect pipeline CSV with tiers (A/B/C) and notes
- Reasoning for each selection and each exclusion
- Any foundations where eligibility was unclear

**Why this matters:** This is the last chance to change direction before we write the report. The enrichment data directly becomes the "How to Apply" sections. The prospect pipeline becomes VetsBoats' roadmap for the next 6-12 months.

**You'll decide:** Are these the right 5? Any swaps? Is the prospect pipeline useful? Any foundations to add to the pipeline?

### >>> PAUSE — Review & Discuss <<<

---

### CHECKPOINT 5: Draft Report Review
**Phases covered:** 4 (Report Assembly)
**Goal:** Review the draft report before final polish

**What I'll do:**
1. **Calculate funder snapshot metrics** for each of the 5 foundations (8 SQL queries each)
2. **Find proof-of-fit grants** — 2-3 grants per foundation showing alignment with VetsBoats
3. **Generate positioning strategies** — what to lead with, comparable grants, suggested ask, framing
4. **Generate action plans** — week-by-week steps, "If You Only Have 5 Hours" callout
5. **Assemble full report** using the monthly template format

**What I'll present at the checkpoint:**
- The full draft report in markdown
- Each foundation profile with: Why This Foundation, Fit Evidence, Funder Snapshot, How to Apply, Contacts, Positioning Strategy, Action Steps
- The "If You Only Have 5 Hours" section
- Monthly action plan timeline
- Quick reference section

**Why this matters:** This is what Terry and Matt will read. The positioning strategies need to resonate with VetsBoats' specific story (Navy veteran founder, therapeutic sailing, Clover restoration, national expansion). The action plans need to be realistic for a small all-volunteer org.

**You'll decide:** Tone right? Positioning strategies compelling? Action plans realistic? Any sections need rework? Ready for final polish?

### >>> PAUSE — Review & Discuss <<<

---

### CHECKPOINT 6: Final Delivery
**Phases covered:** 5 (Quality Review) + Final Output
**Goal:** Deliver polished report + prospect pipeline

**What I'll do:**
1. **Apply all feedback** from Checkpoint 5
2. **Run quality checklist** (no prior funders, active foundations, CA-eligible, formatting, links)
3. **Convert to Word (.docx)**
4. **Export prospect pipeline CSV**
5. **Write internal process report** (SOP compliance)

**What I'll present:**
- Final report (markdown + Word)
- Prospect pipeline CSV (tiered for future months)
- Quality checklist results
- Internal process report

**You'll decide:** Ready to send to Terry?

### >>> FINAL REVIEW <<<

---

## Output Files

All saved to `5. Runs/VetsBoats/2026-02-06/`:

| File | Description |
|------|-------------|
| `PLAN_2026-02-06_vetsboats_report_build.md` | This plan document |
| `REPORT_2026-02-06_vetsboats_grant_report.md` | Final client-facing report (markdown) |
| `REPORT_2026-02-06_vetsboats_grant_report.docx` | Final client-facing report (Word) |
| `DATA_2026-02-06_foundation_scores.csv` | Full scored foundation list |
| `DATA_2026-02-06_prospect_pipeline.csv` | Tiered prospect list for future reports |
| `DATA_2026-02-06_enrichment_log.csv` | Research notes on each foundation |
| `REPORT_2026-02-06_vetsboats_process_report.md` | Internal process report (SOP compliance) |
| `RETRO_2026-02-06_vetsboats_report_retrospective.md` | Post-build retrospective |

---

*Plan created during planning session on 2026-02-06*
