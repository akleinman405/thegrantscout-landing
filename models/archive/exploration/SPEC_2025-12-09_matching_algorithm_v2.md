# SPEC: Matching Algorithm v2 - Discovery-Based Foundation Matching

**Document Type:** SPEC  
**Date:** 2025-12-09  
**Status:** Draft for Dev Team Review  
**Schema:** f990_2025 (ignore public schema)

---

## 1. Overview & Core Philosophy

### The Problem with v1

The original algorithm optimized for the wrong question:
- **v1 asked:** "Which foundations are most likely to fund this nonprofit?"
- **Product promises:** "Find funders you don't already know about"

Prior relationship correlation (67-72%) is statistically accurate but counterproductive for discovery. Surfacing existing relationships shows users opportunities they already know about.

### v2 Philosophy

**Discovery-first matching** based on two insights from recommendation systems:

1. **Collaborative Filtering** (Netflix/Amazon model): "Foundations that funded Org A also funded Org B" — find foundations via similar recipients, not direct profile matching

2. **Two-Sided Matching** (Dating/Job model): Foundation must also "want" the nonprofit — openness score indicates likelihood to fund new grantees

### Core Principle

> **No black-box match score.** Rich descriptive columns on each entity + alignment between client profile and those columns = match.

The algorithm checks alignment across multiple dimensions. Foundations that align on MORE dimensions rank higher. No synthetic 0-100 composite score needed.

---

## 2. Entity Profiles (Descriptive Columns)

### 2.1 Foundation Profile

| Column | Type | Example | Source | Purpose |
|--------|------|---------|--------|---------|
| ein | VARCHAR(10) | 943106605 | pf_returns | Primary key |
| name | VARCHAR | "Ford Foundation" | pf_returns | Display |
| state | VARCHAR(2) | "NY" | pf_returns | Geographic filtering |
| assets | BIGINT | 15000000000 | pf_returns | Capacity indicator |
| accepts_applications | BOOLEAN | TRUE | Derived from `only_contri_to_preselected_ind` | Hard filter |
| grants_to_orgs | BOOLEAN | TRUE | Derived from `grants_to_organizations_ind` | Hard filter |
| last_active_year | INT | 2024 | MAX(grants.tax_year) | Recency filter |
| total_grants_5yr | INT | 450 | COUNT(grants) last 5 years | Activity level |
| total_giving_5yr | BIGINT | 125000000 | SUM(grants.amount) last 5 years | Capacity |
| median_grant | INT | 45000 | MEDIAN(grants.amount) | Size matching |
| grant_range_min | INT | 5000 | MIN(grants.amount) | Size matching |
| grant_range_max | INT | 500000 | MAX(grants.amount) | Size matching |
| geographic_focus | JSONB | {"CA": 0.60, "national": 0.25, "NY": 0.15} | Aggregated from grants | Geographic alignment |
| sector_focus | JSONB | {"education": 0.40, "health": 0.35, "arts": 0.25} | Aggregated from recipient NTEE | Sector alignment |
| project_types | JSONB | {"general_support": 0.50, "capital": 0.20, "program": 0.30} | Purpose text analysis | Project alignment |
| typical_recipient_size | VARCHAR | "medium" | Mode of recipient size_tier | Size alignment |
| openness_score | DECIMAL(3,2) | 0.35 | % grants to first-time recipients | Discovery ranking |
| repeat_rate | DECIMAL(3,2) | 0.65 | % recipients funded 2+ times | Relationship style |
| unique_recipients_5yr | INT | 180 | COUNT(DISTINCT recipient) | Breadth indicator |
| giving_trend | VARCHAR | "growing" | YoY comparison | Health indicator |
| website_url | VARCHAR | "https://fordfoundation.org" | pf_returns or scraped | Opportunity scraping |
| calculated_at | TIMESTAMP | 2025-12-09 | System | Cache management |

### 2.2 Recipient Profile

| Column | Type | Example | Source | Purpose |
|--------|------|---------|--------|---------|
| id | SERIAL | 12345 | System generated | Primary key |
| name_raw | VARCHAR | "BOYS & GIRLS CLUB OF AMERICA" | pf_grants | Original text |
| name_normalized | VARCHAR | "boys girls club america" | Normalized | Deduplication |
| ein | VARCHAR(10) | 530196550 | EIN enrichment | Deduplication, BMF lookup |
| state | VARCHAR(2) | "GA" | pf_grants.recipient_state or EIN lookup | Geographic matching |
| sector | VARCHAR(3) | "O20" | NTEE enrichment | Sector matching |
| sector_broad | VARCHAR | "Youth Development" | Derived from NTEE | Display |
| size_tier | VARCHAR | "medium" | Based on funding received or BMF | Size matching |
| total_funders | INT | 12 | COUNT(DISTINCT foundation_ein) | Popularity signal |
| total_funding_received | BIGINT | 2500000 | SUM(grants.amount) | Size proxy |
| grant_types_received | JSONB | {"general": 0.60, "program": 0.40} | Purpose text analysis | Project matching |
| years_funded | ARRAY[INT] | [2020, 2021, 2023] | From grants | Activity pattern |
| funder_eins | ARRAY[VARCHAR] | ["943106605", "131684331"] | From grants | Collaborative filtering |
| calculated_at | TIMESTAMP | 2025-12-09 | System | Cache management |

### 2.3 Grant Profile

| Column | Type | Example | Source | Purpose |
|--------|------|---------|--------|---------|
| id | SERIAL | 987654 | System generated | Primary key |
| foundation_ein | VARCHAR(10) | 943106605 | pf_grants.filer_ein | FK to foundations |
| recipient_id | INT | 12345 | Linked after dedup | FK to recipients |
| recipient_name_raw | VARCHAR | "BOYS & GIRLS CLUB" | pf_grants | Backup reference |
| amount | INT | 50000 | pf_grants.cash_grant_amt | Matching, stats |
| purpose_text | VARCHAR | "For general operating support" | pf_grants.grant_purpose | Project analysis |
| purpose_type | VARCHAR | "general_support" | Extracted from purpose_text | Project matching |
| purpose_keywords | ARRAY[VARCHAR] | ["general", "operating", "support"] | Extracted | Keyword search |
| tax_year | INT | 2023 | pf_grants | Recency weighting |
| is_first_time | BOOLEAN | TRUE | Calculated: first grant to this recipient from this foundation | Openness calc |
| source | VARCHAR | "2024_TEOS" | Import tracking | Data quality |

### 2.4 Client Profile

