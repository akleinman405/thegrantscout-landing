#!/usr/bin/env python3
"""
Email Campaign Tracker for TheGrantScout
Monitors Gmail for bounces and replies, updates tracking CSVs, generates analytics.

Usage:
    python campaign_tracker.py --interactive  # Review each update before saving
    python campaign_tracker.py --auto         # Automatically update CSVs
    python campaign_tracker.py --help         # Show help
"""

import os
import sys
import re
import csv
import json
import argparse
import time
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Optional
import base64
import email
from email.utils import parsedate_to_datetime

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install -r requirements_tracker.txt")
    sys.exit(1)

# Import config for BASE_DIR and paths
try:
    import config
except ImportError:
    print("Error: config.py not found. Make sure you're in the correct directory.")
    sys.exit(1)


# ============================================================================
# CONSTANTS
# ============================================================================

# Gmail API scope (read-only)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# File paths from config
CREDENTIALS_FILE = os.path.join(
    os.path.dirname(__file__),
    'credentials',
    'credentials.json'
)
TOKEN_FILE = os.path.join(
    os.path.dirname(__file__),
    'credentials',
    'token.json'
)

# Tracking files (using config paths)
SENT_TRACKER = config.SENT_TRACKER
RESPONSE_TRACKER = config.RESPONSE_TRACKER

# Output directory for reports
REPORTS_DIR = os.path.join(
    os.path.dirname(__file__),
    'reports'
)

# Bounce detection patterns
BOUNCE_PATTERNS = {
    'from_mailer_daemon': 'from:mailer-daemon',
    'from_postmaster': 'from:postmaster',
    'delivery_status': 'subject:"Delivery Status Notification"',
    'undeliverable': 'subject:Undeliverable',
    'delivery_failed': 'subject:"Mail Delivery Failed"',
    'returned_mail': 'subject:"Returned mail"',
    'failure_notice': 'subject:"failure notice"',
}

# Common bounce email indicators in body
BOUNCE_BODY_INDICATORS = [
    'delivery has failed',
    'delivery status notification',
    'undeliverable',
    'recipient address rejected',
    'user unknown',
    'mailbox unavailable',
    'address not found',
    'does not exist',
    'invalid recipient',
    '550 5.1.1',
    '550 5.7.1',
    'permanent error',
]


# ============================================================================
# GMAIL AUTHENTICATION
# ============================================================================

def authenticate_gmail() -> Optional[object]:
    """
    Authenticate with Gmail API using OAuth2.
    Returns Gmail service object or None on failure.
    """
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except (ValueError, KeyError) as e:
            print(f"Warning: Invalid token file: {e}")
            print("Deleting invalid token and requesting new authentication...")
            try:
                os.remove(TOKEN_FILE)
            except OSError as rm_err:
                print(f"Warning: Could not delete invalid token: {rm_err}")
            creds = None

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            try:
                creds.refresh(Request())
            except RefreshError as e:
                print(f"Token refresh failed: {e}")
                print("Deleting invalid token and requesting new authentication...")
                try:
                    os.remove(TOKEN_FILE)
                except OSError as rm_err:
                    print(f"Warning: Could not delete invalid token: {rm_err}")
                creds = None
            except Exception as e:
                print(f"Unexpected error during token refresh: {e}")
                return None

        # If creds is None (no valid token), start new OAuth flow
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"Error: {CREDENTIALS_FILE} not found.")
                print("Please follow TRACKER_SETUP.md to set up Gmail API credentials.")
                return None

            print("Starting OAuth2 authentication flow...")
            print("A browser window will open for you to authorize access.")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Error during OAuth2 flow: {e}")
                return None

        # Save credentials for future use
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
                token.flush()
                os.fsync(token.fileno())  # WSL compatibility
            print(f"Credentials saved to {TOKEN_FILE}")
        except (IOError, OSError) as e:
            print(f"Warning: Could not save token file: {e}")
            print("Authentication will work but you'll need to re-authenticate next time.")

    try:
        service = build('gmail', 'v1', credentials=creds)
        print("Successfully authenticated with Gmail API")
        return service
    except HttpError as e:
        print(f"HTTP error building Gmail service: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error building Gmail service: {e}")
        return None


