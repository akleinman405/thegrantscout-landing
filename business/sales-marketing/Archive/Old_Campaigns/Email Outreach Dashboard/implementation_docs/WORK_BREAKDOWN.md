# WORK BREAKDOWN STRUCTURE
**Campaign Control Center Dashboard**

---

## DATABASE ENGINEER - DETAILED TASKS

### Task DB-1: Database Schema Implementation
**File:** `database/schema.py`  
**Estimated Time:** 45 minutes  
**Priority:** P0 (Critical Path)

**Subtasks:**
1. Create schema.py file with complete SQL statements
2. Implement CREATE TABLE statements:
   - `verticals` table
   - `email_accounts` table
   - `account_verticals` table (many-to-many)
   - `email_templates` table
   - `campaign_settings` table
3. Add indexes for performance
4. Add foreign key constraints with CASCADE
5. Create `create_schema()` function
6. Create `database_exists()` check function
7. Create `initialize_database()` function

**Acceptance Criteria:**
- All tables created with correct schema
- Indexes created
- Foreign keys work with CASCADE delete
- Function creates database without errors
- Database file created at correct Windows path

**Code Template:**
```python
import sqlite3
import os
from utils.windows_paths import get_database_path

def create_schema():
    """Create all database tables and indexes"""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS verticals (...)''')
    # ... etc
    
    # Create indexes
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_...''')
    
    conn.commit()
    conn.close()
```

---

### Task DB-2: CRUD Operations - Verticals
**File:** `database/models.py`  
**Estimated Time:** 30 minutes  
**Priority:** P0

**Functions to Implement:**
1. `get_verticals(active_only=False) -> List[Dict]`
2. `get_vertical(vertical_id) -> Dict`
3. `create_vertical(vertical_id, display_name, target_industry, csv_filename) -> bool`
4. `update_vertical(vertical_id, **kwargs) -> bool`
5. `delete_vertical(vertical_id) -> bool`
6. `toggle_vertical_active(vertical_id, active) -> bool`

**Error Handling:**
- Catch IntegrityError for duplicate vertical_id
- Validate inputs before insert
- Return None for not found
- Use parameterized queries (NO string concatenation)

---

### Task DB-3: CRUD Operations - Email Accounts
**File:** `database/models.py`  
**Estimated Time:** 45 minutes  
**Priority:** P0

**Functions to Implement:**
1. `get_email_accounts(active_only=False) -> List[Dict]`
2. `get_email_account(account_id) -> Dict`
3. `create_email_account(email, smtp_host, smtp_port, username, password, daily_limit, display_name=None) -> int`
   - Must encrypt password before storing
4. `update_email_account(account_id, **kwargs) -> bool`
5. `delete_email_account(account_id) -> bool`
6. `toggle_account_active(account_id, active) -> bool`
7. `get_account_password_decrypted(account_id) -> str`

**Special Requirements:**
- Password encrypted before insert (use encryption.py)
- Return account_id on create
- Join with account_verticals to include assigned verticals

---

### Task DB-4: CRUD Operations - Account-Vertical Assignments
**File:** `database/models.py`  
**Estimated Time:** 30 minutes  
**Priority:** P1

**Functions to Implement:**
1. `assign_account_to_vertical(account_id, vertical_id) -> bool`
2. `unassign_account_from_vertical(account_id, vertical_id) -> bool`
3. `get_account_verticals(account_id) -> List[str]`
4. `get_vertical_accounts(vertical_id) -> List[Dict]`
5. `get_assignment_matrix() -> Dict[int, List[str]]`

**Returns:**
- `get_assignment_matrix()` returns dict like:
  ```python
  {
      1: ['debarment', 'food_recall'],  # account_id: [vertical_ids]
      2: ['grant_alerts']
  }
  ```

---

### Task DB-5: CRUD Operations - Email Templates
**File:** `database/models.py`  
**Estimated Time:** 45 minutes  
**Priority:** P1

**Functions to Implement:**
1. `get_templates(vertical_id=None, template_type=None, active_only=False) -> List[Dict]`
2. `get_template(template_id) -> Dict`
3. `create_template(vertical_id, template_type, template_name, subject_line, email_body) -> int`
4. `update_template(template_id, **kwargs) -> bool`
5. `delete_template(template_id) -> bool`
6. `toggle_template_active(template_id, active) -> bool`
7. `get_active_template(vertical_id, template_type) -> Dict`

**Validation:**
- `template_type` must be 'initial' or 'followup'
- Unique constraint on (vertical_id, template_type, template_name)

---

### Task DB-6: Settings Management
**File:** `database/models.py`  
**Estimated Time:** 20 minutes  
**Priority:** P2

