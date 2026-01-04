# Archive - Pre-CRM Data

**Archived:** 2025-12-31
**Reason:** Data migrated to CRM system

---

## What's Here

This folder contains prospect lists and call tracking files that were used before the CRM was built. All data has been migrated to:

```
/4. Sales & Marketing/CRM/
```

---

## Do NOT Use These Files For

- Adding new prospects (use CRM)
- Logging calls (use CRM)
- Tracking pipeline (use CRM)

---

## When to Reference

- **Auditing:** Verify CRM data matches original source
- **Historical:** Check original criteria for prospect lists
- **Recovery:** If CRM data is lost (restore from these + CRM backups)

---

## Folder Contents

### Prospect_Lists/
Original CSVs with prospect data (26 files). Includes:
- Nonprofit call lists (600+ prospects)
- Foundation management contacts (101 contacts, 38 companies)
- Partner/publication outreach lists
- Mission clarity analysis files

### Call_Tracking/
`Beta Test Group Calls.xlsx` - Original call tracking before CRM.
- Nonprofits: 626 prospects, 78 calls logged
- Foundations: 146 prospects, 12 calls logged
- Foundation Mgmt: 101 contacts (0 calls at archive time)

### Foundation_Research/
Research and batch files from foundation contact enrichment project (Dec 2025).
- Batch_Files/: 24 intermediate batch files
- Prompts, reports, and analysis files

### Launch_Strategy/
Early prospect segmentation work (Dec 2025):
- Network analysis (beta client connections)
- Community foundation cohorts
- Nonprofit targeting criteria
- TA provider pools

### Cold_Calls_Scripts/
Python scripts used for prospect enrichment:
- `scrape_events.py` - Event scraping
- `enrich_with_places.py` - Google Places API enrichment
- Related prompts, reports, and lessons learned

### Partners_Research/
Publication and YouTube channel outreach research.

### Old_Campaigns/
Legacy email campaign code and dashboards.

---

## Migration Record

| Source File | Records | Migrated To | Date |
|-------------|---------|-------------|------|
| Beta Test Group Calls.xlsx (Nonprofits) | 626 | CRM prospects table | 2025-12-31 |
| Beta Test Group Calls.xlsx (Foundations) | 146 | CRM prospects table | 2025-12-31 |
| DATA_2025-12-18_fdn_mgmt_contacts_FINAL.csv | 101 | CRM prospects table | 2025-12-31 |
| DATA_2025-12-12_prospect_call_list_v2.csv | 600 | CRM prospects table | 2025-12-31 |

---

*Archived as part of CRM migration - see CRM/README.md for current system*
