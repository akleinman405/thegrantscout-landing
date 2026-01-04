# SPEC: DATABASE_SPEC.md

**Document Type:** SPEC  
**Purpose:** Final database architecture  
**Date:** 2025-12-08

---

## Sections

### 1. Schema Overview
- All tables at a glance
- Relationships diagram (ERD)
- Database technology (PostgreSQL, extensions)

### 2. Core Tables
For each core table (foundations, historical_grants, nonprofits, matches, current_opportunities):
- Purpose
- Key fields with types
- Indexes
- Constraints
- Row count (current)
- Population status

### 3. Derived Tables
For each derived table (foundation_intelligence, openness_scores):
- Purpose
- Calculated fields and their formulas
- Refresh frequency
- Dependencies on source tables

### 4. Source Tables
- f990_2025 schema (pf_returns, pf_grants, officers, etc.)
- IRS BMF tables
- Purpose of each
- How they feed into core tables

### 5. Current State
- What's populated vs empty
- Row counts per table
- Data quality issues known
- Recent imports/updates

### 6. Build Tasks
- SQL migrations needed
- Python scripts needed to populate derived tables
- Data enrichment tasks (EIN matching, URL cleaning, etc.)
- Priority order

### 7. Source Files
- File paths to DATA_DICTIONARY.md
- File paths to migration scripts
- File paths to import validation reports

---

## Source Files to Reference
- `/mnt/project/DATA_DICTIONARY.md`
- `/mnt/project/Build_Plan.md`
- `/mnt/project/REPORT_2025-12-4_1_import_validation.md`
- `/mnt/project/REPORT_2025-12-5_1_grant_purpose_bug.md`
- `/mnt/project/DATABASE_VALIDATION_REPORT.md`
- `/mnt/project/data-engineer.md`
