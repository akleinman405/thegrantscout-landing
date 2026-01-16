# PROMPT: Build Foundation Matching Algorithm Script

**Date:** 2025-12-10  
**For:** Claude Code CLI  
**Schema:** f990_2025

---

## Context

We have all the pieces ready:
- `dim_foundations` / `calc_foundation_profiles` - foundation attributes + metrics
- `dim_recipients` / `calc_recipient_profiles` - recipient attributes + funder lists
- `fact_grants` - 8.3M grant transactions
- `grant_embeddings` - semantic vectors for grant purposes
- `dim_clients` / `client_embeddings` - client profiles + mission vectors

Now build the script that combines these to find the best foundation matches for a client.

---

## Create: `match_foundations.py`

### CLI Interface

```bash
# Match for one client
python match_foundations.py --client-id 3

# Match for all active clients
python match_foundations.py --all

# Limit results
python match_foundations.py --client-id 3 --top 100

# Output format
python match_foundations.py --client-id 3 --output json
python match_foundations.py --client-id 3 --output csv
```

**Args:**
- `--client-id` (int): Specific client to match
- `--all`: Run for all clients with status='active'
- `--top` (default: 100): Number of matches to return
- `--output` (default: json): Output format (json, csv)
- `--output-dir` (default: `./match_results/`)
- `--db-host` (default: localhost)
- `--min-openness` (default: 0.1): Minimum openness score to consider
- `--min-grants` (default: 5): Minimum grants in last 5 years
- `--exclude-inactive` (default: True): Skip foundations with no grants since 2020

---

## Matching Algorithm

### Step 1: Load Client Profile

```sql
SELECT 
    c.id, c.name, c.ein, c.state, c.sector_ntee, c.sector_broad,
    c.budget_min, c.budget_max, c.grant_size_min, c.grant_size_max,
    c.mission_text, c.project_need_text, c.populations_served,
    c.geographic_scope, c.known_funders, c.recipient_ein,
    e.mission_embedding, e.project_embedding, e.combined_embedding
FROM f990_2025.dim_clients c
LEFT JOIN f990_2025.client_embeddings e ON c.id = e.client_id
WHERE c.id = {client_id};
```

### Step 2: Pre-filter Foundations

Reduce from ~170K to ~30-50K candidates:

```sql
SELECT fp.ein
FROM f990_2025.calc_foundation_profiles fp
WHERE fp.has_grant_history = TRUE
  AND fp.last_active_year >= 2020
  AND fp.total_grants_5yr >= 5
  AND fp.openness_score >= 0.1
  AND fp.median_grant BETWEEN {client.grant_size_min * 0.5} AND {client.grant_size_max * 2}
  -- Exclude client's known funders
  AND fp.ein NOT IN (SELECT UNNEST({client.known_funders}))
```

### Step 3: Score Each Foundation

For each candidate foundation, calculate component scores (all 0-1 scale):

#### 3A: Semantic Similarity Score (weight: 0.30)

Find top 20 grants from this foundation most similar to client mission:

```sql
SELECT AVG(1 - (ge.purpose_embedding <=> {client.combined_embedding})) as semantic_score
FROM f990_2025.grant_embeddings ge
JOIN f990_2025.fact_grants fg ON ge.grant_id = fg.id
WHERE fg.foundation_ein = {foundation.ein}
ORDER BY ge.purpose_embedding <=> {client.combined_embedding}
LIMIT 20;
```

#### 3B: Collaborative Filtering Score (weight: 0.25)

If client has recipient_ein, find foundations that funded similar orgs:

```sql
-- Get client's funder list
SELECT funder_eins FROM f990_2025.calc_recipient_profiles WHERE ein = {client.recipient_ein};

-- For candidate foundation, check overlap with funders of similar recipients
WITH client_funders AS (
    SELECT UNNEST(funder_eins) as funder_ein
    FROM f990_2025.calc_recipient_profiles
    WHERE ein = {client.recipient_ein}
),
similar_recipients AS (
    -- Recipients that share funders with client
    SELECT rp.ein, COUNT(*) as shared_funders
    FROM f990_2025.calc_recipient_profiles rp, client_funders cf
    WHERE cf.funder_ein = ANY(rp.funder_eins)
      AND rp.ein != {client.recipient_ein}
    GROUP BY rp.ein
    ORDER BY shared_funders DESC
    LIMIT 100
)
SELECT COUNT(*) as funded_similar_count
FROM f990_2025.fact_grants fg
JOIN similar_recipients sr ON fg.recipient_ein = sr.ein
WHERE fg.foundation_ein = {foundation.ein};
```

Normalize to 0-1 based on max across all candidates.

If client has no recipient_ein, use NTEE similarity as fallback:
- Find recipients with same NTEE code
- Score based on how many this foundation has funded

