# f990_2025 Schema Summary

**Last Updated:** 2025-12-22
**Total Tables:** 30
**Total Size:** 75 GB

---

## Table Inventory

### Core Data Tables
| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| pf_returns | 683,304 | 680 MB | Private foundation 990-PF filings |
| pf_grants | 8,304,824 | 3,353 MB | Individual grant records (raw) |
| nonprofit_returns | 2,953,274 | 5,070 MB | 990/990-EZ nonprofit filings |
| officers | 25,140,446 | 4,304 MB | Board members and officers |
| schedule_a | 1,487,038 | 219 MB | Charity classifications |

### Dimension Tables (dim_)
| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| dim_foundations | 143,184 | 25 MB | Foundation master records |
| dim_recipients | 1,652,766 | 308 MB | Grant recipient master records |
| dim_clients | 7 | 32 kB | TheGrantScout client nonprofits |

### Fact Tables (fact_)
| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| fact_grants | 8,309,021 | 4,685 MB | Matched grant transactions |

### Calculated Tables (calc_)
| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| calc_foundation_profiles | 143,184 | 95 MB | Foundation giving profiles |
| calc_foundation_behavior | 112,520 | 40 MB | Openness scores, repeat rates |
| calc_foundation_features | 143,184 | 94 MB | Comprehensive foundation features for ML |
| calc_foundation_primary_sector | 457,093 | 35 MB | Foundation sector focus rankings |
| calc_recipient_profiles | 263,895 | 249 MB | Recipient funding profiles |
| calc_recipient_features | 1,654,327 | 448 MB | Comprehensive recipient features for ML |
| calc_recipient_prior_funders | 646,906 | 52 MB | Prior funder counts by year |
| calc_recipient_prior_grants | 646,906 | 52 MB | Prior grant counts by year |

### Embedding Tables (emb_)
| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| emb_grant_purposes | 8,322,998 | 48 GB | 384-dim vectors for grant purpose text |
| emb_nonprofit_missions | 528,833 | 3,343 MB | 384-dim vectors for nonprofit missions |
| emb_programs | 317,320 | 2,022 MB | 384-dim vectors for program descriptions |
| emb_prospects | 73,836 | 468 MB | 384-dim vectors for prospect missions |
| emb_clients | 7 | 192 kB | 384-dim vectors for client missions/projects |

### Staging Tables (stg_)
| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| stg_import_log | 1,673,831 | 682 MB | ETL run tracking |
| stg_processed_xml_files | 1,395,645 | 630 MB | XML file processing status |

### Reference Tables (ref_)
| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| ref_irs_bmf | 1,921,604 | 549 MB | IRS Business Master File |
| ref_org_name_lookup | 2,429,295 | 707 MB | Organization name lookup/normalization |
| ref_org_aliases | 150 | 64 kB | Organization name variations |
| ref_recipient_alias_mappings | 129 | 64 kB | Recipient canonical name mappings |

### Other Tables
| Table | Rows | Size | Purpose |
|-------|------|------|---------|
| prospects | 74,144 | 46 MB | Sales prospect list |
| fundraising_events | 273 | 384 kB | Fundraising event data |

---

## Key Relationships

```
fact_grants.foundation_ein → dim_foundations.ein
fact_grants.recipient_ein → dim_recipients.ein
pf_grants.return_id → pf_returns.id (CASCADE delete)
emb_grant_purposes.grant_id → fact_grants.id
officers.pf_return_id → pf_returns.id
officers.np_return_id → nonprofit_returns.id
schedule_a.np_return_id → nonprofit_returns.id
```

---

## Naming Convention

| Prefix | Meaning |
|--------|---------|
| `dim_` | Dimension table (entities) |
| `fact_` | Fact table (events/transactions) |
| `calc_` | Calculated/derived table |
| `emb_` | Embedding vectors |
| `stg_` | Staging/import tracking |
| `ref_` | Reference/lookup table |

---

## Recent Changes

| Date | Change |
|------|--------|
| 2025-12-22 | Schema cleanup - dropped 9 training artifacts (~10GB freed), renamed 17 tables with prefixes |
| 2025-12-17 | Added comprehensive feature tables for ML modeling |
| 2025-12-16 | Completed grant embedding generation (8.3M vectors) |

---

## Space Usage by Category

| Category | Size | % of Total |
|----------|------|------------|
| Embeddings (emb_) | 54 GB | 72% |
| Core Data | 13.6 GB | 18% |
| Calculated (calc_) | 1.1 GB | 1.5% |
| Reference (ref_) | 1.3 GB | 1.7% |
| Staging (stg_) | 1.3 GB | 1.7% |
| Dimension (dim_) | 0.3 GB | 0.4% |
