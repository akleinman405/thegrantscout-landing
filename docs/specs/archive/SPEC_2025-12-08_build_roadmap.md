# BUILD_ROADMAP.md

**Document Type:** SPEC
**Purpose:** What's left to build and priorities
**Date:** 2025-12-08
**Version:** 1.0

---

## 1. Current State Summary

### What's Working Today

| Component | Status | Details |
|-----------|--------|---------|
| F990 2025 Database Import | Complete | 85,470 foundations, 1,624,501 grants (2016-2024) |
| Database Schema (f990_2025) | Complete | 6 tables: pf_returns, pf_grants, nonprofit_returns, officers, schedule_a, import_log |
| Landing Page | Built | Next.js 14, responsive, form UI coded |
| Matching Algorithm Code | Exists | `matching_algorithm.py` - needs optimization |
| Beta Reports (Round 1) | Delivered | 5 orgs in BG1, 1 in BG2 |

### What's Manual (Should Be Automated)

| Manual Process | Current Effort | Automation Priority |
|----------------|----------------|---------------------|
| Report generation | 40+ hours per org | Critical |
| Foundation website scraping | Per-foundation manual | High |
| Opportunity discovery | Web search per client | High |
| Grant purpose text matching | Manual review | Medium |
| Contact info extraction | Manual lookup | Medium |
| QA validation | Human review | Medium |

### What's Broken or Incomplete

| Issue | Status | Impact |
|-------|--------|--------|
| Grant purpose text parser | Fixed (Dec 5) | Was using wrong XPath (`PurposeOfGrantTxt` vs `GrantOrContributionPurposeTxt`) |
| Website form API connection | Not connected | CTA button doesn't submit |
| Mobile header | Needs fix | Words cut off, too busy |
| Foundation intelligence table | Empty | Openness scores, patterns not calculated |
| Current opportunities | Only ~42 | Need 500+ for production |
| Recipient EIN matching | Sparse | Many grants lack recipient EINs |

### Key Blockers

1. **No automated matching-to-report pipeline** - Each report requires extensive manual research
2. **Openness scoring not implemented** - Can't rank foundations by likelihood to fund new grantees
3. **Website scraping infrastructure missing** - Can't automatically check for current opportunities
4. **QA process undefined** - Beta errors (wrong grant names, expired deadlines, broken links)

---

## 2. Critical Path Items

### Must-Haves Before First Paying Customer

| Priority | Item | Dependency | Effort |
|----------|------|------------|--------|
| P0 | Complete BG1 Round 2 reports | None | Active |
| P0 | Fix Ka Ulukoa Bank of Hawaii deadline | None | Small |
| P0 | Validate F990 data quality | None | Small |
| P1 | Implement openness scoring | Database schema | Medium |
| P1 | Build foundation intelligence table | Openness scoring | Medium |
| P1 | Connect website form API | None | Small |
| P2 | Build semi-automated report generator | Foundation intelligence | Large |
| P2 | Create 50+ current opportunities | Web scraping | Medium |
| P2 | QA checklist implementation | Report template | Small |

### Conversion Readiness Checklist

- [ ] One complete report delivered with <5 errors
- [ ] Pricing validated (~$100/mo confirmed)
- [ ] Report format validated (opp-focused vs foundation-focused)
- [ ] Website form connected and working
- [ ] Payment processing set up
- [ ] Email automation ready (Brevo)

---

## 3. Phase 1: Database Completion

### 3.1 Tables to Populate

| Table | Current State | Action Needed |
|-------|---------------|---------------|
| foundation_intelligence | Empty | Create and populate |
| matches | Empty | Generate for beta clients |
| current_opportunities | ~42 records | Expand to 500+ |

### 3.2 Derived Fields to Calculate

**New Table: foundation_intelligence**

| Field | Calculation | Source |
|-------|-------------|--------|
| openness_score | % of grants to first-time recipients | pf_grants history |
| repeat_funding_rate | % of grantees funded 2+ times | pf_grants grouping |
| geographic_concentration | Top 3 states by grant count | pf_grants.recipient_state |
| typical_grant_size | Median, min, max grant amounts | pf_grants.amount |
| sector_concentration | Top NTEE codes funded | Recipient enrichment |
| giving_trend | 3-year rolling average change | pf_grants by year |
| last_active_year | Most recent grant year | MAX(pf_grants.tax_year) |
| application_status | 'Open'/'Preselected'/'Unknown' | pf_returns flags |

