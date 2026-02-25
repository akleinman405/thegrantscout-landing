#!/usr/bin/env python3
"""
CLI for the nonprofit email scraper.

Commands:
    scrape-emails   Scrape a batch of nonprofit websites for emails
    run-overnight   Continuous scraping with graceful shutdown
    status          Show pipeline progress statistics
    clean           Remove junk emails (cross-org duplicates in 3+ orgs)
    classify        Classify emails by type (junk/role/generic/personal)
    validate-mx     Validate MX records for all email domains
    fix-existing    Fix existing emails (delete junk, strip @www., reclassify)
    rescrape        Reset not_found sites for re-scraping with enhanced extraction

Usage:
    python3 cli.py scrape-emails --limit 1000 --concurrency 10
    python3 cli.py run-overnight --max-hours 8 --concurrency 10
    python3 cli.py status
    python3 cli.py clean --dry-run
    python3 cli.py clean --execute
    python3 cli.py classify --execute
    python3 cli.py validate-mx --concurrency 50
    python3 cli.py fix-existing --dry-run
    python3 cli.py fix-existing --execute
    python3 cli.py rescrape --dry-run
    python3 cli.py rescrape --execute
"""

import sys
import signal
import asyncio
import argparse
import logging
import time
from datetime import datetime, timedelta

from email_scraper import NonprofitEmailScraper, classify_email_type
from db import DatabaseManager

# Graceful shutdown flag
shutdown_requested = False


def signal_handler(signum, frame):
    global shutdown_requested
    shutdown_requested = True
    print("\n[SHUTDOWN] Signal received. Finishing current batch...")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def setup_logging(log_file: str = None):
    """Configure logging to console and optional file."""
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        handlers=handlers,
    )
    return logging.getLogger('nonprofit_scraper')


async def cmd_scrape_emails(args, logger):
    """Scrape a single batch of nonprofit websites."""
    db = DatabaseManager()
    try:
        # Reset any stuck in_progress rows from previous crashed runs
        reset_count = db.reset_stuck_in_progress(hours=2)
        if reset_count:
            logger.info(f"Reset {reset_count} stuck in_progress rows from previous run")

        # Fetch prospects
        logger.info(f"Fetching up to {args.limit} prospects to scrape...")
        prospects = db.get_prospects_to_scrape(limit=args.limit)
        if not prospects:
            logger.info("No prospects available to scrape.")
            return

        logger.info(f"Got {len(prospects)} prospects. Starting scrape (concurrency={args.concurrency})...")

        # Mark as in-progress
        eins = [p['ein'] for p in prospects]
        db.mark_scrape_started(eins)

        # Scrape in batches
        scraper = NonprofitEmailScraper(
            concurrency=args.concurrency,
            timeout=args.timeout,
        )

        batch_size = args.batch_size
        total_emails = 0
        total_processed = 0
        total_with_email = 0

        for batch_start in range(0, len(prospects), batch_size):
            if shutdown_requested:
                logger.info("[SHUTDOWN] Stopping before next batch.")
                break

            batch = prospects[batch_start:batch_start + batch_size]
            batch_num = batch_start // batch_size + 1
            total_batches = (len(prospects) + batch_size - 1) // batch_size

            logger.info(f"Batch {batch_num}/{total_batches} ({len(batch)} sites)...")

            def progress_cb(done, total, result):
                nonlocal total_emails, total_processed, total_with_email
                total_processed += 1
                email_count = len(result.emails)
                total_emails += email_count
                if email_count > 0:
                    total_with_email += 1
                if total_processed % 100 == 0:
                    rate = total_with_email / total_processed * 100 if total_processed else 0
                    logger.info(
                        f"  Progress: {total_processed}/{len(prospects)} | "
                        f"Sites w/email: {total_with_email} ({rate:.1f}%) | "
                        f"Emails: {total_emails}"
                    )

            results = await scraper.scrape_batch(batch, progress_callback=progress_cb)

            # Save to database
            db.save_batch_results(results)

            # Batch summary
            batch_emails = sum(len(r.emails) for r in results)
            batch_found = sum(1 for r in results if r.emails)
            status_counts = {}
            for r in results:
                status_counts[r.status] = status_counts.get(r.status, 0) + 1
            logger.info(
                f"  Batch {batch_num} done: {batch_found}/{len(batch)} sites had emails "
                f"({batch_emails} total). Statuses: {status_counts}"
            )

        # Final summary
        find_rate = total_with_email / total_processed * 100 if total_processed else 0
        logger.info(f"\n{'='*60}")
        logger.info(f"SCRAPE COMPLETE")
        logger.info(f"  Processed: {total_processed}")
        logger.info(f"  Sites with email: {total_with_email} ({find_rate:.1f}%)")
        logger.info(f"  Total emails: {total_emails}")
        logger.info(f"  Avg per site: {total_emails / total_with_email:.1f}" if total_with_email else "")
        logger.info(f"{'='*60}")

    finally:
        db.close()


