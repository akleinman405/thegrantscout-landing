# PROMPT: Email Campaign Implementation + Send via Resend

**Date:** 2026-02-17
**For:** Claude Code CLI
**Schema:** f990_2025
**Priority:** High - execute today

---

## Situation

We have two finalized email templates for cold outreach to nonprofits. The email pipeline data is rebuilt (cohort_foundation_lists_v2, prospect quality tiers, foundation exclusion list). We need to:

1. Generate the actual emails from database data
2. QC a sample
3. Send via Resend API using our 10 existing subdomains

---

## The Two Email Templates

### Template A: "Raising Awareness" (list offer)

**Subject:** Private funders for {{sector}} in {{state}}

```
Hi {{first_name}},

My name is Alec and I run a company called TheGrantScout. We help nonprofits impacted by recent federal funding cuts find private funding alternatives.

We've been raising awareness of who the local private funders are in each state, and I put together a list of {{count}} private foundations that fund {{sector}} organizations in {{state}}, along with their contact info and recent giving history.

Let me know if you're interested and I'll send it your way.

Alec Kleinman
TheGrantScout
740 E, 2320 N, Provo, UT 84604

P.S - If this isn't relevant just let me know and I won't reach out again.
```

**Merge fields:**
- `{{first_name}}` = contact_first_name from nonprofits_prospects2
- `{{sector}}` = sector_label from cohort_foundation_lists_v2 (human-readable: "Human Services", "Education", etc.)
- `{{state}}` = full state name (convert 2-letter code)
- `{{count}}` = foundation_count from cohort_viability

### Template C: "Direct Call" (personalized)

**Subject:** Foundation funding for {{organization_name}}

```
Hi {{first_name}},

My name is Alec and I'm with a company called TheGrantScout. I saw that {{organization_name}} does {{mission_short}} and wanted to see if we can help you find private foundation funding.

Let me know if you're open to a quick call!

Alec Kleinman
TheGrantScout
740 E, 2320 N, Provo, UT 84604

P.S - If this isn't relevant just let me know and I won't reach out again.
```

**Merge fields:**
- `{{first_name}}` = contact_first_name
- `{{organization_name}}` = organization_name
- `{{mission_short}}` = **GENERATE THIS.** Read `mission_description` from nonprofits_prospects2 and write a 5-8 word plain-English summary of what the org does. Examples:
  - "provides shelter for families experiencing homelessness"
  - "runs after-school programs for at-risk youth"
  - "offers addiction recovery services"
  - Keep it lowercase, natural, no jargon. If mission_description is NULL or too vague, use the NTEE code to write a generic version like "supports human services programs" but flag it.

---

## Task 1: Pull Sendable Prospects + Report Counts

Query all prospects that are ready to send to:

```sql
SELECT
    np.ein, np.organization_name, np.contact_first_name, np.contact_email,
    np.state, np.ntee_code, np.mission_description,
    np.email_quality_tier, np.email_quality_flags,
    cv.foundation_count,
    cfl.sector_label
FROM f990_2025.nonprofits_prospects2 np
JOIN f990_2025.cohort_viability cv
    ON cv.state = np.state AND cv.ntee_sector = LEFT(np.ntee_code, 1)
LEFT JOIN LATERAL (
    SELECT DISTINCT sector_label
    FROM f990_2025.cohort_foundation_lists_v2 cfl2
    WHERE cfl2.state = np.state AND cfl2.ntee_sector = LEFT(np.ntee_code, 1)
    LIMIT 1
) cfl ON true
WHERE np.email_quality_tier IN ('A', 'B')
  AND np.contact_email IS NOT NULL
  AND np.contact_email NOT LIKE '%.gov'
  AND np.contact_first_name NOT IN ('there', 'Hi', 'Hello', 'Dear', 'Sir', 'Madam', 'whom', 'Team')
ORDER BY np.email_quality_tier, np.state;
```

