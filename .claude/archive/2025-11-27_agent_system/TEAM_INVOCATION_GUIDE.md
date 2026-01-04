# Team Invocation Guide
**Last Updated**: 2025-11-27

## Overview

You now have **16 autonomous agents** organized into teams:
- **The Dev Team** (9 agents) - Builds products with parallel development
- **The Research Team** (5 agents) - Investigates and analyzes
- **Router** (1 agent) - Orchestrates complex workflows
- **CDFI-extractor** (1 agent) - Specialized data extraction

This guide shows you how to effectively invoke teams and individual agents.

---

## Quick Reference

### Invoking The Dev Team

```bash
# Team-level command (project-manager coordinates)
"Dev Team, please implement the features in ARTIFACTS/sprint-backlog.md"

# Specific builders (4 available for parallel work)
"Builder, implement user authentication"
"Builder-1, create API endpoints"
"Builder-2, build frontend components"
"Builder-3, write integration tests"

# Specialists
"ML-engineer, optimize the embedding model"
"Data-engineer, optimize database queries"
"Reviewer, review the auth code in src/auth/"
"Problem-solver, debug the failing integration test"
```

### Invoking The Research Team

```bash
# Team-level command (scout starts the pipeline)
"Research Team, investigate grant matching algorithms used by competitors"

# Specific agents
"Scout, find data on foundation giving patterns"
"Analyst, analyze the grant success data"
"Synthesizer, create implementation recommendations"
"Validator, fact-check the competitive analysis"
"Reporter, write the final research report"
```

### Invoking Router for Complex Workflows

```bash
# Router orchestrates multi-step workflows
"Router, orchestrate the complete grant matching MVP workflow"
"Router, route this task to the appropriate team and monitor progress"
```

---

## How Team Invocation Works

When you address a **team** instead of an individual agent, the team's **coordinator agent** takes the lead and orchestrates the work:

### Dev Team Coordination
**Team Coordinator**: `project-manager`

```
You: "Dev Team, build the grant matching feature"
       ↓
project-manager: Reads request, breaks down into tasks
       ↓
project-manager: Assigns tasks to builder, ml-engineer, data-engineer
       ↓
Agents work autonomously, coordinating via mailbox.jsonl
       ↓
reviewer: Reviews completed work
       ↓
project-manager: Reports completion to you
```

### Research Team Coordination
**Team Coordinator**: `scout` (starts the pipeline)

```
You: "Research Team, research competitor pricing models"
       ↓
scout: Gathers all data sources on competitor pricing
       ↓
analyst: Analyzes pricing patterns statistically
       ↓
synthesizer: Creates strategic pricing recommendations
       ↓
validator: Fact-checks all claims
       ↓
reporter: Writes final report and implementation brief
```

---

## Command Patterns

### Pattern 1: Direct Team Command

**Use when**: You want the whole team to tackle a problem

```bash
# Dev Team examples
"Dev Team, implement the MVP features listed in ARTIFACTS/mvp-scope.md"
"Dev Team, fix all failing tests and deploy to staging"
"Dev Team, refactor the matching algorithm for better performance"

# Research Team examples
"Research Team, analyze user behavior patterns in our analytics data"
"Research Team, research best practices for semantic search in grant matching"
"Research Team, validate our pricing assumptions against market data"
```

**What happens**: The coordinator agent (project-manager for Dev, scout for Research) reads your request, plans the work, and coordinates team members via shared files.

---

### Pattern 2: Team + Specific Prompt File

**Use when**: You have a detailed prompt written out

```bash
# Dev Team with prompt file
"Dev Team, please complete this prompt: ARTIFACTS/prompts/build-recommendation-engine.md"

# Research Team with prompt file
"Research Team, please complete this prompt: ARTIFACTS/prompts/market-research-foundation-landscape.md"
```

**What happens**: The team reads the prompt file, which should contain:
- Objective
- Acceptance criteria
- Context and constraints
- Deliverables expected

---

