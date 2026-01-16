# Cookie Cutter Data Science Migration Report

**Date:** 2026-01-04
**Prompt:** Migrate TheGrantScout project to Cookie Cutter Data Science structure
**Status:** Complete
**Owner:** Alec Kleinman

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-04 | Claude | Initial migration complete |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Migration Phases](#migration-phases)
3. [New Folder Structure](#new-folder-structure)
4. [Files Moved](#files-moved)
5. [Git Commits](#git-commits)
6. [Rollback Instructions](#rollback-instructions)
7. [Cleanup Recommendations](#cleanup-recommendations)
8. [Notes](#notes)

---

## Executive Summary

Successfully migrated TheGrantScout project from ad-hoc folder structure to industry-standard Cookie Cutter Data Science layout. All 8 phases completed with git commits between each phase for rollback capability.

**Key Metrics:**
- 8 migration phases completed
- 8 git commits created
- All pipeline imports verified working
- All critical paths validated
- CLAUDE.md updated to v5.0

**New Structure Highlights:**
- `docs/` - Centralized documentation
- `models/` - Versioned model artifacts with `current` symlink
- `pipeline/` - All scripts and configs
- `runs/` - Client execution outputs
- `business/` - Sales, marketing, beta testing
- `data/raw/` - Symlink to IRS XML data (30GB)

---

## Migration Phases

| Phase | Description | Commit | Status |
|-------|-------------|--------|--------|
| 1 | Create folder structure | e2d2be0 | ✅ Complete |
| 2 | Move documentation | 3d13711 | ✅ Complete |
| 3 | Move model versions | 2703b2a | ✅ Complete |
| 4 | Move pipeline scripts | 317963a | ✅ Complete |
| 5 | Move client runs | 67ca60d | ✅ Complete |
| 6 | Move business folders | 8662cf3 | ✅ Complete |
| 7 | Update .claude paths | 5f1844d | ✅ Complete |
| 8 | Archive old specs | 345c34e | ✅ Complete |

---

## New Folder Structure

```
TheGrantScout/
├── .claude/                    # Claude Code configuration (932K)
│   ├── CLAUDE.md              # Main context file (v5.0)
│   ├── rules/                 # Domain-specific rules
│   ├── guides/                # How-to guides
│   └── skills/                # Claude skills
├── docs/                       # Documentation (296K)
│   ├── data-dictionary.md     # Database schema reference
│   ├── database-summary.md    # Stats and counts
│   └── specs/archive/         # Historical specs (16 files)
├── models/                     # Algorithm versions (632K)
│   ├── current -> v6.1/       # Symlink to production
│   ├── v6.1/                  # LASSO V6.1 (AUC: 0.94)
│   ├── v6/                    # Archived
│   ├── v5/                    # Archived
│   └── archive/exploration/   # Early R&D
├── pipeline/                   # Scripts and config (1.4M)
│   ├── scripts/               # 01-09 pipeline scripts
│   ├── config/                # coefficients.json, etc.
│   └── archive/               # Pipeline v1
├── runs/                       # Client outputs (7.3M, gitignored)
│   ├── PSMF/                  # Patient Safety Movement Foundation
│   ├── HN/                    # Horizons National
│   ├── FCSD/                  # Florida schools
│   └── ... (13 clients)
├── business/                   # Operations (93M)
│   ├── sales-marketing/       # LinkedIn, email sequences
│   ├── beta-testing/          # Client questionnaires
│   └── website/               # Landing page (no node_modules)
├── data/                       # Data files
│   └── raw/ -> ../1. Database/0. Raw IRS Data/  # Symlink (30GB)
└── .gitignore                  # Updated for new structure
```

---

## Files Moved

### Documentation (docs/)
| Source | Destination |
|--------|-------------|
| 1. Database/DATA_DICTIONARY_2025-12-22.md | docs/data-dictionary.md |
| 1. Database/DATABASE_SUMMARY_2025-12-22.md | docs/database-summary.md |
| 7. The Grant Scout Specs/*.md | docs/specs/archive/ |

### Models (models/)
| Source | Destination |
|--------|-------------|
| Pipeline v2/outputs/v5/ | models/v5/ |
| Pipeline v2/outputs/v6/ | models/v6/ |
| Pipeline v2/outputs/v6.1/ | models/v6.1/ |
| 5. Matching Algorithm/*.md | models/archive/exploration/ |

### Pipeline (pipeline/)
| Source | Destination |
|--------|-------------|
| Pipeline v2/scripts/ | pipeline/scripts/ |
| Pipeline v2/config/ | pipeline/config/ |
| 5. Pipeline/Pipeline v1/ | pipeline/archive/v1/ |

### Business (business/)
| Source | Destination |
|--------|-------------|
| 4. Sales & Marketing/ | business/sales-marketing/ |
| 2. Beta Testing/ | business/beta-testing/ |
| 3. Website/ | business/website/ |

---

## Git Commits

```
345c34e Phase 8: Archive old specs to docs/specs/archive/
5f1844d Phase 7: Update .claude paths for Cookie Cutter structure
8662cf3 Phase 6: Move business folders
67ca60d Phase 5: Move client runs to runs/
317963a Phase 4: Move pipeline scripts and config
2703b2a Phase 3: Move model versions to models/
3d13711 Phase 2: Move documentation to docs/
e2d2be0 Phase 1: Create Cookie Cutter folder structure
```

---

## Rollback Instructions

To rollback to any phase, use:

```bash
git reset --hard <commit-hash>
```

**Rollback points:**
- Before Phase 1: `git reset --hard HEAD~8`
- Before Phase 4: `git reset --hard e2d2be0~1` (keep folder structure only)

**Note:** Files were COPIED, not moved. Original folders still exist and can be referenced.

---

## Cleanup Recommendations

### Safe to Delete (After Validation)
Once you've validated the new structure works, these can be removed:

| Folder | Size | Notes |
|--------|------|-------|
| `7. The Grant Scout Specs/` | 200K | Archived to docs/specs/archive/ |
| `0. OLD/` | 4.8GB | Historical data, audit before deleting |

### Keep As-Is
| Folder | Size | Reason |
|--------|------|--------|
| `1. Database/` | 30GB | Raw IRS data referenced via symlink |
| `5. TheGrantScout - Pipeline/` | 3.5GB | Contains large training CSVs |

### Disk Space Recovery Potential
| Action | Savings |
|--------|---------|
| Delete 7. The Grant Scout Specs/ | ~200K |
| Delete 0. OLD/ (after audit) | ~4.8GB |
| Clear node_modules from original 3. Website/ | ~600MB |

---

## Notes

### Excluded from Git
- `runs/*/` - Client outputs (can be regenerated)
- `data/raw/` - Symlink to 30GB IRS data
- `*.m4a`, `*.mp3`, `*.wav` - Audio recordings in business/

### Large Files Not Migrated
Training CSVs (1.4GB total) remain in original location:
- `5. TheGrantScout - Pipeline/Pipeline v2/outputs/v*/`

### Path Updates in CLAUDE.md
Key Paths section updated to reflect new structure:
- `docs/` for documentation
- `models/current/` for production model
- `pipeline/scripts/` for pipeline execution
- `runs/{client}/{date}/` for outputs

---

*Generated by Claude Code on 2026-01-04*
