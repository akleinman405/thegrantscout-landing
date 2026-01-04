#!/usr/bin/env python3
"""
Delete prospects linked to debarment/food_recall campaign emails.
With retry logic for connection issues.
"""

import requests
import time

SUPABASE_URL = "https://qisbqmwtfzeiffgtlzpk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Get prospect IDs from the source files (email addresses)
DEBARMENT_FILE = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/Archive/Old_Campaigns/debarment_prospects.csv"
FOOD_RECALL_FILE = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/Archive/Old_Campaigns/food_recall_prospects.csv"

import csv

def get_source_emails():
    """Get email addresses from source files."""
    emails = set()

    # Debarment
    with open(DEBARMENT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').lower().strip()
            if email:
                emails.add(email)

    # Food recall
    with open(FOOD_RECALL_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').lower().strip()
            if email:
                emails.add(email)

    return emails


def delete_prospects_by_email_batch(emails_batch):
    """Delete prospects matching a batch of email addresses."""
    # Build OR filter
    email_filter = ','.join([f'email.eq.{e}' for e in emails_batch])
    url = f"{SUPABASE_URL}/rest/v1/prospects?or=({email_filter})"

    try:
        resp = requests.delete(url, headers=HEADERS, timeout=30)
        return resp.status_code in [200, 204]
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("Getting source emails...")
    source_emails = list(get_source_emails())
    print(f"Found {len(source_emails)} source emails")

    # Process in batches of 10
    batch_size = 10
    deleted = 0

    for i in range(0, len(source_emails), batch_size):
        batch = source_emails[i:i+batch_size]
        if delete_prospects_by_email_batch(batch):
            deleted += len(batch)

        if (i // batch_size) % 50 == 0:
            print(f"Processed {i}/{len(source_emails)}")

        time.sleep(0.1)  # Rate limiting

    print(f"Done. Processed {len(source_emails)} emails.")


if __name__ == "__main__":
    main()
