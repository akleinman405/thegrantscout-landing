# Prompt: Explore Project Structure & Propose Cookie Cutter Migration

## Context
TheGrantScout is an AI-powered grant matching service. The project has grown organically and now needs reorganization to follow industry-standard "Cookie Cutter Data Science" patterns. This is an **exploratory task only** - no files will be moved yet.

## Your Task
Explore the specified folders, understand what's there, and propose a migration plan to Cookie Cutter Data Science structure.

## Folders to Explore

Examine these folders in depth (list files, read key ones to understand purpose):

1. **`5. TheGrantScout - Pipeline/`** - Report generation pipeline, scripts
2. **`1. Database/`** - Database schemas, modeling files, algorithm work
3. **`7. The Grant Scout Specs/`** - Project specifications (may be outdated)
4. **`outputs/`** - Generated outputs, model artifacts
5. **`3. Website/`** - Website-related files
6. **`4. Sales & Marketing/`** - Business development materials
7. **`2. Beta Testing/`** - Beta tester feedback and tracking
8. **`4. Research/`** - Research materials

For each folder:
- List all files with brief descriptions
- Identify which files are current vs. outdated/superseded
- Note any version progressions (v1, v2, v6.1, etc.)
- Flag files that reference paths to other files (scripts with imports, configs)

## Target Structure (Cookie Cutter Data Science)

The industry standard structure we're moving toward:

```
TheGrantScout/
├── README.md                    # Project overview (1-2 pages)
├── CHANGELOG.md                 # Version history
├── .claude/
│   └── CLAUDE.md               # AI assistant context
│
├── docs/                        # Component documentation
│   ├── architecture.md         # System design
│   ├── data-dictionary.md      # Database reference
│   └── onboarding.md           # Getting started guide
│
├── models/                      # Model versioning
│   ├── README.md               # "How the matching algorithm works"
│   ├── CHANGELOG.md            # Model version history
│   ├── v6.1/                   # Each version preserved
│   │   ├── README.md
│   │   ├── coefficients.json
│   │   └── REPORT_*.md
│   └── current -> v6.1/        # Symlink to current version
│
├── pipeline/                    # Report generation
│   ├── README.md               # "How to generate a client report"
│   ├── scripts/                # Active scripts
│   ├── config/                 # Configuration files
│   └── archive/                # Old script versions (dated)
│
├── data/                        # Data documentation & schemas
│   ├── README.md               # Data sources, refresh schedule
│   └── schemas/                # SQL schemas, ERDs
│
├── reports/                     # Analysis & evaluation reports
│   ├── 2025-12/
│   └── 2026-01/
│
├── research/                    # Research materials
│   └── README.md
│
└── business/                    # Non-technical folders
    ├── sales-marketing/
    ├── beta-testing/
    └── website/
```

## Deliverables

### 1. Inventory Report
For each explored folder, provide:
```
## [Folder Name]
**Purpose:** What this folder contains
**File Count:** X files, Y subfolders
**Key Files:**
- filename.ext - description, current/outdated, last modified if visible

**Version Progressions Found:**
- [list any v1→v2→v3 patterns]

**Scripts with Path Dependencies:**
- script.py references: path/to/file.sql, other/config.json
```

### 2. Proposed Migration Map
Create a table showing:
```
| Current Location | Proposed Location | Action | Notes |
|------------------|-------------------|--------|-------|
| 1. Database/schema.sql | data/schemas/schema.sql | Move | Active |
| 1. Database/old_model.py | models/archive/old_model.py | Archive | Superseded by v6 |
```

### 3. Path Updates Required
List every script that would need path updates:
```
| Script | Current Import/Path | New Path After Migration |
|--------|---------------------|--------------------------|
```

### 4. Recommendations
- Which files should be archived vs. kept active?
- Which specs/docs are outdated and should be marked as such?
- What new README files need to be created?
- Suggested order of migration (dependencies first)

### 5. Questions for Human
List any ambiguities or decisions needed before migration can proceed.

## Important Notes
- **DO NOT move any files** - this is exploration only
- Preserve version history - don't flatten everything to "current only"
- Flag anything that looks important but unclear
- Note file sizes for large files that might need special handling

## Output Format
Create a single report: `REPORT_2025-01-04_cookie_cutter_exploration.md` with all findings organized by the deliverable sections above.
