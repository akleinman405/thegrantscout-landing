#!/usr/bin/env python3
"""Generate 100-nonprofit cold call prospect list (national).

Keywords: veterans, sailing/maritime, aviation, adaptive/recreational therapy,
equine therapy, adventure therapy, wounded warrior.
Only includes GO-viable orgs (adjusted foundation_count >= 50).
Excludes private foundations (pf_returns filers).
Revenue capped at $5M (ED is the right contact at this size).
Caps ~15 orgs per state for geographic diversity.
"""

import csv
import re
import psycopg2

OUTPUT_PATH = "/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-25/DATA_2026-02-25.1_prospect_call_list.csv"

QUERY = """
WITH keyword_matches AS (
    SELECT
        np.ein,
        np.organization_name,
        np.phone,
        np.website,
        np.state,
        np.mission_description,
        np.program_1_desc,
        COALESCE(np.ntee_code, np.bmf_ntee_cd) AS ntee_code,
        COALESCE(np.ed_ceo_name, np.president_name, np.chair_name) AS contact_name,
        COALESCE(np.ed_ceo_title, np.president_title, np.chair_title) AS contact_title,
        CASE
            WHEN np.mission_description ILIKE '%%sailing%%'
              OR np.mission_description ILIKE '%%sailboat%%'
              OR np.mission_description ILIKE '%%maritime%%'
              OR np.program_1_desc ILIKE '%%sailing%%'
              OR np.program_1_desc ILIKE '%%sailboat%%'
              OR np.program_1_desc ILIKE '%%maritime%%'
              OR np.program_2_desc ILIKE '%%sailing%%'
              OR np.program_2_desc ILIKE '%%sailboat%%'
              OR np.program_2_desc ILIKE '%%maritime%%'
              OR np.program_3_desc ILIKE '%%sailing%%'
              OR np.program_3_desc ILIKE '%%sailboat%%'
              OR np.program_3_desc ILIKE '%%maritime%%'
              THEN 'sailing_maritime'
            WHEN np.mission_description ILIKE '%%aviation%%'
              OR np.mission_description ILIKE '%%airplane%%'
              OR np.mission_description ILIKE '%%flight%%'
              OR np.program_1_desc ILIKE '%%aviation%%'
              OR np.program_1_desc ILIKE '%%airplane%%'
              OR np.program_2_desc ILIKE '%%aviation%%'
              OR np.program_3_desc ILIKE '%%aviation%%'
              THEN 'aviation'
            WHEN np.mission_description ILIKE '%%equine therap%%'
              OR np.mission_description ILIKE '%%adventure therap%%'
              OR np.mission_description ILIKE '%%adaptive sport%%'
              OR np.mission_description ILIKE '%%adaptive recreation%%'
              OR np.mission_description ILIKE '%%recreational therap%%'
              OR np.program_1_desc ILIKE '%%equine therap%%'
              OR np.program_1_desc ILIKE '%%adaptive sport%%'
              OR np.program_1_desc ILIKE '%%adaptive recreation%%'
              OR np.program_1_desc ILIKE '%%recreational therap%%'
              OR np.program_1_desc ILIKE '%%adventure therap%%'
              OR np.program_2_desc ILIKE '%%equine therap%%'
              OR np.program_2_desc ILIKE '%%adaptive sport%%'
              OR np.program_2_desc ILIKE '%%recreational therap%%'
              OR np.program_3_desc ILIKE '%%equine therap%%'
              OR np.program_3_desc ILIKE '%%adaptive sport%%'
              OR np.program_3_desc ILIKE '%%recreational therap%%'
              THEN 'adaptive_therapy'
            WHEN np.mission_description ILIKE '%%veteran%%'
              OR np.mission_description ILIKE '%%wounded warrior%%'
              OR np.program_1_desc ILIKE '%%veteran%%'
              OR np.program_1_desc ILIKE '%%wounded warrior%%'
              OR np.program_2_desc ILIKE '%%veteran%%'
              OR np.program_2_desc ILIKE '%%wounded warrior%%'
              OR np.program_3_desc ILIKE '%%veteran%%'
              OR np.program_3_desc ILIKE '%%wounded warrior%%'
              THEN 'veterans'
            ELSE 'other'
        END AS keyword_category
    FROM f990_2025.nonprofits_prospects2 np
    WHERE np.phone IS NOT NULL
      AND np.website IS NOT NULL
      AND np.website NOT IN ('N/A', 'NONE', '0', '')
      AND COALESCE(np.ed_ceo_name, np.president_name, np.chair_name) IS NOT NULL
      AND np.ein NOT IN (SELECT DISTINCT ein FROM f990_2025.pf_returns)
      AND np.state IS NOT NULL
      AND LENGTH(np.state) = 2
      AND (
        np.mission_description ILIKE '%%veteran%%'
        OR np.mission_description ILIKE '%%wounded warrior%%'
        OR np.mission_description ILIKE '%%sailing%%'
        OR np.mission_description ILIKE '%%sailboat%%'
        OR np.mission_description ILIKE '%%maritime%%'
        OR np.mission_description ILIKE '%%aviation%%'
        OR np.mission_description ILIKE '%%airplane%%'
        OR np.mission_description ILIKE '%%flight%%'
        OR np.mission_description ILIKE '%%equine therap%%'
        OR np.mission_description ILIKE '%%adventure therap%%'
        OR np.mission_description ILIKE '%%adaptive sport%%'
        OR np.mission_description ILIKE '%%adaptive recreation%%'
        OR np.mission_description ILIKE '%%recreational therap%%'
        OR np.program_1_desc ILIKE '%%veteran%%'
        OR np.program_1_desc ILIKE '%%wounded warrior%%'
        OR np.program_1_desc ILIKE '%%sailing%%'
        OR np.program_1_desc ILIKE '%%sailboat%%'
        OR np.program_1_desc ILIKE '%%maritime%%'
        OR np.program_1_desc ILIKE '%%aviation%%'
        OR np.program_1_desc ILIKE '%%airplane%%'
        OR np.program_1_desc ILIKE '%%equine therap%%'
        OR np.program_1_desc ILIKE '%%adaptive sport%%'
        OR np.program_1_desc ILIKE '%%adaptive recreation%%'
        OR np.program_1_desc ILIKE '%%recreational therap%%'
        OR np.program_1_desc ILIKE '%%adventure therap%%'
        OR np.program_2_desc ILIKE '%%veteran%%'
        OR np.program_2_desc ILIKE '%%wounded warrior%%'
        OR np.program_2_desc ILIKE '%%sailing%%'
        OR np.program_2_desc ILIKE '%%sailboat%%'
        OR np.program_2_desc ILIKE '%%maritime%%'
        OR np.program_2_desc ILIKE '%%aviation%%'
        OR np.program_2_desc ILIKE '%%equine therap%%'
        OR np.program_2_desc ILIKE '%%adaptive sport%%'
        OR np.program_2_desc ILIKE '%%recreational therap%%'
        OR np.program_3_desc ILIKE '%%veteran%%'
        OR np.program_3_desc ILIKE '%%wounded warrior%%'
        OR np.program_3_desc ILIKE '%%sailing%%'
        OR np.program_3_desc ILIKE '%%sailboat%%'
        OR np.program_3_desc ILIKE '%%maritime%%'
        OR np.program_3_desc ILIKE '%%aviation%%'
        OR np.program_3_desc ILIKE '%%equine therap%%'
        OR np.program_3_desc ILIKE '%%adaptive sport%%'
        OR np.program_3_desc ILIKE '%%recreational therap%%'
      )
),
with_revenue AS (
    SELECT
        km.*,
        nr_rev.total_revenue
    FROM keyword_matches km
    LEFT JOIN LATERAL (
        SELECT nr.total_revenue
        FROM f990_2025.nonprofit_returns nr
        WHERE nr.ein = km.ein
        ORDER BY nr.tax_year DESC
        LIMIT 1
    ) nr_rev ON TRUE
    WHERE COALESCE(nr_rev.total_revenue, 0) <= 5000000
),
with_viability AS (
    SELECT
        wr.*,
        cv.foundation_count,
        FLOOR(cv.foundation_count * 0.85) AS adjusted_count,
        cv.sector_label
    FROM with_revenue wr
    LEFT JOIN f990_2025.cohort_viability cv
        ON cv.state = wr.state
        AND cv.ntee_sector = COALESCE(LEFT(wr.ntee_code, 1), 'Z')
    WHERE FLOOR(COALESCE(cv.foundation_count, 0) * 0.85) >= 50
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
),
ranked AS (
    SELECT
        wf.*,
        ROW_NUMBER() OVER (
            PARTITION BY wf.state
            ORDER BY wf.existing_funder_count DESC, wf.ein
        ) AS state_rank
    FROM with_funders wf
)
SELECT
    ein,
    organization_name,
    phone,
    website,
    state,
    mission_description,
    program_1_desc,
    contact_name,
    contact_title,
    keyword_category,
    foundation_count,
    adjusted_count,
    sector_label,
    existing_funder_count,
    total_revenue
FROM ranked
WHERE state_rank <= 15
ORDER BY existing_funder_count DESC, ein
LIMIT 130
"""

