# Lessons Learned: Daily Allotment Issue

**Date:** 2025-12-17
**Topic:** Email Campaign Capacity Management

---

## What Went Wrong

1. **Magic Numbers:** Hardcoded values (225, 300, 450) were used instead of referencing `config.TOTAL_DAILY_LIMIT`

2. **Config Drift:** When `TOTAL_DAILY_LIMIT` was updated from 450 to 400, the dependent values in `coordination.py` were not updated

3. **Dead Code:** `USE_CONSERVATIVE_PACING` and `NATURAL_HOURLY_RATE` were added to config but never implemented in the actual logic

4. **Display vs. Logic Mismatch:** Display messages showed different numbers (300) than the actual limit being used (400)

---

## Key Lessons

### 1. Single Source of Truth

**Problem:** Multiple files had their own idea of what the daily limit was.

**Solution:** Always reference `config.TOTAL_DAILY_LIMIT` rather than hardcoding values. Use:

```python
# Good
MAX_FOLLOWUP_CAPACITY = config.TOTAL_DAILY_LIMIT // 2

# Bad
MAX_FOLLOWUP_CAPACITY = 225
```

### 2. Derived Values Should Be Calculated

**Problem:** `MAX_FOLLOWUP_CAPACITY = 225` was manually calculated as "half of 450"

**Solution:** Let the code calculate derived values:

```python
# The relationship is "half of daily limit"
# Express the relationship, not the result
MAX_FOLLOWUP_CAPACITY = config.TOTAL_DAILY_LIMIT // 2
```

### 3. Comments Can Become Lies

**Problem:** Comment said "Half of 450" but limit was changed to 400

**Solution:** Comments about specific numbers become outdated. Better:

```python
# Cap followup at half of daily capacity
MAX_FOLLOWUP_CAPACITY = config.TOTAL_DAILY_LIMIT // 2
```

### 4. Dead Code Is Dangerous

**Problem:** Config had pacing settings that were never used, creating false confidence

**Solution:** Either implement the feature or remove the config. Document clearly:

```python
# TODO: Not yet implemented
# USE_CONSERVATIVE_PACING = True
```

Or implement it properly.

### 5. Test After Config Changes

**Problem:** Changing `TOTAL_DAILY_LIMIT` didn't trigger any errors, but behavior was wrong

**Solution:** Add validation that surfaces mismatches:

```python
def validate_config():
    """Run at startup to catch configuration issues"""
    if MAX_FOLLOWUP_CAPACITY > config.TOTAL_DAILY_LIMIT:
        raise ValueError(f"MAX_FOLLOWUP_CAPACITY ({MAX_FOLLOWUP_CAPACITY}) exceeds TOTAL_DAILY_LIMIT ({config.TOTAL_DAILY_LIMIT})")
```

---

## Checklist for Future Config Changes

When changing `TOTAL_DAILY_LIMIT` or similar core settings:

- [ ] Search codebase for hardcoded values that might depend on it
- [ ] Update display messages that show the limit
- [ ] Test with `--dry-run` to verify capacity calculations
- [ ] Check comments that reference specific numbers
- [ ] Verify coordination.json is reset (or manually clear it)

---

## Code Patterns to Avoid

### Bad: Hardcoded Capacity

```python
MAX_FOLLOWUP_CAPACITY = 225  # Magic number, no context
daily_limit: int = 300  # Where does 300 come from?
```

### Good: Referenced from Config

```python
MAX_FOLLOWUP_CAPACITY = config.TOTAL_DAILY_LIMIT // 2
daily_limit: int = config.TOTAL_DAILY_LIMIT
```

### Bad: Hardcoded in Display

```python
print(f"Daily limit: {300}")  # Will become stale
```

### Good: Dynamic Display

```python
print(f"Daily limit: {config.TOTAL_DAILY_LIMIT}")
```

---

## Architecture Note

The email campaign system has good bones:
- Config centralization (`config.py`)
- Coordination between scripts (`coordination.py`)
- Rolling 24h capacity tracking
- Even pacing calculation

The issue was **leaky abstractions** where `coordination.py` bypassed the config for some values. The fix is simple: ensure all capacity-related values flow from `config.TOTAL_DAILY_LIMIT`.

---

## Quick Reference: What Each File Controls

| File | Controls |
|------|----------|
| `config.py` | ALL limits, business hours, templates |
| `coordination.py` | Allocation between initial/followup, capacity tracking |
| `send_initial_outreach.py` | Sending logic for first contact |
| `send_followup.py` | Sending logic for follow-ups |

**Golden Rule:** If it's a number that might change, it belongs in `config.py` and should be referenced everywhere else.
