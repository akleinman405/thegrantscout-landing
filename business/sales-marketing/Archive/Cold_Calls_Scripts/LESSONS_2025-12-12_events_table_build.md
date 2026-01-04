# Lessons Learned: Events Table Build
**Date:** 2025-12-12

---

## What Worked Well

1. **PostgreSQL `pg_trgm` extension** — Built-in similarity matching is fast and effective. The `similarity()` function and `CROSS JOIN LATERAL` pattern enables efficient fuzzy matching against 74K prospects.

2. **UPSERT pattern for deduplication** — `ON CONFLICT ... DO UPDATE` elegantly handles re-scraping without creating duplicates. The `UNIQUE(source, source_event_id)` constraint is the key.

3. **Org name normalization** — Removing suffixes (INC, LLC, FOUNDATION) before matching significantly improved match quality. "HEARTS IN MOTION" matches "HEARTS IN MOTION INC" at 89%.

4. **View for call lists** — The `prospects_with_events` view provides a clean interface for downstream use without requiring knowledge of the join logic.

5. **Reusable script** — `scrape_events.py` encapsulates all logic and can be run repeatedly for maintenance.

---

## What Was Harder Than Expected

1. **Match quality vs. quantity tradeoff** —
   - 40% threshold: 34 matches but many false positives
   - 80% threshold: Only 3 matches but very accurate
   - Settled on 60% for the view as a compromise

2. **Event organizer vs. beneficiary** — Many events are hosted by venues/companies but benefit nonprofits. The "Boys & Girls Club of Metro LA" event was actually hosted by "General Informatics" with BGC as beneficiary.

3. **Geographic mismatch** — Event locations don't always match org registered states:
   - "Dress for Success" event in Pittsburgh matched "DRESS FOR SUCCESS SEATTLE"
   - Both are legitimate chapters but different locations

4. **Low scrape volume** — 59 events from 6 search terms across entire US. Eventbrite coverage is sparse for nonprofit events.

---

## What I Wish I Knew Going In

1. **`pg_trgm` similarity scale** — Values 0.0-1.0, not 0-100. Need to multiply by 100 for confidence scores.

2. **LATERAL join performance** — `CROSS JOIN LATERAL` with `LIMIT 1` is efficient for finding the single best match per event.

3. **Event platforms are fragmented** — Eventbrite is just one of many platforms. Facebook Events, GiveSmart, BetterWorld, and local calendars each have their own audiences.

---

## Technical Insights

### Effective Matching Query
```sql
SELECT
    e.event_id,
    p.ein,
    similarity(e.org_name_normalized, UPPER(p.org_name)) AS sim_score
FROM f990_2025.fundraising_events e
CROSS JOIN LATERAL (
    SELECT ein, org_name
    FROM f990_2025.prospects
    WHERE similarity(e.org_name_normalized, UPPER(org_name)) > 0.4
    ORDER BY similarity DESC
    LIMIT 1
) p
```

**Why this works:**
- `CROSS JOIN LATERAL` evaluates subquery per event
- `LIMIT 1` returns only best match
- `> 0.4` threshold in WHERE clause enables index usage
- `ORDER BY similarity DESC` ensures best match selected

### Normalization Function
```python
def normalize_org_name(name):
    name = name.upper().strip()
    for suffix in [' INC', ' LLC', ' FOUNDATION', ...]:
        name = name.replace(suffix, '')
    name = re.sub(r'[^\w\s]', '', name)
    return ' '.join(name.split())
```

**Key transformations:**
- Uppercase for case-insensitive matching
- Remove legal suffixes that vary
- Remove punctuation
- Normalize whitespace

---

## False Positive Examples

| Event Org | Matched To | Similarity | Issue |
|-----------|------------|------------|-------|
| Omega Psi Phi Fraternity | CHI OMEGA FRATERNITY | 67% | Different fraternities |
| Save the Brave | Save The Bay | 62% | Different causes |
| Touch of Life Foundation | TOUCH-A-LIFE | 69% | Different organizations |
| Education First | EDUCATION COMES FIRST INC | 62% | Different organizations |

**Mitigation:** Set view threshold to 60%+ and flag 60-79% matches for manual review.

---

## Recommendations for Production

1. **Add manual verification flag**
   ```sql
   ALTER TABLE f990_2025.fundraising_events
   ADD COLUMN manually_verified BOOLEAN DEFAULT FALSE;
   ```

2. **Create confidence tiers**
   - Auto-accept: ≥95% (exact matches)
   - High-confidence: 80-94% (likely correct)
   - Review-needed: 60-79% (verify before use)
   - Reject: <60% (too uncertain)

3. **Log matching attempts**
   - Track which events couldn't be matched
   - Identify patterns for improving normalization

4. **Consider EIN-based matching**
   - Some event platforms include org EINs
   - Would eliminate fuzzy matching errors

5. **Add more data sources**
   - Facebook Events (API required)
   - GiveSmart (gala platform)
   - Classy (fundraising platform)
   - Local foundation calendars

---

## Performance Notes

- Table insert: ~1 second for 59 events
- Fuzzy matching: ~5 seconds against 74K prospects
- View query: <1 second for 12 results
- Index on `matched_ein` essential for view performance

---

*Generated: 2025-12-12*
