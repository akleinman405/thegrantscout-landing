# Campaign Tracker Setup Guide

## Overview

This setup guide enables automated bounce detection and reply tracking for your email campaigns via the Gmail API. The tracker monitors your Gmail inbox for bounces, out-of-office replies, and genuine prospect responses, automatically updating your campaign CSV files with this intelligence.

**What it does:**
- Detects hard bounces (invalid addresses) and soft bounces (full mailboxes)
- Identifies out-of-office auto-replies
- Flags genuine prospect replies for manual follow-up
- Updates campaign CSV files with tracking data
- Generates analytics reports on campaign performance

**Time to complete:** Approximately 15 minutes

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed on your system
- **Gmail account** (the same account used to send campaigns)
- **Google Cloud account** (free tier is sufficient)
- **Basic command line familiarity**

## Step 1: Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements_tracker.txt
```

**What gets installed:**
- `google-auth` - OAuth2 authentication
- `google-auth-oauthlib` - OAuth2 flow handling
- `google-auth-httplib2` - HTTP client for Google APIs
- `google-api-python-client` - Gmail API client library

**Troubleshooting:**
- If `pip` is not found, try `pip3` instead
- On Windows, you may need to run Command Prompt as Administrator
- On macOS/Linux, you may need to use `pip install --user` if you don't have admin rights

## Step 2: Create Google Cloud Project

1. **Navigate to Google Cloud Console:**
   - Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Sign in with your Google account (use the same account as your Gmail)

2. **Create a new project:**
   - Click the project dropdown at the top of the page
   - Click "New Project"
   - Enter project name: `TheGrantScout Tracker` (or your preferred name)
   - Leave organization field as "No organization" unless you have one
   - Click "Create"

3. **Wait for project creation:**
   - This takes 10-30 seconds
   - You'll see a notification when complete

4. **Select your project:**
   - Click the project dropdown again
   - Select your newly created project

**Note:** Write down your project name - you may need it for reference.

## Step 3: Enable Gmail API

1. **Navigate to API Library:**
   - In the left sidebar, click "APIs & Services" > "Library"
   - Or use the search bar at the top and search for "API Library"

2. **Find Gmail API:**
   - In the API Library search box, type "Gmail API"
   - Click on "Gmail API" from the results

3. **Enable the API:**
   - Click the blue "Enable" button
   - Wait for the API to be enabled (5-10 seconds)
   - You'll be redirected to the API overview page

## Step 4: Create OAuth2 Credentials

### 4.1 Configure OAuth Consent Screen

If this is your first time creating credentials, you'll need to configure the consent screen:

1. **Navigate to OAuth consent screen:**
   - Go to "APIs & Services" > "OAuth consent screen"

2. **Select user type:**
   - Choose "External" (allows any Gmail user)
   - Click "Create"

3. **Fill in App Information:**
   - **App name:** `Campaign Tracker` (or your preferred name)
   - **User support email:** Select your email from dropdown
   - **Developer contact information:** Enter your email address
   - Leave other fields blank or default
   - Click "Save and Continue"

4. **Scopes (Step 2):**
   - Click "Add or Remove Scopes"
   - Search for `gmail.readonly`
   - Check the box next to `.../auth/gmail.readonly` (read-only access)
   - Click "Update"
   - Click "Save and Continue"

5. **Test Users (Step 3):**
   - Click "Add Users"
   - Enter your Gmail address (the one you'll use for campaigns)
   - Click "Add"
   - Click "Save and Continue"

6. **Summary (Step 4):**
   - Review your settings
   - Click "Back to Dashboard"

### 4.2 Create OAuth Client ID

1. **Navigate to Credentials:**
   - Go to "APIs & Services" > "Credentials"

2. **Create new credentials:**
   - Click "+ Create Credentials" at the top
   - Select "OAuth client ID"

3. **Configure the client:**
   - **Application type:** Select "Desktop app" from dropdown
   - **Name:** `Campaign Tracker` (or your preferred name)
   - Click "Create"

4. **Credentials created:**
   - You'll see a popup with "OAuth client created"
   - Click "OK" (we'll download in the next step)

## Step 5: Download Credentials

1. **Find your credentials:**
   - On the Credentials page, you'll see your OAuth 2.0 Client IDs listed
   - Find the one you just created ("Campaign Tracker")

2. **Download JSON file:**
   - Click the download icon (⬇️) on the right side of the row
   - The file will download to your default downloads folder
   - It will have a name like `client_secret_XXXXX.apps.googleusercontent.com.json`

3. **Rename and move the file:**
   - Rename the downloaded file to exactly: `credentials.json`
   - Move it to: `/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences/Email Campaign 2025-11-3/tracker/credentials/`

**Security reminder:** This file contains your OAuth client ID and secret. Do not share it publicly or commit it to version control.

## Step 6: First Run

Now you're ready to authorize the tracker to access your Gmail account.

1. **Navigate to the tracker folder:**
   ```bash
   cd "/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences/Email Campaign 2025-11-3/tracker"
   ```

2. **Run the tracker in interactive mode:**
   ```bash
   python campaign_tracker.py --interactive
   ```

3. **Authorization flow:**
   - A browser window will automatically open
   - You'll see "Sign in with Google"
   - Sign in with your campaign Gmail account

4. **Grant permissions:**
   - You may see "Google hasn't verified this app" warning
   - Click "Advanced" then "Go to Campaign Tracker (unsafe)"
   - This is safe - it's your own app!
   - Review the permissions (read-only access to Gmail)
   - Click "Allow"

5. **Success:**
   - You'll see "The authentication flow has completed"
   - Close the browser tab
   - Return to your terminal

6. **First scan:**
   - The tracker will scan your inbox for campaign-related emails
   - Review the detected bounces, OOO replies, and responses
   - Confirm to update CSV files (or decline to review first)

**What just happened:**
- A `token.json` file was created in the `tracker/credentials/` folder
- This stores your OAuth access token (auto-refreshes when needed)
- You won't need to authorize again unless you delete this file

## Usage

### Interactive Mode (Recommended)

Run the tracker and review updates before they're applied:

```bash
python campaign_tracker.py --interactive
```

**What happens:**
1. Scans Gmail inbox for campaign emails (last 30 days by default)
2. Detects bounces, OOO, and replies
3. Shows you what will be updated
4. Asks for confirmation before writing to CSV files
5. Generates a timestamped report

**When to use:** Daily or weekly checks, when you want to review before updating.

### Auto Mode

Automatically update CSV files without prompts:

```bash
python campaign_tracker.py --auto
```

**What happens:**
1. Scans inbox
2. Automatically updates CSV files
3. Generates report
4. Exits without user interaction

**When to use:** Scheduled automation (cron jobs, Task Scheduler), when you trust the detection logic.

### Custom Date Range

Limit scanning to recent emails:

```bash
# Check last 7 days only
python campaign_tracker.py --days 7

