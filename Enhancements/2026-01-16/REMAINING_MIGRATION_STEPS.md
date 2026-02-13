# Remaining Migration Steps

**Created:** 2026-01-16
**Status:** Export in progress

---

## Connection Details

```
Host: db.pwhzckeihqyimrdtspoa.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: igalRzwY9UG9USV6
```

---

## Step 1: Check if Export Finished

```bash
ls -lh ~/supabase-migration/thegrantscout_backup.dump
ps aux | grep pg_dump
```

If pg_dump is still running, wait. When done, file should be ~2-3GB.

---

## Step 2: Import to Supabase

```bash
PGPASSWORD='igalRzwY9UG9USV6' pg_restore \
  --host=db.pwhzckeihqyimrdtspoa.supabase.co \
  --port=5432 \
  --username=postgres \
  --dbname=postgres \
  --no-owner \
  --no-acl \
  --verbose \
  ~/supabase-migration/thegrantscout_backup.dump
```

This takes 30-60 minutes. Watch for errors.

---

## Step 3: Verify Migration

```bash
PGPASSWORD='igalRzwY9UG9USV6' psql \
  -h db.pwhzckeihqyimrdtspoa.supabase.co \
  -U postgres -d postgres -c "
SELECT tablename, pg_size_pretty(pg_total_relation_size('f990_2025.' || tablename)) as size
FROM pg_tables WHERE schemaname = 'f990_2025'
ORDER BY pg_total_relation_size('f990_2025.' || tablename) DESC
LIMIT 10;"
```

Expected: ~36 tables, largest being officers (~4GB), nonprofit_returns (~2.7GB), etc.

---

## Step 4: Update Environment File

Edit `/Users/aleckleinman/Documents/TheGrantScout/4. Pipeline/.env`:

```
DB_HOST=db.pwhzckeihqyimrdtspoa.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=igalRzwY9UG9USV6
```

---

## Step 5: Test Python Connection

```bash
cd "/Users/aleckleinman/Documents/TheGrantScout/4. Pipeline"
python3 -c "
from dotenv import load_dotenv
import psycopg2
import os
load_dotenv()
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM f990_2025.dim_foundations')
print(f'Foundations: {cur.fetchone()[0]}')
conn.close()
print('SUCCESS')
"
```

---

## Step 6: Create GitHub Repo

1. Go to https://github.com/new
2. Name: `TheGrantScout`
3. Visibility: Private
4. Don't initialize with README

---

## Step 7: Push to GitHub

```bash
cd "/Users/aleckleinman/Documents/TheGrantScout"
git add .
git commit -m "Prepare for collaboration - Supabase migration"
git remote add origin git@github.com:YOUR_USERNAME/TheGrantScout.git
git branch -M main
git push -u origin main
```

---

## Step 8: Add Brother as Collaborator

1. Go to repo on GitHub
2. Settings → Collaborators → Add people
3. Enter brother's GitHub username

---

## What's Already Done

- [x] Supabase project created (Pro plan)
- [x] pgvector extension enabled
- [x] f990_2025 schema created (36 tables)
- [x] 22 unnecessary tables deleted from local DB (saved 4GB)
- [x] Reports consolidated to `5. Runs/`
- [x] `.gitignore` updated
- [x] Export complete (5.2GB at ~/supabase-migration/thegrantscout_backup.dump)
- [ ] **NEXT: Import to Supabase** (use resume script below)
- [ ] Verify migration
- [ ] Update .env
- [ ] Push to GitHub

## RESUME IMPORT (run this first)

```bash
~/supabase-migration/resume_import.sh
```

This script will:
- Run pg_restore with verbose output
- Show timestamps for each step
- Verify table counts when done

---

*If Claude Code context resets, just run the steps above in order.*
