#!/usr/bin/env python3
"""
Email Validation Campaign System - Follow-up
Sends follow-up emails to non-responders 3+ days after initial outreach.
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
from typing import List, Dict, Tuple, Optional, Set
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
# HELPER FUNCTIONS (reused from initial script)
# ============================================================================

def get_current_time_est() -> datetime:
    """Get current time in EST"""
    return datetime.now(pytz.timezone(config.TIMEZONE))

def is_business_hours() -> bool:
    """Check if current time is within business hours (9am-3pm EST, Mon-Fri)"""
    now = get_current_time_est()

    if now.weekday() >= 5:
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
        days_until_monday = 2
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        return next_window, format_time_remaining(next_window - now)

    if now.weekday() == 6:
        days_until_monday = 1
        next_window = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
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

def initialize_tracking_files():
    """Initialize CSV tracking files if they don't exist"""
    if not os.path.exists(config.SENT_TRACKER):
        with open(config.SENT_TRACKER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'email', 'vertical', 'message_type', 'subject_line', 'status', 'error_message'])

    if not os.path.exists(config.RESPONSE_TRACKER):
        with open(config.RESPONSE_TRACKER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'vertical', 'initial_sent_date', 'replied', 'followup_sent_date', 'notes'])

    if not os.path.exists(config.ERROR_LOG):
        with open(config.ERROR_LOG, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'email', 'vertical', 'error_type', 'error_message', 'action_taken'])

def get_emails_sent_last_24h() -> int:
    """Count how many emails were sent in the last 24 hours"""
    if not os.path.exists(config.SENT_TRACKER):
        return 0

    try:
        df = pd.read_csv(config.SENT_TRACKER)
        if df.empty:
            return 0

        df = df[df['status'] == 'SUCCESS']
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = get_current_time_est() - timedelta(hours=24)
        recent = df[df['timestamp'] >= cutoff]
        return len(recent)
    except Exception as e:
        print(f"⚠️  Warning: Could not count recent emails: {e}")
        return 0

def send_email(to_email: str, subject: str, body: str) -> Tuple[bool, Optional[str]]:
    """Send email via Gmail SMTP"""
    if not config.APP_PASSWORD:
        return False, "APP_PASSWORD not configured"

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{config.YOUR_NAME} <{config.YOUR_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.YOUR_EMAIL, config.APP_PASSWORD)
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
        writer.writerow([timestamp, email, vertical, 'followup', subject, status, error_msg or ''])

def log_error(email: str, vertical: str, error_type: str, error_msg: str, action: str):
    """Log error to error log file"""
    timestamp = get_current_time_est().strftime('%Y-%m-%d %H:%M:%S')

    with open(config.ERROR_LOG, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, email, vertical, error_type, error_msg, action])

def update_response_tracker_followup(email: str, vertical: str):
    """Update response tracker with follow-up sent date"""
    # Read current tracker
    if not os.path.exists(config.RESPONSE_TRACKER):
        return

    try:
        df = pd.read_csv(config.RESPONSE_TRACKER)

        # Find matching row
        mask = (df['email'] == email) & (df['vertical'] == vertical)

        if mask.any():
            # Update followup_sent_date
            df.loc[mask, 'followup_sent_date'] = get_current_time_est().strftime('%Y-%m-%d')

            # Save back
            df.to_csv(config.RESPONSE_TRACKER, index=False)
    except Exception as e:
        print(f"⚠️  Warning: Could not update response tracker: {e}")

def calculate_send_delay(emails_remaining: int, time_remaining_seconds: int, emails_sent_count: int) -> float:
    """Calculate delay before next email with anti-spam randomization"""

    if time_remaining_seconds <= 0 or emails_remaining <= 0:
        base = random.uniform(config.BASE_DELAY_MIN, config.BASE_DELAY_MAX)
        jitter = random.uniform(-2, 2)
        return max(1, base + jitter)

    target_pace = time_remaining_seconds / emails_remaining
    min_delay = target_pace * 0.85
    max_delay = target_pace * 1.15
    base_delay = random.uniform(min_delay, max_delay)
    jitter = random.uniform(-2, 2)
    final_delay = base_delay + jitter
    final_delay = max(config.BASE_DELAY_MIN, final_delay)

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

# ============================================================================
# FOLLOW-UP SPECIFIC LOGIC
# ============================================================================

