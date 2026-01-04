# EMAIL CAMPAIGN DASHBOARD - Claude Code CLI Build Prompt

## CONTEXT & OBJECTIVE

Build a **production-ready Streamlit dashboard** called "Campaign Control Center" for managing multi-vertical email outreach campaigns. This is a **Windows environment** and must be optimized for Windows compatibility.

## EXISTING SYSTEM CONTEXT

**CRITICAL**: The user already has working Python email automation scripts. Your job is to build a dashboard that integrates with this existing system, NOT to rebuild from scratch.

**Existing Scripts Location**: `C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Campaign 2025-11-3\`

**Key Existing Files**:
1. **config.py** - Contains all email templates, SMTP settings, vertical configurations, and campaign parameters
2. **coordination.py** - Manages capacity allocation between initial and follow-up campaigns
3. **send_initial_outreach.py** - Sends initial outreach emails
4. **send_followup.py** - Sends follow-up emails

**Current Data Files** (at `C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\`):
- `sent_tracker.csv` - Log of all sent emails
- `response_tracker.csv` - Tracks responses
- `error_log.csv` - Error tracking
- `debarment_prospects.csv` - Debarment vertical prospects
- `food_recall_prospects.csv` - Food recall vertical prospects  
- `grant_alerts_prospects.csv` - Grant alerts vertical prospects
- `coordination.json` - Real-time coordination between scripts

**Current Active Verticals**:
- **IDEA_078** / "debarment" - Federal contractor debarment monitoring
- **IDEA_042** / "food_recall" - Restaurant food recall alerts
- **IDEA_062** / "grant_alerts" - Nonprofit grant opportunity alerts

The user is running automated email campaigns across multiple business verticals and needs a centralized dashboard to:
- Track campaign performance across all verticals
- Manage prospect lists via drag-and-drop CSV uploads
- Control multiple email accounts with different quotas
- Edit email templates and see changes reflected immediately
- View daily/weekly sending plans
- Add new business verticals dynamically
- Monitor email account health and quota usage

## INTEGRATION REQUIREMENTS

Your dashboard **MUST** integrate seamlessly with the existing Python scripts:

1. **Read from the same data files** the scripts use:
   - `sent_tracker.csv` - for metrics and status
   - `response_tracker.csv` - for response tracking
   - `coordination.json` - for real-time capacity allocation
   - Prospect CSVs for each vertical

2. **Write to the same data files** so scripts pick up changes:
   - Template updates should modify files that scripts read
   - Prospect uploads should be accessible to scripts
   - Settings changes should update shared config

3. **Respect the existing architecture**:
   - Scripts use `coordination.py` for capacity management
   - Scripts read from `config.py` for settings
   - Don't break the existing email sending workflow

4. **Windows compatibility**:
   - Use Windows file paths (backslashes or os.path.join)
   - Test all file operations on Windows
   - Ensure Streamlit runs correctly on Windows

## TECHNICAL ARCHITECTURE

### Core Technology Stack
- **Streamlit** - Dashboard framework (fast, Python-native, easy to modify)
- **SQLite** - Database for tracking (no separate server needed)
- **Pandas** - CSV/data manipulation
- **Plotly** - Interactive charts
- **Python cryptography** - Secure credential storage

### Data Layer Architecture

**SQLite Database** (`campaign_control.db`):
```sql
-- Verticals
CREATE TABLE verticals (
    vertical_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    target_industry TEXT,
    csv_filename TEXT,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email Accounts
CREATE TABLE email_accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_address TEXT UNIQUE NOT NULL,
    display_name TEXT,
    smtp_host TEXT NOT NULL,
    smtp_port INTEGER NOT NULL,
    smtp_username TEXT NOT NULL,
    password_encrypted BLOB NOT NULL,
    daily_send_limit INTEGER NOT NULL,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Account-Vertical Assignments
CREATE TABLE account_verticals (
    account_id INTEGER,
    vertical_id TEXT,
    PRIMARY KEY (account_id, vertical_id),
    FOREIGN KEY (account_id) REFERENCES email_accounts(account_id) ON DELETE CASCADE,
    FOREIGN KEY (vertical_id) REFERENCES verticals(vertical_id) ON DELETE CASCADE
);

-- Email Templates
CREATE TABLE email_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vertical_id TEXT NOT NULL,
    template_type TEXT NOT NULL, -- 'initial' or 'followup'
    template_name TEXT NOT NULL,
    subject_line TEXT NOT NULL,
    email_body TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vertical_id) REFERENCES verticals(vertical_id) ON DELETE CASCADE
);

