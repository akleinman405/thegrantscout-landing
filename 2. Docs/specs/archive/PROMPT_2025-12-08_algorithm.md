# SPEC: ALGORITHM_SPEC.md

**Document Type:** SPEC  
**Purpose:** Define matching algorithm and document research behind it  
**Date:** 2025-12-08

---

## Sections

### 1. Executive Summary
- What the algorithm does in 2-3 sentences

### 2. Research Process
- How we arrived at 10 signals
- Sources reviewed
- Hypotheses tested
- Iterations and pivots

### 3. Signal Definitions
For each of the 10 signals:
- Signal name
- Weight (points out of 100)
- Data source (which table/field)
- Calculation logic
- Why it matters

### 4. Scoring Mechanics
- How signals combine into final score
- Score ranges and interpretation
- Thresholds for "good match" vs "marginal" vs "poor"

### 5. Openness Score
- Separate sub-algorithm for "likelihood to fund new grantees"
- Components (% first-time recipients, accepts unsolicited, etc.)
- How it integrates with main scoring

### 6. Known Limitations
- What the algorithm doesn't capture
- Edge cases
- Future improvements needed

### 7. Source Files
- File paths to original research docs
- File paths to algorithm code
- File paths to validation/testing results

---

## Source Files to Reference
- `/mnt/project/ALGORITHM_SPECIFICATION.md`
- `/mnt/project/ALGORITHM_QUICK_REFERENCE.md`
- `/mnt/project/ALGORITHM_RECOMMENDATIONS.md`
- `/mnt/project/MATCHING_ALGORITHM_DEEP_DIVE.md`
- `/mnt/project/WHAT_THEY_WANT_ALGORITHM_SPEC.md`
- `/mnt/project/THEGRANTSCOUT_SUMMARY_2025-12-5.md` (Section 3)
- `/mnt/project/ml-engineer.md`
- `/mnt/project/data-engineer.md`