# ============================================================================
# EMAIL FETCHING
# ============================================================================

def search_emails(service, query: str, max_results: int = 500) -> List[Dict]:
    """
    Search Gmail for emails matching query with rate limiting.
    Returns list of message dictionaries.
    """
    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return []

        # Fetch full message details with rate limiting
        full_messages = []
        for idx, msg in enumerate(messages):
            # Add small delay every 10 messages to avoid rate limiting
            if idx > 0 and idx % 10 == 0:
                time.sleep(0.1)

            # Retry logic with exponential backoff for rate limit errors
            max_retries = 3
            retry_count = 0
            base_delay = 1.0

            while retry_count < max_retries:
                try:
                    full_msg = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    full_messages.append(full_msg)
                    break  # Success, exit retry loop

                except HttpError as e:
                    # Handle rate limiting (429 error)
                    if e.resp.status == 429:
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = base_delay * (2 ** (retry_count - 1))
                            print(f"Rate limit hit for message {msg['id']}, waiting {wait_time}s (retry {retry_count}/{max_retries})...")
                            time.sleep(wait_time)
                        else:
                            print(f"Warning: Max retries reached for message {msg['id']}, skipping")
                            break
                    else:
                        # Other HTTP error, skip this message
                        print(f"Warning: Could not fetch message {msg['id']}: {e}")
                        break

                except Exception as e:
                    print(f"Warning: Unexpected error fetching message {msg['id']}: {e}")
                    break

        return full_messages

    except HttpError as e:
        print(f"Error searching emails: {e}")
        return []


def get_header(message: Dict, header_name: str) -> Optional[str]:
    """Extract header value from Gmail message."""
    headers = message.get('payload', {}).get('headers', [])
    for header in headers:
        if header['name'].lower() == header_name.lower():
            return header['value']
    return None


def get_email_body(message: Dict) -> str:
    """Extract plain text body from Gmail message."""
    payload = message.get('payload', {})

    # Check for plain text in body
    if 'body' in payload and payload['body'].get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')

    # Check parts for plain text
    parts = payload.get('parts', [])
    for part in parts:
        if part['mimeType'] == 'text/plain' and part['body'].get('data'):
            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')

        # Check nested parts
        if 'parts' in part:
            for subpart in part['parts']:
                if subpart['mimeType'] == 'text/plain' and subpart['body'].get('data'):
                    return base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8', errors='ignore')

    return ""


def extract_email_addresses(text: str) -> Set[str]:
    """
    Extract all email addresses from text using regex with RFC 5321 validation.

    Validates:
    - Maximum length: 320 characters (64 local + @ + 255 domain)
    - Exactly one @ symbol
    - Local part: max 64 characters
    - Domain: max 255 characters, at least one dot
    """
    # Stricter pattern: requires domain with at least one dot and valid TLD
    email_pattern = r'\b[A-Za-z0-9][A-Za-z0-9._%+-]{0,63}@[A-Za-z0-9][A-Za-z0-9.-]{0,253}\.[A-Za-z]{2,}\b'
    potential_emails = re.findall(email_pattern, text, re.IGNORECASE)

    validated_emails = set()
    for email in potential_emails:
        # Length validation (RFC 5321)
        if len(email) > 320:
            continue

        # Ensure exactly one @ symbol
        if email.count('@') != 1:
            continue

        # Split and validate local and domain parts
        local, domain = email.split('@')
        if len(local) > 64 or len(domain) > 255:
            continue

        # Domain must have at least one dot
        if '.' not in domain:
            continue

        validated_emails.add(email)

    return validated_emails


# ============================================================================
# BOUNCE DETECTION
# ============================================================================

