#!/usr/bin/env python3
"""greeting_resolver.py - Determine safe greeting name from email + 990 officer name.

Only personalizes when the email prefix confirms the 990 officer name.
Never guesses names from email prefixes (83.8% false positive rate per data review).

Usage:
    from greeting_resolver import resolve_greeting, format_greeting_line

    name, reason = resolve_greeting("Kathleen", "info@org.com")
    line = format_greeting_line(name)  # "Hello,"
"""

import re

# ---------------------------------------------------------------------------
# Generic email prefixes (~120 entries)
# ---------------------------------------------------------------------------

GENERIC_EMAIL_PREFIXES = {
    "info", "admin", "office", "contact", "hello", "team", "general", "mail",
    "support", "community", "programs", "director", "grants", "development",
    "fundraising", "giving", "donate", "membership", "volunteer", "help",
    "staff", "frontdesk", "reception", "outreach", "services", "executive",
    "operations", "main", "org", "foundation", "hresources", "hr",
    "information", "contactus", "connect", "webmaster", "administration",
    "administrator", "frontoffice", "donations", "inquiries", "inquiry",
    "service", "press", "enroll", "web", "feedback", "friends", "alumni",
    "intake", "jobs", "hotline", "email", "donor", "board", "billing",
    "accounting", "finance", "registrar", "enrollment", "careers",
    "recruitment", "scheduling", "referrals", "dispatch", "records", "legal",
    "compliance", "safety", "security", "facilities", "payroll", "training",
    "purchasing", "helpdesk", "postmaster", "noreply", "donotreply",
    "newsletter", "subscriptions", "chapel", "parish", "church", "library",
    "clinic", "store", "shop", "gallery", "museum", "theater", "theatre",
    "boxoffice", "admissions", "tickets", "events", "education", "marketing",
    "media", "communications", "president", "secretary", "treasurer",
    "receptionist", "coordinator", "manager", "bookkeeper",
    "reservations", "welcome", "ask", "questions",
}

# ---------------------------------------------------------------------------
# Generic email pattern rules (regex)
# ---------------------------------------------------------------------------

GENERIC_PATTERNS = [
    re.compile(r"^(info|contact|general|member|donor|front|customer|public|ask|no)[._-]"),
    re.compile(r"(office|admin|info|contact)$"),
    re.compile(r"^do[._-]?not[._-]?reply"),
    re.compile(r"^no[._-]?reply"),
]

# ---------------------------------------------------------------------------
# Junk email domains / patterns
# ---------------------------------------------------------------------------

JUNK_DOMAINS = {"group.calendar.google.com"}
JUNK_EXTENSIONS = {".webp", ".png", ".jpg", ".gif"}

# ---------------------------------------------------------------------------
# Placeholder officer names (not real people)
# ---------------------------------------------------------------------------

PLACEHOLDER_NAMES = {
    "there", "hi", "hello", "dear", "sir", "madam", "whom", "team",
    "friend", "director", "manager", "coordinator", "admin",
    "info", "office", "contact", "support", "n/a", "na", "none",
    "unknown", "test",
}

# ---------------------------------------------------------------------------
# Nickname map (bidirectional)
# ---------------------------------------------------------------------------

_NICKNAME_GROUPS = [
    ("katherine", {"kate", "kathy", "katie", "kath", "kat"}),
    ("kathleen", {"kate", "kathy", "katie", "kath", "kat"}),
    ("catherine", {"kate", "cathy", "cat", "cath", "katie"}),
    ("william", {"will", "bill", "billy", "liam", "wil"}),
    ("robert", {"rob", "bob", "bobby", "robbie", "bert"}),
    ("james", {"jim", "jimmy", "jamie"}),
    ("elizabeth", {"liz", "beth", "betsy", "betty", "eliza", "lizzy"}),
    ("richard", {"rich", "rick", "dick", "ricky"}),
    ("michael", {"mike", "mikey"}),
    ("joseph", {"joe", "joey"}),
    ("thomas", {"tom", "tommy"}),
    ("charles", {"charlie", "chuck", "chas"}),
    ("christopher", {"chris"}),
    ("daniel", {"dan", "danny"}),
    ("matthew", {"matt", "matty"}),
    ("anthony", {"tony"}),
    ("andrew", {"andy", "drew"}),
    ("joshua", {"josh"}),
    ("david", {"dave", "davey"}),
    ("steven", {"steve"}),
    ("stephen", {"steve"}),
    ("edward", {"ed", "eddie", "ted", "teddy"}),
    ("jonathan", {"jon", "john"}),
    ("benjamin", {"ben", "benny"}),
    ("samuel", {"sam", "sammy"}),
    ("nicholas", {"nick", "nicky"}),
    ("timothy", {"tim", "timmy"}),
    ("patrick", {"pat", "patty", "paddy"}),
    ("patricia", {"pat", "patty", "trish", "tricia"}),
    ("jennifer", {"jen", "jenny"}),
    ("jessica", {"jess", "jessie"}),
    ("margaret", {"maggie", "meg", "peggy", "marge"}),
    ("rebecca", {"becky", "becca"}),
    ("alexandra", {"alex", "lexi"}),
    ("alexander", {"alex"}),
    ("pamela", {"pam"}),
    ("deborah", {"deb", "debbie"}),
    ("susan", {"sue", "susie"}),
    ("cynthia", {"cindy"}),
    ("dorothy", {"dot", "dotty"}),
    ("barbara", {"barb", "barbie"}),
    ("christine", {"chris", "christy", "tina"}),
    ("christina", {"chris", "christy", "tina"}),
    ("virginia", {"ginny", "ginger"}),
    ("theresa", {"terry", "tess"}),
    ("teresa", {"terry", "tess"}),
    ("gregory", {"greg"}),
    ("gerald", {"jerry"}),
    ("lawrence", {"larry"}),
    ("raymond", {"ray"}),
    ("kenneth", {"ken", "kenny"}),
    ("ronald", {"ron", "ronny"}),
    ("donald", {"don", "donny"}),
    ("douglas", {"doug"}),
    ("frederick", {"fred", "freddy"}),
    ("leonard", {"len", "lenny"}),
    ("philip", {"phil"}),
    ("phillip", {"phil"}),
    ("nathaniel", {"nate", "nathan"}),
    ("nathan", {"nate"}),
    ("zachary", {"zach", "zack"}),
    ("victoria", {"vicky", "vic"}),
    ("henry", {"hank", "harry"}),
    ("harold", {"hal", "harry"}),
    ("walter", {"walt", "wally"}),
    ("arthur", {"art"}),
    ("theodore", {"ted", "teddy", "theo"}),
    ("melanie", {"mel"}),
    ("jacqueline", {"jackie", "jacqui"}),
    ("samantha", {"sam"}),
    ("stephanie", {"steph"}),
    ("nicole", {"nikki"}),
    ("valerie", {"val"}),
    ("abigail", {"abby"}),
]

