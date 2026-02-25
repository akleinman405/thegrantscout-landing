# PROMPT: Phase 5 (Send) & Phase 6 (Track) — Research & Recommendations

**Date:** 2026-02-16
**Agent:** Claude Code CLI
**Type:** Online research → Gap analysis → Recommendations
**Prerequisite:** Read `REPORT_2026-02-16_send_track_audit.md` first. If that file doesn't exist, STOP and tell the user to run the audit prompt first.

---

## Start in Planning Mode

Read the audit report, design research plan, get approval before executing.

## Context

The audit report documents the actual state of our email sending and tracking infrastructure. This prompt does the external research to identify what needs to change before we start sending.

### Our Setup (from audit)

- 20 email subdomains across 2 domains (thegrantscout.com, filteredmessaging.com)
- Google Workspace for sending (SMTP via app passwords)
- Gmail API for response monitoring
- Target volume: 150-300 emails/day across both campaigns
- Two buyer types: nonprofits ($99/month) and foundations ($50/month per grantee)
- Previous campaign: 1,844 sent, 6.1% bounce, 0.23% reply rate
- Current state: 0 emails in queue, no campaign running — this is pre-launch

### What We Need Answers To

The audit tells us what IS. This prompt tells us what SHOULD BE and what's the gap.

## Research Topics

**Important guidance:**
- **Prioritize depth over breadth.** If any section would be shallow, flag it and recommend a follow-up prompt instead.
- **Staged delivery:** If the full scope is too much for one pass, deliver in priority order: (A) Infrastructure & deliverability, (B) Compliance & risk, (C) Build vs buy. Stop after A if you're running long and note what's deferred.
- **Include numeric thresholds wherever possible.** Not "keep bounce rate low" — give the number.
- **Filter out enterprise practices that don't apply below 500 emails/day.** Our volume is small. Don't overcomplicate.
- **Compliance scope: US-only, 501(c)(3) nonprofits and private foundations.** No international.
- **Organize findings into priority tiers:**
  - **Tier 1 (launch-blocking):** Must be resolved before first send
  - **Tier 2 (performance):** Improves results but not blocking
  - **Tier 3 (strategic):** Longer-term decisions

### 1. Subdomain Warm-Up

We have 20 subdomains that have mostly never sent email. Research:

- Pre-research estimate: How many days/weeks does warm-up take? What daily volume ramp would you guess?
- Then research: **Design a recommended warm-up strategy for our exact configuration** (20 subdomains on Google Workspace, target 8-15 emails/day per subdomain) **and justify it.**
- Simultaneous vs sequential warm-up across subdomains?
- Warm-up services (Instantly warm-up, Warmbox, Lemwarm) — cost, effectiveness with Google Workspace. Worth it at our volume?
- What happens if we skip warm-up? How bad is the penalty at 8-15/day per subdomain?

### 2. Deliverability & Sender Reputation

- Pre-research estimate: What bounce rate gets you blacklisted? What's "good" for cold B2B email?
- Then research: Google Postmaster Tools setup and monitoring — what metrics matter?
- Our 6.1% bounce rate — how bad is that? What's the threshold for blacklisting?
- SPF/DKIM/DMARC — we have them, but are there optimization settings beyond just "exists"?
- Subdomain isolation: if outreach3.thegrantscout.com gets flagged, does it affect thegrantscout.com?
- Shared IP (Google Workspace) vs dedicated IP at our volume — does it matter?
- Inbox placement rates for cold email via Google Workspace vs dedicated ESP (SendGrid, Mailgun)
- List-Unsubscribe header: is it required? Does adding it help deliverability?

### 3. Send Cadence & Timing

- Pre-research estimate: What's the best day/time to email a nonprofit ED? A foundation program officer?
- Then research: Optimal send times for nonprofit/foundation sector (cite studies)
- Inter-email delay: what's the minimum between individual sends to avoid triggering spam filters?
- Daily volume per sender/subdomain: is 15/day conservative, aggressive, or about right?
- Follow-up timing: 3 days? 5 days? 7 days? What does the data say?
- Number of touches: our spec says 4 (initial + 3 follow-ups). Is this optimal? What's the drop-off curve?
- "Break-up" email: does it actually work or is it a sales myth?

### 4. Bounce Management & List Hygiene

