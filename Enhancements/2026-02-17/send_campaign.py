#!/usr/bin/env python3
"""send_campaign.py - Email campaign pipeline with stage-based subcommands.

Each stage writes a CSV checkpoint that the next stage reads.

Usage:
    python3 send_campaign.py pull
    python3 send_campaign.py generate
    python3 send_campaign.py qc
    python3 send_campaign.py send --dry-run
    python3 send_campaign.py send --test-email alec.m.kleinman@gmail.com --limit-total 1
    python3 send_campaign.py send --limit-per-domain 50
    python3 send_campaign.py report
"""

import argparse
import csv
import os
import random
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

from greeting_resolver import resolve_greeting, format_greeting_line

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
ENV_PATH = (
    PROJECT_ROOT
    / "6. Business"
    / "3. sales-marketing"
    / "5. Email_Campaign"
    / ".env"
)

TODAY = datetime.now().strftime("%Y-%m-%d")
PULL_CSV = SCRIPT_DIR / f"DATA_{TODAY}_sendable_prospects.csv"
GENERATE_CSV = SCRIPT_DIR / f"DATA_{TODAY}_generated_emails.csv"
QC_CSV = SCRIPT_DIR / f"DATA_{TODAY}_qc_results.csv"
SEND_LOG_CSV = SCRIPT_DIR / f"DATA_{TODAY}_send_log.csv"
REPORT_MD = SCRIPT_DIR / f"REPORT_{TODAY}_email_campaign_send.md"

SUBDOMAINS = [
    "ai", "connect", "contact", "email", "funding",
    "grants", "growth", "hello", "help", "info",
    "insights", "mail", "nonprofits", "outreach", "partner",
    "privatefunding", "reports", "scout", "service", "team",
]

CAMPAIGN_VERTICAL = "v2_campaign"

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
    "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "PR": "Puerto Rico", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
    "VI": "Virgin Islands", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}

PLACEHOLDER_NAMES = {
    "there", "hi", "hello", "dear", "sir", "madam", "whom", "team",
    "friend", "director", "manager", "coordinator", "admin",
    "info", "office", "contact", "support",
}

# ---------------------------------------------------------------------------
# Email Templates (plain text, no em dashes)
# ---------------------------------------------------------------------------

TEMPLATE_A_SUBJECT = "Private funders for {sector} organizations in {state}"

TEMPLATE_A_BODY = (
    "{greeting_line}\n"
    "\n"
    "My name is Alec and I run a company called TheGrantScout. We help "
    "nonprofits impacted by recent federal funding cuts find private "
    "funding alternatives.\n"
    "\n"
    "We've been raising awareness of who the local private funders are "
    "in each state, and I put together a list of {count} private "
    "foundations that fund {sector} organizations in {state}, along "
    "with their contact info and recent giving history.\n"
    "\n"
    "Let me know if you're interested and I'll send it your way.\n"
    "\n"
    "Alec Kleinman\n"
    "TheGrantScout\n"
    "740 E, 2320 N, Provo, UT 84604\n"
    "\n"
    "P.S - If this isn't relevant just let me know and I won't reach "
    "out again."
)

TEMPLATE_C_SUBJECT = "Foundation funding for {organization_name}"

