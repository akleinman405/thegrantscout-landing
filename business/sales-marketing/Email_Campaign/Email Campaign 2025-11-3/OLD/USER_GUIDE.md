# Email Campaign System - User Guide

## Table of Contents
1. [Understanding the Statistics](#understanding-the-statistics)
2. [Running the Scripts](#running-the-scripts)
3. [Understanding Daily Limits](#understanding-daily-limits)
4. [Test Mode](#test-mode)
5. [Production Mode](#production-mode)
6. [Tracking and Reports](#tracking-and-reports)
7. [Troubleshooting](#troubleshooting)

---

## Understanding the Statistics

When you run either the initial outreach or follow-up script, you'll see a statistics box like this:

```
╔════════════════════════════════════════════════════════════╗
║  EMAIL SENDING STATISTICS                                  ║
╠════════════════════════════════════════════════════════════╣
║  All-time sent (for deduplication):  449                   ║
║  Sent in last 24 hours:              0                     ║
║                                                            ║
║  Sent this week (by sender):                               ║
║    your-email@example.com                            123   ║
║    TOTAL THIS WEEK                                    123   ║
╚════════════════════════════════════════════════════════════╝
```

### What Each Statistic Means

#### 1. **All-time sent (for deduplication)**
- **What it is:** Total number of emails ever sent to unique recipients across all campaigns
- **Purpose:** Prevents you from accidentally sending duplicate emails to the same person
- **Does NOT affect:** Your daily sending limit or tomorrow's capacity
- **Example:** If you see 449, it means you've sent emails to 449 unique (email, vertical) combinations total

#### 2. **Sent in last 24 hours**
- **What it is:** Total emails sent in the rolling 24-hour window
- **Purpose:** This is what controls your daily limit
- **DOES affect:** How many more emails you can send today
- **Example:** If you have a 300/day limit and sent 50 in the last 24 hours, you can send 250 more

#### 3. **Sent this week (by sender)**
- **What it is:** Total emails sent since Monday 00:00 EST, broken down by sender email address
- **Purpose:** Weekly tracking and accountability; useful if using multiple sender accounts
- **Does NOT affect:** Daily limits (only the 24-hour count matters for that)
- **Example:** Helps you see which sender addresses are being used most

---

## Running the Scripts

### Initial Outreach Script

**Purpose:** Sends first-contact emails to new prospects

**Command:**
```bash
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Campaign 2025-11-3"
python send_initial_outreach.py
```

**What happens:**
1. Script loads prospect lists from configured CSV files
2. Displays statistics (all-time, 24h, weekly)
3. Checks if it's business hours (Mon-Fri, 9am-3pm EST)
4. Checks daily limit (based on last 24 hours)
5. Coordinates with follow-up script for capacity allocation
6. Sends emails evenly spaced across the business day
7. Logs all sends to `sent_tracker.csv`
8. Updates `response_tracker.csv` for follow-up tracking

### Follow-up Script

**Purpose:** Sends follow-up emails to non-responders 3+ days after initial contact

**Command:**
```bash
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Campaign 2025-11-3"
python send_followup.py
```

**What happens:**
1. Script loads response_tracker.csv to find candidates
2. Filters to those who haven't replied and received initial 3+ days ago
3. Displays statistics
4. Checks business hours and daily limit
5. Coordinates with initial script for capacity allocation
6. Sends follow-ups and updates tracking files

---

## Understanding Daily Limits

### Key Principle: Rolling 24-Hour Window

Your daily limit is **NOT** based on calendar days (midnight to midnight). Instead, it's a **rolling 24-hour window**.

#### Examples:

**Scenario 1: Understanding the Rolling Window**
- Daily limit: 300 emails
- Monday 2pm: You send 150 emails
- Tuesday 9am: How many can you send?
  - Look back 24 hours from now (Tuesday 9am)
  - From Monday 9am to Tuesday 9am, you sent 150 emails
  - You can send: 300 - 150 = **150 more emails**

**Scenario 2: Limit Resets Gradually**
- Daily limit: 300 emails
- Monday 9am-3pm: You send 300 emails (maxed out)
- Tuesday 9am: Can you send?
  - Looking back 24 hours (from Tuesday 9am to Tuesday 9am)
  - All 300 emails from Monday are within that window
  - You can send: 300 - 300 = **0 emails**
- Tuesday 3pm: Can you send now?
  - Looking back 24 hours (from Tuesday 3pm to Tuesday 3pm)
  - Monday's emails (sent before Monday 3pm) are now OUTSIDE the 24h window
  - You can send: **300 emails again**

**Scenario 3: The 449 "All-time" Count Won't Block You**
- All-time sent: 449 emails
- Sent in last 24 hours: 0 emails
- Daily limit: 300 emails
- **You can send:** 300 emails (the 449 doesn't matter for daily limits!)

### Why This Matters

The "all-time sent" number is **only** for deduplication. It means:
- "Don't send to john@example.com again because we already contacted him"
- It does **NOT** mean "You've hit your limit"

---

## Test Mode

### What is Test Mode?

Test mode lets you send test emails to yourself or test addresses without affecting production data or using up your daily quota.

### How to Enable Test Mode

Edit `config.py`:

```python
TEST_MODE = True  # Enable test mode

# Add your test email addresses
TEST_EMAIL_ADDRESSES = [
    "your-email@example.com",
    "another-test@example.com"
]

TEST_VERTICAL = "grant_alerts"  # Which vertical to test
TEST_EMAIL_TYPE = "initial"     # "initial" or "followup"
```

### Running in Test Mode

```bash
python send_initial_outreach.py
```

**What happens:**
- Sends one test email to EACH address in `TEST_EMAIL_ADDRESSES`
- Uses templates from the `TEST_VERTICAL`
- Does NOT log to tracking files
- Does NOT count toward daily limits
- Does NOT check business hours
- Exits after sending tests

**Example output:**
```
🧪 TEST MODE ENABLED
   Vertical: Grant Alerts
   Email type: initial
   Test emails: your-email@example.com, another-test@example.com
   Will send 2 test email(s)

[10:30:15] ✓ Test email sent to your-email@example.com
[10:30:17] ✓ Test email sent to another-test@example.com

   Vertical: Grant Alerts
   Subject: Something to Help With Funding
   First name used: (none)
   Total sent: 2/2
```

---

## Production Mode

### How to Enable Production Mode

Edit `config.py`:

```python
TEST_MODE = False  # Disable test mode

# Choose which verticals to send to
ACTIVE_VERTICALS = ["grant_alerts"]  # Or multiple: ["grant_alerts", "debarment", "food_recall"]

# Set daily limits
TOTAL_DAILY_LIMIT = 300  # Total emails per day (24-hour rolling window)
```

### Running in Production Mode

```bash
python send_initial_outreach.py
```

**What happens:**
1. **Business Hours Check:**
   - Only sends during Mon-Fri, 9am-3pm EST
   - If outside hours, waits and shows countdown

2. **Daily Limit Check:**
   - Counts emails sent in last 24 hours
   - Only sends if under daily limit
   - Shows remaining capacity

3. **Coordination:**
   - Both scripts share the daily capacity
   - Follow-ups get up to 50% (150/300)
   - Initial outreach gets the rest
   - Displayed in coordination status box

4. **Smart Pacing:**
   - Spreads emails evenly across business hours
   - Adds random delays to look natural
   - Prevents spam-like bursts

5. **Continuous Running:**
   - Runs continuously, checking conditions every 15 minutes
   - Can be stopped with Ctrl+C (saves progress gracefully)
   - Run again to pick up where you left off

### Coordination Between Scripts

Both scripts can run simultaneously. They coordinate via `coordination.json`:

```
╔════════════════════════════════════════════════════════════╗
║  COORDINATION STATUS - CENTRAL VIEW                        ║
╠════════════════════════════════════════════════════════════╣
║  Date: 2025-11-10                                          ║
║                                                            ║
║  Initial Outreach:                                         ║
║    Needs:     500                                          ║
║    Allocated: 150                                          ║
║    Sent:      75                                           ║
║    Remaining: 75                                           ║
║    Status:    running                                      ║
║                                                            ║
║  Follow-up:                                                ║
║    Needs:     200                                          ║
║    Allocated: 150                                          ║
║    Sent:      50                                           ║
║    Remaining: 100                                          ║
║    Status:    running                                      ║
║                                                            ║
║  Total Needs:     700                                      ║
║  Total Allocated: 300                                      ║
║  Total Sent:      125                                      ║
║  Total Remaining: 175                                      ║
╚════════════════════════════════════════════════════════════╝
```

**Key Points:**
- Follow-ups get priority (up to 50% of daily capacity)
- Initial outreach fills remaining capacity
- Both scripts update coordination in real-time
- New day = fresh allocation

---

## Tracking and Reports

### CSV Files Generated

#### 1. `sent_tracker.csv`

**Purpose:** Logs every email sent

**Columns:**
- `timestamp`: When email was sent (ISO format, EST)
- `email`: Recipient email address
- `vertical`: Which vertical (grant_alerts, debarment, food_recall)
- `message_type`: initial or followup
- `subject_line`: Subject used
- `status`: SUCCESS or FAILED
- `error_message`: Error details if failed
- `from_email`: Sender email address (NEW!)

**Use cases:**
- See all sent emails
- Track successes vs failures
- Analyze send patterns
- Identify problematic recipient domains

**Example:**
```csv
timestamp,email,vertical,message_type,subject_line,status,error_message,from_email
2025-11-10T09:15:30-05:00,john@nonprofit.org,grant_alerts,initial,Something to Help With Funding,SUCCESS,,your@email.com
2025-11-10T09:16:45-05:00,jane@charity.org,grant_alerts,initial,Something to Help With Funding,FAILED,Connection timeout,your@email.com
```

#### 2. `response_tracker.csv`

**Purpose:** Tracks responses and follow-up status

**Columns:**
- `email`: Recipient email
- `vertical`: Which vertical
- `initial_sent_date`: When initial email was sent
- `replied`: PENDING, NO, or YES
- `followup_sent_date`: When follow-up was sent (if applicable)
- `notes`: Manual notes

**Use cases:**
- See who needs follow-ups
- Track response rates
- Manually mark responses

**Example:**
```csv
email,vertical,initial_sent_date,replied,followup_sent_date,notes
john@nonprofit.org,grant_alerts,2025-11-03,PENDING,,
jane@charity.org,grant_alerts,2025-11-03,NO,2025-11-07,
```

**How to mark manual responses:**
1. Open `response_tracker.csv`
2. Find the email address
3. Change `replied` from PENDING to YES
4. Add notes if desired
5. Save file

This prevents the follow-up script from sending to responders.

#### 3. `error_log.csv`

**Purpose:** Detailed error tracking

**Columns:**
- `timestamp`: When error occurred
- `email`: Which recipient
- `vertical`: Which vertical
- `error_type`: SEND_FAILURE, etc.
- `error_message`: Detailed error
- `action_taken`: What the script did

**Use cases:**
- Debug sending issues
- Identify bad email addresses
- Track SMTP problems

---

## Analyzing Your Statistics

### Viewing Last 24 Hours Breakdown

The scripts show you the total, but you can dig deeper:

**Using Python/Pandas:**
```python
import pandas as pd
from datetime import datetime, timedelta

# Load tracker
df = pd.read_csv('sent_tracker.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Get last 24 hours
cutoff = datetime.now() - timedelta(hours=24)
recent = df[df['timestamp'] >= cutoff]

# Group by hour
recent['hour'] = recent['timestamp'].dt.hour
hourly = recent.groupby('hour').size()
print("Emails sent by hour (last 24h):")
print(hourly)

# Group by vertical
by_vertical = recent.groupby('vertical').size()
print("\nBy vertical:")
print(by_vertical)

# Group by sender
if 'from_email' in recent.columns:
    by_sender = recent.groupby('from_email').size()
    print("\nBy sender:")
    print(by_sender)
```

### Viewing Weekly Breakdown

**Already built-in!** The scripts show this automatically:
```
║  Sent this week (by sender):                               ║
║    your-email@example.com                            123   ║
║    another@email.com                                  87   ║
║    TOTAL THIS WEEK                                    210   ║
```

**For more detail:**
```python
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('sent_tracker.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Get this week (Monday to now)
today = datetime.now()
start_of_week = today - timedelta(days=today.weekday())
start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

week_df = df[df['timestamp'] >= start_of_week]

# By day
week_df['day'] = week_df['timestamp'].dt.day_name()
by_day = week_df.groupby('day').size()
print("Emails sent by day this week:")
print(by_day)

# By sender and day
if 'from_email' in week_df.columns:
    pivot = week_df.pivot_table(
        index='day',
        columns='from_email',
        values='email',
        aggfunc='count',
        fill_value=0
    )
    print("\nBy sender and day:")
    print(pivot)
```

---

## Troubleshooting

### "Daily limit reached" but I just started today

**Check:**
```python
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('sent_tracker.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# What's in the last 24 hours?
cutoff = datetime.now() - timedelta(hours=24)
recent = df[df['timestamp'] >= cutoff]
print(f"Emails sent in last 24 hours: {len(recent)}")
print("\nBreakdown by timestamp:")
print(recent[['timestamp', 'email', 'vertical']].tail(20))
```

**Possible causes:**
- You sent emails yesterday afternoon, and they're still in the 24h window
- Multiple sender accounts are being counted together
- The clock/timezone is incorrect

### "449 emails sent previously" - will this block me?

**No!** The 449 is just for deduplication. It means you won't re-send to those same people.

**To confirm you can still send:**
Check the "Sent in last 24 hours" number. That's what matters for daily limits.

### Emails aren't sending during business hours

**Check business hours configuration in `config.py`:**
```python
BUSINESS_HOURS_START = 9   # 9 AM EST
BUSINESS_HOURS_END = 15    # 3 PM EST
TIMEZONE = 'US/Eastern'
```

**Verify current time:**
```python
import pytz
from datetime import datetime

est = pytz.timezone('US/Eastern')
now = datetime.now(est)
print(f"Current time (EST): {now}")
print(f"Day of week: {now.strftime('%A')}")
print(f"Hour: {now.hour}")
print(f"Is business hours? {9 <= now.hour < 15 and now.weekday() < 5}")
```

### "No follow-up candidates found"

**Requirements for follow-up:**
1. Initial email must have been sent 3+ days ago
2. Recipient must be in `response_tracker.csv`
3. `replied` column must be "NO" or "PENDING"
4. `followup_sent_date` must be empty

**Check:**
```python
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('response_tracker.csv')
df['initial_sent_date'] = pd.to_datetime(df['initial_sent_date'])

# Who's eligible?
cutoff = datetime.now() - timedelta(days=3)
eligible = df[
    (df['initial_sent_date'] <= cutoff) &
    (df['replied'].str.upper().isin(['NO', 'PENDING'])) &
    (df['followup_sent_date'].isna() | (df['followup_sent_date'] == ''))
]

print(f"Eligible for follow-up: {len(eligible)}")
print(eligible[['email', 'vertical', 'initial_sent_date', 'replied']])
```

### Script crashes or hangs

**Safe stop:**
- Press `Ctrl+C` (script saves progress gracefully)
- Check `error_log.csv` for clues
- Run again to resume

**Common issues:**
- SMTP password wrong: Check `config.APP_PASSWORD`
- Network down: Check internet connection
- Gmail blocked: Check Gmail security settings
- CSV corrupted: Check CSV files aren't open in Excel

---

## Best Practices

### 1. Start with Test Mode
Always test with `TEST_MODE = True` before production sends.

### 2. Monitor Daily Limits
Keep the daily limit reasonable (300 is safe for Gmail).

### 3. Check Response Tracker Regularly
Manually mark responses as "YES" to prevent follow-ups to engaged prospects.

### 4. Review Error Log
If you see repeated failures, investigate before continuing.

### 5. Use Multiple Sender Accounts (Advanced)
To scale beyond 300/day, you can:
- Set up multiple Gmail accounts with app passwords
- Modify the script to rotate senders
- Track usage per sender in weekly stats

### 6. Back Up Tracking Files
Before major changes, copy your CSV files:
```bash
cp sent_tracker.csv sent_tracker_backup.csv
cp response_tracker.csv response_tracker_backup.csv
```

---

## Quick Reference Commands

### Check current statistics
```bash
# Initial outreach stats
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Campaign 2025-11-3"
python send_initial_outreach.py
# (Press Ctrl+C after seeing stats)
```

### Test mode
```python
# Edit config.py
TEST_MODE = True
```

### Production mode
```python
# Edit config.py
TEST_MODE = False
ACTIVE_VERTICALS = ["grant_alerts"]
```

### Stop script safely
```
Press Ctrl+C
```

### Resume after stopping
```bash
# Just run the same command again
python send_initial_outreach.py
```

---

## Questions?

- **"Can I run both scripts at once?"** Yes! They coordinate via coordination.json
- **"What happens if I restart the script?"** It picks up where it left off using tracking files
- **"Does the 449 all-time count reset?"** No, it's cumulative. But it doesn't affect daily limits!
- **"Can I send more than 300/day?"** Yes, increase `TOTAL_DAILY_LIMIT` in config.py (Gmail has limits ~500/day)
- **"How do I add a new vertical?"** Add to `VERTICALS` dict in config.py with CSV file and templates

---

**Last Updated:** November 10, 2025
**Version:** 2.0 (with enhanced statistics tracking)
