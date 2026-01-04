# PROMPT: Pipeline Audit & Status Report

**Date:** 2025-12-30  
**Agent:** Builder (or direct CLI)  
**Priority:** High  

---

## Situation

We ran a series of 9+ build prompts overnight to create the TheGrantScout report generation pipeline. The PHASE_COMPLETE.md files indicate Phases 0, 2, 3a, and 3b are done. A dry-run was already executed. Now we need a comprehensive audit of:
- What files actually exist
- Which modules work vs are broken/stubs
- What reports were generated
- What's missing before production use

**Pipeline Location:** Find the `TheGrantScout - Pipeline/` folder (likely in the parent directory or a sibling folder)

---

## Tasks

### 1. Directory Inventory
```bash
# Find the pipeline folder first
find ~ -type d -name "*Pipeline*" 2>/dev/null | head -5

# Then map the structure
cd [pipeline_folder]
find . -type f -name "*.py" | wc -l
find . -type f -name "*.py" | sort
ls -la outputs/reports/ 2>/dev/null || echo "No reports dir"
```

### 2. Module Import Tests

Test each required import in Python. Record pass/fail:

```python
# Test script - run each import separately
imports_to_test = [
    "from config import init_pool, query_df",
    "from config.settings import PROJECT_ROOT",
    "from scoring import GrantScorer", 
    "from scoring.features import calculate_features",
    "from enrichment import get_funder_snapshot, find_connections",
    "from loaders import load_questionnaire, get_all_clients, ClientProfile",
    "from assembly import assemble_report_data",
    "from scraper import gather_for_report",
    "from ai import generate_all_narratives", 
    "from rendering import ReportRenderer"
]
```

### 3. Database Connection Test

```python
from config.database import init_pool, query_df
init_pool()
result = query_df("SELECT COUNT(*) as cnt FROM foundations")
print(f"Foundations count: {result['cnt'].iloc[0]}")
```

### 4. Find Generated Outputs

```bash
# Check for any generated reports
find . -name "*.md" -path "*/outputs/*" -type f
find . -name "*.json" -path "*/outputs/*" -type f
find . -name "*.log" -path "*/outputs/*" -type f

# Check for cached data
ls -la data/cache/ 2>/dev/null
```

### 5. Questionnaire Check

```python
from loaders import get_all_clients
clients = get_all_clients()
print(f"Clients found: {len(clients)}")
for c in clients:
    print(f"  - {c.organization_name} ({c.ein})")
```

### 6. Component Deep Check

For any module that imports successfully, verify it's not a stub:
- Check if key functions have actual implementation (>10 lines)
- Look for `pass` or `raise NotImplementedError`

---

## Expected Output

Create `PIPELINE_AUDIT_REPORT.md` in the pipeline's root folder with:

### Section 1: Directory Structure
- Tree view of all Python files
- Count of files per module folder

### Section 2: Module Status Table

| Module | Import Status | Key Functions | Notes |
|--------|---------------|---------------|-------|
| config | ✓/✗ | init_pool, query_df | |
| scoring | ✓/✗ | GrantScorer.score_nonprofit | |
| enrichment | ✓/✗ | get_funder_snapshot | |
| loaders | ✓/✗ | load_questionnaire, get_all_clients | |
| assembly | ✓/✗ | assemble_report_data | |
| scraper | ✓/✗ | gather_for_report | |
| ai | ✓/✗ | generate_all_narratives | |
| rendering | ✓/✗ | ReportRenderer.render | |

### Section 3: Generated Reports
- List all .md and .json files in outputs/ with timestamps
- Note which clients have reports

### Section 4: Database Status
- Connection: working/failed
- Foundation count
- Sample query result

### Section 5: Client Inventory
- List all clients from questionnaire with EINs

### Section 6: Issues Found
- Import errors (with full traceback)
- Missing files
- Stub implementations
- Broken dependencies

### Section 7: Recommended Next Steps
- Prioritized list of what needs fixing
- Estimated complexity (low/medium/high)

---

## Success Criteria

- [ ] All 8 core modules tested for imports
- [ ] Database connection verified
- [ ] All generated reports listed
- [ ] All questionnaire clients identified
- [ ] Clear issue list with specific errors
- [ ] Actionable next steps provided

---

## Notes

- This is discovery/audit only - do NOT fix anything
- If a module fails to import, capture the full error
- Check for `.env` file existence (don't print credentials)
- The dry-run already completed, so reports should exist somewhere
