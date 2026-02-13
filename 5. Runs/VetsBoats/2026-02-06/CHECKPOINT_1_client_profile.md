# CHECKPOINT 1: VetsBoats Client Profile & Identity Verification

**Date:** 2026-02-06
**Status:** Ready for Review

---

## 1. Client Identity (Verified)

| Field | Value | Source |
|-------|-------|--------|
| **Legal Name** | Wooden Boats For Veterans | ProPublica, pf_returns |
| **DBA** | VetsBoats (eff. Jan 1, 2024) | GuideStar, website |
| **EIN** | 46-4194065 (stored as 464194065) | ProPublica, pf_returns |
| **Tax Status** | 501(c)(3) Private Operating Foundation | ProPublica, pf_returns |
| **Filing Type** | 990-PF | ProPublica |
| **NTEE Code** | W99 (Public, Society Benefit - Other) | ProPublica, dim_recipients |
| **Address** | 1001 Bridgeway St, Suite 608, Sausalito, CA 94965 | ProPublica (updated) |
| **Phone** | (707) 334-3424 | Website |
| **Email** | tbmoran@vetsboats.org | Website |
| **Website** | vetsboats.org | Verified |
| **Founded** | 2014 (tax-exempt since June 2014) | ProPublica |

---

## 2. Financial Profile

### From Our Database (pf_returns)

| Tax Year | Revenue | Assets EOY | grants_to_orgs | preselected_only |
|----------|---------|------------|----------------|------------------|
| 2023 | $278,676 | $352,566 | FALSE | TRUE |
| 2022 | $389,352 | $94,449 | FALSE | TRUE |
| 2020 | $52,594 | $125,092 | FALSE | TRUE |
| 2019 | $66,714 | $113,668 | FALSE | TRUE |
| 2018 | $7,750 | $69,380 | FALSE | TRUE |

### From External Sources (FY2024 — more recent than our DB)

| Metric | Value | Source |
|--------|-------|--------|
| Revenue | $136,943 | ProPublica (FY2024 filing) |
| Expenses | $186,050 | ProPublica |
| Total Assets | $279,349 | ProPublica |
| Cash & Investments | $9,349 | ProPublica |
| Net Operating | -$49,107 (deficit) | Calculated |
| Debt | ~$300,000 | Pre-call brief (LENDonate) |
| Paid Employees | 0 | ProPublica, confirmed all-volunteer |

### Revenue for dim_clients Budget Tier
- FY2024 revenue: $136,943 → **Budget tier: Under $250K**
- Peak revenue (FY2022): $389,352
- Revenue is volatile — the $137K figure is the current reality

---

## 3. Mission & Programs

**Mission (official):**
> "To provide measurable improvement in health and well-being to military veterans who suffer from PTSD and Traumatic Injuries, using mindfulness-based therapeutic sailing."

**Key Programs:**
1. **Mindfulness-Based Therapeutic Sailing** — Day sailing excursions on SF Bay
2. **Sail Training** — Multi-day sailing instruction for veterans
3. **Wooden Boat Restoration** — Hands-on restoration (notably SV Clover, a 1938 WWII cutter)
4. **Multi-Day Voyages** — Extended trips; capstone Hawaii voyage planned with Clover
5. **Wheelchair Regatta Support** — Partnership serving disabled veterans
6. **Veteran Benefits Navigation** — Connecting veterans to VA resources

**Impact:** 2,500+ veterans and families served since founding

**Expansion Plans:** San Diego CA, Galveston TX, Springfield OH, Annapolis MD

---

## 4. Key People

| Name | Role | Notes |
|------|------|-------|
| **Terry Moran** | Founder & Executive Director | Navy F-14 pilot, USCG 100-ton Master, primary grant writer |
| **Jen Moran** | Marketing Director | Terry's wife |
| **Matt Goettelman** | Advisory Board Member | Former West Point, Goldman Sachs; advises family offices/foundations |
| **Tom Gilheany** | Board Member | Cybersecurity executive |
| **Matt Cline** | Board Member | Establishing Midwest operations |

**CORRECTION from sales call:** Terry referred to "Matt" as new "Director of Development" — this is Matt Goettelman, whose actual title is Advisory Board Member. He's not a development director; he advises on foundation/family office relationships.

---

## 5. Known Past Funders (EXCLUDE from report)

### Confirmed in Our Database (fact_grants)

| Foundation | EIN | Amount | Year | Purpose |
|------------|-----|--------|------|---------|
| Tahoe Maritime Foundation | 943073894 | $25,000 | 2023 | General purpose contribution |
| Henry Mayo Newhall Foundation | 946073084 | $15,000 | 2023 | Veterans sailing outings & emotional support/healing |
| Sidney Stern Memorial Trust | 956495222 | $3,500 | 2023 | General operating |

### From External Sources (not in our DB but referenced in pre-call brief)

