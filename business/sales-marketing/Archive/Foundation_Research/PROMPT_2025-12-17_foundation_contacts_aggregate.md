# PROMPT: Aggregate Foundation Contact Research

**Date:** 2025-12-17  
**For:** Claude Code CLI  
**Run after:** Batches 1, 2, and 3 are complete

---

## Standards

**FIRST:** Review `CLAUDE.md` for project conventions before starting.

**Output location:** Save all outputs in the same folder as this prompt.

---

## Situation

Three parallel research batches have completed:
- `OUTPUT_2025-12-17_foundation_contacts_batch1.csv` (foundations 1-34)
- `OUTPUT_2025-12-17_foundation_contacts_batch2.csv` (foundations 35-67)
- `OUTPUT_2025-12-17_foundation_contacts_batch3.csv` (foundations 68-100)

Need to combine into final outputs.

**Location:** `C:\TheGrantScout\4. Sales & Marketing\Foundations\`

---

## Tasks

### 1. Combine CSVs

Merge all three batch files into one master CSV:

**File:** `TABLE_2025-12-17_foundation_contacts_100.csv`

Sort by foundation name alphabetically.

### 2. Create Detailed Writeup

**File:** `REPORT_2025-12-17_foundation_contacts_100.md`

Format each foundation like:

```markdown
### 1. [Foundation Name] (EIN: [EIN])

**Primary Contact:** [Name]
- **Title:** [Title]
- **LinkedIn:** [URL]
- **Phone:** [Number] (source: [source])
- **Email:** [Email] (source: [source])
- **Website:** [URL]

**Notes:** [Any notes from research]

---
```

### 3. Summary Statistics

At the top of the REPORT, include:

```markdown
## Summary

| Metric | Count |
|--------|-------|
| Total foundations researched | 100 |
| Contacts found | X |
| With LinkedIn | X |
| With direct email | X |
| With phone | X |
| Program-level contacts | X |
| ED/President only | X |
| Website not found | X |
| Appears inactive | X |

### Contact Title Breakdown
| Title Type | Count |
|------------|-------|
| VP/Director Programs | X |
| Chief Strategy/Impact | X |
| Grants Management | X |
| Program Officer | X |
| ED/President | X |
| Other | X |
```

### 4. Quality Flags

Create a section listing any foundations with issues:
- No contact found
- Website broken/missing
- Appears inactive
- Only has trustees (no staff)

### 5. Data Source Analysis

```markdown
## Research Methodology

### Where Data Came From
| Data Type | Primary Source | Secondary Source |
|-----------|---------------|------------------|
| Phone numbers | Foundation websites | 990 filings |
| Emails | Website staff pages | Pattern inference |
| Contact names | Website team pages | LinkedIn |
| LinkedIn URLs | Direct search | N/A |

### Coverage by Source
| Source | Foundations Found |
|--------|-------------------|
| Foundation website | X/100 |
| LinkedIn | X/100 |
| 990/ProPublica | X/100 |
| Other | X/100 |
```

---

## Outputs

| File | Description |
|------|-------------|
| `TABLE_2025-12-17_foundation_contacts_100.csv` | Combined CSV for tracking |
| `REPORT_2025-12-17_foundation_contacts_100.md` | Detailed writeup with all contacts |

---

## Notes

- Keep batch files as backup
- Flag any duplicates or inconsistencies between batches
- If any foundations were skipped, note why
