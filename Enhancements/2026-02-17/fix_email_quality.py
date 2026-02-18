#!/usr/bin/env python3
"""
Fix email quality issues in generated_emails.csv:
1. Fix ugly sector labels in Template A subjects + bodies
2. Fix mission_short issues in Template C emails
3. Reassign "unknown" sector to proper labels
4. Regenerate email bodies for all changed records
"""

import csv
import re
import sys

from greeting_resolver import resolve_greeting, format_greeting_line

CSV_IN = "DATA_2026-02-17.3_generated_emails.csv"
CSV_OUT = "DATA_2026-02-17.3_generated_emails.csv"  # overwrite in place

# ── SECTOR LABEL MAPPING ──────────────────────────────────────────────
SECTOR_FIXES = {
    "animal-related": "animal welfare",
    "crime/legal": "legal services",
    "disease/disorder": "disease and disorder research",
    "food/agriculture": "food and agriculture",
    "mutual/membership": "community organizations",
    "social science": "social science research",
    "arts & culture": "arts and culture",
    "unknown": None,  # handled per-EIN below
}

# Manual sector assignment for "unknown" (Z99) EINs
UNKNOWN_SECTOR_OVERRIDES = {
    "582005291": "education",           # Mobile Area Education Foundation
    "680298871": "mental health",       # Alcohol and Drug Awareness Program
    "954366755": "religion",            # China Evangelical Seminary
    "310804746": "human services",      # Wasco Inc
    "911552277": "legal services",      # Whatcom Dispute Resolution Center
    "203209113": "environment",         # Lake Whatcom Center Foundation
    "464505562": "youth development",   # Motivated Youth Academy
    "943213120": "human services",      # SF Senior and Disability
    "770258318": "housing",             # Sierra Salem Christian Homes
    "330411888": "environment",         # Agua Hedionda Lagoon Foundation
    "840795455": "health",              # Rocky Mountain Multiple Sclerosis
    "990255760": "health",              # Na Pu'uwai (Hawaiian health org)
    "364024533": "youth development",   # Girls in the Game
    "680101133": "housing",             # Phoenix Family Housing Corp
    "581509463": "human services",      # Adult Life Programs
    "930957946": "food and agriculture",# Wheat Marketing Center
    "471004312": "human services",      # Entryway
    "911381310": "human services",      # Kadima
}

