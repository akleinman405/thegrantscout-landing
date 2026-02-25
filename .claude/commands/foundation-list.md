---
description: Generate branded foundation list PDF for LinkedIn lead gen
argument-hint: "Bay Area Youth Education" or "NYC Arts Culture"
allowed-tools: Read, Grep, Glob, Bash(python3 *), Bash(ls *), Write, mcp__postgres__execute_query
---

# Generate Foundation List

Create a branded "Top N Foundations" PDF + CSV for a geography and topic.

**Arguments:** $ARGUMENTS

## Instructions

**STEP 0: Parse arguments.**

Map `$ARGUMENTS` to script parameters. If arguments are empty, ask: "What geography and topic? Example: Bay Area Youth Education"

### Known tested combinations

**Bay Area + Youth/Education** (tested 2026-02-23, 150 results):
```
--state CA
--cities "SAN FRANCISCO,OAKLAND,BERKELEY,PALO ALTO,SAN JOSE,MENLO PARK,MOUNTAIN VIEW,SUNNYVALE,SANTA CLARA,REDWOOD CITY,SAN MATEO,FREMONT,HAYWARD,RICHMOND,WALNUT CREEK,CONCORD,PLEASANTON,LIVERMORE,DUBLIN,SAN RAFAEL,MILL VALLEY,SAUSALITO,TIBURON,NOVATO,LARKSPUR,CORTE MADERA,ROSS,FAIRFAX,SAN ANSELMO,BELVEDERE,KENTFIELD,BURLINGAME,HILLSBOROUGH,ATHERTON,WOODSIDE,PORTOLA VALLEY,LOS ALTOS,LOS ALTOS HILLS,CUPERTINO,CAMPBELL,SARATOGA,LOS GATOS,MILPITAS,SANTA CRUZ,CAPITOLA,SCOTTS VALLEY,DALY CITY,SOUTH SAN FRANCISCO,PACIFICA,HALF MOON BAY,SAN CARLOS,BELMONT,FOSTER CITY,ALAMEDA,EMERYVILLE,PIEDMONT,ORINDA,LAFAYETTE,MORAGA,DANVILLE,SAN RAMON,UNION CITY,NEWARK,NAPA,SONOMA,PETALUMA,SANTA ROSA,HEALDSBURG,SEBASTOPOL,VALLEJO,BENICIA"
--topic-regex "youth|education|school|student|children|after.school|tutoring|literacy|scholarship|elementary|secondary|k.12|young people|child"
--topic-label "Youth & Education"
--geo-label "Bay Area"
```

### Mapping rules for new combinations

For **geography**, determine:
- `--state`: The 2-letter state code (REQUIRED, bounds the query)
- `--cities`: Major cities in the metro area, UPPER CASE, comma-separated. Omit for statewide.
- `--geo-label`: Human-readable label (e.g., "Bay Area", "Los Angeles", "NYC Metro")

For **topic**, determine:
- `--topic-regex`: PostgreSQL case-insensitive regex matching grant purpose text. Include synonyms and related terms. Use `|` for alternatives.
- `--topic-label`: Human-readable label (e.g., "Youth & Education", "Arts & Culture")

Common topic regex patterns:
- Arts/Culture: `art|arts|culture|museum|theater|theatre|music|dance|visual art|performing art|gallery|orchestra|symphony`
- Environment: `environment|conservation|climate|sustainability|wildlife|habitat|ecology|clean energy|renewable`
- Health: `health|medical|hospital|clinic|mental health|wellness|disease|patient|healthcare`
- Housing: `housing|homeless|shelter|affordable housing|transitional|supportive housing`

**STEP 1: For NEW (untested) combinations, validate first.**

Run a COUNT(*) query to estimate results:

```sql
SELECT COUNT(DISTINCT fg.foundation_ein) as foundation_count,
       COUNT(*) as grant_count,
       SUM(fg.amount)::bigint as total_giving
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_foundations df ON fg.foundation_ein = df.ein
WHERE df.state = '{state}'
  AND fg.tax_year >= {min_year}
  AND fg.amount > 0
  AND fg.purpose_text ~* '{topic_regex}'
```

Show the user: "Found {N} foundations with {M} matching grants ({$X total}). Proceed?"

If foundation_count < 20, warn: "Only {N} foundations match. Consider broadening the topic regex or removing city filters."

**STEP 2: Run the script.**

```bash
python3 "0. Tools/generate_foundation_list.py" \
    --state {STATE} \
    --cities "{CITIES}" \
    --topic-regex "{REGEX}" \
    --topic-label "{TOPIC_LABEL}" \
    --geo-label "{GEO_LABEL}" \
    --output-dir "Enhancements/{YYYY-MM-DD}/" \
    --skip-pdf
```

Note: Run with `--skip-pdf` first to review the data before generating PDF.

**STEP 3: STOP gate.**

Show the user:
- Top 10 foundations from the summary output
- Total combined giving and grant count
- Count of foundations and any truncation warnings
- Ask: "Data looks good? Generate PDF?"

**STEP 4: Generate PDF.**

```bash
python3 "0. Tools/md_to_pdf.py" --input "{md_path}" --output "{pdf_path}"
```

Verify the PDF was created and report its file size.

**STEP 5: Write session report.**

Create `REPORT_YYYY-MM-DD_foundation_list_{geo_slug}.md` in `Enhancements/{YYYY-MM-DD}/` with:
- Query parameters used
- Foundation count, combined giving, total grants
- Top 10 list
- Data quality notes (truncation warnings, city distribution)
- File paths for all outputs

## Extension notes

- **"Based in" filter:** v1 filters by where foundations are headquartered, not where they send grants. A San Francisco foundation may fund nationally.
- **National queries:** Not supported in v1. `--state` is required to prevent 8.3M-row regex scans.
- **Name overrides:** When new truncated names appear, add them to `NAME_OVERRIDES` in `0. Tools/generate_foundation_list.py`.
