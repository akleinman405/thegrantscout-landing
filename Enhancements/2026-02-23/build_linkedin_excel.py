#!/usr/bin/env python3
"""Parse LinkedIn search results and build outreach Excel file."""
import sys, re
sys.path.insert(0, "/Users/aleckleinman/Documents/TheGrantScout/0. Tools")
from xlsx_utils import create_workbook

def split_title_org(line):
    """Split a combined title+org line into (title, org)."""
    line = line.strip()

    # First try: double-space split (most reliable)
    parts = re.split(r'  +', line)
    if len(parts) >= 2:
        return parts[0].strip(), " ".join(parts[1:]).strip()

    # Second try: "at" keyword between title and org
    # e.g. "Director of Development at Ascension Living Ascension Healthcare Services"
    # But be careful: "at UC Berkeley" is part of org name
    at_match = re.search(r'\b(at)\s+(?=[A-Z])', line)

    # Third try: heuristic split using role keywords and functional areas
    role_words = [
        'Director', 'Officer', 'Manager', 'President', 'Lead', 'Coordinator',
        'Specialist', 'Strategist', 'Principal', 'Partner', 'Founder',
        'Associate', 'Estimator', 'Navigator', 'Scheduler'
    ]

    functional_areas = {
        'Development', 'Marketing', 'Communications', 'Partnerships', 'Engagement',
        'Operations', 'Programs', 'Advancement', 'Strategy', 'Sales', 'Business',
        'Grantmaking', 'Training', 'Initiatives', 'Impact', 'Innovation', 'Growth',
        'Fundraising', 'Membership', 'Community', 'Fund', 'Grants', 'Lodge'
    }

    connectors = {'of', 'for', 'and', '&', '-', 'at', 'in', 'the', ',', '+'}

    words = line.split()

    # Find the last role keyword position
    last_role_idx = -1
    for i, w in enumerate(words):
        clean_w = w.strip('(),')
        # Handle prefixes like "Co-Principal" and abbreviations like "VP"
        clean_w = re.sub(r'^Co-', '', clean_w)
        if clean_w in role_words or clean_w in ('VP', 'SVP', 'EVP', 'CDO', 'COO', 'CEO'):
            last_role_idx = i

    if last_role_idx == -1:
        # No role keyword found, return whole line as title
        return line, ""

    # From the role keyword, scan forward through functional area modifiers
    end_of_title = last_role_idx
    i = last_role_idx + 1

    # Handle parenthetical like (CDO) right after role word
    if i < len(words) and words[i].startswith('('):
        while i < len(words):
            end_of_title = i
            if words[i].endswith(')'):
                i += 1
                break
            i += 1

    # Now scan through connector + functional area patterns
    # Only consume a connector if it's followed by a functional area
    while i < len(words):
        w = words[i]
        clean_w = w.strip('(),')
        if clean_w in functional_areas:
            end_of_title = i
            i += 1
        elif clean_w.lower() in connectors or clean_w in ('&', '-', '+', ','):
            # It's a connector - only consume if next word is functional area or connector
            if i + 1 < len(words):
                nw = words[i + 1].strip('(),')
                if nw in functional_areas or nw.lower() in connectors or nw in ('&', '-', '+'):
                    end_of_title = i
                    i += 1
                else:
                    break
            else:
                break
        else:
            break

    title = " ".join(words[:end_of_title + 1])
    org_words = words[end_of_title + 1:]
    # Strip leading connectors from org name
    while org_words and (org_words[0].strip('(),').lower() in connectors or org_words[0] in ('&', '-', '+', ',')):
        org_words = org_words[1:]
    org = " ".join(org_words)
    return title.strip().rstrip(','), org.strip()


# Read the markdown
with open("/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-23/Linkedin.md") as f:
    text = f.read()

lines = text.split("\n")

# Extract person blocks using "Go to X's profile" as delimiter
people = []
seen = set()

i = 0
while i < len(lines):
    line = lines[i].strip()

    # Match "Go to X's profile" (handles both straight and curly apostrophes)
    m = re.match(r"Go to (.+?)(?:['\u2019]s|['\u2019]) profile", line)
    if not m:
        i += 1
        continue

    # Find the name (next non-empty line)
    j = i + 1
    full_name = ""
    while j < len(lines) and j < i + 5:
        candidate = lines[j].strip()
        if candidate and "Go to" not in candidate and "Add " not in candidate:
            full_name = candidate
            break
        j += 1

    if not full_name or full_name in seen:
        i = j + 1
        continue

    # Find the title/org line: look for lines ending with 3+ spaces in the raw text
    title_org_line = ""
    k = j + 1
    while k < len(lines) and k < j + 10:
        raw = lines[k]
        stripped = raw.strip()

        # Skip empty, connection, degree lines
        if not stripped or "degree connection" in stripped or stripped.startswith("·"):
            k += 1
            continue

        # The title/org line typically ends with trailing spaces in the raw file
        # and contains a role-like keyword
        role_indicators = ['Director', 'Officer', 'Manager', 'President', 'Development',
                          'Principal', 'Partner', 'Founder', 'Coordinator', 'Strategist',
                          'Lead', 'Associate', 'Specialist', 'Estimator', 'Navigator',
                          'Scheduler']

        if any(kw in stripped for kw in role_indicators) and raw.rstrip('\n').endswith('   '):
            title_org_line = stripped
            break

        # Also catch lines with role indicators that might not have trailing spaces
        if any(kw in stripped for kw in role_indicators) and not any(
            x in stripped for x in ['United States', 'in role', 'About:', 'recent post',
                                    'mutual connection', 'Add ', 'Message', 'Save',
                                    'Recently', 'Shared']):
            title_org_line = stripped
            break

        # If we hit location or time-in-role, we passed it
        if any(x in stripped for x in ['United States', 'Bay Area', 'in role', 'About:']):
            break

        k += 1

    if full_name and title_org_line:
        seen.add(full_name)
        title, org = split_title_org(title_org_line)

        # Get first name
        clean_name = re.split(r',\s', full_name)[0]
        first_name = clean_name.split()[0]

        if org:
            message = f"Hey {first_name}, I ran into {org} online and wanted to connect."
        else:
            message = f"Hey {first_name}, I came across your profile online and wanted to connect."

        people.append([full_name, org, title, message])

    i = k + 1 if k > i else i + 1

print(f"Found {len(people)} unique people")

# Show a few samples for verification
for p in people[:5]:
    print(f"  {p[0]} | {p[2]} | {p[1]}")
print("...")
# Show some that were previously broken
for p in people:
    if any(n in p[0] for n in ['Andres', 'Sam Ass', 'Lisa Rud', 'Adam Stan']):
        print(f"  {p[0]} | {p[2]} | {p[1]}")

# Create Excel
headers = ["Name", "Organization", "Job Title", "Message"]
output_path = "/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-23/DATA_2026-02-23_linkedin_outreach.xlsx"
create_workbook(people, headers, output_path)
print(f"\nSaved {len(people)} contacts to {output_path}")
