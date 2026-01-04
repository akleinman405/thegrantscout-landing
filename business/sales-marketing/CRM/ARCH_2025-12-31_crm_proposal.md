# Architecture Proposal: TheGrantScout Personal CRM

**Date:** 2025-12-31
**Status:** AWAITING APPROVAL
**Prepared for:** Aleck Kleinman

---

## Recommendation: Option B - Supabase + Cloudflare Pages

Based on your requirements:
- ❌ Mac not always on → Rules out local tunnel (Option A)
- ✅ Zero cost → Both Supabase and Cloudflare have generous free tiers
- ✅ CLI-manageable → `supabase` and `wrangler` CLIs
- ✅ Mobile-accessible → Always-on cloud hosting

---

## Stack Overview

| Layer | Technology | CLI | Free Tier |
|-------|------------|-----|-----------|
| Database | Supabase PostgreSQL | `supabase` | 500MB, 50K MAU |
| API | Supabase PostgREST (auto-generated) | Built-in | Unlimited requests |
| Frontend | Static HTML/CSS/JS | N/A | N/A |
| Hosting | Cloudflare Pages | `wrangler` | Unlimited sites, 500 builds/mo |
| Auth | Simple API key (personal use) | N/A | N/A |

### Why This Stack?

1. **No backend code needed** - Supabase auto-generates REST API from your schema
2. **PostgreSQL** - Familiar SQL, same as your main database
3. **Always accessible** - Cloud-hosted, works from anywhere
4. **Claude Code friendly** - All operations via CLI commands
5. **500MB is plenty** - Your ~1,100 prospects + calls won't exceed 10MB

---

## Revised Entity Model (with Emails)

```
┌─────────────────┐
│  source_lists   │
├─────────────────┤
│ id              │
│ name            │
│ criteria        │──────────────────────┐
│ file_origin     │                      │
│ record_count    │                      │
│ created_at      │                      │
└─────────────────┘                      │
                                         │
┌─────────────────┐    ┌─────────────────┴───────────────────┐
│    pipeline     │    │             prospects               │
├─────────────────┤    ├─────────────────────────────────────┤
│ id              │    │ id                                  │
│ prospect_id     │◄───│ org_name                            │
│ stage           │    │ ein, phone, email, website          │
│ value           │    │ contact_name, contact_title         │
│ expected_close  │    │ segment (nonprofit/fdn/fdn_mgmt)    │
│ notes           │    │ status                              │
└─────────────────┘    │ source_list_id ─────────────────────┘
                       │ city, state, ntee_code, icp_score   │
                       │ created_at, updated_at              │
                       └──────────────┬──────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     calls       │    │     emails      │    │    tasks        │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id              │    │ id              │    │ id              │
│ prospect_id     │    │ prospect_id     │    │ prospect_id     │
│ call_date       │    │ sent_date       │    │ due_date        │
│ outcome         │    │ direction       │    │ type            │
│ interest        │    │ subject         │    │ description     │
│ notes           │    │ body_preview    │    │ completed       │
│ follow_up_date  │    │ response_date   │    │ created_at      │
└─────────────────┘    │ notes           │    └─────────────────┘
                       └─────────────────┘
```

### New: Emails Entity

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL | Primary key |
| prospect_id | INTEGER | FK to prospects |
| sent_date | TIMESTAMP | When email was sent |
| direction | TEXT | 'outbound' or 'inbound' |
| subject | TEXT | Email subject line |
| body_preview | TEXT | First 500 chars of email |
| response_date | TIMESTAMP | When they replied (if applicable) |
| notes | TEXT | Additional context |
| created_at | TIMESTAMP | Record creation time |

### New: Tasks Entity (Bonus)

Useful for tracking follow-ups across calls AND emails:

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL | Primary key |
| prospect_id | INTEGER | FK to prospects |
| due_date | DATE | When to follow up |
| type | TEXT | 'call', 'email', 'other' |
| description | TEXT | What to do |
| completed | BOOLEAN | Done? |
| created_at | TIMESTAMP | Record creation time |