-- Prospect tracking is handled via existing CSV files
-- Sent emails tracked via existing sent_tracker.csv
-- Responses tracked via existing response_tracker.csv
```

**File System Structure**:
```
C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\
├── campaign_control.db (NEW - dashboard database)
├── dashboard.py (NEW - main Streamlit app)
├── sent_tracker.csv (EXISTING - read by dashboard)
├── response_tracker.csv (EXISTING - read by dashboard)
├── error_log.csv (EXISTING - read by dashboard)
├── coordination.json (EXISTING - read by dashboard)
├── verticals/ (NEW - organized prospect storage)
│   ├── debarment/
│   │   ├── prospects.csv
│   │   └── templates/
│   │       ├── initial_template_1.txt
│   │       └── followup_template_1.txt
│   ├── food_recall/
│   │   ├── prospects.csv
│   │   └── templates/
│   ├── grant_alerts/
│   │   ├── prospects.csv
│   │   └── templates/
```

## DASHBOARD PAGES & FEATURES

### Page 1: 📊 Dashboard (Home)

**Top Metrics Row** (Big cards):
- Total emails sent (all time)
- Emails sent today
- Emails sent this week  
- Emails sent this month
- Response rate (from response_tracker.csv)

**Vertical Breakdown** (Dropdown selector):
- "All Verticals" (default)
- Individual verticals (debarment, food_recall, grant_alerts, etc.)
- Updates all metrics based on selection

**Interactive Charts**:
- Line chart: Emails sent over time (last 30 days) by vertical
- Bar chart: Emails by vertical (today)
- Donut chart: Response rates by vertical

**Email Account Status** (table):
- Account name
- Status (active/paused)
- Sent today / Daily limit
- Progress bar showing quota usage
- Assigned verticals

**Campaign Status**:
- Current status from coordination.json
- Scripts running status
- Next scheduled send time
- Pause/Resume buttons (writes to coordination.json)

### Page 2: 📥 Prospects Manager

**Dynamic Vertical Zones**:
- Shows upload zone for each ACTIVE vertical
- Drag-and-drop CSV file upload
- Auto-validation on upload:
  - Required columns: email, first_name, company, state (minimum)
  - Shows validation errors before accepting
  - Deduplication against existing prospects
  
**Prospect List Viewer**:
- Dropdown to select vertical
- Data table showing all prospects for that vertical
- Columns: email, first_name, company, state, status, initial_sent_date, followup_sent_date, responded
- Filters: Status (not contacted / initial sent / followup sent / responded)
- Search box
- Export to CSV button
- Delete selected prospects button

**Upload Statistics**:
- Total prospects per vertical
- Not contacted count
- Initial sent count
- Followup sent count
- Response count
- Last upload date

### Page 3: 📧 Email Accounts

**Account Management Table**:
- List all email accounts with:
  - Email address
  - Display name
  - Daily limit
  - Sent today
  - Status (Active/Inactive)
  - Assigned verticals (as badges)
  - Actions: Edit | Delete | Test Connection

**Add Account Button** → Opens modal form:
- Email address*
- Display name
- SMTP host*
- SMTP port*
- Username*
- Password* (encrypted storage)
- Daily send limit*
- Assigned verticals (multi-select checkboxes)

**Test Connection Feature**:
- Attempts SMTP connection
- Shows success/failure message
- Logs connection test results

**Account Assignment Matrix** (visual grid):
- Rows: Email accounts
- Columns: Verticals
- Checkboxes to assign/unassign
- Live updates

**Capacity Summary**:
- Total daily capacity across all accounts
- Current usage today
- Remaining capacity
- Capacity by vertical (based on account assignments)

### Page 4: 🔧 Verticals Manager

**Vertical Management Table**:
- List all verticals with:
  - Vertical ID (e.g., IDEA_042)
  - Display Name (e.g., "Food Recall Alerts")
  - Target Industry
  - Prospect Count
  - Active Templates
  - Email Accounts Assigned
  - Status (Active/Inactive)
  - Actions: Edit | Delete | View Details

**Add Vertical Button** → Opens form:
- Vertical ID* (e.g., IDEA_078)
- Display Name* (e.g., "Debarment Monitor")
- Target Industry
- Active (toggle)

**On vertical creation**:
- Create folder structure: `verticals/{vertical_id}/`
- Create empty prospects.csv with standard headers
- Create templates folder
- Insert into database

**Edit Vertical**:
- Update display name, target industry
- Toggle active status
- Cannot change vertical_id (primary key)

**Delete Vertical** (with confirmation):
- Removes from database
- Archives folder (moves to `verticals/_archived/`)
- Does not delete permanently

### Page 5: ✉️ Templates Manager

**Vertical Selector** (tabs or dropdown):
- Select which vertical's templates to manage
- Shows template count for each vertical

**Template List** (for selected vertical):
- Shows all templates (initial + followup)
- Template name
- Subject line preview
- Last modified date
- Active status toggle
- Actions: Edit | Duplicate | Delete

**Edit Template** (main interface):
- Template type (Initial / Followup)
- Template name
- Subject line (text input)
- Email body (large text area with syntax highlighting)
- Available variables display: `{greeting}`, `{first_name}`, `{company}`, etc.
- Live preview pane (shows how it renders with sample data)
- Save button
- Test send button (sends to test email)

**Save Behavior**:
- Writes template to database
- Also writes to text file: `verticals/{vertical_id}/templates/{type}_{name}.txt`
- Updates timestamp
- Shows success message

**Template Assignment**:
- Which email accounts use which templates
- Matrix view: Accounts (rows) × Templates (columns)
- Checkboxes for active assignments

### Page 6: 📅 Campaign Planner

**Today's Plan**:
- Table showing scheduled sends for today:
  - Vertical
  - Email account
  - Campaign type (initial/followup)
  - Planned quantity
  - Already sent
  - Remaining
  - Status
- Calculated from coordination.json + account capacities + prospect availability

**Weekly Forecast**:
- Day-by-day breakdown for next 7 days
- Shows: Date, Vertical, Type, Planned Sends
- Accounts for:
  - Business hours (9am-3pm EST)
  - Weekends (skips Saturday/Sunday)
  - Daily limits per account
  - Available prospects

**Manual Controls**:
- Pause Campaign button (updates coordination.json)
- Resume Campaign button
- Adjust Daily Limits (per account override)
- Skip Today button (resets daily counters)

**Capacity Calculator**:
- Input: Number of prospects to send
- Output: Days required (based on current config)
- Shows: Daily breakdown by vertical and account

### Page 7: ⚙️ Settings

**Global Campaign Settings**:
- Business hours start (default: 9 AM EST)
- Business hours end (default: 3 PM EST)
- Timezone (default: US/Eastern)
- Conservative pacing mode (toggle)
- Hourly send rate (calculated automatically)

**Anti-Spam Settings**:
- Base delay min/max (seconds between emails)
- Break frequency (emails between breaks)
- Break duration (seconds per break)

**File Paths** (display only, not editable):
- Base directory
- Sent tracker location
- Response tracker location
- Error log location

**Data Management**:
- Export all data button (creates ZIP)
- Import data button
- Clear test data button
- Reset daily counters button

**System Info**:
- Dashboard version
- Database size
- Total prospects across all verticals
- Total sent emails (lifetime)
- Uptime

## IMPLEMENTATION REQUIREMENTS

### Multi-Agent Team Approach

**Use a specialized multi-agent team** to ensure high quality and efficiency:

**Agent 1: Project Manager / Architect**
- Review requirements thoroughly
- Design overall system architecture
- Create implementation plan with milestones
- Coordinate between other agents
- Make final integration decisions
- Write SETUP_INSTRUCTIONS.md

**Agent 2: Database Engineer**
- Design SQLite schema
- Write database initialization scripts
- Create migration utilities
- Build data access layer (functions for CRUD operations)
- Ensure data integrity and relationships
- Handle encryption for passwords

**Agent 3: Backend Developer**
- Build integration with existing scripts
- File I/O operations (CSV reading/writing)
- Parse coordination.json
- Parse sent_tracker.csv
- Template file management
- Prospect CSV validation and import
- Ensure Windows path compatibility

**Agent 4: Frontend Developer (Streamlit)**
- Build all 7 pages
- Create reusable components (cards, tables, forms)
- Implement drag-and-drop file upload
- Build interactive charts with Plotly
- Ensure responsive design
- Handle user input validation
- Error handling and user feedback

**Agent 5: QA / Testing Specialist**
- Write test plan
- Test all CRUD operations
- Test file uploads (various CSV formats)
- Test Windows compatibility
- Test integration with existing scripts
- Test edge cases (empty data, malformed CSVs, etc.)
- Create test data fixtures
- Write troubleshooting guide

**Coordination Protocol**:
1. PM creates implementation plan and assigns tasks
2. Database engineer creates schema first
3. Backend developer builds data layer on top of schema
4. Frontend developer builds UI using data layer
5. QA tests each component and end-to-end
6. PM coordinates integration and creates documentation

### Code Quality Standards

1. **Windows Compatibility**:
   - Use `os.path.join()` for all file paths
   - Test on Windows filesystem
   - Handle Windows path separators correctly
   - Use raw strings for Windows paths: `r"C:\path\to\file"`

2. **Error Handling**:
   - Try-except blocks around all file I/O
   - Try-except around all database operations
   - User-friendly error messages in UI
   - Log errors to error_log.csv

3. **Data Validation**:
   - Validate all user inputs
   - Validate CSV formats before import
   - Validate email addresses
   - Prevent SQL injection
   - Sanitize file paths

4. **Performance**:
   - Cache data where appropriate (use st.cache_data)
   - Lazy load large datasets
   - Optimize database queries
   - Keep UI responsive (async operations where needed)

5. **Code Organization**:
   - Modular design (separate files for each component)
   - Clear function/class names
   - Docstrings for all functions
   - Type hints where appropriate

### File Structure (What to Create)

```
dashboard_project/
├── dashboard.py                 # Main Streamlit app entry point
├── database/
│   ├── __init__.py
│   ├── schema.py               # Database schema and initialization
│   ├── models.py               # Data access layer (CRUD operations)
│   └── encryption.py           # Password encryption utilities
├── integrations/
│   ├── __init__.py
│   ├── csv_handler.py          # Read/write prospect CSVs
│   ├── tracker_reader.py       # Read sent_tracker.csv, response_tracker.csv
│   ├── coordination_reader.py  # Parse coordination.json
│   └── template_manager.py     # Template file operations
├── pages/
│   ├── __init__.py
│   ├── 1_dashboard.py          # Home page
│   ├── 2_prospects.py          # Prospects manager
│   ├── 3_email_accounts.py     # Email accounts
│   ├── 4_verticals.py          # Verticals manager
│   ├── 5_templates.py          # Templates manager
│   ├── 6_planner.py            # Campaign planner
│   └── 7_settings.py           # Settings
├── components/
│   ├── __init__.py
│   ├── cards.py                # Reusable metric cards
│   ├── charts.py               # Chart components
│   ├── forms.py                # Form components
│   └── tables.py               # Table components
├── utils/
│   ├── __init__.py
│   ├── validators.py           # Input validation
│   ├── formatters.py           # Data formatting
│   └── windows_paths.py        # Windows path helpers
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_integrations.py
│   ├── test_validators.py
│   └── fixtures/               # Test data
├── requirements.txt             # Python dependencies
├── SETUP_INSTRUCTIONS.md        # Detailed setup guide
├── TROUBLESHOOTING.md          # Common issues and solutions
└── README.md                   # Project overview
```

### Required Python Packages

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
cryptography>=41.0.0
pytz>=2023.3
```

