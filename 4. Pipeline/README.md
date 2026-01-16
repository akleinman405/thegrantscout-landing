# V3 Pipeline: Sibling-Based Foundation Matching

**Version:** 3.0
**Updated:** 2026-01-13

## Overview

The V3 pipeline uses **sibling-based methodology** to find foundations most likely to fund a client. Instead of relying solely on statistical patterns (LASSO), V3 finds foundations that have given **target grants** (matching purpose) to **similar nonprofits** (siblings).

**Key Insight:** A foundation that gave a grant for "patient safety education" to an organization similar to yours is more likely to fund you than one that just gave any grant to any similar organization.

---

## The Matching Goal

**Find foundations who gave TARGET GRANTS to SIMILAR NONPROFITS (siblings).**

| Term | Definition |
|------|------------|
| **Sibling** | A nonprofit with similar mission (cosine similarity >= 0.50) and similar budget (0.2x to 5.0x) |
| **Target Grant** | A grant whose purpose matches the client's work (via keywords OR semantic similarity >= 0.55) |
| **Gold Standard** | Target grant + First-time grant + Geographic match |

---

## Quick Start

```bash
cd "/Users/aleckleinman/Documents/TheGrantScout/4. Pipeline"

# Step 1: Create tables (run once)
psql -h localhost -U postgres -d thegrantscout -f sql/01_create_tables.sql

# Step 2: Populate sibling grants (after siblings identified)
# Edit sql/02_populate_sibling_grants.sql with client EIN, then:
psql -h localhost -U postgres -d thegrantscout -f sql/02_populate_sibling_grants.sql

# Step 3: Generate semantic similarity (Python)
python3 scripts/generate_semantic_similarity.py --ein 462730379

# Step 4: Update keyword matches
# Edit sql/03_update_keywords.sql with client EIN, then:
psql -h localhost -U postgres -d thegrantscout -f sql/03_update_keywords.sql

# Step 5: Update target grant flags
psql -h localhost -U postgres -d thegrantscout -f sql/04_update_target_grants.sql

# Step 6: Aggregate to foundation scores
psql -h localhost -U postgres -d thegrantscout -f sql/05_aggregate_scores.sql

# Step 7: Verify quality
psql -h localhost -U postgres -d thegrantscout -f sql/06_verify_quality.sql
```

---

## Pipeline Files

### SQL Files (`sql/`)

| File | Purpose |
|------|---------|
| `01_create_tables.sql` | Create V3 tables (calc_client_sibling_grants, calc_client_foundation_scores) |
| `02_populate_sibling_grants.sql` | Insert all grants to sibling nonprofits |
| `03_update_keywords.sql` | Flag grants matching client keywords |
| `04_update_target_grants.sql` | Mark target grants (keyword OR semantic) |
| `05_aggregate_scores.sql` | Roll up to foundation-level scores |
| `06_verify_quality.sql` | Quality check queries for each step |

### Metric SQL Files (`sql/`)

| File | Purpose |
|------|---------|
| `annual_giving.sql` | Foundation annual giving metrics |
| `comparable_grant.sql` | Find comparable grants |
| `funding_trend.sql` | Foundation giving trends |
| `geographic_focus.sql` | Geographic concentration |
| `giving_style.sql` | General support vs. program-specific |
| `recipient_profile.sql` | Typical recipient profile |
| `repeat_funding.sql` | Repeat funding rate |
| `typical_grant.sql` | Typical grant size |

### Python Scripts (`scripts/`)

| File | Purpose |
|------|---------|
| `generate_semantic_similarity.py` | Calculate semantic similarity for grant purposes |

---

## Database Tables

### `calc_client_siblings`
Sibling nonprofits for each client. Pre-populated via pgvector similarity search.

### `calc_client_sibling_grants`
All grants to sibling nonprofits with flags:
- `is_first_grant` - First grant from foundation to recipient
- `purpose_quality` - Data quality indicator
- `keyword_match` - Purpose matches client keywords
- `semantic_similarity` - Cosine similarity to client mission
- `is_target_grant` - Keyword OR semantic match
- `target_grant_reason` - Why it's a target grant

### `calc_client_foundation_scores`
Aggregated scores per foundation:
- `target_grants_to_siblings` - Key ranking metric
- `gold_standard_grants` - Target + First + Geo
- Manual research fields (eligibility, opportunities)

---

## Configuration

### Environment Variables (`.env`)

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=thegrantscout
DB_USER=postgres
DB_PASSWORD=<your_password>
```

---

## Folder Structure

```
4. Pipeline/
├── scripts/
│   ├── generate_semantic_similarity.py
│   ├── utils/
│   ├── python/
│   └── r/
├── sql/
│   ├── 01-06 V3 SQL files
│   └── metric SQL files
├── config/
├── runs/
├── templates/
├── Enhancements/
├── logs/
├── outputs/
├── archive/v1/
├── .env
└── README.md
```

---

## See Also

- **Detailed Guide:** `Enhancements/2026-01-13/GUIDE_2026-01-13_PSMF_report_step_by_step.md`
- **Session State:** `Enhancements/2026-01-13/SESSION_STATE_psmf_report.md`
- **V2 Pipeline (archived):** `/Users/aleckleinman/Documents/TheGrantScout/9. Pipeline Legacy (Large CSVs)/Pipeline v2/`

---

*V3 Pipeline - Sibling Methodology*
*Created: 2026-01-13*