# ── MISSION_SHORT MANUAL OVERRIDES ─────────────────────────────────────
# Key = EIN, Value = corrected mission_short
MISSION_OVERRIDES = {
    # Broken grammar
    "222936068": "supports educational and religious programs",
    "825513595": "helps over 1500 girls in india",
    "474784379": "supports women who have nowhere else to turn",
    "930717332": "provides care and supervision for children",
    "943111738": "improves health and well-being for clients",
    "200664128": "supports walsh college programs and students",
    "571146474": "serves the community through live theater",
    "832331834": "helps families navigate financial challenges",
    "113623769": "supports student academic and career programs",
    "452440083": "promotes recirculating farm and agriculture practices",
    "844890857": "helps young people serve their country",
    "060919178": "supports senior socialization through programs and education",
    "844138362": "supports student success through community partnership",
    "010659307": "empowers the community through service and outreach",
    "201438278": "supports adolescent mothers and young fathers",
    "850411367": "supports local soil and water conservation districts",
    "842942167": "supports staff, parents, and community engagement",
    "472671013": "guides vulnerable populations of all ages",
    "593520130": "supports child abuse prevention and education",
    "383798900": "supports excellence in education and research",
    # Filing language / not a mission
    "860211414": "supports cochise college students and programs",
    "330174451": "supports behavioral health services and programs",
    "362883552": "provides shelter and support for families in crisis",
    # Too vague
    "112890302": "supports local economic development projects",
    "390961077": "promotes golf and community recreation programs",
    "260149521": "provides community outreach and support services",
    "943256879": "advances sports medicine education and research",
    "952535904": "advances laser technology education and safety",
    "364885536": "provides faith-based community services",
    # Semicolons / HTML entities
    "464085027": "serves community health programs",
    "942576101": "supports choral music performance and education",
    "060763897": "provides educational, cultural, and recreational programs",
    # Dashes
    "760564888": "provides street lights and pest control services",
    # Dollar amount
    # (860211414 already handled above)
    # Nonsensical
    "382647323": "develops future leaders in business and politics",
    "741191697": "provides educational, cultural, and social programs",
    "454474058": "provides free veterinary care for retired police dogs",
    "900901189": "promotes applied learning programs",
    "580619035": "provides care for surrendered and rescued pets",
    "113700175": "provides peer support and advocacy for parents",
    "461362294": "educates deaf and hard-of-hearing children",
    "742304542": "provides emergency shelter and crisis intervention services",
    "134038993": "operates an incubator for experimental performance",
    "043342182": "promotes racial justice and community health",
    "463134601": "strengthens community resilience before and after disasters",
    "270513560": "promotes positive youth development and family support",
    "954840800": "promotes personal development and organizational leadership",
    "251894523": "supports resilient solutions for watershed health",
    "204570887": "educates students with learning differences",
    "113247651": "provides a transformative musical education for students",
    "310736673": "creates community excellence through arts and culture",
    "742428647": "provides recreational softball for girls",
    "043341661": "inspires and enables all young people",
    "264106369": "inspires high school students to engage civically",
    "203890194": "educates and empowers men, women, and children",
    "208540050": "supports american muslim storytelling and representation",
    "860947944": "provides free long-term care for sick children",
    "203496878": "inspires curiosity and creativity in children",
    "452721646": "educates and inspires children holistically",
    "626074113": "promotes regional arts, culture, and creativity",
    "272081900": "educates and empowers veterans to live engaged lives",
    "850626336": "promotes decent, safe, and sanitary housing",
    "830317641": "supports and expands access to quality health services",
    "475449750": "supports community development throughout rural north dakota",
    "822026061": "improves healthcare through innovation and biomedical research",
    "263042342": "provides a space where teens can explore and grow",
    "237001357": "educates and enriches lives through orchestral music",
    "232798276": "supports employer recruitment, growth, and retention",
    "043769200": "helps students grow spiritually and intellectually",
}

# ── TEMPLATE BODIES ────────────────────────────────────────────────────
TEMPLATE_A_BODY = """{greeting_line}

My name is Alec and I run a company called TheGrantScout. We help nonprofits impacted by recent federal funding cuts find private funding alternatives.

We've been raising awareness of who the local private funders are in each state, and I put together a list of {count} private foundations that fund {sector} organizations in {state}, along with their contact info and recent giving history.

Let me know if you're interested and I'll send it your way.

Alec Kleinman
TheGrantScout
740 E, 2320 N, Provo, UT 84604

P.S - If this isn't relevant just let me know and I won't reach out again."""

TEMPLATE_C_BODY = """{greeting_line}

My name is Alec and I'm with a company called TheGrantScout. I saw that {organization_name} {mission_short} and wanted to see if we can help you find private foundation funding.

Let me know if you're open to a quick call!

Alec Kleinman
TheGrantScout
740 E, 2320 N, Provo, UT 84604

P.S - If this isn't relevant just let me know and I won't reach out again."""


