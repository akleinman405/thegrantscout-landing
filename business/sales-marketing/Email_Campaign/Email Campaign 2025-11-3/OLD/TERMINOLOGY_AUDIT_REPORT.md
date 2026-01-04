# Terminology Audit Report
## Email Campaign Scripts - 2025-11-12

### Executive Summary

This audit identifies confusing terminology in the email campaign scripts where messages say "today" or "sent today" but actually refer to different time windows. The user's concern is valid: the scripts mix terminology between:
- **Last 24 hours (rolling window)** - Used for rate limiting
- **Today's allocation (coordination file)** - Used for script coordination
- **This run (current session)** - Actual sends in this execution

### Critical Findings

#### Finding 1: "Remaining today" is MISLEADING (HIGH PRIORITY)

**Location**: `send_initial_outreach.py` line 918
```python
print(f"✅ Remaining today: {daily_limit_remaining} emails\n")
```

**What it actually shows**: `daily_limit_remaining` = `TOTAL_DAILY_LIMIT - emails_last_24h`

**Problem**: This says "Remaining today" but it's actually showing "Remaining in the rolling 24-hour window". These are NOT the same thing!

**Example of confusion**:
- It's 9am on Tuesday
- Yesterday (Monday) at 9am: sent 100 emails
- Yesterday (Monday) at 3pm: sent 100 emails  
- Display shows: "Remaining today: 100 emails"
- User thinks: "I can only send 100 more today"
- Reality: By 3pm today, yesterday's 9am emails will be >24h old, freeing up 100 more capacity

**Fix Required**: Change to "Remaining in rolling 24h window: X emails"

---

#### Finding 2: "Already sent today" is AMBIGUOUS (HIGH PRIORITY)

**Location**: `send_initial_outreach.py` line 957
```python
print(f"║  Already sent today:              {allocated_capacity - remaining_capacity:<24} ║")
```

**Location**: `send_followup.py` line 788
```python
print(f"║  Already sent today:              {allocated_capacity - remaining_capacity:<24} ║")
```

**What it actually shows**: This is showing emails sent IN THIS ALLOCATION (from coordination file), NOT in the last 24 hours, and NOT from start of calendar day.

**Problem**: "Already sent today" could mean:
1. Sent since midnight (calendar day)
2. Sent in last 24 hours (rolling window)
3. Sent from this allocation (coordination)

**Reality**: It's #3, but users might think it's #1 or #2.

**Fix Required**: Change to "Already sent (this allocation): X"

---

#### Finding 3: Progress display says "today" but means "this run" (MEDIUM PRIORITY)

**Location**: `send_initial_outreach.py` line 725
```python
print(f"[{timestamp}] ✓ Sent to {email} ({vertical_name}, {first_name_display}) ({total_sent}/{total_to_send} today)")
```

**Location**: `send_followup.py` line 535
```python
print(f"[{timestamp}] ✓ Follow-up sent to {email} ({vertical_name}, {first_name_display}) ({total_sent}/{total_to_send} today)")
```

**What it shows**: Progress in THIS execution/run

**Problem**: Says "today" but `total_to_send` is not "all emails for today" - it's just "emails in this batch/run"

**Fix Required**: Change to "(X/Y in this batch)" or "(X/Y this run)"

---

#### Finding 4: "Total allocated today" is clear but incomplete (LOW PRIORITY)

**Location**: `send_initial_outreach.py` line 956
```python
print(f"║  Total allocated today:           {allocated_capacity:<24} ║")
```

**What it shows**: Allocation from coordination system for this script

**Assessment**: This is relatively clear, but could be enhanced to show it's from coordination.

**Suggested Enhancement**: Add context that this is from the coordination system, and that it's different from the rolling 24h capacity.

---

### Additional Observations

#### Observation 1: No display of rolling capacity breakdown

**Problem**: The scripts calculate emails sent in last 24 hours, but don't show WHEN those emails will age out, or how much capacity will become available as time passes.

**Impact**: Users cannot see:
- How many emails will age out by end of business hours
- Optimal send schedule to maximize throughput
- Whether they should wait an hour for more capacity

**Fix Required**: Implement rolling capacity analysis (see Problem 2 in main task)

---

#### Observation 2: Two different "capacity" concepts are mixed

**Concept A: Daily Limit Capacity (Rolling 24h)**
- Enforced by: `get_emails_sent_last_24h()`
- Limit: 300 emails in any 24-hour period
- Purpose: Rate limiting to avoid spam flags

**Concept B: Allocation Capacity (Coordination)**  
- Enforced by: `coordination.py` allocation system
- Limit: Split between initial and followup scripts
- Purpose: Fair sharing between two scripts

**Problem**: Displays mix these two concepts without clarifying which is which.

**Fix Required**: Clearly label which capacity is which in all displays.

---

### Terminology Recommendations

#### Recommended Terms

**For Rolling 24h Window:**
- "Sent in last 24 hours"
- "Rolling 24h window"
- "Remaining in rolling window"

**For Calendar Day:**
- "Sent today (since midnight)"
- "Today's total"

**For Allocation/Coordination:**
- "Allocated by coordination system"
- "Sent from this allocation"
- "Remaining allocation"

**For Current Run/Session:**
- "Sent this run"
- "In this batch"
- "This execution"

#### Anti-Patterns to Avoid

- "Sent today" (ambiguous - which today?)
- "Remaining today" (ambiguous - remaining from what?)
- "Already sent" (ambiguous - when?)
- "Daily quota" without specifying "rolling 24h" vs "calendar day"

---

### Summary of Required Changes

| File | Line | Current Text | Recommended Text |
|------|------|-------------|------------------|
| send_initial_outreach.py | 918 | "Remaining today: X emails" | "Remaining in rolling 24h window: X emails" |
| send_initial_outreach.py | 957 | "Already sent today: X" | "Already sent (this allocation): X" |
| send_initial_outreach.py | 958 | "Remaining to send today: X" | "Remaining (this allocation): X" |
| send_initial_outreach.py | 725 | "(X/Y today)" | "(X/Y this run)" |
| send_followup.py | 748 | "Remaining today: X emails" | "Remaining in rolling 24h window: X emails" |
| send_followup.py | 788 | "Already sent today: X" | "Already sent (this allocation): X" |
| send_followup.py | 789 | "Remaining to send today: X" | "Remaining (this allocation): X" |
| send_followup.py | 535 | "(X/Y today)" | "(X/Y this run)" |

---

### Verification Checklist

After fixes are applied, verify:

- [ ] No message says "today" without specifying which timeframe
- [ ] Rolling 24h window is always labeled as such
- [ ] Allocation counts are clearly labeled as "allocation"
- [ ] Current run counts are labeled as "this run" or "this batch"
- [ ] User can distinguish between rolling window and allocation
- [ ] All displays are unambiguous and precise

---

### Next Steps

1. Apply terminology fixes to both scripts
2. Implement rolling capacity calculation (Problem 2)
3. Add enhanced displays showing capacity breakdown
4. Test with real scenarios to verify clarity
5. Document the two capacity systems for users

---

**Audit completed**: 2025-11-12  
**Auditor**: Claude Code Project Manager  
**Status**: Ready for implementation
