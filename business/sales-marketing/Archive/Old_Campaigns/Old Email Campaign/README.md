# Email Validation Campaign System

Automated email campaign system for validating 3 business ideas simultaneously. Sends initial outreach emails and follow-ups to prospects across Food Recall, Debarment Monitoring, and Grant Alert verticals.

## 📋 Features

- **Smart Continuous Running**: Automatically waits for business hours and respects daily limits
- **Anti-Spam Randomization**: Human-like sending patterns with variable delays and coffee breaks
- **Business Hours Only**: Sends Mon-Fri, 9am-3pm EST only
- **Daily Limits**: 450 emails/day total (150 per vertical), 24-hour rolling window
- **Deduplication**: Never sends to the same email twice
- **Follow-up Tracking**: Automatically sends follow-ups 3+ days after initial email (non-responders only)
- **Progress Tracking**: All sends logged with detailed CSV tracking
- **Graceful Shutdown**: Ctrl+C saves progress, resume where you left off

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas pytz
```

### 2. Setup Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Google account (alec.m.kleinman@gmail.com)
3. Create a new app password named "Email Campaign System"
4. Copy the 16-character password

### 3. Configure App Password

Open `config.py` and fill in the `APP_PASSWORD` field:

```python
APP_PASSWORD = "your-16-char-password-here"  # No spaces
```

### 4. Add Your Prospect Lists

Create three CSV files in this directory with prospect data:

- `food_recall_prospects.csv` - Restaurant contacts
- `debarment_prospects.csv` - Federal contractor contacts
- `grant_alerts_prospects.csv` - Nonprofit contacts

**Required column:** `email`

**Optional columns:** `first_name`, `company`, `state`

**Example CSV:**
```csv
email,first_name,company,state
john@restaurant.com,John,ABC Restaurant,NY
jane@contractor.com,Jane,XYZ Contractors,VA
```

### 5. Test Mode (Recommended First)

Before running production, test with 9 emails:

1. Open `config.py`
2. Set `TEST_MODE = True`
3. Run initial outreach:

```bash
python send_initial_outreach.py
```

This will send 3 test emails per vertical (9 total) and exit.

### 6. Production Mode

Once testing is successful:

1. Open `config.py`
2. Set `TEST_MODE = False`
3. Run initial outreach:

```bash
python send_initial_outreach.py
```

The script will run continuously, sending emails during business hours and waiting when outside the window.

**To stop:** Press `Ctrl+C` - progress is saved automatically

**To resume:** Just run the script again - it picks up where it left off

## 📧 Email Templates

All email templates are in `config.py`. Edit them as needed:

- `FOOD_RECALL_INITIAL` / `FOOD_RECALL_FOLLOWUP`
- `DEBARMENT_INITIAL` / `DEBARMENT_FOLLOWUP`
- `GRANT_ALERT_INITIAL` / `GRANT_ALERT_FOLLOWUP`

**Subject lines** are randomly selected from the lists at the top of `config.py`:
- `FOOD_RECALL_SUBJECTS`
- `DEBARMENT_SUBJECTS`
- `GRANT_ALERT_SUBJECTS`

Feel free to add/edit subject lines!

## 🔄 Follow-up System

### When to Run Follow-ups

Wait at least 3 days after your initial campaign starts, then run:

```bash
python send_followup.py
```

### How Follow-ups Work

The script automatically:
1. Finds all initial emails sent 3+ days ago
2. Excludes anyone marked as "replied = YES" in `response_tracker.csv`
3. Sends follow-ups to everyone with "replied = NO" or "replied = PENDING"
4. Respects the same daily limits and business hours
5. Never sends follow-up twice to the same person

### Tracking Responses

**Manually update `response_tracker.csv` when people reply:**

1. Open `response_tracker.csv` in Excel or Google Sheets
2. Find the row with the person's email
3. Update the `replied` column:
   - `YES` - They replied (won't get follow-up)
   - `NO` - Confirmed they're not interested (will still get follow-up)
   - `PENDING` - No response yet (will get follow-up)
4. Add notes in the `notes` column
5. Save the file

## 📊 Tracking Files

### sent_tracker.csv
Detailed log of every email sent (auto-generated):
- `timestamp` - When email was sent
- `email` - Recipient address
- `vertical` - Which business idea (food_recall/debarment/grant_alerts)
- `message_type` - initial or followup
- `subject_line` - Which subject line was used
- `status` - SUCCESS or FAILED
- `error_message` - Error details if failed

### response_tracker.csv
Manual tracking of responses (you update this):
- `email` - Recipient address
- `vertical` - Which business idea
- `initial_sent_date` - When initial email was sent
- `replied` - YES/NO/PENDING (you update this manually)
- `followup_sent_date` - When follow-up was sent (auto-filled)
- `notes` - Your notes about their response

### error_log.csv
Detailed error log for troubleshooting (auto-generated):
- `timestamp` - When error occurred
- `email` - Email that failed
- `vertical` - Which vertical
- `error_type` - Type of error
- `error_message` - Full error details
- `action_taken` - What the system did

## ⚙️ Configuration

All settings are in `config.py`:

### Sending Limits
```python
EMAILS_PER_VERTICAL_PER_DAY = 150   # Per vertical
TOTAL_DAILY_LIMIT = 450              # Total across all verticals
```

### Business Hours
```python
BUSINESS_HOURS_START = 9   # 9 AM EST
BUSINESS_HOURS_END = 15    # 3 PM EST
TIMEZONE = 'US/Eastern'
```

### Delay Settings (Anti-Spam)
```python
BASE_DELAY_MIN = 5          # Min seconds between emails
BASE_DELAY_MAX = 10         # Max seconds between emails
BREAK_FREQUENCY_MIN = 10    # Coffee break every 10-20 emails
BREAK_FREQUENCY_MAX = 20
BREAK_DURATION_MIN = 30     # Break lasts 30-90 seconds
BREAK_DURATION_MAX = 90
```

## 🔧 Troubleshooting

### "APP_PASSWORD not configured"
→ Edit `config.py` and fill in your Gmail app password

### "Prospect file not found"
→ Make sure you have created the CSV files:
- `food_recall_prospects.csv`
- `debarment_prospects.csv`
- `grant_alerts_prospects.csv`

### "5 consecutive failures detected"
→ Check your Gmail settings:
- App password is correct
- 2-factor authentication is enabled
- You haven't hit Gmail's daily limit (500/day)

### Emails sending too fast/slow
→ Edit delay settings in `config.py`:
- Increase `BASE_DELAY_MIN` and `BASE_DELAY_MAX` to slow down
- Decrease to speed up (but stay above 5 seconds)

### Daily limit reached but wants to send more
→ The system uses a 24-hour rolling window. It will automatically resume when the oldest email is >24 hours old.

## 🎯 Campaign Timeline

### Day 1: Initial Outreach
```bash
# Set TEST_MODE = False in config.py
python send_initial_outreach.py
```
- Sends up to 450 emails across 3 verticals
- Script runs continuously throughout the day
- Press Ctrl+C when done, or let it finish

### Days 2-3: Monitor Responses
- Check your email inbox for replies
- Update `response_tracker.csv`:
  - Mark "YES" for anyone who replied positively
  - Mark "NO" for anyone who declined
  - Leave as "PENDING" for non-responders

### Day 4+: Send Follow-ups
```bash
python send_followup.py
```
- Automatically sends to non-responders from 3+ days ago
- Skips anyone marked "YES" in response tracker
- Same continuous running mode

## 📈 Expected Results

Based on industry benchmarks:

**Food Recall (Restaurants):**
- Reply rate: 5-8%
- Strong leads: 2-3 out of 100

**Debarment (Federal Contractors):**
- Reply rate: 3-5%
- Strong leads: 1-2 out of 100

**Grant Alerts (Nonprofits):**
- Reply rate: 10-15%
- Strong leads: 3-5 out of 100

## 🔒 Security & Privacy

- **Gmail App Passwords**: More secure than your main password, can be revoked anytime
- **No Data Stored**: Email addresses are only in your local CSV files
- **SMTP/TLS**: All emails sent via encrypted connection
- **Local Only**: All data stays on your computer

## 💡 Tips

1. **Start with test mode** - Always test with 9 emails first
2. **Monitor first batch** - Watch the first 20-30 sends to ensure everything works
3. **Track responses daily** - Update response_tracker.csv every day
4. **Check spam folder** - Some replies might go to spam
5. **Vary subject lines** - If low open rates, edit subject lines in config.py
6. **Weekend prep** - Start Monday morning for best results

## 🐛 Common Issues

**Script stops at 3pm**
→ This is normal! It waits until next business day (9am EST)

**Script says "Daily limit reached"**
→ Wait 24 hours from first email sent. Rolling window, not calendar day.

**"Weekend detected"**
→ Script automatically waits until Monday 9am EST

**Want to change email templates**
→ Edit the template variables in `config.py`

**Need to change subject lines**
→ Edit the `*_SUBJECTS` lists at top of `config.py`

## 📞 Support

If you encounter issues:
1. Check `error_log.csv` for detailed error messages
2. Review this README troubleshooting section
3. Verify Gmail app password is correct
4. Ensure prospect CSV files have required `email` column

## 📄 License

This is a custom script for internal use. Not for redistribution.

---

**Questions?** Check the configuration section in `config.py` - all settings are documented there.
