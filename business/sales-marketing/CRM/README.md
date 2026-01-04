# TheGrantScout CRM

Personal CRM for tracking prospects, calls, and emails.

**Stack:** Supabase (PostgreSQL + API) + Cloudflare Pages (static hosting)

---

## Features

- **Call Queue** - Mobile-optimized list of prospects to call
- **Quick Logging** - Fast call/email outcome entry from phone
- **Task Management** - Unified follow-up tracking
- **CSV Import** - Bulk import with source list tracking
- **Search** - Find prospects by name, phone, or EIN
- **Dashboard** - Pipeline stats and activity overview

---

## Quick Start

### 1. Prerequisites

```bash
npm install -g supabase wrangler
pip3 install supabase pandas openpyxl
```

### 2. Setup Supabase

```bash
supabase login
supabase projects create thegrantscout-crm
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

### 3. Configure Frontend

Edit `frontend/js/config.js` with your Supabase credentials:

```javascript
const SUPABASE_URL = 'https://xxxxx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGc...';
```

### 4. Deploy

```bash
wrangler pages deploy frontend --project-name tgs-crm
```

Access at: `https://tgs-crm.pages.dev`

---

## Mobile Workflow

1. Open CRM on phone browser
2. Tap **Queue** to see prospects to call
3. Tap phone number to dial
4. After call, tap **Log Call**
5. Select outcome + interest level
6. Add notes (voice-to-text friendly)
7. Set follow-up if needed
8. **Save & Continue** → next prospect

---

## Folder Structure

```
CRM/
├── CLI.md                    # All CLI commands
├── README.md                 # This file
├── frontend/
│   ├── index.html           # Main app
│   ├── css/style.css        # Mobile-first styles
│   └── js/
│       ├── config.js        # Supabase credentials
│       ├── api.js           # API wrapper
│       ├── app.js           # Main app logic
│       └── views/*.js       # View components
├── supabase/
│   ├── config.toml          # Supabase config
│   └── migrations/          # Database schema
└── scripts/
    └── import_existing.py   # Data import tool
```

---

## Data Model

| Table | Purpose |
|-------|---------|
| `source_lists` | Track why prospects were pulled |
| `prospects` | Master contact list |
| `calls` | Call activity log |
| `emails` | Email tracking |
| `tasks` | Unified follow-ups |
| `pipeline` | Deal/stage tracking |

---

## Import Existing Data

```bash
export SUPABASE_URL='https://xxxxx.supabase.co'
export SUPABASE_KEY='service-role-key'

python3 scripts/import_existing.py \
    --file "prospects.csv" \
    --source-name "Dec 2025 Healthcare" \
    --segment nonprofit
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Focus search |
| `Esc` | Close modal |

---

## See Also

- [CLI.md](CLI.md) - Full CLI command reference
- [ARCH_2025-12-31_crm_proposal.md](ARCH_2025-12-31_crm_proposal.md) - Architecture decision

---

*Built with Claude Code - 2025-12-31*