| Column | Type | Example (Ka Ulukoa) | Source | Purpose |
|--------|------|---------------------|--------|---------|
| id | SERIAL | 4 | System generated | Primary key |
| name | VARCHAR | "Ka Ulukoa" | Questionnaire | Display |
| ein | VARCHAR(10) | 990123456 | Questionnaire or lookup | Deduplication, BMF |
| state | VARCHAR(2) | "HI" | Questionnaire | Geographic filtering |
| city | VARCHAR | "Honolulu" | Questionnaire | Local targeting |
| sector | VARCHAR(3) | "N20" | NTEE from questionnaire | Sector alignment |
| sector_broad | VARCHAR | "Recreation/Sports" | Derived | Display |
| budget | VARCHAR | "1M-5M" | Questionnaire | Size alignment |
| budget_min | INT | 1000000 | Parsed | Queries |
| budget_max | INT | 5000000 | Parsed | Queries |
| grant_size_seeking | VARCHAR | "100K-500K" | Questionnaire | Hard filter |
| grant_size_min | INT | 100000 | Parsed | Queries |
| grant_size_max | INT | 500000 | Parsed | Queries |
| mission_text | TEXT | "We identify, select, and train youth athletes..." | Questionnaire | Semantic matching (future) |
| project_need_text | TEXT | "facility acquisition" | Questionnaire "anything else" | Project matching |
| project_type | VARCHAR | "capital" | Extracted from project_need_text | Project alignment |
| project_keywords | ARRAY[VARCHAR] | ["facility", "acquisition", "building"] | Extracted | Keyword search |
| populations_served | ARRAY[VARCHAR] | ["children", "youth"] | Questionnaire | Population alignment |
| geographic_scope | VARCHAR | "statewide" | Questionnaire | Context |
| known_funders | ARRAY[VARCHAR] | ["941234567", "942345678"] | Questionnaire + EIN lookup | Exclusion list |
| org_type | VARCHAR | "501c3" | Questionnaire | Hard filter |
| grant_capacity | VARCHAR | "no_dedicated_staff" | Questionnaire | Context |
| created_at | TIMESTAMP | 2025-11-14 | System | Tracking |
| updated_at | TIMESTAMP | 2025-12-09 | System | Recalc trigger |

---

## 3. Matching Logic

### 3.1 Hard Filters (Pass/Fail)

Every foundation must pass ALL hard filters before soft alignment is evaluated.

| Filter | Logic | Rationale |
|--------|-------|-----------|
| Accepts Applications | `foundation.accepts_applications = TRUE` | Can't apply to invite-only |
| Grants to Organizations | `foundation.grants_to_orgs = TRUE` | Some only give to individuals |
| Grant Size Overlap | `foundation.grant_range_max >= client.grant_size_min AND foundation.grant_range_min <= client.grant_size_max` | Won't fund outside their range |
| Geographic Eligibility | `client.state IN foundation.geographic_focus.keys() OR 'national' IN foundation.geographic_focus.keys()` | Many foundations are geographically restricted |
| Recently Active | `foundation.last_active_year >= CURRENT_YEAR - 2` | Don't show dormant foundations |
| Org Type Eligible | `client.org_type = '501c3' OR foundation accepts other types` | Some require 501(c)(3) |

**Result:** 85K foundations → ~5K-15K pass hard filters (varies by client)

### 3.2 Soft Alignment (Degree of Fit)

For foundations that pass hard filters, evaluate alignment across multiple dimensions:

| Dimension | Alignment Check | Signal Strength |
|-----------|-----------------|-----------------|
| **Org Similarity** | How many recipients similar to client has this foundation funded? | Count + recency |
| **Project Match** | Does foundation fund the project TYPE client needs? | % of giving to that project type |
| **Sector Alignment** | Does foundation fund client's sector? | % of giving to that sector |
| **Size Alignment** | Does foundation typically fund orgs of client's size? | Match to typical_recipient_size |
| **Geographic Bonus** | Is client in foundation's primary geography? | Higher % = stronger fit |
| **Population Alignment** | Does foundation fund orgs serving same populations? | Overlap count |
| **Openness Score** | How likely to fund NEW grantees? | Higher = better for discovery |

### 3.3 No Composite Score — Dimension Reporting

Instead of collapsing to single score, report alignment per dimension:

```json
{
  "foundation_ein": "943106605",
  "foundation_name": "Example Foundation",
  "hard_filters": "PASS",
  "alignment": {
    "org_similarity": {
      "similar_recipients_funded": 8,
      "most_recent_year": 2023,
      "strength": "strong"
    },
    "project_match": {
      "client_project_type": "capital",
      "foundation_pct_capital": 0.25,
      "matching_grants_count": 12,
      "strength": "moderate"
    },
    "sector_alignment": {
      "client_sector": "N20",
      "foundation_pct_sector": 0.15,
      "strength": "weak"
    },
    "size_alignment": {
      "client_size": "medium",
      "foundation_typical": "medium",
      "strength": "strong"
    },
    "geographic": {
      "client_state": "HI",
      "foundation_pct_state": 0.05,
      "foundation_pct_national": 0.60,
      "strength": "moderate"
    },
    "openness": {
      "score": 0.35,
      "strength": "moderate"
    }
  },
  "tier": 1,
  "match_reasons": [
    "Funded 8 similar youth-serving organizations",
    "25% of giving goes to capital/facility projects",
    "35% of grants go to first-time recipients"
  ]
}
```

### 3.4 Ranking Logic

```
TIER 1 (Top Matches):
  - Strong org_similarity (5+ similar recipients funded)
  - AND strong project_match (15%+ of giving to project type)
  - AND openness_score > 0.25
  
TIER 2 (Good Matches):
  - Strong on org_similarity OR project_match (not both)
  - AND openness_score > 0.20
  
TIER 3 (Possible Matches):
  - Moderate alignment on multiple dimensions
  - OR strong on one dimension with lower openness

Within tiers, sort by:
  1. similar_recipients_funded (DESC)
  2. openness_score (DESC)
  3. foundation_pct_to_project_type (DESC)
  4. last_grant_year (DESC) — recency tiebreaker
```

---

