#!/usr/bin/env python3
"""
Backfill initial_body, template_used, greeting_name, greeting_reason
for the 1,122 Resend-era rows in grantscout_campaign.campaign_prospect_status.

Reads generated_emails CSVs + send_log CSVs, joins on contact_email/to_email,
and outputs UPDATE SQL for review (does NOT execute anything).
"""

import csv
import sys
from collections import defaultdict

BASE = "/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-17"

GENERATED_FILES = [
    f"{BASE}/DATA_2026-02-17.3_generated_emails.csv",
    f"{BASE}/DATA_2026-02-18_generated_emails.csv",
]

SEND_LOG_FILES = [
    f"{BASE}/DATA_2026-02-17.3_send_log.csv",
    f"{BASE}/DATA_2026-02-18_send_log.csv",
]

# ---------------------------------------------------------------------------
# 1. Build set of sent emails from send logs
# ---------------------------------------------------------------------------
sent_emails = set()
for path in SEND_LOG_FILES:
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["status"] == "sent":
                sent_emails.add(row["to_email"].strip().lower())

print(f"Total sent emails across send logs: {len(sent_emails)}")

# ---------------------------------------------------------------------------
# 2. Load generated emails, keep only those that were sent
# ---------------------------------------------------------------------------
# Key: contact_email (lowered) -> dict with email_body, template_used, contact_first_name
generated = {}
dupes = 0
for path in GENERATED_FILES:
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            email_key = row["contact_email"].strip().lower()
            if email_key in sent_emails:
                if email_key in generated:
                    dupes += 1
                    # Keep the first one (shouldn't happen given no overlap)
                    continue
                generated[email_key] = {
                    "email_body": row["email_body"],
                    "template_used": row["template_used"],
                    "contact_first_name": row["contact_first_name"],
                }

print(f"Matched generated emails for sent rows: {len(generated)}")
if dupes:
    print(f"  (skipped {dupes} duplicate email keys)")

# Check for sent emails that had no generated match
unmatched = sent_emails - set(generated.keys())
if unmatched:
    print(f"WARNING: {len(unmatched)} sent emails had no generated email match:")
    for e in sorted(unmatched)[:10]:
        print(f"  {e}")

# ---------------------------------------------------------------------------
# 3. Build UPDATE statements
# ---------------------------------------------------------------------------

def pg_escape(s: str) -> str:
    """Escape a string for Postgres single-quoted literal using dollar quoting
    fallback for bodies that contain single quotes."""
    if s is None:
        return "NULL"
    # Replace single quotes by doubling them (standard SQL escaping)
    return "'" + s.replace("'", "''") + "'"


# Build VALUES list for a single UPDATE ... FROM (VALUES ...) approach
values_rows = []
for email_key, data in sorted(generated.items()):
    values_rows.append(
        f"  ({pg_escape(email_key)}, {pg_escape(data['email_body'])}, "
        f"{pg_escape(data['template_used'])}, {pg_escape(data['contact_first_name'])}, "
        f"'officer_name')"
    )

print(f"\nRows to update: {len(values_rows)}")
print(f"Expected: 1122")
if len(values_rows) != 1122:
    print(f"  ** MISMATCH — investigate before running! **")

# ---------------------------------------------------------------------------
# 4. Print 3 sample UPDATE statements (individual form for review)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("SAMPLE INDIVIDUAL UPDATE STATEMENTS (3 of {})".format(len(values_rows)))
print("=" * 70)

samples = sorted(generated.items())[:3]
for email_key, data in samples:
    sql = (
        f"UPDATE grantscout_campaign.campaign_prospect_status\n"
        f"SET initial_body = {pg_escape(data['email_body'])},\n"
        f"    template_used = {pg_escape(data['template_used'])},\n"
        f"    greeting_name = {pg_escape(data['contact_first_name'])},\n"
        f"    greeting_reason = 'officer_name',\n"
        f"    updated_at = NOW()\n"
        f"WHERE source_file = 'send_campaign.py'\n"
        f"  AND lower(email) = {pg_escape(email_key)};\n"
    )
    print(sql)

# ---------------------------------------------------------------------------
# 5. Print the full batch UPDATE using VALUES list
# ---------------------------------------------------------------------------
print("=" * 70)
print("FULL BATCH UPDATE (UPDATE ... FROM VALUES)")
print("=" * 70)

batch_sql = """UPDATE grantscout_campaign.campaign_prospect_status AS cps
SET initial_body   = v.initial_body,
    template_used  = v.template_used,
    greeting_name  = v.greeting_name,
    greeting_reason = v.greeting_reason,
    updated_at     = NOW()
FROM (VALUES
{}
) AS v(email, initial_body, template_used, greeting_name, greeting_reason)
WHERE cps.source_file = 'send_campaign.py'
  AND lower(cps.email) = v.email;
""".format(",\n".join(values_rows))

# Write to file since it will be huge
output_path = f"{BASE}/backfill_resend_era.sql"
with open(output_path, "w") as f:
    f.write("-- Backfill initial_body, template_used, greeting_name, greeting_reason\n")
    f.write("-- for 1,122 Resend-era rows in grantscout_campaign.campaign_prospect_status\n")
    f.write("-- Generated by backfill_resend_era.py\n")
    f.write("-- DO NOT RUN without reviewing first!\n\n")
    f.write("BEGIN;\n\n")
    f.write(batch_sql)
    f.write("\n-- Verify count before committing:\n")
    f.write("-- SELECT count(*) FROM grantscout_campaign.campaign_prospect_status\n")
    f.write("-- WHERE source_file = 'send_campaign.py' AND initial_body IS NOT NULL;\n")
    f.write("-- Expected: 1122\n\n")
    f.write("-- COMMIT;\n")
    f.write("-- (uncomment COMMIT above after verifying)\n")
    f.write("ROLLBACK;\n")

print(f"\nFull SQL written to: {output_path}")
print(f"File size: ", end="")

import os
size = os.path.getsize(output_path)
if size > 1024 * 1024:
    print(f"{size / 1024 / 1024:.1f} MB")
else:
    print(f"{size / 1024:.1f} KB")

# Also print the first ~100 lines of the SQL for inline review
print("\n--- First 30 lines of SQL file ---")
with open(output_path) as f:
    for i, line in enumerate(f):
        if i >= 30:
            print("... (truncated, see full file)")
            break
        print(line, end="")

