# Nonprofit Email Scraper

Async web scraper that extracts contact emails from nonprofit websites for cold outreach campaigns.

## Files

| File | Purpose |
|------|---------|
| `cli.py` | CLI interface with subcommands (scrape-emails, run-overnight, classify, validate-mx, fix-existing, rescrape) |
| `db.py` | DatabaseManager class — psycopg2 operations for org_url_enrichment, web_emails, web_pages |
| `email_scraper.py` | Core async scraper with multi-pass extraction (mailto, cfemail, JSON-LD, regex), confidence scoring |

## Usage

```bash
# Scrape emails for orgs with websites but no emails yet
python3 cli.py scrape-emails --limit 100

# Run overnight (continuous batches with delays)
python3 cli.py run-overnight --batch-size 50

# Classify email types (generic, personal, role-based)
python3 cli.py classify

# Fix data quality issues (junk removal, @www. correction, reclassification)
python3 cli.py fix-existing --dry-run
```

## Data Flow

1. Reads from `f990_2025.org_url_enrichment` (orgs with `website_url` populated)
2. Scrapes contact pages asynchronously via aiohttp + BeautifulSoup
3. Writes results to `f990_2025.web_emails` and `f990_2025.web_pages`
4. Updates `scrape_status` in org_url_enrichment for tracking

## Dependencies

- aiohttp, beautifulsoup4, lxml (scraping)
- psycopg2 (database)
- dnspython (MX validation)
