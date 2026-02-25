# EIN Corrections: VetsBoats Supplemental Report Foundations

**Date:** 2026-02-21
**Purpose:** Corrected EINs for 4 foundations where prompt-provided EINs did not match DB records. Use DB EINs for all future queries.

| Foundation | Prompt EIN | DB EIN (correct) | Verified By |
|---|---|---|---|
| St. Francis Sailing Foundation | 942956977 | 942956977 | Direct match |
| Kim & Harold Louie Family Foundation | 843767498 | 870757807 | Name ILIKE match in pf_returns (CA, Burlingame) |
| Charles H. Stout Foundation | 363441837 | 942797249 | Name ILIKE match in pf_returns (NV, Reno) |
| Kovler Family Foundation | 366080579 | 366152744 | Name ILIKE match in pf_returns (IL, Chicago) |
| Howard Family Foundation | 366538061 | 367041179 | Name match + verified Judd Goldman + Wounded Warrior grants |

**Note:** Kovler grants are all flagged `is_individual = TRUE` in pf_grants. Pull metrics without the `is_individual = FALSE` filter for this foundation.
