# Phase 4: Optimization (Model Tiering + Permissions)

## Objective

Right-size the system for cost and security:

1. **Model Tiering** - Use Haiku for simple agents, Sonnet for complex reasoning
2. **Permission Scoping** - Restrict each agent to only the tools they need
3. **Fallback Protocol** - If Haiku fails, escalate to Sonnet

Currently all 11 agents use Sonnet with full tool access. This is expensive and insecure.

---

## Context

### Model Tiers

| Model | Cost | Speed | Use For |
|-------|------|-------|---------|
| Haiku | $1/$5 per MTok | 2x faster | Simple tasks, routing, formatting |
| Sonnet | $3/$15 per MTok | Baseline | Analysis, coding, reasoning |
| Opus | $15/$75 per MTok | Slower | Complex reasoning (rarely needed) |

### Current State

All agents have:
```yaml
model: sonnet
tools: [everything]
```

### Target State

Agents matched to appropriate model and minimal tools.

---

## Tasks

### 1. Apply Model Tiering

Update the `model:` field in each agent's YAML frontmatter:

| Agent | Current | New Model | Reasoning |
|-------|---------|-----------|-----------|
| router.md | sonnet | **haiku** | Just reads state, simple decisions |
| scout.md | sonnet | **haiku** | Mostly web fetching, categorization |
| reporter.md | sonnet | **haiku** | Formatting and document generation |
| analyst.md | sonnet | sonnet | Statistical reasoning required |
| synthesizer.md | sonnet | sonnet | Strategic thinking required |
| validator.md | sonnet | sonnet | Critical QA, needs accuracy |
| builder.md | sonnet | sonnet | Code generation |
| builder-1.md | sonnet | sonnet | Code generation |
| builder-2.md | sonnet | sonnet | Code generation |
| builder-3.md | sonnet | sonnet | Code generation |
| reviewer.md | sonnet | sonnet | Code review needs nuance |
| project-manager.md | sonnet | sonnet | Planning requires reasoning |
| problem-solver.md | sonnet | sonnet | Debugging is complex |
| ml-engineer.md | sonnet | sonnet | ML work is complex |
| data-engineer.md | sonnet | sonnet | Data work is complex |

**Change these 3 agents to Haiku**:
- router.md
- scout.md  
- reporter.md

### 2. Apply Permission Scoping

Update the `tools:` field in each agent based on what they actually need:

| Agent | New Tools | Removed | Reasoning |
|-------|-----------|---------|-----------|
| **router.md** | `Read` | All others | Only reads state, never modifies |
| **scout.md** | `Read, WebSearch, WebFetch, Write` | Bash, Edit, Grep | Discovery doesn't need code execution |
| **analyst.md** | `Read, Write, Bash` | WebSearch, WebFetch, Edit | Analysis is local, needs Python |
| **synthesizer.md** | `Read, Write, WebSearch` | Bash, Edit | Research synthesis, no code |
| **validator.md** | `Read, WebSearch, WebFetch` | Write, Bash, Edit | QA should NOT modify data it validates |
| **reporter.md** | `Read, Write` | All others | Just reads and writes docs |
| **builder.md** | `Read, Write, Edit, Bash, Grep, Glob` | None | Needs full dev access |
| **builder-1/2/3.md** | `Read, Write, Edit, Bash, Grep, Glob` | None | Needs full dev access |
| **reviewer.md** | `Read, Bash, Grep, Glob` | Write, Edit | Reviews code, shouldn't modify |
| **project-manager.md** | `Read, Write, Bash, Grep, Glob` | Edit | Plans work, updates docs |
| **problem-solver.md** | `Read, Write, Edit, Bash, Grep, Glob, WebSearch` | None | Needs everything to debug |
| **ml-engineer.md** | `Read, Write, Edit, Bash, Grep, Glob` | WebSearch | ML work is local |
| **data-engineer.md** | `Read, Write, Edit, Bash, Grep, Glob` | WebSearch | Data work is local |

**Key restrictions**:
- Validator: NO Write (can't modify what it's validating)
- Reviewer: NO Write/Edit (can't modify code it's reviewing)
- Router: Read ONLY (never modifies anything)

### 3. Add Fallback Protocol

Add this section to the 3 Haiku agents (router.md, scout.md, reporter.md):

```markdown
## Model Fallback Protocol

This agent uses Haiku for speed and cost efficiency. If you encounter:
- Repeated failures on the same task (2+ attempts)
- Tasks requiring complex reasoning beyond categorization
- Unexpected edge cases that Haiku struggles with

Escalation path:
1. Log the issue to mailbox.jsonl with event "haiku_escalation"
2. Recommend human invoke the Sonnet version: "Re-run with --model sonnet"
3. Include details of what failed and why

Do NOT attempt complex reasoning tasks. Delegate to appropriate Sonnet agent instead.
```

