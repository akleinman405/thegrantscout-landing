# Phase 1: Foundation

## Objective

Set up the infrastructure for the enhanced multi-agent system. This creates the folder structure, adds token tracking to state management, creates a simple status command, and establishes the memory system skeleton.

No agent behavior changes yet - just laying groundwork.

---

## Context

You're working in a multi-agent system located at:
```
C:\Business Factory (Research) 11-1-2025\.claude\
```

The system has:
- 11 agent definition files (scout.md, analyst.md, builder.md, etc.)
- State files: `state/state.json` and `state/mailbox.jsonl`
- Guide documents in the root .claude folder

Read the existing files first to understand the current structure before making changes.

---

## Tasks

### 1. Create Memory Folder Structure

Create this directory structure:
```
.claude/
├── memory/
│   ├── lessons.md
│   ├── patterns/
│   │   └── .gitkeep
│   └── projects/
│       └── .gitkeep
```

The `lessons.md` file should be a simple template:
```markdown
# Team Lessons Learned

## How to Use This File
After each project, add lessons below. Format:
- **Date**: What we learned (which project, which agent)

---

## Lessons

(None yet - add after completing projects)
```

### 2. Create Commands Folder with Status Command

Create:
```
.claude/
├── commands/
│   └── status.md
```

The `status.md` command should:
- Read state.json and summarize current project status
- Read mailbox.jsonl and show last 5 events
- List which agents are active/inactive
- Show current phase and progress

Keep the command under 50 lines. It should output a clean, readable status report.

### 3. Add Token Tracking to State Schema

Modify `state/state.json` to include a token tracking section. Add this field at the root level:

```json
{
  "token_tracking": {
    "current_session": {
      "started_at": null,
      "agents_invoked": []
    },
    "project_totals": {
      "estimated_input_tokens": 0,
      "estimated_output_tokens": 0
    }
  },
  ... existing fields ...
}
```

Preserve all existing data in state.json. Just add the new field.

### 4. Create Scripts Folder

Create:
```
.claude/
├── scripts/
│   └── .gitkeep
```

This will hold utility scripts in later phases.

---

## Constraints

- Do NOT modify any agent .md files in this phase
- Do NOT delete or overwrite existing state data
- Preserve all existing mailbox.jsonl entries
- All new files should use UTF-8 encoding
- Keep lessons.md simple - don't over-engineer it

---

## Success Criteria

After completion, verify:

- [ ] `.claude/memory/` folder exists
- [ ] `.claude/memory/lessons.md` exists and contains the template
- [ ] `.claude/memory/patterns/` folder exists
- [ ] `.claude/memory/projects/` folder exists
- [ ] `.claude/commands/` folder exists
- [ ] `.claude/commands/status.md` exists and is a valid command
- [ ] `.claude/scripts/` folder exists
- [ ] `state.json` contains `token_tracking` field
- [ ] `state.json` is valid JSON (no syntax errors)
- [ ] All existing state.json data is preserved

---

## Validation

After completing all tasks, run these checks:

**PowerShell:**
```powershell
# Check folder structure exists
Get-ChildItem .claude\memory\
Get-ChildItem .claude\commands\
Get-ChildItem .claude\scripts\

# Validate state.json is valid JSON
Get-Content .claude\state\state.json | ConvertFrom-Json
# If no error, JSON is valid

# Check token_tracking field exists
Select-String -Path .claude\state\state.json -Pattern "token_tracking"
```

**Or Git Bash:**
```bash
ls -la .claude/memory/
ls -la .claude/commands/
cat .claude/state/state.json | python -m json.tool
grep "token_tracking" .claude/state/state.json
```

Then manually test:
```
You: /status
Expected: A readable summary of current project state, recent events, and agent status
```

---

## Rollback

If something goes wrong:

**PowerShell:**
```powershell
git checkout -- .claude\state\state.json
Remove-Item -Recurse -Force .claude\memory\
Remove-Item -Recurse -Force .claude\commands\
Remove-Item -Recurse -Force .claude\scripts\
```

**Or Git Bash:**
```bash
git checkout -- .claude/state/state.json
rm -rf .claude/memory/
rm -rf .claude/commands/
rm -rf .claude/scripts/
```

---

## Next Phase

Once validated, proceed to Phase 2: The Brain (Router + Task Graph)
