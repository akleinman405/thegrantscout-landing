# 🎯 Coordination System - Both Scripts Running Simultaneously!

## What's New

Your email system now has intelligent coordination that allows **both scripts to run at the same time** and **share the 450 daily capacity fairly**.

---

## 📋 How It Works

### The Rule:
- **Follow-ups:** Get up to 225 emails (half of 450) max
- **Initial:** Gets the rest
- **Both scripts can run 24/7 without conflicts**

### Coordination File: `coordination.json`
Located: `C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\coordination.json`

This file tracks:
- Daily allocations for each script
- How many each script has sent
- Current status (running/stopped/idle)

### Example coordination.json:
```json
{
  "date": "2025-11-03",
  "last_updated": "2025-11-03T10:15:30",
  "initial": {
    "allocated": 300,
    "sent": 125,
    "status": "running"
  },
  "followup": {
    "allocated": 150,
    "sent": 45,
    "status": "running"
  }
}
```

---

## 🎬 Real-World Examples

### Day 1-3: No Followups Ready Yet
```
Initial script:
  - Needs: 450 prospects to send
  - Allocated: 450 (followup needs 0)
  - Sends: 450 emails

Followup script:
  - Needs: 0 (no one ready for followup yet)
  - Allocated: 0
  - Status: "No follow-up candidates"
  - Exits peacefully
```

### Day 4: 100 Followups Ready
```
Followup script starts first:
  - Needs: 100 followups
  - Allocated: 100 (under 225 cap)
  - Starts sending...

Initial script starts:
  - Needs: 450 prospects
  - Sees: Followup allocated 100
  - Allocated: 350 (450 - 100)
  - Starts sending...

Result: 100 followups + 350 initials = 450 total
```

### Day 7: 300 Followups Ready
```
Both scripts running:

Followup:
  - Needs: 300 followups
  - Allocated: 225 (capped at half)
  - Sends: 225

Initial:
  - Needs: 450 prospects
  - Sees: Followup allocated 225
  - Allocated: 225 (450 - 225)
  - Sends: 225

Result: 225 followups + 225 initials = 450 total (perfect split!)
```

---

## 🚀 How to Run Both Scripts

### Option A: Two Command Windows (Recommended)

**Window 1 - Initial Outreach:**
```bash
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"
python send_initial_outreach.py
```

**Window 2 - Follow-up:**
```bash
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"
python send_followup.py
```

Both will coordinate automatically via `coordination.json`

### Option B: Background Processes (Advanced)

Use Windows Task Scheduler or `pythonw` to run both scripts in background.

---

## 📊 What You'll See

### Console Output (Initial Script):
```
======================================================================
EMAIL VALIDATION CAMPAIGN SYSTEM - INITIAL OUTREACH
======================================================================

✅ Business hours detected (Mon-Fri, 9am-3pm EST)
✅ Daily quota: 0/450 sent in last 24h
✅ Remaining today: 450 emails

📊 Coordinating with follow-up script...

╔════════════════════════════════════════════════════════════╗
║  COORDINATION SUMMARY                                      ║
╠════════════════════════════════════════════════════════════╣
║  Date: 2025-11-03                                          ║
║                                                            ║
║  Initial Outreach:                                         ║
║    Allocated: 300                                          ║
║    Sent:      0                                            ║
║    Remaining: 300                                          ║
║    Status:    running                                      ║
║                                                            ║
║  Follow-up:                                                ║
║    Allocated: 150                                          ║
║    Sent:      0                                            ║
║    Remaining: 150                                          ║
║    Status:    running                                      ║
║                                                            ║
║  Total Allocated: 450                                      ║
║  Total Sent:      0                                        ║
╚════════════════════════════════════════════════════════════╝

✅ Initial script allocated: 300 emails
✅ Effective capacity (after pacing): 300 emails

📊 Sending 300 emails per vertical (300 total)
   ✓ Debarment: 300 ready to send

[09:15:32] ✓ Sent to john@contractor.com (Debarment, John) (1/300 today)
...
```

---

## 🔄 Crash Recovery