def find_bounced_emails(service, days_back: int = 30) -> Dict[str, Dict]:
    """
    Search for bounce notifications and extract failed email addresses.
    Returns dict: {email: {reason, date, message_snippet}}
    """
    print(f"\nSearching for bounce notifications (last {days_back} days)...")

    # Calculate date range
    since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')

    bounced_emails = {}

    # Search for each bounce pattern
    for pattern_name, pattern_query in BOUNCE_PATTERNS.items():
        query = f"{pattern_query} after:{since_date}"
        print(f"  Searching: {pattern_name}...")

        messages = search_emails(service, query, max_results=200)

        for msg in messages:
            # Extract failed email addresses
            subject = get_header(msg, 'Subject') or ''
            body = get_email_body(msg)
            from_addr = get_header(msg, 'From') or ''
            date_str = get_header(msg, 'Date') or ''

            # Parse date
            try:
                msg_date = parsedate_to_datetime(date_str)
            except (TypeError, ValueError, OverflowError):
                msg_date = datetime.now()

            # Combine subject and body for analysis
            full_text = f"{subject}\n{from_addr}\n{body}"

            # Check if it's really a bounce
            is_bounce = False
            bounce_reason = pattern_name

            for indicator in BOUNCE_BODY_INDICATORS:
                if indicator.lower() in full_text.lower():
                    is_bounce = True
                    bounce_reason = indicator
                    break

            if is_bounce:
                # Extract all email addresses
                emails = extract_email_addresses(full_text)

                # Filter to only include our sent emails (from sent_tracker)
                for email_addr in emails:
                    # Skip system emails
                    if 'mailer-daemon' in email_addr.lower():
                        continue
                    if 'postmaster' in email_addr.lower():
                        continue

                    # Add to bounced list
                    if email_addr not in bounced_emails:
                        bounced_emails[email_addr] = {
                            'reason': bounce_reason,
                            'date': msg_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'snippet': subject[:100]
                        }

    print(f"  Found {len(bounced_emails)} potential bounced addresses")
    return bounced_emails


# ============================================================================
# REPLY DETECTION
# ============================================================================

def find_replies(service, sent_emails: Set[str], days_back: int = 30) -> Dict[str, Dict]:
    """
    Find replies from recipients in sent_emails list.
    Returns dict: {email: {date, subject, snippet}}
    """
    print(f"\nSearching for replies from campaign recipients (last {days_back} days)...")

    since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')

    replies = {}

    # Search in inbox (excluding sent)
    query = f"in:inbox after:{since_date} -in:sent"
    messages = search_emails(service, query, max_results=1000)

    print(f"  Analyzing {len(messages)} inbox messages...")

    for msg in messages:
        from_addr = get_header(msg, 'From') or ''

        # Extract email from "Name <email@domain.com>" format
        from_email = None
        email_match = re.search(r'<(.+?)>', from_addr)
        if email_match:
            from_email = email_match.group(1).lower().strip()
        else:
            from_email = from_addr.lower().strip()

        # Check if this is from one of our campaign recipients
        if from_email in sent_emails:
            subject = get_header(msg, 'Subject') or ''
            date_str = get_header(msg, 'Date') or ''
            snippet = msg.get('snippet', '')

            # Parse date
            try:
                msg_date = parsedate_to_datetime(date_str)
            except (TypeError, ValueError, OverflowError):
                msg_date = datetime.now()

            # Only add if not already recorded (take earliest reply)
            if from_email not in replies:
                replies[from_email] = {
                    'date': msg_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'subject': subject,
                    'snippet': snippet[:200]
                }

    print(f"  Found {len(replies)} replies from campaign recipients")
    return replies


# ============================================================================
# CSV OPERATIONS
# ============================================================================

