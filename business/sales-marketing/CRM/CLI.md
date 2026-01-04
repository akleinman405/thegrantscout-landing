# CRM CLI Commands

All commands for setting up, running, and managing the TGS CRM.

---

## Prerequisites

```bash
# Node.js (for Supabase and Wrangler CLIs)
brew install node

# Python packages (for import scripts)
pip3 install supabase pandas openpyxl
```

---

## Initial Setup (One-Time)

### 1. Install CLIs

```bash
# Supabase CLI
npm install -g supabase

# Cloudflare Wrangler CLI
npm install -g wrangler
```

### 2. Login to Services

```bash
# Login to Supabase (opens browser)
supabase login

# Login to Cloudflare (opens browser)
wrangler login
```

### 3. Create Supabase Project

```bash
# Create new project (interactive)
supabase projects create thegrantscout-crm

# Link to project (get project-ref from Supabase dashboard)
cd "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/CRM"
supabase link --project-ref YOUR_PROJECT_REF
```

### 4. Apply Database Schema

```bash
# Push schema to Supabase
supabase db push

# Or run migration manually
supabase db execute --file supabase/migrations/001_initial_schema.sql
```

### 5. Get Credentials

```bash
# Show project URL and keys
supabase status
```

Copy the **API URL** and **anon key** to `frontend/js/config.js`:

```javascript
const SUPABASE_URL = 'https://xxxxx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGc...';
```

### 6. Deploy Frontend

```bash
# Create Cloudflare Pages project
wrangler pages project create tgs-crm

# Deploy
wrangler pages deploy frontend --project-name tgs-crm
```

Your CRM will be available at: `https://tgs-crm.pages.dev`

---

## Daily Operations

### Start Local Development

```bash
# Start local Supabase (optional, for offline development)
supabase start

# Serve frontend locally
python3 -m http.server 8000 --directory frontend
# Then open http://localhost:8000
```

### Deploy Changes

```bash
# Deploy frontend changes
wrangler pages deploy frontend --project-name tgs-crm

# Push database schema changes
supabase db push
```

---

## Database Operations

### Query Database

```bash
# Run SQL query
supabase db execute "SELECT COUNT(*) FROM prospects"

# Check prospect counts by status
supabase db execute "SELECT status, COUNT(*) FROM prospects GROUP BY status"

# Check today's calls
supabase db execute "SELECT COUNT(*) FROM calls WHERE call_date::date = CURRENT_DATE"
```

### Backup Database

```bash
# Export full database dump
supabase db dump > backup_$(date +%Y-%m-%d).sql

# Export specific table to CSV
supabase db execute "COPY prospects TO STDOUT WITH CSV HEADER" > prospects_backup.csv
```

### Reset Database (DANGER!)

```bash
# Reset to clean state (DELETES ALL DATA)
supabase db reset
```

---

## Import Data

### Import Prospects from CSV

```bash
# Set credentials
export SUPABASE_URL='https://xxxxx.supabase.co'
export SUPABASE_KEY='your-service-role-key'  # Use service role key, not anon

# Import prospects
python3 scripts/import_existing.py \
    --file "/path/to/prospects.csv" \
    --source-name "Dec 2025 Healthcare ICP 10" \
    --segment nonprofit \
    --criteria "NTEE E, ICP score >= 10"
```

### Import Foundation Management Contacts

```bash
python3 scripts/import_existing.py \
    --file "/path/to/fdn_mgmt_contacts.csv" \
    --source-name "Foundation Management Contacts" \
    --segment foundation_mgmt
```

### Import Call History

```bash
python3 scripts/import_existing.py \
    --file "/path/to/Beta Test Group Calls.xlsx" \
    --type calls \
    --sheet "Nonprofits"
```

### List Source Lists

```bash
python3 scripts/import_existing.py --list-sources
```

---

## Troubleshooting

### Check Supabase Connection

```bash
# Check project status
supabase status

# Check if linked to correct project
supabase projects list
```

### View Logs

```bash
# Database logs
supabase db logs

# Function logs (if using edge functions)
supabase functions logs
```

### Common Errors

| Error | Solution |
|-------|----------|
| "Invalid API key" | Check SUPABASE_ANON_KEY in config.js |
| "relation does not exist" | Run `supabase db push` to apply schema |
| "permission denied" | Check RLS policies are enabled |
| "wrangler: command not found" | Run `npm install -g wrangler` |

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy frontend | `wrangler pages deploy frontend --project-name tgs-crm` |
| Push schema | `supabase db push` |
| Backup DB | `supabase db dump > backup.sql` |
| Query DB | `supabase db execute "SELECT ..."` |
| View status | `supabase status` |
| Import CSV | `python3 scripts/import_existing.py --file data.csv --source-name "Name"` |

---

## File Locations

| File | Purpose |
|------|---------|
| `frontend/js/config.js` | Supabase credentials |
| `supabase/migrations/*.sql` | Database schema |
| `scripts/import_existing.py` | Data import script |

---

## Environment Variables

For scripts and CLI operations:

```bash
export SUPABASE_URL='https://xxxxx.supabase.co'
export SUPABASE_KEY='your-service-role-key'
```

Add to `~/.zshrc` or `~/.bashrc` to persist.

---

*Last updated: 2025-12-31*
