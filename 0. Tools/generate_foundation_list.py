#!/usr/bin/env python3
"""
TheGrantScout Foundation List Generator
========================================

Queries the database for foundations matching a geography + topic filter,
then generates a branded markdown report + CSV. Optionally converts to PDF.

Usage:
    python3 "0. Tools/generate_foundation_list.py" \
        --state CA \
        --cities "SAN FRANCISCO,OAKLAND,BERKELEY,PALO ALTO,..." \
        --topic-regex "youth|education|school|student|children" \
        --topic-label "Youth & Education" \
        --geo-label "Bay Area" \
        --output-dir "Enhancements/2026-02-23/" \
        --limit 150

Required: --state, --topic-regex, --topic-label
Optional: --cities, --geo-label, --output-dir, --limit, --min-year, --skip-pdf
"""

import argparse
import csv
import datetime
import os
import re
import subprocess
import sys
from collections import Counter

import psycopg2
import psycopg2.extras


# ============================================================================
# Database connection (env var pattern from pull_funder_snapshots.py)
# ============================================================================

def get_connection():
    """Connect to thegrantscout database using environment variables."""
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", "5432")),
        database=os.environ.get("PGDATABASE", "thegrantscout"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", "Mapping1!"),
    )


# ============================================================================
# SQL query template
# ============================================================================

QUERY = """
WITH topic_grants AS (
    SELECT
        fg.foundation_ein,
        df.name AS foundation_name,
        df.city AS foundation_city,
        df.assets,
        df.accepts_applications,
        fg.amount,
        fg.tax_year
    FROM f990_2025.fact_grants fg
    JOIN f990_2025.dim_foundations df ON fg.foundation_ein = df.ein
    WHERE df.state = %s
      {city_filter}
      AND fg.tax_year >= %s
      AND fg.amount > 0
      AND fg.purpose_text ~* %s
)
SELECT
    foundation_ein,
    foundation_name,
    foundation_city,
    assets,
    accepts_applications,
    SUM(amount)::bigint AS total_giving,
    COUNT(*) AS grant_count,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount)::bigint AS median_grant,
    MAX(amount)::bigint AS largest_grant,
    MAX(tax_year) AS most_recent_year
FROM topic_grants
GROUP BY foundation_ein, foundation_name, foundation_city, assets, accepts_applications
ORDER BY total_giving DESC
LIMIT %s
"""


# ============================================================================
# Name formatting
# ============================================================================

# IRS truncates names at ~35-40 chars. These EIN-keyed overrides provide
# the complete, correctly formatted name for foundations we know are truncated.
NAME_OVERRIDES = {
    '463460261': 'The Eric and Wendy Schmidt Fund for Strategic Innovation',
    '946062858': 'The Carl Gellert and Celia Berta Gellert Foundation',
    '770029903': 'The Kyupin Philip and C. Gemma Hwang Foundation',
    '204319424': 'The Nancy P. and Richard K. Robbins Family Foundation',
    '136894208': 'UD LD Mellam for Mellam Family Foundation',
    '912154616': 'Ronald and Ann Williams Charitable Foundation',
    '731661679': 'Bernard E. and Alba Witkin Charitable Foundation',
    '941540333': 'Northern California Scholarship Foundation',
    '383667071': 'The Elizabeth R. and William J. Patterson Foundation',
    '770259860': 'The Richard and Jean Coyne Family Foundation',
    '472767206': 'Eastern European Jewish Heritage Foundation',
    '942822302': "California Physicians' Service Foundation",
    '770527966': 'Caldwell Fisher Family Foundation',
    '203940983': 'Hobson/Lucas Family Foundation',
    '832713007': 'Sandberg Goldberg Bernthal Family Foundation',
    '461194887': 'Sandberg Goldberg Bernthal Family Foundation',
    '464180144': 'P.J. and K.A. Dougherty Foundation',
    '680168017': 'Simpson PSB Fund',
    '208766740': "The O'Donnell Foundation",
    '941392803': 'S.H. Cowell Foundation',
    '946719570': 'Randall A. Wolf Family Foundation',
    '463653488': 'UCSF Discovery Fellows Fund',
    '943316088': 'MZ Foundation',
    '931463652': 'KHR Family Fund',
    # NY foundations
    '161448017': 'M&T Charitable Foundation',
    '137184401': 'The Leona M. and Harry B. Helmsley Charitable Trust',
    '900747216': 'The JPB Foundation',
    '456290317': 'Donald MacDavid Charitable Trust',
    '273655593': 'S&P Global Foundation',
}

