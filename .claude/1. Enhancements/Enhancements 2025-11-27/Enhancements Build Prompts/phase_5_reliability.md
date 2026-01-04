# Phase 5: Reliability (Checkpoints + Error Handling)

## Objective

Make the system resilient to failures:

1. **Checkpoints** - Save progress at intervals so failures don't lose everything
2. **Error Handling Tiers** - Auto-retry common errors, escalate serious ones
3. **Recovery Protocol** - Clear process to resume from checkpoints

Currently, if extraction fails at 80%, you restart from 0%. This phase fixes that.

---

## Context

### The Problem

```
Scout processing 61 CDFIs...
  ✓ CDFI 1-50 complete
  ✗ CDFI 51 fails (network error)
  
Current behavior: Start over from CDFI 1
Desired behavior: Resume from CDFI 51
```

### Checkpoint Strategy

Save state every N items (configurable). Checkpoints include:
- Items processed so far
- Items remaining
- Partial results
- Quality metrics to date
- Timestamp

---

## Tasks

### 1. Add Checkpoint Schema to State.json

Update state.json to support checkpoints in each phase:

```json
{
  "phases": {
    "extraction": {
      "status": "in_progress",
      "claimed_by": "scout",
      "started_at": "2025-11-18T10:00:00Z",
      "checkpoints": {
        "enabled": true,
        "frequency": 10,
        "last_checkpoint": {
          "id": "extraction_cp_50",
          "timestamp": "2025-11-18T12:30:00Z",
          "items_processed": 50,
          "items_remaining": 11,
          "checkpoint_file": "checkpoints/extraction_cp_50.json"
        }
      }
    }
  }
}
```

### 2. Create Checkpoints Folder

Create `.claude/state/checkpoints/` with a README:

```markdown
# Checkpoints Directory

This folder stores checkpoint files for long-running operations.

## Checkpoint Format

Each checkpoint is a JSON file:
```json
{
  "checkpoint_id": "extraction_cp_50",
  "phase": "extraction",
  "agent": "scout",
  "timestamp": "2025-11-18T12:30:00Z",
  "processed": ["item1", "item2", ...],
  "remaining": ["item51", "item52", ...],
  "partial_results_file": "research_outputs/02_extractor/partial_50.json",
  "metrics": {
    "success_rate": 0.94,
    "avg_quality": 0.52
  },
  "can_resume": true,
  "notes": "Optional notes about state at checkpoint"
}
```

## Resuming from Checkpoint

To resume: "Scout, resume extraction from checkpoint extraction_cp_50"

Agent will:
1. Read checkpoint file
2. Load partial results
3. Continue with remaining items
4. Create new checkpoints as it progresses
```

### 3. Add Checkpoint Protocol to Long-Running Agents

Add this section to these agents: scout.md, analyst.md, builder.md, data-engineer.md

```markdown
## Checkpoint Protocol

For tasks processing multiple items (>10), save checkpoints:

### When to Checkpoint
- Every 10 items processed (configurable via state.json)
- Before any risky operation
- When pausing for any reason

### How to Checkpoint
1. Create checkpoint file: `.claude/state/checkpoints/[phase]_cp_[count].json`
2. Include: processed items, remaining items, partial results path, metrics
3. Update state.json with last_checkpoint reference
4. Log checkpoint event to mailbox

### Checkpoint File Format
```json
{
  "checkpoint_id": "[phase]_cp_[count]",
  "phase": "[current phase]",
  "agent": "[your name]",
  "timestamp": "[ISO timestamp]",
  "processed": ["list of completed item IDs"],
  "remaining": ["list of remaining item IDs"],
  "partial_results_file": "[path to partial results]",
  "metrics": { "relevant": "metrics" },
  "can_resume": true
}
```

### Resuming from Checkpoint
When instructed to resume:
1. Read the specified checkpoint file
2. Verify partial_results_file exists and is valid
3. Load remaining items list
4. Continue processing from where checkpoint left off
5. Create new checkpoints as you progress
```

### 4. Add Error Handling Tiers to All Agents

Add this section to ALL agent .md files:

