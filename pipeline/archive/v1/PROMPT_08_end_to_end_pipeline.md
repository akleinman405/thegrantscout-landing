# PROMPT_08: Phase 8 - End-to-End Pipeline

**Date:** 2025-12-27
**Phase:** 8
**Agent:** Dev Team
**Estimated Time:** 4-5 hours
**Depends On:** All previous phases (0-7) complete

---

## Objective

Create the master CLI script that orchestrates the entire pipeline from client EIN to finished Word document.

---

## Context

All components are now built:
- Scoring (Phase 2)
- Enrichment (Phase 3)
- Assembly (Phase 4)
- Scraping (Phase 5)
- AI Narratives (Phase 6)
- MD Rendering (Phase 7)

This phase ties them together into a single executable pipeline.

**Existing Asset:** `Report Templates/convert_to_docx.py` - MD to Word converter

---

## Tasks

### Task 1: Create `generate_report.py`

Main CLI entry point.

```python
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

from config.database import init_pool
from config.settings import OUTPUT_DIR, LOG_DIR
from loaders.questionnaire import load_questionnaire
from loaders.client_data import enrich_client
from scoring.scoring import GrantScorer
from enrichment import get_funder_snapshot, find_comparable_grant, find_connections
from assembly.report_data import assemble_report_data
from scraper import gather_for_report
from ai.narratives import generate_all_narratives
from rendering import ReportRenderer


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log file with timestamp
    log_file = log_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
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
        Path to generated Word document
    """
    logger = logging.getLogger('generate_report')
    
    output_dir = Path(output_dir or OUTPUT_DIR) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # --- Step 1: Load Client Data ---
    logger.info(f"Step 1/7: Loading client data for '{client_identifier}'")
    
    client = load_questionnaire(
        path=questionnaire_path,
        organization_name=client_identifier
    )
    enriched_client = enrich_client(client)
    
    logger.info(f"  Client: {enriched_client.organization_name} ({enriched_client.state})")
    
    # --- Step 2: Score Foundations ---
    logger.info("Step 2/7: Scoring foundations")
    
    scorer = GrantScorer()
    matches = scorer.score_nonprofit(
        recipient_ein=enriched_client.ein,
        top_k=50,
        exclude_prior_funders=True
    )
    
    logger.info(f"  Found {len(matches)} potential matches")
    
    # --- Step 3: Assemble Report Data ---
    logger.info("Step 3/7: Assembling report data")
    
    report_data = assemble_report_data(
        client_identifier=client_identifier,
        questionnaire_path=questionnaire_path,
        top_k=5,
        week_number=week_number
    )
    
    logger.info(f"  Assembled {len(report_data.opportunities)} opportunities")
    
    # --- Step 4: Gather Foundation Data (Scraping) ---
    if not dry_run and not skip_scrape:
        logger.info("Step 4/7: Gathering foundation data from websites")
        
        opportunities, fallbacks = gather_for_report(report_data.opportunities)
        report_data.opportunities = opportunities
        
        if fallbacks:
            logger.warning(f"  {len(fallbacks)} foundations need manual data entry")
            # Save fallback templates
            fallback_path = output_dir / f"{client_identifier}_manual_entry.md"
            save_fallback_templates(fallbacks, str(fallback_path))
    else:
        logger.info("Step 4/7: Skipping web scraping (dry-run or skip-scrape)")
    
    # --- Step 5: Generate AI Narratives ---
    logger.info("Step 5/7: Generating AI narratives")
    
    result = generate_all_narratives(
        client=report_data.client,
        opportunities=report_data.opportunities,
        use_fallbacks=dry_run
    )
    
    report_data.opportunities = result['opportunities']
    report_data.executive_summary.update(result['executive_summary'])
    
    logger.info("  Generated narratives for all opportunities")
    
    # --- Step 6: Render to Markdown ---
    logger.info("Step 6/7: Rendering markdown")
    
    renderer = ReportRenderer()
    md_content = renderer.render(report_data.to_dict())
    
    # Generate filename
    safe_name = "".join(c if c.isalnum() else "_" for c in enriched_client.organization_name)
    timestamp = datetime.now().strftime("%Y%m%d")
    md_filename = f"{safe_name}_Week{report_data.report_meta['week_number']}_{timestamp}.md"
    md_path = output_dir / md_filename
    
    with open(md_path, 'w') as f:
        f.write(md_content)
    
    logger.info(f"  Saved markdown: {md_path}")
    
    # --- Step 7: Convert to Word ---
    logger.info("Step 7/7: Converting to Word document")
    
    docx_path = convert_md_to_docx(str(md_path))
    
    logger.info(f"  Saved Word doc: {docx_path}")
    
    return docx_path


def convert_md_to_docx(md_path: str) -> str:
    """
    Convert markdown to Word document using existing script.
    
    Args:
        md_path: Path to markdown file
        
    Returns:
        Path to generated Word document
    """
    import subprocess
    
    # Path to existing converter
    converter_path = Path(__file__).parent / "Report Templates" / "convert_to_docx.py"
    
    # Run converter
    result = subprocess.run(
        ["python", str(converter_path), md_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Word conversion failed: {result.stderr}")
    
    # Assume output is same name with .docx extension
    docx_path = md_path.replace('.md', '.docx')
    return docx_path


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
    init_pool()
    
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
        print(f"✓ Report generated successfully!")
        print(f"  Output: {output_path}")
        print(f"  Time: {elapsed:.1f} seconds")
        print(f"{'='*50}\n")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        print(f"\n✗ Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Task 2: Create Error Handling Wrapper

```python
# Add to generate_report.py

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