def load_sent_tracker() -> Tuple[List[Dict], Set[str]]:
    """
    Load sent_tracker.csv with validation.
    Returns (list of rows, set of sent emails)
    """
    if not os.path.exists(SENT_TRACKER):
        print(f"Warning: {SENT_TRACKER} not found")
        return [], set()

    rows = []
    sent_emails = set()
    required_fields = {'email', 'status', 'timestamp'}

    try:
        with open(SENT_TRACKER, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate CSV has required columns
            if reader.fieldnames is None:
                print(f"Error: {SENT_TRACKER} is empty or has no header row")
                return [], set()

            fieldnames_set = set(reader.fieldnames)
            missing_fields = required_fields - fieldnames_set

            if missing_fields:
                print(f"Error: {SENT_TRACKER} missing required columns: {missing_fields}")
                return [], set()

            # Process rows
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                email = row.get('email', '').strip()

                # Skip rows with empty email addresses
                if not email:
                    print(f"Warning: Row {row_num} has empty email address, skipping")
                    continue

                rows.append(row)
                sent_emails.add(email.lower())

        print(f"Loaded {len(rows)} records from sent_tracker.csv")
        return rows, sent_emails

    except csv.Error as e:
        print(f"Error: CSV parsing failed for {SENT_TRACKER}: {e}")
        return [], set()
    except UnicodeDecodeError as e:
        print(f"Error: File encoding issue in {SENT_TRACKER}: {e}")
        print("Hint: Ensure file is saved as UTF-8")
        return [], set()
    except Exception as e:
        print(f"Error: Unexpected error loading {SENT_TRACKER}: {type(e).__name__} - {e}")
        return [], set()


def load_response_tracker() -> List[Dict]:
    """Load response_tracker.csv with validation."""
    if not os.path.exists(RESPONSE_TRACKER):
        print(f"Warning: {RESPONSE_TRACKER} not found")
        return []

    rows = []
    required_fields = {'email', 'replied'}

    try:
        with open(RESPONSE_TRACKER, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate CSV has required columns
            if reader.fieldnames is None:
                print(f"Error: {RESPONSE_TRACKER} is empty or has no header row")
                return []

            fieldnames_set = set(reader.fieldnames)
            missing_fields = required_fields - fieldnames_set

            if missing_fields:
                print(f"Error: {RESPONSE_TRACKER} missing required columns: {missing_fields}")
                return []

            # Process rows
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                email = row.get('email', '').strip()

                # Skip rows with empty email addresses
                if not email:
                    print(f"Warning: Row {row_num} has empty email address, skipping")
                    continue

                rows.append(row)

        print(f"Loaded {len(rows)} records from response_tracker.csv")
        return rows

    except csv.Error as e:
        print(f"Error: CSV parsing failed for {RESPONSE_TRACKER}: {e}")
        return []
    except UnicodeDecodeError as e:
        print(f"Error: File encoding issue in {RESPONSE_TRACKER}: {e}")
        print("Hint: Ensure file is saved as UTF-8")
        return []
    except Exception as e:
        print(f"Error: Unexpected error loading {RESPONSE_TRACKER}: {type(e).__name__} - {e}")
        return []


def save_sent_tracker(rows: List[Dict]) -> None:
    """Save updated sent_tracker.csv with WSL compatibility."""
    if not rows:
        print("Warning: No rows to save in sent_tracker")
        return

    # Get fieldnames from first row
    fieldnames = list(rows[0].keys())

    # Write to temp file first
    temp_file = SENT_TRACKER + '.tmp'
    with open(temp_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        f.flush()
        os.fsync(f.fileno())  # WSL compatibility

    # Move temp file to final location
    os.replace(temp_file, SENT_TRACKER)
    print(f"Saved {len(rows)} records to sent_tracker.csv")


def save_response_tracker(rows: List[Dict]) -> None:
    """Save updated response_tracker.csv with WSL compatibility."""
    if not rows:
        print("Warning: No rows to save in response_tracker")
        return

    # Get fieldnames from first row
    fieldnames = list(rows[0].keys())

    # Write to temp file first
    temp_file = RESPONSE_TRACKER + '.tmp'
    with open(temp_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        f.flush()
        os.fsync(f.fileno())  # WSL compatibility

    # Move temp file to final location
    os.replace(temp_file, RESPONSE_TRACKER)
    print(f"Saved {len(rows)} records to response_tracker.csv")


# ============================================================================
# UPDATE LOGIC
# ============================================================================

def update_sent_tracker_with_bounces(
    sent_rows: List[Dict],
    bounced_emails: Dict[str, Dict]
) -> Tuple[List[Dict], int]:
    """
    Update sent_tracker with bounce information.
    Returns (updated_rows, num_updated)
    """
    updated_count = 0

    for row in sent_rows:
        email = row.get('email', '').lower().strip()

        if email in bounced_emails:
            bounce_info = bounced_emails[email]

            # Update status to BOUNCED if currently SUCCESS
            if row.get('status') == 'SUCCESS':
                row['status'] = 'BOUNCED'
                row['error_message'] = f"Bounce: {bounce_info['reason']} ({bounce_info['date']})"
                updated_count += 1

    return sent_rows, updated_count


def update_response_tracker_with_replies(
    response_rows: List[Dict],
    replies: Dict[str, Dict]
) -> Tuple[List[Dict], int]:
    """
    Update response_tracker with reply information.
    Returns (updated_rows, num_updated)
    """
    updated_count = 0

    for row in response_rows:
        email = row.get('email', '').lower().strip()

        if email in replies:
            reply_info = replies[email]

            # Update replied status if currently PENDING
            if row.get('replied') == 'PENDING':
                row['replied'] = 'YES'
                row['notes'] = f"Replied {reply_info['date']}: {reply_info['subject'][:50]}"
                updated_count += 1

    return response_rows, updated_count


# ============================================================================
# ANALYTICS & REPORTING
# ============================================================================

def generate_analytics(
    sent_rows: List[Dict],
    response_rows: List[Dict],
    bounced_emails: Dict[str, Dict],
    replies: Dict[str, Dict]
) -> Dict:
    """Generate analytics summary."""

    # Calculate metrics
    total_sent = len(sent_rows)
    total_success = sum(1 for r in sent_rows if r.get('status') == 'SUCCESS')
    total_bounced = sum(1 for r in sent_rows if r.get('status') == 'BOUNCED')
    total_replied = sum(1 for r in response_rows if r.get('replied') == 'YES')
    total_pending = sum(1 for r in response_rows if r.get('replied') == 'PENDING')

    # By vertical
    verticals = {}
    for row in sent_rows:
        vertical = row.get('vertical', 'unknown')
        if vertical not in verticals:
            verticals[vertical] = {
                'sent': 0,
                'success': 0,
                'bounced': 0,
                'replied': 0,
                'pending': 0
            }

        verticals[vertical]['sent'] += 1
        if row.get('status') == 'SUCCESS':
            verticals[vertical]['success'] += 1
        elif row.get('status') == 'BOUNCED':
            verticals[vertical]['bounced'] += 1

    # Count replies by vertical
    for row in response_rows:
        vertical = row.get('vertical', 'unknown')
        if vertical in verticals:
            if row.get('replied') == 'YES':
                verticals[vertical]['replied'] += 1
            elif row.get('replied') == 'PENDING':
                verticals[vertical]['pending'] += 1

    # Calculate rates
    bounce_rate = (total_bounced / total_sent * 100) if total_sent > 0 else 0
    reply_rate = (total_replied / total_success * 100) if total_success > 0 else 0

    return {
        'timestamp': datetime.now().isoformat(),
        'total_sent': total_sent,
        'total_success': total_success,
        'total_bounced': total_bounced,
        'new_bounces': len(bounced_emails),
        'total_replied': total_replied,
        'new_replies': len(replies),
        'total_pending': total_pending,
        'bounce_rate': round(bounce_rate, 2),
        'reply_rate': round(reply_rate, 2),
        'verticals': verticals
    }


def print_analytics(analytics: Dict) -> None:
    """Print analytics to console."""
    print("\n" + "="*70)
    print("EMAIL CAMPAIGN ANALYTICS")
    print("="*70)
    print(f"Generated: {analytics['timestamp']}")
    print()

    print("OVERALL METRICS:")
    print(f"  Total Emails Sent:     {analytics['total_sent']}")
    print(f"  Successfully Delivered: {analytics['total_success']}")
    print(f"  Bounced:               {analytics['total_bounced']} ({analytics['bounce_rate']}%)")
    print(f"  New Bounces Found:     {analytics['new_bounces']}")
    print()

    print("RESPONSE METRICS:")
    print(f"  Total Replies:         {analytics['total_replied']}")
    print(f"  New Replies Found:     {analytics['new_replies']}")
    print(f"  Pending Responses:     {analytics['total_pending']}")
    print(f"  Reply Rate:            {analytics['reply_rate']}%")
    print()

    print("BY VERTICAL:")
    print(f"{'Vertical':<20} {'Sent':<8} {'Bounced':<10} {'Replied':<10} {'Pending':<10}")
    print("-" * 70)

    for vertical, stats in analytics['verticals'].items():
        reply_rate = (stats['replied'] / stats['success'] * 100) if stats['success'] > 0 else 0
        print(f"{vertical:<20} {stats['sent']:<8} {stats['bounced']:<10} "
              f"{stats['replied']:<10} {stats['pending']:<10}")

    print("="*70)


def save_analytics_report(analytics: Dict) -> str:
    """Save analytics to CSV report file."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(REPORTS_DIR, f'campaign_report_{timestamp}.csv')

    # Write overall metrics
    with open(report_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        writer.writerow(['Campaign Analytics Report'])
        writer.writerow(['Generated', analytics['timestamp']])
        writer.writerow([])

        writer.writerow(['Overall Metrics'])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Emails Sent', analytics['total_sent']])
        writer.writerow(['Successfully Delivered', analytics['total_success']])
        writer.writerow(['Total Bounced', analytics['total_bounced']])
        writer.writerow(['New Bounces Found', analytics['new_bounces']])
        writer.writerow(['Bounce Rate %', analytics['bounce_rate']])
        writer.writerow(['Total Replies', analytics['total_replied']])
        writer.writerow(['New Replies Found', analytics['new_replies']])
        writer.writerow(['Pending Responses', analytics['total_pending']])
        writer.writerow(['Reply Rate %', analytics['reply_rate']])
        writer.writerow([])

        writer.writerow(['By Vertical'])
        writer.writerow(['Vertical', 'Sent', 'Success', 'Bounced', 'Replied', 'Pending', 'Reply Rate %'])

        for vertical, stats in analytics['verticals'].items():
            reply_rate = (stats['replied'] / stats['success'] * 100) if stats['success'] > 0 else 0
            writer.writerow([
                vertical,
                stats['sent'],
                stats['success'],
                stats['bounced'],
                stats['replied'],
                stats['pending'],
                round(reply_rate, 2)
            ])

        f.flush()
        os.fsync(f.fileno())  # WSL compatibility

    print(f"\nAnalytics report saved to: {report_file}")
    return report_file


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Email Campaign Tracker for TheGrantScout',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python campaign_tracker.py --interactive    # Review updates before saving
  python campaign_tracker.py --auto           # Automatically update CSVs
  python campaign_tracker.py --days 7         # Check last 7 days only
        """
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Review updates before saving (default)'
    )

    parser.add_argument(
        '--auto',
        action='store_true',
        help='Automatically save updates without confirmation'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to search back (default: 30)'
    )

    args = parser.parse_args()

    # Default to interactive if neither flag is set
    interactive_mode = args.interactive or not args.auto

    print("="*70)
    print("EMAIL CAMPAIGN TRACKER - TheGrantScout")
    print("="*70)
    print(f"Mode: {'INTERACTIVE' if interactive_mode else 'AUTO'}")
    print(f"Search range: Last {args.days} days")
    print()

    # Step 1: Authenticate with Gmail
    print("[1/6] Authenticating with Gmail API...")
    service = authenticate_gmail()
    if not service:
        print("Failed to authenticate. Exiting.")
        sys.exit(1)

    # Step 2: Load tracking CSVs
    print("\n[2/6] Loading tracking CSVs...")
    sent_rows, sent_emails = load_sent_tracker()
    response_rows = load_response_tracker()

    if not sent_rows:
        print("No sent emails found. Exiting.")
        sys.exit(1)

    # Step 3: Search for bounces
    print("\n[3/6] Searching for bounce notifications...")
    bounced_emails = find_bounced_emails(service, days_back=args.days)

    # Filter bounces to only include emails we actually sent
    relevant_bounces = {
        email: info for email, info in bounced_emails.items()
        if email.lower() in sent_emails
    }

    if relevant_bounces:
        print(f"\nFound {len(relevant_bounces)} bounced emails from campaign:")
        for email, info in list(relevant_bounces.items())[:10]:  # Show first 10
            print(f"  - {email}: {info['reason']}")
        if len(relevant_bounces) > 10:
            print(f"  ... and {len(relevant_bounces) - 10} more")
    else:
        print("No bounced emails found from campaign.")

    # Step 4: Search for replies
    print("\n[4/6] Searching for replies...")
    replies = find_replies(service, sent_emails, days_back=args.days)

    if replies:
        print(f"\nFound {len(replies)} replies:")
        for email, info in list(replies.items())[:10]:  # Show first 10
            print(f"  - {email}: {info['subject'][:50]}")
        if len(replies) > 10:
            print(f"  ... and {len(replies) - 10} more")
    else:
        print("No replies found.")

    # Step 5: Update tracking data
    print("\n[5/6] Updating tracking data...")

    updated_sent_rows, bounce_updates = update_sent_tracker_with_bounces(
        sent_rows, relevant_bounces
    )

    updated_response_rows, reply_updates = update_response_tracker_with_replies(
        response_rows, replies
    )

    print(f"  Sent tracker: {bounce_updates} records updated with bounces")
    print(f"  Response tracker: {reply_updates} records updated with replies")

    # Step 6: Generate analytics
    print("\n[6/6] Generating analytics...")
    analytics = generate_analytics(
        updated_sent_rows,
        updated_response_rows,
        relevant_bounces,
        replies
    )

    print_analytics(analytics)

    # Save analytics report
    report_file = save_analytics_report(analytics)

    # Interactive confirmation
    if interactive_mode and (bounce_updates > 0 or reply_updates > 0):
        print("\n" + "="*70)
        print("UPDATES SUMMARY:")
        print(f"  {bounce_updates} bounces to mark in sent_tracker.csv")
        print(f"  {reply_updates} replies to mark in response_tracker.csv")
        print()

        response = input("Save these updates to CSV files? [y/N]: ").strip().lower()

        if response == 'y':
            if bounce_updates > 0:
                save_sent_tracker(updated_sent_rows)
            if reply_updates > 0:
                save_response_tracker(updated_response_rows)
            print("\nUpdates saved successfully!")
        else:
            print("\nUpdates discarded. CSV files unchanged.")

    elif not interactive_mode and (bounce_updates > 0 or reply_updates > 0):
        # Auto mode - save without confirmation
        if bounce_updates > 0:
            save_sent_tracker(updated_sent_rows)
        if reply_updates > 0:
            save_response_tracker(updated_response_rows)
        print("\nUpdates saved automatically (auto mode).")

    else:
        print("\nNo updates to save.")

    print("\n" + "="*70)
    print("Campaign tracking complete!")
    print("="*70)


if __name__ == '__main__':
    main()
