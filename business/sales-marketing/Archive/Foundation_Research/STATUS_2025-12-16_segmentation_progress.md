# Foundation Segmentation Research - Progress Checkpoint

**Date:** 2025-12-16
**Task:** PROMPT_2025-12-15_foundation_segmentation_phase1.md
**Status:** COMPLETE

---

## Completed

### Part A: Existing Research Review ✅
Reviewed all files in `4. Sales & Marketing/Launch Strategy/`:
- OUTPUT_2025-12-10.1_outreach_strategy_analysis.md - Comprehensive 18-avenue outreach strategy
- CHAT_2025-12-10.1_capacity_building_programs_brainstorm.md - Government/SBA capacity programs
- 2. Community Foundations/ - 50 community foundations researched, top 20 identified
- 4. TA Provider Pools/ - 21 state TA provider programs, King County & PANO top picks

### Part B: Discovery Queries - Partial ✅

**Q1-3: Foundation Size & Volume** ✅
| Metric | Value |
|--------|-------|
| Foundations with 10+ grantees (EIN) | 32,172 |
| Foundations with 50+ grantees | 4,506 |
| Foundations with 100+ grantees | 1,471 |
| Foundations with 200+ grantees | 532 |
| Under $100K giving | 14,374 |
| $100K-$500K giving | 5,690 |
| $500K-$1M giving | 1,158 |
| $1M-$5M giving | 1,018 |
| $5M+ giving | 190 |
| Active 2023-2024 | 92,906 |

**Q4-6: Capacity Building Patterns** ✅
| Keyword | Grant Count |
|---------|-------------|
| capacity building | 6,462 |
| technical assistance | 2,653 |
| organizational development | 628 |
| general operating | 488,384 |
| operating support | 467,519 |
| infrastructure | 3,847 |
| **TOTAL (any CB keyword)** | **743,967** |

- Total foundations with grants: 112,520
- Foundations with CB grants: 13,406
- **Percentage with CB grants: 11.9%**

**Q5: Top 20 CB Foundations** ✅
1. WK Kellogg Foundation (MI) - 451 CB grants, $454M assets, Open
2. THE CALIFORNIA ENDOWMENT (CA) - 373 CB grants, $4.5B assets, Preselected
3. THE FORD FOUNDATION (NY) - 335 CB grants, $16.8B assets, Open
4. KEN BIRDWELL FOUNDATION (WA) - 257 CB grants, $100M assets, Preselected
5. EDWARD JONES FOUNDATION (MO) - 211 CB grants, $101M assets, Preselected
6. MEYER MEMORIAL TRUST (OR) - 206 CB grants, $885M assets, Open
7. Community Memorial Foundation (IL) - 195 CB grants, $99M assets, Open
8. THE ROBERT WOOD JOHNSON FOUNDATION (NJ) - 160 CB grants, $13.7B assets, Open
9. Annie E Casey Foundation Inc (MD) - 159 CB grants, $2.3B assets, Preselected
10. ROGERSSLATER FOUNDATION INC (GA) - 136 CB grants, $3.6M assets, Open
(+ 10 more in query results)

**Q7-8: Intermediary/Consultant Funding** ✅
| Name Pattern | Grant Count |
|--------------|-------------|
| Consulting | 753 |
| Advisors | 1,499 |
| Associates | 3,567 |
| LLC | 7,402 |
| Partners | 39,135 |
| Group | 16,628 |
| Solutions | 6,073 |
| **TOTAL intermediary patterns** | **74,223** |

| Purpose Keyword | Grant Count |
|-----------------|-------------|
| evaluation | 2,171 |
| consulting | 553 |
| assessment | 1,907 |
| technical assistance | 2,653 |
| training | 27,527 |

**Q9: Top 20 Intermediary Funders** ⏳ INTERRUPTED (query was running)

---

## Remaining Queries to Run

### Q9: Top 20 foundations funding intermediaries (rerun)

### Q10-13: Geographic Distribution
- Q10: Top 10 states by capacity-building foundations
- Q11: California foundations with 20+ grantees
- Q12: New York foundations with 20+ grantees
- Q13: Regional (>80% one state) vs National (<50% any state)

### Q14-15: Grantee Type Concentration
- Q14: Foundations specializing in specific sectors (>50% to one area)
- Q15: Most common recipient NTEE codes

### Q16-18: Officer/Contact Data
- Q16: Most common officer titles in foundations
- Q17: Foundations with Program/Executive/Director/Grants officers
- Q18: Sample 10 foundations with officer lists

---

## Remaining Tasks

- [ ] Complete remaining queries (Q9-18)
- [ ] Part C: Propose 6 segmentation frameworks with criteria
- [ ] Part D: Prioritization recommendations
- [ ] Generate final report: REPORT_2025-12-15_foundation_segmentation_research.md

---

## Resume Instructions

When resuming, tell Claude:

> "Continue the foundation segmentation research from STATUS_2025-12-16_segmentation_progress.md.
> Pick up at Q9 (top 20 foundations funding intermediaries) and complete remaining queries Q10-18,
> then write the segmentation framework and final report."

---

## Database Connection Info
```python
import psycopg2
conn = psycopg2.connect(
    host='172.26.16.1', port=5432, database='postgres',
    user='postgres', password='kmalec21'
)
```

Tables used:
- f990_2025.pf_grants (filer_ein, recipient_ein, recipient_name, purpose, amount, tax_year)
- f990_2025.pf_returns (ein, business_name, state, total_assets_eoy_amt, only_contri_to_preselected_ind)
- f990_2025.officers (ein, person_nm, title_txt)
