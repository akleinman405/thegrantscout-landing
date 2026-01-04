"""
Shared configuration for email validation campaign system.
Contains email templates, SMTP settings, and campaign parameters.
"""

import os

# ============================================================================
# TEST MODE CONFIGURATION - Edit these for testing
# ============================================================================

TEST_MODE = False  # Set to True to send test emails only

# Multiple test email addresses (all will receive the test email)
TEST_EMAIL_ADDRESSES = [
    "alec@kleinmansolutions.com",
    "alec.m.kleinman@gmail.com",
    "alec@kleinmanventures.com",
    "alecspots@gmail.com"
]

TEST_VERTICAL = "grant_alerts"  # Only grant_alerts is active
TEST_EMAIL_TYPE = "followup"  # Which email type to test: "initial" or "followup"

# ============================================================================
# ACTIVE VERTICALS - Grant Alerts is the only active vertical
# ============================================================================

# Only grant_alerts is active - food_recall and debarment are deprecated
ACTIVE_VERTICALS = ["grant_alerts"]

# -----------------------------
# Sender / SMTP
# -----------------------------
YOUR_EMAIL    = os.getenv("OUTREACH_EMAIL", "")
YOUR_NAME     = os.getenv("OUTREACH_NAME", "")
APP_PASSWORD  = os.getenv("OUTREACH_APP_PASSWORD", "")
SMTP_SERVER   = os.getenv("OUTREACH_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("OUTREACH_SMTP_PORT", "587"))
# ============================================================================
# FILE PATHS
# ============================================================================

# Auto-detect OS and set appropriate path
import platform
if platform.system() == 'Windows':
    BASE_DIR = r"C:\TheGrantScout\4. Sales & Marketing\Email Campaign"
else:
    # macOS / Linux - go up one level from script directory to get Email_Campaign folder
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV_FOOD = os.path.join(BASE_DIR, "food_recall_prospects.csv")
INPUT_CSV_DEBARMENT = os.path.join(BASE_DIR, "debarment_prospects.csv")
INPUT_CSV_GRANTS = os.path.join(BASE_DIR, "grant_alerts_prospects.csv")
SENT_TRACKER = os.path.join(BASE_DIR, "sent_tracker.csv")
RESPONSE_TRACKER = os.path.join(BASE_DIR, "response_tracker.csv")
ERROR_LOG = os.path.join(BASE_DIR, "error_log.csv")

# ============================================================================
# SENDING LIMITS
# ============================================================================

EMAILS_PER_VERTICAL_PER_DAY = 150  # Max per vertical (only applies if 3 verticals active)
TOTAL_DAILY_LIMIT = 400            # Total daily limit (24-hour rolling window)
BUSINESS_HOURS_START = 9           # 9 AM EST
BUSINESS_HOURS_END = 19            # 7 PM EST
TIMEZONE = 'US/Eastern'

# Pacing Mode: Conservative (recommended)
# Maintains consistent 75 emails/hour pacing regardless of start time
# - Start at 9am (6 hours left) → Send 450 emails at 75/hour
# - Start at 1pm (2 hours left) → Send 150 emails at 75/hour
# - Next day at 9am → Can send full 450 again
# This prevents spam-like bursts and keeps daily capacity predictable
USE_CONSERVATIVE_PACING = True

# Natural hourly rate (calculated from full business day)
# 450 emails ÷ 6 hours = 75 emails/hour
NATURAL_HOURLY_RATE = TOTAL_DAILY_LIMIT / (BUSINESS_HOURS_END - BUSINESS_HOURS_START)

# ============================================================================
# DELAY SETTINGS (Anti-Spam)
# ============================================================================

BASE_DELAY_MIN = 5          # Min seconds between emails
BASE_DELAY_MAX = 10         # Max seconds between emails
BREAK_FREQUENCY_MIN = 10    # Take break every 10-20 emails
BREAK_FREQUENCY_MAX = 20
BREAK_DURATION_MIN = 30     # Break lasts 30-90 seconds
BREAK_DURATION_MAX = 90

# ============================================================================
# SUBJECT LINES
# ============================================================================

# Food Recall Alert System - Subject Lines
FOOD_RECALL_SUBJECTS = [
    "Food recall tracking question",
]

# Debarment Monitor System - Subject Lines
DEBARMENT_SUBJECTS = [
    "Debarment monitoring question"
]

# Grant Alert System - Subject Lines
GRANT_ALERT_SUBJECTS = [
    "Help Finding Grant Opportunities"
]

# Follow-up Subject Lines
FOOD_RECALL_FOLLOWUP_SUBJECTS = [
    "Quick follow-up on FDA recall system"
]

DEBARMENT_FOLLOWUP_SUBJECTS = [
    "Quick follow-up on debarment monitoring question"
]

GRANT_ALERT_FOLLOWUP_SUBJECTS = [
    "Follow-up on funding help"
]

# ============================================================================
# EMAIL TEMPLATES
# ============================================================================

# Food Recall Alert - Initial Email
FOOD_RECALL_INITIAL = """Hi{greeting},

I built a system that monitors FDA/USDA recall lists and automatically alerts restaurants when products they use are recalled.

Looking for 10 restaurants to test this for free in exchange for feedback. If you're one of the first 10, you'll get lifetime free access.

Let me know if you're interested!

Alec Kleinman
(281) 245-4596"""

# Food Recall Alert - Follow-up Email
FOOD_RECALL_FOLLOWUP = """Hi{greeting},

Not sure if you saw my email about free recall monitoring.

Only 3 spots left out of 10. After that, it'll be $99/month when we launch.

Let me know if you want to try it out!

Alec Kleinman
(281) 245-4596"""

# Debarment Monitor - Initial Email
DEBARMENT_INITIAL = """Hi{greeting},

I built a system that monitors a company's vendors/subcontractors against the SAM.gov exclusion list and sends alerts instantly if any get debarred.

Looking for 10 federal contractors to test this in exchange for feedback. First 10 get lifetime free access.

Let me know if you're interested!

Alec Kleinman
(281) 245-4596"""

# Debarment Monitor - Follow-up Email
DEBARMENT_FOLLOWUP = """Hi{greeting},

Following up on the debarment monitoring tool.

6 contractors already signed up for early access and we just need 4 more.

After that, it goes to $199/month at launch.

Let me know if you want to try it out.

Alec Kleinman
(281) 245-4596"""

# Grant Alert - Initial Email
GRANT_ALERT_INITIAL = """Hi{greeting},

I built an AI tool that monitors grant opportunities and sends a weekly email report with the highly relevant opportunities and how best to position yourself when applying.

We've had a few nonprofits test it out and we're looking for feedback from a few more.

Let me know if you're interested. I just need an email address to send alerts to, plus a quick survey so I know what to match you with.

Also feel free to give me a call so I can introduce myself: (281)245-4596

Best,
Alec Kleinman
(281) 245-4596
Linkedin: https://www.linkedin.com/in/alec-kleinman-3670381b7/"""

# Grant Alert - Follow-up Email
GRANT_ALERT_FOLLOWUP = """Hi{greeting}

Last month I reached out about our new AI grant matching tool. 

Quick update: We finished beta testing with 6 nonprofits and are launching in January. 

Based on feedback, we shifted from weekly alerts to a monthly report with 5 curated foundation matches, funder intelligence, and positioning strategy.

Sample report: https://thegrantscout.com

Founding member pricing is $99/month (or $83/month annually).

Interested? Book a quick call:
https://calendly.com/alec_kleinman/meeting-with-alec

Best,
Alec Kleinman
(281) 245-4596

---
Not relevant? Reply "irrelevant" and I'll remove you from future emails."""

# ============================================================================
# VERTICAL CONFIGURATION
# NOTE: Only 'grant_alerts' is active. food_recall and debarment are deprecated
#       but kept here for historical reference.
# ============================================================================

VERTICALS = {
    'food_recall': {  # DEPRECATED - not in use
        'name': 'Food Recall',
        'csv_file': INPUT_CSV_FOOD,
        'initial_subject_lines': FOOD_RECALL_SUBJECTS,
        'followup_subject_lines': FOOD_RECALL_FOLLOWUP_SUBJECTS,
        'initial_template': FOOD_RECALL_INITIAL,
        'followup_template': FOOD_RECALL_FOLLOWUP,
    },
    'debarment': {  # DEPRECATED - not in use
        'name': 'Debarment',
        'csv_file': INPUT_CSV_DEBARMENT,
        'initial_subject_lines': DEBARMENT_SUBJECTS,
        'followup_subject_lines': DEBARMENT_FOLLOWUP_SUBJECTS,
        'initial_template': DEBARMENT_INITIAL,
        'followup_template': DEBARMENT_FOLLOWUP,
    },
    'grant_alerts': {  # ACTIVE - primary vertical
        'name': 'Grant Alerts',
        'csv_file': INPUT_CSV_GRANTS,
        'initial_subject_lines': GRANT_ALERT_SUBJECTS,
        'followup_subject_lines': GRANT_ALERT_FOLLOWUP_SUBJECTS,
        'initial_template': GRANT_ALERT_INITIAL,
        'followup_template': GRANT_ALERT_FOLLOWUP,
    }
}