async def cmd_run_overnight(args, logger):
    """Continuous scraping with configurable max runtime."""
    start_time = time.time()
    max_seconds = args.max_hours * 3600
    cycle = 0
    grand_total_processed = 0
    grand_total_emails = 0

    logger.info(f"Starting overnight run (max {args.max_hours}h, concurrency={args.concurrency})")

    db = DatabaseManager()
    try:
        # Reset any stuck in_progress rows from previous crashed runs
        reset_count = db.reset_stuck_in_progress(hours=4)
        if reset_count:
            logger.info(f"Reset {reset_count} stuck in_progress rows from previous run")

        while not shutdown_requested:
            elapsed = time.time() - start_time
            if elapsed >= max_seconds:
                logger.info(f"Max runtime ({args.max_hours}h) reached. Stopping.")
                break

            remaining_hours = (max_seconds - elapsed) / 3600
            cycle += 1
            logger.info(f"\n--- Cycle {cycle} | {remaining_hours:.1f}h remaining ---")

            # Fetch next batch
            prospects = db.get_prospects_to_scrape(limit=args.batch_size)
            if not prospects:
                logger.info("No more prospects to scrape. Done!")
                break

            logger.info(f"Scraping {len(prospects)} sites...")
            eins = [p['ein'] for p in prospects]
            db.mark_scrape_started(eins)

            scraper = NonprofitEmailScraper(
                concurrency=args.concurrency,
                timeout=args.timeout,
            )

            cycle_emails = 0

            def progress_cb(done, total, result):
                nonlocal cycle_emails
                cycle_emails += len(result.emails)

            results = await scraper.scrape_batch(prospects, progress_callback=progress_cb)
            db.save_batch_results(results)

            cycle_found = sum(1 for r in results if r.emails)
            grand_total_processed += len(results)
            grand_total_emails += cycle_emails

            rate = grand_total_emails / grand_total_processed * 100 if grand_total_processed else 0
            logger.info(
                f"Cycle {cycle}: {cycle_found}/{len(results)} sites had emails "
                f"({cycle_emails} emails). Cumulative: {grand_total_processed} processed, "
                f"{grand_total_emails} emails ({rate:.1f}%)"
            )

            # Brief pause between cycles
            if not shutdown_requested:
                await asyncio.sleep(2)

    except Exception as e:
        logger.error(f"Overnight run error: {e}", exc_info=True)
    finally:
        # Post-scrape cleanup: clean junk, validate MX for new domains
        logger.info("\n--- Post-scrape cleanup ---")
        try:
            dupes = db.get_cross_org_duplicates(min_orgs=3)
            if dupes:
                total_junk = sum(d['row_count'] for d in dupes)
                deleted = db.delete_cross_org_duplicates(min_orgs=3)
                logger.info(f"Cleaned {deleted} cross-org junk email rows ({len(dupes)} emails)")
            else:
                logger.info("No cross-org junk found")

            unvalidated = db.get_unvalidated_domains()
            if unvalidated:
                logger.info(f"Validating MX for {len(unvalidated)} new domains...")
                try:
                    import dns.asyncresolver
                    import dns.resolver
                    semaphore = asyncio.Semaphore(50)
                    resolver = dns.asyncresolver.Resolver()
                    resolver.timeout = 5
                    resolver.lifetime = 10

                    async def check_mx(domain):
                        async with semaphore:
                            try:
                                await resolver.resolve(domain, 'MX')
                                return (True, domain)
                            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
                                    dns.resolver.NoNameservers, dns.resolver.LifetimeTimeout):
                                return (False, domain)
                            except Exception:
                                return (False, domain)

                    tasks = [check_mx(d) for d in unvalidated]
                    mx_results = await asyncio.gather(*tasks)
                    db.update_mx_validation(list(mx_results))
                    valid = sum(1 for r in mx_results if r[0])
                    logger.info(f"MX validation: {valid} valid, {len(mx_results) - valid} invalid")
                except ImportError:
                    logger.warning("dnspython not installed, skipping MX validation")
            else:
                logger.info("No new domains to validate")
        except Exception as e:
            logger.error(f"Post-scrape cleanup error: {e}", exc_info=True)

        db.close()
        elapsed_h = (time.time() - start_time) / 3600
        logger.info(f"\nOvernight run finished after {elapsed_h:.1f}h")
        logger.info(f"Total: {grand_total_processed} sites, {grand_total_emails} emails")
        if grand_total_processed:
            logger.info(f"Find rate: {grand_total_emails / grand_total_processed * 100:.1f}%")


