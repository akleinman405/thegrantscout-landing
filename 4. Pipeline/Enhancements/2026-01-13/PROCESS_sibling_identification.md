# PROCESS: Sibling Nonprofit Identification

**Date:** 2026-01-13
**Version:** 2.0
**Purpose:** Document the methodology for finding high-quality sibling nonprofits

---

## What Is a Sibling Nonprofit?

A **sibling nonprofit** is an organization that:
1. Does similar work to the client
2. Competes for the same foundation funding
3. Has received grants the client would also be a good fit for

**Goal:** Find foundations that fund siblings → those foundations are likely good prospects for the client.

---

## Step 1: Build Client Profile

Before finding siblings, understand the client deeply:

### 1.1 Core Mission Characteristics
- What is their primary cause/focus area?
- Are they single-issue or multi-program?
- What's their geographic scope? (local/state/national/global)
- What's their approach? (direct service, education, advocacy, research, coalition-building)

### 1.2 Priority Program for Funding
- Which program are they seeking funding for specifically?
- What type of grants would fund that program?
- Example: PSMF's Fellowship Program needs education/training grants

### 1.3 Operational Scale
- Annual revenue/budget range
- Staff size
- Similar-sized orgs compete for similar grant sizes

### 1.4 Key Activities (for keyword matching)
Extract keywords from:
- Mission statement
- Program descriptions
- Priority program details

---

## Step 2: Define Sibling Criteria

Based on client profile, define what makes a TRUE sibling:

### 2.1 PSMF Example Criteria

| Criterion | Why It Matters |
|-----------|----------------|
| Patient safety / healthcare quality mission | Core cause alignment |
| Multi-program structure | Single-issue orgs attract different funders |
| Education/training component | Match fellowship focus |
| Evidence-based approach | Match toolkit/best practices model |
| Hospital/health system engagement | Coalition-building funders |
| Budget $100K-$5M | Similar grant competitiveness |
| National/global scope | Not purely local |

### 2.2 Anti-Patterns (False Positives to Avoid)

| Pattern | Why It's Wrong |
|---------|---------------|
| Same keywords, different sector | "Training + safety" matched labor unions |
| Single-issue disease foundations | Different funding ecosystem |
| Service delivery orgs | Different model than education/advocacy |
| Very large orgs ($50M+) | Different funder tier |
| Local-only orgs | If client is national/global |

---

## Step 3: Database Search Strategy

### 3.1 Keyword-Based Search

```sql
SELECT DISTINCT ON (ein)
    ein, organization_name, state, total_revenue,
    mission_description, ntee_code
FROM f990_2025.nonprofit_returns
WHERE
    total_revenue BETWEEN {min_budget} AND {max_budget}
    AND (
        -- Core mission keywords
        LOWER(organization_name) LIKE '%{keyword1}%'
        OR LOWER(mission_description) LIKE '%{keyword1}%'
        OR LOWER(mission_description) LIKE '%{keyword2}%'
        -- Add more keywords...
    )
    AND LEFT(ntee_code, 1) IN ({allowed_ntee_categories})
ORDER BY ein, total_revenue DESC;
```

### 3.2 NTEE Category Filtering

Filter by relevant NTEE major categories:
- E = Healthcare
- F = Mental Health
- G = Diseases/Disorders
- H = Medical Research
- B = Education (for education-focused clients)

### 3.3 Name-Based Search

Search for organizations with sector keywords in their name:
- "[State] Patient Safety"
- "[Specialty] Quality Improvement"
- "Healthcare Quality"
- "Patient Safety Organization"

---

## Step 4: External Source Validation

### 4.1 Industry Registries
- **AHRQ PSO List:** ~90 federally-listed Patient Safety Organizations
- **State PSO websites:** Each state may have patient safety centers
- **Professional associations:** Member directories

### 4.2 Conference/Summit Attendees
- Who speaks at relevant conferences?
- Who sponsors events in the client's space?

### 4.3 Foundation Grant Databases
- Who else do major funders in this space support?
- Commonwealth Fund, RWJF, etc. grantee lists

### 4.4 Known Reference Organizations
Cross-reference with well-known orgs in the space:
- Institute for Healthcare Improvement (reference, even if too large)
- Leapfrog Group
- State-level patient safety centers

---

## Step 5: Manual Verification

For each candidate, verify against criteria:

### 5.1 Verification Checklist
- [ ] Mission explicitly mentions core cause (patient safety, quality, etc.)
- [ ] Multiple programs listed in 990 Part III
- [ ] Education/training mentioned
- [ ] Works with target institutions (hospitals, health systems)
- [ ] Active (filed 990 in last 2 years)
- [ ] Budget in target range
- [ ] Geographic scope appropriate

### 5.2 Tiered Classification

| Tier | Description | Confidence |
|------|-------------|------------|
| Tier 1 | Core mission match, multi-program, all criteria met | High |
| Tier 2 | Strong match, may be narrower specialty or different model | Medium-High |
| Tier 3 | Partial match, keep for volume but flag as marginal | Medium |
| Remove | False positive, wrong sector, weak alignment | N/A |

---

## Step 6: Load to Database

### 6.1 Clear Old Data
```sql
DELETE FROM f990_2025.calc_client_siblings
WHERE client_ein = '{client_ein}';
```

### 6.2 Insert Verified Siblings
```sql
INSERT INTO f990_2025.calc_client_siblings
    (client_ein, sibling_ein, similarity_score, similarity_method)
VALUES
    ('{client_ein}', '{sibling_ein}', {score}, 'manual_verified')
ON CONFLICT (client_ein, sibling_ein) DO UPDATE SET
    similarity_score = EXCLUDED.similarity_score,
    similarity_method = EXCLUDED.similarity_method;
```

### 6.3 Similarity Scores
- 0.90-1.00: Tier 1 core matches
- 0.75-0.89: Tier 2 strong matches
- 0.60-0.74: Tier 3 marginal matches

---

## Lessons Learned (PSMF Case Study)

### What Worked
1. **Name-based search** found most PSOs directly ("Patient Safety" in name)
2. **NTEE filtering** eliminated most false positives
3. **Tiered approach** allowed prioritization without losing candidates
4. **External sources** (AHRQ PSO list) added high-quality candidates

### What Didn't Work
1. **Embedding-only search** had 20-30% false positives (labor unions, athletic clubs)
2. **Budget-only filtering** missed mission misalignment
3. **Too-narrow keywords** missed quality improvement organizations

### Optimal Approach
1. Start with **name-based search** for sector keywords
2. Expand with **mission keyword search** in nonprofit_returns
3. Validate with **external sources** (registries, associations)
4. **Manually verify** each candidate against checklist
5. **Tier and score** based on alignment strength

---

## Quality Metrics

| Metric | Target | PSMF Result |
|--------|--------|-------------|
| False positive rate | <10% | 0% (manual verified) |
| Tier 1 coverage | 40-60% of total | 50% (20/40) |
| Budget range coverage | Client ±10x | $88K-$4.9M ✓ |
| Geographic diversity | Multiple states | 25+ states ✓ |
| NTEE category diversity | 2-3 related categories | E, B, H, F ✓ |

---

## Files Reference

| File | Purpose |
|------|---------|
| PSMF_organization_profile.md | Client deep-dive template |
| PSMF_verified_siblings_v2.md | Verified sibling list with SQL |
| REPORT_2026-01-13.2_sibling_quality_improvement.md | Process evolution notes |

---

*Process documented 2026-01-13 based on PSMF sibling identification experience*
