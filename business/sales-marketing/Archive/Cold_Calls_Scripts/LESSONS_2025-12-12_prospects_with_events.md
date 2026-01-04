# Lessons Learned: Prospects with Upcoming Events
**Date:** 2025-12-12

---

## What Worked Well

1. **Eventbrite as a source** — Rich data including org names, event names, dates, locations, and URLs. API-like structured data from web scraping.

2. **Multiple search terms** — Different queries surfaced different events: "nonprofit gala" (formal events), "charity fundraiser" (varied events), "benefit dinner" (meal events), "charity auction" (special events).

3. **Multi-strategy matching** — Using three matching approaches (exact normalized, high fuzzy, key phrase) caught different types of matches while maintaining quality.

4. **Confidence scoring** — Assigning match confidence allowed filtering false positives. The 100% exact matches are highly reliable; lower scores need verification.

5. **RapidFuzz library** — Fast fuzzy matching against 74K prospects in seconds. Token set ratio worked better than simple ratio for org names with different word orders.

---

## What Was Harder Than Expected

1. **Org name variations** — Same org uses different names:
   - Eventbrite: "Dress for Success"
   - Database: "Dress for Success Cincinnati"
   - Both are correct but fuzzy matching needed to be lenient

2. **False positive rate** — Initial 65% threshold produced many false positives like:
   - "AREAA Boston" → "Boston Athletic Academy" (different orgs)
   - "Save the Brave" → "Save The Bay" (different causes)
   Raising threshold to 90%+ for fuzzy, 100% for exact reduced these.

3. **Event organizer ≠ beneficiary** — Some events are hosted by venues or companies but benefit nonprofits:
   - "General Informatics" hosts casino night for "Boys & Girls Club"
   - Matching to the beneficiary requires reading event descriptions

4. **Limited event data volume** — Only 32 events across entire US. Many nonprofits don't use Eventbrite for their events.

---

## What I Wish I Knew Going In

1. **Most nonprofits in the database won't have Eventbrite events** — 13 matches from 74K prospects (0.02%). Event-based personalization is a niche strategy.

2. **Name normalization is critical** — Removing INC, LLC, FOUNDATION suffixes before matching significantly improved exact match rate.

3. **Geographic mismatch is common** — Eventbrite event location may differ from org's registered state (e.g., national org hosting local event).

---

## Data Quality Issues

| Issue | Impact | Recommendation |
|-------|--------|----------------|
| Org name variations | Missed matches | Use multiple matching strategies |
| Event organizer vs beneficiary | Wrong matches | Parse event descriptions |
| Low event volume | Few matches | Search multiple platforms |
| Geographic mismatch | False positives | Don't weight state matching too heavily |
| Missing contact info | 1 prospect had no officer | Supplement with LinkedIn |

---

## Matching Algorithm Insights

### What Worked
```python
# Exact normalized match (removes Inc, LLC, etc.)
def normalize(name):
    name = name.upper()
    for suffix in [' INC', ' LLC', ' FOUNDATION']:
        name = name.replace(suffix, '')
    return name.strip()

# Token set ratio for fuzzy (handles word order differences)
fuzz.token_set_ratio("Dress for Success", "Dress for Success Cincinnati")  # 100
```

### What Didn't Work
```python
# Simple ratio fails on word order differences
fuzz.ratio("Hearts in Motion", "HEARTS IN MOTION INC")  # ~75 instead of 100

# Low thresholds produce false positives
# "Save the Brave" → "Save The Bay" at 77%
```

---

## Suggestions for Scaling

1. **Add more event sources:**
   - Facebook Events (requires API)
   - Local newspaper event calendars
   - Foundation/nonprofit directories with event listings
   - GuideStar/Candid event data

2. **Improve matching:**
   - Use EIN matching if events list EINs
   - Match on org address/city + name
   - Use website domain matching

3. **Automate weekly:**
   - Schedule weekly Eventbrite scrape
   - Store matched events in prospects table
   - Alert when new matches found

4. **Expand geographically:**
   - Search by state for better coverage
   - Use Eventbrite location filters

---

## False Positive Examples (Avoid)

| Event Org | Matched To | Why Wrong |
|-----------|------------|-----------|
| AREAA Boston | Boston Athletic Academy | Different organization types |
| Save the Brave | Save The Bay | Different causes (veterans vs. environment) |
| Denver Winter Ball | Step Denver | Coincidental word match |
| Atlanta Classic Soulful Symphony | Symphony in C | Different orchestras |

---

*Generated: 2025-12-12*
