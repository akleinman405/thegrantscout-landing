#!/usr/bin/env python3
"""
pull_funder_snapshots.py - Pull funder snapshot data from PostgreSQL

Queries the thegrantscout database (schema f990_2025) to build structured
funder dossiers for grant report generation. Handles both private foundations
(990-PF) and public charities (990/990-EZ).

Usage:
    python3 pull_funder_snapshots.py input.json
    python3 pull_funder_snapshots.py input.json --output snapshots.json

Input JSON format:
    {
        "client": {
            "name": "Org Name",
            "ein": "123456789",
            "state": "CA",
            "ntee_code": "X20",
            "annual_revenue": 5000000
        },
        "foundations": [
            {"ein": "123456789", "name": "Foundation Name"},
            ...
        ]
    }
"""

import argparse
import json
import os
import sys
from decimal import Decimal

import psycopg2
import psycopg2.extras


def decimal_default(obj):
    """JSON serializer for Decimal objects."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def get_connection():
    """Connect to thegrantscout database."""
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", "5432")),
        database=os.environ.get("PGDATABASE", "thegrantscout"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", "Mapping1!"),
    )


def determine_foundation_type(cur, ein):
    """Determine if a foundation is a private foundation (PF) or public charity (PC).

    Returns 'PF' if found in pf_returns, 'PC' if found in nonprofit_returns, or None.
    """
    cur.execute(
        "SELECT 1 FROM f990_2025.pf_returns WHERE ein = %s LIMIT 1",
        (ein,),
    )
    if cur.fetchone():
        return "PF"

    cur.execute(
        "SELECT 1 FROM f990_2025.nonprofit_returns WHERE ein = %s LIMIT 1",
        (ein,),
    )
    if cur.fetchone():
        return "PC"

    return None


def get_pf_profile(cur, ein):
    """Get private foundation profile from pf_returns (most recent year)."""
    cur.execute(
        """
        SELECT
            ein,
            business_name,
            state,
            city,
            website_url,
            phone_num,
            email_address_txt,
            total_assets_eoy_amt,
            total_grant_paid_amt,
            only_contri_to_preselected_ind,
            mission_desc,
            activity_or_mission_desc,
            primary_exempt_purpose,
            ntee_code,
            app_submission_deadlines,
            app_restrictions,
            app_form_requirements,
            app_contact_name,
            app_contact_phone,
            app_contact_email,
            application_submission_info,
            tax_year
        FROM f990_2025.pf_returns
        WHERE ein = %s
        ORDER BY tax_year DESC
        LIMIT 1
        """,
        (ein,),
    )
    row = cur.fetchone()
    if not row:
        return None

    return {
        "ein": row["ein"],
        "name": row["business_name"],
        "state": row["state"],
        "city": row["city"],
        "website": row["website_url"],
        "phone": row["phone_num"],
        "email": row["email_address_txt"],
        "total_assets": row["total_assets_eoy_amt"],
        "total_grants_paid": row["total_grant_paid_amt"],
        "preselected_only": row["only_contri_to_preselected_ind"],
        "mission": row["mission_desc"] or row["activity_or_mission_desc"] or row["primary_exempt_purpose"],
        "ntee_code": row["ntee_code"],
        "tax_year": row["tax_year"],
        "application_info": {
            "deadlines": row["app_submission_deadlines"],
            "restrictions": row["app_restrictions"],
            "form_requirements": row["app_form_requirements"],
            "contact_name": row["app_contact_name"],
            "contact_phone": row["app_contact_phone"],
            "contact_email": row["app_contact_email"],
            "submission_info": row["application_submission_info"],
        },
    }


def get_pc_profile(cur, ein):
    """Get public charity profile from nonprofit_returns (most recent year)."""
    cur.execute(
        """
        SELECT
            ein,
            organization_name,
            state,
            city,
            website,
            phone,
            total_assets_eoy,
            grants_and_similar_paid_amt,
            mission_description,
            ntee_code,
            tax_year
        FROM f990_2025.nonprofit_returns
        WHERE ein = %s
        ORDER BY tax_year DESC
        LIMIT 1
        """,
        (ein,),
    )
    row = cur.fetchone()
    if not row:
        return None

    return {
        "ein": row["ein"],
        "name": row["organization_name"],
        "state": row["state"],
        "city": row["city"],
        "website": row["website"],
        "phone": row["phone"],
        "total_assets": row["total_assets_eoy"],
        "total_grants_paid": row["grants_and_similar_paid_amt"],
        "mission": row["mission_description"],
        "ntee_code": row["ntee_code"],
        "tax_year": row["tax_year"],
    }


def get_pf_grant_metrics(cur, ein, client_state=None):
    """Compute grant metrics from pf_grants for a private foundation."""
    cur.execute(
        """
        SELECT
            COUNT(*) AS grant_count,
            SUM(amount) AS total_giving,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_grant,
            MIN(amount) AS min_grant,
            MAX(amount) AS max_grant,
            MIN(tax_year) AS earliest_year,
            MAX(tax_year) AS latest_year,
            COUNT(DISTINCT tax_year) AS active_years
        FROM f990_2025.pf_grants
        WHERE filer_ein = %s
          AND is_individual = FALSE
          AND amount > 0
        """,
        (ein,),
    )
    totals = cur.fetchone()

    if not totals or totals["grant_count"] == 0:
        return {
            "grant_count": 0,
            "total_giving": None,
            "median_grant": None,
            "grant_range": None,
            "annual_giving": None,
            "geographic_pct": None,
            "repeat_rate": None,
            "giving_trend": None,
            "giving_style_pct": None,
        }

    active_years = totals["active_years"] or 1
    annual_giving = float(totals["total_giving"]) / active_years if totals["total_giving"] else None

    # Geographic concentration (% in client's state)
    geo_pct = None
    if client_state:
        cur.execute(
            """
            SELECT
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE recipient_state = %s) / NULLIF(COUNT(*), 0),
                    1
                ) AS state_pct
            FROM f990_2025.pf_grants
            WHERE filer_ein = %s
              AND is_individual = FALSE
              AND amount > 0
            """,
            (client_state, ein),
        )
        geo_row = cur.fetchone()
        geo_pct = float(geo_row["state_pct"]) if geo_row and geo_row["state_pct"] else 0.0

    # Repeat funding rate (% recipients funded 2+ times)
    cur.execute(
        """
        WITH recipient_counts AS (
            SELECT recipient_ein, COUNT(*) AS grant_count
            FROM f990_2025.pf_grants
            WHERE filer_ein = %s
              AND is_individual = FALSE
              AND amount > 0
              AND recipient_ein IS NOT NULL
            GROUP BY recipient_ein
        )
        SELECT
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE grant_count >= 2) / NULLIF(COUNT(*), 0),
                1
            ) AS repeat_rate
        FROM recipient_counts
        """,
        (ein,),
    )
    repeat_row = cur.fetchone()
    repeat_rate = float(repeat_row["repeat_rate"]) if repeat_row and repeat_row["repeat_rate"] else 0.0

    # Giving trend (3-year comparison)
    cur.execute(
        """
        WITH yearly AS (
            SELECT
                tax_year,
                SUM(amount) AS year_total
            FROM f990_2025.pf_grants
            WHERE filer_ein = %s
              AND is_individual = FALSE
              AND amount > 0
            GROUP BY tax_year
            ORDER BY tax_year DESC
            LIMIT 6
        )
        SELECT
            COALESCE(SUM(year_total) FILTER (WHERE tax_year >= (SELECT MAX(tax_year) - 2 FROM yearly)), 0) AS recent_3yr,
            COALESCE(SUM(year_total) FILTER (WHERE tax_year < (SELECT MAX(tax_year) - 2 FROM yearly)), 0) AS prior_3yr
        FROM yearly
        """,
        (ein,),
    )
    trend_row = cur.fetchone()
    giving_trend = _compute_trend(trend_row)

    # Giving style (general support vs program-specific) - approximation from purpose text
    cur.execute(
        """
        SELECT
            ROUND(
                100.0 * COUNT(*) FILTER (
                    WHERE LOWER(purpose) LIKE '%%general%%'
                       OR LOWER(purpose) LIKE '%%operating%%'
                       OR LOWER(purpose) LIKE '%%unrestricted%%'
                ) / NULLIF(COUNT(*), 0),
                1
            ) AS general_support_pct
        FROM f990_2025.pf_grants
        WHERE filer_ein = %s
          AND is_individual = FALSE
          AND amount > 0
          AND purpose IS NOT NULL
          AND purpose <> ''
        """,
        (ein,),
    )
    style_row = cur.fetchone()
    general_pct = float(style_row["general_support_pct"]) if style_row and style_row["general_support_pct"] else None

    return {
        "grant_count": totals["grant_count"],
        "total_giving": totals["total_giving"],
        "median_grant": totals["median_grant"],
        "grant_range": {"min": totals["min_grant"], "max": totals["max_grant"]},
        "annual_giving": annual_giving,
        "active_years": active_years,
        "earliest_year": totals["earliest_year"],
        "latest_year": totals["latest_year"],
        "geographic_pct": geo_pct,
        "repeat_rate": repeat_rate,
        "giving_trend": giving_trend,
        "giving_style_pct": {"general_support": general_pct, "program_specific": (100 - general_pct) if general_pct is not None else None},
    }


def get_pc_grant_metrics(cur, ein, client_state=None):
    """Compute grant metrics from schedule_i_grants for a public charity."""
    cur.execute(
        """
        SELECT
            COUNT(*) AS grant_count,
            SUM(amount) AS total_giving,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_grant,
            MIN(amount) AS min_grant,
            MAX(amount) AS max_grant,
            MIN(tax_year) AS earliest_year,
            MAX(tax_year) AS latest_year,
            COUNT(DISTINCT tax_year) AS active_years
        FROM f990_2025.schedule_i_grants
        WHERE filer_ein = %s
          AND amount > 0
        """,
        (ein,),
    )
    totals = cur.fetchone()

    if not totals or totals["grant_count"] == 0:
        return {
            "grant_count": 0,
            "total_giving": None,
            "median_grant": None,
            "grant_range": None,
            "annual_giving": None,
            "geographic_pct": None,
            "repeat_rate": None,
            "giving_trend": None,
            "giving_style_pct": None,
        }

    active_years = totals["active_years"] or 1
    annual_giving = float(totals["total_giving"]) / active_years if totals["total_giving"] else None

    # Geographic concentration
    geo_pct = None
    if client_state:
        cur.execute(
            """
            SELECT
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE recipient_state = %s) / NULLIF(COUNT(*), 0),
                    1
                ) AS state_pct
            FROM f990_2025.schedule_i_grants
            WHERE filer_ein = %s
              AND amount > 0
            """,
            (client_state, ein),
        )
        geo_row = cur.fetchone()
        geo_pct = float(geo_row["state_pct"]) if geo_row and geo_row["state_pct"] else 0.0

    # Repeat funding rate
    cur.execute(
        """
        WITH recipient_counts AS (
            SELECT recipient_ein, COUNT(*) AS grant_count
            FROM f990_2025.schedule_i_grants
            WHERE filer_ein = %s
              AND amount > 0
              AND recipient_ein IS NOT NULL
            GROUP BY recipient_ein
        )
        SELECT
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE grant_count >= 2) / NULLIF(COUNT(*), 0),
                1
            ) AS repeat_rate
        FROM recipient_counts
        """,
        (ein,),
    )
    repeat_row = cur.fetchone()
    repeat_rate = float(repeat_row["repeat_rate"]) if repeat_row and repeat_row["repeat_rate"] else 0.0

    # Giving trend
    cur.execute(
        """
        WITH yearly AS (
            SELECT
                tax_year,
                SUM(amount) AS year_total
            FROM f990_2025.schedule_i_grants
            WHERE filer_ein = %s
              AND amount > 0
            GROUP BY tax_year
            ORDER BY tax_year DESC
            LIMIT 6
        )
        SELECT
            COALESCE(SUM(year_total) FILTER (WHERE tax_year >= (SELECT MAX(tax_year) - 2 FROM yearly)), 0) AS recent_3yr,
            COALESCE(SUM(year_total) FILTER (WHERE tax_year < (SELECT MAX(tax_year) - 2 FROM yearly)), 0) AS prior_3yr
        FROM yearly
        """,
        (ein,),
    )
    trend_row = cur.fetchone()
    giving_trend = _compute_trend(trend_row)

    return {
        "grant_count": totals["grant_count"],
        "total_giving": totals["total_giving"],
        "median_grant": totals["median_grant"],
        "grant_range": {"min": totals["min_grant"], "max": totals["max_grant"]},
        "annual_giving": annual_giving,
        "active_years": active_years,
        "earliest_year": totals["earliest_year"],
        "latest_year": totals["latest_year"],
        "geographic_pct": geo_pct,
        "repeat_rate": repeat_rate,
        "giving_trend": giving_trend,
        "giving_style_pct": None,
    }


def _compute_trend(trend_row):
    """Compute giving trend label from recent vs prior 3-year totals."""
    if not trend_row:
        return "Unknown"
    recent = float(trend_row["recent_3yr"]) if trend_row["recent_3yr"] else 0
    prior = float(trend_row["prior_3yr"]) if trend_row["prior_3yr"] else 0
    if prior == 0:
        return "Insufficient data"
    pct_change = ((recent - prior) / prior) * 100
    if pct_change > 15:
        return f"Growing (+{pct_change:.0f}%)"
    elif pct_change < -15:
        return f"Declining ({pct_change:.0f}%)"
    else:
        return f"Stable ({pct_change:+.0f}%)"


def get_comparable_grantee(cur, ein, foundation_type, client_state=None):
    """Find the most comparable recent grantees to the client."""
    if foundation_type == "PF":
        query = """
            SELECT
                pg.recipient_name,
                pg.recipient_state,
                pg.amount,
                pg.purpose,
                pg.tax_year
            FROM f990_2025.pf_grants pg
            WHERE pg.filer_ein = %s
              AND pg.is_individual = FALSE
              AND pg.amount > 0
              AND pg.tax_year >= 2019
        """
        params = [ein]

        if client_state:
            query += " AND pg.recipient_state = %s"
            params.append(client_state)

        query += " ORDER BY pg.tax_year DESC, pg.amount DESC LIMIT 5"
    else:
        query = """
            SELECT
                sg.recipient_name,
                sg.recipient_state,
                sg.amount,
                sg.purpose,
                sg.tax_year
            FROM f990_2025.schedule_i_grants sg
            WHERE sg.filer_ein = %s
              AND sg.amount > 0
              AND sg.tax_year >= 2019
        """
        params = [ein]

        if client_state:
            query += " AND sg.recipient_state = %s"
            params.append(client_state)

        query += " ORDER BY sg.tax_year DESC, sg.amount DESC LIMIT 5"

    cur.execute(query, params)
    rows = cur.fetchall()

    if not rows:
        return []

    return [
        {
            "name": row["recipient_name"],
            "state": row["recipient_state"],
            "amount": row["amount"],
            "purpose": row["purpose"],
            "year": row["tax_year"],
        }
        for row in rows
    ]


def get_officers(cur, ein):
    """Get officers/directors for a foundation (most recent year)."""
    cur.execute(
        """
        SELECT
            person_nm,
            title_txt,
            compensation_amt,
            is_officer,
            is_director,
            is_trustee,
            is_key_employee,
            tax_year
        FROM f990_2025.officers
        WHERE ein = %s
        ORDER BY tax_year DESC, compensation_amt DESC NULLS LAST
        LIMIT 15
        """,
        (ein,),
    )
    rows = cur.fetchall()

    if not rows:
        return []

    most_recent_year = rows[0]["tax_year"]

    return [
        {
            "name": row["person_nm"],
            "title": row["title_txt"],
            "compensation": row["compensation_amt"],
            "is_officer": row["is_officer"],
            "is_director": row["is_director"],
            "is_trustee": row["is_trustee"],
            "is_key_employee": row["is_key_employee"],
            "tax_year": row["tax_year"],
        }
        for row in rows
        if row["tax_year"] == most_recent_year
    ]


def build_snapshot(cur, fdn_ein, fdn_name, client_info):
    """Build a complete funder snapshot for one foundation."""
    fdn_type = determine_foundation_type(cur, fdn_ein)
    if not fdn_type:
        return {
            "ein": fdn_ein,
            "name": fdn_name,
            "error": "Foundation not found in pf_returns or nonprofit_returns",
        }

    client_state = client_info.get("state")

    # Get profile
    if fdn_type == "PF":
        profile = get_pf_profile(cur, fdn_ein)
        metrics = get_pf_grant_metrics(cur, fdn_ein, client_state)
    else:
        profile = get_pc_profile(cur, fdn_ein)
        metrics = get_pc_grant_metrics(cur, fdn_ein, client_state)

    # Get comparable grantees and officers
    comparable = get_comparable_grantee(cur, fdn_ein, fdn_type, client_state)
    officers = get_officers(cur, fdn_ein)

    snapshot = {
        "ein": fdn_ein,
        "name": profile.get("name", fdn_name) if profile else fdn_name,
        "foundation_type": fdn_type,
        "profile": profile,
        "metrics": metrics,
        "comparable_grantees": comparable,
        "officers": officers,
    }

    return snapshot


def main():
    parser = argparse.ArgumentParser(
        description="Pull funder snapshot data from PostgreSQL for grant report generation.",
        epilog="Input JSON must contain 'client' and 'foundations' keys. See script docstring for format.",
    )
    parser.add_argument("input", help="Path to input JSON file with client info and foundation list")
    parser.add_argument("--output", "-o", help="Output JSON file path (default: stdout)")

    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    client_info = data.get("client", {})
    foundations = data.get("foundations", [])

    if not foundations:
        print("Error: No foundations specified in input JSON", file=sys.stderr)
        sys.exit(1)

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            snapshots = []
            for fdn in foundations:
                fdn_ein = fdn.get("ein", "").strip()
                fdn_name = fdn.get("name", "Unknown")
                if not fdn_ein:
                    snapshots.append({"ein": "", "name": fdn_name, "error": "Missing EIN"})
                    continue
                print(f"Processing: {fdn_name} ({fdn_ein})...", file=sys.stderr)
                snapshot = build_snapshot(cur, fdn_ein, fdn_name, client_info)
                snapshots.append(snapshot)

        result = {
            "client": client_info,
            "snapshots": snapshots,
            "foundation_count": len(snapshots),
        }

        output_json = json.dumps(result, indent=2, default=decimal_default)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output_json)
            print(f"Wrote {len(snapshots)} snapshots to {args.output}", file=sys.stderr)
        else:
            print(output_json)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
