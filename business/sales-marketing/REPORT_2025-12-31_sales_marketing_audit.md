# Sales & Marketing Folder Audit Report

**Date:** 2025-12-31
**Prompt:** PROMPT_2025-12-31_sales_marketing_audit.md

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total files found | 82 project CSVs/Excel (21,703 including venv) |
| Prospect lists identified | 18 active lists |
| Total unique nonprofit prospects | 824 (across all sources) |
| Foundation management contacts | 101 contacts at 38 companies |
| Calls logged (nonprofits) | 78 of 626 (12.5%) |
| Calls logged (foundations) | 12 of 146 (8.2%) |
| Calls logged (fdn mgmt companies) | **0 of 101 (0%)** |
| Email campaign sent | 2,690 emails |
| Email responses tracked | 1,841 (many bounces) |

### Key Findings

1. **Foundation Management Companies** - A complete B2B call list exists with 38 companies and 101 contacts across tiers. **No calls have been made yet.** This is ready to use.

2. **Duplicate Data Sources** - The Excel workbook `Beta Test Group Calls.xlsx` contains copies of many CSV lists. The "Prospects V2" sheet and "Cold Calls CSV v2" overlap by only 12 EINs, meaning they're largely distinct lists.

3. **Best List for Continued Calling** - `DATA_2025-12-12_prospect_call_list_v2.csv` has 600 prospects with **100% phone coverage** and is the most call-ready nonprofit list.

4. **Call Tracking is Split** - Nonprofit call tracking happens in the Excel workbook's "Nonprofits" sheet (78 calls logged), but this list is separate from the 600-prospect CSV.

---

## Current Folder Structure

```
4. Sales & Marketing/
├── PROMPT_2025-12-31_sales_marketing_audit.md
├── SPEC_2025-12-10.1_gameplan_v1.docx
├── SPEC_2025-12-10.2_gameplan_v2.md
├── 0. Launch Strategy/
│   ├── 1. Network/
│   │   └── 1. Beta Connections/          # 6 CSVs with beta client network data
│   ├── 2. Community Foundations/          # 3 CSVs with community foundation cohorts
│   ├── 3. Nonprofit/
│   │   ├── Organize This/                 # 3 analysis CSVs
│   │   └── Prospects1 - Concrete Missions/ # 4 enriched prospect CSVs
│   └── 4. TA Provider Pools/              # 1 CSV with TA provider prospects
├── 0. Sales Calls/
│   └── 2025-12-4 VetsBoats/               # Sales call notes and research
├── 1. Nonprofits/                          # Empty
├── 2. Foundations/                         # 27 files: Foundation contact research
│   ├── DATA_2025-12-18_fdn_mgmt_contacts_FINAL.csv  ★ KEY FILE
│   ├── DATA_2025-12-18_fdn_mgmt_call_tracker.csv    ★ KEY FILE
│   ├── DATA_2025-12-17_foundation_management_companies.csv
│   ├── [15+ batch files from contact research]
│   └── Cold Calls script and notes.docx
├── 3. Partners/                            # 3 CSVs + research for publication outreach
├── 4. Cold Calls/                          # 11 files: Nonprofit call prospect lists
│   ├── DATA_2025-12-12_prospect_call_list_v2.csv    ★ KEY FILE (600 w/phones)
│   ├── Beta Test Group Calls(Phone Outreach Prospects).csv
│   ├── scrape_events.py
│   └── enrich_with_places.py
├── 5. Email Campaign/
│   ├── response_tracker.csv               # 1,841 tracked responses
│   ├── sent_tracker.csv                   # 2,690 sent emails
│   ├── grant_alerts_prospects.csv         # 6,370 email prospects
│   ├── Email Campaign 2025-11-3/          # Active campaign code + venv
│   ├── 1. Enhancements/
│   └── OLD/                               # Archived dashboard + old code
└── 6. Linkedin Outreach/
    ├── Carousels/                         # PDFs and scripts for content
    ├── Queue/
    ├── Research/
    └── Strategy/
```

---

## File Inventory

### Prospect Lists (CSV/Excel) - Active

