# Team Collaboration Guide
**Last Updated**: 2025-11-27

## Overview

This project now has **16 autonomous agents** organized into specialized teams that work together:

### Dev Team (9 Agents)
1. **builder** - Primary developer (implements features, writes tests)
2. **builder-1** - Parallel builder #1
3. **builder-2** - Parallel builder #2
4. **builder-3** - Parallel builder #3
5. **reviewer** - Code quality guardian (reviews, security, standards)
6. **problem-solver** - Expert debugger and architect
7. **project-manager** - Task planning, progress tracking, workflow
8. **ml-engineer** - Machine learning specialist (models, training, deployment)
9. **data-engineer** - Data pipeline specialist (ETL, databases, processing)

### Research Team (5 Agents)
1. **scout** - Data discovery and collection (Haiku model)
2. **analyst** - Statistical analysis, modeling, visualizations (Sonnet)
3. **synthesizer** - Strategic insights synthesis (Sonnet)
4. **validator** - Quality assurance and fact-checking (Sonnet)
5. **reporter** - Final report generation (Haiku model)

### Orchestration (1 Agent)
1. **router** - Intelligent workflow routing and orchestration (Haiku model)

### Specialized (1 Agent)
1. **cdfi-extractor** - CDFI data extraction specialist (Sonnet)

---

## How Teams Collaborate

### Workflow: Research → Development

The Research Team and Dev Team are designed to work in **sequence** or **parallel**, with research outputs feeding directly into development work.

#### Pattern 1: Sequential (Research First, Then Build)

```
1. Research Team investigates a topic
   ↓
2. Research outputs saved to research_outputs/
   ↓
3. Dev Team uses research findings to build features
   ↓
4. Product ships based on validated research
```

**Example**:
```
Research Team: "Analyze grant matching algorithms"
  → scout collects grant data
  → analyst finds patterns in successful matches
  → synthesizer identifies optimal matching strategy
  → reporter creates technical spec

Dev Team: "Implement grant matching feature"
  → builder reads research_outputs/final_report.md
  → ml-engineer builds matching algorithm based on research findings
  → data-engineer sets up grant data pipeline
  → Product ships with research-backed features
```

#### Pattern 2: Parallel (Research and Development Together)

```
Research Team                    Dev Team
     ↓                               ↓
Scout gathers data     ←→    Data-engineer builds pipelines
     ↓                               ↓
Analyst runs analysis  ←→    ML-engineer trains models
     ↓                               ↓
Research validates     ←→    Builder implements features
     ↓                               ↓
     Both teams sync via shared files
```

**Shared coordination files**:
- `ARTIFACTS/RESEARCH_FINDINGS.md` - Research team posts findings
- `ARTIFACTS/DEV_QUESTIONS.md` - Dev team posts questions for research
- `.claude/state/mailbox.jsonl` - Both teams log coordination events

---

## Inter-Team Handoff Protocol

### Research Team → Dev Team Handoff

When Research Team completes work, they should:

1. **Finalize Research Outputs**
   ```
   research_outputs/
   ├── final_report.md           # Executive summary
   ├── technical_spec.md          # Implementation recommendations
   ├── data/                      # Cleaned datasets
   ├── models/                    # Statistical models/analysis
   └── visualizations/            # Charts, graphs
   ```

2. **Create Implementation Brief**
   Create `ARTIFACTS/IMPLEMENTATION_BRIEF.md`:
   ```markdown
   # Implementation Brief - [Feature Name]

   ## Research Summary
   [1-2 paragraph summary of research findings]

   ## Recommended Implementation
   - Architecture: [Approach based on research]
   - Data sources: [What data to use]
   - Key algorithms: [What the research revealed works best]
   - Success metrics: [How to measure if it's working]

   ## Research Artifacts
   - Full report: `research_outputs/final_report.md`
   - Dataset: `research_outputs/data/cleaned_data.csv`
   - Model specs: `research_outputs/models/model_details.json`
   ```