def get_followup_eligible_emails() -> Dict[str, List[str]]:
    """Get list of emails eligible for follow-up (sent 3+ days ago, no reply, no followup sent yet)"""
    eligible = {'food_recall': [], 'debarment': [], 'grant_alerts': []}

    if not os.path.exists(config.SENT_TRACKER) or not os.path.exists(config.RESPONSE_TRACKER):
        return eligible

    try:
        # Load sent tracker
        sent_df = pd.read_csv(config.SENT_TRACKER)
        sent_df['timestamp'] = pd.to_datetime(sent_df['timestamp'])

        # Load response tracker
        response_df = pd.read_csv(config.RESPONSE_TRACKER)

        # Calculate cutoff date (3 days ago)
        cutoff = get_current_time_est() - timedelta(days=3)

        # Find initial emails sent 3+ days ago
        initial_emails = sent_df[
            (sent_df['message_type'] == 'initial') &
            (sent_df['status'] == 'SUCCESS') &
            (sent_df['timestamp'] <= cutoff)
        ]

        # For each vertical
        for vertical in eligible.keys():
            vertical_emails = initial_emails[initial_emails['vertical'] == vertical]

            for _, row in vertical_emails.iterrows():
                email = row['email']

                # Check if already sent followup
                already_followed_up = sent_df[
                    (sent_df['email'] == email) &
                    (sent_df['vertical'] == vertical) &
                    (sent_df['message_type'] == 'followup') &
                    (sent_df['status'] == 'SUCCESS')
                ]

                if not already_followed_up.empty:
                    continue  # Skip if already sent followup

                # Check response tracker for replies
                response_row = response_df[
                    (response_df['email'] == email) &
                    (response_df['vertical'] == vertical)
                ]

                if not response_row.empty:
                    replied = response_row.iloc[0]['replied']

                    # Only send to PENDING or NO (not YES)
                    if replied in ['PENDING', 'NO']:
                        eligible[vertical].append(email)
                else:
                    # Not in response tracker - assume PENDING
                    eligible[vertical].append(email)

        return eligible

    except Exception as e:
        print(f"⚠️  Warning: Could not determine eligible emails: {e}")
        return eligible

