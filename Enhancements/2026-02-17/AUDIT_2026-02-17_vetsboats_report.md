# VetsBoats February 2026 Report - Full Audit

**Date:** 2026-02-17
**Report Audited:** `5. Runs/VetsBoats/2026-02-06/REPORT_2026-02-06_vetsboats_grant_report.md`
**Trigger:** Matt Goettelman reported bouncing email (hello@billsimpsonfoundation.org)
**Status:** Complete - All corrections applied

---

## Audit Methodology

Three verification layers, run independently:

| Layer | Method | What It Catches |
|-------|--------|-----------------|
| **1. Grant Data Cross-Check** | SQL queries against `f990_2025.fact_grants` for every cited number | Wrong amounts, wrong years, inflated counts |
| **2. Contact/Email Verification** | MX record checks + web research on foundation websites | Bouncing emails, wrong phone numbers, stale staff info |
| **3. Opportunity Verification** | Foundation website scraping + third-party sources (Instrumentl, GrantStation) | Wrong deadlines, incorrect application processes, stale contact methods |

---

## Summary Scorecard

| Foundation | Layer 1 (Data) | Layer 2 (Contacts) | Layer 3 (Opportunity) | Total Errors |
|---|---|---|---|---|
| #1 Bill Simpson | 2 minor | 1 critical + 1 high | 1 high (re-confirmed Jan-Apr window) | **5** |
| #2 Herzstein | 4 (incl Sailing Angels amount, PF count) | 1 caveat (Peter Nagel may be leaving) | 0 | **5** |
| #3 Kovler | 3 (PF count, repeat rate, NY geo) | 0 | 0 | **3** |
| #4 Barry | 3 (new grantees, FEHE amount, PSEC size) | 2 (Paul Callahan title, PSEC $) | 0 | **5** |
| #5 Van Beuren | 5 (trend reversed, repeat rate, etc.) | 3 (chairman wrong, Kim Dame title, Kaila email) | 0 | **8** |
| **TOTAL** | **17** | **7** | **1** | **26** |

---

## All Corrections Applied

### Critical (Would Mislead Client)

| # | Foundation | Original | Corrected | Source |
|---|---|---|---|---|
| 1 | Bill Simpson | Email: hello@billsimpsonfoundation.org | elizabeth.burdette@signaturefd.com | 990-PF filing, Grantmakers.io |
| 2 | Kovler | 41 confirmed PF-to-PF grants | 6 confirmed | fact_grants SQL |
| 3 | Van Beuren | "Declining, 31% decrease" | "Growing, ~$8M to ~$14.6M" | fact_grants SQL |
| 4 | Barry | PSEC "$11.8B" | "$7.3B AUM" | SEC filings, Yahoo Finance |

### High (Significant Inaccuracy)

| # | Foundation | Original | Corrected | Source |
|---|---|---|---|---|
| 5 | Herzstein | 9 PF-to-PF grants | 5 confirmed | fact_grants SQL |
| 6 | Bill Simpson | Phone: (317) 337-9550 | (404) 473-4924 | 990-PF via Grantmakers.io |
| 7 | Barry | "8-12 new grantees/year" | "3-10 new grantees/year" | fact_grants SQL |
| 8 | Van Beuren | Chairman: Archbold D. Van Beuren | Chair: Barbara van Beuren; Archbold is Vice Chair | vbcfoundation.org/about |
| 9 | Van Beuren | Kim Dame, Grants Manager | Kim Dame is Operations Manager (not grants contact) | CauseIQ, vbcfoundation.org |
| 10 | Bill Simpson | Application window: conflicting info | Website says Jan-Apr; 990-PF says rolling. Report now shows both. | billsimpsonfoundation.org/contact |

### Medium (Directionally Correct but Inaccurate)

