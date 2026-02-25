#!/usr/bin/env python3
"""
TheGrantScout Call List Generator
==================================

Queries the database for nonprofits matching keyword categories, applies
viability screening, geographic diversity caps, and revenue filters, then
outputs a cold-call prospect CSV.

Keywords and presets are defined in:
    4. Pipeline/config/call_list_keywords.json

Usage:
    python3 "0. Tools/generate_call_list.py" --preset veterans-national
    python3 "0. Tools/generate_call_list.py" --categories veterans,sailing_maritime --state CA
    python3 "0. Tools/generate_call_list.py" --list-presets
    python3 "0. Tools/generate_call_list.py" --preset veterans-national --preview-only
    python3 "0. Tools/generate_call_list.py" --preset veterans-national --dry-run
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("Error: psycopg2 not installed. Run: pip3 install psycopg2", file=sys.stderr)
    sys.exit(1)

# Add Tools directory to path for text_utils import
_tools_dir = os.path.dirname(os.path.abspath(__file__))
if _tools_dir not in sys.path:
    sys.path.insert(0, _tools_dir)

from text_utils import (
    STATE_TIMEZONE, format_phone, clean_website, title_case_name,
    title_case_org, clean_title, truncate_about, revenue_bucket,
)

# ============================================================================
# Constants
# ============================================================================

SCHEMA = "f990_2025"

# Resolve config path relative to project root (two levels up from 0. Tools/)
_project_root = Path(_tools_dir).parent
CONFIG_PATH = _project_root / "4. Pipeline" / "config" / "call_list_keywords.json"

# Whitelist of allowed search fields (prevents SQL injection via config)
ALLOWED_FIELDS = {"mission_description", "program_1_desc", "program_2_desc", "program_3_desc", "org_description"}

# Category name validation pattern
CATEGORY_NAME_RE = re.compile(r'^[a-z][a-z0-9_]*$')

CSV_COLUMNS = [
    "Org", "Priority", "Date Contacted", "Phone", "Contact", "Title",
    "Email", "State", "Timezone", "Dependents", "EIN", "Rating",
    "Website", "About", "Revenue",
]


# ============================================================================
# Config loading
# ============================================================================

def load_config(config_path=None):
    """Load and validate keyword config JSON."""
    path = Path(config_path) if config_path else CONFIG_PATH
    if not path.exists():
        print(f"Error: Config file not found at {path}", file=sys.stderr)
        print(f"Expected: 4. Pipeline/config/call_list_keywords.json", file=sys.stderr)
        sys.exit(1)

    with open(path, "r") as f:
        config = json.load(f)

    # Validate search_fields against whitelist
    for field in config.get("search_fields", []):
        if field not in ALLOWED_FIELDS:
            print(f"Error: search_field '{field}' not in allowed list: {ALLOWED_FIELDS}", file=sys.stderr)
            sys.exit(1)

    # Validate category names (used as SQL string literals in CASE THEN)
    for cat_name in config.get("categories", {}):
        if not CATEGORY_NAME_RE.match(cat_name):
            print(f"Error: Category name '{cat_name}' must be lowercase alphanumeric + underscores", file=sys.stderr)
            sys.exit(1)

    return config


def resolve_params(config, args):
    """Merge preset + CLI flags + defaults into final parameters."""
    defaults = config.get("defaults", {})
    params = {
        "categories": list(config["categories"].keys()),
        "state": None,
        "max_revenue": defaults.get("max_revenue", 5000000),
        "viability_haircut": defaults.get("viability_haircut", 0.85),
        "viability_threshold": defaults.get("viability_threshold", 50),
        "state_cap": defaults.get("state_cap", 15),
        "limit": defaults.get("limit", 100),
        "grant_year_cutoff": defaults.get("grant_year_cutoff", 2019),
    }

    # Apply preset if specified
    if args.preset:
        presets = config.get("presets", {})
        if args.preset not in presets:
            print(f"Error: Unknown preset '{args.preset}'", file=sys.stderr)
            print(f"Available presets:", file=sys.stderr)
            for name, p in presets.items():
                print(f"  {name}: {p.get('description', '')}", file=sys.stderr)
            sys.exit(1)
        preset = presets[args.preset]
        for key in ["categories", "state", "max_revenue", "limit", "state_cap"]:
            if key in preset:
                params[key] = preset[key]

    # CLI flags override preset and defaults
    if args.categories:
        params["categories"] = [c.strip() for c in args.categories.split(",")]
    if args.state:
        params["state"] = args.state.upper()
    if args.max_revenue is not None:
        params["max_revenue"] = args.max_revenue
    if args.limit is not None:
        params["limit"] = args.limit
    if args.state_cap is not None:
        params["state_cap"] = args.state_cap

    # Validate selected categories exist in config
    for cat in params["categories"]:
        if cat not in config["categories"]:
            print(f"Error: Category '{cat}' not found in config. Available: {list(config['categories'].keys())}", file=sys.stderr)
            sys.exit(1)

    return params


# ============================================================================
# SQL builder
# ============================================================================

def build_sql(config, resolved):
    """Build parameterized SQL query. Returns (sql_string, params_tuple).

    CRITICAL: WHERE clause and CASE statement both generate %s placeholders.
    A single shared `params` list accumulates all values in order. An assertion
    at the end verifies placeholder count matches param count.
    """
    search_fields = config["search_fields"]
    categories = config["categories"]
    selected = resolved["categories"]
    params = []

    # --- Build WHERE keyword clause ---
    where_keyword_parts = []
    for cat_name in selected:
        cat = categories[cat_name]
        for kw in cat["keywords"]:
            field_ors = []
            for field in search_fields:
                field_ors.append(f"np.{field} ILIKE %s")
                params.append(f"%{kw}%")
            where_keyword_parts.append(f"({' OR '.join(field_ors)})")

    where_keywords_sql = " OR ".join(where_keyword_parts)

    # --- Build CASE statement (sorted by priority, lower = evaluated first) ---
    sorted_cats = sorted(
        [(name, categories[name]) for name in selected],
        key=lambda x: x[1].get("priority", 99)
    )

    case_whens = []
    for cat_name, cat in sorted_cats:
        for kw in cat["keywords"]:
            field_ors = []
            for field in search_fields:
                field_ors.append(f"np.{field} ILIKE %s")
                params.append(f"%{kw}%")
            case_whens.append(f"WHEN {' OR '.join(field_ors)} THEN '{cat_name}'")

    case_sql = "CASE\n" + "\n".join(f"            {w}" for w in case_whens) + "\n            ELSE 'other'\n        END"

    # --- State filter ---
    state_where = ""
    if resolved["state"]:
        state_where = "AND np.state = %s"
        params.append(resolved["state"])

    # --- Remaining parameters (in SQL order) ---
    params.append(resolved["max_revenue"])        # revenue cap
    params.append(resolved["viability_haircut"])   # haircut for adjusted_count display
    params.append(resolved["viability_haircut"])   # haircut for WHERE clause
    params.append(resolved["viability_threshold"]) # threshold
    params.append(resolved["grant_year_cutoff"])   # grant year cutoff

    # State cap: use a very large number if None (no cap)
    effective_state_cap = resolved["state_cap"] if resolved["state_cap"] is not None else 999999
    params.append(effective_state_cap)             # state_rank cap
    params.append(resolved["limit"] + 30)          # query limit (pad for filtering)

    sql = f"""
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
        {case_sql} AS keyword_category
    FROM {SCHEMA}.nonprofits_prospects2 np
    WHERE np.phone IS NOT NULL
      AND np.website IS NOT NULL
      AND np.website NOT IN ('N/A', 'NONE', '0', '')
      AND COALESCE(np.ed_ceo_name, np.president_name, np.chair_name) IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM {SCHEMA}.pf_returns pr WHERE pr.ein = np.ein
      )
      AND np.state IS NOT NULL
      AND LENGTH(np.state) = 2
      {state_where}
      AND ({where_keywords_sql})
),
with_revenue AS (
    SELECT
        km.*,
        nr_rev.total_revenue
    FROM keyword_matches km
    LEFT JOIN LATERAL (
        SELECT nr.total_revenue
        FROM {SCHEMA}.nonprofit_returns nr
        WHERE nr.ein = km.ein
        ORDER BY nr.tax_year DESC
        LIMIT 1
    ) nr_rev ON TRUE
    WHERE COALESCE(nr_rev.total_revenue, 0) <= %s
),
with_viability AS (
    SELECT
        wr.*,
        cv.foundation_count,
        FLOOR(cv.foundation_count * %s) AS adjusted_count,
        cv.sector_label
    FROM with_revenue wr
    LEFT JOIN {SCHEMA}.cohort_viability cv
        ON cv.state = wr.state
        AND cv.ntee_sector = COALESCE(LEFT(wr.ntee_code, 1), 'Z')
    WHERE FLOOR(COALESCE(cv.foundation_count, 0) * %s) >= %s
),
with_funders AS (
    SELECT
        wv.*,
        COALESCE(fc.funder_count, 0) AS existing_funder_count
    FROM with_viability wv
    LEFT JOIN (
        SELECT fg.recipient_ein, COUNT(DISTINCT fg.foundation_ein) AS funder_count
        FROM {SCHEMA}.fact_grants fg
        WHERE fg.tax_year >= %s
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
WHERE state_rank <= %s
ORDER BY existing_funder_count DESC, ein
LIMIT %s
"""

    # Safety assertion: placeholder count must match params count
    placeholder_count = sql.count('%s')
    assert placeholder_count == len(params), (
        f"SQL placeholder mismatch: {placeholder_count} placeholders vs {len(params)} params"
    )

    return sql, tuple(params)


# ============================================================================
# Database connection
# ============================================================================

def connect_db():
    """Connect to thegrantscout database using environment variables."""
    try:
        return psycopg2.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=int(os.environ.get("PGPORT", "5432")),
            database=os.environ.get("PGDATABASE", "thegrantscout"),
            user=os.environ.get("PGUSER", "postgres"),
            password=os.environ.get("PGPASSWORD", "Mapping1!"),
        )
    except psycopg2.OperationalError as e:
        print(f"Error: Cannot connect to database.", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        print(f"  Try: brew services start postgresql", file=sys.stderr)
        sys.exit(1)


# ============================================================================
# Result processing
# ============================================================================

def compute_stats(rows, limit):
    """Compute category, state, and revenue statistics from query results."""
    output_rows = rows[:limit]

    cats = {}
    states = {}
    rev_buckets = {}
    funder_counts = []
    adj_counts = []

    for row in output_rows:
        (ein, org_name, phone, website, state, mission, prog1, contact, title,
         kw_cat, fdn_count, adj_count, sector_label, funder_count, total_rev) = row

        cats[kw_cat] = cats.get(kw_cat, 0) + 1
        states[state] = states.get(state, 0) + 1
        rev_buckets[revenue_bucket(total_rev)] = rev_buckets.get(revenue_bucket(total_rev), 0) + 1
        funder_counts.append(funder_count or 0)
        adj_counts.append(adj_count or 0)

    return {
        "total_query_rows": len(rows),
        "output_rows": len(output_rows),
        "categories": dict(sorted(cats.items(), key=lambda x: -x[1])),
        "states": dict(sorted(states.items(), key=lambda x: -x[1])),
        "state_count": len(states),
        "revenue_buckets": dict(sorted(rev_buckets.items())),
        "funder_min": min(funder_counts) if funder_counts else 0,
        "funder_max": max(funder_counts) if funder_counts else 0,
        "funder_median": sorted(funder_counts)[len(funder_counts) // 2] if funder_counts else 0,
        "with_funders": sum(1 for f in funder_counts if f > 0),
        "adj_min": min(adj_counts) if adj_counts else 0,
        "adj_max": max(adj_counts) if adj_counts else 0,
        "adj_median": sorted(adj_counts)[len(adj_counts) // 2] if adj_counts else 0,
    }


def print_stats(stats, resolved):
    """Print formatted statistics summary."""
    print(f"\n{'='*60}")
    print(f"CALL LIST SUMMARY")
    print(f"{'='*60}")
    print(f"Query returned: {stats['total_query_rows']} rows (after viability + state cap)")
    print(f"Output rows: {stats['output_rows']} (limit={resolved['limit']})")

    print(f"\nCategory breakdown:")
    for cat, cnt in stats["categories"].items():
        print(f"  {cat}: {cnt}")

    print(f"\nState distribution ({stats['state_count']} states, top 10):")
    for i, (st, cnt) in enumerate(stats["states"].items()):
        if i >= 10:
            break
        print(f"  {st}: {cnt}")

    max_state_count = max(stats["states"].values()) if stats["states"] else 0
    if resolved["state_cap"] and max_state_count > resolved["state_cap"]:
        print(f"  WARNING: State cap ({resolved['state_cap']}) exceeded!")

    print(f"\nRevenue buckets:")
    for bucket, cnt in stats["revenue_buckets"].items():
        print(f"  {bucket}: {cnt}")

    print(f"\nFunder counts: min={stats['funder_min']}, max={stats['funder_max']}, "
          f"median={stats['funder_median']}, with_funders={stats['with_funders']}/{stats['output_rows']}")
    print(f"Adjusted foundation counts: min={stats['adj_min']}, max={stats['adj_max']}, "
          f"median={stats['adj_median']}")


def print_preview(rows, limit):
    """Print diverse sample rows for preview mode."""
    output_rows = rows[:limit]
    if not output_rows:
        print("No rows to preview.")
        return

    n = len(output_rows)

    # Diverse sample: top 3 by funder count, bottom 3, 4 random from middle
    sample_indices = set()
    # Top 3
    for i in range(min(3, n)):
        sample_indices.add(i)
    # Bottom 3
    for i in range(max(0, n - 3), n):
        sample_indices.add(i)
    # 4 from middle
    if n > 6:
        import random
        middle = list(range(3, max(3, n - 3)))
        random.seed(42)  # deterministic
        for i in random.sample(middle, min(4, len(middle))):
            sample_indices.add(i)

    sample = sorted(sample_indices)

    print(f"\n{'='*60}")
    print(f"PREVIEW: {len(sample)} diverse sample rows (of {n} total)")
    print(f"{'='*60}")
    print(f"{'#':>3}  {'Org':<45} {'State':>5} {'Cat':<18} {'Funders':>7} {'Revenue'}")
    print(f"{'---':>3}  {'---':<45} {'---':>5} {'---':<18} {'---':>7} {'---'}")

    for idx in sample:
        row = output_rows[idx]
        ein, org_name, phone, website, state, mission, prog1, contact, title, \
            kw_cat, fdn_count, adj_count, sector_label, funder_count, total_rev = row
        org_display = title_case_org(org_name)[:45]
        rev_display = revenue_bucket(total_rev)
        print(f"{idx+1:>3}  {org_display:<45} {state:>5} {kw_cat:<18} {funder_count or 0:>7} {rev_display}")


def verify_results(rows, resolved):
    """Run verification checks on results. Returns list of warnings."""
    warnings = []
    output_rows = rows[:resolved["limit"]]

    if not output_rows:
        warnings.append("WARN: 0 rows returned. Broaden search filters.")
        return warnings

    # Check for nulls in required fields
    null_counts = {"org": 0, "phone": 0, "contact": 0, "ein": 0, "website": 0}
    for row in output_rows:
        if not row[0]: null_counts["ein"] += 1
        if not row[1]: null_counts["org"] += 1
        if not row[2]: null_counts["phone"] += 1
        if not row[3]: null_counts["website"] += 1
        if not row[7]: null_counts["contact"] += 1
    for field, count in null_counts.items():
        if count > 0:
            warnings.append(f"WARN: {count} rows with null {field}")

    # Check state cap
    if resolved["state_cap"]:
        state_counts = {}
        for row in output_rows:
            st = row[4]
            state_counts[st] = state_counts.get(st, 0) + 1
        for st, cnt in state_counts.items():
            if cnt > resolved["state_cap"]:
                warnings.append(f"WARN: State {st} has {cnt} rows (cap={resolved['state_cap']})")

    # Check revenue cap
    for row in output_rows:
        rev = row[14]
        if rev is not None and float(rev) > resolved["max_revenue"]:
            warnings.append(f"WARN: EIN {row[0]} revenue ${rev:,.0f} exceeds cap ${resolved['max_revenue']:,.0f}")

    if not warnings:
        warnings.append("PASS: All verification checks passed")

    return warnings


def format_csv_rows(rows, limit):
    """Format query rows into CSV-ready lists."""
    csv_rows = []
    for row in rows[:limit]:
        ein, org_name, phone, website, state, mission, prog1, contact, title, \
            kw_cat, fdn_count, adj_count, sector_label, funder_count, total_rev = row

        csv_rows.append([
            title_case_org(org_name),
            "",  # Priority (blank for manual fill)
            "",  # Date Contacted
            format_phone(phone),
            title_case_name(contact),
            clean_title(title),
            "",  # Email
            state,
            STATE_TIMEZONE.get(state, ""),
            "",  # Dependents
            ein,
            "",  # Rating
            clean_website(website),
            truncate_about(mission, prog1),
            revenue_bucket(total_rev),
        ])
    return csv_rows


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate nonprofit cold-call prospect list for TGS sales.",
        epilog="Keywords and presets are defined in 4. Pipeline/config/call_list_keywords.json",
    )
    parser.add_argument("--preset", help="Named preset from config (e.g., veterans-national)")
    parser.add_argument("--categories", help="Comma-separated category names (e.g., veterans,sailing_maritime)")
    parser.add_argument("--state", help="2-letter state code. Omit for national.")
    parser.add_argument("--max-revenue", type=float, help="Revenue cap in dollars (default: from config)")
    parser.add_argument("--limit", type=int, help="Max rows in output CSV (default: from config)")
    parser.add_argument("--state-cap", type=int, help="Max orgs per state for diversity (default: from config)")
    parser.add_argument("--output-dir", default=".", help="Directory for output files")
    parser.add_argument("--output-name", default="prospect_call_list", help="Base name for output CSV")
    parser.add_argument("--preview-only", action="store_true", help="Show stats + sample rows, no CSV")
    parser.add_argument("--dry-run", action="store_true", help="Print generated SQL + params, exit")
    parser.add_argument("--list-presets", action="store_true", help="Show available presets and exit")
    parser.add_argument("--verbose", action="store_true", help="Print SQL and detailed stats")
    parser.add_argument("--config", help="Override config file path")
    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # List presets mode
    if args.list_presets:
        presets = config.get("presets", {})
        print("Available presets:")
        print()
        for name, p in presets.items():
            cats = ", ".join(p.get("categories", []))
            state = p.get("state", "national")
            limit = p.get("limit", config["defaults"]["limit"])
            print(f"  {name}")
            print(f"    {p.get('description', '')}")
            print(f"    Categories: {cats}")
            print(f"    State: {state} | Limit: {limit} | State cap: {p.get('state_cap', 'default')}")
            print()
        return

    # Need either preset or categories
    if not args.preset and not args.categories:
        print("Error: Specify --preset or --categories", file=sys.stderr)
        print("Run with --list-presets to see options", file=sys.stderr)
        sys.exit(1)

    # Resolve parameters
    resolved = resolve_params(config, args)

    print(f"Parameters:")
    print(f"  Categories: {', '.join(resolved['categories'])}")
    print(f"  State: {resolved['state'] or 'national'}")
    print(f"  Revenue cap: ${resolved['max_revenue']:,.0f}")
    print(f"  Limit: {resolved['limit']}")
    print(f"  State cap: {resolved['state_cap'] or 'none'}")
    print(f"  Viability: {resolved['viability_haircut']} haircut, >={resolved['viability_threshold']} threshold")
    print(f"  Grant year cutoff: {resolved['grant_year_cutoff']}")

    # Build SQL
    sql, sql_params = build_sql(config, resolved)

    # Dry-run mode
    if args.dry_run:
        print(f"\n{'='*60}")
        print("DRY RUN: Generated SQL")
        print(f"{'='*60}")
        print(sql)
        print(f"\nParameters ({len(sql_params)} values):")
        for i, p in enumerate(sql_params):
            print(f"  ${i+1}: {repr(p)}")
        return

    if args.verbose:
        print(f"\nGenerated SQL ({sql.count('%s')} params):")
        print(sql[:500] + "..." if len(sql) > 500 else sql)

    # Execute query
    print(f"\nConnecting to database...")
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, sql_params)
        rows = cur.fetchall()
        cur.close()
    finally:
        conn.close()

    print(f"Query returned {len(rows)} rows")

    if not rows:
        print("No matching prospects. Broaden filters (more categories, remove --state, increase --max-revenue).")
        return

    # Compute and print stats
    stats = compute_stats(rows, resolved["limit"])
    print_stats(stats, resolved)

    # Verification
    warnings = verify_results(rows, resolved)
    print(f"\nVerification:")
    for w in warnings:
        print(f"  {w}")

    # Preview mode
    if args.preview_only:
        print_preview(rows, resolved["limit"])
        return

    # Write CSV
    os.makedirs(args.output_dir, exist_ok=True)
    csv_path = os.path.join(args.output_dir, f"{args.output_name}.csv")

    csv_rows = format_csv_rows(rows, resolved["limit"])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_COLUMNS)
        writer.writerows(csv_rows)

    print(f"\nWrote {len(csv_rows)} rows to {csv_path}")
    file_size = os.path.getsize(csv_path)
    print(f"File size: {file_size:,} bytes")


if __name__ == "__main__":
    main()
