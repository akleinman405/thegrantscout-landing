"""
Shared configuration for email validation campaign system.
Contains email templates, SMTP settings, and campaign parameters.
"""

import os

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

# Test Mode
TEST_MODE = False  # Set to True to send only 9 test emails (3 per vertical)

# Gmail Credentials
YOUR_EMAIL = "alec.m.kleinman@gmail.com"
YOUR_NAME = "Alec Kleinman"
APP_PASSWORD = ""  # FILL THIS IN - Get from https://myaccount.google.com/apppasswords

# SMTP Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# File Paths
BASE_DIR = r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"
INPUT_CSV_FOOD = os.path.join(BASE_DIR, "food_recall_prospects.csv")
INPUT_CSV_DEBARMENT = os.path.join(BASE_DIR, "debarment_prospects.csv")
INPUT_CSV_GRANTS = os.path.join(BASE_DIR, "grant_alerts_prospects.csv")
SENT_TRACKER = os.path.join(BASE_DIR, "sent_tracker.csv")
RESPONSE_TRACKER = os.path.join(BASE_DIR, "response_tracker.csv")
ERROR_LOG = os.path.join(BASE_DIR, "error_log.csv")

# Sending Limits
EMAILS_PER_VERTICAL_PER_DAY = 150
TOTAL_DAILY_LIMIT = 450
BUSINESS_HOURS_START = 9   # 9 AM EST
BUSINESS_HOURS_END = 15    # 3 PM EST (actually 3pm, not 15 hours after midnight)
TIMEZONE = 'US/Eastern'

# Delay Settings (seconds)
BASE_DELAY_MIN = 5
BASE_DELAY_MAX = 10
BREAK_FREQUENCY_MIN = 10  # Take break every 10-20 emails
BREAK_FREQUENCY_MAX = 20
BREAK_DURATION_MIN = 30   # Break lasts 30-90 seconds
BREAK_DURATION_MAX = 90

# ============================================================================
# SUBJECT LINES - EDIT THESE AS NEEDED
# ============================================================================

# Food Recall Alert System - Subject Lines
FOOD_RECALL_SUBJECTS = [
    "Food recall tracking question",
]

# Debarment Monitor System - Subject Lines
DEBARMENT_SUBJECTS = [
    "Curious how you handle vendor checks"
]

# Grant Alert System - Subject Lines
GRANT_ALERT_SUBJECTS = [
    "Built something for nonprofit funding"
]

# Follow-up Subject Lines
FOOD_RECALL_FOLLOWUP_SUBJECTS = [
    "Quick follow-up on FDA recall system"
]

DEBARMENT_FOLLOWUP_SUBJECTS = [
    "Quick follow-up on debarment monitoring question"
]

GRANT_ALERT_FOLLOWUP_SUBJECTS = [
    "Quick follow-up on grant monitoring question"
]

# ============================================================================
# EMAIL TEMPLATES
# ============================================================================

# Food Recall Alert - Initial Email
FOOD_RECALL_INITIAL = """Hi,

I built a system that monitors FDA/USDA recall lists and automatically alerts restaurants when products they use are recalled.

Right now I've heard checking recalls manually can take 10-15 hours per month. I'm guessing you've experienced something similar'.

Looking for 10 restaurants to test this for free in exchange for feedback. If you're one of the first 10, you get lifetime free access.

Let me know if you're interested!.

Alec Kleinman
(281) 245-4596"""

# Food Recall Alert - Follow-up Email
FOOD_RECALL_FOLLOWUP = """Hi,

Not sure if you saw my email about free recall monitoring.

Only 3 spots left out of 10. After that, it'll be $99/month when we launch.

Let me know if you want to try it out!

Alec Kleinman
(281) 245-4596"""

# Debarment Monitor - Initial Email
DEBARMENT_INITIAL = """Hi,

I built a system that monitors your vendors/subcontractors against the SAM.gov exclusion list and alerts you instantly if any get debarred.

FAR 9.404 requires checking before awarding contracts and throughout the relationship, but most people just spot-check manually.

Looking for 10 federal contractors to test this in exchange for feedback. First 10 get lifetime free access.

Let me know if you want to try it out!

Alec Kleinman
(281) 245-4596"""

# Debarment Monitor - Follow-up Email
DEBARMENT_FOLLOWUP = """Hi,

Following up on the debarment monitoring tool.

6 contractors already signed up for early access. Need 4 more.

After that, it goes to $199/month at launch.

Let me know if you want to try it out!

Alec Kleinman
(281) 245-4596"""

# Grant Alert - Initial Email
GRANT_ALERT_INITIAL = """Hi,

I built a system that monitors Grants.gov and alerts nonprofits when relevant grant opportunities match their mission/activities.

Most nonprofits manually check or miss opportunities entirely. This automates it.

Looking for 10 nonprofits to test in exchange for feedback. First 10 get lifetime free access.

Let me know if you're interested!

Alec Kleinman
(281) 245-4596"""

# Grant Alert - Follow-up Email
GRANT_ALERT_FOLLOWUP = """Hi,

Quick follow-up on the grant alert system.

7 nonprofits have signed up for early access. Looking for 3 more.

After that, it'll be $99/month when we launch to the public.

Let me know if you're interested!

Alec Kleinman
(281) 245-4596"""

# ============================================================================
# VERTICAL CONFIGURATION
# ============================================================================

VERTICALS = {
    'food_recall': {
        'name': 'Food Recall',
        'csv_file': INPUT_CSV_FOOD,
        'initial_subject_lines': FOOD_RECALL_SUBJECTS,
        'followup_subject_lines': FOOD_RECALL_FOLLOWUP_SUBJECTS,
        'initial_template': FOOD_RECALL_INITIAL,
        'followup_template': FOOD_RECALL_FOLLOWUP,
    },
    'debarment': {
        'name': 'Debarment',
        'csv_file': INPUT_CSV_DEBARMENT,
        'initial_subject_lines': DEBARMENT_SUBJECTS,
        'followup_subject_lines': DEBARMENT_FOLLOWUP_SUBJECTS,
        'initial_template': DEBARMENT_INITIAL,
        'followup_template': DEBARMENT_FOLLOWUP,
    },
    'grant_alerts': {
        'name': 'Grant Alerts',
        'csv_file': INPUT_CSV_GRANTS,
        'initial_subject_lines': GRANT_ALERT_SUBJECTS,
        'followup_subject_lines': GRANT_ALERT_FOLLOWUP_SUBJECTS,
        'initial_template': GRANT_ALERT_INITIAL,
        'followup_template': GRANT_ALERT_FOLLOWUP,
    }
}
