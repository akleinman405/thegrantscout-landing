# PROMPT: LinkedIn Post Queue Review

**Date:** 2025-12-31
**Type:** Content Quality Review
**Purpose:** Review queued LinkedIn posts for accuracy, honesty, engagement, and brand alignment

---

## Context

TheGrantScout has created a LinkedIn content calendar with posts scheduled for Q1 2025. Posts include data insights derived from the f990_2025 database (143,184 foundations, 8.3M grants), founder journey content, and grant strategy tips.

**Brand Voice (from Content Framework):**
- Data-driven ("We analyzed...")
- Direct (no jargon)
- Helpful (value-first)
- Confident (not arrogant)
- Human (conversational)

**Content Pillars:**
- Foundation Intelligence (35%) - database-driven insights
- Grant Strategy (25%) - actionable advice
- Sector Trends (20%) - industry patterns
- Founder Journey (15%) - behind-the-scenes
- Proof & Validation (5%) - social proof

---

## Target Files

Review all post content in the LinkedIn folder. Likely locations:

1. **Queue folder:**
   ```
   [LinkedIn folder]/1_Ready_to_Post/
   ```
   or
   ```
   [LinkedIn folder]/Queue/
   ```

2. **Calendar with scripted posts:**
   ```
   CALENDAR_2025-01-01.4_linkedin_q1.md
   ```

3. **Carousel PDFs:**
   ```
   CAROUSEL_2025-01-09_foundation_size_distribution.pdf
   CAROUSEL_2025-01-14_cross_state_giving.pdf
   ```

4. **Insights catalog (source data):**
   ```
   DATA_2025-01-01.3_linkedin_insights_catalog.md
   ```

---

## Review Criteria

For EACH post, evaluate against these criteria:

### 1. Accuracy (Critical)
| Check | Question |
|-------|----------|
| Data correctness | Are the statistics accurate based on f990_2025 data? |
| Source verification | Can the claim be verified by querying the database? |
| Methodology transparency | Is it clear how the number was derived? |
| Sample size | Is the sample size appropriate for the claim? |
| Recency | Is the data current enough to be valid? |

**If a data claim is made, verify it against the database where possible.**

### 2. Honesty & Integrity
| Check | Question |
|-------|----------|
| No cherry-picking | Are we presenting data fairly, not just what looks good? |
| Caveats included | Are limitations or context acknowledged where needed? |
| No misleading framing | Could the post be misinterpreted? |
| Authentic voice | Does it sound genuine, not salesy? |
| Promises kept | Do we only claim what we can deliver? |

### 3. Engagement Potential
| Check | Question |
|-------|----------|
| Hook strength | Does the opening line stop the scroll? |
| Curiosity gap | Does it create desire to read more? |
| Value delivery | Does the reader learn something useful? |
| Call to action | Is there a clear next step (even if soft)? |
| Conversation starter | Would this prompt comments? |
| Shareability | Would someone share this with a colleague? |

### 4. Brand Alignment
| Check | Question |
|-------|----------|
| Voice consistency | Does it match our brand voice guidelines? |
| Positioning | Does it reinforce "data-driven foundation intelligence"? |
| Differentiation | Does it show what makes us different from competitors? |
| Audience fit | Is it relevant to nonprofit development professionals? |
| Professional tone | Appropriate for LinkedIn (not Twitter casual)? |

### 5. Technical Quality
| Check | Question |
|-------|----------|
| Length appropriate | Text posts: 150-300 words ideal for LinkedIn |
| Formatting | Line breaks for readability? No walls of text? |
| Hashtags | 3-5 relevant hashtags included? |
| No typos | Spelling and grammar correct? |
| Emoji usage | Minimal/appropriate (per brand guidelines)? |

---

## Output Format

Create: `REVIEW_2025-12-31_linkedin_post_queue.md`

### Report Structure:

```markdown
# LinkedIn Post Queue Review

## Summary
- Posts reviewed: X
- Approved as-is: X
- Minor edits suggested: X
- Major revision needed: X
- Data verification needed: X

## Review by Post

### Post 1: [Title/Date]
**File:** [filename]
**Type:** [Text / Carousel / Poll]
**Scheduled:** [date]

**Content Preview:**
> [First 2-3 lines of post]

**Scores:**
| Criteria | Score (1-5) | Notes |
|----------|-------------|-------|
| Accuracy | X | [brief note] |
| Honesty | X | [brief note] |
| Engagement | X | [brief note] |
| Brand Alignment | X | [brief note] |
| Technical Quality | X | [brief note] |
| **Overall** | X | |

**Data Verification:**
- Claim: "[specific claim made]"
- Verified: ✅ / ❌ / ⚠️ (needs check)
- Source: [query or reference]

**Suggested Edits:**
- [Edit 1]
- [Edit 2]

**Verdict:** ✅ Approved / ⚠️ Minor Edits / ❌ Needs Revision

---

[Repeat for each post]

---

## Data Claims Requiring Verification

| Post | Claim | Status | Action Needed |
|------|-------|--------|---------------|
| [date] | "70% of foundations..." | ✅ Verified | None |
| [date] | "48% cross state lines" | ⚠️ Check | Re-run query |

## Common Issues Found
1. [Pattern 1]
2. [Pattern 2]

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

## Revised Content (if needed)
[Include rewritten versions of any posts that need major revision]
```

---

## Data Verification Queries

For posts with database-driven claims, verify against f990_2025 schema:

**Example verifications:**

```sql
-- Verify: "70% of foundations have under $1M in assets"
SELECT 
  COUNT(*) FILTER (WHERE total_assets < 1000000) * 100.0 / COUNT(*) as pct_under_1m
FROM pf_returns
WHERE tax_year = 2023;

-- Verify: "Median grant is $3,500"
SELECT 
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY grant_amount) as median_grant
FROM fact_grants
WHERE grant_amount > 0;

-- Verify: "48% of grants cross state lines"
SELECT 
  COUNT(*) FILTER (WHERE filer_state != recipient_state) * 100.0 / COUNT(*) as pct_cross_state
FROM fact_grants
WHERE recipient_state IS NOT NULL;
```

If you cannot verify a claim, flag it for manual review.

---

## Priority Order

Review in this order:
1. **Launch week posts (Jan 6-10)** - These go live first
2. **Week 2 posts (Jan 13-17)** - Next priority
3. **Carousel PDFs** - High visibility content
4. **Remaining Q1 posts** - Lower urgency

---

## Important Notes

1. **Be constructive** - Goal is to improve posts, not just criticize
2. **Flag, don't assume** - If unsure about data accuracy, flag for verification rather than assuming wrong
3. **Preserve voice** - Edits should maintain the authentic founder voice
4. **Consider context** - Some posts are part of sequences (e.g., poll → reveal)
5. **LinkedIn norms** - What works on LinkedIn may differ from other platforms

---

## Deliverables

- [ ] `REVIEW_2025-12-31_linkedin_post_queue.md` - Full review report
- [ ] List of posts approved as-is
- [ ] List of posts needing edits (with specific suggestions)
- [ ] List of data claims requiring database verification
- [ ] Revised content for any posts needing major changes

---

*Prepared for Claude Code CLI execution*
