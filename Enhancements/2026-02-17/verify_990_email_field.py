#!/usr/bin/env python3
"""
Verify IRS 990 XML Email Fields Across All TEOS ZIPs
=====================================================
Scans every XML file in every TEOS ZIP on disk to produce definitive counts of:
  1. EMailAddressTxt in Filer section (filer email - expected: 0 in public releases)
  2. RecipientEmailAddressTxt (990-PF Part XV grant application email)
  3. Any other email-related elements

Output: Console summary + CSV with per-ZIP counts

Created: 2026-02-17
"""

import csv
import os
import sys
import time
import zipfile
from collections import defaultdict
from pathlib import Path


RAW_IRS_DIR = Path(__file__).resolve().parent.parent.parent / "1. Database" / "0. Raw IRS Data"
OUTPUT_CSV = Path(__file__).resolve().parent / "DATA_2026-02-17.7_email_field_verification.csv"

# Byte-level search patterns (much faster than XML parsing)
EMAIL_PATTERNS = {
    "EMailAddressTxt": b"EMailAddressTxt",
    "RecipientEmailAddressTxt": b"RecipientEmailAddressTxt",
    "ProfileEmailAddressChangeInd": b"ProfileEmailAddressChangeInd",
    "EmailAddress": b"EmailAddress",  # catch-all for any other email element
}


def scan_zip(zip_path):
    """Scan a single ZIP for email-related XML elements. Returns per-pattern counts."""
    counts = defaultdict(int)
    total_files = 0
    files_with_filer_email = []
    files_with_recipient_email = []

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            xml_names = [n for n in zf.namelist() if n.lower().endswith(".xml")]
            total_files = len(xml_names)

            for xml_name in xml_names:
                try:
                    data = zf.read(xml_name)
                except Exception:
                    continue

                for pattern_name, pattern_bytes in EMAIL_PATTERNS.items():
                    if pattern_bytes in data:
                        counts[pattern_name] += 1

                        # Track specific files for deeper inspection
                        if pattern_name == "EMailAddressTxt":
                            # Exclude RecipientEmailAddressTxt matches
                            if b"RecipientEmailAddressTxt" not in data or (
                                data.replace(b"RecipientEmailAddressTxt", b"").find(b"EMailAddressTxt") >= 0
                            ):
                                # Check if it's truly a Filer email, not just Recipient
                                stripped = data.replace(b"RecipientEmailAddressTxt", b"XXXX")
                                if b"EMailAddressTxt" in stripped:
                                    files_with_filer_email.append(xml_name)

                        if pattern_name == "RecipientEmailAddressTxt":
                            files_with_recipient_email.append(xml_name)

    except (zipfile.BadZipFile, FileNotFoundError) as e:
        print(f"  ERROR reading {zip_path.name}: {e}")
        return total_files, counts, files_with_filer_email, files_with_recipient_email

    return total_files, counts, files_with_filer_email, files_with_recipient_email


def main():
    zip_files = sorted(RAW_IRS_DIR.glob("*.zip"))
    if not zip_files:
        print(f"No ZIP files found in {RAW_IRS_DIR}")
        sys.exit(1)

    print(f"Scanning {len(zip_files)} ZIP files in {RAW_IRS_DIR.name}/")
    print("=" * 80)

    grand_totals = defaultdict(int)
    grand_xml_count = 0
    all_filer_email_files = []
    all_recipient_email_files = []
    csv_rows = []

    start = time.time()

    for i, zip_path in enumerate(zip_files, 1):
        t0 = time.time()
        total_files, counts, filer_files, recip_files = scan_zip(zip_path)
        elapsed = time.time() - t0

        grand_xml_count += total_files
        for k, v in counts.items():
            grand_totals[k] += v
        all_filer_email_files.extend([(zip_path.name, f) for f in filer_files])
        all_recipient_email_files.extend([(zip_path.name, f) for f in recip_files])

        # Progress
        recip_count = counts.get("RecipientEmailAddressTxt", 0)
        filer_count = len(filer_files)
        print(f"  [{i:2d}/{len(zip_files)}] {zip_path.name:<45s} {total_files:>6,d} XMLs | "
              f"Filer: {filer_count:>4d} | Recipient: {recip_count:>4d} | {elapsed:.1f}s")

        csv_rows.append({
            "zip_file": zip_path.name,
            "xml_count": total_files,
            "filer_email_count": filer_count,
            "recipient_email_count": recip_count,
            "email_address_any": counts.get("EmailAddress", 0),
            "profile_email_change": counts.get("ProfileEmailAddressChangeInd", 0),
        })

    elapsed_total = time.time() - start

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "zip_file", "xml_count", "filer_email_count",
            "recipient_email_count", "email_address_any", "profile_email_change"
        ])
        writer.writeheader()
        writer.writerows(csv_rows)
        # Summary row
        writer.writerow({
            "zip_file": "TOTAL",
            "xml_count": grand_xml_count,
            "filer_email_count": len(all_filer_email_files),
            "recipient_email_count": grand_totals.get("RecipientEmailAddressTxt", 0),
            "email_address_any": grand_totals.get("EmailAddress", 0),
            "profile_email_change": grand_totals.get("ProfileEmailAddressChangeInd", 0),
        })

    # Print summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total ZIP files scanned:        {len(zip_files):>10,d}")
    print(f"Total XML files scanned:        {grand_xml_count:>10,d}")
    print(f"Time elapsed:                   {elapsed_total:>10.1f}s")
    print()
    print("Email Element Counts:")
    print(f"  EMailAddressTxt (Filer):      {len(all_filer_email_files):>10,d}")
    print(f"  RecipientEmailAddressTxt:     {grand_totals.get('RecipientEmailAddressTxt', 0):>10,d}")
    print(f"  EmailAddress (any):           {grand_totals.get('EmailAddress', 0):>10,d}")
    print(f"  ProfileEmailAddressChangeInd: {grand_totals.get('ProfileEmailAddressChangeInd', 0):>10,d}")
    print()

    if all_filer_email_files:
        print(f"UNEXPECTED: {len(all_filer_email_files)} files contain Filer EMailAddressTxt!")
        for zip_name, xml_name in all_filer_email_files[:10]:
            print(f"  {zip_name} -> {xml_name}")
    else:
        print("CONFIRMED: 0 files contain Filer EMailAddressTxt (IRS strips from public releases)")

    print()
    print(f"RecipientEmailAddressTxt found in {grand_totals.get('RecipientEmailAddressTxt', 0):,d} files")
    print(f"  (990-PF Part XV grant application contact email)")
    print()
    print(f"CSV saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
