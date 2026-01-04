# State Persistence & Token Management Guide

**Last Updated**: 2025-11-27

---

## Your Questions Answered

### ✅ Q1: Can teams see what's been worked on even if the terminal is closed?

**YES!** Teams maintain complete state across terminal sessions through file-based coordination.

### ✅ Q2: Should I close the terminal when reaching 200k tokens and will teams continue work?

**YES!** Close and reopen when you approach 200k tokens. Teams will seamlessly continue work by reading the state files.

---

## How State Persistence Works

### File-Based Coordination

Your teams **never lose state** because they coordinate through files, not through conversation memory:

#### Core State Files

| File | Purpose | Persists? |
|------|---------|-----------|
| `.claude/state/state.json` | Work queues, agent status, research phases, checkpoints | ✅ Yes |
| `.claude/state/mailbox.jsonl` | Complete event log (append-only) | ✅ Yes |
| `.claude/state/task_graph.json` | Pipeline definitions and dependencies | ✅ Yes |
| `.claude/state/checkpoints/` | Checkpoint files for long-running operations | ✅ Yes |
| `docs/decisions/WORKBOARD.md` | Human-readable kanban board | ✅ Yes |
| `ARTIFACTS/TASKS.md` | Dev Team task backlog | ✅ Yes |
| `ARTIFACTS/RESEARCH_QUESTIONS.md` | Research Team questions | ✅ Yes |
| `.claude/state/locks/` | Task locks (prevent conflicts) | ✅ Yes |
| `research_outputs/` | All research deliverables | ✅ Yes |
| `.claude/memory/lessons.md` | Lessons learned across sessions | ✅ Yes |

**These files live on your filesystem** - they survive terminal closes, reboots, everything.

---

## Example: Work Across Terminal Sessions

### Session 1 (Morning)

```bash
# Terminal opens at Business Factory
claude

# You assign work
You: "Dev Team, implement user authentication feature"

# Project-manager breaks down task, adds to state.json
# Builder starts implementation
# ...work in progress...

# Check what's happening
cat .claude/state/mailbox.jsonl | tail -5
```

Output shows:
```json
{"timestamp":"2025-11-15T09:00:00Z","team":"dev","agent":"project-manager","event":"task_planned","task":"auth-001"}
{"timestamp":"2025-11-15T09:05:00Z","team":"dev","agent":"builder","event":"task_claimed","task":"auth-001"}
{"timestamp":"2025-11-15T09:30:00Z","team":"dev","agent":"builder","event":"progress","task":"auth-001","progress":"50%"}
```

### You close terminal (session ends)

**All state saved to files!**

- `state.json` shows builder is working on auth-001
- `mailbox.jsonl` has complete history
- `WORKBOARD.md` shows task in "In Progress"
- Lock file exists: `.claude/state/locks/auth-001.lock`

---

### Session 2 (Afternoon - NEW TERMINAL)

```bash
# Open fresh terminal
claude
📁 Working in Business Factory Research Project

# Check status (without asking any agent)
cat docs/decisions/WORKBOARD.md
```

You see:
```markdown
### In Progress
- auth-001: Implement user authentication (builder, 50% complete)
```

```bash
# Continue work
You: "Builder, continue working on auth-001"

# Builder reads state.json, sees auth-001 is their task
# Builder reads mailbox.jsonl, sees what they already did
# Builder continues from where they left off
# No context lost!
```

---

## How Agents Resume Work

When you reopen a terminal and invoke an agent, here's what happens:

### Step 1: Agent Reads State Files

```python
# What builder does when invoked
1. Read .claude/state/state.json
   → See that auth-001 is in "doing" queue
   → See that builder.current_task = "auth-001"
   → See last_seen timestamp
   → Check for any checkpoints

2. Read .claude/state/mailbox.jsonl
   → Filter for task_id="auth-001"
   → See all previous work logged
   → Understand what's been done

3. Read .claude/state/task_graph.json
   → Check task dependencies
   → See if any prerequisite tasks are complete

4. Check for checkpoint files
   → Read .claude/state/checkpoints/auth-001.json if exists
   → Resume from last checkpoint if task was interrupted

5. Read ARTIFACTS/TASKS.md
   → Understand full task requirements
   → Check acceptance criteria

6. Check filesystem
   → See what code was already written
   → Read test files
   → Understand current state
```

### Step 2: Agent Continues Work

```python
# Builder's logic
if current_task == "auth-001" and status == "doing":
    # Read what I already did from mailbox
    previous_work = parse_mailbox_for_task("auth-001")

    # Check filesystem for actual code
    existing_code = read_files(previous_work.files_modified)

    # Continue from where I left off
    continue_implementation(existing_code)
```

**The agent has perfect memory via files!**

---

## Token Management Strategy

### The 200k Token Limit

You (the orchestrating Claude) have a 200k token context limit. Agents invoked via Task tool have their own separate contexts.

### When to Close & Reopen Terminal

#### ⚠️ Close Terminal When:

- **Approaching 200k tokens** (~180k used is a good threshold)
- **Session feels "heavy"** (lots of back-and-forth)
- **Starting a new phase** (finished research, starting dev)
- **Natural breakpoint** (end of day, milestone complete)

#### ✅ Continue Current Session When:

- You've used <100k tokens
- Quick follow-up questions
- Checking status
- Small corrections

### How to Check Token Usage

You can see token usage in the system warnings I receive. Example:
```
Token usage: 89566/200000; 110434 remaining
```

When remaining drops below ~50k, consider starting fresh.

