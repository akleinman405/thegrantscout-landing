# Build Contact Verification System for Grant Reports

## Situation

We deliver monthly grant opportunity reports to nonprofit clients. Each report includes 5 foundation matches with contact info (emails, phone numbers, application URLs, deadlines). Our first paying client (VetsBoats/Matt Goettelman) just reported a bouncing email address — and when we audited the full report, we found 25 errors across 5 foundations including wrong emails, wrong phone numbers, and stale staff info.

**The problem:** Our current pipeline verifies nothing. Numbers come from 990-PF data and web research but are never validated before delivery. MX domain checks only confirm the domain accepts mail — they don't confirm a specific mailbox exists.

**What we have already:** A full email campaign infrastructure built in Nov 2025:
- `send_initial_outreach.py` — sends emails via Gmail API with tracking
- `send_followup.py` — follow-up sequences
- `campaign_tracker.py` — monitors bounces and replies via Gmail API
- `export_bounces.py` — extracts bounce data
- `config.py` — Gmail API auth, rate limits, sending config
- `sent_tracker.csv`, `response_tracker.csv` — tracking files

All in: `06_GO_TO_MARKET/outreach_sequences/Email Campaign 2025-11-3/`

## Objective

Build a contact verification module (`09_contact_verification.py`) that integrates into the report pipeline, PLUS immediately verify the 5 VetsBoats foundation contacts.

## Tasks

### Task 1: Explore & Document Existing Infrastructure
- Read all files in `06_GO_TO_MARKET/outreach_sequences/Email Campaign 2025-11-3/`
- Document: Gmail API auth method, how sending works, how bounce detection works
- Identify what we can reuse for verification
- Output: Brief summary in the session report

### Task 2: Build SMTP Verification Module
Build `09_contact_verification.py` with these verification layers (no email sent):

**Layer 1 — MX Check** (already done in audit, but formalize it)
- `dig MX domain` or Python `dns.resolver`
- Result: PASS/FAIL/WARN

**Layer 2 — SMTP Handshake Verification** (the key new capability)
- Connect to mail server on port 25/587
- EHLO → MAIL FROM:<verify@thegrantscout.com> → RCPT TO:<target@domain.com>
- If server returns 250 → mailbox exists (VERIFIED)
- If server returns 550 → mailbox doesn't exist (FAIL)
- If server returns 252 or accepts all → INCONCLUSIVE (catch-all server)
- QUIT without sending any actual email
- Important: Handle timeouts, rate limits, greylisting. Some servers delay response on first attempt — retry once after 30 seconds.

**Layer 3 — Website Liveness Check**
- HTTP HEAD/GET on all URLs in the report
- Check for 200, redirects, 404s
- Flag any URL that doesn't resolve

**Output format:** JSON + human-readable summary
```json
{
  "email": "elizabeth.burdette@signaturefd.com",
  "mx_check": "PASS",
  "smtp_verify": "VERIFIED",  // or FAIL, INCONCLUSIVE, ERROR
  "smtp_detail": "250 OK",
  "verified_at": "2026-02-18T10:30:00Z"
}
```

### Task 3: Verify All 5 VetsBoats Contacts NOW
Run the module against these specific contacts from the corrected report:

| Foundation | Email | Phone | URL |
|---|---|---|---|
| Bill Simpson | elizabeth.burdette@signaturefd.com | (404) 473-4924 | billsimpsonfoundation.org |
| Herzstein | (find from report) | (find from report) | herzsteinfoundation.org |
| Kovler | app@kovler-b.com | (find from report) | kovler-b.com |
| Barry | (find from report) | (find from report) | barryfamilyfoundation.org |
| Van Beuren | support@vbcfoundation.org | (find from report) | vbcfoundation.org |

Pull any missing emails/phones from: `5. Runs/VetsBoats/2026-02-06/REPORT_2026-02-06_vetsboats_grant_report.md`

### Task 4: Integration with Report Pipeline
Design (don't build yet) how `09_contact_verification.py` fits into the report generation workflow:

- After report is generated but before delivery
- Verification results appended to report as a confidence appendix
- Any FAIL results block delivery and flag for manual review
- Output: Brief design doc (1 page max)

## Output Location
- Module: `pipeline/09_contact_verification.py`
- VetsBoats results: `Enhancements/2026-02-18/OUTPUT_2026-02-18_vetsboats_verification.json`
- Design doc: `pipeline/DESIGN_contact_verification_integration.md`

## Constraints
- Python 3.x, use `dnspython` for MX/SMTP checks
- Reuse existing Gmail API auth from campaign infrastructure — don't rebuild
- SMTP verification must have configurable timeout and retry logic
- All verification results must be timestamped and logged
- Foundation outreach emails require manual approval before send (no auto-send)

## Definition of Done
- [ ] SMTP verification returns VERIFIED/FAIL/INCONCLUSIVE for each email
- [ ] All 5 VetsBoats contacts verified with results in JSON
- [ ] Design doc for pipeline integration complete
- [ ] Session report with lessons learned

## Mandatory Report
File: `Enhancements/2026-02-18/REPORT_2026-02-18_contact_verification.md`
Include:
- What was built
- VetsBoats verification results (the actual PASS/FAIL for each contact)
- Any issues or limitations discovered with SMTP verification
- Lessons learned
- Recommendations for next steps
