# Sales & Marketing

## Folder Structure

### CRM/
**Primary prospect and call tracking system.**
- Access locally: `http://localhost:54321` (Supabase)
- Frontend: `CRM/frontend/index.html`
- See `CRM/CLI.md` for all management commands
- See `CRM/README.md` for full documentation

### Email_Campaign/
**Automated email outreach system.**
- Separate from CRM (different workflow)
- `sent_tracker.csv` - Emails sent
- `response_tracker.csv` - Response tracking
- `grant_alerts_prospects.csv` - Email prospect list

### LinkedIn/
**LinkedIn content strategy and posting queue.**
- `Carousels/` - PDF carousels and scripts
- `Queue/` - Posts waiting to be published
- `Research/` - Competitor and market research
- `Strategy/` - Overall LinkedIn strategy docs

### Materials/
**Sales collateral and reference docs.**
- `Call_Scripts/` - Cold call scripts
- `One_Pagers/` - Product one-pagers
- `Gameplans/` - Sales strategy documents
- `Research/` - Prospect research (e.g., VetsBoats)

### Archive/
**Pre-CRM data (reference only).**
- Original CSVs and Excel tracking
- DO NOT USE for active tracking
- See `Archive/README.md` for details

---

## Quick Reference

| Task | Where |
|------|-------|
| Log a call | CRM |
| View call queue | CRM → Queue |
| Import prospects | CRM → Import |
| Send cold emails | Email_Campaign/ |
| Post on LinkedIn | LinkedIn/Queue/ |
| Find call script | Materials/Call_Scripts/ |
| Check old data | Archive/ |

---

## Key Metrics (as of 2025-12-31)

| Metric | Value |
|--------|-------|
| Total prospects in CRM | 824+ |
| Foundation mgmt contacts | 101 (38 companies) |
| Nonprofit prospects | 600+ |
| Cold call conversion | 6% |
| Email conversion | 0.23% |

---

*Reorganized 2025-12-31 as part of CRM migration*