# Check last 24 hours
python campaign_tracker.py --days 1

# Check last 60 days
python campaign_tracker.py --days 60
```

**Why use this:** Faster scans, reduce API quota usage, focus on recent campaigns.

### Dry Run (Preview Only)

See what would be updated without making changes:

```bash
python campaign_tracker.py --dry-run
```

**What happens:**
1. Scans inbox
2. Shows detected bounces, OOO, and replies
3. Does NOT update CSV files
4. Does NOT generate reports

**When to use:** Testing, debugging, verifying detection logic.

### Combine Options

```bash
# Scan last 7 days in auto mode
python campaign_tracker.py --auto --days 7

# Scan last 3 days, dry run to preview
python campaign_tracker.py --dry-run --days 3
```

## Files Created

The tracker creates and updates several files:

### Auto-Generated Files

**`credentials/token.json`**
- Stores your OAuth2 access and refresh tokens
- Auto-created on first run in the `credentials/` subfolder
- Auto-refreshed when expired (every ~1 hour)
- **Keep private** - contains authentication credentials

**`reports/campaign_report_YYYY-MM-DD_HHMM.csv`**
- Timestamped analytics reports stored in `reports/` subfolder
- One created per tracker run
- Contains: email, status, bounce_type, reply_received, timestamp
- Use for historical analysis and reporting

### Updated Campaign Files

The tracker updates these existing files with tracking data:

- `arborbrook_prospects_campaign.csv`
- `ka_ulukoa_prospects_campaign.csv`
- `rhf_prospects_campaign.csv`

**Columns added/updated:**
- `bounce_detected` - TRUE/FALSE
- `bounce_type` - "hard" (invalid address), "soft" (temp failure), "ooo" (out of office)
- `reply_received` - TRUE/FALSE
- `last_checked` - Timestamp of last tracker run

## Tracking Reports

Each run generates a CSV report with these columns:

| Column | Description | Example Values |
|--------|-------------|----------------|
| `email` | Recipient email address | `grants@foundation.org` |
| `status` | Email delivery status | `delivered`, `bounced`, `replied` |
| `bounce_type` | Type of bounce (if bounced) | `hard`, `soft`, `ooo`, `null` |
| `reply_received` | Whether prospect replied | `TRUE`, `FALSE` |
| `timestamp` | When status was detected | `2025-11-30 14:32:15` |
| `subject` | Email subject line | `Re: Grant opportunity...` |
| `snippet` | First 100 chars of email | `Thank you for reaching...` |

**Use reports for:**
- Calculate bounce rates by campaign
- Identify foundations that replied
- Track response times
- Measure campaign effectiveness

## Troubleshooting

### "credentials.json not found"

**Problem:** The tracker can't find your OAuth credentials file.

**Solution:**
1. Download credentials from Google Cloud Console (Step 5 above)
2. Rename to exactly `credentials.json` (case-sensitive)
3. Place in the `tracker/credentials/` subfolder
4. Verify path: `/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences/Email Campaign 2025-11-3/tracker/credentials/credentials.json`

### "Access blocked: This app isn't verified"

**Problem:** Google is warning that your app hasn't been verified by Google.

**Solution:**
1. Click "Advanced" link on the warning page
2. Click "Go to Campaign Tracker (unsafe)"
3. This is safe - you created the app yourself
4. Alternative: Add your email as a test user in OAuth consent screen

### "Access blocked: Campaign Tracker has not completed the Google verification process"

**Problem:** Your app isn't in testing mode or you're not added as a test user.

**Solution:**
1. Go to Google Cloud Console > OAuth consent screen
2. Ensure publishing status is "Testing"
3. Under "Test users", add your Gmail address
4. Save changes and try authorizing again

### "The user did not grant your app the permissions it requested"

**Problem:** You clicked "Deny" or closed the authorization window.

**Solution:**
1. Run the tracker again: `python campaign_tracker.py --interactive`
2. When the browser opens, click "Allow" to grant permissions
3. If you intentionally want to deny, the tracker won't work without Gmail access

### "Quota exceeded: userRateLimitExceeded"

**Problem:** You've hit Gmail API daily quota limits.

**Solution:**
- Gmail API allows 1 billion quota units per day (free tier)
- Reading emails uses 5 units per message
- You can read ~200 million messages per day (more than enough)
- If you somehow hit this, wait 24 hours or run less frequently

**More likely issue:** Running tracker too frequently. Recommended: once per day.

### "Invalid grant: Token has been expired or revoked"

**Problem:** Your `token.json` file is invalid or corrupted.

**Solution:**
1. Delete `token.json` file
2. Run tracker again: `python campaign_tracker.py --interactive`
3. You'll need to re-authorize (browser will open)
4. New token.json will be created

### "ModuleNotFoundError: No module named 'google'"

**Problem:** Google API libraries aren't installed.

**Solution:**
```bash
pip install -r requirements_tracker.txt
```

If that doesn't work:
```bash
pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### No emails detected / No bounces found