def cmd_clean(args, logger):
    """Remove junk emails: cross-org duplicates appearing in 3+ distinct orgs."""
    db = DatabaseManager()
    try:
        dupes = db.get_cross_org_duplicates(min_orgs=args.min_orgs)
        if not dupes:
            logger.info("No cross-org duplicate emails found.")
            return

        total_rows = sum(d['row_count'] for d in dupes)
        logger.info(f"Found {len(dupes)} emails appearing in {args.min_orgs}+ orgs ({total_rows} total rows)")
        print(f"\n{'Email':<45} {'Orgs':>5} {'Rows':>6}")
        print(f"{'-'*45} {'-'*5} {'-'*6}")
        for d in dupes[:30]:
            print(f"{d['email']:<45} {d['org_count']:>5} {d['row_count']:>6}")
        if len(dupes) > 30:
            print(f"  ... and {len(dupes) - 30} more")

        if args.execute:
            deleted = db.delete_cross_org_duplicates(min_orgs=args.min_orgs)
            logger.info(f"Deleted {deleted} junk email rows.")
        else:
            print(f"\nDry run. Use --execute to delete {total_rows} rows.")
    finally:
        db.close()


def cmd_classify(args, logger):
    """Classify all emails by type (junk, role, generic, personal)."""
    db = DatabaseManager()
    try:
        emails = db.get_unclassified_emails()
        if not emails:
            logger.info("No unclassified emails found.")
            return

        logger.info(f"Classifying {len(emails)} emails...")
        updates = []
        counts = {}
        for row in emails:
            email_type = classify_email_type(row['email'])
            updates.append((email_type, row['id']))
            counts[email_type] = counts.get(email_type, 0) + 1

        logger.info(f"Classification results: {counts}")

        if args.execute:
            batch_size = 5000
            for i in range(0, len(updates), batch_size):
                db.update_email_types(updates[i:i + batch_size])
            logger.info(f"Updated {len(updates)} emails.")
        else:
            print(f"\nDry run. Use --execute to update {len(updates)} emails.")
    finally:
        db.close()


