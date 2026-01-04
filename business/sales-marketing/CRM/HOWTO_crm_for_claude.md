# CRM HOWTO for Claude Code CLI

**Purpose:** Reference guide for future Claude Code sessions to work with TheGrantScout CRM.

---

## Architecture Overview

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Supabase Cloud    │◄────│   CRM Frontend      │     │   Local PostgreSQL  │
│   (CRM Database)    │     │   (Cloudflare)      │     │   (thegrantscout)   │
│                     │     │                     │     │                     │
│   - prospects       │     │   tgs-crm.pages.dev │     │   - f990_2025.*     │
│   - calls           │     │                     │     │   - prospects       │
│   - emails          │     │                     │     │   - pf_returns      │
│   - tasks           │     │                     │     │   - fact_grants     │
│   - campaign_emails │     │                     │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

**Two separate databases:**
1. **Supabase** - CRM data (prospects, calls, tasks) - cloud hosted
2. **Local PostgreSQL** - Source data (IRS filings, grants, 74K nonprofit prospects) - localhost:5432

---

## Supabase Connection

### Credentials
```
URL: https://qisbqmwtfzeiffgtlzpk.supabase.co
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo
Dashboard: https://supabase.com/dashboard/project/qisbqmwtfzeiffgtlzpk
```

### Python Access
```python
import os
import urllib.request
import json

SUPABASE_URL = "https://qisbqmwtfzeiffgtlzpk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo"

def supabase_get(endpoint):
    """GET from Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    req = urllib.request.Request(url, headers={"apikey": SUPABASE_KEY})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def supabase_post(endpoint, data):
    """POST to Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    req = urllib.request.Request(url, headers=headers, method='POST')
    req.data = json.dumps(data).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Examples:
# prospects = supabase_get("prospects?segment=eq.foundation_mgmt&select=*")
# calls = supabase_get("calls?select=*,prospects(org_name)")
```

---

## CRM Schema (Supabase)

### Core Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `prospects` | Master contact list | id, org_name, ein, phone, email, segment, tier, icp_score, status |
| `calls` | Call activity log | prospect_id, outcome, interest, notes, follow_up_date |
| `emails` | Manual email log | prospect_id, direction, subject, body_preview |
| `tasks` | Follow-up tasks | prospect_id, due_date, type, completed |
| `campaign_emails` | Email campaign syncs | email_address, prospect_id, vertical, status, sent_at |
| `source_lists` | Import batch tracking | name, segment, record_count, criteria |

### Segments
- `nonprofit` - 501(c)(3) organizations
- `foundation` - Private foundations (open to applications)
- `foundation_mgmt` - Foundation management companies (B2B targets)

### Statuses
- `not_contacted` - Fresh lead
- `contacted` - At least one call/email attempt
- `interested` - Expressed interest
- `not_interested` - Declined
- `converted` - Became customer

### Key Views
```sql
v_call_queue        -- Prospects to call, ordered by tier/icp_score
v_dashboard_stats   -- Pipeline metrics
v_campaign_stats    -- Email campaign metrics
v_prospect_summary  -- Prospects with last call info
```

---

## Querying the CRM

### Get all prospects by segment
```python
# Foundation management companies
fdn_mgmt = supabase_get("prospects?segment=eq.foundation_mgmt&select=*")

# Open foundations
foundations = supabase_get("prospects?segment=eq.foundation&select=*")

# Nonprofits (sorted by ICP score)
nonprofits = supabase_get("prospects?segment=eq.nonprofit&order=icp_score.desc&limit=100")
```

### Get call history for a prospect
```python
calls = supabase_get("calls?prospect_id=eq.123&select=*&order=call_date.desc")
```

### Get prospects in the call queue
```python
queue = supabase_get("v_call_queue?limit=50")
```

### Count by segment
```python
# Direct SQL via Supabase RPC isn't available, but you can:
all_prospects = supabase_get("prospects?select=segment")
from collections import Counter
counts = Counter(p['segment'] for p in all_prospects)
```

---

## Importing Prospects

### Using existing import scripts
```bash
cd "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/CRM/scripts"

# Set credentials
export SUPABASE_URL='https://qisbqmwtfzeiffgtlzpk.supabase.co'
export SUPABASE_KEY='<service-role-key>'  # Use service role for imports

# Import from CSV
python3 import_existing.py --file "prospects.csv" --source-name "Jan 2026 Import" --segment nonprofit
```

