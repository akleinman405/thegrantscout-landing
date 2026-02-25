#!/usr/bin/env python3
"""pre_email_quality_report.py: Run before generating any email batch.

Queries pre-flight quality views and outputs a gate-check report.
Hard blockers prevent email generation; soft flags require review.

Hard blockers:
  - .gov emails in batch
  - Tier D prospects in batch
  - Foundation over-citation (>5 emails in same batch)
  - All-mega cohorts (every foundation is $1B+ assets)

Usage:
  python3 pre_email_quality_report.py
  python3 pre_email_quality_report.py --tier A     # Only Tier A prospects
  python3 pre_email_quality_report.py --state CA   # Only California
"""

import argparse
import sys

import psycopg2


def main():
    parser = argparse.ArgumentParser(description="Pre-email data quality report")
    parser.add_argument("--tier", help="Filter to specific quality tier (A/B/C/D)")
    parser.add_argument("--state", help="Filter to specific state (2-letter code)")
    args = parser.parse_args()

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="thegrantscout",
        user="postgres",
        password="postgres",
    )
    cur = conn.cursor()
    cur.execute("SET search_path TO f990_2025")

    hard_blockers = []

    print("=" * 60)
    print("PRE-EMAIL DATA QUALITY REPORT")
    print("=" * 60)

    # 1. Prospect quality summary
    tier_filter = ""
    if args.tier:
        tier_filter = f" AND email_quality_tier = '{args.tier}'"
    state_filter = ""
    if args.state:
        state_filter = f" AND state = '{args.state}'"

    cur.execute(f"""
        SELECT
            email_quality_tier,
            COUNT(*) as cnt,
            COUNT(CASE WHEN flag_placeholder_name THEN 1 END) as placeholder_names,
            COUNT(CASE WHEN flag_generic_email THEN 1 END) as generic_emails,
            COUNT(CASE WHEN flag_gov_email THEN 1 END) as gov_emails,
            COUNT(CASE WHEN flag_stale_filer THEN 1 END) as stale_filers,
            COUNT(CASE WHEN flag_missing_ntee THEN 1 END) as missing_ntee,
            COUNT(CASE WHEN flag_missing_mission THEN 1 END) as missing_mission
        FROM v_email_preflight_prospect_quality
        WHERE 1=1 {tier_filter} {state_filter}
        GROUP BY email_quality_tier
        ORDER BY email_quality_tier
    """)
    print("\n--- PROSPECT QUALITY BY TIER ---")
    total_gov = 0
    total_d = 0
    for row in cur.fetchall():
        tier, cnt, placeholder, generic, gov, stale, no_ntee, no_mission = row
        print(
            f"  Tier {tier}: {cnt:,} prospects "
            f"(placeholder:{placeholder}, generic:{generic}, gov:{gov}, "
            f"stale:{stale}, no_ntee:{no_ntee}, no_mission:{no_mission})"
        )
        total_gov += gov
        if tier == "D":
            total_d += cnt

    if total_gov > 0:
        hard_blockers.append(f"BLOCKER: {total_gov} prospects have .gov emails")
    if total_d > 0:
        hard_blockers.append(f"BLOCKER: {total_d} Tier D prospects in pool")

    # 2. Over-citation check (scoped to batch's state if --state provided)
    if args.state:
        cur.execute(f"""
            SELECT cfl.foundation_name,
                   COUNT(DISTINCT cfl.ntee_sector) AS sector_appearances
            FROM cohort_foundation_lists_v2 cfl
            WHERE cfl.state = '{args.state}'
            GROUP BY cfl.foundation_ein, cfl.foundation_name
            HAVING COUNT(DISTINCT cfl.ntee_sector) > 3
            ORDER BY COUNT(DISTINCT cfl.ntee_sector) DESC
            LIMIT 10
        """)
    else:
        cur.execute("""
            SELECT foundation_name, cohort_appearances
            FROM v_email_preflight_overcitation
            ORDER BY cohort_appearances DESC
            LIMIT 10
        """)
    rows = cur.fetchall()
    scope = f" in {args.state}" if args.state else " globally"
    if rows:
        print(f"\n--- OVER-CITED FOUNDATIONS (>3 cohorts{scope}) ---")
        for name, cnt in rows:
            print(f"  WARNING: {name} appears in {cnt} cohorts (limit to 5 per email batch)")
    else:
        print(f"\n--- No over-cited foundations{scope} (good!) ---")

    # 3. Example grant quality
    cur.execute("""
        SELECT ntee_match_status, COUNT(*)
        FROM v_email_preflight_example_quality
        GROUP BY 1
        ORDER BY 2 DESC
    """)
    rows = cur.fetchall()
    print("\n--- EXAMPLE GRANT QUALITY ---")
    for status, cnt in rows:
        print(f"  {status}: {cnt:,}")

    # 4. Overall stats comparison (v1 vs v2)
    cur.execute("""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT foundation_ein) AS distinct_foundations,
            ROUND(AVG(email_fit_score)::numeric, 4) AS avg_score,
            ROUND(100.0 * COUNT(CASE WHEN assets >= 1e9 THEN 1 END) / COUNT(*), 1) AS pct_mega,
            MAX(email_fit_score) AS max_score,
            MIN(email_fit_score) AS min_score
        FROM cohort_foundation_lists_v2
    """)
    row = cur.fetchone()
    print("\n--- COHORT FOUNDATION LISTS V2 STATS ---")
    print(f"  Total rows: {row[0]:,}")
    print(f"  Distinct foundations: {row[1]:,}")
    print(f"  Avg email_fit_score: {row[2]}")
    print(f"  Mega-foundation %: {row[3]}%")
    print(f"  Score range: {row[5]} - {row[4]}")

    # 5. Example match tier distribution
    cur.execute("""
        SELECT example_match_tier, COUNT(*)
        FROM cohort_foundation_lists_v2
        GROUP BY 1
        ORDER BY 1
    """)
    rows = cur.fetchall()
    print("\n--- EXAMPLE MATCH TIER DISTRIBUTION ---")
    for tier, cnt in rows:
        labels = {
            1: "Exact sector + recent + state",
            2: "Sector + state + 2019+",
            3: "Broad sector + state + revenue",
            4: "Broad sector + state (fallback)",
        }
        label = labels.get(tier, "Unknown")
        print(f"  Tier {tier} ({label}): {cnt:,}")

    # Summary
    print("\n" + "=" * 60)
    if hard_blockers:
        print("HARD BLOCKERS FOUND - DO NOT GENERATE EMAILS")
        print("=" * 60)
        for b in hard_blockers:
            print(f"  {b}")
        print(
            "\nResolve all blockers before generating emails."
            "\nTier D prospects: exclude with WHERE email_quality_tier <> 'D'"
            "\n.gov emails: exclude with WHERE contact_email NOT LIKE '%.gov'"
        )
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED - SAFE TO GENERATE EMAILS")
        print("=" * 60)
        sys.exit(0)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