| File | Location | Rows | Phone Coverage | Purpose | Status |
|------|----------|------|----------------|---------|--------|
| DATA_2025-12-18_fdn_mgmt_contacts_FINAL.csv | 2. Foundations/ | 101 | Partial | Foundation mgmt B2B contacts | **READY - 0 calls made** |
| DATA_2025-12-18_fdn_mgmt_call_tracker.csv | 2. Foundations/ | 60 | Partial | Prioritized fdn mgmt contacts | **READY - 0 calls made** |
| DATA_2025-12-12_prospect_call_list_v2.csv | 4. Cold Calls/ | 600 | 100% | Enriched nonprofit prospects | Best for calling |
| Beta Test Group Calls.xlsx (Nonprofits) | Downloads/ | 626 | Yes | Active nonprofit call tracking | 78 calls logged |
| Beta Test Group Calls.xlsx (Foundations) | Downloads/ | 146 | Partial | Foundation call tracking | 12 calls logged |
| Beta Test Group Calls.xlsx (Sheet4) | Downloads/ | 101 | Partial | Fdn mgmt contacts (duplicate) | Same as FINAL.csv |
| Beta Test Group Calls.xlsx (Prospects V2) | Downloads/ | 600 | 100% | Enriched prospects | Mirror of CSV |
| grant_alerts_prospects.csv | 5. Email Campaign/ | 6,370 | Email only | Email outreach list | Active campaign |

### Campaign Materials

| File | Type | Purpose | Status |
|------|------|---------|--------|
| SPEC_2025-12-10.2_gameplan_v2.md | Strategy | Sales gameplan | Current |
| Cold Calls script and notes.docx | Script | Foundation call scripts | Current |
| ONEPAGER_2025-12-10_foundation_partnership.md | Marketing | Foundation partnership pitch | Current |
| 00_START_HERE.md | Guide | Foundation folder navigation | Current |

### Scripts & Tools

