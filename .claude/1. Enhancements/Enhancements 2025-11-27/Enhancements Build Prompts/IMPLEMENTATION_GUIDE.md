# Multi-Agent Team Enhancement: Implementation Guide

## Overview

This guide orchestrates the implementation of 5 phases to enhance your multi-agent system. Each phase has its own prompt file for Claude Code CLI.

**Total Estimated Time**: 3-4 hours across all phases  
**Recommended Approach**: One phase per session, validate before proceeding

---

## Phase Files

| Phase | File | Focus | Time |
|-------|------|-------|------|
| 1 | `phase_1_foundation.md` | Folders, token tracking, /status | 15-20 min |
| 2 | `phase_2_router.md` | Router agent, task graph | 30-45 min |
| 3 | `phase_3_communication.md` | Handoffs, mailbox rotation | 45-60 min |
| 4 | `phase_4_optimization.md` | Model tiering, permissions | 30 min |
| 5 | `phase_5_reliability.md` | Checkpoints, error handling | 45-60 min |

---

## Before You Start

### Prerequisites

1. **Git initialized** in your project folder
   ```powershell
   cd "C:\Business Factory (Research) 11-1-2025"
   git status  # Should show a repo
   ```

2. **Create a backup branch**
   ```powershell
   git checkout -b pre-enhancement-backup
   git add -A
   git commit -m "Backup before multi-agent enhancement"
   git checkout main  # or master
   ```

3. **Claude Code CLI installed and working**
   ```powershell
   claude --version
   ```

### Windows Notes

- Use **PowerShell** or **Git Bash** (not CMD) for best compatibility
- Path separators: Claude Code CLI handles both `/` and `\`
- Shell scripts (`.sh`) will need Git Bash or WSL to run
- Alternatively, Claude can create `.ps1` PowerShell versions

---

## How to Run Each Phase

### Step 1: Open the Phase Prompt

Open the phase file (e.g., `phase_1_foundation.md`) in a text editor or viewer.

### Step 2: Start Claude Code CLI

```powershell
cd "C:\Business Factory (Research) 11-1-2025\.claude"
claude
```

### Step 3: Give Claude the Phase Prompt

Copy the entire contents of the phase file and paste it into Claude Code CLI.

Or reference the file:
```
Please read and implement the instructions in: [path to phase file]
```

### Step 4: Let Claude Work

Claude Code CLI will:
- Read existing files to understand context
- Create new files and folders
- Modify existing files as specified
- Report what it did

### Step 5: Run Validation

Each phase includes validation commands. Run them:
```bash
# Example for Phase 1
ls -la .claude/memory/
cat .claude/state/state.json | python -m json.tool
```

### Step 6: Manual Testing

Each phase includes manual tests. Run them:
```
You: "/status"
Expected: [see phase file for expected output]
```

### Step 7: Commit if Successful

```bash
git add -A
git commit -m "Phase N: [description] complete"
```

### Step 8: Proceed to Next Phase

Only after validation passes!

---

## Phase-by-Phase Checklist

### Phase 1: Foundation
```
□ Paste phase_1_foundation.md into Claude Code CLI
□ Claude creates folder structure
□ Run validation commands
□ Test /status command works
□ git commit -m "Phase 1: Foundation complete"
```

### Phase 2: The Brain
```
□ Paste phase_2_router.md into Claude Code CLI
□ Claude creates router.md and task_graph.json
□ Run validation commands
□ Test: "Router, what's next?"
□ git commit -m "Phase 2: Router and task graph complete"
```

### Phase 3: Communication
```
□ Paste phase_3_communication.md into Claude Code CLI
□ Claude adds Handoff Protocol to all agents
□ Claude creates mailbox rotation script
□ Run validation commands
□ Test phase summary generation
□ git commit -m "Phase 3: Communication protocols complete"
```

### Phase 4: Optimization
```
□ Paste phase_4_optimization.md into Claude Code CLI
□ Claude updates model and tools in all agents
□ Run validation commands
□ Test Haiku agents work
□ Test permission restrictions work
□ git commit -m "Phase 4: Model tiering and permissions complete"
```

### Phase 5: Reliability
```
□ Paste phase_5_reliability.md into Claude Code CLI
□ Claude adds checkpoint and error handling protocols
□ Run validation commands
□ Test checkpoint creation
□ Test checkpoint resume
□ git commit -m "Phase 5: Reliability complete"
```

---

## Troubleshooting

### Claude Code CLI Doesn't Understand

If Claude seems confused:
1. Make sure you're in the `.claude` directory
2. Tell Claude to read existing files first:
   ```
   Before making changes, please read:
   - state/state.json
   - agents/scout.md
   - TEAM_COLLABORATION_GUIDE.md
   ```

### Validation Fails

1. Check the specific error
2. Ask Claude to fix it:
   ```
   The validation check for [X] failed because [Y]. Please fix it.
   ```
3. Re-run validation

### Need to Rollback

Each phase has rollback commands. Example:
```bash
git checkout -- .claude/agents/
rm -rf .claude/memory/
```

Or rollback entire phase:
```bash
git checkout HEAD~1 -- .claude/
```

### Something Broke That Worked Before

```bash
# See what changed
git diff HEAD~1 .claude/

# Restore specific file
git checkout HEAD~1 -- .claude/agents/scout.md
```

---

## After All Phases Complete

### Verify Everything

```bash
# Folder structure
ls -la .claude/memory/
ls -la .claude/commands/
ls -la .claude/state/checkpoints/
ls -la .claude/templates/
ls -la .claude/scripts/

# All agents have new sections
for agent in .claude/agents/*.md; do
  echo "=== $agent ==="
  grep -c "Handoff Protocol" "$agent"
  grep -c "Error Handling" "$agent"
  grep "^model:" "$agent"
  grep "^tools:" "$agent"
done

# Router exists and is correct
cat .claude/agents/router.md | head -20

# Task graph is valid
cat .claude/state/task_graph.json | python -m json.tool | head -30
```

### Run Full System Test

```
You: "Router, what's the current state and what should happen next?"

You: "Scout, do a small test discovery and create a phase summary"

You: "Validator, try to write a file" (should fail - no Write permission)

You: "/status"
```

### Final Commit

```bash
git add -A
git commit -m "Multi-agent enhancement complete: all 5 phases implemented"
git tag v2.0-enhanced
```

---

## What You Now Have

After all 5 phases:

| Component | What It Does |
|-----------|--------------|
| **Router Agent** | Orchestrates workflow, checks dependencies |
| **Task Graph** | Explicit dependencies between phases |
| **Phase Summaries** | 500-word handoffs between agents |
| **Mailbox Rotation** | Bounded event log with archival |
| **Model Tiering** | Haiku for simple, Sonnet for complex |
| **Permission Scoping** | Each agent has minimal required tools |
| **Checkpoints** | Resume from failure, don't restart |
| **Error Handling** | Auto-retry, skip, or escalate |
| **Recovery Guide** | Clear process to resume work |
| **Token Tracking** | Visibility into costs |
| **Lessons File** | Simple institutional memory |
| **/status Command** | Quick system status check |

---

## Next Steps (After Enhancement)

1. **Run a real project** through the enhanced system
2. **Update lessons.md** after completion
3. **Monitor token usage** to validate cost savings
4. **Refine Router** based on actual usage patterns
5. **Add patterns** to memory/patterns/ as you discover them

---

Good luck! 🚀
