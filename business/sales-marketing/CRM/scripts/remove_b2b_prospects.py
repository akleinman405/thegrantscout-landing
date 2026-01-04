#!/usr/bin/env python3
"""
Remove debarment and food_recall prospects from CRM.
1. Get prospect_ids linked to debarment/food_recall campaign_emails
2. Unlink campaign_emails (set prospect_id = null)
3. Delete the prospects
"""

import requests

# Supabase config
SUPABASE_URL = "https://qisbqmwtfzeiffgtlzpk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}


def get_linked_campaign_emails(vertical):
    """Get campaign emails with prospect_id for a given vertical."""
    emails = []
    offset = 0
    limit = 1000

    while True:
        url = f"{SUPABASE_URL}/rest/v1/campaign_emails?vertical=eq.{vertical}&prospect_id=not.is.null&select=id,prospect_id,email_address&limit={limit}&offset={offset}"
        resp = requests.get(url, headers=HEADERS)
        batch = resp.json()
        if not batch:
            break
        emails.extend(batch)
        offset += limit
        if len(batch) < limit:
            break

    return emails


def unlink_campaign_email(campaign_email_id):
    """Set prospect_id to null for a campaign email."""
    url = f"{SUPABASE_URL}/rest/v1/campaign_emails?id=eq.{campaign_email_id}"
    data = {"prospect_id": None}
    resp = requests.patch(url, headers=HEADERS, json=data)
    return resp.status_code in [200, 204]


def delete_prospect(prospect_id):
    """Delete a prospect by ID."""
    url = f"{SUPABASE_URL}/rest/v1/prospects?id=eq.{prospect_id}"
    resp = requests.delete(url, headers=HEADERS)
    return resp.status_code in [200, 204]


def main():
    print("=" * 60)
    print("Removing Debarment and Food Recall Prospects")
    print("=" * 60)

    # Get all prospect IDs to delete
    prospect_ids = set()

    # Get debarment linked emails
    debarment_emails = get_linked_campaign_emails('debarment')
    print(f"Found {len(debarment_emails)} debarment emails with prospects")
    for e in debarment_emails:
        prospect_ids.add(e['prospect_id'])

    # Get food_recall linked emails
    food_recall_emails = get_linked_campaign_emails('food_recall')
    print(f"Found {len(food_recall_emails)} food_recall emails with prospects")
    for e in food_recall_emails:
        prospect_ids.add(e['prospect_id'])

    print(f"Total unique prospects to delete: {len(prospect_ids)}")

    # Step 1: Unlink campaign emails
    print("\nStep 1: Unlinking campaign emails...")
    unlinked = 0
    all_emails = debarment_emails + food_recall_emails
    for e in all_emails:
        if unlink_campaign_email(e['id']):
            unlinked += 1
        if unlinked % 50 == 0:
            print(f"  Unlinked {unlinked}/{len(all_emails)}")

    print(f"  Unlinked {unlinked} campaign emails")

    # Step 2: Delete prospects
    print("\nStep 2: Deleting prospects...")
    deleted = 0
    for pid in prospect_ids:
        if delete_prospect(pid):
            deleted += 1
        if deleted % 50 == 0:
            print(f"  Deleted {deleted}/{len(prospect_ids)}")

    print(f"  Deleted {deleted} prospects")

    print("=" * 60)
    print("Results:")
    print(f"  Campaign emails unlinked: {unlinked}")
    print(f"  Prospects deleted: {deleted}")
    print("=" * 60)


if __name__ == "__main__":
    main()
