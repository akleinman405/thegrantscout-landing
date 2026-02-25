#!/usr/bin/env python3
"""Generate 100-nonprofit cold call prospect list for CA.

Keywords: veterans, sailing/maritime, aviation, adaptive/recreational therapy.
Only includes GO-viable orgs (50+ production-ready foundations).
Excludes private foundations (pf_returns filers).
"""

import csv
import re
import sys
import psycopg2

OUTPUT_PATH = "/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-25/DATA_2026-02-25.1_prospect_call_list.csv"

QUERY = """
WITH keyword_matches AS (
    SELECT
        np.ein,
        np.organization_name,
        np.phone,
        np.website,
        np.mission_description,
        np.program_1_desc,
        COALESCE(np.ntee_code, np.bmf_ntee_cd) AS ntee_code,
        COALESCE(np.ed_ceo_name, np.president_name, np.chair_name) AS contact_name,
        COALESCE(np.ed_ceo_title, np.president_title, np.chair_title) AS contact_title,
        CASE
            WHEN np.mission_description ILIKE '%%sailing%%'
              OR np.mission_description ILIKE '%%maritime%%'
              OR np.program_1_desc ILIKE '%%sailing%%'
              OR np.program_1_desc ILIKE '%%maritime%%'
              OR np.program_2_desc ILIKE '%%sailing%%'
              OR np.program_2_desc ILIKE '%%maritime%%'
              OR np.program_3_desc ILIKE '%%sailing%%'
              OR np.program_3_desc ILIKE '%%maritime%%'
              THEN 'sailing'
            WHEN np.mission_description ILIKE '%%aviation%%'
              OR np.program_1_desc ILIKE '%%aviation%%'
              OR np.program_2_desc ILIKE '%%aviation%%'
              OR np.program_3_desc ILIKE '%%aviation%%'
              THEN 'aviation'
            WHEN np.mission_description ILIKE '%%adaptive therap%%'
              OR np.mission_description ILIKE '%%recreational therap%%'
              OR np.program_1_desc ILIKE '%%adaptive therap%%'
              OR np.program_1_desc ILIKE '%%recreational therap%%'
              OR np.program_2_desc ILIKE '%%adaptive therap%%'
              OR np.program_2_desc ILIKE '%%recreational therap%%'
              OR np.program_3_desc ILIKE '%%adaptive therap%%'
              OR np.program_3_desc ILIKE '%%recreational therap%%'
              THEN 'adaptive'
            ELSE 'veterans'
        END AS keyword_category
    FROM f990_2025.nonprofits_prospects2 np
    WHERE np.state = 'CA'
      AND np.phone IS NOT NULL
      AND np.website IS NOT NULL
      AND np.website NOT IN ('N/A', 'NONE', '0', '')
      AND COALESCE(np.ed_ceo_name, np.president_name, np.chair_name) IS NOT NULL
      AND np.ein NOT IN (SELECT DISTINCT ein FROM f990_2025.pf_returns)
      AND (
        np.mission_description ILIKE '%%veteran%%'
        OR np.mission_description ILIKE '%%sailing%%'
        OR np.mission_description ILIKE '%%maritime%%'
        OR np.mission_description ILIKE '%%aviation%%'
        OR np.mission_description ILIKE '%%adaptive therap%%'
        OR np.mission_description ILIKE '%%recreational therap%%'
        OR np.program_1_desc ILIKE '%%veteran%%'
        OR np.program_1_desc ILIKE '%%sailing%%'
        OR np.program_1_desc ILIKE '%%maritime%%'
        OR np.program_1_desc ILIKE '%%aviation%%'
        OR np.program_1_desc ILIKE '%%adaptive therap%%'
        OR np.program_1_desc ILIKE '%%recreational therap%%'
        OR np.program_2_desc ILIKE '%%veteran%%'
        OR np.program_2_desc ILIKE '%%sailing%%'
        OR np.program_2_desc ILIKE '%%maritime%%'
        OR np.program_2_desc ILIKE '%%aviation%%'
        OR np.program_2_desc ILIKE '%%adaptive therap%%'
        OR np.program_2_desc ILIKE '%%recreational therap%%'
        OR np.program_3_desc ILIKE '%%veteran%%'
        OR np.program_3_desc ILIKE '%%sailing%%'
        OR np.program_3_desc ILIKE '%%maritime%%'
        OR np.program_3_desc ILIKE '%%aviation%%'
        OR np.program_3_desc ILIKE '%%adaptive therap%%'
        OR np.program_3_desc ILIKE '%%recreational therap%%'
      )
),
with_viability AS (
    SELECT
        km.*,
        cv.foundation_count,
        FLOOR(cv.foundation_count * 0.85) AS adjusted_count,
        cv.sector_label
    FROM keyword_matches km
    LEFT JOIN f990_2025.cohort_viability cv
        ON cv.state = 'CA'
        AND cv.ntee_sector = COALESCE(LEFT(km.ntee_code, 1), 'Z')
),
with_funders AS (
    SELECT
        wv.*,
        COALESCE(fc.funder_count, 0) AS existing_funder_count
    FROM with_viability wv
    LEFT JOIN (
        SELECT fg.recipient_ein, COUNT(DISTINCT fg.foundation_ein) AS funder_count
        FROM f990_2025.fact_grants fg
        WHERE fg.tax_year >= 2019
        GROUP BY fg.recipient_ein
    ) fc ON fc.recipient_ein = wv.ein
    WHERE wv.adjusted_count >= 50
)
SELECT
    ein,
    organization_name,
    phone,
    website,
    mission_description,
    program_1_desc,
    contact_name,
    contact_title,
    keyword_category,
    foundation_count,
    adjusted_count,
    sector_label,
    existing_funder_count
FROM with_funders
ORDER BY existing_funder_count DESC, ein
LIMIT 120
"""


