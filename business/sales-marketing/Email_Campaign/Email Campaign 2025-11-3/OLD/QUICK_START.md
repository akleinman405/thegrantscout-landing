# Quick Reference - Updated Email System

## 🎯 What Changed

**NEW:** Both scripts can now run simultaneously with intelligent coordination!

## 📁 Files Updated

1. **[config.py](computer:///mnt/user-data/outputs/config.py)** 
   - Multiple test emails support
   - Conservative pacing enabled

2. **[coordination.py](computer:///mnt/user-data/outputs/coordination.py)** ⭐ NEW
   - Manages allocation between scripts
   - Tracks sent counts
   - Handles crash recovery

3. **[send_initial_outreach.py](computer:///mnt/user-data/outputs/send_initial_outreach.py)**
   - Integrated with coordination system
   - Requests allocation before sending
   - Updates sent counts in real-time

4. **[send_followup.py](computer:///mnt/user-data/outputs/send_followup.py)**
   - Integrated with coordination system
   - Capped at 225 emails max (half)
   - Coordinates with initial script

5. **[COORDINATION_SYSTEM_GUIDE.md](computer:///mnt/user-data/outputs/COORDINATION_SYSTEM_GUIDE.md)**
   - Complete guide to new system

## 🚀 How to Use

### Run Both Scripts Simultaneously:

**Window 1:**
```bash
python send_initial_outreach.py
```

**Window 2:**
```bash
python send_followup.py
```

Both will coordinate automatically!

## 📊 Allocation Rules

- **Follow-up:** Max 225 emails (half of 450)
- **Initial:** Gets the rest (450 - followup_amount)
- **Total:** Always ≤ 450 per day

### Examples:
- 0 followups ready → Initial: 450, Followup: 0
- 100 followups ready → Followup: 100, Initial: 350
- 300 followups ready → Followup: 225 (capped), Initial: 225

## 🔄 Key Features

✅ **Both scripts run 24/7** without conflicts
✅ **Fair allocation** - followups capped at half
✅ **Crash recovery** - coordination.json persists
✅ **Conservative pacing** - maintains 75/hour rate
✅ **Manual control** - update response_tracker.csv anytime
✅ **Multiple test emails** - test with whole team

## 📂 Auto-Generated Files

- **coordination.json** - Daily allocation tracking (don't edit)
- Resets each day automatically
- Persists through crashes

## 🧪 Testing

Still works the same:
```python
# config.py
TEST_MODE = True
TEST_EMAIL_ADDRESSES = [
    "alec.m.kleinman@gmail.com",
    "team@gmail.com",
]
TEST_VERTICAL = "debarment"
```

```bash
python send_initial_outreach.py  # Sends to all test addresses
```

## ⚙️ Configuration

```python
# config.py
TOTAL_DAILY_LIMIT = 450  # Shared between both scripts
USE_CONSERVATIVE_PACING = True  # 75 emails/hour
ACTIVE_VERTICALS = ["debarment"]
```

## 📊 Monitoring

Check `coordination.json` anytime:
```json
{
  "date": "2025-11-03",
  "initial": {"allocated": 300, "sent": 125},
  "followup": {"allocated": 150, "sent": 45}
}
```

## 💡 Pro Tips

1. **Start both scripts Monday 9am** - let them run all week
2. **Check coordination.json** to see real-time allocation
3. **Update response_tracker.csv daily** when people reply
4. **Stop/restart anytime** - coordination persists
5. **Watch console** for coordination summary display

## 🆘 Troubleshooting

**"Both scripts fighting for capacity?"**
→ Check coordination.json - they should have different allocations

**"Script says 0 allocated?"**
→ Other script claimed capacity first, or no prospects to send

**"coordination.json missing?"**
→ Auto-created on first run

**"Want to reset allocations?"**
→ Delete coordination.json, will recreate with fresh allocations

## 📈 Expected Behavior

**Days 1-3:** Only initial sends (0 followups ready)
**Day 4+:** Both send (followups ready, fair split)

This is normal and expected!

---

**Ready to start?** Just run both scripts in separate windows. They'll coordinate automatically! 🎯
