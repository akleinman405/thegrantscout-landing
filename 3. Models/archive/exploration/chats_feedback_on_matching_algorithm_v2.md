# Chat's Feedback on Matching Algorithm V2 Spec

This document summarizes ChatGPT's detailed feedback on your **Matching Algorithm V2** specification.

## 1. Big-Picture Strengths

### Clear and Strong Conceptual Shift
- Moves away from “who is likely to fund you?” toward “who funds orgs like you + how open are they to new orgs?”
- Sellable and technically implementable.
- Two-sided framing prevents rediscovering only current funders.

### Clean Warehouse-Oriented Schema
- `src_*` → `dim_*` → `fact_grants` → `calc_*` → `match_*` mirrors modern warehouse patterns.
- Profiles separated from per-client match rows, enabling traceability and debugging.

### Transparent, Human-Explainable Matching
- Hard filters are deterministic.
- Soft alignment gives dimension-level reasons.
- Tier system is simple but powerful.
- Workflow diagrams logically match data dependencies.

### Roadmap is Realistic
- Phase 1–5 build sequencing is sound.
- Backtesting on 2020–22 training / 2023 testing is appropriate.
- Embeddings treated as an upgrade, not a blocker.

---

## 2. What Should Be “Core V2”

These are the **minimum viable components** required to deliver a functioning V2 foundation matching engine.

### Core Tables
- `src_pf_returns`, `src_pf_grants`
- `dim_foundations`
- `dim_recipients`
- `fact_grants`
- `dim_clients`
- `calc_foundation_profiles`
- `match_similar_recipients`
- `match_client_foundations`

### Core Logic
- Hard filters (geographic, size, org type, requested grant amount)
- Structured similarity (state, NTEE, size tier, populations)
- Keyword-based project matching
- Tiers 1–3 with alignment reasons
- No embeddings required initially

### What Can Wait for Later Versions
- `calc_recipient_profiles` (nice-to-have)
- `calc_recurring_programs`
- Embeddings and `pgvector` indexes
- `dim_opportunities` and opportunity matching

The core slice lets you generate meaningful, defensible foundation matches immediately.

---

## 3. Simplifications and Design Tweaks

### Improve Recipient Deduplication
Current uniqueness is `(name_normalized, state)`. Issues:
- Many unrelated orgs share the same normalized name + state.
- Many identical orgs appear under variant names.

Recommendation:
- Treat EIN as canonical when available.
- Only use `(name_normalized, state)` when EIN missing.
- Add a `dedupe_confidence` field (`high`, `medium`, `low`).

### Org Type Eligibility Field Missing
Add `eligible_org_types TEXT[]` to `dim_foundations` or `calc_foundation_profiles`.
- V2 default: all 501(c)(3).
- Later: detect gov, tribal, school district funding patterns.

### Geographic Focus JSON Rules
Define a clear rule:
- Use last 5 years of grants.
- Either keep all states with values or keep top N states + `"other"`.

### Start with a Simple Similarity Model
**V2.0:** structured attributes only  
**V2.1:** hybrid (structured + embeddings)

### Scores vs Composite Score
Internal dimensional scores are fine.  
You aren’t breaking your philosophy by computing a multi-factor linear score *internally*.

### Recalculation Strategy
Keep recalculations **client-centric**, even when batch-updating all clients.

---

## 4. Edge Cases & Gaps

### Known Funders Must Map to EINs
Maintain both:
- `known_funders_eins`
- `known_funder_names_raw`

### Foundations with Low Activity
Openness scores are noisy with <10 grants.
- Shrink toward 0.5
- Possibly exclude from Tier 1

### Project Type Extraction Coverage
Expect:
- Noisy text
- Many “general support” grants
- Some dual-purpose grants

Consider simple fallback heuristics.

---

## 5. Recommended Next Steps

1. **Freeze the Core V2 Scope**  
   - Foundation matching only  
   - No embeddings  
   - Keyword project matching

2. **Make Small Schema Adjustments**  
   - Add `eligible_org_types`  
   - Adjust recipient dedupe strategy  
   - Prepare JSONB indexes for future queries

3. **Write ETL Scripts**  
   - Populate `dim_foundations`, `dim_recipients`, `fact_grants`, `calc_foundation_profiles`

4. **Build a Complete Per-Client Pipeline**  
   - Hard filters  
   - Similarity  
   - Project match  
   - Tiers + reasons

5. **Manual Review of a Real Client**  
   - Tune filters before backtesting.

---

If you'd like, the next steps could include generating SQL `CREATE TABLE` statements, ETL scripts, or the function skeletons (`calculate_similar_recipients`, `calculate_foundation_matches`) so your Claude Dev Team can implement the pipeline directly.
