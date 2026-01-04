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

### Scenario: Rate Limited by API
1. Agent hits Tier 1 error (429)
2. Auto-retry with exponential backoff kicks in
3. If still failing after 3 retries, escalates to Tier 2
4. Check mailbox.jsonl for "item_skipped" events
5. May need to wait longer or reduce request rate

### Scenario: >20% Items Failing
1. Agent stops (Tier 3 escalation)
2. Check mailbox for "escalation_required" event
3. Review failure reasons in logs
4. Fix underlying issue (credentials, data format, etc.)
5. Resume from last checkpoint

---

## Error Handling Tiers Reference

### Tier 1: Auto-Retry
- Network timeout → Wait 30s, retry (max 3)
- Rate limit (429) → Exponential backoff (max 3)
- Server error (5xx) → Wait 10s, retry (max 3)
- File lock → Wait 5s, retry (max 3)

### Tier 2: Skip and Continue
- Single item fails → Log, continue to next
- Optional field missing → Use default, continue
- Non-critical warning → Log, don't block

### Tier 3: Stop and Escalate
- Authentication failure → Stop, request credentials
- >20% items failing → Stop, request review
- Data corruption → Stop, preserve state
- Unknown error → Stop, log details

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
mkdir -p .claude/state/checkpoints/archive/
mv .claude/state/checkpoints/*.json .claude/state/checkpoints/archive/
# Or delete
rm .claude/state/checkpoints/[project]_*.json
```

### Checkpoint Retention
- Keep checkpoints for 30 days
- Archive after project completion
- Delete archived checkpoints after 90 days

---

## Debugging Failed Operations

### Check Mailbox for Errors
```bash
# Last 20 events
tail -20 .claude/state/mailbox.jsonl

# Filter for errors
grep "error\|failed\|skipped\|escalation" .claude/state/mailbox.jsonl
```

### Check State for Blocked Tasks
```bash
cat .claude/state/state.json | python -m json.tool | grep -A5 "blocked"
```

### Verify Checkpoint Integrity
```bash
# Check all checkpoints are valid JSON
for f in .claude/state/checkpoints/*.json; do
  python -m json.tool "$f" > /dev/null && echo "$f: OK" || echo "$f: INVALID"
done
```

---

## Emergency Recovery

### If State Files Are Corrupted
```bash
# Restore from git (if committed)
git checkout -- .claude/state/state.json
git checkout -- .claude/state/mailbox.jsonl

# Or restore from backup
cp .claude/state/state.json.backup .claude/state/state.json
```

### If Checkpoint Is Invalid
1. Delete the invalid checkpoint
2. Find the previous valid checkpoint
3. Resume from the valid checkpoint (may reprocess some items)

### If Everything Is Broken
1. Stop all agent work
2. Backup current state: `cp -r .claude/state .claude/state.backup`
3. Reset state.json to clean state
4. Manually review what was completed
5. Update state.json to reflect actual progress
6. Resume operations

---

## Prevention Tips

1. **Commit checkpoints to git** - Can restore if files corrupted
2. **Run mailbox rotation regularly** - Keeps mailbox bounded
3. **Monitor failure rates** - Address issues before hitting 20% threshold
4. **Test on small batches first** - Catch errors early
5. **Document API rate limits** - Know when to slow down
