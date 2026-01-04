# PROMPT: Build Personal CRM for Prospect & Call Tracking

**Date:** 2025-12-31
**Type:** Requirements → Design → Build
**Constraint:** Zero cost, CLI-manageable, mobile-accessible

---

## Context

TheGrantScout needs a simple CRM to track:
- Prospects (nonprofits, foundations, foundation management companies)
- Why each prospect was pulled (source list + criteria)
- Call activity and outcomes
- Pipeline status

**Current State:**
- Prospect data scattered across 18+ CSVs
- Call tracking in Excel workbook (Beta Test Group Calls.xlsx)
- No record of why prospects were included in specific lists
- ~824 unique nonprofit prospects, 101 foundation mgmt contacts, 146 foundations

**User Requirements:**
- Must work from phone (mobile browser for calling + note-taking)
- Must work from desktop (CSV imports, bulk operations)
- Zero additional cost (free hosting/tools only)
- All tools must have CLIs that Claude Code can use to build, manage, and upgrade

---

## Phase 1: Requirements Gathering

### Core Entities

**1. Prospects**
- Organization name, EIN, phone, email, website
- Contact name, title
- Segment: nonprofit / foundation / foundation_mgmt
- Status: not_contacted / called / interested / converted / not_interested
- Source list (linked)
- Notes
- Created date, last updated

**2. Source Lists**
- List name (e.g., "Dec 2025 Healthcare ICP 10")
- Date created
- Criteria description (why these prospects were pulled)
- Query or filters used
- Record count
- File origin (which CSV it came from)

**3. Calls**
- Prospect (linked)
- Date/time
- Outcome: vm_left / talked_to_someone / reached_decision_maker / sent_email_request
- Interest level: yes / no / maybe / uncertain
- Notes
- Follow-up date
- Duration (optional)

**4. Pipeline** (optional for MVP)
- Prospect (linked)
- Stage: lead / beta / negotiating / paying / churned
- Value
- Expected close date
- Notes

### Core Views Needed

| View | Purpose | Platform |
|------|---------|----------|
| **Call Queue** | Today's calls, filtered by segment | Mobile |
| **Quick Log** | Fast call outcome entry | Mobile |
| **Prospect Detail** | Full info + call history | Both |
| **Import** | CSV upload + source list creation | Desktop |
| **Search** | Find by name, EIN, phone | Both |
| **Follow-ups** | Prospects needing follow-up | Both |
| **Dashboard** | Counts by status, calls this week | Desktop |

### User Workflows

**Calling from phone:**
1. Open Call Queue view (filtered to segment, e.g., "Foundation Mgmt")
2. See prospect name, phone, last note
3. Tap to call (or copy number)
4. After call → tap "Log Call"
5. Quick select: outcome + interest level
6. Add notes (voice-to-text friendly)
7. Set follow-up date if needed
8. Save → next prospect

**Importing new prospects (desktop):**
1. Upload CSV
2. Map columns to fields
3. Name the source list + describe criteria
4. Preview import
5. Confirm → prospects created with source linked

**Reviewing pipeline (desktop):**
1. See all prospects by status
2. Filter by segment, source list, date range
3. Bulk update status if needed
4. Export for reporting

---

## Phase 2: Architecture Proposal

**STOP after proposing architecture. Wait for user approval before building.**

### Evaluate These Stack Options

**Option A: Local + Tunnel (Simplest)**
```
Database: SQLite (local file)
Backend: FastAPI (Python)
Frontend: Static HTML/JS (Jinja templates or vanilla JS)
Access: Cloudflare Tunnel (cloudflared CLI)
```

| Component | CLI | Install |
|-----------|-----|---------|
| SQLite | `sqlite3` | Built into Python |
| FastAPI | `uvicorn` | `pip install fastapi uvicorn` |
| Cloudflare Tunnel | `cloudflared` | brew install cloudflared |

Pros: Everything local, Claude Code has full access, zero external dependencies
Cons: Must keep computer running to access from phone