def fix_mission_short(ms):
    """Apply automated fixes to mission_short text."""
    if not ms:
        return ms

    # Strip trailing punctuation (comma, semicolon, colon)
    ms = re.sub(r"[,;:]+\s*$", "", ms.strip())

    # Replace ampersands with 'and'
    ms = ms.replace(" & ", " and ").replace("&", " and ")

    # Fix missing spaces after commas
    ms = re.sub(r",([a-zA-Z])", r", \1", ms)

    # Fix common misspellings
    ms = ms.replace("kindergarden", "kindergarten")
    ms = ms.replace("thier", "their")
    ms = ms.replace("childern", "children")
    ms = ms.replace("perserve", "preserve")
    ms = ms.replace("strenthen", "strengthen")
    ms = ms.replace("recreationalteams", "recreational teams")
    ms = ms.replace("futureexcellence", "future excellence")
    ms = ms.replace("thatchanges", "that changes")
    ms = ms.replace("organization al", "organizational")
    ms = ms.replace("couseling", "counseling")

    # Fix verb mismatches: "VERBs and VERB" → "VERBs and VERBs"
    def fix_verb_mismatch(match):
        v1 = match.group(1)
        v2 = match.group(2)
        # Add 's' to second verb
        if v2.endswith("e"):
            v2_fixed = v2 + "s"
        elif v2.endswith("y"):
            v2_fixed = v2[:-1] + "ies"  # Not common but handle it
        else:
            v2_fixed = v2 + "s"
        return f"{v1} and {v2_fixed}"

    ms = re.sub(
        r"\b(provides|promotes|creates|inspires|educates|supports|fosters|empowers|"
        r"ensures|improves|enriches|helps|operates|serves|advocates|reduces|protects|"
        r"increases|makes|connects) and (enable|empower|transform|stabilize|entertain|"
        r"inspire|challenge|educate|share|facilitate|support|enhance|direct|execute|"
        r"steward|coach|nurture|enrich|advance|expand|accelerate|implement|hope|"
        r"strenthen|strengthen|celebrate|train|safe|supervision|prevention|centered|"
        r"preserve|perserve|test|share)\b",
        fix_verb_mismatch, ms
    )

    # Remove dangling trailing words
    dangling = {"inspiring", "leading", "preparing", "presenting",
                "experiential", "involved", "focusing", "integrate"}
    words = ms.split()
    while words and words[-1].rstrip(".,;:") in dangling:
        words.pop()
    ms = " ".join(words)

    # Strip trailing punctuation again (after word removal)
    ms = re.sub(r"[,;:]+\s*$", "", ms.strip())

    # Remove semicolons within text (replace with commas)
    ms = ms.replace(";", ",")

    # Remove nbsp entities
    ms = re.sub(r"\s*nbsp\s*", " ", ms)
    ms = re.sub(r"\s+", " ", ms).strip()

    return ms


def fix_sector_label(label, ein=None):
    """Fix ugly sector labels."""
    if label == "unknown" and ein and ein in UNKNOWN_SECTOR_OVERRIDES:
        return UNKNOWN_SECTOR_OVERRIDES[ein]
    if label in SECTOR_FIXES:
        fixed = SECTOR_FIXES[label]
        return fixed if fixed else label  # keep "unknown" if no override
    return label


def regenerate_body_a(row, sector):
    """Regenerate Template A email body with fixed sector."""
    gname, _ = resolve_greeting(
        row.get("contact_first_name"), row.get("contact_email")
    )
    return TEMPLATE_A_BODY.format(
        greeting_line=format_greeting_line(gname),
        count=row.get("foundation_count", row.get("display_count", "")),
        sector=sector,
        state=extract_state_from_subject(row["subject_line"]),
    )


def regenerate_body_c(row, mission_short):
    """Regenerate Template C email body with fixed mission_short."""
    gname, _ = resolve_greeting(
        row.get("contact_first_name"), row.get("contact_email")
    )
    return TEMPLATE_C_BODY.format(
        greeting_line=format_greeting_line(gname),
        organization_name=row["organization_name"],
        mission_short=mission_short,
    )


def extract_state_from_subject(subject):
    """Extract state from Template A subject line."""
    # 'Private funders for {sector} in {state}'
    if " in " in subject:
        return subject.rsplit(" in ", 1)[1]
    return ""


def extract_sector_from_subject(subject):
    """Extract sector from Template A subject line."""
    # 'Private funders for {sector} in {state}'
    cleaned = subject.replace("Private funders for ", "")
    if " in " in cleaned:
        return cleaned.rsplit(" in ", 1)[0]
    return cleaned


