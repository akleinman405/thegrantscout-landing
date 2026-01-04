# PROMPT: Google Places API Enrichment Script

**Date:** 2025-12-12

---

## Task

Build a Python script that takes a prospect CSV, queries Google Places API to find matching businesses, and outputs enriched data including website, phone, and **business hours** (for timing calls when they're open).

---

## Input CSV Columns

From prospects table - script should accept any/all of these:

| Column | Required | Used For |
|--------|----------|----------|
| ein | Yes | Unique ID for output |
| org_name | Yes | Places search query |
| city | Yes | Location bias |
| state | Yes | Location bias |
| zip | Preferred | More precise location |
| address | Optional | Address matching validation |

**Example input row:**
```
ein,org_name,city,state,zip
123456789,Hope for the Homeless,Tulare,CA,93274
```

---

## Google Places API Setup

### API Required
- **Places API (New)** - enable in Google Cloud Console
- Billing account required (first $200/month free)

### Endpoints Used

**1. Text Search (find the place)**
```
POST https://places.googleapis.com/v1/places:searchText
```

**2. Place Details (get hours, website)**
```
GET https://places.googleapis.com/v1/places/{place_id}
```

### API Key
- Store in environment variable: `GOOGLE_PLACES_API_KEY`
- Or read from `google_places_api_key.txt` in project root

---

## Script Workflow

### Step 1: Load Input CSV
```python
import pandas as pd

df = pd.read_csv(input_file)
required_cols = ['ein', 'org_name', 'city', 'state']
# Validate required columns exist
```

### Step 2: Build Search Query
```python
def build_search_query(row):
    # "Hope for the Homeless Tulare CA"
    query = f"{row['org_name']} {row['city']} {row['state']}"
    if pd.notna(row.get('zip')):
        query += f" {row['zip']}"
    return query
```

### Step 3: Search Places API
```python
import requests

def search_place(query, api_key):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.regularOpeningHours"
    }
    payload = {
        "textQuery": query,
        "maxResultCount": 1
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

### Step 4: Extract Business Hours
```python
def parse_hours(opening_hours):
    """
    Convert Google's opening hours to readable format.
    Returns dict with day -> hours string
    """
    if not opening_hours:
        return None, None
    
    hours_by_day = {}
    weekday_text = opening_hours.get('weekdayDescriptions', [])
    
    # ["Monday: 9:00 AM – 5:00 PM", "Tuesday: 9:00 AM – 5:00 PM", ...]
    for day_text in weekday_text:
        if ':' in day_text:
            day, hours = day_text.split(':', 1)
            hours_by_day[day.strip()] = hours.strip()
    
    # Also get current open status
    is_open_now = opening_hours.get('openNow', None)
    
    return hours_by_day, is_open_now
```

### Step 5: Determine Best Call Times
```python
from datetime import datetime

def get_call_window(hours_by_day):
    """
    Returns recommended call times based on business hours.
    Prioritizes mid-day (avoid opening rush, closing prep).
    """
    today = datetime.now().strftime('%A')  # "Monday"
    
    if today not in hours_by_day:
        return "Unknown - check website"
    
    hours = hours_by_day[today]
    
    if 'Closed' in hours:
        return "Closed today"
    
    # Parse "9:00 AM – 5:00 PM" -> recommend 10am-4pm
    # (Simple version - can enhance)
    return f"Business hours: {hours}"
```

---

## Output Columns

| Column | Source | Description |
|--------|--------|-------------|
| ein | Input | Pass-through |
| org_name | Input | Pass-through |
| google_place_id | API | Unique Google ID |
| google_name | API | Name in Google |
| google_address | API | Full formatted address |
| google_phone | API | Phone number |
| google_website | API | Website URL |
| is_open_now | API | Boolean - currently open |
| hours_monday | API | Monday hours |
| hours_tuesday | API | Tuesday hours |
| hours_wednesday | API | Wednesday hours |
| hours_thursday | API | Thursday hours |
| hours_friday | API | Friday hours |
| hours_saturday | API | Saturday hours |
| hours_sunday | API | Sunday hours |
| match_confidence | Calculated | Name similarity score |
| api_status | Metadata | success/not_found/error |

---

## Rate Limiting & Costs

### Rate Limits
- 600 requests per minute (default)
- Add 0.1 second delay between requests to be safe

### Costs (as of 2024)
- Text Search: $0.032 per request
- Place Details: $0.017 per request
- **Total per prospect:** ~$0.05

### Cost Estimate
| Prospects | Estimated Cost |
|-----------|----------------|
| 100 | $5 |
| 1,000 | $50 |
| 10,000 | $500 |

### Optimization
- Cache results by EIN (don't re-query same org)
- Skip if we already have website + phone
- Batch by state to reduce API calls if similar results

---

## CLI Interface

```bash
# Basic usage
python enrich_places.py --input prospects.csv --output enriched.csv

# With API key file
python enrich_places.py --input prospects.csv --output enriched.csv --api-key-file google_api_key.txt

# Limit for testing
python enrich_places.py --input prospects.csv --output enriched.csv --limit 10

# Resume from checkpoint
python enrich_places.py --input prospects.csv --output enriched.csv --resume
```

---

## Checkpoint/Resume

```python
# Save progress every 50 records
CHECKPOINT_FILE = "places_enrichment_checkpoint.json"

def save_checkpoint(processed_eins, results):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({
            'processed_eins': list(processed_eins),
            'last_updated': datetime.now().isoformat()
        }, f)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return set(json.load(f)['processed_eins'])
    return set()
```

---

## Error Handling

| Error | Action |
|-------|--------|
| 429 Too Many Requests | Wait 60 seconds, retry |
| 404 Not Found | Mark api_status = 'not_found', continue |
| API key invalid | Exit with clear error message |
| Network timeout | Retry 3 times with backoff |

---

## Outputs

1. **Script:** `enrich_places.py`
2. **Output CSV:** User-specified (default: `DATA_enriched_places.csv`)
3. **Report:** `REPORT_2025-12-12_places_enrichment.md`
4. **Lessons:** `LESSONS_2025-12-12_places_enrichment.md`

---

## Success Criteria

- [ ] Script runs with `--input` and `--output` arguments
- [ ] Handles missing API key gracefully
- [ ] Rate limiting prevents 429 errors
- [ ] Checkpoint/resume works on interruption
- [ ] Output includes all columns listed above
- [ ] Match confidence helps filter false positives

---

## Notes

- Google Places works best for orgs with physical locations (shelters, clinics, schools)
- May not find orgs that are purely administrative or use home addresses
- Cross-reference google_website with prospects.website to validate matches
