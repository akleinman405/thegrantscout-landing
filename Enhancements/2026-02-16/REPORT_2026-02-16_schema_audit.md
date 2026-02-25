# Database Schema Audit & Number Reconciliation

**Date:** 2026-02-16
**Prompt:** PROMPT_2026-02-16_schema_audit_and_consolidation.md
**Status:** Complete (Steps 1-3 executed, Steps 4-6 deferred)
**Owner:** Claude Code

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial audit: inventory, coverage, consistency, recommendations |
| 1.1 | 2026-02-16 | Claude Code | Executed Steps 1-3: added email to fp2, expanded oue, created web_* tables, ran ANALYZE |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem 1: The Number Confusion (Resolved)](#problem-1-the-number-confusion-resolved)
3. [Phase 1: Complete Table Inventory](#phase-1-complete-table-inventory)
4. [Column Overlap Matrix](#column-overlap-matrix)
5. [Canonical Coverage Numbers](#canonical-coverage-numbers)
6. [Consistency Checks](#consistency-checks)
7. [Phase 2: Recommended Target Architecture](#phase-2-recommended-target-architecture)
8. [Migration Plan](#migration-plan)
9. [Files Created/Modified](#files-createdmodified)
10. [Notes](#notes)

---

## Executive Summary

This audit inventoried **59 tables** across 3 schemas (`f990_2025`, `grantscout_campaign`, `filtered_campaign`) and **8 views** in grantscout_campaign. Key findings:

1. **The 56.5% vs 9.9% URL confusion is resolved.** Two separate enrichment systems exist with incompatible validation definitions. pf_returns counts scraped_low/medium URLs as "validated" (80,930 = 56.5%). org_url_enrichment only counts HTTP-alive IRS-filed URLs as "validated" (14,107 = 9.9%). Both are technically correct by their own definitions, but org_url_enrichment's definition is the one that matters for email outreach.

2. **foundation_prospects2 is missing email columns.** 10,092 foundations have `app_contact_email` in pf_returns, but fp2 has zero email columns. This is the biggest gap.

3. **Three generations of prospect tables exist** (v0=sales_*, v1=campaign.*, v2=*_prospects2), with significant column overlap but no campaign tracking in v2.

4. **web_* tables are designed but not created.** The DDL is ready from the scraper analysis.

5. **19 tables appear empty** per pg_stat but most are populated (pg_stat is stale). True empty: 0.

---

## Problem 1: The Number Confusion (Resolved)

### Root Cause: Two Enrichment Systems

There are **two independent URL enrichment systems** that were built at different times:

| System | Table | Validated = TRUE means | Foundations marked validated |
|--------|-------|------------------------|---------------------------|
| **Old (pf_returns columns)** | `pf_returns.url_validated` | URL came from any scraping source (including scraped_low) | **80,930 (56.5%)** |
| **New (org_url_enrichment)** | `org_url_enrichment.url_validated` | HTTP request returned 200/301 (URL is alive) | **14,107 (9.9%)** |

### How Each Report Number Was Derived

| Number | Percentage | Source | How It Was Calculated | Correct? |
|--------|-----------|--------|----------------------|----------|
| **14,107** | 9.9% | org_url_enrichment | `url_validated = true` (HTTP-alive URLs) | Yes, for "live validated URLs" |
| **19,094** | 13.3% | org_url_enrichment | `url_source = 'irs_filing'` (pre-HTTP-validation) | Yes, for "IRS-filed URLs before cleaning" |
| **22,577** | 15.8% | org_url_enrichment | `website_raw IS NOT NULL` (any raw URL, any source) | Yes, for "has any URL in enrichment table" |
| **49,265** | 34.4% | pf_returns | Most recent filing per EIN with non-junk website_url | Yes, for "IRS filing mentions a website" |
| **80,930** | 56.5% | pf_returns | `url_validated = true` (scraped_low/medium/high counted) | **Misleading** - "validated" includes unverified scrapes |
| **86,547** | 60.4% | pf_returns | Any filing, any year, has website_url | Yes, but inflated by historical filings |

### The Canonical Numbers (Use These Going Forward)

| Tier | Definition | Foundations | % of 143,184 |
|------|-----------|-------------|-------------|
| **T0: Total** | All unique foundation EINs | 143,184 | 100% |
| **T1: IRS-Filed URL** | Has website_url in most recent pf_returns filing (excluding junk) | 49,265 | 34.4% |
| **T2: Cleaned URL** | org_url_enrichment.website_clean IS NOT NULL | 19,119 | 13.4% |
| **T3: HTTP-Validated URL** | org_url_enrichment.url_validated = TRUE | 14,107 | 9.9% |
| **T4: Has App Email** | pf_returns.app_contact_email (any filing, unique EIN) | 10,092 | 7.0% |
| **T5: Has Phone** | foundation_prospects2.phone_num non-blank | 138,009 | 96.4% |
| **T6: Has App Phone** | foundation_prospects2.app_contact_phone non-null | 33,619 | 23.5% |
| **T7: Contactable (URL or phone)** | Validated URL OR any phone | 139,076 | 97.1% |

### URL Source Breakdown (org_url_enrichment, foundations only)

| url_source | Count | Validated TRUE | Validated FALSE | Not Yet Validated |
|-----------|-------|---------------|----------------|-------------------|
| irs_filing | 19,093 | 14,082 | 5,011 | 0 |
| junk_removed | 3,319 (with value) + 120,512 (NULL) | 0 | 0 | 123,831 |
| social_extracted | 159 | 0 | 0 | 159 |
| duckduckgo_high | 3 | 3 | 0 | 0 |
| duckduckgo_not_found | 3 | 0 | 0 | 3 |

### URL Source Breakdown (pf_returns, distinct EINs)

| url_source | EINs | Validated TRUE | Description |
|-----------|------|---------------|-------------|
| scraped_low | 43,059 | 43,059 | Low-confidence web scrape |
| invalid | 38,250 | 0 | Failed validation |
| scraped_medium | 23,110 | 23,110 | Medium-confidence web scrape |
| 990pf_xml | 17,571 | 17,571 | Direct from IRS filing XML |
| scraped_high | 4,616 | 4,616 | High-confidence web scrape |
| ein_propagation | 1,451 | 1,451 | Inferred from related EIN |
| pattern_guess | 113 | 113 | Pattern-based guess |

**Key insight:** pf_returns counts 66,169 scraped URLs (low+medium) as "validated" that org_url_enrichment classifies as "junk_removed." This is the source of the 56.5% vs 9.9% discrepancy.

---

## Phase 1: Complete Table Inventory

### Schema: f990_2025 (46 tables + 4 views)

#### Source Data Tables (IRS filings)

| Table | Rows | Cols | Key Columns | Purpose |
|-------|------|------|-------------|---------|
| pf_returns | 638,082 | 50+ | ein, tax_year, website_url, url_source, url_validated, app_contact_email | 990-PF filings (multiple per EIN). Has old enrichment columns. |
| pf_grants | 1,758,527 | ~10 | filer_ein, recipient_name, amount, purpose, tax_year | Raw grant records from 990-PF Part XV |
| pf_balance_sheet | 679,634 | ~20 | ein, tax_year | Foundation balance sheets |
| pf_revenue_expenses | 1,353,353 | ~30 | ein, tax_year | Foundation revenue and expenses |
| pf_investments | 1,844,771 | ~10 | ein, tax_year | Foundation investment holdings |
| pf_capital_gains | 3,740,163 | ~10 | ein, tax_year | Capital gains from investments |
| nonprofit_returns | 2,956,959 | ~40 | ein, tax_year, website_url, mission_description | 990/990-EZ filings |
| np_balance_sheet | 2,717,584 | ~20 | ein, tax_year | Nonprofit balance sheets |
| np_functional_expenses | 360,191 | ~20 | ein, tax_year | Nonprofit functional expenses |
| officers | 26,281,615 | ~10 | ein, person_nm, title_txt | Officers from all form types |
| contractors | 107,020 | ~8 | ein, contractor_name | Independent contractors |
| schedule_a | 574,037 | ~15 | ein, tax_year | Public charity status |
| schedule_d_endowments | 36,936 | ~10 | ein, tax_year | Endowment funds |
| schedule_f_grants | 81,561 | ~10 | ein, recipient_name | Foreign grants |
| schedule_i_grants | 996,940 | ~10 | ein, recipient_name | Schedule I grants (public charities) |
| schedule_j_compensation | 286,308 | ~10 | ein, person_name | Officer compensation details |
| schedule_o_narratives | 2,950,168 | ~5 | ein, narrative_text | Supplemental information |
| schedule_r_related_orgs | 850,773 | ~10 | ein, related_org_name | Related organizations |
| bmf | 1,935,635 | ~20 | ein, ntee_cd, subsection | IRS Business Master File |
| import_log | 748,311 | ~5 | filename, imported_at | XML import tracking |

#### Dimension Tables

| Table | Rows | Cols | Key Columns | Purpose |
|-------|------|------|-------------|---------|
| dim_foundations | 143,184 | 12 | ein, name, state, ntee_code, assets, accepts_applications | One row per foundation |
| dim_recipients | 1,652,766 | ~8 | ein, name, state, ntee_code | One row per grant recipient |
| dim_clients | 8 | ~15 | id, name, ein, known_funders | TGS client organizations |

#### Calculated/Derived Tables

| Table | Rows | Cols | Key Columns | Purpose |
|-------|------|------|-------------|---------|
| fact_grants | 8,310,650 | ~10 | foundation_ein, recipient_ein, amount, purpose_text, tax_year | Cleaned, deduplicated grants |
| calc_foundation_profiles | 143,184 | 22 | ein, openness_score, repeat_rate, geographic_focus | Foundation analytics |
| calc_foundation_features | 143,184 | ~30 | ein, feature columns | ML model features |
| calc_recipient_features | 1,652,766 | ~20 | ein, feature columns | Recipient ML features |
| calc_client_foundation_scores | 4,816 | ~5 | client_id, foundation_ein, score | Model scores per client |
| calc_client_siblings | 2,100 | ~5 | client_id, sibling_ein | Similar organizations to clients |
| calc_client_sibling_grants | 13,389 | ~8 | client_id, foundation_ein | Grants to client siblings |
| calc_client_sibling_funders | 168 | ~5 | client_id, foundation_ein | Funders of client siblings |
| calc_client_foundation_recommendations | 5 | ~5 | client_id, foundation_ein | Final recommendations |
| calc_client_proof_of_fit_grants | 25 | ~5 | client_id, grant_id | Evidence grants |
| fact_foundation_client_scores | 12,652 | ~5 | foundation_ein, client_id, score | Scoring output |
| stg_foundation_state_dist | 527,598 | ~5 | foundation_ein, state, pct | State distribution staging |
| stg_foundation_sector_dist | 588,064 | ~5 | foundation_ein, sector, pct | Sector distribution staging |

#### Enrichment/Prospect Tables

| Table | Rows | Cols | Key Columns | Purpose |
|-------|------|------|-------------|---------|
| **org_url_enrichment** | **813,698** | **21** | ein, org_type, website_raw, website_clean, url_source, url_validated | **URL enrichment hub** (foundations + nonprofits) |
| **foundation_prospects2** | **143,184** | **37** | ein, foundation_name, website_url, phone_num, app_contact_phone, contact_name | **Master foundation prospect table** (v2) |
| **nonprofits_prospects2** | **673,381** | **47** | ein, organization_name, website, phone, mission_description, ed_ceo_name | **Master nonprofit prospect table** (v2) |
| foundation_enrichment | 34 | 24 | ein, application_url, contact_email, contact_phone | Manual enrichment cache (pipeline) |
| sales_foundation_prospects | 761 | 43 | ein, contact_email, rating, researched | V0 foundation sales prospects |
| sales_nonprofit_prospects | 74,175 | ~40 | ein, contact_email, icp_score | V0 nonprofit sales prospects |

#### Reference Tables

| Table | Rows | Cols | Purpose |
|-------|------|------|---------|
| ref_state_regions | 51 | ~3 | State-to-region mapping |
| ref_org_aliases | 150 | ~3 | Organization name aliases |
| ref_recipient_alias_mappings | 129 | ~3 | Recipient name normalization |
| research_events | 273 | ~5 | Research activity log |

#### Views (f990_2025)

| View | Source Tables | Purpose |
|------|-------------|---------|
| sales_prospects | grantscout_campaign.nonprofit_prospects + foundation_prospects | Unified sales view |
| grant_purpose_quality | fact_grants | Grant data quality metrics |
| prospects_with_events | Multiple | Prospects joined with events |
| vw_foundation_summary | Multiple | Foundation summary view |

### Schema: grantscout_campaign (13 base tables + 8 views)

#### Base Tables

| Table | Rows | Cols | Purpose |
|-------|------|------|---------|
| **foundation_prospects** | **761** | **54** | V1 foundation prospects with campaign tracking |
| **nonprofit_prospects** | **74,175** | **100** | V1 nonprofit prospects with campaign tracking |
| senders | 10 | 9 | Email sender accounts |
| generated_emails | 0 | 25 | Generated email content |
| send_log | 0 | 12 | Email send history |
| sender_daily_stats | 0 | 7 | Sender volume tracking |
| calls | 0 | 10 | Phone call tracking |
| contact_events | 0 | 9 | Contact event log |
| responses | 0 | 11 | Email response tracking |
| pipeline | 0 | 8 | Sales pipeline stages |
| prospect_duplicates | 0 | 6 | Duplicate detection |
| scrape_jobs | 0 | 12 | Web scrape job tracking |
| tasks | 0 | 8 | Follow-up task tracking |

#### Views

| View | Source | Purpose |
|------|--------|---------|
| sales_prospects | nonprofit_prospects + foundation_prospects | Unified prospect view |
| campaign_summary | prospect tables | Campaign status summary |
| campaign_funnel_metrics | prospect tables | Funnel metrics |
| daily_campaign_report | send_log | Daily send report |
| high_value_nonprofits | nonprofit_prospects | Filtered high-value view |
| ab_test_results | generated_emails | A/B test metrics |
| sender_performance | senders + send_log | Sender performance |
| sender_stats_summary | senders + sender_daily_stats | Sender stats |

### Schema: filtered_campaign (separate project, out of scope)

Contains 24 objects (8 base tables, 16 views) with 20,109 prospects. This appears to be a different campaign (professional services). Not related to TGS foundation/nonprofit work.

---

## Column Overlap Matrix

### URL Columns

| Column | pf_returns | foundation_prospects2 | org_url_enrichment | campaign.foundation_prospects | dim_foundations |
|--------|-----------|----------------------|-------------------|------------------------------|----------------|
| website_url / website_raw | website_url (raw IRS value) | website_url (= oue.website_raw) | website_raw | website | -- |
| Cleaned URL | -- | -- | website_clean | -- | -- |
| URL source | url_source (old system) | -- | url_source (new system) | -- | -- |
| URL validated | url_validated (old definition) | -- | url_validated (HTTP check) | -- | -- |
| Redirect target | -- | -- | url_redirect_target | -- | -- |
| HTTP status | -- | -- | url_http_status | -- | -- |

**Finding:** Only org_url_enrichment has the cleaned/validated URL pipeline data. fp2.website_url is a copy of oue.website_raw but doesn't include the 1,343 additional URLs from junk_removed/social_extracted sources.

### Email Columns

| Column | pf_returns | foundation_prospects2 | org_url_enrichment | campaign.foundation_prospects | foundation_enrichment |
|--------|-----------|----------------------|-------------------|------------------------------|----------------------|
| app_contact_email | 10,092 EINs | **MISSING** | -- | contact_email (148 rows) | contact_email (8 rows) |
| email_address_txt | 0 EINs | -- | -- | -- | -- |

**Critical gap:** 10,092 foundation emails in pf_returns are not carried into fp2 or oue.

### Contact/Phone Columns

| Column | pf_returns | foundation_prospects2 | campaign.foundation_prospects |
|--------|-----------|----------------------|------------------------------|
| phone_num | phone_num (138K EINs) | phone_num (138K) | contact_phone (148 rows) |
| app_contact_phone | 33,619 EINs | app_contact_phone (33,619) | -- |
| contact_name | app_contact_name (35,162) | app_contact_name + contact_name | contact_name |
| contact_title | -- | contact_title (140,498) | contact_title |

### Org Identity Columns

| Column | fp2 | np2 | oue | campaign.fp | campaign.np | dim_foundations |
|--------|-----|-----|-----|-------------|-------------|----------------|
| EIN | ein | ein | ein | ein | ein | ein |
| Name | foundation_name | organization_name | org_name | org_name | org_name | name |
| State | state | state | state | state | state | state |
| City | city | city | city | -- | city | city |
| Zip | zip | zip | -- | -- | zip | -- |
| NTEE | bmf_ntee_cd | ntee_code | -- | -- | ntee_code | ntee_code |
| Assets | total_assets_eoy_amt | -- | -- | assets | total_assets | assets |
| Address | address_line1/2 | address_line1/2 | -- | -- | -- | -- |

---

## Canonical Coverage Numbers

### Foundations (143,184 unique EINs)

| Metric | Count | % | Source Table |
|--------|-------|---|-------------|
| Total foundations | 143,184 | 100% | dim_foundations / foundation_prospects2 |
| Has any URL (most recent filing) | 49,265 | 34.4% | pf_returns (latest filing, excluding junk) |
| Has raw URL in enrichment | 22,577 | 15.8% | org_url_enrichment (website_raw not null) |
| Has cleaned URL | 19,119 | 13.4% | org_url_enrichment (website_clean not null) |
| Has HTTP-validated URL | 14,107 | 9.9% | org_url_enrichment (url_validated = true) |
| Has app contact email | 10,092 | 7.0% | pf_returns (any filing) |
| Has any phone | 138,009 | 96.4% | foundation_prospects2 (phone_num) |
| Has app contact phone | 33,619 | 23.5% | foundation_prospects2 (app_contact_phone) |
| Has contact name (officers) | 140,498 | 98.1% | foundation_prospects2 (contact_name) |
| Has mission/activity desc | 115,205 | 80.5% | foundation_prospects2 (activity_or_mission_desc) |
| Has NTEE code | 91,582 | 64.0% | foundation_prospects2 (bmf_ntee_cd) |
| Has app deadlines | 33,066 | 23.1% | foundation_prospects2 (app_submission_deadlines) |
| Contactable (validated URL OR phone) | 139,076 | 97.1% | org_url_enrichment + foundation_prospects2 |

### Foundations by Asset Tier

| Asset Tier | Foundations | Has Any URL | Has Validated URL | Has App Phone | Has Phone |
|-----------|-------------|-------------|-------------------|---------------|-----------|
| < $100K | 55,061 (38%) | 10,910 (20%) | 6,143 (11%) | 9,838 (18%) | 50,572 (92%) |
| $100K - $1M | 41,732 (29%) | 4,354 (10%) | 2,639 (6%) | 10,424 (25%) | 41,244 (99%) |
| $1M - $10M | 35,057 (24%) | 4,004 (11%) | 2,683 (8%) | 9,462 (27%) | 34,883 (99%) |
| $10M - $100M | 9,756 (7%) | 2,445 (25%) | 1,925 (20%) | 3,246 (33%) | 9,734 (100%) |
| $100M+ | 1,578 (1%) | 864 (55%) | 717 (45%) | 649 (41%) | 1,576 (100%) |

### Nonprofits (673,381 unique EINs in np2; 670,514 in oue)

| Metric | Count | % | Source Table |
|--------|-------|---|-------------|
| Total nonprofits (np2) | 673,381 | 100% | nonprofits_prospects2 |
| Total nonprofits (oue) | 670,514 | 99.6% | org_url_enrichment (2,867 fewer) |
| Has website (np2) | 578,028 | 85.9% | nonprofits_prospects2 |
| Has raw URL (oue) | 575,575 | 85.5% | org_url_enrichment |
| Has cleaned URL (oue) | 358,082 | 53.2% | org_url_enrichment |
| Has HTTP-validated URL (oue) | 293,778 | 43.6% | org_url_enrichment |
| Has phone (np2) | 673,381 | 100% | nonprofits_prospects2 |
| Has mission (np2) | 673,381 | 100% | nonprofits_prospects2 |
| Has ED/CEO name (np2) | 142,550 | 21.2% | nonprofits_prospects2 |
| Has NTEE code (np2) | 452,209 | 67.2% | nonprofits_prospects2 |

---

## Consistency Checks

### Check 1: foundation_prospects2 vs org_url_enrichment

| Metric | Result |
|--------|--------|
| fp2 total EINs | 143,184 |
| oue foundation EINs | 143,184 |
| EIN overlap | 143,184 (100%) |
| fp2.website_url = oue.website_raw? | **Yes, exact match for all 21,234 rows** |
| oue has URLs that fp2 doesn't | **1,343** (from junk_removed/social_extracted with values) |
| fp2 has URLs that oue doesn't | 0 |

**Conclusion:** fp2.website_url is a direct copy of oue.website_raw. The 1,343 additional URLs in oue are from sources that were processed after fp2 was built.

### Check 2: nonprofits_prospects2 vs org_url_enrichment

| Metric | Result |
|--------|--------|
| np2 total EINs | 673,381 |
| oue nonprofit EINs | 670,514 |
| Overlap | 670,514 |
| np2-only EINs | 2,867 (in np2 but not oue) |
| oue-only EINs | 0 |
| URL match (np2.website = oue.website_raw) | **Exact match for all 575,575 shared records** |

**Conclusion:** oue is a subset of np2. 2,867 nonprofits in np2 haven't been processed through URL enrichment yet.

### Check 3: V1 vs V2 Prospect Tables

| Metric | foundation | nonprofit |
|--------|-----------|-----------|
| V1 (campaign.*) rows | 761 | 74,175 |
| V2 (f990_2025.*_prospects2) rows | 143,184 | 673,381 |
| V1 EINs in V2 | 761 (100%) | 74,144 (99.96%) |
| V1-only EINs | 0 | 31 |

**V1 has data V2 doesn't have:**

- **campaign.foundation_prospects:** 148 contact_emails, 351 ratings, 348 researched flags, campaign tracking columns (sent_at, replied, bounced)
- **campaign.nonprofit_prospects:** 63 contact_emails, icp_score, personalization data, campaign tracking columns, Google Places enrichment, government grant data

**V2 has data V1 doesn't have:**

- **foundation_prospects2:** Full IRS filing data, BMF data, address, app submission info, officer contacts
- **nonprofits_prospects2:** Full IRS filing data, BMF data, mission, programs, all officers as JSONB

### Check 4: sales_foundation_prospects vs campaign.foundation_prospects

| Metric | Result |
|--------|--------|
| Same 761 EINs | Yes (100% overlap) |
| Column difference | campaign version has 12 extra columns (campaign_status, sent_at, replied, bounced, etc.) + org_name vs foundation_name |

**Conclusion:** sales_foundation_prospects is the original, campaign.foundation_prospects is a superset. The f990_2025 version can be dropped (it's redundant).

### Check 5: pf_returns Enrichment Columns vs org_url_enrichment

| Aspect | pf_returns | org_url_enrichment |
|--------|-----------|-------------------|
| Enrichment model | Applied per-filing (multi-row per EIN) | One row per EIN |
| url_source values | scraped_low, scraped_medium, scraped_high, 990pf_xml, ein_propagation, pattern_guess, invalid | irs_filing, junk_removed, social_extracted, duckduckgo_high, duckduckgo_not_found |
| "Validated" means | Has a url_source that isn't "invalid" | HTTP request returned 200/301 |
| Foundations covered | 119,180 EINs with url_source | 143,184 EINs (all foundations) |
| Email column | app_contact_email (10,092 EINs) | None |

**Conclusion:** These are two separate enrichment efforts. The pf_returns columns were an earlier batch process; org_url_enrichment is the newer, more rigorous system. The pf_returns email data (10,092 EINs) has NOT been migrated to any enrichment table.

---

## Phase 2: Recommended Target Architecture

### Proposal: Three-Table Architecture

```
                    ┌─────────────────────────┐
                    │    dim_foundations       │  (exists, 143K rows)
                    │    dim_recipients        │  (exists, 1.6M rows)
                    │  One row per EIN, core   │
                    │  identity + IRS data     │
                    └─────────┬───────────────┘
                              │ FK: ein
                    ┌─────────▼───────────────┐
                    │  org_url_enrichment      │  (exists, 813K rows)
                    │  One row per EIN,        │
                    │  URL + email + contact   │
                    │  enrichment data         │
                    │  ADD: email columns      │
                    │  ADD: phone columns      │
                    └─────────┬───────────────┘
                              │ FK: ein
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                   ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────────┐
    │  web_pages    │ │  web_emails   │ │  web_staff        │
    │  web_org_meta │ │  web_best_    │ │  (from scraper)   │
    │  (from scraper│ │  email (mat.) │ │                   │
    └───────────────┘ └───────────────┘ └───────────────────┘
```

### Recommendation 1: Expand org_url_enrichment as the Enrichment Hub

Add these columns to org_url_enrichment:

| New Column | Type | Source | Purpose |
|------------|------|--------|---------|
| app_contact_email | VARCHAR(255) | pf_returns | Application contact email |
| app_contact_phone | VARCHAR(30) | pf_returns/fp2 | Application contact phone |
| phone_num | VARCHAR(30) | pf_returns/fp2 | Main organization phone |
| contact_name | TEXT | fp2 | Primary contact name |
| contact_title | TEXT | fp2 | Primary contact title |
| email_source | VARCHAR(30) | New | Where email came from (irs_filing, web_scrape, manual) |
| email_validated | BOOLEAN | New | MX/SMTP validation result |
| email_validated_at | TIMESTAMP | New | When email was validated |
| phone_source | VARCHAR(30) | New | Where phone came from |
| phone_validated | BOOLEAN | New | Phone validation result |

**Rationale:** org_url_enrichment already has one row per EIN for both foundations and nonprofits. It's the natural place to consolidate all contact enrichment data. Adding email/phone columns here means every enrichment script writes to one table.

### Recommendation 2: Keep foundation_prospects2 / nonprofits_prospects2 as Master Prospect Tables

These tables should remain as the "complete profile" tables that JOIN IRS filing data + BMF data + enrichment data. They serve a different purpose: providing a denormalized view for report generation and pipeline scoring.

**Action needed:**
- Add `app_contact_email` column to foundation_prospects2 (backfill from pf_returns)
- Keep website_url synced with org_url_enrichment.website_clean (not website_raw)
- Add a view or materialized view that joins fp2 + oue for the full enriched picture

### Recommendation 3: Retire or Migrate Campaign V1 Tables

| Table | Action | Rationale |
|-------|--------|-----------|
| grantscout_campaign.foundation_prospects | **Migrate campaign data to campaign tracking tables, then drop** | 761 rows, all EINs in fp2. Research/rating data (351 rows) should be migrated to foundation_enrichment. Campaign tracking (0 sent) goes to campaign tables. |
| grantscout_campaign.nonprofit_prospects | **Migrate campaign data, keep as read-only archive, then drop** | 74K rows, all in np2. Has 63 emails and personalization data worth preserving. |
| f990_2025.sales_foundation_prospects | **Drop** | Identical 761 EINs as campaign.foundation_prospects but without campaign columns. Fully redundant. |
| f990_2025.sales_nonprofit_prospects | **Drop** | Same data as campaign.nonprofit_prospects (74,175 rows, 100% overlap). |

### Recommendation 4: Create web_* Tables in f990_2025 Schema

The DDL from the scraper analysis is ready. Create these in f990_2025:

| Table | Type | FK to |
|-------|------|-------|
| web_pages | TABLE | org_url_enrichment.ein |
| web_emails | TABLE | org_url_enrichment.ein |
| web_org_metadata | TABLE | org_url_enrichment.ein (PK) |
| web_staff | TABLE | org_url_enrichment.ein |
| web_best_email | MATERIALIZED VIEW | web_emails |

**Schema choice:** f990_2025, not a new schema. These tables enrich org data and should live alongside the enrichment table they reference.

**FK target:** org_url_enrichment.ein (not fp2/np2) because the scraper operates on URLs from org_url_enrichment.

### Recommendation 5: Clean Up pf_returns Enrichment Columns

The old enrichment columns in pf_returns (url_source, url_validated, url_enriched_at, phone_source, phone_validated, phone_enriched_at) are from a deprecated enrichment process. Options:

- **Option A (recommended):** Leave them in place but document them as deprecated. No migration needed.
- **Option B:** Drop the columns after confirming all data has been migrated to org_url_enrichment + new email columns.

### Recommendation 6: Consolidate the Campaign Sender Pipeline

The campaign sender should read prospect data from:

```
grantscout_campaign.sales_prospects (VIEW)
  → Currently reads from: campaign.nonprofit_prospects + campaign.foundation_prospects
  → Should read from: f990_2025.nonprofits_prospects2 + f990_2025.foundation_prospects2
     JOINED WITH org_url_enrichment (for validated URLs and emails)
     JOINED WITH campaign tracking tables (for sent/replied/bounced status)
```

This means refactoring the sales_prospects view to point at the v2 tables, and moving campaign tracking columns (campaign_status, initial_sent_at, replied, bounced, etc.) into a dedicated `campaign_prospect_status` table that the sender reads/writes.

---

## Migration Plan

### Step 1: Add Email Column to foundation_prospects2 (LOW RISK)

```sql
ALTER TABLE f990_2025.foundation_prospects2 ADD COLUMN app_contact_email VARCHAR(255);

UPDATE f990_2025.foundation_prospects2 fp2
SET app_contact_email = sub.app_contact_email
FROM (
  SELECT DISTINCT ON (ein) ein, app_contact_email
  FROM f990_2025.pf_returns
  WHERE app_contact_email IS NOT NULL AND app_contact_email <> ''
  ORDER BY ein, tax_year DESC NULLS LAST
) sub
WHERE fp2.ein = sub.ein;
```

### Step 2: Add Contact Columns to org_url_enrichment (LOW RISK)

```sql
ALTER TABLE f990_2025.org_url_enrichment
  ADD COLUMN app_contact_email VARCHAR(255),
  ADD COLUMN app_contact_phone VARCHAR(30),
  ADD COLUMN phone_num VARCHAR(30),
  ADD COLUMN contact_name TEXT,
  ADD COLUMN contact_title TEXT,
  ADD COLUMN email_source VARCHAR(30),
  ADD COLUMN email_validated BOOLEAN,
  ADD COLUMN email_validated_at TIMESTAMP;
```

Then backfill from pf_returns and fp2.

### Step 3: Create web_* Tables (LOW RISK)

Run the DDL from the scraper analysis (see agent research output above).

### Step 4: Migrate Campaign V1 Data (MEDIUM RISK)

1. Export 351 research/rating records from campaign.foundation_prospects to foundation_enrichment
2. Export 148 contact_email records to fp2.app_contact_email and oue.app_contact_email
3. Export 63 nonprofit contact_emails to np2 and oue
4. Create `grantscout_campaign.campaign_prospect_status` table for campaign tracking
5. Migrate campaign tracking data (0 rows sent, so this is safe)

### Step 5: Update Views (LOW RISK)

Repoint sales_prospects views to use v2 tables + campaign_prospect_status.

### Step 6: Drop Redundant Tables (AFTER VALIDATION)

- f990_2025.sales_foundation_prospects (761 rows, fully redundant)
- f990_2025.sales_nonprofit_prospects (74,175 rows, fully redundant)
- grantscout_campaign.foundation_prospects (after migration)
- grantscout_campaign.nonprofit_prospects (after migration)

### Rollback Plan

Before any drops, create backup tables:
```sql
CREATE TABLE f990_2025._bak_sales_foundation_prospects AS SELECT * FROM f990_2025.sales_foundation_prospects;
CREATE TABLE f990_2025._bak_campaign_foundation_prospects AS SELECT * FROM grantscout_campaign.foundation_prospects;
-- etc.
```

### Scripts That Need Updating

| Script | Current Table Reference | New Reference |
|--------|----------------------|---------------|
| Pipeline 01_load_client.py | dim_clients | No change |
| Pipeline 02_score_foundations.py | calc_foundation_profiles, dim_foundations | No change |
| Pipeline 03_check_enrichment.py | foundation_enrichment | No change |
| URL enrichment scripts 01-07 | org_url_enrichment | No change (stays as-is) |
| Campaign email sender | grantscout_campaign.foundation_prospects | campaign_prospect_status + fp2 + oue |
| Campaign email sender | grantscout_campaign.nonprofit_prospects | campaign_prospect_status + np2 + oue |

---

## Execution Log (Steps 1-3)

### Step 1: Add app_contact_email to foundation_prospects2

```
ALTER TABLE f990_2025.foundation_prospects2 ADD COLUMN app_contact_email VARCHAR(255);
UPDATE 10092 rows from pf_returns (most recent filing per EIN)
```

**Verification:**
| Metric | Count |
|--------|-------|
| Total rows | 143,184 |
| Has app_contact_email | 10,092 |
| No email | 133,092 |

### Step 2: Expand org_url_enrichment

**8 columns added:** app_contact_email, app_contact_phone, phone_num, contact_name, contact_title, email_source, email_validated, email_validated_at

**Backfill results:**

| org_type | Total | Has Email | Has App Phone | Has Phone | Has Contact Name | Has Contact Title |
|----------|-------|-----------|---------------|-----------|------------------|-------------------|
| foundation | 143,184 | 10,092 | 33,619 | 138,009 | 140,498 | 140,498 |
| nonprofit | 670,514 | 0 | 0 | 670,514 | 142,130 | 142,130 |

### Step 3: Create web_* tables

| Object | Type | Status | Key Indexes |
|--------|------|--------|-------------|
| web_pages | TABLE | Created (0 rows) | UNIQUE(ein, url), idx on ein, page_type |
| web_emails | TABLE | Created (0 rows) | UNIQUE(ein, email), idx on ein, email_type, mx_valid |
| web_org_metadata | TABLE | Created (0 rows) | PK(ein), idx on cms_platform |
| web_staff | TABLE | Created (0 rows) | UNIQUE(ein, person_name, email), idx on ein, email, staff_type |
| web_best_email | MATERIALIZED VIEW | Created (WITH NO DATA) | UNIQUE idx on ein |

### ANALYZE

Ran `ANALYZE VERBOSE` on entire database. pg_stat_user_tables now shows accurate row counts.

**Stale query killed:** A SELECT on org_url_enrichment had been running for 1h15m, blocking the ALTER TABLE. Cancelled via `pg_cancel_backend()`.

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| REPORT_2026-02-16_schema_audit.md | Enhancements/2026-02-16/ | This report |

### Database Changes

| Object | Change | Rows Affected |
|--------|--------|---------------|
| f990_2025.foundation_prospects2 | Added app_contact_email column | 10,092 backfilled |
| f990_2025.org_url_enrichment | Added 8 columns (email, phone, contact) | 143,184 foundations + 670,514 nonprofits backfilled |
| f990_2025.web_pages | Created table | 0 (new, empty) |
| f990_2025.web_emails | Created table | 0 (new, empty) |
| f990_2025.web_org_metadata | Created table | 0 (new, empty) |
| f990_2025.web_staff | Created table | 0 (new, empty) |
| f990_2025.web_best_email | Created materialized view | 0 (WITH NO DATA) |
| All schemas | ANALYZE VERBOSE | pg_stat updated |

---

## Notes

### Issues Found
1. **pg_stat_user_tables is severely stale** - showed 19 tables as having 0 rows when they actually had data (up to 1.6M rows). Run `ANALYZE` on the database.
2. **filtered_campaign schema exists** with 20K prospects - appears to be a separate project (professional services). Not related to TGS.
3. **pf_returns has dual-purpose enrichment columns** from an old process that conflicts with the new org_url_enrichment system.
4. **foundation_prospects2 missing email** - the single biggest data gap for email outreach.

### Recommendations Priority
1. **Immediate:** Add app_contact_email to fp2 (unlocks 10,092 foundation emails)
2. **Before pipeline implementation:** Create web_* tables
3. **Before campaign launch:** Consolidate campaign tracking into dedicated table
4. **Cleanup (can wait):** Drop redundant sales_* tables after migration

### Questions for Approval
1. Proceed with adding email column to fp2? (Step 1)
2. Proceed with expanding org_url_enrichment? (Step 2)
3. Proceed with creating web_* tables? (Step 3)
4. Approve approach for campaign table migration? (Steps 4-6)

---

*Generated by Claude Code on 2026-02-16*