### 4. Update TEAM_COLLABORATION_GUIDE.md

Add a section explaining the model tiering:

```markdown
## Model Tiering

Agents use different Claude models based on task complexity:

### Haiku Agents (Fast, Cheap)
- **Router**: Workflow decisions
- **Scout**: Data discovery
- **Reporter**: Document formatting

### Sonnet Agents (Balanced)
- All other agents

### When to Override
If a Haiku agent struggles, you can force Sonnet:
```
Scout --model sonnet, do complex analysis on these sites
```

### Cost Implications
- Haiku: ~$1 per million tokens
- Sonnet: ~$3 per million tokens
- Using Haiku for Scout/Reporter saves ~60% on those agents
```

---

## Constraints

- Only change `model:` and `tools:` in YAML frontmatter
- Do NOT change agent logic or responsibilities
- Do NOT remove tools that agents genuinely need
- Validator must NOT have Write access (critical for QA integrity)
- Reviewer must NOT have Edit access (critical for review integrity)
- All agents must remain functional after changes

---

## Success Criteria

After completion, verify:

- [ ] router.md has `model: haiku`
- [ ] scout.md has `model: haiku`
- [ ] reporter.md has `model: haiku`
- [ ] All other agents still have `model: sonnet`
- [ ] validator.md does NOT have Write, Edit, or Bash in tools
- [ ] reviewer.md does NOT have Write or Edit in tools
- [ ] router.md only has Read in tools
- [ ] Haiku agents have Fallback Protocol section
- [ ] TEAM_COLLABORATION_GUIDE.md has Model Tiering section

---

## Validation

After completing all tasks:

**PowerShell:**
```powershell
# Check model assignments
Write-Host "=== Model Check ==="
Get-ChildItem .claude\agents\*.md | ForEach-Object {
    $model = Select-String -Path $_.FullName -Pattern "^model:" | Select-Object -First 1
    Write-Host "$($_.Name): $($model.Line)"
}

# Check Haiku agents
Write-Host "=== Haiku Agents ==="
Select-String -Path .claude\agents\*.md -Pattern "model: haiku" | ForEach-Object { $_.Filename }

# Check Validator has no Write
Write-Host "=== Validator Tools ==="
Select-String -Path .claude\agents\validator.md -Pattern "^tools:"

# Check Reviewer has no Edit  
Write-Host "=== Reviewer Tools ==="
Select-String -Path .claude\agents\reviewer.md -Pattern "^tools:"

# Check Router is Read-only
Write-Host "=== Router Tools ==="
Select-String -Path .claude\agents\router.md -Pattern "^tools:"

# Check Fallback Protocol exists in Haiku agents
Write-Host "=== Fallback Protocol ==="
@("router", "scout", "reporter") | ForEach-Object {
    $has = Select-String -Path ".claude\agents\$_.md" -Pattern "Fallback Protocol" -Quiet
    if ($has) { Write-Host "$_.md: ✓" } else { Write-Host "$_.md: MISSING" }
}
```

**Or Git Bash:**
```bash
echo "=== Model Check ==="
for agent in .claude/agents/*.md; do
  model=$(grep "^model:" "$agent" | head -1)
  echo "$agent: $model"
done

echo "=== Haiku Agents ==="
grep -l "model: haiku" .claude/agents/*.md

echo "=== Validator Tools ==="
grep "^tools:" .claude/agents/validator.md

echo "=== Reviewer Tools ==="
grep "^tools:" .claude/agents/reviewer.md

echo "=== Router Tools ==="
grep "^tools:" .claude/agents/router.md

echo "=== Fallback Protocol ==="
for agent in router scout reporter; do
  grep -q "Fallback Protocol" .claude/agents/$agent.md && echo "$agent.md: ✓" || echo "$agent.md: MISSING"
done
```

Then manually test:

**Test 1: Haiku agent works**
```
You: "Scout, search for 'test query'"
Expected: Scout works normally (should be slightly faster)
```

**Test 2: Permission restriction works**
```
You: "Validator, write a test file to outputs/test.txt"
Expected: Validator refuses or errors (no Write tool)
```

**Test 3: Reviewer can't edit**
```
You: "Reviewer, fix this typo in src/main.py"
Expected: Reviewer refuses or explains it can only review, not edit
```

---

## Rollback

If something goes wrong:

**PowerShell:**
```powershell
git checkout -- .claude\agents\
git checkout -- .claude\TEAM_COLLABORATION_GUIDE.md
```

**Or Git Bash:**
```bash
git checkout -- .claude/agents/
git checkout -- .claude/TEAM_COLLABORATION_GUIDE.md
```

---

## Next Phase

Once validated, proceed to Phase 5: Reliability (Checkpoints + Error Handling)