### Testing Requirements

**Test Scenarios** (QA must verify):

1. **Database Operations**:
   - Create vertical → verify DB entry
   - Create email account → verify encrypted password
   - Assign account to vertical → verify relationship
   - Delete vertical → verify cascade delete

2. **File Operations**:
   - Upload valid CSV → verify import
   - Upload invalid CSV → verify error message
   - Modify template → verify file updated
   - Read sent_tracker.csv → verify metrics

3. **Integration with Scripts**:
   - Dashboard creates vertical → existing scripts can access
   - Dashboard updates template → scripts use new template
   - Scripts send email → dashboard shows updated metrics
   - Scripts write to coordination.json → dashboard reflects status

4. **UI Functionality**:
   - All forms validate inputs
   - All buttons perform expected actions
   - All charts render correctly
   - All tables allow sorting/filtering
   - File uploads show progress
   - Error messages are clear

5. **Windows Compatibility**:
   - Dashboard runs on Windows 10/11
   - File paths work correctly
   - CSV uploads work
   - Database creation works
   - No path separator issues

6. **Edge Cases**:
   - Empty database (first run)
   - No prospects loaded
   - No verticals created
   - Invalid SMTP credentials
   - Malformed CSV files
   - Large CSV files (10,000+ rows)
   - Concurrent access (if applicable)

