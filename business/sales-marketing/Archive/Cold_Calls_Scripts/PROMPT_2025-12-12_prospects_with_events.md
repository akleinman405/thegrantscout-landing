# PROMPT: Prospects with Upcoming Fundraising Events

**Date:** 2025-12-12

---

## Task

Find nonprofits with upcoming fundraising events for cold call personalization.

---

## Step 1: Search Eventbrite

Search for nonprofit/charity fundraising events:

**Search terms:**
- "nonprofit gala"
- "charity auction"
- "fundraiser"
- "benefit dinner"

**Filters:**
- Timeframe: Next 60 days
- Location: US

---

## Step 2: Extract Event Data

For each event, capture:
- Organization name
- Event name
- Event date
- City/State
- Event URL

---

## Step 3: Cross-Reference Prospects

Match event org names against `f990_2025.prospects` table:
- Use fuzzy matching on `org_name`
- Return matches with similarity score

---

## Step 4: Output

Matched prospects with event details appended:
- All standard prospect columns
- event_name
- event_date
- event_city
- event_state
- event_url
- match_confidence

**Output file:** `DATA_2025-12-12_prospects_with_events.csv`

---

## DB Connection

Per CLAUDE.md
