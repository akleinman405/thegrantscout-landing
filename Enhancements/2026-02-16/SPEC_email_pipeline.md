# TheGrantScout Email Pipeline: Technical Reference

**Version:** 1.0
**Date:** 2026-02-16
**Status:** Living document
**Owner:** Aleck Kleinman

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial consolidation from 6 source documents |

---

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [Phase 1: Get URLs (Scripts 01-03)](#phase-1-get-urls)
3. [Phase 2: Get Emails from Websites (Scripts 04-05)](#phase-2-get-emails-from-websites)
4. [Phase 3: Validate and Enrich (Scripts 06-07)](#phase-3-validate-and-enrich)
5. [Phase 4: Write Emails (Campaign Content)](#phase-4-write-emails)
6. [Phase 5: Send Emails (Campaign Delivery)](#phase-5-send-emails)
7. [Database Quick-Reference](#database-quick-reference)
8. [Infrastructure](#infrastructure)
9. [Known Issues and Risks](#known-issues-and-risks)
10. [Improvement Roadmap](#improvement-roadmap)

---

## Pipeline Overview

TheGrantScout's email pipeline turns 813,698 IRS 990 organization records into deliverable email contacts for two purposes: (1) foundation contact data for client grant reports (product), and (2) nonprofit prospect emails for cold outreach campaigns (sales). The pipeline has 7 Python scripts organized into 5 phases, from raw URL discovery through email delivery.

```
IRS 990 Filings (raw XML)
    |
    v
f990_2025 schema (143K foundations, 670K nonprofits, 8.3M grants)
    |
    v
org_url_enrichment (813,698 rows)
    |
    |-- Phase 1: Get URLs
    |   |-- [01] Clean URLs ---------> 377K real URLs (46.4%)
    |   |-- [02] Validate URLs ------> 308K alive (81.6% of cleaned)
    |   |-- [03] Search DuckDuckGo --> Fill gaps for orgs without URLs
    |
    |-- Phase 2: Get Emails from Websites
    |   |-- [04] Fetch pages --------> HTML cached to disk (gzip)
    |   |-- [05] Extract data -------> Emails + Staff + Metadata
    |
    |-- Phase 3: Validate and Enrich
    |   |-- [06] Validate emails ----> Syntax + MX records
    |   |-- [07] Materialize --------> Best email per org
    |
    |-- Phase 4: Write Emails
    |   |-- generate_emails.py ------> AI-generated campaign content
    |   |-- assign_variants.py ------> A/B variant assignment
    |
    |-- Phase 5: Send Emails
    |   |-- campaign_manager.py -----> Multi-sender delivery
    |   |-- send_generated_emails.py > Send from PostgreSQL queue
    |   |-- track_response.py -------> Bounce/reply monitoring
    |
    v
Campaign Tables (grantscout_campaign)
    |
    v
Email outreach to nonprofit prospects
```

---

## Phase 1: Get URLs

**Scripts:** 01, 02, 03 (+ 03b, 03c variants)
**Status:** DONE
**Schema:** f990_2025
**Central table:** org_url_enrichment (813,698 rows)

This phase discovers and validates website URLs for all organizations in the database. IRS 990 filings include an optional website field, but about 53% of entries are junk (phone numbers, "N/A", aggregator sites). Three scripts clean, validate, and fill in missing URLs.

### Script 01: Clean and Normalize URLs

**File:** `01_clean_org_urls.py`
**Purpose:** Separate real URLs from junk in raw IRS data, normalize formatting
**Speed:** ~5,000 rows/sec

What it does:

- Reads all 813K rows from org_url_enrichment where url_source is NULL
- Junk detection: 63 exact matches ("N/A", "NONE", "0", phone patterns) + 12 regex patterns
- Aggregator filter: 24 blocked domains (GuideStar, Charity Navigator, ProPublica, IRS.gov)
- Social media extraction: Facebook and LinkedIn URLs moved to separate columns
- Normalization: adds https://, lowercases domain, strips tracking params and fragments
- Sets `url_source` column to track provenance: "irs_filing", "junk_removed", "social_extracted"

**Results:**

| Category | Count | Percentage |
|----------|-------|------------|
| Real URLs (cleaned) | 377,201 | 46.4% |
| Junk removed | ~434,900 | 53.4% |
| Social media extracted | ~1,600 | 0.2% |

### Script 02: Validate URLs with HTTP Requests

**File:** `02_validate_org_urls.py`
**Purpose:** Check which cleaned URLs point to live websites
**Speed:** 50 concurrent connections, 15s timeout

What it does:

- Async HTTP HEAD requests to all 377K cleaned URLs (falls back to GET if HEAD fails)
- Classifies: alive (200-399), bot-blocked/still alive (403, 405, 429, 503), dead (DNS fail, 404, timeout)
- Captures redirect targets (final URL after all redirects)
- Checkpoint/resume via state file (can stop and restart)

**Results:**

| Category | Count | Percentage |
|----------|-------|------------|
| Alive (confirmed working) | 307,885 | 81.6% |
| Dead (site gone) | 69,316 | 18.4% |
| Pending (not yet checked) | 0 | 0% |

**Configuration:**

| Setting | Value |
|---------|-------|
| Concurrent connections | 50 |
| Timeout per request | 15 seconds |
| Max redirects | 5 |
| SSL verification | Disabled (many nonprofits have expired certs) |

### Script 03: Search for Missing URLs

**File:** `03_search_org_urls.py`
**Purpose:** Find websites for orgs that had no IRS-filed URL
**Speed:** 3 workers, 2-5s delays between requests

What it does:

- Searches DuckDuckGo for each org without a URL (org name + city + state)
- 3 parallel worker threads with rate limiting and iterative backoff
- Domain-name matching: full name, multi-word, acronym, snippet verification
- Filters 120+ aggregator/directory domains + .gov and .edu
- Only "high" confidence matches saved (medium disabled: 0% accuracy on test)

**Test results (100 foundations):**

| Metric | Value |
|--------|-------|
| URLs found | 25 (25% hit rate) |
| Confidence level | 100% high |
| False positives | 0 |

### Phase 1 Known Issues

- Aggregator URLs leaking through: cybo.com, rocketreach.co, buzzfile.com, eintaxid.com, ltddir.com survived the 24-domain blocklist
- Script 02 had overwritten `url_source` provenance for 226,645 rows (fixed, data restored)

### Phase 1 Next Steps

- Expand aggregator blocklist with the 5 domains identified above
- Consider periodic re-validation of URLs (domains expire over time)

---

## Phase 2: Get Emails from Websites

**Scripts:** 04, 05
**Status:** BUILT, smoke-tested on 5 foundations. NOT RUN AT SCALE.
**Schema:** f990_2025
**Tables:** web_pages, web_emails, web_org_metadata, web_staff (NOT YET CREATED in database)

This phase scrapes validated websites to extract email addresses, staff names/titles, and organization metadata. The scripts are fully written and tested but the database tables have not been created yet.

### Script 04: Fetch Website Pages

**File:** `04_fetch_website_pages.py`
**Purpose:** Download homepage + up to 4 internal pages per org
**Speed:** 25 concurrent async connections, 1 req/sec/domain

What it does:

- Fetches homepage, then discovers and fetches up to 4 internal pages (contact, about, team, leadership, grants)
- 25 concurrent connections via httpx (HTTP/2 support)
- Per-domain rate limiting: max 1 request per second
- Respects robots.txt (cached per domain)
- Stores HTML on disk as gzip-compressed JSON (~5:1 compression)
- Checkpoint/resume via scrape_status in database
- Time window enforcement: weekdays 10pm-9am, weekends all day
- Graceful SIGINT shutdown with buffer flushing
- Tiered prioritization: open foundations (by assets) then other foundations then nonprofits

**Page discovery patterns:**

| Page Type | URL Patterns | Link Text Patterns |
|-----------|-------------|-------------------|
| Contact | /contact, /contact-us, /get-in-touch | "Contact", "Reach Us", "Email Us" |
| About | /about, /about-us, /who-we-are | "About", "Our Story", "Our Mission" |
| Team | /team, /staff, /our-team, /people | "Team", "Staff", "Our People" |
| Leadership | /leadership, /board, /board-of-directors | "Board", "Leadership", "Officers" |
| Grants | /grants, /apply, /rfp, /funding | "Grants", "How to Apply", "Funding" |

**Scraping tiers:**

| Tier | Description | Count | Est. Runtime |
|------|-------------|-------|-------------|
| Tier 1 | Foundations open to applications (by assets) | ~12,653 | ~1 night |
| Tier 2 | Other foundations | ~130,000 | ~4 nights |
| Tier 3 | Nonprofits | ~100,000+ | ~3-4 nights |

**HTML cache:** `~/Documents/TheGrantScout/8. Data/web_cache/` organized by EIN prefix (e.g., `012/012345678.json.gz`). Estimated total size: ~14GB for all orgs.

**Database table: web_pages** (one row per page fetched)

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Auto-increment ID |
| ein | VARCHAR(20) | Organization EIN |
| url | TEXT | Page URL |
| page_type | VARCHAR(30) | homepage, contact, about, team, leadership, grants |
| http_status | SMALLINT | HTTP status code |
| html_hash | VARCHAR(64) | SHA-256 hash of HTML |
| html_size_bytes | INTEGER | Size of raw HTML |
| fetched_at | TIMESTAMP | When page was fetched |

### Script 05: Extract Emails, Staff, and Metadata

**File:** `05_extract_website_data.py` (~660 lines)
**Purpose:** Parse cached HTML to find emails, staff, and metadata
**Speed:** 200-500 orgs/sec (CPU-only, no network I/O)

**5 email extraction methods (priority order):**

1. **Mailto links** (highest confidence): `<a href="mailto:info@example.org">`
2. **Cloudflare email decode**: XOR cipher on `data-cfemail` attributes
3. **JSON-LD structured data**: schema.org Organization/NGO/NonprofitOrganization types
4. **AT/DOT obfuscation**: `info [at] example [dot] org` (bracket delimiters required)
5. **Regex scan** (broadest, lowest confidence): standard email pattern matching

**Email filtering (auto-discarded):**

- noreply@, no-reply@, donotreply@, unsubscribe@
- careers@, jobs@, hr@
- webmaster@, postmaster@, mailer-daemon@, bounce@
- Platform emails: @wix.com, @squarespace.com, @wordpress.com, @mailchimp.com
- Grant platforms: @submittable.com, @fluxx.io, @instrumentl.com
- Test/placeholder: user@domain, email@example, test@test
- Image extensions: .png, .jpg, .gif, .svg

**Email classification:**

| Type | Examples | Meaning |
|------|---------|---------|
| General | info@, contact@, hello@, admin@, office@ | Generic organizational inbox |
| Role | grants@, development@, fundraising@, programs@ | Department-specific |
| Person | jane.doe@, jsmith@ | Individual (highest value) |

**Confidence scoring (0.00-1.00):**

| Factor | Score |
|--------|-------|
| Email domain matches org website | +0.40 |
| Found via mailto link | +0.10 |
| Found via JSON-LD structured data | +0.10 |
| Found on contact or about page | +0.15 |
| Person-type email | +0.10 |
| General prefix + matching domain | +0.15 |
| Domain does NOT match website | -0.30 |

Maximum possible score: 0.80. Example: media@hewlett.org via mailto on hewlett.org's contact page scores 0.65 (domain match + mailto + contact page).

**Staff extraction:**

- Strategy 1: CSS selectors matching class names with "team", "staff", "member", "person", "bio", "profile"
- Strategy 2: Heading patterns in h2/h3/h4/strong/b tags for capitalized names, adjacent title text

| Staff Type | Detection | Examples |
|------------|-----------|---------|
| Executive | CEO, President, Executive Director, COO, CFO | Jane Doe, Executive Director |
| Board | Page type "board" or title with Board Member, Trustee, Chair | John Smith, Board Chair |
| Leadership | Director, VP, Vice President | Sarah Lee, Program Director |
| Advisory | Advisory, Advisor, Emeritus | Dr. James, Advisory Board |
| Staff | Everything else | Mike R., Program Associate |

**Metadata extraction:** Mission text, meta description, social media URLs, phone numbers, physical address, CMS platform (WordPress/Squarespace/Wix/Drupal), Cloudflare detection, JS rendering needed (React/Next.js/Vue).

**Database table: web_emails**

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Auto-increment ID |
| ein | VARCHAR(20) | Organization EIN |
| email | VARCHAR(255) | The email address |
| email_type | VARCHAR(20) | general, role, or person |
| email_domain | VARCHAR(255) | Domain part of email |
| domain_matches_website | BOOLEAN | Email domain matches org website? |
| person_name | TEXT | Person name (if person-type) |
| person_title | TEXT | Job title |
| source_url | TEXT | URL where email was found |
| source_page_type | VARCHAR(30) | homepage, contact, about, etc. |
| extraction_method | VARCHAR(30) | mailto, cfemail, json_ld, at_dot, regex |
| confidence | NUMERIC(3,2) | Confidence score 0.00-1.00 |
| syntax_valid | BOOLEAN | Email syntax is valid? |
| mx_valid | BOOLEAN | Domain has MX records? |
| validated_at | TIMESTAMP | When validation was done |

UNIQUE constraint on (ein, email): if same email found by multiple methods, highest confidence kept.

**Database table: web_org_metadata** (one row per org, PK = ein): Mission text, social links, phone, address, CMS, Cloudflare/JS flags.

**Database table: web_staff** (one row per staff member): Name, title, email, phone, staff_type, confidence.

### Phase 2 Smoke Test Results (5 Foundations)

Tested on Gates, Ford, MacArthur, Lilly Endowment, Hewlett:

| Stage | Result |
|-------|--------|
| Fetch | 5/5 orgs, 21 pages, 13.7s, 0 failures |
| Extract | 8 real emails, 100% org coverage, 5 staff found |
| Validate | 8/8 syntax valid, 8/8 MX valid |
| Materialize | 4 best emails (correctly excluded Lilly's non-matching domain) |

**Bug fixed during testing:** AT/DOT regex was matching within English words ("foundation" produced `found@ion.to`). Fixed by requiring bracket delimiters. Reduced 56 emails to 8 clean emails (0 false positives).

### Phase 2 Known Issues

- Database tables (web_pages, web_emails, web_org_metadata, web_staff) do not exist yet
- 14GB estimated cache vs 16GB free disk; must process in waves
- web_staff INSERT has no ON CONFLICT clause (duplicates on crash/restart)
- Only 13.4% of foundations have discoverable websites (19,119 of 143,184)
- Of 12,653 Tier 1 foundations, only ~6,816 (54%) have live websites
- At 15-30% email yield, web scraping will produce emails for 1,000-2,000 Tier 1 foundations (8-16%)

### Phase 2 Next Steps

1. Create the 4 database tables + materialized view
2. Fix web_staff ON CONFLICT
3. Run pipeline on Tier 1 foundations (~6,816 with live URLs), process in disk-space waves
4. Add Playwright for JS-rendered foundation sites (15-20% of sites need it)

---

## Phase 3: Validate and Enrich

**Scripts:** 06, 07
**Status:** BUILT, smoke-tested. Missing SMTP/catch-all validation.
**Schema:** f990_2025 (enrichment) bridging to grantscout_campaign (prospects)

### Script 06: Validate Emails

**File:** `06_validate_emails.py`
**Purpose:** Verify email syntax and deliverability
**Speed:** 50 concurrent DNS lookups, domain-level caching

Two validation layers:

| Layer | What It Checks | Status |
|-------|---------------|--------|
| Syntax check | RFC 5321 format via email-validator library | YES |
| MX record lookup | Domain has mail servers (async DNS via dnspython) | YES |
| Catch-all detection | Domain accepts ALL addresses | NOT BUILT |
| SMTP RCPT TO | Specific mailbox exists | NOT BUILT |

Performance: emails grouped by domain for cache efficiency. Batch commits every 500 emails.

### Script 07: Materialize Best Email

**File:** `07_materialize_best_email.py`
**Purpose:** Pick the single best email per org, optionally backfill campaign tables
**Speed:** Seconds (SQL view refresh)

**Ranking logic (in order):**

1. Domain matches website (emails on org's own domain always win)
2. MX records valid (confirmed deliverable)
3. Email type: Person > Role > General
4. Confidence score (highest wins)

Only emails with syntax_valid = TRUE and domain_matches_website = TRUE are considered.

With `--backfill` flag, copies best email into grantscout_campaign.nonprofit_prospects and foundation_prospects.

**Database view: web_best_email (materialized)**

| Column | Type | Description |
|--------|------|-------------|
| ein | VARCHAR(20) | Organization EIN (unique index) |
| email | VARCHAR(255) | Winning email address |
| email_type | VARCHAR(20) | person, role, or general |
| person_name | TEXT | Contact name |
| person_title | TEXT | Job title |
| confidence | NUMERIC(3,2) | Confidence score |
| mx_valid | BOOLEAN | MX validation result |

### Phase 3 Known Issues

- Confidence score not updated by validation (only sets mx_valid/syntax_valid booleans)
- Two different quality emails can both score 0.65 (narrow band around 0.55-0.65)
- No catch-all detection (~30-40% of nonprofit domains are catch-all)
- No commercial SMTP verification (self-hosted probing risks residential IP blacklisting)
- Need separate materialized views for foundations vs nonprofits (different email type preferences)

### Phase 3 Next Steps

1. Add validation_status column (pending/mx_valid/mx_invalid/smtp_verified/smtp_rejected/catch_all) separate from extraction confidence
2. Commercial email verification API (ZeroBounce/NeverBounce, ~$100-750 one-time for full corpus)
3. Split into foundation-specific and nonprofit-specific best-email views (foundations prefer role emails like grants@; nonprofits prefer person emails)

---

## Phase 4: Write Emails

**Scripts:** generate_emails.py, assign_variants.py, config.py
**Status:** BUILT (scripts exist, rewired to PostgreSQL on Feb 9). No emails generated yet.
**Schema:** grantscout_campaign

Campaign email generation scripts that create personalized outreach content using AI.

| Script | Purpose |
|--------|---------|
| generate_emails.py | AI-generated email content from prospect data |
| assign_variants.py | A/B variant assignment for testing |
| config.py | Campaign configuration (templates, settings) |

**Database table: generated_emails** (0 rows)

Stores AI-generated email content ready for sending.

### Phase 4 Known Issues

- No emails generated yet from new PostgreSQL-based system
- Scripts were rewired from CSV/Supabase to PostgreSQL on Feb 9; need testing with live data

### Phase 4 Next Steps

- Generate first batch using populated email data from Phases 2-3
- Test A/B variant assignment

---

## Phase 5: Send Emails

**Scripts:** campaign_manager.py, send_generated_emails.py, sender_pool.py, track_response.py
**Status:** PARTIAL. Infrastructure built, no sends from new system.
**Schema:** grantscout_campaign

### Email Infrastructure

Built on Feb 9, 2026:

- **20 email subdomains** (10 per domain) for sender rotation:
  - thegrantscout.com: ai, connect, contact, email, hello, info, insights, mail, outreach, team
  - filteredmessaging.com: same + partner
- Full email authentication per subdomain: MX records, SPF, DMARC (monitor mode), DKIM
- All 14 domain aliases added in Google Workspace Admin
- 88/88 DNS record checks passed (100%)

**Why 10 subdomains per domain:** Research showed 30 subdomains on one root domain is a red flag for ESPs. 10 per domain with 15 emails/day each = 150/day capacity per domain.

### Campaign Scripts

| Script | Purpose |
|--------|---------|
| campaign_manager.py | Multi-sender delivery with subdomain rotation, business-hours pacing (Mon-Fri 9am-7pm), 15 emails/day per sender |
| send_generated_emails.py | Send from PostgreSQL queue |
| sender_pool.py | Manage sender rotation and daily limits |
| track_response.py | Bounce and reply monitoring via Gmail API |

### Gmail Filters

Built on Feb 10, 2026. 5 filters auto-sort campaign email:

1. All Bounces: from mailer-daemon/postmaster, skip inbox
2. TGS Auto-Replies: OOO/vacation from TGS subdomains, skip inbox, mark read
3. TGS Responses: Real replies from TGS subdomains, keep in inbox
4. FM Auto-Replies: OOO from FM subdomains, skip inbox, mark read
5. FM Responses: Real replies from FM subdomains, keep in inbox

### Database Tables

| Table | Rows | Purpose |
|-------|------|---------|
| senders | 10 | Sender email accounts for rotation |
| send_log | 0 | Record of every email sent |
| responses | 0 | Bounce/reply tracking |
| sender_daily_stats | 0 | Daily send counts per sender |

### Previous Campaign Results (Nov 2025, old scraper)

| Metric | Value |
|--------|-------|
| Total Sent | 1,844 |
| Delivered | 1,731 (93.9%) |
| Bounced | 113 (6.1%) |
| Replied | 4 (0.23%) |

### Phase 5 Known Issues

- No sends from new PostgreSQL-based system yet
- Old campaign had 6.1% bounce rate (target: under 2%)
- Campaign scripts rewired from CSV/Supabase on Feb 9; need end-to-end test

### Phase 5 Next Steps

- Send test batch after Phase 2-3 populate emails
- Target under 2% bounce rate with commercial verification

---

## Database Quick-Reference

All tables across both schemas, with current row counts.

### f990_2025 Schema (IRS data + enrichment)

| Table | Rows | Purpose | Status |
|-------|------|---------|--------|
| org_url_enrichment | 813,698 | Master enrichment tracking (one row per org) | Active |
| web_pages | N/A | Fetched page metadata (HTML on disk) | NOT CREATED |
| web_emails | N/A | Extracted emails with classification + confidence | NOT CREATED |
| web_org_metadata | N/A | Website metadata (mission, social, phone, CMS) | NOT CREATED |
| web_staff | N/A | Staff names, titles, types from websites | NOT CREATED |
| web_best_email | N/A | Materialized view: best email per org | NOT CREATED |

### grantscout_campaign Schema (sales/campaign)

| Table | Rows | Purpose | Status |
|-------|------|---------|--------|
| nonprofit_prospects | 74,175 | Campaign prospect list | Active |
| foundation_prospects | 761 | Foundation prospects | Active |
| generated_emails | 0 | AI-generated campaign content | Empty |
| senders | 10 | Sender email accounts | Active |
| send_log | 0 | Email send records | Empty |
| responses | 0 | Bounce/reply tracking | Empty |
| sender_daily_stats | 0 | Daily stats per sender | Empty |
| scrape_jobs | 0 | Scraping job tracking | Empty |

### CRM Tables (grantscout_campaign)

| Table | Purpose |
|-------|---------|
| calls | Call log |
| tasks | Task tracking |
| pipeline | Sales pipeline stages |
| contact_events | Contact activity log |
| prospect_duplicates | Dedup tracking |

---

## Infrastructure

### File Locations

| Item | Location |
|------|----------|
| Pipeline scripts (01-07) | `1. Database/2. Enrich Database/2. URL, NTEE, and Phone Enrichment/` |
| Campaign scripts | `6. Business/3. sales-marketing/5. Email_Campaign/` |
| HTML cache | `~/Documents/TheGrantScout/8. Data/web_cache/` |
| Nightly logs | `...2. URL, NTEE, and Phone Enrichment/logs/` |
| Scheduler plist | `~/Library/LaunchAgents/com.thegrantscout.scraper.plist` |
| State files | Same folder as scripts (validate_state.json, search_state.json) |
| Gmail filter export | `6. Business/3. sales-marketing/5. Email_Campaign/DATA_2026-02-10_gmail_filters.xml` |

### Dependencies

| Package | Version | Used By | Purpose |
|---------|---------|---------|---------|
| httpx | 0.28.1 | Script 04 | Async HTTP client with HTTP/2 |
| beautifulsoup4 | 4.14.3 | Script 05 | HTML parsing |
| lxml | 6.0.2 | Script 05 | Fast HTML parser backend |
| email-validator | 2.3.0 | Script 06 | Email syntax validation |
| dnspython | 2.7.0 | Script 06 | Async DNS (MX record) lookups |
| psycopg2 | - | All scripts | PostgreSQL database access |
| aiohttp | - | Script 02 | Async HTTP for URL validation |
| duckduckgo-search | - | Script 03 | DuckDuckGo search API |

### Overnight Scheduler (launchd)

**Plist:** `~/Library/LaunchAgents/com.thegrantscout.scraper.plist`

| Day | Trigger Time | Effective Window |
|-----|-------------|-----------------|
| Monday-Friday | 10:00 PM | 10pm-9am (Script 04 auto-stops at 9am) |
| Saturday | 12:00 AM | All day |
| Sunday | 12:00 AM | All day |

**Orchestrator:** `run_scraper.sh` runs scripts in order: 04 (fetch) then 05 (extract) then 06 (validate) then 07 (materialize). Uses caffeinate to prevent sleep. Logs all output with timestamps. All stages run regardless of prior stage failures.

**Estimated full run:** 8-10 overnight sessions for all 308K validated orgs.

---

## Known Issues and Risks

### Critical

| Issue | Impact | Mitigation |
|-------|--------|------------|
| Database tables don't exist | Pipeline cannot run at scale | Create web_pages, web_emails, web_org_metadata, web_staff, web_best_email |
| Only 13.4% of foundations have websites | Web scraping cannot reach majority of foundations | Alternative channels needed (Candid API, LinkedIn, phone, manual research) |
| 16GB free disk, 14GB cache needed | Could fill disk during full scrape | Process in waves, delete cache between tiers |

### High

| Issue | Impact | Mitigation |
|-------|--------|------------|
| Residential IP blacklisting risk | Self-hosted SMTP probing looks like spam | Use commercial verification API or disposable VPS |
| web_staff no ON CONFLICT clause | Duplicate staff records on crash/restart | Add conflict handling |
| Aggregator URLs in pipeline | Scraping wrong sites yields wrong emails | Expand blocklist with 5 identified domains |

### Medium

| Issue | Impact | Mitigation |
|-------|--------|------------|
| caffeinate -i doesn't prevent lid-close sleep | Overnight scraping interrupted | Switch to caffeinate -s + PID lock file |
| Confidence score poorly calibrated | Different quality emails score similarly | Separate extraction confidence from validation status |
| 6.1% bounce rate (old campaign) | Sender reputation damage | Commercial verification to target under 2% |

---

## Improvement Roadmap

Prioritized by business value. Product improvements (foundation contacts for client reports) come first because they directly improve what clients pay for. Campaign improvements (nonprofit outreach emails) come second.

### Phase A: Foundation Contact Intelligence (Next Priority)

| # | Task | Effort | Why First |
|---|------|--------|-----------|
| A.1 | Create the 5 database tables | 1 hour | Nothing runs without this |
| A.2 | Fix web_staff ON CONFLICT | 30 min | Data integrity |
| A.3 | Expand aggregator blocklist | 30 min | Prevents scraping wrong sites |
| A.4 | Create foundation vs nonprofit best-email views | 1 hour | Right email ranking for each use case |
| A.5 | Run pipeline on Tier 1 foundations (~6,816 with live URLs) | Overnight | Get the data |
| A.6 | Fix run_scraper.sh reliability (caffeinate -s, PID lock) | 1 hour | Prevent overnight failures |

### Phase B: Validation and Coverage (Following Month)

| # | Task | Effort |
|---|------|--------|
| B.1 | Add validation_status column (separate from confidence) | 2 hours |
| B.2 | Add catch-all detection via VPS | 3 hours |
| B.3 | Commercial email verification API (~$100-750) | 2-3 hours |
| B.4 | Process in disk-space waves | 1 hour |
| B.5 | Playwright for JS-rendered foundation sites | 4-6 hours |

### Phase C: Officer Cross-Reference (Further Out)

| # | Task | Effort |
|---|------|--------|
| C.1 | Clean officer data (77% ALLCAPS, truncated titles, institutional names) | 4-6 hours |
| C.2 | Fuzzy match officers + web_staff by EIN | 8-10 hours |
| C.3 | Foundation-specific extraction (deadlines, LOI process) | 4-6 hours |
| C.4 | Re-verification scheduling (every 90 days) | 2-3 hours |

### Phase D: Future / Lower Priority

- Bounce feedback loop (parse bounces, update validation retroactively)
- Email pattern inference (officer name + domain, then verify)
- Candid/GuideStar API (premium)
- Alternative contact channels for 86% of foundations with no website

### Key Targets

| Metric | Current | Target |
|--------|---------|--------|
| Tier 1 foundations scraped | 0 | 6,816 (those with live URLs) |
| Foundation email coverage | 19% (of those with prospects) | 65%+ |
| Campaign bounce rate | 6.1% | Under 2% |
| Validation layers | 2 (syntax + MX) | 4 (+ catch-all + commercial SMTP) |
| Confidence architecture | Single mixed score | Extraction confidence + validation status |

---

## Source Documents

This spec was consolidated from:

1. `Enhancements/2026-02-09/SESSION_REPORT.md` (email infrastructure + DB schema)
2. `Enhancements/2026-02-10/SESSION_REPORT.md` (Gmail filters + sourcing research)
3. `Enhancements/2026-02-11/SESSION_REPORT.md` (URL enrichment pipeline)
4. `Enhancements/2026-02-13/SESSION_REPORT.md` (website scraping pipeline)
5. `Enhancements/2026-02-13/OUTPUT_2026-02-13.2_email_system_documentation.md` (full system doc)
6. `Enhancements/2026-02-13/OUTPUT_2026-02-13.4_email_scraper_analysis.md` (analysis + roadmap)

---

*Generated by Claude Code on 2026-02-16*
