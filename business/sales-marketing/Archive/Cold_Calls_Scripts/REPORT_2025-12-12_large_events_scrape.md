# REPORT: Large-Scale Fundraising Events Scrape

**Date:** 2025-12-12
**Task:** Build large events database targeting 5,000+ events

---

## Executive Summary

Scraped **273 unique fundraising events** from Eventbrite across all 50 states + DC using parallel agents. **169 events (62%)** were successfully fuzzy-matched to prospects in the database. The 5,000+ event target was not achieved due to rate limiting and unavailability of secondary sources (GiveSmart, Classy, Facebook).

---

## Results vs. Targets

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Total events scraped | 5,000+ | 273 | Below target |
| Unique after dedupe | 4,000+ | 273 | Below target |
| Matched to prospect EIN | 30-40% | 62% (169) | **Exceeds target** |
| High confidence matches (>=80%) | 500+ | 28 | Below target |
| States covered | 50 + DC | 50 + DC | **Met** |

---

## Scraping Results by Source

| Source | Status | Events | Notes |
|--------|--------|--------|-------|
| Eventbrite | Success | 273 | All 50 states + DC scraped |
| GiveSmart | Failed | 0 | HTTP 303 redirect errors |
| Classy | Failed | 0 | HTTP 404 errors |
| Facebook | Skipped | 0 | Requires JS rendering |
| Google/DuckDuckGo | Not attempted | 0 | Deprioritized |

---

## Events by State (Top 15)

| State | Events | Matched | Match Rate |
|-------|--------|---------|------------|
| MD | 12 | 7 | 58% |
| AL | 11 | 9 | 82% |
| LA | 10 | 8 | 80% |
| MA | 10 | 6 | 60% |
| GA | 10 | 6 | 60% |
| NJ | 9 | 5 | 56% |
| CT | 9 | 6 | 67% |
| MN | 8 | 5 | 63% |
| KY | 8 | 5 | 63% |
| CA | 8 | 5 | 63% |
| MS | 7 | 4 | 57% |
| PA | 7 | 4 | 57% |
| TX | 7 | 4 | 57% |
| WA | 6 | 4 | 67% |
| NE | 6 | 4 | 67% |

---

## Match Quality Analysis

| Confidence Level | Count | Percentage |
|-----------------|-------|------------|
| High (>=80%) | 28 | 17% |
| Medium (60-79%) | 22 | 13% |
| Low (40-59%) | 119 | 70% |
| **Total Matched** | **169** | **62%** |
| Unmatched | 104 | 38% |

**Average Match Confidence:** 56.6%

---

## Match Method Breakdown

| Method | Matches | Avg Confidence |
|--------|---------|----------------|
| fuzzy_state (same state) | 26 | 60.9% |
| fuzzy_national | 109 | 55.4% |
| fuzzy (from batch 1) | 33 | 55.8% |
| exact | 1 | 100% |

---

## Top High-Confidence Matches

| Event | Organization | Date | Location | Confidence |
|-------|--------------|------|----------|------------|
| Tree Lot Party | The Guardsmen | 2025-12-13 | San Francisco, CA | 100% |
| Hearts in Harmony Recital | Santa Fe Desert Chorale | 2025-12-22 | Santa Fe, NM | 100% |
| [Name withheld] | The Call | 2026-02-07 | Texarkana, AR | 100% |
| [Multiple events] | Habitat for Humanity | Various | Various | 100% |
| [Multiple events] | NAMI Nebraska | 2026-02-13 | Lincoln, NE | 100% |

---

## Event Date Distribution

| Month | Events |
|-------|--------|
| December 2025 | 168 |
| January 2026 | 52 |
| February 2026 | 40 |
| March 2026 | 6 |
| April 2026 | 4 |
| May 2026 | 3 |

**Date Range:** 2025-12-12 to 2026-05-30

---

## Process Details

### Approach
1. **Parallel Agents:** Used 5 concurrent agents to scrape Eventbrite (10 states each)
2. **Search Terms:** 13 terms per state ("nonprofit gala", "charity auction", etc.)
3. **Rate Management:** 2-3 second delays between requests per agent
4. **Deduplication:** UPSERT with UNIQUE constraint on (source, source_event_id)

### Agent Batches
| Batch | States | Events Found |
|-------|--------|--------------|
| 1 | AL, AK, AZ, AR, CA, CO, CT, DE, FL, GA | 49 |
| 2 | HI, ID, IL, IN, IA, KS, KY, LA, ME, MD | 57 |
| 3 | MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ | 52 |
| 4 | NM, NY, NC, ND, OH, OK, OR, PA, RI, SC | 34 |
| 5 | SD, TN, TX, UT, VT, VA, WA, WV, WI, WY, DC | 35 |

### Database Updates
- **Inserted:** 214 new events
- **Duplicates skipped:** 12 (from initial batch)
- **Pre-existing:** 59 (from earlier events_table_build task)
- **Final total:** 273 events

---

## Artifacts Created

1. **Script:** `scrape_events_large.py` (CLI with --source, --states, --resume, --match-only flags)
2. **Data:** 273 events in `f990_2025.fundraising_events` table
3. **Index:** GIN index on `org_name gin_trgm_ops` for fast fuzzy matching
4. **CSV Exports:** `/tmp/events_batch_1.csv` through `/tmp/events_batch_5.csv`

---

## Why Target Wasn't Met

| Factor | Impact |
|--------|--------|
| **Rate limiting** | Eventbrite returned 429 errors after ~50-100 requests per session |
| **GiveSmart unavailable** | HTTP 303 redirect to login page |
| **Classy unavailable** | HTTP 404 page not found |
| **Facebook complexity** | JS rendering requires headless browser (skipped) |
| **Event density** | Many states have few public charity events on Eventbrite |

---

## Recommendations for Scaling

### Immediate (This Week)
1. **Retry GiveSmart** with authenticated session or API access
2. **Try Classy Discover** with different URL patterns
3. **Add BetterWorld** as fallback source

### Short-term (Next Week)
1. **Implement Playwright** for JS-rendered pages (Facebook, etc.)
2. **Add proxy rotation** to avoid rate limiting
3. **Schedule periodic re-scraping** (weekly) to catch new events

### Long-term (Next Month)
1. **Partner with event platforms** for API access
2. **Build email alerts** for matched prospects
3. **Add historical event tracking** to identify recurring galas

---

## Database Assets

```sql
-- Count events
SELECT COUNT(*) FROM f990_2025.fundraising_events;  -- 273

-- Count matched
SELECT COUNT(*) FROM f990_2025.fundraising_events WHERE matched_ein IS NOT NULL;  -- 169

-- View prospects with events
SELECT * FROM f990_2025.prospects_with_events LIMIT 10;
```

---

## Next Steps

1. Investigate alternative event sources (BetterWorld, local chamber of commerce sites)
2. Consider API partnerships with GiveSmart/Classy for legitimate access
3. Set up weekly scraping job to grow database over time
4. Build sales workflow around high-confidence event matches

---

**End of Report**
