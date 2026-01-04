#!/usr/bin/env python3
"""
Campaign Manager - Unified Email Campaign System for TheGrantScout

Consolidates send_initial_outreach.py, send_followup.py, and campaign_tracker.py
into a single unified script with shared code and consistent behavior.

Usage:
    python campaign_manager.py send                    # Send initial + followup emails
    python campaign_manager.py send --type initial     # Send only initial emails
    python campaign_manager.py send --type followup    # Send only follow-up emails
    python campaign_manager.py send --dry-run          # Preview without sending
    python campaign_manager.py check                   # Check for bounces/replies
    python campaign_manager.py check --days 7          # Check last N days
    python campaign_manager.py status                  # Show campaign status
    python campaign_manager.py sync                    # Force sync to CRM

Features:
    - Auto-save progress on Ctrl+C or natural close
    - Auto-check bounces on close
    - Auto-sync to CRM every 100 emails (or on close)
    - Business hours enforcement (Mon-Fri, 9am-7pm EST)
    - Duplicate prevention
    - Coordination between initial and followup
"""

import os
import sys
import time
import random
import smtplib
import csv
import signal
import argparse
import re
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parsedate_to_datetime
from typing import List, Dict, Tuple, Optional, Set
import pandas as pd
import pytz

# Import local modules
import config
import coordination

# Optional imports for Gmail API (bounce checking)
try:
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

# ============================================================================
# GLOBAL STATE
# ============================================================================

interrupted = False
emails_sent_this_session = 0
emails_since_last_sync = 0
CRM_SYNC_INTERVAL = 100

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global interrupted
    print("\n\n🛑 Interruption detected. Running shutdown hooks...")
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)

# ============================================================================
# TIME & BUSINESS HOURS HELPERS
# ============================================================================

def get_current_time_est() -> datetime:
    """Get current time in EST"""
    return datetime.now(pytz.timezone(config.TIMEZONE))

def is_business_hours() -> bool:
    """Check if current time is within business hours (Mon-Fri, 9am-7pm EST)"""
    now = get_current_time_est()
    if now.weekday() >= 5:  # Weekend
        return False
    if now.hour < config.BUSINESS_HOURS_START or now.hour >= config.BUSINESS_HOURS_END:
        return False
    return True

def calculate_next_send_window() -> Tuple[datetime, str]:
    """Calculate when the next valid send window opens"""
    now = get_current_time_est()

    if now.weekday() < 5 and now.hour < config.BUSINESS_HOURS_START:
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0)
        return next_window, format_time_remaining(next_window - now)

    if now.weekday() < 5 and now.hour >= config.BUSINESS_HOURS_END:
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0) + timedelta(days=1)
        if next_window.weekday() == 5:
            next_window += timedelta(days=2)
        return next_window, format_time_remaining(next_window - now)

    if now.weekday() == 5:
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0) + timedelta(days=2)
        return next_window, format_time_remaining(next_window - now)

    if now.weekday() == 6:
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return next_window, format_time_remaining(next_window - now)

    return now, "now"

def format_time_remaining(td: timedelta) -> str:
    """Format timedelta as human-readable string"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours} hours, {minutes} minutes"
    elif minutes > 0:
        return f"{minutes} minutes, {seconds} seconds"
    else:
        return f"{seconds} seconds"

def format_greeting(first_name: str, email_type: str = 'initial') -> str:
    """Format greeting with first name if available"""
    if first_name and str(first_name).strip() and str(first_name).lower() != 'nan':
        if email_type == 'followup':
            return f" {first_name.strip()},"
        return f" {first_name.strip()}"
    else:
        if email_type == 'followup':
            return ","
        return ""

# ============================================================================
# FILE & TRACKING HELPERS
# ============================================================================

def initialize_tracking_files():
    """Initialize CSV tracking files if they don't exist"""
    if not os.path.exists(config.SENT_TRACKER):
        with open(config.SENT_TRACKER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'email', 'vertical', 'message_type', 'subject_line', 'status', 'error_message', 'from_email'])

    if not os.path.exists(config.RESPONSE_TRACKER):
        with open(config.RESPONSE_TRACKER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'vertical', 'initial_sent_date', 'replied', 'followup_sent_date', 'notes'])

    if not os.path.exists(config.ERROR_LOG):
        with open(config.ERROR_LOG, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'email', 'vertical', 'error_type', 'error_message', 'action_taken'])