---

## Best Practice Workflow

### Multi-Day Projects

**Day 1:**
```bash
# Fresh terminal
claude

# Assign work
"Research Team, investigate grant matching algorithms"
"Dev Team, set up project structure"

# Work happens...
# Agents log to mailbox.jsonl
# State updates in state.json

# Before closing, check status
cat docs/decisions/WORKBOARD.md
cat .claude/state/mailbox.jsonl | tail -20

# Close terminal when done
exit
```

**Day 2:**
```bash
# Fresh terminal - NO STATE LOST
claude

# Check what happened yesterday
cat docs/decisions/WORKBOARD.md
cat .claude/state/mailbox.jsonl | tail -30

# Continue work
"Builder, continue with yesterday's tasks"
"Research Team, finish the analysis phase"

# Agents read mailbox.jsonl and state.json
# They know exactly where they left off!
```

**Day 3:**
```bash
# Same pattern - infinite continuity
claude

# Research → Dev handoff
cat research_outputs/final_report.md
cat ARTIFACTS/IMPLEMENTATION_BRIEF.md

"Dev Team, implement features from implementation brief"
```

---

## Monitoring Work Progress

### Real-Time Status Check

```bash
# Human-readable status
cat docs/decisions/WORKBOARD.md

# Detailed event log (last 20 events)
cat .claude/state/mailbox.jsonl | tail -20

# Current work queues
cat .claude/state/state.json | grep -A 10 "queues"

# Agent status
cat .claude/state/state.json | grep -A 50 "agent_status"

# Research pipeline status
cat .claude/state/state.json | grep -A 30 "research_state"
```

### Example: Checking After Terminal Reopen

```bash
# What did teams do while I was away?
cat .claude/state/mailbox.jsonl | tail -50

# Output shows complete history:
{"timestamp":"2025-11-15T09:00:00Z","team":"dev","agent":"builder","event":"task_claimed","task":"auth-001"}
{"timestamp":"2025-11-15T09:45:00Z","team":"dev","agent":"builder","event":"task_completed","task":"auth-001"}
{"timestamp":"2025-11-15T09:50:00Z","team":"dev","agent":"reviewer","event":"review_started","task":"auth-001"}
{"timestamp":"2025-11-15T10:15:00Z","team":"dev","agent":"reviewer","event":"approved","task":"auth-001"}
{"timestamp":"2025-11-15T10:20:00Z","team":"research","agent":"scout","event":"discovery_complete","sources":25}
{"timestamp":"2025-11-15T13:00:00Z","team":"research","agent":"analyst","event":"analysis_complete"}
```

**You can see everything that happened!**

---

## Example: 3-Terminal Session Project

### Terminal Session 1 (2 hours, ~60k tokens)

```bash
You: "Research Team, investigate semantic search for grant matching"
You: "Dev Team, set up database schema"

# Check logs
mailbox.jsonl shows:
- Research Team: scout gathering data
- Dev Team: data-engineer designing schema
```

### Close & Reopen (Token Reset)

All work saved! Mailbox has complete record.

### Terminal Session 2 (3 hours, ~90k tokens)

```bash
# Agents resume automatically
cat mailbox.jsonl | tail -20  # See what was done

You: "Research Team, continue analysis phase"
You: "Builder, implement API endpoints"

# More work...
```

### Close & Reopen (Token Reset Again)

### Terminal Session 3 (2 hours, ~50k tokens)

```bash
# Complete continuity
cat docs/decisions/WORKBOARD.md

You: "Reporter, write final research report"
You: "Dev Team, integrate research recommendations"

# Project completes!
```

**3 terminal sessions, zero state loss, infinite project continuity!**

---

## Key Insights

### 🎯 Agents Have Perfect Memory

- They read `mailbox.jsonl` for history
- They read `state.json` for current state
- They read filesystem for actual code/data
- Terminal closes don't affect them

### 🎯 You (Orchestrator) Need Token Management

- Your context has 200k limit
- Close & reopen when approaching limit
- Agents don't care - they read files

### 🎯 State Files Are Source of Truth

- Not conversation history
- Not Claude's memory
- **Files on disk**

---

## Summary

### ✅ Can teams see work history after terminal close?

**YES!** Complete history in:
- `mailbox.jsonl` (every event)
- `state.json` (current state)
- `task_graph.json` (pipeline definitions)
- `checkpoints/` (recovery points for long operations)
- `WORKBOARD.md` (human-readable)
- `memory/lessons.md` (lessons learned)

### ✅ Should I close terminal at 200k tokens?

**YES!** When you approach 200k tokens (~180k used):
1. Check status: `cat docs/decisions/WORKBOARD.md`
2. Save checkpoint if needed: Long-running operations auto-checkpoint
3. Close terminal: `exit`
4. Reopen: `claude` (auto-navigates to Business Factory)
5. Continue work: Teams read state files and resume from checkpoints

### ✅ Will work continue seamlessly?

**YES!** Agents read state files every time they're invoked:
- See what was done (mailbox.jsonl)
- See what's in progress (state.json)
- Check task dependencies (task_graph.json)
- Resume from checkpoints if interrupted
- Continue from exact point they left off
- Apply lessons learned from previous sessions

---

## You're Ready!

Your teams have **perfect state persistence**. Close and reopen terminals as much as you want. Work never stops, context never loses.

**Try it**:
1. Assign a task
2. Let it start
3. Close terminal
4. Reopen
5. Check `mailbox.jsonl` - it's all there!
