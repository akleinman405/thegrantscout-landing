"""
Test script for integration layer.
Tests reading actual files from the campaign directory.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrations import (
    read_prospects,
    read_sent_tracker,
    read_response_tracker,
    read_coordination,
    get_allocation_status,
    get_daily_metrics,
    get_vertical_breakdown,
    get_prospect_count,
    get_prospect_stats
)
from utils import (
    get_base_dir,
    get_vertical_csv_path,
    get_sent_tracker_path,
    get_coordination_path,
    format_number,
    format_percentage,
    format_date
)


def test_paths():
    """Test that all paths are correctly configured."""
    print("=" * 60)
    print("TESTING PATH UTILITIES")
    print("=" * 60)

    base_dir = get_base_dir()
    print(f"Base Directory: {base_dir}")

    debarment_csv = get_vertical_csv_path('debarment')
    print(f"Debarment CSV: {debarment_csv}")
    print(f"  Exists: {os.path.exists(debarment_csv)}")

    sent_tracker = get_sent_tracker_path()
    print(f"Sent Tracker: {sent_tracker}")
    print(f"  Exists: {os.path.exists(sent_tracker)}")

    coordination = get_coordination_path()
    print(f"Coordination: {coordination}")
    print(f"  Exists: {os.path.exists(coordination)}")

    print()


def test_read_prospects():
    """Test reading prospect CSV files."""
    print("=" * 60)
    print("TESTING PROSPECT READER")
    print("=" * 60)

    verticals = ['debarment', 'food_recall', 'grant_alerts']

    for vertical in verticals:
        try:
            df = read_prospects(vertical)
            count = len(df)
            print(f"\n{vertical.upper()}:")
            print(f"  Total Prospects: {format_number(count)}")

            if count > 0:
                print(f"  Columns: {', '.join(df.columns.tolist())}")
                print(f"  Sample Email: {df.iloc[0]['email'] if 'email' in df.columns else 'N/A'}")

        except Exception as e:
            print(f"\n{vertical.upper()}: ERROR - {str(e)}")

    print()


def test_read_trackers():
    """Test reading sent and response tracker files."""
    print("=" * 60)
    print("TESTING TRACKER READERS")
    print("=" * 60)

    try:
        # Sent tracker
        sent_df = read_sent_tracker()
        print(f"\nSent Tracker:")
        print(f"  Total Sent: {format_number(len(sent_df))}")

        if not sent_df.empty:
            print(f"  Columns: {', '.join(sent_df.columns.tolist())}")
            print(f"  Date Range: {sent_df['date'].min()} to {sent_df['date'].max()}")

            # Count by vertical
            if 'vertical' in sent_df.columns:
                vertical_counts = sent_df['vertical'].value_counts()
                print("\n  By Vertical:")
                for vertical, count in vertical_counts.items():
                    print(f"    {vertical}: {format_number(count)}")

    except Exception as e:
        print(f"\nSent Tracker: ERROR - {str(e)}")

    try:
        # Response tracker
        response_df = read_response_tracker()
        print(f"\nResponse Tracker:")
        print(f"  Total Responses: {format_number(len(response_df))}")

        if not response_df.empty:
            print(f"  Columns: {', '.join(response_df.columns.tolist())}")

    except Exception as e:
        print(f"\nResponse Tracker: ERROR - {str(e)}")

    print()


def test_coordination():
    """Test reading coordination.json."""
    print("=" * 60)
    print("TESTING COORDINATION READER")
    print("=" * 60)

    try:
        coord = read_coordination()
        print(f"\nCoordination Data:")
        print(f"  Date: {coord.get('date', 'N/A')}")
        print(f"  Last Updated: {coord.get('last_updated', 'N/A')}")

        if 'initial' in coord:
            initial = coord['initial']
            print(f"\n  Initial Campaign:")
            print(f"    Allocated: {initial.get('allocated', 0)}")
            print(f"    Sent: {initial.get('sent', 0)}")
            print(f"    Status: {initial.get('status', 'N/A')}")

        if 'followup' in coord:
            followup = coord['followup']
            print(f"\n  Followup Campaign:")
            print(f"    Allocated: {followup.get('allocated', 0)}")
            print(f"    Sent: {followup.get('sent', 0)}")
            print(f"    Status: {followup.get('status', 'N/A')}")

        # Test allocation status
        status = get_allocation_status()
        print(f"\n  Total Capacity: {status['total_capacity']}")
        print(f"  Total Sent: {status['total_sent']}")
        print(f"  Total Remaining: {status['total_remaining']}")

    except Exception as e:
        print(f"\nCoordination: ERROR - {str(e)}")

    print()


def test_metrics():
    """Test metric calculations."""
    print("=" * 60)
    print("TESTING METRICS")
    print("=" * 60)

    try:
        metrics = get_daily_metrics()
        print(f"\nDaily Metrics:")
        print(f"  Sent Today: {format_number(metrics['sent_today'])}")
        print(f"  Sent This Week: {format_number(metrics['sent_this_week'])}")
        print(f"  Sent This Month: {format_number(metrics['sent_this_month'])}")
        print(f"  Response Rate: {format_percentage(metrics['response_rate'])}")
        print(f"  Error Rate: {format_percentage(metrics['error_rate'])}")

    except Exception as e:
        print(f"\nDaily Metrics: ERROR - {str(e)}")

    try:
        breakdown = get_vertical_breakdown()
        print(f"\nVertical Breakdown:")
        for item in breakdown:
            print(f"  {item['vertical'].upper()}:")
            print(f"    Total Sent: {format_number(item['sent_total'])}")
            print(f"    Sent Today: {format_number(item['sent_today'])}")
            print(f"    Response Rate: {format_percentage(item['response_rate'])}")

    except Exception as e:
        print(f"\nVertical Breakdown: ERROR - {str(e)}")

    print()


def test_prospect_stats():
    """Test prospect statistics."""
    print("=" * 60)
    print("TESTING PROSPECT STATS")
    print("=" * 60)

    verticals = ['debarment', 'food_recall']
    sent_df = read_sent_tracker()

    for vertical in verticals:
        try:
            stats = get_prospect_stats(vertical, sent_df)
            print(f"\n{vertical.upper()}:")
            print(f"  Total: {format_number(stats['total'])}")
            print(f"  Not Contacted: {format_number(stats['not_contacted'])}")
            print(f"  Initial Sent: {format_number(stats['initial_sent'])}")
            print(f"  Followup Sent: {format_number(stats['followup_sent'])}")

        except Exception as e:
            print(f"\n{vertical.upper()}: ERROR - {str(e)}")

    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "INTEGRATION LAYER TEST SUITE" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    try:
        test_paths()
        test_read_prospects()
        test_read_trackers()
        test_coordination()
        test_metrics()
        test_prospect_stats()

        print("=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