def load_sent_emails(message_type: str = None) -> Set[Tuple[str, str]]:
    """Load set of (email, vertical) tuples already sent"""
    sent_emails = set()
    if os.path.exists(config.SENT_TRACKER):
        try:
            df = pd.read_csv(config.SENT_TRACKER)
            if message_type:
                df = df[df['message_type'] == message_type]
            for _, row in df.iterrows():
                sent_emails.add((row['email'], row['vertical']))
        except Exception as e:
            print(f"⚠️  Warning: Could not load sent tracker: {e}")
    return sent_emails

def get_emails_sent_last_24h() -> int:
    """Count how many emails were sent in the last 24 hours"""
    if not os.path.exists(config.SENT_TRACKER):
        return 0
    try:
        df = pd.read_csv(config.SENT_TRACKER)
        if df.empty:
            return 0
        df = df[df['status'] == 'SUCCESS']
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        cutoff = get_current_time_est() - timedelta(hours=24)
        if cutoff.tzinfo is None:
            cutoff = pytz.timezone(config.TIMEZONE).localize(cutoff)
        recent = df[df['timestamp'] >= cutoff]
        return len(recent)
    except Exception as e:
        print(f"⚠️  Warning: Could not count recent emails: {e}")
        return 0

def get_emails_sent_today(message_type: str = 'initial') -> int:
    """Get count of emails sent today (calendar day)"""
    if not os.path.exists(config.SENT_TRACKER):
        return 0
    try:
        df = pd.read_csv(config.SENT_TRACKER)
        if df.empty:
            return 0
        df = df[(df['status'] == 'SUCCESS') & (df['message_type'] == message_type)]
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        today = get_current_time_est().date()
        est_tz = pytz.timezone(config.TIMEZONE)
        df['date'] = df['timestamp'].apply(lambda x: x.astimezone(est_tz).date())
        today_df = df[df['date'] == today]
        return len(today_df)
    except Exception as e:
        print(f"⚠️  Warning: Could not count emails sent today: {e}")
        return 0

