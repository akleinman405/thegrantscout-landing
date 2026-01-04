# Client Report Runs

This folder contains output from pipeline runs for each client.

## Structure

```
runs/
├── {Client_Name}/
│   └── {YYYY-MM-DD}/
│       ├── 01_client.json
│       ├── 02_scored_foundations.csv
│       ├── 03_enrichment_status.json
│       ├── 04_viable_foundations.json
│       ├── 05_opportunities.json
│       ├── 06_narratives.json
│       ├── 07_report_data.json
│       ├── 08_report.md
│       └── 08_report.docx
```

## Current Clients

| Client | Code | Status |
|--------|------|--------|
| Patient Safety Movement Foundation | PSMF | Active |
| Horizons National | HN | Active |
| Friendship Circle SD | FCSD | Active |
| Senior Network Services | SNS | Beta |
| Retirement Housing Foundation | RHF | Beta |
| Ka Ulukoa | KU | Beta |
| Arborbrook Christian Academy | ACA | Beta |

## Notes

- Runs are excluded from git (see .gitignore)
- Each run is dated for version tracking
- Large CSV files can be regenerated from pipeline

---

*Part of Cookie Cutter Data Science reorganization - 2026-01-04*
