# Document Naming Rules - TheGrantScout

Standard naming conventions for all project files.

---

## Format

```
DOCTYPE_YYYY-MM-DD[.version]_description.ext
```

- **DOCTYPE** = Type of document (see categories below)
- **YYYY-MM-DD** = Date created
- **version** = Optional, order of that file type on that day (e.g., `.1`, `.2`)
- **description** = Brief snake_case description
- **ext** = File extension (.md, .py, .sql, etc.)

---

## Examples

```
REPORT_2025-12-05_beta_feedback_summary.md
SPEC_2025-11-17.1_opportunity_matcher.md     # first SPEC on Nov 17
PROMPT_2025-12-05.1_schema_gathering.md      # first PROMPT on Dec 5
PROMPT_2025-12-05.2_validation_check.md      # second PROMPT on Dec 5
OUTPUT_2025-12-10_sns_foundation_matches.md
DATA_2025-12-01_prospect_list.csv
```

---

## DOCTYPE Categories

| Type | Direction | Purpose |
|------|-----------|---------|
| SPEC | Input → Agent | Requirements, specifications, API contracts |
| PROMPT | Input → Agent | Instructions for Claude Code CLI |
| TASK | Input → Agent | Assigned work items |
| SOP | Reference | Standard operating procedures - repeatable workflows |
| SKILL | Reference | Claude skill definitions - domain-specific instructions |
| REPORT | Agent → Output | Analysis, findings, summaries |
| OUTPUT | Agent → Output | Generated deliverables, client-facing docs |
| LOG | Agent → Output | Activity logs, status updates |
| DATA | Bidirectional | Data files, exports, CSVs |
| README | Reference | Project/folder documentation |
| QUICKSTART | Reference | Getting started guides |

---

## Document Type Details

### SPEC (Specification)
- Requirements documents
- Algorithm specifications
- API contracts
- **Required sections:** Overview, Requirements, Acceptance Criteria

### PROMPT
- Instructions for Claude Code CLI
- Task assignments
- **Required sections:** Context/Situation, Tasks, Expected Output

### REPORT
- Analysis findings
- Status updates
- Research summaries
- **Required sections:** Executive Summary, Findings, Recommendations

### OUTPUT
- Generated deliverables
- Client-facing documents
- **Required sections:** Varies by deliverable type

### LOG
- Session activity logs
- Status updates
- Work logs
- **Format:** Timestamped entries

### DATA
- CSV exports
- JSON data files
- Database dumps
- **Convention:** Include column headers, use UTF-8 encoding

### SOP (Standard Operating Procedure)
- Repeatable workflows
- Step-by-step process guides
- Quality checklists
- **Required sections:** Overview, Prerequisites, Workflow Steps, Quality Checks
- **Example:** `SOP_report_generation.md`

### SKILL
- Claude skill definitions
- Domain-specific instructions for Claude Code
- **Required sections:** Overview, Required Fields, Process Steps, Output Format
- **Example:** `SKILL_foundation_scraper.md`

---

## Folder Structure

### Project Root
```
~/Documents/TheGrantScout/
├── .claude/
│   ├── CLAUDE.md
│   ├── rules/
│   ├── mcp/
│   ├── hooks/
│   └── templates/
├── 1. Database/
├── 2. Beta Testing/
├── 3. Website/
├── 4. Research/
├── 4. Sales & Marketing/
├── 5. Reports/
├── 6. Admin/
└── 7. The Grant Scout Specs/
```

### Project Template (for multi-prompt initiatives)

Use this structure when a project has multiple phases/prompts:

```
ProjectName_YYYY-MM/
├── 0_prompts/
│   ├── PROMPT_YYYY-MM-DD.1_phase1.md
│   ├── PROMPT_YYYY-MM-DD.2_phase2.md
│   └── ...
├── 1_outputs/
│   ├── phase1/
│   ├── phase2/
│   └── ...
├── 2_reports/
│   ├── REPORT_YYYY-MM-DD.1_phase1.md
│   ├── REPORT_YYYY-MM-DD.2_phase2.md
│   └── LESSONS_LEARNED.md
└── README.md
```

**Template location:** `.claude/templates/project_template/`

**To start a new project:**
```bash
cp -r .claude/templates/project_template "NewProject_2025-01"
```

---

## Output Location Rules

### Standard (single prompt)
1. **Outputs:** Same folder as the prompt file
2. **Reports:** Same folder as the prompt file

### Project Structure (multi-prompt)
1. **Prompts:** `0_prompts/`
2. **Outputs:** `1_outputs/phase{N}/`
3. **Reports:** `2_reports/`
4. **Lessons:** `2_reports/LESSONS_LEARNED.md`

### Global Locations
- **Data exports:** `1. Database/`
- **Client deliverables:** `2. Beta Testing/{client}/`

---

*See CLAUDE.md for project overview.*
