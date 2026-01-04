# Campaign Control Page - Complete Guide ✅

**Date:** November 4, 2025
**Feature:** Campaign Control, Live Monitoring, and Test Emails
**Status:** ✅ IMPLEMENTED

---

## Overview

The new **Campaign Control** page (🚀 Campaign Control) provides three essential capabilities:

1. **Campaign Control** - Start and manage email campaigns
2. **Live Feed** - Real-time monitoring of emails being sent
3. **Test Emails** - Send test emails to verify templates before campaigns

---

## Location

**Navigation:** Sidebar → 🚀 Campaign Control (Page 8)

**File:** `pages/8_🚀_Campaign_Control.py`

---

## Tab 1: Campaign Control

### Features

#### Status Display
- **Campaign Status:** Shows whether campaign is running or stopped
- **Sent Today:** Count of emails sent today from all campaigns
- **Business Hours:** Indicates if currently in business hours (9am-3pm EST, Mon-Fri)

#### Campaign Configuration
- **Campaign Type:** Choose between:
  - Initial Outreach Only
  - Follow-up Only
  - Both (Initial + Follow-up)
- **Target Vertical:** Select specific vertical or "All Verticals"
- **Daily Limit Override:** Optionally set custom daily limit

#### Controls
- **▶️ Start Campaign** button (marks campaign as active)
- **⏹️ Mark as Stopped** button (marks campaign as inactive)

### How to Use

#### Starting a Campaign

1. Go to Campaign Control tab
2. Select campaign type (initial/followup/both)
3. Select target vertical
4. (Optional) Enable and set daily limit override
5. Click "▶️ Start Campaign"

**Note:** Campaign scripts still need to be run manually in terminal:

```bash
cd "C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Campaign 2025-11-3"

# For initial outreach
python send_initial_outreach.py

# For follow-up
python send_followup.py
```

#### Stopping a Campaign

1. In the terminal where the script is running, press `Ctrl + C`
2. Return to dashboard and click "⏹️ Mark as Stopped"

---

## Tab 2: Live Feed (Real-Time Monitoring)

### Features

#### Auto-Refresh
- Automatically refreshes every 5 seconds
- Shows newly sent emails in real-time
- Toggle on/off with checkbox

#### Email Display
- **Configurable Count:** Show last 10-500 emails (default: 50)
- **Color-Coded Status:**
  - 🟢 Green = SUCCESS
  - 🔴 Red = ERROR
- **Columns Shown:**
  - Time (timestamp)
  - Recipient (email address)
  - Vertical
  - Type (initial/followup)
  - Subject line
  - Status

#### Summary Stats
- ✅ Successful sends
- ❌ Errors
- 📊 Success rate percentage

### How to Use

#### Monitor Active Campaigns

1. Go to Live Feed tab
2. Enable "🔄 Auto-Refresh (5 seconds)"
3. Watch emails appear in real-time as they're sent
4. Adjust "Show Last N Emails" slider to see more/fewer emails

#### Manual Refresh

1. Click "🔃 Refresh Now" button
2. Data updates immediately without waiting for auto-refresh

#### View Details

- Scroll through the table to see all recent emails
- Check status column for any errors
- Review summary stats at the bottom

---

## Tab 3: Test Emails

### Features

#### Test Configuration
- **From Email Account:** Select which account to send from
- **Vertical / Template:** Choose vertical (determines template)
- **Test Email Address:** Your email to receive the test
- **Message Type:** Initial or Follow-up template

#### Test Data
Customize template variables:
- First Name (default: John)
- Company Name (default: Test Company Inc.)
- State (default: CA)
- Website (default: www.example.com)

#### Email Preview
- Shows formatted preview before sending
- Displays: From, To, Subject, Body
- Verifies template variables are filled correctly

#### SMTP Sending
- Uses actual SMTP connection from configured account
- Decrypts stored password automatically
- Shows success/failure feedback
- Includes detailed error messages if sending fails

### How to Use

#### Send a Test Email

1. Go to Test Emails tab
2. Fill out the form:
   - **From Email Account:** Choose sending account
   - **Vertical / Template:** Select which template to test
   - **Test Email Address:** Enter your email address
   - **Message Type:** Choose initial or followup
3. (Optional) Customize test data fields
4. Click "📧 Send Test Email"
5. Review the email preview
6. Check your inbox for the test email

#### Verify Templates

**Before running campaigns, test each vertical:**

