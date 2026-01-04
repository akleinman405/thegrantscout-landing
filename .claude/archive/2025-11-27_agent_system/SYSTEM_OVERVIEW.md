# Multi-Agent System Overview

**Last Updated**: 2025-11-27
**System Status**: Production-Ready
**Total Agents**: 16

---

## Quick Reference

### Check System Status
```bash
/status                                    # Full status report
cat .claude/state/mailbox.jsonl | tail -20 # Recent events
cat .claude/state/state.json               # Current state
```

### Invoke Teams
```bash
"Dev Team, implement [feature]"            # Dev Team coordinates
"Research Team, investigate [topic]"       # Research pipeline starts
"Router, what's next?"                     # Get workflow guidance
```

---

## System Architecture

### Teams & Agents

```
┌─────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   ORCHESTRATION │    │           DEV TEAM (9)          │ │
│  │                 │    │                                 │ │
│  │  router (haiku) │───▶│  project-manager    (sonnet)   │ │
│  │                 │    │  builder            (sonnet)   │ │
│  └─────────────────┘    │  builder-1          (sonnet)   │ │
│                         │  builder-2          (sonnet)   │ │
│  ┌─────────────────┐    │  builder-3          (sonnet)   │ │
│  │   SPECIALIZED   │    │  reviewer           (sonnet)   │ │
│  │                 │    │  problem-solver     (sonnet)   │ │
│  │  cdfi-extractor │    │  ml-engineer        (sonnet)   │ │
│  │    (sonnet)     │    │  data-engineer      (sonnet)   │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   RESEARCH TEAM (5)                      │ │
│  │                                                          │ │
│  │  scout (haiku) → analyst (sonnet) → synthesizer (sonnet)│ │
│  │                           ↓                              │ │
│  │              validator (sonnet) → reporter (haiku)       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Agent Summary Table

| Agent | Team | Model | Primary Function |
|-------|------|-------|------------------|
| **router** | Orchestration | Haiku | Workflow decisions, routing |
| **project-manager** | Dev | Sonnet | Task planning, coordination |
| **builder** | Dev | Sonnet | Feature implementation |
| **builder-1** | Dev | Sonnet | Parallel development |
| **builder-2** | Dev | Sonnet | Parallel development |
| **builder-3** | Dev | Sonnet | Parallel development |
| **reviewer** | Dev | Sonnet | Code review, quality |
| **problem-solver** | Dev | Sonnet | Debugging, architecture |
| **ml-engineer** | Dev | Sonnet | ML/AI implementation |
| **data-engineer** | Dev | Sonnet | Data pipelines, databases |
| **scout** | Research | Haiku | Data discovery |
| **analyst** | Research | Sonnet | Statistical analysis |
| **synthesizer** | Research | Sonnet | Strategic insights |
| **validator** | Research | Sonnet | Quality assurance |
| **reporter** | Research | Haiku | Documentation |
| **cdfi-extractor** | Specialized | Sonnet | CDFI data extraction |

---

## Workflows

### Dev Team Pipeline
```
planning (PM) → implementation (builders) → review (reviewer) → done
```

### Research Team Pipeline
```
discovery (scout) → analysis (analyst) → synthesis (synthesizer)
                           ↓
               validation (validator) → reporting (reporter)
```

### Cross-Team Handoff
```
Research Team completes → creates IMPLEMENTATION_BRIEF.md → Dev Team builds
```

---

## Infrastructure

### Directory Structure

```
.claude/
├── agents/                    # 16 agent definitions
│   ├── router.md             # Orchestration (haiku)
│   ├── builder.md            # Primary developer
│   ├── builder-1.md          # Parallel builder
│   ├── builder-2.md          # Parallel builder
│   ├── builder-3.md          # Parallel builder
│   ├── reviewer.md           # Code reviewer
│   ├── problem-solver.md     # Debugger
│   ├── project-manager.md    # Coordinator
│   ├── ml-engineer.md        # ML specialist
│   ├── data-engineer.md      # Data specialist
│   ├── scout.md              # Research discovery (haiku)
│   ├── analyst.md            # Statistical analysis
│   ├── synthesizer.md        # Insights
│   ├── validator.md          # QA
│   ├── reporter.md           # Documentation (haiku)
│   └── cdfi-extractor.md     # Specialized extraction
│
├── state/
│   ├── state.json            # Queues, tasks, phases
│   ├── mailbox.jsonl         # Event log
│   ├── task_graph.json       # Pipeline definitions
│   ├── checkpoints/          # Checkpoint files
│   └── mailbox_archive/      # Rotated logs
│
├── memory/
│   ├── lessons.md            # Team lessons learned
│   ├── patterns/             # Reusable patterns
│   └── projects/             # Project-specific memory
│
├── commands/
│   └── status.md             # /status command
│
├── scripts/
│   ├── rotate_mailbox.sh     # Linux/Mac rotation
│   └── rotate_mailbox.ps1    # Windows rotation
│
├── templates/
│   └── phase_summary_template.md
│
├── guides/
│   ├── ROUTER_GUIDE.md       # Router usage
│   └── RECOVERY_GUIDE.md     # Error recovery
│
└── [Documentation Files]
    ├── SYSTEM_OVERVIEW.md         # This file
    ├── TEAM_COLLABORATION_GUIDE.md
    ├── TEAM_INVOCATION_GUIDE.md
    ├── MULTI_BUILDER_GUIDE.md
    ├── CONTEXT_TRACKING_GUIDE.md
    ├── STATE_PERSISTENCE_GUIDE.md
    └── SESSION_STATUS.md
