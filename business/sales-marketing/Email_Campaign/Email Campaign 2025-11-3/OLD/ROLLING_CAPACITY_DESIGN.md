# Rolling Capacity Algorithm - Design Document
## Email Campaign Scripts - 2025-11-12

### Problem Statement

The current system is overly conservative when calculating how many emails can be sent. It uses a simple formula:

```
remaining_capacity = DAILY_LIMIT - emails_sent_in_last_24h
```

This approach misses opportunities because it doesn't account for emails "aging out" of the 24-hour window as time passes.

**Example Problem Scenario:**
```
Time: Tuesday 9:00 AM
Daily limit: 300 emails

Emails in last 24 hours:
- Monday 9:00 AM: 100 emails sent
- Monday 3:00 PM: 100 emails sent

Current calculation:
- emails_sent_in_last_24h = 200
- remaining_capacity = 300 - 200 = 100
- Script only sends 100 emails

Missed opportunity:
- At Tuesday 9:00 AM, Monday's 9am emails are EXACTLY 24h old (aged out)
- At Tuesday 3:00 PM, Monday's 3pm emails will be 24h old (age out)
- Could actually send 200+ emails if we're smart about timing!
```

### Solution: Smart Rolling Capacity Calculation

Instead of a simple subtraction, we need to:

1. **Analyze when emails will age out** (become >24h old)
2. **Calculate available capacity NOW** (already aged out)
3. **Calculate future capacity** (will age out by end of business hours)
4. **Schedule sends intelligently** to maximize throughput

---

## Algorithm Design

### Step 1: Load and Parse Historical Sends

```python
def get_rolling_capacity_analysis(current_time, business_hours_end, daily_limit=300):
    """
    Analyze rolling 24h capacity with age-out projections.
    
    Args:
        current_time: Current datetime (EST, timezone-aware)
        business_hours_end: End of sending window today (EST, timezone-aware)
        daily_limit: Maximum emails in any 24h period (default 300)
    
    Returns:
        dict with:
            - current_capacity: Can send right now
            - capacity_by_hour: When capacity will free up
            - total_capacity_by_eob: Total sendable by end of business
            - emails_by_hour: Historical sends grouped by hour
    """
```

**Load sent_tracker.csv:**
- Read all SUCCESS emails
- Parse timestamps (convert to EST timezone)
- Filter to last 24 hours (from current_time)

### Step 2: Group Emails by Hour Sent

Group historical emails by the hour they were sent:

```python
emails_by_hour = {
    datetime(2025, 11, 11, 9, 0): 45,   # Monday 9am: 45 emails
    datetime(2025, 11, 11, 10, 0): 32,  # Monday 10am: 32 emails
    datetime(2025, 11, 11, 11, 0): 28,  # Monday 11am: 28 emails
    ...
}
```

### Step 3: Calculate Age-Out Times

For each hour bucket, calculate when those emails age out (24h later):

```python
age_out_schedule = {
    datetime(2025, 11, 12, 9, 0): 45,   # Tuesday 9am: 45 will age out
    datetime(2025, 11, 12, 10, 0): 32,  # Tuesday 10am: 32 will age out
    datetime(2025, 11, 12, 11, 0): 28,  # Tuesday 11am: 28 will age out
    ...
}
```

### Step 4: Calculate Current Capacity

Count emails that have ALREADY aged out (age-out time <= current_time):

```python
current_capacity = daily_limit - sum([
    count for age_out_time, count in age_out_schedule.items()
    if age_out_time > current_time
])
```

### Step 5: Project Future Capacity

Calculate cumulative capacity as hours pass:

```python
capacity_by_hour = {}
accumulated_freed = 0

for hour in range(current_hour, business_hours_end_hour):
    hour_datetime = current_date + timedelta(hours=hour)
    
    # Count emails aging out in this hour
    freed_this_hour = age_out_schedule.get(hour_datetime, 0)
    accumulated_freed += freed_this_hour
    
    capacity_by_hour[hour_datetime] = current_capacity + accumulated_freed
```

**Example Output:**
```python
{
    datetime(2025, 11, 12, 9, 0): 150,   # Right now: 150 available
    datetime(2025, 11, 12, 10, 0): 182,  # By 10am: 182 available
    datetime(2025, 11, 12, 11, 0): 210,  # By 11am: 210 available
    datetime(2025, 11, 12, 12, 0): 238,  # By noon: 238 available
    datetime(2025, 11, 12, 13, 0): 266,  # By 1pm: 266 available
    datetime(2025, 11, 12, 14, 0): 294,  # By 2pm: 294 available
    datetime(2025, 11, 12, 15, 0): 300,  # By 3pm: 300 available (max)
}
```

### Step 6: Calculate Total Sendable By End of Business

```python
total_capacity_by_eob = capacity_by_hour[business_hours_end]
```

This is the MAXIMUM we could send if we spread it across the entire business day.

---

## Display Enhancement

### Enhanced Display Format