# Build lookup: formal_lower -> set of nicknames, nickname_lower -> set of formals
_FORMAL_TO_NICK = {}
_NICK_TO_FORMAL = {}
for formal, nicks in _NICKNAME_GROUPS:
    fl = formal.lower()
    _FORMAL_TO_NICK.setdefault(fl, set()).update(nicks)
    for n in nicks:
        _NICK_TO_FORMAL.setdefault(n.lower(), set()).add(fl)


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def resolve_greeting(contact_first_name, contact_email):
    """Determine the safe greeting name from email address + 990 officer name.

    Returns (verified_name, reason) or (None, reason).
    Only personalizes when the email prefix confirms the 990 name.

    Reasons:
        "no_email"         - No email address provided
        "junk_email"       - Email is a junk/calendar/image URL
        "placeholder_name" - Officer name is a placeholder (e.g. "there", "admin")
        "generic_inbox"    - Email prefix is a generic inbox (info@, admin@, etc.)
        "initial_only"     - Email first part is a single initial
        "exact_match"      - Email prefix matches officer first name exactly
        "nickname_match"   - Email prefix is a known nickname of officer name
        "no_match"         - Email prefix doesn't match officer name
    """
    # Guard: no email
    if not contact_email or not contact_email.strip():
        return (None, "no_email")

    email = contact_email.strip().lower()

    # Guard: junk email
    for domain in JUNK_DOMAINS:
        if email.endswith(domain):
            return (None, "junk_email")
    for ext in JUNK_EXTENSIONS:
        if ext in email:
            return (None, "junk_email")

    # Guard: placeholder officer name
    officer = (contact_first_name or "").strip()
    if not officer or officer.lower() in PLACEHOLDER_NAMES:
        return (None, "placeholder_name")

    # Extract prefix (part before @)
    at_idx = email.find("@")
    if at_idx <= 0:
        return (None, "no_email")
    prefix = email[:at_idx]

    # Check generic inbox: explicit set
    if prefix in GENERIC_EMAIL_PREFIXES:
        return (None, "generic_inbox")

    # Check generic inbox: pattern rules
    for pat in GENERIC_PATTERNS:
        if pat.search(prefix):
            return (None, "generic_inbox")

    # Check generic inbox: prefix too long (>20 chars = always org name)
    if len(prefix) > 20:
        return (None, "generic_inbox")

    # Split prefix on . _ - to get email first part
    parts = re.split(r"[._\-]", prefix)
    email_first = parts[0].lower() if parts else ""

    # Initial only: first part is 1 char
    if len(email_first) <= 1:
        return (None, "initial_only")

    officer_lower = officer.lower()

    # Exact match: email first part == officer name
    if email_first == officer_lower:
        return (officer.capitalize(), "exact_match")

    # Nickname match: check both directions
    # 1. Officer is formal, email is nickname
    officer_nicks = _FORMAL_TO_NICK.get(officer_lower, set())
    if email_first in officer_nicks:
        # Use the nickname as it appears in the email (capitalize it)
        return (email_first.capitalize(), "nickname_match")

    # 2. Officer is nickname, email is formal (e.g. officer="Steve", email="steven@")
    officer_formals = _NICK_TO_FORMAL.get(officer_lower, set())
    if email_first in officer_formals:
        # Use the formal name from the email (capitalize it)
        return (email_first.capitalize(), "nickname_match")

    # 3. Both are nicknames of the same formal name
    for formal_of_officer in officer_formals:
        nicks_of_formal = _FORMAL_TO_NICK.get(formal_of_officer, set())
        if email_first in nicks_of_formal:
            return (email_first.capitalize(), "nickname_match")

    # 4. Officer is formal, email is also formal but different spelling
    #    e.g. officer="Katherine", email="kathleen@" - NOT a match (different names)
    #    This case correctly falls through to no_match.

    # Default: no match
    return (None, "no_match")


def format_greeting_line(greeting_name):
    """Format the greeting line for email body.

    Returns "Hi Name," if greeting_name is provided, otherwise "Hello,".
    """
    if greeting_name:
        return f"Hi {greeting_name},"
    return "Hello,"
