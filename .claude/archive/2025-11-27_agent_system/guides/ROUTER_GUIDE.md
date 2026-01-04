# Router Guide

## What is the Router?

The Router is a lightweight orchestration agent that reads system state and recommends what should happen next. It's the "brain" that helps coordinate the multi-agent workflow.

**Key characteristics:**
- Uses Haiku model (fast, cheap)
- READ-ONLY (cannot modify files)
- Advisory only (recommends but doesn't execute)

## When to Use the Router

Use the Router when you:
- Don't know which agent to invoke next
- Want to check if dependencies are satisfied
- Need a quick status assessment
- Are resuming work after a break

## How to Invoke

Simply ask:
```
Router, what's next?
```

Or more specifically:
```
Router, can we start the analysis phase?
Router, what's blocking progress?
Router, which agent should handle this?
```

## What the Router Reads

The Router examines three files to make decisions:

1. **state.json** - Current queues, tasks, and phase status
2. **task_graph.json** - Pipeline definitions and dependencies
3. **mailbox.jsonl** - Recent events and updates

## Router Recommendations

### Example: No Active Project
```
"No active project found.
- For research: Create ARTIFACTS/RESEARCH_QUESTIONS.md
- For development: Create ARTIFACTS/TASKS.md or invoke project-manager"
```

### Example: Work Ready
```
"Ready to proceed:
Next task: task-003 - Design scraper architecture
Recommendation: Invoke builder-2 to begin."
```

### Example: Blocked
```
"Blocked tasks detected:
- task-005: Waiting on API credentials
Recommendation: Invoke problem-solver to address blockers."
```

### Example: Dependencies Not Met
```
"Cannot start review phase.
Waiting on: implementation phase must complete first.
Current status: 2 tasks still in progress."
```

## Router vs Direct Invocation

| Scenario | Use Router | Use Direct |
|----------|------------|------------|
| Unsure what's next | Yes | No |
| Know exactly what to do | No | Yes |
| Checking dependencies | Yes | No |
| Simple task continuation | No | Yes |
| After long break | Yes | No |

## Pipelines the Router Understands

### Research Pipeline
```
discovery → analysis → synthesis → validation → reporting
(scout)    (analyst)  (synthesizer) (validator) (reporter)
```

### Dev Pipeline
```
planning → implementation → review → done
(PM)       (builders)       (reviewer)
```

### Support Agents
- **problem-solver** - When work is blocked
- **ml-engineer** - For ML/model tasks
- **data-engineer** - For data infrastructure

## Important Notes

1. **Router doesn't execute** - It only recommends. You decide whether to follow.
2. **Router doesn't modify** - It has no write access to any files.
3. **Router is fast** - Uses Haiku, so responses are quick and cheap.
4. **Trust but verify** - Router reads state files, so keep them updated.

## Troubleshooting

**Router gives outdated info:**
- Ensure agents are logging to mailbox.jsonl
- Check that state.json reflects current status

**Router seems confused:**
- Verify task_graph.json is valid JSON
- Check that phase names match between files

**Router recommends wrong agent:**
- Review task assignments in state.json
- Check pipeline definitions in task_graph.json