def send_followup_batch(eligible_by_vertical: Dict[str, List[str]], daily_limit_remaining: int) -> int:
    """Send batch of follow-up emails"""
    global interrupted, emails_sent_this_session

    total_sent = 0
    consecutive_failures = 0

    # Calculate emails per vertical
    if config.TEST_MODE:
        emails_per_vertical = 3
        print("\n🧪 TEST MODE: Sending 3 follow-ups per vertical (9 total)\n")
    else:
        emails_per_vertical = min(config.EMAILS_PER_VERTICAL_PER_DAY, daily_limit_remaining // 3)

    total_to_send = min(emails_per_vertical * 3, daily_limit_remaining)

    # Calculate time remaining
    now = get_current_time_est()
    end_time = now.replace(hour=config.BUSINESS_HOURS_END, minute=0, second=0, microsecond=0)
    time_remaining_seconds = (end_time - now).total_seconds()

    print(f"📊 Ready to send follow-ups:")
    print(f"   • Total emails: {total_to_send}")
    print(f"   • Per vertical: {emails_per_vertical}")
    print(f"   • Time remaining: {format_time_remaining(end_time - now)}")
    print(f"   • Average pace: ~{int((total_to_send / (time_remaining_seconds / 3600)) if time_remaining_seconds > 0 else 0)} emails/hour (randomized)\n")

    # Prepare pools
    pools = {}
    for vertical, emails in eligible_by_vertical.items():
        random.shuffle(emails)
        pools[vertical] = emails[:emails_per_vertical]  # Limit per vertical

    # Interleave verticals
    vertical_keys = list(pools.keys())
    vertical_index = 0

    while total_sent < total_to_send and not interrupted:
        if not is_business_hours():
            print("\n⏰ Business hours ended. Stopping for today.")
            break

        vertical = vertical_keys[vertical_index % len(vertical_keys)]
        vertical_index += 1

        if not pools[vertical]:
            continue

        email = pools[vertical].pop(0)

        # Select random subject line
        subject = random.choice(config.VERTICALS[vertical]['followup_subject_lines'])

        # Get email body
        body = config.VERTICALS[vertical]['followup_template']

        # Send email
        success, error = send_email(email, subject, body)

        if success:
            log_sent_email(email, vertical, subject, 'SUCCESS')
            update_response_tracker_followup(email, vertical)

            total_sent += 1
            emails_sent_this_session += 1
            consecutive_failures = 0

            timestamp = get_current_time_est().strftime('%H:%M:%S')
            vertical_name = config.VERTICALS[vertical]['name']
            print(f"[{timestamp}] ✓ Sent follow-up to {email} ({vertical_name}) ({total_sent}/{total_to_send} today)")

            emails_remaining = total_to_send - total_sent
            time_remaining_seconds = (end_time - get_current_time_est()).total_seconds()
            delay = calculate_send_delay(emails_remaining, time_remaining_seconds, total_sent)

            if emails_remaining > 0:
                print(f"           Waiting {delay:.0f} seconds before next send...")
                time.sleep(delay)
        else:
            log_sent_email(email, vertical, subject, 'FAILED', error)
            log_error(email, vertical, 'SEND_FAILURE', error, 'Skipped and continued')

            consecutive_failures += 1
            print(f"[{get_current_time_est().strftime('%H:%M:%S')}] ❌ Failed to send to {email}: {error}")

            if consecutive_failures >= 5:
                print("\n🚨 5 consecutive failures detected. Pausing for 30 minutes...")
                print("   Check your Gmail settings and APP_PASSWORD")
                time.sleep(1800)
                consecutive_failures = 0

    return total_sent

def display_session_summary(total_sent: int):
    """Display summary at end of session"""
    success_count = 0
    failure_count = 0
    by_vertical = {'food_recall': 0, 'debarment': 0, 'grant_alerts': 0}

    if os.path.exists(config.SENT_TRACKER):
        df = pd.read_csv(config.SENT_TRACKER)
        df_followup = df[df['message_type'] == 'followup']
        df_recent = df_followup.tail(total_sent) if total_sent > 0 else df_followup.tail(10)

        success_count = len(df_recent[df_recent['status'] == 'SUCCESS'])
        failure_count = len(df_recent[df_recent['status'] == 'FAILED'])

        for vertical in by_vertical.keys():
            by_vertical[vertical] = len(df_recent[(df_recent['vertical'] == vertical) & (df_recent['status'] == 'SUCCESS')])

    next_window, time_str = calculate_next_send_window()

    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  FOLLOW-UP SESSION SUMMARY                                 ║")
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
    """Main execution loop for follow-up emails"""
    global interrupted

    print("=" * 70)
    print("EMAIL VALIDATION CAMPAIGN SYSTEM - FOLLOW-UP")
    print("=" * 70)
    print(f"\nStarted: {get_current_time_est().strftime('%Y-%m-%d %H:%M:%S %Z')}\n")

    if config.TEST_MODE:
        print("🧪 TEST MODE ENABLED - Will send only 9 follow-ups (3 per vertical)\n")

    # Initialize tracking files
    initialize_tracking_files()

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

            for i in range(15):
                if interrupted:
                    break
                time.sleep(60)
            continue

        # Check daily limit
        emails_last_24h = get_emails_sent_last_24h()
        daily_limit_remaining = config.TOTAL_DAILY_LIMIT - emails_last_24h

        if daily_limit_remaining <= 0:
            print(f"\n📊 Daily limit reached ({emails_last_24h}/{config.TOTAL_DAILY_LIMIT})")
            next_window, time_str = calculate_next_send_window()
            display_status_box("DAILY LIMIT REACHED - Waiting for next window", next_window, time_str)

            for i in range(15):
                if interrupted:
                    break
                time.sleep(60)
            continue

        # Get eligible emails for follow-up
        print("📋 Finding emails eligible for follow-up (sent 3+ days ago, no reply)...")
        eligible = get_followup_eligible_emails()

        total_eligible = sum(len(emails) for emails in eligible.values())

        if total_eligible == 0:
            print("\n📊 No emails eligible for follow-up at this time.")
            print("   (Need initial emails sent 3+ days ago with no reply)")
            print("\n⏸️  Waiting 1 hour before checking again...")

            for i in range(60):
                if interrupted:
                    break
                time.sleep(60)
            continue

        print(f"\n✅ Found {total_eligible} eligible for follow-up:")
        for vertical, emails in eligible.items():
            print(f"   • {config.VERTICALS[vertical]['name']}: {len(emails)}")

        print(f"\n✅ Business hours detected (Mon-Fri, 9am-3pm EST)")
        print(f"✅ Daily quota: {emails_last_24h}/{config.TOTAL_DAILY_LIMIT} sent in last 24h")
        print(f"✅ Remaining today: {daily_limit_remaining} emails\n")

        # Send batch
        sent_count = send_followup_batch(eligible, daily_limit_remaining)

        # Display summary
        if sent_count > 0:
            display_session_summary(sent_count)

        # In test mode, exit after one batch
        if config.TEST_MODE:
            print("🧪 Test mode complete. Exiting.")
            break

        # Otherwise, wait and check again
        print("\n⏸️  Batch complete. Checking for new eligible emails in 1 hour...")
        for i in range(60):
            if interrupted:
                break
            time.sleep(60)

    # Graceful shutdown
    print(f"\n\n✅ Stopped. Sent {emails_sent_this_session} follow-ups this session. All progress saved.")
    print("💡 Run script again to pick up where you left off.\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
