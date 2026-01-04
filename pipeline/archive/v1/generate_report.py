#!/usr/bin/env python3
"""
TheGrantScout Report Generator

Generates grant opportunity reports for nonprofits.

Usage:
    python generate_report.py --client "Organization Name"
    python generate_report.py --ein 123456789
    python generate_report.py --client "Org Name" --dry-run
    python generate_report.py --client "Org Name" --output ./reports/
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List

# Custom exceptions
class ReportGenerationError(Exception):
    """Base exception for report generation errors."""
    pass

class ClientNotFoundError(ReportGenerationError):
    """Client not found in questionnaire."""
    pass

class ScoringError(ReportGenerationError):
    """Error during foundation scoring."""
    pass

class EnrichmentError(ReportGenerationError):
    """Error during data enrichment."""
    pass

class RenderingError(ReportGenerationError):
    """Error during markdown rendering."""
    pass


def setup_logging(verbose: bool = False, log_dir: str = None) -> logging.Logger:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO

    # Create logs directory
    log_path = Path(log_dir or "outputs/logs")
    log_path.mkdir(parents=True, exist_ok=True)

    # Log file with timestamp
    log_file = log_path / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger('generate_report')


def generate_report(
    client_identifier: str,
    questionnaire_path: str = None,
    output_dir: str = None,
    dry_run: bool = False,
    skip_scrape: bool = False,
    week_number: int = None
) -> str:
    """
    Generate complete grant report for a client.

    Args:
        client_identifier: Organization name or EIN
        questionnaire_path: Path to questionnaire CSV
        output_dir: Output directory (default: outputs/reports/)
        dry_run: If True, skip AI and scraping (use fallbacks)
        skip_scrape: If True, skip web scraping only
        week_number: Week number for report

    Returns:
        Path to generated markdown file
    """
    logger = logging.getLogger('generate_report')

    # Import here to allow CLI to show help without loading everything
    from config.database import init_pool
    from assembly import assemble_report_data
    from scraper import gather_for_report, save_fallbacks_to_markdown
    from ai import generate_all_narratives
    from rendering import ReportRenderer

    # Initialize database
    init_pool()

    output_path = Path(output_dir or "outputs") / "reports"
    output_path.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Assemble Report Data ---
    logger.info(f"Step 1/5: Assembling report data for '{client_identifier}'")

    try:
        report_data = assemble_report_data(
            client_identifier=client_identifier,
            questionnaire_path=questionnaire_path,
            top_k=5,
            week_number=week_number
        )
    except ValueError as e:
        raise ClientNotFoundError(str(e))

    logger.info(f"  Client: {report_data.client['organization_name']} ({report_data.client.get('state', 'N/A')})")
    logger.info(f"  Assembled {len(report_data.opportunities)} opportunities")

    # --- Step 2: Gather Foundation Data (Scraping) ---
    if not dry_run and not skip_scrape:
        logger.info("Step 2/5: Gathering foundation data from websites")

        opp_dicts = [opp.to_dict() for opp in report_data.opportunities]
        updated_opps, fallbacks = gather_for_report(
            opp_dicts,
            client_context=report_data.client
        )

        # Update opportunities with scraped data
        for i, opp_dict in enumerate(updated_opps):
            for key in ['deadline', 'portal_url', 'contact_name', 'contact_email',
                        'contact_phone', 'application_requirements']:
                if opp_dict.get(key):
                    setattr(report_data.opportunities[i], key, opp_dict[key])

        if fallbacks:
            logger.warning(f"  {len(fallbacks)} foundations need manual data entry")
            fallback_file = output_path / f"{client_identifier.replace(' ', '_')}_manual_entry.md"
            save_fallbacks_to_markdown(fallbacks, str(fallback_file))
    else:
        logger.info("Step 2/5: Skipping web scraping (dry-run or skip-scrape)")

    # --- Step 3: Generate AI Narratives ---
    logger.info("Step 3/5: Generating AI narratives")

    opp_dicts = [opp.to_dict() for opp in report_data.opportunities]
    result = generate_all_narratives(
        client=report_data.client,
        opportunities=opp_dicts,
        use_fallbacks=dry_run
    )

    # Update opportunities with narratives
    for i, opp_dict in enumerate(result['opportunities']):
        for key in ['why_this_fits', 'positioning_strategy', 'next_steps']:
            if opp_dict.get(key):
                setattr(report_data.opportunities[i], key, opp_dict[key])

    # Update executive summary
    report_data.executive_summary.update(result['executive_summary'])

    logger.info("  Generated narratives for all opportunities")

    # --- Step 4: Render to Markdown ---
    logger.info("Step 4/5: Rendering markdown")

    renderer = ReportRenderer()
    md_content = renderer.render(report_data.to_dict())

    # Generate filename
    safe_name = "".join(c if c.isalnum() else "_" for c in report_data.client['organization_name'])
    timestamp = datetime.now().strftime("%Y%m%d")
    md_filename = f"{safe_name}_Week{report_data.report_meta['week_number']}_{timestamp}.md"
    md_path = output_path / md_filename

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    logger.info(f"  Saved markdown: {md_path}")

    # --- Step 5: Save JSON data ---
    logger.info("Step 5/5: Saving JSON data")

    json_path = output_path / md_filename.replace('.md', '.json')
    report_data.to_json(str(json_path))
    logger.info(f"  Saved JSON: {json_path}")

    return str(md_path)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate grant opportunity reports for nonprofits"
    )

    # Client identification (one required)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--client', '-c',
        help="Organization name from questionnaire"
    )
    group.add_argument(
        '--ein', '-e',
        help="Organization EIN"
    )

    # Optional arguments
    parser.add_argument(
        '--questionnaire', '-q',
        help="Path to questionnaire CSV file"
    )
    parser.add_argument(
        '--output', '-o',
        help="Output directory"
    )
    parser.add_argument(
        '--week', '-w',
        type=int,
        help="Week number for report"
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

    # Setup
    logger = setup_logging(args.verbose)

    # Determine client identifier
    client_id = args.client or args.ein

    logger.info(f"Starting report generation for: {client_id}")
    start_time = datetime.now()

    try:
        output_path = generate_report(
            client_identifier=client_id,
            questionnaire_path=args.questionnaire,
            output_dir=args.output,
            dry_run=args.dry_run,
            skip_scrape=args.skip_scrape,
            week_number=args.week
        )

        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"\n{'='*50}")
        print(f"Report generated successfully!")
        print(f"  Output: {output_path}")
        print(f"  Time: {elapsed:.1f} seconds")
        print(f"{'='*50}\n")

        sys.exit(0)

    except ClientNotFoundError as e:
        logger.error(f"Client not found: {e}")
        print(f"\nClient not found: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        print(f"\nFailed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
