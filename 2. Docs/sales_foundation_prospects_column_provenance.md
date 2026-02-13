# sales_foundation_prospects -- Column Provenance

| | |
|---|---|
| **Table** | `f990_2025.sales_foundation_prospects` |
| **Granularity** | One row per foundation (EIN is unique) |
| **Row count** | 761 (as of 2026-01-09) |
| **Created** | 2026-01-05 as `b2b_prospects`, renamed 2026-01-20 |
| **Purpose** | B2B sales prospect list: foundations that might purchase TheGrantScout for their grantees |

---

## How the 761 Rows Were Selected

The initial list (~748 foundations) was generated on 2026-01-05 by `rebuild_excel.py`, which queried `fact_grants` (tax_year >= 2022) for foundations meeting ALL of:

- **50+ total grantees** (distinct recipient EINs in recent grants)
- **20+ dependent grantees** (grantees where this foundation provides >= 80% of their total foundation funding AND the grantee has < $50M revenue)

An additional 13 foundations were added on 2026-01-09 via a separate query targeting foundations with capacity-building grant keywords, < 100 grantees, >= $500K assets, open to applications, and active in the past 3 years.

A handful of user-specified priority foundations were also inserted manually via `add_priority_foundations.py`.

**This is NOT all 143K foundations.** It is a curated subset.

---

## Column-by-Column Provenance

### Identity & Location

| Column | Type | Source Table |
|--------|------|-------------|
| `id` | INTEGER | Auto-generated |
| `foundation_name` | VARCHAR | `pf_returns` |
| `ein` | VARCHAR | `pf_returns` |
| `state` | VARCHAR | `pf_returns` |
| `assets` | BIGINT | `pf_returns` |
| `website` | VARCHAR | `pf_returns` |

**`id`** -- PostgreSQL serial primary key.

**`foundation_name`** -- `pf_returns.business_name` from the most recent filing (ordered by `tax_year DESC`).

**`ein`** -- Foundation EIN. Unique constraint on the table.

**`state`** -- State code from the most recent 990-PF filing.

**`assets`** -- `pf_returns.total_assets_eoy_amt` (end-of-year assets) from the most recent filing.

**`website`** -- `pf_returns.website_url` from the most recent filing. Added 2026-01-07 via ALTER TABLE. Values of 'N/A', 'NONE', '0', and empty string were excluded.

---

### Grantee Analysis

All computed from `fact_grants` where `tax_year >= 2022`.

| Column | Type | Source Table |
|--------|------|-------------|
| `total_grantees` | INTEGER | `fact_grants` |
| `dependent_grantees` | INTEGER | `fact_grants` + `nonprofit_returns` |
| `pct_dependent` | NUMERIC | Calculated |
| `top_5_grantees` | TEXT | `fact_grants` |

**`total_grantees`** -- `COUNT(DISTINCT recipient_ein)` for this foundation.

**`dependent_grantees`** -- Count of distinct recipients meeting BOTH conditions:
1. This foundation provides >= 80% of the recipient's total foundation funding (across all foundations, tax_year >= 2022)
2. Recipient's total revenue < $50M (from most recent `nonprofit_returns` filing)

This identifies grantees who are highly dependent on this one foundation and small enough to need help.

**`pct_dependent`** -- `dependent_grantees / total_grantees`. Stored as decimal (0.211 = 21.1%).

**`top_5_grantees`** -- Pipe-separated list of the 5 recipients receiving the most total funding from this foundation, by `SUM(amount) DESC`. Uses `recipient_name_raw`.

---

### Capacity Building Metrics

All computed from `fact_grants` where `tax_year >= 2022`.

| Column | Type | Source Table |
|--------|------|-------------|
| `capacity_pct` | NUMERIC | `fact_grants` |
| `cb_service_grants` | INTEGER | `fact_grants` |
| `cb_service_total` | INTEGER | `fact_grants` |
| `cb_service_examples` | TEXT | `fact_grants` |

**`capacity_pct`** -- Percentage of grants whose `purpose_text` matches GENERAL support keywords:
- `GENERAL SUPPORT`, `GENERAL OPERATING`, `OPERATING SUPPORT`
- `UNRESTRICTED`, `CAPACITY BUILDING`, `CORE SUPPORT`

Calculated as `capacity_grants / total_grants`. Stored as decimal (0.389 = 38.9%).

**`cb_service_grants`** -- Count of grants whose `purpose_text` matches SPECIFIC capacity-building service keywords:
- `STRATEGIC PLAN%`
- `FUNDRAIS%CAPACITY%`
- `ORGANIZATIONAL DEVELOPMENT`
- `TECHNICAL ASSISTANCE`
- `CAPACITY BUILDING` (excluding general support)