def extract_count_from_body(body):
    """Extract foundation count from Template A body."""
    m = re.search(r"a list of (\d+) private foundations", body)
    return m.group(1) if m else "50"


def main():
    with open(CSV_IN, "r") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    fixed_ms = 0
    fixed_sector = 0
    fixed_unknown = 0
    removed = []

    for row in rows:
        ein = row["prospect_ein"]

        if row["template_used"] == "A":
            # Fix sector labels
            old_sector = extract_sector_from_subject(row["subject_line"])
            state = extract_state_from_subject(row["subject_line"])
            new_sector = fix_sector_label(old_sector, ein)

            if new_sector != old_sector:
                if old_sector == "unknown":
                    if ein not in UNKNOWN_SECTOR_OVERRIDES:
                        removed.append((ein, row["contact_first_name"], row["organization_name"], "unknown sector, no override"))
                        row["quality_flag"] = "REMOVE:unknown_sector"
                        continue
                    fixed_unknown += 1
                fixed_sector += 1

                # Update subject
                row["subject_line"] = f"Private funders for {new_sector} in {state}"

                # Update body
                count = extract_count_from_body(row["email_body"])
                gname, _ = resolve_greeting(
                    row.get("contact_first_name"), row.get("contact_email")
                )
                row["email_body"] = TEMPLATE_A_BODY.format(
                    greeting_line=format_greeting_line(gname),
                    count=count,
                    sector=new_sector,
                    state=state,
                )

        elif row["template_used"] == "C":
            ms = row.get("mission_short", "")

            # Check manual override first
            if ein in MISSION_OVERRIDES:
                ms = MISSION_OVERRIDES[ein]
                fixed_ms += 1
            else:
                # Apply automated fixes
                old_ms = ms
                ms = fix_mission_short(ms)
                if ms != old_ms:
                    fixed_ms += 1

            row["mission_short"] = ms

            # Regenerate body with fixed mission_short
            gname, _ = resolve_greeting(
                row.get("contact_first_name"), row.get("contact_email")
            )
            row["email_body"] = TEMPLATE_C_BODY.format(
                greeting_line=format_greeting_line(gname),
                organization_name=row["organization_name"],
                mission_short=ms,
            )

    # Remove flagged rows
    final_rows = [r for r in rows if r.get("quality_flag") != "REMOVE:unknown_sector"]

    with open(CSV_OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"=== EMAIL QUALITY FIXES APPLIED ===")
    print(f"Mission_shorts fixed: {fixed_ms}")
    print(f"Sector labels fixed:  {fixed_sector}")
    print(f"Unknown sectors resolved: {fixed_unknown}")
    print(f"Rows removed (unresolvable unknown sector): {len(removed)}")
    print(f"Final row count: {len(final_rows)}")
    print()

    if removed:
        print("=== REMOVED ROWS ===")
        for ein, name, org, reason in removed:
            print(f"  {ein} | {name} | {org} | {reason}")
        print()

    # Verification: spot-check some fixes
    fixed_rows = {r["prospect_ein"]: r for r in final_rows}

    print("=== SAMPLE FIXED SECTOR LABELS ===")
    sample_sectors = ["582005291", "680298871", "364024533", "680101133"]
    for ein in sample_sectors:
        if ein in fixed_rows:
            r = fixed_rows[ein]
            if r["template_used"] == "A":
                print(f"  {ein}: {r['subject_line']}")

    print()
    print("=== SAMPLE FIXED MISSION_SHORTS ===")
    sample_ms = ["832331834", "454474058", "461362294", "860211414", "043341661", "264106369"]
    for ein in sample_ms:
        if ein in fixed_rows:
            r = fixed_rows[ein]
            if r["template_used"] == "C":
                print(f"  {ein}: {r['mission_short']}")


if __name__ == "__main__":
    main()
