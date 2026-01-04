# Context Tracking & Team Effectiveness Guide

**Last Updated**: 2025-11-27

---

## Your Questions Answered

### ✅ Q1: Will both you and agents see which subdirectory work is being done in?

**YES!** Enhanced state tracking now includes:
- Project root directory
- Subdirectory per task
- File paths for all modified files
- Working directory logged in mailbox events

### ✅ Q2: Will agents remember file paths, prompts, and resources to pick up where they left off?

**YES!** Enhanced tracking includes:
- Saved prompts registry
- File paths for all resources
- Data source locations
- External API references
- Complete task context

### ✅ Q3: Can project-manager create new builder agents to go faster?

**NO - but there's a better solution!** Project-manager can't dynamically spawn agents, BUT can coordinate parallel work across existing specialists. See "Team Scaling Strategy" below.

---

## Enhanced State Tracking

### What's Now Tracked

#### 1. Subdirectory & File Paths

**In `state.json`**:
```json
{
  "project_root": "/mnt/c/Business Factory (Research) 11-1-2025",
  "active_subdirectories": {
    "grant_matching_mvp": "01_VALIDATED_IDEAS/TIER_1_BOOTSTRAPPED/IDEA_062_Grant_Alerts/MVP",
    "market_research": "03_ANALYSIS_REPORTS/grant_matching_competitors"
  },
  "task_contexts": {
    "task-001": {
      "title": "Implement grant matching API",
      "subdirectory": "01_VALIDATED_IDEAS/TIER_1_BOOTSTRAPPED/IDEA_062_Grant_Alerts/MVP",
      "working_files": [
        "src/api/match.py",
        "src/models/foundation.py",
        "tests/test_matching.py"
      ],
      "prompt_used": "ARTIFACTS/prompts/build-matching-engine.md",
      "dependencies": [
        "research_outputs/semantic_search_recommendations.md",
        "ARTIFACTS/IMPLEMENTATION_BRIEF.md"
      ]
    }
  }
}
```

**In `mailbox.jsonl`**:
```json
{"timestamp":"...","agent":"builder","event":"task_claimed","task":"task-001","subdirectory":"01_VALIDATED_IDEAS/.../MVP","working_directory":"/mnt/c/Business Factory (Research) 11-1-2025/01_VALIDATED_IDEAS/TIER_1_BOOTSTRAPPED/IDEA_062_Grant_Alerts/MVP"}
{"timestamp":"...","agent":"builder","event":"file_modified","file":"src/api/match.py","lines_added":145}
```

#### 2. Resource Registry

**In `state.json`**:
```json
{
  "resource_registry": {
    "prompts": [
      "ARTIFACTS/prompts/build-matching-engine.md",
      "ARTIFACTS/prompts/research-semantic-search.md"
    ],
    "data_sources": [
      "research_outputs/grant_data_cleaned.csv",
      "research_outputs/foundation_profiles.json"
    ],
    "external_apis": [
      {
        "name": "OpenAI GPT-4",
        "purpose": "Match explanations",
        "docs": "https://platform.openai.com/docs"
      }
    ],
    "documentation": [
      "research_outputs/semantic_search_technical_spec.md",
      "ARTIFACTS/IMPLEMENTATION_BRIEF_matching_algorithm.md"
    ]
  }
}
```

---

## How Agents Use This Information

### When Agent Is Invoked After Terminal Reopen

**Builder resumes task-001**:

```python
# 1. Read state.json
state = read_json('.claude/state/state.json')
my_task = state['task_contexts']['task-001']

# 2. Know exactly where to work
subdirectory = my_task['subdirectory']
working_files = my_task['working_files']  # ['src/api/match.py', ...]

# 3. Know what resources were used
prompt = read_file(my_task['prompt_used'])  # Original requirements
dependencies = my_task['dependencies']  # Research Team's outputs

# 4. Read mailbox for history
events = read_mailbox_for_task('task-001')
# See: "Modified src/api/match.py, added 145 lines"
# See: "Tests passing: 8/10"
# See: "Still need: error handling for timeout"

# 5. Navigate to correct directory
cd(f"{state['project_root']}/{subdirectory}")

# 6. Continue work from exact point
continue_implementation(working_files, events, dependencies)
```

**Perfect context restoration!**

---

## Making Teams Maximally Effective

### Speed Optimizations

#### 1. Parallel Work Assignment

**Project-manager coordinates simultaneous work**:

```bash
# Instead of sequential:
"Builder, do task A"  # Wait...
"Builder, do task B"  # Wait...

# Parallel across specialists:
"Builder, implement API endpoints"
"ML-engineer, train matching model"      # Same time!
"Data-engineer, optimize database"       # Same time!
```

**3x faster** when work is parallelizable.

#### 2. Clear Task Boundaries

