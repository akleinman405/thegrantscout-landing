# CAMPAIGN CONTROL CENTER - IMPLEMENTATION PLAN
**Project Manager: Claude Code**  
**Date: 2025-11-04**  
**Project Type: Streamlit Dashboard Integration with Existing Email Automation System**

---

## EXECUTIVE SUMMARY

This document provides a comprehensive implementation plan for building the "Campaign Control Center" Streamlit dashboard. The dashboard will integrate seamlessly with an existing, working Python-based email automation system without disrupting current operations.

**Key Constraints:**
- MUST NOT break existing automation scripts
- Windows environment (path compatibility critical)
- Integration with existing CSV files and coordination.json
- Production-ready quality required
- Single-session build timeline

**Success Criteria:**
- All 7 dashboard pages functional
- Seamless integration with existing scripts
- Windows-compatible file operations
- Professional UI with real-time metrics
- Comprehensive documentation

---

## TABLE OF CONTENTS

1. [System Analysis](#1-system-analysis)
2. [Architecture Overview](#2-architecture-overview)
3. [Data Model Design](#3-data-model-design)
4. [Integration Strategy](#4-integration-strategy)
5. [File Structure](#5-file-structure)
6. [Technical Decisions](#6-technical-decisions)
7. [Work Breakdown](#7-work-breakdown)
8. [Risk Assessment](#8-risk-assessment)
9. [Implementation Timeline](#9-implementation-timeline)

---

## 1. SYSTEM ANALYSIS

### 1.1 Existing System Components

**Scripts Analyzed:**
- `config.py` (205 lines) - Configuration hub
- `coordination.py` (216 lines) - Capacity allocation manager
- `send_initial_outreach.py` - Initial email sender
- `send_followup.py` - Follow-up email sender

**Data Files:**
- `sent_tracker.csv` - Email send log (7 columns)
- `response_tracker.csv` - Response tracking (6 columns)
- `coordination.json` - Real-time coordination state
- `debarment_prospects.csv` - Prospect list (5 columns: email, first_name, company_name, state, website)
- `food_recall_prospects.csv` - Prospect list
- `grant_alerts_prospects.csv` - Prospect list (placeholder)
- `error_log.csv` - Error tracking

### 1.2 Current System Architecture

```
Existing Architecture:
┌─────────────────────────────────────────────────────────────┐
│  config.py                                                   │
│  - SMTP settings (env vars)                                  │
│  - Email templates (hardcoded strings)                       │
│  - Vertical definitions (dict)                               │
│  - File paths (Windows paths)                                │
│  - Rate limiting parameters                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  coordination.py                                             │
│  - Allocates 450 daily capacity                              │
│  - Splits: Initial (up to 225) + Followup (up to 225)        │
│  - Manages coordination.json                                 │
│  - Date-based reset logic                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────┬──────────────────────────────────┐
│  send_initial_outreach.py│  send_followup.py                │
│  - Reads prospect CSVs   │  - Reads response_tracker.csv    │
│  - Checks coordination   │  - Identifies followup targets   │
│  - Sends emails          │  - Sends followup emails         │
│  - Writes sent_tracker   │  - Updates response_tracker      │
│  - Updates coordination  │  - Updates coordination          │
└──────────────────────────┴──────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Data Layer (CSV Files)                                      │
│  - sent_tracker.csv (append-only log)                        │
│  - response_tracker.csv (status updates)                     │
│  - coordination.json (daily state)                           │
│  - prospect CSVs (read-only for scripts)                     │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Key Observations

**What Works Well:**
1. Clean separation of concerns (config, coordination, sending)
2. Robust coordination system preventing over-sending
3. CSV-based approach is simple and debuggable
4. Conservative pacing (75 emails/hour) prevents spam flags
5. Multi-vertical support with fair allocation

**Integration Points:**
1. **Read-Only Integration:**
   - sent_tracker.csv (for metrics)
   - response_tracker.csv (for response rates)
   - coordination.json (for status display)

2. **Read-Write Integration:**
   - Prospect CSVs (dashboard uploads, scripts read)
   - Templates (dashboard edits, scripts use via config.py)
   - Email account settings (needs new storage)

3. **No Direct Integration:**
   - Scripts don't need to know about dashboard database
   - Dashboard doesn't execute sending logic
   - Clean separation maintained

**Critical Constraints:**
1. **Must NOT modify existing script logic** - Scripts are working
2. **Must use same file paths** - Windows paths with backslashes
3. **Must respect coordination.json format** - Scripts depend on it
4. **Must maintain CSV schemas** - Scripts expect specific columns

---

## 2. ARCHITECTURE OVERVIEW

### 2.1 Hybrid Data Architecture

**Design Decision: Dual Data Layer**

We'll implement a hybrid approach:
- **SQLite Database:** Dashboard-specific data (accounts, verticals metadata, templates)
- **CSV Files:** Shared data layer (prospects, sent logs, responses)

**Rationale:**
1. Scripts continue using CSV files (no changes required)
2. Dashboard gets relational benefits (accounts, templates)
3. Clear separation of concerns
4. Migration path: Dashboard can later wrap CSV access

### 2.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMPAIGN CONTROL CENTER                       │
│                      (Streamlit Dashboard)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Pages      │  │  Components  │  │   Utils      │          │
│  │  (7 pages)   │  │  (Cards,     │  │  (Validators,│          │
│  │              │  │   Charts,    │  │   Formatters)│          │
│  │              │  │   Forms)     │  │              │          │
│  └──────┬───────┘  └──────────────┘  └──────────────┘          │
│         │                                                        │
│  ┌──────▼─────────────────────────────────────────────┐         │
│  │           Integration Layer                        │         │
│  │  - CSV Handler (prospect upload/read)              │         │
│  │  - Tracker Reader (sent/response metrics)          │         │
│  │  - Coordination Reader (status display)            │         │
│  │  - Template Manager (read/write templates)         │         │
│  └──────┬─────────────────────────────────────────────┘         │
│         │                                                        │
│  ┌──────▼─────────────────────────────────────────────┐         │
│  │           Data Access Layer                        │         │
│  │  - Database Models (CRUD operations)               │         │
│  │  - Encryption (password security)                  │         │
│  │  - Windows Path Handler                            │         │
│  └──────┬─────────────────────────────────────────────┘         │
│         │                                                        │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER (DUAL)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐      ┌─────────────────────────────┐ │
│  │  SQLite Database     │      │  CSV Files (Shared)         │ │
│  │  (Dashboard Only)    │      │  (Dashboard + Scripts)      │ │
│  ├──────────────────────┤      ├─────────────────────────────┤ │
│  │ - email_accounts     │      │ - sent_tracker.csv          │ │
│  │ - verticals          │      │ - response_tracker.csv      │ │
│  │ - account_verticals  │      │ - coordination.json         │ │
│  │ - email_templates    │      │ - debarment_prospects.csv   │ │
│  │                      │      │ - food_recall_prospects.csv │ │
│  │                      │      │ - grant_alerts_prospects.csv│ │
│  └──────────────────────┘      └─────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                          ▲
                          │ (Scripts read CSV files unchanged)
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                   EXISTING AUTOMATION SCRIPTS                    │
│  - send_initial_outreach.py                                      │
│  - send_followup.py                                              │
│  - config.py                                                     │
│  - coordination.py                                               │
└──────────────────────────────────────────────────────────────────┘
```

### 2.3 Component Responsibilities

**Streamlit Pages (User Interface):**
- Display metrics, tables, charts
- Handle user input (forms, uploads)
- Route actions to integration layer
- Manage UI state

**Integration Layer (Bridge):**
- Translate between dashboard and existing system
- Read CSV files using pandas
- Parse coordination.json
- Write prospect CSVs in correct format
- Sync templates with config.py (future enhancement)

**Data Access Layer (Persistence):**
- CRUD operations on SQLite
- Password encryption/decryption
- Windows path normalization
- Transaction management

**Existing Scripts (Unchanged):**
- Continue reading config.py
- Continue using coordination.py
- Continue writing to CSV files
- No modifications required

---

## 3. DATA MODEL DESIGN

### 3.1 SQLite Schema Design

```sql
-- ============================================================================
-- TABLE: verticals
-- Stores vertical/business line metadata
-- ============================================================================
CREATE TABLE verticals (
    vertical_id TEXT PRIMARY KEY,           -- e.g., 'debarment', 'food_recall'
    display_name TEXT NOT NULL,             -- e.g., 'Debarment Monitor'
    target_industry TEXT,                   -- e.g., 'Federal Contractors'
    csv_filename TEXT NOT NULL,             -- e.g., 'debarment_prospects.csv'
    active BOOLEAN DEFAULT 1,               -- Enable/disable vertical
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: email_accounts
-- Stores SMTP account credentials and settings
-- ============================================================================
CREATE TABLE email_accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_address TEXT UNIQUE NOT NULL,     -- e.g., 'alec@example.com'
    display_name TEXT,                      -- e.g., 'Alec Kleinman'
    smtp_host TEXT NOT NULL,                -- e.g., 'smtp.gmail.com'
    smtp_port INTEGER NOT NULL,             -- e.g., 587
    smtp_username TEXT NOT NULL,            -- Often same as email_address
    password_encrypted BLOB NOT NULL,       -- Encrypted using cryptography
    daily_send_limit INTEGER NOT NULL,      -- e.g., 450
    active BOOLEAN DEFAULT 1,               -- Enable/disable account
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: account_verticals
-- Many-to-many relationship: which accounts handle which verticals
-- ============================================================================
CREATE TABLE account_verticals (
    account_id INTEGER NOT NULL,
    vertical_id TEXT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (account_id, vertical_id),
    FOREIGN KEY (account_id) REFERENCES email_accounts(account_id) 
        ON DELETE CASCADE,
    FOREIGN KEY (vertical_id) REFERENCES verticals(vertical_id) 
        ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: email_templates
-- Stores email templates (subject + body)
-- Note: Current scripts use templates from config.py
-- This table allows dashboard editing; future: sync to config.py
-- ============================================================================
CREATE TABLE email_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vertical_id TEXT NOT NULL,
    template_type TEXT NOT NULL,            -- 'initial' or 'followup'
    template_name TEXT NOT NULL,            -- e.g., 'Default Initial'
    subject_line TEXT NOT NULL,
    email_body TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vertical_id) REFERENCES verticals(vertical_id) 
        ON DELETE CASCADE,
    UNIQUE(vertical_id, template_type, template_name)
);

-- ============================================================================
-- TABLE: campaign_settings
-- Global settings (business hours, pacing, etc.)
-- ============================================================================
CREATE TABLE campaign_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES for performance
-- ============================================================================
CREATE INDEX idx_templates_vertical ON email_templates(vertical_id);
CREATE INDEX idx_templates_type ON email_templates(template_type);
CREATE INDEX idx_account_verticals_account ON account_verticals(account_id);
CREATE INDEX idx_account_verticals_vertical ON account_verticals(vertical_id);
CREATE INDEX idx_email_accounts_active ON email_accounts(active);
CREATE INDEX idx_verticals_active ON verticals(active);
```

### 3.2 CSV File Schemas (Existing - Read Only for Analysis)

**sent_tracker.csv:**
```csv
timestamp,email,vertical,message_type,subject_line,status,error_message
2025-11-04T09:16:52.821919-05:00,a.closson@synegygroupjv.com,debarment,initial,Debarment monitoring question,SUCCESS,
```

**response_tracker.csv:**
```csv
email,vertical,initial_sent_date,replied,followup_sent_date,notes
grant.dick@usfingroup.com,debarment,2025-11-03,PENDING,,
```

**Prospect CSV Schema (Standard):**
```csv
email,first_name,company_name,state,website
example@company.com,John,Acme Corp,CA,www.acme.com
```

**coordination.json:**
```json
{
  "date": "2025-11-04",
  "last_updated": "2025-11-04T11:42:22.746794-05:00",
  "initial": {
    "allocated": 225,
    "sent": 641,
    "status": "stopped"
  },
  "followup": {
    "allocated": 225,
    "sent": 0,
    "status": "idle"
  }
}
```

### 3.3 Data Flow Patterns

**Pattern 1: Prospect Upload**
```
User uploads CSV → Dashboard validates → Dashboard writes to 
  C:\...\outreach_sequences\{vertical}_prospects.csv
  → Scripts read on next run
```

**Pattern 2: Template Edit**
```
User edits template in dashboard → Save to email_templates table
  → (Future) Sync to config.py or separate template files
  → Scripts read updated templates
```

**Pattern 3: Metrics Display**
```
Dashboard reads sent_tracker.csv → Parse with pandas
  → Calculate metrics (total sent, response rate, etc.)
  → Display in Streamlit charts
```

**Pattern 4: Coordination Status**
```
Dashboard reads coordination.json → Parse JSON
  → Display current allocation, sent counts, status
  → Show real-time campaign progress
```

---

## 4. INTEGRATION STRATEGY

### 4.1 Integration Principles

1. **Non-Invasive:** Dashboard reads existing files without modifying scripts
2. **Bi-Directional:** Dashboard writes files scripts can read (prospects, templates)
3. **Atomic Operations:** File writes are atomic to prevent corruption
4. **Schema Compliance:** Dashboard writes CSVs with exact column order scripts expect
5. **Path Consistency:** Use same Windows paths from config.py

### 4.2 Integration Points Detail

#### Integration Point 1: Prospect Management

**Current State:**
- Scripts read: `debarment_prospects.csv`, `food_recall_prospects.csv`, etc.
- Expected columns: `email, first_name, company_name, state, website`

**Dashboard Integration:**
1. Upload CSV via drag-and-drop
2. Validate columns match expected schema
3. Deduplicate against existing prospects (by email)
4. Write to correct vertical CSV file
5. Scripts automatically pick up new prospects on next run

**Implementation:**
```python
# Pseudo-code
def upload_prospects(vertical_id, uploaded_file):
    # Read uploaded CSV
    df = pd.read_csv(uploaded_file)
    
    # Validate schema
    required_cols = ['email', 'first_name', 'company_name', 'state', 'website']
    if not all(col in df.columns for col in required_cols):
        raise ValidationError("Missing required columns")
    
    # Load existing prospects
    csv_path = get_vertical_csv_path(vertical_id)
    existing_df = pd.read_csv(csv_path) if os.exists(csv_path) else pd.DataFrame()
    
    # Deduplicate
    new_df = df[~df['email'].isin(existing_df['email'])]
    
    # Append to file
    combined_df = pd.concat([existing_df, new_df])
    combined_df.to_csv(csv_path, index=False)
    
    return len(new_df)  # Count of new prospects added
```

#### Integration Point 2: Metrics Reading

**Current State:**
- Scripts append to `sent_tracker.csv` after each send
- Format: `timestamp,email,vertical,message_type,subject_line,status,error_message`

**Dashboard Integration:**
1. Read entire CSV on page load (with caching)
2. Parse timestamps, group by date/vertical
3. Calculate metrics:
   - Total sent all-time
   - Sent today/this week/this month
   - Sent by vertical
   - Success rate (SUCCESS vs errors)
4. Display in charts and metric cards

**Implementation:**
```python
# Pseudo-code with Streamlit caching
@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_sent_tracker():
    df = pd.read_csv(config.SENT_TRACKER)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    return df

def calculate_metrics(df, vertical_filter='all'):
    if vertical_filter != 'all':
        df = df[df['vertical'] == vertical_filter]
    
    total_sent = len(df)
    sent_today = len(df[df['date'] == datetime.now().date()])
    # ... more calculations
    
    return {
        'total_sent': total_sent,
        'sent_today': sent_today,
        # ...
    }
```

#### Integration Point 3: Coordination Status

**Current State:**
- Scripts write to `coordination.json` (daily state)
- Format: `{date, last_updated, initial: {allocated, sent, status}, followup: {...}}`

**Dashboard Integration:**
1. Read coordination.json
2. Display current allocation and status
3. Show remaining capacity
4. (Future) Allow pause/resume via coordination updates

**Implementation:**
```python
def load_coordination_status():
    with open(COORDINATION_FILE, 'r') as f:
        coord = json.load(f)
    
    return {
        'date': coord['date'],
        'initial_sent': coord['initial']['sent'],
        'initial_allocated': coord['initial']['allocated'],
        'initial_remaining': coord['initial']['allocated'] - coord['initial']['sent'],
        'initial_status': coord['initial']['status'],
        # ... similar for followup
    }
```

#### Integration Point 4: Template Management (Phase 2)

**Current State:**
- Templates hardcoded in `config.py` as Python strings
- Scripts read from `config.VERTICALS[vertical]['initial_template']`

**Dashboard Integration (Two Options):**

**Option A: Template Files (Recommended)**
1. Create `verticals/{vertical_id}/templates/` directory structure
2. Store templates as text files: `initial_default.txt`, `followup_default.txt`
3. Modify config.py to read from files instead of hardcoded strings
4. Dashboard edits files, scripts read files

**Option B: Config.py Rewriting (Risky)**
1. Dashboard parses config.py
2. Modifies template string sections
3. Writes back to config.py
4. Risk: Could break config.py syntax

**Recommendation: Use Option A (Template Files)**

### 4.3 Windows Path Compatibility Strategy

**Problem:** Windows uses backslashes; mixing separators causes issues

**Solution: Path Normalization Layer**

```python
# utils/windows_paths.py

import os
import platform

def normalize_path(path):
    """
    Normalize path for current OS.
    On Windows, ensures backslashes.
    """
    return os.path.normpath(path)

def join_path(*parts):
    """
    Safe path joining that works on all OS.
    """
    return os.path.join(*parts)

def get_base_dir():
    """
    Get base directory from config, normalized.
    """
    # Read from config.py or settings
    base = r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"
    return normalize_path(base)

def get_vertical_csv_path(vertical_id):
    """
    Get path to vertical's prospect CSV.
    """
    filename = f"{vertical_id}_prospects.csv"
    return join_path(get_base_dir(), filename)

def get_database_path():
    """
    Get path to SQLite database.
    """
    return join_path(get_base_dir(), "campaign_control.db")
```

**Usage:**
- ALL file operations use these helpers
- Never hardcode paths in dashboard code
- Always use `os.path.join()` or helper functions

### 4.4 Migration Strategy for Existing Data

**Initial Setup (First Run):**

1. **Detect existing verticals:**
   - Scan for `*_prospects.csv` files
   - Parse filenames to get vertical IDs
   - Populate `verticals` table

2. **Import existing templates:**
   - Read templates from config.py
   - Insert into `email_templates` table
   - Mark as active

3. **Seed email account (from env vars):**
   - Read SMTP settings from environment
   - Encrypt password
   - Create first account
   - Assign to all detected verticals

4. **Calculate initial metrics:**
   - Load sent_tracker.csv
   - Display historical data immediately

**Migration Function:**
```python
def initialize_dashboard():
    """
    First-time setup: populate database from existing files.
    """
    # Create database and tables
    db.create_schema()
    
    # Detect verticals
    for csv_file in glob.glob(os.path.join(BASE_DIR, "*_prospects.csv")):
        vertical_id = extract_vertical_id(csv_file)
        display_name = config.VERTICALS.get(vertical_id, {}).get('name', vertical_id)
        
        db.create_vertical(
            vertical_id=vertical_id,
            display_name=display_name,
            csv_filename=os.path.basename(csv_file)
        )
    
    # Import templates from config.py
    for vertical_id, vertical_config in config.VERTICALS.items():
        db.create_template(
            vertical_id=vertical_id,
            template_type='initial',
            subject_line=vertical_config['initial_subject_lines'][0],
            email_body=vertical_config['initial_template']
        )
        # ... same for followup
    
    # Create default email account from env vars
    if config.YOUR_EMAIL:
        db.create_email_account(
            email_address=config.YOUR_EMAIL,
            smtp_host=config.SMTP_SERVER,
            smtp_port=config.SMTP_PORT,
            password=config.APP_PASSWORD,
            daily_limit=config.TOTAL_DAILY_LIMIT
        )
```

---

## 5. FILE STRUCTURE

### 5.1 Complete Directory Layout

```
C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\
│
├── Email Campaign 2025-11-3\          # Existing scripts (unchanged)
│   ├── config.py
│   ├── coordination.py
│   ├── send_initial_outreach.py
│   ├── send_followup.py
│   └── venv\
│
├── Email Outreach Dashboard\          # NEW: Dashboard project
│   ├── dashboard.py                   # Main Streamlit entry point
│   │
│   ├── database\                      # Database layer
│   │   ├── __init__.py
│   │   ├── schema.py                  # Schema definition + initialization
│   │   ├── models.py                  # CRUD operations
│   │   └── encryption.py              # Password encryption utilities
│   │
│   ├── integrations\                  # Integration with existing system
│   │   ├── __init__.py
│   │   ├── csv_handler.py             # Read/write prospect CSVs
│   │   ├── tracker_reader.py          # Parse sent/response trackers
│   │   ├── coordination_reader.py     # Parse coordination.json
│   │   └── template_manager.py        # Template file operations
│   │
│   ├── pages\                         # Streamlit pages (7 pages)
│   │   ├── __init__.py
│   │   ├── 1_📊_Dashboard.py          # Home page (metrics, charts)
│   │   ├── 2_📥_Prospects.py          # Prospect upload/management
│   │   ├── 3_📧_Email_Accounts.py     # Account management
│   │   ├── 4_🔧_Verticals.py          # Vertical management
│   │   ├── 5_✉️_Templates.py          # Template editor
│   │   ├── 6_📅_Planner.py            # Campaign planning
│   │   └── 7_⚙️_Settings.py           # Global settings
│   │
│   ├── components\                    # Reusable UI components
│   │   ├── __init__.py
│   │   ├── cards.py                   # Metric cards
│   │   ├── charts.py                  # Plotly chart wrappers
│   │   ├── forms.py                   # Form components
│   │   └── tables.py                  # Data table components
│   │
│   ├── utils\                         # Utilities
│   │   ├── __init__.py
│   │   ├── validators.py              # Input validation
│   │   ├── formatters.py              # Data formatting
│   │   └── windows_paths.py           # Windows path handling
│   │
│   ├── tests\                         # Test suite
│   │   ├── __init__.py
│   │   ├── test_database.py           # Database tests
│   │   ├── test_integrations.py       # Integration tests
│   │   ├── test_validators.py         # Validation tests
│   │   └── fixtures\                  # Test data
│   │       ├── sample_prospects.csv
│   │       └── sample_sent_tracker.csv
│   │
│   ├── docs\                          # Documentation
│   │   ├── SETUP_INSTRUCTIONS.md      # Detailed setup guide
│   │   ├── TROUBLESHOOTING.md         # Common issues
│   │   └── API_REFERENCE.md           # Function documentation
│   │
│   ├── requirements.txt               # Python dependencies
│   ├── README.md                      # Project overview
│   ├── .streamlit\                    # Streamlit config
│   │   └── config.toml                # Theme, settings
│   └── .gitignore
│
├── campaign_control.db                # NEW: SQLite database
│
├── sent_tracker.csv                   # Existing (read by dashboard)
├── response_tracker.csv               # Existing (read by dashboard)
├── error_log.csv                      # Existing (read by dashboard)
├── coordination.json                  # Existing (read by dashboard)
│
├── debarment_prospects.csv            # Existing (read/write by dashboard)
├── food_recall_prospects.csv          # Existing (read/write by dashboard)
└── grant_alerts_prospects.csv         # Existing (read/write by dashboard)
```

### 5.2 Key Files Explained

**dashboard.py (Main Entry Point):**
```python
"""
Campaign Control Center - Main Dashboard

Launch: streamlit run dashboard.py
"""

import streamlit as st
from database import models
from utils.windows_paths import get_database_path

# Page config
st.set_page_config(
    page_title="Campaign Control Center",
    page_icon="📊",
    layout="wide"
)

# Initialize database on first run
if not models.database_exists():
    models.initialize_database()

# Main page (or redirect to pages/)
st.title("📊 Campaign Control Center")
st.write("Welcome to the Email Campaign Dashboard")
# ... metrics display ...
```

**database/schema.py:**
- Contains SQL schema definitions
- `create_tables()` function
- Database initialization logic

**database/models.py:**
- CRUD functions for each table
- `get_verticals()`, `create_vertical()`, `update_vertical()`, etc.
- `get_email_accounts()`, `create_email_account()`, etc.
- Query builders with parameterization

**database/encryption.py:**
- Password encryption using `cryptography` library
- `encrypt_password(plain_text) -> bytes`
- `decrypt_password(encrypted) -> str`
- Key management (stored in settings or env)

**integrations/csv_handler.py:**
- `read_prospects(vertical_id) -> DataFrame`
- `write_prospects(vertical_id, dataframe)`
- `validate_prospect_csv(dataframe) -> bool`
- `deduplicate_prospects(new_df, existing_df) -> DataFrame`

**integrations/tracker_reader.py:**
- `read_sent_tracker() -> DataFrame`
- `read_response_tracker() -> DataFrame`
- `calculate_metrics(df, filters) -> dict`
- `get_response_rate(sent_df, response_df) -> float`

**integrations/coordination_reader.py:**
- `read_coordination() -> dict`
- `get_allocation_status() -> dict`
- `get_remaining_capacity(script_type) -> int`
- (Future) `update_coordination_status(updates)`

**components/cards.py:**
- `metric_card(title, value, delta, icon)`
- `status_card(title, status, details)`
- `account_card(account_data)`

**components/charts.py:**
- `line_chart_emails_over_time(df)`
- `bar_chart_by_vertical(df)`
- `donut_chart_response_rates(data)`
- All use Plotly for interactivity

---

## 6. TECHNICAL DECISIONS

### 6.1 Technology Stack Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Dashboard Framework** | Streamlit | Fast development, Python-native, excellent for data apps |
| **Database** | SQLite | No server needed, file-based, perfect for single-user dashboard |
| **Data Processing** | Pandas | CSV manipulation, powerful analytics, integrates with Streamlit |
| **Charts** | Plotly | Interactive, professional, works well with Streamlit |
| **Encryption** | cryptography (Fernet) | Industry-standard, symmetric encryption for passwords |
| **Date/Time** | pytz | Timezone support (EST), consistent with existing scripts |

### 6.2 Key Design Decisions

**Decision 1: Hybrid Data Layer (SQLite + CSV)**

**Options Considered:**
- A) Pure SQLite (migrate all CSV data)
- B) Pure CSV (no database)
- C) Hybrid (database for dashboard data, CSV for shared data)

**Chosen: C (Hybrid)**

**Rationale:**
- Scripts continue working without modification
- Dashboard gets relational benefits
- Clear separation: dashboard owns database, both share CSVs
- Future migration path available

**Trade-offs:**
- Slight complexity maintaining two data layers
- Must keep schemas in sync
- Worth it for zero-impact on existing scripts

---

**Decision 2: Template Storage Approach**

**Options Considered:**
- A) Hardcode in config.py (current approach)
- B) Store in database only
- C) Store in database + sync to text files
- D) Store as text files, read by both dashboard and scripts

**Chosen: C (Database + Text Files) - Phase 2**

**Initial Implementation (Phase 1):**
- Templates in database for dashboard editing
- Scripts continue using config.py
- Manual sync needed

**Future Enhancement (Phase 2):**
- Dashboard writes to both database and text files
- Modify config.py to read from files
- Full two-way sync

**Rationale:**
- Phase 1 is safer (no config.py changes)
- Phase 2 enables full integration
- User can test dashboard before modifying scripts

---

**Decision 3: Windows Path Handling**

**Approach:**
- Centralize all path operations in `utils/windows_paths.py`
- Use `os.path.join()` exclusively
- Never hardcode paths with slashes
- Test on Windows from day 1

**Implementation:**
```python
# WRONG
path = "C:/folder/file.csv"  # Forward slash on Windows

# CORRECT
from utils.windows_paths import join_path, get_base_dir
path = join_path(get_base_dir(), "file.csv")
```

---

**Decision 4: Caching Strategy**

**Streamlit Caching:**
```python
@st.cache_data(ttl=60)  # 60 second TTL
def load_sent_tracker():
    # Expensive CSV read
    pass

@st.cache_resource
def get_database_connection():
    # Singleton database connection
    pass
```

**Rationale:**
- CSV reads are expensive (10,000+ rows)
- Cache for 60 seconds (near-real-time)
- Database connection is singleton
- Improves dashboard responsiveness

---

**Decision 5: Error Handling Strategy**

**Approach: Defensive Programming**

```python
def read_prospects(vertical_id):
    try:
        csv_path = get_vertical_csv_path(vertical_id)
        
        if not os.path.exists(csv_path):
            # Return empty DataFrame with correct schema
            return pd.DataFrame(columns=['email', 'first_name', 'company_name', 'state', 'website'])
        
        df = pd.read_csv(csv_path)
        return df
        
    except pd.errors.EmptyDataError:
        st.warning(f"Prospect file for {vertical_id} is empty")
        return pd.DataFrame(columns=['email', 'first_name', 'company_name', 'state', 'website'])
        
    except Exception as e:
        st.error(f"Error reading prospects: {str(e)}")
        log_error("read_prospects", vertical_id, str(e))
        return pd.DataFrame(columns=['email', 'first_name', 'company_name', 'state', 'website'])
```

**Principles:**
- Never crash the dashboard
- User-friendly error messages
- Log errors to error_log.csv
- Graceful degradation (show empty data instead of crash)

---

**Decision 6: Security Approach**

**Password Storage:**
- Encrypt using Fernet (symmetric encryption)
- Key stored in environment variable or settings table
- Never store plain-text passwords
- Decrypt only when needed for SMTP connection

**SQL Injection Prevention:**
- Use parameterized queries exclusively
- Never string concatenation in SQL
- SQLite3 library handles escaping

**File Upload Security:**
- Validate file extensions (.csv only)
- Validate file size (< 10MB)
- Scan for malicious content (basic check)
- Sanitize filenames

---

## 7. WORK BREAKDOWN

### 7.1 Team Structure

**Multi-Agent Team:**
1. **Project Manager / Architect** (This document's author)
2. **Database Engineer**
3. **Backend Developer**
4. **Frontend Developer**
5. **QA / Testing Specialist**

### 7.2 Agent Responsibilities

#### Agent 1: Project Manager / Architect

**Deliverables:**
- [ ] Implementation plan (this document)
- [ ] SETUP_INSTRUCTIONS.md
- [ ] TROUBLESHOOTING.md
- [ ] README.md
- [ ] Integration coordination
- [ ] Final review and approval

**Tasks:**
1. Review all requirements
2. Design architecture
3. Make technical decisions
4. Create work breakdown
5. Coordinate agents
6. Write documentation
7. Test end-to-end integration
8. Approve deliverables

---

#### Agent 2: Database Engineer

**Deliverables:**
- [ ] database/schema.py (full schema)
- [ ] database/models.py (CRUD layer)
- [ ] database/encryption.py (password security)
- [ ] Database initialization script
- [ ] Migration utilities
- [ ] tests/test_database.py

**Tasks:**

**Phase 1: Schema Design (30 minutes)**
1. Implement schema.py
   - Create CREATE TABLE statements
   - Add indexes
   - Add constraints
   - Write `create_schema()` function

**Phase 2: CRUD Layer (60 minutes)**
2. Implement models.py
   - Verticals: create, read, update, delete, list
   - Email Accounts: create, read, update, delete, list
   - Account-Vertical assignments: assign, unassign, list
   - Templates: create, read, update, delete, list by vertical
   - Settings: get, set
   - Connection management

**Phase 3: Security (30 minutes)**
3. Implement encryption.py
   - Generate encryption key
   - Encrypt password function
   - Decrypt password function
   - Key storage strategy

**Phase 4: Testing (30 minutes)**
4. Write database tests
   - Test schema creation
   - Test all CRUD operations
   - Test cascade deletes
   - Test encryption/decryption
   - Test concurrent access

**Acceptance Criteria:**
- All tables created with correct schema
- CRUD operations work for all entities
- Passwords encrypted securely
- Tests pass 100%
- No SQL injection vulnerabilities

---

#### Agent 3: Backend Developer

**Deliverables:**
- [ ] integrations/csv_handler.py
- [ ] integrations/tracker_reader.py
- [ ] integrations/coordination_reader.py
- [ ] integrations/template_manager.py
- [ ] utils/validators.py
- [ ] utils/formatters.py
- [ ] utils/windows_paths.py
- [ ] tests/test_integrations.py

**Tasks:**

**Phase 1: Path Utilities (15 minutes)**
1. Implement windows_paths.py
   - `get_base_dir()`
   - `get_vertical_csv_path(vertical_id)`
   - `get_database_path()`
   - `join_path(*parts)`
   - `normalize_path(path)`

**Phase 2: CSV Handler (45 minutes)**
2. Implement csv_handler.py
   - `read_prospects(vertical_id) -> DataFrame`
   - `write_prospects(vertical_id, df)`
   - `append_prospects(vertical_id, df)`
   - `validate_prospect_schema(df) -> bool`
   - `deduplicate_by_email(df) -> DataFrame`
   - `get_prospect_count(vertical_id) -> int`

**Phase 3: Tracker Reader (45 minutes)**
3. Implement tracker_reader.py
   - `read_sent_tracker() -> DataFrame`
   - `read_response_tracker() -> DataFrame`
   - `get_sent_count(filters) -> int`
   - `get_sent_by_date(date) -> DataFrame`
   - `get_sent_by_vertical(vertical) -> DataFrame`
   - `calculate_response_rate(vertical=None) -> float`
   - `get_error_rate() -> float`

**Phase 4: Coordination Reader (30 minutes)**
4. Implement coordination_reader.py
   - `read_coordination() -> dict`
   - `get_allocation_status() -> dict`
   - `get_daily_summary() -> dict`
   - `is_capacity_available() -> bool`

**Phase 5: Validators (30 minutes)**
5. Implement validators.py
   - `validate_email(email) -> bool`
   - `validate_csv_schema(df, required_columns) -> bool`
   - `validate_smtp_settings(host, port, username, password) -> bool`
   - `validate_vertical_id(vertical_id) -> bool`
   - `sanitize_filename(filename) -> str`

**Phase 6: Formatters (30 minutes)**
6. Implement formatters.py
   - `format_number(num) -> str` (e.g., 1234 -> "1,234")
   - `format_percentage(num) -> str` (e.g., 0.125 -> "12.5%")
   - `format_datetime(dt) -> str`
   - `format_date(dt) -> str`
   - `truncate_text(text, length) -> str`

**Phase 7: Testing (30 minutes)**
7. Write integration tests
   - Test CSV read/write
   - Test tracker parsing
   - Test coordination parsing
   - Test Windows path handling
   - Test validators with edge cases

**Acceptance Criteria:**
- All CSV operations work correctly
- Tracker files parsed accurately
- Windows paths work correctly
- Validators catch invalid inputs
- Tests pass 100%
- No file corruption issues

---

#### Agent 4: Frontend Developer (Streamlit)

**Deliverables:**
- [ ] dashboard.py (main entry point)
- [ ] pages/1_📊_Dashboard.py
- [ ] pages/2_📥_Prospects.py
- [ ] pages/3_📧_Email_Accounts.py
- [ ] pages/4_🔧_Verticals.py
- [ ] pages/5_✉️_Templates.py
- [ ] pages/6_📅_Planner.py
- [ ] pages/7_⚙️_Settings.py
- [ ] components/cards.py
- [ ] components/charts.py
- [ ] components/forms.py
- [ ] components/tables.py
- [ ] .streamlit/config.toml

**Tasks:**

**Phase 1: Setup (15 minutes)**
1. Create dashboard.py
   - Page config
   - Database initialization check
   - Navigation
   - Welcome screen

2. Create .streamlit/config.toml
   - Theme settings
   - Layout preferences

**Phase 2: Components (60 minutes)**
3. Implement cards.py
   - `metric_card(title, value, delta, icon)`
   - `status_card(title, status, color, icon)`
   - `account_card(account_info)`
   - `vertical_card(vertical_info)`

4. Implement charts.py
   - `line_chart_emails_over_time(df, verticals_filter)`
   - `bar_chart_by_vertical(df)`
   - `donut_chart_response_rates(response_data)`
   - `progress_bar_quota(sent, limit)`

5. Implement forms.py
   - `email_account_form()`
   - `vertical_form()`
   - `template_editor_form()`
   - `settings_form()`

6. Implement tables.py
   - `prospect_table(df, editable=False)`
   - `account_table(accounts)`
   - `vertical_table(verticals)`
   - `template_table(templates)`

**Phase 3: Page 1 - Dashboard (45 minutes)**
7. Implement 1_📊_Dashboard.py
   - Top metrics row (5 cards)
   - Vertical dropdown selector
   - Metrics update based on selection
   - Line chart: emails over time
   - Bar chart: emails by vertical today
   - Donut chart: response rates
   - Email account status table
   - Campaign status from coordination.json

**Phase 4: Page 2 - Prospects (45 minutes)**
8. Implement 2_📥_Prospects.py
   - Vertical selector tabs
   - File uploader for each vertical
   - CSV validation on upload
   - Deduplication logic
   - Upload statistics
   - Prospect table viewer
   - Filter: status (not contacted / initial sent / followup sent / responded)
   - Search box
   - Export button

**Phase 5: Page 3 - Email Accounts (45 minutes)**
9. Implement 3_📧_Email_Accounts.py
   - Account list table
   - Add account button → form modal
   - Edit account → pre-filled form
   - Delete account with confirmation
   - Test SMTP connection button
   - Account-vertical assignment matrix
   - Capacity summary

**Phase 6: Page 4 - Verticals (30 minutes)**
10. Implement 4_🔧_Verticals.py
    - Vertical list table
    - Add vertical button → form
    - Edit vertical → form
    - Delete vertical with confirmation (archives folder)
    - Vertical statistics (prospect count, templates)
    - Create folder structure on add

**Phase 7: Page 5 - Templates (60 minutes)**
11. Implement 5_✉️_Templates.py
    - Vertical selector
    - Template list for selected vertical
    - Add template button
    - Template editor:
      - Template type dropdown (Initial/Followup)
      - Template name input
      - Subject line input
      - Body textarea (large)
      - Available variables display
      - Live preview pane
    - Save button
    - Delete button with confirmation

**Phase 8: Page 6 - Planner (45 minutes)**
12. Implement 6_📅_Planner.py
    - Today's plan table (from coordination.json)
    - Weekly forecast table
    - Capacity calculator tool
    - Pause/Resume campaign buttons
    - Manual override controls
    - Send schedule visualization

**Phase 9: Page 7 - Settings (30 minutes)**
13. Implement 7_⚙️_Settings.py
    - Global settings form
    - Business hours settings
    - Anti-spam settings
    - File paths (display only)
    - Data management tools
    - System info display

**Phase 10: Styling & Polish (30 minutes)**
14. Improve UI/UX
    - Consistent color scheme
    - Proper spacing
    - Icons for all pages
    - Loading spinners
    - Success/error messages
    - Responsive layout

**Acceptance Criteria:**
- All 7 pages load without errors
- All forms validate inputs
- All tables display data correctly
- Charts render properly
- File uploads work
- UI is professional and intuitive
- No layout issues

---

#### Agent 5: QA / Testing Specialist

**Deliverables:**
- [ ] Test plan document
- [ ] Test results report
- [ ] tests/fixtures/ (sample data)
- [ ] Bug reports (if any)
- [ ] Performance benchmarks
- [ ] Windows compatibility report

**Tasks:**

**Phase 1: Test Planning (30 minutes)**
1. Create comprehensive test plan
   - Database tests
   - Integration tests
   - UI tests
   - Windows compatibility tests
   - Edge case tests

**Phase 2: Create Test Fixtures (30 minutes)**
2. Generate test data
   - Sample prospect CSVs (valid + invalid)
   - Sample sent_tracker.csv
   - Sample response_tracker.csv
   - Sample coordination.json
   - Large CSV files (10,000 rows) for performance testing

**Phase 3: Database Testing (45 minutes)**
3. Test all CRUD operations
   - Create vertical → verify in DB
   - Create email account → verify encryption
   - Assign account to vertical → verify relationship
   - Delete vertical → verify cascade
   - Update template → verify changes
   - Concurrent access → verify no corruption

**Phase 4: Integration Testing (60 minutes)**
4. Test file operations
   - Upload valid CSV → verify file written
   - Upload invalid CSV → verify error message
   - Read sent_tracker.csv → verify metrics correct
   - Read coordination.json → verify status display
   - Write prospect CSV → scripts can read it
   - Large file handling (10,000 rows)

**Phase 5: UI Testing (90 minutes)**
5. Test all pages
   - Dashboard page: metrics update correctly
   - Prospects page: upload, view, filter, search
   - Email Accounts page: add, edit, delete, test connection
   - Verticals page: add, edit, delete, view stats
   - Templates page: edit, save, preview
   - Planner page: display, forecast, controls
   - Settings page: save changes

**Phase 6: Edge Cases (45 minutes)**
6. Test edge cases
   - Empty database (first run)
   - No prospects loaded
   - No verticals created
   - Invalid SMTP credentials
   - Malformed CSV files
   - Large CSV files (100,000 rows)
   - Concurrent file access
   - Disk space issues

**Phase 7: Windows Compatibility (45 minutes)**
7. Test on Windows
   - Dashboard launches correctly
   - All file paths work
   - CSV uploads work
   - Database creation works
   - No path separator issues
   - SMTP connection works

**Phase 8: Performance Testing (30 minutes)**
8. Benchmark performance
   - Load time with 10,000 sent emails
   - Chart rendering time
   - CSV upload time (1,000 rows)
   - Database query performance
   - Page navigation speed

**Phase 9: Integration with Scripts (60 minutes)**
9. Test dashboard + scripts interaction
   - Dashboard uploads prospects → scripts send emails
   - Scripts write sent_tracker → dashboard shows metrics
   - Dashboard creates vertical → scripts can use it
   - Dashboard edits template → scripts use new template
   - Coordination status updates correctly

**Phase 10: Documentation Review (30 minutes)**
10. Review all documentation
    - SETUP_INSTRUCTIONS.md is accurate
    - TROUBLESHOOTING.md covers common issues
    - README.md is clear
    - Code comments are helpful

**Phase 11: Create Test Report (30 minutes)**
11. Document all findings
    - Test summary (pass/fail counts)
    - Bug reports with reproduction steps
    - Performance metrics
    - Recommendations for improvements

**Acceptance Criteria:**
- 95%+ tests passing
- All critical bugs fixed
- Windows compatibility confirmed
- Performance meets requirements (<3s page load)
- Documentation is accurate
- Integration with scripts verified

---

### 7.3 Task Dependencies

```
Project Manager creates plan
         ↓
Database Engineer creates schema
         ↓
Backend Developer builds integration layer
         ↓
Frontend Developer builds UI
         ↓
QA tests everything
         ↓
Project Manager writes documentation
         ↓
Final integration testing
         ↓
DEPLOYMENT
```

**Critical Path:**
1. PM: Architecture design (this document)
2. DB Engineer: Schema + CRUD layer
3. Backend: Integration layer (depends on schema)
4. Frontend: UI (depends on integration layer)
5. QA: Testing (depends on all above)
6. PM: Documentation (depends on QA results)

**Parallelizable Work:**
- DB Engineer + Backend can work concurrently after schema done
- Frontend can start on components while backend builds integrations
- QA can write test plan while development ongoing

---

## 8. RISK ASSESSMENT

### 8.1 Technical Risks

**Risk 1: Breaking Existing Scripts**
- **Probability:** Medium
- **Impact:** Critical
- **Mitigation:**
  - Read-only integration initially
  - Extensive testing before modifying shared files
  - Version control for all changes
  - Backup existing files before dashboard writes

**Risk 2: Windows Path Issues**
- **Probability:** High
- **Impact:** High
- **Mitigation:**
  - Centralized path handling from day 1
  - Test on Windows early and often
  - Use os.path.join() exclusively
  - Code review for hardcoded paths

**Risk 3: CSV File Corruption**
- **Probability:** Low
- **Impact:** Critical
- **Mitigation:**
  - Atomic file writes (write to temp, then rename)
  - File locking during writes
  - Backup before write operations
  - Validation before and after writes

**Risk 4: Database Corruption**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - Use transactions for all writes
  - Regular backups
  - Database integrity checks
  - Easy re-initialization from existing data

**Risk 5: Password Security**
- **Probability:** Medium
- **Impact:** Critical
- **Mitigation:**
  - Use industry-standard encryption (Fernet)
  - Never log passwords
  - Secure key storage
  - Decrypt only when needed

### 8.2 Integration Risks

**Risk 6: Template Sync Issues**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Phase 1: Manual sync acceptable
  - Clear documentation on template workflow
  - Phase 2: Automated sync
  - Validation on both sides

**Risk 7: Coordination.json Conflicts**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Dashboard reads only (no writes initially)
  - If writes needed: file locking
  - Atomic JSON writes
  - Validation on read

**Risk 8: Metrics Calculation Errors**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Extensive unit tests
  - Cross-validate with manual counts
  - Clear metric definitions
  - Show sample size with metrics

### 8.3 Usability Risks

**Risk 9: Complex Setup Process**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Extremely detailed SETUP_INSTRUCTIONS.md
  - Screenshots in documentation
  - Automated initialization script
  - Helpful error messages

**Risk 10: Confusing UI**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - Intuitive navigation
  - Clear labels and tooltips
  - Consistent design patterns
  - User testing during development

### 8.4 Performance Risks

**Risk 11: Slow Dashboard with Large Data**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Streamlit caching (60s TTL)
  - Lazy loading
  - Pagination for large tables
  - Database indexes
  - Performance benchmarks

**Risk 12: Memory Issues**
- **Probability:** Low
- **Impact:** Low
- **Mitigation:**
  - Stream large CSV files
  - Clear cache periodically
  - Monitor memory usage
  - Optimize pandas operations

---

## 9. IMPLEMENTATION TIMELINE

### 9.1 Estimated Effort

| Agent | Estimated Time | Tasks |
|-------|----------------|-------|
| **Project Manager** | 3 hours | Planning, coordination, documentation |
| **Database Engineer** | 2.5 hours | Schema, CRUD, encryption, tests |
| **Backend Developer** | 4 hours | Integrations, validators, utilities, tests |
| **Frontend Developer** | 6 hours | 7 pages, components, styling |
| **QA Specialist** | 6 hours | Test plan, testing, reporting |
| **Total** | ~21.5 hours | |

### 9.2 Phased Approach

**Phase 1: Foundation (Hours 0-3)**
- PM: Create implementation plan ✓
- DB Engineer: Schema + basic CRUD
- Backend: Path utilities + CSV handler

**Phase 2: Integration (Hours 3-6)**
- DB Engineer: Complete CRUD + encryption
- Backend: Tracker reader + coordination reader
- Frontend: Components (cards, charts, forms)

**Phase 3: UI Development (Hours 6-12)**
- Frontend: Pages 1-4 (Dashboard, Prospects, Accounts, Verticals)
- Backend: Validators + formatters
- DB Engineer: Testing

**Phase 4: UI Completion (Hours 12-16)**
- Frontend: Pages 5-7 (Templates, Planner, Settings)
- Frontend: Styling and polish
- QA: Test plan + fixtures

**Phase 5: Testing (Hours 16-20)**
- QA: All testing phases
- Bug fixes by respective agents
- Integration testing

**Phase 6: Documentation (Hours 20-22)**
- PM: SETUP_INSTRUCTIONS.md
- PM: TROUBLESHOOTING.md
- PM: README.md
- QA: Test report

**Phase 7: Final Review (Hours 22-24)**
- PM: End-to-end testing
- All agents: Code review
- Final adjustments
- Deployment preparation

---

## 10. SUCCESS METRICS

### 10.1 Functional Completeness

- [ ] All 7 pages implemented
- [ ] All CRUD operations working
- [ ] CSV upload/download working
- [ ] Metrics display accurately
- [ ] Charts render correctly
- [ ] Forms validate inputs
- [ ] Database operations secure

### 10.2 Integration Success

- [ ] Dashboard reads sent_tracker.csv
- [ ] Dashboard reads response_tracker.csv
- [ ] Dashboard reads coordination.json
- [ ] Dashboard writes prospect CSVs scripts can read
- [ ] Templates editable (Phase 1: DB only)
- [ ] Existing scripts continue working unchanged

### 10.3 Windows Compatibility

- [ ] Runs on Windows 10/11
- [ ] All file paths work
- [ ] No path separator errors
- [ ] CSV operations work
- [ ] Database creation works

### 10.4 Quality Metrics

- [ ] 95%+ test coverage
- [ ] 0 critical bugs
- [ ] <3 seconds page load time
- [ ] <5 seconds large CSV upload
- [ ] No security vulnerabilities

### 10.5 Documentation Quality

- [ ] SETUP_INSTRUCTIONS.md complete
- [ ] TROUBLESHOOTING.md comprehensive
- [ ] README.md clear
- [ ] Code well-commented
- [ ] API documented

---

## 11. NEXT STEPS

### 11.1 Immediate Actions

1. **Project Manager:**
   - Share this plan with all agents
   - Create GitHub/project repository
   - Set up communication channels
   - Assign tasks

2. **Database Engineer:**
   - Start schema.py implementation
   - Create database/__init__.py structure
   - Begin CRUD layer design

3. **Backend Developer:**
   - Implement windows_paths.py
   - Set up integrations/ directory structure
   - Prepare test fixtures

4. **Frontend Developer:**
   - Set up Streamlit project structure
   - Create .streamlit/config.toml
   - Start component library

5. **QA Specialist:**
   - Write detailed test plan
   - Create sample data fixtures
   - Set up testing environment

### 11.2 Pre-Development Checklist

- [ ] All agents have reviewed this plan
- [ ] Questions/concerns addressed
- [ ] Development environment set up (Windows)
- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Initial dependencies installed
- [ ] Git repository initialized (if applicable)
- [ ] Backup of existing system created

### 11.3 Development Workflow

1. **Daily Standup:** Sync progress, blockers
2. **Code Reviews:** All code reviewed by PM
3. **Continuous Testing:** QA tests as features complete
4. **Integration Checkpoints:** Test dashboard + scripts together
5. **Documentation Updates:** Keep docs in sync with code

---

## 12. APPENDIX

### 12.1 Configuration File Reference

**config.py Key Values:**
```python
BASE_DIR = r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"
TOTAL_DAILY_LIMIT = 450
BUSINESS_HOURS_START = 9
BUSINESS_HOURS_END = 15
TIMEZONE = 'US/Eastern'

VERTICALS = {
    'food_recall': {...},
    'debarment': {...},
    'grant_alerts': {...}
}
```

### 12.2 Coordination.json Schema

```json
{
  "date": "YYYY-MM-DD",
  "last_updated": "ISO8601 timestamp",
  "initial": {
    "allocated": 225,
    "sent": 0,
    "status": "idle|running|stopped"
  },
  "followup": {
    "allocated": 225,
    "sent": 0,
    "status": "idle|running|stopped"
  }
}
```

### 12.3 Prospect CSV Schema

```csv
email,first_name,company_name,state,website
john@example.com,John,Acme Corp,CA,www.acme.com
```

**Required Columns:**
- `email` (unique identifier)
- `first_name` (can be empty)
- `company_name`
- `state`
- `website` (can be empty)

### 12.4 Sent Tracker Schema

```csv
timestamp,email,vertical,message_type,subject_line,status,error_message
2025-11-04T09:16:52.821919-05:00,test@example.com,debarment,initial,Subject,SUCCESS,
```

### 12.5 Response Tracker Schema

```csv
email,vertical,initial_sent_date,replied,followup_sent_date,notes
test@example.com,debarment,2025-11-04,PENDING,,
```

**Replied Values:**
- `PENDING` - No response yet
- `INTERESTED` - Positive response
- `NOT_INTERESTED` - Declined
- `BOUNCED` - Email bounced
- (other custom values)

### 12.6 Required Python Packages

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
cryptography>=41.0.0
pytz>=2023.3
```

**Optional:**
```txt
pytest>=7.4.0  # For testing
black>=23.0.0  # Code formatting
flake8>=6.0.0  # Linting
```

---

## 13. CONTACT & SUPPORT

**Project Manager:** Claude Code  
**Project Start Date:** 2025-11-04  
**Target Completion:** Single session (24 hours development time)

**Documentation Location:**
- Implementation Plan: `/Email Outreach Dashboard/implementation_docs/IMPLEMENTATION_PLAN.md`
- Setup Guide: (To be created) `/Email Outreach Dashboard/docs/SETUP_INSTRUCTIONS.md`
- Troubleshooting: (To be created) `/Email Outreach Dashboard/docs/TROUBLESHOOTING.md`

---

## CONCLUSION

This implementation plan provides a comprehensive blueprint for building the Campaign Control Center dashboard. The hybrid data architecture ensures seamless integration with existing scripts while providing the dashboard with relational database benefits.

**Key Success Factors:**
1. **Non-invasive integration** - Scripts continue working unchanged
2. **Windows compatibility** - Centralized path handling from day 1
3. **Production quality** - Comprehensive testing and error handling
4. **Clear documentation** - Detailed setup and troubleshooting guides
5. **Team coordination** - Multi-agent approach with clear responsibilities

The phased approach allows for iterative development and testing, reducing risk while maintaining momentum. The detailed work breakdown ensures each agent knows exactly what to build and how it fits into the larger system.

**Next Step:** Share this plan with all agents and begin Phase 1 development.

---

**END OF IMPLEMENTATION PLAN**