**Problem:** Tracker isn't finding campaign-related emails.

**Possible causes:**
1. **Emails not sent yet** - Run campaigns first, then run tracker
2. **Date range too narrow** - Try: `python campaign_tracker.py --days 60`
3. **Different Gmail account** - Ensure token.json is for the account that SENT the campaigns
4. **Emails in Spam/Trash** - Tracker only scans Inbox by default

**Debug:**
```bash
# Run in dry-run mode to see what's detected
python campaign_tracker.py --dry-run --days 60

# Check if any emails match your campaign subjects
```

### CSV files not updating

**Problem:** Tracker runs but CSV files don't change.

**Possible causes:**
1. **Running in dry-run mode** - Remove `--dry-run` flag
2. **No updates to apply** - No new bounces or replies detected
3. **File permissions** - Ensure CSV files aren't read-only
4. **File open in Excel** - Close CSV files before running tracker

**Verify:**
```bash
# Run in interactive mode to see what would update
python campaign_tracker.py --interactive
```

### Browser doesn't open on first run

**Problem:** Authorization flow should open browser, but nothing happens.

**Solution (Manual authorization):**
1. Look in terminal output for a URL starting with `https://accounts.google.com/o/oauth2/auth...`
2. Copy the entire URL
3. Paste it into your browser manually
4. Complete authorization
5. Browser will show "The authentication flow has completed"

**For headless servers:**
```bash
# Use this flow if running on a remote server without a display
python campaign_tracker.py --noauth_local_webserver
```

## Security Notes

### What the tracker can access

**Permissions requested:**
- `https://www.googleapis.com/auth/gmail.readonly` - Read-only access to Gmail

**What this means:**
- Can READ your emails, labels, threads
- CANNOT send emails
- CANNOT delete emails
- CANNOT modify emails
- CANNOT access other Google services (Drive, Calendar, etc.)