LOWERCASE_WORDS = {'and', 'of', 'for', 'the', 'in', 'at', 'by', 'to', 'a', 'an', 'on', 'or'}
ROMAN_NUMERALS = {'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'}
ABBREVIATIONS = {'LLC', 'LP', 'USA', 'US', 'YMCA', 'YWCA', 'STEM', 'SF', 'SJ', 'SJSU', 'UCLA', 'USC', 'UCSF', 'UC', 'CSU'}
ACRONYM_NAMES = {'RJM', 'AAM', 'KLA', 'MZ', 'KHR', 'XQ', 'PSB', 'K5', 'J-P'}
STRIP_SUFFIXES = [' Inc', ' INC', ' Incorporated']


def clean_foundation_name(raw_name, ein=None):
    """Convert foundation name to clean title case with proper handling of
    articles, prepositions, Roman numerals, and abbreviations."""
    if not raw_name:
        return raw_name

    if ein and ein in NAME_OVERRIDES:
        return NAME_OVERRIDES[ein]

    words = raw_name.strip().split()
    result = []

    for i, word in enumerate(words):
        upper = word.upper()

        if upper in ROMAN_NUMERALS:
            result.append(upper)
        elif upper in ACRONYM_NAMES:
            result.append(upper)
        elif upper in ABBREVIATIONS:
            result.append(upper)
        elif upper.lower() in LOWERCASE_WORDS and i > 0:
            result.append(upper.lower())
        elif "'" in word:
            parts = word.split("'")
            titled = parts[0].capitalize()
            if len(parts) > 1 and len(parts[0]) <= 1:
                rest = "'".join(p.capitalize() for p in parts[1:])
            else:
                rest = "'".join(p.lower() for p in parts[1:])
            result.append(f"{titled}'{rest}")
        elif '-' in word:
            result.append('-'.join(
                p.capitalize() if p.upper() not in LOWERCASE_WORDS else p.lower()
                for p in word.split('-')
            ))
        else:
            result.append(word.capitalize())

    name = ' '.join(result)

    name = re.sub(r'\bMc([a-z])', lambda m: 'Mc' + m.group(1).upper(), name)
    name = re.sub(r'\bMac([a-z])([a-z]{3,})', lambda m: 'Mac' + m.group(1).upper() + m.group(2), name)

    for suffix in STRIP_SUFFIXES:
        if name.endswith(suffix):
            name = name[:-len(suffix)]

    name = name.strip().rstrip('.')
    name = re.sub(r'\s+', ' ', name)

    name = re.sub(r'\bFdn\b', 'Foundation', name)
    name = re.sub(r'\bFnd\b', 'Fund', name)
    name = re.sub(r'\bTr\b', 'Trust', name)

    return name


def clean_city_name(raw_city):
    """Title-case city name."""
    if not raw_city:
        return raw_city
    return raw_city.strip().title()


def fmt_dollars(amount):
    """Format as $X,XXX,XXX."""
    if amount is None:
        return "N/A"
    return f"${amount:,.0f}"


def slugify(label):
    """Convert label to snake_case for filenames."""
    return re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')


# ============================================================================
# State name lookup
# ============================================================================

