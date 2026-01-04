# PROMPT_01: Phase 0 - Infrastructure Setup

**Date:** 2025-12-27
**Phase:** 0
**Agent:** Dev Team
**Estimated Time:** 2-3 hours

---

## Objective

Set up the project structure, configuration files, and dependencies for the TheGrantScout Report Pipeline.

---

## Context

**Project Location:** `/Users/aleckleinman/Documents/TheGrantScout/5. TheGrantScout - Pipeline`

**Existing Files in Location:**
- `Report Templates/convert_to_docx.py` - MD → Word converter (keep, integrate)

**Database:** PostgreSQL with `f990_2025` schema containing foundation and grant data.

---

## Tasks

### Task 1: Create Folder Structure

Create the following directory structure:

```
TheGrantScout - Pipeline/
├── config/
│   ├── __init__.py
│   ├── database.py
│   ├── settings.py
│   ├── coefficients.json      # Created in Phase 2
│   └── scaling.json           # Created in Phase 2
├── scoring/
│   ├── __init__.py
│   ├── scoring.py             # Created in Phase 2
│   └── features.py            # Created in Phase 2
├── enrichment/
│   ├── __init__.py
│   ├── funder_snapshot.py     # Created in Phase 3
│   ├── cache.py               # Created in Phase 3
│   ├── comparable_grant.py    # Created in Phase 3
│   └── connections.py         # Created in Phase 3
├── loaders/
│   ├── __init__.py
│   ├── questionnaire.py       # Created in Phase 4
│   └── client_data.py         # Created in Phase 4
├── assembly/
│   ├── __init__.py
│   └── report_data.py         # Created in Phase 4
├── scraper/
│   ├── __init__.py
│   ├── scraper.py             # Created in Phase 5
│   ├── extractors.py          # Created in Phase 5
│   └── cache.py               # Created in Phase 5
├── ai/
│   ├── __init__.py
│   ├── narratives.py          # Created in Phase 6
│   ├── fallbacks.py           # Created in Phase 6
│   └── prompts/               # Created in Phase 6
│       └── .gitkeep
├── rendering/
│   ├── __init__.py
│   ├── md_renderer.py         # Created in Phase 7
│   └── templates/
│       └── .gitkeep
├── schemas/
│   └── report_schema.json     # Created in Phase 4
├── data/
│   ├── questionnaires/        # CSV input location
│   │   └── .gitkeep
│   └── cache/                 # Cached data
│       └── .gitkeep
├── outputs/
│   ├── reports/               # Generated reports
│   │   └── .gitkeep
│   └── logs/                  # Execution logs
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── test_scoring.py        # Created in Phase 9
│   ├── test_enrichment.py     # Created in Phase 9
│   └── fixtures/
│       └── .gitkeep
├── Report Templates/          # Existing folder
│   └── convert_to_docx.py     # Existing file
├── generate_report.py         # Created in Phase 8
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Task 2: Create `config/database.py`

Database connection module with connection pooling.

**Requirements:**
- Use `psycopg2` with connection pooling
- Read credentials from environment variables
- Provide `get_connection()` context manager
- Provide `query_df()` helper that returns pandas DataFrame
- Default schema: `f990_2025`

**Environment Variables:**
- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: thegrantscout)
- `DB_USER` (default: postgres)
- `DB_PASSWORD` (required)

### Task 3: Create `config/settings.py`

Centralized settings module.

**Requirements:**
- Load from `.env` file using `python-dotenv`
- Expose paths as constants:
  - `PROJECT_ROOT`
  - `DATA_DIR`
  - `OUTPUT_DIR`
  - `CACHE_DIR`
  - `LOG_DIR`
  - `QUESTIONNAIRE_DIR`
- Expose API settings:
  - `ANTHROPIC_API_KEY`
- Expose cache settings:
  - `CACHE_TTL_DAYS` (default: 7)
- Expose logging settings:
  - `LOG_LEVEL` (default: INFO)

### Task 4: Create `requirements.txt`

```
# Database
psycopg2-binary>=2.9.0

