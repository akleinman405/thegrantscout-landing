# Phase 3: Foundation Discovery Guide

**Version:** 4.0
**Created:** 2026-01-16
**Status:** Production Ready
**Replaces:** Phase 3 sections of GUIDE_2026-01-13_PSMF_report_step_by_step.md

---

## Table of Contents

1. [Overview](#1-overview)
2. [Key Concepts](#2-key-concepts)
3. [Phase 3.0: Semantic Framing](#3-phase-30-semantic-framing)
4. [Phase 3.1: Sibling Discovery](#4-phase-31-sibling-discovery)
5. [Phase 3.1.5: Foundation Classification](#5-phase-315-foundation-classification)
6. [Phase 3.2: Grant Population](#6-phase-32-grant-population)
7. [Phase 3.3: Scoring & Ranking](#7-phase-33-scoring--ranking)
8. [Phase 3.4: Eligibility Enrichment](#8-phase-34-eligibility-enrichment)
9. [Phase 3.5: Final Selection](#9-phase-35-final-selection)
10. [Edge Cases by Nonprofit Type](#10-edge-cases-by-nonprofit-type)
11. [Troubleshooting](#11-troubleshooting)
12. [Schema Reference](#12-schema-reference)

---

## 1. Overview

**Goal:** Identify foundations most likely to fund the client by analyzing who funded similar organizations for similar purposes.

### The Core Insight

Foundations that gave **TARGET GRANTS** (matching purpose) to **SIBLINGS** (similar nonprofits) for the **FIRST TIME** in the client's **GEOGRAPHY** are the strongest prospects. We call these "Best Prospects."

### Key Change from Previous Process

**Old Process:** Score all foundations by fit, then eliminate inaccessible ones late (Phase 3.4)
- Problem: 78% of "gold standard" foundations were invite-only, wasting significant effort

**New Process:** Classify foundations by accessibility early (Phase 3.1.5), then process by tier
- Tier A (Open): Full processing, primary report section
- Tier B (Relationship-Required): Lightweight processing, secondary report section
- Tier C (Dormant): Minimal processing, monitor only

### Expected Outcomes

| Metric | Target |
|--------|--------|
| Tier A prospects identified | 8-15 |
| Tier B relationship targets | 5-10 |
| Total processing time | < 45 minutes |
| Prospects eliminated as inaccessible | 0 (classified, not eliminated) |

---

## 2. Key Concepts

### Terminology

| Term | Definition |
|------|------------|
| **Sibling** | Nonprofit with similar mission (similarity >= threshold) and comparable budget |
| **Target Grant** | Grant whose purpose matches client's work (keyword match OR semantic >= 0.55) |
| **Best Fit** | Foundation with target grants to siblings (measures alignment) |
| **Best Prospect** | Best Fit + Accessible + Client Eligible (measures actionability) |
| **Tier A** | Open to applications per IRS + website verification |
| **Tier B** | "Relationship-required" - high fit but needs introduction |
| **Tier C** | Dormant, captive, or explicitly closed |
| **Viability Score** | 0-100 score combining accessibility, capacity, and recency |
| **Prospect Score** | Fit Score × Viability Score (final ranking metric) |

### The Accessibility Reality

The IRS 990-PF question "only_contri_to_preselected_ind" indicates whether a foundation self-reports as invite-only. However:
- This is self-reported and reflects current practice, not legal restriction
- ~60-70% of foundation grants come from relationships, not applications
- Foundations CAN and DO fund new organizations through introductions
- A high-fit Tier B foundation may be more valuable than a low-fit Tier A

**Therefore:** We classify for processing efficiency but never eliminate based solely on IRS indicator.

---

## 3. Phase 3.0: Semantic Framing

**Purpose:** Establish search parameters before running queries.

### Step 3.0.1: Extract Key Terms

From the client's questionnaire and IRS mission, identify:
- Primary program type (e.g., "vocational training," "fellowship program")
- Target population (e.g., "adults with disabilities," "healthcare professionals")
- Geographic scope (local, regional, national, international)

### Step 3.0.2: Classify Nonprofit Type

| Type | Characteristics | Special Handling |
|------|-----------------|------------------|
| **Local/Community** | Single county/city service area | Lower thresholds, include local community foundation |
| **Regional** | Multi-county or single state | Standard thresholds |
| **National** | Multi-state or national programs | Higher thresholds, exclude hyper-local funders |
| **International** | Global programs | Specialized funder pool |
| **Identity-Based** | Jewish, faith, disability, LGBTQ+, ethnic | Apply 0.75/0.25 fit/viability weights |
| **Niche Sector** | Arts, environment, health research | Include sector-specific databases |

### Step 3.0.3: Create Target Grant Purpose

Write a 1-2 sentence description of what a matching grant would fund:

**Template:**
> "[Program type] providing [services] to [target population] in [geography]"

**Example (Friendship Circle):**
> "Programs serving people with disabilities including employment training, vocational services, job placement, recreation, social inclusion, and community integration"

**Lesson Learned (PSMF):** If initial target purpose is too narrow (< 20 grants >= 0.55 similarity), broaden to sector-level framing. Document both versions.

### Step 3.0.4: Define Matching Keywords

Identify 8-12 keywords that should appear in matching grant purposes:

**Example (Friendship Circle):**
```
disability, special needs, vocational, employment, job training,
inclusion, developmental, jewish, recreation, social enterprise
```

### Quality Checks
- [ ] Target grant purpose is specific enough to be meaningful
- [ ] Target grant purpose is broad enough to find 20+ matches
- [ ] Keywords cover both program AND population terms
- [ ] Nonprofit type classification is accurate

---

## 4. Phase 3.1: Sibling Discovery

**Purpose:** Find similar nonprofits whose funders we'll analyze.

### Step 3.1.1: Find Siblings via Semantic Search

**Query pattern:**
```sql
-- Using pgvector similarity search
INSERT INTO f990_2025.calc_client_siblings
SELECT
    '{client_ein}' as client_ein,
    r.ein as sibling_ein,
    r.name as sibling_name,
    r.state as sibling_state,
    r.total_revenue as sibling_revenue,
    1 - (e.embedding <=> '{client_embedding}'::vector) as similarity
FROM f990_2025.emb_nonprofit_missions e
JOIN f990_2025.nonprofit_returns r ON r.ein = e.ein
WHERE 1 - (e.embedding <=> '{client_embedding}'::vector) >= {similarity_threshold}
  AND r.total_revenue BETWEEN {client_revenue} * 0.2 AND {client_revenue} * 5.0
ORDER BY similarity DESC
LIMIT 150;
```

### Parameter Selection by Nonprofit Type

| Type | Similarity Threshold | Budget Range | Expected Siblings |
|------|---------------------|--------------|-------------------|
| General | 0.50 | 0.2x - 5.0x | 80-150 |
| Identity-Based | 0.60 | 0.1x - 10.0x | 30-80 |
| Niche Sector | 0.55 | 0.2x - 5.0x | 50-100 |
| Local | 0.50 | 0.1x - 5.0x | 50-120 |
| Startup (< $500K) | 0.50 | 0.1x - 10.0x | 60-100 |

**Lesson Learned (Friendship Circle):** For specialized missions, RAISE similarity threshold (0.72) to improve quality. Verify top 10 siblings are genuinely similar before proceeding.

### Step 3.1.2: Verify Sibling Quality

Spot-check top 10 siblings:
- [ ] Missions are genuinely similar
- [ ] Program types align
- [ ] No obvious mismatches (e.g., hospital vs. small nonprofit)

**If quality is poor:** Adjust similarity threshold or budget range, re-run.

---

## 5. Phase 3.1.5: Foundation Classification

**Purpose:** Classify foundations by accessibility BEFORE expensive grant processing.

### Step 3.1.5.1: Create/Refresh Accessibility View

```sql
-- Ensure mv_accessible_foundations is current
REFRESH MATERIALIZED VIEW f990_2025.mv_accessible_foundations;
```

### Step 3.1.5.2: Identify Candidate Foundations

```sql
-- Get all foundations that funded siblings
CREATE TEMP TABLE temp_candidate_foundations AS
SELECT DISTINCT fg.foundation_ein
FROM f990_2025.fact_grants fg
WHERE fg.recipient_ein IN (
    SELECT sibling_ein FROM f990_2025.calc_client_siblings
    WHERE client_ein = '{client_ein}'
);
```

### Step 3.1.5.3: Classify by Tier

```sql
-- Classify each candidate foundation
INSERT INTO f990_2025.calc_client_foundation_tiers
SELECT
    '{client_ein}' as client_ein,
    cf.foundation_ein,
    CASE
        -- Tier A: Open to applications
        WHEN COALESCE(df.verified_accepts_applications, maf.irs_accepts_applications) = TRUE
        THEN 'A'
        -- Tier B: Relationship-required but active and substantial
        WHEN maf.irs_accepts_applications = FALSE
             AND fg_stats.total_grants >= 5
             AND fg_stats.unique_recipients >= 3
             AND df.assets >= 500000
        THEN 'B'
        -- Tier C: Dormant, captive, or minimal
        ELSE 'C'
    END as tier,
    maf.irs_accepts_applications,
    df.verified_accepts_applications,
    df.assets,
    fg_stats.total_grants,
    fg_stats.unique_recipients,
    fg_stats.last_grant_year
FROM temp_candidate_foundations cf
LEFT JOIN f990_2025.mv_accessible_foundations maf ON maf.ein = cf.foundation_ein
LEFT JOIN f990_2025.dim_foundations df ON df.ein = cf.foundation_ein
LEFT JOIN (
    SELECT foundation_ein,
           COUNT(*) as total_grants,
           COUNT(DISTINCT recipient_ein) as unique_recipients,
           MAX(tax_year) as last_grant_year
    FROM f990_2025.fact_grants
    WHERE tax_year >= 2019
    GROUP BY foundation_ein
) fg_stats ON fg_stats.foundation_ein = cf.foundation_ein;
```

### Step 3.1.5.4: Check Minimum Viable Threshold

```sql
-- Count Tier A foundations
SELECT COUNT(*) as tier_a_count
FROM f990_2025.calc_client_foundation_tiers
WHERE client_ein = '{client_ein}' AND tier = 'A';
```

**Minimum Thresholds by Type:**
| Nonprofit Type | Minimum Tier A | Action if Below |
|----------------|----------------|-----------------|
| General | 8 | Broaden search parameters |
| Identity-Based | 4 | Include identity-aligned Tier B as "A*" |
| Local | 5 | Include community foundation |
| National | 12 | Expand geographic scope |

**If below minimum:** See [Troubleshooting](#11-troubleshooting).

### Quality Checks
- [ ] Tier A count meets minimum threshold
- [ ] No obvious Tier A foundations misclassified as B/C
- [ ] Tier B includes high-fit foundations worth relationship-building

---

## 6. Phase 3.2: Grant Population

**Purpose:** Gather grant history, prioritized by tier.

### Step 3.2.1: Populate Sibling Grants (Tier A Priority)

```sql
-- Insert grants from Tier A foundations first
INSERT INTO f990_2025.calc_client_sibling_grants
SELECT
    '{client_ein}' as client_ein,
    fg.foundation_ein,
    fg.recipient_ein as sibling_ein,
    fg.id as grant_id,
    fg.amount,
    fg.tax_year,
    fg.recipient_state,
    fg.purpose_text,
    -- First grant detection
    NOT EXISTS (
        SELECT 1 FROM f990_2025.fact_grants fg2
        WHERE fg2.foundation_ein = fg.foundation_ein
          AND fg2.recipient_ein = fg.recipient_ein
          AND fg2.tax_year < fg.tax_year
    ) as is_first_grant
FROM f990_2025.fact_grants fg
JOIN f990_2025.calc_client_siblings cs
    ON cs.sibling_ein = fg.recipient_ein AND cs.client_ein = '{client_ein}'
JOIN f990_2025.calc_client_foundation_tiers cft
    ON cft.foundation_ein = fg.foundation_ein AND cft.client_ein = '{client_ein}'
WHERE cft.tier = 'A'
  AND fg.tax_year >= 2018;

-- Add Tier B grants (summary mode - can be lighter processing)
INSERT INTO f990_2025.calc_client_sibling_grants
SELECT ... -- Same query but WHERE cft.tier = 'B'
```

### Step 3.2.2: Generate Semantic Similarity

Run embedding comparison between target grant purpose and each grant's purpose_text.

```python
# Python script: generate_semantic_similarity.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
target_embedding = model.encode(target_grant_purpose)

# For each grant purpose, calculate cosine similarity
# Update calc_client_sibling_grants.semantic_similarity
```

**Lesson Learned (Friendship Circle):** Initial run yielded only 4 grants >= 0.55. After broadening target purpose, found 65. **Always check result count and iterate if needed.**

### Step 3.2.3: Update Keyword Matches

```sql
UPDATE f990_2025.calc_client_sibling_grants
SET keyword_match = (
    purpose_text ILIKE ANY(ARRAY[
        '%disability%', '%special needs%', '%vocational%',
        '%employment%', '%job training%', '%inclusion%',
        '%developmental%', '%jewish%', '%recreation%', '%social enterprise%'
    ])
)
WHERE client_ein = '{client_ein}';
```

### Step 3.2.4: Update Target Grant Flags

```sql
UPDATE f990_2025.calc_client_sibling_grants
SET
    is_target_grant = (
        semantic_similarity >= 0.55
        OR keyword_match = TRUE
    ),
    target_grant_reason = CASE
        WHEN semantic_similarity >= 0.55 AND keyword_match = TRUE THEN 'BOTH'
        WHEN semantic_similarity >= 0.55 THEN 'SEMANTIC'
        WHEN keyword_match = TRUE THEN 'KEYWORD'
        ELSE NULL
    END
WHERE client_ein = '{client_ein}';
```

**Decision: AND vs OR Logic**

| Logic | Use When | Typical Result |
|-------|----------|----------------|
| OR (semantic OR keyword) | Need more prospects | 10-15% of grants flagged |
| AND (semantic AND keyword) | High precision needed | 3-8% of grants flagged |

**Lesson Learned (Friendship Circle):** Started with AND logic for precision, yielded 61 target grants. For PSMF (narrow mission), OR logic may be needed.

---

## 7. Phase 3.3: Scoring & Ranking

**Purpose:** Generate ranked prospect list.

### Step 3.3.1: Aggregate Foundation Scores

```sql
INSERT INTO f990_2025.calc_client_foundation_scores
SELECT
    '{client_ein}' as client_ein,
    g.foundation_ein,
    df.name as foundation_name,
    df.state as foundation_state,
    df.assets as foundation_total_assets,
    cft.tier,

    -- Grant metrics
    COUNT(DISTINCT g.sibling_ein) as siblings_funded,
    COUNT(*) as grants_to_siblings,
    SUM(g.amount) as total_amount_to_siblings,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY g.amount) as median_grant_size,

    -- Target grant metrics
    COUNT(*) FILTER (WHERE g.is_target_grant) as target_grants_to_siblings,
    COUNT(*) FILTER (WHERE g.is_target_grant AND g.is_first_grant) as target_first_grants,

    -- Geographic metrics
    COUNT(*) FILTER (WHERE g.recipient_state = '{client_state}') as geo_grants_to_siblings,
    COUNT(*) FILTER (WHERE g.is_target_grant AND g.recipient_state = '{client_state}') as target_geo_grants,

    -- Gold standard (Best Fit)
    COUNT(*) FILTER (
        WHERE g.is_target_grant
          AND g.is_first_grant
          AND g.recipient_state = '{client_state}'
    ) as gold_standard_grants,

    -- Recency
    MAX(g.tax_year) as most_recent_grant_year,
    MAX(g.tax_year) FILTER (WHERE g.is_target_grant) as most_recent_target_year

FROM f990_2025.calc_client_sibling_grants g
JOIN f990_2025.dim_foundations df ON df.ein = g.foundation_ein
JOIN f990_2025.calc_client_foundation_tiers cft
    ON cft.foundation_ein = g.foundation_ein AND cft.client_ein = g.client_ein
WHERE g.client_ein = '{client_ein}'
GROUP BY g.foundation_ein, df.name, df.state, df.assets, cft.tier;
```

### Step 3.3.2: Calculate Composite Scores

```sql
-- Calculate viability score (0-100)
UPDATE f990_2025.calc_client_foundation_scores
SET viability_score =
    CASE tier
        WHEN 'A' THEN
            LEAST(100,
                (CASE WHEN most_recent_grant_year >= 2023 THEN 40 ELSE 20 END) +
                (CASE WHEN foundation_total_assets >= 10000000 THEN 30
                      WHEN foundation_total_assets >= 1000000 THEN 20
                      ELSE 10 END) +
                (CASE WHEN siblings_funded >= 3 THEN 20 ELSE siblings_funded * 5 END) +
                10  -- Tier A bonus
            )
        WHEN 'B' THEN
            LEAST(70,  -- Capped at 70 for Tier B
                (CASE WHEN most_recent_grant_year >= 2023 THEN 30 ELSE 15 END) +
                (CASE WHEN foundation_total_assets >= 10000000 THEN 25 ELSE 15 END) +
                (CASE WHEN siblings_funded >= 3 THEN 15 ELSE siblings_funded * 5 END)
            )
        ELSE 0  -- Tier C
    END
WHERE client_ein = '{client_ein}';

-- Calculate fit score (0-100 based on target grants)
UPDATE f990_2025.calc_client_foundation_scores
SET fit_score = LEAST(100,
    (gold_standard_grants * 25) +
    (target_first_grants * 15) +
    (target_geo_grants * 10) +
    (target_grants_to_siblings * 5)
)
WHERE client_ein = '{client_ein}';

-- Calculate final prospect score
UPDATE f990_2025.calc_client_foundation_scores
SET prospect_score = (fit_score * 0.6) + (viability_score * 0.4)
WHERE client_ein = '{client_ein}';
```

**For Identity-Based Missions:** Use 0.75/0.25 weights:
```sql
SET prospect_score = (fit_score * 0.75) + (viability_score * 0.25)
```

---

## 8. Phase 3.4: Eligibility Enrichment

**Purpose:** Verify top prospects and gather actionable details.

### Step 3.4.1: Select Foundations for Enrichment

```sql
-- Top Tier A foundations
SELECT * FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = '{client_ein}' AND tier = 'A'
ORDER BY prospect_score DESC
LIMIT 20;

-- Top Tier B foundations (for relationship section)
SELECT * FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = '{client_ein}' AND tier = 'B'
ORDER BY fit_score DESC
LIMIT 10;
```

### Step 3.4.2: Research Each Foundation

For each Tier A foundation, verify:

| Field | Source | Required |
|-------|--------|----------|
| geo_eligible | Website, 990 giving patterns | Yes |
| open_to_applicants | Website (check for LOI/application) | Yes |
| client_eligible | Website guidelines vs. client profile | Yes |
| eligibility_notes | Manual research | Yes |
| application_url | Website | If available |
| deadline | Website | If available |
| contact_email | Website | If available |

**Lesson Learned (Friendship Circle - Gilbert Foundation):** IRS said `preselected = FALSE`, website said "Does not accept unsolicited requests." **Always verify via website.**

### Step 3.4.3: Update Verification Status

```sql
UPDATE f990_2025.calc_client_foundation_scores
SET
    geo_eligible = TRUE,
    open_to_applicants = TRUE,  -- or FALSE if website contradicts IRS
    client_eligible = TRUE,
    eligibility_notes = 'Accepts applications via website. Focus: children/youth development.',
    reviewed_at = NOW()
WHERE client_ein = '{client_ein}' AND foundation_ein = '203198081';
```

### Step 3.4.4: Tier B Relationship Research

For Tier B foundations, gather:
- Board member names (from 990)
- Overlap with client's board/network
- Mutual funders (who funded both client and foundations' other grantees)
- Events where foundation staff participate

---

## 9. Phase 3.5: Final Selection

**Purpose:** Select foundations for report.

### Step 3.5.1: Final Tier A List

```sql
SELECT
    foundation_name,
    foundation_state,
    foundation_total_assets,
    prospect_score,
    target_grants_to_siblings,
    gold_standard_grants,
    eligibility_notes
FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = '{client_ein}'
  AND tier = 'A'
  AND open_to_applicants = TRUE
  AND client_eligible = TRUE
ORDER BY prospect_score DESC
LIMIT 15;
```

### Step 3.5.2: Final Tier B List

```sql
SELECT
    foundation_name,
    foundation_state,
    foundation_total_assets,
    fit_score,
    target_grants_to_siblings,
    eligibility_notes as relationship_notes
FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = '{client_ein}'
  AND tier = 'B'
ORDER BY fit_score DESC
LIMIT 10;
```

### Quality Checks
- [ ] At least 8 Tier A foundations in final list
- [ ] All Tier A foundations have verified `open_to_applicants = TRUE`
- [ ] All Tier A foundations have `client_eligible = TRUE`
- [ ] Tier B list includes relationship path notes
- [ ] No duplicates between Tier A and Tier B

---

## 10. Edge Cases by Nonprofit Type

### Local/Community Nonprofits

**Characteristics:** Single county/city service area

**Adjustments:**
- Auto-include local community foundation as Tier A
- Lower minimum Tier A threshold to 5
- Weight geographic match at 1.5x
- Include regional family foundations in Tier B even if "preselected only"

**Example Clients:** Friendship Circle San Diego, local food banks, neighborhood centers

### National Nonprofits

**Characteristics:** Multi-state or national programs

**Adjustments:**
- Raise minimum Tier A threshold to 12
- Exclude foundations with `funded_states < 5` unless mission-specific
- Prioritize federated funders (United Way, corporate giving programs)
- De-emphasize geographic match in scoring

**Example Clients:** PSMF (global), national advocacy organizations

### Identity-Based Missions

**Characteristics:** Jewish, faith-based, disability, LGBTQ+, ethnic-specific

**Adjustments:**
- Apply 0.75/0.25 fit/viability weight split
- Lower minimum Tier A threshold to 4
- Auto-promote identity-aligned Tier B foundations to "A*"
- Include identity-specific foundation databases
- Accept smaller prospect pools

**Example Clients:** Friendship Circle (Jewish + disability), faith-based schools

### Startups (< 3 Years Old)

**Characteristics:** Limited track record, may lack 3 years of 990s

**Adjustments:**
- De-prioritize foundations requiring 3+ years of audited financials
- Boost community foundations and "emerging organization" programs
- Emphasize Tier B relationship introductions
- Include fiscal sponsor network analysis

### Large Established Nonprofits (> $5M Budget)

**Characteristics:** Substantial infrastructure, seeking major grants

**Adjustments:**
- Exclude foundations with median grant < $10K
- Include corporate foundation prospects
- Add "renewal likelihood" scoring
- Consider multi-year and capital campaign potential

---

## 11. Troubleshooting

### Problem: Tier A Count Below Minimum

**Symptoms:** After Phase 3.1.5, fewer than 8 Tier A foundations

**Solutions (in order):**
1. **Broaden semantic framing** - Expand target purpose to sector level
2. **Switch to OR logic** - Accept semantic OR keyword match
3. **Lower similarity threshold** - Reduce from 0.55 to 0.50
4. **Expand geographic scope** - Include adjacent states
5. **Promote Tier B** - Add highest-fit Tier B as "A*" with relationship notes

### Problem: Semantic Similarity Too Narrow

**Symptoms:** < 20 grants >= 0.55 similarity

**Lesson (PSMF):** "Healthcare training program providing clinical education fellowships" yielded max 0.499 similarity.

**Solution:** Broaden to: "Healthcare education and training programs including fellowships, residencies, and professional development for medical professionals"

### Problem: IRS Indicator Contradicts Website

**Symptoms:** Foundation shows `preselected = FALSE` but website says "by invitation only"

**Lesson (Gilbert Foundation):** The Gilbert Foundation had this exact issue.

**Solution:**
1. Trust website over IRS indicator
2. Update `verified_accepts_applications = FALSE`
3. Move to Tier B with note: "Website indicates invitation-only despite IRS filing"
4. Include in relationship-building section

### Problem: Strong Fit But No CA Grants

**Symptoms:** Foundation has many target grants but none in client's state

**Analysis:** May still be approachable if:
- They fund neighboring states
- They have expanding geographic footprint
- Their mission explicitly includes underserved regions

**Solution:** Include in Tier A if other signals strong, note: "No prior CA grants but pattern suggests openness to expansion"

### Problem: Prior Funder Appears in Results

**Symptoms:** Foundation that already funds client appears in prospect list

**Example (Ekstrom → Friendship Circle):** Ekstrom funded "Friendship Circle CA" in 2020 - might be same or sister org.

**Solution:**
1. Check if same EIN as client → Exclude as prior funder
2. If different EIN but similar name → Note as "possible prior relationship"
3. If same organization → Move to "renewal" category, not new prospect

---

## 12. Schema Reference

### Core Tables

| Table | Purpose |
|-------|---------|
| `calc_client_siblings` | Similar nonprofits for this client |
| `calc_client_sibling_grants` | Grants to siblings with flags |
| `calc_client_foundation_tiers` | Tier A/B/C classification |
| `calc_client_foundation_scores` | Final scores and enrichment |
| `mv_accessible_foundations` | Pre-computed accessibility view |

### Key Columns in calc_client_foundation_scores

| Column | Type | Description |
|--------|------|-------------|
| client_ein | VARCHAR(9) | Client identifier |
| foundation_ein | VARCHAR(9) | Foundation identifier |
| tier | CHAR(1) | A, B, or C |
| fit_score | INTEGER | 0-100 based on target grants |
| viability_score | INTEGER | 0-100 based on accessibility/capacity |
| prospect_score | NUMERIC | Final ranking score |
| gold_standard_grants | INTEGER | Target + first-time + geography |
| geo_eligible | BOOLEAN | Does foundation fund client's state? |
| open_to_applicants | BOOLEAN | Verified accepts applications? |
| client_eligible | BOOLEAN | Client meets foundation requirements? |
| eligibility_notes | TEXT | Manual research notes |
| reviewed_at | TIMESTAMP | When enrichment was completed |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 4.0 | 2026-01-16 | Major revision: Added Phase 3.0, 3.1.5, Tier classification, edge cases |
| 3.0 | 2026-01-13 | Original PSMF-specific guide |

---

*Guide created 2026-01-16 based on learnings from PSMF and Friendship Circle San Diego*