STATE_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia',
}


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate a branded foundation list PDF for LinkedIn lead gen.',
        epilog=(
            'Note: Foundations are filtered by their home location (where they are '
            'based), not by where they send grants. A Bay Area foundation may fund '
            'organizations nationwide.'
        ),
    )
    parser.add_argument('--state', required=True, help='2-letter state code (e.g., CA, NY). Bounds the query.')
    parser.add_argument('--cities', help='Comma-separated city names, UPPER CASE. Omit for all cities in state.')
    parser.add_argument('--topic-regex', required=True, help='PostgreSQL ~* regex for purpose_text filtering.')
    parser.add_argument('--topic-label', required=True, help='Human-readable topic label for PDF title (e.g., "Youth & Education").')
    parser.add_argument('--geo-label', help='Human-readable geography label (e.g., "Bay Area"). Defaults to state name.')
    parser.add_argument('--output-dir', default='.', help='Directory for output files. Default: current directory.')
    parser.add_argument('--limit', type=int, default=150, help='Top N foundations by total giving. Default: 150.')
    parser.add_argument('--min-year', type=int, default=None, help='Earliest tax_year. Default: current_year - 3.')
    parser.add_argument('--skip-pdf', action='store_true', help='Write .md and .csv only, skip PDF conversion.')
    args = parser.parse_args()

    state = args.state.upper()
    if state not in STATE_NAMES:
        print(f"Error: Unknown state code '{state}'", file=sys.stderr)
        sys.exit(1)

    cities = None
    if args.cities:
        cities = [c.strip().upper() for c in args.cities.split(',') if c.strip()]

    geo_label = args.geo_label or STATE_NAMES[state]
    topic_label = args.topic_label
    min_year = args.min_year or (datetime.datetime.now().year - 3)
    limit = args.limit
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    # Build filename slug from labels
    file_slug = f"{slugify(geo_label)}_{slugify(topic_label)}_foundations_{datetime.datetime.now().year}"

    # ========================================================================
    # Query database
    # ========================================================================
    print(f"Connecting to database...")
    conn = get_connection()

    # Build query with optional city filter
    if cities:
        city_filter = "AND UPPER(df.city) = ANY(%s)"
        query = QUERY.format(city_filter=city_filter)
        params = (state, cities, min_year, args.topic_regex, limit)
    else:
        city_filter = ""
        query = QUERY.format(city_filter=city_filter)
        params = (state, min_year, args.topic_regex, limit)

    print(f"Running query (state={state}, cities={'custom list' if cities else 'all'}, min_year={min_year})...")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"Got {len(rows)} foundations")

    if not rows:
        print("No results. Check your --state, --cities, and --topic-regex parameters.", file=sys.stderr)
        sys.exit(1)

    # ========================================================================
    # Format data
    # ========================================================================
    foundations = []
    for row in rows:
        foundations.append({
            'ein': row['foundation_ein'],
            'name': clean_foundation_name(row['foundation_name'], row['foundation_ein']),
            'city': clean_city_name(row['foundation_city']),
            'assets': row['assets'],
            'accepts_applications': row['accepts_applications'],
            'total_giving': int(row['total_giving']),
            'grant_count': int(row['grant_count']),
            'median_grant': int(row['median_grant']),
            'largest_grant': int(row['largest_grant']),
            'most_recent_year': int(row['most_recent_year']),
        })

    # Truncation warning: names >= 35 chars not in overrides
    truncated = [f for f in foundations if len(f['name']) >= 35 and f['ein'] not in NAME_OVERRIDES]
    if truncated:
        print(f"WARNING: {len(truncated)} foundation names >= 35 chars without overrides (may be IRS-truncated)")

    # ========================================================================
    # Write CSV
    # ========================================================================
    csv_path = os.path.join(output_dir, f'{file_slug}.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'rank', 'ein', 'foundation_name', 'city', 'total_giving',
            'grant_count', 'median_grant', 'largest_grant',
            'assets', 'accepts_applications', 'most_recent_year'
        ])
        writer.writeheader()
        for i, fdn in enumerate(foundations, 1):
            writer.writerow({
                'rank': i,
                'ein': fdn['ein'],
                'foundation_name': fdn['name'],
                'city': fdn['city'],
                'total_giving': fdn['total_giving'],
                'grant_count': fdn['grant_count'],
                'median_grant': fdn['median_grant'],
                'largest_grant': fdn['largest_grant'],
                'assets': fdn['assets'],
                'accepts_applications': fdn['accepts_applications'],
                'most_recent_year': fdn['most_recent_year'],
            })
    print(f"CSV written: {csv_path}")

    # ========================================================================
    # Write Markdown
    # ========================================================================
    total_combined = sum(f['total_giving'] for f in foundations)
    total_grants = sum(f['grant_count'] for f in foundations)
    now = datetime.datetime.now()
    month_year = now.strftime('%B %Y')
    title = f"Top {len(foundations)} {geo_label} Foundations Funding {topic_label}"

    md_lines = []

    # Title area
    md_lines.append(f"# {title}")
    md_lines.append("")
    md_lines.append("# A Free Resource from TheGrantScout")
    md_lines.append("")
    md_lines.append("**Prepared by:** TheGrantScout")
    md_lines.append("")
    md_lines.append(f"**Date:** {month_year}")
    md_lines.append("")
    md_lines.append(f"**Data Source:** IRS 990-PF filings ({min_year}-{now.year - 1})")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # Intro blurb
    md_lines.append("## About This List")
    md_lines.append("")
    md_lines.append(
        f"This list identifies the **top {len(foundations)} private foundations** based in the {geo_label} area "
        f"that have funded {topic_label.lower()} programs between {min_year} and {now.year - 1}. "
        f"Together, these foundations have awarded **{fmt_dollars(total_combined)}** "
        f"across **{total_grants:,} grants** to organizations working in this space."
    )
    md_lines.append("")
    md_lines.append(
        "Foundations are ranked by total giving in this category. "
        "Grant data comes from publicly available IRS 990-PF filings, "
        "which private foundations are required to file annually."
    )
    md_lines.append("")

    # Summary stats
    md_lines.append(f"**Combined {topic_label} Giving:** {fmt_dollars(total_combined)}")
    md_lines.append("")
    md_lines.append(f"**Total Grants in Category:** {total_grants:,}")
    md_lines.append("")
    md_lines.append(f"**Foundations Listed:** {len(foundations)}")
    md_lines.append("")
    if cities:
        city_counts = Counter(f['city'] for f in foundations)
        top_cities = [c for c, _ in city_counts.most_common(10)]
        md_lines.append(f"**Top Cities Represented:** {', '.join(top_cities)}")
    else:
        md_lines.append(f"**State:** {STATE_NAMES[state]}")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # Table
    md_lines.append("## Foundation Rankings")
    md_lines.append("")
    md_lines.append("| Rank | Foundation | City | Total Giving | Grants | Median Grant | Largest Grant |")
    md_lines.append("|------|-----------|------|-------------|--------|-------------|--------------|")

    for i, fdn in enumerate(foundations, 1):
        md_lines.append(
            f"| {i} | {fdn['name']} | {fdn['city']} | "
            f"{fmt_dollars(fdn['total_giving'])} | {fdn['grant_count']:,} | "
            f"{fmt_dollars(fdn['median_grant'])} | {fmt_dollars(fdn['largest_grant'])} |"
        )

    md_lines.append("")

    # Page break + About
    md_lines.append("<!-- PAGE_BREAK -->")
    md_lines.append("")
    md_lines.append("## About TheGrantScout")
    md_lines.append("")
    md_lines.append(
        "TheGrantScout analyzes IRS data on 143,000+ foundations to find the funders "
        "most likely to say yes to your nonprofit. Each month you get:"
    )
    md_lines.append("")
    md_lines.append("- **Personalized foundation matches** ranked by fit with your mission, geography, and budget")
    md_lines.append("- **Contact info, application details, and giving pattern intelligence** for each funder")
    md_lines.append("- **Positioning strategies** based on which similar organizations they have already funded")
    md_lines.append("")
    md_lines.append("Schedule a call to learn more: [aleck@thegrantscout.com](mailto:aleck@thegrantscout.com)")
    md_lines.append("")
    md_lines.append("[thegrantscout.com](https://thegrantscout.com) | *Your mission deserves funding. We will help you find it.*")
    md_lines.append("")
    md_lines.append("*Your mission deserves funding. We will help you find it.*")
    md_lines.append("")

    md_content = '\n'.join(md_lines)
    md_path = os.path.join(output_dir, f'{file_slug}.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Markdown written: {md_path}")

    # ========================================================================
    # Generate PDF
    # ========================================================================
    if not args.skip_pdf:
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_script = os.path.join(tools_dir, 'md_to_pdf.py')
        pdf_path = os.path.join(output_dir, f'{file_slug}.pdf')

        if os.path.exists(pdf_script):
            print(f"Generating PDF...")
            result = subprocess.run(
                ['python3', pdf_script, '--input', md_path, '--output', pdf_path],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print(f"PDF written: {pdf_path}")
            else:
                print(f"PDF generation failed: {result.stderr}", file=sys.stderr)
        else:
            print(f"WARNING: md_to_pdf.py not found at {pdf_script}, skipping PDF", file=sys.stderr)

    # ========================================================================
    # Print summary stats for STOP gate review
    # ========================================================================
    print(f"\n{'='*60}")
    print(f"SUMMARY: {title}")
    print(f"{'='*60}")
    print(f"Foundations: {len(foundations)}")
    print(f"Combined giving: {fmt_dollars(total_combined)}")
    print(f"Total grants: {total_grants:,}")
    print(f"\nTop 10:")
    for i, fdn in enumerate(foundations[:10], 1):
        print(f"  {i}. {fdn['name']} ({fdn['city']}) - {fmt_dollars(fdn['total_giving'])} ({fdn['grant_count']} grants)")

    city_counts = Counter(f['city'] for f in foundations)
    print(f"\nCity distribution (top 10):")
    for city, count in city_counts.most_common(10):
        print(f"  {city}: {count}")

    print(f"\nOutput files:")
    print(f"  CSV: {csv_path}")
    print(f"  Markdown: {md_path}")
    if not args.skip_pdf:
        print(f"  PDF: {os.path.join(output_dir, f'{file_slug}.pdf')}")


if __name__ == '__main__':
    main()
