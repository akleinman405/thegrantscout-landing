---
description: Run the report generation pipeline for a client
argument-hint: Client name (e.g., "SNS", "VetsBoats", "HN")
allowed-tools: Read, Grep, Glob, Bash(python3 *), Bash(ls *), Bash(git *), Write, mcp__postgres__execute_query
---

# Run Report Generation Pipeline

Execute the V2 report generation pipeline for a client.

Client: $ARGUMENTS

## Instructions

**STEP 0: Validate.** If `$ARGUMENTS` is empty, ask: "Which client should I run the pipeline for?" List known clients from `dim_clients`.

**STEP 1: Load client profile.**

Check if a client profile exists:
- `4. Pipeline/config/clients/` for JSON profiles
- `dim_clients` table for database records

```sql
SELECT id, name, ein, known_funders FROM f990_2025.dim_clients WHERE name ILIKE '%{client}%';
```

If no profile exists, inform the user and offer to create one from the questionnaire.

**STEP 2: Confirm run parameters** with the user:

```
Pipeline Run: {Client Name}
Date: YYYY-MM-DD
Output: 5. Runs/{Client}/YYYY-MM-DD/
Profile: {profile path}
Known funders to exclude: {count}
```

Ask: "Ready to run, or any adjustments?"

**STEP 3: Execute pipeline stages sequentially.**

Create the output directory: `5. Runs/{Client}/YYYY-MM-DD/`

Run each stage, checking for errors before proceeding:

| Stage | Script | Output |
|-------|--------|--------|
| 01 | `02_score_foundations_v6.1.py` | `02_scored_foundations.csv` |
| 02 | `03_check_enrichment.py` | `03_enrichment_status.json` |
| 03 | `04_filter_viable.py` | `04_viable_foundations.json` |
| 04 | `05_assemble_opportunities.py` | `05_opportunities.json` |
| 05 | `06_generate_narratives.py` | `06_narratives.json` |
| 06 | `07_build_report_data.py` | `07_report_data.json` |
| 07 | `08_render_report.py` | `08_report.md` |
| 08 | `09_convert_to_docx.py` | `08_report.docx` |

After each stage, report: stage name, duration, output file size, any warnings.

**STEP 4: Quality checks.**

After the pipeline completes:
- [ ] Report has correct client name
- [ ] No known funders appear in results
- [ ] All foundations have recent grant activity (within 3 years)
- [ ] Dollar amounts formatted consistently
- [ ] No duplicate foundations
- [ ] Contact info or URLs present for each match

**STEP 5: Summary.**

Present results:
```
Pipeline Complete: {Client Name}
Foundations scored: {count}
Viable matches: {count}
Report: 5. Runs/{Client}/YYYY-MM-DD/08_report.md
Word doc: 5. Runs/{Client}/YYYY-MM-DD/08_report.docx
Duration: {total time}
```
