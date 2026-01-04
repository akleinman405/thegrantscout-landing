#!/usr/bin/env python3
"""
Import contact history from Beta Test Group Calls Excel file into CRM.
Maps Excel contacts to CRM prospects and creates call records.
"""

import pandas as pd
import requests
import warnings
from datetime import datetime
import re

warnings.filterwarnings('ignore')

# Supabase config
SUPABASE_URL = 'https://qisbqmwtfzeiffgtlzpk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo'

EXCEL_PATH = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/Archive/Call_Tracking/Beta Test Group Calls.xlsx'

def get_headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }

def load_excel_contacts():
    """Load and parse the Beta Group sheet from Excel"""
    df = pd.read_excel(EXCEL_PATH, sheet_name='Beta Group', header=None)

    # Find the header row (row with 'Company')
    header_row = None
    for i, row in df.iterrows():
        if 'Company' in str(row.values):
            header_row = i
            break

    if header_row is None:
        # Try alternative parsing
        print("Looking for data structure...")
        print(df.head(10).to_string())
        return []

    # Set proper headers
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]

    contacts = []
    for _, row in df.iterrows():
        company = str(row.get('Company', '')).strip()
        if not company or company == 'nan' or company == 'NaN':
            continue

        contact = {
            'company': company,
            'contact_name': str(row.get('Contact Name', '')).strip() if pd.notna(row.get('Contact Name')) else None,
            'state': str(row.get('State', '')).strip() if pd.notna(row.get('State')) else None,
            'phone': str(row.get('Phone Number', '')).strip() if pd.notna(row.get('Phone Number')) else None,
            'email': str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else None,
            'contact_date': row.get('Contact Date'),
            'notes': str(row.get('Notes', '')).strip() if pd.notna(row.get('Notes')) else None,
            'status': str(row.get('Status', '')).strip() if pd.notna(row.get('Status')) else None,
            'contact_method': str(row.get('Contact Method', '')).strip() if pd.notna(row.get('Contact Method')) else None,
        }
        contacts.append(contact)

    return contacts

def load_nonprofits_sheet():
    """Load the Nonprofits sheet which has more detailed call tracking"""
    df = pd.read_excel(EXCEL_PATH, sheet_name='Nonprofits', header=None)

    # Find header row
    header_row = None
    for i, row in df.iterrows():
        row_str = ' '.join(str(v) for v in row.values)
        if 'Organization_Name' in row_str or 'Contact Date' in row_str:
            header_row = i
            break

    if header_row is None:
        return []

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)
    df.columns = [str(c).strip() for c in df.columns]

    contacts = []
    for _, row in df.iterrows():
        org_name = row.get('Organization_Name')
        if pd.isna(org_name):
            continue

        # Parse outcome columns
        vm = row.get('VM/Message', 0)
        talked = row.get('Talked to Someone', 0)
        email_sent = row.get('Send us an Email', 0)
        reached_dm = row.get('Reached Decision Maker', 0)

        # Determine outcome
        outcome = 'no_answer'
        if reached_dm == 1:
            outcome = 'reached_decision_maker'
        elif talked == 1:
            outcome = 'talked_to_someone'
        elif email_sent == 1:
            outcome = 'sent_email_request'
        elif vm == 1:
            outcome = 'vm_left'

        contact = {
            'company': str(org_name).strip(),
            'contact_name': str(row.get('Decision Maker', '')).strip() if pd.notna(row.get('Decision Maker')) else None,
            'state': str(row.get('State', '')).strip() if pd.notna(row.get('State')) else None,
            'phone': str(row.get('Phone', '')).strip() if pd.notna(row.get('Phone')) else None,
            'contact_date': row.get('Contact Date'),
            'notes': str(row.get('Notes', '')).strip() if pd.notna(row.get('Notes')) else None,
            'outcome': outcome,
            'interest': str(row.get('Yes/No/Maybe/Uncertain', '')).strip().lower() if pd.notna(row.get('Yes/No/Maybe/Uncertain')) else None,
        }

        # Only include if there's a contact date (meaning they were contacted)
        if pd.notna(contact['contact_date']):
            contacts.append(contact)

    return contacts

def get_crm_prospects():
    """Get all prospects from CRM for matching"""
    headers = get_headers()
    prospects = []
    offset = 0

    while True:
        r = requests.get(
            f'{SUPABASE_URL}/rest/v1/prospects?select=id,org_name,ein,phone,state&offset={offset}&limit=1000',
            headers=headers
        )
        if r.status_code != 200:
            print(f"Error fetching prospects: {r.text}")
            break

        batch = r.json()
        if not batch:
            break
        prospects.extend(batch)
        offset += 1000
        if len(batch) < 1000:
            break

    return prospects

