# SPEC: WORKFLOW_SPEC.md

**Document Type:** SPEC  
**Purpose:** End-to-end pipeline from new client to delivered report  
**Date:** 2025-12-08

---

## Sections

### 1. Workflow Diagram
- Visual flow: Intake → Match → Scrape → Report → Send
- ASCII or Mermaid diagram

### 2. Step 1: Client Intake
- Questionnaire fields collected
- How data enters nonprofits table
- Required vs optional fields
- Validation/cleaning

### 3. Step 2: Foundation Matching
- Which tables are queried
- Matching script logic
- Output format (matches table structure)
- How many foundations scored per client

### 4. Step 3: Opportunity Gathering
- Scraping pipeline for matched foundations
- current_opportunities table population
- Manual supplement process
- Federal/state grant sources

### 5. Step 4: Report Generation
- Template structure (email brief vs PDF)
- Where AI is used (positioning text, recommendations)
- PDF creation process
- Quality checks before delivery

### 6. Step 5: Delivery & Feedback
- Email sending mechanism
- Feedback collection process
- Learning loop (how feedback improves algorithm)

### 7. Required Tables
For each table needed:
- Table name
- Purpose in workflow
- Key fields used
- Upstream/downstream dependencies

### 8. Required Scripts
For each script:
- Script name/purpose
- Inputs
- Outputs
- Dependencies
- Frequency (one-time, daily, per-client, etc.)

### 9. Source Files
- File paths to existing code
- File paths to templates
- File paths to related specs

---

## Source Files to Reference
- `/mnt/project/THEGRANTSCOUT_SUMMARY_2025-12-5.md` (Section 6)
- `/mnt/project/Build_Plan.md`
- `/mnt/project/REPORT_SECTION_DEFINITIONS.md`
- `/mnt/project/WEEKLY_REPORT_TEMPLATE.md`
- `/mnt/project/EMAIL_BRIEF_TEMPLATE.md`
- `/mnt/project/02_REALIGNMENT_PLAN.md`
- `/mnt/project/03_SIMPLIFIED_TOOL_DESIGN.md`
- `/mnt/project/cdfi-extractor.md`
