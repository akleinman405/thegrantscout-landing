#!/usr/bin/env python3
"""
Generate Bay Area Youth & Education Foundation List
====================================================
Queries the database, formats data, writes markdown + CSV.
"""

import os
import re
import csv
import psycopg2
import psycopg2.extras

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# Bay Area cities (6 counties: SF, Alameda, San Mateo, Santa Clara, Marin, Contra Costa
# plus Napa, Sonoma, Santa Cruz for broader Bay Area)
# ============================================================================
BAY_AREA_CITIES = [
    'SAN FRANCISCO','OAKLAND','BERKELEY','PALO ALTO','SAN JOSE','MENLO PARK',
    'MOUNTAIN VIEW','SUNNYVALE','SANTA CLARA','REDWOOD CITY','SAN MATEO',
    'FREMONT','HAYWARD','RICHMOND','WALNUT CREEK','CONCORD','PLEASANTON',
    'LIVERMORE','DUBLIN','SAN RAFAEL','MILL VALLEY','SAUSALITO','TIBURON',
    'NOVATO','LARKSPUR','CORTE MADERA','ROSS','FAIRFAX','SAN ANSELMO',
    'BELVEDERE','KENTFIELD','BURLINGAME','HILLSBOROUGH','ATHERTON','WOODSIDE',
    'PORTOLA VALLEY','LOS ALTOS','LOS ALTOS HILLS','CUPERTINO','CAMPBELL',
    'SARATOGA','LOS GATOS','MILPITAS','SANTA CRUZ','CAPITOLA','SCOTTS VALLEY',
    'DALY CITY','SOUTH SAN FRANCISCO','PACIFICA','HALF MOON BAY',
    'SAN CARLOS','BELMONT','FOSTER CITY','ALAMEDA','EMERYVILLE','PIEDMONT',
    'ORINDA','LAFAYETTE','MORAGA','DANVILLE','SAN RAMON','UNION CITY',
    'NEWARK','NAPA','SONOMA','PETALUMA','SANTA ROSA','HEALDSBURG',
    'SEBASTOPOL','VALLEJO','BENICIA',
]

PURPOSE_REGEX = r'youth|education|school|student|children|after.school|tutoring|literacy|scholarship|elementary|secondary|k.12|young people|child'