### If a script crashes:
1. **coordination.json persists** with accurate counts
2. Other script keeps running normally
3. Restart crashed script - it reads coordination.json and continues

### Example:
```
Initial script crashes after sending 150/300

coordination.json:
{
  "initial": {
    "allocated": 300,
    "sent": 150,  <-- Accurate count saved
    "status": "stopped"
  }
}

Restart initial script:
- Reads: Already sent 150
- Sends: Remaining 150
- Total: 300 (as allocated)
```

---

## 🎛️ Manual Response Tracking

Both scripts respect your manual updates to `response_tracker.csv`:

```csv
email,vertical,initial_sent_date,replied,followup_sent_date,notes
john@co.com,debarment,2025-11-03,YES,,He replied interested!
mary@co.com,debarment,2025-11-03,PENDING,,No response yet
```

**When you mark replied = YES:**
- ✅ Followup script skips them (never sends followup)
- ✅ Both scripts see the update immediately

---

## 📁 Files in the System

1. **coordination.json** - Daily allocation tracking (auto-generated)
2. **sent_tracker.csv** - Real-time log of every email sent (existing)
3. **response_tracker.csv** - Manual tracking of responses (you update)
4. **coordination.py** - Coordination module (new)
5. **send_initial_outreach.py** - Initial emails (updated with coordination)
6. **send_followup.py** - Follow-up emails (updated with coordination)
7. **config.py** - Settings (updated with pacing + test emails)

---

## ✅ Benefits

### 1. **True "Set and Forget"**
- Start both scripts Monday morning
- They run all week
- Automatically coordinate
- Handle weekends/business hours
- Maintain conservative pacing

### 2. **Fair Allocation**
- Followups never starve (guaranteed up to 225)
- Initials get remaining capacity
- Total always ≤ 450

### 3. **Crash-Safe**
- coordination.json persists
- Real-time sent_tracker.csv
- Restart anytime without data loss

### 4. **Manual Control**
- Update response_tracker.csv anytime
- Both scripts see changes immediately
- Stop/start scripts as needed

---

## 🔧 Configuration

All settings remain in `config.py`:

```python
# Coordination happens automatically
TOTAL_DAILY_LIMIT = 450
USE_CONSERVATIVE_PACING = True  # Maintains 75/hour rate

# Test mode still works
TEST_MODE = False
TEST_EMAIL_ADDRESSES = ["your@email.com"]

# Active verticals
ACTIVE_VERTICALS = ["debarment"]
```

---

## 📊 Monitoring

### Check Coordination Status:
Look at `coordination.json` anytime to see:
- How much allocated to each script
- How much each has sent
- Current status

### Check Sent Tracker:
`sent_tracker.csv` has every email sent with timestamps.

### Check Response Tracker:
`response_tracker.csv` shows who replied (you update manually).

---

## 🚨 Common Scenarios

### "Both scripts want capacity, who wins?"
**Both get fair share:**
- Calculate needs for each
- Followup capped at 225
- Initial gets rest
- Total = 450

### "What if only initial has work?"
**Initial gets full 450:**
- Followup allocated: 0
- Initial allocated: 450

### "What if only followup has work?"
**Followup gets what it needs (up to 225):**
- 100 followups ready → Followup: 100, Initial: 350
- 300 followups ready → Followup: 225, Initial: 225

### "What if I stop one script?"
**Other continues normally:**
- coordination.json marks stopped script as "stopped"
- Running script keeps using its allocation
- Restart stopped script anytime

---

## 🎯 Quick Start

1. **Configure both scripts** (done - they have coordination built in)
2. **Start initial script** in one window
3. **Start followup script** in another window
4. **Watch coordination.json** to see allocation
5. **Update response_tracker.csv** when people reply

Both scripts will coordinate automatically via coordination.json!

---

## 📝 Notes

- **coordination.json is auto-generated** - don't edit manually
- **Resets daily** - new allocation calculated each day
- **Conservative pacing applies** to both scripts independently
- **Business hours respected** by both scripts
- **24-hour rolling window** shared between both scripts

You now have a fully coordinated, crash-safe, fair-allocation email system that can run 24/7! 🎉
