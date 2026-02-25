# First Cohort Email Campaign: CA Test Batch (20 Emails)

**Date:** 2026-02-16
**Prompt:** Build prospect profiles and write personalized cold emails for first test cohort
**Status:** Complete — Ready for test send
**Owner:** Claude Code

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Claude Code | Initial: cohort selection, profiling, email drafting, sender script |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Cohort Selection](#cohort-selection)
3. [Profile Generation](#profile-generation)
4. [Email Drafting](#email-drafting)
5. [Sending Infrastructure](#sending-infrastructure)
6. [Files Created](#files-created)
7. [Next Steps](#next-steps)
8. [Notes](#notes)

---

## Executive Summary

Selected 20 California prospects (10 foundations + 10 nonprofits) as the first test cohort for the new "give first" cold email campaign. Built data profiles for each using angle-specific SQL queries against 8.3M grant records, then drafted 20 personalized emails with real, verifiable 990 data in the body. Created a lightweight sender script (`send_cohort.py`) with test and live modes that plugs into the existing SMTP infrastructure.

**Key numbers:**

| Metric | Value |
|--------|-------|
| Foundations selected | 10 (CA, mid-size, $5M-$500M assets) |
| Nonprofits selected | 10 (CA, $4.7M-$15.2M revenue, never contacted) |
| Emails drafted | 20 (all personalized with real grant data) |
| Foundation angle | New Grantee Discovery (scored 13/15) |
| Nonprofit angle | Peer Funder Discovery (scored 14/15) |
| Previously contacted | 0 (verified against campaign_prospect_status) |
| Bounced addresses | 0 (verified against suppression list) |

---

## Cohort Selection

### Selection Criteria

**Foundations (New Grantee Discovery angle):**
- State: California
- Has valid email (contains @)
- Accepts applications (only_contri_to_preselected = FALSE or NULL)
- Assets: $5M-$500M (mid-size, reachable via cold email)
- Active grantmaker: total_giving_5yr > $100K, unique_recipients >= 5
- Not previously contacted, not bounced
- Preferred personal email addresses over generic (info@, grants@)

**Nonprofits (Peer Funder Discovery angle):**
- State: California
- Has valid email (contains @, not calendar/junk)
- Never contacted (no record in campaign_prospect_status)
- Revenue: $500K-$50M
- Has NTEE code for peer matching

### Foundation Cohort (10)

| # | Foundation | EIN | Contact | Email | Assets | 5yr Giving | Trend |
|---|-----------|-----|---------|-------|--------|------------|-------|
| FDN-1 | Ralph M Parsons Foundation | 956085895 | Jennifer Price-Letscher | letscher@rmpf.org | $439M | $82.6M | declining |
| FDN-2 | Price Philanthropies | 465129465 | Terry Malavenda | stear@pricephilanthropies.org | $471M | $66.2M | declining |
| FDN-3 | S Mark Taper Foundation | 320516588 | Adrienne Wittenberg | QUESTIONS@SMTFOUNDATION.ORG | $186M | $27.0M | growing |
| FDN-4 | Zellerbach Family Foundation | 946069482 | (department) | COMMUNITYARTS@ZFF.ORG | $160M | $17.2M | stable |
| FDN-5 | Blue Shield CA Foundation | 942822302 | (generic) | BSCF@BLUESHIELDCAFOUNDATION.ORG | $77M | $131M | declining |
| FDN-6 | Doheny Foundation | 956202911 | Nina Shepherd | DOHENY@DOHENYFOUNDATION.ORG | $200M | $24.6M | stable |
| FDN-7 | Irwin Charity Foundation | 946069873 | Melissa Morazan | MMORAZAN@PFS-LLC.NET | $111M | $27.7M | growing |
| FDN-8 | Ann Jackson Family Foundation | 953367511 | Palmer Jackson Jr | palmer.jackson@gmail.com | $89M | $12.8M | declining |
| FDN-9 | Greenberg Animal Welfare | 954738423 | Robert Ferber | GREENBERGANIMALFOUNDATION@GMAIL.COM | $7.5M | $11.2M | declining |
| FDN-10 | O L Halsell Foundation | 956027266 | (admin) | mroach@ncousa.com | $49M | $11.2M | stable |

### Nonprofit Cohort (10)

| # | Organization | EIN | Contact | Email | Revenue | NTEE |
|---|-------------|-----|---------|-------|---------|------|
| NP-1 | Sacramento Tree Foundation | 942825234 | Jessica Sanders | hr@sactree.org | $15.2M | C36Z |
| NP-2 | Students Rising Above | 810615887 | Elizabeth Devaney | info@studentsrisingabove.org | $5.0M | T30 |
| NP-3 | Growth Public Schools | 474456355 | Audria Johnson | info@growthps.org | $4.9M | B29 |
| NP-4 | PlayCV | 871612445 | Amy Ramos | info@playcv.org | $4.9M | B80 |
| NP-5 | Oakland Children's Fairyland | 943209054 | Kymberly Miller | info@fairyland.org | $4.9M | N320 |
| NP-6 | Forever Balboa Park | 330849518 | Elizabeth Babcock | info@balboapark.org | $4.8M | X99 |
| NP-7 | Hyde Street Community Services | 450493846 | Joanne Azulay | info@hydestreetcs.org | $4.8M | S21 |
| NP-8 | Rancho Los Amigos Foundation | 953849600 | Deborah Arroyo | contact@ranchofoundation.org | $4.8M | E22I |
| NP-9 | East Palo Alto Tennis & Tutoring | 263316879 | (director) | contact@epatt.org | $4.7M | N66 |
| NP-10 | Children's Museum of Sonoma Co. | 203496878 | Collette Michaud | info@cmosc.org | $4.7M | A52 |

---

## Profile Generation

### Foundation Profiles (New Grantee Discovery)

For each foundation, identified the top 2 NTEE sectors by grant count (2019-2024), then found California nonprofits in those sectors that:
- Have been funded by 3-80 distinct foundations recently (mid-popularity, actually discoverable)
- The target foundation has NOT funded
- Were active in 2020-2024

**Query approach:** Two-pass. First pass identified top sectors per foundation. Second pass found candidate nonprofits via `fact_grants` JOIN `dim_recipients`, filtering out the foundation's existing grant recipients, ranked by number of co-funders.

| Foundation | Top Sectors | Example Matches |
|-----------|-------------|-----------------|
| Parsons | B (education), P (human services) | Thacher School (78 co-funders), Oakland Public Ed Fund (76), Braille Institute (76) |
| Price Philanthropies | P, B | United Friends of Children (77), Oakland Public Ed Fund (76), Social Good Fund (366) |
| S Mark Taper | A (arts), P | Film Collaborative (80), Segerstrom Center (77), Music Academy of the West (76) |
| Zellerbach | A (38% of grants!), P | Film Collaborative (80), Segerstrom Center (77), United Friends of Children (77) |
| Blue Shield CA | P, T (philanthropy), E (health) | Rady Children's Hospital (77), Focusing Philanthropy (78), PATH (78) |
| Doheny | P, B | Unity Shoppe (78), United Friends of Children (77), Oakland Public Ed Fund (76) |
| Irwin Charity | P, A | Film Collaborative (80), Segerstrom Center (77), United Friends of Children (77) |
| Ann Jackson | B, A | Film Collaborative (80), Thacher School (78), Segerstrom Center (77) |
| Greenberg Animal | D (animal, 47%), C (environment) | Golden Gate Parks Conservancy (80), Greater LA Zoo (76), Helen Woodward (71) |
| O L Halsell | P, O (youth dev) | United Friends of Children (77), Playworks (76), Braille Institute (76) |

### Nonprofit Profiles (Peer Funder Discovery)

For each nonprofit, identified CA peer organizations in the same NTEE sector, then found foundations that:
- Fund 3+ of their CA peers
- Have NOT funded the target nonprofit
- Accept applications (where data available)

| Nonprofit | NTEE Sector | Best Matches |
|-----------|-------------|-------------|
| Sacramento Tree Foundation | C (environment) | Clif Family (55 peers, growing), Schmidt Family (51 peers, $100K median), Bank of America (70 peers) |
| Students Rising Above | T (philanthropy) | CA Wellness Foundation (56 peers, $10K median), Bank of America (149 peers) |
| Growth Public Schools | B (education) | Enterprise Holdings (124 peers, $2.5K), Bank of America (532 peers) |
| PlayCV | B (education) | Enterprise Holdings (124 peers), Bank of America (532 peers) |
| Oakland Fairyland | N (recreation) | Dick's Sporting Goods (24 peers, growing), Enterprise Holdings (35 peers) |
| Forever Balboa Park | X (public benefit) | Bank of America (118 peers), Verizon Foundation (42 peers, growing) |
| Hyde Street Community | S (community dev) | CA Wellness Foundation (48 peers, $10K), Bank of America (91 peers) |
| Rancho Los Amigos | E (health) | CA Wellness Foundation (89 peers, $10K), Delta Dental (52 peers) |
| East Palo Alto Tennis | N (recreation) | Enterprise Holdings (35 peers), Bank of America (142 peers) |
| Children's Museum Sonoma | A (arts/museums) | Hewlett Foundation (175 peers, $125K median), Bank of America (273 peers) |

**Observation:** Bank of America Charitable appears across many nonprofits because it funds broadly. The higher-value matches are sector-specific: CA Wellness Foundation (health/community), Clif Family and Schmidt Family (environment), Enterprise Holdings (education), Hewlett (arts), Dick's Sporting Goods (recreation).

---

## Email Drafting

### Template Design

All 20 emails follow the "give first" strategy from the research:

- **Format:** Plain text, no HTML, no tracking pixels, no images
- **Length:** 60-90 words (slightly over the 50-80 target for foundation emails with 3+ org names)
- **Structure:** Hook (I analyze 990 data) -> Value (real names, real numbers) -> Soft CTA (want me to send more?)
- **Personalization level:** L3 (situation-specific) using actual grant records
- **No selling:** No mention of pricing, product, or service in first touch
- **Signature:** Name only, no phone, no links (keeps it clean and non-salesy)

### Foundation Email Template Pattern

```
Hi [First Name],

I [analyze/study] foundation giving [using/from] [public] 990 [data/filings].
[Foundation] has funded [N] organizations in [sectors] [in California / across California].

[Three/Five] organizations your co-funders support that [Foundation short] hasn't funded:

- [Org 1] -- [N] of your co-funders, $[X]M total
- [Org 2] -- [N] co-funders, $[X]M total
- [Org 3] -- [N] co-funders, $[X]M total

I have a longer list with giving trends. [Want me to send it? / Interested?]

Alec Kleinman
TheGrantScout
```

### Nonprofit Email Template Pattern

```
Hi [First Name],

I [analyze/study] foundation giving [using/from] [public] 990 [data/filings].
[N] foundations [actively fund / fund] [sector] organizations [across/in] California
but haven't connected with [Org]:

- [Foundation 1] -- funds [N] of your [CA] peers, $[X]K median grant[, growing]
- [Foundation 2] -- funds [N] peers, $[X]K median grant
- [Foundation 3] -- funds [N] peers

[I have a longer list... / I have a detailed brief...] [Interested? / Want me to send it?]

Alec Kleinman
TheGrantScout
```

### Variations Applied

To avoid all 20 emails reading identically, rotated:
- Opening verb: "analyze" vs "study"
- Data source phrasing: "990 data" vs "990 filings" vs "public 990 data"
- CTA phrasing: 5 different soft CTAs
- Greeting: first name where available, "Hi there" for generic contacts
- Greenberg email lists 5 orgs (all animal-specific) vs standard 3

### Recommended Send Order (by expected reply rate)

1. FDN-9 Greenberg (personal gmail, niche sector, 5 specific animal welfare matches)
2. FDN-3 S Mark Taper (growing giving, personal contact, strong arts matches)
3. FDN-7 Irwin Charity (growing giving, personal contact at management firm)
4. FDN-1 Parsons (personal email, large foundation with 590 recipients)
5. NP-1 Sacramento Tree (3 strong matches, all accept applications)
6. NP-8 Rancho Los Amigos (CA Wellness funds 89 of their peers)
7. NP-10 Children's Museum (Hewlett funds 175 of their peers)
8. NP-7 Hyde Street (CA Wellness is a strong sector-specific match)
9. FDN-8 Ann Jackson (personal gmail, arts/education focus)
10. NP-2 Students Rising Above (CA Wellness match, clear mission alignment)

---

## Sending Infrastructure

### Existing System

The campaign system uses:
- `grantscout_campaign.generated_emails` table for pre-generated email content
- `grantscout_campaign.senders` table with 10 TGS subdomain sender aliases
- `grantscout_campaign.sender_daily_stats` for per-sender tracking
- Central Google Workspace SMTP auth (alec@kleinmanventures.com) with send-as aliases
- SMTP: smtp.gmail.com:587

### New Script: `send_cohort.py`

Created a lightweight sender that bypasses the `generated_emails` table (which uses static templates) and sends directly from a JSON file of pre-written emails. Uses the same SMTP config and credentials.

**Modes:**

| Mode | Command | Behavior |
|------|---------|----------|
| Dry run | `python3 send_cohort.py --dry-run` | Preview all emails, no sending |
| Test | `python3 send_cohort.py --test` | Send all 20 to alec@kleinmansolutions.com with [TEST] prefix |
| Test (partial) | `python3 send_cohort.py --test --limit 3` | Send first 3 to test address |
| Live | `python3 send_cohort.py --live` | Send to real recipients, record in campaign_prospect_status |
| Live (specific) | `python3 send_cohort.py --live --ids FDN-1 NP-1` | Send only specified IDs |

**Features:**
- Reads from `cohort_emails.json` (20 structured email records)
- Test mode sends all emails to Alec's test address with ID-prefixed subjects
- Live mode records sends to `f990_2025.campaign_prospect_status` with vertical = 'new_grantee_discovery'
- Natural pacing (5-15 second random delay between emails)
- Ctrl+C graceful shutdown
- Confirmation prompt before sending

### SMTP Verification

| Check | Status |
|-------|--------|
| TGS_AUTH_EMAIL configured | alec@kleinmanventures.com |
| TGS_APP_PASSWORD configured | Set (19 chars) |
| SMTP server | smtp.gmail.com:587 |
| Dry run | Passed (all 20 emails load correctly) |
| Test send | Not yet run (pending user approval) |

---

## Files Created

| File | Path | Description |
|------|------|-------------|
| EMAILS_2026-02-16_first_cohort_CA.md | Enhancements/2026-02-16/ | All 20 emails in readable format with metadata, sending notes, A/B test plan |
| REPORT_2026-02-16_first_cohort_emails.md | Enhancements/2026-02-16/ | This report |
| cohort_emails.json | 6. Business/.../Email Campaign 2025-11-3/ | Structured JSON with 20 email records (to, subject, body, ein, type) |
| send_cohort.py | 6. Business/.../Email Campaign 2025-11-3/ | Sender script with test/live/dry-run modes |

### Database Changes

None. All queries were read-only SELECT statements. Database writes only happen when `send_cohort.py --live` is run.

---

## Next Steps

1. **Test today:** Run `python3 send_cohort.py --test --limit 3` to send 3 test emails, verify formatting in inbox
2. **Review emails:** Read all 20 in `EMAILS_2026-02-16_first_cohort_CA.md`, edit as needed, update `cohort_emails.json`
3. **Full test:** Run `python3 send_cohort.py --test` to send all 20 to test inbox
4. **Send tomorrow:** Run `python3 send_cohort.py --live --limit 10` (foundations first), then remaining 10 the next day
5. **Monitor:** Check for replies, bounces, and out-of-office responses over 3 days
6. **Follow-up:** Draft touch 2 emails (Day 3) with new data points for non-repliers
7. **Scale:** If reply rate > 5%, expand to next cohort (NY or TX, 20 more)

---

## Notes

### Observations

1. **Foundation email overlap:** Several suggested nonprofits (Unity Shoppe, Film Collaborative, Segerstrom Center) appear across multiple foundation profiles. This is because they're well-funded CA organizations in popular sectors. Each foundation still gets a unique email because the framing references their specific giving patterns.

2. **Nonprofit profile depth varies:** Sacramento Tree Foundation got 3 strong matches (all accept applications). Some nonprofits like Forever Balboa Park and East Palo Alto Tennis got only 2, with Bank of America being one. The Bank of America match is less compelling since they fund almost everything. Future cohorts should prioritize nonprofits with 3+ specific funder matches.

3. **Email addresses skew generic for nonprofits:** 7 of 10 nonprofit emails are info@ or hr@ addresses. These have lower open rates than personal emails. The foundation cohort has better email quality (5 personal, 2 organizational, 3 generic).

4. **No phone number or links in signature:** Intentional departure from the existing templates (which include phone, LinkedIn, Calendly). The research found 0-1 links optimal for first touch. Phone and links can go in follow-up emails.

5. **Em dashes used in emails:** The emails use em dashes (--) in the bullet point lists. Per the PDF formatting rules, em dashes should be avoided in client reports, but these are plain text cold emails, not PDF documents.

### Risks

| Risk | Mitigation |
|------|------------|
| Blue Shield CA Foundation is very large, unlikely to respond to cold email | Included for data coverage; expect no reply from FDN-5 |
| Generic emails (info@, hr@) may not reach decision-makers | Foundation emails prioritized personal addresses; NP emails are what's available |
| Some co-funder counts are very high (80+) suggesting ubiquitous funders | Filtered to 3-80 range for New Grantee Discovery to avoid mega-orgs |
| The same "Alec Kleinman / TheGrantScout" sender has been used for prior campaigns | Prior campaign was grant_alerts vertical to nonprofits; foundation contacts are fresh |

---

*Generated by Claude Code on 2026-02-16*
