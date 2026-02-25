# Data Pull: LinkedIn Lead Gen — Bay Area Youth/Education Foundations & Nonprofits

**Document Type:** PROMPT
**Purpose:** Run queries to size the opportunity for a LinkedIn freebie post offering a list of Bay Area foundations funding youth/education, and count the nonprofits who'd want that list
**Date:** 2026-02-23

---

## Situation

We're creating a weekly LinkedIn lead gen play: post offering a free list of foundation funders in a specific niche/geography, connect with nonprofits in that space, send the list to anyone who asks, and mention TheGrantScout in the follow-up email. Week 1 target: **California / Youth & Education**.

We need to know: (1) how many foundations we can put on the list, (2) how many nonprofits would want it, and (3) how many of those nonprofits we've already emailed.

---

## Tasks

### Task 1: Count CA foundations funding youth/education

```sql
-- 1a: Summary counts
SELECT 
  count(DISTINCT df.ein) AS total_foundations,
  count(DISTINCT df.ein) FILTER (WHERE df.accepts_applications = true) AS open_to_applications,
  count(DISTINCT df.ein) FILTER (WHERE df.grants_to_orgs = true AND df.accepts_applications = true) AS open_and_grants_to_orgs,
  round(avg(fg.amount), 0) AS avg_grant,
  percentile_cont(0.5) WITHIN GROUP (ORDER BY fg.amount) AS median_grant
FROM f990_2025.dim_foundations df
JOIN f990_2025.fact_grants fg ON fg.foundation_ein = df.ein
WHERE df.state = 'CA'
  AND fg.amount > 0
  AND fg.purpose ~* 'youth|education|school|student|children|after.school|tutoring|literacy|scholarship|elementary|secondary|k.12|young people|child';

-- 1b: Top 15 cities by foundation count
SELECT df.city, count(DISTINCT df.ein) AS foundation_count
FROM f990_2025.dim_foundations df
JOIN f990_2025.fact_grants fg ON fg.foundation_ein = df.ein
WHERE df.state = 'CA'
  AND fg.amount > 0
  AND fg.purpose ~* 'youth|education|school|student|children|after.school|tutoring|literacy|scholarship|elementary|secondary|k.12|young people|child'
GROUP BY df.city
ORDER BY 2 DESC
LIMIT 15;
```

### Task 2: Count CA nonprofits in youth/education space

```sql
-- 2a: Total CA nonprofits by match type (NTEE vs keyword)
SELECT 
  count(DISTINCT ein) AS total_orgs,
  count(DISTINCT ein) FILTER (WHERE ntee_code LIKE 'B%') AS education_ntee,
  count(DISTINCT ein) FILTER (WHERE ntee_code ~ '^(O5|P3)') AS youth_services_ntee,
  count(DISTINCT ein) FILTER (WHERE ntee_code NOT LIKE 'B%' AND ntee_code !~ '^(O5|P3)') AS keyword_match_only
FROM (
  SELECT DISTINCT ON (ein) ein, ntee_code, mission_description
  FROM f990_2025.nonprofit_returns
  WHERE state = 'CA'
    AND tax_year >= 2021
    AND (
      ntee_code LIKE 'B%' OR ntee_code ~ '^(O5|P3)'
      OR mission_description ~* 'youth|education|school|student|children|after.school|tutoring|literacy|scholarship|young people'
    )
  ORDER BY ein, tax_year DESC
) latest;
```

### Task 3: Check prospect table coverage and email overlap

```sql
-- 3a: How many are in nonprofits_prospects2 with email?
SELECT 
  count(*) AS in_prospect_table,
  count(*) FILTER (WHERE contact_email IS NOT NULL) AS has_email
FROM f990_2025.nonprofits_prospects2 np2
WHERE np2.state = 'CA'
  AND (
    np2.ntee_code LIKE 'B%' OR np2.ntee_code ~ '^(O5|P3)'
    OR np2.mission_description ~* 'youth|education|school|student|children|after.school|tutoring|literacy|scholarship|young people'
  );

-- 3b: How many already emailed via campaigns?
SELECT count(DISTINCT cps.ein) AS already_emailed
FROM f990_2025.campaign_prospect_status cps
JOIN f990_2025.nonprofits_prospects2 np2 ON np2.ein = cps.ein
WHERE np2.state = 'CA'
  AND (
    np2.ntee_code LIKE 'B%' OR np2.ntee_code ~ '^(O5|P3)'
    OR np2.mission_description ~* 'youth|education|school|student|children|after.school|tutoring|literacy|scholarship|young people'
  );
```

---

## Expected Output

Print all results clearly with labels. No files needed yet — just the numbers. Example format:

```
=== FOUNDATIONS (CA, Youth/Education) ===
Total foundations: X
Open to applications: X
Open + grants to orgs: X
Avg grant: $X | Median grant: $X

Top 15 cities:
  San Francisco: X
  Los Angeles: X
  ...

=== NONPROFITS (CA, Youth/Education) ===
Total orgs: X (Education NTEE: X, Youth Services NTEE: X, Keyword only: X)
In prospect table: X (with email: X)
Already emailed: X
```

---

## Database Connection

- **Schema:** f990_2025
- **Key tables:** dim_foundations, fact_grants, nonprofit_returns, nonprofits_prospects2, campaign_prospect_status
- **Note:** dim_foundations and nonprofit_returns both have state indexes — queries should be fast