## DELIVERABLES

### 1. Complete Working Dashboard
- All code files organized as specified
- Database initialized with schema
- All 7 pages functional
- Integration with existing scripts verified

### 2. SETUP_INSTRUCTIONS.md

**Must include** (detailed, step-by-step):

#### Prerequisites
- Windows version requirements
- Python version (3.9+ recommended)
- Existing files/folders needed

#### Installation Steps
1. Navigate to project directory
2. Install Python dependencies
3. Verify existing script locations
4. Initialize database
5. Configure base paths
6. Migrate existing data (if any)

#### First-Time Setup
1. Launch dashboard
2. Add first email account
3. Create first vertical
4. Upload first prospect list
5. Configure first template
6. Verify integration with existing scripts

#### Running the Dashboard
- Command to launch: `streamlit run dashboard.py`
- Expected output
- How to access in browser
- Troubleshooting startup issues

#### Configuration
- Where to set file paths
- How to change business hours
- How to adjust rate limits
- How to add test mode

#### Integration Verification
- How to verify scripts can read dashboard data
- How to verify dashboard reads script data
- How to test the coordination system
- How to check template updates propagate

### 3. TROUBLESHOOTING.md

**Must include**:

#### Common Issues
- Dashboard won't start
- Database errors
- File not found errors
- Path issues on Windows
- CSV upload failures
- SMTP connection failures
- Template not updating
- Metrics not showing

