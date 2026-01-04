# Time Tracking Feature - Planning Document

## User Request
Clock in/out function to track:
- When worked
- How long worked
- What worked on
- Integrate with call schedule

---

## Proposed Design

### Database Schema

```sql
CREATE TABLE work_sessions (
    id SERIAL PRIMARY KEY,
    clock_in TIMESTAMPTZ NOT NULL,
    clock_out TIMESTAMPTZ,           -- NULL = still clocked in
    planned_hours NUMERIC(4,2),       -- Hours planned for this session
    planned_calls INTEGER,            -- Target calls for this session
    notes TEXT,                       -- What they worked on
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Link calls to sessions for productivity tracking
ALTER TABLE calls ADD COLUMN work_session_id INTEGER REFERENCES work_sessions(id);
```

### UI Design

**Option A: Floating Timer (Recommended for Mobile)**
```
┌──────────────────────────────────────┐
│ Call Queue                           │
├──────────────────────────────────────┤
│ [TODAY] [TOMORROW] [WEEK]            │
│                                      │
│ ... prospect cards ...               │
│                                      │
│                                      │
│           ┌─────────────┐            │
│           │ ⏱️ 1:45:23   │  ← Floating
│           │ 12 calls    │    timer
│           │ [Clock Out] │            │
│           └─────────────┘            │
└──────────────────────────────────────┘
```

**Option B: Header Integration**
```
┌──────────────────────────────────────┐
│ Call Queue        ⏱️ 1:45 | 12 calls │
├──────────────────────────────────────┤
```

**Option C: Dashboard Card**
```
┌────────────────────────────────────┐
│ TODAY'S SESSION                    │
│ ┌──────────────────────────────┐   │
│ │ Clocked in: 9:15 AM          │   │
│ │ Duration: 1h 45m             │   │
│ │ Calls made: 12               │   │
│ │ Calls/hour: 6.9              │   │
│ │                              │   │
│ │ [CLOCK OUT]                  │   │
│ └──────────────────────────────┘   │
└────────────────────────────────────┘
```

### Integration with Schedule

**When clocking in:**
1. Show: "How many hours do you have for calls today?"
2. Show: "How many calls do you want to make?"
3. Auto-calculate: "At 5 min/call, you can make ~24 calls in 2 hours"
4. Option: "Auto-schedule top prospects for today?"

**During session:**
- Track calls made during this session
- Show progress: "12/24 calls (50%)"
- Show time remaining: "45 min left"
- Alert when approaching target

**When clocking out:**
- Summary of session
- Calls made, duration, calls/hour
- Option to add notes about what was accomplished

### Workflow

```
Morning:
1. Open app → See "Clock In" prompt
2. Enter planned hours (e.g., 2 hours)
3. AI suggests call count (e.g., 20 calls)
4. Clock in → Timer starts

During work:
5. Make calls from queue
6. Each call logged, linked to session
7. See live progress in floating timer

End of session:
8. Click "Clock Out"
9. See session summary
10. Add notes (optional)

Later:
11. View history in Dashboard
12. See productivity trends
```

### Data Views

**Daily Summary:**
| Date | Clock In | Clock Out | Duration | Calls | Calls/Hr |
|------|----------|-----------|----------|-------|----------|
| Jan 2 | 9:15 AM | 11:45 AM | 2h 30m | 18 | 7.2 |
| Jan 2 | 2:00 PM | 4:30 PM | 2h 30m | 15 | 6.0 |

**Weekly Summary:**
- Total hours: 12.5
- Total calls: 85
- Avg calls/hour: 6.8
- Best day: Tuesday (22 calls)

---

## Implementation Steps

1. **Database Migration** (006_work_sessions.sql)
   - Create work_sessions table
   - Add work_session_id to calls table

2. **API Methods**
   - `clockIn(plannedHours, plannedCalls)`
   - `clockOut(notes)`
   - `getCurrentSession()`
   - `getSessionHistory(days)`
   - `getSessionStats()`

3. **UI Components**
   - ClockInModal - Set targets
   - FloatingTimer - Show progress
   - ClockOutModal - Summary + notes
   - SessionHistory - In dashboard

4. **Integration**
   - Link calls to active session
   - Update call log to include session

---

## Questions for User

1. **Timer style preference:**
   - A) Floating button (always visible)
   - B) Header bar (compact)
   - C) Dashboard card only

2. **AI scheduling integration:**
   - Want AI to auto-suggest prospects when clocking in?
   - Based on planned hours + priority scoring?

3. **Reminders:**
   - Notify when target time is almost up?
   - Notify when not clocked in and it's work hours?
