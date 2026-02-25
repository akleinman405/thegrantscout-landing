#!/usr/bin/env python3
"""Build cohort_foundation_lists: top 15 foundations per state+sector combo."""

import psycopg2
import time

NTEE_LABELS = {
    'A': 'Arts & Culture', 'B': 'Education', 'C': 'Environment',
    'D': 'Animal-Related', 'E': 'Health', 'F': 'Mental Health',
    'G': 'Disease/Disorder', 'H': 'Medical Research', 'I': 'Crime/Legal',
    'J': 'Employment', 'K': 'Food/Agriculture', 'L': 'Housing',
    'M': 'Public Safety', 'N': 'Recreation', 'O': 'Youth Development',
    'P': 'Human Services', 'Q': 'International', 'R': 'Civil Rights',
    'S': 'Community Improvement', 'T': 'Philanthropy', 'U': 'Science',
    'V': 'Social Science', 'W': 'Public Policy', 'X': 'Religion',
    'Y': 'Mutual/Membership', 'Z': 'Unknown'
}

conn = psycopg2.connect(
    host='localhost', port=5432, database='thegrantscout',
    user='postgres', password='postgres'
)
conn.autocommit = False
cur = conn.cursor()
cur.execute("SET search_path TO f990_2025")

# Get all state+sector combos with emailable prospects
cur.execute("""
    SELECT DISTINCT state, LEFT(ntee_code, 1) as sector
    FROM nonprofits_prospects2
    WHERE contact_email IS NOT NULL
      AND ntee_code IS NOT NULL
      AND state IS NOT NULL
    ORDER BY state, sector
""")
combos = cur.fetchall()
print(f"Processing {len(combos)} state+sector combos...")

start = time.time()
total_inserted = 0
batch_count = 0

for state, sector in combos:
    sector_label = NTEE_LABELS.get(sector, 'Other')

    # Find top 15 foundations for this state+sector
    # Join fact_grants to find foundations that gave to recipients in this state+sector
    cur.execute("""
        WITH foundation_giving AS (
            SELECT
                fg.foundation_ein,
                df.name as foundation_name,
                SUM(fg.amount) as total_giving_5yr,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fg.amount) as median_grant,
                COUNT(DISTINCT fg.recipient_ein) as unique_recipients
            FROM fact_grants fg
            JOIN dim_foundations df ON df.ein = fg.foundation_ein
            JOIN dim_recipients dr ON dr.ein = fg.recipient_ein
            JOIN calc_foundation_profiles cfp ON cfp.ein = fg.foundation_ein
            WHERE fg.recipient_state = %s
              AND LEFT(dr.ntee_code, 1) = %s
              AND fg.tax_year >= 2019
              AND fg.amount > 0
              AND cfp.accepts_applications = true
            GROUP BY fg.foundation_ein, df.name
            HAVING SUM(fg.amount) > 0
            ORDER BY SUM(fg.amount) DESC
            LIMIT 15
        ),
        with_example AS (
            SELECT
                fgv.*,
                ROW_NUMBER() OVER (PARTITION BY fgv.foundation_ein ORDER BY fg2.amount DESC) as rn,
                fg2.recipient_name as ex_recipient,
                fg2.amount as ex_amount,
                fg2.purpose_text as ex_purpose
            FROM foundation_giving fgv
            LEFT JOIN LATERAL (
                SELECT dr.name as recipient_name, fg.amount, fg.purpose_text
                FROM fact_grants fg
                JOIN dim_recipients dr ON dr.ein = fg.recipient_ein
                WHERE fg.foundation_ein = fgv.foundation_ein
                  AND fg.recipient_state = %s
                  AND LEFT(dr.ntee_code, 1) = %s
                  AND fg.tax_year >= 2019
                  AND fg.amount > 0
                ORDER BY fg.amount DESC
                LIMIT 1
            ) fg2 ON true
        )
        SELECT foundation_ein, foundation_name, total_giving_5yr, median_grant,
               ex_recipient, ex_amount, ex_purpose
        FROM with_example
        WHERE rn = 1
        ORDER BY total_giving_5yr DESC
    """, (state, sector, state, sector))

    rows = cur.fetchall()

    for rank, row in enumerate(rows, 1):
        f_ein, f_name, total_5yr, median_g, ex_recip, ex_amt, ex_purp = row
        cur.execute("""
            INSERT INTO cohort_foundation_lists
                (state, ntee_sector, sector_label, foundation_rank, foundation_ein,
                 foundation_name, total_giving_5yr, median_grant, giving_trend,
                 accepts_applications, example_recipient_name, example_grant_amount,
                 example_grant_purpose)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (state, ntee_sector, foundation_rank) DO NOTHING
        """, (state, sector, sector_label, rank, f_ein, f_name, total_5yr,
              median_g, None, True, ex_recip, ex_amt, ex_purp))
        total_inserted += 1

    batch_count += 1
    if batch_count % 50 == 0:
        conn.commit()
        elapsed = time.time() - start
        print(f"  {batch_count}/{len(combos)} combos done ({elapsed:.0f}s, {total_inserted} rows)")

conn.commit()
elapsed = time.time() - start
print(f"\nDone in {elapsed:.0f}s")
print(f"Total rows inserted: {total_inserted}")
print(f"Combos processed: {batch_count}")

# Summary stats
cur.execute("""
    SELECT state, ntee_sector, COUNT(*) as foundations
    FROM cohort_foundation_lists
    GROUP BY state, ntee_sector
    ORDER BY foundations DESC
    LIMIT 20
""")
print("\nTop 20 cohorts by foundation count:")
for r in cur.fetchall():
    print(f"  {r[0]}-{r[1]}: {r[2]} foundations")

cur.execute("SELECT COUNT(*) FROM cohort_foundation_lists")
print(f"\nTotal cohort_foundation_lists rows: {cur.fetchone()[0]}")

cur.close()
conn.close()
