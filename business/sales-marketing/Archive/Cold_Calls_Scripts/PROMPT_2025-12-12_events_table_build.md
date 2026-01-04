# PROMPT: Fundraising Events Aggregation Table

**Date:** 2025-12-12

---

## Task

Build a persistent events table that aggregates nonprofit fundraising events from multiple sources, then fuzzy matches to prospects to attach EINs.

---

## Step 1: Create Events Table

```sql
CREATE TABLE IF NOT EXISTS f990_2025.fundraising_events (
    event_id SERIAL PRIMARY KEY,
    source VARCHAR(50),              -- eventbrite, facebook, givesmart, etc.
    source_event_id VARCHAR(100),    -- deduplication key
    org_name_raw VARCHAR(500),       -- original org name from source
    org_name_normalized VARCHAR(500),-- cleaned for matching
    event_name VARCHAR(500),
    event_date DATE,
    event_time TIME,
    event_city VARCHAR(100),
    event_state VARCHAR(2),
    event_url VARCHAR(1000),
    event_description TEXT,
    
    -- Matching fields
    matched_ein VARCHAR(9),
    matched_org_name VARCHAR(500),
    match_confidence SMALLINT,       -- 0-100
    match_method VARCHAR(50),        -- exact, fuzzy, manual
    
    -- Metadata
    scraped_at TIMESTAMP DEFAULT NOW(),
    expires_at DATE,                 -- event_date + 1 day
    is_active BOOLEAN DEFAULT TRUE,
    
    UNIQUE(source, source_event_id)
);

CREATE INDEX idx_events_ein ON f990_2025.fundraising_events(matched_ein);
CREATE INDEX idx_events_date ON f990_2025.fundraising_events(event_date);
CREATE INDEX idx_events_state ON f990_2025.fundraising_events(event_state);
```

---

## Step 2: Build Scraper for Each Source

### Source 1: Eventbrite (Priority - already working)

**Search URL pattern:**
```
https://www.eventbrite.com/d/united-states/charity-and-causes--events/?q={term}
```

**Search terms:**
- nonprofit gala
- charity auction
- charity fundraiser
- benefit dinner
- annual fundraiser
- charity ball

**Extract:**
- org_name_raw: Event organizer
- event_name: Title
- event_date/time: Date and time
- event_city/state: Location
- event_url: Eventbrite link
- event_description: First 500 chars

**Rate limit:** 2-3 seconds between requests

### Source 2: Facebook Events (if accessible)

**Search approach:**
- Search "nonprofit fundraiser" + state
- Parse public event pages

**Note:** May require Playwright/headless browser for JS rendering

### Source 3: Google Search (fallback)

**Search queries:**
```
"charity gala" site:eventbrite.com OR site:facebook.com/events 2025
"nonprofit fundraiser" [state] 2025
```

**Parse:** Extract event URLs, then fetch details

---

## Step 3: Normalize Org Names

```python
def normalize_org_name(name):
    if not name:
        return ""
    name = name.upper().strip()
    
    # Remove common suffixes
    suffixes = [
        ' INC', ' INCORPORATED', ' LLC', ' CORP', ' CORPORATION',
        ' FOUNDATION', ' FUND', ' TRUST', ' ASSOC', ' ASSOCIATION',
        ' NFP', ' NPO', ' 501C3', ' 501(C)(3)'
    ]
    for suffix in suffixes:
        name = name.replace(suffix, '')
    
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    return name.strip()
```

---

## Step 4: Fuzzy Match to Prospects

### Matching Query

```sql
-- Enable extension if needed
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Match events to prospects
WITH event_matches AS (
    SELECT 
        e.event_id,
        e.org_name_normalized,
        p.ein,
        p.org_name,
        similarity(e.org_name_normalized, UPPER(p.org_name)) AS sim_score
    FROM f990_2025.fundraising_events e
    CROSS JOIN LATERAL (
        SELECT ein, org_name
        FROM f990_2025.prospects
        WHERE similarity(e.org_name_normalized, UPPER(org_name)) > 0.5
        ORDER BY similarity(e.org_name_normalized, UPPER(org_name)) DESC
        LIMIT 1
    ) p
    WHERE e.matched_ein IS NULL
)
UPDATE f990_2025.fundraising_events e
SET 
    matched_ein = m.ein,
    matched_org_name = m.org_name,
    match_confidence = ROUND(m.sim_score * 100),
    match_method = CASE 
        WHEN m.sim_score >= 0.95 THEN 'exact'
        ELSE 'fuzzy'
    END
FROM event_matches m
WHERE e.event_id = m.event_id;
```

### Match Confidence Thresholds
- **95-100%:** Auto-accept (exact match)
- **80-94%:** High confidence (likely correct)
- **60-79%:** Medium confidence (verify before use)
- **50-59%:** Low confidence (probably wrong)
- **<50%:** No match

---

## Step 5: Maintenance Scripts

### Mark Expired Events
```sql
UPDATE f990_2025.fundraising_events
SET is_active = FALSE
WHERE event_date < CURRENT_DATE;
```

### Dedup on Re-scrape
```sql
-- UPSERT pattern handles duplicates via UNIQUE constraint
INSERT INTO f990_2025.fundraising_events (source, source_event_id, ...)
VALUES (...)
ON CONFLICT (source, source_event_id) 
DO UPDATE SET 
    event_date = EXCLUDED.event_date,
    scraped_at = NOW();
```

---

## Step 6: Output View for Call Lists

```sql
CREATE OR REPLACE VIEW f990_2025.prospects_with_events AS
SELECT 
    p.*,
    e.event_name,
    e.event_date,
    e.event_time,
    e.event_city AS event_city,
    e.event_state AS event_state,
    e.event_url,
    e.match_confidence
FROM f990_2025.prospects p
JOIN f990_2025.fundraising_events e ON p.ein = e.matched_ein
WHERE e.is_active = TRUE
  AND e.event_date >= CURRENT_DATE
  AND e.match_confidence >= 80
ORDER BY e.event_date ASC;
```

---

## Outputs

1. **Table created:** `f990_2025.fundraising_events`
2. **View created:** `f990_2025.prospects_with_events`
3. **Script:** `scrape_events.py` (reusable for weekly runs)
4. **Report:** `REPORT_2025-12-12_events_table_build.md`
5. **Lessons:** `LESSONS_2025-12-12_events_table_build.md`

---

## Success Criteria

- [ ] Table created with all columns
- [ ] At least 50 events scraped from Eventbrite
- [ ] Fuzzy matching populates EINs where possible
- [ ] View returns prospects with upcoming events
- [ ] Script is rerunnable without duplicates

---

## DB Connection

Per CLAUDE.md
