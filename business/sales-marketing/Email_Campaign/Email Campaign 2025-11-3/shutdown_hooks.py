"""
Shutdown Hooks for Email Campaign System

Provides automatic cleanup actions when campaign scripts close:
1. Save progress (coordination.json)
2. Check for bounces (Gmail API)
3. Sync to CRM (Supabase)

Usage:
    from shutdown_hooks import run_shutdown_hooks, sync_to_crm_batch

    # At end of script or in signal handler:
    run_shutdown_hooks(script_type='initial', check_bounces=True)

    # Periodic sync every N emails:
    sync_to_crm_batch(emails_sent_since_last_sync)
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional

import config
import coordination

# Track emails since last CRM sync
_emails_since_last_sync = 0
CRM_SYNC_INTERVAL = 100  # Sync to CRM every N emails


def increment_email_counter():
    """Increment the email counter and check if we need to sync."""
    global _emails_since_last_sync
    _emails_since_last_sync += 1

    if _emails_since_last_sync >= CRM_SYNC_INTERVAL:
        sync_to_crm_batch()
        _emails_since_last_sync = 0


def sync_to_crm_batch():
    """
    Sync recent emails from sent_tracker.csv to CRM.
    Only syncs emails from the last 24 hours that aren't already synced.
    """
    try:
        import crm_integration as crm

        print("\n📤 Syncing recent emails to CRM...")

        # Sync emails from today
        today = datetime.now().strftime('%Y-%m-%d')
        stats = crm.sync_sent_tracker_to_crm(since_date=today)

        if stats.get('error'):
            print(f"   ⚠️  CRM sync error: {stats['error']}")
        else:
            print(f"   ✅ Synced {stats.get('synced', 0)} emails to CRM")
            if stats.get('skipped', 0) > 0:
                print(f"   ℹ️  {stats['skipped']} emails skipped (not in CRM)")

    except ImportError:
        print("   ⚠️  CRM integration module not available")
    except Exception as e:
        print(f"   ⚠️  CRM sync error: {e}")


def check_bounces_quick():
    """
    Quick bounce check using Gmail API (if authenticated).
    Only checks last 7 days and auto-updates CSVs.
    """
    try:
        # Check if we have a valid token
        token_file = os.path.join(
            os.path.dirname(__file__),
            'credentials',
            'token.json'
        )

        if not os.path.exists(token_file):
            print("\n📬 Bounce check skipped (Gmail not authenticated)")
            print("   Run 'python campaign_tracker.py' to authenticate")
            return

        print("\n📬 Checking for bounces and replies...")

        # Import tracker module
        import campaign_tracker as tracker

        # Authenticate
        service = tracker.authenticate_gmail()
        if not service:
            print("   ⚠️  Gmail authentication failed")
            return

        # Load tracking data
        sent_rows, sent_emails = tracker.load_sent_tracker()
        response_rows = tracker.load_response_tracker()

        if not sent_rows:
            print("   ℹ️  No sent emails to check")
            return

        # Search for bounces (last 7 days only for speed)
        bounced_emails = tracker.find_bounced_emails(service, days_back=7)

        # Filter to our emails
        relevant_bounces = {
            email: info for email, info in bounced_emails.items()
            if email.lower() in sent_emails
        }

        # Search for replies
        replies = tracker.find_replies(service, sent_emails, days_back=7)

        # Update tracking data
        updated_sent_rows, bounce_updates = tracker.update_sent_tracker_with_bounces(
            sent_rows, relevant_bounces
        )
        updated_response_rows, reply_updates = tracker.update_response_tracker_with_replies(
            response_rows, replies
        )

        # Save if there are updates
        if bounce_updates > 0:
            tracker.save_sent_tracker(updated_sent_rows)
            print(f"   ✅ Updated {bounce_updates} bounces in sent_tracker.csv")
        else:
            print("   ✅ No new bounces found")

        if reply_updates > 0:
            tracker.save_response_tracker(updated_response_rows)
            print(f"   ✅ Updated {reply_updates} replies in response_tracker.csv")
        else:
            print("   ✅ No new replies found")

    except ImportError as e:
        print(f"\n📬 Bounce check skipped (missing module: {e})")
    except Exception as e:
        print(f"\n📬 Bounce check error: {e}")


def run_shutdown_hooks(
    script_type: str,
    check_bounces: bool = True,
    sync_crm: bool = True,
    verbose: bool = True
):
    """
    Run all shutdown hooks for clean campaign close.

    Args:
        script_type: 'initial' or 'followup'
        check_bounces: Whether to check Gmail for bounces
        sync_crm: Whether to sync to CRM
        verbose: Print progress messages
    """
    if verbose:
        print("\n" + "="*60)
        print("RUNNING SHUTDOWN HOOKS")
        print("="*60)

    # 1. Mark script as stopped in coordination
    try:
        coordination.mark_script_stopped(script_type)
        if verbose:
            print(f"\n✅ Marked {script_type} script as stopped")
    except Exception as e:
        if verbose:
            print(f"\n⚠️  Could not update coordination: {e}")

    # 2. Sync to CRM
    if sync_crm:
        sync_to_crm_batch()

    # 3. Check for bounces
    if check_bounces:
        check_bounces_quick()

    if verbose:
        print("\n" + "="*60)
        print("SHUTDOWN COMPLETE")
        print("="*60 + "\n")


# Convenience function for signal handlers
def create_shutdown_handler(script_type: str):
    """
    Create a signal handler that runs shutdown hooks.

    Usage:
        import signal
        from shutdown_hooks import create_shutdown_handler

        signal.signal(signal.SIGINT, create_shutdown_handler('initial'))
    """
    def handler(sig, frame):
        print("\n\n🛑 Interruption detected. Running shutdown hooks...")
        run_shutdown_hooks(script_type, check_bounces=True, sync_crm=True)
        sys.exit(0)

    return handler
