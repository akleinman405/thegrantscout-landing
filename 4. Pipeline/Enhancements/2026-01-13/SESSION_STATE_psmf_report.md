# SESSION STATE: PSMF Report Build

**Last Updated:** 2026-01-14 00:30 (New fellowship-sibling approach defined)
**Purpose:** Maintain continuity across context compactions

## IMMEDIATE NEXT SESSION ACTIONS
1. **Execute new fellowship-sibling approach** (see below)
2. Find orgs running similar fellowship programs (regardless of topic)
3. Pull grants those orgs received for fellowship/training programs
4. Identify foundations that fund fellowship programs → those are PSMF prospects

---

## NEW APPROACH: Fellowship-Program Siblings (NOT Patient Safety Siblings)

### The Key Insight
The patient safety sibling approach failed because those orgs are mostly:
- State-level (get state funding)
- Direct service (get service delivery grants)
- Different operating model than PSMF

**New approach:** Find organizations that run **similar PROGRAMS** (global health fellowships) regardless of topic area. Funders who fund fellowship programs will fund fellowship programs.

### What PSMF's Fellowship Program Looks Like

| Characteristic | Detail |
|----------------|--------|
| **Name** | Global Interprofessional Patient Safety Fellowship (Kiani Fellowship) |
| **Duration** | 12 months |
| **Format** | Monthly live virtual classroom sessions |
| **Target** | Healthcare professionals from ALL WHO regions |
| **Countries** | Argentina, Sudan, Lebanon, Uganda, Pakistan, Indonesia, Kenya, Malaysia, Australia |
| **Focus** | Leadership development for healthcare professionals |
| **Cost** | FREE to fellows |
| **Special emphasis** | Leaders from lower-middle and middle-income countries |

### Fellowship-Sibling Criteria (NEW)

| Criterion | Why It Matters |
|-----------|----------------|
| Runs a **fellowship or training program** | Same program model |
| **Global/international** scope | Not US-only |
| **Healthcare professionals** as audience | Same target trainees |
| **Leadership development** focus | Building future leaders |
| Budget $500K-$10M | Similar operational scale |
| **Topic can be ANYTHING** | Matching on program type, not cause area |

### Keywords to Search

```sql
-- Search for orgs running health fellowship programs
LOWER(mission_description) LIKE '%fellowship%' AND LOWER(mission_description) LIKE '%health%'
LOWER(mission_description) LIKE '%global health%' AND LOWER(mission_description) LIKE '%training%'
LOWER(mission_description) LIKE '%healthcare%' AND LOWER(mission_description) LIKE '%leadership%'
LOWER(organization_name) LIKE '%fellowship%' AND healthcare-related NTEE
```

### Process to Execute
1. Search database for orgs running health fellowship/training programs
2. Manually verify they match the fellowship model
3. Load as "fellowship siblings"
4. Pull grants they received with keywords: "fellowship", "training", "education", "leadership"
5. Evaluate which grants PSMF would have been perfect for
6. Those foundations become PSMF prospects

---

## KEY FINDING FROM PREVIOUS GRANT REVIEW
- Only 1 grant scored 9/10 (Moore Foundation → IHI for fellowship opportunities)
- Sibling grants scored poorly (max 6/10) due to geographic restrictions
- Most valuable info: Consuelo feedback call + understanding what PSMF is NOT
- **Lesson:** Match on PROGRAM TYPE, not CAUSE AREA

---

## HOW WE'RE WORKING (Important for Next Session)

We're building a **reusable pipeline guide** while simultaneously building the PSMF report. The pattern is:

1. **For each phase/step:**
   - Review what needs to be done
   - Create TASK.md file with instructions for Claude Code CLI
   - Create any SQL/Python scripts needed
   - Update GUIDE with step details and file references
   - Execute for PSMF
   - Update status docs