---

## Updated Schema (PostgreSQL)

```sql
-- Source lists
CREATE TABLE source_lists (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    criteria TEXT,
    file_origin TEXT,
    record_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- Prospects
CREATE TABLE prospects (
    id SERIAL PRIMARY KEY,
    org_name TEXT NOT NULL,
    ein VARCHAR(20),
    phone TEXT,
    email TEXT,
    website TEXT,
    contact_name TEXT,
    contact_title TEXT,
    segment TEXT CHECK(segment IN ('nonprofit', 'foundation', 'foundation_mgmt')),
    status TEXT DEFAULT 'not_contacted'
        CHECK(status IN ('not_contacted', 'contacted', 'interested', 'not_interested', 'converted')),
    source_list_id INTEGER REFERENCES source_lists(id),
    city TEXT,
    state VARCHAR(2),
    ntee_code VARCHAR(10),
    annual_budget BIGINT,
    icp_score INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Calls
CREATE TABLE calls (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    call_date TIMESTAMPTZ DEFAULT NOW(),
    outcome TEXT CHECK(outcome IN (
        'vm_left', 'talked_to_someone', 'reached_decision_maker',
        'sent_email_request', 'no_answer', 'wrong_number', 'disconnected'
    )),
    interest TEXT CHECK(interest IN ('yes', 'no', 'maybe', 'uncertain')),
    notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Emails (NEW)
CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    sent_date TIMESTAMPTZ DEFAULT NOW(),
    direction TEXT DEFAULT 'outbound' CHECK(direction IN ('outbound', 'inbound')),
    subject TEXT,
    body_preview TEXT,
    response_date TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks (NEW - unified follow-ups)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    due_date DATE NOT NULL,
    type TEXT DEFAULT 'call' CHECK(type IN ('call', 'email', 'meeting', 'other')),
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pipeline (optional)
CREATE TABLE pipeline (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER UNIQUE NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    stage TEXT CHECK(stage IN ('lead', 'beta', 'negotiating', 'paying', 'churned')),
    value INTEGER,
    expected_close DATE,
    notes TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_prospects_status ON prospects(status);
CREATE INDEX idx_prospects_segment ON prospects(segment);
CREATE INDEX idx_prospects_source ON prospects(source_list_id);
CREATE INDEX idx_calls_prospect ON calls(prospect_id);
CREATE INDEX idx_calls_followup ON calls(follow_up_date) WHERE follow_up_date IS NOT NULL;
CREATE INDEX idx_emails_prospect ON emails(prospect_id);
CREATE INDEX idx_tasks_due ON tasks(due_date) WHERE completed = FALSE;
CREATE INDEX idx_tasks_prospect ON tasks(prospect_id);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prospects_updated_at
    BEFORE UPDATE ON prospects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

---

## Security Approach

Since this is a **personal, single-user CRM**, we'll use a simple approach:

1. **Supabase anon key** for frontend API calls
2. **Row Level Security (RLS)** - Permissive policies (allow all operations)
3. **Cloudflare Access** (optional) - Add password protection to the Pages site

This avoids login complexity while keeping the data private.

---

## File Structure

```
/4. Sales & Marketing/7. CRM/crm/
├── README.md                    # Setup + usage guide
├── supabase/
│   ├── config.toml              # Supabase project config
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   └── seed.sql                 # Optional sample data
├── frontend/
│   ├── index.html               # Main app shell (SPA)
│   ├── css/
│   │   └── style.css            # Mobile-first styles
│   └── js/
│       ├── config.js            # Supabase URL + anon key
│       ├── api.js               # Supabase client wrapper
│       ├── app.js               # Main app logic + routing
│       └── views/
│           ├── queue.js         # Call queue view
│           ├── prospect.js      # Prospect detail + history
│           ├── log-call.js      # Call logging form
│           ├── log-email.js     # Email logging form
│           ├── tasks.js         # Tasks/follow-up view
│           ├── import.js        # CSV import
│           └── search.js        # Search view
├── scripts/
│   ├── import_existing.py       # Migrate from current CSVs
│   ├── backup.sh                # Export database backup
│   └── deploy.sh                # Deploy frontend to Cloudflare
└── CLI.md                       # All CLI commands
```

---

## CLI Commands (Preview)

```bash
# === SETUP (one-time) ===