### Pattern 3: Specific Agent for Specific Task

**Use when**: You know exactly which agent you need

```bash
# Dev Team agents (9 total)
"Builder, implement the /api/match endpoint as specified in ARTIFACTS/api-spec.md"
"Builder-1, create the user authentication system"
"Builder-2, implement the frontend dashboard"
"Builder-3, write comprehensive integration tests"
"ML-engineer, train the matching model with the new dataset in data/grants_2024.csv"
"Data-engineer, optimize the fuzzy matching query—it's taking 5+ seconds"
"Reviewer, review the ML model code in src/ml/"
"Problem-solver, the tests are failing with a database connection error"
"Project-manager, create a sprint plan for the next 2 weeks"

# Research Team agents (5 total)
"Scout, find all publicly available grant databases"
"Analyst, run statistical analysis on the nonprofit success data"
"Synthesizer, create strategic recommendations from analyst's findings"
"Validator, fact-check the claims in research_outputs/synthesis.md"
"Reporter, write an executive summary of the research for stakeholders"

# Orchestration agent
"Router, orchestrate the end-to-end grant matching feature from research to deployment"

# Specialized agent
"CDFI-extractor, extract and structure CDFI data from the Treasury website"
```

---

## Prompt File Format

When using "Dev Team, please complete this prompt: path/to/prompt.md", structure your prompt file like this:

### Example: Dev Team Prompt

```markdown
# Build Grant Matching Recommendation Engine

## Objective
Build a recommendation system that suggests which foundations a nonprofit should apply to, ranked by probability of success.

## Context
- We have 15,000 foundations in our database
- We have historical grant data (1.6M grants)
- We need <500ms response time
- Must handle 1000 concurrent users

## Acceptance Criteria
- [ ] API endpoint `/api/recommend` accepts nonprofit EIN
- [ ] Returns top 50 foundation recommendations
- [ ] Each recommendation includes:
  - Foundation name and EIN
  - Match score (0-100)
  - Match reasoning (GPT-generated)
  - Historical relationship indicator
- [ ] Response time <500ms (p95)
- [ ] Unit tests with >80% coverage
- [ ] Integration tests for full matching pipeline
- [ ] API documentation in OpenAPI format

## Technical Constraints
- Use existing PostgreSQL database
- Use pgvector for semantic search
- Use Sentence-BERT (all-MiniLM-L6-v2) for embeddings
- GPT-4o-mini for match explanations
- Python/FastAPI backend

## Deliverables
1. Implemented and tested API endpoint
2. Database migrations (if needed)
3. Documentation
4. Performance benchmarks

## Team Assignments (project-manager will refine)
- data-engineer: Database schema and query optimization
- ml-engineer: Semantic search and scoring algorithm
- builder: API implementation and integration
- reviewer: Code review and security audit
```

### Example: Research Team Prompt

```markdown
# Research: Semantic Search for Grant Matching

## Research Question
What semantic search approaches are most effective for matching nonprofits to foundations based on mission alignment?

## Context
We're building a grant matching tool. We need to understand:
- Which embedding models work best for nonprofit/foundation text
- How to weigh semantic similarity vs other factors
- What accuracy/recall metrics similar tools achieve

## Research Scope
- **Time**: 3-5 days
- **Sources**: Academic papers, competitor tools, industry blogs
- **Data needed**: Benchmarks, model comparisons, real-world results

## Deliverables
1. Literature review of semantic search in grant matching
2. Comparison of embedding models (BERT, Sentence-BERT, OpenAI Ada)
3. Analysis of how competitors implement semantic search
4. Recommendations for our implementation
5. Implementation brief for Dev Team

## Team Workflow (scout will coordinate)
- scout: Find papers, competitor research, benchmark data
- analyst: Compare model performance quantitatively
- synthesizer: Create implementation recommendations
- validator: Verify all technical claims
- reporter: Write technical spec for Dev Team
```

---

## Team Communication Examples

### Example 1: Research → Dev Handoff