2. **File structure:**
   - `GUIDE_2026-01-13_PSMF_report_step_by_step.md` - Main reference (ToC + step details)
   - `phases/{phase_folder}/TASK.md` - Instructions for each phase
   - `phases/{phase_folder}/*.sql` or `*.py` - Actual code
   - `SESSION_STATE_psmf_report.md` - This file (current status)
   - `REPORT_2026-01-13.1_psmf_build_log.md` - Detailed history

3. **Key principle:** TASK.md files tell Claude what to do, separate script/SQL files contain the actual code (for easier debugging/modification)

---

## Current Status

**Phase:** 3 - Foundation Discovery
**Step:** PAUSED - Sibling Quality Review
**Status:** Need to replace siblings with verified list

### Key Discovery
- Embedding-based siblings had ~20-30% false positives (labor unions, etc.)
- Manual research initially found 20 verified siblings
- **EXPANDED to 40 siblings** on 2026-01-13 21:00 session
- See `PSMF_verified_siblings_v2.md` for full list with 3 tiers:
  - Tier 1: 20 Core Patient Safety orgs (PSOs, safety foundations)
  - Tier 2: 10 Healthcare Simulation & Education orgs
  - Tier 3: 10 Healthcare Quality Collaboratives

### Siblings Removed (Not True Matches):
- ACNL (nurse leadership, not safety-focused)
- Virginia Telehealth Network (access, not safety)
- Vital Talk, NP Fellowship, Fellowship Council (training structure, not safety mission)

### Next Session Should:
1. Run SQL from PSMF_verified_siblings_v2.md to load 40 siblings
2. Re-run Steps 3.2.1-3.2.4 with clean data
3. Consider lowering semantic threshold to 0.40

---

## Immediate Next Actions

### 1. Run Step 3.2.3: Update Keyword Matches

Use PSMF keywords to flag matching grant purposes:
```sql
-- Run with client_ein = '462730379'
-- SQL file: phases/phase3_2_sibling_grants/03_update_keywords.sql
```

### 2. Run Step 3.2.4: Update Target Grant Flags
```sql
-- SQL file: phases/phase3_2_sibling_grants/04_update_target_grants.sql
```

### 3. Run Step 3.3.1: Aggregate Foundation Scores
```sql
-- SQL file: phases/phase3_3_foundation_scores/05_aggregate_scores.sql
```

---

## What's Complete

### Phase 1: Pre-Flight Setup ✅
- GUIDE section: Complete
- `phases/phase1_preflight/TASK.md`: Complete

### Phase 2: Client Understanding ✅
- GUIDE section: Complete
- `phases/phase2_client_understanding/TASK.md`: Complete
- All 6 SQL files: Complete
- PSMF target_grant_purpose: Set in database

### Phase 3.1: Build calc_client_siblings ✅
- GUIDE section: ✅ Complete
- TASK.md: ✅ Created
- PSMF data: ✅ Done (91 siblings in calc_client_siblings)

### Phase 3.2: Build calc_client_sibling_grants ⚠️ IN PROGRESS
- GUIDE section: ✅ Complete
- TASK.md: ✅ Created
- SQL/Python files: ✅ All exist
- PSMF Step 3.2.1: ✅ Done (298 grants populated)
- PSMF Step 3.2.2: ✅ Done (259 grants with semantic_similarity using target_grant_purpose)
- PSMF Step 3.2.3: ❌ Pending
- PSMF Step 3.2.4: ❌ Pending

---

## Step 3.2.2 Results (Just Completed)

Semantic similarity was regenerated using `target_grant_purpose` instead of `mission_text`:

| Metric | Value |
|--------|-------|
| Grants processed | 259 |
| High (>=0.55) | 0 |
| Medium (0.40-0.55) | 38 |
| Low (<0.40) | 221 |
| Average similarity | 0.222 |
| Max similarity | 0.499 |

**Note:** The specific `target_grant_purpose` (fellowship/clinical education) yields lower semantic similarity scores than a broad mission match would. This is expected - **keyword matching (Step 3.2.3) will be the primary target grant identifier for PSMF**.

---

## Files in Phase Folders