Additionally filtered to `amount BETWEEN 5000 AND 150000` (typical CB service grant size range).

**`cb_service_total`** -- `SUM(amount)` of the grants counted in `cb_service_grants`.

**`cb_service_examples`** -- Pipe-separated `purpose_text` from up to 3 distinct grants matching the CB service keywords. Provides human-readable examples.

> **Note:** `capacity_pct` measures GENERAL support (GOS/unrestricted), while `cb_service_grants` measures SPECIFIC capacity-building services. These are different concepts.

---

### Application Status

| Column | Type | Source Table |
|--------|------|-------------|
| `accepts_apps` | VARCHAR | `pf_returns` |

**`accepts_apps`** -- Derived from `pf_returns.only_contri_to_preselected_ind`:
- `FALSE` = "Yes"
- `TRUE` = "No - Preselected Only"

Based on the most recent 990-PF filing.

---

### Scoring

Added 2026-01-08 after discovering the original single-dimension `rating` was conflating CB fit with reachability.

| Column | Type | Source |
|--------|------|--------|
| `cb_fit_score` | INTEGER (1-3) | Computed |
| `reach_score` | INTEGER (1-3) | Computed |
| `sales_priority` | VARCHAR(2) | Computed |
| `grantee_profile_score` | INTEGER | Computed |
| `community_signals` | INTEGER | Computed |
| `institution_signals` | INTEGER | Computed |
| `predicted_poor` | BOOLEAN | Computed |
| `predicted_excellent` | BOOLEAN | Computed |

**`cb_fit_score`** -- Capacity building fit, scored 1-3.

For the 348 researched foundations, scored by Claude agents based on grantee analysis. For the 397 unresearched foundations, auto-scored using keyword matching on `top_5_grantees`.

| Score | Label | Criteria |
|-------|-------|----------|
| 3 | High | `cb_service_grants >= 10`, OR `dependent_grantees >= 50` AND `cb_service_grants > 0`, OR community nonprofit grantees |
| 2 | Medium | `cb_service_grants` 1-9, OR `dependent_grantees` 20-49, OR mixed grantees |
| 1 | Low | `cb_service_grants = 0` AND institutional grantees |

**`reach_score`** -- How easy it is to contact the foundation, scored 1-3. Only populated for researched foundations.

| Score | Label | Criteria |
|-------|-------|----------|
| 3 | Easy | Email found AND (phone OR LinkedIn) |
| 2 | Medium | Email found, OR phone AND named contact |
| 1 | Hard | No email, no phone with named contact |

**`sales_priority`** -- Matrix of `cb_fit_score` x `reach_score`:

| | Reach 3 (Easy) | Reach 2 (Medium) | Reach 1 (Hard) |
|---|---|---|---|
| **CB 3 (High)** | P1 | P2 | P3 |
| **CB 2 (Medium)** | P4 | P5 | P6 |
| **CB 1 (Low)** | P7 | P8 | P9 |

**`grantee_profile_score`** -- `community_signals - institution_signals`. Higher = more community-oriented grantee portfolio.

**`community_signals`** -- Count of community nonprofit keywords found in `top_5_grantees`:
- United Way, Food Bank, YMCA, Boys & Girls, Habitat, Meals on Wheels, Catholic Charities, Salvation Army, Goodwill, Junior Achievement, Head Start, Literacy, Rescue Mission, 4-H, Scouts, Big Brothers/Big Sisters, etc.

**`institution_signals`** -- Count of institutional keywords found in `top_5_grantees`:
- University, Stanford, MIT, Harvard, Hospital, Medical Center, Nature Conservancy, NRDC, Environmental Defense, Human Rights Watch, Urban Institute, Brookings, UNICEF, Smithsonian, etc.

**`predicted_poor`** -- Added 2026-01-07. TRUE if `top_5_grantees` contains university/large national org keywords and foundation was not yet researched.

**`predicted_excellent`** -- Added 2026-01-07. TRUE if `top_5_grantees` contains community org keywords, `predicted_poor = FALSE`, and not yet researched.

---

### Contact Info

Populated by Claude Code agents doing web research (foundation websites, LinkedIn, staff pages) during research batches 2026-01-07 through 2026-01-09. About 348 of 761 foundations were researched.

