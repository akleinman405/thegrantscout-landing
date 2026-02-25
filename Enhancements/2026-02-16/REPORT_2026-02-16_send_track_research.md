# Phase 5 (Send) & Phase 6 (Track) — Research & Recommendations

**Date:** 2026-02-16
**Prompt:** PROMPT_2026-02-16_send_track_research.md
**Status:** Complete
**Owner:** Claude Code

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial research report: 8 topics, gap analysis, roadmap |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Research Findings by Topic](#research-findings-by-topic)
   - [Topic 1: Subdomain Warm-Up](#topic-1-subdomain-warm-up)
   - [Topic 2: Deliverability & Sender Reputation](#topic-2-deliverability--sender-reputation)
   - [Topic 3: Send Cadence & Timing](#topic-3-send-cadence--timing)
   - [Topic 4: Bounce Management & List Hygiene](#topic-4-bounce-management--list-hygiene)
   - [Topic 5: Response Tracking & Classification](#topic-5-response-tracking--classification)
   - [Topic 6: Follow-Up Automation](#topic-6-follow-up-automation)
   - [Topic 7: Compliance](#topic-7-compliance)
   - [Topic 8: Build vs Buy](#topic-8-build-vs-buy)
3. [Gap Analysis](#gap-analysis)
4. [Pre-Send Checklist](#pre-send-checklist)
5. [Warm-Up Plan](#warm-up-plan)
6. [Build vs Buy Recommendation](#build-vs-buy-recommendation)
7. [Kill Switches](#kill-switches)
8. [90-Day Implementation Roadmap](#90-day-implementation-roadmap)
9. [Files Created/Modified](#files-createdmodified)
10. [Notes](#notes)

---

## Executive Summary

This report answers the question: **what needs to be true before we send the first email from the new system?** It covers 8 research topics across infrastructure, compliance, and strategy, cross-references the audit findings, and provides a concrete 90-day roadmap.

**The single most important finding:** Use **Smartlead Pro** ($78.30/month) instead of building and maintaining custom sending infrastructure. Standalone warm-up for 20 accounts costs $180-400/month. The entire Smartlead platform costs half that and includes warm-up, sender rotation, follow-up automation, bounce handling, OOO detection, and API/webhook integration with PostgreSQL.

**Five launch-blocking items:**

1. Pre-send email verification (previous 6.1% bounce rate is dangerous)
2. Smartlead setup + 2-week warm-up period
3. CAN-SPAM compliance (physical address, unsubscribe mechanism, honest headers)
4. SPF/DKIM/DMARC authentication for all 20 subdomains
5. PostgreSQL-to-Smartlead API integration (bidirectional sync)

**Key numbers:**

| Metric | Target | Warning | Hard Stop |
|--------|--------|---------|-----------|
| Bounce rate | < 2% | > 3% | > 5% |
| Spam complaint rate | < 0.1% | > 0.1% | > 0.3% |
| Daily volume (warm-up complete) | 8-15/subdomain | > 20/subdomain | > 30/subdomain |
| Warm-up duration | 3-4 weeks min | -- | Skipping warm-up |
| Inter-email delay | 60-120 seconds | < 30 seconds | < 5 seconds |
| Follow-up touches | 3 total | > 4 | > 5 |
| Reply rate (target) | 1-3% | < 0.5% | < 0.1% |
| Inbox placement | > 80% | < 60% | < 40% |

---

## Research Findings by Topic

### Topic 1: Subdomain Warm-Up

**Priority:** Tier 1 (launch-blocking)

**Pre-research estimate:** 2-4 weeks, starting at 5/day and doubling weekly.

**Post-research findings:**

Warm-up is non-negotiable, even at 8-15 emails/day per subdomain. Without warm-up, Gmail and Outlook immediately flag new senders as suspicious, resulting in near-zero inbox placement. Recovery from a spam-flagged domain takes months.

**Warm-up schedule for 20 subdomains:**

| Week | Warm-up Emails/Day/Subdomain | Cold Emails/Day/Subdomain | Total/Subdomain |
|------|-----|-----|------|
| 1 | 10-15 | 0 | 10-15 |
| 2 | 15-20 | 2-3 | 17-23 |
| 3 | 15-20 | 5-8 | 20-28 |
| 4 | 10-15 | 8-12 | 18-27 |
| 5+ | 5-10 (maintenance) | 10-15 | 15-25 |

**Simultaneous vs. sequential warm-up:** Warm all 20 subdomains simultaneously but in staggered batches of 5 every 3-5 days. This prevents a sudden spike of 20 new senders appearing at once, which could trigger pattern detection. Schedule:

- Days 1-3: Start warm-up on subdomains 1-5
- Days 4-6: Add subdomains 6-10
- Days 7-9: Add subdomains 11-15
- Days 10-12: Add subdomains 16-20

**Subdomain reputation sharing:** Google Postmaster Tools tracks reputation at the parent domain level. Subdomains within thegrantscout.com share a reputation pool. filteredmessaging.com is a separate pool. This means a flagged subdomain on thegrantscout.com can affect sibling subdomains, but not filteredmessaging.com subdomains.

**Warm-up services comparison:**

| Service | Monthly Cost (20 accounts) | Included with Platform? |
|---------|---------------------------|------------------------|
| Warmup Inbox | $180 ($9/account) | No |
| MailReach | $400 ($20/account) | No |
| Lemwarm | ~$580 ($29/account) | Lemlist only |
| **Smartlead warm-up** | **$0 (included in $78.30/mo Pro)** | **Yes** |
| **Instantly warm-up** | **$0 (included in $77.60/mo Hypergrowth)** | **Yes** |

**Recommendation:** Use Smartlead's built-in warm-up (included free). Standalone warm-up costs 2-5x more than the entire platform. Smartlead's dynamic variable-volume warm-up mimics human patterns better than fixed-volume approaches.

**What happens if we skip warm-up?** At 8-15/day per subdomain, skipping warm-up will not immediately trigger bounces (the volume is too low for hard rejections). Instead, emails silently route to spam folders. You burn through prospects without knowing they never saw your message. By the time you realize deliverability is poor, you have wasted hundreds of sends and contaminated subdomain reputation. Recovery takes 4-8 weeks of careful rehabilitation.

**Sources:**

- [MailReach - Warm Up Email Domain](https://www.mailreach.co/blog/how-to-warm-up-email-domain)
- [Instantly - Email Warmup Guide](https://instantly.ai/blog/email-warmup-guide/)
- [Allegrow - Domain Warm-Up](https://www.allegrow.co/knowledge-base/how-to-warm-up-email-domain)
- [Smartlead - Domain Warm-Up](https://www.smartlead.ai/blog/how-to-warm-up-domain-for-cold-email-outreach)
- [Warmforge - Warm Up Email Domain 2025](https://www.warmforge.ai/blog/how-to-warm-up-email-domain)

---

### Topic 2: Deliverability & Sender Reputation

**Priority:** Tier 1 (SPF/DKIM), Tier 2 (DMARC, monitoring)

**Pre-research estimate:** Bounce rate above 5% risks blacklisting. Good cold B2B bounce rate is under 3%.

**Post-research findings:**

**Bounce rate thresholds:**

| Zone | Bounce Rate | What Happens |
|------|------------|--------------|
| Healthy | < 2% | Normal inbox placement |
| Caution | 2-3% | Investigate list quality |
| Danger | 3-5% | Throttling begins, deliverability degrades |
| Emergency | > 5% | Active blacklisting risk |
| Our previous campaign | **6.1%** | **Above emergency threshold** |

Industry benchmarks: B2B cold email averages 0.39-0.67% bounce rate with proper verification. Our 6.1% from the old campaign was approximately 10x the healthy average. This must not be repeated.

**Google Postmaster Tools:** Set up for all domains. Key metrics to monitor:

- Spam Rate: keep below 0.1%, never reach 0.3%
- Domain Reputation: Low/Medium/High/Bad
- IP Reputation: tracked at Google's shared IP level
- Authentication: SPF, DKIM, DMARC pass rates

**SPF/DKIM/DMARC optimization:**

| Protocol | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| SPF | `v=spf1 include:_spf.google.com ~all` | Same, but use `-all` (hardfail) after warm-up confirms alignment | Each subdomain needs its own SPF record |
| DKIM | 1024-bit key from Google Workspace | 2048-bit key (generate in Admin console) | Each subdomain needs its own DKIM key |
| DMARC | `v=DMARC1; p=none; rua=mailto:dmarc@thegrantscout.com` | Start p=none, upgrade to p=quarantine after 2 weeks of monitoring, then p=reject | Publish at parent domain level |

**DMARC progression:** Start with `p=none` (monitoring only) to confirm all legitimate email passes authentication. After 2 weeks, upgrade to `p=quarantine`. After 4 weeks with clean results, upgrade to `p=reject` for maximum protection.

**Subdomain isolation:** Partial, not complete. Parent domain sets a ceiling on subdomain reputation. If thegrantscout.com has good reputation, its subdomains benefit. If one subdomain tanks, it drags siblings down but does not affect filteredmessaging.com subdomains. Using two separate parent domains provides meaningful isolation.

**Shared IP vs dedicated IP:** At our volume (150-300/day), shared IP (Google Workspace) is correct. Dedicated IPs require 300,000+ emails/month to maintain warm reputation and cost approximately $651/month for 200 mailboxes. Not relevant at our scale.

**Inbox placement:** Google Workspace achieves 80%+ inbox placement for properly configured cold email. ESPs like SendGrid (61%) and Mailgun (26-71%) perform worse because: (1) cold email violates their terms of service, (2) they route through known bulk-sending IPs that spam filters recognize, and (3) they land in the Promotions tab rather than Primary inbox. Google Workspace is the correct infrastructure for cold email at our volume.

**List-Unsubscribe header:** Not required below 5,000 emails/day to personal Gmail accounts. However, strongly recommended because: (1) Gmail displays an "Unsubscribe" button when this header is present, giving recipients an alternative to clicking "Report Spam," and (2) every spam report counts against our 0.1% threshold, while unsubscribe clicks do not.

**Sources:**

- [InfraForge - Bounce Rates Impact](https://www.infraforge.ai/blog/how-bounce-rates-impact-cold-email-deliverability)
- [MailReach - Email Bounce Rate](https://www.mailreach.co/blog/email-bounce-rate)
- [Emailwarmup - Bulk Sender Requirements 2026](https://emailwarmup.com/blog/gmail-and-yahoo-bulk-sender-requirements/)
- [InfraMail - Dedicated vs Shared IP](https://inframail.io/blog-detail/dedicated-ip-vs-shared-ip-for-cold-email-google-workspace-shared-pools-explained)
- [MailKarma - Google Workspace for Cold Outreach](https://www.mailkarma.ai/blog/is-google-workspace-the-best-email-infra-for-cold-outreach)
- [Digital Bloom - B2B Deliverability Benchmarks 2025](https://thedigitalbloom.com/learn/b2b-email-deliverability-benchmarks-2025/)

---

### Topic 3: Send Cadence & Timing

**Priority:** Tier 2 (performance improvement)

**Pre-research estimate:** Tuesday-Thursday, 9-11 AM local time for nonprofit EDs. 10 AM-12 PM for foundation program officers.

**Post-research findings:**

**Optimal send times:**

| Audience | Best Time | Best Days | Peak Performance |
|----------|-----------|-----------|-----------------|
| Nonprofit EDs | 9-10 AM local | Tue-Thu | Thursday 9-11 AM: 44% open rate |
| Foundation officers | 10-11 AM local | Tue-Thu | Tuesday mornings: 27-28% open rate |
| General B2B | 6-9 AM (opens), 10 AM-12 PM (replies) | Tue-Thu | Midweek mornings |

**Days to avoid:** Friday (mental checkout), Monday (inbox overload), weekends.

**Inter-email delay:** 60-120 seconds between individual sends. This is critical for Google Workspace:

- New domains: start at 20-30 emails/day total per account
- Mature Google Workspace inboxes: safely send up to 100/day
- Spreading 10-15 emails across 2-3 hours with 60-120 second gaps mimics human behavior
- Sending 15 emails in 15 minutes (1/minute) is detectably automated

**Daily volume per subdomain assessment:**

| Account Age | Safe Daily Volume | Our Target | Assessment |
|-------------|-------------------|------------|------------|
| Week 1-2 (new) | 2-5 cold emails | 0 (warm-up only) | Correct |
| Week 3-4 | 5-8 cold emails | 5-8 | Conservative, good |
| Week 5-8 | 8-15 cold emails | 8-15 | Appropriate for mature accounts |
| Week 9+ | 15-25 cold emails | 10-15 | Conservative, safe |

15/day per subdomain is appropriate for mature accounts (5+ weeks old). During the first 4 weeks, keep it lower.

**Follow-up timing:** Increasing intervals outperform consistent spacing.

| Cadence | Schedule | Notes |
|---------|----------|-------|
| **Recommended: 3-7 increasing** | Day 0, Day 3, Day 10 | Balances persistence with professionalism |
| Standard 3-7-7 | Day 0, Day 3, Day 10, Day 17 | For 4-touch sequences |
| Aggressive 3-3-3 | Day 0, Day 3, Day 6, Day 9 | Risks annoyance in nonprofit sector |

**Number of touches:** 3 total (initial + 2 follow-ups) is optimal.

| Touch | % of Total Replies | Cumulative |
|-------|-------------------|------------|
| Initial email | 58% | 58% |
| Follow-up 1 (Day 3) | ~28% | ~86% |
| Follow-up 2 / Break-up (Day 10) | ~7-14% | ~93-100% |
| Touch 4+ | Diminishing, 30% drop per touch | Not worth the reputation risk |

Campaigns with 3 email rounds have the highest reply rates at 9.2%. Going beyond 3 follow-ups is not worth the complexity or reputation risk in the nonprofit sector.

**Break-up email:** Works. HubSpot reports 33% response rate on break-up emails. The psychology is loss aversion: signaling you will stop reaching out triggers fear of missing out. Key: keep it 2-3 sentences, remove all sales pressure, express genuine warmth toward their mission.

**Sources:**

- [Zeliq - Best Days for Email Open Rates](https://www.zeliq.com/blog/best-days-for-email-open-rates)
- [Martal - Best Time to Send Cold Emails](https://martal.ca/best-time-to-send-cold-emails-lb/)
- [GMass - Cold Email Throttling](https://www.gmass.co/blog/mail-merge-feature-throttle-your-email-campaign/)
- [Smartlead - Gmail Sending Limits 2026](https://www.smartlead.ai/blog/gmail-sending-limits)
- [Martal - 2025 Cold Email Statistics](https://martal.ca/b2b-cold-email-statistics-lb/)
- [Instantly - Cold Email Cadence](https://instantly.ai/blog/cold-email-cadence/)
- [Close.com - The Breakup Email](https://blog.close.com/the-breakup-email/)

---

### Topic 4: Bounce Management & List Hygiene

**Priority:** Tier 1 (launch-blocking)

**Pre-research estimate:** Two-stage verification (bulk + catch-all secondary pass). Hard limit at 3% bounce rate.

**Post-research findings:**

**Verification tool comparison:**

| Tool | Price (10K) | Price (100K) | Accuracy | Catch-All Handling | Best For |
|------|------------|-------------|----------|-------------------|---------|
| **Reoon** | **$12** | **$94** | 98-99% | Flags as risky | Budget leader, strong accuracy |
| MillionVerifier | $37 | $129 | ~97% | Flags as "Risky" | Credits never expire |
| NeverBounce | $50 | $300 | 97% | Labels as "accept-all" | Large user base |
| ZeroBounce | $100+ | ~$400 | 99.6% | Flags as "catch-all" | Bundled deliverability tools |
| BriteVerify | $80 | ~$500 | 95.2% | Standard flagging | Enterprise (Validity) |
| **BounceBan** | **$21** | Variable | 97%+ for catch-alls | **Classifies 83%+ of catch-alls** as deliverable/undeliverable | Catch-all specialist |

**Recommendation:** Use **Reoon** as primary verifier ($12/10K, cheapest with competitive accuracy). Add **BounceBan** as secondary pass specifically for catch-all addresses. Total cost: ~$22 per 10K emails.

**Two-stage verification workflow:**

1. **Stage 1:** Run entire list through Reoon. Classifies as valid, invalid, catch-all/risky, unknown.
2. **Stage 2:** Remove all "invalid" permanently. Add to global suppression list.
3. **Stage 3:** Run catch-all/risky subset through BounceBan for secondary classification.
4. **Stage 4:** Keep BounceBan "deliverable" catch-alls. Suppress "undeliverable." Send "still-risky" in small test batches (3-5 per subdomain/day) with real-time monitoring.

**Hard vs. soft bounce handling:**

| Bounce Type | Action | Threshold |
|-------------|--------|-----------|
| Hard bounce | Instant permanent suppression across all 20 subdomains | Zero tolerance, never retry |
| Soft bounce | Retry once after 7 days | 3 consecutive soft bounces over 2+ weeks = treat as hard |

**Bounce rate targets:**

| Metric | Target | Warning | Hard Stop |
|--------|--------|---------|-----------|
| Hard bounce rate | < 0.5% | > 1% | > 2% |
| Soft bounce rate | < 1% | > 2% | > 5% |
| Combined bounce rate | < 2% | > 3% | > 5% |

ISPs consider bounce rates under 2% as healthy. At 5%+, ISPs begin throttling or blocking. Our previous 6.1% was in active danger territory.

**Catch-all domains:** 15-38% of nonprofit domains are catch-all. Do not ban them outright (too much market lost). Instead:

- Cap catch-all emails at 20% of any send batch
- Monitor bounce rates per subdomain in real-time
- Suppress on first bounce (zero tolerance for catch-all bounces)
- Test data shows 4% bounce rate from catch-all sends, with 50% open rate and 1% reply rate

**List decay rate (nonprofit sector):** 2.5-3% per month (~30-36% annually). Nonprofit development directors have 18-24 month average tenure. Re-verify the full list quarterly (every 90 days) at $12/run via Reoon.

**Cost of NOT verifying:** At 6.1% bounce rate on 10K emails: 610 bounces, reputation damage that drags open rates from 25% to under 10% within weeks, 4-8 week recovery period, 4,200-16,800 emails lost during recovery. ROI on verification exceeds 10,000%.

**Sources:**

- [Warmup Inbox - Best Verification Tools 2025](https://www.warmupinbox.com/blog/email-marketing/best-email-verification-tools/)
- [Reoon Email Verifier](https://www.reoon.com/email-verifier/)
- [BounceBan - Catch-All Verifier](https://bounceban.com/)
- [NeverBounce Pricing](https://www.neverbounce.com/pricing)
- [ZeroBounce Pricing](https://www.zerobounce.net/email-validation-pricing)
- [Neon One - Nonprofit Email Benchmarks](https://neonone.com/resources/blog/nonprofit-email-benchmarks/)
- [SmarteAI - B2B Data Decay](https://www.smarte.pro/blog/b2b-data-decay)
- [Cognism - Data Decay](https://www.cognism.com/blog/data-decay)
- [Foundation List - 2025 HR Trends Nonprofits](https://www.foundationlist.org/2025-hr-trends/)
- [Oleg Tomenko - Catch-All in Cold Email](https://olegtomenko.com/notes/catch-all-emails)

---

### Topic 5: Response Tracking & Classification

**Priority:** Tier 1 (thread matching, unsubscribe/bounce detection), Tier 2 (AI classification)

**Pre-research estimate:** Gmail API can handle 20 inboxes easily. 5-minute polling is optimal.

**Post-research findings:**

**Gmail API quotas (per-minute, not daily):**

| Limit | Value |
|-------|-------|
| Per-user quota | 15,000 units/minute |
| Per-project quota | 1,200,000 units/minute |
| messages.list cost | 5 units |
| messages.get cost | 5 units |
| messages.send cost | 100 units |

**Quota usage model (20 inboxes, 5-minute polling):**

| Metric | Value |
|--------|-------|
| API calls per poll | 20 (one messages.list per inbox) |
| Quota units per poll | 100 |
| Polls per day | 288 |
| Total calls per day | 5,760 |
| Total units per day | 28,800 |
| Peak per-minute usage | 200 units (1.3% of per-user limit) |
| **Headroom** | **75x current usage** |

Gmail API quotas are a complete non-issue. We could monitor 1,500 inboxes at this polling rate and stay within limits. **If using Smartlead, this polling becomes unnecessary** since the Master Inbox handles reply aggregation automatically.

**Polling frequency:** 5 minutes is optimal. Sub-5-minute reply detection produces 3x higher meeting booking rates vs. 30-minute response times. Push notifications (Gmail Pub/Sub) are not worth the complexity at our volume.

**Response classification (hybrid approach recommended):**

**Stage 1: Rule-based instant triage (cost: $0, latency: instant):**

| Category | Detection Pattern |
|----------|------------------|
| Unsubscribe | "unsubscribe", "remove me", "stop emailing", "opt out", "take me off", "do not contact" |
| Out-of-office | `X-Auto-Reply` header, "out of office", "automatic reply", "OOO", "away from the office" |
| Bounce | `Content-Type: multipart/report`, "delivery failure", "undeliverable", "550", "551" |
| Auto-reply | `Auto-Submitted` header, "this is an automated response" |

Captures 50-60% of all replies (the unambiguous ones).

**Stage 2: Claude Haiku classification (cost: ~$0.12/month):**

- Average reply: 200 tokens input + 100 tokens output = $0.0008/classification
- At 5 classifications/day: $0.004/day = $0.12/month
- Categories: interested, not interested, wrong person, OOO, bounce, unsubscribe, auto-reply, forwarded
- Accuracy: 95%+ for all categories including nuanced replies

**Why hybrid:** Rule-based handles compliance-critical categories (unsubscribe, bounce) at zero latency and zero cost. Haiku handles ambiguity ("Interesting timing! We were just discussing this at our board meeting..."). If Haiku API is temporarily unavailable, the most critical categories still process.

**OOO date parsing:** Use Haiku ($0.0008/parse) rather than maintaining regex patterns. Common formats: "back on March 3rd", "out until 2/28", "returning Monday." Action: pause sequence, reschedule for return date + 1 business day.

**Thread matching (reply-to-campaign linking):**

| Method | Reliability | How |
|--------|------------|-----|
| Gmail Thread ID (primary) | 99%+ for Gmail-to-Gmail | Store threadId on send, match on reply receipt |
| Message-ID / In-Reply-To (secondary) | 99%+ cross-platform | Store Message-ID header, match against In-Reply-To on replies |
| Subject + sender (fallback) | ~90% | Last resort, risk of false positives |

Store on every send: `gmail_thread_id`, `rfc_message_id`, `recipient_email`, `campaign_id`, `sequence_step`, `sent_at`. Match replies using threadId first, then In-Reply-To header fallback.

**Note:** If using Smartlead, thread matching, reply classification, and OOO handling are all built-in. The above is relevant for the DIY PostgreSQL layer that receives webhook events.

**Sources:**

- [Google - Gmail API Usage Limits](https://developers.google.com/workspace/gmail/api/reference/quota)
- [Google - Gmail Push Notifications](https://developers.google.com/workspace/gmail/api/guides/push)
- [Instantly - AI Reply Classification](https://instantly.ai/blog/automate-email-triage-classification-ai/)
- [cloudHQ - Message ID vs Thread ID](https://support.cloudhq.net/understanding-the-distinction-between-message-id-and-thread-id-in-gmail/)
- [Anthropic - Claude Pricing](https://www.anthropic.com/pricing)

---

### Topic 6: Follow-Up Automation

**Priority:** Tier 1 (launch-blocking: follow-ups generate 42% of replies)

**Pre-research estimate:** Daily cron job, 2 follow-ups, increasing intervals. ~200 lines of Python.

**Post-research findings:**

**Sequence design (3 touches total):**

| Touch | Day | Content | Tone |
|-------|-----|---------|------|
| Initial email | 0 | Value proposition, personalized to org | Professional, helpful |
| Follow-up 1 | 3 | Reference original, add one new value point | Conversational, brief |
| Break-up email | 10 | 2-3 sentences, remove sales pressure, wish well | Warm, genuine, no CTA |

**Why 3 touches, not 4:** Touch 1 + Touch 2 capture 86% of all replies. Touch 3 (break-up) captures another 7-14%. Touch 4+ shows 30% drop in per-touch effectiveness and risks being perceived as spam in the relationship-driven nonprofit sector.

**Threading:** All follow-ups must be in the same email thread (Re: original subject, with In-Reply-To header). Same-thread follow-ups: (1) keep context visible, (2) bump conversation to inbox top, (3) mimic genuine human behavior. All major cold email platforms default to same-thread follow-ups.

**Personalization strategy:**

| Level | Example | Impact | Cost | Data Source |
|-------|---------|--------|------|------------|
| Name + Org | "Hi Sarah at Horizons National" | Table stakes | Free | PostgreSQL |
| Sector/Geography | "Working with youth programs in Hawaii" | 26% higher open rates | Free | NTEE codes, state |
| Specific detail | "Your $2.3M budget puts you in range for..." | Strong lift | Free | Revenue data in DB |
| Recent news | "Congrats on the expansion..." | Highest impact | $2.70/day with AI | Web scraping (Phase 2) |

**Recommendation:** Use template-based merge fields from PostgreSQL for launch. Save AI personalization for after baseline reply rates are established.

**Tracking pixels and click tracking: DO NOT USE.**

- Emails with tracking pixels are 15% more likely to be flagged as spam
- Campaigns with tracking disabled achieve **2x the reply rates** vs. tracking enabled
- Apple Mail Privacy Protection (50% of recipients) makes open data unreliable anyway
- Nonprofits are privacy-conscious: covert tracking contradicts their values

Send follow-ups on a timer. Measure success by reply rate only.

**Pause/resume logic:**

| Event | Action |
|-------|--------|
| Reply received | Cancel all pending follow-ups, route to sales |
| Hard bounce | Cancel follow-ups, permanently suppress |
| Unsubscribe | Cancel follow-ups, add to global suppression |
| Out-of-office (with date) | Pause, reschedule for return date + 2 business days |
| Out-of-office (no date) | Pause for 14 days, then resume |

**If using Smartlead:** All follow-up automation, threading, pause/resume, and OOO handling are built-in.

**Sources:**

- [Martal - 2025 Cold Email Statistics](https://martal.ca/b2b-cold-email-statistics-lb/)
- [Woodpecker - Cold Email Statistics](https://woodpecker.co/blog/cold-email-statistics/)
- [Instantly - Cold Email Benchmark Report 2026](https://instantly.ai/cold-email-benchmark-report-2026)
- [MailForge - Open Rate Tracking Hurts Deliverability](https://www.mailforge.ai/blog/how-open-rate-tracking-can-hurt-your-email-deliverability)
- [MailForge - Apple Mail Privacy Impact](https://www.mailforge.ai/blog/how-apple-mail-privacy-impacts-cold-email-tracking)
- [Close.com - The Breakup Email](https://blog.close.com/the-breakup-email/)
- [GrowLeads - Breakup Email Templates](https://growleads.io/blog/breakup-email-templates-outbound-email-outreach/)

---

### Topic 7: Compliance

**Priority:** Tier 1 (CAN-SPAM basics), Tier 2 (CCPA, DMARC), Tier 3 (state monitoring)

**Pre-research estimate:** Physical address, unsubscribe, honest headers required. Google bulk sender rules do not apply below 5,000/day.

**Post-research findings:**

**CAN-SPAM requirements (applies fully to B2B cold email):**

| Requirement | What's Required | Our Implementation |
|-------------|----------------|-------------------|
| Accurate "From" | Real business name and sender address | "Aleck at The Grant Scout" with real subdomain |
| Non-deceptive subject | Truthfully describe email content | "Grant prospecting for [Org Name]" |
| Identify as advertisement | "Clear and conspicuous" disclosure | Footer: "This is a commercial message from The Grant Scout" |
| **Physical address** | Valid postal address in every email | **PO Box or CMRA private mailbox (see below)** |
| **Unsubscribe mechanism** | Clear opt-out, functional 30 days after send | Unsubscribe link in footer, process within 10 business days (instant preferred) |
| Honor opt-outs | Process within 10 business days | Automated, instant suppression across all 20 subdomains |
| Monitor third parties | Responsible for compliance of tools used | We manage our own infrastructure |

**Penalty:** Up to $53,088 per violating email. No private right of action (individual recipients cannot sue under CAN-SPAM). Enforcement by FTC, state AGs, and ISPs.

**Physical address options:**

| Option | CAN-SPAM Compliant? | Monthly Cost |
|--------|---------------------|-------------|
| USPS PO Box | Yes (explicitly listed) | $4.67-30/month |
| CMRA Private Mailbox (UPS Store) | Yes (if registered CMRA) | $10-30/month |
| Virtual Mailbox (Anytime Mailbox) | Yes (if registered CMRA) | $10-30/month |
| Registered Agent only | Legally debatable | $50-200/year |

**Recommendation:** Start with a USPS PO Box ($4.67/month) or upgrade to a CMRA private mailbox for a real street address.

**Google bulk sender requirements:**

The 5,000/day threshold does NOT apply to us. However, some requirements apply to ALL senders:

| Requirement | Applies to Us? | Status |
|-------------|---------------|--------|
| SPF authentication | Yes (all senders) | Must configure for all 20 subdomains |
| DKIM authentication | Yes (all senders) | Must configure for all 20 subdomains |
| DMARC record | Recommended (required for 5K+) | Configure proactively |
| Spam complaint rate < 0.3% | Yes (all senders) | Critical: 1 spam report at 150/day = 0.67% |
| One-click unsubscribe (RFC 8058) | No (5K+ only) | Implement anyway for deliverability benefit |

**Critical math on spam complaints at our volume:**

- At 150 emails/day: 1 spam report = 0.67% (2x danger threshold)
- At 300 emails/day: 1 spam report = 0.33% (above hard limit)
- This is precisely why 20 subdomains is correct: distributes risk

**State-specific laws:**

| State | Key Law | Risk | Action Needed |
|-------|---------|------|--------------|
| California | CCPA/CPRA (B2B exemption expired 1/1/2023) | Medium-low | Privacy policy, honor deletion requests |
| Washington | CEMA (stricter than CAN-SPAM, private right of action) | Low (if subject lines honest) | Honest subject lines, $500/violation |
| New York | No comprehensive email statute | Low | CAN-SPAM compliance sufficient |

**Legal risk assessment:**

| Risk | Probability | Severity |
|------|------------|----------|
| FTC enforcement | Very low | High ($53K/email) |
| Private lawsuit (CAN-SPAM) | **Zero** (no private right of action) | N/A |
| Private lawsuit (WA CEMA) | Very low (honest subject lines) | Low-Medium ($500/violation) |
| ISP enforcement (spam-foldering) | Medium | Medium (deliverability damage) |
| **Reputational damage** | **Medium** | **High** |

**The real risk is reputational, not legal.** Nonprofits and foundations are a tight-knit sector. Getting flagged as "that spam company targeting foundations" damages credibility far more than any fine. Managed through quality targeting, personalization, respectful volume, easy opt-out, and genuine value.

**Sources:**

- [FTC - CAN-SPAM Compliance Guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [Google - Email Sender Guidelines](https://support.google.com/a/answer/81126?hl=en)
- [RedSift - Gmail Enforcement Ramps Up](https://redsift.com/resources/blog/gmails-enforcement-ramps-up-what-bulk-senders-need-to-know)
- [TermsFeed - CCPA B2B Exemption](https://www.termsfeed.com/blog/ccpa-b2b-exemption/)
- [InsideClassActions - State Anti-Spam Laws 2025](https://www.insideclassactions.com/2025/12/03/recent-class-actions-under-state-anti-spam-laws-target-retail-email-marketing-practices-and-raise-questions-about-can-spam-act-preemption/)
- [Faegre Drinker - WA CEMA Ruling Jan 2026](https://www.faegredrinker.com/en/insights/publications/2026/1/federal-court-upholds-washington-state-commercial-electronic-mail-act-against-can-spam-preemption-argument)
- [AWeber - CAN-SPAM Physical Address](https://blog.aweber.com/learn/canspam-physical-address.htm)

---

### Topic 8: Build vs Buy

**Priority:** Tier 1 (launch-blocking decision)

**Pre-research estimate:** A platform at $40-100/month would save enough headaches to justify the cost. Use it for warm-up and sending, keep data in PostgreSQL.

**Post-research findings:**

**Platform comparison (for our setup: 20 accounts, 150-300/day):**

| Feature | Smartlead Pro | Instantly Hypergrowth | Woodpecker Growth | Lemlist Expert |
|---------|--------------|----------------------|-------------------|----------------|
| **Monthly (annual)** | **$78.30** | $77.60 | $146 | $316+ |
| **Monthly (monthly)** | $94 | $97 | $209 | $396+ |
| Email accounts | Unlimited | Unlimited | Unlimited | 20 (4 users x 5) |
| Warm-up included | Yes, unlimited | Yes, unlimited | Yes, 20 slots | Yes |
| Emails/month | 150,000 | 125,000 | 100,000 | Unlimited |
| Active contacts | 30,000 | 25,000 | 10,000 | N/A |
| API included | Yes | Yes | +$20/mo add-on | Yes |
| Sender rotation | SmartSenders (per-mailbox health) | Uniform volume | Adaptive | Standard |
| Reply classification | AI-powered | AI-powered (Unibox) | AI interest detection | Yes |
| Best for | **Technical users, API-first** | Plug-and-play, lead sourcing | Deliverability-obsessed | Multi-SDR teams |

**Why Smartlead wins:**

1. **Cheapest per feature dollar.** $78.30/month vs $77.60 (Instantly) with more emails (150K vs 125K) and more contacts (30K vs 25K)
2. **SmartSenders** provides per-mailbox IP assessment. Critical for 20-subdomain setups
3. **Variable-volume sending** mimics human patterns better than Instantly's fixed-volume
4. **API-first architecture** built for technical users with custom databases (us)
5. **We don't need Instantly's lead database** (160M contacts). We have 143K foundations and 673K nonprofits
6. **Lemlist eliminated:** Per-user pricing at $316+/month is 4x more for no incremental value
7. **Woodpecker eliminated:** $146/month is nearly 2x with tighter limits

**DIY cost comparison:**

| Component | DIY Monthly Cost | Smartlead Cost |
|-----------|-----------------|---------------|
| Warm-up (20 accounts) | $180-400 | $0 (included) |
| Google Workspace (20 accounts) | $120-140 | $120-140 (same either way) |
| MillionVerifier | $6-13 | $6-13 (same either way) |
| Follow-up automation | Build time (32-64 hrs initial) | $0 (included) |
| Bounce handling | Build time | $0 (included) |
| Sender rotation | Build time | $0 (included) |
| Ongoing maintenance | 5-10 hrs/month | 1-2 hrs/month |
| **Total (excl. shared costs)** | **$186-413 + 37-74 hrs/year** | **$78.30 + 12-24 hrs/year** |

**The decisive insight:** Standalone warm-up alone ($180-400/month) costs 2-5x more than the entire Smartlead subscription. DIY is economically irrational at our scale.

**Year 1 savings: $2,736-5,700 plus 72-148 hours of developer time.**

**Hybrid architecture (recommended):**

```
PostgreSQL (source of truth)
  ├── Prospect data, scoring, analytics, campaign history
  ├── Content generation (templates, AI personalization)
  └── Push qualified prospects to Smartlead via API
          │
          ▼
Smartlead (sending infrastructure)
  ├── Warm-up, SMTP sending, mailbox rotation
  ├── Follow-up scheduling, OOO handling
  ├── Bounce detection, reply classification
  └── Webhook events back to PostgreSQL
          │
          ▼
PostgreSQL (receives events)
  ├── Reply/bounce/unsubscribe events
  ├── Campaign analytics
  └── Feedback to scoring/targeting
```

**Migration path:** DIY-to-platform is easy (upload prospects via API, connect accounts, configure sequences, done in a day). Platform-to-DIY is painful and expensive.

**Sources:**

- [SalesHandy - Smartlead Pricing](https://www.saleshandy.com/blog/smartlead-pricing/)
- [SalesHandy - Instantly Pricing](https://www.saleshandy.com/blog/instantly-pricing/)
- [Woodpecker Pricing](https://woodpecker.co/pricing/)
- [Sera Leads - Smartlead vs Instantly 2026](https://blog.seraleads.com/kb/sales-tool-reviews/smartlead-vs-instantly-2026/)
- [Smartlead - API Documentation](https://helpcenter.smartlead.ai/en/articles/125-full-api-documentation)
- [Smartlead - Webhooks](https://helpcenter.smartlead.ai/en/articles/35-set-up-smartlead-webhooks-for-campaign-automation)
- [Instantly Developer Docs](https://developer.instantly.ai/)
- [InfraMail - Cold Email ROI Calculator](https://inframail.io/blog-detail/cold-email-infrastructure-roi-calculator-agency-cost-comparison-2025)

---

## Gap Analysis

Cross-referencing the audit findings (REPORT_2026-02-16_send_track_audit.md) against research best practices:

### Critical Gaps (Launch-Blocking)

| # | Audit Finding | Best Practice | Gap | Fix Effort |
|---|--------------|---------------|-----|------------|
| G1 | **No pre-send email verification.** Previous 6.1% bounce rate. | Verify entire list before first send. Target < 1% bounce post-verification. | No verification pipeline exists | Low: $12-22 via Reoon + BounceBan |
| G2 | **No suppression list.** No table, no code. | Global suppression list checked before every send. CAN-SPAM requires honoring opt-outs. | suppression_list table missing, no code | Medium: create table, add check to send path |
| G3 | **No warm-up done.** 20 subdomains have mostly never sent. | 3-4 week warm-up before cold sends. | 0 warm-up activity | 3-4 weeks via Smartlead (automatic) |
| G4 | **No physical address in emails.** Templates in config.py have no postal address. | CAN-SPAM requires valid postal address in every commercial email. | Missing from all 8 email templates | Low: add to templates, set up PO box |
| G5 | **No unsubscribe link in emails.** Templates have no unsubscribe mechanism. | CAN-SPAM requires clear unsubscribe mechanism. | Missing from all 8 email templates | Low: add link, create endpoint |
| G6 | **SPF/DKIM not confirmed for all 20 subdomains.** | Required by all email providers. Emails may be rejected without them. | Status unknown for subdomains | Low: verify/configure in Google Workspace Admin + DNS |
| G7 | **Send scripts read from retiring tables.** campaign_manager.py and send_generated_emails.py read from grantscout_campaign.nonprofit_prospects and foundation_prospects (being retired). | Should read from f990_2025.foundation_prospects2 and nonprofits_prospects2. | Table migration not done | Medium if DIY. Low if using Smartlead (push from correct tables via API) |

### High Gaps (Performance/Risk)

| # | Audit Finding | Best Practice | Gap | Fix Effort |
|---|--------------|---------------|-----|------------|
| G8 | **No process lock.** Two instances send duplicates. | PID file or PostgreSQL advisory lock. | No locking mechanism | Low (if using Smartlead, handled by platform) |
| G9 | **SMTP-before-DB write order.** Crash between SMTP and DB creates duplicates. | Use pending/sending/sent state machine. | Current code sends then writes | Low (if using Smartlead, handled by atomic claim) |
| G10 | **No response classification.** track_response.py is manual only. | Automated rule-based + AI classification. | No automation | Medium if DIY. Zero if using Smartlead (built-in) |
| G11 | **No follow-up automation.** No 3-4-7 day cadence logic. | 3-touch sequence with increasing intervals. | No follow_up_queue table, no code | High if DIY. Zero if using Smartlead (built-in) |
| G12 | **No DMARC record.** | Start p=none, progress to p=reject. | DMARC not configured | Low: add DNS records |
| G13 | **2 broken scripts.** export_bounces.py and shutdown_hooks.py crash on import. | Delete dead code. | Broken imports | Low: delete files |
| G14 | **No file-based logging** for campaign_manager.py. stdout only. | File-based structured logging. | campaign_logger.py exists but campaign_manager.py doesn't use it | Low if DIY. N/A if using Smartlead |
| G15 | **Historical CSV data not migrated.** 1,844 sends and 1,841 responses only in CSV. | Migrate to PostgreSQL for unified history. | CSV data orphaned | Medium: write migration script |
| G16 | **No List-Unsubscribe header.** | Add for deliverability benefit (reduces spam complaints). | Not implemented | Low: add headers to all outgoing emails |
| G17 | **No Google Postmaster Tools.** | Monitor spam rate, reputation daily. | Not set up | Low: verify domains in Postmaster Tools |

### Medium Gaps (Nice-to-Have)

| # | Audit Finding | Best Practice | Gap | Fix Effort |
|---|--------------|---------------|-----|------------|
| G18 | No A/B testing in campaign_manager.py (hardcodes Variant D). | Route through generate_emails.py for A/B support. | Bypass of A/B infrastructure | N/A if using Smartlead (built-in A/B) |
| G19 | No connection pooling (fresh connection per operation). | Connection pool or shared connection. | Performance inefficiency | N/A if using Smartlead |
| G20 | No feedback loop: bounces do not update Phase 2 web_emails. | Bounce data should flow back to email validation tables. | Missing integration | Medium: add webhook handler |
| G21 | No feedback loop: reply rates do not update template selection. | A/B reply rates should inform template weighting. | ab_test_results view unused | Low: review after first campaign |
| G22 | No open/click tracking. | **DO NOT ADD.** Research shows tracking hurts deliverability (15% more spam, 2x lower reply rates). | Intentionally missing | Keep it this way |

---

## Pre-Send Checklist

Everything that must be true before sending the first email from the new system.

### Tier 1: Must Complete Before First Send

- [ ] **Email list verified** via Reoon (target < 1% bounce rate post-verification)
- [ ] **Smartlead Pro account** created and all 20 Google Workspace accounts connected
- [ ] **Warm-up running** for at least 2 weeks (ideally 3-4 weeks)
- [ ] **SPF records** configured for all 20 subdomains
- [ ] **DKIM keys** generated and published for all 20 subdomains
- [ ] **DMARC record** published for thegrantscout.com and filteredmessaging.com (p=none minimum)
- [ ] **Physical postal address** established (PO Box or CMRA) and added to email templates
- [ ] **Unsubscribe link** in every email template, functional and tested
- [ ] **Global suppression list** created (either in Smartlead or PostgreSQL, synced bidirectionally)
- [ ] **PostgreSQL-to-Smartlead API integration** built (prospect push, webhook receiver)
- [ ] **3-touch sequence** configured in Smartlead (Day 0, Day 3, Day 10)
- [ ] **Google Postmaster Tools** set up for both domains
- [ ] **Test send** of all 3 sequence steps to internal test addresses, verify formatting/links

### Tier 2: Complete Within First 2 Weeks of Operation

- [ ] **DMARC upgraded** from p=none to p=quarantine
- [ ] **Catch-all handling** added (BounceBan secondary pass)
- [ ] **AI reply classification** via Claude Haiku (Stage 2 of hybrid classifier)
- [ ] **OOO date parsing** implemented
- [ ] **List-Unsubscribe header** (RFC 8058) added to all outgoing emails
- [ ] **Privacy policy** page created and linked from emails (CCPA compliance)
- [ ] **Historical CSV data** migrated to PostgreSQL (1,844 sends + 1,841 responses)
- [ ] **Broken scripts** deleted (export_bounces.py, shutdown_hooks.py)

### Tier 3: Complete Within 90 Days

- [ ] **DMARC upgraded** to p=reject
- [ ] **Quarterly re-verification** schedule established
- [ ] **Feedback loop:** bounce data flows back to org_url_enrichment
- [ ] **Campaign table migration:** send scripts rewired from grantscout_campaign to f990_2025 tables
- [ ] **Campaign_prospect_status table** created per schema audit recommendation

---

## Warm-Up Plan

**Duration:** 4 weeks minimum before first cold send at full volume.

### Phase 1: Account Setup (Days 1-3)

- Sign up for Smartlead Pro ($78.30/month annual)
- Connect first batch of 5 Google Workspace accounts (subdomains 1-5)
- Start warm-up on these 5 accounts
- Verify SPF/DKIM/DMARC for these subdomains

### Phase 2: Staggered Onboarding (Days 4-12)

| Days | Accounts Added | Total Warming |
|------|---------------|---------------|
| 1-3 | Subdomains 1-5 | 5 |
| 4-6 | Subdomains 6-10 | 10 |
| 7-9 | Subdomains 11-15 | 15 |
| 10-12 | Subdomains 16-20 | 20 |

### Phase 3: Warm-Up Ramp (Weeks 1-4)

Smartlead handles the warm-up volume automatically. Expected progression:

| Week | Warm-Up Emails/Account/Day | Cold Emails/Account/Day | Total Active Subdomains |
|------|---------------------------|------------------------|------------------------|
| 1 | 10-15 | 0 | 5 (adding more) |
| 2 | 15-20 | 0 | 20 (all warming) |
| 3 | 15-20 | 2-5 (test batch only) | 20 |
| 4 | 10-15 | 5-10 | 20 |

### Phase 4: Production Ramp (Weeks 5-8)

| Week | Cold Emails/Account/Day | Total Daily Cold Sends |
|------|------------------------|----------------------|
| 5 | 8-10 | 160-200 |
| 6 | 10-12 | 200-240 |
| 7 | 12-15 | 240-300 |
| 8+ | 10-15 (steady state) | 200-300 |

**Monitoring during ramp:**

- Check Smartlead deliverability dashboard daily
- Check Google Postmaster Tools daily
- If bounce rate exceeds 3% on any subdomain, pause that subdomain and investigate
- If spam complaint rate appears in Postmaster Tools above 0.1%, reduce volume immediately

---

## Build vs Buy Recommendation

**Use Smartlead Pro at $78.30/month (annual billing).**

This is a definitive recommendation, not a suggestion. The economics are unambiguous:

| Metric | Smartlead Pro | DIY |
|--------|--------------|-----|
| Monthly hard cost (excl. Google Workspace) | $78.30 | $186-413 |
| Year 1 total cost | $2,496-2,736 | $5,232-8,436 |
| Initial build time | 8-12 hours (API integration) | 32-64 hours |
| Ongoing maintenance | 1-2 hours/month | 5-10 hours/month |
| Warm-up | Included, unlimited | $180-400/month standalone |
| Follow-up automation | Built-in | Must build (8-16 hrs) |
| Bounce handling | Automatic | Must build (4-8 hrs) |
| Reply classification | AI-powered | Must build (4-8 hrs) |
| Sender rotation | SmartSenders with health scoring | Must build (4-8 hrs) |

**Year 1 savings: $2,736-5,700 plus 72-148 hours of developer time.**

The warm-up service alone (required for 20 accounts) costs 2-5x more than the entire Smartlead subscription. Every other feature Smartlead provides is free on top of that.

**What we keep in-house:**

- PostgreSQL as source of truth for all prospect data, scoring, and analytics
- Content generation (templates, AI personalization via our own scripts)
- Campaign composition (which prospects to target, segmentation logic)
- Analytics and reporting beyond what Smartlead provides

**What Smartlead handles:**

- Warm-up across all 20 accounts
- SMTP sending with mailbox rotation
- Follow-up sequence scheduling and execution
- Bounce detection and handling
- Reply classification and routing
- OOO detection and sequence pausing
- Deliverability monitoring per mailbox

---

## Kill Switches

Specific thresholds where we stop sending and investigate.

### Immediate Stop (All Sending)

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Spam complaint rate | > 0.3% (per Google) | Stop all campaigns immediately. Review email content, targeting, and list quality. Do not resume until root cause identified. |
| Bounce rate (any subdomain) | > 5% in any 24-hour period | Pause affected subdomain. Investigate list segment. Re-verify before resuming. |
| Account suspension | Google suspends any sending account | Stop sending from that account. Contact Google support. Do not attempt to circumvent. |
| Multiple complaints from same org | 2+ complaints from same organization | Permanently suppress entire organization domain. Review targeting criteria. |

### Pause and Investigate

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Bounce rate (any subdomain) | > 3% over 7-day rolling window | Pause subdomain, re-verify that segment's emails, resume when fixed |
| Spam complaint rate | > 0.1% | Review recent email content and targeting. Reduce volume by 50% until rate drops. |
| Reply rate drops | < 0.1% sustained over 2 weeks | Review email content, subject lines, targeting. Possible deliverability issue. |
| Smartlead health score | Any mailbox drops to "Poor" | Reduce volume on that mailbox, increase warm-up ratio |
| Google Postmaster reputation | Domain reputation drops to "Low" or "Bad" | Reduce volume across all subdomains on that domain by 75%. Investigate. |

### Weekly Monitoring Checklist

- [ ] Check Smartlead dashboard: deliverability scores per mailbox
- [ ] Check Google Postmaster Tools: spam rate, domain reputation, IP reputation
- [ ] Review bounce rate by subdomain (target < 2% each)
- [ ] Review reply rate by campaign (investigate if < 0.5%)
- [ ] Check suppression list growth (normal is 1-3% of sends)
- [ ] Count unsubscribe requests (flag if > 1% of sends)
- [ ] Verify warm-up is still running on all accounts

---

## 90-Day Implementation Roadmap

### Week 1: Foundation (Days 1-7)

| Day | Task | Owner | Depends On |
|-----|------|-------|-----------|
| 1 | Sign up for Smartlead Pro ($78.30/mo annual) | Aleck | -- |
| 1 | Set up PO Box or CMRA private mailbox | Aleck | -- |
| 1 | Run full email list through Reoon verification ($12/10K) | Aleck | -- |
| 1-2 | Configure SPF/DKIM/DMARC for all 20 subdomains | Aleck | DNS access |
| 2-3 | Connect first 5 Google Workspace accounts to Smartlead, start warm-up | Aleck | Smartlead account |
| 3-5 | Connect remaining 15 accounts in batches of 5 (every 2-3 days) | Aleck | Smartlead account |
| 5-7 | Update email templates: add physical address, unsubscribe link, honest subject lines | Aleck | PO box |
| 7 | Set up Google Postmaster Tools for thegrantscout.com and filteredmessaging.com | Aleck | DNS access |

### Week 2: Integration Build (Days 8-14)

| Day | Task | Owner | Depends On |
|-----|------|-------|-----------|
| 8-10 | Build PostgreSQL-to-Smartlead prospect push script (Python, REST API) | Claude Code | Smartlead API key |
| 10-12 | Build Smartlead webhook receiver (Flask endpoint receiving reply/bounce/unsubscribe events, writing to PostgreSQL) | Claude Code | Server for webhook endpoint |
| 12-13 | Create `campaign_prospect_status` table in PostgreSQL (per schema audit recommendation) | Claude Code | -- |
| 13-14 | Configure 3-touch sequence in Smartlead (Day 0, Day 3, Day 10 break-up) | Aleck | Templates finalized |

### Week 3: Testing (Days 15-21)

| Day | Task | Owner | Depends On |
|-----|------|-------|-----------|
| 15-16 | End-to-end test: push 50 test prospects from PostgreSQL to Smartlead, send all 3 sequence steps to internal test addresses | Both | Integration built |
| 16-17 | Verify webhook events flow back to PostgreSQL correctly (reply, bounce, unsubscribe) | Claude Code | Test sends complete |
| 17-18 | Test unsubscribe link functionality end-to-end | Aleck | Unsubscribe endpoint |
| 18-19 | Run BounceBan secondary pass on catch-all subset of verified list | Aleck | Reoon results |
| 19-21 | Fix any issues found in testing. Finalize suppression list sync. | Both | Testing complete |

### Week 4: Soft Launch (Days 22-28)

| Day | Task | Owner | Depends On |
|-----|------|-------|-----------|
| 22-23 | Push first real batch: 200 highest-scored nonprofit prospects | Aleck | Testing passed |
| 22 | **First cold emails sent** (2-5 per subdomain, conservative) | Smartlead | Warm-up 3+ weeks |
| 23-28 | Monitor deliverability daily. Check Postmaster Tools, Smartlead health scores. | Aleck | Sends active |
| 25-28 | Ramp to 5-8 per subdomain if metrics are healthy | Aleck | No kill switch triggers |

### Weeks 5-8: Ramp to Full Volume

| Week | Daily Cold Volume | Key Activities |
|------|------------------|----------------|
| 5 | 160-200 (8-10/subdomain) | Monitor, adjust. Add List-Unsubscribe header. |
| 6 | 200-240 (10-12/subdomain) | Upgrade DMARC to p=quarantine. Implement Claude Haiku reply classification. |
| 7 | 240-300 (12-15/subdomain) | Add OOO date parsing. Privacy policy page live. |
| 8 | 200-300 (steady state) | Migrate historical CSV data to PostgreSQL. Delete broken scripts. |

### Weeks 9-12: Optimize and Clean Up

| Week | Key Activities |
|------|----------------|
| 9 | First quarterly re-verification of full email list ($12 via Reoon) |
| 10 | Analyze first month of campaign data: reply rate by segment, bounce rate by subdomain, follow-up conversion |
| 11 | Campaign table migration: update views/scripts to read from f990_2025.foundation_prospects2 and nonprofits_prospects2 instead of grantscout_campaign tables |
| 12 | Upgrade DMARC to p=reject. Build bounce-to-org_url_enrichment feedback loop. Set up quarterly re-verification calendar reminder. |

### Table Migration Integration (per Schema Audit)

The schema audit recommended migrating from grantscout_campaign.{nonprofit,foundation}_prospects to f990_2025.{nonprofits_prospects2,foundation_prospects2} with a campaign_prospect_status tracking table. With Smartlead as the send infrastructure, the migration simplifies:

1. **Week 2:** Create `campaign_prospect_status` table in f990_2025 schema. This tracks: ein, campaign_id, status (not_contacted/sent/replied/bounced/unsubscribed), smartlead_lead_id, sequence_step, sent_at, replied_at, bounced_at
2. **Week 2:** Push prospects to Smartlead from f990_2025.{prospects2} tables (not the old campaign tables)
3. **Week 2:** Webhook receiver writes events to campaign_prospect_status (not the old campaign tables)
4. **Week 11:** Update any remaining views (sales_prospects, campaign_summary, etc.) to read from the new tables
5. **Week 12:** After confirming no scripts depend on the old tables, mark them for archival

This approach means the old grantscout_campaign.{nonprofit,foundation}_prospects tables are simply never written to by the new system. They remain as read-only archives until formally dropped.

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| REPORT_2026-02-16_send_track_research.md | Enhancements/2026-02-16/ | This report |

---

## Notes

### Key Decisions Made

1. **Smartlead Pro over DIY.** Warm-up alone costs 2-5x more standalone than the entire Smartlead subscription. Unanimous across all cost scenarios.
2. **3 touches, not 4.** Touch 3 (break-up) captures the last meaningful replies. Touch 4+ risks reputation damage in the nonprofit sector.
3. **No open/click tracking.** Research shows 2x higher reply rates with tracking disabled. Privacy-conscious nonprofit audience makes this doubly important.
4. **Reoon + BounceBan for verification.** Two-stage approach at $22/10K covers both standard and catch-all addresses.
5. **Timer-based follow-ups, not trigger-based.** At our volume, behavioral triggers add complexity without meaningful lift.

### Open Questions for User

1. **PO Box vs CMRA:** Do you want the cheaper PO Box ($5/month) or a CMRA private mailbox ($10-30/month) that provides a real street address?
2. **Smartlead billing:** Monthly ($94) or annual ($78.30)? Annual saves $189/year.
3. **Webhook endpoint:** Where will the Smartlead webhook receiver run? (Your MacBook, a VPS, a cloud function?)
4. **Which 200 nonprofits for the soft launch?** Highest-scored? A specific geography? Need to decide targeting for week 4.

### Risk Factors

- **Warm-up takes time.** 3-4 weeks minimum before meaningful cold sends. Cannot be rushed without damaging deliverability.
- **Previous 6.1% bounce rate** means our lists have known quality issues. Verification before first send is non-negotiable.
- **Nonprofit sector reputation risk** is higher than typical B2B. Every email must be genuinely valuable and easy to opt out of.
- **Table migration** (schema audit recommendations) should happen during weeks 9-12, not before launch. The Smartlead integration naturally routes around the old tables.

---

*Generated by Claude Code on 2026-02-16*