**Functions to Implement:**
1. `get_setting(key, default=None) -> str`
2. `set_setting(key, value, description=None) -> bool`
3. `get_all_settings() -> Dict[str, str]`
4. `delete_setting(key) -> bool`

**Default Settings to Seed:**
```python
DEFAULT_SETTINGS = {
    'business_hours_start': '9',
    'business_hours_end': '15',
    'timezone': 'US/Eastern',
    'conservative_pacing': 'true',
    'base_delay_min': '5',
    'base_delay_max': '10',
}
```

---

### Task DB-7: Password Encryption
**File:** `database/encryption.py`  
**Estimated Time:** 30 minutes  
**Priority:** P0

**Functions to Implement:**
1. `generate_key() -> bytes`
2. `save_key(key) -> None`
3. `load_key() -> bytes`
4. `encrypt_password(password: str) -> bytes`
5. `decrypt_password(encrypted: bytes) -> str`

**Implementation:**
```python
from cryptography.fernet import Fernet
import os
from utils.windows_paths import get_base_dir

KEY_FILE = os.path.join(get_base_dir(), '.encryption_key')

def generate_key():
    return Fernet.generate_key()

def encrypt_password(password: str) -> bytes:
    key = load_key()
    f = Fernet(key)
    return f.encrypt(password.encode())

def decrypt_password(encrypted: bytes) -> str:
    key = load_key()
    f = Fernet(key)
    return f.decrypt(encrypted).decode()
```

**Security:**
- Store key in `.encryption_key` file (add to .gitignore)
- Generate key on first run if not exists
- Never log passwords or keys

---

### Task DB-8: Database Testing
**File:** `tests/test_database.py`  
**Estimated Time:** 30 minutes  
**Priority:** P1

**Test Cases:**
1. Test schema creation
2. Test vertical CRUD
3. Test email account CRUD with encryption
4. Test account-vertical assignments
5. Test template CRUD
6. Test cascade delete (delete vertical → templates deleted)
7. Test unique constraints
8. Test concurrent access (if applicable)

---

## BACKEND DEVELOPER - DETAILED TASKS

### Task BE-1: Windows Path Utilities
**File:** `utils/windows_paths.py`  
**Estimated Time:** 20 minutes  
**Priority:** P0 (Critical)

**Functions to Implement:**
1. `get_base_dir() -> str`
   - Returns: `C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences`
2. `get_database_path() -> str`
3. `get_vertical_csv_path(vertical_id) -> str`
4. `get_sent_tracker_path() -> str`
5. `get_response_tracker_path() -> str`
6. `get_coordination_path() -> str`
7. `get_error_log_path() -> str`
8. `join_path(*parts) -> str`
9. `normalize_path(path) -> str`

**Testing:**
- Verify paths work on Windows
- Verify backslashes used correctly
- Verify files exist at returned paths

---

### Task BE-2: CSV Handler - Prospect Operations
**File:** `integrations/csv_handler.py`  
**Estimated Time:** 60 minutes  
**Priority:** P0

**Functions to Implement:**

1. `read_prospects(vertical_id) -> pd.DataFrame`
   ```python
   def read_prospects(vertical_id):
       """Read prospects CSV for a vertical"""
       csv_path = get_vertical_csv_path(vertical_id)
       
       if not os.path.exists(csv_path):
           return pd.DataFrame(columns=['email', 'first_name', 'company_name', 'state', 'website'])
       
       try:
           df = pd.read_csv(csv_path)
           return df
       except pd.errors.EmptyDataError:
           return pd.DataFrame(columns=['email', 'first_name', 'company_name', 'state', 'website'])
   ```

2. `write_prospects(vertical_id, df) -> bool`
   - Validate schema before write
   - Write to temp file, then rename (atomic)
   - Preserve column order

3. `append_prospects(vertical_id, new_df) -> int`
   - Read existing
   - Deduplicate by email
   - Append new rows
   - Return count added

4. `validate_prospect_schema(df) -> Tuple[bool, str]`
   - Check required columns present
   - Validate email format
   - Return (is_valid, error_message)

5. `deduplicate_prospects(df) -> pd.DataFrame`
   - Remove duplicate emails
   - Keep first occurrence

6. `get_prospect_count(vertical_id) -> int`

7. `get_prospect_stats(vertical_id) -> Dict`
   ```python
   {
       'total': 1500,
       'not_contacted': 1200,
       'initial_sent': 200,
       'followup_sent': 80,
       'responded': 20
   }
   ```

**Error Handling:**
- FileNotFoundError → return empty DataFrame
- Invalid CSV → return error message
- Encoding issues → try different encodings

---

### Task BE-3: Tracker Reader - Sent/Response Metrics
**File:** `integrations/tracker_reader.py`  
**Estimated Time:** 60 minutes  
**Priority:** P0