| Foundation | Amount | Year | Source | DB Verification |
|------------|--------|------|--------|-----------------|
| Silicon Valley Community Foundation | $30,000 | 2023 | GuideStar/Candid | Not a private foundation — won't be in pf_returns |
| American Online Giving Foundation | $5,054-$24,151 | 2024-2025 | Cause IQ | DAF aggregator — won't be in pf_returns |
| Charis Fund | $5,000 | 2022 | Pre-call brief | **NOT CONFIRMED** — Charis Fund grants in our DB went to "Veteran Rites Inc", not VetsBoats |
| Bonnell Cove Foundation | $5,000+$2,500 | 2022-2023 | Pre-call brief | **NOT CONFIRMED** — No VetsBoats grants found; Bonnell Cove grants are maritime/environmental |
| Goodfellow Fund | $60,000 | 2020-2021 | Pre-call brief | **ERROR** — Pre-call brief confused "Center for Wooden Boats" (WA) with "Wooden Boats for Veterans" (CA) |
| JPMorgan Chase Foundation | $8,550 | 2018-2021 | Pre-call brief | **ERROR** — Same confusion; JPMorgan grants went to Center for Wooden Boats |
| Bristol-Myers Squibb Foundation | $2,520 | 2020 | Pre-call brief | **ERROR** — Same confusion with Center for Wooden Boats |

### Known Funders EIN List (for exclusion)

**Definitely exclude (confirmed grants to VetsBoats):**
- `943073894` — Tahoe Maritime Foundation
- `946073084` — Henry Mayo Newhall Foundation
- `956495222` — Sidney Stern Memorial Trust
- `946077619` — Charis Fund (confirmed by client 2026-02-06)
- `133556721` — Bonnell Cove Foundation (confirmed by client 2026-02-06)

**Also exclude (from external sources, not in our DB as private foundations):**
- Silicon Valley Community Foundation (community foundation, not in pf_returns)
- American Online Giving Foundation (DAF aggregator)

---

## 6. Data Quality Flags