1. Send test email for initial template
2. Send test email for followup template
3. Check for:
   - ✅ All variables filled correctly (no `{first_name}` showing)
   - ✅ Subject line looks professional
   - ✅ Email formatting is correct
   - ✅ Links work (if applicable)
   - ✅ Sender name displays properly
   - ✅ Email doesn't land in spam

---

## Technical Details

### Data Sources

#### Live Feed
- **Source:** `sent_tracker.csv`
- **Columns:** timestamp, email, vertical, message_type, subject_line, status
- **Update Frequency:** Every 5 seconds (when auto-refresh enabled)

#### Campaign Status
- **Source:** Session state (`st.session_state`)
- **Persistence:** Resets when dashboard restarts

### SMTP Configuration

Test emails use credentials from Email Accounts page:
- **Host:** From account's smtp_host field
- **Port:** From account's smtp_port field
- **Username:** From account's smtp_username field
- **Password:** Decrypted from account's password_encrypted field
- **Security:** STARTTLS enabled

### Template Variables

Test emails support these variables:
- `{first_name}` - First name from test data
- `{company}` or `{company_name}` - Company name from test data
- `{state}` - State from test data
- `{website}` - Website from test data
- `{greeting}` - Auto-generated greeting (e.g., "Hello John")

---

## Common Issues & Solutions

### Issue 1: Auto-Refresh Not Working

**Symptoms:** Live Feed doesn't update automatically

**Solutions:**
- Verify "🔄 Auto-Refresh" checkbox is enabled
- Check that emails are actually being sent (run campaign script)
- Click "🔃 Refresh Now" to force update
- Check console for errors

### Issue 2: No Emails in Live Feed

**Symptoms:** Live Feed shows "No emails sent yet"

**Causes & Solutions:**
- **Campaign not started:** Run email script in terminal
- **Wrong time period:** Check if emails were sent outside displayed range
- **CSV file empty:** Verify `sent_tracker.csv` has data
- **File path issue:** Check `utils/windows_paths.py` for correct path

### Issue 3: Test Email Fails to Send

**Symptoms:** Error message after clicking "Send Test Email"

**Common Errors:**

#### SMTP Authentication Failed
- **Cause:** Incorrect password stored in Email Accounts
- **Solution:** Go to Email Accounts page, update password

#### SMTP Connection Error
- **Cause:** Incorrect SMTP host or port
- **Solution:** Verify SMTP settings for your email provider

#### Template Variable Error
- **Cause:** Template has undefined variable
- **Solution:** Go to Templates Manager, fix template syntax

### Issue 4: Campaign Status Not Updating

**Symptoms:** Status stays "Running" even after stopping script

**Solution:**
- Manually click "⏹️ Mark as Stopped"
- Status is UI-only, doesn't control actual scripts

---

## Best Practices

### Before Running Campaigns

1. ✅ Send test emails for ALL verticals
2. ✅ Verify test emails look professional
3. ✅ Check spam score (use mail-tester.com)
4. ✅ Ensure all template variables populate correctly
5. ✅ Test each email account you'll use
6. ✅ Verify business hours configuration

### During Campaigns

1. ✅ Monitor Live Feed for errors
2. ✅ Check success rate stays above 95%
3. ✅ Watch for SMTP authentication errors
4. ✅ Verify emails are spreading across verticals
5. ✅ Keep terminal window visible for script output

### After Campaigns

1. ✅ Mark campaigns as stopped in dashboard
2. ✅ Review final metrics in Dashboard page
3. ✅ Check response tracker for replies
4. ✅ Archive sent_tracker.csv if needed

---

## Files Modified

| File | Purpose |
|------|---------|
| `pages/8_🚀_Campaign_Control.py` | Main Campaign Control page (new file) |
| `integrations/tracker_reader.py` | Already existed, used for reading CSV data |
| `database/models.py` | Already existed, used for accounts/verticals |
| `database/encryption.py` | Already existed, used for password decryption |

**Total:** 1 new file, 520+ lines

---

## Features Summary

### ✅ Implemented

- Campaign status display
- Campaign type selection (initial/followup/both)
- Vertical targeting
- Daily limit override
- Real-time email feed with auto-refresh
- Configurable display count (10-500 emails)
- Color-coded status indicators
- Summary statistics
- Test email form with account selection
- Vertical/template selection for tests
- Customizable test data
- Email preview before sending
- Actual SMTP sending
- Error handling and feedback
- Template variable substitution

### 🚧 Future Enhancements

- Subprocess integration (launch scripts from dashboard)
- Pause/resume campaign controls
- Campaign scheduling
- Email rate throttling controls
- Export live feed to CSV
- Filter live feed by vertical/status
- Test email history tracking
- Bulk test sending (multiple recipients)
- Template A/B testing

