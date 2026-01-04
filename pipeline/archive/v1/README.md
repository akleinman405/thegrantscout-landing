# TheGrantScout Report Pipeline

Automated grant opportunity report generation for nonprofits.

## Overview

This pipeline takes a nonprofit's EIN and questionnaire responses, then generates a professional Word document with:
- Top 5 matched foundations
- Funder intelligence (giving patterns, typical grants, trends)
- AI-generated positioning strategy
- Action items with deadlines

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your database password and API key

# 3. Generate a report
python generate_report.py --client "Organization Name"

# 4. Or run in dry-run mode (no AI/scraping)
python generate_report.py --client "Organization Name" --dry-run
```

## CLI Options

| Option | Description |
|--------|-------------|
| `--client`, `-c` | Organization name from questionnaire |
| `--ein`, `-e` | Organization EIN |
| `--questionnaire`, `-q` | Path to questionnaire CSV |
| `--output`, `-o` | Output directory |
| `--week`, `-w` | Week number for report |
| `--dry-run` | Skip AI and scraping (use fallbacks) |
| `--skip-scrape` | Skip web scraping only |
| `--verbose`, `-v` | Verbose logging |

## Project Structure

```
TheGrantScout - Pipeline/
├── config/           # Configuration and database connection
├── scoring/          # Foundation scoring using LASSO model
├── enrichment/       # Funder snapshot data enrichment
├── loaders/          # Questionnaire and client data loading
├── assembly/         # Report data assembly
├── scraper/          # Foundation website scraping
├── ai/               # AI narrative generation
│   └── prompts/      # Prompt templates
├── rendering/        # Markdown report rendering
│   └── templates/    # Report templates
├── schemas/          # JSON schemas for validation
├── data/             # Input data
│   ├── questionnaires/
│   └── cache/
├── outputs/          # Generated outputs
│   ├── reports/
│   └── logs/
├── tests/            # Unit and integration tests
└── Report Templates/ # Word conversion scripts
```

## Pipeline Flow

```
Client EIN + Questionnaire
        ↓
    Scoring (LASSO model)
        ↓
    Enrichment (Funder Snapshots)
        ↓
    Assembly (Combine data)
        ↓
    Scraping (Foundation websites)
        ↓
    AI Narratives (Claude API)
        ↓
    Markdown Rendering
        ↓
    Word Document Conversion
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_NAME` | thegrantscout | Database name |
| `DB_USER` | postgres | Database user |
| `DB_PASSWORD` | (required) | Database password |
| `ANTHROPIC_API_KEY` | (required for AI) | Claude API key |
| `LOG_LEVEL` | INFO | Logging level |
| `CACHE_TTL_DAYS` | 7 | Cache expiration |

## Development

### Running Tests

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Adding New Features

1. Create module in appropriate package
2. Add unit tests in `tests/`
3. Update this README

## Troubleshooting

### Database Connection Failed
- Check `.env` has correct DB_PASSWORD
- Verify PostgreSQL is running: `brew services start postgresql`

### AI Generation Failed
- Check ANTHROPIC_API_KEY in `.env`
- Verify API key is valid

### Word Conversion Failed
- Install python-docx: `pip install python-docx`

---

*TheGrantScout - Your mission deserves funding. We'll help you find it.*