```
╔════════════════════════════════════════════════════════════╗
║  ROLLING 24-HOUR CAPACITY ANALYSIS                         ║
╠════════════════════════════════════════════════════════════╣
║  Daily limit (rolling 24h):       300                      ║
║  Sent in last 24 hours:           200                      ║
║                                                            ║
║  Current capacity available:      150 emails               ║
║  Will free up by 3pm EST:         +150 more                ║
║  Total sendable by 3pm:           300 emails               ║
║                                                            ║
║  CAPACITY FREED BY HOUR:                                   ║
║    9am (now):    150 available                             ║
║    10am:         182 available (+32)                       ║
║    11am:         210 available (+28)                       ║
║    12pm:         238 available (+28)                       ║
║    1pm:          266 available (+28)                       ║
║    2pm:          294 available (+28)                       ║
║    3pm:          300 available (+6, max reached)           ║
╚════════════════════════════════════════════════════════════╝
```

### Compact Display (for routine runs)

```
✅ Rolling 24h capacity: 150 now, 300 total by 3pm EST (+150 will free up)
```

---

## Integration Points

### Integration with send_initial_outreach.py

**Current code (line ~917):**
```python
emails_last_24h = get_emails_sent_last_24h()
daily_limit_remaining = config.TOTAL_DAILY_LIMIT - emails_last_24h

print(f"✅ Daily quota: {emails_last_24h}/{config.TOTAL_DAILY_LIMIT} sent in last 24h")
print(f"✅ Remaining in rolling 24h window: {daily_limit_remaining} emails\n")
```

**Enhanced code:**
```python
# Get rolling capacity analysis
capacity_analysis = get_rolling_capacity_analysis(
    current_time=get_current_time_est(),
    business_hours_end=end_time,
    daily_limit=config.TOTAL_DAILY_LIMIT
)

# Display enhanced capacity info
display_rolling_capacity_analysis(capacity_analysis, detailed=True)

# Use smart capacity for decision making
available_now = capacity_analysis['current_capacity']
total_by_eob = capacity_analysis['total_capacity_by_eob']
```

### Integration with send_followup.py

Same integration as above.

---

## Edge Cases to Handle

### Edge Case 1: No emails in last 24 hours

```python
if len(emails_in_last_24h) == 0:
    return {
        'current_capacity': daily_limit,
        'total_capacity_by_eob': daily_limit,
        'capacity_by_hour': {business_hours_end: daily_limit},
        'emails_by_hour': {}
    }
```

### Edge Case 2: All capacity used, none aging out soon

```python
# All 300 sent in last 2 hours, none aging out until tomorrow
current_capacity = 0
total_capacity_by_eob = 0
# Display: "No capacity available. Next capacity frees at [time]"
```

### Edge Case 3: Emails sent throughout yesterday

```python
# Normal case - capacity frees gradually
# Show hour-by-hour breakdown
```

### Edge Case 4: Past end of business hours

```python
if current_time >= business_hours_end:
    # Show capacity for tomorrow
    # Or just show current capacity without projections
```

### Edge Case 5: Emails sent >24h ago (should be ignored)

```python
# Filter in Step 1: only include emails sent within last 24h
cutoff = current_time - timedelta(hours=24)
df = df[df['timestamp'] >= cutoff]
```

---

## Implementation Plan

### Phase 1: Core Function (coordination.py)

Add function `get_rolling_capacity_analysis()` to coordination.py:
- Reads sent_tracker.csv
- Groups by hour
- Calculates age-out schedule
- Returns capacity analysis dict

### Phase 2: Display Function (coordination.py)

Add function `display_rolling_capacity_analysis()` to coordination.py:
- Takes capacity analysis dict
- Displays in nice formatted boxes
- Has detailed and compact modes

### Phase 3: Integration (send_initial_outreach.py)

Replace simple capacity check with rolling analysis:
- Call analysis function
- Display results
- Use for decision making
- Consider in approval prompts

### Phase 4: Integration (send_followup.py)

Same as Phase 3.

### Phase 5: Testing

Create test scenarios:
- Empty tracker (first run)
- All emails recent (no capacity)
- Emails from yesterday morning (capacity now)
- Emails from yesterday afternoon (capacity later)
- Mixed timing (gradual capacity)

---

## Benefits

1. **Maximize Throughput**: Send full 300 emails/day instead of being overly conservative
2. **User Clarity**: Show exactly when capacity will free up
3. **Better Planning**: User can decide whether to wait for more capacity
4. **Accurate Forecasting**: "Can send 150 now, 300 by 3pm" is actionable information
5. **Maintains Safety**: Still respects 300/day limit, never exceeds it

---

## Potential Enhancements (Future)

1. **Smart Scheduling**: Automatically pace sends to use capacity as it frees
2. **Multi-Day View**: Show capacity for next 24h, 48h, etc.
3. **Graphical Display**: ASCII chart showing capacity over time
4. **Alerts**: "Wait 2 hours for 50 more capacity" suggestions
5. **Optimization**: Recommend best time to send based on capacity

---

**Design completed**: 2025-11-12  
**Designer**: Claude Code Project Manager  
**Status**: Ready for implementation