---

## Example Workflows

### Workflow 1: Testing New Template

1. Create template in Templates Manager
2. Go to Campaign Control → Test Emails
3. Select account and vertical
4. Enter your email address
5. Customize test data if needed
6. Send test email
7. Check inbox and verify formatting
8. If issues found, edit template and retest

### Workflow 2: Running Daily Campaign

1. Go to Campaign Control tab
2. Verify business hours are active (green checkmark)
3. Select campaign type and vertical
4. Click "▶️ Start Campaign"
5. Open terminal, navigate to scripts folder
6. Run: `python send_initial_outreach.py`
7. Switch to Live Feed tab
8. Enable auto-refresh
9. Monitor emails being sent in real-time
10. Check success rate stays high
11. When complete, press Ctrl+C in terminal
12. Click "⏹️ Mark as Stopped" in dashboard

### Workflow 3: Troubleshooting Failed Sends

1. Notice errors in Live Feed (red rows)
2. Check error messages in status column
3. If SMTP auth error:
   - Go to Email Accounts page
   - Update password for failing account
   - Send test email to verify fix
4. If template error:
   - Go to Templates Manager
   - Fix template variable syntax
   - Send test email to verify
5. Resume campaign once fixed

---

## API Reference

### Session State Variables

```python
st.session_state.campaign_process = None  # Placeholder for future subprocess integration
st.session_state.campaign_running = False  # Boolean: Is campaign marked as running?
st.session_state.last_email_count = 0     # Cache for email count
```

### Key Functions Used

#### From integrations.tracker_reader:
```python
read_sent_tracker() -> pd.DataFrame
read_response_tracker() -> pd.DataFrame
```

#### From database.models:
```python
get_email_accounts(active_only=True) -> List[Dict]
get_verticals(active_only=True) -> List[Dict]
get_templates(vertical_id, template_type, active_only) -> List[Dict]
```

#### From database.encryption:
```python
decrypt_password(encrypted_password: bytes) -> str
```

---

## Testing Checklist

After implementing Campaign Control page, verify:

- [ ] Page loads without errors
- [ ] All three tabs display correctly
- [ ] Campaign status indicators show current state
- [ ] Business hours detection works (9am-3pm EST, Mon-Fri)
- [ ] Sent Today count matches actual sent emails
- [ ] Campaign type dropdown has all options
- [ ] Vertical selector shows configured verticals
- [ ] Daily limit override works
- [ ] Live Feed displays recent emails
- [ ] Auto-refresh updates every 5 seconds
- [ ] Status colors show correctly (green/red)
- [ ] Summary stats calculate correctly
- [ ] Test email form has all required fields
- [ ] Account dropdown shows configured accounts
- [ ] Vertical dropdown shows configured verticals
- [ ] Test data fields accept input
- [ ] Email preview displays correctly
- [ ] Test email actually sends to recipient
- [ ] SMTP errors show helpful messages
- [ ] Template variables substitute correctly

---

## Support

### Error Messages

#### "❌ No email accounts configured!"
- **Solution:** Go to Email Accounts page and add an account

#### "❌ No verticals configured!"
- **Solution:** Go to Verticals Manager and create a vertical

#### "❌ No {message_type} template found for {vertical_id}"
- **Solution:** Go to Templates Manager and create the missing template

#### "❌ SMTP Authentication Failed"
- **Solution:** Update email account password in Email Accounts page

#### "❌ Template has undefined variable: {variable_name}"
- **Solution:** Fix template in Templates Manager or add variable to test data

### Debugging

Enable debug mode to see detailed information:
```python
# In Campaign Control page
st.write("Debug Info:")
st.write("Campaign Running:", st.session_state.campaign_running)
st.write("Sent Tracker Data:", read_sent_tracker())
st.write("Accounts:", models.get_email_accounts())
st.write("Verticals:", models.get_verticals())
```

---

## Changelog

### Version 1.0 (November 4, 2025)
- ✅ Initial implementation of Campaign Control page
- ✅ Added three-tab interface
- ✅ Implemented real-time live feed with auto-refresh
- ✅ Created test email functionality with SMTP sending
- ✅ Added campaign status indicators
- ✅ Integrated with existing tracker files
- ✅ Fixed deprecated pandas `applymap` → `map`
- ✅ Added error handling for auto-refresh

---

**Implemented By:** Claude Code
**Date:** November 4, 2025
**Version:** 1.0.0