# Data processing
pandas>=2.0.0
numpy>=1.24.0

# AI
anthropic>=0.18.0

# Scraping
requests>=2.31.0
beautifulsoup4>=4.12.0

# Document generation
python-docx>=0.8.11

# Utilities
python-dotenv>=1.0.0

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
```

### Task 5: Create `.env.example`

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=thegrantscout
DB_USER=postgres
DB_PASSWORD=your_password_here

# API Keys
ANTHROPIC_API_KEY=your_api_key_here

# Settings
LOG_LEVEL=INFO
CACHE_TTL_DAYS=7
```

### Task 6: Create `.gitignore`

```
# Environment
.env
*.pyc
__pycache__/
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp

# Outputs
outputs/reports/*
outputs/logs/*
!outputs/reports/.gitkeep
!outputs/logs/.gitkeep

# Cache
data/cache/*
!data/cache/.gitkeep

# OS
.DS_Store
Thumbs.db
```

### Task 7: Create `README.md`

Create a README with:
- Project overview
- Setup instructions (pip install, .env configuration)
- Usage examples
- Folder structure explanation
- Link to detailed documentation

### Task 8: Verify Existing `convert_to_docx.py`

1. Check that `Report Templates/convert_to_docx.py` exists
2. Document its inputs/outputs
3. Note any dependencies it requires (add to requirements.txt if missing)
4. Confirm it can be called from the pipeline

---

## Input Files

| File | Location | Purpose |
|------|----------|---------|
| convert_to_docx.py | `Report Templates/convert_to_docx.py` | Existing MD→Word converter |

---

## Output Files

| File | Description |
|------|-------------|
| `config/__init__.py` | Package init |
| `config/database.py` | DB connection module |
| `config/settings.py` | Settings module |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment template |
| `.gitignore` | Git ignore rules |
| `README.md` | Project documentation |
| All `__init__.py` files | Package markers |
| All `.gitkeep` files | Empty folder markers |

---

## Done Criteria

- [ ] All folders created as specified
- [ ] All `__init__.py` files created
- [ ] `config/database.py` exists and is syntactically valid
- [ ] `config/settings.py` exists and is syntactically valid
- [ ] `requirements.txt` exists with all dependencies
- [ ] `.env.example` exists with all required variables
- [ ] `.gitignore` exists
- [ ] `README.md` exists

---

## Verification Tests

### Test 1: Folder Structure
```bash
# Verify key directories exist
ls -la config/ scoring/ enrichment/ loaders/ assembly/ scraper/ ai/ rendering/ tests/ data/ outputs/
```

### Test 2: Python Imports (after pip install)
```bash
pip install -r requirements.txt
python -c "from config import database, settings; print('Config imports OK')"
```

### Test 3: Database Connection (requires .env)
```bash
# Create .env from .env.example first, fill in DB_PASSWORD
python -c "
from config.database import init_pool, get_connection
init_pool()
with get_connection() as conn:
    cur = conn.cursor()
    cur.execute('SELECT 1')
    print('DB connection OK')
"
```

### Test 4: Settings Load
```bash
python -c "
from config.settings import PROJECT_ROOT, DATA_DIR, OUTPUT_DIR
print(f'PROJECT_ROOT: {PROJECT_ROOT}')
print(f'DATA_DIR: {DATA_DIR}')
print(f'OUTPUT_DIR: {OUTPUT_DIR}')
"
```

---

## Notes

- Do NOT create actual `.env` file (only `.env.example`) - user will create with real credentials
- All `__init__.py` files can be empty for now
- `.gitkeep` files are empty files to preserve empty directories in git
- The `convert_to_docx.py` file already exists - do not overwrite, just verify it works

---

## Handoff

After completion:
1. Run all verification tests
2. Create completion report listing all files created
3. Note any issues or deviations from spec
4. PM reviews before proceeding to PROMPT_02

---

*Next: PROMPT_02 (Scoring Function)*
