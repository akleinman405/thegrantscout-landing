# Phase 2: The Brain (Router + Task Graph)

## Objective

Create the orchestration layer that's currently missing. Right now, the human manually decides which agent to invoke next. This phase adds:

1. A **Router agent** - lightweight orchestrator that reads state and recommends next action
2. A **Task Graph** - explicit dependency definitions so agents know what must complete before they can start

This is the most important phase. The Router becomes the "brain" of the system.

---

## Context

The system has two teams with implicit pipelines:

**Research Team Pipeline**:
```
Scout → Analyst → Synthesizer → Validator → Reporter
```

**Dev Team Pipeline**:
```
Project-Manager → Builder(s) → Reviewer → Done
                      ↑
              Problem-Solver (if blocked)
```

These pipelines exist in documentation but aren't enforced. Agents don't know what depends on what.

---

## Tasks

### 1. Create the Router Agent

Create `.claude/agents/router.md`:

**Requirements**:
- Model: `haiku` (routing decisions are simple)
- Tools: `Read` only (Router doesn't modify anything)
- Size: Under 4KB (keep it lightweight)

**Core Responsibilities**:
1. Read `state.json` to understand current project status
2. Read `task_graph.json` to understand dependencies
3. Determine which phase/task should run next
4. Check if dependencies are satisfied before recommending
5. Output a clear recommendation: "Next: invoke [agent] for [phase]"

**Router Logic**:
```
IF no active project:
  → "No active project. Create ARTIFACTS/RESEARCH_QUESTIONS.md or ARTIFACTS/TASKS.md to start."

IF current_phase is "complete":
  → "Project complete. Run /status for summary."

IF current_phase has unsatisfied dependencies:
  → "Waiting on: [list dependencies]. Cannot proceed."

IF current_phase is "pending" and dependencies satisfied:
  → "Next: invoke [appropriate agent] to start [phase]"

IF current_phase is "in_progress":
  → "[Agent] is working on [phase]. Check mailbox for updates."

IF current_phase is "blocked":
  → "Blocked: [reason]. Invoke problem-solver or address blocker."
```

**Do NOT give Router any capabilities to**:
- Invoke other agents directly
- Modify files
- Make decisions about task content (only task sequencing)

### 2. Create the Task Graph

Create `.claude/state/task_graph.json`:

```json
{
  "version": "1.0",
  "description": "Defines task dependencies for Research and Dev teams",
  
  "research_pipeline": {
    "discovery": {
      "agent": "scout",
      "requires": [],
      "produces": ["research_outputs/01_scout/"],
      "description": "Gather data sources and raw information"
    },
    "analysis": {
      "agent": "analyst",
      "requires": ["discovery"],
      "produces": ["research_outputs/02_analyst/"],
      "description": "Statistical analysis and modeling"
    },
    "synthesis": {
      "agent": "synthesizer",
      "requires": ["analysis"],
      "produces": ["research_outputs/03_synthesizer/"],
      "description": "Strategic insights and recommendations"
    },
    "validation": {
      "agent": "validator",
      "requires": ["synthesis"],
      "produces": ["research_outputs/04_validator/"],
      "description": "Fact-checking and quality assurance"
    },
    "reporting": {
      "agent": "reporter",
      "requires": ["validation"],
      "produces": ["research_outputs/05_reporter/"],
      "description": "Final documentation and deliverables"
    }
  },
  
  "dev_pipeline": {
    "planning": {
      "agent": "project-manager",
      "requires": [],
      "produces": ["ARTIFACTS/TASKS.md", "docs/decisions/WORKBOARD.md"],
      "description": "Break down work into tasks"
    },
    "implementation": {
      "agent": "builder",
      "requires": ["planning"],
      "produces": ["src/", "tests/"],
      "parallel_allowed": true,
      "description": "Build features and write tests"
    },
    "review": {
      "agent": "reviewer",
      "requires": ["implementation"],
      "produces": ["review approved"],
      "description": "Code review and quality check"
    }
  },
  
  "support_agents": {
    "problem-solver": {
      "trigger": "blocked status in any phase",
      "description": "Debug issues and unblock work"
    },
    "ml-engineer": {
      "trigger": "task tagged with 'ml' or 'model'",
      "description": "Machine learning specific work"
    },
    "data-engineer": {
      "trigger": "task tagged with 'data' or 'pipeline'",
      "description": "Data infrastructure work"
    }
  }
}
```

### 3. Update State.json Schema

Add a `dependencies_satisfied` helper field to each phase in state.json. Example:

```json
{
  "phases": {
    "analysis": {
      "status": "pending",
      "dependencies_satisfied": false,
      "waiting_on": ["discovery"]
    }
  }
}
```

The Router will use this to quickly check what can run.

### 4. Create Router Guide

Create `.claude/guides/ROUTER_GUIDE.md`:

Explain:
- What the Router does
- How to invoke it ("Router, what's next?")
- How it reads task_graph.json
- When to use Router vs. directly invoking agents
- Examples of Router recommendations

Keep under 2 pages.

---

## Constraints

- Router must be READ-ONLY (no Write, Edit, or Bash tools)
- Router must use Haiku model (fast, cheap)
- Router must not invoke other agents (only recommends)
- Task graph must be valid JSON
- Don't modify existing agent files in this phase
- Preserve all existing state.json data

---

## Success Criteria

After completion, verify:

- [ ] `.claude/agents/router.md` exists
- [ ] Router uses `model: haiku`
- [ ] Router only has `Read` in tools list
- [ ] Router prompt is under 4KB
- [ ] `.claude/state/task_graph.json` exists
- [ ] task_graph.json is valid JSON
- [ ] task_graph.json contains both research_pipeline and dev_pipeline
- [ ] `.claude/guides/ROUTER_GUIDE.md` exists
- [ ] state.json schema supports dependency tracking

---

## Validation

After completing all tasks:

**PowerShell:**
```powershell
# Check Router exists
Get-Item .claude\agents\router.md

# Validate task_graph.json
Get-Content .claude\state\task_graph.json | ConvertFrom-Json

# Check Router file size (should be under 4KB)
(Get-Item .claude\agents\router.md).Length

# Check Router has correct model
Select-String -Path .claude\agents\router.md -Pattern "model: haiku"

# Check Router tools
Select-String -Path .claude\agents\router.md -Pattern "^tools:"
```

**Or Git Bash:**
```bash
ls -la .claude/agents/router.md
cat .claude/state/task_graph.json | python -m json.tool
wc -c .claude/agents/router.md
grep "model: haiku" .claude/agents/router.md
grep "tools:" .claude/agents/router.md
```

Then manually test:
```
You: "Router, what should happen next?"

Expected (if no active project): 
"No active project found. To start a research project, create ARTIFACTS/RESEARCH_QUESTIONS.md. To start a dev project, create ARTIFACTS/TASKS.md."

Expected (if project in progress):
"Current phase: [phase]. Status: [status]. Next: invoke [agent] to [action]."
```

Test dependency checking:
```
You: "Router, can we start the analysis phase?"

Expected (if discovery not complete):
"Cannot start analysis. Waiting on: discovery phase must complete first."

Expected (if discovery complete):
"Yes, analysis phase is ready. Invoke Analyst to begin."
```

---

## Rollback

If something goes wrong:

**PowerShell:**
```powershell
Remove-Item .claude\agents\router.md
Remove-Item .claude\state\task_graph.json
Remove-Item .claude\guides\ROUTER_GUIDE.md
git checkout -- .claude\state\state.json
```

**Or Git Bash:**
```bash
rm .claude/agents/router.md
rm .claude/state/task_graph.json
rm .claude/guides/ROUTER_GUIDE.md
git checkout -- .claude/state/state.json
```

---

## Next Phase

Once validated, proceed to Phase 3: Communication (Handoffs + Mailbox)