**Functions to Implement:**

1. `read_sent_tracker() -> pd.DataFrame`
   - Parse timestamp column to datetime
   - Add 'date' column
   - Cache with Streamlit (60s TTL)

2. `read_response_tracker() -> pd.DataFrame`

3. `get_sent_count(vertical=None, date_from=None, date_to=None) -> int`

4. `get_sent_by_date(vertical=None) -> pd.DataFrame`
   - Columns: date, count
   - Grouped by date

5. `get_sent_by_vertical() -> Dict[str, int]`
   ```python
   {
       'debarment': 450,
       'food_recall': 320,
       'grant_alerts': 100
   }
   ```

6. `calculate_response_rate(vertical=None) -> float`
   - Join sent_tracker with response_tracker
   - Count non-PENDING in response_tracker
   - Return percentage (e.g., 0.125 for 12.5%)

7. `get_daily_metrics(date=None) -> Dict`
   ```python
   {
       'sent_today': 150,
       'sent_this_week': 950,
       'sent_this_month': 3200,
       'response_rate': 0.125,
       'error_rate': 0.02
   }
   ```

8. `get_vertical_breakdown() -> List[Dict]`
   ```python
   [
       {
           'vertical': 'debarment',
           'sent_total': 450,
           'sent_today': 75,
           'response_rate': 0.15
       },
       # ...
   ]
   ```

**Performance:**
- Use Streamlit caching
- Optimize pandas operations
- Limit DataFrame size if very large

---

### Task BE-4: Coordination Reader
**File:** `integrations/coordination_reader.py`  
**Estimated Time:** 30 minutes  
**Priority:** P1

**Functions to Implement:**

1. `read_coordination() -> Dict`
   - Parse coordination.json
   - Handle missing file (return default structure)

2. `get_allocation_status() -> Dict`
   ```python
   {
       'date': '2025-11-04',
       'initial': {
           'allocated': 225,
           'sent': 150,
           'remaining': 75,
           'status': 'running'
       },
       'followup': {
           'allocated': 225,
           'sent': 0,
           'remaining': 225,
           'status': 'idle'
       },
       'total_capacity': 450,
       'total_sent': 150,
       'total_remaining': 300
   }
   ```

3. `is_capacity_available() -> bool`

4. `get_daily_summary() -> str`
   - Human-readable summary for display

**Future Enhancement (Phase 2):**
5. `update_coordination(updates: Dict) -> bool`
   - For pause/resume functionality

---

### Task BE-5: Validators
**File:** `utils/validators.py`  
**Estimated Time:** 45 minutes  
**Priority:** P1

**Functions to Implement:**

1. `validate_email(email: str) -> bool`
   ```python
   import re
   EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
   
   def validate_email(email):
       return bool(re.match(EMAIL_REGEX, email))
   ```

2. `validate_csv_schema(df, required_columns) -> Tuple[bool, str]`
   - Check all required columns present
   - Return (is_valid, error_message)

3. `validate_smtp_settings(host, port, username, password) -> Tuple[bool, str]`
   - Attempt SMTP connection
   - Return (success, error_message)

4. `validate_vertical_id(vertical_id) -> bool`
   - Alphanumeric + underscore only
   - No spaces, special chars

5. `sanitize_filename(filename) -> str`
   - Remove path separators
   - Remove special characters
   - Limit length

6. `validate_file_upload(file, allowed_extensions, max_size_mb) -> Tuple[bool, str]`
   - Check extension
   - Check file size
   - Basic malware check (scan for executable patterns)

**Testing:**
- Test valid/invalid emails
- Test edge cases (empty, None, very long)
- Test CSV with missing/extra columns

---

### Task BE-6: Formatters
**File:** `utils/formatters.py`  
**Estimated Time:** 30 minutes  
**Priority:** P2

**Functions to Implement:**

1. `format_number(num: int) -> str`
   ```python
   def format_number(num):
       return f"{num:,}"  # 1234 -> "1,234"
   ```

2. `format_percentage(value: float, decimals=1) -> str`
   ```python
   def format_percentage(value, decimals=1):
       return f"{value * 100:.{decimals}f}%"  # 0.125 -> "12.5%"
   ```

3. `format_datetime(dt, format='%Y-%m-%d %H:%M:%S') -> str`

4. `format_date(dt) -> str`
   - Returns: "Nov 04, 2025"

5. `format_time_ago(dt) -> str`
   - Returns: "2 hours ago", "3 days ago"

6. `truncate_text(text, length, suffix='...') -> str`

---

### Task BE-7: Integration Testing
**File:** `tests/test_integrations.py`  
**Estimated Time:** 45 minutes  
**Priority:** P1

