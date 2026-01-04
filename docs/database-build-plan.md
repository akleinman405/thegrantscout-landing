# TheGrantScout Database Build Plan

**Updated:** 2025-12-10  
**Schema:** f990_2025

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  Raw Import Tables (populated)                                          │
│  ├── pf_returns (638K) - Foundation filings                             │
│  ├── pf_grants (8.3M) - Grant transactions                              │
│  ├── nonprofits (~800K) - 990/990-EZ filers                             │
│  ├── officers - Foundation/nonprofit officers                           │
│  └── irs_bmf (1.9M) - IRS Business Master File                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PHASE 1: ENTITY TABLES                             │
├─────────────────────────────────────────────────────────────────────────┤
│  dim_foundations (~170K) - One row per foundation EIN                   │
│  dim_recipients (~350K) - One row per recipient EIN                     │
│  fact_grants (8.3M) - Grant transactions linked to dims                 │
│  dim_clients (7) - Paying clients from questionnaire                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: CALCULATED TABLES                           │
├─────────────────────────────────────────────────────────────────────────┤
│  calc_foundation_profiles (~170K) - Aggregated metrics per foundation   │
│    └── openness_score, geographic_focus, sector_focus, grant sizes      │
│  calc_recipient_profiles (~350K) - Aggregated metrics per recipient     │
│    └── funder_eins array, funding patterns, consistency                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      EMBEDDING TABLES                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  grant_embeddings (8.3M) - Semantic vectors for grant purposes          │
│  client_embeddings (7) - Semantic vectors for client missions           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   PHASE 3: OPERATIONAL TABLES                           │
├─────────────────────────────────────────────────────────────────────────┤
│  match_runs - Algorithm execution log                                   │
│  match_results - Scored foundation matches per client                   │
│  match_reviews - Scout/Validator decisions                              │
│  client_reports - Delivered reports                                     │
│  match_feedback - Client ratings and outcomes (learning loop)           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Build Sequence

### Enrichment (Before Phase 1)

| Step | Script | Status | Notes |
|------|--------|--------|-------|
| 1 | `ein_enrichment_executor.py` | TODO | Match 8.3M grants to BMF |
| 2 | `import_scraped_urls.py` | TODO | Import ~60K scraped URLs |
| 3 | `url_ntee_phone_executor.py` | TODO | Validate URLs, enrich NTEE |

### Phase 1: Entity Tables

| Step | Script/Prompt | Status | Notes |
|------|---------------|--------|-------|
| 1 | PROMPT_2025-12-10_phase1_rebuild.md | TODO | Rebuild with 8.3M grants |

**Output Tables:**
- `dim_foundations` (~170K rows)
- `dim_recipients` (~350-400K rows)
- `fact_grants` (~8.3M rows)
- `dim_clients` (7 rows) - unchanged

### Phase 2: Calculated Tables

| Step | Script/Prompt | Status | Notes |
|------|---------------|--------|-------|
| 1 | PROMPT_2025-12-10_phase2_calculated_tables.md | TODO | After Phase 1 |

**Output Tables:**
- `calc_foundation_profiles` (~170K rows)
- `calc_recipient_profiles` (~350-400K rows)

### Embeddings

| Step | Script/Prompt | Status | Notes |
|------|---------------|--------|-------|
| 1 | PROMPT_2025-12-10_semantic_embeddings.md | TODO | ~14 hrs CPU |

**Output Tables:**
- `grant_embeddings` (~8.3M rows)
- `client_embeddings` (7 rows)

### Matching Algorithm

| Step | Script/Prompt | Status | Notes |
|------|---------------|--------|-------|
| 1 | PROMPT_2025-12-10_matching_algorithm.md | TODO | Requires embeddings |

**Output:** JSON files → loaded into Phase 3 tables

### Phase 3: Operational Tables

| Step | Script/Prompt | Status | Notes |
|------|---------------|--------|-------|
| 1 | PROMPT_2025-12-10_phase3_operational_tables.md | TODO | After matching works |

**Output Tables:**
- `match_runs`
- `match_results`
- `match_reviews`
- `client_reports`
- `match_feedback`

---

## Table Reference

### Raw Import Tables (f990_2025)

