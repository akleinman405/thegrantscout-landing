# PROMPT 2 of 4: VetsBoats — Targeted Crawl for Opportunity Leads

**Date:** 2026-02-21  
**Type:** Targeted web crawl + structured extraction  
**Schema:** f990_2025  
**Client:** VetsBoats Foundation (EIN 464194065, "Wooden Boats for Veterans")  
**Depends on:** PROMPT 1 output (complete) + Alec's approved candidate list (below)  
**Next:** PROMPT 4 (report generation, after Alec reviews)

---

## Situation

Prompt 1 produced 18 candidates from Schedule I queries. After review, most were Tahoe-area community foundations funding Achieve Tahoe locally (not relevant for SF Bay-based VetsBoats), DAF-like platforms that slipped through filters, or geographically irrelevant keyword matches.

**5 approved for targeted crawl:**

| # | Organization | EIN | Why |
|---|-------------|-----|-----|
| 1 | Christopher Reeve Foundation | 222939536 | $25K to Achieve Tahoe for "Adaptive Sports." National funder, established program. Top priority. |
| 2 | Orange County Community Foundation | 330378778 | Only multi-peer funder (2 peers). $96M grantmaking, 596 CA grants. Check open RFPs. |
| 3 | Bob Woodruff Foundation | 237047543 | HIGH fit from PF deep crawl. $10M annual grantmaking for veteran services. Confirm PF eligibility. |
| 4 | Rehabilitation Institute of Chicago (SRAlab) | 362256036 | Funds Judd Goldman Adaptive Sailing. Healthcare system making adaptive sports grants. Quick check. |
| 5 | Tahoe Fund | 010974628 | $100K to Achieve Tahoe. Big grant but Tahoe-focused — verify if SF Bay orgs are eligible. Quick check. |

**Already researched PF leads (DO NOT re-crawl — include in final 5 selection):**
- Kim & Harold Louie Family Foundation (STRONG_FIT, rolling LOI)
- Charles H. Stout Foundation (STRONG_FIT, June 15 deadline)
- Kovler Family Foundation (POSSIBLE_FIT, mid-Nov deadline)
- Howard Family Foundation (POSSIBLE_FIT, bank-managed)

---

## Tasks

### 1. Targeted web search for each of the 5 approved candidates

For each:
```
"[org name]" grants application OR funding opportunities OR RFP OR "how to apply"
```

### 2. Targeted page fetch (2-5 pages per org)

Fetch ONLY:
- The grants/funding/apply page
- Eligibility guidelines if linked from that page
- Current RFPs or program descriptions if listed
- Contact/staff page if it lists program officers

**Do NOT fetch:** About pages, news/blog, annual reports, financials, event pages, donor pages, or anything else.

### 3. Structured extraction

For each candidate, extract into this schema:

```json
{
  "filer_name": "",
  "filer_ein": "",
  "website": "",
  "application_url": "",
  "has_open_application": true/false/unknown,
  "application_method": "online portal / LOI / letter / email / phone / unknown",
  "eligibility": {
    "pf_eligible": true/false/unknown,
    "geographic_restrictions": "",
    "org_type_requirements": "",
    "budget_size_requirements": "",
    "other_restrictions": ""
  },
  "program_areas_funded": [],
  "grant_size_range": "$X - $Y",
  "deadlines": "",
  "funding_cycle": "rolling / annual / quarterly / unknown",
  "contact_info": {
    "name": "",
    "title": "",
    "email": "",
    "phone": ""
  },
  "recent_grantees_listed": [],
  "fit_notes": "",
  "confidence": "HIGH / MEDIUM / LOW",
  "flags_for_alec": ""
}
```

**Important:**
- If you can't find application info, set `has_open_application: unknown` and note in `flags_for_alec`
- If eligibility is ambiguous (says "501(c)(3)" without specifying public charity), set `pf_eligible: unknown` and flag it
- Don't make final eligibility calls — extract what's there and flag anything uncertain
- For Tahoe Fund and SRAlab: these are quick checks. If geographic restrictions or mission mismatch is obvious from the first page, note it and move on.

### 4. Output extraction cards

Present each candidate as a card Alec can quickly scan and approve/reject.

---

## Output

| File | Description |
|------|-------------|
| DATA_2026-02-21_vetsboats_targeted_crawl.json | Structured extraction for all 5 candidates |
| DATA_2026-02-21_vetsboats_opportunity_cards.md | Formatted cards for Alec to review |

### Format for opportunity cards

```
## [Org Name] (EIN, State)
**Confidence:** HIGH / MEDIUM / LOW
**Application:** [URL or method] | Deadline: [date or rolling]
**PF Eligible:** Yes / No / Unknown — [evidence]
**Geographic:** [any restrictions]
**Grant Range:** $X - $Y
**Program Areas:** [list]
**Contact:** [name, title, email/phone]
**Peer Grant Evidence:** [which peers, amounts]
**Fit Notes:** [why this is relevant for VetsBoats]
**⚠ Flags:** [anything Alec needs to verify]
```

### STOP HERE

Do not select the final 5 or write the client-facing report. Alec will review the cards and combine with PF leads to select the best 5 overall for the opportunities report.
