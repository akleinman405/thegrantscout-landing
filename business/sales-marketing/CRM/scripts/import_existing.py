#!/usr/bin/env python3
"""
Import existing prospect data into the CRM.

Usage:
    python3 import_existing.py --file "prospects.csv" --source-name "Dec 2025 List" --segment nonprofit
    python3 import_existing.py --file "calls.xlsx" --type calls
    python3 import_existing.py --list-sources

Requirements:
    pip3 install supabase pandas openpyxl
"""

import argparse
import os
import sys
from datetime import datetime
import pandas as pd

# Supabase credentials - set these or use environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL', 'YOUR_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'YOUR_SERVICE_ROLE_KEY')

try:
    from supabase import create_client, Client
except ImportError:
    print("Please install supabase: pip3 install supabase")
    sys.exit(1)


def get_client() -> Client:
    """Create Supabase client."""
    if 'YOUR_' in SUPABASE_URL or 'YOUR_' in SUPABASE_KEY:
        print("Error: Please set SUPABASE_URL and SUPABASE_KEY environment variables")
        print("  export SUPABASE_URL='https://your-project.supabase.co'")
        print("  export SUPABASE_KEY='your-service-role-key'")
        sys.exit(1)
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def import_prospects(file_path: str, source_name: str, segment: str, criteria: str = None):
    """Import prospects from CSV file."""
    print(f"Importing prospects from: {file_path}")

    # Read file
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)

    print(f"Found {len(df)} rows")

    # Column mapping - try to auto-detect
    column_map = {}
    for col in df.columns:
        col_lower = col.lower().replace(' ', '_').replace('-', '_')
        if 'org' in col_lower and 'name' in col_lower:
            column_map['org_name'] = col
        elif col_lower == 'name' or col_lower == 'company':
            column_map['org_name'] = col
        elif col_lower == 'ein':
            column_map['ein'] = col
        elif 'phone' in col_lower:
            column_map['phone'] = col
        elif 'email' in col_lower:
            column_map['email'] = col
        elif 'website' in col_lower or col_lower == 'url':
            column_map['website'] = col
        elif col_lower == 'contact' or 'contact_name' in col_lower:
            column_map['contact_name'] = col
        elif 'title' in col_lower:
            column_map['contact_title'] = col
        elif 'city' in col_lower:
            column_map['city'] = col
        elif col_lower == 'state':
            column_map['state'] = col
        elif 'ntee' in col_lower:
            column_map['ntee_code'] = col
        elif 'budget' in col_lower or 'revenue' in col_lower:
            column_map['annual_budget'] = col
        elif 'icp' in col_lower or col_lower == 'score':
            column_map['icp_score'] = col
        elif 'tier' in col_lower:
            column_map['tier'] = col
        elif 'linkedin' in col_lower:
            column_map['linkedin_url'] = col
        elif 'note' in col_lower:
            column_map['notes'] = col

    print(f"Column mapping: {column_map}")

    if 'org_name' not in column_map:
        print("Error: Could not find organization name column")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)

    # Connect to Supabase
    supabase = get_client()

    # Create source list
    source_data = {
        'name': source_name,
        'criteria': criteria,
        'file_origin': os.path.basename(file_path),
        'record_count': len(df),
        'segment': segment
    }
    result = supabase.table('source_lists').insert(source_data).execute()
    source_list_id = result.data[0]['id']
    print(f"Created source list: {source_name} (ID: {source_list_id})")

    # Prepare prospects
    prospects = []
    for _, row in df.iterrows():
        prospect = {
            'segment': segment,
            'status': 'not_contacted',
            'source_list_id': source_list_id
        }

        for crm_field, csv_col in column_map.items():
            value = row.get(csv_col)
            if pd.notna(value):
                # Clean up value
                if isinstance(value, str):
                    value = value.strip()
                    if value.lower() in ('n/a', 'none', 'null', ''):
                        continue

                # Type conversions
                if crm_field in ('tier', 'icp_score'):
                    try:
                        value = int(float(value))
                    except (ValueError, TypeError):
                        continue
                elif crm_field == 'annual_budget':
                    try:
                        value = int(float(str(value).replace('$', '').replace(',', '')))
                    except (ValueError, TypeError):
                        continue

                prospect[crm_field] = value

        if prospect.get('org_name'):
            prospects.append(prospect)

    print(f"Prepared {len(prospects)} valid prospects")

    # Batch insert (Supabase handles up to 1000 at a time)
    batch_size = 500
    inserted = 0
    for i in range(0, len(prospects), batch_size):
        batch = prospects[i:i + batch_size]
        result = supabase.table('prospects').insert(batch).execute()
        inserted += len(result.data)
        print(f"Inserted {inserted}/{len(prospects)} prospects...")

    print(f"Done! Imported {inserted} prospects.")
    return inserted