| Table | Rows | Purpose |
|-------|------|---------|
| pf_returns | 638K | Foundation 990-PF filings |
| pf_grants | 8.3M | Individual grant records |
| nonprofits | ~800K | Nonprofit 990/990-EZ filings |
| officers | TBD | Officers from both form types |
| schedule_a | TBD | Charity classification data |
| irs_bmf | 1.9M | IRS Business Master File |

### Phase 1: Entity Tables

| Table | Rows | Purpose | Key Fields |
|-------|------|---------|------------|
| dim_foundations | ~170K | Foundation master | ein, name, state, ntee_code, assets |
| dim_recipients | ~350K | Recipient master | ein, name, state, ntee_code, name_variants |
| fact_grants | 8.3M | Grant transactions | foundation_ein, recipient_ein, amount, purpose_text, is_first_time |
| dim_clients | 7 | Client profiles | name, ein, state, sector_ntee, mission_text, known_funders |

### Phase 2: Calculated Tables

| Table | Rows | Purpose | Key Fields |
|-------|------|---------|------------|
| calc_foundation_profiles | ~170K | Foundation metrics | openness_score, geographic_focus, sector_focus, median_grant |
| calc_recipient_profiles | ~350K | Recipient metrics | funder_eins[], total_funders, funding_consistency |

### Embedding Tables

| Table | Rows | Purpose | Key Fields |
|-------|------|---------|------------|
| grant_embeddings | 8.3M | Purpose vectors | grant_id, purpose_embedding (384 dims) |
| client_embeddings | 7 | Mission vectors | client_id, mission_embedding, project_embedding |

### Phase 3: Operational Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| match_runs | Algorithm execution log | client_id, params, algorithm_version |
| match_results | Scored matches | client_id, foundation_ein, score, score_breakdown, review_status |
| match_reviews | Review decisions | match_result_id, decision, rejection_reason, research_findings |
| client_reports | Delivered reports | client_id, delivered_at, file_path |
| match_feedback | Client feedback | match_result_id, outcome, amount_awarded |

---

## Workflow: Client → Report

```
1. CLIENT ONBOARDED
   └── dim_clients row created from questionnaire

2. MATCHING ALGORITHM RUNS
   ├── match_runs row created (params, version)
   └── match_results rows created (top 100 foundations)

3. SCOUT REVIEWS
   ├── Opens v_pending_reviews
   ├── Researches each foundation (website, recent 990)
   └── Creates match_reviews rows (approve/reject)

4. VALIDATOR NARROWS
   ├── Reviews approved matches
   └── Updates match_results.review_status

5. REPORTER GENERATES
   ├── Creates client_reports row
   ├── Links match_results.report_id
   └── Generates PDF/email

6. CLIENT RECEIVES
   └── client_reports.delivered_at updated

7. FEEDBACK CAPTURED
   ├── Survey sent after 30 days
   └── match_feedback rows created (ratings, outcomes)

8. LEARNING LOOP
   └── v_algorithm_performance shows success rates by version
```

---

## Prompts Ready

| Prompt | Purpose | Depends On |
|--------|---------|------------|
| PROMPT_2025-12-10_ein_enrichment_update.md | Update EIN enrichment scripts | - |
| PROMPT_2025-12-10_import_scraped_urls.md | Import scraped URLs | URL scraper completion |
| PROMPT_2025-12-10_phase1_rebuild.md | Rebuild entity tables | EIN enrichment |
| PROMPT_2025-12-10_phase2_calculated_tables.md | Build calc tables | Phase 1 |
| PROMPT_2025-12-10_semantic_embeddings.md | Generate embeddings | Phase 2 |
| PROMPT_2025-12-10_matching_algorithm.md | Build matching script | Embeddings |
| PROMPT_2025-12-10_phase3_operational_tables.md | Build operational tables | Matching algorithm |

---

## Current Status

**Completed:**
- [x] pf_returns import (638K)
- [x] pf_grants import (8.3M, purpose bug fixed)
- [x] nonprofits import (running, ~800K)
- [x] URL scraper (running, ~60K found)

**In Progress:**
- [ ] EIN enrichment (script needs update)
- [ ] URL import script (prompt ready)

**Pending:**
- [ ] Phase 1 rebuild
- [ ] Phase 2 calc tables
- [ ] Embeddings (~14 hrs)
- [ ] Matching algorithm
- [ ] Phase 3 operational tables