## 4. Two-Phase Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: FOUNDATION DISCOVERY                                   │
│ Triggers: (a) New F990 data import, (b) Client profile changes  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CLIENT PROFILE                                                 │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ HARD FILTERS                                                ││
│  │ • Accepts applications?                                     ││
│  │ • Grants to organizations?                                  ││
│  │ • Grant size range overlaps?                                ││
│  │ • Geographic eligibility?                                   ││
│  │ • Active in past 2 years?                                   ││
│  │ • Org type eligible?                                        ││
│  └──────────────────────┬──────────────────────────────────────┘│
│                         │                                       │
│         (85K foundations → ~8K pass filters)                    │
│                         │                                       │
│                         ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ PATH A: ORG SIMILARITY MATCHING                             ││
│  │                                                             ││
│  │ 1. Find recipients SIMILAR to client:                       ││
│  │    - Same state                                             ││
│  │    - Same/similar sector (NTEE)                             ││
│  │    - Similar size tier                                      ││
│  │    - Overlapping populations served                         ││
│  │    - Similar mission keywords (future: embeddings)          ││
│  │                                                             ││
│  │ 2. Find foundations that funded those similar recipients    ││
│  │                                                             ││
│  │ 3. Score: COUNT of similar recipients funded + recency      ││
│  └──────────────────────┬──────────────────────────────────────┘│
│                         │                                       │
│                         ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ PATH B: PROJECT MATCHING                                    ││
│  │                                                             ││
│  │ 1. Extract client's project keywords:                       ││
│  │    "facility acquisition" → [facility, capital, building]   ││
│  │                                                             ││
│  │ 2. Search grants.purpose_keywords for matches               ││
│  │                                                             ││
│  │ 3. Find foundations that made those grants                  ││
│  │                                                             ││
│  │ 4. Score: COUNT of matching grants + % of foundation giving ││
│  └──────────────────────┬──────────────────────────────────────┘│
│                         │                                       │
│                         ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ COMBINE + RANK                                              ││
│  │                                                             ││
│  │ • Foundations strong on BOTH paths = Tier 1                 ││
│  │ • Foundations strong on ONE path = Tier 2                   ││
│  │ • Apply openness_score as ranking boost                     ││
│  │ • EXCLUDE client's known_funders                            ││
│  │ • Output: Top 50-100 matched foundations with reasons       ││
│  └──────────────────────┬──────────────────────────────────────┘│
│                         │                                       │
│                         ▼                                       │
│              MATCHED FOUNDATIONS TABLE                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: OPPORTUNITY MATCHING                                   │
│ Triggers: (a) New opportunities scraped, (b) Foundation matches │
│           change, (c) Daily deadline check                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MATCHED FOUNDATIONS (from Phase 1)                             │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ JOIN TO OPPORTUNITIES                                       ││
│  │                                                             ││
│  │ • Match by foundation EIN                                   ││
│  │ • Filter: deadline > TODAY + 14 days                        ││
│  │ • Filter: opportunity.status = 'open'                       ││
│  └──────────────────────┬──────────────────────────────────────┘│
│                         │                                       │
│                         ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ RANK OPPORTUNITIES                                          ││
│  │                                                             ││
│  │ Sort by:                                                    ││
│  │ 1. Foundation tier (from Phase 1)                           ││
│  │ 2. Project type fit to opportunity                          ││
│  │ 3. Amount fit (opportunity range vs client seeking)         ││
│  │ 4. Deadline urgency (sooner = surface earlier)              ││
│  └──────────────────────┬──────────────────────────────────────┘│
│                         │                                       │
│                         ▼                                       │
│              TOP 5-10 OPPORTUNITIES FOR REPORT                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Recalculation Triggers

| Event | What Recalculates | Frequency |
|-------|-------------------|-----------|
| **New F990 Data Import** | All foundation_profiles, recipient_profiles, grants. Then all client matches. | Annual (or when new TEOS released) |
| **Client Profile Changes** | That client's similar_recipients, foundation_matches, opportunity_matches | On-demand |
| **New Client Added** | That client's similar_recipients, foundation_matches, opportunity_matches | On-demand |
| **New Opportunities Scraped** | All client opportunity_matches | Weekly or on-demand |
| **Daily Deadline Check** | Flag expired opportunities, re-rank by urgency | Daily |

### Cascade Logic

```
F990 Import
    └── Rebuild: foundations, recipients, grants
        └── Rebuild: foundation_profiles, recipient_profiles
            └── Rebuild: ALL client_similar_recipients
                └── Rebuild: ALL client_foundation_matches
                    └── Rebuild: ALL client_opportunity_matches

Client Profile Update
    └── Rebuild: THIS client's client_similar_recipients
        └── Rebuild: THIS client's client_foundation_matches
            └── Rebuild: THIS client's client_opportunity_matches
```

---

## 6. Data Infrastructure

### 6.1 Schema: f990_2025

All tables in `f990_2025` schema. Ignore `public` schema.

### 6.2 Table Categories

```
SOURCE TABLES (raw imported data)
=================================
src_pf_returns       - Raw 990-PF filings (existing: pf_returns)
src_pf_grants        - Raw grant records (existing: pf_grants)
src_nonprofit_returns - Raw 990/990-EZ filings (existing: nonprofit_returns)
src_officers         - Raw officer records (existing: officers)
src_schedule_a       - Raw Schedule A (existing: schedule_a)

DIMENSION TABLES (one row per entity, deduplicated)
===================================================
dim_foundations      - One row per foundation EIN
dim_recipients       - One row per unique recipient (deduplicated)
dim_clients          - One row per paying client

FACT TABLES (transactions)
==========================
fact_grants          - One row per grant, linked to dim tables

CALCULATED TABLES (derived metrics)
===================================
calc_foundation_profiles  - Aggregated stats per foundation
calc_recipient_profiles   - Aggregated stats per recipient
calc_recurring_programs   - Detected ongoing grant programs

CLIENT MATCH TABLES (per-client calculations)
=============================================
match_similar_recipients  - Which recipients are similar to each client
match_client_foundations  - Ranked foundations per client
match_client_opportunities - Ranked opportunities per client

OPPORTUNITY TABLES (external data)
==================================
dim_opportunities    - Live RFPs with deadlines, scraped or manual
```

### 6.3 Table Definitions

#### dim_foundations
```sql
CREATE TABLE f990_2025.dim_foundations (
    ein VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    state VARCHAR(2),
    city VARCHAR(100),
    assets BIGINT,
    accepts_applications BOOLEAN DEFAULT TRUE,
    grants_to_orgs BOOLEAN DEFAULT TRUE,
    website_url VARCHAR(500),
    last_return_year INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Populated from: Most recent pf_returns per EIN
-- accepts_applications derived from: only_contri_to_preselected_ind = FALSE or NULL
-- grants_to_orgs derived from: grants_to_organizations_ind = TRUE or NULL
```

#### dim_recipients
```sql
CREATE TABLE f990_2025.dim_recipients (
    id SERIAL PRIMARY KEY,
    name_raw VARCHAR(255) NOT NULL,
    name_normalized VARCHAR(255) NOT NULL,
    ein VARCHAR(10),  -- NULL if not enriched
    state VARCHAR(2),
    city VARCHAR(100),
    sector_ntee VARCHAR(10),  -- NULL if not enriched
    sector_broad VARCHAR(100),
    size_tier VARCHAR(20),  -- 'small', 'medium', 'large', 'major'
    first_seen_year INT,
    last_seen_year INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(name_normalized, state)  -- Dedup key
);

CREATE INDEX idx_recipients_state ON f990_2025.dim_recipients(state);
CREATE INDEX idx_recipients_sector ON f990_2025.dim_recipients(sector_ntee);
CREATE INDEX idx_recipients_ein ON f990_2025.dim_recipients(ein);
```

