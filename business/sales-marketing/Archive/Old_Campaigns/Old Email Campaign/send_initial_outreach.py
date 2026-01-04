#!/usr/bin/env python3
"""
Email Validation Campaign System - Initial Outreach
Sends initial validation emails to prospects across 3 verticals with smart pacing and anti-spam measures.
"""

import os
import sys
import time
import random
import smtplib
import csv
import signal
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Tuple, Optional
import pandas as pd
import pytz

# Import configuration
import config

# ============================================================================
# GLOBAL STATE
# ============================================================================

interrupted = False
emails_sent_this_session = 0

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global interrupted
    print("\n\n🛑 Interruption detected. Saving progress and shutting down...")
    interrupted = True

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

def initialize_tracking_files():
    """Initialize CSV tracking files if they don't exist"""
    # Initialize sent_tracker.csv
    if not os.path.exists(config.SENT_TRACKER):
        with open(config.SENT_TRACKER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'email', 'vertical', 'message_type', 'subject_line', 'status', 'error_message'])

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

        # Parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Get cutoff time (24 hours ago)
        cutoff = get_current_time_est() - timedelta(hours=24)

        # Count emails sent after cutoff
        recent = df[df['timestamp'] >= cutoff]
        return len(recent)
    except Exception as e:
        print(f"⚠️  Warning: Could not count recent emails: {e}")
        return 0

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
        msg = MIMEMultipart()
        msg['From'] = f"{config.YOUR_NAME} <{config.YOUR_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail SMTP
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.YOUR_EMAIL, config.APP_PASSWORD)

        # Send email
        server.send_message(msg)
        server.quit()

        return True, None
    except Exception as e:
        return False, str(e)

def log_sent_email(email: str, vertical: str, subject: str, status: str, error_msg: Optional[str] = None):
    """Log sent email to tracking file"""
    timestamp = get_current_time_est().strftime('%Y-%m-%d %H:%M:%S')

    with open(config.SENT_TRACKER, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, email, vertical, 'initial', subject, status, error_msg or ''])

def log_error(email: str, vertical: str, error_type: str, error_msg: str, action: str):
    """Log error to error log file"""
    timestamp = get_current_time_est().strftime('%Y-%m-%d %H:%M:%S')

    with open(config.ERROR_LOG, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, email, vertical, error_type, error_msg, action])

def update_response_tracker(email: str, vertical: str):
    """Add entry to response tracker for manual tracking"""
    timestamp = get_current_time_est().strftime('%Y-%m-%d')

    with open(config.RESPONSE_TRACKER, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email, vertical, timestamp, 'PENDING', '', ''])

def calculate_send_delay(emails_remaining: int, time_remaining_seconds: int, emails_sent_count: int) -> float:
    """Calculate delay before next email with anti-spam randomization"""

    # If we have plenty of time, use base delay
    if time_remaining_seconds <= 0 or emails_remaining <= 0:
        base = random.uniform(config.BASE_DELAY_MIN, config.BASE_DELAY_MAX)
        jitter = random.uniform(-2, 2)
        return max(1, base + jitter)

    # Calculate target pace
    target_pace = time_remaining_seconds / emails_remaining

    # Apply ±15% variation
    min_delay = target_pace * 0.85
    max_delay = target_pace * 1.15

    # Random delay in range
    base_delay = random.uniform(min_delay, max_delay)

    # Add micro-jitter (±2 seconds)
    jitter = random.uniform(-2, 2)
    final_delay = base_delay + jitter

    # Ensure minimum 5 seconds
    final_delay = max(config.BASE_DELAY_MIN, final_delay)

    # Add occasional coffee breaks (every 10-20 emails)
    if emails_sent_count > 0 and emails_sent_count % random.randint(config.BREAK_FREQUENCY_MIN, config.BREAK_FREQUENCY_MAX) == 0:
        break_time = random.uniform(config.BREAK_DURATION_MIN, config.BREAK_DURATION_MAX)
        print(f"☕ Taking a coffee break... ({break_time:.0f} seconds)")
        final_delay += break_time

    return final_delay