# Install CLIs
npm install -g supabase wrangler

# Login to services
supabase login
wrangler login

# Create Supabase project
supabase projects create thegrantscout-crm --org-id <your-org-id>
supabase link --project-ref <project-ref>

# Apply schema
supabase db push

# === DEVELOPMENT ===

# Start local Supabase (optional, for testing)
supabase start

# Deploy schema changes
supabase db push

# Deploy frontend
wrangler pages deploy frontend --project-name tgs-crm

# === DATABASE OPERATIONS ===

# Backup database
supabase db dump > backup_2025-12-31.sql

# Run SQL query
supabase db execute "SELECT COUNT(*) FROM prospects"

# === IMPORT DATA ===
python scripts/import_existing.py --file "prospects.csv" --source-name "Dec 2025 Healthcare"
```

---

## Mobile Views (Wireframes)

### Call Queue (Mobile)

```
┌─────────────────────────────────┐
│ ☰  Call Queue          [Filter] │
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │ Senior Network Services     │ │
│ │ 📞 (310) 555-1234          │ │
│ │ Last: VM left 12/28        │ │
│ │ [Call] [Log] [Skip]        │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ Oak Foundation Mgmt         │ │
│ │ 📞 (415) 555-5678          │ │
│ │ Last: Never contacted      │ │
│ │ [Call] [Log] [Skip]        │ │
│ └─────────────────────────────┘ │
│ ...                             │
└─────────────────────────────────┘
```

### Quick Log (Mobile)

```
┌─────────────────────────────────┐
│ ← Log Call                      │
├─────────────────────────────────┤
│ Oak Foundation Mgmt             │
│ (415) 555-5678                  │
├─────────────────────────────────┤
│ Outcome:                        │
│ [VM Left] [Talked] [DM] [Email] │
│ [No Answer] [Wrong #]           │
├─────────────────────────────────┤
│ Interest:                       │
│ [Yes] [Maybe] [No] [Uncertain]  │
├─────────────────────────────────┤
│ Notes:                          │
│ ┌─────────────────────────────┐ │
│ │ Spoke with Susan, she'll    │ │
│ │ discuss with board...       │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ Follow-up: [📅 Jan 7, 2025]     │
├─────────────────────────────────┤
│         [Save & Next]           │
└─────────────────────────────────┘
```

---

## Comparison: Why Not Other Options?

| Option | Why Not |
|--------|---------|
| **A: Local + Tunnel** | Mac not always on - can't access from phone when Mac is asleep |
| **C: Fly.io Hybrid** | Requires writing/maintaining FastAPI backend - more code to break |
| **Airtable** | No CLI, can't be managed by Claude Code |
| **Notion** | No CLI for database operations |
| **Google Sheets** | Poor for relational data, no real API without OAuth complexity |

---

## Next Steps (After Approval)

1. Create Supabase project via CLI
2. Apply database schema
3. Build mobile-first frontend
4. Set up Cloudflare Pages deployment
5. Create import script for existing data
6. Migrate ~1,100 prospects + call history

---

## Questions Before Proceeding

1. **Confirm stack:** Supabase + Cloudflare Pages OK?
2. **Tasks entity:** Include the unified tasks table, or just use follow_up_date in calls?
3. **Any additional fields** needed in any entity?
4. **Cloudflare Access:** Want password protection on the site, or leave open?

---

**STOP HERE - Awaiting your approval before building.**

---

*Generated by Claude Code on 2025-12-31*