**Test Cases:**
1. Test read_prospects with valid CSV
2. Test read_prospects with missing file
3. Test append_prospects with deduplication
4. Test read_sent_tracker parsing
5. Test calculate_response_rate
6. Test coordination reader
7. Test Windows path handling
8. Test validators with edge cases

---

## FRONTEND DEVELOPER - DETAILED TASKS

### Task FE-1: Project Setup
**Files:** `dashboard.py`, `.streamlit/config.toml`  
**Estimated Time:** 20 minutes  
**Priority:** P0

**Dashboard.py:**
```python
import streamlit as st
from database import models

st.set_page_config(
    page_title="Campaign Control Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
if not models.database_exists():
    with st.spinner("Initializing database..."):
        models.initialize_database()
    st.success("Database initialized!")

st.title("📊 Campaign Control Center")
st.markdown("---")

# Main page content (metrics overview)
```

**.streamlit/config.toml:**
```toml
[theme]
primaryColor = "#3498db"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

---

### Task FE-2: Reusable Components - Cards
**File:** `components/cards.py`  
**Estimated Time:** 45 minutes  
**Priority:** P1

**Functions to Implement:**

1. `metric_card(title, value, delta=None, icon=None)`
   ```python
   def metric_card(title, value, delta=None, icon=None):
       col1, col2 = st.columns([1, 4])
       with col1:
           if icon:
               st.markdown(f"### {icon}")
       with col2:
           st.metric(label=title, value=value, delta=delta)
   ```

2. `status_card(title, status, color, details)`
   - Display status with colored badge
   - Show details below

3. `account_card(account_info)`
   - Show email, daily limit, sent today, status
   - Progress bar for quota

4. `vertical_card(vertical_info)`
   - Show vertical name, prospect count, status

---

### Task FE-3: Reusable Components - Charts
**File:** `components/charts.py`  
**Estimated Time:** 60 minutes  
**Priority:** P1

**Functions to Implement:**

1. `line_chart_emails_over_time(df, vertical_filter='all')`
   ```python
   import plotly.express as px
   
   def line_chart_emails_over_time(df, vertical_filter='all'):
       if vertical_filter != 'all':
           df = df[df['vertical'] == vertical_filter]
       
       # Group by date
       daily = df.groupby('date').size().reset_index(name='count')
       
       fig = px.line(daily, x='date', y='count', 
                     title='Emails Sent Over Time',
                     labels={'date': 'Date', 'count': 'Emails Sent'})
       
       st.plotly_chart(fig, use_container_width=True)
   ```

2. `bar_chart_by_vertical(df)`
   - Bar chart showing sent count by vertical

3. `donut_chart_response_rates(data)`
   - Pie/donut chart showing response breakdown

4. `progress_bar_quota(sent, limit, label)`
   - Progress bar with percentage

---

### Task FE-4: Reusable Components - Forms
**File:** `components/forms.py`  
**Estimated Time:** 60 minutes  
**Priority:** P1

**Functions to Implement:**

1. `email_account_form(account=None)`
   - Returns: dict with form data or None if cancelled
   - If account provided, pre-fill for editing
   ```python
   def email_account_form(account=None):
       with st.form("email_account_form"):
           email = st.text_input("Email Address*", value=account['email'] if account else "")
           display_name = st.text_input("Display Name", value=account['display_name'] if account else "")
           smtp_host = st.text_input("SMTP Host*", value=account['smtp_host'] if account else "smtp.gmail.com")
           smtp_port = st.number_input("SMTP Port*", value=account['smtp_port'] if account else 587)
           # ...
           
           submitted = st.form_submit_button("Save")
           if submitted:
               return {
                   'email': email,
                   'display_name': display_name,
                   # ...
               }
       return None
   ```

2. `vertical_form(vertical=None)`

3. `template_editor_form(template=None)`

4. `settings_form()`

---

### Task FE-5: Reusable Components - Tables
**File:** `components/tables.py`  
**Estimated Time:** 45 minutes  
**Priority:** P1

**Functions to Implement:**

1. `prospect_table(df, editable=False)`
   - Display DataFrame with formatting
   - Optional: select rows for delete

2. `account_table(accounts)`
   - Show accounts with actions (Edit/Delete buttons)

3. `vertical_table(verticals)`

4. `template_table(templates)`

---

### Task FE-6: Page 1 - Dashboard (Home)
**File:** `pages/1_📊_Dashboard.py`  
**Estimated Time:** 60 minutes  
**Priority:** P0

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Campaign Dashboard                                       │
├─────────────────────────────────────────────────────────────┤
│  Filter: [All Verticals ▼]                                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 📧 1,234 │ │ 📆 150   │ │ 📅 950   │ │ 💬 12.5% │       │
│  │ Total    │ │ Today    │ │ This Week│ │ Response │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│  [Line Chart: Emails Over Time]                             │
├─────────────────────────────────────────────────────────────┤
│  [Bar Chart: By Vertical] │ [Donut: Response Rates]         │
├─────────────────────────────────────────────────────────────┤
│  Email Accounts Status:                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Account          │ Sent  │ Limit │ Status │ Progress │  │
│  │ alec@example.com │ 150   │ 450   │ Active │ [████░] │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Campaign Status (from coordination.json):                  │
│  Initial: 150/225 sent | Followup: 0/225 sent               │
└─────────────────────────────────────────────────────────────┘
```