def display_status_box(message: str, next_window: Optional[datetime] = None, time_remaining: Optional[str] = None):
    """Display status in a formatted box"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print(f"║  {message:<56}  ║")
    if next_window:
        print("╠════════════════════════════════════════════════════════════╣")
        print(f"║  Next window: {next_window.strftime('%A %I:%M%p EST'):<43}  ║")
    if time_remaining:
        print(f"║  Time remaining: {time_remaining:<42}  ║")
    print("║                                                            ║")
    print("║  Press Ctrl+C to stop                                      ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

def send_batch(prospects_by_vertical: Dict[str, pd.DataFrame], sent_emails: set, daily_limit_remaining: int) -> int:
    """Send batch of emails across all verticals"""
    global interrupted, emails_sent_this_session

    total_sent = 0
    consecutive_failures = 0
    emails_since_save = 0

    # Prepare prospect pools
    pools = {}
    for vertical, df in prospects_by_vertical.items():
        # Filter out already-sent emails
        unsent = df[~df.apply(lambda row: (row['email'], vertical) in sent_emails, axis=1)]
        pools[vertical] = unsent.to_dict('records')
        random.shuffle(pools[vertical])  # Randomize order

    # Calculate total emails to send
    if config.TEST_MODE:
        emails_per_vertical = 3
        print("\n🧪 TEST MODE: Sending 3 emails per vertical (9 total)\n")
    else:
        emails_per_vertical = min(config.EMAILS_PER_VERTICAL_PER_DAY, daily_limit_remaining // 3)

    total_to_send = min(emails_per_vertical * 3, daily_limit_remaining)

    # Calculate time remaining today
    now = get_current_time_est()
    end_time = now.replace(hour=config.BUSINESS_HOURS_END, minute=0, second=0, microsecond=0)
    time_remaining_seconds = (end_time - now).total_seconds()

    print(f"📊 Ready to send:")
    print(f"   • Total emails: {total_to_send}")
    print(f"   • Per vertical: {emails_per_vertical}")
    print(f"   • Time remaining: {format_time_remaining(end_time - now)}")
    print(f"   • Average pace: ~{int((total_to_send / (time_remaining_seconds / 3600)) if time_remaining_seconds > 0 else 0)} emails/hour (randomized)\n")

    # Interleave emails from all three verticals
    vertical_keys = list(pools.keys())
    vertical_index = 0

    while total_sent < total_to_send and not interrupted:
        # Check if we've left business hours
        if not is_business_hours():
            print("\n⏰ Business hours ended. Stopping for today.")
            break

        # Round-robin through verticals
        vertical = vertical_keys[vertical_index % len(vertical_keys)]
        vertical_index += 1

        # Skip if this vertical is exhausted
        if not pools[vertical]:
            continue

        # Get next prospect
        prospect = pools[vertical].pop(0)
        email = prospect['email']

        # Select random subject line
        subject = random.choice(config.VERTICALS[vertical]['initial_subject_lines'])

        # Get email body
        body = config.VERTICALS[vertical]['initial_template']

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

            # Display progress
            timestamp = get_current_time_est().strftime('%H:%M:%S')
            vertical_name = config.VERTICALS[vertical]['name']
            print(f"[{timestamp}] ✓ Sent to {email} ({vertical_name}) ({total_sent}/{total_to_send} today)")

            # Calculate delay before next email
            emails_remaining = total_to_send - total_sent
            time_remaining_seconds = (end_time - get_current_time_est()).total_seconds()
            delay = calculate_send_delay(emails_remaining, time_remaining_seconds, total_sent)

            if emails_remaining > 0:
                print(f"           Waiting {delay:.0f} seconds before next send...")
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

def display_session_summary(total_sent: int):
    """Display summary at end of session"""
    # Count successes and failures
    success_count = 0
    failure_count = 0
    by_vertical = {'food_recall': 0, 'debarment': 0, 'grant_alerts': 0}

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
    print(f"║    Food Recall:     {by_vertical['food_recall']:<36} sent  ║")
    print(f"║    Debarment:       {by_vertical['debarment']:<36} sent  ║")
    print(f"║    Grant Alerts:    {by_vertical['grant_alerts']:<36} sent  ║")
    print("║                                                            ║")
    print(f"║  Next send window: {next_window.strftime('%A %I:%M%p EST'):<35}  ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution loop with continuous running mode"""
    global interrupted

    print("=" * 70)
    print("EMAIL VALIDATION CAMPAIGN SYSTEM - INITIAL OUTREACH")
    print("=" * 70)
    print(f"\nStarted: {get_current_time_est().strftime('%Y-%m-%d %H:%M:%S %Z')}\n")

    if config.TEST_MODE:
        print("🧪 TEST MODE ENABLED - Will send only 9 emails (3 per vertical)\n")

    # Initialize tracking files
    initialize_tracking_files()

    # Load prospects
    print("📋 Loading prospect lists...")
    prospects_by_vertical = {}
    for vertical in config.VERTICALS.keys():
        df = load_prospects(vertical)
        if not df.empty:
            prospects_by_vertical[vertical] = df
            print(f"   ✓ {config.VERTICALS[vertical]['name']}: {len(df)} prospects")
        else:
            print(f"   ❌ {config.VERTICALS[vertical]['name']}: No prospects found")

    if not prospects_by_vertical:
        print("\n❌ No prospect data found. Exiting.")
        return

    # Load already-sent emails
    sent_emails = load_sent_emails()
    print(f"\n📊 Previously sent: {len(sent_emails)} emails")

    # Main continuous loop
    while not interrupted:
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

        # Check daily limit
        emails_last_24h = get_emails_sent_last_24h()
        daily_limit_remaining = config.TOTAL_DAILY_LIMIT - emails_last_24h

        if daily_limit_remaining <= 0:
            print(f"\n📊 Daily limit reached ({emails_last_24h}/{config.TOTAL_DAILY_LIMIT})")
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
        print(f"✅ Daily quota: {emails_last_24h}/{config.TOTAL_DAILY_LIMIT} sent in last 24h")
        print(f"✅ Remaining today: {daily_limit_remaining} emails\n")

        # Send batch
        sent_count = send_batch(prospects_by_vertical, sent_emails, daily_limit_remaining)

        # Display summary
        if sent_count > 0:
            display_session_summary(sent_count)

        # In test mode, exit after one batch
        if config.TEST_MODE:
            print("🧪 Test mode complete. Exiting.")
            break

        # Otherwise, wait and check again
        print("\n⏸️  Batch complete. Checking conditions again in 15 minutes...")
        for i in range(15):
            if interrupted:
                break
            time.sleep(60)

    # Graceful shutdown
    print(f"\n\n✅ Stopped. Sent {emails_sent_this_session} emails this session. All progress saved.")
    print("💡 Run script again to pick up where you left off.\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