```markdown
## Error Handling Protocol

### Tier 1: Auto-Retry (Handle Silently)
These errors are temporary. Retry automatically:

| Error | Action | Max Retries |
|-------|--------|-------------|
| Network timeout | Wait 30s, retry | 3 |
| Rate limit (429) | Exponential backoff (30s, 60s, 120s) | 3 |
| Server error (5xx) | Wait 10s, retry | 3 |
| Temporary file lock | Wait 5s, retry | 3 |

After max retries, escalate to Tier 2.

### Tier 2: Skip and Continue (Log Warning)
These errors affect single items. Log and continue:

| Error | Action |
|-------|--------|
| Single item fails extraction | Log failure, continue to next item |
| Optional field missing | Use default/null, continue |
| Non-critical validation warning | Log warning, don't block |

Log format:
```json
{"timestamp":"...","agent":"...","event":"item_skipped","item":"...","reason":"...","will_retry":false}
```

### Tier 3: Stop and Escalate (Human Required)
These errors need human attention:

| Error | Action |
|-------|--------|
| Authentication failure | Stop, request credentials |
| >20% of items failing | Stop, request review |
| Critical data corruption | Stop, preserve state |
| Unknown/unexpected error | Stop, log details |

When escalating:
1. Save checkpoint immediately
2. Log detailed error to mailbox with event "escalation_required"
3. Update state.json status to "blocked"
4. Clearly state what went wrong and what's needed to proceed
```

### 5. Create Recovery Guide

Create `.claude/guides/RECOVERY_GUIDE.md`:

```markdown
# Recovery Guide

## Resuming from Failure

### Step 1: Check What Happened
```
You: "/status"
```
or
```
You: "Router, what's the current state?"
```

### Step 2: Find Last Checkpoint
```bash
ls -la .claude/state/checkpoints/
```
Find the most recent checkpoint for the failed phase.

### Step 3: Verify Checkpoint
```bash
cat .claude/state/checkpoints/[checkpoint_file].json | python -m json.tool
```
Check that `can_resume: true` and `partial_results_file` exists.

### Step 4: Resume
```
You: "[Agent], resume from checkpoint [checkpoint_id]"
```

Example:
```
You: "Scout, resume extraction from checkpoint extraction_cp_50"
```

### Step 5: Monitor
Watch for new checkpoint creation to confirm progress.

---

## Common Recovery Scenarios

### Scenario: Network Failure Mid-Extraction
1. Scout was extracting, network died
2. Check last checkpoint: `extraction_cp_30`
3. Resume: "Scout, resume extraction from checkpoint extraction_cp_30"
4. Scout continues from item 31

### Scenario: Terminal Closed Accidentally
1. Reopen terminal, navigate to project
2. Run /status to see current state
3. Last checkpoint shows progress saved
4. Resume from checkpoint

### Scenario: Agent Made Bad Decisions
1. Identify last good checkpoint
2. Delete checkpoints after that point
3. Resume from good checkpoint
4. Optionally: add guidance to prevent same mistake

---

## Checkpoint Hygiene

### After Successful Completion
Checkpoints are kept for debugging. To clean up:

**PowerShell:**
```powershell
# Archive old checkpoints
New-Item -ItemType Directory -Force .claude\state\checkpoints\archive\
Move-Item .claude\state\checkpoints\*.json .claude\state\checkpoints\archive\