| # | Foundation | Original | Corrected | Source |
|---|---|---|---|---|
| 11 | Herzstein | Sailing Angels "$12K (2022)" | $10K (2022), $12K (2023) | fact_grants SQL |
| 12 | Herzstein | "36% increase" trend | ~11% increase | fact_grants SQL |
| 13 | Herzstein | Repeat rate 49% | 56% | fact_grants SQL |
| 14 | Kovler | Repeat rate 58% | 79% | fact_grants SQL |
| 15 | Van Beuren | Repeat rate 67% | 61% | fact_grants SQL |
| 16 | Bill Simpson | Repeat rate 17% | 23% | fact_grants SQL |
| 17 | Bill Simpson | Geographic: NC 42% | NC 36% (all states adjusted) | fact_grants SQL |
| 18 | Kovler | NY 5% | NY 8% | fact_grants SQL |
| 19 | Barry | Paul Callahan "Executive Director" | CEO | sailtoprevail.org |
| 20 | Barry | Tom Brunner "CEO" | President and CEO | glaucoma.org |
| 21 | Van Beuren | Sailing total "$630K+" | ~$560K | fact_grants SQL |
| 22 | Van Beuren | "20-37 new grantees/year" | 15-32 | fact_grants SQL |
| 23 | Van Beuren | Kaila Acheson: kacheson@vbcfoundation.org | support@vbcfoundation.org (per grants page) | vbcfoundation.org/grants |
| 24 | Barry | FEHE "$4.3M/year" | $3.7M/year avg ($14.9M total) | fact_grants SQL |
| 25 | Herzstein | Sailing Angels "$12K/yr" in summary | "$10-12K/yr" | fact_grants SQL |

### Low (Verified as Accurate)

| Foundation | What Passed |
|---|---|
| Bill Simpson | CRAB $80K (2024), Freedom Waters $10K (2023), Guide Dogs amounts, assets $18M, 85% general support |
| Herzstein | All veteran grant amounts, annual giving $4.3M, median $8K, 88% Texas, assets $127M, Renee Masaryk President confirmed |
| Kovler | Judd Goldman Adaptive Sailing amounts, annual giving $5.5M, median $3K, Ron Levin/Invest For Kids connection confirmed |
| Barry | All Sail to Prevail amounts, Guardian Revival $1.2M, Veterans Consortium $320K, assets $477M, no unsolicited requests confirmed |
| Van Beuren | Sail to Prevail $25-30K/yr, IYRS $115K, annual giving $10.7M, median $15K, geographic 50% RI, Elizabeth Lynn confirmed |

---

## MX Validation Results

| Domain | MX Records | Status |
|---|---|---|
| signaturefd.com | signaturefd-com.mail.protection.outlook.com | PASS (Office 365) |
| billsimpsonfoundation.org | aspmx.l.google.com (Google Workspace) | PASS (domain works, hello@ mailbox bounces) |
| herzsteinfoundation.org | herzsteinfoundation-org.mail.protection.outlook.com | PASS |
| kovler-b.com | eforward1-5.registrar-servers.com | PASS (forwarding) |
| vbcfoundation.org | vbcfoundation-org.mail.protection.outlook.com | PASS |

## Website Liveness

| URL | HTTP Status |
|---|---|
| billsimpsonfoundation.org | 200 |
| herzsteinfoundation.org | 200 |
| barryfamilyfoundation.org | 200 |
| vbcfoundation.org | 200 |
| kovler-b.com | 404 (no public website) |
| apply.yourcausegrants.com (Van Beuren portal) | 200 |

---

## Caveats on Methodology

1. **Funding trend comparison** is sensitive to missing years in the DB (2021 missing for Van Beuren and Herzstein). Comparisons use available years only.
2. **"New grantees" for Barry** - 2019 is first year in DB so all grantees appear new. Range uses 2020-2022 only.
3. **Repeat funding rate** counts recipients appearing 2+ times across all DB years. Pipeline may use different methodology.
4. **Peter Nagel (Herzstein)** - still listed on website but foundation is actively hiring for same role. Status uncertain.
5. **kovler-b.com** returns 404 - the app@kovler-b.com email may still work via MX forwarding.
6. **"Trusted advisor" (Tom Brunner for Barry)** - plausible given glaucoma research funding pattern but cannot independently verify.

---

## Recommendations for Future Reports

1. **Add automated SQL verification step** before delivery (every cited number checked against DB)
2. **Run MX + website checks** on all email domains and URLs
3. **Verify staff/contacts on foundation websites** before including in report
4. **Cross-reference 990-PF claims with foundation websites** when they conflict (website is more current)
5. **Build `09_audit_report.py`** to automate the data verification layer

---

*Generated by Claude Code on 2026-02-17*