**Implementation:**
- Vertical filter dropdown at top
- Metrics cards (4 across)
- Line chart (full width)
- Bar chart + donut chart (2 columns)
- Account status table
- Coordination status summary

---

### Task FE-7: Page 2 - Prospects Manager
**File:** `pages/2_📥_Prospects.py`  
**Estimated Time:** 75 minutes  
**Priority:** P0

**Features:**
1. **Upload Section:**
   - Tabs or expanders for each vertical
   - File uploader per vertical
   - Validation on upload
   - Success/error messages
   - Show count of new prospects added

2. **Viewer Section:**
   - Dropdown to select vertical
   - Data table with filters
   - Search box (by email, company)
   - Status filter (not contacted, initial sent, followup sent, responded)
   - Export to CSV button
   - Delete selected button

**Implementation:**
```python
import streamlit as st
from database import models
from integrations import csv_handler
from utils import validators

st.title("📥 Prospect Manager")

# Get verticals
verticals = models.get_verticals(active_only=True)

# Upload section
st.header("Upload Prospects")
for vertical in verticals:
    with st.expander(f"{vertical['display_name']} ({vertical['vertical_id']})"):
        uploaded_file = st.file_uploader(
            f"Upload CSV for {vertical['display_name']}", 
            key=f"upload_{vertical['vertical_id']}",
            type=['csv']
        )
        
        if uploaded_file:
            # Validate and process
            df = pd.read_csv(uploaded_file)
            is_valid, error = validators.validate_csv_schema(df, ['email', 'first_name', 'company_name', 'state', 'website'])
            
            if is_valid:
                count_added = csv_handler.append_prospects(vertical['vertical_id'], df)
                st.success(f"✅ Added {count_added} new prospects!")
            else:
                st.error(f"❌ Invalid CSV: {error}")

# Viewer section
st.header("View Prospects")
selected_vertical = st.selectbox("Select Vertical", [v['vertical_id'] for v in verticals])
# ... rest of viewer
```

---

### Task FE-8: Page 3 - Email Accounts
**File:** `pages/3_📧_Email_Accounts.py`  
**Estimated Time:** 60 minutes  
**Priority:** P1

**Features:**
1. Account list table
2. Add account button → modal/form
3. Edit account → pre-filled form
4. Delete account with confirmation
5. Test SMTP connection button
6. Account-vertical assignment matrix
7. Capacity summary

**Implementation:**
- Use `st.data_editor` or custom table
- `st.dialog` for add/edit forms (Streamlit 1.28+)
- Confirmation dialog for delete
- Show success/error messages after actions

---

### Task FE-9: Page 4 - Verticals Manager
**File:** `pages/4_🔧_Verticals.py`  
**Estimated Time:** 45 minutes  
**Priority:** P1

**Features:**
1. Vertical list table
2. Add vertical → creates DB entry + CSV file
3. Edit vertical
4. Delete vertical (with confirmation, archives folder)
5. Show stats (prospect count, active templates)

---

### Task FE-10: Page 5 - Templates Manager
**File:** `pages/5_✉️_Templates.py`  
**Estimated Time:** 90 minutes  
**Priority:** P1

**Features:**
1. Vertical selector (tabs)
2. Template list for selected vertical
3. Add template button
4. Template editor:
   - Type dropdown (Initial/Followup)
   - Name input
   - Subject line input
   - Body textarea (large, 10+ rows)
   - Available variables display
   - Live preview pane
5. Save button
6. Delete with confirmation

**Preview Pane:**
```python
st.subheader("Preview")
preview_data = {
    'greeting': ' John',
    'first_name': 'John',
    'company': 'Acme Corp',
    'state': 'CA'
}

preview_subject = subject_line  # As entered
preview_body = email_body.format(**preview_data)

st.text(f"Subject: {preview_subject}")
st.text_area("Body Preview", preview_body, height=200, disabled=True)
```

---

### Task FE-11: Page 6 - Campaign Planner
**File:** `pages/6_📅_Planner.py`  
**Estimated Time:** 60 minutes  
**Priority:** P2

**Features:**
1. **Today's Plan:**
   - Table from coordination.json
   - Show: Vertical, Type, Allocated, Sent, Remaining, Status

