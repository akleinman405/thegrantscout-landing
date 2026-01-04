# Google Places API Enrichment - Report & Lessons Learned

**Date:** 2025-12-12
**Script:** `enrich_with_places.py`
**Purpose:** Add website, business hours, and place_id from Google Places API to prospect CSV

---

## Overview

Python script to enrich the prospect call list CSV with data from Google Places API:
- `places_id` - Google Place ID for future API lookups
- `places_website` - Website from Google
- `places_phone` - Phone from Google
- `places_hours` - Business hours (e.g., "Monday: 9:00 AM – 5:00 PM | Tuesday: ...")
- `places_found` - Y/N match indicator
- `google_maps_url` - Direct link to Google Maps listing

Also inserts/updates records to `f990_2025.prospects` table in PostgreSQL.

---

## Setup Requirements

### Dependencies
```bash
pip install requests psycopg2-binary
pip install cryptography  # Optional, for secure credential storage
```

### Google Cloud Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable **Places API** (the legacy one, NOT "Places API (New)")
4. Create an API key under APIs & Services > Credentials
5. (Recommended) Restrict the API key to Places API only

### Pricing (as of Dec 2025)
| API Call | Cost | Free Tier |
|----------|------|-----------|
| Text Search | $32 per 1,000 | $200/month credit |
| Place Details | $17 per 1,000 | Included in credit |

For 500 prospects: ~2 calls each = 1,000 calls = ~$49 (within free tier)

---

## Usage

### Test Run (5 records)
```cmd
python enrich_with_places.py --api-key YOUR_KEY --test 5
```

### Full Run
```cmd
python enrich_with_places.py --api-key YOUR_KEY
```

### Skip Database Insert
```cmd
python enrich_with_places.py --api-key YOUR_KEY --no-db
```

### All Options
```
--api-key KEY    Google Places API key
--test N         Only process first N records
--no-db          Skip database insert
--help           Show help
```

---

## Output

### CSV Output
- Test: `DATA_<name>_enriched_TEST.csv`
- Full: `DATA_<name>_enriched.csv`

### New Columns Added
| Column | Description |
|--------|-------------|
| `places_id` | Google Place ID (for future API calls) |
| `places_website` | Website from Google Places |
| `places_phone` | Phone from Google Places |
| `places_hours` | Business hours (pipe-separated days) |
| `places_found` | Y/N - whether Google found a match |
| `google_maps_url` | Direct link to Google Maps |

### Renamed Column
| Original | New Name |
|----------|----------|
| `website` | `f990_website` |

### Database Table
Creates/updates `f990_2025.prospects` with all enriched data.

---

## Technical Details

### API Choice: Legacy vs New

**IMPORTANT:** This script uses the **Legacy Places API**, not the new one.

| Feature | Legacy API | New API |
|---------|------------|---------|
| Endpoint | `maps.googleapis.com/maps/api/place/...` | `places.googleapis.com/v1/...` |
| Hours | `opening_hours.weekday_text` (reliable) | `regularOpeningHours` (less reliable) |
| Auth | `key` param | `X-Goog-Api-Key` header |

The Legacy API returns hours as human-readable strings like:
```
Monday: 9:00 AM – 5:00 PM | Tuesday: 9:00 AM – 5:00 PM | ...
```

### Two-Step Lookup
1. **Text Search** - Find the place_id using org name + city + state
2. **Place Details** - Get website, phone, hours using place_id

This is how your existing scripts work and ensures we get complete data.

### Rate Limiting
- 0.5 second delay between each record
- 0.3 second delay between search and details calls
- Auto-retry on OVER_QUERY_LIMIT with 60s wait

---

## Lessons Learned

### 1. Legacy API Works Better for Hours
The new Places API (v1) often returns empty `regularOpeningHours`. The legacy API's `opening_hours.weekday_text` is more reliable and returns formatted strings.

### 2. Two API Calls Per Record
You need both Text Search AND Place Details:
- Text Search finds the `place_id`
- Place Details gets `opening_hours`, `website`, `formatted_phone_number`

One call won't give you everything.

### 3. Nonprofit Match Rates
Many nonprofits don't have Google Business listings:
- Expected match rate: 40-60%
- Hours availability: 20-40% of matches

Small orgs often operate from residential addresses or never claimed their listing.

### 4. Place ID is Valuable
Store the `places_id` - it allows:
- Direct lookups without searching again
- Linking to Google Maps
- Future enrichment without re-searching

### 5. Windows Terminal Input Issues
`getpass()` can freeze in some Windows terminals. Script falls back to visible input when needed.

---

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS f990_2025.prospects (
    id SERIAL PRIMARY KEY,
    ein VARCHAR(20) UNIQUE,
    org_name TEXT,
    state VARCHAR(10),
    city VARCHAR(100),
    zip VARCHAR(20),
    f990_website TEXT,
    f990_phone VARCHAR(50),
    places_id VARCHAR(500),
    places_website TEXT,
    places_phone VARCHAR(50),
    places_hours TEXT,
    places_found BOOLEAN,
    google_maps_url TEXT,
    icp_score INTEGER,
    priority_tier INTEGER,
    enriched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Uses `ON CONFLICT (ein) DO UPDATE` for upsert behavior.

---

## Files

| File | Purpose |
|------|---------|
| `enrich_with_places.py` | Main enrichment script |
| `REPORT_2025-12-12_places_api_enrichment.md` | This report |
| `.places_credentials` | Encrypted API key (created on first run) |
| `.places_salt` | Encryption salt (created on first run) |
| `DATA_*_enriched.csv` | Output file (created on run) |
| `DATA_*_enriched_TEST.csv` | Test output (with --test flag) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No hours returned | Normal - many nonprofits don't have Google listings with hours |
| "REQUEST_DENIED" | Enable Places API (legacy) in Google Cloud Console |
| Low match rate | Expected for nonprofits - try simplifying org names |
| Database connection failed | Check PostgreSQL is running on WSL2, verify credentials |
| Input frozen | Use `--api-key` flag instead of interactive input |

---

## Example Output

```
[1/5] Searching: EDUCHRIST... Found! Hours: no
[2/5] Searching: Vietnam Health Education... Found! Hours: YES
[3/5] Searching: MEDICAL MINISTRIES INTERNATIONAL... Found! Hours: YES
[4/5] Searching: HEALING GROVE HEALTH CENTER... Not found
[5/5] Searching: WE LOVE OUR CITY... Found! Hours: no

Complete!
  Total records: 5
  Places found: 4 (80.0%)
  With hours: 2 (40.0%)
  Output: DATA_..._enriched_TEST.csv
  Database: 5 records upserted to f990_2025.prospects
```
