# PROMPT: Large-Scale Fundraising Events Aggregation

**Date:** 2025-12-12

---

## Task

Build a large events database (target: **5,000+ events**) by scraping multiple sources with geographic granularity. Use existing `f990_2025.fundraising_events` table and fuzzy matching pipeline.

---

## Target Volume

| Source | Strategy | Expected Events |
|--------|----------|-----------------|
| Eventbrite | Search by state (50 states) | 1,500-3,000 |
| Facebook Events | Search by major city | 2,000-5,000 |
| Google Search | Fallback scraping | 500-1,000 |
| **Total Target** | | **5,000+** |

---

## Source 1: Eventbrite by State

### Approach
Search each state separately for better coverage.

### URL Pattern
```
https://www.eventbrite.com/d/{state-slug}/charity-and-causes--events/?q={term}
```

### State Slugs
```python
STATE_SLUGS = {
    'AL': 'al--alabama', 'AK': 'ak--alaska', 'AZ': 'az--arizona',
    'AR': 'ar--arkansas', 'CA': 'ca--california', 'CO': 'co--colorado',
    'CT': 'ct--connecticut', 'DE': 'de--delaware', 'FL': 'fl--florida',
    'GA': 'ga--georgia', 'HI': 'hi--hawaii', 'ID': 'id--idaho',
    'IL': 'il--illinois', 'IN': 'in--indiana', 'IA': 'ia--iowa',
    'KS': 'ks--kansas', 'KY': 'ky--kentucky', 'LA': 'la--louisiana',
    'ME': 'me--maine', 'MD': 'md--maryland', 'MA': 'ma--massachusetts',
    'MI': 'mi--michigan', 'MN': 'mn--minnesota', 'MS': 'ms--mississippi',
    'MO': 'mo--missouri', 'MT': 'mt--montana', 'NE': 'ne--nebraska',
    'NV': 'nv--nevada', 'NH': 'nh--new-hampshire', 'NJ': 'nj--new-jersey',
    'NM': 'nm--new-mexico', 'NY': 'ny--new-york', 'NC': 'nc--north-carolina',
    'ND': 'nd--north-dakota', 'OH': 'oh--ohio', 'OK': 'ok--oklahoma',
    'OR': 'or--oregon', 'PA': 'pa--pennsylvania', 'RI': 'ri--rhode-island',
    'SC': 'sc--south-carolina', 'SD': 'sd--south-dakota', 'TN': 'tn--tennessee',
    'TX': 'tx--texas', 'UT': 'ut--utah', 'VT': 'vt--vermont',
    'VA': 'va--virginia', 'WA': 'wa--washington', 'WV': 'wv--west-virginia',
    'WI': 'wi--wisconsin', 'WY': 'wy--wyoming', 'DC': 'dc--washington-dc'
}
```

### Search Terms (run each per state)
```python
SEARCH_TERMS = [
    'nonprofit gala',
    'charity auction', 
    'charity fundraiser',
    'benefit dinner',
    'charity ball',
    'charity walk',
    'charity run',
    'nonprofit benefit',
    'foundation gala',
    'annual fundraiser',
    '5k charity',
    'charity golf',
    'silent auction'
]
```

### Rate Limiting
- 2-3 seconds between requests
- 50 states × 13 terms = 650 searches
- Estimated time: ~30-40 minutes
- If blocked, rotate user-agent or wait 10 minutes

### Checkpoint/Resume
```python
# Save progress after each state
CHECKPOINT_FILE = 'eventbrite_scrape_checkpoint.json'

def save_checkpoint(completed_states, events):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({
            'completed_states': completed_states,
            'event_count': len(events),
            'timestamp': datetime.now().isoformat()
        }, f)
```

---

## Source 2: Facebook Events

### Approach
Search major cities for charity/nonprofit events.

### Target Cities (top 50 by nonprofit density)
```python
MAJOR_CITIES = [
    'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
    'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA',
    'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Jacksonville, FL',
    'Fort Worth, TX', 'Columbus, OH', 'Charlotte, NC', 'San Francisco, CA',
    'Indianapolis, IN', 'Seattle, WA', 'Denver, CO', 'Washington, DC',
    'Boston, MA', 'Nashville, TN', 'Baltimore, MD', 'Oklahoma City, OK',
    'Louisville, KY', 'Portland, OR', 'Las Vegas, NV', 'Milwaukee, WI',
    'Albuquerque, NM', 'Tucson, AZ', 'Fresno, CA', 'Sacramento, CA',
    'Atlanta, GA', 'Kansas City, MO', 'Miami, FL', 'Raleigh, NC',
    'Minneapolis, MN', 'Cleveland, OH', 'Tampa, FL', 'St. Louis, MO',
    'Pittsburgh, PA', 'Cincinnati, OH', 'Orlando, FL', 'New Orleans, LA',
    'Detroit, MI', 'Salt Lake City, UT', 'Honolulu, HI', 'Richmond, VA',
    'Hartford, CT', 'Providence, RI'
]
```