2. **Weekly Forecast:**
   - Calculate based on:
     - Available prospects
     - Daily limits
     - Business hours
   - Show day-by-day breakdown

3. **Capacity Calculator:**
   - Input: number of prospects
   - Output: days required
   - Breakdown by vertical

**Implementation:**
```python
# Read coordination
coord = coordination_reader.get_allocation_status()

st.subheader("Today's Plan")
st.write(f"Date: {coord['date']}")

plan_df = pd.DataFrame([
    {
        'Campaign': 'Initial Outreach',
        'Allocated': coord['initial']['allocated'],
        'Sent': coord['initial']['sent'],
        'Remaining': coord['initial']['remaining'],
        'Status': coord['initial']['status']
    },
    {
        'Campaign': 'Follow-up',
        'Allocated': coord['followup']['allocated'],
        'Sent': coord['followup']['sent'],
        'Remaining': coord['followup']['remaining'],
        'Status': coord['followup']['status']
    }
])

st.dataframe(plan_df)
```

---

### Task FE-12: Page 7 - Settings
**File:** `pages/7_⚙️_Settings.py`  
**Estimated Time:** 45 minutes  
**Priority:** P2

**Features:**
1. **Global Campaign Settings:**
   - Business hours (start/end)
   - Timezone
   - Conservative pacing toggle
   - Hourly rate (display only, calculated)

2. **Anti-Spam Settings:**
   - Base delay min/max
   - Break frequency
   - Break duration

3. **File Paths (display only):**
   - Base directory
   - Database path
   - Tracker paths

4. **Data Management:**
   - Export all data button
   - Reset daily counters button

5. **System Info:**
   - Dashboard version
   - Database size
   - Total prospects
   - Total sent emails

**Implementation:**
```python
st.title("⚙️ Settings")

# Load current settings
settings = models.get_all_settings()

with st.form("settings_form"):
    st.subheader("Business Hours")
    
    col1, col2 = st.columns(2)
    with col1:
        start_hour = st.number_input("Start Hour", 0, 23, 
                                     value=int(settings.get('business_hours_start', 9)))
    with col2:
        end_hour = st.number_input("End Hour", 0, 23, 
                                   value=int(settings.get('business_hours_end', 15)))
    
    timezone = st.text_input("Timezone", value=settings.get('timezone', 'US/Eastern'))
    
    # ... more settings
    
    if st.form_submit_button("Save Settings"):
        models.set_setting('business_hours_start', str(start_hour))
        models.set_setting('business_hours_end', str(end_hour))
        # ...
        st.success("Settings saved!")
```

---

### Task FE-13: Styling & Polish
**Estimated Time:** 45 minutes  
**Priority:** P2

**Tasks:**
1. Consistent color scheme across pages
2. Proper spacing (st.markdown("---") between sections)
3. Icons for all pages
4. Loading spinners for slow operations
5. Success/error toast messages
6. Responsive layout (test on different screen sizes)
7. Custom CSS (if needed) via st.markdown

---

## QA SPECIALIST - DETAILED TASKS

### Task QA-1: Test Plan Creation
**Deliverable:** Test plan document  
**Estimated Time:** 30 minutes  
**Priority:** P0

**Contents:**
1. Test objectives
2. Scope (in-scope / out-of-scope)
3. Test environment (Windows 10/11)
4. Test approach (manual, automated)
5. Test cases (list of all scenarios)
6. Pass/fail criteria
7. Bug reporting process

---

### Task QA-2: Create Test Fixtures
**Directory:** `tests/fixtures/`  
**Estimated Time:** 30 minutes  
**Priority:** P0

**Files to Create:**
1. `sample_prospects_valid.csv` - 100 valid prospects
2. `sample_prospects_invalid.csv` - Missing columns
3. `sample_prospects_large.csv` - 10,000 prospects
4. `sample_sent_tracker.csv` - 500 sent emails across dates
5. `sample_response_tracker.csv` - 50 responses
6. `sample_coordination.json` - Various states

---

### Task QA-3: Database Testing
**Estimated Time:** 60 minutes  
**Priority:** P0

**Test Cases:**
1. ✓ Database creation succeeds
2. ✓ All tables created with correct schema
3. ✓ Create vertical → verify in DB
4. ✓ Create email account → verify password encrypted
5. ✓ Assign account to vertical → verify relationship
6. ✓ Delete vertical → verify cascade delete templates
7. ✓ Duplicate vertical ID → verify error
8. ✓ Update template → verify changes saved
9. ✓ Get verticals with active filter → verify results
10. ✓ Encryption/decryption round-trip → verify password matches