**Option B: Supabase + Static Host**
```
Database: Supabase PostgreSQL (free tier)
Backend: Supabase auto-generated API (no code needed)
Frontend: Static HTML/JS
Hosting: Cloudflare Pages (wrangler CLI)
```

| Component | CLI | Install |
|-----------|-----|---------|
| Supabase | `supabase` | npm install -g supabase |
| Cloudflare Pages | `wrangler` | npm install -g wrangler |

Pros: Always accessible, no tunnel needed, scales
Cons: External dependency, 500MB DB limit

**Option C: Hybrid**
```
Database: SQLite (local, synced to cloud backup)
Backend: FastAPI
Frontend: Static HTML/JS
Hosting: Fly.io free tier (flyctl CLI)
```

Pros: Portable, always-on
Cons: Slightly more complex deployment

### Recommendation Criteria

Answer these to help decide:
1. Is your computer always on when you're making calls?
2. Do you need access when away from home network?
3. Preference for Python (FastAPI) vs JavaScript?
4. Comfort level with external services vs. local-only?

### Proposed Schema (SQLite)

```sql
-- Source lists (why prospects were pulled)
CREATE TABLE source_lists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    criteria TEXT,
    file_origin TEXT,
    record_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Prospects (master list)
CREATE TABLE prospects (
    id INTEGER PRIMARY KEY,
    org_name TEXT NOT NULL,
    ein TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    contact_name TEXT,
    contact_title TEXT,
    segment TEXT CHECK(segment IN ('nonprofit', 'foundation', 'foundation_mgmt')),
    status TEXT DEFAULT 'not_contacted' CHECK(status IN ('not_contacted', 'contacted', 'interested', 'not_interested', 'converted')),
    source_list_id INTEGER REFERENCES source_lists(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Denormalized for quick filtering
    city TEXT,
    state TEXT,
    ntee_code TEXT,
    annual_budget INTEGER,
    icp_score INTEGER
);

-- Call log
CREATE TABLE calls (
    id INTEGER PRIMARY KEY,
    prospect_id INTEGER REFERENCES prospects(id),
    call_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    outcome TEXT CHECK(outcome IN ('vm_left', 'talked_to_someone', 'reached_decision_maker', 'sent_email_request', 'no_answer', 'wrong_number')),
    interest TEXT CHECK(interest IN ('yes', 'no', 'maybe', 'uncertain')),
    notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pipeline stages (optional MVP)
CREATE TABLE pipeline (
    id INTEGER PRIMARY KEY,
    prospect_id INTEGER UNIQUE REFERENCES prospects(id),
    stage TEXT CHECK(stage IN ('lead', 'beta', 'negotiating', 'paying', 'churned')),
    value INTEGER,
    expected_close DATE,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_prospects_status ON prospects(status);
CREATE INDEX idx_prospects_segment ON prospects(segment);
CREATE INDEX idx_prospects_source ON prospects(source_list_id);
CREATE INDEX idx_calls_prospect ON calls(prospect_id);
CREATE INDEX idx_calls_followup ON calls(follow_up_date);
```

---

## Phase 3: Build MVP (After Approval)

### MVP Scope (v0.1)

**Include:**
- [ ] Database schema + seed script
- [ ] Prospect list view (filterable by segment, status)
- [ ] Prospect detail view (with call history)
- [ ] Call logging form (mobile-optimized)
- [ ] CSV import with source list creation
- [ ] Search by name/phone/EIN
- [ ] Follow-up view (calls with follow_up_date <= today)

**Defer to v0.2:**
- Pipeline/deal tracking
- Dashboard with charts
- Bulk status updates
- Export functionality
- User auth (single user for now)

### File Structure