### Protecting your credentials

**credentials.json**
- Contains: OAuth2 client ID and client secret
- Keep private: Do not share publicly or commit to GitHub
- Risks if exposed: Someone could create OAuth tokens for your app (but still need to authorize with your Gmail)

**token.json**
- Contains: OAuth2 access token and refresh token
- Keep private: Do not share or commit to version control
- Risks if exposed: Direct access to your Gmail (read-only) until token expires or is revoked

**Recommended .gitignore entries:**
```
tracker/credentials/credentials.json
tracker/credentials/token.json
tracker/reports/
```

### Revoking access

If you need to revoke the tracker's access to Gmail:

1. **Via Google Account Settings:**
   - Go to [https://myaccount.google.com/permissions](https://myaccount.google.com/permissions)
   - Find "Campaign Tracker" or your app name
   - Click "Remove Access"

2. **Via local files:**
   - Delete `tracker/credentials/token.json`
   - The tracker will ask for authorization again on next run

### Best practices

- Run tracker from your personal computer (not shared machines)
- Don't store credentials on cloud drives (Dropbox, OneDrive)
- Use a dedicated Gmail account for campaigns (not your personal email)
- Review OAuth consent screen settings periodically
- Keep credentials.json and token.json out of version control

## Automation (Optional)

### Windows Task Scheduler

Run tracker daily at 9 AM automatically:

1. Open Task Scheduler (search in Start menu)
2. Click "Create Basic Task"
3. Name: "Campaign Tracker Daily"
4. Trigger: Daily at 9:00 AM
5. Action: Start a program
6. Program: `C:\Python\python.exe` (your Python path)
7. Arguments: `campaign_tracker.py --auto`
8. Start in: `C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Campaign 2025-11-3\tracker`
9. Finish and test

### macOS/Linux Cron Job

Add to crontab (`crontab -e`):

```bash
# Run tracker daily at 9 AM
0 9 * * * cd "/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences/Email Campaign 2025-11-3/tracker" && /usr/bin/python3 campaign_tracker.py --auto >> tracker.log 2>&1
```

**Important for automation:**
- Use `--auto` mode (no user interaction required)
- Redirect output to log file for debugging
- Ensure token.json exists (run manually first to authorize)
- Test the command manually before scheduling

## Getting Help

### Check the logs

If tracker produces errors, check:

1. **Console output** - Error messages and stack traces
2. **reports/** - Last successful run data
3. **tracker.log** - If you set up automation with logging

### Common error messages

| Error | Meaning | See Section |
|-------|---------|-------------|
| `FileNotFoundError: credentials.json` | Missing OAuth credentials | Troubleshooting > credentials.json |
| `RefreshError: invalid_grant` | Token expired or revoked | Troubleshooting > Invalid grant |
| `HttpError 403: Request had insufficient authentication scopes` | Wrong permissions | Step 4.1 > Scopes |
| `HttpError 429: Resource has been exhausted` | Quota exceeded | Troubleshooting > Quota exceeded |

### Support resources

- **Gmail API Documentation:** [https://developers.google.com/gmail/api](https://developers.google.com/gmail/api)
- **OAuth2 Troubleshooting:** [https://developers.google.com/identity/protocols/oauth2/web-server#errors](https://developers.google.com/identity/protocols/oauth2/web-server#errors)
- **Python Client Library:** [https://github.com/googleapis/google-api-python-client](https://github.com/googleapis/google-api-python-client)

## Next Steps

Once setup is complete:

1. **Run your first campaign** using the prepared CSV files
2. **Wait 24-48 hours** for bounces and replies
3. **Run the tracker** to update your CSV files
4. **Review the report** to see bounce rates and responses
5. **Follow up** with prospects who replied (marked in CSV)
6. **Exclude bounces** from future campaigns

**Recommended workflow:**
- Send campaigns on Monday
- Run tracker on Wednesday (48 hours later)
- Review replies and schedule follow-ups
- Run tracker again on Friday to catch late replies
- Generate weekly analytics report

## Summary

You've now set up automated bounce detection and reply tracking for your email campaigns. The tracker will:

- Monitor your Gmail inbox for campaign-related emails
- Detect bounces (hard, soft, and out-of-office)
- Identify genuine prospect replies
- Update your campaign CSV files automatically
- Generate analytics reports for performance tracking

**Remember:**
- Run tracker AFTER sending campaigns (wait 24-48 hours)
- Review reports to measure campaign effectiveness
- Use interactive mode until you trust the automation
- Keep credentials.json and token.json private
- Check tracking reports for insights on engagement

Happy tracking!
