# TheGrantScout - Braden Onboarding

**Instructions for Claude Code CLI:** Walk Braden through setting up TheGrantScout on his machine step by step. Run commands for him where possible, and verify each step succeeds before moving on.

---

## Context

TheGrantScout is a grant matching platform that helps nonprofits find foundations likely to fund them. The system uses:
- **PostgreSQL database** hosted on Supabase (shared between Aleck and Braden)
- **Python scripts** for report generation
- **Claude Code CLI** for building client reports

Braden is joining as a collaborator. His machine needs to be set up to:
1. Connect to the shared Supabase database
2. Run the report generation pipeline
3. Push/pull code changes via GitHub

---

## Step 1: Check Prerequisites

Run these commands to check what's already installed:

```bash
# Check for Homebrew
which brew

# Check for Python 3
python3 --version

# Check for pip3
pip3 --version

# Check for git
git --version

# Check for Node.js (needed for Claude Code)
node --version
npm --version
```

**If Homebrew is missing**, install it:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**If Node.js is missing**, install it:
```bash
brew install node
```

---

## Step 2: Install PostgreSQL Client

```bash
brew install libpq
echo 'export PATH="/opt/homebrew/opt/libpq/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Verify with:
```bash
psql --version
```

---

## Step 3: Install Python Packages

```bash
pip3 install psycopg2-binary pandas python-dotenv openpyxl anthropic python-docx sentence-transformers
```

---

## Step 4: Clone the Repository

```bash
cd ~/Documents
git clone https://github.com/akleinman405/TheGrantScout.git
cd TheGrantScout
```

---

## Step 5: Set Up Database Credentials

Create the environment file:

```bash
cd "4. Pipeline"
cat > .env << 'EOF'
DB_HOST=db.pwhzckeihqyimrdtspoa.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=igalRzwY9UG9USV6
EOF
```

---

## Step 6: Test Database Connection

```bash
cd ~/Documents/TheGrantScout/"4. Pipeline"
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
print(f'Foundations in DB: {cur.fetchone()[0]:,}')
cur.execute('SELECT COUNT(*) FROM f990_2025.fact_grants')
print(f'Historical grants: {cur.fetchone()[0]:,}')
conn.close()
print('SUCCESS - Database connected!')
"
```

**Expected output:**
- Foundations in DB: ~143,000
- Historical grants: ~8,300,000
- SUCCESS message

---

## Step 7: Verify Claude Code CLI

If Claude Code isn't installed yet:
```bash
npm install -g @anthropic-ai/claude-code
```

Then authenticate:
```bash
claude auth
```

---

## Step 8: Read the Project Documentation

Once setup is complete, read these key files to understand the project:

```bash
cd ~/Documents/TheGrantScout
cat .claude/CLAUDE.md
```

Key sections to understand:
- **Project Overview** - What TheGrantScout does
- **Database Reference** - Schema and table structure
- **Report Generation Pipeline** - How reports are built
- **Mandatory Workflow** - Report naming conventions

---

## You're Ready!

### Daily Workflow

```bash
# Start of session
cd ~/Documents/TheGrantScout
git pull

# Launch Claude Code
claude

# End of session (after making changes)
git add .
git commit -m "Description of what you did"
git push
```

### Building a Client Report

To generate a report for a client, Claude Code will:
1. Load the client questionnaire from `4. Pipeline/config/`
2. Query the database for matching foundations
3. Score and rank opportunities
4. Generate a formatted report in `5. Runs/{client}/{date}/`

See `.claude/SOP_report_generation.md` for the full workflow.

---

## Key Folders

| Folder | Purpose |
|--------|---------|
| `4. Pipeline/` | Scripts, config, client questionnaires |
| `4. Pipeline/phases/` | Pipeline scripts by phase |
| `4. Pipeline/config/` | Client profiles, coefficients |
| `5. Runs/` | Output reports by client |
| `.claude/` | Claude Code configuration |
| `.claude/CLAUDE.md` | Main project context file |
| `.claude/SOP_report_generation.md` | Report generation workflow |

---

## Troubleshooting

### "Connection refused" error
- Check that the password in `.env` is correct
- Verify you have internet connection

### "Module not found" error
- Run `pip3 install <module-name>`

### Git push rejected
- Run `git pull` first to get latest changes
- Resolve any merge conflicts
- Then push again

---

## Contact

Questions? Ask Aleck or check the documentation in `.claude/`.

---

*Welcome to TheGrantScout team!*
