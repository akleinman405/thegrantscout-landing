# Setup Guide for Braden

Quick setup to get TheGrantScout running on your machine.

---

## 1. Clone the Repository

```bash
cd ~/Documents
git clone https://github.com/akleinman405/TheGrantScout.git
cd TheGrantScout
```

---

## 2. Install Prerequisites

### PostgreSQL Client (for psql commands)
```bash
brew install libpq
echo 'export PATH="/opt/homebrew/opt/libpq/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Python Packages
```bash
pip3 install psycopg2-binary pandas python-dotenv openpyxl anthropic python-docx
```

### Claude Code CLI
```bash
npm install -g @anthropic-ai/claude-code
claude auth
```

---

## 3. Set Up Database Credentials

```bash
cd "4. Pipeline"
cp .env.example .env
```

Then edit `.env` and replace `<get-password-from-aleck>` with the actual password:
```
igalRzwY9UG9USV6
```

---

## 4. Test Connection

```bash
cd "/Users/$USER/Documents/TheGrantScout/4. Pipeline"
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
print(f'Foundations in DB: {cur.fetchone()[0]}')
conn.close()
print('SUCCESS - Database connected!')
"
```

---

## 5. Daily Workflow

```bash
# Start of session
cd ~/Documents/TheGrantScout
git pull

# Work with Claude Code
claude

# End of session
git add .
git commit -m "Description of changes"
git push
```

---

## Key Folders

| Folder | What's in it |
|--------|--------------|
| `4. Pipeline/` | Scripts, config, client questionnaires |
| `5. Runs/` | Client report outputs |
| `.claude/` | Claude Code config (CLAUDE.md, SOP, rules) |

---

## Connection Details (for reference)

```
Host: db.pwhzckeihqyimrdtspoa.supabase.co
Port: 5432
Database: postgres
Schema: f990_2025
User: postgres
Password: <ask Aleck>
```

---

*Questions? Ask Aleck or check `.claude/CLAUDE.md` for full project context.*
