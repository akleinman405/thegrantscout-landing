# Fundraising Events Table Build Report
**Date:** 2025-12-12

---

## Executive Summary

Built a persistent `f990_2025.fundraising_events` table to aggregate nonprofit fundraising events from Eventbrite, with PostgreSQL `pg_trgm` fuzzy matching to link events to prospects. Successfully scraped 59 events and matched 34 to prospect EINs.

---

## Deliverables Created

| Deliverable | Status | Description |
|-------------|--------|-------------|
| `f990_2025.fundraising_events` table | Created | 19 columns, 4 indexes, UNIQUE constraint for dedup |
| `f990_2025.prospects_with_events` view | Created | Joins prospects with upcoming matched events |
| `scrape_events.py` script | Created | Reusable scraper with matching and maintenance |
| `pg_trgm` extension | Enabled | For PostgreSQL similarity matching |

---

## Table Schema

```sql
CREATE TABLE f990_2025.fundraising_events (
    event_id SERIAL PRIMARY KEY,
    source VARCHAR(50),              -- eventbrite, facebook, etc.
    source_event_id VARCHAR(100),    -- deduplication key
    org_name_raw VARCHAR(500),       -- original org name
    org_name_normalized VARCHAR(500),-- cleaned for matching
    event_name VARCHAR(500),
    event_date DATE,
    event_time TIME,
    event_city VARCHAR(100),
    event_state VARCHAR(2),
    event_url VARCHAR(1000),
    event_description TEXT,
    matched_ein VARCHAR(20),
    matched_org_name VARCHAR(500),
    match_confidence SMALLINT,       -- 0-100
    match_method VARCHAR(50),        -- exact, fuzzy, manual
    scraped_at TIMESTAMP DEFAULT NOW(),
    expires_at DATE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(source, source_event_id)
);
```

### Indexes
- `idx_events_ein` — Fast lookup by matched EIN
- `idx_events_date` — Filter by event date
- `idx_events_state` — Filter by state
- `idx_events_source` — Dedupe by source + event ID

---

## Statistics

| Metric | Value |
|--------|-------|
| Total events scraped | 59 |
| Matched to prospect EIN | 34 (58%) |
| Active (upcoming) | 59 |
| High confidence (≥80%) | 3 |
| In view (≥60% confidence) | 12 |

### Match Confidence Distribution

| Confidence | Count | % of Matched |
|------------|-------|--------------|
| 95-100% (exact) | 1 | 3% |
| 80-94% (high) | 2 | 6% |
| 60-79% (medium) | 9 | 26% |
| 40-59% (low) | 22 | 65% |

---

## High-Quality Matches (≥80%)

| Event Org | Prospect Match | Event | Date | Confidence |
|-----------|----------------|-------|------|------------|
| Habitat for Humanity of the River Valley | HABITAT FOR HUMANITY OF THE RIVER VALLEY | Raise the Roof Benefit Dinner | 2026-03-10 | 100% |
| Hearts in Motion | HEARTS IN MOTION INC | Hearts in Motion Benefit Dinner | 2026-02-07 | 89% |
| Care Beyond The Boulevard | CARE BEYOND THE BOULEVARD INC | Holiday Charity Fundraiser | 2025-12-13 | 86% |

---

## View Usage

```sql
-- Get prospects with upcoming events (≥60% confidence)
SELECT org_name, state, event_name, event_date, match_confidence
FROM f990_2025.prospects_with_events
ORDER BY event_date;
```

**Current results:** 12 prospects with events ≥60% confidence

---

## Scraper Script Usage

```bash
# Run scraper (loads data and matches)
python scrape_events.py

# Dry run (no database changes)
python scrape_events.py --dry-run
```

### Script Features
- Loads events from `/tmp/all_eventbrite_events.csv`
- Normalizes org names (removes INC, LLC, etc.)
- Inserts with UPSERT (handles duplicates)
- Runs `pg_trgm` similarity matching
- Creates/updates the view
- Marks expired events inactive
- Prints statistics

---

## Maintenance

### Mark Expired Events (run daily)
```sql
UPDATE f990_2025.fundraising_events
SET is_active = FALSE
WHERE event_date < CURRENT_DATE;
```

### Re-scrape Without Duplicates
The `UNIQUE(source, source_event_id)` constraint handles this:
```sql
INSERT INTO f990_2025.fundraising_events (...)
ON CONFLICT (source, source_event_id)
DO UPDATE SET event_date = EXCLUDED.event_date, scraped_at = NOW();
```

---

## Success Criteria Checklist

- [x] Table created with all columns
- [x] At least 50 events scraped from Eventbrite (59 scraped)
- [x] Fuzzy matching populates EINs where possible (34 matched)
- [x] View returns prospects with upcoming events (12 prospects)
- [x] Script is rerunnable without duplicates (UPSERT pattern)

---

## Next Steps

1. **Add more sources:** Facebook Events, GiveSmart, local calendars
2. **Schedule weekly runs:** Cron job for `scrape_events.py`
3. **Manual review:** Flag medium-confidence matches (60-79%) for human verification
4. **Expand search terms:** Try state-specific searches for better coverage

---

*Generated: 2025-12-12*
