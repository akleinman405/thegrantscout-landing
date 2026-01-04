#!/usr/bin/env python3
"""
Email Validation Campaign System - Initial Outreach
Sends initial validation emails to prospects across verticals with smart pacing and anti-spam measures.
"""

import os
import sys
import time
import random
import smtplib
import csv
import signal
import argparse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Tuple, Optional
import pandas as pd
import pytz

# Import configuration
import config
import coordination
import shutdown_hooks

# ============================================================================
# GLOBAL STATE
# ============================================================================

interrupted = False
emails_sent_this_session = 0

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully with auto-sync and bounce check"""
    global interrupted
    print("\n\n🛑 Interruption detected. Running shutdown hooks...")
    interrupted = True
    # Shutdown hooks will be run in the main loop when it exits

signal.signal(signal.SIGINT, signal_handler)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_time_est() -> datetime:
    """Get current time in EST"""
    return datetime.now(pytz.timezone(config.TIMEZONE))

def is_business_hours() -> bool:
    """Check if current time is within business hours (9am-3pm EST, Mon-Fri)"""
    now = get_current_time_est()

    # Check if weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Check if within 9am-3pm EST
    if now.hour < config.BUSINESS_HOURS_START or now.hour >= config.BUSINESS_HOURS_END:
        return False

    return True

def calculate_next_send_window() -> Tuple[datetime, str]:
    """Calculate when the next valid send window opens"""
    now = get_current_time_est()

    # If it's a weekday but before 9am
    if now.weekday() < 5 and now.hour < config.BUSINESS_HOURS_START:
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0)
        return next_window, format_time_remaining(next_window - now)

    # If it's a weekday but after 3pm
    if now.weekday() < 5 and now.hour >= config.BUSINESS_HOURS_END:
        # Next day at 9am
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0) + timedelta(days=1)
        # If tomorrow is Saturday, skip to Monday
        if next_window.weekday() == 5:
            next_window += timedelta(days=2)
        return next_window, format_time_remaining(next_window - now)

    # If it's Saturday
    if now.weekday() == 5:
        # Monday at 9am
        days_until_monday = 2
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        return next_window, format_time_remaining(next_window - now)

    # If it's Sunday
    if now.weekday() == 6:
        # Monday at 9am
        days_until_monday = 1
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        return next_window, format_time_remaining(next_window - now)

    # Should not reach here
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

def format_greeting(first_name: str) -> str:
    """Format greeting with first name if available"""
    if first_name and str(first_name).strip() and str(first_name).lower() != 'nan':
        return f" {first_name.strip()}"
    else:
        return ""

def initialize_tracking_files():
    """Initialize CSV tracking files if they don't exist"""
    # Initialize sent_tracker.csv
    if not os.path.exists(config.SENT_TRACKER):
        with open(config.SENT_TRACKER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'email', 'vertical', 'message_type', 'subject_line', 'status', 'error_message', 'from_email'])

    # Initialize response_tracker.csv
    if not os.path.exists(config.RESPONSE_TRACKER):
        with open(config.RESPONSE_TRACKER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'vertical', 'initial_sent_date', 'replied', 'followup_sent_date', 'notes'])

    # Initialize error_log.csv
    if not os.path.exists(config.ERROR_LOG):
        with open(config.ERROR_LOG, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'email', 'vertical', 'error_type', 'error_message', 'action_taken'])

def load_sent_emails() -> set:
    """Load list of emails already sent from tracker"""
    sent_emails = set()
    if os.path.exists(config.SENT_TRACKER):
        try:
            df = pd.read_csv(config.SENT_TRACKER)
            # Get emails sent for initial outreach only
            initial_df = df[df['message_type'] == 'initial']
            for _, row in initial_df.iterrows():
                sent_emails.add((row['email'], row['vertical']))
        except Exception as e:
            print(f"⚠️  Warning: Could not load sent tracker: {e}")
    return sent_emails

def detect_duplicates_in_tracker() -> Dict[str, list]:
    """
    Detect if there are any duplicate emails in the sent_tracker.csv
    Returns dict with duplicate emails and their send times
    """
    duplicates = {}
    if not os.path.exists(config.SENT_TRACKER):
        return duplicates

    try:
        df = pd.read_csv(config.SENT_TRACKER)
        if df.empty:
            return duplicates

        # Group by (email, vertical) and count
        grouped = df.groupby(['email', 'vertical']).size()
        dups = grouped[grouped > 1]

        if len(dups) > 0:
            for (email, vertical), count in dups.items():
                # Get all timestamps for this duplicate
                dup_rows = df[(df['email'] == email) & (df['vertical'] == vertical)]
                timestamps = dup_rows['timestamp'].tolist()
                duplicates[f"{email} ({vertical})"] = {
                    'count': count,
                    'timestamps': timestamps
                }
    except Exception as e:
        print(f"⚠️  Warning: Could not check for duplicates: {e}")

    return duplicates