```bash
# Week 1: Research investigates
You: "Research Team, analyze what makes a successful grant proposal based on our historical data"

# Research Team works autonomously...
# Output: research_outputs/grant_success_factors.md
#         ARTIFACTS/IMPLEMENTATION_BRIEF.md

# Week 2: Dev builds based on research
You: "Dev Team, build a proposal strength analyzer based on Research Team's findings in ARTIFACTS/IMPLEMENTATION_BRIEF.md"

# Dev Team implements the feature using research insights
```

### Example 2: Dev Requests Research Support

```bash
# Dev Team hits a question
Builder: "Blocked: Not sure which matching algorithm to use"
(Logs to mailbox with "team":"dev", "event":"blocked")

# You assign Research Team to investigate
You: "Research Team, research grant matching algorithms and recommend the best approach for our use case"

# Research delivers findings
Reporter: Creates ARTIFACTS/IMPLEMENTATION_BRIEF_matching_algorithm.md

# Dev Team proceeds
You: "Builder, implement the collaborative filtering approach recommended in the implementation brief"
```

### Example 3: Parallel Work

```bash
# Both teams work simultaneously
You: "Research Team, investigate nonprofit retention patterns"
You: "Dev Team, build the MVP features while research investigates retention"

# Teams coordinate through shared files
# Research findings inform Dev Team's later iterations
```

---

## Best Practices

### ✅ DO

- **Address teams for coordinated work**: "Dev Team, build X" instead of micromanaging each agent
- **Use prompt files for complex requests**: Clearer requirements = better execution
- **Let coordinators orchestrate**: project-manager and scout know how to delegate
- **Check mailbox.jsonl to see progress**: Transparent log of all team activities
- **Read team outputs before next request**: `research_outputs/`, `docs/decisions/WORKBOARD.md`
- **Use specific agents when needed**: "ML-engineer, optimize the model" for targeted work

### ❌ DON'T

- **Don't micromanage individual agents for team tasks**: Let the team coordinate
- **Don't skip handoff files**: Research → Dev needs IMPLEMENTATION_BRIEF.md
- **Don't ignore blockers**: If agents log "blocked", address it or assign problem-solver
- **Don't restart work from scratch**: Agents maintain state—build on previous work

---

## Common Workflows

### Workflow 1: Feature Development (Dev Team)

```bash
1. You: "Dev Team, implement user authentication"
2. project-manager: Breaks down into tasks, assigns to builder
3. builder: Implements auth, writes tests, moves to review
4. reviewer: Reviews code, requests changes OR approves
5. If approved: Task moves to done
6. project-manager: Reports completion to you
```

### Workflow 2: Research Project (Research Team)

```bash
1. You: "Research Team, analyze competitor grant matching features"
2. scout: Gathers data on 10 competitors
3. analyst: Analyzes feature sets, pricing, user reviews
4. synthesizer: Identifies gaps and opportunities
5. validator: Fact-checks all claims about competitors
6. reporter: Writes competitive analysis report + implementation brief
7. You review: research_outputs/final_report.md
```

### Workflow 3: Research-Driven Development

```bash
1. You: "Research Team, investigate best database architecture for 10M+ grant records"
2. Research Team delivers technical recommendations
3. You: "Dev Team, implement the recommended database architecture from ARTIFACTS/IMPLEMENTATION_BRIEF_database.md"
4. Dev Team builds based on research findings
5. You: "Research Team, benchmark the new database performance"
6. Research validates Dev Team's implementation
```

---

## Checking Team Status

### View What Teams Are Doing

```bash
# Check mailbox for recent activity
cat .claude/state/mailbox.jsonl | tail -20

# Check work queues
cat .claude/state/state.json

# Check human-readable status
cat docs/decisions/WORKBOARD.md

# Check research outputs
ls -la research_outputs/

# Check team coordination guide
cat .claude/TEAM_COLLABORATION_GUIDE.md
```

### Example Mailbox Entries

