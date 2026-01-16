# TASK: Phase 3.2 - Build calc_client_sibling_grants

**Purpose:** Populate and flag all grants to sibling nonprofits
**When:** After Phase 3.1 (siblings identified in calc_client_siblings)
**Folder:** `phases/phase3_2_sibling_grants/`

---

## Overview

This phase creates a granular grant-level table that tracks every grant to a sibling nonprofit, then flags which grants are "target grants" (matching the client's work).

**Definition:**
- **Target Grant** = Grant where purpose matches client's work (keyword match OR semantic similarity >= 0.55)
- **Gold Standard** = Target grant + First-time grant + Geographic match (calculated in Phase 3.3)

**Output:** Populated `calc_client_sibling_grants` table with all flags set

---

## Files in This Folder

| File | Step | Purpose |
|------|------|---------|
| `TASK.md` | - | This file - instructions |
| `01_create_tables.sql` | Setup | Create calc tables |
| `02_populate_sibling_grants.sql` | 3.2.1 | Insert grants to siblings |
| `generate_semantic_similarity.py` | 3.2.2 | Calculate semantic similarity |
| `03_update_keywords.sql` | 3.2.3 | Flag keyword matches |
| `04_update_target_grants.sql` | 3.2.4 | Set is_target_grant flags |
| `06_verify_quality.sql` | QC | Quality verification queries |

---

## Step 3.2.1: Populate Sibling Grants

**SQL:** `02_populate_sibling_grants.sql`

**Instructions for Claude Code CLI:**

1. Ensure `calc_client_sibling_grants` table exists (run `01_create_tables.sql` if needed)

2. Run the populate query with client EIN:
```sql
-- Replace :client_ein with actual EIN
INSERT INTO f990_2025.calc_client_sibling_grants
    (client_ein, foundation_ein, sibling_ein, grant_id, amount, tax_year,
     recipient_state, purpose_text, is_first_grant, purpose_quality)
SELECT
    '[client_ein]' as client_ein,
    fg.foundation_ein,
    fg.recipient_ein as sibling_ein,
    fg.id as grant_id,
    fg.amount,
    fg.tax_year,
    fg.recipient_state,
    fg.purpose_text,
    (fg.tax_year = (SELECT MIN(fg2.tax_year) FROM f990_2025.fact_grants fg2
                    WHERE fg2.foundation_ein = fg.foundation_ein
                    AND fg2.recipient_ein = fg.recipient_ein)) as is_first_grant,
    CASE
        WHEN fg.purpose_text IS NULL THEN 'NULL'
        WHEN TRIM(fg.purpose_text) = '' THEN 'EMPTY'
        WHEN LENGTH(TRIM(fg.purpose_text)) < 10 THEN 'SHORT'
        ELSE 'VALID'
    END as purpose_quality
FROM f990_2025.fact_grants fg
WHERE fg.recipient_ein IN (
    SELECT sibling_ein FROM f990_2025.calc_client_siblings
    WHERE client_ein = '[client_ein]'
);
```

3. Verify results:
```sql
SELECT
    COUNT(*) as total_grants,
    COUNT(DISTINCT foundation_ein) as unique_foundations,
    COUNT(DISTINCT sibling_ein) as unique_siblings,
    COUNT(*) FILTER (WHERE purpose_quality = 'VALID') as valid_purpose
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = '[client_ein]';
```

**Quality Check:**
- [ ] Grants populated (should be hundreds to thousands)
- [ ] Multiple foundations represented
- [ ] At least 80% have VALID purpose_quality

---

## Step 3.2.2: Generate Semantic Similarity

**Script:** `generate_semantic_similarity.py`

**Instructions for Claude Code CLI:**

1. Ensure client has `target_grant_purpose` set in `dim_clients` (from Phase 2, Step 2.5)

2. Run the Python script:
```bash
cd "/Users/aleckleinman/Documents/TheGrantScout/4. Pipeline"
python3 phases/phase3_2_sibling_grants/generate_semantic_similarity.py --ein [client_ein]
```

3. The script will:
   - Load the client's `target_grant_purpose`
   - Generate embeddings for each grant's purpose_text
   - Calculate cosine similarity
   - Update `semantic_similarity` column

4. Review the distribution:
```sql
SELECT
    CASE
        WHEN semantic_similarity >= 0.55 THEN 'High (>=0.55) - TARGET'
        WHEN semantic_similarity >= 0.40 THEN 'Medium (0.40-0.55)'
        WHEN semantic_similarity IS NOT NULL THEN 'Low (<0.40)'
        ELSE 'NULL'
    END as bucket,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) as pct
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = '[client_ein]'
GROUP BY 1
ORDER BY count DESC;
```

**Note:** If using a specific `target_grant_purpose` (rather than broad mission_text), expect fewer high-similarity grants. Keyword matching (Step 3.2.3) becomes more important.

**Quality Check:**
- [ ] All VALID purpose grants have semantic_similarity populated
- [ ] Distribution is reasonable (not all 0 or all 1)
- [ ] Script completed without errors

---

## Step 3.2.3: Update Keyword Matches

**SQL:** `03_update_keywords.sql`

**Instructions for Claude Code CLI:**

1. Get client's keywords from `dim_clients.matching_grant_keywords` (set in Phase 2)

2. Customize the SQL with client-specific keywords. Example for PSMF:
```sql
UPDATE f990_2025.calc_client_sibling_grants
SET keyword_match = (
    purpose_text ~* '\ypatient\s+safety\y' OR
    purpose_text ~* '\yhealthcare\s+education\y' OR
    purpose_text ~* '\yclinical\s+education\y' OR
    purpose_text ~* '\ymedical\s+education\y' OR
    purpose_text ~* '\yfellowship\y' OR
    purpose_text ~* '\ypreventable\s+harm\y' OR
    purpose_text ~* '\yhealthcare\s+quality\y' OR
    purpose_text ~* '\yhospital\s+safety\y' OR
    purpose_text ~* '\ymedical\s+training\y'
)
WHERE client_ein = '[client_ein]'
AND purpose_quality = 'VALID';
```

3. Set FALSE for non-VALID grants:
```sql
UPDATE f990_2025.calc_client_sibling_grants
SET keyword_match = FALSE
WHERE client_ein = '[client_ein]'
AND purpose_quality != 'VALID';
```

4. Verify results:
```sql
SELECT
    COUNT(*) FILTER (WHERE keyword_match = TRUE) as matches,
    COUNT(*) FILTER (WHERE keyword_match = FALSE) as non_matches,
    ROUND(100.0 * COUNT(*) FILTER (WHERE keyword_match = TRUE) / COUNT(*), 1) as match_pct
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = '[client_ein]';
```

**Note:** The SQL uses PostgreSQL word boundary regex (`\y`) to prevent false positives (e.g., "reeducation" won't match "education").

**Quality Check:**
- [ ] Some keyword matches found (typically 5-20%)
- [ ] Sample matches are relevant (spot-check)

---

## Step 3.2.4: Update Target Grant Flags

**SQL:** `04_update_target_grants.sql`

**Instructions for Claude Code CLI:**

1. Run the target grant update:
```sql
UPDATE f990_2025.calc_client_sibling_grants
SET
    is_target_grant = CASE
        WHEN keyword_match = TRUE THEN TRUE
        WHEN semantic_similarity IS NULL THEN NULL  -- Preserve uncertainty
        WHEN semantic_similarity >= 0.55 THEN TRUE
        ELSE FALSE
    END,
    target_grant_reason = CASE
        WHEN keyword_match = TRUE AND COALESCE(semantic_similarity, 0) >= 0.55 THEN 'BOTH'
        WHEN keyword_match = TRUE THEN 'KEYWORD'
        WHEN semantic_similarity >= 0.55 THEN 'SEMANTIC'
        ELSE NULL
    END
WHERE client_ein = '[client_ein]';
```

2. Verify results:
```sql
SELECT
    COUNT(*) FILTER (WHERE is_target_grant = TRUE) as target_grants,
    COUNT(*) FILTER (WHERE is_target_grant = FALSE) as non_target,
    COUNT(*) FILTER (WHERE is_target_grant IS NULL) as unknown,
    COUNT(*) FILTER (WHERE target_grant_reason = 'KEYWORD') as keyword_only,
    COUNT(*) FILTER (WHERE target_grant_reason = 'SEMANTIC') as semantic_only,
    COUNT(*) FILTER (WHERE target_grant_reason = 'BOTH') as both_signals
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = '[client_ein]';
```

**Key Insight:** NULL means "unknown", not "false". Grants without semantic_similarity (NULL or non-VALID purpose) and no keyword match have uncertain target status.

**Quality Check:**
- [ ] Some target grants identified (expect 5-15% of total)
- [ ] target_grant_reason is populated for all targets
- [ ] Unknown count reflects grants without analyzable purpose text

---

## Final Verification

Run `06_verify_quality.sql` to check all aspects:

```sql
-- Summary of calc_client_sibling_grants
SELECT
    COUNT(*) as total_grants,
    COUNT(DISTINCT foundation_ein) as unique_foundations,
    COUNT(DISTINCT sibling_ein) as unique_siblings,
    COUNT(*) FILTER (WHERE is_target_grant = TRUE) as target_grants,
    COUNT(*) FILTER (WHERE is_first_grant = TRUE AND is_target_grant = TRUE) as target_first_grants,
    ROUND(AVG(semantic_similarity)::numeric, 3) as avg_similarity
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = '[client_ein]';
```

---

## PSMF Example Results

| Metric | Value |
|--------|-------|
| Total grants | 298 |
| Unique foundations | ~170 |
| Unique siblings | 91 |
| VALID purpose | ~260 (87%) |
| Semantic similarity range | -0.014 to 0.499 |
| Target grants | TBD (after keywords) |

**Note:** PSMF's specific `target_grant_purpose` (fellowship/clinical education) yields lower semantic similarity scores than a broad mission match would. This is expected and correct - keyword matching will capture additional relevant grants.

---

*Task file created 2026-01-13*
