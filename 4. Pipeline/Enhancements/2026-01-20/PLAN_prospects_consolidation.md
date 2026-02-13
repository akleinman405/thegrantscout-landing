# Prospects Table Consolidation Plan

**Date:** 2026-01-20
**Status:** Draft - Awaiting Review

---

## Current State

| Table | Rows | Purpose | Columns |
|-------|------|---------|---------|
| `prospects` | 74,175 | Nonprofits as customers (B2C) | 84 |
| `b2b_prospects` | 761 | Foundations as customers (B2B) | 43 |
| `foundation_prospects` | 1 | Foundations as customers (duplicate) | 19 |
| `fundraising_events` | 273 | Charity events (intelligence) | 19 |

**Problems:**
1. Two tables for foundation prospects (b2b_prospects, foundation_prospects)
2. 84 columns in prospects table - many seem unused
3. Unclear naming (what's the difference between b2b_prospects and foundation_prospects?)
4. fundraising_events is different purpose but grouped mentally with "prospects"

---

## Proposed Consolidation

### Option A: Unified `sales_pipeline` Table

Create one table for ALL sales prospects with a `prospect_type` field:

```sql
CREATE TABLE sales_pipeline (
    id SERIAL PRIMARY KEY,
    ein VARCHAR(20),
    org_name TEXT,
    prospect_type VARCHAR(20), -- 'nonprofit' or 'foundation'

    -- Common fields
    contact_name TEXT,
    contact_title TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    website TEXT,
    state VARCHAR(2),

    -- Sales tracking (common)
    status VARCHAR(50),
    priority INTEGER,
    last_contact_date DATE,
    next_followup_date DATE,
    notes TEXT,
    call_notes TEXT,
    outcome VARCHAR(100),

    -- Org metrics (common)
    total_assets NUMERIC,

    -- Nonprofit-specific (NULL for foundations)
    icp_score INTEGER,
    total_revenue NUMERIC,
    grant_dependency_pct NUMERIC,
    mission_statement TEXT,

    -- Foundation-specific (NULL for nonprofits)
    total_grantees INTEGER,
    annual_giving BIGINT,
    gives_capacity_grants BOOLEAN,
    geographic_focus TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Pros:**
- Single source of truth for all sales
- Easier to query "all my prospects"
- Simpler to maintain

**Cons:**
- Many NULL columns depending on type
- Different workflows for B2B vs B2C might want different fields
- 84 columns in current prospects table - hard to merge cleanly

---

### Option B: Two Tables (Nonprofit + Foundation)

Keep separate tables but with clear naming and clean up duplicates:

```
sales_nonprofit_prospects  -- renamed from 'prospects', cleaned up columns
sales_foundation_prospects -- merge b2b_prospects + foundation_prospects
```

**Pros:**
- Clear separation of concerns
- No NULL columns for type-specific fields
- Easier migration (less risky)

**Cons:**
- Two places to look for "all prospects"
- Some duplicate logic for common operations

---

### Option C: Keep Current + Delete Duplicate

Minimal change:
1. Migrate `foundation_prospects` (1 row) → `b2b_prospects`
2. Delete `foundation_prospects`
3. Rename for clarity: `prospects` → `nonprofit_prospects`, `b2b_prospects` → `foundation_prospects`

**Pros:**
- Lowest risk
- Quick to implement
- No data migration complexity

**Cons:**
- Doesn't address 84-column bloat in prospects
- Still two separate tables

---

### What About `fundraising_events`?

This table is **fundamentally different** - it's intelligence/research data, not CRM/sales data.

Options:
1. **Keep separate** as `events_calendar` or similar
2. **Delete** if not being used
3. **Move to different schema** (e.g., `research.fundraising_events`)

---

## Questions for Reviewers

1. Do we actually use all 84 columns in the prospects table, or can we trim it?
2. Is the B2B (foundation) sales pipeline active, or was it a one-time experiment?
3. Should fundraising_events stay or go?
4. Which option (A, B, or C) best fits how you actually work?

---

## Recommendation

**Option C (minimal change)** for now:
1. Migrate 1 row from foundation_prospects → b2b_prospects
2. Drop foundation_prospects
3. Rename tables for clarity
4. Defer column cleanup to later

This is lowest risk and addresses the immediate duplicate problem without major restructuring.

