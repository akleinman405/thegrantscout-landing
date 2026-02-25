# Design: Contact Verification in Report Pipeline

**Date:** 2026-02-18
**Status:** Draft

## Where It Fits

```
process_client.py (steps 01-08)
    |
    v
08_render_report.py  -->  report.md generated
    |
    v
09_contact_verification.py  -->  verification_results.json
    |
    v
Decision gate:
  - All PASS/CATCH_ALL  -->  Deliver report
  - Any FAIL            -->  Block delivery, flag for manual review
  - Any INCONCLUSIVE    -->  Deliver with confidence appendix
```

## Integration Points

**Input:** The rendered report markdown (step 08 output) or a contacts JSON extracted from the report.

**Trigger:** Automatically after report generation, before delivery. Called by `process_client.py` as the final step.

**Output:**
1. `verification_results.json` saved alongside the report
2. Confidence appendix appended to the report markdown (before conversion to .docx/.pdf)

## Confidence Appendix Format

Appended to the end of the report before the "Data Sources" section:

```markdown
## Contact Verification Status

Verified on: February 18, 2026

| Foundation | Email | MX | SMTP | Website |
|---|---|---|---|---|
| Bill Simpson | elizabeth.burdette@signaturefd.com | PASS | VERIFIED | PASS |
| Herzstein | rmasaryk@herzsteinfoundation.org | PASS | VERIFIED | PASS |

Note: SMTP verification confirms the mail server accepts the address.
It does not guarantee the person still works there.
```

## Delivery Rules

| Condition | Action |
|---|---|
| All emails VERIFIED or CATCH_ALL, all URLs PASS | Auto-deliver |
| Any email INCONCLUSIVE, no FAIL | Deliver with note in appendix |
| Any email FAIL (mailbox rejected) | Block delivery, alert operator |
| Any URL FAIL (404/unreachable) | Block delivery, alert operator |
| IP blocklisted (all INCONCLUSIVE) | Deliver with caveat, schedule re-check from clean IP |

## Implementation Sketch

Add to `process_client.py` after report rendering:

```python
from pipeline.contact_verification import verify_batch, extract_contacts_from_report

contacts = extract_contacts_from_report(report_path)
results = verify_batch(contacts, output_path=verification_json_path)

failures = [c for c in results["contacts"] if c["overall_status"] == "FAIL"]
if failures:
    print(f"BLOCKED: {len(failures)} contact(s) failed verification")
    # Do not proceed to .docx/.pdf conversion
else:
    append_confidence_appendix(report_path, results)
    # Proceed to conversion and delivery
```

## Limitations and Mitigations

| Limitation | Mitigation |
|---|---|
| SMTP port 25 blocked on many residential IPs | Run from VPS/cloud server with clean IP |
| Spamhaus blocklist blocks verification | Request delisting or use a dedicated verification IP |
| Catch-all servers accept all addresses | Flag as CATCH_ALL, not VERIFIED |
| Phone numbers can't be auto-verified | Always marked "manual verification required" |
| SMTP checks don't confirm person identity | Supplement with web research for staff pages |

## Future Enhancements

1. **API-based verification:** Integrate ZeroBounce, NeverBounce, or Hunter.io for production-grade mailbox verification ($0.003-0.01/check)
2. **Staff page scraper:** Check foundation "About" or "Staff" pages to confirm named contacts still appear
3. **Scheduled re-verification:** Monthly cron job to re-verify all contacts in active reports
