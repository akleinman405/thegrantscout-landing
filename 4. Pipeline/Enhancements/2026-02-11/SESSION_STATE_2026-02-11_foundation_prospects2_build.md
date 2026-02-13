# SESSION STATE: Building foundation_prospects2 Table - 2026-02-11

**Last Updated:** 2026-02-11
**Purpose:** Preserve context for building a new comprehensive foundation prospects table
**Status:** In Progress

---

## CURRENT STATUS - WHERE WE ARE

### Current Step
We just finished adding 7 columns to `f990_2025.foundation_prospects2` (last_filing_year, app fields, phone). The table has 143,184 rows with identity + address + application process + phone data populated.

Next: decide what columns to add next (website? assets? financials? grant metrics? officers?).

### Remaining Steps
1. Add more columns to `foundation_prospects2` (user is building step by step, asking questions as we go)
2. Potentially add: website_url, total_assets, grant totals, grantee counts, officers/contacts, mission text, classification flags, NTEE codes
3. No final column list has been decided yet -- user is exploring the data interactively

---

## What's Done

### Database Table Created
- **`f990_2025.foundation_prospects2`** -- 143,184 rows, one per foundation (EIN is unique)
- Populated from `pf_returns` using most recent filing per EIN for identity fields, most recent NON-NULL value per EIN for app/phone fields

### Current Columns in foundation_prospects2

| Column | Source | Population |
|--------|--------|-----------|
| `id` | Serial PK | 143,184 (starts at 77348 due to shared sequence) |
| `ein` | `pf_returns.ein` | 143,184 (unique) |
| `foundation_name` | `pf_returns.business_name` | 143,184 |
| `address_line1` | `pf_returns.address_line1` | 143,184 |
| `address_line2` | `pf_returns.address_line2` | 0 (dead column in source) |
| `city` | `pf_returns.city` | 143,184 |
| `state` | `pf_returns.state` | 143,184 |
| `zip` | `pf_returns.zip` | 143,184 |
| `last_filing_year` | `MAX(tax_year)` from pf_returns | 143,184 |
| `app_submission_deadlines` | Most recent non-null from pf_returns | 33,066 |
| `app_restrictions` | Most recent non-null from pf_returns | 33,171 |
| `app_form_requirements` | Most recent non-null from pf_returns | 33,301 |
| `app_contact_name` | Most recent non-null from pf_returns | 35,162 |
| `app_contact_phone` | Most recent non-null from pf_returns | 33,619 |
| `phone_num` | Most recent non-null from pf_returns | 138,009 |

### Documentation Created
- **`2. Docs/sales_foundation_prospects_column_provenance.md`** -- Detailed provenance of every column in the OLD `sales_foundation_prospects` table (761 rows, B2B sales)
- **`2. Docs/pf_returns_column_reference.md`** -- Full column reference for `pf_returns` with population stats
- **`2. Docs/pf_returns_column_reference.docx`** -- Word doc version of same
- **`2. Docs/generate_pf_returns_docx.py`** -- Script that generates the .docx

---

## What's Not Started
- Adding remaining columns (website, assets, financials, grant metrics, classification flags, etc.)
- Any filtering or scoring logic
- No report file created yet for this session

---

## Decisions Made

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Use most-recent-non-null for app fields and phone | Most recent filing only | Recovers ~2,750 extra app field values and ~8,450 extra phone numbers where latest filing went null |
| Include ALL 143K foundations | Filtered subset like old table (761) | User wants a comprehensive table this time, filtering comes later |
| Keep old `sales_foundation_prospects` (761 rows) | Replace it | Different purpose: old one is curated B2B sales with CRM data, new one is comprehensive |

---

## Key Data Findings

### pf_returns Structure
- **638,698 total rows**, 143,184 unique EINs, tax years 2016-2024
- One row per filing per foundation per tax year (some amended return duplicates)
- 7 dead columns that are never populated: `address_line2`, `email_address_txt`, `formation_yr`, `mission_desc`, `primary_exempt_purpose`, `activity_code_1/2/3`
- 3 field groups were enriched post-import: NTEE codes (from IRS BMF), website URLs (scraped), phone numbers (propagated across years)

### Application Fields (~23-25% populated)
- `app_submission_deadlines`: 33,066 foundations, but top values are junk ("NONE", "N/A"). Real deadlines start around position 12 ("APRIL 1" = 124 foundations)
- `app_restrictions`: 33,171 foundations, similar junk pattern
- `app_form_requirements`: 33,301 foundations, more useful -- "LETTER" (516), "WRITTEN REQUEST" (278), etc.
- `app_contact_email`: only 10,092 foundations (7%) -- sparsest field

### Phone Comparison
- `phone_num`: 138,009 foundations (96.4%) -- the main phone from the filing header
- `app_contact_phone`: 33,619 foundations (23.5%) -- the application-specific contact
- When both exist (29,033 foundations): 65.8% are the same number, 34.2% differ
- `phone_num` is the field to use for general contact

### application_submission_info JSONB
- Clean structure: always `{name, phone, email, address}`, 4 keys
- Contains exact same data as the separate `app_contact_*` columns (confirmed: 35,138 exact name matches, 0 different)
- Only bonus: has an `address` subfield (application mailing address) that has no separate column

### Multi-Value Stability
- Most foundations (78-87%) have the same app field value across all filings
- `app_contact_name` has the most variation: 21% have 2+ different values (staff turnover)
- Using most recent non-null is the right approach

---

## Database Queries That Worked

```sql
-- Most recent non-null pattern (used for all app fields and phone)
UPDATE f990_2025.foundation_prospects2 fp
SET app_submission_deadlines = sub.val
FROM (
    SELECT DISTINCT ON (ein) ein, app_submission_deadlines as val
    FROM f990_2025.pf_returns
    WHERE app_submission_deadlines IS NOT NULL AND app_submission_deadlines != ''
    ORDER BY ein, tax_year DESC
) sub
WHERE fp.ein = sub.ein;

-- Count foundations where latest is null but a past filing has value
WITH latest AS (
    SELECT DISTINCT ON (ein) ein, app_submission_deadlines
    FROM f990_2025.pf_returns ORDER BY ein, tax_year DESC
),
any_nonnull AS (
    SELECT ein, bool_or(app_submission_deadlines IS NOT NULL AND app_submission_deadlines != '') as ever_had
    FROM f990_2025.pf_returns GROUP BY ein
)
SELECT COUNT(*) FILTER (WHERE (l.app_submission_deadlines IS NULL OR l.app_submission_deadlines = '') AND a.ever_had)
FROM latest l JOIN any_nonnull a USING (ein);
```

---

## Technical Notes
- MCP postgres tool times out on large queries (INSERT 143K rows, COUNT DISTINCT on 638K rows). Use `psql` via Bash tool for bulk operations.
- MCP postgres tool enters aborted transaction state after errors. Use psql for multi-query research.
- `DISTINCT ON (ein) ... ORDER BY ein, tax_year DESC` is the standard pattern for "latest value per foundation"
- The serial ID sequence is shared, so foundation_prospects2 IDs start at 77348 (not 1)

---

*Generated by Claude Code on 2026-02-11*