#### dim_clients
```sql
CREATE TABLE f990_2025.dim_clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ein VARCHAR(10),
    state VARCHAR(2) NOT NULL,
    city VARCHAR(100),
    sector_ntee VARCHAR(10),
    sector_broad VARCHAR(100),
    budget_tier VARCHAR(20),
    budget_min INT,
    budget_max INT,
    grant_size_seeking VARCHAR(50),
    grant_size_min INT,
    grant_size_max INT,
    mission_text TEXT,
    project_need_text TEXT,
    project_type VARCHAR(50),
    project_keywords VARCHAR(255)[],
    populations_served VARCHAR(100)[],
    geographic_scope VARCHAR(50),
    known_funders VARCHAR(10)[],  -- Array of EINs
    org_type VARCHAR(20) DEFAULT '501c3',
    grant_capacity VARCHAR(50),
    email VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### fact_grants
```sql
CREATE TABLE f990_2025.fact_grants (
    id SERIAL PRIMARY KEY,
    foundation_ein VARCHAR(10) NOT NULL REFERENCES f990_2025.dim_foundations(ein),
    recipient_id INT REFERENCES f990_2025.dim_recipients(id),
    recipient_name_raw VARCHAR(255),  -- Backup if recipient_id NULL
    recipient_state VARCHAR(2),
    amount INT,
    purpose_text VARCHAR(1000),
    purpose_type VARCHAR(50),
    purpose_keywords VARCHAR(100)[],
    tax_year INT NOT NULL,
    is_first_time BOOLEAN,  -- First grant from this foundation to this recipient
    source VARCHAR(50),  -- '2023_TEOS', '2024_TEOS', etc.
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (foundation_ein) REFERENCES f990_2025.dim_foundations(ein)
);

