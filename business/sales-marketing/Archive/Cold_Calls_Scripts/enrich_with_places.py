"""
Google Places API Enrichment Script
Adds website and business hours from Google Places API to prospect CSV.

Usage:
    python enrich_with_places.py [OPTIONS] [input.csv]

Options:
    --api-key KEY    Google Places API key
    --test N         Only process first N records (for testing)
    --no-db          Skip database insert
    --help, -h       Show help

Environment:
    GOOGLE_PLACES_API_KEY    Alternative way to provide API key
"""

import csv
import os
import sys
import time
import base64
from pathlib import Path

# Try to import cryptography for secure storage
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


def safe_input(prompt: str, hidden: bool = True) -> str:
    """Get input that works across Windows terminals."""
    if hidden:
        try:
            from getpass import getpass
            result = getpass(prompt)
            return result
        except Exception:
            pass
    print("(Note: Input will be visible)")
    return input(prompt)


# Configuration
SCRIPT_DIR = Path(__file__).parent
CREDENTIALS_FILE = SCRIPT_DIR / ".places_credentials"
SALT_FILE = SCRIPT_DIR / ".places_salt"
DEFAULT_INPUT = SCRIPT_DIR / "DATA_2025-12-12_prospect_call_list_v2.csv"

# Legacy Places API endpoints (these work better for hours)
PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Database config
DB_CONFIG = {
    'host': '172.26.16.1',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'kmalec21'
}


def get_encryption_key(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def save_credentials_secure(api_key: str, password: str) -> None:
    """Save API key with encryption."""
    if HAS_CRYPTO:
        salt = os.urandom(16)
        key = get_encryption_key(password, salt)
        f = Fernet(key)
        encrypted = f.encrypt(api_key.encode())

        with open(SALT_FILE, 'wb') as sf:
            sf.write(salt)
        with open(CREDENTIALS_FILE, 'wb') as cf:
            cf.write(encrypted)
        try:
            os.chmod(SALT_FILE, 0o600)
            os.chmod(CREDENTIALS_FILE, 0o600)
        except:
            pass
    else:
        encoded = base64.b64encode(api_key.encode()).decode()
        with open(CREDENTIALS_FILE, 'w') as cf:
            cf.write(encoded)
        print("Warning: 'cryptography' package not installed. Credentials stored with basic obfuscation.")


def load_credentials_secure(password: str = None) -> str:
    """Load API key from encrypted storage."""
    if not CREDENTIALS_FILE.exists():
        return None

    if HAS_CRYPTO:
        if not SALT_FILE.exists():
            return None
        with open(SALT_FILE, 'rb') as sf:
            salt = sf.read()
        with open(CREDENTIALS_FILE, 'rb') as cf:
            encrypted = cf.read()
        if password is None:
            password = safe_input("Enter password to unlock API key: ")
        try:
            key = get_encryption_key(password, salt)
            f = Fernet(key)
            return f.decrypt(encrypted).decode()
        except Exception as e:
            print(f"Error decrypting credentials: {e}")
            return None
    else:
        with open(CREDENTIALS_FILE, 'r') as cf:
            encoded = cf.read()
        return base64.b64decode(encoded.encode()).decode()


def setup_credentials() -> str:
    """Interactive credential setup."""
    print("\n" + "="*60)
    print("Google Places API Credential Setup")
    print("="*60)

    env_key = os.environ.get('GOOGLE_PLACES_API_KEY')
    if env_key:
        print("\nFound API key in GOOGLE_PLACES_API_KEY environment variable.")
        if test_api_key(env_key):
            print("API key is valid!")
            return env_key
        print("Environment variable key is invalid, continuing with manual setup...")

    if CREDENTIALS_FILE.exists():
        print("\nExisting credentials found.")
        choice = input("Use existing credentials? (Y/n): ").strip().lower()
        if choice != 'n':
            if HAS_CRYPTO:
                api_key = load_credentials_secure()
                if api_key:
                    print("Credentials loaded successfully.")
                    return api_key
                print("Failed to load credentials. Please re-enter.")
            else:
                api_key = load_credentials_secure()
                if api_key:
                    return api_key

    print("\nTo get a Google Places API key:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Create a project or select existing")
    print("3. Enable 'Places API' under APIs & Services")
    print("4. Create an API key under Credentials")
    print()
    print("You can also set GOOGLE_PLACES_API_KEY environment variable")
    print("or pass --api-key YOUR_KEY as command line argument")
    print()

    api_key = safe_input("Enter your Google Places API key: ", hidden=False).strip()

    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)

    print("\nTesting API key...")
    if not test_api_key(api_key):
        print("API key test failed. Please check your key and try again.")
        sys.exit(1)
    print("API key is valid!")

    if HAS_CRYPTO:
        print("\nSet a password to encrypt your API key (for future sessions):")
        password = safe_input("Password: ")
        password_confirm = safe_input("Confirm password: ")
        if password != password_confirm:
            print("Passwords don't match. Credentials not saved.")
            return api_key
        save_credentials_secure(api_key, password)
        print(f"Credentials saved securely to: {CREDENTIALS_FILE}")
    else:
        save = input("\nSave API key for future use? (y/N): ").strip().lower()
        if save == 'y':
            save_credentials_secure(api_key, None)
            print(f"Credentials saved to: {CREDENTIALS_FILE}")

    return api_key


