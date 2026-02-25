"""
TheGrantScout Text Utilities
==============================

Shared text-cleaning functions for call list generation, foundation lists,
and other prospect tools. Follows the branding.py pattern as an importable
constants + utils module.

Used by: generate_call_list.py, generate_foundation_list.py
"""

import re

# ============================================================================
# CONSTANTS
# ============================================================================

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

LOWERCASE_WORDS = {"of", "the", "and", "in", "for", "a", "an", "to", "on", "at", "by", "or", "de", "la", "le", "van", "von"}

ORG_ACRONYMS = {"INC", "LLC", "USA", "US", "II", "III", "IV", "DBA", "PCF", "AFW", "YMCA", "YWCA"}

JUNK_MISSIONS = {"SEE SCHEDULE O", "SEE SCHEDULE O.", "REFER TO SCHEDULE O", "N/A", "NONE"}


# ============================================================================
# FUNCTIONS
# ============================================================================

def format_phone(raw):
    """Format phone number as XXX-XXX-XXXX."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits[0] == "1":
        digits = digits[1:]
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return raw.strip()


def clean_website(url):
    """Lowercase and normalize website URL."""
    if not url:
        return ""
    url = url.strip().lower()
    if not url.startswith("http"):
        url = "https://" + url
    return url


def title_case_name(name):
    """Title-case a person name, handling articles, short caps, and suffixes."""
    if not name:
        return ""
    name = name.strip()
    parts = name.split()
    result = []
    for i, part in enumerate(parts):
        if part.lower() in LOWERCASE_WORDS and i > 0:
            result.append(part.lower())
        elif len(part) <= 3 and part.upper() == part and not part.endswith("."):
            result.append(part.upper())
        else:
            result.append(part.capitalize())
    return " ".join(result)


def title_case_org(name):
    """Title-case an org name, preserving acronyms and handling ALL CAPS input."""
    if not name:
        return ""
    name = name.strip()
    if name == name.upper() and len(name) > 5:
        parts = name.split()
        result = []
        for i, part in enumerate(parts):
            clean = part.rstrip(",.'")
            suffix = part[len(clean):]
            if clean.upper() in ORG_ACRONYMS:
                result.append(clean.upper() + suffix)
            elif clean.lower() in LOWERCASE_WORDS and i > 0:
                result.append(clean.lower() + suffix)
            else:
                result.append(clean.capitalize() + suffix)
        return " ".join(result)
    return name


def clean_title(title):
    """Clean and normalize officer title (CEO, CFO, etc.)."""
    if not title:
        return ""
    title = title.strip()
    if title.upper() == title or title.lower() == title:
        title = title.title()
    title = (title.replace("Ceo", "CEO").replace("Cfo", "CFO")
             .replace("Coo", "COO").replace("Vp ", "VP "))
    return title


def truncate_about(mission, program_desc, max_sentences=2):
    """Extract 1-2 sentences for the About field, filtering junk values."""
    text = mission or program_desc or ""
    text = text.strip()
    if not text:
        return ""
    if text.upper().strip().rstrip(".") in {j.rstrip(".") for j in JUNK_MISSIONS}:
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


def fmt_dollars(amount):
    """Format as $X,XXX,XXX."""
    if amount is None:
        return "N/A"
    return f"${amount:,.0f}"


def slugify(label):
    """Convert label to snake_case for filenames."""
    return re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')