3. **Log Handoff Event**
   Append to `.claude/state/mailbox.jsonl`:
   ```json
   {
     "timestamp": "2025-11-15T21:40:00Z",
     "team": "research",
     "agent": "reporter",
     "event": "research_complete",
     "details": "Grant matching research complete. Implementation brief ready for Dev Team.",
     "artifacts": ["ARTIFACTS/IMPLEMENTATION_BRIEF.md", "research_outputs/"]
   }
   ```

### Dev Team → Research Team Questions

When Dev Team needs research support:

1. **Post Question**
   Create `ARTIFACTS/RESEARCH_REQUESTS.md`:
   ```markdown
   ## Request: Analyze User Behavior Pattern

   **Requested by**: builder
   **Date**: 2025-11-15
   **Priority**: High

   **Question**:
   We're implementing the recommendation engine, but need to understand:
   - What features do users value most?
   - Which user segments have highest engagement?

   **Why We Need This**:
   To prioritize which recommendation features to build first.

   **Deadline**: Next sprint (1 week)
   ```

2. **Log Request**
   ```json
   {
     "timestamp": "2025-11-15T21:40:00Z",
     "team": "dev",
     "agent": "builder",
     "event": "research_request",
     "details": "Need user behavior analysis for recommendation engine",
     "artifact": "ARTIFACTS/RESEARCH_REQUESTS.md"
   }
   ```

---

## Shared File Structure

Both teams coordinate through these shared directories:

```
C:\Business Factory (Research) 11-1-2025\
│
├── .claude\
│   ├── agents\                # All 11 agents (both teams)
│   ├── state\
│   │   ├── mailbox.jsonl      # Cross-team event log
│   │   └── state.json         # Shared work queue
│   └── TEAM_COLLABORATION_GUIDE.md  # This file
│
├── ARTIFACTS\
│   ├── IMPLEMENTATION_BRIEF.md      # Research → Dev handoff
│   ├── RESEARCH_REQUESTS.md         # Dev → Research requests
│   ├── TASKS.md                     # Dev Team backlog
│   └── RESEARCH_QUESTIONS.md        # Research Team backlog
│
├── research_outputs\               # Research Team outputs
│   ├── final_report.md
│   ├── technical_spec.md
│   ├── data\
│   ├── models\
│   └── visualizations\
│
└── [Your code/project files]       # Dev Team works here
```

---

## Example: Full Research → Dev Workflow

### Scenario: Build a Grant Matching Feature

#### Phase 1: Research (Week 1)

```bash
# You assign research
"Scout, research grant matching algorithms used by similar platforms"
"Analyst, analyze what factors predict successful grant matches"
"Synthesizer, create technical recommendations for implementation"
"Reporter, write implementation brief for Dev Team"
```

**Research Team Outputs**:
- Finds 3 grant databases
- Analyzes 50K grant matches
- Identifies 5 key matching factors
- Recommends collaborative filtering approach
- Creates `ARTIFACTS/IMPLEMENTATION_BRIEF.md`

#### Phase 2: Development (Week 2-3)

```bash
# You assign development
"Project-manager, break down grant matching feature from implementation brief"
"Data-engineer, set up data pipeline for grant matching"
"ML-engineer, build collaborative filtering model based on research specs"
"Builder, implement grant matching API"
"Reviewer, review all grant matching code"
```

**Dev Team Outputs**:
- Builds data pipeline (data-engineer)
- Trains matching model (ml-engineer)
- Implements API endpoints (builder)
- All code reviewed (reviewer)
- Feature ships to production

#### Phase 3: Validation (Week 4)

```bash
# Research validates results
"Analyst, analyze production grant matching performance vs research predictions"
"Validator, verify matching quality meets research standards"
```

---

## Best Practices

### ✅ DO

- **Use ARTIFACTS/ for handoffs** - Clear, documented handoffs between teams
- **Log major events to mailbox.jsonl** - Visibility into cross-team coordination
- **Reference research in code comments** - Link back to research findings
- **Keep research outputs organized** - Structured directories for easy Dev Team access
- **Sync regularly** - Check mailbox.jsonl to see what other team is doing

