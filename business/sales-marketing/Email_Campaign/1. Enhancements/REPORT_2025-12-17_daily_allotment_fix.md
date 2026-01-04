# Daily Allotment Fix Report

**Date:** 2025-12-17
**Issue:** Scripts not sending full daily allotment from config file
**Status:** Analysis complete, fixes identified

---

## Executive Summary

The email campaign scripts (`send_initial_outreach.py` and `send_followup.py`) are not sending the full daily allotment due to **hardcoded values in `coordination.py`** that don't match the actual `TOTAL_DAILY_LIMIT` in `config.py`.

---

## Root Causes Identified

### 1. Hardcoded Values Mismatch (Critical)

**Location:** `coordination.py`

| Line | Current Value | Should Be |
|------|---------------|-----------|
| 21 | `MAX_FOLLOWUP_CAPACITY = 225` | `MAX_FOLLOWUP_CAPACITY = config.TOTAL_DAILY_LIMIT // 2` |
| 374 | `daily_limit: int = 300` | `daily_limit: int = config.TOTAL_DAILY_LIMIT` |
| 566 | Display hardcodes `300` | Should use `daily_limit` parameter |

**Impact:** The coordination system caps capacity at 300 emails when `config.py` specifies `TOTAL_DAILY_LIMIT = 400`.

### 2. Follow-up Allocation Cap Incorrect

**Location:** `coordination.py` line 21

```python
MAX_FOLLOWUP_CAPACITY = 225  # Half of 450 (WRONG!)
```

This was written when the daily limit was 450. With current `TOTAL_DAILY_LIMIT = 400`:
- Follow-ups should cap at 200 (half of 400)
- Currently caps at 225 (outdated)

### 3. Conservative Pacing Not Implemented

**Location:** `config.py` lines 67-77

```python
USE_CONSERVATIVE_PACING = True  # DEFINED BUT NEVER USED
NATURAL_HOURLY_RATE = TOTAL_DAILY_LIMIT / (BUSINESS_HOURS_END - BUSINESS_HOURS_START)
```

These settings exist but are **never referenced** in the actual sending logic. The scripts calculate delays dynamically but ignore these intended pacing controls.

### 4. Rolling 24h vs. Daily Coordination Mismatch

**Issue:** The coordination system resets at midnight (calendar day), but the rate limiting uses a rolling 24-hour window.

**Example:**
- Send 200 emails at 11pm Monday
- Midnight: coordination.json resets to `sent: 0`
- Tuesday 9am: coordination thinks you can send 400
- Rolling 24h limit: "You sent 200 in last 24h, only 200 available"

Result: Confusion and potential under-sending.

---

## Current Flow Analysis

### How Capacity Is Calculated

1. **Rolling 24h check:** `coordination.get_rolling_capacity_analysis()` counts emails in last 24 hours
2. **Coordination allocation:** `coordination.report_needs_and_allocate()` divides capacity between initial/followup
3. **Effective capacity:** `min(remaining_capacity, capacity_analysis['current_capacity'])`

### Where It Goes Wrong

The `get_rolling_capacity_analysis()` function at line 374 has:
```python
def get_rolling_capacity_analysis(..., daily_limit: int = 300) -> Dict:
```

Even though the caller passes `config.TOTAL_DAILY_LIMIT` (400), the display function at line 566 hardcodes 300:
```python
print(f"║  Daily limit (rolling 24h):       {300:<24} ║")
```

This is cosmetic but indicates the code wasn't updated when limits changed.

---

## Recommended Fixes

### Fix 1: Update coordination.py Line 21

**Before:**
```python
MAX_FOLLOWUP_CAPACITY = 225  # Half of 450
```

**After:**
```python
# Calculate dynamically from config
MAX_FOLLOWUP_CAPACITY = config.TOTAL_DAILY_LIMIT // 2
```

### Fix 2: Update Default Parameter at Line 374

**Before:**
```python
def get_rolling_capacity_analysis(..., daily_limit: int = 300) -> Dict:
```

**After:**
```python
def get_rolling_capacity_analysis(..., daily_limit: int = None) -> Dict:
    if daily_limit is None:
        daily_limit = config.TOTAL_DAILY_LIMIT
```

### Fix 3: Fix Display Function at Line 566

**Before:**
```python
print(f"║  Daily limit (rolling 24h):       {300:<24} ║")
```

**After:**
```python
print(f"║  Daily limit (rolling 24h):       {config.TOTAL_DAILY_LIMIT:<24} ║")
```

### Fix 4 (Optional): Implement Conservative Pacing

If you want to use `USE_CONSERVATIVE_PACING`, add to `calculate_send_delay()`:

```python
def calculate_send_delay(emails_remaining: int, time_remaining_seconds: float, emails_sent: int) -> float:
    if emails_remaining <= 0:
        return 0

    # Check if conservative pacing is enabled
    if config.USE_CONSERVATIVE_PACING:
        # Use fixed hourly rate instead of dynamic spacing
        delay = 3600 / config.NATURAL_HOURLY_RATE  # seconds per email
    else:
        # Dynamic spacing across remaining time
        delay = time_remaining_seconds / emails_remaining

    # Add small random variation
    variation = delay * 0.1
    delay = random.uniform(delay - variation, delay + variation)

    # Minimum 3 seconds
    return max(3.0, delay)
```

---

## Current Config Settings Reference

From `config.py`:

| Setting | Value | Purpose |
|---------|-------|---------|
| `TOTAL_DAILY_LIMIT` | 400 | Max emails in 24h rolling window |
| `BUSINESS_HOURS_START` | 9 | 9 AM EST |
| `BUSINESS_HOURS_END` | 19 | 7 PM EST (10 hours) |
| `USE_CONSERVATIVE_PACING` | True | (Not implemented) |
| `NATURAL_HOURLY_RATE` | 40 | 400 / 10 hours |

---

## Testing After Fixes

1. Run with `--dry-run` flag to verify capacity calculations
2. Check that "Daily limit" displays 400 (not 300)
3. Check that followup allocation caps at 200 (not 225)
4. Monitor first few sends to confirm even pacing

---

## Files Modified

| File | Changes Needed |
|------|----------------|
| `coordination.py` | Lines 21, 374, 566 |
| `send_initial_outreach.py` | None (already references config.TOTAL_DAILY_LIMIT) |
| `send_followup.py` | None (already references config.TOTAL_DAILY_LIMIT) |

---

## Summary

The scripts ALREADY have the logic to spread emails evenly over business hours. The problem is **hardcoded capacity limits** in `coordination.py` that don't match `config.py`. Three line changes fix the issue.
