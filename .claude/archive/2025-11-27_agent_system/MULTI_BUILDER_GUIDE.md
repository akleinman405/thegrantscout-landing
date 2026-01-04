# Multi-Builder Parallel Development Guide

**Last Updated**: 2025-11-27
**Dev Team Size**: 9 agents (4 builders + 5 specialists)
**Total System**: 16 agents across all teams

---

## Overview

You now have **4 builder agents** that can work simultaneously on different parts of your project:
- **builder** - Original builder for general tasks
- **builder-1** - Parallel builder #1
- **builder-2** - Parallel builder #2
- **builder-3** - Parallel builder #3

All builders have equal capabilities and can work on any type of development task.

---

## How It Works

### Project-Manager Coordinates Multiple Builders

**Project-manager's enhanced role**:
1. Break down epics into 4+ parallel tasks
2. Assign tasks to builder, builder-1, builder-2, builder-3 strategically
3. Coordinate dependencies (builder-2 waits for builder-1's schema)
4. Route all outputs to reviewer
5. Monitor mailbox for conflicts or blockers
6. Can escalate to router agent for complex workflow decisions

### Example: Grant Matching MVP (4x Faster)

**Traditional Sequential** (slow):
```bash
Week 1: Builder does API endpoints
Week 2: Builder does matching algorithm
Week 3: Builder does data layer
Week 4: Builder does frontend
```
**Total: 4 weeks**

**Multi-Builder Parallel** (fast):
```bash
Week 1 (all simultaneous):
- builder: API endpoints + authentication
- builder-1: Matching algorithm + scoring
- builder-2: Data layer + queries
- builder-3: Frontend components

Week 2 (integration):
- builder: Integrate all 4 components
- reviewer: Review all code
```
**Total: 2 weeks** (50% faster!)

---

## When to Use Multiple Builders

### ✅ Use Multiple Builders When:

**1. Parallelizable Features**
```bash
# Good: Independent features
"builder-1, implement user authentication"
"builder-2, implement search functionality"
"builder-3, implement reporting module"
```

**2. Multi-Component Features**
```bash
# Good: One feature, multiple layers
"builder-1, build API layer for grant matching"
"builder-2, build business logic for grant matching"
"builder-3, build database layer for grant matching"
```

**3. Multiple Ideas/Projects**
```bash
# Good: Different projects
"builder-1, work on Idea 062 (Grant Matching)"
"builder-2, work on Idea 099 (Something Else)"
"builder-3, work on Idea 105 (Another Project)"
```

### ❌ Don't Use Multiple Builders When:

**1. Tightly Coupled Work**
```bash
# Bad: builder-2 depends on builder-1's output
"builder-1, create User model"
"builder-2, create UserController (uses User model)"
# Sequential dependency = not parallelizable
```

**2. Small, Simple Tasks**
```bash
# Bad: Overkill for simple work
"builder-1, fix a typo in README.md"
# Just use: "builder, fix typo" (original single builder)
```

**3. Learning/Exploration Phase**
```bash
# Bad: Need deep understanding first
"builder-1, explore codebase and suggest refactoring"
# Use single builder or problem-solver for exploration
```

---

## Coordination Mechanisms

### 1. Task Assignment Strategy

**Project-manager assigns based on**:

**Complexity Balance**:
```
builder-1: Complex task (authentication system)
builder-2: Medium task (search API)
builder-3: Simple task (logging module)
```

**Domain Separation**:
```
builder-1: Frontend components
builder-2: Backend API
builder-3: Database migrations
```

**Project Separation**:
```
builder-1: Idea 062 features
builder-2: Idea 099 features
builder-3: Idea 105 features
```

### 2. Conflict Avoidance

**File-Level Locking**:
```json
// .claude/state/locks/
task-001-builder-1.lock  // builder-1 owns this task
task-002-builder-2.lock  // builder-2 owns this task
```

**Subdirectory Isolation**:
```json
{
  "task_contexts": {
    "task-001": {
      "agent": "builder-1",
      "subdirectory": "src/auth/",
      "working_files": ["src/auth/login.py", "src/auth/jwt.py"]
    },
    "task-002": {
      "agent": "builder-2",
      "subdirectory": "src/search/",
      "working_files": ["src/search/engine.py", "src/search/index.py"]
    }
  }
}
```

**No file overlap** = No conflicts!

### 3. Progress Tracking

**Mailbox shows all 3 builders**:
```json
{"agent":"builder-1","event":"task_claimed","task":"auth-001","subdirectory":"src/auth/"}
{"agent":"builder-2","event":"task_claimed","task":"search-001","subdirectory":"src/search/"}
{"agent":"builder-3","event":"task_claimed","task":"reporting-001","subdirectory":"src/reports/"}

{"agent":"builder-1","event":"progress","task":"auth-001","progress":"50%"}
{"agent":"builder-2","event":"task_completed","task":"search-001"}
{"agent":"builder-3","event":"blocked","task":"reporting-001","reason":"Need database schema"}
```

**You see**: All 3 progressing independently!

### 4. Quality Gate (Reviewer)

**All 3 builders' outputs go to reviewer**:
```
builder-1 completes → review queue
builder-2 completes → review queue
builder-3 completes → review queue
       ↓
Reviewer reviews all 3
       ↓
Approves or requests changes
```

**Quality maintained** even with parallel work!

---

## Invocation Patterns

### Pattern 1: Direct Assignment (You Assign)

```bash
# You manually assign to specific builders
"builder-1, implement user authentication in src/auth/"
"builder-2, implement search engine in src/search/"
"builder-3, implement reporting in src/reports/"
```

**Best for**: When you know the architecture and want direct control.

### Pattern 2: Project-Manager Orchestration (Recommended)

```bash
# You give project-manager the epic
"Project-manager, implement grant matching MVP with the following features:
- User authentication
- Grant search
- Matching algorithm
- Report generation"

# Project-manager breaks down and assigns:
# → builder-1: auth
# → builder-2: search + matching
# → builder-3: reporting
```

**Best for**: Complex multi-feature work, optimal load balancing.

### Pattern 3: Team-Level Command

```bash
# Invoke whole Dev Team
"Dev Team, implement grant matching MVP from ARTIFACTS/prompts/mvp-build.md"

# Project-manager reads prompt, assigns:
# → builder-1, builder-2, builder-3 get different parts
# → ml-engineer, data-engineer work on specialized parts
# → reviewer reviews all
```

**Best for**: Large projects, maximum parallelism.

---

## Updated Collaboration Infrastructure

### What's Changed with Multiple Builders

#### 1. State Tracking

**`state.json` now tracks**:
```json
{
  "teams": {
    "dev": {
      "members": ["builder-1", "builder-2", "builder-3", "reviewer", "problem-solver", "project-manager", "ml-engineer", "data-engineer"]
    }
  },
  "agent_status": {
    "builder-1": {"active": true, "current_task": "auth-001"},
    "builder-2": {"active": true, "current_task": "search-001"},
    "builder-3": {"active": false, "current_task": null}
  }
}
```

**You see**: Which builders are active, what they're working on.

#### 2. Mailbox Events

**Events now distinguish builders**:
```json
{"agent":"builder-1", "event":"task_claimed", ...}
{"agent":"builder-2", "event":"file_modified", "file":"src/search/engine.py", ...}
{"agent":"builder-3", "event":"tests_passed", "tests":15, ...}
```

#### 3. Project-Manager Coordination

**PM now balances load across 3 builders**:

**Load Balancing Logic**:
```
IF builder-1 is idle AND builder-2 is working AND builder-3 is working:
  → Assign next task to builder-1

IF all 3 builders are idle:
  → Assign hardest task to most appropriate builder
  → Assign medium tasks to others

IF all 3 builders are working:
  → Wait for one to finish before assigning more
```

#### 4. Reviewer Knows About Multiple Builders

**Reviewer checks code from all builders**:
```
Review queue:
- auth-001 (from builder-1)
- search-001 (from builder-2)
- reporting-001 (from builder-3)

Reviewer reviews each independently.
```

---

## Example Workflows

### Workflow 1: Sprint with 3 Parallel Features

```bash
# Monday morning
You: "Project-manager, plan sprint with these features:
1. User authentication (high priority)
2. Grant search (medium priority)
3. Reporting module (low priority)"

# Project-manager assigns:
builder-1 → User auth (most complex)
builder-2 → Grant search (medium complexity)
builder-3 → Reporting (simplest)

# All work Monday-Friday in parallel

# Friday afternoon
builder-1 completes auth → reviewer approves
builder-2 completes search → reviewer requests changes
builder-3 completes reporting → reviewer approves

# Monday of week 2
builder-2 fixes issues → reviewer approves

# Done: 3 features in ~1.5 weeks instead of 3+ weeks
```

### Workflow 2: Multi-Idea Portfolio Development

```bash
# You're building multiple ideas simultaneously
"builder-1, work on Idea 062 (Grant Matching MVP)"
"builder-2, work on Idea 099 (Pricing Tool MVP)"
"builder-3, work on Idea 105 (Analytics Dashboard MVP)"

# Each builder works in different subdirectory:
builder-1: 01_VALIDATED_IDEAS/.../IDEA_062.../MVP/
builder-2: 01_VALIDATED_IDEAS/.../IDEA_099.../MVP/
builder-3: 01_VALIDATED_IDEAS/.../IDEA_105.../MVP/

# State tracks all 3 projects independently
# You make progress on 3 ideas at once!
```

### Workflow 3: Research → Multi-Builder Development

```bash
# Week 1: Research
"Research Team, investigate grant matching algorithms"
# → Creates IMPLEMENTATION_BRIEF.md with 3 components:
#    1. Semantic search engine
#    2. Scoring algorithm
#    3. Data layer

# Week 2: Parallel Development
You: "Dev Team, implement the 3 components from implementation brief"

# Project-manager assigns:
builder-1 → Semantic search (uses ml-engineer's model)
builder-2 → Scoring algorithm
builder-3 → Data layer (coordinates with data-engineer)

# All 3 work in parallel
# Week 3: Integration + review
```

---

## Best Practices

### ✅ DO

1. **Assign non-overlapping work** - Different files, different subdirectories
2. **Let project-manager balance load** - They know who's busy
3. **Use all 3 for large features** - Break into parallel-able parts
4. **Check mailbox.jsonl** - See all 3 builders' progress
5. **Route everything through reviewer** - Quality gate for all outputs

### ❌ DON'T

1. **Assign same file to multiple builders** - Will conflict
2. **Micromanage all 3 constantly** - Let them work autonomously
3. **Skip reviews** - More builders = more important to review
4. **Ignore dependencies** - builder-2 can't use builder-1's code until it's done
5. **Overload all 3 with tiny tasks** - Use single builder for simple work

---

## Monitoring Multi-Builder Work

### Check Status

```bash
# See all builder status
cat .claude/state/state.json | grep -A 4 "builder-"

# See recent activity from all builders
cat .claude/state/mailbox.jsonl | grep builder- | tail -20

# Human-readable board
cat docs/decisions/WORKBOARD.md
```

### Example Status Check

```json
{
  "builder-1": {"active": true, "current_task": "auth-001", "last_seen": "2025-11-15T14:30:00Z"},
  "builder-2": {"active": true, "current_task": "search-001", "last_seen": "2025-11-15T14:28:00Z"},
  "builder-3": {"active": false, "current_task": null, "last_seen": "2025-11-15T13:00:00Z"}
}
```

**Interpretation**:
- builder-1 and builder-2 are actively working
- builder-3 finished their task and is idle
- Ready to assign next task to builder-3!

---

## When to Use Original "builder" vs "builder-1/2/3"

### Use Original "builder" For:
- Simple, one-off tasks
- Quick fixes
- Learning/exploration
- When you don't need parallelism

### Use "builder-1/2/3" For:
- Multi-feature sprints
- Large epics
- Multiple projects simultaneously
- Maximum development velocity

**Both approaches work!** Choose based on your needs.

---

## Summary

### What You Have Now

**9 Dev Team Agents**:
- ✅ 4 parallel builders (builder, builder-1, builder-2, builder-3)
- ✅ Reviewer, problem-solver, project-manager
- ✅ ML-engineer, data-engineer

**16 Total Agents**:
- 9 Dev Team agents
- 5 Research Team agents (scout, analyst, synthesizer, validator, reporter)
- 1 Router agent (orchestration)
- 1 CDFI-extractor (specialized)

### Capabilities

**Speed**: 4x faster on parallelizable work
**Scale**: Work on 4+ projects simultaneously
**Quality**: All outputs still reviewed
**Coordination**: Project-manager + router agent orchestrate
**Persistence**: All builders' state persists
**Reliability**: Checkpoint protocol and error handling

### Invocation

```bash
# Direct assignment
"builder-1, do X"
"builder-2, do Y"
"builder-3, do Z"

# PM orchestration (recommended)
"Project-manager, implement features A, B, C"
# → PM assigns to builder-1, builder-2, builder-3

# Team-level
"Dev Team, build the MVP"
# → PM + 3 builders + specialists all coordinate
```

---

**You now have a full development team working in parallel!** 🚀