```

---

## Key Capabilities

### 1. Model Tiering (Cost Optimization)
- **Haiku** (fast, cheap): router, scout, reporter
- **Sonnet** (balanced): All other agents
- **Result**: ~60% cost reduction for discovery/reporting tasks

### 2. Checkpoint Protocol (Reliability)
For long-running operations (>10 items):
- Save checkpoint every 10 items
- Resume from last checkpoint on failure
- Files stored in `.claude/state/checkpoints/`

### 3. Three-Tier Error Handling
| Tier | Errors | Action |
|------|--------|--------|
| 1 | Network, rate limit, 5xx | Auto-retry (max 3) |
| 2 | Single item fails | Skip, log, continue |
| 3 | Auth fail, >20% failing | Stop, escalate |

### 4. Handoff Protocol
- Each phase creates `phase_summary.md` (<500 words)
- Next agent reads summary before starting
- Prevents context bloat between agents

### 5. Permission Scoping
Each agent has only the tools they need:
- **router**: Read only
- **validator**: Read, WebSearch, WebFetch (no Write)
- **reviewer**: Read, Grep, Glob, Bash (no Edit)
- **builders**: Full dev access

### 6. Dependency Tracking
`task_graph.json` defines:
- Pipeline phases and order
- Which agent handles each phase
- What outputs each phase produces
- What dependencies must complete first

---

## Quick Command Reference

### Status & Monitoring
```bash
/status                              # Project status report
Router, what's next?                 # Get workflow guidance
cat .claude/state/mailbox.jsonl      # View event log
```

### Dev Team Commands
```bash
"Dev Team, implement [feature]"
"Builder, [specific task]"
"Builder-1, work on [component A]"
"Builder-2, work on [component B]"
"Reviewer, review [code]"
"Problem-solver, debug [issue]"
"Project-manager, create sprint plan"
```

### Research Team Commands
```bash
"Research Team, investigate [topic]"
"Scout, find data on [subject]"
"Analyst, analyze [data]"
"Synthesizer, create recommendations"
"Validator, verify [findings]"
"Reporter, write report"
```

### Recovery Commands
```bash
"Scout, resume from checkpoint [id]"
cat .claude/state/checkpoints/       # List checkpoints
.claude/scripts/rotate_mailbox.sh    # Rotate mailbox
```

---

## Best Practices

### Do
- Use `/status` to check current state
- Let project-manager coordinate multi-task work
- Use parallel builders for independent features
- Check mailbox for recent events
- Use Router when unsure what to do next

### Don't
- Assign same file to multiple builders
- Skip reviews for parallel work
- Ignore Tier 3 escalations
- Forget phase summaries on handoffs

---

## Enhancement History

| Phase | Capability | Date |
|-------|------------|------|
| 1. Foundation | Memory, /status, token tracking | 2025-11-27 |
| 2. Brain | Router, task graph, dependencies | 2025-11-27 |
| 3. Communication | Handoffs, summaries, rotation | 2025-11-27 |
| 4. Optimization | Model tiering, permissions | 2025-11-27 |
| 5. Reliability | Checkpoints, error tiers | 2025-11-27 |

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `TEAM_COLLABORATION_GUIDE.md` | Cross-team coordination |
| `TEAM_INVOCATION_GUIDE.md` | How to invoke agents |
| `MULTI_BUILDER_GUIDE.md` | Parallel development |
| `CONTEXT_TRACKING_GUIDE.md` | State persistence |
| `STATE_PERSISTENCE_GUIDE.md` | Token management |
| `guides/ROUTER_GUIDE.md` | Router usage |
| `guides/RECOVERY_GUIDE.md` | Error recovery |

---

## System Metrics

From Integration Test (2025-11-27):

| Metric | Value |
|--------|-------|
| Total Agents | 16 |
| Dev Team Workflow | PM → Builder → Reviewer → Done ✓ |
| Research Pipeline | Scout → Analyst → Synthesizer → Validator → Reporter ✓ |
| Mailbox Events Logged | All transitions captured |
| State Updates | Correct at each phase |
| Checkpoint System | Operational |
| Error Handling | 3 tiers implemented |

**System Status: Production-Ready**
