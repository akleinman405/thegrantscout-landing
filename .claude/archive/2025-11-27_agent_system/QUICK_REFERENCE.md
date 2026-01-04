# Multi-Agent Team Quick Reference

**Last Updated**: 2025-11-27

---

## The Easy Way (Recommended)

Just talk to the teams. They manage everything.

**Research project:**
```
Research Team, please complete this:
- Prompt: path/to/my_questions.md
- Output: path/to/outputs/
```

**Dev project:**
```
Dev Team, please build this:
- Prompt: path/to/build_spec.md
- Output: path/to/src/
```

**Or after describing something:**
```
[your description of what you need]

Have the research team do this.
```

```
[your feature requirements]

Have the dev team build this. Put the code in src/my_feature/
```

That's it. The team will:
1. Review your prompt (two agents give feedback)
2. Create a plan
3. Assign work to team members
4. Manage the whole pipeline
5. Deliver results to your output folder
6. Update memory/lessons learned

---

## Commands

| Command | What It Does |
|---------|--------------|
| `/status` | Show current project state, tasks, recent events |
| `Router, what's next?` | Get recommendation for next action |

---

## Teams

| Team | Use For | Members |
|------|---------|---------|
| **Research Team** | Any research/analysis project | Scout, Analyst, Synthesizer, Validator, Reporter |
| **Dev Team** | Any build/coding project | Project-Manager, Builders 1-3, Reviewer, Problem-Solver, ML-Engineer, Data-Engineer |

---

## Direct Agent Access (Optional)

### Research Team (5 Agents)

| Agent | Model | Use For | Example |
|-------|-------|---------|---------|
| **Scout** | Haiku | Web research, data discovery | `Scout, find CDFIs offering affordable housing funding in California` |
| **Analyst** | Sonnet | Statistical analysis, modeling | `Analyst, analyze the data in research_outputs/01_scout/` |
| **Synthesizer** | Sonnet | Strategic insights, recommendations | `Synthesizer, identify top opportunities from the analysis` |
| **Validator** | Sonnet | QA, fact-checking (read-only) | `Validator, verify the URLs and data quality` |
| **Reporter** | Haiku | Final documentation | `Reporter, create executive summary and deliverables` |

**Research Flow:** Scout → Analyst → Synthesizer → Validator → Reporter

---

### Dev Team (9 Agents)

| Agent | Model | Use For | Example |
|-------|-------|---------|---------|
| **Project-Manager** | Sonnet | Planning, task breakdown | `Project-Manager, break down the auth feature into tasks` |
| **Builder 1/2/3** | Sonnet | Code implementation | `Builder-1, implement the login endpoint` |
| **Reviewer** | Sonnet | Code review (read-only) | `Reviewer, review the PR in src/auth/` |
| **Problem-Solver** | Sonnet | Debugging, blockers | `Problem-solver, help debug the API timeout issue` |
| **ML-Engineer** | Sonnet | Machine learning | `ML-engineer, train the grant matching model` |
| **Data-Engineer** | Sonnet | Data pipelines, ETL | `Data-engineer, optimize the database queries` |

**Dev Flow:** Project-Manager → Builders → Reviewer → Done

---

### Orchestration (2 Agents)

| Agent | Model | Use For | Example |
|-------|-------|---------|---------|
| **Router** | Haiku | Workflow decisions, what's next | `Router, what's next?` |
| **CDFI-Extractor** | Sonnet | Specialized CDFI data extraction | `CDFI-Extractor, extract funding data from [site]` |

---

## After Completing a Project

1. **Record lessons learned:**
   ```
   Reporter, add lessons learned to .claude/memory/lessons.md
   ```

2. **Create project summary:**
   ```
   Reporter, create project summary in .claude/memory/projects/2025-11-27_[name]/
   ```

3. **Rotate mailbox (optional):**
   ```powershell
   .\.claude\scripts\rotate_mailbox.ps1
   ```
   ```bash
   ./.claude/scripts/rotate_mailbox.sh
   ```

4. **Commit:**
   ```powershell
   git add -A
   git commit -m "Project [name] complete"
   ```

---

## Key Locations

| Path | Contents |
|------|----------|
| `.claude/agents/` | Agent definitions (18 total) |
| `.claude/state/state.json` | Current project state |
| `.claude/state/mailbox.jsonl` | Event log |
| `.claude/state/task_graph.json` | Pipeline dependencies |
| `.claude/state/checkpoints/` | Recovery points |
| `.claude/memory/lessons.md` | Team learnings |
| `.claude/memory/projects/` | Past project summaries |
| `research_outputs/` | Research team outputs |
| `ARTIFACTS/` | Handoff documents between teams |

---

## Error Recovery

**If something fails mid-task:**
```
Router, what's the current state?
```

**Resume from checkpoint:**
```
Scout, resume from checkpoint [checkpoint_id]
```

**Check available checkpoints:**
```powershell
Get-ChildItem .claude\state\checkpoints\
```
```bash
ls .claude/state/checkpoints/
```

---

## Tips

- **Use team orchestrators** - `Dev Team` and `Research Team` manage everything
- **Router first** - When unsure what to do, ask Router
- **Phase summaries** - Agents create `phase_summary.md` for handoffs
- **Validator is read-only** - Can't modify what it's checking
- **Reviewer is read-only** - Can't edit code it's reviewing
- **Haiku agents** (Scout, Reporter, Router) - Fast and cheap
- **Sonnet agents** - Better reasoning, use for complex tasks

---

## Starting a New Project

**Option 1: Point to a prompt file**
```
Research Team, please complete this:
- Prompt: 02_RESEARCH_FOUNDATION/my_topic/questions.md
- Output: 02_RESEARCH_FOUNDATION/my_topic/outputs/
```

**Option 2: Describe inline, then hand off**
```
I need to understand the CDFI funding landscape in California.
Find the top 20 CDFIs, their funding amounts, and eligibility requirements.
Output as CSV and executive summary.

Have the research team do this. Put outputs in 02_RESEARCH_FOUNDATION/cdfi_california/
```

**Option 3: Simple and direct**
```
Dev Team, build a web scraper for foundation grant data.
Use Python/FastAPI. Output to src/scraper/
```

**Check status anytime:**
```
/status
```

---

## Prompt File Tips

Your prompt file should include:

**For Research:**
- Clear objective
- Specific questions
- Scope (how many sources, what geography, timeframe)
- Output format wanted (CSV, report, both)

**For Dev:**
- What you're building
- Features/requirements
- Tech stack preferences
- Where code should go

---

## Total System: 18 Agents

| Category | Agents | Count |
|----------|--------|-------|
| Team Orchestrators | dev-team, research-team | 2 |
| Dev Team | project-manager, builder, builder-1/2/3, reviewer, problem-solver, ml-engineer, data-engineer | 9 |
| Research Team | scout, analyst, synthesizer, validator, reporter | 5 |
| Orchestration | router | 1 |
| Specialized | cdfi-extractor | 1 |

---

## See Also

- `SYSTEM_OVERVIEW.md` - Full system architecture and capabilities
- `TEAM_COLLABORATION_GUIDE.md` - Cross-team coordination
- `guides/ROUTER_GUIDE.md` - Router usage
- `guides/RECOVERY_GUIDE.md` - Error recovery procedures