| Flag | Impact | Mitigation |
|------|--------|------------|
| **Not in nonprofit_returns** | No IRS mission text, no 990/990-EZ financials | Using pf_returns + external sources |
| **No questionnaire** | Missing structured intake data | Constructing from sales call + research |
| **Files 990-PF** | `only_contri_to_preselected_ind = TRUE` is meaningless for them (they're not a grantmaker) | Ignore this flag in scoring context |
| **No embeddings** | Can't use semantic sibling search | Manual keyword-based siblings (already done) |
| **Revenue volatile** | $7.7K → $389K → $137K over 6 years | Using FY2024 ($137K) as current reality |
| **Pre-call brief errors** | Goodfellow, JPMorgan, BMS grants were for wrong org | Corrected; only 3 confirmed past funders |
| **0 paid staff** | Limits grant compliance capacity | Note in profile; affects "realistic action plans" |
| **~$300K debt** | 2x annual revenue | Important context for positioning |

---

## 7. Proposed Matching Keywords

Tested against `fact_grants.purpose_text` for hit counts:

### Primary Keywords (high specificity, good hit counts)

| Keyword | Hits | Rationale |
|---------|------|-----------|
| `veteran program` | 1,105 | Broad but relevant — VetsBoats runs veteran programs |
| `veteran support` | 1,018 | Common grant purpose language |
| `veteran service` | 1,041 | Common grant purpose language |
| `PTSD` | 348 | Core issue VetsBoats addresses |
| `veteran healing` | 305 | Directly aligned with mission |
| `veteran mental health` | 97 | Core focus area |
| `sailing program` | 103 | Sailing is the delivery mechanism |
| `veteran wellness` | 56 | Aligned with therapeutic mission |
| `adaptive sailing` | 26 | Similar org type |
| `therapeutic sailing` | 5 | Highly specific to VetsBoats |

### Secondary Keywords (lower hits but high relevance)

| Keyword | Hits | Rationale |
|---------|------|-----------|
| `maritime heritage` | 44 | Clover restoration, wooden boats |
| `veteran outdoor` | 35 | Outdoor recreation therapy |
| `sailing education` | 27 | Sail training program |
| `veteran recreation` | 18 | Recreation-based therapy |
| `wooden boat` | 11 | Core identity |
| `boat building` | 41 | Restoration programs |

### Excluded Keywords (too broad or not specific enough)

| Keyword | Hits | Why Excluded |
|---------|------|-------------|
| `military veteran` | 849 | Too broad — includes all veteran grants |
| `veteran trauma` | 133 | Includes medical/clinical trauma programs we don't match |
| `mindfulness` | 297 | Too broad — includes yoga, meditation, non-veteran contexts |
| `veteran suicide` | 66 | Too clinical — VetsBoats doesn't position as suicide prevention |

### Proposed `matching_grant_keywords` Array (10 keywords)

```
{
  "veteran sailing",
  "therapeutic sailing",
  "adaptive sailing",
  "sailing program",
  "veteran wellness",
  "veteran outdoor",
  "boat restoration",
  "wooden boat",
  "maritime heritage",
  "PTSD veteran"
}
```

**Logic:** These are specific enough to find relevant foundations without being so broad they flood with false positives. The primary "veteran program/service/support" keywords have 1,000+ hits each — too many to be useful as distinguishing signals. The proposed set balances specificity with coverage.

---

## 8. Proposed `target_grant_purpose`

> "Therapeutic sailing programs for military veterans suffering from PTSD and traumatic injuries, including mindfulness-based sailing outings, sail training, and wooden boat restoration to support veteran well-being and healing."

**Why this wording:**
- Matches the language in the Henry Mayo Newhall grant purpose ("veterans with sailing outings and lessons as a way to provide emotional support and healing")
- Includes the key program elements (therapeutic sailing, sail training, boat restoration)
- Uses "PTSD and traumatic injuries" from their actual mission statement
- Avoids jargon; uses IRS filing-style language
- Covers both the activity (sailing) and the outcome (well-being/healing)

---

## 9. Proposed dim_clients INSERT

| Field | Proposed Value |
|-------|----------------|
| name | Wooden Boats for Veterans |
| ein | 464194065 |
| state | CA |
| city | Sausalito |
| sector_ntee | W99 |
| sector_broad | W |
| org_type | 501(c)(3) private operating foundation |
| budget_tier | Under $250K |
| budget_min | 50000 |
| budget_max | 250000 |
| grant_size_seeking | $5,000 - $50,000 (small-medium grants) |
| grant_size_min | 5000 |
| grant_size_max | 50000 |
| grant_capacity | No dedicated grant staff (volunteers handle grants) |
| mission_text | To provide measurable improvement in health and well-being to military veterans who suffer from PTSD and Traumatic Injuries, using mindfulness-based therapeutic sailing. |
| project_need_text | Scaling from $150K to $500K annual fundraising to hire staff, expand nationally (San Diego, Galveston TX, Springfield OH, Annapolis MD), restore vessel Clover for Hawaii voyages, and service ~$300K organizational debt. |
| project_type | General operating + program expansion |
| project_keywords | {"therapeutic sailing","veteran PTSD","wooden boat restoration","mindfulness sailing","veteran healing","national expansion"} |
| populations_served | {"military veterans","veterans with PTSD","veterans with traumatic injuries","disabled veterans"} |
| geographic_scope | National (expanding from Bay Area) |
| known_funders | {"943073894","946073084","956495222","946077619","133556721"} |
| recipient_ein | 464194065 |
| email | tbmoran@vetsboats.org |
| status | active |
| matching_grant_keywords | {"veteran sailing","therapeutic sailing","adaptive sailing","sailing program","veteran wellness","veteran outdoor","boat restoration","wooden boat","maritime heritage","PTSD veteran","veteran fishing"} |
| excluded_keywords | {} |
| budget_target_min | 20000 |
| budget_target_max | 750000 |
| database_revenue | 278676.00 |
| database_assets | 352566.00 |
| budget_variance_flag | moderate |
| client_data_quality | partial |
| quality_flags | {"no_questionnaire","no_nonprofit_returns","files_990pf","revenue_volatile","pre_call_brief_errors_corrected"} |
| timeframe | monthly |
| questionnaire_date | NULL |
| questionnaire_version | NULL |
| target_grant_purpose | Therapeutic sailing programs for military veterans suffering from PTSD and traumatic injuries, including mindfulness-based sailing outings, sail training, and wooden boat restoration to support veteran well-being and healing. |

---

## 10. Discrepancies Found

| Issue | Detail | Resolution |
|-------|--------|------------|
| Pre-call brief said Goodfellow Fund gave $60K to VetsBoats | Those grants went to "Center for Wooden Boats" (different org in WA) | Removed from known funders |
| Pre-call brief said JPMorgan gave $8.5K to VetsBoats | Same error — JPMorgan grants to Center for Wooden Boats | Removed |
| Pre-call brief said BMS gave $2.5K | Same error | Removed |
| Sales call said "Director of Development" (Matt) | Matt Goettelman's actual title is Advisory Board Member | Corrected |
| Expansion plans: call said Cape Cod + Ohio | Website now says San Diego, Galveston TX, Springfield OH, Annapolis MD | Using current website info |
| Charis Fund $5K grant to VetsBoats | Not confirmed in our DB — Charis Fund grants to "Veteran Rites Inc" | Flagged as questionable |
| Bonnell Cove $7.5K to VetsBoats | Not confirmed in our DB | Flagged as questionable |

---

## Questions for Your Review

1. **Keywords:** The proposed 10 keywords focus on sailing/maritime + veteran/PTSD. Should I add broader veteran terms like "veteran program" (1,105 hits) even though they'll produce many false positives?

2. **target_grant_purpose:** Does the wording capture what Terry wants funded? Should it emphasize national expansion or the Clover restoration more?

3. **Budget range for sibling matching:** I have $27K-$685K (0.2x to 5x of $137K). The pre-call brief's FY2022 peak was $389K. Should we widen to account for their growth ambitions ($500K target)?

4. **Known funders:** Should I include Charis Fund and Bonnell Cove as known funders (exclude from report) even though they're not confirmed in our DB? The pre-call brief listed them but the data doesn't support it.

5. **Grant size seeking:** I proposed $5K-$50K based on their prior grants ($3.5K-$25K). Their $500K goal might warrant looking at larger grants too. Thoughts?