async def cmd_validate_mx(args, logger):
    """Validate MX records for all unvalidated email domains."""
    try:
        import dns.asyncresolver
        import dns.resolver
    except ImportError:
        logger.error("dnspython not installed. Run: pip3 install dnspython")
        return

    db = DatabaseManager()
    try:
        domains = db.get_unvalidated_domains()
        if not domains:
            logger.info("No unvalidated domains found.")
            return

        logger.info(f"Validating MX records for {len(domains)} domains (concurrency={args.concurrency})...")

        semaphore = asyncio.Semaphore(args.concurrency)
        resolver = dns.asyncresolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 10

        async def check_mx(domain: str) -> tuple[bool, str]:
            async with semaphore:
                try:
                    await resolver.resolve(domain, 'MX')
                    return (True, domain)
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
                        dns.resolver.NoNameservers, dns.resolver.LifetimeTimeout):
                    return (False, domain)
                except Exception:
                    return (False, domain)

        tasks = [check_mx(d) for d in domains]
        results = []
        valid_count = 0
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            results.append(result)
            if result[0]:
                valid_count += 1
            if (i + 1) % 500 == 0:
                logger.info(f"  Progress: {i + 1}/{len(domains)} domains checked, {valid_count} valid")

        # Batch update
        batch_size = 5000
        for i in range(0, len(results), batch_size):
            db.update_mx_validation(results[i:i + batch_size])

        invalid_count = len(results) - valid_count
        logger.info(f"MX validation complete: {valid_count} valid, {invalid_count} invalid out of {len(results)} domains")
    finally:
        db.close()


def cmd_fix_existing(args, logger):
    """Fix existing emails: delete junk, strip @www., reclassify types."""
    db = DatabaseManager()
    try:
        counts = db.fix_existing_emails(dry_run=not args.execute)
        mode = "EXECUTED" if args.execute else "DRY RUN"
        logger.info(f"\n[{mode}] Fix existing emails:")
        logger.info(f"  Junk emails to delete:  {counts['junk_deleted']:>8,}")
        logger.info(f"  @www. emails to fix:    {counts['www_fixed']:>8,}")
        logger.info(f"  Types to reclassify:    {counts['types_reclassified']:>8,}")
        if not args.execute:
            print(f"\nDry run. Use --execute to apply fixes.")
    finally:
        db.close()


def cmd_rescrape(args, logger):
    """Reset not_found sites for re-scraping."""
    db = DatabaseManager()
    try:
        count = db.reset_not_found_for_rescrape(dry_run=not args.execute)
        mode = "EXECUTED" if args.execute else "DRY RUN"
        logger.info(f"\n[{mode}] Rescrape not_found sites:")
        logger.info(f"  Sites to reset:  {count:>8,}")
        if not args.execute:
            print(f"\nDry run. Use --execute to reset {count:,} sites for re-scraping.")
        else:
            logger.info(f"  Reset {count:,} sites. Run scrape-emails to process them.")
    finally:
        db.close()