**In ARTIFACTS/TASKS.md**:
```markdown
### Task: Build Recommendation Engine

**Subdirectory**: 01_VALIDATED_IDEAS/TIER_1_BOOTSTRAPPED/IDEA_062_Grant_Alerts/MVP
**Working Directory**: src/recommendation/
**Files to Create/Modify**:
- src/recommendation/engine.py (new)
- src/recommendation/scorer.py (new)
- tests/test_recommendation.py (new)

**Dependencies**:
- research_outputs/algorithm_recommendations.md
- src/models/foundation.py (existing)

**External Resources**:
- Sentence-BERT model: all-MiniLM-L6-v2
- PostgreSQL pgvector extension
```

Agents know **exactly** what to do - no ambiguity.

#### 3. Prompt Library

**Create reusable prompts**:

```
ARTIFACTS/prompts/
├── build-api-endpoint-template.md
├── optimize-database-query-template.md
├── research-competitor-template.md
└── train-ml-model-template.md
```

Reference templates in tasks:
```markdown
**Prompt Template**: Use ARTIFACTS/prompts/build-api-endpoint-template.md
**Specific Requirements**: [Fill in specifics here]
```

### Quality Optimizations

#### 1. Systematic Reviews

**Every Dev Team output goes through reviewer**:
```
builder completes → review queue → reviewer → approved/rejected
```

**Reviewer checks**:
- Code quality
- Test coverage
- Security (no secrets, input validation)
- Performance
- Documentation

#### 2. Research Validation

**Every Research Team output goes through validator**:
```
synthesizer completes → validator → fact-checks → approved/corrections needed
```

#### 3. Quality Checklists

**In each agent definition** (already included):
- Builder has self-verification checklist
- Reviewer has review checklist
- Validator has validation checklist

### Communication Optimizations

#### 1. Structured Mailbox Events

**Standard event format**:
```json
{
  "timestamp": "2025-11-15T22:00:00Z",
  "team": "dev",
  "agent": "builder",
  "event": "file_modified",
  "task_id": "task-001",
  "subdirectory": "01_VALIDATED_IDEAS/TIER_1_BOOTSTRAPPED/IDEA_062_Grant_Alerts/MVP",
  "file": "src/api/match.py",
  "details": "Implemented semantic search integration",
  "lines_added": 145,
  "tests_added": 8
}
```

**Both you and agents** can parse this for exact status.

#### 2. Handoff Protocols

**Research → Dev handoff**:
```
reporter creates:
├── research_outputs/final_report.md
├── ARTIFACTS/IMPLEMENTATION_BRIEF.md
└── Logs to mailbox: "Research complete, handoff ready"

Dev Team reads:
├── IMPLEMENTATION_BRIEF.md (what to build)
├── research_outputs/ (supporting data)
└── Starts implementation
```

---

## Team Scaling Strategy

### ❌ Can't Do: Dynamically Create Agents

Claude Code agents are defined as `.md` files in `.claude/agents/`. You can't spawn new agents at runtime.

### ✅ Can Do: Parallel Work Across Specialists

You have **9 Dev Team agents** (including 4 builders) that can work **simultaneously**:

**Example: Grant Matching MVP**

```bash
# Project-manager breaks down epic into parallel tracks:

"Data-engineer, build database schema and indexes"           # Track 1
"ML-engineer, implement semantic search engine"              # Track 2
"Builder-1, create API endpoints and business logic"        # Track 3
"Builder-2, implement frontend components"                  # Track 4

# All 4 work in parallel!
# Each logs to mailbox with their subdirectory and files
# Reviewer reviews all outputs when complete
```

**Result**: 4x faster than sequential work.

### ✅ Can Do: Multiple Projects in Parallel

**Grant Matching MVP** (Idea 062):
```bash
"ML-engineer, work on Idea 062 matching algorithm"
"Data-engineer, work on Idea 062 database"
```

**Different Idea** (Idea 099):
```bash
"Builder, work on Idea 099 API"
"Reviewer, review Idea 099 code"
```

**Both projects progress simultaneously!**

State tracks different `subdirectories` in `active_subdirectories`:
```json
{
  "active_subdirectories": {
    "idea_062_mvp": "01_VALIDATED_IDEAS/.../IDEA_062_Grant_Alerts/MVP",
    "idea_099_mvp": "01_VALIDATED_IDEAS/.../IDEA_099_SomethingElse/MVP"
  }
}
```

### Project-Manager's Role in Scaling

**Project-manager doesn't create builders, but**:

1. **Breaks down work** into parallelizable chunks
2. **Assigns to different specialists** (builder, ml-engineer, data-engineer)
3. **Coordinates timing** (data-engineer finishes schema before builder uses it)
4. **Monitors mailbox** for blockers
5. **Ensures reviewer gets everything** before marking done