- Pre-research estimate: What verification approach would you recommend before we start looking at options?
- Then research: Pre-send verification — MillionVerifier ($129/100K) was recommended in earlier research. Confirm or find better options.
- Hard vs soft bounce handling — what action for each?
- Catch-all domains: send or skip? What percentage bounce? (Our earlier research estimated 15-38% of nonprofit domains are catch-all)
- List decay rate for nonprofit sector specifically
- Re-verification frequency: how often should we re-check our email list?
- What's the cost of NOT verifying? Model: if 6.1% of 10K emails bounce, what's the sender reputation impact?

### 5. Response Tracking & Classification

- Pre-research estimate: Can Gmail API polling handle our volume? What are the limitations?
- Then research: Gmail API rate limits and quotas for response monitoring
- **Model this specifically:** Assume 20 inboxes, polling every 5 minutes, using label-based filtering. Calculate quota usage and confirm margin of safety.
- Polling frequency: how often should we check for replies?
- Response classification approaches at low volume (we're talking hundreds of replies, not thousands):
  - Rule-based (keyword matching)
  - AI classification (Claude API)
  - Hybrid
- Out-of-office parsing: extracting return dates
- Thread matching: reliably linking a reply to the original sent email
- Forwarded email detection

### 6. Follow-Up Automation

- Pre-research estimate: What's the simplest follow-up system that would work for us?
- Then research: Multi-touch sequence best practices for B2B nonprofit outreach
- Threading: should follow-ups be in the same thread (reply to original) or new emails?
- Personalization in follow-ups: reference original email, or new angle entirely?
- Behavioral triggers: should we track opens? Is that worth the complexity?
- Pause/resume: what if someone replies between scheduled follow-ups?

### 7. Compliance

- CAN-SPAM requirements for B2B cold email specifically (not B2C, not newsletters)
- Physical address requirement — do we need it in every email?
- Unsubscribe mechanism — is one-click required for our volume?
- Google's 2024 bulk sender requirements — do they apply to us at 150-300/day?
- State-specific email laws (California, New York) that might apply
- What's the actual legal risk of B2B cold email to nonprofits and foundations?

### 8. Build vs Buy

This is the key strategic question. Research:

- **Instantly** — price at our volume (20 senders, 150-300 emails/day), features, Google Workspace integration
- **Smartlead** — same
- **Woodpecker** — same
- **Lemlist** — same

For each: monthly cost, warm-up included?, deliverability features, follow-up automation, response tracking, CRM integration, data export/ownership, PostgreSQL integration possible?

Compare to DIY cost:
- Our time maintaining custom scripts
- MillionVerifier for verification
- Warm-up service if needed
- Google Workspace ($6/user/month × how many accounts?)

**Decision framework:** At what volume does DIY stop making sense? At what volume does a platform stop making sense? Where do we fall?

## Output

### Deliverables

`REPORT_2026-02-16_send_track_research.md` with:

1. **Research findings by topic** (1-8 above), each with:
   - Pre-research estimate vs post-research finding
   - Key data points with sources cited
   - Specific recommendation for our situation

2. **Gap analysis:** Cross-reference audit findings with research best practices. For each gap:
   - What we have vs what we should have
   - Severity (blocks launch / degrades performance / nice-to-have)
   - Fix effort and cost

3. **Pre-send checklist:** Everything that must be true before we send the first email from the new system. Ordered by priority.

4. **Warm-up plan:** Specific daily/weekly volume ramp for our 20 subdomains.

5. **Build vs buy recommendation:** Direct recommendation with cost comparison.

6. **Kill switches:** Specific thresholds where we stop sending:
   - Bounce rate > X% → pause and investigate
   - Spam complaint rate > X% → stop immediately
   - Daily/weekly monitoring metrics

7. **90-day implementation roadmap:** What to do in what order to go from current state to reliable sending infrastructure.

## Notes

- We're pre-launch with 0 emails sent from the new system. This is the right time to get the infrastructure right.
- Our volume is small (150-300/day). Some enterprise best practices may not apply. Focus on what matters at our scale.
- We're not attached to the custom scripts. If Instantly at $30/month does everything better, say so.
- The nonprofit sector is relationship-driven and word travels fast. Reputation damage from bad email practices is worse for us than for a random SaaS company.
- Our cold calling already gets 6% conversion. Email needs to complement phone, not replace it.
- **Strategic context:** Our previous email campaign got 0.23% reply rate. Biggest gains likely come from messaging and list quality, not infrastructure alone. The infrastructure needs to be solid, but don't over-engineer — get it reliable enough to test messaging quickly.