```
phases/
├── phase1_preflight/
│   └── TASK.md ✓
├── phase2_client_understanding/
│   ├── TASK.md ✓
│   ├── 01_review_client_profile.sql ✓
│   ├── 02_compare_missions.sql ✓
│   ├── 03_check_keyword_frequency.sql ✓
│   ├── 04_check_data_quality.sql ✓
│   ├── 05_find_similar_grant_purposes.sql ✓
│   └── 06_add_target_grant_purpose_column.sql ✓
├── phase3_1_siblings/
│   └── TASK.md ✓ (NEW)
├── phase3_2_sibling_grants/
│   ├── TASK.md ✓ (NEW)
│   ├── 01_create_tables.sql ✓
│   ├── 02_populate_sibling_grants.sql ✓ (Step 3.2.1)
│   ├── generate_semantic_similarity.py ✓ (Step 3.2.2)
│   ├── 03_update_keywords.sql ✓ (Step 3.2.3)
│   ├── 04_update_target_grants.sql ✓ (Step 3.2.4)
│   └── 06_verify_quality.sql ✓
├── phase3_3_foundation_scores/
│   └── 05_aggregate_scores.sql ✓
├── phase3_4_enrich/
│   └── (empty)
├── phase3_5_select/
│   └── (empty)
├── phase4_report_assembly/
│   └── (8 metric SQL files) ✓
└── phase5_quality_review/
    └── (empty)
```

---

## PSMF Database State

| Table | Records | Status |
|-------|---------|--------|
| dim_clients (PSMF) | 1 | target_grant_purpose SET |
| calc_client_siblings | 40 | ✅ LOADED with manual_verified_v2 siblings |
| calc_client_sibling_grants | 35 | ✅ LOADED (12 of 40 siblings had grants) |
| calc_client_foundation_scores | 0 | Pending - use foundation prospects from REPORT |

---

## Key Files to Read

1. **This file** - SESSION_STATE_psmf_report.md
2. **GUIDE** - `GUIDE_2026-01-13_PSMF_report_step_by_step.md`
3. **Build Log** - `REPORT_2026-01-13.1_psmf_build_log.md`
4. **PSMF Profile** - `PSMF_organization_profile.md` (8+ programs, fellowship details)
5. **Verified Siblings V2** - `PSMF_verified_siblings_v2.md` (40 verified siblings in 3 tiers)
6. **Sibling Process** - `PROCESS_sibling_identification.md` (methodology)
7. **Foundation Prospects** - `REPORT_2026-01-13.3_psmf_foundation_prospects.md` (8 top prospects)
8. **Grant Matching Methodology** - `REPORT_2026-01-13.4_grant_matching_methodology.md` (how to identify matching grants)
9. **Strategic Funder Discovery** - `REPORT_2026-01-13.5_strategic_funder_discovery.md` ⭐ NEW (4-agent analysis, new targets)
10. **Consuelo Feedback** - `6. Business/beta-testing/2. Feedback/REPORT_2025-12-03_feedback_consuelo_psmf_summary.md`

---

## Step Numbering Reference

| Old | New |
|-----|-----|
| 3.A.1 | 3.1.1 |
| 3.B.1 | 3.2.1 |
| 3.B.2 | 3.2.2 |
| 3.B.3 | 3.2.3 |
| 3.B.4 | 3.2.4 |
| 3.C.1 | 3.3.1 |
| 3.D.1-7 | 3.4.1-7 |
| 3.E.1 | 3.5.1 |

---

## PSMF Client Profile

| Field | Value |
|-------|-------|
| EIN | 462730379 |
| Name | Patient Safety Movement Foundation |
| State | CA |
| Budget (IRS) | $365,177 |
| Budget (Questionnaire) | Over $1,000,000 |
| Budget Variance | RED |
| Target Grant Purpose | Healthcare training program providing clinical education fellowships to reduce preventable patient harm globally |
| Priority Program | Fellowship Program |
| Keywords | patient safety, healthcare education, clinical education, medical education, fellowship, preventable harm, healthcare quality, hospital safety, medical training |

---

*Last updated: 2026-01-13 18:50*
