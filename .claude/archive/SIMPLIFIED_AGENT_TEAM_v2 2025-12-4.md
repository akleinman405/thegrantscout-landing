# Simplified Agent Team v2.0

**Created**: 2025-12-04
**Philosophy**: Simplicity over sophistication. Explicit phases over autonomous coordination.

---

## The Reality Check

Your old 16-agent system was overengineered. It's the same Claude model with different persona prompts — no true parallelism, coordination overhead exceeded benefits.

**New approach**: 3 agents maximum, explicit phases, minimal infrastructure.

---

## The Team

### 1. Builder
**Does things**: code, scripts, configs, implementations

```yaml
---
name: builder
description: Implements features, writes scripts, creates solutions
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---
```

### 2. Reviewer  
**Checks things**: catches what you missed, quality gate

```yaml
---
name: reviewer
description: Reviews code and outputs for quality, security, edge cases
tools: Read, Grep, Glob, Bash
model: sonnet
---
```

### 3. Researcher
**Finds things**: web search, analysis, synthesis

```yaml
---
name: researcher
description: Investigates topics, gathers data, analyzes findings
tools: Read, Write, WebSearch, WebFetch
model: sonnet
---
```

---

## When to Use What

| Situation | Tool | Why |
|-----------|------|-----|
| Quick question, brainstorming, writing | Claude.ai web | Fast, conversational |
| Work on files, run code, iterate | Claude Code (GUI) | Visual, easy file management |
| Automation, scripts, CI/CD | Claude Code CLI | Scriptable, reproducible |
| Risky/complex output | Add reviewer pass | Catches mistakes |
| Multi-step project | Explicit phases, one session each | Control without coordination overhead |

---

## When to Add Reviewer Pass

**Always review:**
- Code going to production
- Scripts that modify/delete data
- Anything involving money, auth, or PII
- Complex logic with edge cases

**Skip review:**
- One-off analysis
- Exploratory work
- Simple formatting/conversion
- Work you'll manually check anyway

---

## Workflow: Explicit Phases (Not Autonomous)

### Old Way (Autonomous — Don't Do This)
```
"Research Team, scrape pain points, analyze clusters, propose solutions"
→ Hope 5 agents coordinate correctly
→ Breaks in unpredictable ways
```

### New Way (Explicit Phases)
```
Session 1: "Scrape pain points from [forums]. Save to research/raw_data.md"
Session 2: "Analyze raw_data.md, cluster into themes. Save to clusters.md"
Session 3: "For each cluster, research solutions. Save to solutions.md"
Session 4: "Create final report from clusters.md + solutions.md"
[Optional] Session 5: "Reviewer, check final report for gaps and errors"
```

**Same outcome. More control. Less failure.**

---

## Folder Structure

```
project/
├── PROCEDURES.md          # Standard workflow (Claude reads first)
├── LESSONS.md             # Accumulated learnings (append after each project)
├── WORKBOARD.md           # Current status (simple, human-readable)
│
├── prompts/               # Reusable prompt templates
│   ├── scraper.md
│   ├── research_report.md
│   ├── data_analysis.md
│   ├── code_build.md
│   └── checklists/
│       ├── scraper_done.md
│       ├── code_done.md
│       └── research_done.md
│
├── components/            # Reusable code patterns
│   ├── scraper_base.py
│   ├── db_connector.py
│   ├── rate_limiter.py
│   └── README.md          # Index of what's here
│
├── projects/              # Active and past work
│   └── YYYY-MM-DD_project_name/
│       ├── BRIEF.md       # What we're building (the prompt)
│       ├── output/        # Deliverables
│       └── notes.md       # Project-specific learnings
│
└── inventory/             # Meta: what prompts/scripts exist
    ├── prompts_inventory.md
    ├── scripts_inventory.md
    └── lessons_compiled.md
```

---

## PROCEDURES.md (Claude Reads This First)