#### 3C: Openness Score (weight: 0.20)

Direct from calc_foundation_profiles:
```python
openness_score = foundation.openness_score  # Already 0-1
```

#### 3D: Geographic Alignment (weight: 0.10)

```python
geo_focus = foundation.geographic_focus  # JSONB like {"CA": 0.6, "NY": 0.25}
client_state = client.state

if client.geographic_scope == 'national':
    geo_score = 1.0  # National orgs match anyone
elif client_state in geo_focus:
    geo_score = geo_focus[client_state]  # Direct state match
else:
    geo_score = geo_focus.get('other', 0.1)  # Weak match
```

#### 3E: Sector Alignment (weight: 0.10)

```python
sector_focus = foundation.sector_focus  # JSONB like {"B": 0.4, "P": 0.35}
client_ntee_broad = client.sector_ntee[0] if client.sector_ntee else None

if client_ntee_broad and client_ntee_broad in sector_focus:
    sector_score = sector_focus[client_ntee_broad]
else:
    sector_score = 0.2  # Weak match
```

#### 3F: Grant Size Fit (weight: 0.05)

```python
foundation_median = foundation.median_grant
client_target = (client.grant_size_min + client.grant_size_max) / 2

if client.grant_size_min <= foundation_median <= client.grant_size_max:
    size_score = 1.0
else:
    # Penalize based on distance
    ratio = foundation_median / client_target
    size_score = max(0, 1 - abs(1 - ratio) * 0.5)
```

### Step 4: Calculate Final Score

```python
final_score = (
    semantic_score * 0.30 +
    collab_score * 0.25 +
    openness_score * 0.20 +
    geo_score * 0.10 +
    sector_score * 0.10 +
    size_score * 0.05
)
```

### Step 5: Gather Evidence

For top N matches, pull supporting evidence:

```sql
-- Top 5 grants most similar to client mission
SELECT 
    fg.recipient_name_raw,
    fg.amount,
    fg.purpose_text,
    fg.tax_year,
    1 - (ge.purpose_embedding <=> {client.combined_embedding}) as similarity
FROM f990_2025.fact_grants fg
JOIN f990_2025.grant_embeddings ge ON fg.id = ge.grant_id
WHERE fg.foundation_ein = {foundation.ein}
ORDER BY ge.purpose_embedding <=> {client.combined_embedding}
LIMIT 5;
```

---

## Output Format

### JSON (per client)

```json
{
  "client_id": 3,
  "client_name": "Patient Safety Movement Foundation",
  "generated_at": "2025-12-10T14:30:00Z",
  "total_candidates": 45230,
  "matches": [
    {
      "rank": 1,
      "foundation_ein": "123456789",
      "foundation_name": "Smith Healthcare Foundation",
      "score": 0.847,
      "score_breakdown": {
        "semantic": 0.92,
        "collaborative": 0.85,
        "openness": 0.75,
        "geographic": 1.0,
        "sector": 0.80,
        "size_fit": 0.90
      },
      "foundation_stats": {
        "assets": 50000000,
        "median_grant": 25000,
        "grants_5yr": 145,
        "openness_score": 0.75,
        "last_active_year": 2023
      },
      "evidence_grants": [
        {
          "recipient": "Hospital Safety Consortium",
          "amount": 30000,
          "purpose": "Patient safety training program",
          "year": 2023,
          "similarity": 0.94
        }
      ],
      "contact": {
        "city": "Chicago",
        "state": "IL",
        "website": "https://smithhealthcare.org"
      }
    }
  ]
}
```

### CSV (for spreadsheet review)

Columns: rank, ein, name, score, semantic, collaborative, openness, geo, sector, size, assets, median_grant, grants_5yr, last_year, city, state, website, top_evidence_purpose

---

## Performance

- Pre-filter: ~170K → ~30-50K candidates (SQL, fast)
- Scoring: Batch semantic similarity queries using pgvector
- Target: < 5 minutes per client

**Optimization:**
- Batch embedding similarity as one query with `ORDER BY embedding <=> x LIMIT n`
- Cache foundation profiles in memory
- Use EXPLAIN ANALYZE on slow queries

---

## Validation Queries

```sql
-- Check score distribution (should be roughly normal, not all clustered)
SELECT 
    ROUND(score, 1) as score_bucket,
    COUNT(*) as foundations
FROM match_results
GROUP BY ROUND(score, 1)
ORDER BY score_bucket DESC;

-- Verify known funders excluded
SELECT * FROM match_results mr
JOIN f990_2025.dim_clients c ON mr.client_id = c.id
WHERE mr.foundation_ein = ANY(c.known_funders);
-- Should return 0 rows
```

---

## Output

1. `match_foundations.py` - main script
2. Test run for one client with `--top 50`
3. Sample JSON output
4. Brief report: timing, score distribution, any issues