| File | Purpose | Inputs | Outputs |
|------|---------|--------|---------|
| scrape_events.py | Event scraping | - | Event data |
| scrape_events_large.py | Large event scraping | - | Event data |
| enrich_with_places.py | Google Places enrichment | Prospects CSV | Enriched CSV |
| Email Campaign 2025-11-3/*.py | Email automation | prospect CSVs | sent/response trackers |

---

## Prospect List Deep Dive

### List 1: DATA_2025-12-18_fdn_mgmt_contacts_FINAL.csv ★ PRIORITY FOR B2B

- **Records:** 101 contacts at 38 companies
- **Columns:** tier, company_name, company_type, company_website, contact_name, contact_title, contact_type, linkedin_url, email, email_source, phone, phone_from_990, office_location, ein_990, assets_from_990, grants_received_2022plus, unique_funders, capacity_grants_received, notes, source_file
- **Companies Include:** Foundation Source, Bessemer Trust, Glenmede Trust, Tides Foundation, Silicon Valley Community Foundation, BlueStone Services, Schwab Charitable, Fidelity Charitable, etc.
- **Tier Distribution:** Tier 1 (15), Tier 2 (9), Tier 3 (22), Tier 6 (15), Tier 7 (9)
- **Status:** **0 calls made - READY TO START**
- **Recommended Action:** KEEP - This is the B2B target list for foundation management companies

### List 2: DATA_2025-12-18_fdn_mgmt_call_tracker.csv

- **Records:** 60 prioritized contacts
- **Columns:** priority, company name, contact name, contact title, phone, email, linkedin, call date, call outcome, follow up date, notes, ein_990, phone_990, assets_990, grants_received_2022plus
- **Status:** 0 calls logged
- **Recommended Action:** KEEP - Use as the active calling queue for fdn mgmt

### List 3: DATA_2025-12-12_prospect_call_list_v2.csv

- **Records:** 600 nonprofits
- **Columns:** 49 columns including ein, org name, phone, website, mission, icp_score, priority_tier, capacity grant info
- **Phone Coverage:** 100% (600/600)
- **Filters:** ICP score 10, priority tier 1, sectors E (health) and P (human services)
- **Overlap with Excel workbook:** Only 12 EINs overlap with Prospects V2 sheet
- **Status:** Fresh list - appears unused for calling
- **Recommended Action:** KEEP - Best list for continued nonprofit cold calling

### List 4: Beta Test Group Calls.xlsx - Nonprofits Sheet

- **Records:** 626 rows
- **Columns:** Organization_Name, Contact Date, Phone, Officer_Name, Officer_Title, Mission Statement, Website, Address, City, State, employee_count, volunteer_count, ZIP, Website2, Total_Revenue, Grants_Revenue, Grant_Dependency_Pct, Total_Expenses, Mission, Max Weekly Hours, NTEE_Codes, Tax_Year, EIN, Prospect_Score, Decision Maker, Decision Maker Title, VM/Message, Talked to Someone, Send us an Email, Reached Decision Maker, Yes/No/Maybe/Uncertain, Notes
- **Calls Logged:** 78 (with contact dates)
- **VMs Left:** 60
- **Status:** ACTIVE - Primary nonprofit call tracking
- **Recommended Action:** KEEP - Continue using for tracking; merge with v2 list

### List 5: Beta Test Group Calls.xlsx - Foundations Sheet

- **Records:** 146 foundations
- **Columns:** business name, Contact Date, phone, Email, website, state, EIN, total assets, grantee count, cb grant count, intermediary grant count, paid officer count, top officer name, top officer title, Column1, Linkedin URL, segment, Sent VM, Talked to Someone, Send us an Email, Reached Decision Maker, Yes/No/Maybe/Uncertain, Notes
- **Calls Logged:** 12
- **Status:** ACTIVE - Primary foundation call tracking
- **Recommended Action:** KEEP - Continue using

### List 6: grant_alerts_prospects.csv

- **Records:** 6,370 email prospects
- **Columns:** org_name, email, first_name, website, address_state
- **Status:** Active for email outreach
- **Recommended Action:** KEEP - Email-only prospects

---

## Call Tracking Workbook Analysis

**Location:** `/Users/aleckleinman/Downloads/Beta Test Group Calls.xlsx`

| Sheet | Rows | Purpose | Status |
|-------|------|---------|--------|
| Progress | 10 | Summary dashboard | Reference |
| Beta Group | 16 | Beta tester CRM | 6 clients tracked |
| Summary | 7 | Outreach metrics | Auto-calculated |
| Nonprofits | 626 | **Active call tracking** | 78 calls, 60 VMs |
| Foundations | 146 | Foundation call tracking | 12 calls logged |
| Sheet4 | 101 | Fdn mgmt contacts | Duplicate of CSV |
| Prospects V2 | 600 | Enriched nonprofit list | 600 with phones |
| Prospects V3 | 48 | Curated high-priority | Small subset |
| Email Outreach Prospects | 18,873 | Old email list | Legacy |
| Restaurants | 1,295 | Old vertical | Inactive |
| Gov Contractors | 200 | Old vertical | Inactive |

**Cross-Reference with Sales & Marketing Folder:**
- Sheet4 = Exact duplicate of `DATA_2025-12-18_fdn_mgmt_contacts_FINAL.csv`
- Prospects V2 appears to be same source as `DATA_2025-12-12_prospect_call_list_v2.csv`
- Nonprofits sheet is the ONLY place with actual call outcomes tracked

---

## Duplicate Analysis

| Duplicate Set | Files | Resolution |
|--------------|-------|------------|
| Foundation Mgmt Contacts | Sheet4 + fdn_mgmt_contacts_FINAL.csv + call_tracker.csv | Use `call_tracker.csv` for calling; archive others |
| Nonprofit Prospects | Prospects V2 + prospect_call_list_v2.csv | Same data, low overlap with Nonprofits sheet |
| Old Email Dashboard | Multiple OLD/ folders with venv | Archive or delete OLD/ folders |
| Batch Contact Files | 15+ DATA_2025-12-17_foundation_contacts_batch*.csv | Consolidated into FINAL.csv; archive batches |

---

## Outreach Pipeline Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PROSPECT SOURCES                            │
├─────────────────────────────────────────────────────────────────────┤
│ Nonprofits (600)     │ Foundations (146)  │ Fdn Mgmt (101)         │
│ prospect_call_list_  │ Excel Foundations  │ fdn_mgmt_contacts_     │
│ v2.csv               │ sheet              │ FINAL.csv              │
└──────────┬───────────┴─────────┬──────────┴──────────┬──────────────┘
           │                     │                     │
           ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CALL TRACKING (Excel Workbook)                   │
├─────────────────────────────────────────────────────────────────────┤
│ Nonprofits sheet:   │ Foundations sheet: │ fdn_mgmt_call_tracker: │
│ 78 called           │ 12 called          │ 0 called (NEW!)        │
│ 60 VMs              │                    │ 60 prioritized         │
└──────────┬──────────┴─────────┬──────────┴──────────┬───────────────┘
           │                    │                     │
           ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         PIPELINE STATUS                             │
├─────────────────────────────────────────────────────────────────────┤
│ Interested: 5-6 from calls (6% conversion)                         │
│ Beta Testers: 6 active (SNS, PSMF, RHF, KU, ACA, HN)              │
│ Email responses: 1,841 tracked (mostly bounces)                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Issues Found

1. **Foundation Management Calls Not Started** - Complete B2B list exists with 101 contacts but 0 calls logged. This is the user's stated priority.

2. **Call Tracking Split Across Systems** - Prospect data in CSVs, tracking in Excel workbook. Creates risk of losing track of who's been called.

3. **Workbook in Downloads Folder** - Primary tracking file `Beta Test Group Calls.xlsx` is in Downloads, not Sales & Marketing folder. Risk of accidental deletion.

4. **Large venv Directories** - Two Python venvs (21,600+ files) bloat the folder. Could be removed.

5. **Duplicate Batch Files** - 15+ `DATA_2025-12-17_foundation_contacts_batch*.csv` files are superseded by FINAL.csv.

6. **Email Campaign HIGH Bounce Rate** - Sent tracker shows many "BOUNCED" statuses. Email list quality issues.

7. **Inactive Verticals** - Restaurants (1,295) and Gov Contractors (200) sheets are legacy data from abandoned verticals.

---

## Recommendations Summary

### Immediate Actions

1. **START CALLING FOUNDATION MANAGEMENT COMPANIES**
   - Use `DATA_2025-12-18_fdn_mgmt_call_tracker.csv` (60 prioritized contacts)
   - Track outcomes in "call date" and "call outcome" columns
   - Focus on Tier 1 companies: Foundation Source, Bessemer Trust, BlueStone, etc.

2. **Move Excel Workbook to Sales & Marketing folder**
   - Current: `/Users/aleckleinman/Downloads/Beta Test Group Calls.xlsx`
   - Move to: `4. Sales & Marketing/Beta Test Group Calls.xlsx`

3. **Continue Nonprofit Calling with Fresh List**
   - Use `DATA_2025-12-12_prospect_call_list_v2.csv` (600 prospects, 100% phones)
   - Add contact outcomes to Excel Nonprofits sheet
   - ~522 uncalled from this list (600 - 78 logged)

### Cleanup Actions

4. **Archive Batch Files**
   - Move `DATA_2025-12-17_*batch*.csv` files to `2. Foundations/Archive/`
   - Keep only FINAL.csv versions

5. **Delete venv Directories** (optional)
   - `5. Email Campaign/Email Campaign 2025-11-3/venv/`
   - `5. Email Campaign/OLD/Email Outreach Dashboard/venv/`
   - Saves 21,600+ files, ~500MB

6. **Archive Inactive Verticals**
   - Remove or archive Restaurants and Gov Contractors sheets from workbook

---

## Foundation Management Companies - Ready to Call

| Company | Contact Count | Tier | Priority Notes |
|---------|---------------|------|----------------|
| Foundation Source | 8 | 1 | Largest dedicated manager, 4000+ clients |
| Bessemer Trust | 5 | 1 | High net worth family offices |
| BlueStone Services | 5 | 1 | Outsourced foundation services |
| Glenmede Trust | 4 | 1 | Wealth management + philanthropy |
| Schwab Charitable | 3 | 1 | Major DAF provider |
| Fidelity Charitable | 3 | 1 | Largest DAF provider |
| Silicon Valley Community Foundation | 3 | 1 | Tech philanthropy hub |
| Tides Foundation | 3 | 1 | Fiscal sponsorship + advised funds |
| National Philanthropic Trust | 2 | 1 | DAF provider |
| JP Morgan Private Bank | 2 | 1 | UHNW philanthropy services |

**Total Tier 1 Contacts:** 15 (start here)

---

## Files Created/Modified

| File | Action | Location |
|------|--------|----------|
| REPORT_2025-12-31_sales_marketing_audit.md | Created | 4. Sales & Marketing/ |

---

## Notes

- **Conversion Rates:** Cold calls convert at 6%, emails at 0.23%. Prioritize calling.
- **B2B Opportunity:** One foundation management company relationship could unlock dozens of foundation clients.
- **Data Freshness:** Most prospect lists from December 2025; Foundation data from 990s through 2024.
- **Next Phase:** After user review, can proceed with reorganization proposal.

---

*Generated by Claude Code on 2025-12-31*
