# Export: LinkedIn Prospect List — CA Youth/Education

**Document Type:** PROMPT
**Purpose:** Export ~300 prioritized CA youth/education nonprofits with contacts and LinkedIn search URLs to Excel
**Date:** 2026-02-23

---

## Situation

We're running a LinkedIn lead gen campaign offering a free list of Bay Area foundations funding youth/education. We need an Excel file of ~300 target nonprofits to connect with, including officer names, titles, and clickable LinkedIn search URLs.

---

## Database Query Rules (READ FIRST)

1. **ALWAYS inspect schema before querying.** Run `SELECT column_name FROM information_schema.columns WHERE table_schema = 'f990_2025' AND table_name = '<table>'` for every table before writing SQL.
2. **NEVER run SQL queries in parallel.** One at a time. Wait for result.
3. **After any SQL error, immediately run `ROLLBACK;`** before retrying.

---

## Tasks

### Task 1: Pull 300 prioritized orgs

Query `f990_2025.nonprofits_prospects2` (np2) for orgs matching ALL of:
- state = 'CA'
- NTEE code starts with B, O5, or P3
- Total revenue between $250,000 and $5,000,000 (check what revenue column is actually named — inspect schema first)
- NOT already emailed (LEFT JOIN campaign_prospect_status, exclude matches)

**Prioritize by:**
1. Bay Area cities first: San Francisco, Oakland, San Jose, Berkeley, Palo Alto, Redwood City, Mountain View, Fremont, Hayward, Richmond, Santa Clara, Sunnyvale, Menlo Park, Walnut Creek, Concord, San Mateo, Alameda, Santa Rosa
2. Then LA metro, San Diego, Sacramento
3. Within each geo group, order by revenue DESC (bigger orgs = more likely on LinkedIn)

Limit to 300 orgs.

### Task 2: Get contacts for each org

For each of the 300 orgs, pull up to 3 officers from the `officers` table (join on EIN):
- Prioritize titles containing: Executive Director, CEO, President, Director, Chief, VP, Founder
- Exclude titles like: Treasurer, Secretary, Board Member (less likely to be active LinkedIn users or decision makers)
- Also include `ed_ceo_name` from np2 if not already captured from officers

**Inspect the officers table schema first** to confirm column names for name, title, and EIN.

### Task 3: Build LinkedIn search URLs

For each contact, construct a URL:
```
https://www.linkedin.com/search/results/people/?keywords=<URL-encoded name + org name>
```

Example: Jane Smith at Oakland Youth Alliance →
```
https://www.linkedin.com/search/results/people/?keywords=Jane%20Smith%20Oakland%20Youth%20Alliance
```

### Task 4: Export to Excel

Create an Excel file with these columns:

| Column | Source |
|--------|--------|
| org_name | np2.organization_name |
| city | np2.city |
| annual_revenue | np2 revenue field |
| ntee_code | np2.ntee_code |
| mission | np2.mission_description (truncate to ~200 chars) |
| contact_name | officers or np2.ed_ceo_name |
| contact_title | officers.title field |
| linkedin_search_url | Constructed URL from Task 3 |
| my_message | LEAVE BLANK — Alec will fill in manually |

**One row per contact** (so an org with 3 contacts = 3 rows).

Sort by: city group priority (Bay Area first), then revenue DESC within each group.

**Make LinkedIn URLs clickable hyperlinks** in the Excel file if possible.

---

## Output

Save to: `/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-23/linkedin_prospects_ca_youth_education.xlsx`

Also save a brief report: `REPORT_2026-02-23_linkedin_prospect_export.md` in the same folder with:
- Final count of orgs and contacts
- Breakdown by city
- Any data quality issues found
