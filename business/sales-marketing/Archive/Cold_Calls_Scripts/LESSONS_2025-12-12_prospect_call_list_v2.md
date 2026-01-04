# Lessons Learned: Prospect Call List v2
**Date:** 2025-12-12

---

## What Worked Well

1. **Simplified filters yielded 600 prospects** — Dropping sparse flags like `likely_active_fundraiser` and `has_concrete_mission` from v1 dramatically increased the pool while maintaining quality criteria.

2. **Phone enrichment from nonprofit_returns was 100% successful** — Every prospect had a phone number match in nonprofit_returns. Using `DISTINCT ON (ein) ... ORDER BY tax_year DESC` reliably got the most recent phone.

3. **Parallel agents for website checking** — Running 3 agents simultaneously processed 74 websites in ~5 minutes. Each agent completed independently with clear results.

4. **28% fundraising hit rate** — 21 of 74 websites (28%) had active fundraising. Higher than expected — nonprofits in this revenue/dependency band are actively seeking donations.

5. **Officer enrichment was robust** — 91% of prospects (546/600) had officer matches with the title-priority ranking system.

---

## What Was Harder Than Expected

1. **Many websites inaccessible** — Of 100 websites exported, 26 were "N/A" placeholders. Several others had SSL errors, connection timeouts, or 403 forbidden responses.

2. **Distinguishing "donate button" from "active campaign"** — Many nonprofits have perpetual donate buttons. Agents had to look for specific campaigns, events with dates, year-end appeals, or named programs to qualify as "active fundraising."

3. **Heavy California concentration** — 229 of 600 prospects (38%) are in California. This may reflect where small nonprofits with high grant dependency cluster, or data bias.

---

## What I Wish I Knew Going In

1. **Website field often contains placeholders** — "N/A", "0", "NONE" values should be filtered before attempting web fetches.

2. **nonprofit_returns has multiple years per EIN** — Must use `DISTINCT ON` or similar to get single row per org, preferably most recent year.

3. **Agent parallelization is effective** — 3 agents checking ~25 sites each completed in roughly the same time as 1 agent checking 25. Good for scaling.

---

## Data Quality Issues Discovered

| Issue | Impact | Recommendation |
|-------|--------|----------------|
| 26% of "websites" were N/A placeholders | Wasted batch slots | Pre-filter website field more aggressively |
| Some URLs missing https:// | Fetch failures | Normalize URLs before fetching |
| Contact missing for 54 prospects | Need manual lookup | May not have filed officers in 990 |
| Heavy CA concentration (38%) | May skew outreach | Consider geographic stratification |

---

## Technical Notes

### Effective SQL for phone enrichment:
```sql
WITH latest_phone AS (
    SELECT DISTINCT ON (ein) ein, phone
    FROM f990_2025.nonprofit_returns
    WHERE phone IS NOT NULL AND phone != ''
    ORDER BY ein, tax_year DESC
)
SELECT p.*, lp.phone
FROM f990_2025.prospects p
LEFT JOIN latest_phone lp ON p.ein = lp.ein
```

### Agent batch sizing:
- 74 websites / 3 agents = ~25 each
- Each agent took ~3-5 minutes
- Total parallel time: ~5 minutes vs ~15 minutes sequential

### Fundraising indicators to look for:
- Year-end giving appeals
- Named campaigns with dollar targets
- Events with dates (galas, walks, golf tournaments)
- "Triple your gift" matching campaigns
- Crowdfunding pages
- Specific programs (Toy Drive, Relief Fund, etc.)

---

## Suggestions for Next Time

1. **Filter website field upfront** — `WHERE website NOT IN ('N/A', 'NA', 'NONE', '0', '') AND website IS NOT NULL`

2. **Consider more agents** — With 600 prospects and 518 valid websites, could use 5-10 agents to check all in reasonable time.

3. **Cache fundraising results** — Store `current_fundraising` findings in prospects table for future use.

4. **Geographic segmentation** — Break call list by state/region for focused campaigns.

---

*Generated: 2025-12-12*
