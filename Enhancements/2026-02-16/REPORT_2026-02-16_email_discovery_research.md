# Email Discovery From URLs: Research Report

**Date:** 2026-02-16
**Prompt:** Research how to significantly improve email yield from orgs that HAVE websites (currently 15-30%)
**Status:** Complete
**Owner:** Aleck Kleinman

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial research (3 parallel agents + synthesis) |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Pre-Research Baseline and Revised Ceiling Estimates](#2-pre-research-baseline-and-revised-ceiling-estimates)
3. [Scraper Improvement Approaches](#3-scraper-improvement-approaches)
4. [Non-Scraping Email Discovery Approaches](#4-non-scraping-email-discovery-approaches)
5. [Validation Improvements](#5-validation-improvements)
6. [Foundation Sales Pipeline Recommendation](#6-foundation-sales-pipeline-recommendation)
7. [Nonprofit Sales Pipeline Recommendation](#7-nonprofit-sales-pipeline-recommendation)
8. [Compounding Model](#8-compounding-model)
9. [A/B Testing Plan](#9-ab-testing-plan)
10. [What We Still Don't Know](#10-what-we-still-dont-know)

---

## 1. Executive Summary

### Five Key Insights

1. **Our biggest untapped asset is IRS data, not better scraping.** We have 8,662 unique foundations with real email addresses already sitting in `pf_returns.app_contact_email`, plus 26.3M officer name records across 791K orgs. Mining this existing data is zero-cost and could match or exceed what web scraping produces.

2. **Pattern inference + SMTP verification is the highest-ROI new capability.** For foundations (1-10 employees), `{first}@domain` accounts for 61-65% of email patterns. Combined with our officer name roster and SMTP probing, this approach could reach 50-65% discovery from name+domain alone, versus our current 15-30% from scraping.

3. **Scraper improvements are additive but hit a ceiling at ~50%.** Better page discovery (sitemaps), footer extraction, CSS obfuscation decode, and Playwright for JS sites can push scraper yield from ~25% to ~45-50%. Beyond that, 15-25% of sites simply have no extractable email (forms only), and we cannot improve past that with scraping alone.

4. **Verification is cheap and essential.** MillionVerifier at $129/100K emails is the clear winner. Catch-all domains (15-38% of all domains) bounce at 27x the rate of verified addresses. Without verification, our outreach will damage sender reputation.

5. **Foundation and nonprofit pipelines need different strategies.** Foundations: we need decision-maker emails (not grants@ inboxes), contacts are stable (~12% annual turnover), and IRS officer data is our key advantage. Nonprofits: we need ED/development staff, contacts churn faster (~21% turnover), and volume is 19x larger (228K vs 12K).

### Three Recommended Actions

1. **Mine `pf_returns.app_contact_email` immediately.** 8,662 foundations already have emails in our database that we have never used. Filtering junk values and deduplicating gives us a head start before any new scraping or API calls. Effort: 2-3 hours. Cost: $0.

2. **Build a pattern inference + SMTP verification engine.** Use MailScout (Python, MIT licensed) to generate email candidates from officer name + domain, verify via MillionVerifier bulk upload. Target the 14K foundation domains first. Estimated cost: $200-400 total (VPS + verification). Expected yield: 50-65% of domains with at least one verified email.

3. **Upgrade the scraper with 5 zero-cost improvements before the next full run.** Sitemap parsing, footer/header extraction, CSS obfuscation decode, extruct-based structured data, and expanded page limits. Combined lift: +15-25 percentage points. Effort: ~16 hours total. Cost: $0.

### One "Don't Pursue" Recommendation

**Do not invest in WHOIS data, image OCR for emails, or self-hosted SMTP verification infrastructure.** WHOIS is privacy-redacted for 95%+ of .org domains. Image-based emails are <0.5% prevalent on nonprofit sites. Self-hosted SMTP verification (Reacher at $749/mo or bare VPS) is more expensive, more complex, and less accurate than MillionVerifier ($129/100K). Also skip: Google cached pages (feature removed July 2025), RocketReach ($48K+ for 228K lookups), Clearbit/Breeze (HubSpot lock-in, credits expire monthly).

---

## 2. Pre-Research Baseline and Revised Ceiling Estimates

### Pre-Research Hypotheses (Written Before External Research)

**Breakdown of the 70-85% zero-yield sites:**

| Category | Pre-Research Estimate | Post-Research Revision |
|----------|----------------------|----------------------|
| JS-rendered (recoverable with Playwright) | 15-20% | 15-20% (confirmed) |
| Contact form only (no email on page) | 20-25% | 15-25% (slightly wider range) |
| Email present but extraction missed | 10-15% | 15-20% (higher than expected: CSS obfuscation, microdata, footer-only emails) |
| Genuinely email-less sites | 25-35% | 20-30% (some have emails in PDFs, privacy policy, linked documents) |
| Other (CAPTCHAs, rate limiting, broken) | 5-10% | 5-10% (confirmed) |

**Ceiling yield estimates:**

| Pipeline | Pre-Research Estimate | Post-Research Revision | Basis |
|----------|----------------------|----------------------|-------|
| Foundation (scraping only) | 45-55% | 45-50% | Form-only ceiling + JS rendering cap |
| Foundation (scraping + pattern inference + IRS data) | Not estimated | 70-80% | Waterfall: scrape + IRS email + pattern inference + verification |
| Nonprofit (scraping only) | 50-65% | 50-60% | Higher baseline URL coverage, similar ceiling constraints |
| Nonprofit (scraping + commercial supplement) | Not estimated | 55-70% | Less IRS data advantage for nonprofits; commercial APIs fill gaps |

**Pattern inference accuracy estimate:**

| Metric | Pre-Research | Post-Research |
|--------|-------------|---------------|
| Pattern detection success | 40-50% | 60-70% (SMTP probing works unless catch-all or blocked) |
| Pattern accuracy when detected | 70-80% | 85-95% (Interseller data: 70%+ of org emails follow one pattern) |
| Name-to-email accuracy | 50-60% | 50-65% (degraded by ALL CAPS, turnover, nicknames) |

**Catch-all domain prevalence:**

| Metric | Pre-Research | Post-Research |
|--------|-------------|---------------|
| Nonprofit domains | 30-40% | 15-38% (wide range; Google Workspace nonprofits are NOT catch-all) |
| Foundation domains | 15-25% | 20-35% (small foundations on shared hosting often are catch-all) |

### Pre-Mortem: Why Improvements May Plateau

**Why yield improvements plateau quickly:**
1. After fixing JS rendering (biggest single gap at +5-8%), remaining gaps are structural: form-only sites, genuinely email-less sites, and image/PDF-embedded emails are each smaller and harder to solve.
2. Catch-all domains (15-38%) cap verification accuracy. For these domains, we can never confirm if an email works without actually sending to it.
3. Foundation sites are often minimal: family foundations and small trusts rarely have staff pages or contact emails.

**Ceiling constraints on email discovery from websites:**
1. 15-25% of sites have contact forms only and no extractable email. This is a hard ceiling on scraping.
2. Only 54% of Tier 1 foundations (6,816 of 12,653) have live websites at all. Scraping cannot reach the other 46%.
3. Even with all improvements, web scraping max for foundations: 54% have URLs x 85% have emails x 80% extraction success = ~37% of all Tier 1 foundations.

**Where more extraction methods hit diminishing returns:**
1. After Playwright + improved regex + footer extraction + CSS decode + sitemap parsing, the remaining missed emails are in images, PDFs behind logins, or simply don't exist. Each additional technique adds <1%.
2. Crawling 10+ pages per site has diminishing returns: 90%+ of contact info appears on 2-3 predictable pages.
3. Multiple verification layers compound cost but not accuracy: after MillionVerifier, a second service gives maybe 1-2% lift.

---

## 3. Scraper Improvement Approaches

These improvements make our existing pipeline (scripts 04-07) better at extracting emails from websites we already crawl.

### 3.1 Sitemap.xml Parsing for Page Discovery

**What it is:** Before crawling, fetch `/sitemap.xml` and `/robots.txt` to discover all pages on the site. Filter for contact-relevant URLs (`/contact`, `/team`, `/staff`, `/grants`, `/apply`, `/directory`, `/people`).

**Yield improvement:** +5-8%

**False positive / bounce rate:** No impact (better page discovery, not email validation change).

**Implementation effort:** 4-6 hours. Use `lxml` or `ultimate-sitemap-parser` to handle standard and WordPress sitemaps.

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | High: foundation sites often have grant/apply pages at non-obvious URLs | Medium: nonprofit sites are more standardized |

### 3.2 Footer/Header Targeted Extraction

**What it is:** Extract `<footer>` and `<header>` HTML elements first and give emails found there a confidence bonus (+0.10). Foundation/nonprofit sites almost universally put primary contact email in the footer.

**Yield improvement:** +3-5%

**False positive / bounce rate:** Low risk. Footer emails are the org's chosen contact method.

**Implementation effort:** 2-3 hours. BeautifulSoup CSS selectors for `footer`, `[role="contentinfo"]`, `[class*="footer"]`.

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | High: many foundation sites have email ONLY in footer | High: same pattern |

### 3.3 CSS Obfuscation Decode

**What it is:** Handle 4 common anti-scraping techniques:
- Strip `display:none` / `visibility:hidden` elements (blocked 100% of spambots in published study)
- Detect `direction:rtl` / `unicode-bidi:bidi-override` and reverse text
- Strip HTML comments inserted mid-email (blocked 98% of bots)
- HTML entity decoding (already handled by BeautifulSoup)

**Yield improvement:** +2-4%

**False positive / bounce rate:** Low. These are real emails being deliberately hidden from bots.

**Implementation effort:** 3-4 hours. Moderately common on WordPress sites with security plugins.

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | Medium: WordPress security plugins common | Medium: same |

### 3.4 Unified Structured Data Extraction (extruct)

**What it is:** Replace our JSON-LD-only extractor with the `extruct` library, which extracts JSON-LD, Microdata (`itemprop="email"`), RDFa, Open Graph, and Microformat data in one pass. Catches emails in `ContactPoint` nested objects and Schema.org `Person` markup.

**Yield improvement:** +2-3%

**False positive / bounce rate:** Very low. Structured data emails are machine-readable by design.

**Implementation effort:** 2-3 hours. Drop-in replacement, well-maintained library (by Zyte/Scrapinghub).

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | Medium: larger foundation sites more likely to have structured data | Medium-High: nonprofits with SEO-aware developers |

### 3.5 Hybrid HTTP/Playwright for JS-Rendered Sites

**What it is:** Detect pages that need JavaScript rendering (React, Next.js, Vue, Angular) during the initial HTTP fetch, then re-fetch those pages with Playwright headless browser.

**Yield improvement:** +5-8% overall (recovers emails from the 15-20% of sites that are currently returning empty HTML).

**False positive / bounce rate:** No change (same extraction on rendered HTML).

**Implementation effort:** 6-8 hours. Playwright-Python is first-class. Block images/fonts to speed rendering 30-60%. Close browser contexts every ~50 pages to prevent memory leaks.

**Performance:** 100-200 pages/hour with Playwright vs 2,000-5,000 with httpx. Hybrid approach keeps 85% of sites on fast HTTP path.

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | High: 15-20% of foundation sites use JS frameworks | Medium: nonprofits more likely to use WordPress (no JS needed) |

### 3.6 Expanded Page Crawl Limit

**What it is:** Increase from 4 to 6-8 internal pages per org. Add: privacy policy (GDPR/CCPA data controller email), donate/support, news/press (press contact emails).

**Yield improvement:** +1-3%

**False positive / bounce rate:** Low. Privacy policy emails are often generic but valid.

**Implementation effort:** 1-2 hours. Add URL patterns to the existing page discovery list.

### Summary: Scraper Improvements

| # | Approach | Yield Lift | Effort | Cost | Priority |
|---|---------|-----------|--------|------|----------|
| 1 | Sitemap.xml parsing | +5-8% | 4-6 hrs | $0 | High |
| 2 | Footer/header extraction | +3-5% | 2-3 hrs | $0 | High |
| 3 | CSS obfuscation decode | +2-4% | 3-4 hrs | $0 | Medium |
| 4 | Structured data via extruct | +2-3% | 2-3 hrs | $0 | Medium |
| 5 | Hybrid HTTP/Playwright | +5-8% | 6-8 hrs | $0 | High |
| 6 | Expanded page limit (4 to 6-8) | +1-3% | 1-2 hrs | $0 | Low |

**Combined estimated lift: +18-31 percentage points** (not purely additive due to overlap). Realistic combined: +15-25 pp, bringing scraper yield from ~25% to ~40-50%.

---

## 4. Non-Scraping Email Discovery Approaches

These are parallel tracks that use domain/name data we already have, without depending on the website scraper.

### 4.1 IRS 990-PF Application Contact Emails (Already in DB)

**What it is:** The `pf_returns.app_contact_email` field contains email addresses that foundations report on their 990-PF filings for grant application inquiries.

**Coverage:** 8,662 unique foundations have real email addresses (containing `@`). Another ~3,900 have junk values ("N/A", "NA", "NONE") that need filtering. Additional fields: `app_contact_name` (155K rows), `app_contact_phone` (149K rows).

**Cost at our scale:** $0 (data already in our database).

**Accuracy / deliverability:** These emails are self-reported by the foundation. Many are personal emails (gmail.com, aol.com) of trustees or attorneys, not organizational emails. Expect 60-70% deliverability after verification (some are years old).

**False positive rate:** Low. These are real emails the foundation chose to report.

**Bounce risk:** Medium. IRS data can be 1-3 years old. Recommend verification before use.

**Legal/TOS considerations:** Public IRS data. No restrictions on use.

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | **Critical.** 8,662 foundations = 6% of all, but likely 20%+ of open-to-applications foundations | Not applicable (990-PF only) |

### 4.2 Email Pattern Inference (Officer Name + Domain)

**What it is:** Generate candidate email addresses by combining IRS officer names with the organization's domain and common email patterns ({first}@, {f}{last}@, {first}.{last}@). Verify each candidate via SMTP or bulk verification service.

**Coverage:** Applies to all 14K foundation domains with validated URLs + 791K unique EINs with officer data. For foundations (1-10 employees), `{first}@domain` accounts for 61-65% of patterns.

**Cost at our scale:**
- 12K foundations: ~$37-74 (MillionVerifier for generated candidates) + $5-10/mo VPS for SMTP pattern detection
- 228K nonprofits: ~$129-200 (MillionVerifier) but we lack officer names for most nonprofits

**Accuracy / deliverability:** When the pattern is correctly detected, 85-95% of generated emails are valid. Main failure modes: person left org, unusual name handling, catch-all domain.

**False positive rate:** 5-15%. Mitigated by SMTP verification (which catches 85-90% of false positives on non-catch-all domains).

**Bounce risk:** Low after verification. Catch-all domains are the wild card (can't verify individual addresses).

**Legal/TOS considerations:** Generating and verifying email addresses is standard B2B practice. No TOS violation; emails are verified, not scraped from a service.

**Key challenge:** 77% of IRS officer names are ALL CAPS and 15.5% have truncated titles. Need name cleaning (Python `nameparser` library).

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | **Very high.** We have officer names for 143K+ foundations | Low for bulk (no 990/990-EZ officer data for most nonprofits in our DB) |

### 4.3 Hunter.io Domain Search API

**What it is:** Commercial API that returns all known email addresses for a given domain, with names, titles, sources, and confidence scores. Database of 150M+ emails built from crawling 30M web pages daily.

**Coverage:** Unknown for nonprofit/foundation sectors specifically (optimized for B2B tech). Likely 30-50% hit rate for foundation domains.

**Cost at our scale:**
- 12K foundations: Business plan at $399/mo covers 50K searches (one month)
- 228K nonprofits: Impractical at standard pricing ($15K+ estimate)

**Accuracy / deliverability:** Returns both "verified" (found publicly) and "guessed" (pattern-based) emails. Verified emails have high deliverability. Guessed emails need separate verification.

**False positive rate:** Moderate for "guessed" emails. Low for "verified."

**Legal/TOS considerations:** Standard commercial service. GDPR-compliant (individuals can opt out of their database).

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | High for gap-filling after our own methods | Low at scale (too expensive for 228K) |

### 4.4 Apollo.io Free Tier

**What it is:** 275M+ contact database with 10K email credits/month on the free tier. Uses waterfall enrichment from 18 data providers.

**Coverage:** Broad B2B coverage. Unknown nonprofit-specific coverage.

**Cost at our scale:** $0 (free tier, 10K/month). Bottleneck is export credits (only 10/month on free tier).

**Accuracy / deliverability:** Claims 98.5% verified accuracy. Export credits severely limit bulk use.

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | Low (export credit bottleneck) | Low (same bottleneck) |

### 4.5 Voila Norbert (Name + Domain Lookup)

**What it is:** Takes a person name + domain and finds the correct email using proprietary methods. Only charges for successful finds. Highest independent accuracy rating (92% per Ahrefs, 1.3x more accurate than Hunter).

**Cost at our scale:**
- 12K foundations: Advisor plan at $199/mo (covers 15K lookups)
- Verification-only: $0.003/email (228K = $684)

**Accuracy / deliverability:** 98% deliverability on verified emails.

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | High (name+domain matches our IRS data exactly) | Medium (need to source names first) |

### 4.6 theHarvester (OSINT Email Discovery)

**What it is:** Open-source Python tool that aggregates emails from 40+ public sources (Google, Bing, DuckDuckGo, PGP keyservers, GitHub, etc.) for a given domain.

**Cost at our scale:** $0. Free and open source.

**Coverage:** Only finds emails already publicly posted somewhere. Supplemental to our scraper, not a replacement.

**Accuracy / deliverability:** Emails are real (found in the wild) but may be stale.

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | Medium (5-15% supplemental) | Medium (10-20% supplemental) |

### 4.7 Apify Contact Scraper Actors

**What it is:** Pre-built scraping actors on the Apify marketplace that extract emails from URLs. Different extraction methods than our scraper may catch emails we miss.

**Cost at our scale:** $0.001-$0.002/page. Pilot test of 1,000 domains: ~$5-10.

| | Foundation relevance | Nonprofit relevance |
|------|---------------------|---------------------|
| Impact | Unknown (diagnostic pilot needed) | Unknown (same) |

### Summary: Non-Scraping Approaches

| # | Approach | Coverage | Cost | Accuracy | Priority |
|---|---------|---------|------|----------|----------|
| 1 | Mine IRS app_contact_email | 8,662 foundations | $0 | 60-70% (after verification) | **Immediate** |
| 2 | Pattern inference + SMTP | 14K foundation domains | $50-100 | 50-65% | **High** |
| 3 | Hunter.io API (gap-fill) | 12K foundations | $399 one-time | 70-85% (verified) | Medium |
| 4 | Voila Norbert | 12K foundations | $199 one-time | 92% | Medium |
| 5 | theHarvester OSINT | 12K-240K | $0 | Variable | Low |
| 6 | Apify pilot | 1K test | $5-10 | Unknown | Diagnostic |
| 7 | Apollo.io free tier | Exploration | $0 | High (limited export) | Low |

---

## 5. Validation Improvements

### 5.1 SMTP Verification Services

**Recommendation: MillionVerifier** for all bulk verification.

| Service | 12K Emails | 240K Emails | Catch-All Detection | Key Advantage |
|---------|-----------|-------------|--------------------|----|
| **MillionVerifier** | ~$37 | ~$129-200 | Yes (not charged) | Cheapest; doesn't charge for catch-all results |
| NeverBounce | ~$50 | ~$720 | Yes (charged) | 99.9% accuracy claim |
| ZeroBounce | ~$75 | ~$600-800 | Yes (charged) | AI abuse scoring |
| EmailListVerify | ~$48 | ~$480 | Yes | Budget option |
| Kickbox | ~$96 | ~$1,440 | Yes (not charged) | Enterprise features |
| Reacher (self-hosted) | $749/mo | $749/mo | Yes (built-in) | Unlimited once licensed |

**Verdict:** MillionVerifier at $129-200 for 240K emails is a fraction of Reacher's $749/month and requires zero infrastructure. Use MillionVerifier for bulk, reserve Reacher's free trial (10K/day) for real-time spot verification.

### 5.2 Catch-All Domain Handling

**What:** 15-38% of domains are catch-all (accept all addresses). Bounce rate for catch-all addresses: ~27% vs ~1% for verified-valid.

**Strategy:**
1. Detect catch-all domains during verification (MillionVerifier flags these for free)
2. Separate into a "risky" tier with lower confidence score
3. For high-value foundation contacts on catch-all domains: use specialized verifiers (BounceBan, claimed 85-98% accuracy within catch-all)
4. Send to catch-all addresses in small batches (5-10% of any campaign) with per-domain bounce monitoring
5. Prefer generic role addresses (info@, contact@) over inferred person addresses on catch-all domains

### 5.3 Freshness and Decay Management

**Email decay rates by sector:**

| Sector | Annual Turnover | Monthly Decay | Re-Verification Frequency |
|--------|----------------|---------------|--------------------------|
| Foundations | 12.3% | ~1%/month | Every 6 months |
| Nonprofits | ~21% | ~2-3%/month | Quarterly |
| General B2B | 23-28% | ~2-3.6%/month | Monthly for active lists |

**Annual re-verification cost (MillionVerifier):**

| List | Frequency | Annual Cost |
|------|-----------|-------------|
| 12K foundations | 2x/year | ~$74 |
| 240K nonprofits | 4x/year | ~$516-800 |
| **Total** | Mixed | **~$600-900/year** |

**Bounce thresholds:** Keep hard bounce rate under 2%. Gmail penalizes at 0.3% spam complaint rate. Immediately suppress hard bounces; suppress soft bounces after 3 consecutive failures.

---

## 6. Foundation Sales Pipeline Recommendation

**Goal:** Reach the person who manages grantee services or capacity-building programs at foundations. Typically a program officer, grants manager, or ED. Not grants@ inboxes (those receive applications).

**Priority order (implement sequentially, each building on the last):**

### Rank 1: Mine IRS Data (Week 1)

**Action:** Extract and clean `app_contact_email` + `app_contact_name` + `app_contact_phone` from pf_returns. Filter junk values ("N/A", "NA", "NONE"). Deduplicate by EIN (take most recent tax year). Verify via MillionVerifier bulk upload.

**Expected yield:** 8,662 foundations with email addresses. After junk filtering and verification: ~5,000-6,000 deliverable contacts.

**Cost:** ~$37 (MillionVerifier for 10K)

**Why first:** Zero development effort. Data already in our database. These are the foundation's chosen contact point for grant inquiries.

### Rank 2: Improve Scraper + Run on Foundation Domains (Weeks 2-3)

**Action:** Implement the 5 zero-cost scraper improvements (sitemap parsing, footer extraction, CSS decode, extruct, expanded pages), then run on all 14K foundation domains with validated URLs.

**Expected yield:** +15-25 percentage points over current 25% baseline = 40-50% of 14K domains = ~5,600-7,000 foundations with scraped emails.

**Cost:** $0 (development time only)

**Why second:** Scraper improvements are free and benefit both pipelines. Run before paid APIs to minimize commercial lookups needed.

### Rank 3: Pattern Inference for Remaining Gaps (Weeks 3-4)

**Action:** For foundation domains where scraping yielded no email:
1. Clean officer names from `officers` table (fix ALL CAPS, expand truncated titles)
2. Detect email pattern per domain (test top 3 patterns via SMTP on a VPS)
3. Generate candidate emails for all officers using detected pattern
4. Verify candidates via MillionVerifier

**Expected yield:** 50-65% of remaining no-email foundations. Adds ~1,500-3,000 more.

**Cost:** ~$50-100 (VPS + MillionVerifier for candidates)

### Rank 4: Commercial API Gap-Fill (Month 2)

**Action:** For high-value foundations still without contacts, use Hunter.io Domain Search API ($399 for 50K searches) and/or Voila Norbert ($199 for 15K name+domain lookups).

**Expected yield:** +10-15% of remaining gaps.

**Cost:** $399-598 one-time

### Rank 5: Hybrid Playwright Pass (Month 2)

**Action:** Re-scrape JS-heavy foundation sites (React/Vue/Angular detected) using Playwright headless browser.

**Expected yield:** +5-8% of the 15-20% of sites that need JS rendering.

**Cost:** $0 (development time)

### Expected Foundation Pipeline Result

| Stage | Cumulative Foundations with Email | % of 12,653 Tier 1 |
|-------|----------------------------------|---------------------|
| Baseline (before work) | ~0 (pipeline not run yet) | 0% |
| After IRS data mining | ~5,000-6,000 | 40-47% |
| After improved scraping | ~7,500-9,500 | 59-75% |
| After pattern inference | ~8,500-11,000 | 67-87% |
| After commercial gap-fill | ~9,000-11,500 | 71-91% |

---

## 7. Nonprofit Sales Pipeline Recommendation

**Goal:** Reach whoever manages fundraising or grant seeking. Typically an ED, development director, or grants manager. Person-name emails ideal; general contact emails fallback.

**Priority order:**

### Rank 1: Improve Scraper + Run on Nonprofit Domains (Weeks 2-4)

**Action:** Same 5 scraper improvements as foundations, then run on 293K nonprofit domains with validated URLs. Process in waves to manage disk space (14GB HTML cache estimate).

**Expected yield:** 40-50% of 293K domains = ~117K-147K nonprofits with scraped emails.

**Cost:** $0 (development time + compute)

**Why first:** Largest pool, free approach, benefits from same scraper work as foundation pipeline.

### Rank 2: Verify + Segment (Week 4)

**Action:** Run all scraped emails through MillionVerifier. Segment results into: valid, catch-all (risky), invalid (suppress).

**Expected yield:** Of ~130K scraped emails, expect ~90K valid, ~25K catch-all, ~15K invalid.

**Cost:** ~$129-200 (MillionVerifier for 130K)

### Rank 3: Generic Role Address Probing (Month 2)

**Action:** For nonprofits without scraped emails, test generic role addresses: info@, contact@, director@, admin@, hello@. Verify each via MillionVerifier.

**Expected yield:** +10-20% of remaining nonprofits. Many orgs have working generic addresses even without them on their website.

**Cost:** ~$50-100 (MillionVerifier for generated candidates)

### Rank 4: Tiered Commercial Supplement (Month 3+)

**Action:** For the highest-value nonprofit prospects (top 10K by ICP score) that still lack contacts:
- Use Hunter.io Domain Search for the domain
- Use Snov.io bulk domain search for remaining gaps ($189 for 20K credits)
- Consider Apify contact scraper as alternative extraction ($0.001/page)

**Expected yield:** +30-50% of targeted tier.

**Cost:** $189-400 for top-tier supplements

### Expected Nonprofit Pipeline Result

| Stage | Cumulative Nonprofits with Email | % of 293K with URLs |
|-------|----------------------------------|---------------------|
| After improved scraping | ~117K-147K | 40-50% |
| After verification/segmentation | ~90K valid + 25K catch-all | 31-39% verified |
| After generic role probing | ~100K-120K valid | 34-41% verified |
| After commercial supplement (top 10K) | +3K-5K high-value | Targeted |

---

## 8. Compounding Model

### How Approaches Layer

The email discovery pipeline is a waterfall where each step catches what the previous steps missed:

```
Foundation Pipeline Waterfall:

Step 1: IRS app_contact_email ──────── catches 40-47% of Tier 1
  │ (remaining: 53-60%)
  ▼
Step 2: Improved web scraping ──────── catches 30-40% of remaining
  │ (remaining: 32-42%)
  ▼
Step 3: Pattern inference + verify ─── catches 40-55% of remaining
  │ (remaining: 19-25%)
  ▼
Step 4: Commercial API gap-fill ────── catches 30-50% of remaining
  │ (remaining: 10-18%)
  ▼
Step 5: Playwright JS re-scrape ────── catches 15-25% of remaining
  │
  ▼
Final: ~71-91% of Tier 1 foundations with at least one email
```

### Where Diminishing Returns Hit

| After Step | Marginal Cost per New Email | Worth It? |
|-----------|---------------------------|-----------|
| Step 1 (IRS data) | ~$0.006 ($37 / 6,000) | Absolutely |
| Step 2 (scraping) | $0 per email (dev time only) | Yes |
| Step 3 (pattern inference) | ~$0.03-0.07 ($100 / 1,500-3,000) | Yes |
| Step 4 (commercial API) | ~$0.40-1.00 ($400 / 400-1,000) | Only for high-value targets |
| Step 5 (Playwright) | $0 per email (dev time) but 10x slower | Selective use |

**Key insight:** Steps 1-3 cover 67-87% of foundations at a total cost of ~$137-174. Step 4 costs $400+ for diminishing marginal returns. The economics strongly favor exhausting free/cheap methods before commercial APIs.

### Compounding Effects

Positive compounding:
- IRS emails provide "known good" emails per domain. These help detect the domain's email pattern, which improves pattern inference for OTHER contacts at the same domain.
- Web scraping provides HTML content that reveals JS rendering need (for Playwright pass) and contact form presence (for flagging form-only sites).
- Verification results feed back into confidence scoring, improving the best-email materialized view.

Negative compounding:
- Catch-all domains remain opaque at every step. Neither scraping, pattern inference, nor verification can confirm individual addresses.
- Bad IRS data (ALL CAPS, old emails) can waste verification credits if not cleaned first.

---

## 9. A/B Testing Plan

### Test 1: IRS Emails vs Scraped Emails (Deliverability)

**Purpose:** Determine which source produces higher-quality contacts for cold outreach.

**Setup:**
- Group A: 200 foundations with emails from IRS `app_contact_email`
- Group B: 200 foundations with emails from web scraping
- Both groups verified via MillionVerifier (valid status only)
- Same email template, same time, same sending domain

**Success metrics:**
- Primary: Bounce rate (target: <2% in both groups)
- Secondary: Open rate, reply rate
- Tertiary: Spam complaint rate (target: <0.3%)

**Sample size:** 200 per group (sufficient for detecting a 5% bounce rate difference at 80% power)

**Stop condition:** Abort if either group exceeds 5% hard bounce rate after 50 sends.

**Cost ceiling:** ~$37 (MillionVerifier for 400 emails) + Instantly.ai subscription ($37/mo)

**Duration:** 1 week sending + 1 week monitoring bounces

### Test 2: Pattern-Inferred Emails vs Commercial API Emails (Accuracy)

**Purpose:** Determine if our DIY pattern inference matches commercial service accuracy before committing to scale.

**Setup:**
- Select 500 foundations with live website URLs where we ALSO found an email via scraping (ground truth)
- Group A: Generate pattern-inferred email using officer name + domain (our method)
- Group B: Look up same domain via Hunter.io Domain Search API
- Compare both to the scraped "ground truth" email

**Success metrics:**
- Match rate vs ground truth (exact email match)
- Verification result distribution (valid, catch-all, invalid)
- Cost per valid email found

**Sample size:** 500 foundations

**Stop condition:** If our pattern inference matches <40% of ground truth, reconsider the approach.

**Cost ceiling:** $0 for Group A (DIY on VPS) + ~$50 for Hunter.io credits (500 searches on Growth plan) + ~$20 MillionVerifier

### Test 3: Improved Scraper vs Current Scraper (Yield)

**Purpose:** Measure actual yield improvement from the 5 scraper upgrades before full-scale deployment.

**Setup:**
- Select 500 foundation domains (mix of known-email and unknown-email sites)
- Group A: Scrape with current pipeline (baseline)
- Group B: Scrape with improved pipeline (sitemap + footer + CSS + extruct + expanded pages)
- Same domains, same timeframe, different pipeline versions

**Success metrics:**
- Yield rate (% of domains producing at least one email)
- Number of unique emails per domain
- Confidence score distribution
- False positive rate (spot-check 50 results manually)

**Sample size:** 500 domains

**Stop condition:** If improved scraper yield is <5 percentage points above baseline, deprioritize remaining improvements.

**Cost ceiling:** $0 (both pipelines run locally)

---

## 10. What We Still Don't Know

### Critical Unknowns

1. **Actual yield at scale.** The 15-30% yield estimate is from smoke-testing 5-10 foundations. True yield across 14K foundation domains could be higher or lower. We need to run the scraper at scale to get real numbers.

2. **IRS email quality at scale.** We found 8,662 foundations with emails in `app_contact_email`, but the sample showed personal emails (gmail, aol, comcast), attorney emails, bank trust officer emails, and institutional contacts. What percentage are actually useful for B2B outreach (vs personal/advisory contacts)?

3. **Nonprofit officer data gap.** We have 26.3M officer records across 791K EINs, but we don't know how many of the 670K nonprofits have officers in our database. The `officers` table covers all form types (990, 990-PF, 990-EZ) but the coverage for small nonprofits may be spotty.

4. **Catch-all prevalence in our specific domains.** The 15-38% range from industry data may not match foundation/nonprofit .org domains. Google Workspace (free for nonprofits, NOT catch-all) vs shared hosting (often catch-all) balance is unknown for our population.

5. **Real-world false positive rate for pattern inference.** Interseller's 85-95% accuracy is for B2B companies with clean name data. Our 77% ALL CAPS + truncated title data may perform worse. Need the 500-foundation A/B test (Test 2) to calibrate.

6. **Hunter.io / Snov.io coverage for nonprofits.** These tools are optimized for B2B tech companies. Coverage for small nonprofits and family foundations is unknown and may be significantly lower than their headline accuracy numbers.

### Moderate Unknowns

7. **How many "contact form only" sites are in our foundation population?** The 15-25% estimate is from general business websites. Foundations may be different (more likely to publish direct contact for grant inquiries, or less likely because they want to control inbound requests).

8. **Email pattern diversity within foundations.** The Interseller data shows small orgs favor `{first}@domain`. But many foundations use their bank/trustee's domain (e.g., `bankofamerica.com`, `usbank.com`), where individual contact emails follow corporate patterns we cannot detect.

9. **Playwright yield on foundation sites specifically.** The 15-20% JS-rendering estimate is from general web data. Foundation sites may be simpler (more static HTML) or more complex (custom React apps) than average.

### Lower-Priority Unknowns

10. **Common Crawl coverage of foundation domains.** Could provide free historical email data, but we don't know how many of our 14K foundation domains appear in the Common Crawl index.

11. **Candid/GuideStar API pricing and nonprofit coverage.** Their Premier API could supplement our nonprofit officer data, but pricing requires a sales conversation.

12. **Board overlap network value.** Our 143K+ foundations' officer data could reveal network hubs (people serving on multiple foundation boards), but the analytical and outreach value of this is unproven.

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| This report | `Enhancements/2026-02-16/REPORT_2026-02-16_email_discovery_research.md` | Synthesized research report (10 sections) |
| Prompt | `Enhancements/2026-02-16/PROMPT_2026-02-16_email_discovery_from_urls.md` | Research prompt (pre-existing) |

Three intermediate agent reports were produced during research (email tools, scraper yield, SMTP verification) and consolidated into this synthesis. Full agent transcripts available in session history.

## Sources

Full source lists are in each agent's detailed report. Key sources:
- Interseller email pattern analysis (5M+ companies)
- Candid/COF 2025 Grantmaker Salary & Benefits Report (foundation turnover: 12.3%)
- Spencer Mortensen email obfuscation study (CSS technique effectiveness)
- ZeroBounce 2025 email list decay report (23-28% annual decay)
- Hunter.io, Snov.io, Apollo.io, Voila Norbert pricing pages (February 2026)
- MillionVerifier pricing ($37/10K, $129/100K)
- Reacher open-source email verification documentation
- TheGrantScout database queries (pf_returns, org_url_enrichment, officers tables)

---

*Generated by Claude Code on 2026-02-16*