def verify_no_duplicates_in_batch(prospects: list, vertical: str, sent_emails: set) -> Tuple[bool, list]:
    """
    Verify that none of the prospects in the batch are already in sent_emails
    Returns (is_clean, duplicates_found)
    """
    duplicates_found = []
    for prospect in prospects:
        email = prospect['email']
        if (email, vertical) in sent_emails:
            duplicates_found.append(email)

    return len(duplicates_found) == 0, duplicates_found

def get_emails_sent_last_24h() -> int:
    """Count how many emails were sent in the last 24 hours"""
    if not os.path.exists(config.SENT_TRACKER):
        return 0

    try:
        df = pd.read_csv(config.SENT_TRACKER)
        if df.empty:
            return 0

        # Filter to successful sends only
        df = df[df['status'] == 'SUCCESS']

        # Parse timestamps with UTC timezone
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

        # Get cutoff time (24 hours ago) - ensure timezone aware
        cutoff = get_current_time_est() - timedelta(hours=24)
        # Convert to UTC for comparison if needed
        if cutoff.tzinfo is None:
            cutoff = pytz.timezone(config.TIMEZONE).localize(cutoff)

        # Count emails sent after cutoff
        recent = df[df['timestamp'] >= cutoff]
        return len(recent)
    except Exception as e:
        print(f"⚠️  Warning: Could not count recent emails: {e}")
        print(f"   Error details: {e}")
        import traceback
        traceback.print_exc()
        return 0


def get_emails_sent_today(message_type='initial') -> int:
    """
    Get count of emails sent today (calendar day) for coordination tracking.

    This counts emails sent on the current calendar date (not rolling 24h window).
    Used for coordination.json daily allocation tracking.

    Args:
        message_type: 'initial' or 'followup'

    Returns:
        Number of emails sent today matching the message type
    """
    if not os.path.exists(config.SENT_TRACKER):
        return 0

    try:
        df = pd.read_csv(config.SENT_TRACKER)
        if df.empty:
            return 0

        # Filter to successful sends of specified type
        df = df[(df['status'] == 'SUCCESS') & (df['message_type'] == message_type)]

        # Parse timestamps with UTC timezone
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

        # Get today's date in EST
        today = get_current_time_est().date()

        # Convert timestamps to EST and extract date
        est_tz = pytz.timezone(config.TIMEZONE)
        df['date'] = df['timestamp'].apply(lambda x: x.astimezone(est_tz).date())

        # Filter to today only
        today_df = df[df['date'] == today]
        return len(today_df)
    except Exception as e:
        print(f"⚠️  Warning: Could not count emails sent today: {e}")
        return 0


def get_emails_sent_this_week_by_sender() -> Dict[str, int]:
    """Get count of emails sent this week, broken down by sending email address"""
    if not os.path.exists(config.SENT_TRACKER):
        return {}

    try:
        df = pd.read_csv(config.SENT_TRACKER)
        if df.empty:
            return {}

        # Filter to successful sends only
        df = df[df['status'] == 'SUCCESS']

        # Parse timestamps with UTC timezone
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

        # Get start of week (Monday 00:00)
        now = get_current_time_est()
        start_of_week = now - timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        if start_of_week.tzinfo is None:
            start_of_week = pytz.timezone(config.TIMEZONE).localize(start_of_week)

        # Filter to this week
        week_df = df[df['timestamp'] >= start_of_week]

        # Group by from_email if column exists
        if 'from_email' in week_df.columns:
            # Handle NaN values by replacing with config.YOUR_EMAIL
            week_df['from_email'] = week_df['from_email'].fillna(config.YOUR_EMAIL)
            by_sender = week_df.groupby('from_email').size().to_dict()
            return by_sender
        else:
            # Fallback: assume all emails from config.YOUR_EMAIL
            total_this_week = len(week_df)
            if total_this_week > 0:
                return {config.YOUR_EMAIL: total_this_week}
            return {}
    except Exception as e:
        print(f"⚠️  Warning: Could not count weekly emails: {e}")
        return {}

def get_vertical_statistics(prospects_by_vertical: Dict[str, pd.DataFrame], sent_emails: set) -> Dict[str, Dict[str, int]]:
    """Get statistics broken down by vertical"""
    stats = {}

    # Load sent tracker for all-time counts by vertical
    sent_by_vertical = {}
    if os.path.exists(config.SENT_TRACKER):
        try:
            df = pd.read_csv(config.SENT_TRACKER)
            if not df.empty:
                # Filter to successful initial sends only
                initial_df = df[(df['status'] == 'SUCCESS') & (df['message_type'] == 'initial')]
                sent_by_vertical = initial_df.groupby('vertical').size().to_dict()
        except Exception as e:
            pass

    for vertical in config.VERTICALS.keys():
        if vertical in prospects_by_vertical:
            df = prospects_by_vertical[vertical]
            total = len(df)
            sent = sent_by_vertical.get(vertical, 0)
            unsent = len(df[~df.apply(lambda row: (row['email'], vertical) in sent_emails, axis=1)])

            stats[vertical] = {
                'total': total,
                'sent': sent,
                'remaining': unsent
            }
        else:
            stats[vertical] = {
                'total': 0,
                'sent': sent_by_vertical.get(vertical, 0),
                'remaining': 0
            }

    return stats

