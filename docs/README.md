# Documentation

This folder contains project-wide documentation for TheGrantScout.

## Contents

| Document | Description |
|----------|-------------|
| [data-dictionary.md](data-dictionary.md) | Database schema reference (f990_2025) |
| [database-summary.md](database-summary.md) | Database statistics and table counts |
| [database-build-plan.md](database-build-plan.md) | Historical database construction plan |
| specs/ | Project specifications (historical reference) |

## Quick Links

- **AI Assistant Context:** `../.claude/CLAUDE.md`
- **Report Generation SOP:** `../.claude/SOP_report_generation.md`
- **Model Documentation:** `../models/README.md`
- **Pipeline Documentation:** `../pipeline/README.md`

## Database Connection

```python
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='thegrantscout',
    user='postgres',
    password='<see .env>'
)
```

**Schema:** `f990_2025`

---

*Part of Cookie Cutter Data Science reorganization - 2026-01-04*