TEMPLATE_C_BODY = (
    "{greeting_line}\n"
    "\n"
    "My name is Alec and I'm with a company called TheGrantScout. "
    "I saw that {organization_name} {mission_short} and wanted to see "
    "if we can help you find private foundation funding.\n"
    "\n"
    "Let me know if you're open to a quick call!\n"
    "\n"
    "Alec Kleinman\n"
    "TheGrantScout\n"
    "740 E, 2320 N, Provo, UT 84604\n"
    "\n"
    "P.S - If this isn't relevant just let me know and I won't reach "
    "out again."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_db_connection():
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", "5432")),
        database=os.environ.get("PGDATABASE", "thegrantscout"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )
    cur = conn.cursor()
    cur.execute("SET search_path TO f990_2025")
    return conn, cur


def load_resend_api_key():
    if not ENV_PATH.exists():
        print(f"ERROR: .env not found at {ENV_PATH}")
        sys.exit(1)
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("RESEND_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    print("ERROR: RESEND_API_KEY not found in .env")
    sys.exit(1)


def smart_title_case(name):
    """Convert ALL CAPS org name to readable title case."""
    if not name:
        return ""
    if name != name.upper():
        return name
    words = name.lower().split()
    small = {
        "a", "an", "the", "and", "but", "or", "for", "nor",
        "on", "at", "to", "by", "of", "in", "is",
    }
    keep_upper = {"inc", "llc", "nfp", "ii", "iii", "iv", "usa", "us", "ymca", "ywca"}
    result = []
    for i, w in enumerate(words):
        if w in keep_upper:
            result.append(w.upper())
        elif i == 0 or w not in small:
            result.append(w.capitalize())
        else:
            result.append(w)
    return " ".join(result)


def generate_mission_short(mission_desc, ntee_code):
    """Generate 5-8 word mission summary from mission_description.

    Returns (mission_short, is_generic) tuple.
    """
    if not mission_desc or len(mission_desc.strip()) < 15:
        return _ntee_fallback(ntee_code), True

    text = mission_desc.upper().strip()

    # Pattern 1: "TO VERB ..." infinitive phrases
    inf_patterns = [
        (r"\bTO\s+(PROVIDE|OFFER|DELIVER|GIVE)\s+(.+)", "provides"),
        (r"\bTO\s+(HELP|ASSIST|AID)\s+(.+)", "helps"),
        (r"\bTO\s+(SUPPORT)\s+(.+)", "supports"),
        (r"\bTO\s+(SERVE|SERVICE)\s+(.+)", "serves"),
        (r"\bTO\s+(PROMOTE|ADVANCE|FURTHER)\s+(.+)", "promotes"),
        (r"\bTO\s+(EDUCATE|TEACH|TRAIN)\s+(.+)", "educates"),
        (r"\bTO\s+(PROTECT|PRESERVE|CONSERVE)\s+(.+)", "protects"),
        (r"\bTO\s+(EMPOWER|ENABLE|STRENGTHEN)\s+(.+)", "empowers"),
        (r"\bTO\s+(IMPROVE|ENHANCE)\s+(.+)", "improves"),
        (r"\bTO\s+(CREATE|BUILD|DEVELOP|ESTABLISH)\s+(.+)", "creates"),
        (r"\bTO\s+(ADVOCATE)\s+(.+)", "advocates"),
        (r"\bTO\s+(PREVENT)\s+(.+)", "prevents"),
        (r"\bTO\s+(REDUCE|ALLEVIATE|ELIMINATE)\s+(.+)", "reduces"),
        (r"\bTO\s+(FOSTER|CULTIVATE|NURTURE)\s+(.+)", "fosters"),
        (r"\bTO\s+(CONNECT|LINK|BRIDGE)\s+(.+)", "connects"),
        (r"\bTO\s+(ENSURE|GUARANTEE)\s+(.+)", "ensures"),
        (r"\bTO\s+(INCREASE|EXPAND|GROW)\s+(.+)", "increases"),
        (r"\bTO\s+(OPERATE|RUN|MANAGE)\s+(.+)", "operates"),
        (r"\bTO\s+(ENRICH)\s+(.+)", "enriches"),
        (r"\bTO\s+(INSPIRE|MOTIVATE)\s+(.+)", "inspires"),
        (r"\bTO\s+(MAKE)\s+(.+)", "makes"),
    ]

    for pat, verb in inf_patterns:
        m = re.search(pat, text)
        if m:
            phrase = _clean_phrase(m.group(2), max_words=7)
            if phrase:
                return f"{verb} {phrase}", False

    # Pattern 2: already-conjugated verbs ("PROVIDES ...", "SERVES ...")
    conj_patterns = [
        (r"\b(PROVIDES?|OFFERS?|DELIVERS?)\s+(.+)", "provides"),
        (r"\b(HELPS?|ASSISTS?)\s+(.+)", "helps"),
        (r"\b(SUPPORTS?)\s+(.+)", "supports"),
        (r"\b(SERVES?)\s+(.+)", "serves"),
        (r"\b(PROMOTES?|ADVANCES?)\s+(.+)", "promotes"),
        (r"\b(EDUCATES?|TEACHES?|TRAINS?)\s+(.+)", "educates"),
        (r"\b(OPERATES?|RUNS?|MANAGES?)\s+(.+)", "operates"),
    ]

    for pat, verb in conj_patterns:
        m = re.search(pat, text)
        if m:
            phrase = _clean_phrase(m.group(2), max_words=7)
            if phrase:
                return f"{verb} {phrase}", False

    return _ntee_fallback(ntee_code), True


def _clean_phrase(raw, max_words=7):
    """Clean extracted phrase: lowercase, strip junk, take max_words."""
    text = raw.lower().strip()
    # Stop at sentence boundary (period followed by space/capital)
    period_match = re.search(r"\.\s", text)
    if period_match:
        text = text[: period_match.start()]
    # Remove trailing punctuation
    text = re.sub(r"[.;,!:]+$", "", text)
    # Remove "and/or" constructs
    text = text.replace("and/or", "and")
    words = text.split()[:max_words]
    # Truncate at "and + unconjugated base verb" anywhere in phrase
    # These create grammar errors like "provides and promote"
    _base_verbs = {
        "provide", "promote", "improve", "maintain", "create",
        "encourage", "serve", "increase", "inform", "help",
        "close", "ensure", "develop", "build", "establish",
        "open", "operate", "run", "manage", "deliver",
        "offer", "teach", "train", "protect", "preserve",
    }
    for j in range(len(words) - 1):
        if words[j] == "and" and words[j + 1] in _base_verbs:
            words = words[:j]
            break
    # Strip trailing function words and dangling references
    trailing = {
        "and", "or", "in", "for", "to", "the", "of", "with",
        "a", "an", "by", "at", "on", "through", "that", "who",
        "which", "these", "those", "its", "their", "our", "has",
        "also", "both", "all", "such", "each", "we", "as",
    }
    while words and words[-1] in trailing:
        words.pop()
    if len(words) >= 3:
        return " ".join(words)
    return None


def _ntee_fallback(ntee_code):
    """Generate generic mission_short from NTEE code."""
    if not ntee_code:
        return "supports community programs"
    sector = ntee_code[0].upper()
    fallbacks = {
        "A": "supports arts and culture programs",
        "B": "provides educational programs and services",
        "C": "supports environmental conservation efforts",
        "D": "supports animal welfare programs",
        "E": "provides health care services",
        "F": "supports mental health and crisis services",
        "G": "supports disease treatment and prevention",
        "H": "supports medical research initiatives",
        "I": "provides legal services and crime prevention",
        "J": "provides employment and job training",
        "K": "supports food and nutrition programs",
        "L": "provides housing and shelter services",
        "M": "supports public safety programs",
        "N": "supports recreation and sports programs",
        "O": "provides youth development programs",
        "P": "provides human services to communities",
        "Q": "supports international development efforts",
        "R": "supports civil rights and advocacy",
        "S": "supports community improvement efforts",
        "T": "supports philanthropic programs",
        "U": "supports science and technology research",
        "V": "supports social science research",
        "W": "supports public policy research",
        "X": "supports faith-based community programs",
        "Y": "supports mutual benefit organizations",
        "Z": "supports community programs",
    }
    return fallbacks.get(sector, "supports community programs")


def get_already_sent_emails():
    """Return set of emails already in campaign_prospect_status."""
    conn, cur = get_db_connection()
    try:
        cur.execute(
            "SELECT DISTINCT email FROM campaign_prospect_status "
            "WHERE email IS NOT NULL"
        )
        emails = {row[0] for row in cur.fetchall()}
        return emails
    finally:
        cur.close()
        conn.close()


def get_today_domain_counts():
    """Return dict of {subdomain: count} for emails sent today."""
    conn, cur = get_db_connection()
    try:
        cur.execute(
            "SELECT initial_sender, COUNT(*) FROM campaign_prospect_status "
            "WHERE initial_sent_at::date = CURRENT_DATE "
            "AND initial_status = 'sent' "
            "GROUP BY initial_sender"
        )
        counts = {}
        for row in cur.fetchall():
            sender = row[0] or ""
            for sd in SUBDOMAINS:
                if f"@{sd}.thegrantscout.com" in sender:
                    counts[sd] = counts.get(sd, 0) + int(row[1])
                    break
        return counts
    finally:
        cur.close()
        conn.close()


def read_csv_file(path):
    """Read CSV and return list of dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv_file(path, rows, fieldnames):
    """Write list of dicts to CSV."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows)} rows to {path.name}")


# ---------------------------------------------------------------------------
# Subcommand: pull
# ---------------------------------------------------------------------------


def cmd_pull(args):
    """Pull sendable Tier A+B prospects, excluding already-contacted."""
    conn, cur = get_db_connection()

    print("=" * 60)
    print("PULL: Fetching sendable prospects")
    print("=" * 60)

    cur.execute("""
        SELECT
            np.ein,
            np.organization_name,
            np.contact_first_name,
            np.contact_email,
            np.state,
            np.ntee_code,
            np.mission_description,
            np.email_quality_tier,
            cv.foundation_count,
            cv.display_count,
            cv.sector_label
        FROM nonprofits_prospects2 np
        JOIN cohort_viability cv
            ON cv.state = np.state
            AND cv.ntee_sector = LEFT(np.ntee_code, 1)
            AND cv.viable = true
        WHERE np.email_quality_tier IN ('A', 'B')
          AND np.contact_email IS NOT NULL
          AND np.contact_email NOT LIKE '%%.gov'
          AND np.contact_first_name NOT IN (
              'there', 'Hi', 'Hello', 'Dear', 'Sir', 'Madam', 'whom', 'Team'
          )
          AND np.contact_email NOT IN (
              SELECT DISTINCT email
              FROM campaign_prospect_status
              WHERE email IS NOT NULL
          )
        ORDER BY np.email_quality_tier, np.state
    """)

    columns = [desc[0] for desc in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]

    # Resolve greeting for each prospect
    for r in rows:
        gname, greason = resolve_greeting(
            r.get("contact_first_name"), r.get("contact_email")
        )
        r["greeting_name"] = gname or ""
        r["greeting_reason"] = greason

    fieldnames = [
        "ein", "organization_name", "contact_first_name", "contact_email",
        "greeting_name", "greeting_reason",
        "state", "ntee_code", "mission_description", "email_quality_tier",
        "foundation_count", "display_count", "sector_label",
    ]
    write_csv_file(PULL_CSV, rows, fieldnames)

    # Greeting resolution summary
    reason_counts = Counter(r["greeting_reason"] for r in rows)
    personalized = sum(
        1 for r in rows if r["greeting_reason"] in ("exact_match", "nickname_match")
    )

    # Summary
    total = len(rows)
    if total == 0:
        print("\n  No sendable prospects found.")
        cur.close()
        conn.close()
        return

    tier_a = sum(1 for r in rows if r["email_quality_tier"] == "A")
    tier_b = sum(1 for r in rows if r["email_quality_tier"] == "B")
    has_mission = sum(1 for r in rows if r.get("mission_description"))
    has_display = sum(1 for r in rows if r.get("display_count"))

    print(f"\n  Total sendable: {total:,}")
    print(f"  Tier A: {tier_a:,}  |  Tier B: {tier_b:,}")
    print(
        f"  Has mission_description: {has_mission:,} "
        f"({100 * has_mission / total:.1f}%)"
    )
    print(
        f"  Has display_count: {has_display:,} "
        f"({100 * has_display / total:.1f}%)"
    )

    # Greeting resolution
    print(f"\n  Greeting resolution:")
    print(f"    Personalized (Hi Name,): {personalized} ({100 * personalized / total:.1f}%)")
    print(f"    Generic (Hello,): {total - personalized} ({100 * (total - personalized) / total:.1f}%)")
    for reason, cnt in sorted(reason_counts.items(), key=lambda x: -x[1]):
        print(f"      {reason}: {cnt}")

    # State breakdown (top 15)
    state_counts = Counter(r["state"] for r in rows)
    print("\n  Top 15 states:")
    for st, cnt in state_counts.most_common(15):
        print(f"    {st}: {cnt}")

    # Sector breakdown
    sector_counts = Counter(
        r["sector_label"] for r in rows if r.get("sector_label")
    )
    print("\n  All sectors:")
    for sec, cnt in sorted(sector_counts.items(), key=lambda x: -x[1]):
        print(f"    {sec}: {cnt}")

    print(f"\n  Output: {PULL_CSV.name}")
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Subcommand: generate
# ---------------------------------------------------------------------------


def cmd_generate(args):
    """Generate personalized emails with 50/50 A/B split."""
    print("=" * 60)
    print("GENERATE: Creating personalized emails")
    print("=" * 60)

    if not PULL_CSV.exists():
        print(f"ERROR: Run 'pull' first. Missing {PULL_CSV.name}")
        sys.exit(1)

    prospects = read_csv_file(PULL_CSV)
    random.seed(42)
    random.shuffle(prospects)

    generated = []
    skipped = 0
    reassigned_c_to_a = 0

    for i, p in enumerate(prospects):
        template = "A" if i % 2 == 0 else "C"

        first_name = p.get("contact_first_name") or ""
        contact_email = p.get("contact_email") or ""
        org_name = smart_title_case(p.get("organization_name", ""))
        state_code = p.get("state", "")
        state_full = STATE_NAMES.get(state_code, state_code)
        sector = (p.get("sector_label") or "").lower()
        mission_desc = p.get("mission_description", "")
        ntee_code = p.get("ntee_code", "")

        # Resolve greeting from CSV if available, else compute fresh
        gname = p.get("greeting_name") or None
        greason = p.get("greeting_reason") or ""
        if not greason:
            gname, greason = resolve_greeting(first_name, contact_email)
        elif gname == "":
            gname = None
        greeting_line = format_greeting_line(gname)

        raw_dc = p.get("display_count", "")
        if raw_dc and raw_dc not in ("", "None", "null"):
            try:
                display_count = int(float(raw_dc))
            except (ValueError, TypeError):
                display_count = None
        else:
            display_count = None

        quality_flags = []
        mission_short = ""

        # Template C: generate mission_short, reassign to A if generic
        if template == "C":
            ms, is_generic = generate_mission_short(mission_desc, ntee_code)
            mission_short = ms
            if is_generic:
                # Reassign to A (don't flag as quality issue since A email is fine)
                template = "A"
                reassigned_c_to_a += 1

        # Template A: skip if no display_count or no sector
        if template == "A":
            if not display_count or display_count == 0:
                skipped += 1
                continue
            if not sector:
                skipped += 1
                continue

            subject = TEMPLATE_A_SUBJECT.format(
                sector=sector, state=state_full,
            )
            body = TEMPLATE_A_BODY.format(
                greeting_line=greeting_line,
                count=display_count,
                sector=sector,
                state=state_full,
            )
        else:
            # Template C (mission_short is valid at this point)
            subject = TEMPLATE_C_SUBJECT.format(
                organization_name=org_name,
            )
            body = TEMPLATE_C_BODY.format(
                greeting_line=greeting_line,
                organization_name=org_name,
                mission_short=mission_short,
            )

        generated.append({
            "prospect_ein": p["ein"],
            "contact_email": contact_email,
            "contact_first_name": first_name,
            "greeting_name": gname or "",
            "greeting_reason": greason,
            "organization_name": org_name,
            "template_used": template,
            "subject_line": subject,
            "email_body": body,
            "mission_short": mission_short if template == "C" else "",
            "quality_flag": "|".join(quality_flags) if quality_flags else "",
            "state": state_code,
            "sector_label": p.get("sector_label", ""),
            "display_count": display_count or "",
            "email_quality_tier": p.get("email_quality_tier", ""),
        })

    fieldnames = [
        "prospect_ein", "contact_email", "contact_first_name",
        "greeting_name", "greeting_reason",
        "organization_name", "template_used", "subject_line",
        "email_body", "mission_short", "quality_flag",
        "state", "sector_label", "display_count", "email_quality_tier",
    ]
    write_csv_file(GENERATE_CSV, generated, fieldnames)

    # Summary
    total = len(generated)
    a_count = sum(1 for r in generated if r["template_used"] == "A")
    c_count = sum(1 for r in generated if r["template_used"] == "C")
    flagged = sum(1 for r in generated if r["quality_flag"])

    personalized = sum(
        1 for r in generated
        if r["greeting_reason"] in ("exact_match", "nickname_match")
    )
    print(f"\n  Total generated: {total:,}")
    print(f"  Template A: {a_count:,}  |  Template C: {c_count:,}")
    print(f"  Reassigned C->A (generic mission): {reassigned_c_to_a}")
    print(f"  Skipped (no display_count/sector): {skipped}")
    print(f"  Quality flagged: {flagged}")
    print(f"  Greeting: {personalized} personalized, {total - personalized} generic")
    print(f"\n  Output: {GENERATE_CSV.name}")


# ---------------------------------------------------------------------------
# Subcommand: qc
# ---------------------------------------------------------------------------


def cmd_qc(args):
    """QC sample of emails (default 50 per template = 100 total)."""
    sample_per_template = args.sample_size
    total_sample = sample_per_template * 2

    print("=" * 60)
    print(f"QC: Checking sample of {total_sample} emails ({sample_per_template} per template)")
    print("=" * 60)

    if not GENERATE_CSV.exists():
        print(f"ERROR: Run 'generate' first. Missing {GENERATE_CSV.name}")
        sys.exit(1)

    emails = read_csv_file(GENERATE_CSV)

    template_a = [e for e in emails if e["template_used"] == "A"]
    template_c = [e for e in emails if e["template_used"] == "C"]

    random.seed(99)
    sample_a = random.sample(template_a, min(sample_per_template, len(template_a)))
    sample_c = random.sample(template_c, min(sample_per_template, len(template_c)))
    sample = sample_a + sample_c

    results = []
    failures = 0

    for e in sample:
        checks = []
        passed = True

        # 1. Greeting coherence check
        greason = e.get("greeting_reason", "")
        body = e.get("email_body", "")
        body_first_line = body.split("\n")[0].strip() if body else ""
        if greason in ("exact_match", "nickname_match"):
            gname = e.get("greeting_name", "")
            if gname and f"Hi {gname}," in body_first_line:
                checks.append(f"OK: personalized ({greason})")
            else:
                checks.append(f"FAIL: personalized greeting missing for {greason}")
                passed = False
        else:
            if body_first_line == "Hello,":
                checks.append(f"OK: generic greeting ({greason})")
            elif body_first_line.startswith("Hi ") and body_first_line.endswith(","):
                checks.append(f"FAIL: has Hi Name but reason={greason}")
                passed = False
            else:
                checks.append(f"OK: greeting ({greason})")

        # 2. No broken merge fields
        if "{{" in body or "}}" in body or "None" in body:
            checks.append("FAIL: broken merge field")
            passed = False
        else:
            checks.append("OK: no broken merges")

        # 3. No em dashes
        if "\u2014" in body or " -- " in body:
            checks.append("FAIL: em dash found")
            passed = False
        else:
            checks.append("OK: no em dashes")

        # 4. Template A: count > 0 and reasonable
        if e["template_used"] == "A":
            dc = e.get("display_count", "")
            try:
                dc_int = int(float(dc)) if dc else 0
                if dc_int <= 0:
                    checks.append("FAIL: display_count <= 0")
                    passed = False
                elif dc_int > 200:
                    checks.append(f"WARN: display_count={dc_int} (high)")
                else:
                    checks.append(f"OK: count={dc_int}")
            except (ValueError, TypeError):
                checks.append(f"FAIL: invalid count={dc}")
                passed = False

        # 5. Template C: mission_short quality
        if e["template_used"] == "C":
            ms = e.get("mission_short", "")
            if not ms or len(ms) < 10:
                checks.append("FAIL: missing/short mission_short")
                passed = False
            else:
                checks.append("OK: mission_short present")

        # 6. Subject and body not empty
        if not e.get("subject_line"):
            checks.append("FAIL: empty subject")
            passed = False
        else:
            checks.append("OK: subject present")

        if not passed:
            failures += 1

        results.append({
            "prospect_ein": e["prospect_ein"],
            "contact_email": e["contact_email"],
            "template_used": e["template_used"],
            "passed": "PASS" if passed else "FAIL",
            "checks": " | ".join(checks),
            "subject_line": e["subject_line"],
        })

    fieldnames = [
        "prospect_ein", "contact_email", "template_used",
        "passed", "checks", "subject_line",
    ]
    write_csv_file(QC_CSV, results, fieldnames)

    # Print results
    pass_count = len(results) - failures
    print(f"\n  Results: {pass_count}/{len(results)} passed\n")

    for r in results:
        status = "PASS" if r["passed"] == "PASS" else "FAIL"
        email_trunc = r["contact_email"][:35].ljust(35)
        print(f"  [{status}] {r['template_used']} | {email_trunc} | {r['checks']}")

    print()
    if failures > 2:
        print(
            f"  GATE FAILED: {failures} failures (max 2). "
            "Fix issues before sending."
        )
        sys.exit(1)
    else:
        print(f"  GATE PASSED: {failures} failure(s). Safe to proceed.")

    print(f"\n  Output: {QC_CSV.name}")


# ---------------------------------------------------------------------------
# Subcommand: send
# ---------------------------------------------------------------------------


def cmd_send(args):
    """Send emails via Resend API."""
    print("=" * 60)
    mode = "DRY RUN" if args.dry_run else "LIVE SEND"
    print(f"SEND: {mode}")
    print("=" * 60)

    if not GENERATE_CSV.exists():
        print(f"ERROR: Run 'generate' first. Missing {GENERATE_CSV.name}")
        sys.exit(1)

    emails = read_csv_file(GENERATE_CSV)

    # Filter out quality-flagged emails
    sendable = [e for e in emails if not e.get("quality_flag")]
    flagged_count = len(emails) - len(sendable)
    if flagged_count:
        print(f"  Skipping {flagged_count} quality-flagged emails")

    # --- DUPLICATE PREVENTION ---
    # Load all already-sent emails from DB to prevent double-sends
    already_sent = get_already_sent_emails()
    before_dedup = len(sendable)
    sendable = [e for e in sendable if e["contact_email"] not in already_sent]
    dedup_removed = before_dedup - len(sendable)
    if dedup_removed:
        print(f"  Removed {dedup_removed} already-contacted prospects")
    print(f"  Fresh prospects available: {len(sendable)}")

    # --- CAPACITY-AWARE DOMAIN ASSIGNMENT ---
    # Query today's actual per-domain sends from DB
    limit_per_domain = args.limit_per_domain
    today_counts = get_today_domain_counts()

    print(f"\n  Today's sends per domain (from DB):")
    for sd in SUBDOMAINS:
        cnt = today_counts.get(sd, 0)
        remaining = max(0, limit_per_domain - cnt)
        if cnt > 0 or remaining > 0:
            print(f"    {sd}: {cnt} sent, {remaining} remaining")

    # Build list of domains with remaining capacity
    domain_remaining = {}
    for sd in SUBDOMAINS:
        remaining = limit_per_domain - today_counts.get(sd, 0)
        if remaining > 0:
            domain_remaining[sd] = remaining

    total_capacity = sum(domain_remaining.values())
    print(f"\n  Total remaining capacity: {total_capacity}")

    if total_capacity == 0:
        print("  All domains at daily limit. Nothing to send.")
        return

    # Assign subdomains using capacity-aware rotation
    assigned = []
    # Cycle through domains with capacity, filling each up to its limit
    domain_assigned = {sd: 0 for sd in domain_remaining}
    domain_cycle = list(domain_remaining.keys())
    idx = 0
    for email in sendable:
        if not domain_cycle:
            break
        # Find next domain with remaining capacity
        attempts = 0
        while attempts < len(domain_cycle):
            sd = domain_cycle[idx % len(domain_cycle)]
            if domain_assigned[sd] < domain_remaining[sd]:
                email["subdomain"] = sd
                domain_assigned[sd] += 1
                assigned.append(email)
                idx += 1
                break
            else:
                # This domain is full, remove from cycle
                domain_cycle.remove(sd)
                if domain_cycle:
                    idx = idx % len(domain_cycle)
                attempts += 1
    sendable = assigned

    # Apply total limit
    if args.limit_total:
        sendable = sendable[: args.limit_total]

    total_to_send = len(sendable)
    print(f"\n  Emails to send this run: {total_to_send}")
    print(f"  Limit per domain (cumulative daily): {limit_per_domain}")
    if args.limit_total:
        print(f"  Limit total: {args.limit_total}")
    if args.test_email:
        print(f"  TEST MODE: All emails -> {args.test_email}")

    # Show planned per-domain breakdown
    planned = Counter(e["subdomain"] for e in sendable)
    print(f"\n  Planned per-domain sends:")
    for sd in SUBDOMAINS:
        p = planned.get(sd, 0)
        if p > 0:
            total_after = today_counts.get(sd, 0) + p
            print(f"    {sd}: +{p} (will be {total_after} total today)")

    if total_to_send == 0:
        print("  Nothing to send.")
        return

    # Load Resend API (only for live sends)
    resend_mod = None
    if not args.dry_run:
        try:
            import resend as resend_mod
        except ImportError:
            print("ERROR: 'resend' package not installed. Run: pip3 install resend")
            sys.exit(1)
        resend_mod.api_key = load_resend_api_key()

    # DB connection for logging (only real sends to real recipients)
    conn = cur = None
    if not args.dry_run and not args.test_email:
        conn, cur = get_db_connection()

    # --- APPEND-MODE CSV (crash-resilient) ---
    log_fieldnames = [
        "prospect_ein", "contact_email", "to_email", "subdomain",
        "template_used", "subject_line", "from_address",
        "status", "message_id", "timestamp", "error",
    ]
    # Write header if file doesn't exist yet
    log_file_exists = SEND_LOG_CSV.exists()

    sent_count = 0
    error_count = 0
    skip_count = 0
    log_fh = open(SEND_LOG_CSV, "a", newline="", encoding="utf-8")

    try:
        log_writer = csv.DictWriter(log_fh, fieldnames=log_fieldnames)
        if not log_file_exists:
            log_writer.writeheader()
        for i, email in enumerate(sendable):
            subdomain = email["subdomain"]
            from_addr = f"Alec Kleinman <alec@{subdomain}.thegrantscout.com>"
            to_addr = (
                args.test_email if args.test_email else email["contact_email"]
            )

            # Final duplicate check (in case DB was updated during this run)
            if email["contact_email"] in already_sent:
                skip_count += 1
                continue

            entry = {
                "prospect_ein": email["prospect_ein"],
                "contact_email": email["contact_email"],
                "to_email": to_addr,
                "subdomain": subdomain,
                "template_used": email["template_used"],
                "subject_line": email["subject_line"],
                "from_address": from_addr,
                "status": "",
                "message_id": "",
                "timestamp": "",
                "error": "",
            }

            if args.dry_run:
                entry["status"] = "dry_run"
                entry["timestamp"] = datetime.now(timezone.utc).isoformat()
                log_writer.writerow(entry)
                log_fh.flush()
                sent_count += 1
                if (i + 1) % 100 == 0 or (i + 1) == total_to_send:
                    print(f"  [DRY RUN] {i + 1}/{total_to_send}")
                continue

            try:
                params = {
                    "from": from_addr,
                    "to": [to_addr],
                    "subject": email["subject_line"],
                    "text": email["email_body"],
                    "reply_to": "alec@thegrantscout.com",
                    "tags": [
                        {"name": "template", "value": email["template_used"]},
                        {"name": "campaign", "value": f"v2_{TODAY}"},
                        {
                            "name": "tier",
                            "value": email.get("email_quality_tier", ""),
                        },
                    ],
                }

                response = resend_mod.Emails.send(params)
                if hasattr(response, "id"):
                    msg_id = response.id
                elif isinstance(response, dict):
                    msg_id = response.get("id", "")
                else:
                    msg_id = str(response)

                entry["status"] = "sent"
                entry["message_id"] = msg_id
                entry["timestamp"] = datetime.now(timezone.utc).isoformat()
                sent_count += 1

                # Add to in-memory set to prevent within-run duplicates
                already_sent.add(email["contact_email"])

                # Log to DB (only real sends to real recipients)
                if cur:
                    try:
                        cur.execute(
                            """
                            INSERT INTO campaign_prospect_status
                                (ein, email, org_name, org_type, vertical,
                                 campaign_status, initial_sent_at,
                                 initial_status, initial_subject,
                                 initial_sender, source_file)
                            VALUES (%s, %s, %s, 'nonprofit', %s,
                                    'initial_sent', NOW(), 'sent',
                                    %s, %s, 'send_campaign.py')
                            ON CONFLICT (email, vertical)
                                WHERE email IS NOT NULL
                            DO UPDATE SET
                                campaign_status = 'initial_sent',
                                initial_sent_at = NOW(),
                                initial_status = 'sent',
                                initial_subject = EXCLUDED.initial_subject,
                                initial_sender = EXCLUDED.initial_sender,
                                updated_at = NOW()
                            """,
                            (
                                email["prospect_ein"],
                                email["contact_email"],
                                email.get("organization_name", ""),
                                CAMPAIGN_VERTICAL,
                                email["subject_line"],
                                from_addr,
                            ),
                        )
                        conn.commit()
                    except Exception as db_err:
                        print(f"  DB log error: {db_err}")
                        conn.rollback()

                print(
                    f"  [{sent_count}/{total_to_send}] "
                    f"Sent to {to_addr[:40]} via {subdomain} "
                    f"(ID: {str(msg_id)[:24]})"
                )

            except KeyboardInterrupt:
                raise
            except Exception as e:
                entry["status"] = "error"
                entry["error"] = str(e)
                entry["timestamp"] = datetime.now(timezone.utc).isoformat()
                error_count += 1
                print(f"  ERROR [{i + 1}] {to_addr}: {e}")

            # Write each entry immediately (crash-resilient)
            log_writer.writerow(entry)
            log_fh.flush()

            # Pacing: 8-12 second random delay between sends
            if i < total_to_send - 1 and not args.dry_run:
                delay = random.uniform(8, 12)
                time.sleep(delay)

    except KeyboardInterrupt:
        print("\n  Interrupted! Progress saved to CSV.")
    finally:
        log_fh.close()

        if cur:
            cur.close()
        if conn:
            conn.close()

    # Summary
    print(f"\n  Sent: {sent_count}  |  Errors: {error_count}  |  Skipped (dupes): {skip_count}")

    print(f"\n  Output: {SEND_LOG_CSV.name}")


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------


def cmd_report(args):
    """Generate campaign report from all stage CSVs."""
    print("=" * 60)
    print("REPORT: Generating campaign report")
    print("=" * 60)

    lines = []

    def add(text=""):
        lines.append(text)

    add("# Email Campaign Send Report")
    add()
    add(f"**Date:** {TODAY}")
    add(f"**Prompt:** send_campaign.py report")
    add("**Status:** Complete")
    add("**Owner:** Alec Kleinman")
    add()
    add("---")
    add()
    add("## Revision History")
    add()
    add("| Version | Date | Author | Changes |")
    add("|---------|------|--------|---------|")
    add(f"| 1.0 | {TODAY} | Claude Code | Initial version |")
    add()
    add("---")
    add()

    # 1. Pull stats
    if PULL_CSV.exists():
        prospects = read_csv_file(PULL_CSV)
        tier_a = sum(1 for r in prospects if r["email_quality_tier"] == "A")
        tier_b = sum(1 for r in prospects if r["email_quality_tier"] == "B")
        has_mission = sum(1 for r in prospects if r.get("mission_description"))

        add("## 1. Prospect Pool")
        add()
        add(f"- **Total sendable prospects:** {len(prospects):,}")
        add(f"- **Tier A:** {tier_a:,}")
        add(f"- **Tier B:** {tier_b:,}")
        add(
            f"- **Has mission_description:** {has_mission:,} "
            f"({100 * has_mission / max(len(prospects), 1):.1f}%)"
        )
        add()

        state_counts = Counter(r["state"] for r in prospects)
        add("**Top 10 states:**")
        add()
        add("| State | Count |")
        add("|-------|-------|")
        for st, cnt in state_counts.most_common(10):
            add(f"| {STATE_NAMES.get(st, st)} ({st}) | {cnt:,} |")
        add()

        sector_counts = Counter(
            r["sector_label"] for r in prospects if r.get("sector_label")
        )
        add("**Sectors:**")
        add()
        add("| Sector | Count |")
        add("|--------|-------|")
        for sec, cnt in sorted(sector_counts.items(), key=lambda x: -x[1]):
            add(f"| {sec} | {cnt:,} |")
        add()

    # 2. Generate stats
    if GENERATE_CSV.exists():
        emails = read_csv_file(GENERATE_CSV)
        a_emails = [e for e in emails if e["template_used"] == "A"]
        c_emails = [e for e in emails if e["template_used"] == "C"]
        flagged = [e for e in emails if e.get("quality_flag")]

        add("## 2. Email Generation")
        add()
        add(f"- **Total emails generated:** {len(emails):,}")
        add(f"- **Template A (list offer):** {len(a_emails):,}")
        add(f"- **Template C (direct call):** {len(c_emails):,}")
        add(f"- **Quality flagged:** {len(flagged)}")
        add()

        # A/B by tier
        a_tier_a = sum(
            1 for e in a_emails if e.get("email_quality_tier") == "A"
        )
        a_tier_b = sum(
            1 for e in a_emails if e.get("email_quality_tier") == "B"
        )
        c_tier_a = sum(
            1 for e in c_emails if e.get("email_quality_tier") == "A"
        )
        c_tier_b = sum(
            1 for e in c_emails if e.get("email_quality_tier") == "B"
        )
        add("**A/B Split by Quality Tier:**")
        add()
        add("| Template | Tier A | Tier B | Total |")
        add("|----------|--------|--------|-------|")
        add(
            f"| Template A | {a_tier_a:,} | {a_tier_b:,} "
            f"| {len(a_emails):,} |"
        )
        add(
            f"| Template C | {c_tier_a:,} | {c_tier_b:,} "
            f"| {len(c_emails):,} |"
        )
        add()

    # 3. QC results
    if QC_CSV.exists():
        qc = read_csv_file(QC_CSV)
        passed = sum(1 for r in qc if r["passed"] == "PASS")

        add("## 3. QC Results")
        add()
        add(f"- **Sample size:** {len(qc)}")
        add(f"- **Passed:** {passed}/{len(qc)}")
        gate = "PASSED" if passed >= len(qc) - 2 else "FAILED"
        add(f"- **Gate:** {gate}")
        add()

        add("| EIN | Email | Template | Result | Checks |")
        add("|-----|-------|----------|--------|--------|")
        for r in qc:
            checks_short = r["checks"][:80]
            add(
                f"| {r['prospect_ein']} | {r['contact_email'][:30]} "
                f"| {r['template_used']} | {r['passed']} | {checks_short} |"
            )
        add()

    # 4. Send results
    if SEND_LOG_CSV.exists():
        log = read_csv_file(SEND_LOG_CSV)
        sent = [e for e in log if e["status"] == "sent"]
        dry_runs = [e for e in log if e["status"] == "dry_run"]
        errors = [e for e in log if e["status"] == "error"]

        add("## 4. Send Results")
        add()
        add(f"- **Successfully sent:** {len(sent):,}")
        add(f"- **Errors:** {len(errors)}")
        if dry_runs:
            add(f"- **Dry run entries (not counted):** {len(dry_runs)}")
        add()

        domain_counts = Counter(e["subdomain"] for e in sent)
        add("**Per domain:**")
        add()
        add("| Domain | Sent |")
        add("|--------|------|")
        for sd in SUBDOMAINS:
            cnt = domain_counts.get(sd, 0)
            if cnt:
                add(f"| {sd}.thegrantscout.com | {cnt} |")
        add()

        template_counts = Counter(e["template_used"] for e in sent)
        add("**Per template:**")
        add()
        add(f"- Template A: {template_counts.get('A', 0)}")
        add(f"- Template C: {template_counts.get('C', 0)}")
        add()

        # State breakdown of sent
        state_counts = Counter(e.get("state", "") for e in sent if e.get("state"))
        if state_counts:
            add("**Top 10 states sent:**")
            add()
            add("| State | Sent |")
            add("|-------|------|")
            for st, cnt in state_counts.most_common(10):
                add(f"| {STATE_NAMES.get(st, st)} | {cnt} |")
            add()

        if errors:
            add("**Errors:**")
            add()
            for e in errors[:10]:
                add(f"- {e['contact_email']}: {e['error']}")
            if len(errors) > 10:
                add(f"- ... and {len(errors) - 10} more")
            add()

    # 5. Sample emails
    if GENERATE_CSV.exists():
        emails = read_csv_file(GENERATE_CSV)
        a_pool = [e for e in emails if e["template_used"] == "A"]
        c_pool = [e for e in emails if e["template_used"] == "C"]

        random.seed(123)
        sample_a = random.sample(a_pool, min(3, len(a_pool)))
        sample_c = random.sample(c_pool, min(2, len(c_pool)))

        add("## 5. Sample Emails")
        add()
        for idx, e in enumerate(sample_a + sample_c, 1):
            add(f"### Sample {idx} (Template {e['template_used']})")
            add()
            add(f"**To:** {e['contact_email']}")
            add()
            add(f"**Subject:** {e['subject_line']}")
            add()
            for line in e["email_body"].split("\n"):
                add(f"> {line}")
            add()

    # 6. Warm-up notes
    add("## 6. Warm-up Notes")
    add()
    add(f"- {len(SUBDOMAINS)} sending subdomains active")
    add(f"- Target: 100 emails per domain per day during warm-up")
    add("- 8-12 second random delay between sends")
    add("- Monitor bounce rates before scaling up")
    add("- Scale to 150-200/domain if bounce rate stays under 5%")
    add()

    # Files
    add("## Files Created/Modified")
    add()
    add("| File | Description |")
    add("|------|-------------|")
    add(f"| {PULL_CSV.name} | Sendable prospects from DB |")
    add(f"| {GENERATE_CSV.name} | Generated emails with A/B split |")
    add(f"| {QC_CSV.name} | QC check results |")
    add(f"| {SEND_LOG_CSV.name} | Send log with message IDs |")
    add(f"| {REPORT_MD.name} | This report |")
    add()
    add("---")
    add()
    add(f"*Generated by Claude Code on {TODAY}*")

    report_text = "\n".join(lines)
    with open(REPORT_MD, "w") as f:
        f.write(report_text)

    print(f"  Report written to {REPORT_MD.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Email campaign send pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 send_campaign.py pull\n"
            "  python3 send_campaign.py generate\n"
            "  python3 send_campaign.py qc\n"
            "  python3 send_campaign.py send --dry-run\n"
            "  python3 send_campaign.py send --test-email "
            "alec.m.kleinman@gmail.com --limit-total 1\n"
            "  python3 send_campaign.py send --limit-per-domain 50\n"
            "  python3 send_campaign.py report\n"
        ),
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("pull", help="Pull sendable prospects from DB")
    sub.add_parser(
        "generate", help="Generate personalized emails with A/B split"
    )
    qc_p = sub.add_parser("qc", help="QC sample of emails")
    qc_p.add_argument(
        "--sample-size",
        type=int,
        default=50,
        dest="sample_size",
        help="Number of emails to sample per template (default: 50, total = 2x this)",
    )

    send_p = sub.add_parser("send", help="Send emails via Resend API")
    send_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate everything without calling Resend API",
    )
    send_p.add_argument(
        "--test-email",
        help="Override all recipients with this email address",
    )
    send_p.add_argument(
        "--limit-total",
        type=int,
        help="Maximum total emails to send",
    )
    send_p.add_argument(
        "--limit-per-domain",
        type=int,
        default=50,
        help="Maximum emails per subdomain (default: 50)",
    )

    sub.add_parser("report", help="Generate campaign report")

    args = parser.parse_args()

    commands = {
        "pull": cmd_pull,
        "generate": cmd_generate,
        "qc": cmd_qc,
        "send": cmd_send,
        "report": cmd_report,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
