# Database Layer Quick Start Guide
**Campaign Control Center Dashboard**

## Installation

The database layer is already implemented and tested. No additional dependencies required beyond standard Python libraries:

```bash
# Required: Python 3.11+ with these packages
pip install cryptography
# (SQLite3 is included with Python)
```

## Basic Usage

### 1. Initialize Database (First Run)

```python
from database import schema

# Check if database exists
if not schema.database_exists():
    # Create tables and seed default settings
    schema.init_database()
    print("✓ Database initialized!")
```

### 2. Create a Vertical

```python
from database import models

# Create a new vertical/business line
success = models.create_vertical(
    vertical_id='debarment',
    display_name='Debarment Monitor',
    csv_filename='debarment_prospects.csv',
    target_industry='Federal Contractors'
)
```

### 3. Create an Email Account (with encrypted password)

```python
# Password is automatically encrypted before storage
account_id = models.create_email_account(
    email_address='alec@example.com',
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    smtp_username='alec@example.com',
    password='my_app_password',  # Will be encrypted
    daily_send_limit=450,
    display_name='Alec Kleinman'
)

print(f"Created account with ID: {account_id}")
```

### 4. Assign Account to Vertical

```python
# Create relationship between account and vertical
models.assign_account_to_vertical(account_id, 'debarment')

# Get all verticals for this account
verticals = models.get_account_verticals(account_id)
print(f"Account assigned to: {verticals}")
```

### 5. Create Email Template

```python
template_id = models.create_template(
    vertical_id='debarment',
    template_type='initial',  # or 'followup'
    template_name='Default Initial',
    subject_line='Debarment monitoring question',
    email_body='''Hi{greeting},

I wanted to reach out because I noticed {company} works with federal agencies.

Are you currently monitoring the SAM.gov debarment list?

Best regards'''
)
```

### 6. Retrieve Data

```python
# Get all active verticals
verticals = models.get_verticals(active_only=True)

# Get specific vertical
vertical = models.get_vertical('debarment')

# Get all email accounts
accounts = models.get_email_accounts(active_only=True)

# Get templates for a vertical
templates = models.get_templates(
    vertical_id='debarment',
    template_type='initial',
    active_only=True
)

# Get settings
timezone = models.get_setting('timezone', default='US/Eastern')
```

### 7. Get Decrypted Password (for SMTP connection)

```python
# Get decrypted password when needed
password = models.get_account_password_decrypted(account_id)

# Use for SMTP connection
import smtplib
server = smtplib.SMTP(account['smtp_host'], account['smtp_port'])
server.login(account['smtp_username'], password)
# ... send email
server.quit()
```

## Complete Example

```python
from database import models, schema

# Initialize database
if not schema.database_exists():
    schema.init_database()

# Create vertical
models.create_vertical(
    vertical_id='debarment',
    display_name='Debarment Monitor',
    csv_filename='debarment_prospects.csv',
    target_industry='Federal Contractors'
)

# Create email account
account_id = models.create_email_account(
    email_address='alec@example.com',
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    smtp_username='alec@example.com',
    password='my_app_password',
    daily_send_limit=450
)

# Assign account to vertical
models.assign_account_to_vertical(account_id, 'debarment')

# Create template
models.create_template(
    vertical_id='debarment',
    template_type='initial',
    template_name='Default',
    subject_line='Debarment monitoring',
    email_body='Hi{greeting}, ...'
)

# Retrieve all data
verticals = models.get_verticals(active_only=True)
accounts = models.get_email_accounts(active_only=True)
templates = models.get_templates(vertical_id='debarment')

print(f"✓ {len(verticals)} verticals")
print(f"✓ {len(accounts)} accounts")
print(f"✓ {len(templates)} templates")
```

## Error Handling

All functions raise descriptive exceptions:

```python
try:
    # Try to create duplicate vertical
    models.create_vertical('debarment', 'Test', 'test.csv')
except ValueError as e:
    print(f"Validation error: {e}")  # "Vertical with ID 'debarment' already exists"
except RuntimeError as e:
    print(f"Database error: {e}")
```

## Testing

Run the comprehensive test suite:

```bash
cd "Email Outreach Dashboard"
python3 -m database.test_database
```

Expected output:
```
============================================================
TOTAL: 8/8 tests passed (100.0%)
============================================================
```

## Database Location

```
Database File:
/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences/campaign_control.db

Encryption Key:
/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences/Email Outreach Dashboard/.encryption_key
```

## Common Operations

### Update a Vertical
```python
models.update_vertical(
    'debarment',
    display_name='Updated Name',
    target_industry='New Industry'
)
```

### Disable/Enable
```python
# Disable vertical
models.toggle_vertical_active('debarment', False)

# Disable account
models.toggle_account_active(account_id, False)

# Disable template
models.toggle_template_active(template_id, False)
```

### Delete (with cascade)
```python
# Delete vertical (also deletes its templates and assignments)
models.delete_vertical('debarment')

# Delete account (also deletes its assignments)
models.delete_email_account(account_id)
```

### Settings
```python
# Set a setting
models.set_setting('business_hours_start', '9')

# Get a setting with default
start_hour = models.get_setting('business_hours_start', default='9')

# Get all settings
all_settings = models.get_all_settings()
```

## Migration & Backup

### Backup Database
```python
from database import migrations

# Create backup
backup_path = migrations.backup_database()
print(f"Backup created: {backup_path}")
```

### Export to JSON
```python
# Export all data
migrations.export_database_to_json('backup.json')
```

### Get Statistics
```python
stats = migrations.get_database_stats()
print(f"Database size: {stats['database_size_mb']} MB")
print(f"Verticals: {stats['verticals_count']}")
print(f"Accounts: {stats['accounts_count']}")
```

### Verify Integrity
```python
report = migrations.verify_database_integrity()
print(f"Schema valid: {report['schema_valid']}")
print(f"Encryption working: {report['encryption_working']}")
print(f"Issues: {len(report['issues'])}")
```

## For Streamlit Integration

### With Caching
```python
import streamlit as st
from database import models

@st.cache_data(ttl=60)
def load_verticals():
    """Cache verticals for 60 seconds"""
    return models.get_verticals(active_only=True)

@st.cache_data(ttl=300)
def load_templates(vertical_id):
    """Cache templates for 5 minutes"""
    return models.get_templates(vertical_id=vertical_id)

# Usage
verticals = load_verticals()
st.write(f"Found {len(verticals)} verticals")
```

### With Forms
```python
with st.form("create_vertical"):
    vertical_id = st.text_input("Vertical ID")
    display_name = st.text_input("Display Name")
    csv_filename = st.text_input("CSV Filename")

    if st.form_submit_button("Create"):
        try:
            models.create_vertical(
                vertical_id=vertical_id,
                display_name=display_name,
                csv_filename=csv_filename
            )
            st.success("✓ Vertical created!")
        except ValueError as e:
            st.error(f"Error: {e}")
```

## Reference

For complete API documentation, see:
- `DATABASE_IMPLEMENTATION_SUMMARY.md` - Full documentation
- `models.py` - CRUD operations source code
- `schema.py` - Database schema definition
- `test_database.py` - Usage examples

## Support

All database functions include:
- Type hints for IDE autocomplete
- Comprehensive docstrings
- Error handling with descriptive messages
- Input validation

Use your IDE's autocomplete to explore available functions!
