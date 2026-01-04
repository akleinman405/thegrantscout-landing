# REPORT: Semantic Signal Investigation

**Date:** 2025-12-20
**Prerequisite:** Part 1 baseline results

---

## Executive Summary

Investigation into why semantic similarity underperformed (4x random vs 52x for collaborative filtering) revealed that **81% of grant purposes are too generic or short to provide meaningful signal**. Filtering to specific purposes improved performance from 4x to 7x random, but this is still far below collaborative filtering (52x).

**Recommendation:** Deprioritize semantic signal in the matching algorithm. It adds complexity without meaningful improvement.

---

## Grant Purpose Quality Analysis

### Distribution of Purpose Quality

| Category | Grants | Percentage | Description |
|----------|--------|------------|-------------|
| too_short | 4,360,814 | 52.5% | Less than 30 characters |
| specific | 1,568,875 | 18.9% | Meaningful, unique text |
| generic_general | 1,454,026 | 17.5% | "General support", "Operating" |
| generic_start | 739,538 | 8.9% | Starts with "Charitable", "Donation" |
| too_vague | 187,178 | 2.3% | "See attachment", "Per schedule" |
| empty | 219 | 0.0% | NULL or empty string |

**Finding:** Only 18.9% of grants have purpose text suitable for semantic matching.

### Sample Purpose Text

**Generic Examples (unusable):**
- "GENERAL PURPOSE"
- "CHARITABLE"
- "DONATION"

**Specific Examples (usable):**
- "For religious education purposes"
- "To support diabetes research and patient education programs"
- "Capital campaign for new community health center"

---

## Filtered Semantic Test Results

### Filtering Criteria

Included grants where:
- `length(purpose_text) >= 50`
- NOT matching `'general.*(support|operating|purpose)'`
- NOT starting with `'charitable|contribution|grant|donation'`
- NOT `'see|per schedule'`

### Filter Impact

| Metric | Before Filter | After Filter |
|--------|---------------|--------------|
| Grants | 6,424,973 | 567,760 |
| Percentage kept | 100% | 8.8% |

### Performance Comparison

| Version | Hit Rate@100 | vs Random | Improvement |
|---------|--------------|-----------|-------------|
| Unfiltered (Part 1) | 2.00% | 4x | baseline |
| Filtered (specific only) | 3.57% | 7x | 1.8x |

**Note:** Only 56% of test nonprofits had enough filtered grant data to test.

---

## Root Cause Analysis

### Why Semantic Underperforms

1. **Data Quality:** 81% of grant purposes are uninformative
   - Generic text ("general support") dominates
   - Short entries lack context
   - Embeddings of generic text don't discriminate

2. **Coverage Loss:** Filtering removes 91% of grants
   - Many foundations only have generic purpose entries
   - Reduces foundation coverage significantly

3. **Embedding Averaging:** Averaging embeddings loses specificity
   - A foundation with 100 grants averaging to generic vector
   - Individual grant specificity is lost

### Why Collaborative Works Better

1. **Behavioral Signal:** Based on actual funding patterns, not text
2. **No Data Quality Issue:** EINs are structured, reliable
3. **Network Effects:** Captures implicit relationships

---

## Recommendation

### Primary: Exclude Semantic from Production Algorithm

**Rationale:**
- 7x random is far below collaborative (52x)
- Adds computational complexity (embedding lookups, similarity calculations)
- Limited coverage (only 9% of grants usable after filtering)

### Alternative: Future Improvement

If semantic is desired in future:
1. **Mission-based matching:** Use nonprofit mission statements instead of grant purposes
2. **Foundation profiles:** Hand-curate foundation descriptions
3. **LLM enrichment:** Use GPT to expand generic purposes
4. **Keyword matching:** Simpler text matching on program keywords

---

## Conclusion

The semantic signal investigation confirms that grant purpose text quality is too poor for reliable semantic matching. The 1.8x improvement from filtering is not sufficient to justify inclusion in the production algorithm.

**Final Decision:** Use collaborative filtering as primary signal. Add sector and geographic as secondary signals for coverage.