**Report:**
- Total sendable prospects (Tier A + B with valid name and non-gov email)
- Breakdown by state
- Breakdown by sector
- Breakdown by quality tier
- How many have mission_description populated vs NULL

This tells us how many we CAN send to and helps us plan the A/B split.

## Task 2: A/B Split Assignment

Split prospects 50/50 between Template A and Template C:
- Template A (list offer): 50% of prospects, randomly assigned
- Template C (direct call): 50% of prospects, randomly assigned

For Template C prospects: generate the `{{mission_short}}` field using mission_description. Output all of them for review. Flag any where mission_description was NULL or the summary feels generic.

## Task 3: Generate All Emails

For every sendable prospect, generate the filled-in email using the assigned template. Save to a file/table with columns:
- prospect_ein
- contact_email
- contact_first_name
- template_used (A or C)
- subject_line
- email_body (complete, ready to send)
- mission_short (for Template C only)
- quality_flag (any concerns)

## Task 4: QC Sample

Manually review 20 randomly selected emails (10 from each template):
- Does the first name look real? (not a placeholder)
- Does the sector label match what the org actually does?
- Does the foundation count seem reasonable? (not 0, not wildly high)
- For Template C: does the mission_short accurately describe the org?
- Is the email properly formatted? (no broken merge fields, no weird characters)
- Would you send this email? Yes/No with reason if No.

Report pass/fail rate. If more than 2/20 fail, stop and flag the issue before sending.

## Task 5: Send via Resend API

We have 10 subdomains already configured in Resend. Look up the existing domain configuration in the Resend account to get the domain names and API key.

**IMPORTANT DELIVERABILITY NOTE:** Alec wants 100 per domain (1,000 total) today. However, if these domains are not warmed up, this risks deliverability. Check the sending history on the domains first. If they've been sending already, 100/domain is fine. If they're brand new (0 sends), recommend starting at 20-30/domain (200-300 total) and flag this to Alec.

**Sending plan:**
- Distribute emails evenly across the 10 subdomains
- Use a consistent from name: "Alec Kleinman" or "Alec from TheGrantScout"
- From email: alec@[subdomain]
- Set reply-to: alec@thegrantscout.com (or whatever the main domain is)
- Space sends out over a few hours (not all at once). Suggested: batch of 10-20 per domain per hour.
- Log every send: email address, template used, subdomain used, timestamp, Resend message ID
- Track bounces and failures

**Resend API pattern:**
```python
import resend

resend.api_key = "re_XXXXX"  # Get from environment or config

for email in batch:
    params = {
        "from": f"Alec Kleinman <alec@{email['subdomain']}>",
        "to": [email['contact_email']],
        "subject": email['subject_line'],
        "text": email['email_body'],
        "reply_to": "alec@thegrantscout.com"
    }
    response = resend.Emails.send(params)
    # Log response.id, status, timestamp
```

## Task 6: Output Report

Save a report (`REPORT_2026-02-17_3_email_campaign_send.md`) with:
- Total prospects available
- Total emails generated
- Total emails sent (by domain, by template)
- QC results (pass/fail, any issues found)
- A/B split breakdown
- Any flags or concerns
- Sample of 5 sent emails (full text) for reference
- Bounces/failures if any

---

## File References

- Database schema: f990_2025
- Prospect table: nonprofits_prospects2 (has email_quality_tier, email_quality_flags)
- Cohort data: cohort_viability (has foundation_count, display_text)
- Foundation lists: cohort_foundation_lists_v2 (has sector_label)
- Pre-flight script: Enhancements/2026-02-17/pre_email_quality_report.py

---

## Notes

- Plain text emails only. No HTML, no images, no links.
- Do NOT use em dashes anywhere. Use commas, periods, or "and" instead.
- The "P.S" line is part of the email body, not a separate element.
- State names should be full names ("California" not "CA") in the email body.
- For Template A, if foundation_count is NULL or 0 for a cohort, skip that prospect.
- For Template C, if mission_description is NULL and you can't write a reasonable mission_short from the NTEE code, skip that prospect or assign them to Template A instead.
