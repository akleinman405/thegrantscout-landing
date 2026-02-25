# PROMPT C: Generate Additional Funders List + Convert to PDF

**Date:** 2026-02-21  
**Type:** Run additional-funders skill + PDF conversion  
**Schema:** f990_2025 (database: thegrantscout)  
**Depends on:** Prompt B (grant report approved by Alec)

---

## Situation

The VetsBoats grant opportunities report (Prompt B) has been reviewed and approved. Now generate the companion "additional funders" document and convert both deliverables to PDF.

---

## Task 1: Run additional-funders skill

1. Read the additional-funders skill at `.claude/skills/additional-funders/SKILL.md`
2. Generate the additional funders document using the input data below
3. Output: `REPORT_2026-02-21_vetsboats_additional_funders.md`

### Input Data

```json
{
  "client": {
    "name": "VetsBoats Foundation",
    "ein": "464194065",
    "mission": "Adaptive sailing for veterans in the SF Bay Area",
    "org_type": "private_foundation",
    "state": "CA"
  },
  "additional_funders": [
    {
      "ein": "843123162",
      "name": "LB Charitable Foundation",
      "state": "CA",
      "assets": "$50M",
      "grant_range": "$10,000-$100,000",
      "why": "'Uplifting and aiding veterans' explicitly named in mission. $290K in veteran grants across 11 organizations. No restriction on private foundation applicants found. California-based.",
      "caveat": "Application pages returned 404 errors during research. Direct email outreach may be needed.",
      "next_step": "Email grants@lbcharitablefoundation.org to introduce VetsBoats and confirm application process. Disclose private foundation status upfront.",
      "contact": "grants@lbcharitablefoundation.org"
    },
    {
      "ein": "473818599",
      "name": "Richard Reed Foundation",
      "state": "CO",
      "assets": "$9M",
      "grant_range": "$25,000-$40,000",
      "why": "Funded Achieve Tahoe $55,000 for 'adaptive sports and recreational activities for individuals of all ages and all disabilities.' Also funded equine therapy for veterans ($40K). Best adaptive recreation giving track record outside our primary leads.",
      "caveat": "Colorado-based with no California sailing grants. Small foundation driven by founder interests.",
      "next_step": "Email info@richardreedfoundation.org. Lead with adaptive recreation angle and cite the Achieve Tahoe parallel — VetsBoats is doing similar work through sailing.",
      "contact": "info@richardreedfoundation.org"
    },
    {
      "ein": "136201175",
      "name": "Widgeon Point Charitable Foundation",
      "state": "ME",
      "assets": "Unknown",
      "grant_range": "Unknown",
      "why": "Funds Sail to Prevail, an adaptive sailing program for people with disabilities in Rhode Island — the closest analog to VetsBoats in any foundation's portfolio. Also funds Sail Maine, NY Sailing Foundation, and Maine Adaptive Sports. Exceptional sailing + adaptive sports fit.",
      "caveat": "Was invite-only in 2025 due to volume of AI-generated applications. Historically accepts LOIs March 1 - September 15.",
      "next_step": "Monitor for 2026 application reopening. If they reopen, submit LOI immediately citing VetsBoats' parallel to Sail to Prevail.",
      "contact": null
    },
    {
      "ein": "222939536",
      "name": "Christopher & Dana Reeve Foundation",
      "state": "NJ",
      "assets": "$11M",
      "grant_range": "$5,000-$25,000",
      "why": "Awarded $25,000 to Achieve Tahoe for adaptive sports. Funds adaptive sports programs nationally, with Bay Area precedent (BORP received grants). Quality of Life grants up to $25K. Veterans receive 'special consideration.'",
      "caveat": "Programs must serve people with paralysis specifically (spinal cord injury, stroke, MS). Private foundation eligibility is unconfirmed — one source lists PFs as ineligible.",
      "next_step": "Email QOL@Reeve.org to confirm whether private foundations can apply. If eligible, next deadline is March 12, 2026 — action needed immediately.",
      "contact": "QOL@Reeve.org"
    },
    {
      "ein": "261441650",
      "name": "Bob Woodruff Foundation",
      "state": "NY",
      "assets": "Unknown (public charity)",
      "grant_range": "$5,000-$500,000 (avg $100K)",
      "why": "Strongest programmatic fit of any funder found. Core mission is veteran services. Funds adaptive sports including water-based programs through Move United ($2.5M+) and Disabled Sports USA. Rolling applications year-round.",
      "caveat": "Application requires filing Form 990 or 990-EZ (not 990-PF). This may be a hard disqualifier for VetsBoats.",
      "next_step": "Email grants@bobwoodrufffoundation.org to confirm whether organizations filing 990-PF are eligible. If confirmed, this becomes a top-priority application.",
      "contact": "grants@bobwoodrufffoundation.org"
    }
  ]
}
```

---

## Task 2: Convert both reports to PDF

Convert both deliverables to professional PDFs:

1. `REPORT_2026-02-21_vetsboats_grant_opportunities.md` → `REPORT_2026-02-21_vetsboats_grant_opportunities.pdf`
2. `REPORT_2026-02-21_vetsboats_additional_funders.md` → `REPORT_2026-02-21_vetsboats_additional_funders.pdf`

Use the pdf skill at `/mnt/skills/public/pdf/SKILL.md` for conversion guidance.

Clean, professional formatting. No code blocks or raw markdown visible in the PDF.

---

## Output

| File | Description |
|------|-------------|
| `REPORT_2026-02-21_vetsboats_additional_funders.md` | Additional funders markdown |
| `REPORT_2026-02-21_vetsboats_grant_opportunities.pdf` | Grant opportunities PDF (client-facing) |
| `REPORT_2026-02-21_vetsboats_additional_funders.pdf` | Additional funders PDF (client-facing) |

---

## Notes

- Both PDFs will be emailed to Matt Goettelman at VetsBoats
- Frame as supplemental analysis: "additional opportunities we found during deeper research"
- Keep additional funders doc to 2-3 pages