### Direct API import
```python
def import_prospect(prospect_data):
    """Import a single prospect"""
    return supabase_post("prospects", prospect_data)

# Example:
import_prospect({
    "org_name": "Acme Foundation",
    "ein": "123456789",
    "phone": "555-1234",
    "segment": "foundation",
    "tier": 2,
    "icp_score": 85,
    "status": "not_contacted"
})
```

---

## ICP Scoring Logic

### Nonprofit Scoring (from local PostgreSQL)
```
Score based on "underfunded" status:
- ≤3 unique funders + <$100K received → ICP 80, Tier 3
- ≤3 funders + >$100K received → ICP 60, Tier 4
- 4-10 funders → ICP 50, Tier 4
- >10 funders → ICP 30, Tier 5 (well-funded, lower priority)
```

### Foundation Scoring
```
Score based on capacity building grant history:
- 10+ capacity grants → ICP 90, Tier 2
- 1-9 capacity grants → ICP 70, Tier 3
- No capacity grants → ICP 40, Tier 4
```

### Foundation Management
```
Always: ICP 100, Tier 1 (highest priority)
```

---

## Data Sources

### Local PostgreSQL (thegrantscout)

| Table | Records | Key Fields |
|-------|---------|------------|
| `f990_2025.prospects` | 74,144 | Nonprofit prospects with ICP scores |
| `f990_2025.pf_returns` | 143,184 | Foundation 990-PF filings |
| `f990_2025.fact_grants` | 8.3M | Historical grant records |

### CSV Files

| File | Records | Purpose |
|------|---------|---------|
| `DATA_2025-12-17_non_bank_foundation_mgmt_companies.csv` | 53 | Foundation management companies |
| `DATA_2025-12-17_foundation_management_companies.csv` | 25 | Bank + non-bank managers |
| `sent_tracker.csv` | 2,690 | Email campaign history |

---

## Common Operations

### Update prospect tier/score
```python
def update_prospect(prospect_id, updates):
    url = f"prospects?id=eq.{prospect_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{url}",
        headers=headers,
        method='PATCH'
    )
    req.data = json.dumps(updates).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# Example:
update_prospect(123, {"tier": 1, "icp_score": 95, "pitch_angle": "..."})
```

### Log a call
```python
supabase_post("calls", {
    "prospect_id": 123,
    "outcome": "vm_left",  # or: talked_to_someone, reached_decision_maker, no_answer
    "interest": "maybe",   # or: yes, no, uncertain
    "notes": "Left message about grant research service"
})
```

### Check if prospect exists by EIN
```python
existing = supabase_get(f"prospects?ein=eq.123456789&select=id,org_name")
if existing:
    print(f"Already exists: {existing[0]['org_name']}")
```

---

## Enrichment Fields

| Field | Description | Source |
|-------|-------------|--------|
| `pitch_angle` | Why this prospect would be interested | Manual research |
| `contact_name` | Key contact person | Research / IRS filings |
| `contact_title` | Contact's title | Research |
| `linkedin_url` | Contact's LinkedIn | Research |
| `description` | Org description | Auto-generated or manual |
| `timezone` | Derived from state | Auto-calculated |

---

## Key Scripts

| Script | Purpose |
|--------|---------|
| `import_existing.py` | Bulk CSV import |
| `import_foundations.py` | Import from PostgreSQL pf_returns |
| `prioritize_foundations.py` | Update foundation tiers based on capacity grants |
| `update_priority_scores.py` | Recalculate all ICP scores |
| `enrich_phones.py` | Look up phone numbers |
| `sync_campaign_emails.py` | Sync from sent_tracker.csv |

---

## Debugging

### Check CRM stats
```python
stats = supabase_get("v_dashboard_stats")
print(stats[0])
```

### Check recent calls
```python
calls = supabase_get("calls?order=created_at.desc&limit=10&select=*,prospects(org_name)")
```

### Find duplicate EINs
```python
all_p = supabase_get("prospects?select=ein")
eins = [p['ein'] for p in all_p if p['ein']]
from collections import Counter
dupes = [(ein, c) for ein, c in Counter(eins).items() if c > 1]
```

---

## Notes

1. **MCP postgres tool** connects to local `thegrantscout` database, NOT Supabase
2. **Phone numbers** for foundation mgmt companies need manual lookup (only websites in source)
3. **Nonprofit emails** are in `contact_email` field in local PostgreSQL, need import to CRM
4. **Email campaigns** tracked in `campaign_emails` table, synced from `sent_tracker.csv`

---

*Created 2026-01-02 for Claude Code CLI reference*
