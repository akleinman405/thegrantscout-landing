# SOP: Grant Report Generation

**Version:** 2.0
**Created:** 2026-01-06
**Updated:** 2026-01-06
**Purpose:** Standard procedure for generating high-quality grant opportunity reports

---

## Overview

This SOP covers generating grant opportunity reports for TheGrantScout clients. The process is designed to be manual-first with quality checkpoints, prioritizing report quality over speed.

**Philosophy:** Each report batch is a learning opportunity. We build infrastructure that supports the best possible reports by Claude Code CLI, then automate incrementally.

**Time estimate:** 2-4 hours per client (manual enrichment is the bottleneck)
**Output:** Client-ready report (markdown + docx)

---

## Table of Contents

1. [Phase 0: Pre-Flight Checks](#phase-0-pre-flight-checks)
2. [Phase 1: Client Understanding](#phase-1-client-understanding)
3. [Phase 2: Foundation Discovery](#phase-2-foundation-discovery)
4. [Phase 3: Enrichment & Research](#phase-3-enrichment--research)
5. [Phase 4: Report Assembly](#phase-4-report-assembly)
6. [Phase 5: Quality Checkpoints](#phase-5-quality-checkpoints)
7. [Handling Special Cases](#handling-special-cases)
8. [Troubleshooting](#troubleshooting)

---

## Phase 0: Pre-Flight Checks

Before starting ANY report generation:

### 0.1 Environment Verification

```bash
# Verify database connection
psql -h localhost -U postgres -d thegrantscout -c "SELECT COUNT(*) FROM f990_2025.dim_foundations;"

# Check pipeline scripts exist
ls "/Users/aleckleinman/Documents/TheGrantScout/4. Pipeline/scripts/"
```

### 0.2 Client Data Verification

- [ ] Client exists in `4. Pipeline/config/clients.json`
- [ ] Questionnaire data is available (6. Business/beta-testing/ or equivalent)
- [ ] EIN is correct and matches questionnaire
- [ ] No recent report exists (check `5. Runs/{client}/`)

---

## Phase 1: Client Understanding

**Goal:** Ensure complete understanding of client needs BEFORE running any algorithms.

### 1.1 Required Questions (Verify Before Starting)

| Question | Why It Matters | Where to Find |
|----------|----------------|---------------|
| What is their PRIMARY funding need right now? | Determines search strategy | Questionnaire, specific_ask_text |
| Do they have MULTIPLE priorities? | May need multiple search passes | Questionnaire, notes |
| What is their geographic scope? (City/County/State/National) | Algorithm is state-level; may need adjustment | Questionnaire, geographic_scope |
| What is their grant size target? | Filters foundations by typical grant size | Questionnaire |
| Who are their known/prior funders? | EXCLUDE from results | prior_funders array |
| What customer type are they? | Determines report format | See section 1.2 |

### 1.2 Identify Customer Type

**CRITICAL:** Different customer types need different outputs.

| Type | Signals | What They Want | Report Approach |
|------|---------|----------------|-----------------|
| **Calendar Managers** | "We already know most foundations"; experienced grant writer; values organization | Reminders, deadlines, nothing overlooked | Comprehensive list, emphasis on timeline |
| **Niche Seekers** | "Help us find new funders"; specific geography like Hawaii; looking outside usual sources | Discovery of unexpected matches | Prioritize novel foundations over obvious ones |
| **Relationship Builders** | "We prefer LOIs over formal apps"; interested in board connections; multi-mission org | Foundation profiles for prospecting | Fewer foundations (5), deeper research on each |

**Examples from beta:**
- **Calendar Manager:** Andy (RHF) - "Info organized in one place was valuable"
- **Niche Seeker:** Ka Ulukoa - Hawaii-specific foundations prioritized
- **Relationship Builder:** Consuelo (PSMF) - "Prefers ~5 foundations with relationship-building info"

### 1.3 Handle Multi-Priority Clients

**When client has 2+ distinct funding priorities:**

```
Example: FCSD
- Priority 1: Vocational training bakery (~$100K expansion)
- Priority 2: Future community center building (capital)
```

**Process:**
1. Document EACH priority separately in client profile
2. Run foundation discovery ONCE per priority
3. Merge results, ensuring coverage of BOTH priorities
4. Final report should address EACH priority explicitly

**Minimum coverage rule:** At least 2 foundations per priority in final Top 5.

### 1.4 Handle Geographic Specificity

| Client Says | Algorithm Does | Gap | Claude Action |
|-------------|----------------|-----|---------------|
| "San Diego" | Matches CA state | City not matched | Add manual filter for SD-area foundations |
| "National" | Matches HQ state (CT) | Only gets CT | Add curated national foundations manually |
| "Hawaii" | Matches HI state | OK | Standard process works |
| "DeKalb County, GA" | Matches GA state | County not matched | Review top 100 for Atlanta-area specifically |

### 1.5 Output: Client Brief

Before proceeding, create a client brief (can be mental or documented):

```
CLIENT BRIEF: [Organization Name]
- Customer Type: [Calendar Manager / Niche Seeker / Relationship Builder]
- Primary Priority: [What they want funding for]
- Secondary Priority: [If applicable]
- Geographic Scope: [City/State/National] - Algorithm adjustment needed? [Y/N]
- Target Grant Size: [$X - $Y]
- Known Funders to Exclude: [List]
- Report Format: [Opportunity-focused / Foundation-focused]
```

---

## Phase 2: Foundation Discovery

**Goal:** Identify the best-fit foundations using algorithmic scoring AND manual curation.

### 2.1 Decision: Algorithm vs. Manual Research

| Situation | Approach |
|-----------|----------|
| Standard client (state-level geography, common sector) | Use algorithm (Script 02) |
| Niche geography (city-specific, Hawaii, etc.) | Algorithm + manual curation |
| National scope | Algorithm flags HQ state; manually add national foundations |
| Unusual sector (patient safety, maritime, etc.) | Algorithm + keyword search in grant purposes |
| Capital project | Algorithm + filter for capital funders |
| Multi-priority | Run algorithm TWICE with different parameters |

### 2.2 Algorithmic Scoring (Standard Path)

**Script:** `02_score_foundations_v6.1.py`

```bash
cd "/Users/aleckleinman/Documents/TheGrantScout/4. Pipeline"
python3 scripts/02_score_foundations_v6.1.py --client "{client_name}" --output "runs/{client}/{date}/02_scored_foundations.csv"
```

**Output:** Top 100 foundations ranked by LASSO V6.1 model

### 2.3 Quality Check: Algorithm Output

**STOP and review the top 20 before proceeding:**

| Check | Pass | Fail |
|-------|------|------|
| At least 5 foundations in client's state? | Continue | Add curated foundations |
| Grant sizes appropriate for client? | Continue | Adjust target_grant_size |
| Sectors represented match client? | Continue | Check client profile |
| Any prior funders in list? | Remove them | |
| For capital clients: Any capital funders? | Continue | Add curated capital funders |

### 2.4 Curated Foundations (Manual Research Path)

**When to use:** Algorithm output doesn't match client needs.

**Process:**
1. Research foundations manually using:
   - Candid/GuideStar sector searches
   - Foundation Directory by geography
   - Known capital/program funders in sector
   - Board overlap analysis
2. Document each curated foundation with EIN
3. Generate snapshots for curated foundations

**Curated Foundation Research Sources:**
- Candid Foundation Directory
- Council on Foundations member list
- State association of grantmakers
- Similar organizations' 990s (who funded them?)

### 2.5 Merge Scored + Curated

**Final foundation list should include:**
- Top 10-15 from algorithm
- 5-10 curated foundations (if needed)
- Total: ~20-30 foundations for grant purpose filtering

### 2.6 Sibling Nonprofit Methodology (V3.0 - Added 2026-01-13)

**CRITICAL:** Before deep enrichment, find foundations that have funded organizations SIMILAR to the client.

**Why this matters:**
- "They funded orgs like you" is stronger evidence than "they fund your sector"
- Semantic embeddings catch synonyms that keyword search misses
- Combines mission similarity + budget compatibility

**Sibling Definition:**
A nonprofit S is a "sibling" of client C if:
1. `cosine_similarity(S.mission_embedding, C.mission_embedding) >= 0.50`
2. `S.budget BETWEEN C.budget × 0.2 AND C.budget × 5.0`

**Process:**

**Step 1: Generate client embedding**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
client_embedding = model.encode(client_mission_text)
```

**Step 2: Find sibling nonprofits**
```sql
-- Find nonprofits similar to client by mission + budget
SELECT
    ein,
    name,
    total_revenue as budget,
    1 - (mission_embedding <=> %(client_embedding)s) as similarity
FROM f990_2025.emb_nonprofit_missions em
JOIN f990_2025.nonprofit_returns nr ON em.ein = nr.ein
WHERE nr.total_revenue BETWEEN %(budget_min)s AND %(budget_max)s
  AND 1 - (mission_embedding <=> %(client_embedding)s) >= 0.50
ORDER BY similarity DESC;
```

**Step 3: Find foundations that funded siblings**
```sql
SELECT
    fg.foundation_ein,
    df.name as foundation_name,
    COUNT(DISTINCT fg.recipient_ein) as siblings_funded,
    COUNT(*) as total_grants_to_siblings,
    SUM(fg.amount) as total_amount,
    MAX(fg.tax_year) as most_recent_year
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_foundations df ON fg.foundation_ein = df.ein
WHERE fg.recipient_ein IN (SELECT ein FROM sibling_nonprofits)
GROUP BY fg.foundation_ein, df.name
HAVING COUNT(DISTINCT fg.recipient_ein) >= 2
ORDER BY siblings_funded DESC, total_amount DESC;
```

**Step 4: Combine with keyword matching**
Also check grant PURPOSE keywords for foundations that may have funded similar WORK but not the exact siblings.

**Output:** Ranked list of foundations with:
- Number of siblings funded
- Total grants to siblings
- Grant purpose keyword matches
- LASSO score (for validation)

### 2.7 Grant Purpose Filter (Complementary)

**Use alongside sibling methodology:**

```sql
SELECT COUNT(*) as matching_grants
FROM f990_2025.fact_grants
WHERE foundation_ein = '[EIN]'
AND purpose_text ILIKE ANY(array['%keyword1%', '%keyword2%', ...]);
```

Categorize:
- **VALIDATED:** 3+ matching grants
- **PARTIAL:** 1-2 matching grants
- **UNVALIDATED:** 0 matching grants

**Note:** Sibling methodology is PRIMARY; keyword matching is COMPLEMENTARY.

---

## Phase 3: Quick Eligibility Filtering

**Goal:** Quickly filter foundations by eligibility criteria BEFORE deep enrichment.

**Philosophy (Updated 2026-01-13):** Filter first, then research. Don't waste time on deep research for foundations that will be filtered out.

### 3.1 What to Check (Quick Research - 5-10 min per foundation)

For top 15-20 foundations from Phase 2, check ONLY:

| Check | Source | Action if Fail |
|-------|--------|----------------|
| `accepts_unsolicited` | Foundation website | SKIP (unless excellent fit → WATCH) |
| `eligibility_fit` | Foundation guidelines | SKIP if client doesn't qualify |
| `geographic_focus` | Foundation website | SKIP if client area excluded |
| `program_priorities` | Foundation website | SKIP if sector mismatch |

**DO NOT research yet:** contact info, deadline details, application requirements, comparable grant details.

### 3.2 Eligibility Tiers (Updated)

| Tier | Foundations | Research Depth |
|------|-------------|----------------|
| **Tier 1** | Top 15 by score with grant match | Quick eligibility check only |
| **Tier 2** | Ranks 16-25 or partial grant match | Only if Tier 1 yields <8 viable |
| **Tier 3** | Unvalidated grant match | Last resort |

### 3.2 Essential vs. Nice-to-Have Enrichment

**Essential (MUST have for every foundation in final report):**

| Field | Why Essential | Source |
|-------|---------------|--------|
| `accepts_unsolicited` | Determines if actionable | Website guidelines |
| `application_type` | Determines approach (LOI, RFP, etc.) | Website |
| `geographic_focus` | Confirms client is eligible | Website, 990 analysis |
| `program_priorities` | Confirms mission alignment | Website "What We Fund" |
| `eligibility_fit` | Confirms client qualifies | Website guidelines (see 3.2.1) |

#### 3.2.1 Eligibility Criteria (NEW - Added 2026-01-13)

**CRITICAL:** Before including a foundation in the report, verify the client meets ALL stated eligibility requirements. If client doesn't meet requirements → **SKIP** (not CONDITIONAL).

| Criteria | What to Look For | Where to Find | Example Disqualifier |
|----------|------------------|---------------|---------------------|
| `budget_requirement` | Min/max recipient budget | Guidelines, eligibility page | "Orgs must have budget >$1M" |
| `org_age_requirement` | Years in operation | Guidelines | "Must be operating 3+ years" |
| `org_type_requirement` | 501(c)(3), public charity, etc. | Guidelines | "Private foundations not eligible" |
| `grant_size_range` | Typical/max grant amount | Guidelines, 990 analysis | Too small to be meaningful for client |
| `geographic_restrictions` | Specific city/county/region | Guidelines | "San Diego County only" |
| `project_type_restrictions` | Capital, program, general operating | Guidelines | "No capital grants" |
| `other_restrictions` | New grantees only, no repeat, etc. | Guidelines | "Previous grantees not eligible" |

**Eligibility Check Process:**
1. Read foundation's eligibility/guidelines page completely
2. Compare EACH stated requirement against client profile
3. Document any requirement that client does NOT meet
4. If ANY requirement not met → SKIP (unless requirement is ambiguous → CONDITIONAL)

**Nice-to-Have (include if time permits):**

| Field | Value | Source |
|-------|-------|--------|
| `contact_name` | Personalization | Staff page |
| `contact_email` | Direct outreach | Staff page |
| `current_deadline` | Action planning | RFP page |
| `grant_range_stated` | Request sizing | Guidelines |
| `application_requirements` | Prep planning | Guidelines |

### 3.3 Enrichment Process

**Use SKILL_foundation_scraper.md for each foundation:**

1. **Find website:**
   - Search: `"{foundation_name}" foundation grants`
   - Verify EIN matches
   - Document URL

2. **Navigate to grants page:**
   - Look for: "Grants", "What We Fund", "How to Apply", "For Grantseekers"

3. **Extract required fields:**
   - Does it accept unsolicited proposals?
   - What is the application type?
   - What are program priorities?
   - What is geographic focus?

4. **Identify red flags:**
   - `no_unsolicited`: States "do not accept unsolicited proposals"
   - `invite_only_strict`: "Grants by invitation only"
   - `geographic_mismatch`: Excludes client's area
   - `sector_mismatch`: Doesn't fund client's work
   - `possibly_dormant`: No recent grants (3+ years)

### 3.4 Track Enrichment (For Future Runs)

**Store enrichment data in database:**

```bash
python3 scripts/03b_store_enrichment.py --file enrichment_batch.json
```

**Track what was researched:**
- Keep log of which foundations were researched
- Note date of research
- Flag for refresh if >90 days old

### 3.5 Viability Assessment

After enrichment, categorize each foundation:

| Tier | Criteria | Action |
|------|----------|--------|
| **READY** | accepts_unsolicited=true, no red flags, deadline >30 days | Include in report |
| **CONDITIONAL** | accepts_unsolicited unclear, or minor concerns | Include with caveats |
| **WATCH** | invite_only but good fit | Include for relationship building |
| **SKIP** | Red flags, geographic mismatch, dormant | Exclude |

**Minimum viable count:** 5 READY or CONDITIONAL foundations

If <5 viable: Expand to Tier 2/3 foundations or add curated.

---

## Phase 4: Select Final 5 + Deep Enrichment

**Goal:** Select final foundations and gather detailed info for report.

**Philosophy (Updated 2026-01-13):** Only do deep research on foundations that will actually appear in the report.

### 4.1 Select Final 5

From viable foundations (Phase 3 output), select top 5 based on:

1. **Grant purpose validation:** VALIDATED > PARTIAL > UNVALIDATED
2. **Viability tier:** READY > CONDITIONAL > WATCH
3. **Alignment score:** From algorithm or manual assessment
4. **Priority coverage:** For multi-priority clients, ensure both covered
5. **Diversity:** Mix of grant sizes, application types

### 4.2 Deep Enrichment (NEW - Only for Final 5)

**Now** research the following for ONLY the final 5 foundations:

| Field | Source | Purpose |
|-------|--------|---------|
| `contact_name` | Staff page | Personalization |
| `contact_email` | Staff page | Direct outreach |
| `current_deadline` | RFP/Guidelines | Action planning |
| `application_requirements` | Guidelines | Prep planning |
| `grant_range_stated` | Guidelines | Request sizing |
| `application_url` | Website | Link in report |

### 4.3 Select Comparable Grants (for Final 5)

For each foundation, use `matching_grant_keywords` to find 2-3 relevant grants:

```sql
SELECT recipient_name, amount, tax_year, purpose_text
FROM f990_2025.fact_grants
WHERE foundation_ein = '[EIN]'
AND purpose_text ILIKE ANY(array['%keyword1%', '%keyword2%', ...])
ORDER BY tax_year DESC, amount DESC
LIMIT 5;
```

**Select grants that:**
- Are from last 3 years
- Match client's sector/work type
- Have meaningful amounts for client's budget

### 4.4 Generate Narratives

**For each foundation, create:**

| Section | Content | Length |
|---------|---------|--------|
| Why This Fits | Specific alignment points between foundation and client | 2-3 sentences |
| Comparable Grant | Similar org they funded, with amount and purpose | 1 sentence |
| Positioning Strategy | How to approach (general support vs. program, grant size to request) | 2-3 sentences |
| Next Steps | Specific actions with deadlines | 3-5 bullets |

### 4.5 Run Report Scripts

```bash
cd "/Users/aleckleinman/Documents/TheGrantScout/4. Pipeline"

# Assemble opportunities
python3 scripts/05_assemble_opportunities.py --client "{client}"

# Generate narratives
python3 scripts/06_generate_narratives.py --client "{client}"

# Build report data
python3 scripts/07_build_report_data.py --client "{client}"

# Render markdown
python3 scripts/08_render_report.py --client "{client}"

# Convert to Word
python3 scripts/09_convert_to_docx.py --client "{client}"
```

### 4.4 Report Format by Customer Type

| Type | Report Emphasis | Foundations Count |
|------|-----------------|-------------------|
| Calendar Manager | Timeline, deadlines, comprehensive | 5-7 |
| Niche Seeker | Discovery, novel matches, fit explanation | 5 |
| Relationship Builder | Deep profiles, connection paths, LOI strategy | 3-5 |

---

## Phase 5: Quality Checkpoints

### 5.1 Pre-Delivery Checklist

**MANDATORY - Check every item:**

**Client Alignment:**
- [ ] Report addresses client's PRIMARY funding priority
- [ ] Report addresses client's SECONDARY priority (if applicable)
- [ ] Geographic scope matches client need (not just HQ state)
- [ ] Grant sizes are appropriate for client budget
- [ ] No prior funders included in report

**Foundation Quality:**
- [ ] All 5 foundations have given grants in past 3 years
- [ ] All foundations' geographic focus includes client's area
- [ ] All foundations' program priorities align with client mission
- [ ] No expired deadlines included
- [ ] All links verified working

**Report Quality:**
- [ ] Comparable grants are relevant (not just any grant)
- [ ] "Why This Fits" is specific to THIS client (not generic)
- [ ] Positioning strategies are actionable
- [ ] Dollar amounts formatted consistently
- [ ] No spelling/grammar errors

### 5.2 Alignment Score

**Rate alignment on 1-10 scale:**

| Score | Meaning | Action |
|-------|---------|--------|
| 9-10 | Excellent match | Proceed to delivery |
| 7-8 | Good match with minor gaps | Document gaps, proceed |
| 5-6 | Partial match | **FLAG FOR HUMAN REVIEW** |
| <5 | Poor match | **DO NOT DELIVER** - rework |

**Alignment Criteria:**
- Primary priority addressed? (+3 points)
- Secondary priority addressed? (+2 points)
- Geographic scope correct? (+2 points)
- Customer type format used? (+1 point)
- At least 3 novel discoveries? (+2 points)

**Minimum acceptable score: 7/10**

### 5.3 Flag for Human Review

**Automatically flag if:**
- Alignment score <7
- <5 viable foundations found
- Client has unusual requirements not in standard process
- Algorithm output didn't match client needs (had to use >50% curated)
- Any foundation has red flags that were included anyway

**Review format:**
```
FLAG FOR REVIEW: [Client Name]
- Issue: [What went wrong]
- Current state: [What report looks like now]
- Recommended action: [What should happen]
- Human decision needed: [Specific question]
```

### 5.4 Post-Delivery Tracking

After report sent:
- [ ] Log delivery date
- [ ] Note any client feedback
- [ ] Update client profile if new information learned
- [ ] Add to lessons learned if process issues found

---

## Handling Special Cases

### Case: National Organization (Like HN)

**Problem:** Algorithm matches HQ state (CT) but client wants national funders.

**Solution:**
1. Run algorithm normally (will get CT foundations)
2. Add curated national foundations:
   - Search for "national youth education foundations"
   - Check major national funders (Lilly, Kresge, Ford)
   - Look at similar national orgs' 990s
3. Final mix: 2-3 local (CT), 2-3 national

### Case: Multi-Priority Client (Like FCSD)

**Problem:** Two distinct needs (bakery + building) but report only addresses one.

**Solution:**
1. Run algorithm with Priority 1 keywords
2. Run algorithm with Priority 2 keywords (or search manually for capital funders)
3. Merge results
4. Final report: At least 2 foundations per priority
5. Label each foundation's relevance: "Best for: Bakery" or "Best for: Building"

### Case: Niche Geography (Like Hawaii)

**Problem:** Limited foundations in state; algorithm may not find enough.

**Solution:**
1. Run algorithm (will get Hawaii foundations)
2. If <10 viable, add:
   - Pacific region foundations
   - National foundations interested in Hawaii
   - Foundations that have funded Hawaii orgs before
3. Final report should have Hawaii foundations first

### Case: Niche Sector (Like Patient Safety)

**Problem:** Generic health funders appear instead of patient-safety-specific.

**Solution:**
1. Run algorithm normally
2. Search grant purposes for keywords:
   ```sql
   SELECT DISTINCT foundation_ein
   FROM f990_2025.fact_grants
   WHERE purpose_text ILIKE '%patient safety%'
      OR purpose_text ILIKE '%medical error%'
      OR purpose_text ILIKE '%healthcare quality%';
   ```
3. Add foundations that have funded similar work
4. Final report should lead with sector-specific foundations

### Case: Capital Project

**Problem:** Most foundations fund programs, not buildings.

**Solution:**
1. Check `grant_type_keywords` for "capital", "building", "facility"
2. Search grant purposes:
   ```sql
   SELECT DISTINCT foundation_ein
   FROM f990_2025.fact_grants
   WHERE purpose_text ILIKE '%capital%'
      OR purpose_text ILIKE '%building%'
      OR purpose_text ILIKE '%construction%'
      OR purpose_text ILIKE '%facility%';
   ```
3. Research known capital funders (Kresge, local community foundations)
4. Flag foundations that explicitly exclude capital

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| <5 viable foundations | Narrow niche or strict viability | Expand to top 50, add curated |
| Poor algorithm matches | Client profile incomplete | Review specific_ask_text, grant_type_keywords |
| Stale enrichment | Cache >90 days | Re-research foundations |
| Missing contacts | Foundation website sparse | Note in report, suggest LinkedIn research |
| All foundations in wrong state | Geographic scope mismatch | Add curated foundations for correct area |
| Client already knows all 5 | No discovery value | Expand search, find newer/smaller foundations |

---

## Output Locations

All outputs saved to: `5. Runs/{client_name}/YYYY-MM-DD/`

| File | Description |
|------|-------------|
| 01_client.json | Client profile |
| 02_scored_foundations.csv | Algorithm output |
| 03_snapshots.json | Foundation profiles |
| 04_viable_foundations.json | Post-enrichment viability |
| 05_opportunities.json | Assembled opportunities |
| 06_narratives.json | Generated narratives |
| 07_report_data.json | Structured report data |
| 08_report.md | Markdown report |
| 08_report.docx | Word document |

---

## Appendix: What Goes Where

### CLAUDE.md (Reference During All Sessions)

**Include:**
- Quick reference tables (foundation count, model version)
- Database connection info
- Key paths
- Gotchas and common errors
- Model coefficients summary
- Mandatory workflow reminders

**Don't include:**
- Detailed step-by-step processes
- Special case handling
- Troubleshooting guides

### SOP (Reference During Report Generation)

**Include:**
- Complete step-by-step workflow
- Quality checkpoints with criteria
- Special case handling
- Troubleshooting
- Decision trees

**Don't include:**
- Code snippets for scripts
- Database schema details
- Client-specific information

### Per-Run Instructions (Provided by User or in PROMPT File)

**Include:**
- Client name and specific ask
- Any special requirements for this run
- Deadlines for delivery
- Specific foundations to include/exclude
- Format preferences

**Example per-run instruction:**
```
Generate January 2026 report for FCSD.
- Address BOTH priorities (bakery + building)
- Include at least 2 capital funders
- Report due January 8
- Client prefers relationship-builder format
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-01-06 | Complete rewrite: Added customer types, multi-priority handling, geographic specificity, quality checkpoints with alignment scoring, special case handling |
| 1.0 | 2026-01-02 | Initial version |

---

*SOP Version 2.0 - Created 2026-01-06*
*Philosophy: High-quality manual reports now, automate incrementally*
