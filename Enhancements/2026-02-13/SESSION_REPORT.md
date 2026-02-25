# Session Report: 2026-02-13

## Overview

Six projects: Website scraping pipeline implementation (build + test), Enhancement folder organization, government funding cuts knowledge base, email system documentation, dual-format workflow (md+docx), and email scraper deep analysis.

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

## Project 3: Government Funding Cuts Knowledge Base

**Goal:** Build a comprehensive knowledge base documenting 2025-2026 government funding cuts to nonprofits, establish database methodology for identifying impacted organizations, and create a Phase 2 roadmap for org-level matching.

### What Was Done

Parallel research and database analysis:
- **Web research agent:** Comprehensive research across 10 sectors on executive orders, agency actions, program cuts, foundation responses, and key statistics
- **Database agent:** 8+ SQL queries analyzing government-dependent nonprofits, NTEE sector mapping, foundation capacity, and vulnerability cross-references

### Key Findings

| Metric | Value |
|--------|-------|
| Nonprofits reporting government grants (2023) | 57,448 |
| Total government grants reported (2023) | $97.9B |
| Orgs 50%+ government-dependent | 35,083 |
| Highly vulnerable orgs (50%+ dependent, <3 foundation grants) | 26,257 |
| At-risk government funding | $124.7B |
| Foundation giving capacity (2022-2024, all sectors) | $108.9B |
| Most dependent sector | Crime/Legal (52% avg) |
| Largest dollar exposure | Education ($45.4B in gov grants) |

### Document Structure (54 KB, 12 sections)

**Part 1 - What Happened:** Executive summary, timeline (30+ events Jan 2025 - Feb 2026), policy framework table (7 EOs/laws), 10 sector profiles with programs, amounts, statuses, impact severity, and Phase 2 identification strategies.

**Part 2 - Database Methodology:** Government grants field analysis, dependency distribution, NTEE coverage (47% via dim_recipients), 4 tested SQL query templates (sector filter, vulnerability score, foundation capacity, cross-reference), data gaps analysis.

**Part 3 - Foundation Landscape:** Foundation responses (Meet the Moment pledge, emergency funds, individual actions), capacity by sector with supply vs. demand gap analysis. Biggest gaps: Housing (4.5x), Healthcare (3.6x), Employment (3.2x).

**Part 4 - Phase 2 Roadmap:** 5-step methodology, data pipeline spec, expected per-org output format, enrichment needs (NTEE from BMF, USAspending.gov integration).

### Key Files
- `Enhancements/2026-02-13/PROMPT_2026-02-13.1_government_funding_cuts_research.md`
- `Enhancements/2026-02-13/REPORT_2026-02-13.1_government_funding_cuts_knowledge_base.md` (main deliverable)
- `Enhancements/2026-02-13/REPORT_2026-02-13.1_government_funding_cuts_knowledge_base.docx`
- `Enhancements/2026-02-13/REPORT_2026-02-13.1_federal_funding_cuts_nonprofits.md` (intermediate web research)

---

## Project 4: Email System Documentation (Prompt .2)

**Goal:** Write a comprehensive Word document explaining the full email discovery pipeline step-by-step.

### What Was Done

Created an ~18-page Word document covering the entire email pipeline end-to-end, written in plain language with "why we're doing this" explanations for each step.

**Document covers:**
- **Phase A (Finding Websites):** How we clean IRS-filed URLs (53% are junk), validate them with HTTP requests (64% alive), and search DuckDuckGo for missing ones
- **Phase B (Scraping for Emails):** How we fetch multiple pages per org, extract emails using 5 methods (mailto, Cloudflare decode, JSON-LD, AT/DOT, regex), classify and score them, validate with MX records, and pick the best one
- All 7 scripts with purpose, configuration, and database interactions
- All 6 database tables + 1 materialized view with column definitions
- Confidence scoring system explained with examples
- Overnight scheduling via launchd with time windows
- End-to-end pipeline flow diagram

**Formatting:** Calibri 11pt, dark blue (#2F5496) headers, Light Grid Accent 1 table style, Consolas for pipeline diagram.

### Key Files
- `Enhancements/2026-02-13/OUTPUT_2026-02-13.2_email_system_documentation.docx`
- `Enhancements/2026-02-13/OUTPUT_2026-02-13.2_email_system_documentation.md`
- `Enhancements/2026-02-13/PROMPT_2026-02-13.2_email_system_documentation.md`
- `Enhancements/2026-02-13/REPORT_2026-02-13.2_email_system_documentation.md`

---

## Project 5: Dual Format Workflow (Prompt .3)

**Goal:** Establish a dual-format workflow so Word documents always have a parallel .md file (write .md first, convert to .docx second).

### What Was Done

1. Converted `OUTPUT_2026-02-13.2_email_system_documentation.docx` to .md using `pandoc ... -t gfm --wrap=none`
2. Added new "Word Documents" rule to CLAUDE.md establishing the dual-format workflow:
   - Write .md first (source of truth for Claude/terminals)
   - Convert to .docx second (for human reading/sharing)
   - Use `pandoc` for simple docs, `09_convert_to_docx.py` for branded reports
   - Both files share the same base name
   - Recovery: `pandoc input.docx -t gfm --wrap=none -o output.md`

### Key Files
- `Enhancements/2026-02-13/PROMPT_2026-02-13.3_dual_format_workflow.md`
- `Enhancements/2026-02-13/REPORT_2026-02-13.3_dual_format_workflow.md`
- `.claude/CLAUDE.md` (modified: added Word Document workflow rules)

---

## Project 6: Email Scraper Deep Analysis (Prompt .4)

**Goal:** Deep analysis of the email scraping pipeline, answering 7 specific questions with data-backed recommendations. Used multi-agent research (3 exploration + 3 review agents with business, technical, and data quality lenses).

### Key Findings

| Question | Answer | Action |
|----------|--------|--------|
| Q1: Accuracy | ~85-90% deliverable, 6.1% bounce rate | Coverage is the bigger gap than accuracy |
| Q2: Better validation | SMTP + catch-all detection missing | Use commercial API ($100-750), not self-hosted |
| Q3: MX changes confidence? | No (confirmed gap) | Add separate validation_status column |
| Q4: Keep all emails? | Yes (pipeline already does, view picks winner) | Add foundation-specific view |
| Q5: Additional tools | Commercial verification API, Playwright, disposable-domain list | Phase by priority |
| Q6: Saving contacts? | Yes in web_staff, plus untapped officers table (26.3M records) | Cross-reference after data cleaning |
| Q7: Foundation vs nonprofit | Need different approaches | Separate materialized views |

### Critical Discoveries
- Database tables don't exist yet (pipeline has only been smoke-tested on 10 orgs)
- Only 16GB free disk space vs 14GB needed for full HTML cache
- Officer data is 77% ALL CAPS with truncated titles
- Only 13.4% of foundations have a discoverable website (coverage gap)
- Roadmap reprioritized: Foundation contact intelligence first (product value), campaign improvements second

### Key Files
- `Enhancements/2026-02-13/OUTPUT_2026-02-13.4_email_scraper_analysis.md`
- `Enhancements/2026-02-13/PROMPT_2026-02-13.4_email_scraper_analysis.md`
- `Enhancements/2026-02-13/REPORT_2026-02-13.4_email_scraper_analysis.md`

---

*Generated by Claude Code on 2026-02-13. Updated 2026-02-16.*
