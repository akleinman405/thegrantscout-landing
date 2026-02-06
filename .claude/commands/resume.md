# Resume From Last Session

Pick up where the last development session left off. Quickly load context and present a summary.

Optional: Load a specific date's context by passing a date: $ARGUMENTS

## Instructions

1. **Determine which session to resume**:
   - If `$ARGUMENTS` contains a date (YYYY-MM-DD format), use that date
   - Otherwise, find the most recent folder that contains session files by checking:
     - `4. Pipeline/Enhancements/YYYY-MM-DD/` folders (newest first)
     - `5. Runs/*/YYYY-MM-DD/` folders (for recent client work)

2. **Gather context** by running these in parallel:
   - `git status` to check for uncommitted work-in-progress
   - `git log --oneline -10` for recent commit history
   - List files in the target enhancement or run folder

3. **Read session files in priority order** (stop once you have enough context, but read all that exist):
   - **Priority 1:** `SESSION_STATE_*.md` or `CONTINUITY_*.md` files — these have the most actionable resume info
   - **Priority 2:** Highest-numbered `REPORT_YYYY-MM-DD.N_*.md` — most recent work
   - **Priority 3:** Any `GUIDE_*.md` or `PLAN_*.md` files for broader context

4. **Check for active blockers**:
   - Look for "Blockers" or "Next Actions" sections in any files read
   - Check for incomplete todo items (items marked with a spinner or "IN PROGRESS")
   - Note any database or pipeline issues mentioned

5. **Present a compact resume summary**:

```
## Session Resume

**Last session:** YYYY-MM-DD
**Source:** [SESSION_STATE / CONTINUITY / REPORT file name]
**Folder:** [path to the session folder]

### Resume Point
[The most critical "what to do next" from the source file]

### Recent Commits
[Last 5-10 commits from git log]

### Uncommitted Changes
[From git status — or "Working tree clean"]

### Pending Items
[Any items marked as in-progress or untested in the source files]

### Active Blockers
[Any blockers found — or "None"]

### Quick Context
[2-3 sentence summary of where the project stands]
```

6. **Ask the user**: "Ready to continue from here, or would you like to focus on something specific?"