### ❌ DON'T

- **Don't duplicate work** - Check if research already exists before starting
- **Don't skip handoff docs** - Dev Team needs context, not just raw data
- **Don't modify other team's outputs** - Research outputs are read-only for Dev Team
- **Don't work in silos** - Teams should coordinate via shared files

---

## Invoking Agents

All 11 agents are now available from any directory within the Business Factory project:

### Dev Team Agents
```bash
# Navigate anywhere in project
cd "C:\Business Factory (Research) 11-1-2025\[any-subfolder]"

# Invoke agents
claude
> Builder, implement user authentication
> Reviewer, review the auth code
> Problem-solver, debug the failing test
> Project-manager, create sprint plan from ARTIFACTS/TASKS.md
> ML-engineer, train the recommendation model
> Data-engineer, build ETL pipeline for user data
```

### Research Team Agents
```bash
# Same directory, different agents
> Scout, find market data on competitors
> Analyst, analyze user engagement patterns
> Synthesizer, create strategic recommendations from analysis
> Validator, fact-check the market research
> Reporter, write final research report
```

---

## Coordination Patterns

### Pattern 1: Research Drives Features
Research discovers opportunity → Dev builds it

### Pattern 2: Dev Requests Research
Dev hits unknowns → Research investigates

### Pattern 3: Continuous Validation
Dev ships feature → Research validates performance

### Pattern 4: Iterative Improvement
Research finds issue → Dev fixes it → Research re-validates

---

## Questions?

- Check `.claude/state/mailbox.jsonl` to see what agents have done
- Read `research_outputs/final_report.md` for research summaries
- Check `ARTIFACTS/IMPLEMENTATION_BRIEF.md` for research → dev handoffs
- Review this guide for collaboration patterns

---

## Summary

You now have a **complete research + development workflow** with:
- ✅ 16 specialized agents working together (9 Dev + 5 Research + 2 specialized)
- ✅ Clear handoff protocols between teams
- ✅ Shared coordination files (state.json, mailbox.jsonl, task_graph.json)
- ✅ Full audit trail of all work
- ✅ Checkpoint protocol for long-running operations
- ✅ Three-tier error handling (auto-retry, skip-continue, escalate)
- ✅ Model tiering for cost optimization (Haiku/Sonnet)
- ✅ Router agent for intelligent workflow orchestration
- ✅ Recovery guide for handling failures

**The Research Team validates ideas. The Dev Team builds them. The Router orchestrates. Together, they ship research-backed products.**

---

## Model Tiering

Agents use different Claude models based on task complexity:

### Haiku Agents (Fast, Cheap)
- **Router**: Workflow decisions and routing
- **Scout**: Data discovery and web fetching
- **Reporter**: Document formatting and generation

### Sonnet Agents (Balanced)
- **Analyst**: Statistical analysis and reasoning
- **Synthesizer**: Strategic insights
- **Validator**: Quality assurance
- **Builder/Builder-1/2/3**: Code generation
- **Reviewer**: Code review
- **Project-Manager**: Task planning
- **Problem-Solver**: Debugging
- **ML-Engineer**: Machine learning
- **Data-Engineer**: Data pipelines

### When to Override

If a Haiku agent struggles with a complex task, you can force Sonnet:
```
Scout --model sonnet, analyze these complex site structures
```

### Cost Implications
- Haiku: ~$1 per million tokens (input) / $5 (output)
- Sonnet: ~$3 per million tokens (input) / $15 (output)
- Using Haiku for Scout/Reporter saves ~60% on those agents

### Fallback Protocol

Haiku agents will automatically recommend escalation to Sonnet if they encounter:
- Repeated failures (2+ attempts)
- Complex reasoning beyond their scope
- Unexpected edge cases

They will log `haiku_escalation` events to mailbox.jsonl with details.
