SET search_path TO f990_2025;

-- Step 1: Get the state+sector combos we care about
CREATE TEMP TABLE target_combos AS
SELECT DISTINCT state, LEFT(ntee_code, 1) as sector
FROM nonprofits_prospects2
WHERE contact_email IS NOT NULL
  AND ntee_code IS NOT NULL
  AND state IS NOT NULL;

CREATE INDEX idx_tc ON target_combos(state, sector);

-- Step 2: Pre-aggregate foundation giving by state+sector in one pass
CREATE TEMP TABLE foundation_state_sector AS
SELECT
    fg.recipient_state as state,
    LEFT(dr.ntee_code, 1) as sector,
    fg.foundation_ein,
    df.name as foundation_name,
    SUM(fg.amount) as total_giving_5yr,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fg.amount) as median_grant,
    COUNT(DISTINCT fg.recipient_ein) as unique_recipients
FROM fact_grants fg
JOIN dim_recipients dr ON dr.ein = fg.recipient_ein
JOIN dim_foundations df ON df.ein = fg.foundation_ein
JOIN calc_foundation_profiles cfp ON cfp.ein = fg.foundation_ein
WHERE fg.tax_year >= 2019
  AND fg.amount > 0
  AND cfp.accepts_applications = true
  AND dr.ntee_code IS NOT NULL
GROUP BY fg.recipient_state, LEFT(dr.ntee_code, 1), fg.foundation_ein, df.name
HAVING SUM(fg.amount) > 0;

CREATE INDEX idx_fss ON foundation_state_sector(state, sector, total_giving_5yr DESC);

-- Step 3: Rank and keep top 15 per combo (only for combos that have emailable prospects)
CREATE TEMP TABLE ranked_foundations AS
SELECT
    fss.*,
    ROW_NUMBER() OVER (PARTITION BY fss.state, fss.sector ORDER BY fss.total_giving_5yr DESC) as rk
FROM foundation_state_sector fss
JOIN target_combos tc ON tc.state = fss.state AND tc.sector = fss.sector;

DELETE FROM ranked_foundations WHERE rk > 15;

-- Step 4: Add one example grant per foundation+state+sector
CREATE TEMP TABLE examples AS
SELECT DISTINCT ON (rf.foundation_ein, rf.state, rf.sector)
    rf.foundation_ein, rf.state, rf.sector,
    dr.name as example_recipient_name,
    fg.amount as example_grant_amount,
    fg.purpose_text as example_grant_purpose
FROM ranked_foundations rf
JOIN fact_grants fg ON fg.foundation_ein = rf.foundation_ein
    AND fg.recipient_state = rf.state
    AND fg.tax_year >= 2019
    AND fg.amount > 0
JOIN dim_recipients dr ON dr.ein = fg.recipient_ein
    AND LEFT(dr.ntee_code, 1) = rf.sector
ORDER BY rf.foundation_ein, rf.state, rf.sector, fg.amount DESC;

-- Step 5: Insert into cohort_foundation_lists
INSERT INTO cohort_foundation_lists
    (state, ntee_sector, sector_label, foundation_rank, foundation_ein,
     foundation_name, total_giving_5yr, median_grant, giving_trend,
     accepts_applications, example_recipient_name, example_grant_amount,
     example_grant_purpose)
SELECT
    rf.state,
    rf.sector,
    CASE rf.sector
        WHEN 'A' THEN 'Arts & Culture'
        WHEN 'B' THEN 'Education'
        WHEN 'C' THEN 'Environment'
        WHEN 'D' THEN 'Animal-Related'
        WHEN 'E' THEN 'Health'
        WHEN 'F' THEN 'Mental Health'
        WHEN 'G' THEN 'Disease/Disorder'
        WHEN 'H' THEN 'Medical Research'
        WHEN 'I' THEN 'Crime/Legal'
        WHEN 'J' THEN 'Employment'
        WHEN 'K' THEN 'Food/Agriculture'
        WHEN 'L' THEN 'Housing'
        WHEN 'M' THEN 'Public Safety'
        WHEN 'N' THEN 'Recreation'
        WHEN 'O' THEN 'Youth Development'
        WHEN 'P' THEN 'Human Services'
        WHEN 'Q' THEN 'International'
        WHEN 'R' THEN 'Civil Rights'
        WHEN 'S' THEN 'Community Improvement'
        WHEN 'T' THEN 'Philanthropy'
        WHEN 'U' THEN 'Science'
        WHEN 'V' THEN 'Social Science'
        WHEN 'W' THEN 'Public Policy'
        WHEN 'X' THEN 'Religion'
        WHEN 'Y' THEN 'Mutual/Membership'
        WHEN 'Z' THEN 'Unknown'
        ELSE 'Other'
    END,
    rf.rk,
    rf.foundation_ein,
    rf.foundation_name,
    rf.total_giving_5yr,
    rf.median_grant,
    NULL,
    TRUE,
    ex.example_recipient_name,
    ex.example_grant_amount,
    ex.example_grant_purpose
FROM ranked_foundations rf
LEFT JOIN examples ex ON ex.foundation_ein = rf.foundation_ein
    AND ex.state = rf.state AND ex.sector = rf.sector
ORDER BY rf.state, rf.sector, rf.rk;

-- Summary
SELECT COUNT(*) as total_rows,
       COUNT(DISTINCT (state, ntee_sector)) as total_combos
FROM cohort_foundation_lists;

DROP TABLE target_combos, foundation_state_sector, ranked_foundations, examples;