#### Error Messages
- List common error messages
- Explanation of each
- Step-by-step fix for each

#### Data Issues
- Missing prospects
- Duplicate prospects
- Metrics incorrect
- Charts not rendering

#### Integration Issues
- Scripts can't find templates
- Coordination not working
- Sent tracker not updating

### 4. README.md

**Must include**:
- Project overview
- Features list
- Screenshots/descriptions of each page
- Quick start guide
- Link to detailed setup instructions
- Link to troubleshooting guide
- Architecture overview
- Technology stack
- File structure explanation

### 5. Test Results

**Document showing**:
- All test scenarios executed
- Pass/fail for each
- Screenshots of working features
- Any known limitations
- Performance metrics (if applicable)

## SUCCESS CRITERIA

The dashboard is considered complete and successful when:

✅ **Functionality**:
- All 7 pages work correctly
- Can create/edit/delete verticals
- Can create/edit/delete email accounts
- Can upload prospect CSVs via drag-and-drop
- Can edit templates and see changes immediately
- Displays accurate metrics from sent_tracker.csv
- Shows real-time coordination status
- Campaign planner calculates correctly

✅ **Integration**:
- Reads existing sent_tracker.csv correctly
- Reads existing response_tracker.csv correctly
- Reads coordination.json correctly
- Template changes propagate to scripts
- Scripts can access uploaded prospects
- No conflicts with existing workflow

✅ **Windows Compatibility**:
- Runs on Windows without errors
- File paths work correctly
- All file operations work
- Database operations work

✅ **User Experience**:
- Intuitive navigation
- Clear error messages
- Responsive interface
- Professional appearance
- No crashes or freezes

✅ **Documentation**:
- SETUP_INSTRUCTIONS.md is clear and complete
- TROUBLESHOOTING.md covers common issues
- README.md provides good overview
- Code is well-commented

✅ **Quality**:
- No critical bugs
- Handles edge cases gracefully
- Validates all user inputs
- Secure password storage
- Clean, maintainable code

## IMPORTANT NOTES

1. **DO NOT break existing scripts** - The user's email automation system is working. Your dashboard must integrate without disrupting the existing workflow.

2. **Windows paths** - Pay careful attention to Windows file path formatting. Use `os.path.join()` or raw strings.

3. **Real data** - The dashboard will be used with real email campaigns. Ensure data integrity and accurate metrics.

4. **Scalability** - Design for growth. The user may add 10+ verticals and 5+ email accounts over time.

5. **Simplicity** - One command to run: `streamlit run dashboard.py`. No complex setup.

6. **Testing** - Actually test on Windows. Don't assume Linux/Mac behavior.

7. **Documentation** - The user needs clear, detailed instructions. Don't skip this.

## GETTING STARTED

**Recommended Workflow**:

1. **PM Agent**: Review all requirements, create implementation plan, assign tasks
2. **Database Engineer**: Design and implement schema, test database operations
3. **Backend Developer**: Build integration layer, test with existing files
4. **Frontend Developer**: Build UI pages, integrate with backend
5. **QA Specialist**: Test everything, create test report
6. **PM Agent**: Review integration, write documentation, create setup guide

**Communication**:
- Each agent should document their work clearly
- Flag any issues or questions immediately
- Coordinate on shared components (e.g., data models)
- Review each other's code for integration compatibility

**Time Management**:
- This is a 1-session project
- Prioritize core functionality over nice-to-haves
- Test as you build (don't wait until the end)
- Focus on Windows compatibility from the start

Good luck! Build something the user will love to use every day. 🚀