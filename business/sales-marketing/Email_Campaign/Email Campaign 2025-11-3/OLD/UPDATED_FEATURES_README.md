# Updated Email Campaign System - New Features

## 🎯 What's New

### 1. Personalized Greetings with First Names
All emails now start with **"Hi {first_name},"** when a first name is available in your CSV.

**Example:**
- If CSV has: `email=john@company.com, first_name=John`
- Email starts with: `Hi John,`
- If no first_name: `Hi,`

### 2. Test Mode Improvements
You can now test specific verticals and email types without sending to real prospects.

**New config.py settings:**
```python
TEST_MODE = False  # Set to True for testing
TEST_EMAIL_ADDRESS = "your.test.email@gmail.com"  # Where test emails go
TEST_VERTICAL = "debarment"  # Which vertical to test
TEST_EMAIL_TYPE = "initial"  # "initial" or "followup"
```

**How to use:**
1. Set `TEST_MODE = True` in config.py
2. Set `TEST_EMAIL_ADDRESS` to your own email
3. Set `TEST_VERTICAL` to which business you want to test
4. Set `TEST_EMAIL_TYPE` to "initial" or "followup"
5. Run `python send_initial_outreach.py` or `python send_followup.py`
6. You'll receive 1 test email at your TEST_EMAIL_ADDRESS

### 3. Active Verticals Control
Choose which verticals to send on any given day.

**New config.py setting:**
```python
ACTIVE_VERTICALS = ["debarment"]  # List which verticals to send today
```

**Examples:**
```python
# Send only debarment emails (450 total)
ACTIVE_VERTICALS = ["debarment"]

# Split 450 emails between two verticals (225 each)
ACTIVE_VERTICALS = ["debarment", "food_recall"]

# Split 450 emails across all three (150 each)
ACTIVE_VERTICALS = ["debarment", "food_recall", "grant_alerts"]
```

**When to use:**
- Right now: Only debarment has leads, so use `["debarment"]`
- Later: When you have leads for multiple verticals, add them to the list
- The system automatically splits your daily limit evenly across active verticals

## 📋 Quick Start Guide

### First Time Setup

1. **Edit config.py:**
   ```python
   # Add your Gmail app password
   APP_PASSWORD = "your-16-char-app-password"
   
   # Set your test email (for testing)
   TEST_EMAIL_ADDRESS = "your.email@gmail.com"
   
   # Choose active verticals (currently only debarment has leads)
   ACTIVE_VERTICALS = ["debarment"]
   ```

2. **Make sure your debarment_prospects.csv has these columns:**
   - `email` (required)
   - `first_name` (recommended for personalization)
   - `company` (optional)
   - `state` (optional)

### Testing Before Sending (Recommended!)

1. **Open config.py and enable test mode:**
   ```python
   TEST_MODE = True
   TEST_EMAIL_ADDRESS = "your.email@gmail.com"
   TEST_VERTICAL = "debarment"
   TEST_EMAIL_TYPE = "initial"
   ```

2. **Run initial email test:**
   ```bash
   python send_initial_outreach.py
   ```
   - You'll receive 1 test email
   - Check the greeting uses first name from CSV
   - Check the email content looks good

3. **Test follow-up email (optional):**
   ```python
   TEST_EMAIL_TYPE = "followup"  # Change in config.py
   ```
   ```bash
   python send_followup.py
   ```

4. **Once tests look good, disable test mode:**
   ```python
   TEST_MODE = False
   ```

### Production Sending (All 450 Debarment Emails)

1. **Verify config.py settings:**
   ```python
   TEST_MODE = False  # Production mode
   ACTIVE_VERTICALS = ["debarment"]  # Only debarment
   TOTAL_DAILY_LIMIT = 450  # All 450 emails
   ```

2. **Run initial outreach:**
   ```bash
   python send_initial_outreach.py
   ```
   - Sends during business hours (9am-3pm EST, Mon-Fri)
   - Spreads emails throughout the day
   - Human-like delays between sends
   - Press Ctrl+C to stop (progress is saved)

3. **Monitor progress:**
   - Watch console output for real-time status
   - Check `sent_tracker.csv` for detailed logs
   - Update `response_tracker.csv` when people reply

4. **Send follow-ups (after 3+ days):**
   ```bash
   python send_followup.py
   ```
   - Automatically finds non-responders from 3+ days ago
   - Skips anyone marked "YES" in response tracker
   - Same business hours and pacing

## 📊 CSV File Requirements

### debarment_prospects.csv
Located at: `C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\debarment_prospects.csv`

**Required columns:**
- `email` - Recipient email address

**Optional but recommended:**
- `first_name` - For personalized greeting "Hi John," vs "Hi,"
- `company` - Company name (not used in email yet, but tracked)
- `state` - State abbreviation (not used in email yet, but tracked)

**Example CSV:**
```csv
email,first_name,company,state
john.smith@acme.com,John,ACME Contractors,VA
mary.jones@defense.com,Mary,Defense Solutions Inc,MD
info@contractor.com,,ABC Federal Services,DC
```