def format_phone(raw):
    """Format phone as XXX-XXX-XXXX."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits[0] == "1":
        digits = digits[1:]
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return raw.strip()


def title_case_name(name):
    """Title-case a person name, handling common patterns."""
    if not name:
        return ""
    name = name.strip()
    lower_words = {"of", "the", "and", "in", "for", "de", "la", "le", "van", "von"}
    parts = name.split()
    result = []
    for i, part in enumerate(parts):
        if part.lower() in lower_words and i > 0:
            result.append(part.lower())
        elif len(part) <= 3 and part.upper() == part and not part.endswith("."):
            result.append(part.upper())
        else:
            result.append(part.capitalize())
    return " ".join(result)


def title_case_org(name):
    """Title-case an org name, preserving acronyms and common patterns."""
    if not name:
        return ""
    name = name.strip()
    if name == name.upper() and len(name) > 5:
        lower_words = {"of", "the", "and", "in", "for", "a", "an", "to", "on", "at", "by"}
        acronyms = {"INC", "LLC", "USA", "US", "II", "III", "IV", "DBA", "PCF", "AFW"}
        parts = name.split()
        result = []
        for i, part in enumerate(parts):
            clean = part.rstrip(",.'")
            suffix = part[len(clean):]
            if clean.upper() in acronyms:
                result.append(clean.upper() + suffix)
            elif clean.lower() in lower_words and i > 0:
                result.append(clean.lower() + suffix)
            else:
                result.append(clean.capitalize() + suffix)
        return " ".join(result)
    return name


def clean_title(title):
    """Clean and normalize officer title."""
    if not title:
        return ""
    title = title.strip()
    if title.upper() == title or title.lower() == title:
        title = title.title()
    title = title.replace("Ceo", "CEO").replace("Cfo", "CFO").replace("Coo", "COO")
    return title


def truncate_about(mission, program_desc, max_sentences=2):
    """Extract 1-2 sentences for the About field. Normalize case if all-caps."""
    text = mission or program_desc or ""
    text = text.strip()
    if not text:
        return ""
    junk = {"SEE SCHEDULE O", "SEE SCHEDULE O.", "REFER TO SCHEDULE O", "N/A", "NONE"}
    if text.upper().strip().rstrip(".") in {j.rstrip(".") for j in junk}:
        text = (program_desc or "").strip()
        if not text:
            return ""
    if text == text.upper() and len(text) > 20:
        text = text.capitalize()
        text = re.sub(r"\.\s+([a-z])", lambda m: ". " + m.group(1).upper(), text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    result = " ".join(sentences[:max_sentences])
    if len(result) > 300:
        cut = result[:300].rfind(" ")
        if cut > 200:
            result = result[:cut] + "..."
        else:
            result = result[:297] + "..."
    return result


def clean_website(url):
    """Lowercase and clean website URL."""
    if not url:
        return ""
    url = url.strip().lower()
    if not url.startswith("http"):
        url = "https://" + url
    return url


def main():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="thegrantscout",
        user="postgres",
        password="postgres",
    )
    try:
        cur = conn.cursor()
        cur.execute(QUERY)
        rows = cur.fetchall()
        cur.close()
    finally:
        conn.close()

    print(f"Query returned {len(rows)} rows")

    # Category stats
    cats = {}
    for row in rows:
        cat = row[8]
        cats[cat] = cats.get(cat, 0) + 1
    print(f"Category breakdown: {cats}")

    # Build CSV rows
    headers = [
        "Org", "Priority", "Date Contacted", "Phone", "Contact", "Title",
        "Email", "State", "Timezone", "Dependents", "EIN", "Rating",
        "Website", "About"
    ]

    csv_rows = []
    for row in rows[:100]:
        ein, org_name, phone, website, mission, prog1, contact, title, \
            kw_cat, fdn_count, adj_count, sector_label, funder_count = row

        csv_rows.append([
            title_case_org(org_name),     # Org
            "",                           # Priority (blank)
            "",                           # Date Contacted (blank)
            format_phone(phone),          # Phone
            title_case_name(contact),     # Contact
            clean_title(title),           # Title
            "",                           # Email (blank)
            "CA",                         # State
            "Pacific",                    # Timezone
            "",                           # Dependents (blank)
            ein,                          # EIN
            "",                           # Rating (blank)
            clean_website(website),       # Website
            truncate_about(mission, prog1),  # About
        ])

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(csv_rows)

    print(f"Wrote {len(csv_rows)} rows to {OUTPUT_PATH}")

    # Print stats for report
    print(f"\n--- Stats for report ---")
    print(f"Total query results: {len(rows)}")
    print(f"CSV rows written: {len(csv_rows)}")
    print(f"Category breakdown (all {len(rows)} results):")
    for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}")

    # Check data quality
    nulls = {h: 0 for h in ["Org", "Phone", "Contact", "EIN", "Website", "About"]}
    for r in csv_rows:
        if not r[0]: nulls["Org"] += 1
        if not r[3]: nulls["Phone"] += 1
        if not r[4]: nulls["Contact"] += 1
        if not r[10]: nulls["EIN"] += 1
        if not r[12]: nulls["Website"] += 1
        if not r[13]: nulls["About"] += 1
    print(f"Null check (should all be 0): {nulls}")

    # Check blank columns are truly blank
    for r in csv_rows:
        for idx, col in [(1, "Priority"), (2, "Date Contacted"), (6, "Email"), (9, "Dependents"), (11, "Rating")]:
            if r[idx]:
                print(f"WARNING: {col} not blank in row {r[10]}")

    # Funder count stats
    funder_counts = [row[12] for row in rows[:100]]
    print(f"Existing funder counts: min={min(funder_counts)}, max={max(funder_counts)}, "
          f"median={sorted(funder_counts)[50]}, with_funders={sum(1 for f in funder_counts if f > 0)}")


if __name__ == "__main__":
    main()