QUERY = """
WITH youth_ed_grants AS (
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
    WHERE df.state = 'CA'
      AND UPPER(df.city) = ANY(%s)
      AND fg.tax_year >= 2022
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
FROM youth_ed_grants
GROUP BY foundation_ein, foundation_name, foundation_city, assets, accepts_applications
ORDER BY total_giving DESC
LIMIT 150
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
}

# Words that should stay lowercase mid-name
LOWERCASE_WORDS = {'and', 'of', 'for', 'the', 'in', 'at', 'by', 'to', 'a', 'an', 'on', 'or'}

# Roman numerals to keep uppercase
ROMAN_NUMERALS = {'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'}

# Known abbreviations to keep uppercase
ABBREVIATIONS = {'LLC', 'LP', 'USA', 'US', 'YMCA', 'YWCA', 'STEM', 'SF', 'SJ', 'SJSU', 'UCLA', 'USC', 'UCSF', 'UC', 'CSU'}

# Short uppercase acronym names (2-4 letter names that are acronyms, not words)
ACRONYM_NAMES = {'RJM', 'AAM', 'KLA', 'MZ', 'KHR', 'XQ', 'PSB', 'K5', 'J-P'}

# Suffixes to strip from display names (still in CSV)
STRIP_SUFFIXES = [' Inc', ' INC', ' Incorporated']


def clean_foundation_name(raw_name, ein=None):
    """Convert foundation name to clean title case with proper handling of
    articles, prepositions, Roman numerals, and abbreviations."""
    if not raw_name:
        return raw_name

    # Check EIN-based overrides first (for truncated IRS names)
    if ein and ein in NAME_OVERRIDES:
        return NAME_OVERRIDES[ein]

    # Start with title case
    words = raw_name.strip().split()
    result = []

    for i, word in enumerate(words):
        upper = word.upper()

        # Roman numerals
        if upper in ROMAN_NUMERALS:
            result.append(upper)
        # Known acronyms (multi-letter foundation name abbreviations)
        elif upper in ACRONYM_NAMES:
            result.append(upper)
        # Known abbreviations
        elif upper in ABBREVIATIONS:
            result.append(upper)
        # Lowercase articles/prepositions (but not first word)
        elif upper.lower() in LOWERCASE_WORDS and i > 0:
            result.append(upper.lower())
        # Handle possessives and contractions
        elif "'" in word:
            parts = word.split("'")
            titled = parts[0].capitalize()
            if len(parts) > 1 and len(parts[0]) <= 1:
                # Single letter prefix (O'Donnell, D'Angelo) - capitalize after apostrophe
                rest = "'".join(p.capitalize() for p in parts[1:])
            else:
                # Possessives (Physicians') - keep lowercase
                rest = "'".join(p.lower() for p in parts[1:])
            result.append(f"{titled}'{rest}")
        # Handle hyphenated words
        elif '-' in word:
            result.append('-'.join(
                p.capitalize() if p.upper() not in LOWERCASE_WORDS else p.lower()
                for p in word.split('-')
            ))
        else:
            result.append(word.capitalize())

    name = ' '.join(result)

    # Fix "Mc" and "Mac" prefixes (McDonald, MacArthur)
    name = re.sub(r'\bMc([a-z])', lambda m: 'Mc' + m.group(1).upper(), name)
    name = re.sub(r'\bMac([a-z])([a-z]{3,})', lambda m: 'Mac' + m.group(1).upper() + m.group(2), name)

    # Strip "Inc" / "INC" suffix for cleaner display
    for suffix in STRIP_SUFFIXES:
        if name.endswith(suffix):
            name = name[:-len(suffix)]

    # Remove trailing periods and extra whitespace
    name = name.strip().rstrip('.')
    name = re.sub(r'\s+', ' ', name)

    # Fix "Fdn" -> "Foundation", "Fnd" -> "Fund"
    name = re.sub(r'\bFdn\b', 'Foundation', name)
    name = re.sub(r'\bFnd\b', 'Fund', name)
    name = re.sub(r'\bTr\b', 'Trust', name)
    name = re.sub(r'\bFnd\b', 'Fund', name)

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


# ============================================================================
# Main
# ============================================================================

def main():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='thegrantscout',
        user='postgres',
        password='rel0aded'
    )

    print("Running query...")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(QUERY, (BAY_AREA_CITIES, PURPOSE_REGEX))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"Got {len(rows)} foundations")

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

    # ========================================================================
    # Write CSV (extra columns, raw numbers)
    # ========================================================================
    csv_path = os.path.join(OUTPUT_DIR, 'bay_area_youth_education_foundations_2026.csv')
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

    md_lines = []

    # Title area
    md_lines.append("# Top 150 Bay Area Foundations Funding Youth and Education")
    md_lines.append("")
    md_lines.append("# A Free Resource from TheGrantScout")
    md_lines.append("")
    md_lines.append("**Prepared by:** TheGrantScout")
    md_lines.append("")
    md_lines.append("**Date:** February 2026")
    md_lines.append("")
    md_lines.append("**Data Source:** IRS 990-PF filings (2022-2024)")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # Intro blurb
    md_lines.append("## About This List")
    md_lines.append("")
    md_lines.append(
        f"This list identifies the **top 150 private foundations** in the San Francisco Bay Area "
        f"that have funded youth and education programs between 2022 and 2024. "
        f"Together, these foundations have awarded **{fmt_dollars(total_combined)}** "
        f"across **{total_grants:,} grants** to organizations working in K-12 education, "
        f"scholarships, literacy, after-school programs, and youth development."
    )
    md_lines.append("")
    md_lines.append(
        "Foundations are ranked by total giving in this category. "
        "Grant data comes from publicly available IRS 990-PF filings, "
        "which private foundations are required to file annually."
    )
    md_lines.append("")

    # Summary stats
    md_lines.append("**Combined Youth/Education Giving:** " + fmt_dollars(total_combined))
    md_lines.append("")
    md_lines.append(f"**Total Grants in Category:** {total_grants:,}")
    md_lines.append("")
    md_lines.append(f"**Foundations Listed:** {len(foundations)}")
    md_lines.append("")
    md_lines.append(f"**Bay Area Counties Covered:** San Francisco, Alameda, San Mateo, Santa Clara, Marin, Contra Costa, Napa, Sonoma, Santa Cruz")
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

    # Page break + CTA
    md_lines.append("<!-- PAGE_BREAK -->")
    md_lines.append("")
    md_lines.append("## What Comes Next?")
    md_lines.append("")
    md_lines.append(
        "This list tells you **who** is funding youth and education in the Bay Area. "
        "But knowing a foundation exists is just the starting point. "
        "The real question is: which of these foundations are the best fit for **your** organization?"
    )
    md_lines.append("")
    md_lines.append("### TheGrantScout helps you answer that question.")
    md_lines.append("")
    md_lines.append("We analyze IRS data on 143,000+ private foundations to find the funders most likely to say yes to your nonprofit. Our reports include:")
    md_lines.append("")
    md_lines.append("- **Personalized funder matches** ranked by fit with your mission, geography, and budget")
    md_lines.append("- **Giving pattern intelligence** showing each foundation's typical grant size, repeat funding rate, and sector focus")
    md_lines.append("- **Contact information and application details** so you can take action immediately")
    md_lines.append("- **Comparable grant examples** showing similar organizations that received funding")
    md_lines.append("- **Relationship-building strategies** tailored to each foundation's giving style")
    md_lines.append("")
    md_lines.append(
        "Whether you are a small nonprofit looking for your first foundation grant or an "
        "experienced fundraiser seeking new prospects, we surface the funders you did not know about "
        "and provide the intelligence to maximize your success."
    )
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("**Ready to find your best-fit funders?**")
    md_lines.append("")
    md_lines.append("Visit [thegrantscout.com](https://thegrantscout.com) to learn more.")
    md_lines.append("")
    md_lines.append("Connect with us on [LinkedIn](https://www.linkedin.com/company/thegrantscout).")
    md_lines.append("")
    md_lines.append("Questions? Email [aleck@thegrantscout.com](mailto:aleck@thegrantscout.com).")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("*Your mission deserves funding. We will help you find it.*")
    md_lines.append("")

    md_content = '\n'.join(md_lines)
    md_path = os.path.join(OUTPUT_DIR, 'Bay_Area_Youth_Education_Foundations_2026.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Markdown written: {md_path}")

    # ========================================================================
    # Print summary stats for session report
    # ========================================================================
    print("\n=== SUMMARY STATS ===")
    print(f"Foundations: {len(foundations)}")
    print(f"Combined giving: {fmt_dollars(total_combined)}")
    print(f"Total grants: {total_grants:,}")
    print(f"Top 10:")
    for i, fdn in enumerate(foundations[:10], 1):
        print(f"  {i}. {fdn['name']} ({fdn['city']}) - {fmt_dollars(fdn['total_giving'])} ({fdn['grant_count']} grants)")

    # City distribution
    from collections import Counter
    city_counts = Counter(f['city'] for f in foundations)
    print(f"\nCity distribution (top 10):")
    for city, count in city_counts.most_common(10):
        print(f"  {city}: {count}")

    print("\nDone!")


if __name__ == '__main__':
    main()
