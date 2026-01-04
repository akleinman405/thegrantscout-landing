# Email Campaign System

Unified email campaign management for TheGrantScout.

## Quick Start

```bash
# Show campaign status
python campaign_manager.py status

# Send emails (initial + followup)
python campaign_manager.py send

# Check for bounces/replies
python campaign_manager.py check

# Force sync to CRM
python campaign_manager.py sync
```

## Commands

| Command | Description |
|---------|-------------|
| `send` | Send emails (initial and/or followup) |
| `send --type initial` | Send only initial outreach emails |
| `send --type followup` | Send only follow-up emails |
| `send --dry-run` | Preview without sending |
| `check` | Check Gmail for bounces and replies |
| `check --days 7` | Check last 7 days only |
| `status` | Show campaign statistics |
| `sync` | Force sync emails to CRM |

## Features

- **Auto-save progress** on Ctrl+C or natural close
- **Auto-check bounces** on close (via Gmail API)
- **Auto-sync to CRM** every 100 emails (or on close)
- **Business hours enforcement** (Mon-Fri, 9am-7pm EST)
- **Duplicate prevention** (won't email same person twice)
- **Coordination** between initial and followup sends

## Folder Structure

```
Email Campaign 2025-11-3/
├── campaign_manager.py    # Main script (use this!)
├── config.py              # Email templates, settings
├── coordination.py        # Capacity tracking between sends
├── crm_integration.py     # Supabase CRM sync
├── shutdown_hooks.py      # Auto-save/sync helpers
├── TRACKER_SETUP.md       # Gmail API setup guide
├── credentials/           # Gmail OAuth credentials
├── reports/               # Generated analytics reports
├── OLD/                   # Archived old scripts/docs
└── README.md              # This file
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install pandas pytz google-auth-oauthlib google-api-python-client requests
   ```

2. **Set environment variables:**
   ```bash
   export OUTREACH_EMAIL="your@email.com"
   export OUTREACH_NAME="Your Name"
   export OUTREACH_APP_PASSWORD="your-app-password"
   ```

3. **Set up Gmail API (for bounce checking):**
   - Follow [TRACKER_SETUP.md](./TRACKER_SETUP.md)
   - Place `credentials.json` in `credentials/` folder

4. **Run campaign:**
   ```bash
   python campaign_manager.py send
   ```

## Data Files

Located in parent folder (`Email_Campaign/`):

- `grant_alerts_prospects.csv` - Prospect list
- `sent_tracker.csv` - Email send history
- `response_tracker.csv` - Reply/bounce tracking

## What's in OLD/

The `OLD/` folder contains archived scripts and documentation that have been superseded by the new consolidated `campaign_manager.py`. Keeping them for reference but they're no longer in use.

## License

Internal tool for TheGrantScout campaign management.