```markdown
# Standard Procedures

## Before Starting Any Task
1. Read LESSONS.md for relevant prior work
2. Check components/ for reusable code
3. Check prompts/ for similar task templates
4. State what "done" looks like before starting

## During Work
- One task at a time
- Save intermediate work (don't lose progress)
- If stuck for more than 2 attempts, state what's blocking

## Before Finishing Any Task
1. Run the relevant checklist from prompts/checklists/
2. Self-review: "If I were a critic, what would I flag?"
3. If complex/risky: request explicit reviewer pass
4. Add lessons to LESSONS.md (what worked, what didn't, reusable patterns)

## Output Standards
- Code: Include error handling, comments on non-obvious parts
- Scripts: Include usage example at top
- Research: Include sources, confidence levels, date of information
- All: State what's NOT included / out of scope
```

---

## LESSONS.md Template

```markdown
# Lessons Learned

## 2025-12-04: F990 Parser
**Project**: Parse IRS F990 XML files into database
**What worked**: 
- Chunking large XMLs before parsing (handles 50MB+ files)
- Using lxml instead of ElementTree (10x faster)
**What failed**: 
- First approach hit memory limits
- Assumed consistent schema (it varies by year)
**Reusable**: See `components/xml_chunker.py`
**Time spent**: ~3 hours

---

## 2025-12-01: Grant Scraper
**Project**: Scrape funder websites for grant opportunities
**What worked**:
- Playwright over requests (handles JS-heavy sites)
- Generic extraction patterns
**What failed**:
- CSS selectors broke across different sites (too specific)
**Reusable**: See `components/playwright_base.py`
**Time spent**: ~4 hours

---
```

---

## Prompt Template Structure

```markdown
## Context
[What exists, what you're working with — keep brief]

## Goal
[One sentence: what "done" looks like]

## Requirements
[Specific constraints, must-haves — bullet list]

## Output
[Exact deliverable: file type, location, format]

## Not In Scope
[What to explicitly skip — prevents scope creep]

## Reference
[Optional: point to components/, similar past work, examples]
```

---

## Example Prompts by Task Type

### Scraper
```markdown
## Context
Need to extract grant opportunities from [URL].

## Goal
Working scraper that extracts all grant listings into structured data.

## Requirements
- Handle pagination (if present)
- Rate limit: 1 request per 2 seconds
- Extract: grant name, deadline, amount, eligibility, URL
- Handle missing fields gracefully (null, don't crash)

## Output
- Script: projects/2025-12-04_grant_scraper/scraper.py
- Data: projects/2025-12-04_grant_scraper/output/grants.json

## Not In Scope
- Database insertion (separate task)
- Deduplication against existing data

## Reference
- Check components/playwright_base.py for starter pattern
- See LESSONS.md entry on grant scraper (CSS selector issues)
```

### Research Report
```markdown
## Context
Researching [topic] to inform [decision/project].

## Goal
Summary document with findings, suitable for [audience].

## Requirements
- Cover: [specific questions to answer]
- Sources: minimum 5, prefer primary sources
- Include: confidence level for each major claim
- Date-stamp information (AI/tech moves fast)

## Output
- Report: research/YYYY-MM-DD_topic/findings.md
- Sources: research/YYYY-MM-DD_topic/sources.md

## Not In Scope
- Implementation recommendations (separate task)
- Competitor pricing (can't reliably access)
```

### Data Analysis
```markdown
## Context
Database/file at [location] containing [description].

## Goal
[Specific question to answer with data]

## Requirements
- Handle nulls/missing data explicitly
- Show sample sizes for any statistics
- Visualizations: [specify if needed]
- Statistical tests: [specify or "recommend appropriate"]

## Output
- Analysis: projects/YYYY-MM-DD_analysis/analysis.md
- Code: projects/YYYY-MM-DD_analysis/analysis.py
- Charts: projects/YYYY-MM-DD_analysis/charts/ (if applicable)

## Not In Scope
- Causal claims (correlation only unless specified)
- Predictions beyond data range
```