def safe_generate_report(
    client_identifier: str,
    **kwargs
) -> tuple[str, list[str]]:
    """
    Generate report with error collection instead of failing.
    
    Returns:
        (output_path, list of warning messages)
    """
    warnings = []
    
    try:
        # ... each step wrapped in try/except
        # Collect warnings instead of failing
        pass
    except Exception as e:
        raise ReportGenerationError(f"Unrecoverable error: {e}")
    
    return output_path, warnings
```

### Task 3: Create Batch Processing

```python
# batch_generate.py

"""
Batch generate reports for multiple clients.

Usage:
    python batch_generate.py --all
    python batch_generate.py --clients "Org1,Org2,Org3"
"""

import argparse
from pathlib import Path
from datetime import datetime
from generate_report import generate_report, setup_logging
from loaders.questionnaire import get_all_clients


def batch_generate(
    client_names: list[str] = None,
    output_dir: str = None,
    dry_run: bool = False
) -> dict:
    """
    Generate reports for multiple clients.
    
    Returns:
        Dict with results: {client_name: {'status': 'success'|'failed', 'path': str, 'error': str}}
    """
    logger = setup_logging()
    
    # Get client list
    if client_names is None:
        clients = get_all_clients()
        client_names = [c.organization_name for c in clients]
    
    results = {}
    
    for i, client_name in enumerate(client_names, 1):
        logger.info(f"\n[{i}/{len(client_names)}] Processing: {client_name}")
        
        try:
            path = generate_report(
                client_identifier=client_name,
                output_dir=output_dir,
                dry_run=dry_run
            )
            results[client_name] = {'status': 'success', 'path': path}
            
        except Exception as e:
            logger.error(f"  Failed: {e}")
            results[client_name] = {'status': 'failed', 'error': str(e)}
    
    # Summary
    success = sum(1 for r in results.values() if r['status'] == 'success')
    failed = len(results) - success
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Batch complete: {success} succeeded, {failed} failed")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Batch generate reports")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help="Process all clients")
    group.add_argument('--clients', help="Comma-separated client names")
    
    parser.add_argument('--output', '-o', help="Output directory")
    parser.add_argument('--dry-run', action='store_true')
    
    args = parser.parse_args()
    
    client_names = None
    if args.clients:
        client_names = [c.strip() for c in args.clients.split(',')]
    
    batch_generate(
        client_names=client_names,
        output_dir=args.output,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
```

### Task 4: Update convert_to_docx.py Integration

Review the existing `Report Templates/convert_to_docx.py` and ensure it:
1. Accepts markdown file path as argument
2. Outputs .docx in same directory
3. Applies branding/styling
4. Returns success/failure status

If needed, create a wrapper function or modify the script.

### Task 5: Create Pipeline README

```markdown
# TheGrantScout Report Pipeline

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your credentials

# Generate a single report
python generate_report.py --client "Organization Name"

# Generate with dry-run (no AI, no scraping)
python generate_report.py --client "Organization Name" --dry-run

# Batch generate all clients
python batch_generate.py --all
```

## CLI Options

| Option | Description |
|--------|-------------|
| `--client`, `-c` | Organization name from questionnaire |
| `--ein`, `-e` | Organization EIN |
| `--questionnaire`, `-q` | Path to questionnaire CSV |
| `--output`, `-o` | Output directory |
| `--week`, `-w` | Week number for report |
| `--dry-run` | Skip AI and scraping |
| `--skip-scrape` | Skip web scraping only |
| `--verbose`, `-v` | Verbose logging |

## Output Files

Reports are saved to `outputs/reports/`:
- `{OrgName}_Week{N}_{date}.md` - Markdown source
- `{OrgName}_Week{N}_{date}.docx` - Word document
- `{OrgName}_manual_entry.md` - Manual entry needed (if scraping failed)

## Logs

Logs are saved to `outputs/logs/` with timestamps.

## Troubleshooting

### Database connection failed
Check `.env` file has correct DB credentials.

### AI generation failed
Check `ANTHROPIC_API_KEY` in `.env`.

### Word conversion failed
Ensure `convert_to_docx.py` dependencies are installed.
```

---

## Output Files

| File | Description |
|------|-------------|
| `generate_report.py` | Main CLI script |
| `batch_generate.py` | Batch processing script |
| `README.md` | Updated with usage instructions |

---

## Done Criteria

- [ ] `python generate_report.py --client "Name"` generates Word doc
- [ ] `--dry-run` works without API/scraping
- [ ] Logging captures all steps
- [ ] Errors handled gracefully
- [ ] Batch processing works
- [ ] README documents usage
- [ ] Generation time < 5 minutes per report

---

## Verification Tests

### Test 1: Dry Run
```bash
python generate_report.py --client "Sample Client" --dry-run -v
# Should complete without API calls
# Should generate .md and .docx files
```

### Test 2: Full Run
```bash
python generate_report.py --client "Sample Client" -v
# Should complete with all steps
# Check output files exist
```

### Test 3: Error Handling
```bash
python generate_report.py --client "Nonexistent Client"
# Should fail gracefully with helpful error message
```

### Test 4: Batch
```bash
python batch_generate.py --clients "Client1,Client2" --dry-run
# Should process both and report results
```

---

## Handoff

After completion:
1. Run full pipeline on 3 beta clients
2. Verify all output files generated
3. Check logs for any warnings
4. PM reviews before proceeding to PROMPT_09

---

*Next: PROMPT_09 (Testing & Validation)*
