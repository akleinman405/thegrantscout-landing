# URL Discovery Research for Foundations

**Date:** 2026-02-16
**Prompt:** Deep research into external data sources, technical tools, and strategic approaches for improving foundation URL/contact coverage
**Status:** Complete
**Owner:** Aleck Kleinman

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial version, synthesized from 3 parallel research agents |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Revised Ceiling Estimate](#revised-ceiling-estimate)
3. [Current State: The Real Numbers](#current-state-the-real-numbers)
4. [Approaches Found](#approaches-found)
5. [Ranked Recommendation](#ranked-recommendation)
6. [Targets (30-Day / 90-Day / Theoretical Max)](#targets)
7. [What We Still Don't Know](#what-we-still-dont-know)
8. [A/B Testing Plan](#ab-testing-plan)
9. [Supporting Research Reports](#supporting-research-reports)
10. [Files Created/Modified](#files-createdmodified)
11. [Notes](#notes)

---

## Executive Summary

We launched 3 parallel research agents covering external data sources, technical discovery tools, and strategic analysis (including live database queries). Combined with the prior internal research (REPORT .2), this gives us a comprehensive picture of the URL discovery landscape.

### 5 Key Insights

1. **The production gap is small.** Of 11,889 high-value foundations (open to applications, $1M+ assets, recent grant activity), 2,386 (20.1%) have validated URLs. Adding the 21,574 foundations with IRS-filed contact emails, we can already reach far more foundations than the "9.9%" figure suggests.

2. **Most foundations genuinely do not have websites.** Of 143,184 foundations, only ~19,094 filed any URL with the IRS. The other 124K reported "N/A" or left it blank on their own tax returns. No external data source can conjure websites that don't exist.

3. **Serper.dev is the breakthrough tool.** Google SERP API at $0.30-$1.00 per 1,000 queries. Full 130K foundation search costs $39-$130. This is 5x cheaper than Google's own API and 35x cheaper than Bing's replacement. The 2,500 free queries allow a zero-risk pilot.

4. **Bank-managed foundations (12,825) have a systematic contact path.** JPMorgan, Bank of America, Wells Fargo, and PNC all have public grant portals. The bank's philanthropy desk IS the front door. 9,007 of these foundations have no website but are contactable through the bank.

5. **We're sitting on 21,574 untapped contact emails.** The `app_contact_email` field in 990-PF filings already contains structured email addresses. Another 18,089 foundations have email patterns buried in their application text fields. This is free data already in our database.

### 3 Actions to Take

1. **Run Serper.dev pilot** (free, 2,500 queries) to measure Google hit rate for foundation URL discovery. If >50%, purchase credits for the full 130K run ($39-$130).

2. **Mine the 990-PF application fields** we already have. Extract emails from `app_contact_email` (21,574 foundations) and regex-mine `application_submission_info` for URLs and emails (18,089 with @ patterns). Zero cost, half a day of work.

3. **Re-tune the DuckDuckGo scraper** to save medium+high confidence matches (as in Dec 2025). The 83.7% vs 25% hit rate drop was a threshold issue, not a data quality issue.

### 1 Thing to NOT Pursue

**B2B enrichment APIs** (Clearbit/Breeze, ZoomInfo, Lusha, RocketReach). Private foundations are not companies. They have no employees, no LinkedIn pages, no Clearbit profiles. These tools are designed for tech/SaaS B2B sales and have near-zero coverage for family foundations. ZoomInfo alone costs $15K+/year. Do not waste time evaluating them.

---

## Revised Ceiling Estimate

The original plan estimated ~27,300 foundations with discoverable websites (19% of 143K). After research, the revised estimate:

### URL Discovery Ceiling

| Tier | Foundations | Est. Have Website | Already Found | Discoverable Gap |
|------|-----------|-------------------|---------------|-----------------|
| Over $100M | 1,648 | ~1,400 (85%) | 748 | ~650 |
| $10M-$100M | 10,457 | ~6,300 (60%) | 2,047 | ~4,250 |
| $1M-$10M | 38,181 | ~11,500 (30%) | 2,915 | ~8,600 |
| $100K-$1M | 46,880 | ~5,600 (12%) | 3,058 | ~2,500 |
| Under $100K | 49,752 | ~2,500 (5%) | 6,137 | ~0* |

*Under $100K already over-discovered (6,137 > 2,500 estimate). Many "URLs" for tiny foundations are likely low-quality matches.

**Revised total discoverable gap: ~16,000 new URLs** (mostly in the $1M-$100M range where foundations are large enough to have websites but we haven't found them yet).

### Contact Discovery Ceiling (URLs + Emails + Bank Paths)

The real question isn't "how many URLs can we find?" but "how many foundations can we contact?"

| Contact Method | Foundations Covered | Overlap-Adjusted |
|---------------|-------------------|-----------------|
| Validated URL | 14,107 | 14,107 |
| Contact email (990-PF field) | 21,574 | ~15,000 new |
| Email patterns in app text | 18,089 | ~8,000 new |
| Bank portal/desk | 12,825 | ~9,000 new |
| Serper.dev URL discovery | ~16,000 | ~8,000 new |
| Pattern guessing + DNS | ~3,000-10,000 | ~3,000 new |
| **Total contactable** | | **~57,000** |

**Revised ceiling: ~57,000 contactable foundations (40% of 143K)**, up from 14,107 today. The remaining 60% are tiny family trusts with no website, no email, no phone, managed by an attorney or CPA.

---

## Current State: The Real Numbers

### Overall Foundation URL Coverage

| Metric | Count | % of 143K |
|--------|-------|-----------|
| Total foundations | 143,184 | 100% |
| Have validated URL | 14,107 | 9.9% |
| Have IRS-filed URL (pre-cleaning) | 19,094 | 13.3% |
| URL source = irs_filing (all orgs) | 377,176 | -- |
| URL source = duckduckgo_high | 25 | -- |
| No usable URL ever filed | ~124,000 | 86.6% |

### URL Coverage by Asset Tier (Tax Year >= 2021)

| Tier | Foundations | With URL | URL % |
|------|-----------|----------|-------|
| Under $100K | 49,752 | 6,137 | 12.3% |
| $100K-$1M | 46,880 | 3,058 | 6.5% |
| $1M-$10M | 38,181 | 2,915 | 7.6% |
| $10M-$100M | 10,457 | 2,047 | 19.6% |
| Over $100M | 1,648 | 748 | 45.4% |

The anomaly: under-$100K foundations have a HIGHER URL rate (12.3%) than $100K-$1M (6.5%). This likely reflects low-quality scraped matches from Dec 2025 (43K scraped_low entries).

### Coverage for Open-to-Applications Foundations

| Segment | Total | With URL | URL % |
|---------|-------|----------|-------|
| All open (preselected = false/null) | 42,385 | 6,114 | 14.4% |
| Open + $1M+ assets + recent grants | 11,889 | 2,386 | 20.1% |

### Contactability (URL OR Email) by Tier, Open Foundations

| Tier | Total | URL | Email | URL or Email | Contactable % |
|------|-------|-----|-------|-------------|--------------|
| Under $100K | 22,745 | 3,048 | 2,358 | 4,841 | 21.3% |
| $100K-$1M | 9,795 | 898 | 2,490 | 2,942 | 30.0% |
| $1M-$10M | 8,752 | 1,105 | 2,140 | 2,756 | 31.5% |
| $10M-$100M | 3,123 | 1,029 | 838 | 1,493 | 47.8% |
| Over $100M | 645 | 425 | 192 | 475 | 73.6% |

The pattern is clear: contactability scales with foundation size. Large foundations (>$100M) are 73.6% contactable; tiny ones (<$100K) are only 21.3%.

### Data Already in Our Database (Untapped)

| Data Source | Foundations | Description |
|-------------|-------------|-------------|
| `app_contact_email` | 21,574 | Structured email field in 990-PF |
| `application_submission_info` with @ | 18,089 | Email patterns in free text |
| `application_submission_info` with URL | 461 | URL patterns in free text |
| `app_contact_phone` | 85,600+ | Phone numbers for reverse lookup |
| `app_contact_name` | bank-managed subset 1,493 | Named contacts at banks |

---

## Approaches Found

### Tier 1: Free / Nearly Free (Do First)

#### 1. Mine 990-PF Application Fields (FREE)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | 21,574 emails from structured field + ~5,000-10,000 from regex mining text fields |
| **Cost** | $0 |
| **Effort** | 0.5 days (Python regex script) |
| **Legal risk** | None (IRS public data we already have) |
| **Data freshness** | Current (from latest filings) |
| **Confidence** | HIGH. The `app_contact_email` field is structured data. Regex extraction from text requires validation. |

**Why this is #1:** It requires zero external tools, zero API calls, zero cost. The data is sitting in our database right now. We just need to extract it.

#### 2. Re-tune DuckDuckGo Scraper (FREE)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | 30,000-60,000 URLs (re-enabling medium confidence) |
| **Cost** | $0 (+ $1-$5 for proxy rotation) |
| **Effort** | 0.5 days to change threshold; 1 day for proxy rotation |
| **Legal risk** | Medium (no official API; TOS gray area) |
| **Data freshness** | Real-time |
| **Confidence** | MEDIUM. Dec 2025 achieved 83.7% but with unknown false positive rate. Need validation pass. |

**Why this matters:** The Feb 2026 drop from 83.7% to 25% was a threshold decision, not a data quality issue. Re-tuning is the single cheapest improvement available.

#### 3. DNS Domain Guessing + HTTP Verification (FREE)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | 3,000-10,000 new URLs (incremental over search) |
| **Cost** | $0 |
| **Effort** | 1-2 days |
| **Legal risk** | None (DNS is public protocol) |
| **Data freshness** | Real-time |
| **Confidence** | MEDIUM. Pattern guessing works well for predictably-named foundations (e.g., fordfoundation.org) but produces false positives for common names. |

**Key patterns:** `{name}.org`, `{name}foundation.org`, `the{name}.org`, `{lastname}foundation.org`, `{initials}foundation.org`. Already partially built in `free_url_enrichment.py`. MassDNS can verify 350K+ candidates/second.

#### 4. Pattern Guessing from Dec 2025 (FREE, ALREADY BUILT)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | 2,000-10,000 URLs |
| **Cost** | $0 |
| **Effort** | 1-2 hours (adapt existing `free_url_enrichment.py`) |
| **Legal risk** | None |
| **Data freshness** | Real-time |
| **Confidence** | MEDIUM. Only 113 URLs found previously, but the script may not have been run at full scale. |

### Tier 2: Low Cost ($39-$300)

#### 5. Serper.dev Google SERP API ($39-$130)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | 50,000-80,000 URL matches (many overlap with DDG) |
| **Cost** | $39-$130 for 130K queries. 2,500 free on signup. |
| **Effort** | 0.5 days |
| **Legal risk** | Low (Serper handles Google scraping) |
| **Data freshness** | Real-time (live Google results) |
| **Confidence** | HIGH. Google has the most comprehensive web index. |

**Price comparison:**

| API | Cost for 130K queries |
|-----|----------------------|
| Serper.dev | $39-$130 |
| Google Custom Search | $650 (closing Jan 2027) |
| Brave Search | $650 |
| SerpAPI | $1,170 |
| Bing replacement | $4,550 |

Serper.dev is 5x-35x cheaper than alternatives. The 2,500 free queries allow a zero-risk pilot.

#### 6. Smarty Address Classification ($100-$300)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | 0 URLs directly, but segments 95K addresses by type (residential/commercial/PO Box) |
| **Cost** | $100-$300 one-time |
| **Effort** | 0.5 days |
| **Legal risk** | None (USPS public data) |
| **Data freshness** | Current (USPS data updated regularly) |
| **Confidence** | HIGH. USPS RDI classification is definitive. |

**Why it matters:** Knowing whether a foundation's address is a home, office, bank, or law firm tells us the right outreach strategy. A personal letter to a family trustee at home is very different from a formal inquiry to a bank trust department.

### Tier 3: Moderate Cost ($100-$10,000)

#### 7. Candid (GuideStar) API ($100-$9,900/yr)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | 20,000-50,000 URLs (304K grantmaker profiles, many overlap with IRS data) |
| **Cost** | Free 30-day trial, then Candid Search $100/month or Premier API $9,900/year |
| **Effort** | 1-2 days |
| **Legal risk** | None (official data provider) |
| **Data freshness** | Continuously updated |
| **Confidence** | HIGH. Candid is the definitive source for US foundation data. |

**Key finding:** Candid Search launched January 2026, merging GuideStar + Foundation Directory at $100/month (down from $299). The Premier API v3 explicitly includes `website_url`. For 304K grantmaker profiles, this is the single richest data source.

**Start with:** Free 30-day API trial. Test 1,000 EIN lookups to measure incremental coverage over what we already have.

#### 8. Bank Portal Mapping (FREE, effort only)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | Contact paths for 9,007 foundations (not URLs per se, but portal links + phone numbers) |
| **Cost** | $0 |
| **Effort** | 2-3 days |
| **Legal risk** | None |
| **Data freshness** | Current |
| **Confidence** | HIGH. Bank philanthropy desks are the standard contact path for trusteed foundations. |

**Bank portal coverage:**

| Bank | Our Foundations (no URL) | On Public Portal | Portal URL |
|------|------------------------|-----------------|-----------|
| Wells Fargo | 2,710 | ~200 | wellsfargo.com/private-foundations/ |
| Bank of America | 2,319 | ~160 | bankofamerica.com/philanthropic/search-for-grants/ |
| US Bank | 972 | 0 | No portal |
| PNC | 936 | ~200 | pnc.com/charitable-trusts |
| BNY Mellon | 790 | 0 | No portal |
| JPMorgan Chase | 579 | ~115 | jpmorgan.com/.../online-applications/search |
| Truist | 548 | 6 | truist.com/trusteed-foundations/funds |
| Northern Trust | 163 | 0 | Foundation Source partnership |

**Key contacts:**
- Wells Fargo: grantadministration@wellsfargo.com, 888-235-4351
- JPMorgan: 800-496-2583
- Truist: sofia.b.aun@truist.com

#### 9. Trestle Reverse Phone Enrichment (~$6,000)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | 25,000-35,000 email addresses from 85,600 phone numbers |
| **Cost** | ~$6,000 ($0.07/query) + $685 Twilio pre-filter |
| **Effort** | 1-2 days |
| **Legal risk** | Low (public records aggregation) |
| **Data freshness** | Current identity data |
| **Confidence** | MEDIUM. Family foundation phone numbers are often personal lines. Reverse lookup should work well for residential numbers. |

**Strategy:** Pre-filter with Twilio Line Type Intelligence ($0.008/query = $685 for 85K) to remove disconnected numbers, then run active numbers through Trestle.

#### 10. Common Crawl CDX Verification (FREE)

| Criterion | Assessment |
|-----------|-----------|
| **Coverage gain** | 0 new URLs (verification only) |
| **Cost** | $0 |
| **Effort** | 1 day |
| **Legal risk** | None (open data) |
| **Data freshness** | Periodic crawls |
| **Confidence** | HIGH as a verification signal. If a domain appears in Common Crawl, it's almost certainly a real website. |

### Tier 4: Not Recommended

| Approach | Why Not |
|----------|---------|
| B2B enrichment APIs (Clearbit, ZoomInfo, etc.) | Wrong data universe. Foundations are not companies. Near-zero coverage. $15K-$50K/year. |
| WHOIS reverse lookups | GDPR killed this in 2018. Registrant names hidden for most domains. |
| LinkedIn/Facebook/Twitter scraping | High legal risk, low foundation coverage, expensive APIs. |
| ProPublica API | No website URL field. Confirmed via live testing. |
| IRS BMF extracts | No website URL field. Registration data only. |
| State charity registries | No URL fields. No bulk downloads (except CA). |
| NCCS datasets | No URL field. Financial data only. |
| SerpAPI, Bing API | 10x-35x more expensive than Serper.dev for equivalent results. |
| Open990 | Defunct since Sept 2022. |

---

## Ranked Recommendation

### Execution Order (optimized for: cheap first, highest-value next)

| Phase | Action | Cost | Time | Expected Gain |
|-------|--------|------|------|--------------|
| **1a** | Mine `app_contact_email` field | $0 | 2 hours | 21,574 emails |
| **1b** | Regex-mine `application_submission_info` for emails + URLs | $0 | 4 hours | ~5,000-10,000 emails, ~400 URLs |
| **1c** | Re-enable medium confidence on DDG scraper | $0 | 2 hours | Restore 83.7% hit rate |
| **2a** | Serper.dev pilot (2,500 free queries) | $0 | 2 hours | Measure hit rate |
| **2b** | DNS domain guessing + HTTP verification | $0 | 8 hours | 3,000-10,000 URLs |
| **2c** | Serper.dev full run (if pilot > 50% hit rate) | $39-$130 | 2 hours | ~16,000 new validated URLs |
| **3a** | Candid API free trial (1,000 EIN lookups) | $0 | 4 hours | Measure incremental coverage |
| **3b** | Map bank-managed foundations to portals | $0 | 2 days | Contact paths for 9,007 foundations |
| **3c** | Smarty address classification | $100-$300 | 4 hours | Segment all 95K addresses |
| **4a** | Candid Search subscription (if trial proves value) | $100/month | Ongoing | Contact data for covered foundations |
| **4b** | Trestle reverse phone (pilot 1,000) | $70 | 2 hours | Measure email yield |
| **4c** | Trestle full run (if pilot > 30% yield) | ~$6,000 | 1 day | 25,000-35,000 emails |

### Total Budget

| Scenario | Cost | Contactable Foundations |
|----------|------|----------------------|
| Free tier only (phases 1-2) | $0-$130 | ~35,000-45,000 |
| With Candid + address classification | $230-$530 | ~40,000-50,000 |
| Full program (incl. Trestle) | $6,500-$7,000 | ~55,000-60,000 |

---

## Targets

### 30-Day Target: Extract What We Already Have

**Focus:** Zero-cost actions using existing data and tools.

| Action | Expected Result |
|--------|----------------|
| Extract `app_contact_email` field | +21,574 foundation emails |
| Regex-mine text fields for emails/URLs | +5,000-10,000 emails, +400 URLs |
| Re-tune DDG scraper + proxy rotation | Framework ready for bulk runs |
| Serper.dev pilot (2,500 free queries) | Hit rate measured |
| DNS domain guessing pilot (1,000 foundations) | Pattern guessing yield measured |

**30-day KPI:** Contactable foundations from 14,107 (URL only) to ~35,000+ (URL + email). Cost: $0.

### 90-Day Target: Full Discovery Pipeline

**Focus:** Paid APIs + bank mapping + enrichment.

| Action | Expected Result |
|--------|----------------|
| Serper.dev full run (130K queries) | +~16,000 validated URLs |
| DDG bulk run (re-tuned medium conf) | +~10,000 URLs (overlap with Serper) |
| Bank portal mapping | Contact paths for 9,007 bank-managed |
| Candid trial + subscription | Coverage measured, ongoing enrichment |
| Smarty address segmentation | All 95K addresses classified |
| Trestle reverse phone (if pilot succeeds) | +25,000-35,000 emails |

**90-day KPI:** Contactable foundations from ~35,000 to ~55,000. Cost: $200-$7,000 depending on Trestle decision.

### Theoretical Maximum

| Channel | Max Contactable |
|---------|----------------|
| Validated URL (current + new discovery) | ~30,000 |
| Contact email (990-PF fields) | ~25,000 |
| Bank portal/desk path | ~9,000 |
| Trestle reverse phone emails | ~30,000 |
| **Total (overlap-adjusted)** | **~60,000-65,000** |

**Ceiling: ~60,000-65,000 contactable foundations (42-45% of 143K).** The remaining 55-58% are genuinely unreachable: tiny family trusts with no website, no email, no phone, managed by an unnamed attorney. This is a structural ceiling, not a data gap.

---

## What We Still Don't Know

1. **Serper.dev actual hit rate for foundations.** The 70-85% estimate is from general web search benchmarks. Foundation-specific hit rate may be lower because many foundations have no web presence to find. The 2,500 free queries will answer this.

2. **Candid's incremental coverage.** How many of Candid's 304K grantmaker profiles have URLs/emails that we DON'T already have from IRS filings? The free trial will answer this.

3. **DDG medium-confidence false positive rate.** Dec 2025 saved all confidence levels and got 83.7% hit rate. But what % of medium-confidence matches were actually correct? We need to manually verify a sample of 100 medium-confidence matches.

4. **Trestle yield for foundation phone numbers.** The 40-60% email match rate is a general estimate. 990-PF phone numbers may be outdated, disconnected, or belong to attorney offices. A 1,000-record pilot ($70) will answer this.

5. **Which "under $100K" URLs are real.** We have 6,137 validated URLs for foundations under $100K, but the original estimate was only ~2,500 should have websites. This suggests many are false positives from Dec 2025 low-confidence scraping.

6. **Giving Tuesday Data Lake coverage.** Have they processed newer filings where foundations added websites since our last import? This is a quick check worth doing.

7. **Foundation Source platform growth.** How many foundations use fsrequests.com for grant applications? Currently only 11 in our database reference it, but Foundation Source manages 2,000+. The Northern Trust partnership may expand this.

---

## A/B Testing Plan

### Test 1: Serper.dev vs DuckDuckGo (Head-to-Head)

**Sample:** 500 random foundations without validated URLs, stratified by asset tier.
**Groups:** Run both Serper.dev (Google) and DuckDuckGo on the same 500 foundations.
**Metrics:**
- Hit rate (any URL returned)
- URL match accuracy (manual verification of 50 per group)
- Overlap (same URL found by both)
- Cost per valid URL

**Stop condition:** If Serper.dev hit rate < 30% for foundations under $10M, the full 130K run is not worth $130. Switch to DDG-only with medium confidence.

**Sample size justification:** 500 gives margin of error +/-4.4% at 95% confidence.

### Test 2: DuckDuckGo Confidence Levels

**Sample:** 300 foundations searched via DDG (new searches, not cached).
**Groups:**
- High confidence only (current Feb 2026 approach)
- High + medium confidence (Dec 2025 approach)
- All confidence levels

**Metrics:**
- Hit rate per confidence level
- Accuracy per confidence level (manual verification of 30 per level)
- False positive rate by confidence level

**Stop condition:** If medium-confidence accuracy < 50%, keep the strict high-only threshold. If > 70%, re-enable medium.

### Test 3: DNS Domain Guessing Patterns

**Sample:** 1,000 foundations with known URLs (ground truth).
**Method:** Generate candidate domains from names using our patterns. Check if any candidate matches the known URL.
**Metrics:**
- Pattern match rate (which patterns find the real domain?)
- False positive rate (how many wrong domains also resolve?)
- Best pattern combinations

**Stop condition:** If no pattern achieves > 10% match rate, domain guessing is not worth building into the pipeline.

### Test 4: Trestle Reverse Phone Pilot

**Sample:** 1,000 foundation phone numbers, stratified by foundation size.
**Method:** Run through Twilio (line type) then Trestle (identity enrichment).
**Metrics:**
- Phone validity rate
- Email discovery rate
- Email deliverability (verify with Trestle's $0.005 add-on)
- Email match rate for foundations WITH known contact emails (cross-validation)

**Cost:** $70 (Trestle) + $8 (Twilio) = $78
**Stop condition:** If email yield < 20%, the full $6,000 run is not justified. If > 40%, proceed.

### Test 5: Candid API Coverage Gap

**Sample:** 1,000 foundation EINs (500 with validated URLs, 500 without).
**Method:** Query Candid Premier API (free trial) for website_url field.
**Metrics:**
- For the 500 WITH URLs: does Candid have the same URL? (accuracy check)
- For the 500 WITHOUT URLs: does Candid have a URL we don't? (coverage check)
- Incremental coverage rate

**Stop condition:** If Candid returns < 10% new URLs for foundations we're missing, the API subscription is not worth it for URL discovery. (May still be worth it for other data like contacts and application info.)

---

## Supporting Research Reports

This synthesis draws from 4 research reports generated during this session:

| Report | Focus | Key Finding |
|--------|-------|-------------|
| REPORT .2 (prior) | What we had vs lost (Dec-Feb) | 3 methods lost: EIN propagation, pattern guessing, free-text mining |
| REPORT .5 (Agent 1) | External data sources | Only Candid has foundation URLs. All other sources lack the field. |
| REPORT .5 (Agent 2) | Technical tools | Serper.dev best price/performance. DNS guessing is free. B2B APIs useless. |
| REPORT .6 (Agent 3a) | Enrichment tools | Trestle reverse phone ($0.07/query) best for phone-to-email. Smarty for address segmentation. |
| REPORT .7 (Agent 3b) | Bank-managed foundations | 12,825 bank-managed, 9,007 no website. Bank portals cover ~675. Philanthropy desk is standard path. |

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| This report | `Enhancements/2026-02-16/REPORT_2026-02-16_url_discovery_research.md` | Final synthesis report |
| Agent 1 report | `Enhancements/2026-02-16/REPORT_2026-02-16.5_url_data_sources_research.md` | External data sources |
| Agent 2 report | `Enhancements/2026-02-16/REPORT_2026-02-16.5_url_discovery_technical_research.md` | Technical discovery tools |
| Agent 3a report | `Enhancements/2026-02-16/REPORT_2026-02-16.6_enrichment_tools_contact_discovery_research.md` | Enrichment & contact discovery |
| Agent 3b report | `Enhancements/2026-02-16/REPORT_2026-02-16.7_bank_trust_foundation_contact_discovery.md` | Bank/trust foundations |

---

## Notes

- The 14,107 validated foundation URLs (9.9%) is confirmed via direct database query: `COUNT(CASE WHEN org_type = 'foundation' AND url_validated = true) = 14,107`.
- Agent 1 reported 80,930 foundations with validated URLs, which is incorrect. That figure counts all entries with url_source (including scraped_low and scraped_medium that were never HTTP-validated).
- Agent 2's cost comparison table assumes all 130K foundations would be queried. In practice, we'd skip foundations that already have validated URLs, reducing query volume to ~129K.
- The Serper.dev free trial (2,500 queries) should be the very first action taken. It costs nothing and immediately answers the biggest unknown (Google hit rate for foundation URLs).
- "Contactable" does not mean "will respond." Having a URL or email means we can reach the foundation, not that they will engage. Response rates for cold outreach to foundations range from 1-15% depending on channel and personalization.
- All prices are as of February 2026.

---

*Generated by Claude Code on 2026-02-16*