### Facebook Search URL
```
https://www.facebook.com/events/search?q={query}&filters={"city":"{city}"}
```

**Note:** Facebook is heavily JS-rendered. Options:
1. Use Playwright/Selenium with headless browser
2. Use unofficial Facebook Events API (if available)
3. Skip if too difficult - focus on other sources

### Alternative: Facebook via Google
```
site:facebook.com/events "charity" OR "nonprofit" OR "fundraiser" {city} 2025
```

---

## Source 3: Google Search Fallback

### Approach
Use Google/DuckDuckGo to find events not on major platforms.

### Search Queries
```python
GOOGLE_QUERIES = [
    '"{city}" nonprofit gala 2025',
    '"{city}" charity auction January 2026',
    '"{city}" fundraiser dinner 2025',
    'site:eventbrite.com OR site:facebook.com/events "{city}" charity',
    '"{city}" 501c3 fundraiser event'
]
```

### Use DuckDuckGo (more scrape-friendly)
```python
import requests

def search_duckduckgo(query):
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    # Parse results for event URLs
    return parse_results(response.text)
```

---

## Source 4: Event Platform Direct Scraping

### GiveSmart (gala platform)
```
https://e.givesmart.com/events/
```
- Many nonprofits use for auctions/galas
- Public event pages

### Classy
```
https://www.classy.org/discover
```
- Fundraising platform
- Lists active campaigns/events

### BetterWorld
```
https://www.betterworld.org/events
```
- Charity auction platform

---

## Deduplication Strategy

Events may appear in multiple sources. Dedupe by:

1. **Primary:** Exact URL match
2. **Secondary:** Same org + same date + same city
3. **Tertiary:** Fuzzy match on event name (>90% similarity) + same date

```sql
-- Before insert, check for duplicates
SELECT event_id FROM f990_2025.fundraising_events
WHERE (event_url = %(url)s)
   OR (org_name_normalized = %(org_norm)s 
       AND event_date = %(date)s 
       AND event_city = %(city)s);
```

---

## Script Structure

```python
#!/usr/bin/env python3
"""
scrape_events_large.py - Large-scale event aggregation

Usage:
    python scrape_events_large.py --source eventbrite
    python scrape_events_large.py --source all
    python scrape_events_large.py --resume
"""

def scrape_eventbrite_by_state():
    """Scrape Eventbrite for all 50 states."""
    pass

def scrape_facebook_events():
    """Scrape Facebook Events for major cities."""
    pass

def scrape_google_fallback():
    """Use Google/DuckDuckGo for additional events."""
    pass

def scrape_givesmart():
    """Scrape GiveSmart event platform."""
    pass

def dedupe_events():
    """Remove duplicate events across sources."""
    pass

def run_fuzzy_matching():
    """Match events to prospects and populate EINs."""
    pass

def main():
    # 1. Scrape all sources
    # 2. Dedupe
    # 3. Insert to database
    # 4. Run fuzzy matching
    # 5. Update view
    # 6. Print stats
    pass
```

---

## CLI Interface

```bash
# Scrape specific source
python scrape_events_large.py --source eventbrite
python scrape_events_large.py --source facebook
python scrape_events_large.py --source google

# Scrape all sources
python scrape_events_large.py --source all

# Resume interrupted scrape
python scrape_events_large.py --resume

# Limit for testing
python scrape_events_large.py --source eventbrite --states CA,NY,TX

# Just run matching (no scraping)
python scrape_events_large.py --match-only
```

---

## Timeframe

Scrape events for next 6 months:
- December 2025
- January 2026
- February 2026
- March 2026
- April 2026
- May 2026

This captures:
- Holiday galas (Dec)
- New year fundraisers (Jan-Feb)
- Spring galas (Mar-May)

---

## Expected Output

| Metric | Target |
|--------|--------|
| Total events scraped | 5,000+ |
| Unique after dedupe | 4,000+ |
| Matched to prospect EIN | 1,500+ (30-40%) |
| High confidence matches (≥80%) | 500+ |

---

## Success Criteria

- [ ] Eventbrite scraped for all 50 states
- [ ] At least one additional source working (Facebook, Google, or GiveSmart)
- [ ] Total events ≥ 5,000
- [ ] Dedupe removes cross-source duplicates
- [ ] Fuzzy matching populates EINs
- [ ] Checkpoint/resume works on interruption
- [ ] Script completes in < 2 hours

---

## Outputs

1. **Script:** `scrape_events_large.py`
2. **Data:** Events inserted into `f990_2025.fundraising_events`
3. **Report:** `REPORT_2025-12-12_large_events_scrape.md`
4. **Lessons:** `LESSONS_2025-12-12_large_events_scrape.md`

---

## DB Connection

Per CLAUDE.md