CREATE INDEX idx_grants_foundation ON f990_2025.fact_grants(foundation_ein);
CREATE INDEX idx_grants_recipient ON f990_2025.fact_grants(recipient_id);
CREATE INDEX idx_grants_year ON f990_2025.fact_grants(tax_year);
CREATE INDEX idx_grants_purpose_type ON f990_2025.fact_grants(purpose_type);
CREATE INDEX idx_grants_purpose_keywords ON f990_2025.fact_grants USING GIN(purpose_keywords);
```

#### calc_foundation_profiles
```sql
CREATE TABLE f990_2025.calc_foundation_profiles (
    ein VARCHAR(10) PRIMARY KEY REFERENCES f990_2025.dim_foundations(ein),
    
    -- Activity metrics
    total_grants_5yr INT,
    total_giving_5yr BIGINT,
    unique_recipients_5yr INT,
    last_active_year INT,
    
    -- Grant size metrics
    median_grant INT,
    avg_grant INT,
    grant_range_min INT,
    grant_range_max INT,
    
    -- Focus metrics (JSONB for flexibility)
    geographic_focus JSONB,  -- {"CA": 0.60, "national": 0.25}
    sector_focus JSONB,      -- {"education": 0.40, "health": 0.35}
    project_types JSONB,     -- {"general_support": 0.50, "capital": 0.20}
    
    -- Recipient profile
    typical_recipient_size VARCHAR(20),
    
    -- Openness metrics
    openness_score DECIMAL(3,2),  -- % to first-time recipients
    repeat_rate DECIMAL(3,2),     -- % recipients funded 2+ times
    
    -- Trend
    giving_trend VARCHAR(20),  -- 'growing', 'stable', 'declining'
    trend_pct_change DECIMAL(5,2),
    
    calculated_at TIMESTAMP DEFAULT NOW()
);
```

#### calc_recipient_profiles
```sql
CREATE TABLE f990_2025.calc_recipient_profiles (
    recipient_id INT PRIMARY KEY REFERENCES f990_2025.dim_recipients(id),
    
    -- Funding received
    total_funders INT,
    total_funding_received BIGINT,
    avg_grant_received INT,
    
    -- Patterns
    grant_types_received JSONB,  -- {"general": 0.60, "program": 0.40}
    years_funded INT[],
    funder_eins VARCHAR(10)[],
    
    -- Inferred attributes (from grant purposes)
    inferred_keywords VARCHAR(100)[],
    
    calculated_at TIMESTAMP DEFAULT NOW()
);
```

#### calc_recurring_programs
```sql
CREATE TABLE f990_2025.calc_recurring_programs (
    id SERIAL PRIMARY KEY,
    foundation_ein VARCHAR(10) REFERENCES f990_2025.dim_foundations(ein),
    
    -- Program identification
    program_pattern VARCHAR(500),  -- Normalized purpose text
    purpose_keywords VARCHAR(100)[],
    
    -- Activity
    years_active INT,
    year_list INT[],
    unique_recipients INT,
    total_grants INT,
    
    -- Amounts
    avg_amount INT,
    min_amount INT,
    max_amount INT,
    
    -- Recipient profile
    typical_recipient_profile JSONB,  -- {"state": "CA", "sector": "education", "size": "medium"}
    
    last_awarded_year INT,
    calculated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recurring_foundation ON f990_2025.calc_recurring_programs(foundation_ein);
CREATE INDEX idx_recurring_keywords ON f990_2025.calc_recurring_programs USING GIN(purpose_keywords);
```

#### match_similar_recipients
```sql
CREATE TABLE f990_2025.match_similar_recipients (
    client_id INT REFERENCES f990_2025.dim_clients(id),
    recipient_id INT REFERENCES f990_2025.dim_recipients(id),
    
    -- Similarity breakdown
    similarity_score DECIMAL(3,2),  -- 0.00 to 1.00
    similarity_reasons JSONB,  -- {"geography": 0.3, "sector": 0.4, "size": 0.2}
    
    -- Flags
    same_state BOOLEAN,
    same_sector BOOLEAN,
    same_size_tier BOOLEAN,
    
    calculated_at TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (client_id, recipient_id)
);

CREATE INDEX idx_similar_client ON f990_2025.match_similar_recipients(client_id);
CREATE INDEX idx_similar_score ON f990_2025.match_similar_recipients(similarity_score DESC);
```

#### match_client_foundations
```sql
CREATE TABLE f990_2025.match_client_foundations (
    client_id INT REFERENCES f990_2025.dim_clients(id),
    foundation_ein VARCHAR(10) REFERENCES f990_2025.dim_foundations(ein),
    
    -- Tier assignment
    tier INT,  -- 1, 2, or 3
    
    -- Alignment details
    alignment JSONB,  -- Full alignment object (see Section 3.3)
    
    -- Summary scores for sorting
    similar_recipients_funded INT,
    project_match_score DECIMAL(3,2),
    sector_alignment_score DECIMAL(3,2),
    openness_score DECIMAL(3,2),
    
    -- Reasons (for display)
    match_reasons TEXT[],
    
    -- Status
    status VARCHAR(20) DEFAULT 'new',  -- 'new', 'viewed', 'applied', 'excluded'
    
    calculated_at TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (client_id, foundation_ein)
);

CREATE INDEX idx_match_client ON f990_2025.match_client_foundations(client_id);
CREATE INDEX idx_match_tier ON f990_2025.match_client_foundations(tier);
```

#### dim_opportunities
```sql
CREATE TABLE f990_2025.dim_opportunities (
    id SERIAL PRIMARY KEY,
    foundation_ein VARCHAR(10) REFERENCES f990_2025.dim_foundations(ein),
    
    -- Opportunity details
    program_name VARCHAR(255),
    description TEXT,
    amount_min INT,
    amount_max INT,
    
    -- Dates
    deadline DATE,
    cycle VARCHAR(50),  -- 'annual', 'quarterly', 'rolling', 'one-time'
    
    -- Requirements
    geographic_requirements VARCHAR(255),
    org_type_requirements VARCHAR(100),
    sector_requirements VARCHAR(255),
    
    -- Application
    application_url VARCHAR(500),
    contact_name VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    
    -- Status
    status VARCHAR(20) DEFAULT 'open',  -- 'open', 'closed', 'paused'
    verified_at TIMESTAMP,
    
    -- Source
    source VARCHAR(50),  -- 'website_scrape', 'manual', 'sam_gov', etc.
    source_url VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_opp_foundation ON f990_2025.dim_opportunities(foundation_ein);
CREATE INDEX idx_opp_deadline ON f990_2025.dim_opportunities(deadline);
CREATE INDEX idx_opp_status ON f990_2025.dim_opportunities(status);
```

#### match_client_opportunities
```sql
CREATE TABLE f990_2025.match_client_opportunities (
    client_id INT REFERENCES f990_2025.dim_clients(id),
    opportunity_id INT REFERENCES f990_2025.dim_opportunities(id),
    
    -- Inherited from foundation match
    foundation_ein VARCHAR(10),
    foundation_tier INT,
    
    -- Opportunity-specific fit
    amount_fit_score DECIMAL(3,2),
    project_fit_score DECIMAL(3,2),
    
    -- Deadline
    deadline DATE,
    days_until_deadline INT,
    urgency VARCHAR(20),  -- 'urgent', 'upcoming', 'future'
    
    -- Ranking
    rank INT,  -- 1 = top opportunity for this client
    
    -- Status
    status VARCHAR(20) DEFAULT 'new',
    
    calculated_at TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (client_id, opportunity_id)
);

CREATE INDEX idx_client_opp_client ON f990_2025.match_client_opportunities(client_id);
CREATE INDEX idx_client_opp_rank ON f990_2025.match_client_opportunities(rank);
```

---

## 7. Validation Approach (Backtesting)

### 7.1 Method

Use historical data to test if algorithm would have predicted actual funding:

```
TRAINING DATA:   Grants from 2020-2022
TEST DATA:       Grants from 2023
HOLDOUT DATA:    Grants from 2024 (final validation)
```

### 7.2 Process

```sql
-- Step 1: Build profiles using only 2020-2022 data
-- (Pretend 2023+ doesn't exist)

-- Step 2: For each recipient that received a grant in 2023,
-- treat them as a "client" and run the matching algorithm

-- Step 3: Check if the foundation that ACTUALLY funded them
-- appears in our top N matches

WITH test_grants AS (
    SELECT DISTINCT recipient_id, foundation_ein
    FROM fact_grants
    WHERE tax_year = 2023
      AND recipient_id IS NOT NULL
),
algorithm_predictions AS (
    -- Run matching algorithm for each recipient
    -- Returns top 50 foundations per "client"
    SELECT recipient_id AS client_id, foundation_ein, tier, rank
    FROM match_client_foundations
    WHERE calculated_using_years <= 2022
)
SELECT 
    tg.recipient_id,
    tg.foundation_ein AS actual_funder,
    ap.rank AS predicted_rank,
    CASE 
        WHEN ap.rank <= 10 THEN 'top_10'
        WHEN ap.rank <= 25 THEN 'top_25'
        WHEN ap.rank <= 50 THEN 'top_50'
        WHEN ap.rank IS NOT NULL THEN 'in_list'
        ELSE 'missed'
    END AS prediction_quality
FROM test_grants tg
LEFT JOIN algorithm_predictions ap 
    ON tg.recipient_id = ap.client_id 
    AND tg.foundation_ein = ap.foundation_ein;
```

### 7.3 Success Metrics

| Metric | Target | Meaning |
|--------|--------|---------|
| **Top-10 Hit Rate** | >15% | Of grants that happened, we predicted funder in top 10 |
| **Top-25 Hit Rate** | >30% | Predicted in top 25 |
| **Top-50 Hit Rate** | >50% | Predicted in top 50 |
| **Miss Rate** | <30% | Actual funder not in our list at all |

### 7.4 Segmented Analysis

Run metrics separately for:
- First-time recipients (harder to predict)
- Repeat recipients (easier, but less relevant for discovery)
- By sector (some may be easier than others)
- By geography (some states have more foundation activity)

---

## 8. Build Sequence

### Phase 1: Entity Tables (Week 1)

```
1.1 Create dim_foundations
    - Query: SELECT DISTINCT ON (ein) FROM pf_returns ORDER BY tax_year DESC
    - Derive: accepts_applications, grants_to_orgs
    - Expected: ~85K rows

1.2 Create dim_recipients  
    - Query: SELECT DISTINCT name, state FROM pf_grants
    - Normalize: UPPER, remove punctuation, standard abbreviations
    - Dedupe: Group by (name_normalized, state)
    - Expected: ~500K-800K rows

1.3 Create fact_grants
    - Query: SELECT * FROM pf_grants with enrichments
    - Link: recipient_id via name_normalized + state lookup
    - Calculate: is_first_time per (foundation, recipient) pair
    - Expected: ~1.5M-2M rows

1.4 Create dim_clients
    - Source: Questionnaire data
    - Parse: Extract project_keywords from project_need_text
    - Lookup: Convert known funder names to EINs
    - Expected: ~7 rows (current beta)
```

### Phase 2: Calculated Tables (Week 2)

```
2.1 Create calc_foundation_profiles
    - Aggregate: grants by foundation
    - Calculate: openness_score = COUNT(is_first_time=TRUE) / COUNT(*)
    - Calculate: geographic_focus, sector_focus, project_types
    - Expected: ~85K rows

2.2 Create calc_recipient_profiles
    - Aggregate: grants by recipient
    - Calculate: funder_eins array, grant_types_received
    - Expected: ~500K-800K rows

2.3 Create calc_recurring_programs
    - Query: Group grants by (foundation, purpose_normalized)
    - Filter: 2+ years, 2+ unique recipients
    - Expected: ~10K-50K rows
```

### Phase 3: Matching Infrastructure (Week 3)

```
3.1 Implement recipient similarity calculation
    - Function: calculate_similar_recipients(client_id)
    - Logic: Score based on state, sector, size, keywords
    - Output: Top 500 similar recipients per client

3.2 Implement foundation matching
    - Function: calculate_foundation_matches(client_id)
    - Logic: Hard filters → Org similarity → Project matching → Combine
    - Output: Top 100 foundations per client with alignment details

3.3 Populate match tables for existing clients
    - Run: calculate_similar_recipients for each client
    - Run: calculate_foundation_matches for each client
```

### Phase 4: Validation (Week 4)

```
4.1 Build backtesting framework
    - Create: training/test data splits
    - Implement: prediction vs actual comparison

4.2 Run initial backtest
    - Measure: Hit rates at top-10, top-25, top-50
    - Identify: Which types of grants we miss and why

4.3 Tune and iterate
    - Adjust: Similarity weights, tier thresholds
    - Re-run: Backtest until targets met
```

### Phase 5: Opportunity Integration (Week 5)

```
5.1 Populate dim_opportunities
    - Source: Existing opportunities table + scraping
    - Link: foundation_ein to dim_foundations

5.2 Implement opportunity matching
    - Function: calculate_opportunity_matches(client_id)
    - Logic: Join to foundation matches → Filter by deadline → Rank

5.3 Generate test reports
    - Output: Top 5 opportunities per client
    - Validate: Manual review for quality
```

---

## 9. Example Queries

### 9.1 Find Similar Recipients for a Client

```sql
-- For client Ka Ulukoa (youth athletics, HI, medium budget)
WITH client AS (
    SELECT * FROM dim_clients WHERE name = 'Ka Ulukoa'
)
SELECT 
    r.id,
    r.name_raw,
    r.state,
    r.sector_broad,
    r.size_tier,
    -- Similarity scoring
    (CASE WHEN r.state = c.state THEN 0.3 ELSE 0 END) +
    (CASE WHEN r.sector_ntee LIKE LEFT(c.sector_ntee, 1) || '%' THEN 0.4 ELSE 0 END) +
    (CASE WHEN r.size_tier = c.budget_tier THEN 0.2 ELSE 0 END) +
    (CASE WHEN 'youth' = ANY(c.populations_served) AND r.sector_broad ILIKE '%youth%' THEN 0.1 ELSE 0 END)
    AS similarity_score
FROM dim_recipients r, client c
WHERE r.state = c.state  -- Start with same state for performance
   OR r.sector_ntee LIKE LEFT(c.sector_ntee, 1) || '%'  -- Same sector category
ORDER BY similarity_score DESC
LIMIT 500;
```

### 9.2 Find Foundations via Similar Recipients

```sql
-- Foundations that funded recipients similar to client
WITH similar AS (
    SELECT recipient_id, similarity_score
    FROM match_similar_recipients
    WHERE client_id = 4  -- Ka Ulukoa
      AND similarity_score > 0.5
)
SELECT 
    f.ein,
    f.name,
    fp.openness_score,
    COUNT(DISTINCT g.recipient_id) AS similar_orgs_funded,
    AVG(s.similarity_score) AS avg_similarity,
    MAX(g.tax_year) AS most_recent_year,
    ARRAY_AGG(DISTINCT r.name_raw ORDER BY r.name_raw) FILTER (WHERE s.similarity_score > 0.7) AS example_recipients
FROM similar s
JOIN fact_grants g ON g.recipient_id = s.recipient_id
JOIN dim_foundations f ON f.ein = g.foundation_ein
JOIN calc_foundation_profiles fp ON fp.ein = f.ein
JOIN dim_recipients r ON r.id = s.recipient_id
WHERE f.accepts_applications = TRUE
  AND fp.last_active_year >= 2022
  AND g.tax_year >= 2020
  AND f.ein NOT IN (SELECT UNNEST(known_funders) FROM dim_clients WHERE id = 4)
GROUP BY f.ein, f.name, fp.openness_score
HAVING COUNT(DISTINCT g.recipient_id) >= 2
ORDER BY similar_orgs_funded DESC, avg_similarity DESC, fp.openness_score DESC
LIMIT 50;
```

### 9.3 Find Foundations via Project Matching

```sql
-- Foundations that fund "facility acquisition" type projects
WITH client AS (
    SELECT * FROM dim_clients WHERE id = 4  -- Ka Ulukoa
)
SELECT 
    f.ein,
    f.name,
    fp.openness_score,
    COUNT(*) AS matching_grants,
    fp.project_types->>'capital' AS pct_capital_giving,
    AVG(g.amount) AS avg_grant_amount,
    MAX(g.tax_year) AS most_recent_year
FROM fact_grants g
JOIN dim_foundations f ON f.ein = g.foundation_ein
JOIN calc_foundation_profiles fp ON fp.ein = f.ein
JOIN client c ON TRUE
WHERE f.accepts_applications = TRUE
  AND fp.last_active_year >= 2022
  AND g.tax_year >= 2020
  AND (
      g.purpose_keywords && c.project_keywords  -- Array overlap
      OR g.purpose_type IN ('capital', 'facility', 'building', 'construction')
  )
  AND f.ein NOT IN (SELECT UNNEST(c.known_funders))
GROUP BY f.ein, f.name, fp.openness_score, fp.project_types->>'capital'
ORDER BY matching_grants DESC, (fp.project_types->>'capital')::DECIMAL DESC
LIMIT 50;
```

### 9.4 Combined Foundation Match

```sql
-- Combine org similarity and project matching
WITH org_matches AS (
    -- Query from 9.2
    SELECT ein, similar_orgs_funded, avg_similarity
    FROM (/* query 9.2 */) org
),
project_matches AS (
    -- Query from 9.3
    SELECT ein, matching_grants, pct_capital_giving
    FROM (/* query 9.3 */) proj
)
SELECT 
    COALESCE(o.ein, p.ein) AS ein,
    f.name,
    fp.openness_score,
    COALESCE(o.similar_orgs_funded, 0) AS similar_orgs_funded,
    COALESCE(p.matching_grants, 0) AS matching_grants,
    CASE 
        WHEN o.similar_orgs_funded >= 3 AND p.matching_grants >= 5 THEN 1
        WHEN o.similar_orgs_funded >= 3 OR p.matching_grants >= 5 THEN 2
        ELSE 3
    END AS tier
FROM org_matches o
FULL OUTER JOIN project_matches p ON o.ein = p.ein
JOIN dim_foundations f ON f.ein = COALESCE(o.ein, p.ein)
JOIN calc_foundation_profiles fp ON fp.ein = f.ein
ORDER BY tier, 
         (COALESCE(o.similar_orgs_funded, 0) + COALESCE(p.matching_grants, 0)) DESC,
         fp.openness_score DESC;
```

---

## 10. Open Questions for Dev Team

1. **Recipient Deduplication Strategy**
   - Current plan: (name_normalized, state) as unique key
   - Alternative: Use EIN where available, fuzzy match names
   - Question: What's acceptable false-positive rate for dedup?

2. **Keyword Extraction Approach**
   - Option A: Simple dictionary/regex (fast, limited)
   - Option B: NLP extraction (better, more complex)
   - Option C: LLM classification (best, expensive)
   - Recommendation: Start with Option A, upgrade later

3. **Similarity Computation Timing**
   - Option A: Precompute for all clients nightly
   - Option B: Compute on-demand when client requests
   - Recommendation: Precompute (only ~10-100 clients)

4. **Sector Alignment Without NTEE**
   - Many recipients lack NTEE codes
   - Option A: Infer from grant purpose keywords
   - Option B: BMF lookup by EIN (requires enrichment)
   - Option C: Skip sector for un-enriched recipients

5. **Openness Score Edge Cases**
   - Foundations with <10 grants: unreliable %
   - Solution: Require minimum grant count, or apply confidence adjustment

---

## 11. Semantic Matching via Embeddings

### 11.1 Overview

Rather than maintaining keyword dictionaries, use sentence embeddings to:
1. Automatically cluster similar organizations
2. Find similar recipients via vector similarity
3. Extract meaning from mission/purpose text without manual rules

**Why embeddings over keywords:**

| Keyword Approach | Embedding Approach |
|------------------|-------------------|
| Must manually define "youth" = ["youth", "children", "kids", "teen"] | Synonyms cluster automatically |
| Misses "Boys & Girls Club" (no keyword match) | Clusters correctly by meaning |
| Constant maintenance as new terms appear | Self-organizing |
| Hard to rank "how similar" | Cosine similarity = continuous score |

### 11.2 Technical Stack

```
sentence-transformers    - Generate embeddings (free, local, fast)
pgvector                - PostgreSQL extension for vector storage/search
scikit-learn            - Clustering (HDBSCAN or KMeans)
```

**Model choice:** `all-MiniLM-L6-v2`
- 384-dimension vectors
- 14,000 sentences/second on CPU
- No GPU required
- Free, open source

### 11.3 Implementation Steps

```
STEP 1: Install dependencies
────────────────────────────
pip install sentence-transformers scikit-learn

# PostgreSQL pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;


STEP 2: Extract texts to embed
──────────────────────────────
-- Nonprofit missions
SELECT DISTINCT 
    ein,
    COALESCE(primary_exempt_purpose, mission_description) as mission_text
FROM nonprofit_returns 
WHERE primary_exempt_purpose IS NOT NULL 
   OR mission_description IS NOT NULL;

-- Grant purposes  
SELECT DISTINCT purpose_text
FROM pf_grants
WHERE purpose_text IS NOT NULL
  AND LENGTH(purpose_text) > 10;

Expected: ~500K-1M unique texts


STEP 3: Generate embeddings
───────────────────────────
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Batch process for efficiency
texts = [...]  # list of mission/purpose strings
embeddings = model.encode(texts, show_progress_bar=True, batch_size=128)

# ~70 seconds for 1M texts on CPU


STEP 4: Store in PostgreSQL
───────────────────────────
-- Add vector column to recipients table
ALTER TABLE f990_2025.dim_recipients 
ADD COLUMN mission_embedding vector(384);

-- Add vector column to grants table
ALTER TABLE f990_2025.fact_grants
ADD COLUMN purpose_embedding vector(384);

-- Create index for fast similarity search
CREATE INDEX idx_recipient_embedding 
ON f990_2025.dim_recipients 
USING ivfflat (mission_embedding vector_cosine_ops)
WITH (lists = 100);


STEP 5: Cluster similar organizations
─────────────────────────────────────
from sklearn.cluster import KMeans

# Cluster into ~100-200 groups
n_clusters = 150
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(embeddings)

# Store cluster assignments
UPDATE dim_recipients SET cluster_id = %s WHERE id = %s;


STEP 6: Label clusters (one-time)
─────────────────────────────────
For each cluster:
  - Sample 10-20 mission statements
  - Use LLM to generate label: "youth athletics", "senior housing", etc.
  - Store in cluster_labels table

-- Or manual review of top 50 clusters (covers 80%+ of orgs)
```

### 11.4 Schema Additions for Embeddings

```sql
-- Add pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Cluster definitions
CREATE TABLE f990_2025.ref_clusters (
    id SERIAL PRIMARY KEY,
    label VARCHAR(100),           -- "youth_athletics", "senior_services"
    label_broad VARCHAR(50),      -- "youth", "seniors"
    sample_missions TEXT[],       -- Example texts for reference
    centroid vector(384),         -- Cluster center for assignment
    member_count INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add to dim_recipients
ALTER TABLE f990_2025.dim_recipients ADD COLUMN IF NOT EXISTS
    mission_text TEXT,
    mission_embedding vector(384),
    cluster_id INT REFERENCES f990_2025.ref_clusters(id);

-- Add to fact_grants  
ALTER TABLE f990_2025.fact_grants ADD COLUMN IF NOT EXISTS
    purpose_embedding vector(384);

-- Add to dim_clients
ALTER TABLE f990_2025.dim_clients ADD COLUMN IF NOT EXISTS
    mission_embedding vector(384),
    project_embedding vector(384);

-- Vector similarity index
CREATE INDEX idx_recipient_embedding 
ON f990_2025.dim_recipients 
USING ivfflat (mission_embedding vector_cosine_ops)
WITH (lists = 100);
```

### 11.5 Similarity Queries with Embeddings

**Find similar recipients to a client:**
```sql
-- Using pgvector's cosine distance operator <=>
SELECT 
    r.id,
    r.name_raw,
    r.state,
    r.cluster_id,
    rc.label as cluster_label,
    1 - (r.mission_embedding <=> c.mission_embedding) as similarity_score
FROM f990_2025.dim_recipients r
JOIN f990_2025.ref_clusters rc ON rc.id = r.cluster_id
CROSS JOIN f990_2025.dim_clients c
WHERE c.id = 4  -- Ka Ulukoa
  AND r.mission_embedding IS NOT NULL
ORDER BY r.mission_embedding <=> c.mission_embedding  -- Nearest neighbors
LIMIT 500;
```

**Find grants with similar purposes to client's project need:**
```sql
-- Client wants "facility acquisition"
-- Find grants with semantically similar purposes
SELECT 
    g.foundation_ein,
    g.purpose_text,
    g.amount,
    1 - (g.purpose_embedding <=> c.project_embedding) as similarity_score
FROM f990_2025.fact_grants g
CROSS JOIN f990_2025.dim_clients c
WHERE c.id = 4
  AND g.purpose_embedding IS NOT NULL
  AND g.tax_year >= 2020
ORDER BY g.purpose_embedding <=> c.project_embedding
LIMIT 100;
```

**Find foundations that fund semantically similar projects:**
```sql
-- Aggregate: which foundations made grants similar to client's need?
WITH similar_grants AS (
    SELECT 
        g.foundation_ein,
        g.purpose_text,
        g.amount,
        1 - (g.purpose_embedding <=> c.project_embedding) as similarity
    FROM f990_2025.fact_grants g
    CROSS JOIN f990_2025.dim_clients c
    WHERE c.id = 4
      AND g.purpose_embedding IS NOT NULL
      AND 1 - (g.purpose_embedding <=> c.project_embedding) > 0.6  -- Threshold
)
SELECT 
    foundation_ein,
    COUNT(*) as similar_grants_count,
    AVG(similarity) as avg_similarity,
    AVG(amount) as avg_amount,
    ARRAY_AGG(purpose_text ORDER BY similarity DESC) FILTER (WHERE similarity > 0.7) as example_purposes
FROM similar_grants
GROUP BY foundation_ein
ORDER BY similar_grants_count DESC, avg_similarity DESC
LIMIT 50;
```

### 11.6 Hybrid Approach: Embeddings + Keywords

Use BOTH approaches for different purposes:

| Task | Approach | Rationale |
|------|----------|-----------|
| Find similar recipients | **Embeddings** | Captures semantic similarity without keyword limits |
| Find similar grant purposes | **Embeddings** | "facility acquisition" ≈ "capital campaign" ≈ "building fund" |
| Extract project_type | **Keywords** | Well-defined categories: general_support, capital, program |
| Hard filters | **Keywords** | "scholarship" vs "operating grant" is binary |
| Clustering/exploration | **Embeddings** | Discover natural groupings in data |

**Project type still uses keywords:**
```python
PROJECT_TYPE_KEYWORDS = {
    'general_support': ['general support', 'general operating', 'unrestricted', 'operating support'],
    'capital': ['capital', 'building', 'facility', 'construction', 'renovation', 'equipment'],
    'program': ['program support', 'project support', 'program grant'],
    'scholarship': ['scholarship', 'fellowship', 'award', 'tuition'],
    'research': ['research', 'study', 'investigation'],
    'emergency': ['emergency', 'disaster', 'relief', 'covid'],
}

def extract_project_type(purpose_text):
    purpose_lower = purpose_text.lower()
    for project_type, keywords in PROJECT_TYPE_KEYWORDS.items():
        if any(kw in purpose_lower for kw in keywords):
            return project_type
    return 'other'
```

### 11.7 Embedding Generation Script

```python
"""
generate_embeddings.py
Run once after data import, then incrementally for new records.
"""

import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

# Config
DB_CONN = "postgresql://user:pass@localhost/thegrantscout"
BATCH_SIZE = 1000
MODEL_NAME = 'all-MiniLM-L6-v2'

def main():
    # Load model
    print("Loading model...")
    model = SentenceTransformer(MODEL_NAME)
    
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    
    # Get recipients without embeddings
    cur.execute("""
        SELECT id, COALESCE(mission_text, name_raw) as text
        FROM f990_2025.dim_recipients
        WHERE mission_embedding IS NULL
          AND (mission_text IS NOT NULL OR name_raw IS NOT NULL)
    """)
    
    rows = cur.fetchall()
    print(f"Processing {len(rows)} recipients...")
    
    # Process in batches
    for i in tqdm(range(0, len(rows), BATCH_SIZE)):
        batch = rows[i:i+BATCH_SIZE]
        ids = [r[0] for r in batch]
        texts = [r[1] for r in batch]
        
        # Generate embeddings
        embeddings = model.encode(texts)
        
        # Update database
        for id_, emb in zip(ids, embeddings):
            cur.execute("""
                UPDATE f990_2025.dim_recipients 
                SET mission_embedding = %s 
                WHERE id = %s
            """, (emb.tolist(), id_))
        
        conn.commit()
    
    print("Done with recipients.")
    
    # Repeat for grants.purpose_text
    cur.execute("""
        SELECT id, purpose_text
        FROM f990_2025.fact_grants
        WHERE purpose_embedding IS NULL
          AND purpose_text IS NOT NULL
          AND LENGTH(purpose_text) > 10
    """)
    
    rows = cur.fetchall()
    print(f"Processing {len(rows)} grants...")
    
    for i in tqdm(range(0, len(rows), BATCH_SIZE)):
        batch = rows[i:i+BATCH_SIZE]
        ids = [r[0] for r in batch]
        texts = [r[1] for r in batch]
        
        embeddings = model.encode(texts)
        
        for id_, emb in zip(ids, embeddings):
            cur.execute("""
                UPDATE f990_2025.fact_grants 
                SET purpose_embedding = %s 
                WHERE id = %s
            """, (emb.tolist(), id_))
        
        conn.commit()
    
    print("Done with grants.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
```

### 11.8 Clustering Script

```python
"""
cluster_recipients.py
Run after embeddings are generated.
"""

import psycopg2
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter

DB_CONN = "postgresql://user:pass@localhost/thegrantscout"
N_CLUSTERS = 150

def main():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    
    # Load all embeddings
    cur.execute("""
        SELECT id, mission_embedding
        FROM f990_2025.dim_recipients
        WHERE mission_embedding IS NOT NULL
    """)
    
    rows = cur.fetchall()
    ids = [r[0] for r in rows]
    embeddings = np.array([r[1] for r in rows])
    
    print(f"Clustering {len(ids)} recipients into {N_CLUSTERS} clusters...")
    
    # Cluster
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    
    # Store cluster centroids
    for i, centroid in enumerate(kmeans.cluster_centers_):
        cur.execute("""
            INSERT INTO f990_2025.ref_clusters (id, centroid, member_count)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET centroid = %s, member_count = %s
        """, (i, centroid.tolist(), int((labels == i).sum()), 
              centroid.tolist(), int((labels == i).sum())))
    
    # Update recipients with cluster assignments
    for id_, label in zip(ids, labels):
        cur.execute("""
            UPDATE f990_2025.dim_recipients 
            SET cluster_id = %s 
            WHERE id = %s
        """, (int(label), id_))
    
    conn.commit()
    
    # Print cluster sizes
    print("\nCluster sizes:")
    for label, count in Counter(labels).most_common(20):
        print(f"  Cluster {label}: {count} recipients")
    
    cur.close()
    conn.close()
    print("\nDone. Now run label_clusters.py to generate labels.")

if __name__ == "__main__":
    main()
```

### 11.9 Build Sequence (Updated)

```
Phase 1: Entity Tables (Week 1)
├── [unchanged]

Phase 2: Calculated Tables (Week 2)  
├── [unchanged]

Phase 2.5: Embeddings (Week 2-3) ← NEW
├── Install pgvector extension
├── Add vector columns to tables
├── Run generate_embeddings.py for recipients (~5 min)
├── Run generate_embeddings.py for grants (~10 min)
├── Run cluster_recipients.py (~2 min)
├── Label top 50 clusters (manual or LLM, ~2 hours)
├── Create vector indexes

Phase 3: Matching Infrastructure (Week 3)
├── Update recipient similarity to use embeddings
├── Update project matching to use embeddings
├── [rest unchanged]
```

---

## Appendix A: Purpose Type Categories

For `purpose_type` extraction from `purpose_text`:

| Category | Keywords/Patterns |
|----------|------------------|
| general_support | "general support", "general operating", "unrestricted", "annual fund" |
| program | "program", "project", "initiative", "services" |
| capital | "capital", "building", "facility", "construction", "renovation", "equipment" |
| scholarship | "scholarship", "fellowship", "award", "prize" |
| research | "research", "study", "investigation" |
| emergency | "emergency", "disaster", "relief", "covid" |
| capacity | "capacity building", "training", "professional development" |
| advocacy | "advocacy", "policy", "campaign" |
| endowment | "endowment", "reserve" |

---

## Appendix B: Size Tier Definitions

| Tier | Budget Range | Typical Grant Range |
|------|--------------|---------------------|
| small | <$500K | $1K - $25K |
| medium | $500K - $5M | $10K - $100K |
| large | $5M - $50M | $25K - $500K |
| major | >$50M | $100K+ |

---

*End of Specification*
