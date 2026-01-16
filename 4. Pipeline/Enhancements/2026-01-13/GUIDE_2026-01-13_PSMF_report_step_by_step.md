# Pipeline Guide: Foundation Matching Report

**Version:** 3.0
**Created:** 2026-01-13
**Status:** In Progress (Phase 3, Step 3.2.3)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Phase 1: Pre-Flight Setup](#3-phase-1-pre-flight-setup)
   - Step 1.1: Load questionnaire into dim_clients
   - Step 1.2: Look up EIN and IRS financials
   - Step 1.3: Create run folder
   - Step 1.4: Verify database connection
4. [Phase 2: Client Understanding](#4-phase-2-client-understanding)
   - Step 2.1: Review client profile
   - Step 2.2: Compare questionnaire mission vs IRS mission
   - Step 2.3: Identify matching keywords
   - Step 2.4: Flag data quality issues
   - Step 2.5: Create target grant purpose
5. [Phase 3: Foundation Discovery](#5-phase-3-foundation-discovery)
   - **Section 3.1: Build calc_client_siblings**
     - Step 3.1.1: Find Siblings (pgvector similarity search)
   - **Section 3.2: Build calc_client_sibling_grants**
     - Step 3.2.1: Populate Sibling Grants
     - Step 3.2.2: Generate Semantic Similarity ✅
     - Step 3.2.3: Update Keyword Matches ← CURRENT
     - Step 3.2.4: Update Target Grant Flags
   - **Section 3.3: Build calc_client_foundation_scores**
     - Step 3.3.1: Aggregate Scores + Run LASSO
   - **Section 3.4: Enrich calc_client_foundation_scores**
     - Step 3.4.1: foundation_type
     - Step 3.4.2: geo_eligible
     - Step 3.4.3: open_to_applicants
     - Step 3.4.4: client_eligible
     - Step 3.4.5: eligibility_notes
     - Step 3.4.6: has_active_opportunities
     - Step 3.4.7: opportunity_notes
   - **Section 3.5: Review and Select**
     - Step 3.5.1: Select final foundations
6. [Phase 4: Report Assembly](#6-phase-4-report-assembly)
   - Step 4.1: Gather enrichment details
   - Step 4.2: Calculate Funder Snapshot metrics
   - Step 4.3: Find comparable grants
   - Step 4.4: Generate positioning strategies
   - Step 4.5: Generate action plans
   - Step 4.6: Assemble into template
7. [Phase 5: Final Quality Review](#7-phase-5-final-quality-review)
8. [Reference: Folder Structure](#8-reference-folder-structure)
9. [Reference: Database Tables](#9-reference-database-tables)
10. [Reference: Lessons Learned](#10-reference-lessons-learned)

---

## 1. Overview

**Goal:** Find foundations who gave TARGET GRANTS (matching purpose) to SIMILAR NONPROFITS (siblings).

| Term | Definition |
|------|------------|
| **Sibling** | Nonprofit with similar mission (similarity >= 0.50) and budget (0.2x-5.0x) |
| **Target Grant** | Grant purpose matches client's work (keyword OR semantic >= 0.55) |
| **Gold Standard** | Target + First-time + Geographic match |

**LASSO is calculated at Step 3.3.1** - used as validation/tiebreaker, not primary signal.

---

## 2. Prerequisites

*To be documented*

---

## 3. Phase 1: Pre-Flight Setup

**Folder:** `phases/phase1_preflight/`

| Step | What | Output |
|------|------|--------|
| 1.1 | Load questionnaire into dim_clients | Client row in database |
| 1.2 | Look up EIN and IRS financials | EIN, database_revenue, database_assets |
| 1.3 | Create run folder | `runs/{client}/{date}/` |
| 1.4 | Verify database connection | Confirmation of counts |

**Files:**
- `TASK.md` - Instructions for Claude Code CLI

**Quality Checks:**
- [ ] Client exists in dim_clients
- [ ] EIN populated (9 digits)
- [ ] mission_text populated
- [ ] state populated
- [ ] database_revenue populated
- [ ] Run folder created

**PSMF Results:**
- EIN: 462730379
- State: CA
- Budget: $365,177 (IRS) vs >$1M (questionnaire) → RED variance flag

---

## 4. Phase 2: Client Understanding

**Folder:** `phases/phase2_client_understanding/`

| Step | What | Input | Output |
|------|------|-------|--------|
| 2.1 | Review client profile | dim_clients row | Understanding of client |
| 2.2 | Compare questionnaire vs IRS mission | Both mission texts | Best mission_text selected |
| 2.3 | Identify matching keywords | Mission, sector | matching_grant_keywords array |
| 2.4 | Flag data quality issues | All client data | quality_flags, budget_variance_flag |
| 2.5 | Create target grant purpose | User input + similar grants | target_grant_purpose |

**Files:**
| File | Step |
|------|------|
| `TASK.md` | Instructions |
| `01_review_client_profile.sql` | 2.1 |
| `02_compare_missions.sql` | 2.2 |
| `03_check_keyword_frequency.sql` | 2.3 |
| `04_check_data_quality.sql` | 2.4 |
| `05_find_similar_grant_purposes.sql` | 2.5 |
| `06_add_target_grant_purpose_column.sql` | Schema (run once) |

**Key Outputs (used later):**
- `mission_text` → Used in Step 3.1.1 for sibling matching
- `matching_grant_keywords` → Used in Step 3.2.3 for keyword filtering
- `target_grant_purpose` → Used in Step 3.2.2 for semantic similarity

**Quality Checks:**
- [ ] Mission text is best version (questionnaire or IRS)
- [ ] 8-12 keywords identified and stored
- [ ] Data quality issues flagged
- [ ] Target grant purpose created and stored

**PSMF Results:**
- Mission Source: Questionnaire (more specific about fellowship)
- Keywords: patient safety, healthcare education, clinical education, fellowship, etc.
- Quality Flags: budget_variance_red
- Target Grant Purpose: "Healthcare training program providing clinical education fellowships to reduce preventable patient harm globally"

---

## 5. Phase 3: Foundation Discovery

### Section 3.1: Build calc_client_siblings

**Folder:** `phases/phase3_1_siblings/`

| Step | What | Input | Output |
|------|------|-------|--------|
| 3.1.1 | Find siblings via pgvector | Client mission embedding | calc_client_siblings populated |

**Files:**
| File | Purpose |
|------|---------|
| `TASK.md` | Instructions for Claude Code CLI |

**Process:**
1. Generate client mission embedding using all-MiniLM-L6-v2 model
2. Query `emb_nonprofit_missions` for similar nonprofits (similarity >= 0.50)
3. Filter by budget (0.2x - 5.0x of client budget)
4. Insert into `calc_client_siblings`

**Key Parameters:**
- Embedding model: all-MiniLM-L6-v2 (384 dimensions)
- Similarity threshold: >= 0.50
- Budget ratio: 0.2x to 5.0x

**Quality Checks:**
- [ ] At least 30 siblings found (lower threshold if fewer)
- [ ] Top 10 siblings are relevant (spot-check missions)
- [ ] Budget ratios within expected range

**PSMF Results:**
- Total siblings: 91
- Similarity range: 0.501 - 0.610
- Types: Healthcare education, patient safety, clinical training organizations

---

### Section 3.2: Build calc_client_sibling_grants

**Folder:** `phases/phase3_2_sibling_grants/`

| Step | What | Input | Output |
|------|------|-------|--------|
| 3.2.1 | Populate sibling grants | calc_client_siblings | Grants to siblings loaded |
| 3.2.2 | Generate semantic similarity | target_grant_purpose | semantic_similarity populated |
| 3.2.3 | Update keyword matches | matching_grant_keywords | keyword_match flags set |
| 3.2.4 | Update target grant flags | All flags | is_target_grant, target_grant_reason set |

**Files:**
| File | Step |
|------|------|
| `TASK.md` | Instructions |
| `01_create_tables.sql` | Create calc tables |
| `02_populate_sibling_grants.sql` | Step 3.2.1 |
| `generate_semantic_similarity.py` | Step 3.2.2 |
| `03_update_keywords.sql` | Step 3.2.3 |
| `04_update_target_grants.sql` | Step 3.2.4 |
| `06_verify_quality.sql` | Quality checks |

**Key Outputs:**
- `is_target_grant`: TRUE if keyword_match OR semantic_similarity >= 0.55
- `target_grant_reason`: 'KEYWORD', 'SEMANTIC', or 'BOTH'
- NULL means unknown (not analyzable), not false

**Quality Checks:**
- [ ] Grants populated (hundreds to thousands)
- [ ] 80%+ have VALID purpose_quality
- [ ] Some target grants identified (5-15% typical)
- [ ] target_grant_reason populated for all targets

**PSMF Results:**
- Total grants: 298
- Unique foundations: ~170
- Valid purpose: ~260 (87%)
- Semantic similarity max: 0.499 (narrow target_grant_purpose yields lower scores)
- Target grants: TBD (pending keyword matching)

---

### Section 3.3: Build calc_client_foundation_scores

**Folder:** `phases/phase3_3_foundation_scores/`

**Files:**
| File | Step |
|------|------|
| `05_aggregate_scores.sql` | Step 3.3.1 |

*To be documented*

---

### Section 3.4: Enrich calc_client_foundation_scores

**Folder:** `phases/phase3_4_enrich/`

*To be documented*

---

### Section 3.5: Review and Select

**Folder:** `phases/phase3_5_select/`

*To be documented*

---

## 6. Phase 4: Report Assembly

**Folder:** `phases/phase4_report_assembly/`

**Files:**
| File | Purpose |
|------|---------|
| `annual_giving.sql` | Foundation annual giving metrics |
| `comparable_grant.sql` | Find similar grant for positioning |
| `funding_trend.sql` | 3-year giving trend |
| `geographic_focus.sql` | Geographic concentration |
| `giving_style.sql` | General support vs program-specific |
| `recipient_profile.sql` | Typical recipient size/sector |
| `repeat_funding.sql` | Repeat funding rate |
| `typical_grant.sql` | Median/range grant size |

*To be documented*

---

## 7. Phase 5: Final Quality Review

**Folder:** `phases/phase5_quality_review/`

*To be documented*

---

## 8. Reference: Folder Structure

```
4. Pipeline/
├── phases/
│   ├── phase1_preflight/
│   ├── phase2_client_understanding/
│   ├── phase3_1_siblings/
│   ├── phase3_2_sibling_grants/
│   ├── phase3_3_foundation_scores/
│   ├── phase3_4_enrich/
│   ├── phase3_5_select/
│   ├── phase4_report_assembly/
│   └── phase5_quality_review/
├── templates/
├── runs/
└── Enhancements/
```

---

## 9. Reference: Database Tables

| Table | Purpose |
|-------|---------|
| `dim_clients` | Client profiles from questionnaire |
| `calc_client_siblings` | Similar nonprofits per client |
| `calc_client_sibling_grants` | Grants to siblings with flags |
| `calc_client_foundation_scores` | Aggregated foundation rankings |

---

## 10. Reference: Lessons Learned

*To be documented as we go*

---

*Guide created 2026-01-13*