def normalize_name(name):
    """Normalize organization name for matching"""
    if not name:
        return ''
    name = name.lower().strip()
    # Remove common suffixes
    for suffix in [' inc', ' inc.', ' llc', ' corp', ' corporation', ' foundation', ' fdn', ' co', ' company']:
        name = name.replace(suffix, '')
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    return name.strip()

def match_prospect(contact, prospects):
    """Find matching CRM prospect for an Excel contact"""
    contact_name = normalize_name(contact['company'])

    # Try exact match first
    for p in prospects:
        if normalize_name(p['org_name']) == contact_name:
            return p

    # Try partial match
    for p in prospects:
        p_name = normalize_name(p['org_name'])
        if contact_name in p_name or p_name in contact_name:
            return p

    # Try state + partial name
    if contact.get('state'):
        for p in prospects:
            if p.get('state') == contact['state']:
                p_name = normalize_name(p['org_name'])
                # Check for significant word overlap
                contact_words = set(contact_name.split())
                p_words = set(p_name.split())
                if len(contact_words & p_words) >= 2:
                    return p

    return None

def create_call_record(prospect_id, contact):
    """Create a call record in the CRM"""
    headers = get_headers()

    # Parse contact date
    call_date = None
    if contact.get('contact_date'):
        try:
            if isinstance(contact['contact_date'], str):
                call_date = contact['contact_date']
            else:
                call_date = contact['contact_date'].isoformat()
        except:
            call_date = datetime.now().isoformat()
    else:
        call_date = datetime.now().isoformat()

    # Determine outcome
    outcome = contact.get('outcome', 'talked_to_someone')
    if not outcome or outcome == 'nan':
        # Infer from notes
        notes = (contact.get('notes') or '').lower()
        if 'vm' in notes or 'voicemail' in notes or 'left message' in notes:
            outcome = 'vm_left'
        elif 'talked' in notes or 'spoke' in notes:
            outcome = 'talked_to_someone'
        elif 'email' in notes:
            outcome = 'sent_email_request'
        else:
            outcome = 'talked_to_someone'

    # Map interest
    interest = contact.get('interest')
    if interest:
        interest_map = {'yes': 'yes', 'no': 'no', 'maybe': 'maybe', 'uncertain': 'uncertain'}
        interest = interest_map.get(interest.lower(), 'uncertain')

    call_data = {
        'prospect_id': prospect_id,
        'call_date': call_date,
        'outcome': outcome,
        'interest': interest,
        'notes': contact.get('notes'),
    }

    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/calls',
        headers=headers,
        json=call_data
    )

    return r.status_code in (200, 201)

def update_prospect_status(prospect_id, status='contacted'):
    """Update prospect status"""
    headers = get_headers()

    r = requests.patch(
        f'{SUPABASE_URL}/rest/v1/prospects?id=eq.{prospect_id}',
        headers=headers,
        json={'status': status}
    )

    return r.status_code in (200, 204)

def main():
    print("=== IMPORTING EXCEL CONTACT HISTORY ===\n")

    # Load Excel data
    print("Loading Beta Group contacts...")
    beta_contacts = load_excel_contacts()
    print(f"  Found {len(beta_contacts)} Beta Group contacts")

    print("Loading Nonprofits sheet contacts...")
    nonprofit_contacts = load_nonprofits_sheet()
    print(f"  Found {len(nonprofit_contacts)} Nonprofit contacts with dates")

    # Combine and dedupe
    all_contacts = beta_contacts + nonprofit_contacts
    print(f"\nTotal contacts to process: {len(all_contacts)}")

    # Get CRM prospects
    print("\nLoading CRM prospects for matching...")
    prospects = get_crm_prospects()
    print(f"  Found {len(prospects)} prospects in CRM")

    # Match and import
    print("\nMatching and importing contacts...")
    matched = 0
    unmatched = []
    calls_created = 0
    statuses_updated = 0

    for contact in all_contacts:
        prospect = match_prospect(contact, prospects)

        if prospect:
            matched += 1

            # Create call record
            if create_call_record(prospect['id'], contact):
                calls_created += 1

            # Update status to contacted
            if update_prospect_status(prospect['id'], 'contacted'):
                statuses_updated += 1
        else:
            unmatched.append(contact['company'])

    print(f"\n=== IMPORT COMPLETE ===")
    print(f"  Matched: {matched}")
    print(f"  Calls created: {calls_created}")
    print(f"  Statuses updated: {statuses_updated}")
    print(f"  Unmatched: {len(unmatched)}")

    if unmatched:
        print(f"\nUnmatched organizations (may need manual import):")
        for org in unmatched[:20]:
            print(f"  - {org}")
        if len(unmatched) > 20:
            print(f"  ... and {len(unmatched) - 20} more")

if __name__ == '__main__':
    main()
