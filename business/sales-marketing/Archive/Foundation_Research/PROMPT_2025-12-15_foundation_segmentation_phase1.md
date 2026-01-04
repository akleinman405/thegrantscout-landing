# PROMPT: Capacity Building Foundation Segmentation Research (Phase 1)

**Date:** 2025-12-15  
**For:** Claude Code CLI  
**Schema:** f990_2025

---

## Standards

Follow CLAUDE.md conventions for file naming, output format, and lessons learned.

---

## Situation

TheGrantScout is exploring B2B sales to foundations - offering our grant discovery service to foundations who would then provide it to their grantees. Need to identify which foundations to target first. This is Phase 1: research and segmentation. Phase 2 will build the actual outreach list.

**Research folder:** `C:\TheGrantScout\4. Sales & Marketing\Launch Strategy\`

---

## Tasks

### Part A: Review Existing Research

Look through `Launch Strategy` folder and subfolders for any existing research on:
- Capacity building foundations
- Foundation outreach strategy
- Foundation contact lists
- Prior analysis of foundation segments

Summarize what's already been done and what gaps remain.

### Part B: Discovery Queries

Answer these questions using f990_2025 database:

**Foundation Size & Volume**
1. How many foundations have 10+, 50+, 100+, 200+ unique grantees (distinct recipient EINs)?
2. What's the distribution of foundations by total annual giving ($100K-$500K, $500K-$1M, $1M-$5M, $5M+)?
3. How many foundations have given grants in the last 2 years (2023-2024)?

**Capacity Building Patterns**
4. How many grants contain capacity-building keywords in purpose_text? (search: "capacity building", "technical assistance", "organizational development", "general operating", "operating support", "infrastructure")
5. Which 20 foundations give the MOST capacity building grants?
6. What % of foundations have given at least one capacity building grant?

**Intermediary/Consultant Funding**
7. How many grants go to recipients with consultant/intermediary name patterns? (search recipient_name for: "Consulting", "Advisors", "Associates", "LLC", "Partners", "Group", "Solutions")
8. How many grants have purpose text suggesting consultant work? (search: "evaluation", "consulting", "assessment", "technical assistance", "training")
9. Which 20 foundations fund intermediaries most frequently?

**Geographic Distribution**
10. Top 10 states by number of capacity-building foundations
11. For California specifically: how many foundations with 20+ grantees?
12. For New York specifically: how many foundations with 20+ grantees?
13. How many foundations give >80% of grants to one state (regional) vs <50% to any single state (national)?

**Grantee Type Concentration**
14. Can we identify foundations that specialize in specific sectors? (e.g., >50% of grants to education, health, youth)
15. What recipient NTEE codes are most common? (if recipient_ein links to nonprofit_returns)

**Officer/Contact Data**
16. What officer titles are most common in the `officers` table for foundations?
17. How many foundations have officers with titles containing: "Program", "Executive", "Director", "Grants"?
18. Sample 10 foundations with their officer lists to assess data quality

### Part C: Propose Segmentation Framework

Based on discovery findings, propose 5-6 segments to test:

**Required segments:**
1. **Size segment** - Large vs small foundations
2. **Volume segment** - High grantee count vs low
3. **Geographic segment** - National vs regional (+ 1-2 specific states)
4. **Intermediary segment** - Foundations that fund consultants/intermediaries
5. **Baseline segment** - Random currently-active foundations (control group)
6. **Grantee-type segment** - Foundations focused on specific nonprofit sectors

For each segment, define:
- Specific criteria (e.g., "50+ grantees, CA-based, at least 1 capacity building grant")
- Estimated count of qualifying foundations
- Rationale for testing this segment

### Part D: Prioritization Recommendation

Recommend which 3-4 segments to prioritize for initial outreach, based on:
- Likely receptiveness (capacity building history)
- Volume opportunity (grantee count)
- Accessibility (regional might be easier than national)
- Data quality (do we have officer contacts?)

---

## Output

**File:** `REPORT_2025-12-15_foundation_segmentation_research.md`

### Sections:

1. **Executive Summary** - Key findings in 5 bullets
2. **Existing Research Review** - What's in Launch Strategy folder
3. **Discovery Findings** - Answers to all questions with data tables
4. **Proposed Segments** - 5-6 segment definitions with criteria
5. **Prioritization Recommendations** - Which segments to target first and why
6. **Data Quality Notes** - Any gaps or issues (missing officers, etc.)
7. **Phase 2 Inputs** - Exact SQL criteria for each segment to use in Phase 2
8. **Lessons Learned** - What worked, what was harder, recommendations

---

## Reference Queries

```sql
-- Grantee count per foundation
SELECT foundation_ein, COUNT(DISTINCT recipient_ein) as grantee_count
FROM f990_2025.fact_grants
WHERE recipient_ein IS NOT NULL
GROUP BY foundation_ein
ORDER BY grantee_count DESC;

-- Capacity building grants
SELECT COUNT(*) 
FROM f990_2025.fact_grants
WHERE purpose_text ILIKE ANY(ARRAY[
    '%capacity building%', 
    '%technical assistance%',
    '%organizational development%',
    '%general operating%',
    '%operating support%'
]);

-- Officers by title pattern
SELECT title_txt, COUNT(*) 
FROM f990_2025.officers
WHERE ein IN (SELECT DISTINCT ein FROM f990_2025.pf_returns)
GROUP BY title_txt
ORDER BY COUNT(*) DESC
LIMIT 50;
```

---

## Notes

- Focus on foundations currently giving (tax_year >= 2022)
- All segments should have capacity building history as baseline filter
- Baseline/random segment is exception - just needs to be currently active
- Officer data quality may vary - note gaps for Phase 2 planning
