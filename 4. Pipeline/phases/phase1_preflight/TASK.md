# TASK: Phase 1 - Pre-Flight Setup

**Purpose:** Prepare the pipeline for a new client report
**When:** Before starting any foundation discovery work

---

## Overview

Phase 1 ensures the client is properly loaded into the database and the environment is ready. Complete all steps in order.

---

## Step 1.1: Load Questionnaire into dim_clients

**Input:** Questionnaire Excel file (e.g., `questionnaire2026-01-08.xlsx`)
**Output:** Row in `f990_2025.dim_clients`

### Instructions for Claude Code CLI

1. Read the questionnaire Excel file using pandas
2. Extract the row for the target client
3. Map questionnaire columns to dim_clients fields (see mapping below)
4. Check if client already exists in dim_clients (by name or EIN)
5. INSERT new row or UPDATE existing row
6. Confirm the record was saved

### Column Mapping

| Questionnaire Column | dim_clients Column |
|---------------------|-------------------|
| Organization Name | name |
| Email Address (The one you want...) | email |
| Organization Type | org_type |
| Where is your organization headquartered? | state |
| What City... | city |
| Your most recent annual budget... | budget_tier |
| What size grants... | grant_size_seeking |
| What is your grant management capacity? | grant_capacity |
| What are your organization's primary program areas? | sector_broad |
| Select all populations... | populations_served |
| What geographic range... | geographic_scope |
| NTEE classification code | sector_ntee |
| In 1-2 sentences, what does your organization do? | mission_text |
| Are there any specific timeframes... | timeframe |
| Which funders have you received grants from... | known_funders |

### Python Code

```python
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def load_questionnaire_to_dim_clients(excel_path: str, client_name: str):
    """Load a client from questionnaire Excel into dim_clients."""

    # Read questionnaire
    df = pd.read_excel(excel_path)

    # Find client row
    client_row = df[df['Organization Name'] == client_name].iloc[0]

    # Map to dim_clients fields
    client_data = {
        'name': client_row['Organization Name'],
        'email': client_row.get('Email Address (The one you want us to send matched grant opportunities to)', None),
        'org_type': client_row.get('Organization Type', '501(c)(3)'),
        'state': str(client_row.get('Where is your organization headquartered?', '')).replace(';', '').strip(),
        'city': client_row.get('What City is your organization located in? (Some grants target specific cities)', None),
        'budget_tier': client_row.get("Your most recent annual budget. This helps us show you grants that match your organization's capacity.", None),
        'grant_size_seeking': client_row.get('What size grants are you typically looking for?', None),
        'grant_capacity': client_row.get('What is your grant management capacity?', None),
        'sector_broad': client_row.get("What are your organization's primary program areas?\xa0Select all areas where your organization works (up to 5).", None),
        'populations_served': str(client_row.get('Select all populations your organization primarily serves', '')).split(';') if pd.notna(client_row.get('Select all populations your organization primarily serves')) else None,
        'geographic_scope': client_row.get('What geographic range does your organization serve?', None),
        'sector_ntee': client_row.get("If you know your IRS NTEE classification code, enter it here", None),
        'mission_text': client_row.get('In 1-2 sentences, what does your organization do?"\n**Example:** "We provide after-school arts programs to low-income youth in Oakland, serving 200 students annually."', None),
        'timeframe': client_row.get("Are there any specific timeframes that you're hoping the grant will fit into?", None),
    }

    # Connect to database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME', 'thegrantscout'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()

    # Check if client exists
    cur.execute("SELECT id FROM f990_2025.dim_clients WHERE name = %s", (client_data['name'],))
    existing = cur.fetchone()

    if existing:
        # Update existing
        cur.execute("""
            UPDATE f990_2025.dim_clients SET
                email = %(email)s,
                org_type = %(org_type)s,
                state = %(state)s,
                city = %(city)s,
                budget_tier = %(budget_tier)s,
                grant_size_seeking = %(grant_size_seeking)s,
                grant_capacity = %(grant_capacity)s,
                sector_broad = %(sector_broad)s,
                geographic_scope = %(geographic_scope)s,
                sector_ntee = %(sector_ntee)s,
                mission_text = %(mission_text)s,
                timeframe = %(timeframe)s,
                updated_at = NOW()
            WHERE name = %(name)s
        """, client_data)
        print(f"Updated existing client: {client_data['name']}")
    else:
        # Insert new
        cur.execute("""
            INSERT INTO f990_2025.dim_clients (name, email, org_type, state, city, budget_tier,
                grant_size_seeking, grant_capacity, sector_broad, geographic_scope,
                sector_ntee, mission_text, timeframe)
            VALUES (%(name)s, %(email)s, %(org_type)s, %(state)s, %(city)s, %(budget_tier)s,
                %(grant_size_seeking)s, %(grant_capacity)s, %(sector_broad)s, %(geographic_scope)s,
                %(sector_ntee)s, %(mission_text)s, %(timeframe)s)
        """, client_data)
        print(f"Inserted new client: {client_data['name']}")

    conn.commit()
    cur.close()
    conn.close()

    return client_data

# Usage:
# load_questionnaire_to_dim_clients('questionnaire2026-01-08.xlsx', 'Patient Safety Movement Foundation')
```

