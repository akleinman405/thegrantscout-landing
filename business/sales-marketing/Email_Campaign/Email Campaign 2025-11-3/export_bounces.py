"""
Export bounced emails from sent_tracker.csv to bounce_list.csv
This utility helps maintain a clean bounce list for future campaign filtering.
"""

import csv
import os
from datetime import datetime
from config import SENT_TRACKER, BASE_DIR

# Define bounce list path (in tracker subfolder)
BOUNCE_LIST = os.path.join(
    os.path.dirname(__file__),
    "bounce_list.csv"
)


def export_bounces():
    """Read sent_tracker.csv and export bounced emails to bounce_list.csv"""

    try:
        # Check if input file exists
        if not os.path.exists(SENT_TRACKER):
            print(f"Error: {SENT_TRACKER} not found")
            return

        bounced_records = []

        # Read sent_tracker.csv and filter for bounced emails
        print(f"Reading {SENT_TRACKER}...")

        try:
            with open(SENT_TRACKER, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    if row.get('status', '').upper() == 'BOUNCED':
                        bounced_records.append({
                            'email': row.get('email', ''),
                            'first_bounced_date': row.get('timestamp', ''),
                            'bounce_count': '1',
                            'reason': row.get('error_message', 'Unknown'),
                            'vertical': row.get('vertical', '')
                        })

        except csv.Error as e:
            print(f"Error: CSV parsing failed for {SENT_TRACKER}: {e}")
            return
        except UnicodeDecodeError as e:
            print(f"Error: File encoding issue in {SENT_TRACKER}: {e}")
            print("Hint: Ensure file is saved as UTF-8")
            return

        # Write to bounce_list.csv
        if bounced_records:
            print(f"Exporting {len(bounced_records)} bounced emails to {BOUNCE_LIST}...")

            try:
                with open(BOUNCE_LIST, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['email', 'first_bounced_date', 'bounce_count', 'reason', 'vertical']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(bounced_records)
                    f.flush()
                    os.fsync(f.fileno())  # WSL compatibility

            except PermissionError as e:
                print(f"Error: Permission denied writing to {BOUNCE_LIST}: {e}")
                print("Hint: Check if file is open in another program")
                return
            except csv.Error as e:
                print(f"Error: CSV writing failed for {BOUNCE_LIST}: {e}")
                return

            print(f"\nExport complete!")
            print(f"Total bounced emails: {len(bounced_records)}")

            # Print summary by vertical
            vertical_counts = {}
            for record in bounced_records:
                vertical = record['vertical']
                vertical_counts[vertical] = vertical_counts.get(vertical, 0) + 1

            print("\nBounces by vertical:")
            for vertical, count in sorted(vertical_counts.items()):
                print(f"  {vertical}: {count}")
        else:
            print("No bounced emails found in sent_tracker.csv")

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        return
    except Exception as e:
        print(f"Error: Unexpected error during export: {type(e).__name__} - {e}")
        return


if __name__ == "__main__":
    export_bounces()