def test_api_key(api_key: str) -> bool:
    """Test if API key is valid with a simple search."""
    params = {
        "query": "Starbucks Seattle",
        "key": api_key
    }
    try:
        response = requests.get(PLACES_TEXT_SEARCH_URL, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "OK":
            return True
        elif data.get("status") == "REQUEST_DENIED":
            print(f"API Error: {data.get('error_message', 'Access denied')}")
            return False
        else:
            print(f"API Error: {data.get('status')} - {data.get('error_message', '')}")
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False


def search_place(api_key: str, org_name: str, city: str, state: str) -> dict:
    """
    Search for a place using Google Places Text Search (legacy API).
    Returns basic info including place_id for details lookup.
    """
    search_query = f"{org_name} {city} {state}"

    params = {
        "query": search_query,
        "key": api_key
    }

    try:
        response = requests.get(PLACES_TEXT_SEARCH_URL, params=params, timeout=15)
        data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            place = data["results"][0]
            return {
                "found": True,
                "place_id": place.get("place_id", ""),
                "name": place.get("name", ""),
                "formatted_address": place.get("formatted_address", "")
            }
        elif data.get("status") == "OVER_QUERY_LIMIT":
            print("Rate limit hit. Waiting 60 seconds...")
            time.sleep(60)
            return search_place(api_key, org_name, city, state)

        return {"found": False, "place_id": "", "name": ""}

    except requests.exceptions.Timeout:
        print(f"  Timeout searching for: {org_name}")
        return {"found": False, "place_id": "", "name": ""}
    except Exception as e:
        print(f"  Error searching for {org_name}: {e}")
        return {"found": False, "place_id": "", "name": ""}


def get_place_details(api_key: str, place_id: str) -> dict:
    """
    Get detailed info for a place using Place Details API (legacy).
    This is where we get website and opening hours.
    """
    # Request the fields we need
    fields = "website,opening_hours,url"

    params = {
        "place_id": place_id,
        "fields": fields,
        "key": api_key
    }

    try:
        response = requests.get(PLACES_DETAILS_URL, params=params, timeout=15)
        data = response.json()

        if data.get("status") == "OK":
            result = data.get("result", {})

            # Extract opening hours
            opening_hours = result.get("opening_hours", {})
            weekday_text = opening_hours.get("weekday_text", [])
            hours_str = " | ".join(weekday_text) if weekday_text else ""

            return {
                "website": result.get("website", ""),
                "hours": hours_str,
                "google_maps_url": result.get("url", "")
            }
        elif data.get("status") == "OVER_QUERY_LIMIT":
            print("Rate limit hit on details. Waiting 60 seconds...")
            time.sleep(60)
            return get_place_details(api_key, place_id)

        return {"website": "", "hours": "", "google_maps_url": ""}

    except Exception as e:
        print(f"  Error getting details: {e}")
        return {"website": "", "hours": "", "google_maps_url": ""}


def ensure_prospects_table(conn) -> None:
    """Create prospects table if it doesn't exist, or add missing columns."""
    # First try to create the table
    create_sql = """
    CREATE TABLE IF NOT EXISTS f990_2025.prospects (
        id SERIAL PRIMARY KEY,
        ein VARCHAR(20),
        org_name TEXT,
        state VARCHAR(10),
        city VARCHAR(100),
        zip VARCHAR(20),
        f990_website TEXT,
        f990_phone VARCHAR(50),
        places_id VARCHAR(500),
        places_website TEXT,
        places_hours TEXT,
        places_found BOOLEAN,
        google_maps_url TEXT,
        icp_score INTEGER,
        priority_tier INTEGER,
        enriched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ein)
    );
    """

    # Columns to ensure exist (for existing tables)
    add_columns = [
        ("f990_website", "TEXT"),
        ("f990_phone", "VARCHAR(50)"),
        ("places_id", "VARCHAR(500)"),
        ("places_website", "TEXT"),
        ("places_hours", "TEXT"),
        ("places_found", "BOOLEAN"),
        ("google_maps_url", "TEXT"),
        ("icp_score", "INTEGER"),
        ("priority_tier", "INTEGER"),
        ("enriched_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ]

    with conn.cursor() as cur:
        cur.execute(create_sql)

        # Add any missing columns to existing table
        for col_name, col_type in add_columns:
            try:
                cur.execute(f"""
                    ALTER TABLE f990_2025.prospects
                    ADD COLUMN IF NOT EXISTS {col_name} {col_type};
                """)
            except Exception:
                pass  # Column might already exist

    conn.commit()
    print("Ensured prospects table exists with all required columns")


def upsert_prospect(conn, row: dict) -> None:
    """Insert or update a prospect record."""
    upsert_sql = """
    INSERT INTO f990_2025.prospects (
        ein, org_name, state, city, zip,
        f990_website, f990_phone, places_id, places_website,
        places_hours, places_found, google_maps_url,
        icp_score, priority_tier, enriched_at
    ) VALUES (
        %(ein)s, %(org_name)s, %(state)s, %(city)s, %(zip)s,
        %(f990_website)s, %(f990_phone)s, %(places_id)s, %(places_website)s,
        %(places_hours)s, %(places_found)s, %(google_maps_url)s,
        %(icp_score)s, %(priority_tier)s, CURRENT_TIMESTAMP
    )
    ON CONFLICT (ein) DO UPDATE SET
        org_name = EXCLUDED.org_name,
        places_id = EXCLUDED.places_id,
        places_website = EXCLUDED.places_website,
        places_hours = EXCLUDED.places_hours,
        places_found = EXCLUDED.places_found,
        google_maps_url = EXCLUDED.google_maps_url,
        enriched_at = CURRENT_TIMESTAMP;
    """

    with conn.cursor() as cur:
        cur.execute(upsert_sql, {
            'ein': row.get('ein', ''),
            'org_name': row.get('org_name', ''),
            'state': row.get('state', ''),
            'city': row.get('city', ''),
            'zip': row.get('zip', ''),
            'f990_website': row.get('f990_website', ''),
            'f990_phone': row.get('phone', ''),
            'places_id': row.get('places_id', ''),
            'places_website': row.get('places_website', ''),
            'places_hours': row.get('places_hours', ''),
            'places_found': row.get('places_found') == 'Y',
            'google_maps_url': row.get('google_maps_url', ''),
            'icp_score': int(row.get('icp_score', 0)) if row.get('icp_score') else None,
            'priority_tier': int(row.get('priority_tier', 0)) if row.get('priority_tier') else None,
        })


def process_csv(input_path: Path, api_key: str, test_limit: int = None, skip_db: bool = False) -> Path:
    """Process CSV and add Places API data."""

    print(f"\nReading: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    total_rows = len(rows)
    if test_limit:
        rows = rows[:test_limit]
        print(f"TEST MODE: Processing first {len(rows)} of {total_rows} records")
    else:
        print(f"Found {len(rows)} records")

    # Rename 'website' to 'f990_website' and add new columns
    if 'website' in fieldnames:
        website_idx = fieldnames.index('website')
        fieldnames[website_idx] = 'f990_website'

    # Add new columns
    new_cols = ['places_id', 'places_website', 'places_hours', 'places_found', 'google_maps_url']
    if 'f990_website' in fieldnames:
        idx = fieldnames.index('f990_website') + 1
    else:
        idx = len(fieldnames)

    for i, col in enumerate(new_cols):
        if col not in fieldnames:
            fieldnames.insert(idx + i, col)

    # Setup database connection
    db_conn = None
    if not skip_db and HAS_PSYCOPG2:
        try:
            print("\nConnecting to database...")
            db_conn = psycopg2.connect(**DB_CONFIG)
            ensure_prospects_table(db_conn)
            print("Database connected!")
        except Exception as e:
            print(f"Warning: Could not connect to database: {e}")
            print("Continuing without database insert...")
            db_conn = None
    elif not HAS_PSYCOPG2 and not skip_db:
        print("Warning: psycopg2 not installed. Skipping database insert.")
        print("Install with: pip install psycopg2-binary")

    # Process each row
    enriched_rows = []
    found_count = 0
    hours_count = 0

    for i, row in enumerate(rows):
        # Rename website column
        if 'website' in row:
            row['f990_website'] = row.pop('website')

        org_name = row.get('org_name', '')
        city = row.get('city', '')
        state = row.get('state', '')

        print(f"[{i+1}/{len(rows)}] Searching: {org_name[:50]}...", end=" ", flush=True)

        # Step 1: Text search to find place_id
        search_result = search_place(api_key, org_name, city, state)

        if search_result.get('found'):
            place_id = search_result['place_id']
            row['places_id'] = place_id
            row['places_found'] = 'Y'
            found_count += 1

            # Step 2: Get details (website, hours) using place_id
            details = get_place_details(api_key, place_id)
            row['places_website'] = details.get('website', '')
            row['places_hours'] = details.get('hours', '')
            row['google_maps_url'] = details.get('google_maps_url', '')

            if details.get('hours'):
                hours_count += 1
                print(f"Found! Hours: YES")
            else:
                print(f"Found! Hours: no")

            # Small delay between detail requests
            time.sleep(0.3)
        else:
            row['places_id'] = ''
            row['places_website'] = ''
            row['places_hours'] = ''
            row['places_found'] = 'N'
            row['google_maps_url'] = ''
            print("Not found")

        enriched_rows.append(row)

        # Insert into database
        if db_conn:
            try:
                upsert_prospect(db_conn, row)
                db_conn.commit()
            except Exception as e:
                print(f"  DB Error: {e}")
                db_conn.rollback()

        # Rate limiting - stay under 100 QPM
        time.sleep(0.5)

    # Close database connection
    if db_conn:
        db_conn.close()
        print("\nDatabase connection closed.")

    # Write output CSV
    stem = input_path.stem
    # Avoid double "DATA_" prefix
    if stem.startswith("DATA_"):
        stem = stem[5:]  # Remove existing DATA_ prefix

    if test_limit:
        output_path = input_path.parent / f"DATA_{stem}_enriched_TEST.csv"
    else:
        output_path = input_path.parent / f"DATA_{stem}_enriched.csv"

    print(f"\nWriting enriched data to: {output_path}")

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    print(f"\nComplete!")
    print(f"  Total records: {len(rows)}")
    print(f"  Places found: {found_count} ({100*found_count/len(rows):.1f}%)")
    print(f"  With hours: {hours_count} ({100*hours_count/len(rows):.1f}%)")
    print(f"  Output: {output_path}")

    if db_conn is None and not skip_db:
        print(f"\n  Note: Records NOT inserted to database (connection failed or psycopg2 not installed)")
    elif not skip_db:
        print(f"  Database: {len(rows)} records upserted to f990_2025.prospects")

    return output_path


def main():
    print("\n" + "="*60)
    print("Google Places API Enrichment Tool")
    print("="*60)

    # Parse command line arguments
    input_path = DEFAULT_INPUT
    api_key_arg = None
    test_limit = None
    skip_db = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--api-key" and i + 1 < len(args):
            api_key_arg = args[i + 1]
            i += 2
        elif args[i] == "--test" and i + 1 < len(args):
            test_limit = int(args[i + 1])
            i += 2
        elif args[i] == "--no-db":
            skip_db = True
            i += 1
        elif args[i] == "--help" or args[i] == "-h":
            print("\nUsage: python enrich_with_places.py [OPTIONS] [input.csv]")
            print("\nOptions:")
            print("  --api-key KEY    Google Places API key")
            print("  --test N         Only process first N records (for testing)")
            print("  --no-db          Skip database insert")
            print("  --help, -h       Show this help message")
            print("\nEnvironment variables:")
            print("  GOOGLE_PLACES_API_KEY    Alternative way to provide API key")
            print("\nDatabase:")
            print("  Inserts to f990_2025.prospects table (requires psycopg2)")
            sys.exit(0)
        elif not args[i].startswith("-"):
            input_path = Path(args[i])
            i += 1
        else:
            i += 1

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    print(f"\nInput file: {input_path}")
    if test_limit:
        print(f"Test mode: {test_limit} records")
    if skip_db:
        print("Database insert: DISABLED")

    # Setup credentials
    if api_key_arg:
        print("\nUsing API key from --api-key argument")
        if not test_api_key(api_key_arg):
            print("API key test failed. Please check your key.")
            sys.exit(1)
        print("API key is valid!")
        api_key = api_key_arg
    else:
        api_key = setup_credentials()

    # Confirm before processing
    print(f"\nReady to process {input_path.name}")
    if test_limit:
        print(f"Will process {test_limit} records (test mode)")
    print("This will query Google Places API for each record.")
    confirm = input("Continue? (Y/n): ").strip().lower()

    if confirm == 'n':
        print("Cancelled.")
        sys.exit(0)

    # Process the CSV
    output_path = process_csv(input_path, api_key, test_limit, skip_db)

    print(f"\nEnriched CSV saved to: {output_path}")


if __name__ == "__main__":
    main()
