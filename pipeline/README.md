# Report Generation Pipeline

This folder contains the grant opportunity report generation pipeline.

## Quick Start

```bash
# 1. Load client profile
python3 scripts/01_load_client.py --client "PSMF"

# 2. Score foundations using V6.1 model
python3 scripts/02_score_foundations_v6.1.py --client "PSMF" --top-k 100

# 3. Check enrichment cache
python3 scripts/03_check_enrichment.py --client "PSMF"

# 4. Filter viable foundations
python3 scripts/04_filter_viable.py --client "PSMF"

# 5. Assemble opportunities
python3 scripts/05_assemble_opportunities.py --client "PSMF"

# 6. Generate narratives
python3 scripts/06_generate_narratives.py --client "PSMF"

# 7. Build report data
python3 scripts/07_build_report_data.py --client "PSMF"

# 8. Render markdown report
python3 scripts/08_render_report.py --client "PSMF"

# 9. Convert to Word
python3 scripts/09_convert_to_docx.py --client "PSMF"
```

## Pipeline Scripts

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| 01_load_client.py | Load client profile | Questionnaire | 01_client.json |
| 02_score_foundations_v6.1.py | Match foundations | Client profile | 02_scored_foundations.csv |
| 03_check_enrichment.py | Check cache | Scored foundations | 03_enrichment_status.json |
| 03b_store_enrichment.py | Store research | Enrichment data | DB: foundation_enrichment |
| 04_filter_viable.py | Apply viability | Enrichment | 04_viable_foundations.json |
| 05_assemble_opportunities.py | Build opportunities | Viable foundations | 05_opportunities.json |
| 06_generate_narratives.py | Create positioning | Opportunities | 06_narratives.json |
| 07_build_report_data.py | Structure report | Narratives | 07_report_data.json |
| 08_render_report.py | Generate markdown | Report data | 08_report.md |
| 09_convert_to_docx.py | Export to Word | Markdown | 08_report.docx |

## Configuration

| File | Purpose |
|------|---------|
| config/coefficients.json | V6.1 model coefficients |
| config/scaling.json | Feature scaling parameters |
| config/clients.json | Client definitions |
| config/grant_type_preferences.json | Grant type filtering |
| config/imputation.json | Missing value defaults |

## Output Location

Reports are generated in `../runs/{client}/{date}/`

## Requirements

```bash
pip3 install psycopg2 pandas sentence-transformers anthropic python-docx
```

## Environment

Copy `.env.example` to `.env` and set:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=thegrantscout
DB_USER=postgres
DB_PASSWORD=<your_password>
```

## See Also

- **Full SOP:** `../.claude/SOP_report_generation.md`
- **Model Documentation:** `../models/README.md`
- **Data Dictionary:** `../docs/data-dictionary.md`

---

*Part of Cookie Cutter Data Science reorganization - 2026-01-04*
