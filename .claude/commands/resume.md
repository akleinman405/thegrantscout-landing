---
description: Load session state and resume where you left off
argument-hint: Date (YYYY-MM-DD) or keyword (optional)
allowed-tools: Read, Grep, Glob, Bash(git *)
---

# Resume From Last Session

Pick up where the last session left off. Load context from the memory directory (primary) or project folders (fallback) and present a task-focused summary.

Optional argument: a date (YYYY-MM-DD) or keyword (e.g., "vetsboats"): $ARGUMENTS

## Instructions

**Step 1: Check memory directory first.**

Read `~/.claude/projects/-Users-aleckleinman-Documents-TheGrantScout/memory/session_state.md`.

- If `$ARGUMENTS` is empty or blank AND the file exists, use it as the primary source. Skip to Step 3.
- If `$ARGUMENTS` contains a date (YYYY-MM-DD) or keyword, proceed to Step 2 (folder search) regardless of whether the memory file exists.
- If the memory file doesn't exist, proceed to Step 2.

**Step 2: Search project folders (fallback or targeted search).**

Search for session state files by checking these locations (newest first):
- `4. Pipeline/Enhancements/YYYY-MM-DD/` folders
- `5. Runs/*/YYYY-MM-DD/` folders (for client work)
- `6. Business/` (for sales/marketing work)

How to search:
- **If a date was given:** Look specifically in folders matching that date. Read any `SESSION_STATE_*.md` or `CONTINUITY_*.md` files found there.
- **If a keyword was given** (e.g., "vetsboats", "psmf"): Search for `SESSION_STATE_*` files whose name or content matches the keyword (case-insensitive). Use Glob to find candidates, then read the best match.
- **If memory file was missing (no args):** Find the most recent folder across Enhancements and Runs that contains a `SESSION_STATE_*.md` file.

Read session files in priority order:
1. `SESSION_STATE_*.md` or `CONTINUITY_*.md` files (most actionable)
2. Highest-numbered `REPORT_YYYY-MM-DD.N_*.md` (most recent work)
3. Any `GUIDE_*.md` or `PLAN_*.md` files for broader context

**Step 3: Gather supplementary git context.** Run these in parallel:
- `git status` to check for uncommitted work-in-progress
- `git log --oneline -10` for recent commit history

These are informational, not the main event.

**Step 4: Present a task-focused resume summary:**

```
## Session Resume

**Last session:** YYYY-MM-DD [HH:MM if available]
**Task:** [task description from session state]
**Source:** [file name and path used]
**Status:** [In Progress / Blocked / Complete]

### Resume Point
[The "Do This Next" item from the session state, or the most critical next action]

### What Was Accomplished
[Key accomplishments from the session state]

### Pending Items
[Items marked as partially done or not started]

### Active Blockers
[Any blockers found, or "None"]

### Git Context
[Brief: last 3-5 commits + uncommitted changes summary, or "Working tree clean"]
```

**Step 5: Ask the user:** "Ready to continue from here, or would you like to focus on something specific?"