**SQL Task: Create foundation_intelligence table**

```sql
CREATE TABLE f990_2025.foundation_intelligence (
    id SERIAL PRIMARY KEY,
    ein VARCHAR(20) NOT NULL UNIQUE,
    openness_score NUMERIC(5,2),
    repeat_funding_rate NUMERIC(5,2),
    geographic_concentration JSONB,
    typical_grant_min NUMERIC(15,2),
    typical_grant_median NUMERIC(15,2),
    typical_grant_max NUMERIC(15,2),
    sector_concentration JSONB,
    giving_trend VARCHAR(20),
    last_active_year INTEGER,
    application_status VARCHAR(50),
    calculated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (ein) REFERENCES pf_returns(ein)
);
```

### 3.3 Data Quality Fixes

| Issue | Query to Identify | Fix |
|-------|-------------------|-----|
| NULL grant purposes | `SELECT COUNT(*) FROM pf_grants WHERE purpose IS NULL` | Backfill ran Dec 5 |
| Placeholder websites | `WHERE website_url IN ('N/A', 'NONE', '0', 'website')` | Filter in queries |
| Missing recipient EINs | `WHERE recipient_ein IS NULL` | ProPublica API enrichment |
| Duplicate returns | `GROUP BY ein, tax_year HAVING COUNT(*) > 1` | Keep most recent |

### 3.4 Python Scripts Needed

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `calculate_openness_scores.py` | Compute openness for all foundations | pf_grants | foundation_intelligence |
| `calculate_repeat_rates.py` | Compute repeat funding metrics | pf_grants | foundation_intelligence |
| `enrich_recipient_eins.py` | Add EINs via ProPublica | pf_grants | pf_grants.recipient_ein |
| `validate_data_quality.py` | Run quality checks | All tables | Validation report |

---

## 4. Phase 2: Automation

### 4.1 Scripts to Build

| Script | Priority | Dependencies | Purpose |
|--------|----------|--------------|---------|
| `generate_matches.py` | High | foundation_intelligence | Score foundations for a nonprofit |
| `scrape_foundation_websites.py` | High | Top match list | Find current opportunities |
| `generate_report.py` | High | matches, opportunities | Create PDF/HTML reports |
| `validate_opportunities.py` | Medium | current_opportunities | Check deadlines, links |
| `send_email_alert.py` | Medium | Brevo API | Notify clients |

### 4.2 Manual Steps to Eliminate

| Current Manual Step | Automation Approach |
|---------------------|---------------------|
| Research each foundation individually | Batch query foundation_intelligence |
| Check foundation websites for RFPs | Scheduled scraping + AI extraction |
| Format report sections | Template-based generation |
| Verify deadlines current | Automated date parsing + validation |
| Compile contact information | Extract from pf_returns + scraping |

### 4.3 Where AI Integration Happens

| Step | AI Role | Model/Approach |
|------|---------|----------------|
| Grant purpose matching | Semantic similarity | Sentence-BERT embeddings |
| Website RFP extraction | Structured extraction | Claude API / GPT-4 |
| Positioning strategy | Generate recommendations | Claude API |
| QA review | Error detection | Claude API |
| Report narrative | Generate "Why This Fits" | Claude API |

### 4.4 Report Generation Pipeline

```
INPUT: nonprofit_id
  |
  v
[1. MATCH] Query foundation_intelligence
  → Score foundations using 10-signal algorithm
  → Filter: grants_to_organizations_ind = TRUE
  → Filter: only_contri_to_preselected_ind = FALSE/NULL
  → Filter: last_active_year >= CURRENT_YEAR - 3
  |
  v
[2. ENRICH] For top 20 matches
  → Scrape foundation website for current RFPs
  → Extract contact info, deadlines, requirements
  → Validate links and dates
  |
  v
[3. RANK] Score opportunities
  → Apply grant size alignment
  → Apply geographic match
  → Apply purpose text similarity
  |
  v
[4. GENERATE] Create report
  → Populate template with top 5-10 opportunities
  → Generate positioning strategies (AI)
  → Create funder snapshots (8 metrics)
  → Build timeline
  |
  v
[5. QA] Validate output
  → Check all links
  → Verify deadlines not passed
  → Confirm grant names accurate
  → Review AI-generated text
  |
  v
OUTPUT: PDF + Email Brief
```