def display_email_statistics(prospects_by_vertical: Dict[str, pd.DataFrame], sent_emails: set):
    """Display comprehensive email sending statistics"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  EMAIL SENDING STATISTICS                                  ║")
    print("╠════════════════════════════════════════════════════════════╣")

    # Get vertical statistics
    vertical_stats = get_vertical_statistics(prospects_by_vertical, sent_emails)

    print("║  BY VERTICAL:                                              ║")
    print("║                                                            ║")

    for vertical in config.VERTICALS.keys():
        if vertical_stats[vertical]['total'] > 0 or vertical_stats[vertical]['sent'] > 0:
            name = config.VERTICALS[vertical]['name'][:18]  # Truncate if needed
            stats = vertical_stats[vertical]
            print(f"║  {name:<18} Total: {stats['total']:>5}  Sent: {stats['sent']:>5}  Remaining: {stats['remaining']:>5} ║")

    # Totals across all verticals
    total_prospects = sum(s['total'] for s in vertical_stats.values())
    total_sent = sum(s['sent'] for s in vertical_stats.values())
    total_remaining = sum(s['remaining'] for s in vertical_stats.values())

    print("║                                                            ║")
    print(f"║  {'ALL VERTICALS':<18} Total: {total_prospects:>5}  Sent: {total_sent:>5}  Remaining: {total_remaining:>5} ║")

    print("║                                                            ║")
    print("╠════════════════════════════════════════════════════════════╣")

    # Last 24 hours (TODAY'S activity)
    last_24h = get_emails_sent_last_24h()
    print(f"║  SENT IN LAST 24 HOURS (ROLLING):    {last_24h:<24} ║")

    # This week by sender
    weekly_by_sender = get_emails_sent_this_week_by_sender()
    print("║                                                            ║")
    print("║  Sent this week (by sender):                               ║")

    if weekly_by_sender:
        for sender, count in weekly_by_sender.items():
            sender_display = sender[:40]  # Truncate if too long
            print(f"║    {sender_display:<45} {count:>5} ║")
        total_week = sum(weekly_by_sender.values())
        print(f"║    {'TOTAL THIS WEEK':<45} {total_week:>5} ║")
    else:
        print("║    No emails sent this week                                ║")

    print("╚════════════════════════════════════════════════════════════╝\n")

    return total_sent, last_24h

def get_user_approval(prospects_by_vertical: Dict[str, pd.DataFrame], sent_emails: set, dry_run: bool = False) -> bool:
    """
    Display comprehensive preview and get user approval before sending
    Returns True if user approves, False otherwise
    """
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║  SEND PREVIEW & APPROVAL                                         ║")
    print("╠══════════════════════════════════════════════════════════════════╣")

    # Check for existing duplicates in tracker
    existing_duplicates = detect_duplicates_in_tracker()
    if existing_duplicates:
        print("║                                                                  ║")
        print("║  ⚠️  WARNING: DUPLICATES DETECTED IN SENT TRACKER!               ║")
        print("║                                                                  ║")
        for dup_email, dup_info in existing_duplicates.items():
            print(f"║  {dup_email[:60]:<60}  ║")
            print(f"║    Sent {dup_info['count']} times                                            ║")
        print("║                                                                  ║")

    # Calculate what will be sent
    total_to_send = 0
    preview_by_vertical = {}

    for vertical in config.ACTIVE_VERTICALS:
        if vertical in prospects_by_vertical:
            df = prospects_by_vertical[vertical]
            available = df[~df.apply(lambda row: (row['email'], vertical) in sent_emails, axis=1)]
            count = len(available)
            if count > 0:
                total_to_send += count
                preview_by_vertical[vertical] = {
                    'count': count,
                    'sample_emails': available['email'].head(10).tolist()
                }

    print("║  EMAILS TO BE SENT TODAY:                                        ║")
    print("║                                                                  ║")

    if total_to_send == 0:
        print("║  No emails to send (all prospects already contacted)            ║")
        print("╚══════════════════════════════════════════════════════════════════╝\n")
        return True  # No emails to send, proceed

    for vertical, info in preview_by_vertical.items():
        vertical_name = config.VERTICALS[vertical]['name']
        print(f"║  {vertical_name[:30]:<30} {info['count']:>4} emails               ║")

    print("║                                                                  ║")
    print(f"║  TOTAL TO SEND: {total_to_send:<49} ║")
    print("║                                                                  ║")

    # Show sample email addresses
    print("║  SAMPLE RECIPIENTS (first 10):                                   ║")
    sample_count = 0
    for vertical, info in preview_by_vertical.items():
        for email in info['sample_emails'][:10 - sample_count]:
            print(f"║    {email[:62]:<62}║")
            sample_count += 1
            if sample_count >= 10:
                break
        if sample_count >= 10:
            break

    print("║                                                                  ║")

    # Duplicate safety check
    all_clean = True
    for vertical, info in preview_by_vertical.items():
        df = prospects_by_vertical[vertical]
        available = df[~df.apply(lambda row: (row['email'], vertical) in sent_emails, axis=1)]
        prospects_list = available.to_dict('records')
        is_clean, duplicates_found = verify_no_duplicates_in_batch(prospects_list, vertical, sent_emails)
        if not is_clean:
            all_clean = False
            print("║  ❌ DUPLICATES DETECTED IN BATCH!                               ║")
            for dup in duplicates_found[:5]:  # Show first 5
                print(f"║    {dup[:62]:<62}║")

    if all_clean:
        print("║  ✅ DUPLICATE CHECK: PASSED (no duplicates detected)            ║")
    else:
        print("║                                                                  ║")
        print("║  ⚠️  DUPLICATE CHECK: FAILED                                     ║")
        print("║  Some recipients have already been contacted!                    ║")

    print("╚══════════════════════════════════════════════════════════════════╝\n")

    if dry_run:
        print("🧪 DRY RUN MODE: No emails will be sent\n")
        return False

    if not all_clean:
        print("❌ Cannot proceed: Duplicates detected in batch")
        print("   Please investigate and fix before running again.\n")
        return False

    # Get user input
    print("Type 'yes' or 'approve' to proceed, or 'no' to cancel:")
    user_input = input("> ").strip().lower()

    if user_input in ['yes', 'approve', 'y']:
        print("✅ Approved! Starting email campaign...\n")
        return True
    else:
        print("❌ Cancelled by user\n")
        return False

def load_prospects(vertical: str) -> pd.DataFrame:
    """Load prospect data from CSV for given vertical"""
    csv_file = config.VERTICALS[vertical]['csv_file']

    if not os.path.exists(csv_file):
        print(f"❌ Error: Prospect file not found: {csv_file}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(csv_file)

        # Standardize column names (case-insensitive)
        df.columns = df.columns.str.lower().str.strip()

        # Ensure 'email' column exists
        if 'email' not in df.columns:
            print(f"❌ Error: No 'email' column found in {csv_file}")
            return pd.DataFrame()

        # Add missing optional columns
        if 'first_name' not in df.columns:
            df['first_name'] = ''
        if 'company' not in df.columns:
            df['company'] = ''
        if 'state' not in df.columns:
            df['state'] = ''

        # Clean email addresses
        df['email'] = df['email'].str.strip().str.lower()
        df['email'] = df['email'].str.replace(r'^[\'"]+|[\'"]+$', '', regex=True).str.strip()
        # Remove invalid emails
        df = df[df['email'].str.contains('@', na=False)]
        df = df[df['email'].str.contains('\.', na=False)]

        return df
    except Exception as e:
        print(f"❌ Error loading {csv_file}: {e}")
        return pd.DataFrame()

def send_email(to_email: str, subject: str, body: str) -> Tuple[bool, Optional[str]]:
    """Send email via Gmail SMTP"""
    if not config.APP_PASSWORD:
        return False, "APP_PASSWORD not configured"

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{config.YOUR_NAME} <{config.YOUR_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach body
        msg.attach(MIMEText(body, 'plain'))

        # Connect and send
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.YOUR_EMAIL, config.APP_PASSWORD)
            server.send_message(msg)

        return True, None
    except Exception as e:
        return False, str(e)

def log_sent_email(email: str, vertical: str, subject: str, status: str, error: Optional[str] = None):
    """Log sent email to tracker (CSV + CRM)"""
    # Log to CSV tracker
    with open(config.SENT_TRACKER, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        timestamp = get_current_time_est().isoformat()
        from_email = config.YOUR_EMAIL
        writer.writerow([timestamp, email, vertical, 'initial', subject, status, error or '', from_email])
        # CRITICAL: Force immediate write to disk (fixes WSL/Windows file caching issue)
        f.flush()
        os.fsync(f.fileno())

    # Log to CRM (if successful)
    if status == 'SUCCESS':
        try:
            import crm_integration as crm
            crm.log_email_by_address(
                email_address=email,
                subject=subject,
                email_type='initial',
                create_if_missing=False  # Don't create new prospects, just log if exists
            )
        except Exception as e:
            # Don't fail email send if CRM logging fails
            print(f"⚠️  CRM logging failed (non-fatal): {e}")

def update_response_tracker(email: str, vertical: str):
    """Add entry to response tracker"""
    with open(config.RESPONSE_TRACKER, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        timestamp = get_current_time_est().strftime('%Y-%m-%d')
        writer.writerow([email, vertical, timestamp, 'PENDING', '', ''])
        # Force immediate write to disk
        f.flush()
        os.fsync(f.fileno())

def log_error(email: str, vertical: str, error_type: str, error_message: str, action: str):
    """Log error to error log"""
    with open(config.ERROR_LOG, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        timestamp = get_current_time_est().isoformat()
        writer.writerow([timestamp, email, vertical, error_type, error_message, action])
        # Force immediate write to disk
        f.flush()
        os.fsync(f.fileno())

def calculate_send_delay(emails_remaining: int, time_remaining_seconds: float, emails_sent: int) -> float:
    """
    Calculate delay to evenly space emails across remaining time period.

    If we have 6 hours (21600 seconds) and 360 emails to send:
    - Average delay = 21600 / 360 = 60 seconds between emails
    - This spreads emails evenly from 9am to 3pm
    """
    if emails_remaining <= 0:
        return 0

    # Calculate even spacing
    even_delay = time_remaining_seconds / emails_remaining

    # Add small random variation (±10%) to look more natural
    variation = even_delay * 0.1
    delay = random.uniform(even_delay - variation, even_delay + variation)

    # Ensure minimum 3 seconds between emails (prevent too fast)
    delay = max(3.0, delay)

    return delay

def display_status_box(title: str, next_window: datetime, time_str: str):
    """Display status box"""
    print(f"\n╔{'═' * 68}╗")
    print(f"║ {title:^66} ║")
    print(f"╠{'═' * 68}╣")
    print(f"║  Next send window: {next_window.strftime('%A %I:%M%p EST'):^46}  ║")
    print(f"║  Time remaining:   {time_str:^46}  ║")
    print(f"╚{'═' * 68}╝\n")

def send_batch(prospects_by_vertical: Dict[str, pd.DataFrame], sent_emails: set, daily_limit_remaining: int) -> int:
    """Send a batch of emails across verticals"""
    global interrupted, emails_sent_this_session

    # Test mode: send test emails to all addresses in TEST_EMAIL_ADDRESSES
    if config.TEST_MODE:
        test_emails = config.TEST_EMAIL_ADDRESSES
        print(f"\n🧪 TEST MODE: Sending test emails from {config.TEST_VERTICAL} vertical")
        print(f"   Test emails will be sent to: {', '.join(test_emails)}\n")
        
        vertical = config.TEST_VERTICAL
        if vertical not in prospects_by_vertical or prospects_by_vertical[vertical].empty:
            print(f"❌ No prospects found for {vertical} vertical")
            return 0
        
        # Get first prospect (just for template data)
        prospect = prospects_by_vertical[vertical].iloc[0]
        
        # Select random subject line
        subject = random.choice(config.VERTICALS[vertical]['initial_subject_lines'])
        
        # Get email body and format greeting
        greeting = format_greeting(prospect.get('first_name', ''))
        body = config.VERTICALS[vertical]['initial_template'].format(greeting=greeting)
        
        # Send to all test addresses
        sent_count = 0
        for test_email in test_emails:
            success, error = send_email(test_email, subject, body)
            
            if success:
                print(f"[{get_current_time_est().strftime('%H:%M:%S')}] ✓ Test email sent to {test_email}")
                sent_count += 1
                if test_email != test_emails[-1]:  # Not the last one
                    time.sleep(2)  # Small delay between test emails
            else:
                print(f"❌ Failed to send test email to {test_email}: {error}")
        
        if sent_count > 0:
            print(f"\n   Vertical: {config.VERTICALS[vertical]['name']}")
            print(f"   Subject: {subject}")
            print(f"   First name used: {prospect.get('first_name', '(none)')}")
            print(f"   Total sent: {sent_count}/{len(test_emails)}")
        
        return sent_count

    # Production mode: send from ACTIVE_VERTICALS only
    active_verticals = [v for v in config.ACTIVE_VERTICALS if v in prospects_by_vertical and not prospects_by_vertical[v].empty]

    if not active_verticals:
        print("❌ No active verticals with prospects available")
        return 0

    print(f"📊 Active verticals: {', '.join([config.VERTICALS[v]['name'] for v in active_verticals])}")

    # Calculate emails per vertical (evenly split)
    emails_per_vertical = daily_limit_remaining // len(active_verticals)
    total_to_send = emails_per_vertical * len(active_verticals)
    
    print(f"📊 Sending {emails_per_vertical} emails per vertical ({total_to_send} total)")
    
    # Create pools for each active vertical
    pools = {}
    for vertical in active_verticals:
        df = prospects_by_vertical[vertical]
        # Filter out already-sent
        available = df[~df.apply(lambda row: (row['email'], vertical) in sent_emails, axis=1)]
        # Convert to list of dicts
        prospects_list = available.head(emails_per_vertical).to_dict('records')
        pools[vertical] = prospects_list
        print(f"   ✓ {config.VERTICALS[vertical]['name']}: {len(prospects_list)} ready to send")
    
    # Calculate time window
    now = get_current_time_est()
    end_time = now.replace(hour=config.BUSINESS_HOURS_END, minute=0, second=0, microsecond=0)
    
    print(f"\n⏰ Sending window: {now.strftime('%H:%M')} - {end_time.strftime('%H:%M')} EST")
    print(f"🚀 Starting send...\n")
    
    # Send in round-robin fashion
    total_sent = 0
    vertical_index = 0
    consecutive_failures = 0
    emails_since_save = 0
    
    while total_sent < total_to_send and not interrupted:
        # Check if we're still in business hours
        if not is_business_hours():
            print(f"\n⏰ Outside business hours. Stopping at {total_sent} emails.")
            break
        
        # Get next vertical (round-robin)
        vertical = active_verticals[vertical_index % len(active_verticals)]
        vertical_index += 1
        
        # Skip if this vertical is exhausted
        if not pools[vertical]:
            continue
        
        # Get next prospect
        prospect = pools[vertical].pop(0)
        email = prospect['email']
        
        # Select random subject line
        subject = random.choice(config.VERTICALS[vertical]['initial_subject_lines'])
        
        # Get email body and format greeting
        greeting = format_greeting(prospect.get('first_name', ''))
        body = config.VERTICALS[vertical]['initial_template'].format(greeting=greeting)
        
        # Send email
        success, error = send_email(email, subject, body)
        
        if success:
            # Log success
            log_sent_email(email, vertical, subject, 'SUCCESS')
            update_response_tracker(email, vertical)
            sent_emails.add((email, vertical))

            total_sent += 1
            emails_sent_this_session += 1
            emails_since_save += 1
            consecutive_failures = 0

            # Update coordination.json with current sent count (real-time tracking)
            coordination.update_sent_count('initial', coordination.load_coordination()['initial']['sent'] + 1)

            # Trigger CRM sync every 100 emails
            shutdown_hooks.increment_email_counter()

            # Display progress
            timestamp = get_current_time_est().strftime('%H:%M:%S')
            vertical_name = config.VERTICALS[vertical]['name']
            first_name_display = prospect.get('first_name', '(no name)')
            print(f"[{timestamp}] ✓ Sent to {email} ({vertical_name}, {first_name_display}) ({total_sent}/{total_to_send} this run)")

            # Calculate delay before next email (even spacing across time window)
            emails_remaining = total_to_send - total_sent
            time_remaining_seconds = (end_time - get_current_time_est()).total_seconds()
            delay = calculate_send_delay(emails_remaining, time_remaining_seconds, total_sent)

            if emails_remaining > 0:
                # Calculate expected completion time
                expected_completion = get_current_time_est() + timedelta(seconds=delay * emails_remaining)
                print(f"           Waiting {delay:.0f}s before next send (will finish ~{expected_completion.strftime('%I:%M%p')})")
                time.sleep(delay)
        else:
            # Log failure
            log_sent_email(email, vertical, subject, 'FAILED', error)
            log_error(email, vertical, 'SEND_FAILURE', error, 'Skipped and continued')
            
            consecutive_failures += 1
            print(f"[{get_current_time_est().strftime('%H:%M:%S')}] ❌ Failed to send to {email}: {error}")
            
            # If 5 consecutive failures, pause and alert
            if consecutive_failures >= 5:
                print("\n🚨 5 consecutive failures detected. Pausing for 30 minutes...")
                print("   Check your Gmail settings and APP_PASSWORD")
                time.sleep(1800)  # 30 minutes
                consecutive_failures = 0
        
        # Save progress every 10 emails
        if emails_since_save >= 10:
            emails_since_save = 0
            # Already saving in real-time, but this is a checkpoint
    
    return total_sent

def display_session_summary(total_sent: int, active_verticals: List[str]):
    """Display summary at end of session"""
    # Count successes and failures
    success_count = 0
    failure_count = 0
    by_vertical = {v: 0 for v in config.VERTICALS.keys()}
    
    if os.path.exists(config.SENT_TRACKER):
        df = pd.read_csv(config.SENT_TRACKER)
        
        # Filter to this session (approximate - last N emails)
        df_recent = df.tail(total_sent) if total_sent > 0 else df.tail(10)
        
        success_count = len(df_recent[df_recent['status'] == 'SUCCESS'])
        failure_count = len(df_recent[df_recent['status'] == 'FAILED'])
        
        # Count by vertical
        for vertical in by_vertical.keys():
            by_vertical[vertical] = len(df_recent[(df_recent['vertical'] == vertical) & (df_recent['status'] == 'SUCCESS')])
    
    # Calculate next send window
    next_window, time_str = calculate_next_send_window()
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  SESSION SUMMARY                                           ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║  Total sent: {total_sent:<44}  ║")
    print(f"║  Success: {success_count:<47}  ║")
    print(f"║  Failed: {failure_count:<48}  ║")
    print("║                                                            ║")
    print("║  Breakdown by vertical:                                    ║")
    for vertical in active_verticals:
        name = config.VERTICALS[vertical]['name']
        count = by_vertical[vertical]
        print(f"║    {name:<20} {count:<32} sent  ║")
    print("║                                                            ║")
    print(f"║  Next send window: {next_window.strftime('%A %I:%M%p EST'):<35}  ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main(dry_run: bool = False):
    """Main execution loop with continuous running mode"""
    global interrupted

    print("=" * 70)
    print("EMAIL VALIDATION CAMPAIGN SYSTEM - INITIAL OUTREACH")
    print("=" * 70)
    print(f"\nStarted: {get_current_time_est().strftime('%Y-%m-%d %H:%M:%S %Z')}\n")

    if dry_run:
        print("🧪 DRY RUN MODE: Preview only, no emails will be sent\n")

    if config.TEST_MODE:
        print(f"🧪 TEST MODE ENABLED")
        print(f"   Vertical: {config.TEST_VERTICAL}")
        print(f"   Email type: {config.TEST_EMAIL_TYPE}")
        print(f"   Test emails: {', '.join(config.TEST_EMAIL_ADDRESSES)}")
        print(f"   Will send {len(config.TEST_EMAIL_ADDRESSES)} test email(s)\n")
    else:
        print(f"🚀 PRODUCTION MODE")
        print(f"   Active verticals: {', '.join(config.ACTIVE_VERTICALS)}")
        print(f"   Daily limit: {config.TOTAL_DAILY_LIMIT} emails\n")
    
    # Initialize tracking files
    initialize_tracking_files()
    
    # Load prospects
    print("📋 Loading prospect lists...")
    prospects_by_vertical = {}
    
    if config.TEST_MODE:
        # Only load TEST_VERTICAL in test mode
        vertical = config.TEST_VERTICAL
        df = load_prospects(vertical)
        if not df.empty:
            prospects_by_vertical[vertical] = df
            print(f"   ✓ {config.VERTICALS[vertical]['name']}: {len(df)} prospects")
        else:
            print(f"   ❌ {config.VERTICALS[vertical]['name']}: No prospects found")
    else:
        # Load all ACTIVE_VERTICALS in production
        for vertical in config.ACTIVE_VERTICALS:
            df = load_prospects(vertical)
            if not df.empty:
                prospects_by_vertical[vertical] = df
                print(f"   ✓ {config.VERTICALS[vertical]['name']}: {len(df)} prospects")
            else:
                print(f"   ❌ {config.VERTICALS[vertical]['name']}: No prospects found")
    
    if not prospects_by_vertical:
        print("\n❌ No prospect data found. Exiting.")
        return

    # Load already-sent emails (for deduplication) - load early for statistics
    sent_emails = load_sent_emails()

    # Display email statistics (all-time, last 24h, this week)
    all_time_count, last_24h_count = display_email_statistics(prospects_by_vertical, sent_emails)

    print("💡 NOTE: 'Sent in last 24 hours' controls your daily limit (rolling window).")
    print("   The all-time 'Sent' counts are for tracking progress and deduplication.\n")

    # Get user approval before proceeding (CRITICAL: prevents accidental duplicate sends)
    if not get_user_approval(prospects_by_vertical, sent_emails, dry_run):
        print("Exiting without sending emails.")
        return

    if dry_run:
        print("🧪 Dry run complete. Exiting.")
        return

    # Main continuous loop
    while not interrupted:
        # In test mode, skip business hours and daily limit checks
        if config.TEST_MODE:
            sent_count = send_batch(prospects_by_vertical, sent_emails, 1)
            print("\n🧪 Test mode complete. Exiting.")
            break
        
        # Check business hours
        if not is_business_hours():
            next_window, time_str = calculate_next_send_window()
            
            if get_current_time_est().weekday() >= 5:
                display_status_box("WEEKEND - Waiting for Monday", next_window, time_str)
            elif get_current_time_est().hour < config.BUSINESS_HOURS_START:
                display_status_box("BEFORE BUSINESS HOURS - Waiting", next_window, time_str)
            else:
                display_status_box("AFTER BUSINESS HOURS - Waiting for tomorrow", next_window, time_str)
            
            # Sleep for 15 minutes, then check again
            for i in range(15):
                if interrupted:
                    break
                time.sleep(60)  # 1 minute
            continue

        # Calculate business hours end time for capacity analysis
        now = get_current_time_est()
        end_time = now.replace(hour=config.BUSINESS_HOURS_END, minute=0, second=0, microsecond=0)

        # Check daily limit using rolling capacity analysis
        temp_capacity_check = coordination.get_rolling_capacity_analysis(
            current_time=now,
            business_hours_end=end_time,
            daily_limit=config.TOTAL_DAILY_LIMIT
        )

        if temp_capacity_check['current_capacity'] <= 0:
            print(f"\n📊 Daily limit reached ({temp_capacity_check['emails_in_last_24h']}/{config.TOTAL_DAILY_LIMIT})")
            next_window, time_str = calculate_next_send_window()
            display_status_box("DAILY LIMIT REACHED - Waiting for next window", next_window, time_str)

            # Sleep for 15 minutes, then check again
            for i in range(15):
                if interrupted:
                    break
                time.sleep(60)
            continue
        
        # Ready to send!
        print(f"\n✅ Business hours detected (Mon-Fri, 9am-3pm EST)")

        # Get rolling capacity analysis with age-out projections
        capacity_analysis = coordination.get_rolling_capacity_analysis(
            current_time=get_current_time_est(),
            business_hours_end=end_time,
            daily_limit=config.TOTAL_DAILY_LIMIT
        )

        # Display rolling capacity analysis
        coordination.display_rolling_capacity_analysis(capacity_analysis, detailed=True)

        # Reload sent_emails from file to catch any emails sent by other instances
        # or since the last batch (prevents duplicates when restarting script)
        print("📋 Reloading sent emails from tracker (deduplication)...")
        sent_emails = load_sent_emails()
        sent_count_before_batch = len(sent_emails)
        print(f"   ✓ Loaded {sent_count_before_batch} previously sent emails\n")

        # Calculate how many initial emails need to be sent (total unsent across all verticals)
        print("📊 Calculating unsent prospects by vertical...")
        needs_by_vertical = {}
        total_initial_needs = 0
        for vertical in config.ACTIVE_VERTICALS:
            if vertical in prospects_by_vertical:
                df = prospects_by_vertical[vertical]
                unsent = df[~df.apply(lambda row: (row['email'], vertical) in sent_emails, axis=1)]
                needs_by_vertical[vertical] = len(unsent)
                total_initial_needs += len(unsent)
                print(f"   ✓ {config.VERTICALS[vertical]['name']}: {len(unsent)} unsent")

        print(f"   Total unsent prospects: {total_initial_needs}\n")

        # Report needs and get allocation from coordination system
        print("📊 Coordinating with follow-up script...")
        allocated_capacity = coordination.report_needs_and_allocate('initial', total_initial_needs)
        coordination.mark_script_running('initial')

        # Display coordination summary (central status view)
        coordination.display_allocation_summary()

        # Get how many we can still send (remaining capacity)
        remaining_capacity = coordination.get_remaining_capacity('initial')

        # Enhanced daily allocation display
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║  TODAY'S ALLOCATION (from coordination)                   ║")
        print("╠════════════════════════════════════════════════════════════╣")
        print(f"║  Total allocated (this script):   {allocated_capacity:<24} ║")
        print(f"║  Already sent (this allocation):  {allocated_capacity - remaining_capacity:<24} ║")
        print(f"║  Remaining (this allocation):     {remaining_capacity:<24} ║")
        print("╚════════════════════════════════════════════════════════════╝\n")

        # If we've already sent our allocation, we're done
        if remaining_capacity <= 0:
            print(f"\n✅ Allocation complete! Already sent {allocated_capacity}/{allocated_capacity} emails.")
            print("   Waiting for next send window...\n")
            # Sleep for 15 minutes, then check again
            for i in range(15):
                if interrupted:
                    break
                time.sleep(60)
            continue

        # Send batch (only what we have remaining)
        # Use the minimum of allocation capacity and rolling 24h capacity
        effective_capacity = min(remaining_capacity, capacity_analysis['current_capacity'])
        print(f"✅ Will send: {effective_capacity} emails\n")

        sent_count = send_batch(prospects_by_vertical, sent_emails, effective_capacity)

        # Update coordination with total sent count (today only, not all-time)
        if sent_count > 0:
            # Count emails sent TODAY (calendar day) for coordination tracking
            total_sent_today = get_emails_sent_today('initial')
            coordination.update_sent_count('initial', total_sent_today)
        
        # Display summary
        if sent_count > 0:
            display_session_summary(sent_count, config.ACTIVE_VERTICALS)
        
        # Wait and check again
        print("\n⏸️  Batch complete. Checking conditions again in 15 minutes...")
        for i in range(15):
            if interrupted:
                break
            time.sleep(60)
    
    # Graceful shutdown with auto-sync and bounce check
    shutdown_hooks.run_shutdown_hooks('initial', check_bounces=True, sync_crm=True)
    print(f"\n✅ Sent {emails_sent_this_session} emails this session.")
    print("💡 Run script again to pick up where you left off.\n")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Email Validation Campaign System - Initial Outreach',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python send_initial_outreach.py              # Normal run with user approval
  python send_initial_outreach.py --dry-run    # Preview mode, show stats but don't send

Safety Features:
  - User approval required before sending
  - Duplicate detection and prevention
  - File sync to prevent WSL/Windows caching issues
  - Comprehensive logging
        '''
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview mode: show statistics and preview without sending emails'
    )
    args = parser.parse_args()

    try:
        main(dry_run=args.dry_run)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