**Example Sprint Plan**:

```markdown
# Sprint: Grant Matching MVP

## Week 1 - Foundation (Parallel)
- [data-engineer] Database schema + indexes
- [ml-engineer] Evaluate embedding models
- [builder] Project structure + config

## Week 2 - Core Features (Parallel)
- [ml-engineer] Implement semantic search
- [data-engineer] Historical relationship detection
- [builder] API endpoints + auth

## Week 3 - Integration (Sequential - dependencies exist)
- [builder] Integrate ML + data layers
- [reviewer] Review integration code
- [problem-solver] Debug any integration issues

## Week 4 - Polish (Parallel)
- [ml-engineer] Optimize embedding speed
- [data-engineer] Query performance tuning
- [builder] Error handling + logging
- [reviewer] Final review
```

**4 weeks, 6 agents working in parallel** = Massive velocity!

---

## What Else Makes Teams Effective?

### 1. Clear Success Criteria

**Every task has measurable acceptance criteria**:

```markdown
### Task: Implement Matching API

**Done When**:
- [ ] API endpoint `/api/match` responds <500ms
- [ ] Returns top 50 recommendations
- [ ] Unit tests >80% coverage
- [ ] Integration tests pass
- [ ] Reviewer approves
```

No ambiguity = faster execution.

### 2. Research Feeds Development

**Research Team validates approaches BEFORE Dev Team builds**:

```bash
# Week 1: Research
"Research Team, which embedding model performs best for grant matching?"

# Week 2: Dev builds validated approach
"ML-engineer, implement Sentence-BERT as recommended in IMPLEMENTATION_BRIEF.md"
```

**Avoids building the wrong thing!**

### 3. Continuous Documentation

Agents log everything:
- What they did
- Why they did it
- What resources they used
- What they learned

**Result**: Complete project documentation with zero extra effort.

### 4. Persistent State

Work never lost across terminal sessions = Long-term projects feasible.

---

## Complete Workflow Example

### Grant Matching Project Across Multiple Ideas

**Terminal Session 1** (Idea 062 Research):
```bash
"Research Team, investigate grant matching algorithms"
# Works in: 01_VALIDATED_IDEAS/TIER_1_BOOTSTRAPPED/IDEA_062_Grant_Alerts/
```

**Terminal Session 2** (Idea 062 Development):
```bash
"Data-engineer, build schema for Idea 062"
"ML-engineer, implement matching for Idea 062"
"Builder, build API for Idea 062"
# All work in: 01_VALIDATED_IDEAS/.../IDEA_062.../MVP/
```

**Terminal Session 3** (Start Idea 099):
```bash
"Research Team, research pricing models for Idea 099"
# Works in: 01_VALIDATED_IDEAS/.../IDEA_099.../
```

**Terminal Session 4** (Both projects):
```bash
"Reviewer, review Idea 062 code"
"Builder, start Idea 099 implementation"
# Multiple subdirectories tracked in state.json
```

**State tracking keeps it all organized!**

---

## Summary

### ✅ Subdirectory Tracking
- `state.json` tracks `active_subdirectories`
- Each task logs `subdirectory` and `working_directory`
- Both you and agents see exactly where work happens

### ✅ Resource Tracking
- `task_contexts` stores prompts, dependencies, file paths
- `resource_registry` tracks all data sources, APIs, docs
- Agents read this to pick up exactly where they left off

### ✅ Team Effectiveness
- **Speed**: Parallel work across 9 Dev + 5 Research + 2 specialized agents (16 total)
- **Quality**: Systematic reviews (reviewer + validator)
- **Persistence**: Work never lost, infinite project continuity
- **Reliability**: Checkpoints, error handling tiers, recovery protocols

### ✅ Team Scaling
- Can't dynamically create builders
- **BUT** can coordinate parallel work across 9 Dev Team specialists (including 4 builders)
- **Result**: Equivalent to "adding builders" without the complexity
- **Orchestration**: Router agent intelligently routes work across all 16 agents

---

## What You're NOT Missing

You have:
- ✅ State persistence (state.json, mailbox.jsonl, task_graph.json)
- ✅ Subdirectory tracking
- ✅ Resource/file path tracking
- ✅ Parallel work coordination (16 agents total)
- ✅ Quality gates (reviewer/validator)
- ✅ Research → Dev handoffs
- ✅ Complete audit trail
- ✅ Checkpoint protocol for long-running operations
- ✅ Three-tier error handling (auto-retry, skip-continue, escalate)
- ✅ Model tiering (Haiku for routing/simple tasks, Sonnet for complex work)
- ✅ Router agent for intelligent workflow orchestration
- ✅ Recovery guide for handling failures

**Your teams are fully equipped for maximum effectiveness!**