def import_calls(file_path: str, sheet_name: str = None):
    """Import call history from Excel file."""
    print(f"Importing calls from: {file_path}")

    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    else:
        df = pd.read_csv(file_path)

    print(f"Found {len(df)} rows")
    print(f"Columns: {list(df.columns)}")

    # This needs custom mapping based on the Excel structure
    # The Beta Test Group Calls.xlsx has a specific format

    supabase = get_client()

    # For each row, find the prospect and create a call record
    imported = 0
    skipped = 0

    for _, row in df.iterrows():
        # Get org name to match
        org_name = row.get('Organization') or row.get('org_name') or row.get('Organization_Name')
        if pd.isna(org_name):
            skipped += 1
            continue

        # Find prospect
        result = supabase.table('prospects').select('id').ilike('org_name', f'%{org_name}%').limit(1).execute()
        if not result.data:
            print(f"Prospect not found: {org_name}")
            skipped += 1
            continue

        prospect_id = result.data[0]['id']

        # Map call data
        call_data = {
            'prospect_id': prospect_id,
        }

        # Date
        date_col = row.get('Contact Date') or row.get('Date') or row.get('call_date')
        if pd.notna(date_col):
            if isinstance(date_col, str):
                call_data['call_date'] = date_col
            else:
                call_data['call_date'] = date_col.isoformat()

        # Outcome - map from various column names
        if row.get('VM/Message') or row.get('Voicemail'):
            call_data['outcome'] = 'vm_left'
        elif row.get('Talked to Someone'):
            call_data['outcome'] = 'talked_to_someone'
        elif row.get('Reached Decision Maker') or row.get('Reached DM'):
            call_data['outcome'] = 'reached_decision_maker'
        elif row.get('No Answer'):
            call_data['outcome'] = 'no_answer'

        # Interest
        interest = row.get('Interest') or row.get('Yes/No/Maybe')
        if pd.notna(interest):
            interest_lower = str(interest).lower()
            if interest_lower in ('yes', 'y'):
                call_data['interest'] = 'yes'
            elif interest_lower in ('no', 'n'):
                call_data['interest'] = 'no'
            elif interest_lower == 'maybe':
                call_data['interest'] = 'maybe'
            else:
                call_data['interest'] = 'uncertain'

        # Notes
        notes = row.get('Notes') or row.get('Call Notes')
        if pd.notna(notes):
            call_data['notes'] = str(notes)

        # Insert call
        try:
            supabase.table('calls').insert(call_data).execute()
            imported += 1
        except Exception as e:
            print(f"Error importing call for {org_name}: {e}")
            skipped += 1

    print(f"Done! Imported {imported} calls, skipped {skipped}")
    return imported


def list_sources():
    """List all source lists."""
    supabase = get_client()
    result = supabase.table('source_lists').select('*').order('created_at', desc=True).execute()

    print(f"\n{'ID':<5} {'Name':<40} {'Segment':<15} {'Count':<8} {'Created'}")
    print('-' * 90)
    for source in result.data:
        print(f"{source['id']:<5} {source['name'][:40]:<40} {source['segment'] or '-':<15} {source['record_count'] or 0:<8} {source['created_at'][:10]}")


def main():
    parser = argparse.ArgumentParser(description='Import data into TGS CRM')
    parser.add_argument('--file', '-f', help='Path to CSV or Excel file')
    parser.add_argument('--source-name', '-n', help='Name for the source list')
    parser.add_argument('--segment', '-s', choices=['nonprofit', 'foundation', 'foundation_mgmt'],
                        default='nonprofit', help='Prospect segment')
    parser.add_argument('--criteria', '-c', help='Criteria description for source list')
    parser.add_argument('--type', '-t', choices=['prospects', 'calls'], default='prospects',
                        help='Type of data to import')
    parser.add_argument('--sheet', help='Sheet name for Excel files')
    parser.add_argument('--list-sources', action='store_true', help='List existing source lists')

    args = parser.parse_args()

    if args.list_sources:
        list_sources()
        return

    if not args.file:
        parser.print_help()
        print("\nExamples:")
        print("  python3 import_existing.py --file data.csv --source-name 'Dec 2025 Healthcare' --segment nonprofit")
        print("  python3 import_existing.py --file calls.xlsx --type calls --sheet 'Nonprofits'")
        print("  python3 import_existing.py --list-sources")
        return

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    if args.type == 'prospects':
        if not args.source_name:
            # Use filename as default
            args.source_name = os.path.basename(args.file).replace('.csv', '').replace('.xlsx', '')
        import_prospects(args.file, args.source_name, args.segment, args.criteria)
    elif args.type == 'calls':
        import_calls(args.file, args.sheet)


if __name__ == '__main__':
    main()