def cmd_status(args, logger):
    """Show pipeline progress statistics."""
    db = DatabaseManager()
    try:
        stats = db.get_stats()

        print(f"\n{'='*60}")
        print(f"  NONPROFIT EMAIL SCRAPER - Pipeline Status")
        print(f"{'='*60}\n")

        total = stats['total_prospects']
        breakdown = stats['status_breakdown']
        pending = breakdown.get('pending', 0)
        completed = breakdown.get('completed', 0) + breakdown.get('not_found', 0)
        in_progress = breakdown.get('in_progress', 0)
        failed = sum(v for k, v in breakdown.items() if k not in ('pending', 'completed', 'not_found', 'in_progress'))

        pct = completed / total * 100 if total else 0
        print(f"  Prospects:     {total:>10,}")
        print(f"  Scraped:       {completed:>10,}  ({pct:.1f}%)")
        print(f"  Pending:       {pending:>10,}")
        if in_progress:
            print(f"  In Progress:   {in_progress:>10,}")
        if failed:
            print(f"  Failed:        {failed:>10,}")
        print()

        print(f"  Status breakdown:")
        for status, count in sorted(breakdown.items(), key=lambda x: -x[1]):
            print(f"    {status:<20} {count:>10,}")
        print()

        print(f"  Emails found:  {stats['emails_found']:>10,}")
        print(f"  Orgs w/email:  {stats['eins_with_email']:>10,}")
        print(f"  Avg per org:   {stats['avg_emails_per_org']:>10}")
        print(f"  Pages fetched: {stats['pages_fetched']:>10,}")
        print()

        if stats['confidence_distribution']:
            print(f"  Confidence distribution:")
            for tier, count in sorted(stats['confidence_distribution'].items()):
                print(f"    {tier:<20} {count:>10,}")
            print()

        if stats.get('email_type_distribution'):
            print(f"  Email type classification:")
            for etype, count in sorted(stats['email_type_distribution'].items(), key=lambda x: -x[1]):
                print(f"    {etype:<20} {count:>10,}")
            print()

        if stats.get('mx_validation'):
            print(f"  MX validation:")
            for status, count in sorted(stats['mx_validation'].items(), key=lambda x: -x[1]):
                print(f"    {status:<20} {count:>10,}")

        print(f"\n{'='*60}\n")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description='Nonprofit Email Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # scrape-emails
    p_scrape = subparsers.add_parser('scrape-emails', help='Scrape a batch of websites')
    p_scrape.add_argument('--limit', type=int, default=1000, help='Max sites to scrape (default: 1000)')
    p_scrape.add_argument('--concurrency', type=int, default=10, help='Concurrent requests (default: 10)')
    p_scrape.add_argument('--timeout', type=int, default=15, help='Per-page timeout in seconds (default: 15)')
    p_scrape.add_argument('--batch-size', type=int, default=50, help='Batch size for progress (default: 50)')
    p_scrape.add_argument('--log-file', type=str, default=None, help='Log to file')

    # run-overnight
    p_overnight = subparsers.add_parser('run-overnight', help='Continuous overnight scraping')
    p_overnight.add_argument('--max-hours', type=float, default=8, help='Max runtime in hours (default: 8)')
    p_overnight.add_argument('--concurrency', type=int, default=10, help='Concurrent requests (default: 10)')
    p_overnight.add_argument('--timeout', type=int, default=15, help='Per-page timeout in seconds (default: 15)')
    p_overnight.add_argument('--batch-size', type=int, default=500, help='Sites per cycle (default: 500)')
    p_overnight.add_argument('--log-file', type=str, default=None, help='Log to file (auto-generated if not set)')

    # status
    subparsers.add_parser('status', help='Show pipeline progress')

    # clean
    p_clean = subparsers.add_parser('clean', help='Remove junk emails (cross-org duplicates)')
    p_clean.add_argument('--execute', action='store_true', help='Actually delete (default: dry run)')
    p_clean.add_argument('--min-orgs', type=int, default=3, help='Min orgs for an email to be junk (default: 3)')

    # classify
    p_classify = subparsers.add_parser('classify', help='Classify emails by type')
    p_classify.add_argument('--execute', action='store_true', help='Actually update (default: dry run)')

    # validate-mx
    p_mx = subparsers.add_parser('validate-mx', help='Validate MX records for email domains')
    p_mx.add_argument('--concurrency', type=int, default=50, help='Concurrent DNS lookups (default: 50)')

    # fix-existing
    p_fix = subparsers.add_parser('fix-existing', help='Fix existing emails (junk, @www., reclassify)')
    p_fix.add_argument('--execute', action='store_true', help='Actually apply fixes (default: dry run)')

    # rescrape
    p_rescrape = subparsers.add_parser('rescrape', help='Reset not_found sites for re-scraping')
    p_rescrape.add_argument('--execute', action='store_true', help='Actually reset (default: dry run)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Auto-generate log file for overnight runs
    if args.command == 'run-overnight' and not args.log_file:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.log_file = f'overnight_{ts}.log'

    logger = setup_logging(getattr(args, 'log_file', None))

    if args.command == 'scrape-emails':
        asyncio.run(cmd_scrape_emails(args, logger))
    elif args.command == 'run-overnight':
        asyncio.run(cmd_run_overnight(args, logger))
    elif args.command == 'status':
        cmd_status(args, logger)
    elif args.command == 'clean':
        cmd_clean(args, logger)
    elif args.command == 'classify':
        cmd_classify(args, logger)
    elif args.command == 'validate-mx':
        asyncio.run(cmd_validate_mx(args, logger))
    elif args.command == 'fix-existing':
        cmd_fix_existing(args, logger)
    elif args.command == 'rescrape':
        cmd_rescrape(args, logger)


if __name__ == '__main__':
    main()
