# PROMPT: Sales & Marketing Folder Audit & Reorganization

**Date:** 2025-12-31
**Type:** Deep Dive Audit + Reorganization Proposal
**Target Path:** `/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing`

---

## Context

The Sales & Marketing folder has accumulated multiple prospect lists, outreach tracking files, and campaign materials over time. The user can no longer remember which prospect list contains what criteria or how files relate to each other. 

**Primary Goal:** Create a comprehensive inventory of all files, understand what each contains, and propose a consolidated organization system.

**Secondary Goal:** Identify which prospect lists are best for continued cold calling (user's highest-converting channel at 6% interest rate).

**Immediate Priority:** User wants to start calling **foundation management companies** (e.g., Whittier Trust, Foundation Source, etc.). These are B2B targets where one relationship could unlock dozens of foundation clients. Identify any existing lists that contain foundation management companies, or flag that a new list needs to be created.

**Call Tracking Workbook:** The user has been tracking calls in:
```
/Users/aleckleinman/Downloads/Beta Test Group Calls.xlsx
```
This is the PRIMARY call tracking file. It contains:
- **Foundations sheet** - foundation call tracking
- **Nonprofits sheet** - nonprofit call tracking
- **Additional sheets** - likely prospect lists, some may be duplicates of lists in the Sales & Marketing folder

Locate this file and document:
- All sheet names and their purposes
- Column structure for each sheet
- How many calls logged per sheet
- Current status of call campaign
- Which sheets are tracking vs. prospect lists
- **Cross-reference with Sales & Marketing folder** - identify any duplicate prospect data

---

## Phase 1: Deep Inventory (Do First)

### Target Locations
Audit BOTH of these locations:

1. **Sales & Marketing folder:**
   ```
   /Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing
   ```

2. **Call Tracking Workbook:**
   ```
   /Users/aleckleinman/Downloads/Beta Test Group Calls.xlsx
   ```

### Task 1.1: Full Directory Scan
Recursively scan the entire folder structure:
```
/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing
```

Create a complete tree showing:
- All folders and subfolders
- All files with extensions
- File sizes and modification dates

### Task 1.2: File-by-File Analysis

For EVERY file found, document:

**For CSV/Excel files:**
| Field | What to Capture |
|-------|-----------------|
| Filename | Full name with extension |
| Location | Subfolder path |
| Row count | Number of records |
| Column names | All column headers |
| Key fields | Email, phone, org name, EIN if present |
| Apparent purpose | What this list seems to be for |
| Date range | If dates present, what range |
| Unique identifiers | What makes records unique |
| Duplicates | Any obvious internal duplicates |
| Data quality | Missing values, formatting issues |

**For Documents (PDF, DOCX, TXT, MD):**
| Field | What to Capture |
|-------|-----------------|
| Filename | Full name |
| Type | Template, report, notes, script, etc. |
| Purpose | What it's used for |
| Status | Current, outdated, draft |
| Related files | What other files it connects to |

**For Scripts (PY, JS, etc.):**
| Field | What to Capture |
|-------|-----------------|
| Filename | Full name |
| Purpose | What it does |
| Input files | What data it reads |
| Output files | What it produces |
| Dependencies | What it requires to run |
| Last modified | When it was last updated |

### Task 1.3: Cross-Reference Analysis

After inventorying all files:

1. **Identify overlapping prospect lists:**
   - Which CSVs contain the same organizations?
   - What's the total unique prospects across all lists?
   - Where are duplicates?

2. **Map the outreach pipeline:**
   - Which lists feed into which scripts?
   - What's the flow from prospect → contacted → responded?

3. **Identify orphaned files:**
   - Files that don't connect to any workflow
   - Outdated versions superseded by newer files

---

## Phase 2: Findings Report

Create: `REPORT_2025-12-31_sales_marketing_audit.md`

### Report Structure:

```markdown
# Sales & Marketing Folder Audit Report

## Executive Summary
- Total files found: X
- Prospect lists identified: X
- Total unique prospects: X
- Recommended actions: X

## Current Folder Structure
[Tree diagram of current state]

## File Inventory

### Prospect Lists (CSV/Excel)
| File | Location | Rows | Key Columns | Purpose | Quality |
|------|----------|------|-------------|---------|---------|

### Campaign Materials
| File | Type | Purpose | Status |
|------|------|---------|--------|

### Scripts & Tools
| File | Purpose | Inputs | Outputs |
|------|---------|--------|---------|

### Other Files
| File | Type | Notes |
|------|------|-------|

## Prospect List Deep Dive

### List 1: [filename]
- **Records:** X
- **Columns:** [list]
- **Filters/Criteria:** [what defines this list]
- **Source:** [where it came from]
- **Overlap with:** [other lists]
- **Recommended action:** Keep / Merge / Archive

[Repeat for each prospect list]

## Duplicate Analysis
- X organizations appear in multiple lists
- [Details on overlaps]

## Outreach Pipeline Map
[Visual or text description of how files connect]

## Issues Found
1. [Issue 1]
2. [Issue 2]
...

## Recommendations Summary
[Numbered list of recommended actions]
```

---

## Phase 3: Reorganization Proposal

**STOP after Phase 2 report and wait for user review.**

After approval, propose new structure:

### Proposed Folder Structure
```
4. Sales & Marketing/
├── 1_Prospects/
│   ├── Master_List.csv              # Single consolidated prospect file
│   ├── Segments/                    # Filtered views
│   │   ├── segment_healthcare.csv
│   │   ├── segment_human_services.csv
│   │   └── segment_california.csv
│   └── Archive/                     # Old lists for reference
├── 2_Outreach/
│   ├── Cold_Calling/
│   │   ├── call_queue.csv          # Current call targets
│   │   ├── call_log.csv            # Outcomes
│   │   └── scripts/
│   ├── Email_Campaign/
│   │   ├── sent_tracker.csv
│   │   ├── response_tracker.csv
│   │   └── scripts/
│   └── LinkedIn/
│       └── [LinkedIn outreach files]
├── 3_Pipeline/
│   ├── leads.csv                   # Interested prospects
│   ├── beta_users.csv              # Active beta testers
│   └── customers.csv               # Paying customers
├── 4_Materials/
│   ├── Templates/
│   ├── Scripts/
│   └── One-Pagers/
└── Archive/
    └── [Old/superseded files with dates]
```

### Master Prospect List Schema
Propose a unified schema for consolidated prospect tracking:

| Column | Type | Description |
|--------|------|-------------|
| org_id | INT | Unique identifier |
| org_name | STR | Organization name |
| ein | STR | IRS EIN |
| email | STR | Primary contact email |
| phone | STR | Primary phone |
| contact_name | STR | Contact person |
| contact_title | STR | Their role |
| city | STR | Location |
| state | STR | State |
| ntee_code | STR | NTEE classification |
| annual_budget | INT | Approximate budget |
| source_list | STR | Which original list they came from |
| date_added | DATE | When added to master |
| outreach_status | STR | not_contacted / emailed / called / responded / converted |
| last_contact_date | DATE | Most recent outreach |
| notes | STR | Free text |

---

## Deliverables Checklist

- [ ] Phase 1: Complete file inventory
- [ ] Phase 2: `REPORT_2025-12-31_sales_marketing_audit.md`
- [ ] STOP for user review
- [ ] Phase 3: Reorganization proposal (after approval)
- [ ] Phase 4: Implementation plan (after approval)

---

## Important Notes

1. **Do not move or modify any files** until reorganization is approved
2. **Preserve all original data** - archive, don't delete
3. **Document everything** - user needs to understand what each file is
4. **Prioritize call prospects** - user's cold calling converts at 6% vs 0.23% email
5. **Flag high-value segments** - Healthcare (NTEE E) and Human Services (NTEE P) are best sectors

---

## Questions to Answer in Report

1. How many total unique organizations exist across all prospect lists?
2. How many have phone numbers? (Critical for cold calling)
3. How many have already been contacted (email or phone)?
4. What's the best untapped list for continued calling?
5. Are there any lists that should be regenerated or updated?
6. **Where is `Beta Test Group Calls.xlsx` and what's its current state?**
7. **Are there any foundation management companies in existing lists?** (e.g., Whittier Trust, Foundation Source, Bessemer Trust, Northern Trust, U.S. Trust, Glenmede, Fiduciary Trust). If not, flag that a new list needs to be created.
8. **What's the overlap between the call tracking workbook and the prospect lists?**

---

*Prepared for Claude Code CLI execution*
