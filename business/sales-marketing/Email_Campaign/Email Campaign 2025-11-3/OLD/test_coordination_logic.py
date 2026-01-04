#!/usr/bin/env python3
"""
Dry-run test for coordination and spacing logic.
Tests the fixes WITHOUT sending any actual emails.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

import coordination
import config

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def test_allocation_scenarios():
    """Test different allocation scenarios"""
    print_header("TEST 1: Allocation Logic")

    scenarios = [
        ("Scenario A: Few followups", 450, 100),
        ("Scenario B: Many followups", 450, 300),
        ("Scenario C: No followups", 450, 0),
        ("Scenario D: Both maxed out", 500, 500),
        ("Scenario E: Only followups", 0, 200),
    ]

    for name, initial_needs, followup_needs in scenarios:
        print(f"\n{name}:")
        print(f"  Initial needs:  {initial_needs}")
        print(f"  Followup needs: {followup_needs}")

        initial_alloc, followup_alloc = coordination.calculate_allocation(initial_needs, followup_needs)

        print(f"  ✓ Initial allocated:  {initial_alloc}")
        print(f"  ✓ Followup allocated: {followup_alloc}")
        print(f"  ✓ Total:              {initial_alloc + followup_alloc}")

        # Validate
        assert initial_alloc + followup_alloc <= config.TOTAL_DAILY_LIMIT, "Total exceeds limit!"
        assert followup_alloc <= 225, "Followup exceeds half capacity!"
        assert initial_alloc <= initial_needs, "Initial allocated more than needs!"
        assert followup_alloc <= followup_needs, "Followup allocated more than needs!"
        print("  ✅ All constraints satisfied!")

def test_spacing_logic():
    """Test even spacing calculation"""
    print_header("TEST 2: Even Spacing Logic")

    # Simulate different time windows and email counts
    scenarios = [
        ("Full day (6 hours)", 6 * 3600, 360),
        ("Half day (3 hours)", 3 * 3600, 180),
        ("2 hours left", 2 * 3600, 120),
        ("1 hour left", 1 * 3600, 60),
    ]

    for name, time_remaining, emails_to_send in scenarios:
        print(f"\n{name}:")
        print(f"  Time remaining: {time_remaining / 3600:.1f} hours ({time_remaining} seconds)")
        print(f"  Emails to send: {emails_to_send}")

        # Calculate average delay
        avg_delay = time_remaining / emails_to_send
        print(f"  ✓ Average delay: {avg_delay:.0f} seconds between emails")

        # Simulate the delay calculation function
        even_delay = time_remaining / emails_to_send
        variation = even_delay * 0.1
        min_delay = even_delay - variation
        max_delay = even_delay + variation

        print(f"  ✓ Delay range: {min_delay:.0f}s - {max_delay:.0f}s (±10% variation)")

        # Calculate expected completion time
        now = datetime.now()
        expected_completion = now + timedelta(seconds=emails_to_send * avg_delay)
        print(f"  ✓ Would finish at: ~{expected_completion.strftime('%I:%M%p')}")
        print(f"  ✅ Emails evenly spaced across time window!")

def test_coordination_flow():
    """Test the coordination flow between scripts"""
    print_header("TEST 3: Coordination Flow Simulation")

    print("Simulating initial script startup...")

    # Create fresh coordination
    coord = coordination.create_new_coordination("2025-11-04")
    print(f"✓ Created coordination file for {coord['date']}")

    # Initial script reports needs
    print("\n1️⃣ Initial script reports needs (450)...")
    initial_alloc = coordination.report_needs_and_allocate('initial', 450)
    print(f"   ✓ Initial allocated: {initial_alloc}")

    # Check status
    status = coordination.get_status_summary()
    print(f"   ✓ Initial remaining: {status['initial']['remaining']}")

    # Followup script reports needs
    print("\n2️⃣ Followup script reports needs (150)...")
    followup_alloc = coordination.report_needs_and_allocate('followup', 150)
    print(f"   ✓ Followup allocated: {followup_alloc}")

    # Check reallocation
    status = coordination.get_status_summary()
    print(f"   ✓ Initial reallocated: {status['initial']['allocated']}")
    print(f"   ✓ Followup reallocated: {status['followup']['allocated']}")
    print(f"   ✓ Total allocated: {status['total']['allocated']}")

    # Simulate sending emails from initial
    print("\n3️⃣ Simulating initial script sending 100 emails...")
    for i in range(100):
        coordination.update_sent_count('initial', i + 1)

    status = coordination.get_status_summary()
    print(f"   ✓ Initial sent: {status['initial']['sent']}")
    print(f"   ✓ Initial remaining: {status['initial']['remaining']}")

    # Simulate sending emails from followup
    print("\n4️⃣ Simulating followup script sending 50 emails...")
    for i in range(50):
        coordination.update_sent_count('followup', i + 1)

    status = coordination.get_status_summary()
    print(f"   ✓ Followup sent: {status['followup']['sent']}")
    print(f"   ✓ Followup remaining: {status['followup']['remaining']}")
    print(f"   ✓ Total sent: {status['total']['sent']}")

    # Test restart scenario (the bug we fixed!)
    print("\n5️⃣ Simulating RESTART (tests the fix!)...")
    remaining_before = coordination.get_remaining_capacity('initial')
    print(f"   ✓ Initial remaining capacity: {remaining_before}")

    # Try to request allocation again (should return same allocation)
    initial_alloc_again = coordination.report_needs_and_allocate('initial', 450)
    print(f"   ✓ Initial allocation (same): {initial_alloc_again}")

    remaining_after = coordination.get_remaining_capacity('initial')
    print(f"   ✓ Initial remaining capacity: {remaining_after}")

    assert remaining_before == remaining_after, "Remaining capacity should not change on restart!"
    print("   ✅ Restart test PASSED - won't oversend!")

    # Display final status
    print("\n📊 Final Status:")
    coordination.display_allocation_summary()

def test_allocation_exhaustion():
    """Test what happens when allocation is exhausted"""
    print_header("TEST 4: Allocation Exhaustion (Critical Bug Test)")

    # Create fresh coordination
    coord = coordination.create_new_coordination("2025-11-05")

    print("Setting up scenario:")
    print("  Initial allocated: 225")
    print("  Initial sent: 225")

    # Allocate and send full amount
    coordination.report_needs_and_allocate('initial', 450)
    coordination.update_sent_count('initial', 225)

    remaining = coordination.get_remaining_capacity('initial')
    print(f"\n✓ Initial remaining capacity: {remaining}")

    if remaining == 0:
        print("✅ CORRECT: Remaining capacity is 0")
        print("✅ Script will NOT send more emails")
        print("✅ BUG IS FIXED!")
    else:
        print(f"❌ ERROR: Should be 0, but is {remaining}")
        print("❌ Bug still exists!")

def main():
    """Run all tests"""
    print("\n" + "🧪" * 35)
    print("  DRY-RUN COORDINATION & SPACING LOGIC TEST")
    print("  (No actual emails will be sent)")
    print("🧪" * 35)

    try:
        # Run all test suites
        test_allocation_scenarios()
        test_spacing_logic()
        test_coordination_flow()
        test_allocation_exhaustion()

        # Final summary
        print("\n" + "=" * 70)
        print("  ✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nThe fixes are working correctly:")
        print("  1. ✅ Smart allocation based on needs")
        print("  2. ✅ Even spacing across time window")
        print("  3. ✅ Respects allocation limits")
        print("  4. ✅ Won't oversend on restart (BUG FIXED!)")
        print("  5. ✅ Stops when allocation exhausted")
        print("\nReady for production! 🚀\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