---

## 5. Phase 3: Scale

### 5.1 What's Needed for 10 Clients

| Requirement | Status | Action |
|-------------|--------|--------|
| Semi-automated reports | Missing | Build Phase 2 pipeline |
| <2 hours per report | Currently 40+ hours | Automation required |
| 70%+ QA pass rate | ~50% estimated | QA checklist + validation |
| Payment processing | Missing | Stripe integration |
| Client onboarding form | Exists (Google Form) | Connect to system |

### 5.2 What's Needed for 50 Clients

| Requirement | Status | Action |
|-------------|--------|--------|
| <30 min per report | Requires full automation | ML matching + AI generation |
| Client dashboard | Missing | Web portal for self-service |
| Automated alerts | Missing | Email scheduler |
| Team capacity | 1 person | May need contractor for QA |
| Current opportunities | 500+ | Ongoing scraping pipeline |

### 5.3 What's Needed for 100 Clients

| Requirement | Status | Action |
|-------------|--------|--------|
| <5 min per report | Requires production ML | Fully automated pipeline |
| Self-service portal | Missing | React/Next.js app |
| API integrations | Missing | CRM, email, payment |
| Monitoring/alerting | Missing | Error tracking, uptime |
| Data refresh pipeline | Manual | Automated IRS data updates |
| Team size | 1 person | 2-3 FTE or contractors |

### 5.4 Infrastructure Considerations

| Component | Current | 10 Clients | 100 Clients |
|-----------|---------|------------|-------------|
| Database | PostgreSQL on WSL2 | Same (adequate) | Cloud PostgreSQL |
| Web hosting | None | Vercel/Railway | Same |
| Email | Manual | Brevo API | Same (scales) |
| File storage | Local | S3/Cloudflare R2 | Same |
| Compute | Local | Railway containers | Railway + Workers |
| ML models | None | Local embeddings | Cloud inference |

---

## 6. Dependencies

### 6.1 What Blocks What

```
[Database Validation] → [Foundation Intelligence] → [Matching Algorithm Optimization]
                                                            |
                                                            v
[Website Form API] ← → [Client Onboarding] → [Report Generation]
                                                    |
                                                    v
                                           [QA Validation] → [Delivery]
                                                    ^
                                                    |
[Website Scraping] → [Current Opportunities] ───────┘
```

### 6.2 External Dependencies

| Dependency | Purpose | Status | Alternative |
|------------|---------|--------|-------------|
| IRS TEOS data | Foundation data source | Available (annual) | ProPublica API |
| ProPublica Nonprofit Explorer API | EIN enrichment | Available (free) | IRS BMF |
| Brevo API | Email delivery | Planned | SendGrid, Mailgun |
| Stripe | Payments | Not set up | PayPal, Square |
| Claude/OpenAI API | AI text generation | Available | Local LLMs |

### 6.3 Skill Dependencies

| Task | Required Skills | Available? |
|------|-----------------|------------|
| Database queries | SQL, PostgreSQL | Yes |
| Python scripts | Python 3.11+ | Yes |
| Web scraping | Python (requests, BeautifulSoup) | Yes |
| ML matching | Sentence-BERT, embeddings | Needs setup |
| Web frontend | Next.js, TypeScript | Partial |
| API development | FastAPI/Flask | Yes |
| PDF generation | Python (reportlab, weasyprint) | Yes |

---

## 7. Milestones

### Sprint 1: Database & Validation (Current)

- [ ] Fix Ka Ulukoa Bank of Hawaii deadline
- [ ] Run F990 data validation queries
- [ ] Create foundation_intelligence table
- [ ] Calculate openness scores for all foundations
- [ ] Calculate repeat funding rates

