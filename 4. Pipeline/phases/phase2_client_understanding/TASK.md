# TASK: Phase 2 - Client Understanding

**Purpose:** Deeply understand the client to enable accurate matching
**When:** After Phase 1 (client loaded into dim_clients)
**Folder:** `phases/phase2_client_understanding/`

---

## Overview

Phase 2 ensures we understand the client's mission, keywords, and specific funding goals before running foundation discovery. This phase produces the inputs needed for semantic matching and keyword filtering.

**Key Outputs:**
- Verified mission_text (best of questionnaire vs IRS)
- matching_grant_keywords (for keyword filtering in Step 3.2.3)
- target_grant_purpose (for semantic matching in Step 3.2.2)

---

## Step 2.1: Review Client Profile

**SQL:** `01_review_client_profile.sql`

**Instructions for Claude Code CLI:**

1. Run the SQL query to pull the client's full profile from dim_clients
2. Review key fields:
   - name, ein, state, city
   - mission_text (from questionnaire)
   - budget_tier, database_revenue (compare for variance)
   - sector_broad, sector_ntee
   - geographic_scope
3. Summarize the client profile for context

**Quality Check:**
- [ ] All key fields populated
- [ ] Mission text is meaningful (not truncated or generic)
- [ ] State and city make sense together

---

## Step 2.2: Compare Questionnaire Mission vs IRS Mission

**SQL:** `02_compare_missions.sql`

**Instructions for Claude Code CLI:**

1. Run the SQL query to get the IRS mission from nonprofit_returns
2. Compare to the questionnaire mission in dim_clients
3. Decide which is better:
   - IRS mission is often more formal/complete
   - Questionnaire mission may be more current or specific
4. If IRS is better, update dim_clients.mission_text
5. Document which was chosen and why

**Decision Criteria:**
| Choose Questionnaire If | Choose IRS If |
|------------------------|---------------|
| More specific to current work | More comprehensive |
| Mentions specific programs | Questionnaire is vague |
| More recent/accurate | Questionnaire is just tagline |

**Quality Check:**
- [ ] Both missions reviewed
- [ ] Decision documented
- [ ] dim_clients.mission_text contains best version

---

## Step 2.3: Identify Matching Keywords

**Instructions for Claude Code CLI:**

1. Review the client's mission_text and sector
2. Identify 8-12 keywords that would appear in grant purposes for work like theirs
3. Keywords should be:
   - Specific enough to filter (not just "education")
   - Broad enough to capture variations
   - Based on actual grant purpose language in the database
4. Run the SQL to check keyword frequency in fact_grants
5. Store final keywords in dim_clients.matching_grant_keywords

**SQL:** `03_check_keyword_frequency.sql`

**Example Keywords for PSMF:**
- patient safety
- healthcare education
- clinical education
- medical education
- fellowship
- preventable harm
- healthcare quality
- hospital safety
- medical training

**Quality Check:**
- [ ] 8-12 keywords identified
- [ ] Keywords tested against fact_grants (have matches)
- [ ] Keywords stored in dim_clients.matching_grant_keywords

---

## Step 2.4: Flag Data Quality Issues

**SQL:** `04_check_data_quality.sql`

**Instructions for Claude Code CLI:**

1. Run the data quality SQL
2. Review flags for:
   - Budget variance (questionnaire vs IRS)
   - Missing required fields
   - Suspicious data (wrong state, no EIN match, etc.)
3. Update dim_clients.quality_flags array with any issues
4. Document issues that may affect matching

**Quality Flags:**
| Flag | Meaning |
|------|---------|
| `budget_variance_red` | >3x difference between questionnaire and IRS |
| `budget_variance_yellow` | 2-3x difference |
| `missing_ein` | Could not find EIN |
| `missing_mission` | No mission text |
| `no_irs_record` | Not found in nonprofit_returns |

---

## Step 2.5: Create Target Grant Purpose

**Purpose:** Create a 1-2 sentence description of what a grant TO this client would say, written in the style of actual grant purpose text from IRS filings. This is used for semantic similarity matching in Step 3.2.2.

**Instructions for Claude Code CLI:**

1. **Gather context about their funding goal:**
   - Check feedback files, questionnaire responses, or ask user
   - Identify: What program needs funding? What's the impact?
   - Look for: `6. Business/beta-testing/2. Feedback/` for client feedback files

2. **Search for similar grants to see funder phrasing:**
   - Run `05_find_similar_grant_purposes.sql` with relevant keywords
   - Note patterns: action verbs, outcome language, beneficiary descriptions
   - Real grants are often short and direct (e.g., "FOR MEDICAL RESEARCH FELLOWSHIP")

3. **Synthesize target grant purpose:**
   - Combine client's specific program with funder-style phrasing
   - Keep it 1-2 sentences, direct, no marketing language
   - Include: program type + activity + outcome/beneficiary

4. **Store in database:**
   ```sql
   UPDATE f990_2025.dim_clients
   SET target_grant_purpose = '[your text]',
       updated_at = NOW()
   WHERE ein = '[client_ein]';
   ```

**SQL:** `05_find_similar_grant_purposes.sql`

**Good target grant purpose characteristics:**
- Reads like a real IRS 990-PF grant purpose entry
- Specific program mentioned (fellowship, training, etc.)
- Clear outcome or beneficiary
- No buzzwords or marketing language

**Quality Check:**
- [ ] Client funding goal understood from feedback/questionnaire
- [ ] Similar grant purposes reviewed for phrasing patterns
- [ ] target_grant_purpose stored in dim_clients
- [ ] Text reads like actual grant purpose (not marketing copy)

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `TASK.md` | This file - instructions |
| `01_review_client_profile.sql` | Step 2.1 query |
| `02_compare_missions.sql` | Step 2.2 query |
| `03_check_keyword_frequency.sql` | Step 2.3 query |
| `04_check_data_quality.sql` | Step 2.4 query |
| `05_find_similar_grant_purposes.sql` | Step 2.5 query |
| `06_add_target_grant_purpose_column.sql` | One-time schema update |

---

## PSMF Example Results

| Field | Value |
|-------|-------|
| Mission Source | Questionnaire (more specific about fellowship program) |
| Keywords | patient safety, healthcare education, clinical education, fellowship, preventable harm, healthcare quality, hospital safety, medical training, medical education |
| Quality Flags | budget_variance_red (questionnaire says >$1M, IRS shows $365K) |
| Target Grant Purpose | Healthcare training program providing clinical education fellowships to reduce preventable patient harm globally |

**How target grant purpose was created:**
1. Read feedback file: `6. Business/beta-testing/2. Feedback/REPORT_2025-12-03_feedback_consuelo_psmf_summary.md`
2. Key insight: Fellowship Program is priority, trains healthcare professionals globally
3. Searched grants with keywords: fellowship, healthcare, clinical education, patient safety
4. Synthesized text combining their program (fellowship/training) + outcome (reduce preventable harm) + scope (globally)

---

*Task file created 2026-01-13*
