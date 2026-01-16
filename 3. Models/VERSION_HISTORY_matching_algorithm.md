# VERSION HISTORY: Grant Matching Algorithm

**Purpose:** Document the evolution of TheGrantScout's grant matching methodology, including rationale for changes.

---

## Current Version: V3.0 (Sibling Nonprofit + Multi-Signal)

**Date:** 2026-01-13
**Status:** In Development

### Approach

Three complementary signals, used in sequence:

| Signal | What It Measures | Question Answered |
|--------|------------------|-------------------|
| **1. Sibling Nonprofits** | Mission + budget similarity | "Have they funded orgs like you?" |
| **2. Grant Purpose Keywords** | Purpose text matching | "Have they funded work like yours?" |
| **3. LASSO Model** | Statistical patterns | "Do foundations like this fund orgs like you?" |

### Sibling Nonprofit Methodology (NEW)

**Definition:** A nonprofit S is a "sibling" of client C if:
1. `cosine_similarity(S.mission_embedding, C.mission_embedding) >= 0.50`
2. `S.budget BETWEEN C.budget × 0.2 AND C.budget × 5.0`

**Rationale:**
- Mission embeddings capture semantic similarity (synonyms, related concepts)
- Budget filter ensures operational similarity (similar-sized orgs have similar funder profiles)
- Geography excluded from sibling definition (handled at foundation level)
- NTEE excluded (embeddings capture this; NTEE ~33% inaccurate)

**Parameters (based on agent analysis):**
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Similarity threshold | 0.50 | Balances precision/recall for all-MiniLM-L6-v2 |
| Budget lower bound | 0.2x | Excludes sub-viable organizations |
| Budget upper bound | 5.0x | Maintains operational similarity |

### Workflow

```
1. IDENTIFY SIBLINGS
   └── Mission embedding similarity >= 0.50
   └── Budget within 0.2x - 5.0x of client
   └── Output: ~50-500 similar nonprofits

2. FIND FOUNDATIONS THAT FUNDED SIBLINGS
   └── Query fact_grants for sibling recipients
   └── Count: grants, unique siblings funded, total amount
   └── Weight by recency (2023 > 2018)

3. FILTER BY GRANT PURPOSE
   └── Keywords from client's matching_grant_keywords
   └── Verify foundation has funded similar WORK

4. VALIDATE WITH LASSO
   └── Check model score for sanity
   └── Use for final ranking among equals

5. ELIGIBILITY CHECK
   └── Accepts applications
   └── Client meets stated requirements
   └── Geographic coverage includes client
```

### Key Tables

| Table | Purpose |
|-------|---------|
| `emb_nonprofit_missions` | 500K+ nonprofit mission embeddings |
| `calc_foundation_avg_embedding` | Foundation grant purpose embeddings |
| `fact_foundation_client_scores` | Pre-computed LASSO scores |
| `fact_grants` | 8.3M grant records |

---

## Previous Versions

---

### V2.0: Keyword Filter + LASSO (2026-01-06 to 2026-01-12)

**Approach:**
1. Run LASSO model to get top 100 foundations
2. Filter by grant purpose keywords
3. Deep enrichment on filtered set

**Workflow:**
- Phase 2a: LASSO scoring (state, sector, size matching)
- Phase 2b: Keyword filter on grant purposes
- Phase 3: Eligibility check
- Phase 4+: Enrichment and report

**Limitations identified:**
- Keywords miss synonyms and related concepts
- No "sibling" signal - only looks at foundations, not similar recipients
- Missed question: "Have they funded orgs LIKE you?"

**Changes from V1:**
- Added grant purpose keyword filtering (Phase 2b)
- Added quick eligibility check before deep research
- Split enrichment into quick vs deep phases
- Added comparable grant selection step

---

### V1.0: LASSO Only (2026-01-03 to 2026-01-05)

**Approach:**
1. Run LASSO model to score all foundations
2. Take top 100
3. Enrich all 100
4. Filter to top 5

**Model:** LASSO V6.1
- Test AUC: 0.94
- Top features: match_state_pct (+1.69), match_sector_pct (+1.60)
- Trained on 1.31M rows with size-matched negative sampling

**Limitations identified:**
- No verification of grant PURPOSE match
- Spent hours enriching foundations that didn't fund relevant work
- State/sector matching missed national foundations for national clients
- No filter-first approach (wasted research time)

---

## Lessons Learned

### From V1 → V2

| Issue | Discovery Date | Solution |
|-------|---------------|----------|
| Gary Milgard in PSMF report (not healthcare) | 2026-01-06 | Added grant purpose keyword filter |
| 4+ hours spent enriching non-viable foundations | 2026-01-06 | Added quick eligibility check before deep research |
| Generic comparable grants | 2026-01-06 | Added sector-specific grant selection |
| CA-only foundations for national clients | 2026-01-06 | Added curated national foundations step |

### From V2 → V3

| Issue | Discovery Date | Solution |
|-------|---------------|----------|
| Keywords miss synonyms | 2026-01-13 | Added semantic embeddings |
| No "funded orgs like you" signal | 2026-01-13 | Added sibling nonprofit methodology |
| Missing: recipient similarity | 2026-01-13 | Mission embeddings + budget filter |
| LASSO as primary vs validation | 2026-01-13 | Redesigned: siblings first, LASSO validates |

---

## Model Files

| Version | Location |
|---------|----------|
| LASSO V6.1 | `3. Models/v6.1/` |
| Coefficients | `4. Pipeline/config/coefficients.json` |
| Scaling | `4. Pipeline/config/scaling.json` |
| Embeddings | `f990_2025.emb_nonprofit_missions`, `f990_2025.calc_foundation_avg_embedding` |

---

## Embedding Tables

| Table | Records | Model | Archived |
|-------|---------|-------|----------|
| `calc_foundation_avg_embedding` | ~112K | all-MiniLM-L6-v2 | Restored 2026-01-13 |
| `emb_nonprofit_missions` | ~500K | all-MiniLM-L6-v2 | Restored 2026-01-13 |
| `emb_programs` | ~317K | all-MiniLM-L6-v2 | Still archived |
| `emb_prospects` | ~74K | all-MiniLM-L6-v2 | Still archived |

---

## Future Considerations

1. **Better embedding model:** Consider bge-base-en-v1.5 or nomic-embed-text-v1.5 for improved similarity
2. **Foundation sibling funding table:** Pre-compute which foundations funded which sibling clusters
3. **Recency weighting:** Weight recent grants higher than older ones
4. **Competitor detection:** Flag when similar orgs are competing for same funding pool
5. **Grant purpose embeddings:** Semantic match on grant purposes, not just keywords

---

*Version History created 2026-01-13*
*Philosophy: Iterate based on evidence, document rationale*