```json
{"timestamp":"2025-11-15T22:00:00Z","team":"dev","agent":"project-manager","event":"sprint_planned","details":"Created 12 tasks for grant matching MVP"}
{"timestamp":"2025-11-15T22:15:00Z","team":"dev","agent":"builder","event":"task_claimed","task":"Implement /api/match endpoint"}
{"timestamp":"2025-11-15T23:00:00Z","team":"dev","agent":"builder","event":"task_completed","task":"Implement /api/match endpoint","tests":15}
{"timestamp":"2025-11-15T23:05:00Z","team":"dev","agent":"reviewer","event":"review_started","task":"Implement /api/match endpoint"}
{"timestamp":"2025-11-15T23:20:00Z","team":"dev","agent":"reviewer","event":"approved","task":"Implement /api/match endpoint"}

{"timestamp":"2025-11-15T22:00:00Z","team":"research","agent":"scout","event":"discovery_started","topic":"Grant matching algorithms"}
{"timestamp":"2025-11-16T01:00:00Z","team":"research","agent":"scout","event":"discovery_complete","sources":25}
{"timestamp":"2025-11-16T01:15:00Z","team":"research","agent":"analyst","event":"analysis_started"}
{"timestamp":"2025-11-16T04:00:00Z","team":"research","agent":"analyst","event":"analysis_complete","findings":8}
{"timestamp":"2025-11-16T05:00:00Z","team":"research","agent":"reporter","event":"report_complete","output":"research_outputs/final_report.md"}
```

---

## Summary

### Team Invocation Syntax

```bash
# Full team (coordinator handles delegation)
"<Team Name>, <what you want done>"
"<Team Name>, please complete this prompt: <path/to/prompt.md>"

# Specific agent
"<Agent Name>, <specific task>"

# Examples
"Dev Team, build the grant matching MVP"
"Dev Team, please complete this prompt: ARTIFACTS/mvp-build.md"
"Research Team, investigate user retention strategies"
"Builder, implement the recommendation endpoint"
"Scout, find grant databases for California foundations"
```

### Team Coordinators

- **Dev Team Coordinator**: `project-manager`
- **Research Team Start**: `scout` (kicks off research pipeline)
- **Workflow Orchestration**: `router` (manages complex multi-team workflows)

### File-Based Coordination

- `mailbox.jsonl` - Cross-team event log
- `state.json` - Work queue state, checkpoints, phases
- `task_graph.json` - Pipeline definitions and dependencies
- `checkpoints/` - Recovery points for long operations
- `WORKBOARD.md` - Human-readable status
- `ARTIFACTS/IMPLEMENTATION_BRIEF.md` - Research → Dev handoffs
- `research_outputs/` - All research deliverables
- `memory/lessons.md` - Lessons learned across sessions

---

## You're Ready!

Your teams are configured, coordinated, and ready to work. Just address them by team name, and they'll handle the rest.

**Examples to try**:

```bash
# Team-level commands
"Dev Team, review the codebase and create a refactoring plan"
"Research Team, analyze our user feedback data"
"Dev Team, please complete this prompt: ARTIFACTS/prompts/build-api.md"

# Parallel builders (4x speed)
"Builder, implement backend API"
"Builder-1, create frontend UI"
"Builder-2, write integration tests"
"Builder-3, set up CI/CD pipeline"

# Specialists
"ML-engineer, optimize the embedding generation speed"
"Data-engineer, improve database query performance"
"Scout, find competitive intelligence on Candid.org"
"Router, orchestrate the complete feature from research to deployment"
```

The teams will coordinate autonomously, log everything to mailbox.jsonl, checkpoint long operations, and deliver results to the appropriate output directories.

**Key Capabilities**:
- 16 agents total (9 Dev + 5 Research + router + cdfi-extractor)
- 4 parallel builders for maximum development speed
- Model tiering (Haiku for routing/simple tasks, Sonnet for complex work)
- Checkpoint protocol for long-running operations
- Three-tier error handling with recovery guide
- Complete state persistence across terminal sessions