Note: If first_name is empty, email will start with just "Hi," instead of "Hi [Name],"

## 🎛️ Configuration Options

### config.py Key Settings

```python
# Test Mode
TEST_MODE = False  # True = send 1 test email only
TEST_EMAIL_ADDRESS = "your.test@gmail.com"
TEST_VERTICAL = "debarment"  # Which vertical to test
TEST_EMAIL_TYPE = "initial"  # "initial" or "followup"

# Active Verticals (Production)
ACTIVE_VERTICALS = ["debarment"]  # Currently only debarment has leads

# Sending Limits
TOTAL_DAILY_LIMIT = 450  # Max emails per day
BUSINESS_HOURS_START = 9  # 9am EST
BUSINESS_HOURS_END = 15  # 3pm EST

# Anti-Spam Delays
BASE_DELAY_MIN = 5  # Min seconds between emails
BASE_DELAY_MAX = 10  # Max seconds between emails
BREAK_FREQUENCY_MIN = 10  # Coffee break every 10-20 emails
BREAK_FREQUENCY_MAX = 20
BREAK_DURATION_MIN = 30  # Break lasts 30-90 seconds
BREAK_DURATION_MAX = 90
```

## 🔄 Workflow Examples

### Scenario 1: Test debarment email before sending
```python
# config.py
TEST_MODE = True
TEST_EMAIL_ADDRESS = "alec.m.kleinman@gmail.com"
TEST_VERTICAL = "debarment"
TEST_EMAIL_TYPE = "initial"
```
Run: `python send_initial_outreach.py`
Result: 1 email sent to alec.m.kleinman@gmail.com with debarment content

### Scenario 2: Send all 450 debarment emails
```python
# config.py
TEST_MODE = False
ACTIVE_VERTICALS = ["debarment"]
```
Run: `python send_initial_outreach.py`
Result: 450 emails sent throughout the day to debarment prospects

### Scenario 3: Later - split between debarment and food recall
```python
# config.py
TEST_MODE = False
ACTIVE_VERTICALS = ["debarment", "food_recall"]
```
Run: `python send_initial_outreach.py`
Result: 225 debarment + 225 food_recall = 450 total

### Scenario 4: Test follow-up email
```python
# config.py
TEST_MODE = True
TEST_EMAIL_ADDRESS = "alec.m.kleinman@gmail.com"
TEST_VERTICAL = "debarment"
TEST_EMAIL_TYPE = "followup"
```
Run: `python send_followup.py`
Result: 1 follow-up email sent to alec.m.kleinman@gmail.com

## 📝 Email Templates

All templates use the `{greeting}` placeholder which automatically becomes:
- `" John,"` if first_name exists (note the space before the name)
- `","` if no first_name (just a comma)

**Current debarment initial email:**
```
Hi{greeting}

I built a tool that automatically monitors your vendor/subcontractor list 
and alerts you if any get debarred.

You upload your vendors once, we check them against SAM.gov daily, you get 
instant alerts if any hit the exclusion list.

FAR 9.404 says you have to check, but nobody has time to manually search 
50+ vendors every week.

Looking for 10 contractors to test this for free in exchange for feedback. 
Lifetime access for early testers.

Interested? Just reply "yes."

Alec Kleinman
(281) 245-4596
```

## 🛠️ Troubleshooting

### "APP_PASSWORD not configured"
→ Edit config.py and add your Gmail app password

### "No prospects found for debarment vertical"
→ Check that debarment_prospects.csv exists at the path in config.py
→ Verify CSV has an 'email' column

### Test email not using first name
→ Check that CSV has 'first_name' column
→ Verify first_name cell is not empty for that row
→ Column name must be exactly 'first_name' (lowercase)

### Want to change email wording
→ Edit the template in config.py:
```python
DEBARMENT_INITIAL = """Hi{greeting},

Your new text here...

Alec Kleinman"""
```
Note: Keep the `{greeting}` placeholder

### Emails sending too fast
→ Increase BASE_DELAY_MIN and BASE_DELAY_MAX in config.py

### Want to add more subject lines
→ Edit DEBARMENT_SUBJECTS list in config.py:
```python
DEBARMENT_SUBJECTS = [
    "Curious how you handle vendor checks",
    "Question about SAM.gov monitoring",
    "Built something for contractor compliance"
]
```

## 📂 Files Included

1. **config.py** - All settings, templates, and verticals
2. **send_initial_outreach.py** - Sends initial emails
3. **send_followup.py** - Sends follow-up emails
4. **UPDATED_FEATURES_README.md** - This file

## 🚀 Ready to Send?

1. ✅ Test mode works with your own email
2. ✅ First names appear in greeting correctly
3. ✅ Email content looks good
4. ✅ APP_PASSWORD configured in config.py
5. ✅ debarment_prospects.csv in correct location
6. ✅ TEST_MODE = False in config.py
7. ✅ ACTIVE_VERTICALS = ["debarment"]

Run: `python send_initial_outreach.py`

Good luck with your validation campaign! 🎯
