# Session Report: 2026-02-13

## Overview

Two projects: Website scraping pipeline implementation (build + test), and Enhancement folder organization.

---

## Project 1: Website Scraping Pipeline

**Goal:** Build a 4-stage pipeline to scrape ~242K validated org websites and extract emails, staff names/titles, and metadata.

### How Org Emails Are Discovered

The website scraping pipeline has 4 stages, run sequentially after the URL enrichment pipeline (scripts 01-03) has identified and validated website URLs:

#### Step 1: Fetch Website Pages (`04_fetch_website_pages.py`)
- Input: `org_url_enrichment` table — orgs with `url_validated = TRUE`
- Fetches homepage + up to 4 internal pages per org (contact, about, team, leadership, grants)
- 25 async connections via httpx, per-domain rate limiting (1 req/sec/domain)
- Respects robots.txt (cached per domain)
- Stores HTML as gzip-compressed JSON on disk (~5:1 compression)
- Checkpoint/resume via `scrape_status` tracking column
- Time window enforcement: weekdays 10pm-9am, weekends all day
- Graceful SIGINT shutdown with buffer flushing
- Tiered prioritization: open foundations (by assets) -> other foundations -> nonprofits

#### Step 2: Extract Website Data (`05_extract_website_data.py`)
- CPU-bound HTML parser, no network I/O
- **5 email extraction methods** (priority order):
  1. **mailto:** links (highest confidence — intentionally published)
  2. **Cloudflare data-cfemail** (XOR cipher decode)
  3. **JSON-LD structured data** (Organization, NGO, contactPoint)
  4. **AT/DOT obfuscation** (requires bracket delimiters: `[at]`, `(dot)`)
  5. **Regex scan** (broadest, lowest confidence)
- **Email classification:** general (info@, contact@) / role (grants@, development@) / person (first.last@)
- **Confidence scoring (0.00-1.00):** domain match (+0.40), mailto (+0.10), contact page (+0.15), person type (+0.10), non-matching domain (-0.30)
- Also extracts: staff names/titles, mission text, social media URLs, phone numbers, physical address, CMS detection, Cloudflare detection

#### Step 3: Validate Emails (`06_validate_emails.py`)
- Syntax check via email-validator library (fallback to regex)
- MX record validation via dnspython async DNS lookups
- 50 concurrent DNS lookups, domain-level caching
- Batch commits every 500 emails

#### Step 4: Materialize Best Email (`07_materialize_best_email.py`)
- Refreshes `web_best_email` materialized view (CONCURRENTLY when data exists)
- Ranking: domain match -> MX validity -> email type (person > role > general) -> confidence
- Optional backfill to `grantscout_campaign.nonprofit_prospects` and `foundation_prospects`

### Database Schema Created

| Table/View | Purpose |
|------------|---------|
| `web_pages` | Page metadata (HTML on disk in gzip cache) |
| `web_emails` | All extracted emails with classification + confidence |
| `web_org_metadata` | Mission, social links, phone, CMS, Cloudflare detection |
| `web_staff` | Staff names, titles, types from team/leadership pages |
| `web_best_email` (mat. view) | Best email per org, ranked by domain match + type + confidence |
| `org_url_enrichment` (5 new columns) | scrape_status, pages_fetched, started_at, completed_at, error |

### Smoke Test Results (5 Foundations)
Tested on Gates, Ford, MacArthur, Lilly Endowment, Hewlett:
- **Fetch:** 5/5 orgs, 21 pages, 13.7s, 0 failures
- **Extract:** 8 real emails, 100% org coverage, 5 staff found
- **Validate:** 8/8 syntax valid, 8/8 MX valid
- **Materialize:** 4 best emails (correctly excluded Lilly's non-matching domain)

### Bug Fix: AT/DOT False Positives
- **Issue:** AT/DOT regex matched within English words ("foundation" -> `found@ion.to`)
- **Result:** 48 false positive emails out of 56 total
- **Fix:** Required bracket delimiters around "at" and "dot" (changed from optional to required)
- **After fix:** 56 emails -> 8 clean emails (0 false positives)

### Overnight Scheduler
- `run_scraper.sh` — orchestrates 04->05->06->07 with `caffeinate -i` and per-stage logging
- `com.thegrantscout.scraper.plist` — launchd schedule (weekdays 10pm, weekends midnight)
- Estimated runtime: ~8-10 overnight sessions for all 242K orgs

### Key Files
- `1. Database/2. Enrich Database/2. URL, NTEE, and Phone Enrichment/04_fetch_website_pages.py`
- `1. Database/2. Enrich Database/2. URL, NTEE, and Phone Enrichment/05_extract_website_data.py`
- `1. Database/2. Enrich Database/2. URL, NTEE, and Phone Enrichment/06_validate_emails.py`
- `1. Database/2. Enrich Database/2. URL, NTEE, and Phone Enrichment/07_materialize_best_email.py`
- `1. Database/2. Enrich Database/2. URL, NTEE, and Phone Enrichment/run_scraper.sh`
- `~/Library/LaunchAgents/com.thegrantscout.scraper.plist`
- `1. Database/2. Enrich Database/2. URL, NTEE, and Phone Enrichment/REPORT_2026-02-13.1_website_scraping_pipeline.md`

---

## Project 2: Enhancement Folder Organization

**Goal:** Organize Enhancement folders for Feb 9-13 work sessions, clean up duplicate sales-marketing folder.

### What Was Done
- Merged duplicate `6. Business/sales-marketing/` folder into canonical `6. Business/3. sales-marketing/`
  - Moved 4 unique files from duplicate to canonical location
  - Merged .env files (added KV Cloudflare credentials from duplicate)
  - Deleted duplicate folder
- Created Enhancement day folders: `2026-02-09/`, `2026-02-10/`, `2026-02-11/`, `2026-02-13/`
- Wrote SESSION_REPORT.md for each day explaining what was built and how the systems work

### Key Files
- `Enhancements/2026-02-09/SESSION_REPORT.md` — Email infrastructure + DB schema reorganization
- `Enhancements/2026-02-10/SESSION_REPORT.md` — Gmail filters + email sourcing pipeline research
- `Enhancements/2026-02-11/SESSION_REPORT.md` — URL enrichment pipeline (clean, validate, search) + IRS data import
- `Enhancements/2026-02-13/SESSION_REPORT.md` — Website scraping pipeline + folder organization (this file)

---

## Full Data Pipeline Summary

The complete data pipeline from IRS filings to actionable email contacts:

```
IRS 990 Filings (raw XML)
    │
    ▼
f990_2025 schema (143K foundations, 8.3M grants, 670K nonprofits)
    │
    ▼
org_url_enrichment (813K orgs — foundations + nonprofits)
    │
    ├── 01_clean_org_urls.py → 377K real URLs (46.4%)
    ├── 02_validate_org_urls.py → 242K alive URLs (64%)
    ├── 03_search_org_urls.py → DuckDuckGo search for missing URLs
    │
    ▼
Website Scraping Pipeline
    │
    ├── 04_fetch_website_pages.py → HTML pages cached to disk
    ├── 05_extract_website_data.py → Emails, staff, metadata extracted
    ├── 06_validate_emails.py → MX record + syntax validation
    └── 07_materialize_best_email.py → Best email per org
         │
         ▼
    Campaign tables (grantscout_campaign / filtered_campaign)
         │
         ├── email_scraper.py → Additional email scraping for prospects
         ├── campaign_manager.py → Multi-sender email sending
         └── Gmail filters → Auto-sort bounces, replies, auto-replies
```

---

*Generated by Claude Code on 2026-02-13*