**Bug Reporting:**
- Document any failures with:
  - Test case number
  - Expected result
  - Actual result
  - Steps to reproduce
  - Screenshots (if applicable)

---

### Task QA-4: Integration Testing
**Estimated Time:** 90 minutes  
**Priority:** P0

**CSV Operations:**
1. ✓ Upload valid CSV → verify file written
2. ✓ Upload invalid CSV → verify error message shown
3. ✓ Upload duplicate prospects → verify deduplication
4. ✓ Read large CSV (10,000 rows) → verify performance <5s
5. ✓ Read sent_tracker → verify metrics calculated correctly
6. ✓ Read coordination.json → verify status displayed correctly

**Metrics Calculation:**
7. ✓ Total sent count → manual verification
8. ✓ Sent today count → filter verification
9. ✓ Response rate → manual calculation vs system
10. ✓ Vertical breakdown → sum verification

**Path Handling:**
11. ✓ All file operations use Windows paths
12. ✓ No path errors on Windows
13. ✓ Database created at correct location

---

### Task QA-5: UI Testing - All Pages
**Estimated Time:** 120 minutes  
**Priority:** P0

**Page 1 - Dashboard:**
1. ✓ Metrics display correctly
2. ✓ Vertical filter updates metrics
3. ✓ Charts render without errors
4. ✓ Account status table shows data
5. ✓ Coordination status accurate

**Page 2 - Prospects:**
6. ✓ File uploader works
7. ✓ CSV validation catches errors
8. ✓ Upload success message shown
9. ✓ Prospect table displays data
10. ✓ Filters work (status, search)
11. ✓ Export button downloads CSV

**Page 3 - Email Accounts:**
12. ✓ Account table displays
13. ✓ Add account form works
14. ✓ Edit account pre-fills form
15. ✓ Delete account shows confirmation
16. ✓ Test SMTP connection works
17. ✓ Assignment matrix updates

**Page 4 - Verticals:**
18. ✓ Vertical table displays
19. ✓ Add vertical creates DB entry + file
20. ✓ Edit vertical updates
21. ✓ Delete vertical confirms + archives
22. ✓ Stats display correctly

**Page 5 - Templates:**
23. ✓ Template list displays
24. ✓ Add template works
25. ✓ Edit template loads correctly
26. ✓ Preview pane updates
27. ✓ Save template persists changes
28. ✓ Delete template confirms

**Page 6 - Planner:**
29. ✓ Today's plan displays
30. ✓ Weekly forecast calculates
31. ✓ Capacity calculator works

**Page 7 - Settings:**
32. ✓ Settings load current values
33. ✓ Save settings persists
34. ✓ System info displays

---

### Task QA-6: Edge Case Testing
**Estimated Time:** 60 minutes  
**Priority:** P1

**Test Cases:**
1. ✓ Empty database (first run)
2. ✓ No prospects loaded
3. ✓ No verticals created
4. ✓ Invalid SMTP credentials
5. ✓ Malformed CSV (extra columns)
6. ✓ Malformed CSV (missing columns)
7. ✓ Empty CSV file
8. ✓ CSV with unicode characters
9. ✓ Very long company names (>200 chars)
10. ✓ Duplicate email in upload
11. ✓ Coordination.json missing
12. ✓ Coordination.json malformed
13. ✓ Sent_tracker.csv very large (100,000 rows)

---

### Task QA-7: Windows Compatibility Testing
**Estimated Time:** 60 minutes  
**Priority:** P0

**Environment:** Windows 10 or Windows 11

**Test Cases:**
1. ✓ Dashboard launches (streamlit run dashboard.py)
2. ✓ No path errors in logs
3. ✓ Database created at correct path
4. ✓ CSV files read correctly
5. ✓ CSV files write correctly
6. ✓ All pages load without errors
7. ✓ File uploads work
8. ✓ File downloads work
9. ✓ No permission errors

**Common Windows Issues to Check:**
- Backslash vs forward slash in paths
- Long path issues (>260 chars)
- Permission errors
- File locking issues

---

### Task QA-8: Performance Testing
**Estimated Time:** 45 minutes  
**Priority:** P2

**Benchmarks:**
1. ✓ Dashboard load time < 3 seconds
2. ✓ Page navigation < 1 second
3. ✓ Metrics calculation (10,000 sent emails) < 2 seconds
4. ✓ Chart rendering < 1 second
5. ✓ CSV upload (1,000 rows) < 3 seconds
6. ✓ CSV upload (10,000 rows) < 10 seconds
7. ✓ Database query < 100ms

**Tools:**
- Use browser DevTools
- Measure with Python time module
- Document actual times

---

### Task QA-9: Integration with Scripts Testing
**Estimated Time:** 90 minutes  
**Priority:** P0 (CRITICAL)

**Test Scenarios:**