STATE_TIMEZONE = {
    "AL": "Central", "AK": "Alaska", "AZ": "Mountain", "AR": "Central",
    "CA": "Pacific", "CO": "Mountain", "CT": "Eastern", "DE": "Eastern",
    "FL": "Eastern", "GA": "Eastern", "HI": "Hawaii", "ID": "Mountain",
    "IL": "Central", "IN": "Eastern", "IA": "Central", "KS": "Central",
    "KY": "Eastern", "LA": "Central", "ME": "Eastern", "MD": "Eastern",
    "MA": "Eastern", "MI": "Eastern", "MN": "Central", "MS": "Central",
    "MO": "Central", "MT": "Mountain", "NE": "Central", "NV": "Pacific",
    "NH": "Eastern", "NJ": "Eastern", "NM": "Mountain", "NY": "Eastern",
    "NC": "Eastern", "ND": "Central", "OH": "Eastern", "OK": "Central",
    "OR": "Pacific", "PA": "Eastern", "RI": "Eastern", "SC": "Eastern",
    "SD": "Central", "TN": "Central", "TX": "Central", "UT": "Mountain",
    "VT": "Eastern", "VA": "Eastern", "WA": "Pacific", "WV": "Eastern",
    "WI": "Central", "WY": "Mountain", "DC": "Eastern", "PR": "Atlantic",
    "VI": "Atlantic", "GU": "Chamorro", "AS": "Samoa", "MP": "Chamorro",
}


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
        acronyms = {"INC", "LLC", "USA", "US", "II", "III", "IV", "DBA", "PCF", "AFW", "YMCA", "YWCA"}
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
    title = (title.replace("Ceo", "CEO").replace("Cfo", "CFO")
             .replace("Coo", "COO").replace("Vp ", "VP "))
    return title