---

## Checklists

### Code Done Checklist
```markdown
- [ ] Runs without errors
- [ ] Handles edge cases (empty input, large input, malformed input)
- [ ] Error messages are helpful (not just stack traces)
- [ ] No hardcoded secrets/paths (uses config or env vars)
- [ ] Has usage example or --help
- [ ] Comments on non-obvious logic
- [ ] Tested on real data (not just happy path)
```

### Scraper Done Checklist
```markdown
- [ ] Handles pagination
- [ ] Rate limiting implemented
- [ ] Retry logic for failures
- [ ] Data validated before save
- [ ] Tested on 3+ example pages
- [ ] Handles missing fields gracefully
- [ ] Output format documented
```

### Research Done Checklist
```markdown
- [ ] All questions addressed (or noted as unanswerable)
- [ ] Sources cited and accessible
- [ ] Confidence levels stated
- [ ] Date of information noted
- [ ] Contradictory findings acknowledged
- [ ] Limitations stated
- [ ] Next steps / open questions listed
```

---

## Multi-Phase Project Example

**Project**: Pain point research → business solutions

### Phase 1: Data Gathering
```
"Scrape pain points from [forums/sources]. 
Save raw data to research/pain_points/raw_data.md
Include: source, date, verbatim quote, context"
```

### Phase 2: Analysis
```
"Read research/pain_points/raw_data.md
Cluster into themes (group similar pain points)
Save to research/pain_points/clusters.md
Include: cluster name, count, representative quotes"
```

### Phase 3: Solution Research
```
"For each cluster in clusters.md:
- Research existing solutions
- Note gaps/opportunities
Save to research/pain_points/solutions.md"
```

### Phase 4: Synthesis
```
"Create final report combining clusters.md + solutions.md
Prioritize by: frequency × severity × solvability
Save to research/pain_points/final_report.md"
```

### Phase 5: Review (Optional)
```
"Reviewer, check final_report.md for:
- Logical gaps
- Unsupported claims  
- Missing obvious solutions
- Clarity for non-expert reader"
```

---

## What NOT to Do

| Don't | Why | Instead |
|-------|-----|---------|
| "Do the whole project" | Too vague, loses control | Explicit phases |
| Autonomous agent coordination | Unreliable, hard to debug | You orchestrate |
| Complex state management | Overhead exceeds benefit | WORKBOARD.md + LESSONS.md |
| Multiple agents per session | Same model anyway | One agent, clear task |
| Skip the review on risky work | You'll regret it | Add reviewer pass |
| Rebuild from scratch each time | Wastes time | Use components/, templates |

---

## When to Scale Up (Signs You Need More)

- Same prompt patterns repeated 10+ times → Formalize template
- Same code patterns in 3+ scripts → Extract to component
- Projects failing at handoffs → Add explicit phase boundaries
- Spending more time coordinating than doing → Simplify further
- True parallelism needed (independent tasks) → Multiple terminals

---

## Quick Reference

**Start a task:**
```
[Read PROCEDURES.md first]
[One clear goal]
[Run checklist when done]
[Add to LESSONS.md]
```

**Choose your tool:**
- Quick/conversational → Claude.ai
- Files/iteration → Claude Code GUI
- Automation/scripts → Claude Code CLI
- Risky output → Add reviewer pass

**End of day:**
- Update WORKBOARD.md if mid-project
- Add any learnings to LESSONS.md
- Commit work to git

---

## Migration from Old System

1. **Keep**: LESSONS.md concept, prompt templates idea, component reuse
2. **Drop**: 16 agents, mailbox.jsonl, state.json, gates, complex handoffs
3. **Simplify**: One agent per task, you orchestrate phases, minimal files

**The goal**: Spend time on work, not on managing the system that manages the work.
