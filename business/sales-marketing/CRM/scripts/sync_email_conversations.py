#!/usr/bin/env python3
"""
Sync Email Conversations from Gmail to CRM

Pulls sent emails and replies from Gmail and stores them in Supabase
for display in the CRM prospect detail view.

Usage:
    python sync_email_conversations.py                    # Sync last 30 days
    python sync_email_conversations.py --days 7           # Sync last 7 days
    python sync_email_conversations.py --full             # Full sync (90 days)
    python sync_email_conversations.py --dry-run          # Preview without saving
"""

import os
import sys
import re
import base64
import argparse
import time
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Tuple
from email.utils import parsedate_to_datetime

import requests

# Add email campaign folder to path for Gmail auth
EMAIL_CAMPAIGN_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'Email_Campaign', 'Email Campaign 2025-11-3'
)
sys.path.insert(0, EMAIL_CAMPAIGN_PATH)

# Gmail API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError as e:
    print(f"Error: Gmail API packages not installed: {e}")
    print("Run: pip install google-auth-oauthlib google-api-python-client")
    GMAIL_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Supabase CRM credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qisbqmwtfzeiffgtlzpk.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo')

HEADERS = {
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Your email address (for determining direction)
YOUR_EMAIL = os.getenv('OUTREACH_EMAIL', '')

# Credentials paths
CREDENTIALS_FILE = os.path.join(EMAIL_CAMPAIGN_PATH, 'credentials', 'credentials.json')
TOKEN_FILE = os.path.join(EMAIL_CAMPAIGN_PATH, 'credentials', 'token.json')

# ============================================================================
# GMAIL AUTHENTICATION
# ============================================================================

def authenticate_gmail():
    """Authenticate with Gmail API using existing credentials"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, GMAIL_SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"Error: {CREDENTIALS_FILE} not found")
                print("Run campaign_manager.py check first to authenticate")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return None

# ============================================================================
# GMAIL MESSAGE FETCHING
# ============================================================================

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

    # Direct body
    if 'body' in payload and payload['body'].get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')

    # Check parts
    parts = payload.get('parts', [])
    for part in parts:
        if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
        # Nested parts
        if 'parts' in part:
            for subpart in part['parts']:
                if subpart.get('mimeType') == 'text/plain' and subpart.get('body', {}).get('data'):
                    return base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8', errors='ignore')

    return ""

def extract_email_address(header_value: str) -> str:
    """Extract email address from 'Name <email>' format"""
    if not header_value:
        return ""
    match = re.search(r'<(.+?)>', header_value)
    if match:
        return match.group(1).lower().strip()
    return header_value.lower().strip()

def fetch_sent_emails(service, days_back: int = 30) -> List[Dict]:
    """Fetch sent emails from Gmail"""
    print(f"\n📤 Fetching sent emails (last {days_back} days)...")

    since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    query = f"in:sent after:{since_date}"

    messages = []
    try:
        results = service.users().messages().list(
            userId='me', q=query, maxResults=500
        ).execute()

        message_ids = results.get('messages', [])
        print(f"   Found {len(message_ids)} sent messages")

        for idx, msg_ref in enumerate(message_ids):
            if idx > 0 and idx % 20 == 0:
                print(f"   Processing {idx}/{len(message_ids)}...")
                time.sleep(0.2)  # Rate limiting

            try:
                msg = service.users().messages().get(
                    userId='me', id=msg_ref['id'], format='full'
                ).execute()
                messages.append(msg)
            except Exception as e:
                continue

    except HttpError as e:
        print(f"Error fetching sent emails: {e}")

    return messages

def fetch_inbox_emails(service, days_back: int = 30) -> List[Dict]:
    """Fetch inbox emails (potential replies)"""
    print(f"\n📥 Fetching inbox emails (last {days_back} days)...")

    since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    query = f"in:inbox after:{since_date}"

    messages = []
    try:
        results = service.users().messages().list(
            userId='me', q=query, maxResults=500
        ).execute()

        message_ids = results.get('messages', [])
        print(f"   Found {len(message_ids)} inbox messages")

        for idx, msg_ref in enumerate(message_ids):
            if idx > 0 and idx % 20 == 0:
                print(f"   Processing {idx}/{len(message_ids)}...")
                time.sleep(0.2)

            try:
                msg = service.users().messages().get(
                    userId='me', id=msg_ref['id'], format='full'
                ).execute()
                messages.append(msg)
            except Exception:
                continue

    except HttpError as e:
        print(f"Error fetching inbox emails: {e}")

    return messages

# ============================================================================
# SUPABASE OPERATIONS
# ============================================================================

def get_existing_message_ids() -> Set[str]:
    """Get set of Gmail message IDs already in database"""
    url = f"{SUPABASE_URL}/rest/v1/email_conversations?select=gmail_message_id"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {row['gmail_message_id'] for row in data if row.get('gmail_message_id')}
    except Exception as e:
        print(f"Warning: Could not fetch existing messages: {e}")
        return set()

def get_prospect_email_map() -> Dict[str, int]:
    """Get mapping of email addresses to prospect IDs"""
    url = f"{SUPABASE_URL}/rest/v1/prospects?select=id,email"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {row['email'].lower(): row['id'] for row in data if row.get('email')}
    except Exception as e:
        print(f"Warning: Could not fetch prospects: {e}")
        return {}

def insert_conversations(conversations: List[Dict]) -> int:
    """Insert conversations into Supabase"""
    if not conversations:
        return 0

    url = f"{SUPABASE_URL}/rest/v1/email_conversations"

    # Insert in batches of 50
    inserted = 0
    batch_size = 50

    for i in range(0, len(conversations), batch_size):
        batch = conversations[i:i+batch_size]
        try:
            response = requests.post(url, headers=HEADERS, json=batch, timeout=30)
            response.raise_for_status()
            inserted += len(batch)
        except Exception as e:
            print(f"   Error inserting batch: {e}")

    return inserted

# ============================================================================
# MESSAGE PROCESSING
# ============================================================================

def process_message(msg: Dict, direction: str, prospect_map: Dict[str, int], your_email: str) -> Optional[Dict]:
    """Process a Gmail message into conversation record"""

    gmail_id = msg.get('id')
    thread_id = msg.get('threadId')

    # Get headers
    subject = get_header(msg, 'Subject') or ''
    from_addr = get_header(msg, 'From') or ''
    to_addr = get_header(msg, 'To') or ''
    date_str = get_header(msg, 'Date') or ''

    # Extract email addresses
    from_email = extract_email_address(from_addr)
    to_email = extract_email_address(to_addr)

    # Determine the other party's email
    if direction == 'outbound':
        other_email = to_email
    else:
        other_email = from_email

    # Skip if no valid email
    if not other_email or '@' not in other_email:
        return None

    # Skip system emails
    skip_domains = ['mailer-daemon', 'postmaster', 'noreply', 'no-reply']
    if any(d in other_email.lower() for d in skip_domains):
        return None

    # Parse date
    try:
        sent_at = parsedate_to_datetime(date_str).isoformat()
    except Exception:
        sent_at = datetime.now().isoformat()

    # Get body preview
    body = get_email_body(msg)
    body_preview = body[:500].strip() if body else ''

    # Look up prospect
    prospect_id = prospect_map.get(other_email.lower())

    # Determine if it's a reply
    is_reply = direction == 'inbound' and 're:' in subject.lower()

    # Check for bounce indicators
    is_bounce = any(ind in body.lower() for ind in ['delivery failed', 'undeliverable', 'bounce'])

    return {
        'prospect_id': prospect_id,
        'email_address': other_email.lower(),
        'gmail_message_id': gmail_id,
        'gmail_thread_id': thread_id,
        'direction': direction,
        'subject': subject[:500] if subject else None,
        'body_preview': body_preview if body_preview else None,
        'sent_at': sent_at,
        'from_email': from_email,
        'to_email': to_email,
        'is_reply': is_reply,
        'is_bounce': is_bounce
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Sync email conversations from Gmail to CRM')
    parser.add_argument('--days', type=int, default=30, help='Days to sync (default: 30)')
    parser.add_argument('--full', action='store_true', help='Full sync (90 days)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    args = parser.parse_args()

    if not GMAIL_AVAILABLE:
        print("Gmail API not available. Cannot proceed.")
        sys.exit(1)

    days = 90 if args.full else args.days

    print("="*60)
    print("EMAIL CONVERSATION SYNC")
    print("="*60)
    print(f"Syncing last {days} days")
    if args.dry_run:
        print("DRY RUN MODE - no changes will be saved")
    print()

    # Authenticate with Gmail
    print("🔑 Authenticating with Gmail...")
    service = authenticate_gmail()
    if not service:
        print("Failed to authenticate with Gmail")
        sys.exit(1)
    print("   ✅ Authenticated")

    # Get existing message IDs (for deduplication)
    print("\n📋 Loading existing data...")
    existing_ids = get_existing_message_ids()
    print(f"   {len(existing_ids)} messages already synced")

    prospect_map = get_prospect_email_map()
    print(f"   {len(prospect_map)} prospects with emails")

    # Fetch emails
    sent_messages = fetch_sent_emails(service, days)
    inbox_messages = fetch_inbox_emails(service, days)

    # Process messages
    print("\n🔄 Processing messages...")
    conversations = []

    your_email = YOUR_EMAIL.lower() if YOUR_EMAIL else ''

    # Process sent emails
    for msg in sent_messages:
        gmail_id = msg.get('id')
        if gmail_id in existing_ids:
            continue

        record = process_message(msg, 'outbound', prospect_map, your_email)
        if record:
            conversations.append(record)

    # Process inbox emails
    for msg in inbox_messages:
        gmail_id = msg.get('id')
        if gmail_id in existing_ids:
            continue

        record = process_message(msg, 'inbound', prospect_map, your_email)
        if record:
            conversations.append(record)

    print(f"   {len(conversations)} new conversations to sync")

    # Count linked vs unlinked
    linked = sum(1 for c in conversations if c.get('prospect_id'))
    unlinked = len(conversations) - linked
    print(f"   {linked} linked to prospects, {unlinked} unlinked")

    # Stats by direction
    outbound = sum(1 for c in conversations if c['direction'] == 'outbound')
    inbound = len(conversations) - outbound
    print(f"   {outbound} outbound, {inbound} inbound")

    if args.dry_run:
        print("\n🧪 Dry run - no changes saved")
        if conversations:
            print("\nSample records:")
            for c in conversations[:5]:
                direction_icon = '→' if c['direction'] == 'outbound' else '←'
                linked_icon = '✓' if c.get('prospect_id') else '✗'
                print(f"   {direction_icon} {c['email_address'][:30]:<30} [{linked_icon}] {c['subject'][:40] if c.get('subject') else '(no subject)'}")
        return

    # Insert into Supabase
    if conversations:
        print("\n💾 Saving to Supabase...")
        inserted = insert_conversations(conversations)
        print(f"   ✅ Inserted {inserted} conversations")
    else:
        print("\n✅ No new conversations to sync")

    print("\n" + "="*60)
    print("SYNC COMPLETE")
    print("="*60)

if __name__ == '__main__':
    main()