| Column | Type | How Populated |
|--------|------|---------------|
| `contact_name` | VARCHAR | Best contact for a CB services conversation (ED, Program Director, Director of Grantmaking). Found via foundation staff pages and LinkedIn. |
| `contact_title` | VARCHAR | Job title of the contact |
| `contact_email` | VARCHAR | From foundation website or inferred from email patterns |
| `contact_phone` | VARCHAR | From foundation website |
| `contact_linkedin` | VARCHAR | LinkedIn profile URL |

---

### Legacy Rating (deprecated)

| Column | Type | Notes |
|--------|------|-------|
| `rating` | VARCHAR | Excellent / Good / Fair / Poor. **Deprecated 2026-01-08** in favor of `cb_fit_score` + `reach_score`. |
| `why_rating` | TEXT | Free-text explanation. Typically mentions dependent grantee count, CB grant count, contact quality. |

---

### Research Workflow Tracking

| Column | Type | Description |
|--------|------|-------------|
| `researching` | BOOLEAN | TRUE while an agent is actively researching this foundation. Prevents duplicate work. |
| `researched` | BOOLEAN | TRUE when research is complete (contacts found, rating assigned). |
| `claimed_at` | TIMESTAMP | When an agent claimed this foundation |
| `completed_at` | TIMESTAMP | When research was finished |
| `agent_id` | VARCHAR | Identifier of the Claude agent that did the research |
| `priority` | INTEGER | Research queue order. Lower = higher priority. -1 = user-specified top priority. Default ordering by `dependent_grantees DESC`. |

---

### CRM / Sales Tracking

Manually entered by Alec during outreach calls.

| Column | Type | Description |
|--------|------|-------------|
| `status` | VARCHAR | Sales pipeline status (e.g., "Contacted", "Interested") |
| `call_notes` | TEXT | Free-text notes from phone calls and email exchanges |
| `contact_date` | DATE | Date of most recent contact |
| `outcome` | VARCHAR | Outcome classification (e.g., "3. Talked to Someone", "4. Reached Decision Maker") |
| `notes` | TEXT | General notes. Initially populated by agents with staff details. Appended manually later. |

---

### Timestamps

| Column | Type | Description |
|--------|------|-------------|
| `created_at` | TIMESTAMP | Row creation (defaults to NOW()) |
| `updated_at` | TIMESTAMP | Last update |

---

## Table History

| Date | Event |
|------|-------|
| 2026-01-05 | Table created as `b2b_prospects` with ~748 rows from `rebuild_excel.py`. Initial columns: identity, grantee analysis, capacity metrics, accepts_apps, top_5_grantees, contact fields (empty), rating (empty), workflow fields. |
| 2026-01-05 | 10 Excellent + 7 Good foundations get contacts via `insert_b2b_prospects.sql`. |
| 2026-01-07 | 135 foundations researched in 7 agent batches. Contact info, ratings, notes populated. |
| 2026-01-07 | `website` column added from `pf_returns.website_url`. |
| 2026-01-07 | `predicted_poor` and `predicted_excellent` columns added (keyword flags). |
| 2026-01-08 | Two-dimension scoring: `cb_fit_score`, `reach_score`, `sales_priority` added. 348 foundations scored. `rating` deprecated. |
| 2026-01-08 | Keyword scoring: `community_signals`, `institution_signals`, `grantee_profile_score` added for 397 unresearched foundations. |
| 2026-01-08-09 | Additional research batches. More contacts populated. |
| 2026-01-09 | 13 new foundations added (CB keyword query, < 100 grantees, open to apps). |
| 2026-01-09 | CRM columns populated as calls were made. |
| 2026-01-20 | Table renamed from `b2b_prospects` to `sales_foundation_prospects`. |

---

## Key Source Tables

| Source | What It Provides |
|--------|-----------------|
| `pf_returns` | Foundation identity, assets, website, application status |
| `fact_grants` | All grant-derived metrics (grantee counts, CB grants, capacity_pct, top_5, examples) |
| `nonprofit_returns` | Recipient revenue (for dependent_grantees $50M filter) |
| Web research | Contact info, ratings, notes (Claude agents) |
| Manual entry | CRM fields, priority overrides |

---

## Important Caveats

- The dependent grantees calculation uses an **80% threshold**: the grantee gets 80%+ of their total foundation funding from this single foundation.
- The **$50M revenue filter** on dependent grantees excludes large institutions that happen to get most of their foundation funding from one source but aren't actually "dependent."
- All grant-based calculations use **`tax_year >= 2022`** (3-year window at time of creation in Jan 2026).
- `capacity_pct` (general support) and `cb_service_grants` (specific CB services) measure **different things**.
