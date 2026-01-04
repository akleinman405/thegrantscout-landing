#!/usr/bin/env python3
"""
Batch generate reports for multiple clients.

Usage:
    python batch_generate.py --all
    python batch_generate.py --clients "Org1,Org2,Org3"
"""

import argparse
import sys
from datetime import datetime
from typing import List, Dict, Optional

from generate_report import generate_report, setup_logging


def batch_generate(
    client_names: List[str] = None,
    output_dir: str = None,
    dry_run: bool = False,
    skip_scrape: bool = False
) -> Dict[str, Dict]:
    """
    Generate reports for multiple clients.

    Args:
        client_names: List of client names (None = all clients)
        output_dir: Output directory
        dry_run: Skip AI and scraping
        skip_scrape: Skip web scraping only

    Returns:
        Dict with results: {client_name: {'status': 'success'|'failed', 'path': str, 'error': str}}
    """
    import logging
    from loaders import get_all_clients

    logger = logging.getLogger('batch_generate')

    # Get client list
    if client_names is None:
        clients = get_all_clients()
        client_names = [c.organization_name for c in clients]

    if not client_names:
        logger.warning("No clients found to process")
        return {}

    logger.info(f"Processing {len(client_names)} clients")
    results = {}

    for i, client_name in enumerate(client_names, 1):
        logger.info(f"\n[{i}/{len(client_names)}] Processing: {client_name}")
        logger.info("-" * 40)

        try:
            path = generate_report(
                client_identifier=client_name,
                output_dir=output_dir,
                dry_run=dry_run,
                skip_scrape=skip_scrape
            )
            results[client_name] = {'status': 'success', 'path': path}
            logger.info(f"  SUCCESS: {path}")

        except Exception as e:
            logger.error(f"  FAILED: {e}")
            results[client_name] = {'status': 'failed', 'error': str(e)}

    # Summary
    success = sum(1 for r in results.values() if r['status'] == 'success')
    failed = len(results) - success

    logger.info(f"\n{'='*50}")
    logger.info(f"BATCH COMPLETE")
    logger.info(f"  Succeeded: {success}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"{'='*50}")

    # List failures
    if failed > 0:
        logger.info("\nFailed clients:")
        for name, result in results.items():
            if result['status'] == 'failed':
                logger.info(f"  - {name}: {result.get('error', 'Unknown error')}")

    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Batch generate reports for multiple clients"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--all',
        action='store_true',
        help="Process all clients from questionnaire"
    )
    group.add_argument(
        '--clients',
        help="Comma-separated client names"
    )

    parser.add_argument(
        '--output', '-o',
        help="Output directory"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Skip AI and scraping, use fallbacks"
    )
    parser.add_argument(
        '--skip-scrape',
        action='store_true',
        help="Skip web scraping only"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Verbose output"
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.verbose)
    logger.info("Starting batch report generation")

    # Parse client names
    client_names = None
    if args.clients:
        client_names = [c.strip() for c in args.clients.split(',')]

    # Initialize database
    from config.database import init_pool
    init_pool()

    start_time = datetime.now()

    # Run batch
    results = batch_generate(
        client_names=client_names,
        output_dir=args.output,
        dry_run=args.dry_run,
        skip_scrape=args.skip_scrape
    )

    elapsed = (datetime.now() - start_time).total_seconds()

    # Final summary
    success = sum(1 for r in results.values() if r['status'] == 'success')
    failed = len(results) - success

    print(f"\n{'='*50}")
    print(f"Batch complete in {elapsed:.1f} seconds")
    print(f"  Succeeded: {success}")
    print(f"  Failed: {failed}")
    print(f"{'='*50}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
