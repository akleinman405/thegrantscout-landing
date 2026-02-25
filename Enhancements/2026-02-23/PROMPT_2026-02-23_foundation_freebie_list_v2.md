# Export: Free Foundation List — Bay Area Youth/Education Funders

**Document Type:** PROMPT
**Purpose:** Generate a polished, branded PDF list of top Bay Area foundations funding youth/education to offer as a free download on LinkedIn
**Date:** 2026-02-23
**Version:** 2.0 (updated with branding + CTA)

---

## Context & Decision Log

This list is the centerpiece of a LinkedIn lead gen strategy. We post offering a free list, connect with nonprofits in the space, and send it to anyone who asks with a brief mention of TheGrantScout and a CTA for a video call.

**Key design decisions:**

1. **Top 150 (not "all"):** A curated list feels like someone did work for them. "All foundations who match" would be 1,000+ and feel like a raw data dump. "150+ Bay Area Foundations" is a compelling headline number.

2. **Ranked by total $ to youth/education:** Puts the most impressive/relevant funders at the top. Someone scanning the list sees big names first and keeps scrolling.

3. **Bay Area + last 3 years (not just SF last year):** Broadens the numbers significantly. More foundations, bigger grant totals, more impressive list. Bay Area = SF, Oakland, San Jose, Berkeley, Palo Alto, plus surrounding cities in SF/Alameda/Santa Clara/San Mateo/Contra Costa/Marin counties.

4. **Grant stats are youth/education-specific:** Median and largest grant are filtered to youth/education grants only, not the foundation's overall giving. This makes the data directly relevant to the recipient.

5. **Includes foundations that don't accept applications:** The list is about awareness/discovery, not immediate action. Many "closed" foundations can still be approached via board connections or LOIs. Excluding them would shrink the list unnecessarily.

6. **No contact info, no strategy:** The free list shows WHAT exists. The paid report shows HOW to approach them: contact person, phone, email, website, application requirements, deadlines, positioning strategy, and which similar orgs they've already funded. That's the upsell.

7. **PDF with TheGrantScout branding:** Must match the same look and feel as our client reports (e.g., the VetsBoats/Matt reports). See branding section below.

---

## Database Query Rules

1. **ALWAYS inspect schema before querying.** Check column names with `information_schema.columns` for every table before writing SQL.
2. **NEVER run SQL queries in parallel.** One at a time.
3. **After any SQL error, run `ROLLBACK;`** before retrying.

---

## Task 0: Figure out the branding

Before building the PDF, look at how we've generated recent branded reports for clients. Check these locations for the most recent report generation scripts, templates, and PDF styling:

- `/Users/aleckleinman/Documents/TheGrantScout/` — look for recent report outputs (especially anything for VetsBoats or Matt Gettleman)
- Look for any Python scripts that generate PDFs (reportlab, weasyprint, fpdf, or markdown-to-pdf pipelines)
- Check for CSS files, templates, or style configs used in report generation
- Check the Enhancements folders for recent report work

**Goal:** Identify the exact colors, fonts, header/footer styles, and layout used in our most recent client-facing PDF reports, then replicate that styling for this foundation list. The freebie should look like it came from the same brand as our paid reports.

**Brand reference (fallback if no report templates found):**
- Primary: Deep Navy #1e3a5f
- Accent: Warm Gold #d4a853
- Background: White #ffffff
- Text: Dark Charcoal #2d3748
- Font: Inter (or whatever the reports use)

---

## Task 1: Identify Bay Area foundations funding youth/education

Query `f990_2025.dim_foundations` joined with `f990_2025.fact_grants`.