# Or delete if not needed
Remove-Item .claude\state\checkpoints\[project]_*.json
```

**Git Bash:**
```bash
mv .claude/state/checkpoints/*.json .claude/state/checkpoints/archive/
rm .claude/state/checkpoints/[project]_*.json
```

### Checkpoint Retention
- Keep checkpoints for 30 days
- Archive after project completion
- Delete archived checkpoints after 90 days
```

---

## Constraints

- Checkpoints must be valid JSON
- Checkpoint files must be small (<100KB each)
- Error handling must not hide critical issues
- Tier 3 errors MUST stop processing (no silent failures)
- All agents must get the same Error Handling Protocol section
- Recovery must be possible from any checkpoint

---

## Success Criteria

After completion, verify:

- [ ] state.json schema supports checkpoints in phases
- [ ] `.claude/state/checkpoints/` folder exists with README
- [ ] scout.md has Checkpoint Protocol section
- [ ] analyst.md has Checkpoint Protocol section
- [ ] builder.md has Checkpoint Protocol section
- [ ] data-engineer.md has Checkpoint Protocol section
- [ ] ALL agents have Error Handling Protocol section
- [ ] `.claude/guides/RECOVERY_GUIDE.md` exists
- [ ] Error handling tiers are consistent across agents

---

## Validation

After completing all tasks:

**PowerShell:**
```powershell
# Check checkpoints folder
Get-ChildItem .claude\state\checkpoints\

# Check Checkpoint Protocol in long-running agents
@("scout", "analyst", "builder", "data-engineer") | ForEach-Object {
    $has = Select-String -Path ".claude\agents\$_.md" -Pattern "Checkpoint Protocol" -Quiet
    if ($has) { Write-Host "$_`: ✓ Checkpoint" } else { Write-Host "$_`: MISSING Checkpoint" }
}

# Check Error Handling in all agents
Get-ChildItem .claude\agents\*.md | ForEach-Object {
    $has = Select-String -Path $_.FullName -Pattern "Error Handling Protocol" -Quiet
    if ($has) { Write-Host "$($_.Name): ✓ Error Handling" } else { Write-Host "$($_.Name): MISSING Error Handling" }
}

# Check Recovery Guide exists
Get-Item .claude\guides\RECOVERY_GUIDE.md

# Validate state.json still valid
Get-Content .claude\state\state.json | ConvertFrom-Json
```

**Or Git Bash:**
```bash
ls -la .claude/state/checkpoints/

for agent in scout analyst builder data-engineer; do
  grep -q "Checkpoint Protocol" .claude/agents/$agent.md && echo "$agent: ✓ Checkpoint" || echo "$agent: MISSING Checkpoint"
done

for agent in .claude/agents/*.md; do
  grep -q "Error Handling Protocol" "$agent" && echo "$agent: ✓ Error Handling" || echo "$agent: MISSING Error Handling"
done

ls -la .claude/guides/RECOVERY_GUIDE.md

cat .claude/state/state.json | python -m json.tool > /dev/null && echo "state.json valid" || echo "state.json INVALID"
```

Then manually test checkpoint flow:

**Test 1: Checkpoint Creation**
```
You: "Scout, pretend you're extracting 20 items. Create a checkpoint after 'processing' 10 of them."

Expected:
1. Scout creates .claude/state/checkpoints/test_cp_10.json
2. Checkpoint contains processed/remaining lists
3. state.json updated with last_checkpoint reference
```

**Test 2: Checkpoint Resume**
```
You: "Scout, resume from checkpoint test_cp_10"

Expected:
1. Scout reads the checkpoint file
2. Reports: "Resuming from checkpoint. 10 items already processed, 10 remaining."
3. Continues from item 11
```

**Test 3: Error Handling Tier 1**
```
You: "Scout, what would you do if you got a 429 rate limit error?"

Expected:
Scout explains: "Tier 1 error. I would wait 30 seconds and retry, up to 3 times with exponential backoff."
```

---

## Rollback

If something goes wrong:

**PowerShell:**
```powershell
git checkout -- .claude\agents\
git checkout -- .claude\state\state.json
Remove-Item -Recurse -Force .claude\state\checkpoints\
Remove-Item .claude\guides\RECOVERY_GUIDE.md
```

**Or Git Bash:**
```bash
git checkout -- .claude/agents/
git checkout -- .claude/state/state.json
rm -rf .claude/state/checkpoints/
rm .claude/guides/RECOVERY_GUIDE.md
```

---

## Completion

After all 5 phases are validated, you have:

✅ **Foundation**: Folder structure, token tracking, memory skeleton, /status command
✅ **Brain**: Router agent, task graph, dependency checking
✅ **Communication**: Phase summaries, handoff protocol, mailbox rotation
✅ **Optimization**: Model tiering (Haiku/Sonnet), permission scoping, fallback protocol
✅ **Reliability**: Checkpoints, error handling tiers, recovery guide

The system is now ready for production use with:
- Lower costs (Haiku for simple agents)
- Better security (scoped permissions)
- Failure recovery (checkpoints)
- Cleaner communication (phase summaries)
- Intelligent orchestration (Router + task graph)

🎉 **Congratulations!**
