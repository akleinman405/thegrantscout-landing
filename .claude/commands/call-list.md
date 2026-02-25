---
description: Generate nonprofit cold-call prospect list for TGS sales
argument-hint: "veterans-national" or describe what you need
allowed-tools: Read, Grep, Glob, Bash(python3 *), Bash(ls *), Write
---

# Generate Call List

Create a cold-call prospect CSV with viability screening, keyword matching, and geographic diversity.

**Arguments:** $ARGUMENTS

## Instructions

**STEP 0: Parse arguments + determine .N prompt number.**

Scan `Enhancements/` for today's date folder. Count existing PROMPT/REPORT/DATA files to determine the next `.N` value. Use this for all output files.

If `$ARGUMENTS` matches a preset name exactly (e.g., "veterans-national"), use `--preset`.
If `$ARGUMENTS` is empty, run `--list-presets` and ask the user to pick.
Otherwise, interpret natural language to identify:
- Categories (map to `--categories`)
- State filter (map to `--state`)
- Limit (map to `--limit`)
- Any other overrides

Run `--list-presets` first to show available options if the mapping is ambiguous.

### Available presets

- **veterans-national**: Veteran/sailing/aviation/therapy nonprofits, national, <$5M, 100 limit
- **veterans-ca**: California veteran/sailing/therapy, <$5M, 50 limit
- **maritime-national**: Sailing/maritime orgs nationally, 50 limit

### Keyword categories

- **veterans**: veteran, wounded warrior
- **sailing_maritime**: sailing, sailboat, maritime
- **aviation**: aviation, airplane, flight
- **adaptive_therapy**: equine therapy, adventure therapy, adaptive sport, adaptive recreation, recreational therapy

Config file: `4. Pipeline/config/call_list_keywords.json`

**STEP 1: Preview (STOP gate).**

Run the tool in preview mode:

```bash
python3 "0. Tools/generate_call_list.py" --preset {PRESET} --preview-only --verbose
```

Or with manual params:

```bash
python3 "0. Tools/generate_call_list.py" \
    --categories {CATEGORIES} \
    --state {STATE} \
    --limit {LIMIT} \
    --preview-only --verbose
```

Show the user:
- Row count and category breakdown
- State distribution (top 10)
- Revenue bucket breakdown
- 10 diverse sample rows
- Any verification warnings

Ask: "Preview shows {N} prospects across {S} states. Proceed to generate CSV?"

If < 20 rows, warn: "Only {N} results. Consider broadening: more categories, remove --state, increase --max-revenue."

**STEP 2: Generate CSV.**

Run without `--preview-only`:

```bash
python3 "0. Tools/generate_call_list.py" \
    --preset {PRESET} \
    --output-dir "Enhancements/{YYYY-MM-DD}/" \
    --output-name "DATA_{YYYY-MM-DD}.{N}_prospect_call_list"
```

Show the non-blocking verification summary: row count, file size, pass/fail.

After CSV is written, rename to follow naming convention if needed. The output file should be:
`Enhancements/{YYYY-MM-DD}/DATA_{YYYY-MM-DD}.{N}_prospect_call_list.csv`

**STEP 3: Write session report.**

Create `Enhancements/{YYYY-MM-DD}/REPORT_{YYYY-MM-DD}.{N}_prospect_call_list.md` with:
- Parameters used (preset, categories, state, limit, caps)
- Row count, category breakdown table
- State distribution table (top 15)
- Revenue bucket breakdown table
- Verification results
- File paths for all outputs
- Follow the standard report structure from CLAUDE.md

## Tool reference

```
python3 "0. Tools/generate_call_list.py" --help

Key flags:
  --preset NAME           Load a named preset from config
  --categories a,b,c      Comma-separated category names
  --state XX              2-letter state code (omit for national)
  --max-revenue N         Revenue cap in dollars
  --limit N               Max output rows
  --state-cap N           Max orgs per state
  --output-dir DIR        Output directory
  --output-name NAME      Base name for CSV (no extension)
  --preview-only          Stats + sample, no CSV
  --dry-run               Print SQL + params, exit
  --list-presets           Show available presets
  --verbose               Extra detail
```

## Extension notes

- To add new keywords: edit `4. Pipeline/config/call_list_keywords.json` only. No Python changes needed.
- To add a new preset: add an entry to the `presets` object in the same JSON file.
- All database access goes through the Python tool (no MCP queries in this command).
