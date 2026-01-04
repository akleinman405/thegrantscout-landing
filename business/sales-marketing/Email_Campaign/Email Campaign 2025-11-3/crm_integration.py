"""
CRM Integration Module for Email Campaign System

Provides bidirectional sync between email campaigns and Supabase CRM:
- Pull prospects from CRM (source of truth)
- Log email sends to CRM
- Update prospect status after sends
- Track replies and bounces

Supabase CRM Tables:
- prospects: Master contact list
- emails: Email send/receive history
- tasks: Follow-up reminders
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pytz

# Import local config
import config

# ============================================================================
# SUPABASE CONFIGURATION
# ============================================================================

# CRM Supabase credentials (same as frontend config.js)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qisbqmwtfzeiffgtlzpk.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo')

# API headers
HEADERS = {
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ============================================================================
# API HELPER FUNCTIONS
# ============================================================================

def _api_request(endpoint: str, method: str = 'GET', data: dict = None) -> dict:
    """
    Make a request to Supabase REST API.

    Args:
        endpoint: API endpoint (e.g., 'prospects?status=eq.not_contacted')
        method: HTTP method (GET, POST, PATCH, DELETE)
        data: JSON data for POST/PATCH

    Returns:
        JSON response from API
    """
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"

    try:
        if method == 'GET':
            response = requests.get(url, headers=HEADERS, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=HEADERS, json=data, timeout=30)
        elif method == 'PATCH':
            response = requests.patch(url, headers=HEADERS, json=data, timeout=30)
        elif method == 'DELETE':
            response = requests.delete(url, headers=HEADERS, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()

        # Handle empty responses
        if response.text:
            return response.json()
        return None

    except requests.exceptions.RequestException as e:
        print(f"⚠️  CRM API error: {e}")
        return None


# ============================================================================
# PROSPECT FUNCTIONS (CRM → Email Campaign)
# ============================================================================

def get_email_prospects(
    segment: str = 'nonprofit',
    status: str = None,
    limit: int = 500,
    exclude_recently_emailed_days: int = 7
) -> List[Dict]:
    """
    Get prospects from CRM for email campaigns.

    Args:
        segment: Filter by segment ('nonprofit', 'foundation', 'foundation_mgmt', or None for all)
        status: Filter by status ('not_contacted', 'contacted', 'interested', etc.)
        limit: Max records to return
        exclude_recently_emailed_days: Skip prospects emailed within N days

    Returns:
        List of prospect dicts with email, org_name, contact_name, etc.
    """
    # Build query - filter for valid emails (contains @)
    query = f"prospects?select=id,org_name,email,contact_name,website,state,status,segment"
    query += f"&email=ilike.*@*"  # Must have @ in email (valid email format)
    query += f"&limit={limit}"
    query += "&order=icp_score.desc.nullslast,org_name"

    if segment:
        query += f"&segment=eq.{segment}"
    if status:
        query += f"&status=eq.{status}"

    prospects = _api_request(query)

    if not prospects:
        return []

    # Filter out recently emailed if requested
    if exclude_recently_emailed_days > 0:
        prospects = _filter_recently_emailed(prospects, exclude_recently_emailed_days)

    return prospects


def _filter_recently_emailed(prospects: List[Dict], days: int) -> List[Dict]:
    """Filter out prospects who received email within N days."""
    cutoff = (datetime.now(pytz.UTC) - timedelta(days=days)).isoformat()

    # Get recent email recipients from CRM
    recent_query = f"emails?sent_date=gte.{cutoff}&direction=eq.outbound&select=prospect_id"
    recent_emails = _api_request(recent_query)

    if not recent_emails:
        return prospects

    recently_emailed_ids = {e['prospect_id'] for e in recent_emails}

    return [p for p in prospects if p['id'] not in recently_emailed_ids]


def get_followup_candidates(days_since_initial: int = 3, days_max: int = 14) -> List[Dict]:
    """
    Get prospects eligible for follow-up email.

    Criteria:
    - Received initial email 3-14 days ago
    - Haven't received follow-up yet
    - Haven't replied

    Args:
        days_since_initial: Min days since initial email
        days_max: Max days since initial email

    Returns:
        List of prospects ready for follow-up
    """
    now = datetime.now(pytz.UTC)
    min_date = (now - timedelta(days=days_max)).isoformat()
    max_date = (now - timedelta(days=days_since_initial)).isoformat()

    # Get prospects who received initial outreach in the window
    query = f"emails?sent_date=gte.{min_date}&sent_date=lte.{max_date}"
    query += "&direction=eq.outbound&select=prospect_id,sent_date,subject"

    initial_emails = _api_request(query)

    if not initial_emails:
        return []

    # Get prospect IDs who already got follow-up
    followup_query = f"emails?direction=eq.outbound&subject=ilike.*follow*&select=prospect_id"
    followup_emails = _api_request(followup_query) or []
    followup_ids = {e['prospect_id'] for e in followup_emails}

    # Get prospect IDs who replied
    reply_query = f"emails?direction=eq.inbound&select=prospect_id"
    replies = _api_request(reply_query) or []
    replied_ids = {e['prospect_id'] for e in replies}

    # Filter to eligible prospects
    eligible_ids = []
    for email in initial_emails:
        pid = email['prospect_id']
        if pid not in followup_ids and pid not in replied_ids:
            eligible_ids.append(pid)

    if not eligible_ids:
        return []

    # Get full prospect details
    # Supabase doesn't support IN clause easily, so we'll batch
    prospects = []
    for pid in eligible_ids[:100]:  # Limit to 100
        p = _api_request(f"prospects?id=eq.{pid}")
        if p:
            prospects.extend(p)

    return prospects


def lookup_prospect_by_email(email: str) -> Optional[Dict]:
    """
    Find prospect in CRM by email address.

    Args:
        email: Email address to search

    Returns:
        Prospect dict or None if not found
    """
    # Case-insensitive search
    query = f"prospects?email=ilike.{email.lower()}"
    results = _api_request(query)

    if results and len(results) > 0:
        return results[0]
    return None


# ============================================================================
# EMAIL LOGGING FUNCTIONS (Email Campaign → CRM)
# ============================================================================

def log_email_sent(
    prospect_id: int,
    subject: str,
    body_preview: str = None,
    direction: str = 'outbound',
    email_type: str = 'initial'
) -> bool:
    """
    Log an email send to the CRM.

    Args:
        prospect_id: CRM prospect ID
        subject: Email subject line
        body_preview: First ~200 chars of email body
        direction: 'outbound' or 'inbound'
        email_type: 'initial' or 'followup'

    Returns:
        True if logged successfully
    """
    data = {
        'prospect_id': prospect_id,
        'sent_date': datetime.now(pytz.UTC).isoformat(),
        'direction': direction,
        'subject': subject,
        'body_preview': body_preview[:500] if body_preview else None,
        'notes': f"Automated {email_type} via email campaign"
    }

    result = _api_request('emails', method='POST', data=data)
    return result is not None


def log_email_by_address(
    email_address: str,
    subject: str,
    body_preview: str = None,
    email_type: str = 'initial',
    create_if_missing: bool = False
) -> Tuple[bool, Optional[int]]:
    """
    Log email send by looking up prospect by email address.

    Args:
        email_address: Recipient email
        subject: Email subject
        body_preview: Email body preview
        email_type: 'initial' or 'followup'
        create_if_missing: If True, create prospect if not found

    Returns:
        (success, prospect_id) tuple
    """
    # Look up prospect
    prospect = lookup_prospect_by_email(email_address)

    if not prospect:
        if create_if_missing:
            # Create minimal prospect record
            new_prospect = {
                'email': email_address.lower(),
                'org_name': email_address.split('@')[1].split('.')[0].title(),
                'segment': 'nonprofit',
                'status': 'contacted'
            }
            result = _api_request('prospects', method='POST', data=new_prospect)
            if result and len(result) > 0:
                prospect = result[0]
            else:
                return False, None
        else:
            # Prospect not in CRM, skip logging
            return False, None

    # Log the email
    success = log_email_sent(
        prospect_id=prospect['id'],
        subject=subject,
        body_preview=body_preview,
        email_type=email_type
    )

    return success, prospect['id']


def log_email_reply(
    prospect_id: int,
    subject: str,
    body_preview: str = None,
    reply_date: datetime = None
) -> bool:
    """
    Log an inbound reply from prospect.

    Args:
        prospect_id: CRM prospect ID
        subject: Reply subject
        body_preview: Reply body preview
        reply_date: When reply was received

    Returns:
        True if logged successfully
    """
    data = {
        'prospect_id': prospect_id,
        'sent_date': (reply_date or datetime.now(pytz.UTC)).isoformat(),
        'direction': 'inbound',
        'subject': subject,
        'body_preview': body_preview[:500] if body_preview else None
    }

    result = _api_request('emails', method='POST', data=data)

    if result:
        # Also update prospect status to 'interested'
        update_prospect_status(prospect_id, 'interested')

    return result is not None


def log_bounce(
    prospect_id: int,
    bounce_reason: str = None
) -> bool:
    """
    Log an email bounce.

    Args:
        prospect_id: CRM prospect ID
        bounce_reason: Why it bounced

    Returns:
        True if logged successfully
    """
    data = {
        'prospect_id': prospect_id,
        'sent_date': datetime.now(pytz.UTC).isoformat(),
        'direction': 'outbound',
        'subject': 'BOUNCED',
        'notes': bounce_reason or 'Email bounced'
    }

    result = _api_request('emails', method='POST', data=data)
    return result is not None


# ============================================================================
# PROSPECT STATUS FUNCTIONS
# ============================================================================

def update_prospect_status(prospect_id: int, status: str) -> bool:
    """
    Update prospect status in CRM.

    Valid statuses: not_contacted, contacted, interested, not_interested, converted

    Args:
        prospect_id: CRM prospect ID
        status: New status

    Returns:
        True if updated successfully
    """
    valid_statuses = ['not_contacted', 'contacted', 'interested', 'not_interested', 'converted']
    if status not in valid_statuses:
        print(f"⚠️  Invalid status: {status}")
        return False

    data = {
        'status': status,
        'last_contacted_at': datetime.now(pytz.UTC).isoformat()
    }

    result = _api_request(f'prospects?id=eq.{prospect_id}', method='PATCH', data=data)
    return result is not None


def mark_prospect_contacted(email_address: str) -> bool:
    """
    Mark prospect as contacted by email address.

    Args:
        email_address: Prospect's email

    Returns:
        True if updated successfully
    """
    prospect = lookup_prospect_by_email(email_address)
    if not prospect:
        return False

    # Only update if not already past 'contacted' stage
    if prospect.get('status') == 'not_contacted':
        return update_prospect_status(prospect['id'], 'contacted')
    return True


# ============================================================================
# SYNC FUNCTIONS
# ============================================================================

def sync_sent_tracker_to_crm(tracker_path: str = None, since_date: str = None) -> Dict:
    """
    Sync sent_tracker.csv to CRM emails table.

    Args:
        tracker_path: Path to sent_tracker.csv (defaults to config)
        since_date: Only sync emails after this date (YYYY-MM-DD)

    Returns:
        Dict with sync stats
    """
    import pandas as pd

    tracker_path = tracker_path or config.SENT_TRACKER

    if not os.path.exists(tracker_path):
        return {'error': 'Tracker file not found', 'synced': 0}

    df = pd.read_csv(tracker_path)

    # Filter to successful sends
    df = df[df['status'] == 'SUCCESS']

    # Filter by date if specified
    if since_date:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[df['timestamp'] >= since_date]

    stats = {
        'total': len(df),
        'synced': 0,
        'skipped': 0,
        'errors': 0
    }

    for _, row in df.iterrows():
        email_type = row.get('message_type', 'initial')
        subject = row.get('subject_line', 'Outreach')

        success, _ = log_email_by_address(
            email_address=row['email'],
            subject=subject,
            email_type=email_type,
            create_if_missing=False  # Don't create prospects, just log if exists
        )

        if success:
            stats['synced'] += 1
        else:
            stats['skipped'] += 1

    return stats


def export_crm_prospects_to_csv(
    output_path: str,
    segment: str = 'nonprofit',
    status: str = 'not_contacted'
) -> int:
    """
    Export CRM prospects to CSV for email campaign.

    Args:
        output_path: Where to save CSV
        segment: Filter by segment
        status: Filter by status

    Returns:
        Number of prospects exported
    """
    import pandas as pd

    prospects = get_email_prospects(segment=segment, status=status)

    if not prospects:
        return 0

    # Convert to DataFrame with columns matching email campaign format
    df = pd.DataFrame(prospects)

    # Rename columns to match expected format
    column_map = {
        'org_name': 'org_name',
        'email': 'email',
        'contact_name': 'first_name',
        'website': 'website',
        'state': 'address_state'
    }

    df = df.rename(columns=column_map)

    # Extract first name from contact_name if available
    if 'first_name' in df.columns:
        df['first_name'] = df['first_name'].apply(
            lambda x: x.split()[0] if pd.notna(x) and x else ''
        )

    # Select only needed columns
    output_cols = ['org_name', 'email', 'first_name', 'website', 'address_state']
    df = df[[c for c in output_cols if c in df.columns]]

    df.to_csv(output_path, index=False)

    return len(df)


# ============================================================================
# TASK CREATION (for follow-up reminders)
# ============================================================================

def create_followup_task(
    prospect_id: int,
    days_from_now: int = 3,
    description: str = "Email follow-up"
) -> bool:
    """
    Create a follow-up task for a prospect.

    Args:
        prospect_id: CRM prospect ID
        days_from_now: When to follow up
        description: Task description

    Returns:
        True if created successfully
    """
    due_date = (datetime.now() + timedelta(days=days_from_now)).strftime('%Y-%m-%d')

    data = {
        'prospect_id': prospect_id,
        'due_date': due_date,
        'type': 'email',
        'description': description,
        'completed': False
    }

    result = _api_request('tasks', method='POST', data=data)
    return result is not None


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_crm_status():
    """Display current CRM connection status and stats."""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  CRM INTEGRATION STATUS                                    ║")
    print("╠════════════════════════════════════════════════════════════╣")

    # Test connection
    try:
        test = _api_request('prospects?limit=1')
        if test is not None:
            print("║  Connection:          ✅ Connected                         ║")
        else:
            print("║  Connection:          ❌ Failed                             ║")
            print("╚════════════════════════════════════════════════════════════╝\n")
            return
    except Exception as e:
        print(f"║  Connection:          ❌ Error: {str(e)[:30]:<30} ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        return

    # Get counts
    nonprofits = _api_request('prospects?segment=eq.nonprofit&select=count')
    not_contacted = _api_request('prospects?status=eq.not_contacted&segment=eq.nonprofit&select=count')
    emails_logged = _api_request('emails?direction=eq.outbound&select=count')

    # Parse counts (Supabase returns [{"count": N}])
    np_count = nonprofits[0].get('count', 0) if nonprofits else 0
    nc_count = not_contacted[0].get('count', 0) if not_contacted else 0
    em_count = emails_logged[0].get('count', 0) if emails_logged else 0

    print(f"║  Nonprofit Prospects: {np_count:<36} ║")
    print(f"║  Not Contacted:       {nc_count:<36} ║")
    print(f"║  Emails Logged:       {em_count:<36} ║")
    print("╚════════════════════════════════════════════════════════════╝\n")


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == '__main__':
    print("Testing CRM Integration...")
    display_crm_status()

    # Test prospect lookup
    print("\nTesting prospect lookup...")
    prospects = get_email_prospects(limit=5)
    if prospects:
        print(f"Found {len(prospects)} prospects")
        for p in prospects[:3]:
            print(f"  - {p.get('org_name', 'Unknown')}: {p.get('email', 'no email')}")
    else:
        print("No prospects found or connection failed")