def load_prospects(vertical: str) -> pd.DataFrame:
    """Load prospect data from CSV for given vertical"""
    csv_file = config.VERTICALS[vertical]['csv_file']
    if not os.path.exists(csv_file):
        print(f"❌ Error: Prospect file not found: {csv_file}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.lower().str.strip()
        if 'email' not in df.columns:
            print(f"❌ Error: No 'email' column found in {csv_file}")
            return pd.DataFrame()
        if 'first_name' not in df.columns:
            df['first_name'] = ''
        if 'company' not in df.columns:
            df['company'] = ''
        if 'state' not in df.columns:
            df['state'] = ''
        df['email'] = df['email'].str.strip().str.lower()
        df['email'] = df['email'].str.replace(r'^[\'"]+|[\'"]+$', '', regex=True).str.strip()
        df = df[df['email'].str.contains('@', na=False)]
        df = df[df['email'].str.contains(r'\.', na=False)]
        return df
    except Exception as e:
        print(f"❌ Error loading {csv_file}: {e}")
        return pd.DataFrame()

def load_followup_candidates() -> Dict[str, List[Dict]]:
    """Load candidates who need follow-up emails (initial sent 3+ days ago, not replied)"""
    if not os.path.exists(config.RESPONSE_TRACKER):
        return {}
    try:
        df = pd.read_csv(config.RESPONSE_TRACKER)
        df['replied'] = df['replied'].str.strip().str.upper()
        candidates = df[
            ((df['replied'] == 'NO') | (df['replied'] == 'PENDING')) &
            (df['followup_sent_date'].isna() | (df['followup_sent_date'] == ''))
        ]
        candidates = candidates.copy()
        candidates['initial_sent_date'] = pd.to_datetime(candidates['initial_sent_date'], format='mixed', errors='coerce')
        cutoff_date = get_current_time_est().replace(tzinfo=None) - timedelta(days=3)
        candidates = candidates[candidates['initial_sent_date'] <= cutoff_date]

        by_vertical = {}
        for vertical in config.VERTICALS.keys():
            vertical_candidates = candidates[candidates['vertical'] == vertical]
            if not vertical_candidates.empty:
                by_vertical[vertical] = vertical_candidates.to_dict('records')
        return by_vertical
    except Exception as e:
        print(f"❌ Error loading response tracker: {e}")
        return {}

# ============================================================================
# EMAIL SENDING
# ============================================================================

def send_email(to_email: str, subject: str, body: str) -> Tuple[bool, Optional[str]]:
    """Send email via Gmail SMTP"""
    if not config.APP_PASSWORD:
        return False, "APP_PASSWORD not configured"
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{config.YOUR_NAME} <{config.YOUR_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.YOUR_EMAIL, config.APP_PASSWORD)
            server.send_message(msg)
        return True, None
    except Exception as e:
        return False, str(e)

def log_sent_email(email: str, vertical: str, subject: str, message_type: str, status: str, error: Optional[str] = None):
    """Log sent email to CSV tracker"""
    with open(config.SENT_TRACKER, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        timestamp = get_current_time_est().isoformat()
        from_email = config.YOUR_EMAIL
        writer.writerow([timestamp, email, vertical, message_type, subject, status, error or '', from_email])
        f.flush()
        os.fsync(f.fileno())

    # Log to CRM (if successful)
    if status == 'SUCCESS':
        try:
            import crm_integration as crm
            crm.log_email_by_address(
                email_address=email,
                subject=subject,
                email_type=message_type,
                create_if_missing=False
            )
        except Exception as e:
            pass  # Non-fatal

def update_response_tracker(email: str, vertical: str, is_followup: bool = False):
    """Add or update entry in response tracker"""
    if is_followup:
        # Update existing row with followup date
        df = pd.read_csv(config.RESPONSE_TRACKER)
        mask = (df['email'] == email) & (df['vertical'] == vertical)
        df.loc[mask, 'followup_sent_date'] = get_current_time_est().strftime('%Y-%m-%d')
        df.to_csv(config.RESPONSE_TRACKER, index=False)
    else:
        # Add new row for initial send
        with open(config.RESPONSE_TRACKER, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            timestamp = get_current_time_est().strftime('%Y-%m-%d')
            writer.writerow([email, vertical, timestamp, 'PENDING', '', ''])
            f.flush()
            os.fsync(f.fileno())

def log_error(email: str, vertical: str, error_type: str, error_message: str, action: str):
    """Log error to error log"""
    with open(config.ERROR_LOG, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        timestamp = get_current_time_est().isoformat()
        writer.writerow([timestamp, email, vertical, error_type, error_message, action])
        f.flush()
        os.fsync(f.fileno())

def calculate_send_delay(emails_remaining: int, time_remaining_seconds: float) -> float:
    """Calculate delay to evenly space emails across remaining time period"""
    if emails_remaining <= 0:
        return 0
    even_delay = time_remaining_seconds / emails_remaining
    variation = even_delay * 0.1
    delay = random.uniform(even_delay - variation, even_delay + variation)
    return max(3.0, delay)

# ============================================================================
# CRM SYNC
# ============================================================================

def sync_to_crm():
    """Sync today's emails to CRM"""
    try:
        import crm_integration as crm
        print("\n📤 Syncing emails to CRM...")
        today = datetime.now().strftime('%Y-%m-%d')
        stats = crm.sync_sent_tracker_to_crm(since_date=today)
        if stats.get('error'):
            print(f"   ⚠️  CRM sync error: {stats['error']}")
        else:
            print(f"   ✅ Synced {stats.get('synced', 0)} emails to CRM")
    except ImportError:
        print("   ⚠️  CRM integration module not available")
    except Exception as e:
        print(f"   ⚠️  CRM sync error: {e}")

def maybe_sync_to_crm():
    """Sync to CRM if we've hit the interval"""
    global emails_since_last_sync
    emails_since_last_sync += 1
    if emails_since_last_sync >= CRM_SYNC_INTERVAL:
        sync_to_crm()
        emails_since_last_sync = 0

# ============================================================================
# GMAIL BOUNCE/REPLY CHECKING
# ============================================================================

GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
BOUNCE_PATTERNS = {
    'from_mailer_daemon': 'from:mailer-daemon',
    'from_postmaster': 'from:postmaster',
    'delivery_status': 'subject:"Delivery Status Notification"',
    'undeliverable': 'subject:Undeliverable',
    'delivery_failed': 'subject:"Mail Delivery Failed"',
}
BOUNCE_BODY_INDICATORS = [
    'delivery has failed', 'undeliverable', 'recipient address rejected',
    'user unknown', 'mailbox unavailable', 'address not found',
    '550 5.1.1', '550 5.7.1', 'permanent error',
]

def authenticate_gmail():
    """Authenticate with Gmail API"""
    if not GMAIL_AVAILABLE:
        print("❌ Gmail API packages not installed")
        return None

    token_file = os.path.join(os.path.dirname(__file__), 'credentials', 'token.json')
    creds_file = os.path.join(os.path.dirname(__file__), 'credentials', 'credentials.json')

    creds = None
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, GMAIL_SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            if not os.path.exists(creds_file):
                print(f"❌ {creds_file} not found. See TRACKER_SETUP.md")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    try:
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"❌ Gmail service error: {e}")
        return None

def search_gmail(service, query: str, max_results: int = 500) -> List[Dict]:
    """Search Gmail for emails matching query"""
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        if not messages:
            return []

        full_messages = []
        for idx, msg in enumerate(messages):
            if idx > 0 and idx % 10 == 0:
                time.sleep(0.1)
            try:
                full_msg = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                full_messages.append(full_msg)
            except Exception:
                continue
        return full_messages
    except Exception as e:
        print(f"Error searching emails: {e}")
        return []

def get_header(message: Dict, header_name: str) -> Optional[str]:
    """Extract header value from Gmail message"""
    headers = message.get('payload', {}).get('headers', [])
    for header in headers:
        if header['name'].lower() == header_name.lower():
            return header['value']
    return None

def get_email_body(message: Dict) -> str:
    """Extract plain text body from Gmail message"""
    payload = message.get('payload', {})
    if 'body' in payload and payload['body'].get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    parts = payload.get('parts', [])
    for part in parts:
        if part['mimeType'] == 'text/plain' and part['body'].get('data'):
            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
    return ""

def find_bounced_emails(service, days_back: int = 30) -> Dict[str, Dict]:
    """Search for bounce notifications"""
    print(f"\n📬 Searching for bounces (last {days_back} days)...")
    since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    bounced_emails = {}

    for pattern_name, pattern_query in BOUNCE_PATTERNS.items():
        query = f"{pattern_query} after:{since_date}"
        messages = search_gmail(service, query, max_results=200)

        for msg in messages:
            subject = get_header(msg, 'Subject') or ''
            body = get_email_body(msg)
            from_addr = get_header(msg, 'From') or ''
            date_str = get_header(msg, 'Date') or ''

            try:
                msg_date = parsedate_to_datetime(date_str)
            except Exception:
                msg_date = datetime.now()

            full_text = f"{subject}\n{from_addr}\n{body}"
            is_bounce = any(ind.lower() in full_text.lower() for ind in BOUNCE_BODY_INDICATORS)

            if is_bounce:
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
                emails = set(re.findall(email_pattern, full_text, re.IGNORECASE))
                for email_addr in emails:
                    if 'mailer-daemon' not in email_addr.lower() and 'postmaster' not in email_addr.lower():
                        if email_addr not in bounced_emails:
                            bounced_emails[email_addr] = {
                                'reason': pattern_name,
                                'date': msg_date.strftime('%Y-%m-%d'),
                                'snippet': subject[:100]
                            }

    print(f"   Found {len(bounced_emails)} potential bounced addresses")
    return bounced_emails

def find_replies(service, sent_emails: Set[str], days_back: int = 30) -> Dict[str, Dict]:
    """Find replies from recipients"""
    print(f"\n📬 Searching for replies (last {days_back} days)...")
    since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    query = f"in:inbox after:{since_date} -in:sent"
    messages = search_gmail(service, query, max_results=1000)

    replies = {}
    for msg in messages:
        from_addr = get_header(msg, 'From') or ''
        email_match = re.search(r'<(.+?)>', from_addr)
        from_email = email_match.group(1).lower().strip() if email_match else from_addr.lower().strip()

        if from_email in sent_emails and from_email not in replies:
            replies[from_email] = {
                'date': get_header(msg, 'Date') or '',
                'subject': get_header(msg, 'Subject') or '',
                'snippet': msg.get('snippet', '')[:200]
            }

    print(f"   Found {len(replies)} replies")
    return replies

def update_trackers_with_bounces_replies(bounced_emails: Dict, replies: Dict, sent_emails: Set[str]):
    """Update CSV trackers with bounce and reply info"""
    # Load trackers
    sent_rows = []
    if os.path.exists(config.SENT_TRACKER):
        with open(config.SENT_TRACKER, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sent_rows = list(reader)

    response_rows = []
    if os.path.exists(config.RESPONSE_TRACKER):
        with open(config.RESPONSE_TRACKER, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            response_rows = list(reader)

    # Filter bounces to our sent emails
    relevant_bounces = {e: info for e, info in bounced_emails.items() if e.lower() in sent_emails}

    # Update sent tracker with bounces
    bounce_updates = 0
    for row in sent_rows:
        email = row.get('email', '').lower().strip()
        if email in relevant_bounces and row.get('status') == 'SUCCESS':
            row['status'] = 'BOUNCED'
            row['error_message'] = f"Bounce: {relevant_bounces[email]['reason']}"
            bounce_updates += 1

    # Update response tracker with replies
    reply_updates = 0
    for row in response_rows:
        email = row.get('email', '').lower().strip()
        if email in replies and row.get('replied') == 'PENDING':
            row['replied'] = 'YES'
            row['notes'] = f"Replied: {replies[email]['subject'][:50]}"
            reply_updates += 1

    # Save updates
    if bounce_updates > 0 and sent_rows:
        fieldnames = list(sent_rows[0].keys())
        with open(config.SENT_TRACKER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sent_rows)
        print(f"   ✅ Updated {bounce_updates} bounces")

    if reply_updates > 0 and response_rows:
        fieldnames = list(response_rows[0].keys())
        with open(config.RESPONSE_TRACKER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(response_rows)
        print(f"   ✅ Updated {reply_updates} replies")

    if bounce_updates == 0 and reply_updates == 0:
        print("   ✅ No updates needed")

    return bounce_updates, reply_updates

# ============================================================================
# DISPLAY HELPERS
# ============================================================================

def display_status_box(title: str, next_window: datetime, time_str: str):
    """Display status box"""
    print(f"\n╔{'═' * 68}╗")
    print(f"║ {title:^66} ║")
    print(f"╠{'═' * 68}╣")
    print(f"║  Next send window: {next_window.strftime('%A %I:%M%p EST'):^46}  ║")
    print(f"║  Time remaining:   {time_str:^46}  ║")
    print(f"╚{'═' * 68}╝\n")

def display_campaign_stats():
    """Display comprehensive campaign statistics"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  CAMPAIGN STATUS                                           ║")
    print("╠════════════════════════════════════════════════════════════╣")

    # Load stats
    last_24h = get_emails_sent_last_24h()
    initial_today = get_emails_sent_today('initial')
    followup_today = get_emails_sent_today('followup')

    print(f"║  Emails sent last 24h:          {last_24h:<26} ║")
    print(f"║  Initial emails today:          {initial_today:<26} ║")
    print(f"║  Follow-up emails today:        {followup_today:<26} ║")
    print(f"║  Daily limit:                   {config.TOTAL_DAILY_LIMIT:<26} ║")
    print(f"║  Remaining capacity:            {max(0, config.TOTAL_DAILY_LIMIT - last_24h):<26} ║")
    print("║                                                            ║")

    # Business hours status
    if is_business_hours():
        print("║  Status: ✅ BUSINESS HOURS (ready to send)                ║")
    else:
        next_window, time_str = calculate_next_send_window()
        print(f"║  Status: ⏸️  Outside business hours                       ║")
        print(f"║  Next window: {next_window.strftime('%A %I:%M%p EST'):<44} ║")

    # Followup candidates
    followup_candidates = load_followup_candidates()
    total_followups = sum(len(c) for c in followup_candidates.values())
    print("║                                                            ║")
    print(f"║  Follow-up candidates ready:    {total_followups:<26} ║")

    print("╚════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# SHUTDOWN HOOKS
# ============================================================================

def run_shutdown_hooks(script_type: str = 'campaign', check_bounces: bool = True, sync_crm: bool = True):
    """Run all shutdown hooks for clean campaign close"""
    print("\n" + "="*60)
    print("RUNNING SHUTDOWN HOOKS")
    print("="*60)

    # Mark script stopped
    try:
        coordination.mark_script_stopped(script_type)
        print(f"\n✅ Marked {script_type} as stopped")
    except Exception:
        pass

    # Sync to CRM
    if sync_crm:
        sync_to_crm()

    # Check bounces
    if check_bounces and GMAIL_AVAILABLE:
        token_file = os.path.join(os.path.dirname(__file__), 'credentials', 'token.json')
        if os.path.exists(token_file):
            try:
                service = authenticate_gmail()
                if service:
                    sent_emails = {e.lower() for e, v in load_sent_emails()}
                    bounced = find_bounced_emails(service, days_back=7)
                    replies = find_replies(service, sent_emails, days_back=7)
                    update_trackers_with_bounces_replies(bounced, replies, sent_emails)
            except Exception as e:
                print(f"   ⚠️  Bounce check error: {e}")
        else:
            print("\n📬 Bounce check skipped (Gmail not authenticated)")

    print("\n" + "="*60)
    print("SHUTDOWN COMPLETE")
    print("="*60 + "\n")

# ============================================================================
# SEND COMMAND
# ============================================================================

def send_batch(email_type: str, prospects_by_vertical: Dict[str, pd.DataFrame],
               sent_emails: Set, daily_limit: int, followup_candidates: Dict = None) -> int:
    """Send a batch of emails (initial or followup)"""
    global interrupted, emails_sent_this_session

    # Determine which pool to use
    if email_type == 'followup':
        if not followup_candidates:
            print("❌ No follow-up candidates available")
            return 0
        active_verticals = [v for v in config.ACTIVE_VERTICALS if v in followup_candidates and followup_candidates[v]]
        if not active_verticals:
            print("❌ No follow-up candidates in active verticals")
            return 0

        # Build pools from followup candidates
        emails_per_vertical = daily_limit // len(active_verticals)
        pools = {}
        for vertical in active_verticals:
            pools[vertical] = followup_candidates[vertical][:emails_per_vertical]
    else:
        # Initial emails - filter out already sent
        active_verticals = [v for v in config.ACTIVE_VERTICALS if v in prospects_by_vertical and not prospects_by_vertical[v].empty]
        if not active_verticals:
            print("❌ No prospects available in active verticals")
            return 0

        emails_per_vertical = daily_limit // len(active_verticals)
        pools = {}
        for vertical in active_verticals:
            df = prospects_by_vertical[vertical]
            available = df[~df.apply(lambda row: (row['email'], vertical) in sent_emails, axis=1)]
            pools[vertical] = available.head(emails_per_vertical).to_dict('records')

    total_to_send = sum(len(p) for p in pools.values())
    if total_to_send == 0:
        print(f"ℹ️  No {email_type} emails to send (all already contacted)")
        return 0

    print(f"\n📧 Sending {total_to_send} {email_type} emails across {len(active_verticals)} vertical(s)")

    # Calculate time window
    now = get_current_time_est()
    end_time = now.replace(hour=config.BUSINESS_HOURS_END, minute=0, second=0, microsecond=0)

    # Send in round-robin fashion
    total_sent = 0
    vertical_index = 0
    consecutive_failures = 0

    while total_sent < total_to_send and not interrupted:
        if not is_business_hours():
            print(f"\n⏰ Outside business hours. Stopping at {total_sent} emails.")
            break

        # Get next vertical (round-robin)
        vertical = active_verticals[vertical_index % len(active_verticals)]
        vertical_index += 1

        if not pools[vertical]:
            continue

        # Get next prospect
        prospect = pools[vertical].pop(0)
        email = prospect['email']
        first_name = prospect.get('first_name', '')

        # Select random subject and format email
        if email_type == 'followup':
            subject = random.choice(config.VERTICALS[vertical]['followup_subject_lines'])
            greeting = format_greeting(first_name, 'followup')
            body = config.VERTICALS[vertical]['followup_template'].format(greeting=greeting)
        else:
            subject = random.choice(config.VERTICALS[vertical]['initial_subject_lines'])
            greeting = format_greeting(first_name, 'initial')
            body = config.VERTICALS[vertical]['initial_template'].format(greeting=greeting)

        # Send email
        success, error = send_email(email, subject, body)

        if success:
            log_sent_email(email, vertical, subject, email_type, 'SUCCESS')
            update_response_tracker(email, vertical, is_followup=(email_type == 'followup'))
            sent_emails.add((email, vertical))

            total_sent += 1
            emails_sent_this_session += 1
            consecutive_failures = 0

            # Update coordination
            total_sent_today = get_emails_sent_today(email_type)
            coordination.update_sent_count(email_type, total_sent_today)

            # Maybe sync to CRM
            maybe_sync_to_crm()

            # Display progress
            timestamp = get_current_time_est().strftime('%H:%M:%S')
            vertical_name = config.VERTICALS[vertical]['name']
            print(f"[{timestamp}] ✓ {email_type.capitalize()} sent to {email} ({vertical_name}) ({total_sent}/{total_to_send})")

            # Calculate delay
            emails_remaining = total_to_send - total_sent
            time_remaining = (end_time - get_current_time_est()).total_seconds()
            delay = calculate_send_delay(emails_remaining, time_remaining)

            if emails_remaining > 0 and delay > 0:
                time.sleep(delay)
        else:
            log_sent_email(email, vertical, subject, email_type, 'FAILED', error)
            log_error(email, vertical, 'SEND_FAILURE', error, 'Skipped')
            consecutive_failures += 1
            print(f"[{get_current_time_est().strftime('%H:%M:%S')}] ❌ Failed: {email}: {error}")

            if consecutive_failures >= 5:
                print("\n🚨 5 consecutive failures. Pausing 30 minutes...")
                time.sleep(1800)
                consecutive_failures = 0

    return total_sent

def cmd_send(args):
    """Handle send command"""
    global interrupted, emails_sent_this_session

    print("="*70)
    print("CAMPAIGN MANAGER - SEND")
    print("="*70)
    print(f"Started: {get_current_time_est().strftime('%Y-%m-%d %H:%M:%S %Z')}")

    if args.dry_run:
        print("\n🧪 DRY RUN MODE: Preview only\n")

    email_types = []
    if args.type == 'initial':
        email_types = ['initial']
    elif args.type == 'followup':
        email_types = ['followup']
    else:
        email_types = ['initial', 'followup']

    print(f"Email types: {', '.join(email_types)}")
    print(f"Active verticals: {', '.join(config.ACTIVE_VERTICALS)}\n")

    initialize_tracking_files()

    # Load prospects
    print("📋 Loading prospects...")
    prospects_by_vertical = {}
    for vertical in config.ACTIVE_VERTICALS:
        df = load_prospects(vertical)
        if not df.empty:
            prospects_by_vertical[vertical] = df
            print(f"   ✓ {config.VERTICALS[vertical]['name']}: {len(df)} prospects")

    if not prospects_by_vertical:
        print("\n❌ No prospect data found. Exiting.")
        return

    # Load sent emails
    sent_emails_initial = load_sent_emails('initial')
    sent_emails_followup = load_sent_emails('followup')

    # Display stats
    display_campaign_stats()

    if args.dry_run:
        print("🧪 Dry run complete. Exiting.")
        return

    # Get user approval
    print("Type 'yes' to proceed, or 'no' to cancel:")
    user_input = input("> ").strip().lower()
    if user_input not in ['yes', 'y', 'approve']:
        print("❌ Cancelled by user")
        return

    print("✅ Approved! Starting campaign...\n")

    # Main loop
    while not interrupted:
        if not is_business_hours():
            next_window, time_str = calculate_next_send_window()
            display_status_box("OUTSIDE BUSINESS HOURS", next_window, time_str)
            for i in range(15):
                if interrupted:
                    break
                time.sleep(60)
            continue

        # Check capacity
        capacity = coordination.get_rolling_capacity_analysis(
            current_time=get_current_time_est(),
            business_hours_end=get_current_time_est().replace(hour=config.BUSINESS_HOURS_END, minute=0),
            daily_limit=config.TOTAL_DAILY_LIMIT
        )

        if capacity['current_capacity'] <= 0:
            print(f"\n📊 Daily limit reached ({capacity['emails_in_last_24h']}/{config.TOTAL_DAILY_LIMIT})")
            next_window, time_str = calculate_next_send_window()
            display_status_box("DAILY LIMIT REACHED", next_window, time_str)
            for i in range(15):
                if interrupted:
                    break
                time.sleep(60)
            continue

        available_capacity = capacity['current_capacity']

        # Send initial emails
        if 'initial' in email_types:
            sent_emails_initial = load_sent_emails('initial')
            initial_capacity = available_capacity // 2 if 'followup' in email_types else available_capacity
            initial_sent = send_batch('initial', prospects_by_vertical, sent_emails_initial, initial_capacity)
            available_capacity -= initial_sent

        # Send followup emails
        if 'followup' in email_types and available_capacity > 0:
            followup_candidates = load_followup_candidates()
            sent_emails_followup = load_sent_emails('followup')
            followup_sent = send_batch('followup', prospects_by_vertical, sent_emails_followup,
                                       available_capacity, followup_candidates)

        # Wait and check again
        print("\n⏸️  Batch complete. Checking again in 15 minutes...")
        for i in range(15):
            if interrupted:
                break
            time.sleep(60)

    # Shutdown
    run_shutdown_hooks('campaign' if len(email_types) > 1 else email_types[0])
    print(f"\n✅ Sent {emails_sent_this_session} emails this session.")

# ============================================================================
# CHECK COMMAND
# ============================================================================

def cmd_check(args):
    """Handle check command (bounces/replies)"""
    print("="*70)
    print("CAMPAIGN MANAGER - CHECK BOUNCES/REPLIES")
    print("="*70)

    if not GMAIL_AVAILABLE:
        print("\n❌ Gmail API packages not installed.")
        print("Run: pip install google-auth-oauthlib google-api-python-client")
        return

    service = authenticate_gmail()
    if not service:
        print("❌ Gmail authentication failed")
        return

    print(f"\n✅ Gmail authenticated")
    print(f"Checking last {args.days} days...\n")

    # Load sent emails
    sent_emails = {e.lower() for e, v in load_sent_emails()}
    print(f"Loaded {len(sent_emails)} sent email addresses")

    # Find bounces and replies
    bounced = find_bounced_emails(service, days_back=args.days)
    replies = find_replies(service, sent_emails, days_back=args.days)

    # Update trackers
    bounce_updates, reply_updates = update_trackers_with_bounces_replies(bounced, replies, sent_emails)

    print(f"\n✅ Check complete!")
    print(f"   Bounces updated: {bounce_updates}")
    print(f"   Replies updated: {reply_updates}")

# ============================================================================
# STATUS COMMAND
# ============================================================================

def cmd_status(args):
    """Handle status command"""
    print("="*70)
    print("CAMPAIGN MANAGER - STATUS")
    print("="*70)
    display_campaign_stats()
    coordination.display_allocation_summary()

# ============================================================================
# SYNC COMMAND
# ============================================================================

def cmd_sync(args):
    """Handle sync command"""
    print("="*70)
    print("CAMPAIGN MANAGER - SYNC TO CRM")
    print("="*70)
    sync_to_crm()
    print("\n✅ Sync complete!")

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Unified Email Campaign Manager for TheGrantScout',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Commands:
  send      Send emails (initial and/or followup)
  check     Check Gmail for bounces and replies
  status    Show campaign status
  sync      Force sync to CRM

Examples:
  python campaign_manager.py send                    # Send both initial + followup
  python campaign_manager.py send --type initial     # Send only initial
  python campaign_manager.py send --type followup    # Send only followup
  python campaign_manager.py send --dry-run          # Preview without sending
  python campaign_manager.py check --days 7          # Check last 7 days
  python campaign_manager.py status                  # Show stats
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Send command
    send_parser = subparsers.add_parser('send', help='Send emails')
    send_parser.add_argument('--type', choices=['initial', 'followup', 'both'], default='both',
                            help='Type of emails to send')
    send_parser.add_argument('--dry-run', action='store_true', help='Preview without sending')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check for bounces/replies')
    check_parser.add_argument('--days', type=int, default=30, help='Days to search back')

    # Status command
    subparsers.add_parser('status', help='Show campaign status')

    # Sync command
    subparsers.add_parser('sync', help='Force sync to CRM')

    args = parser.parse_args()

    if args.command == 'send':
        cmd_send(args)
    elif args.command == 'check':
        cmd_check(args)
    elif args.command == 'status':
        cmd_status(args)
    elif args.command == 'sync':
        cmd_sync(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