### Sprint 2: Matching & Reports

- [ ] Optimize matching algorithm with new scores
- [ ] Build report generation template
- [ ] Generate BG1 Round 2 reports
- [ ] Collect and process feedback
- [ ] Finalize report format

### Sprint 3: Website & Onboarding

- [ ] Connect website form API
- [ ] Fix mobile header issues
- [ ] Create example reports page
- [ ] Set up payment processing
- [ ] Test end-to-end onboarding flow

### Sprint 4: Automation Foundation

- [ ] Build website scraping infrastructure
- [ ] Expand current_opportunities to 100+
- [ ] Create opportunity validation pipeline
- [ ] Set up email automation (Brevo)
- [ ] Build QA checklist validation

### Sprint 5: First Paying Client

- [ ] Convert BG1/BG2 member or VetsBoats to paid
- [ ] Deliver first paid report
- [ ] Iterate based on feedback
- [ ] Document process for scaling

### Decision Points

| Decision | When | Options |
|----------|------|---------|
| Report format | After BG1 R2 feedback | Opportunity-focused vs Foundation-focused vs Hybrid |
| Pricing tier | After 3 paid clients | Single tier vs Multiple tiers |
| Vertical focus | After 10 clients | Horizontal vs Specific sectors |
| Team expansion | At 50 clients | Contractor vs FTE |

---

## 8. Source Files Reference

### Code Files

| File | Location | Purpose |
|------|----------|---------|
| `import_f990.py` | `1. Database/F990-2025/1. Import/` | IRS data import |
| `backfill_grant_purpose.py` | `1. Database/F990-2025/1. Import/` | Purpose text fix |
| `matching_algorithm.py` | Root | Matching logic |
| `schema.sql` | `1. Database/F990-2025/1. Import/` | Database schema |
| `parse_990pf.py` | `1. Database/F990-2025/1. Import/xml_parsers/` | 990-PF XML parsing |

### Spec Files

| File | Location | Purpose |
|------|----------|---------|
| `CLAUDE.md` | `.claude/` | Project context |
| `SCHEMA_SUMMARY.md` | `.claude/Team Enhancements/Enhancements 2025-12-05/` | Database documentation |
| `config.yaml` | `1. Database/F990-2025/1. Import/` | Import configuration |

### Summary Files

| File | Location | Purpose |
|------|----------|---------|
| `THEGRANTSCOUT_SUMMARY 2025-12-5.md` | Root | Current product summary |
| `folder_structure_2025-12-05.json` | Root | Full project structure |

### Beta Testing Files

| File | Location | Purpose |
|------|----------|---------|
| `Grant Alerts Questionnaire (1-6).csv` | `2. Beta Testing/` | Beta client intake data |
| Reports | `2. Beta Testing/1. Reports/` | Delivered reports |
| Feedback | `2. Beta Testing/2. Feedback/` | Client feedback |

---

## Appendix: 10-Signal Scoring Algorithm

| Signal | Points | Description | Data Source |
|--------|--------|-------------|-------------|
| Prior Relationship | 40 | Has foundation funded this nonprofit before? | pf_grants |
| Geographic Match | 15 | In-state funding preference | pf_grants.recipient_state |
| Grant Size Alignment | 12 | Typical grant size matches ask | foundation_intelligence |
| Repeat Funding Rate | 10 | Foundation favors existing grantees | foundation_intelligence |
| Portfolio Concentration | 8 | How focused on specific sectors | foundation_intelligence |
| Purpose Text Match | 5 | Semantic similarity to past purposes | ML embeddings |
| Recipient Validation | 4 | Foundation's grantee quality patterns | pf_grants analysis |
| Foundation Size | 3 | Capacity to fund at requested level | pf_returns.total_assets_eoy_amt |
| Regional Proximity | 2 | Cross-state giving corridors | pf_grants analysis |
| Grant Frequency | 1 | Active vs. sporadic grantmaker | pf_grants by year |

**Total Possible Score:** 100 points

---

*Document generated: 2025-12-08*
*Next review: After BG1 Round 2 feedback collection*
