#!/usr/bin/env python3
"""
Match campaign_emails to prospects by email address.
Import missing prospects from campaign source files.
"""

import csv
import json
import requests
from collections import defaultdict

# Supabase config
SUPABASE_URL = "https://qisbqmwtfzeiffgtlzpk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Source files
GRANT_ALERTS_FILE = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/Email_Campaign/grant_alerts_prospects.csv"
DEBARMENT_FILE = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/Archive/Old_Campaigns/debarment_prospects.csv"
FOOD_RECALL_FILE = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/Archive/Old_Campaigns/food_recall_prospects.csv"


def get_all_prospects_with_email():
    """Get all prospects that have email addresses."""
    prospects = []
    offset = 0
    limit = 1000

    while True:
        url = f"{SUPABASE_URL}/rest/v1/prospects?email=not.is.null&select=id,email,org_name&limit={limit}&offset={offset}"
        resp = requests.get(url, headers=HEADERS)
        batch = resp.json()
        if not batch:
            break
        prospects.extend(batch)
        offset += limit
        if len(batch) < limit:
            break

    # Create email -> prospect_id lookup (lowercase)
    email_to_prospect = {}
    for p in prospects:
        if p.get('email'):
            email_to_prospect[p['email'].lower().strip()] = p['id']

    print(f"Loaded {len(prospects)} prospects with emails")
    return email_to_prospect


def get_unmatched_campaign_emails():
    """Get campaign emails without prospect_id."""
    emails = []
    offset = 0
    limit = 1000

    while True:
        url = f"{SUPABASE_URL}/rest/v1/campaign_emails?prospect_id=is.null&select=id,email_address,vertical&limit={limit}&offset={offset}"
        resp = requests.get(url, headers=HEADERS)
        batch = resp.json()
        if not batch:
            break
        emails.extend(batch)
        offset += limit
        if len(batch) < limit:
            break

    print(f"Found {len(emails)} unmatched campaign emails")
    return emails


def update_campaign_email_prospect(campaign_email_id, prospect_id):
    """Update campaign_email with prospect_id."""
    url = f"{SUPABASE_URL}/rest/v1/campaign_emails?id=eq.{campaign_email_id}"
    data = {"prospect_id": prospect_id}
    resp = requests.patch(url, headers=HEADERS, json=data)
    return resp.status_code == 200


def load_source_prospects():
    """Load prospect data from source CSV files."""
    source_prospects = {}  # email -> {org_name, state, website, segment, first_name}

    # Grant Alerts (nonprofits)
    try:
        with open(GRANT_ALERTS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('email', '').lower().strip()
                if email:
                    source_prospects[email] = {
                        'org_name': row.get('org_name', ''),
                        'state': row.get('address_state', ''),
                        'website': row.get('website', ''),
                        'segment': 'nonprofit',
                        'contact_name': row.get('first_name', '')
                    }
        print(f"Loaded {len(source_prospects)} from grant_alerts")
    except Exception as e:
        print(f"Error loading grant_alerts: {e}")

    # Debarment (B2B - government contractors)
    try:
        with open(DEBARMENT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                email = row.get('email', '').lower().strip()
                if email and email not in source_prospects:
                    source_prospects[email] = {
                        'org_name': row.get('company_name', ''),
                        'state': row.get('state', ''),
                        'website': row.get('website', ''),
                        'segment': 'foundation_mgmt',  # Using as B2B segment
                        'contact_name': row.get('first_name', '')
                    }
                    count += 1
        print(f"Added {count} from debarment")
    except Exception as e:
        print(f"Error loading debarment: {e}")

    # Food Recall (B2B - restaurants)
    try:
        with open(FOOD_RECALL_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                email = row.get('email', '').lower().strip()
                if email and email not in source_prospects:
                    source_prospects[email] = {
                        'org_name': row.get('company', ''),
                        'state': row.get('state', ''),
                        'website': row.get('website', ''),
                        'segment': 'foundation',  # Using as B2B segment
                        'contact_name': row.get('first_name', '')
                    }
                    count += 1
        print(f"Added {count} from food_recall")
    except Exception as e:
        print(f"Error loading food_recall: {e}")

    print(f"Total source prospects: {len(source_prospects)}")
    return source_prospects


def create_prospect(data):
    """Create a new prospect in the database."""
    url = f"{SUPABASE_URL}/rest/v1/prospects"
    prospect_data = {
        'org_name': data.get('org_name', '')[:255] if data.get('org_name') else '',
        'email': data.get('email', ''),
        'state': data.get('state', '')[:2] if data.get('state') else None,
        'website': data.get('website', '')[:500] if data.get('website') else None,
        'segment': data.get('segment', 'nonprofit'),
        'contact_name': data.get('contact_name', '')[:255] if data.get('contact_name') else None,
        'status': 'contacted'  # They've been emailed
    }

    resp = requests.post(url, headers=HEADERS, json=prospect_data)
    if resp.status_code in [200, 201]:
        result = resp.json()
        if result:
            return result[0].get('id')
    else:
        print(f"Failed to create prospect: {resp.status_code} - {resp.text[:100]}")
    return None


def main():
    print("=" * 60)
    print("Campaign Email to Prospect Matching")
    print("=" * 60)

    # Step 1: Get existing prospect emails
    email_to_prospect = get_all_prospects_with_email()

    # Step 2: Get unmatched campaign emails
    unmatched = get_unmatched_campaign_emails()

    # Step 3: Load source prospect data
    source_prospects = load_source_prospects()

    # Step 4: Match and update
    matched_count = 0
    created_count = 0
    failed_count = 0

    for ce in unmatched:
        email = ce['email_address'].lower().strip()
        campaign_email_id = ce['id']

        # Try to match existing prospect
        if email in email_to_prospect:
            prospect_id = email_to_prospect[email]
            if update_campaign_email_prospect(campaign_email_id, prospect_id):
                matched_count += 1
            else:
                failed_count += 1

        # Not in DB, but in source files - create new prospect
        elif email in source_prospects:
            source_data = source_prospects[email]
            source_data['email'] = email

            prospect_id = create_prospect(source_data)
            if prospect_id:
                if update_campaign_email_prospect(campaign_email_id, prospect_id):
                    created_count += 1
                    email_to_prospect[email] = prospect_id  # Add to lookup
                else:
                    failed_count += 1
            else:
                failed_count += 1

        # Progress update every 100
        total = matched_count + created_count + failed_count
        if total % 100 == 0 and total > 0:
            print(f"Progress: {total}/{len(unmatched)} (matched: {matched_count}, created: {created_count})")

    print("=" * 60)
    print("Results:")
    print(f"  Matched to existing prospects: {matched_count}")
    print(f"  Created new prospects: {created_count}")
    print(f"  Failed/Unmatched: {failed_count}")
    print(f"  Remaining unmatched: {len(unmatched) - matched_count - created_count - failed_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