```
crm/
├── README.md                 # Setup + CLI commands
├── requirements.txt          # Python dependencies
├── database/
│   ├── schema.sql           # Table definitions
│   ├── seed.sql             # Sample data (optional)
│   └── crm.db               # SQLite database file
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   ├── routes/
│   │   ├── prospects.py     # CRUD for prospects
│   │   ├── calls.py         # Call logging
│   │   ├── source_lists.py  # Source list management
│   │   └── import_csv.py    # CSV import logic
│   └── database.py          # DB connection
├── frontend/
│   ├── index.html           # Main app shell
│   ├── css/
│   │   └── style.css        # Mobile-first styles
│   └── js/
│       ├── app.js           # Main app logic
│       ├── api.js           # API calls
│       └── views/
│           ├── queue.js     # Call queue view
│           ├── prospect.js  # Prospect detail
│           ├── log-call.js  # Call logging form
│           └── import.js    # CSV import
├── scripts/
│   ├── import_existing.py   # Import from current CSVs/Excel
│   ├── backup.sh            # Database backup
│   └── tunnel.sh            # Start cloudflared tunnel
└── CLI.md                   # All CLI commands for management
```

### CLI Commands Documentation (CLI.md)

```markdown
# CRM CLI Commands

## Setup
pip install -r requirements.txt
sqlite3 database/crm.db < database/schema.sql

## Run locally
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

## Access from phone (tunnel)
cloudflared tunnel --url http://localhost:8000

## Database operations
# Backup
sqlite3 database/crm.db ".backup 'database/backup_$(date +%Y%m%d).db'"

# Query directly
sqlite3 database/crm.db "SELECT COUNT(*) FROM prospects WHERE status='not_contacted'"

# Export to CSV
sqlite3 -header -csv database/crm.db "SELECT * FROM prospects" > export.csv

## Import data
python scripts/import_existing.py --file "path/to/prospects.csv" --source-name "Dec 2025 Healthcare" --criteria "NTEE E, ICP 10"

## Upgrade database (when schema changes)
sqlite3 database/crm.db < database/migrations/001_add_field.sql
```

---

## Phase 4: Migration Plan

After MVP is working, import existing data:

### Import Order

1. **Source Lists** - Create entries for each known prospect list
2. **Foundation Mgmt Contacts** - `DATA_2025-12-18_fdn_mgmt_contacts_FINAL.csv`
3. **Nonprofit Prospects** - `DATA_2025-12-12_prospect_call_list_v2.csv`
4. **Foundation Prospects** - From Excel Foundations sheet
5. **Call History** - From Excel Nonprofits + Foundations sheets

### Data Mapping

| Current Field | CRM Field |
|---------------|-----------|
| Organization_Name / org_name / company_name | org_name |
| EIN | ein |
| Phone / phone | phone |
| Email / email | email |
| Contact Date | calls.call_date |
| VM/Message | calls.outcome = 'vm_left' |
| Talked to Someone | calls.outcome = 'talked_to_someone' |
| Yes/No/Maybe/Uncertain | calls.interest |
| Notes | calls.notes |

---

## Deliverables Checklist

### Phase 1
- [ ] Confirm requirements are complete
- [ ] User approves entity model

### Phase 2
- [ ] Architecture proposal document
- [ ] Stack recommendation with rationale
- [ ] **STOP - Wait for user approval**

### Phase 3 (after approval)
- [ ] Working MVP deployed locally
- [ ] Accessible from phone via tunnel
- [ ] CSV import functional
- [ ] Call logging functional
- [ ] CLI.md with all management commands

### Phase 4
- [ ] Existing data migrated
- [ ] Source lists documented
- [ ] Old Excel/CSVs archived

---

## Important Constraints

1. **Zero cost** - No paid services, hosting, or tools
2. **CLI-manageable** - Every tool must have a CLI that Claude Code can invoke
3. **Mobile-first** - Call queue and logging must work well on phone browser
4. **Simple** - Prefer fewer dependencies, vanilla JS over frameworks
5. **Claude Code maintainable** - Clear file structure, documented commands, no GUI-only config

---

## Questions to Answer Before Building

1. Is your Mac typically running when you make calls? (determines tunnel vs. hosted)
2. Preferred location for the CRM folder? (e.g., `/Users/aleckleinman/Documents/TheGrantScout/crm/`)
3. Any additional fields needed beyond what's listed?
4. Do you want to track email outreach in this system too, or keep that separate?

---

*Prepared for Claude Code CLI execution*