def truncate_about(mission, program_desc, max_sentences=2):
    """Extract 1-2 sentences for the About field."""
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


def revenue_bucket(revenue):
    """Map revenue to a sortable bucket label."""
    if revenue is None:
        return "Unknown"
    rev = float(revenue)
    if rev < 250000:
        return "1: Under $250K"
    elif rev < 500000:
        return "2: $250K-$500K"
    elif rev < 1000000:
        return "3: $500K-$1M"
    elif rev < 2000000:
        return "4: $1M-$2M"
    else:
        return "5: $2M-$5M"


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

    print(f"Query returned {len(rows)} rows (after viability + state cap)")

    # Category stats (keyword_category=idx 9, state=idx 4)
    cats = {}
    states = {}
    for row in rows:
        cat = row[9]
        st = row[4]
        cats[cat] = cats.get(cat, 0) + 1
        states[st] = states.get(st, 0) + 1
    print(f"Category breakdown: {cats}")
    print(f"State distribution ({len(states)} states): {dict(sorted(states.items(), key=lambda x: -x[1]))}")

    headers = [
        "Org", "Priority", "Date Contacted", "Phone", "Contact", "Title",
        "Email", "State", "Timezone", "Dependents", "EIN", "Rating",
        "Website", "About", "Revenue"
    ]

    csv_rows = []
    for row in rows[:100]:
        ein, org_name, phone, website, state, mission, prog1, contact, title, \
            kw_cat, fdn_count, adj_count, sector_label, funder_count, total_rev = row

        csv_rows.append([
            title_case_org(org_name),
            "",
            "",
            format_phone(phone),
            title_case_name(contact),
            clean_title(title),
            "",
            state,
            STATE_TIMEZONE.get(state, ""),
            "",
            ein,
            "",
            clean_website(website),
            truncate_about(mission, prog1),
            revenue_bucket(total_rev),
        ])

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(csv_rows)

    print(f"\nWrote {len(csv_rows)} rows to {OUTPUT_PATH}")

    # Stats for report
    print(f"\n--- Stats for report ---")
    print(f"Total query results (viable, state-capped): {len(rows)}")
    print(f"CSV rows written: {len(csv_rows)}")

    # Category breakdown for output rows
    out_cats = {}
    out_states = {}
    for row in rows[:100]:
        cat = row[9]
        st = row[4]
        out_cats[cat] = out_cats.get(cat, 0) + 1
        out_states[st] = out_states.get(st, 0) + 1
    print(f"\nCategory breakdown (output {len(csv_rows)} rows):")
    for cat, cnt in sorted(out_cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}")

    print(f"\nState distribution (output {len(csv_rows)} rows, {len(out_states)} states):")
    for st, cnt in sorted(out_states.items(), key=lambda x: -x[1]):
        print(f"  {st}: {cnt}")

    # Max per state check
    max_state = max(out_states.values())
    max_state_name = [s for s, c in out_states.items() if c == max_state][0]
    print(f"\nMax orgs in one state: {max_state} ({max_state_name})")
    if max_state > 15:
        print(f"WARNING: State cap exceeded!")

    # Revenue bucket breakdown
    rev_buckets = {}
    for r in csv_rows:
        b = r[14]
        rev_buckets[b] = rev_buckets.get(b, 0) + 1
    print(f"\nRevenue bucket breakdown:")
    for b, cnt in sorted(rev_buckets.items()):
        print(f"  {b}: {cnt}")

    # Data quality checks
    nulls = {h: 0 for h in ["Org", "Phone", "Contact", "EIN", "Website", "About"]}
    for r in csv_rows:
        if not r[0]: nulls["Org"] += 1
        if not r[3]: nulls["Phone"] += 1
        if not r[4]: nulls["Contact"] += 1
        if not r[10]: nulls["EIN"] += 1
        if not r[12]: nulls["Website"] += 1
        if not r[13]: nulls["About"] += 1
    print(f"Null check (should all be 0): {nulls}")

    # Blank column check
    blank_ok = True
    for r in csv_rows:
        for idx, col in [(1, "Priority"), (2, "Date Contacted"), (6, "Email"), (9, "Dependents"), (11, "Rating")]:
            if r[idx]:
                print(f"WARNING: {col} not blank in row {r[10]}")
                blank_ok = False
    if blank_ok:
        print("Blank columns: all verified empty")

    # Funder count stats
    funder_counts = [row[13] for row in rows[:100]]
    with_funders = sum(1 for f in funder_counts if f > 0)
    print(f"Existing funder counts: min={min(funder_counts)}, max={max(funder_counts)}, "
          f"median={sorted(funder_counts)[len(funder_counts)//2]}, with_funders={with_funders}/{len(funder_counts)}")

    # Viability stats
    adj_counts = [row[11] for row in rows[:100]]
    print(f"Adjusted foundation counts: min={min(adj_counts)}, max={max(adj_counts)}, "
          f"median={sorted(adj_counts)[len(adj_counts)//2]}")


if __name__ == "__main__":
    main()