**Bay Area filter:** Foundation is located in CA AND in one of these cities (case-insensitive matching):
- SF County: San Francisco, Daly City, South San Francisco, Brisbane
- Alameda County: Oakland, Berkeley, Fremont, Hayward, Alameda, Livermore, Pleasanton, Dublin, Union City, Newark, San Leandro, Emeryville
- Santa Clara County: San Jose, Palo Alto, Mountain View, Sunnyvale, Santa Clara, Los Gatos, Saratoga, Cupertino, Milpitas, Los Altos, Campbell
- San Mateo County: San Mateo, Redwood City, Menlo Park, Burlingame, Foster City, San Carlos, Belmont, Half Moon Bay, Atherton, Woodside, Hillsborough, Portola Valley
- Contra Costa County: Walnut Creek, Concord, Lafayette, Orinda, Danville, San Ramon, Pleasant Hill, Martinez, Richmond, El Cerrito, Antioch
- Marin County: San Rafael, Mill Valley, Tiburon, Sausalito, Novato, Corte Madera, Larkspur, Ross, San Anselmo, Fairfax

**Youth/education filter on grants:** (inspect fact_grants schema first for the purpose column name)
```
purpose_text ~* 'youth|education|school|student|children|after.school|tutoring|literacy|scholarship|elementary|secondary|k.12|young people|child'
```

**Time filter:** tax_year >= 2022 (last 3 filing years: 2022, 2023, 2024)

**Grant filter:** amount > 0

---

## Task 2: Calculate stats per foundation

For each matching foundation, compute:

| Column | Calculation |
|--------|------------|
| foundation_name | dim_foundations.name |
| city | dim_foundations.city (normalize to Title Case) |
| total_youth_ed_giving | SUM(amount) for matching grants, last 3 years |
| num_youth_ed_grants | COUNT of matching grants, last 3 years |
| median_youth_ed_grant | percentile_cont(0.5) of matching grant amounts |
| largest_youth_ed_grant | MAX(amount) of matching grants |

---

## Task 3: Rank and limit to top 150

Order by `total_youth_ed_giving` DESC. Take top 150.

If fewer than 150 foundations match, include all and note the actual count.

---

## Task 4: Build the PDF

Use the same branding/styling identified in Task 0. The PDF should have three sections:

### Section 1: Header / Title Page Area

- **Title:** "Bay Area Foundations Funding Youth & Education Programs"
- **Subtitle:** "Top foundations ranked by total giving (2022-2024 IRS filings)"
- **Byline:** "Compiled by TheGrantScout"
- **Date:** February 2026

### Section 2: Intro Blurb (short, 2-3 sentences)

> This list highlights the top Bay Area foundations that have funded youth and education programs over the past three years, ranked by total giving. Data sourced from IRS 990-PF filings (2022-2024).

### Section 3: The Table

**Columns:**

| # | Foundation Name | City | Total Giving | # Grants | Median Grant | Largest Grant |

**Formatting:**
- Dollar amounts with commas and $ sign, no cents (e.g., $1,250,000)
- Row numbers 1-150
- Alternating row shading for readability
- Table header styled with brand primary color

### Section 4: Bottom CTA

> **Want more help finding foundation funders?**
>
> TheGrantScout delivers a monthly funding acquisition workbook with an actionable step-by-step plan to secure foundation funding.
>
> Each month you get:
> - **5 high-probability foundation matches** identified by predictive modeling based on their giving patterns, grant history, and alignment with your mission
> - **Confirmed eligibility** for each foundation before we include them
> - **Funder intelligence profiles** with contact info, application deadlines, and giving history
> - **Positioning strategy** showing how to approach each funder based on which similar organizations they've already funded
>
> See an example report: thegrantscout.com/example-report
>
> Schedule a meeting: Email alec@thegrantscout.com or visit thegrantscout.com

**Note:** Make the website URLs and email clickable hyperlinks in the PDF. Do NOT use em dashes anywhere in the document, use regular hyphens or commas instead.

---

## Task 5: Also export as CSV

Save a CSV version for our records.

---

## Output

1. **PDF:** `/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-23/Bay_Area_Youth_Education_Foundations_2026.pdf`
2. **CSV:** `/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-23/bay_area_youth_education_foundations_2026.csv`
3. **Report:** `REPORT_2026-02-23_foundation_list_export.md` in the same folder with:
   - Final count of foundations
   - Total combined giving across the list
   - Top 10 foundations by giving
   - Branding approach used (what templates/styles were found and replicated)
   - Any data quality issues