**Scenario 1: Dashboard Uploads → Scripts Send**
1. Dashboard: Upload 10 new prospects to debarment vertical
2. Verify: debarment_prospects.csv updated
3. Run: send_initial_outreach.py
4. Verify: Scripts send to new prospects
5. Verify: sent_tracker.csv has new entries
6. Dashboard: Refresh, verify metrics updated

**Scenario 2: Scripts Send → Dashboard Shows**
1. Run: send_initial_outreach.py (send 50 emails)
2. Dashboard: Refresh dashboard page
3. Verify: "Sent Today" metric increased by 50
4. Verify: Charts updated
5. Verify: Account quota updated

**Scenario 3: Create Vertical in Dashboard**
1. Dashboard: Create new vertical "test_vertical"
2. Verify: Database entry created
3. Verify: test_vertical_prospects.csv created
4. Verify: Can upload prospects
5. Verify: Scripts can read CSV (check manually)

**Scenario 4: Coordination Status Sync**
1. Run: send_initial_outreach.py (in progress)
2. Dashboard: View Planner page
3. Verify: Status shows "running"
4. Verify: Allocated/sent counts match
5. Stop script
6. Verify: Status updates

**Acceptance Criteria:**
- All 4 scenarios pass
- No data corruption
- No file locking errors
- Dashboard and scripts never conflict

---

### Task QA-10: Create Test Report
**Deliverable:** Test report document  
**Estimated Time:** 30 minutes  
**Priority:** P0

**Contents:**
1. Executive summary
2. Test statistics (X total, Y passed, Z failed)
3. Test results by category
4. Bug reports (with severity)
5. Performance benchmarks
6. Windows compatibility results
7. Integration test results
8. Recommendations
9. Sign-off

**Format:**
```
# TEST REPORT
Date: 2025-11-04
Tester: QA Specialist

## Summary
- Total Test Cases: 150
- Passed: 145 (96.7%)
- Failed: 5 (3.3%)
- Blocked: 0

## Critical Issues
1. [BUG-001] CSV upload fails with unicode characters (Priority: P1)
   - Steps to reproduce: ...
   - Expected: ...
   - Actual: ...

## Performance Results
- Dashboard load: 2.1s (Target: <3s) ✓
- CSV upload (1K rows): 2.8s (Target: <3s) ✓
...

## Recommendation
Dashboard is ready for deployment after fixing BUG-001.
```

---

## PROJECT MANAGER - FINAL DELIVERABLES

### Task PM-1: SETUP_INSTRUCTIONS.md
**Estimated Time:** 60 minutes  
**Priority:** P0

**Required Sections:**
1. Prerequisites
2. Installation Steps (detailed, numbered)
3. First-Time Setup
4. Running the Dashboard
5. Configuration
6. Integration Verification
7. Troubleshooting Common Setup Issues

---

### Task PM-2: TROUBLESHOOTING.md
**Estimated Time:** 45 minutes  
**Priority:** P0

**Required Sections:**
1. Dashboard Won't Start
2. Database Errors
3. File Not Found Errors
4. Path Issues on Windows
5. CSV Upload Failures
6. SMTP Connection Failures
7. Template Not Updating
8. Metrics Incorrect
9. Charts Not Rendering
10. Integration Issues

---

### Task PM-3: README.md
**Estimated Time:** 30 minutes  
**Priority:** P0

**Required Sections:**
1. Project Overview
2. Features List
3. Screenshots (or descriptions)
4. Quick Start
5. Documentation Links
6. Technology Stack
7. File Structure
8. Architecture Overview
9. Contributing
10. License

---

### Task PM-4: Final Integration Testing
**Estimated Time:** 60 minutes  
**Priority:** P0

**Checklist:**
- [ ] All pages load without errors
- [ ] All CRUD operations work
- [ ] CSV upload/download works
- [ ] Metrics accurate
- [ ] Integration with scripts verified
- [ ] Windows compatibility confirmed
- [ ] Documentation accurate
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Code reviewed

---

## SUMMARY

**Total Estimated Effort:**
- Database Engineer: 4.5 hours
- Backend Developer: 6 hours
- Frontend Developer: 10.5 hours
- QA Specialist: 9.5 hours
- Project Manager: 4 hours

**Total: ~34.5 hours**

**Critical Path:**
1. PM: Plan (done)
2. DB: Schema + CRUD (4.5 hours)
3. Backend: Integration layer (6 hours)
4. Frontend: All pages (10.5 hours)
5. QA: Testing (9.5 hours)
6. PM: Documentation (4 hours)

**Parallel Work Opportunities:**
- DB + Backend can overlap after schema done
- Frontend can start components early
- QA can write test plan during development

---

**END OF WORK BREAKDOWN**