---

## Step 1.2: Look Up EIN and IRS Financials

**Input:** Client name from dim_clients
**Output:** EIN, database_revenue, database_assets populated

### Instructions for Claude Code CLI

1. Search nonprofit_returns for the organization by name
2. Get the EIN and most recent financial data
3. Update dim_clients with EIN, database_revenue, database_assets
4. Flag any budget variance (questionnaire vs IRS data)

### SQL Queries

```sql
-- Find EIN by organization name (fuzzy match)
SELECT ein, organization_name, state, total_revenue, total_assets, tax_year
FROM f990_2025.nonprofit_returns
WHERE LOWER(organization_name) LIKE LOWER('%Patient Safety Movement%')
ORDER BY tax_year DESC
LIMIT 5;

-- Get most recent financials for a known EIN
SELECT ein, organization_name, total_revenue, total_assets, tax_year
FROM f990_2025.nonprofit_returns
WHERE ein = '462730379'
ORDER BY tax_year DESC
LIMIT 1;

-- Update dim_clients with EIN and financials
UPDATE f990_2025.dim_clients
SET
    ein = '462730379',
    database_revenue = 365177,  -- from IRS data
    database_assets = 123456,   -- from IRS data
    updated_at = NOW()
WHERE name = 'Patient Safety Movement Foundation';

-- Check for budget variance
-- Compare database_revenue to budget_tier from questionnaire
-- Flag if > 2x difference
UPDATE f990_2025.dim_clients
SET budget_variance_flag = CASE
    WHEN budget_tier LIKE '%Over $1,000,000%' AND database_revenue < 500000 THEN 'RED'
    WHEN budget_tier LIKE '%$500,000%' AND database_revenue < 250000 THEN 'YELLOW'
    ELSE 'GREEN'
END
WHERE name = 'Patient Safety Movement Foundation';
```

---

## Step 1.3: Create Run Folder

**Input:** Client name, date
**Output:** Folder structure created

### Instructions for Claude Code CLI

Create the run folder structure:
```
runs/{client_name}/{YYYY-MM-DD}/
```

### Bash Command

```bash
# Create run folder for client
CLIENT_NAME="Patient_Safety_Movement_Foundation"
RUN_DATE=$(date +%Y-%m-%d)
RUN_PATH="/Users/aleckleinman/Documents/TheGrantScout/4. Pipeline/runs/${CLIENT_NAME}/${RUN_DATE}"

mkdir -p "${RUN_PATH}"
echo "Created: ${RUN_PATH}"
```

---

## Step 1.4: Verify Database Connection

**Input:** None
**Output:** Confirmation that database is accessible and has expected data

### Instructions for Claude Code CLI

Run these verification queries and confirm counts are reasonable:

### SQL Queries

```sql
-- Verify connection and basic counts
SELECT 'foundations' as table_name, COUNT(*) as row_count FROM f990_2025.dim_foundations
UNION ALL
SELECT 'grants', COUNT(*) FROM f990_2025.fact_grants
UNION ALL
SELECT 'clients', COUNT(*) FROM f990_2025.dim_clients
UNION ALL
SELECT 'nonprofit_returns', COUNT(*) FROM f990_2025.nonprofit_returns;

-- Expected approximate counts:
-- foundations: ~143,000
-- grants: ~8,300,000
-- clients: varies
-- nonprofit_returns: ~2,900,000

-- Verify client was loaded
SELECT id, name, ein, state, budget_tier, database_revenue, mission_text IS NOT NULL as has_mission
FROM f990_2025.dim_clients
WHERE name ILIKE '%Patient Safety%';
```

---

## Quality Checks

After completing Phase 1, verify:

- [ ] Client exists in dim_clients with correct name
- [ ] EIN is populated and valid (9 digits, no dashes)
- [ ] mission_text is populated (needed for sibling matching)
- [ ] state is populated (needed for geographic matching)
- [ ] database_revenue is populated (needed for budget filtering)
- [ ] Run folder exists at expected path
- [ ] Database connection works and has expected row counts

---

## Example: PSMF Phase 1 Results

| Field | Value |
|-------|-------|
| name | Patient Safety Movement Foundation |
| ein | 462730379 |
| state | CA |
| budget_tier | Over $1,000,000 (questionnaire) |
| database_revenue | $365,177 (IRS) |
| budget_variance_flag | RED (5.5x discrepancy) |
| mission_text | We protect patients because everyone will be a patient one day... |
| run_folder | runs/Patient_Safety_Movement_Foundation/2026-01-13/ |

---

*Task file created 2026-01-13*
