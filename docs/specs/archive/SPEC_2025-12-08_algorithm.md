# ALGORITHM_SPEC.md - Grant Matching Algorithm Specification

**Document Type:** SPEC
**Purpose:** Comprehensive specification for TheGrantScout matching algorithm
**Version:** 1.0
**Date:** 2025-12-08
**Status:** PRODUCTION-READY

---

## 1. Executive Summary

TheGrantScout's matching algorithm identifies foundations most likely to fund a given nonprofit by analyzing 1.6+ million historical grants from 85,470 foundations. The algorithm combines 10 weighted signals validated through statistical analysis of actual funding patterns.

**Key insight:** Prior relationships and geographic proximity are the strongest predictors of funding success, outweighing sector alignment in importance. This was a surprising discovery that fundamentally shaped the algorithm design.

**Core methodology:** Score foundations on 10 evidence-based signals, filter by openness to new grantees, and rank by likelihood of funding success.

---

## 2. Research Process

### 2.1 How We Arrived at 10 Signals

The signal ranking emerged from Phase 0 research (November 2025) analyzing:

- **1,621,833 historical grants** from IRS Form 990-PF filings
- **66,732 active foundations** (out of 85,470 total in database)
- **$65.1 billion** in total funding (2024 snapshot)
- **8 years of data** (2016-2024)

### 2.2 Sources Reviewed

| Source | Content | Contribution |
|--------|---------|--------------|
| IRS Form 990-PF | Foundation financials, grant lists | Primary data source |
| f990_grants table | 1.6M+ grant records | Pattern analysis |
| Foundation websites | Application info, guidelines | Openness scoring |
| Academic literature | Philanthropic behavior research | Signal hypotheses |
| Beta tester feedback | Real-world validation | Algorithm refinement |

### 2.3 Hypotheses Tested

| Hypothesis | Result | Finding |
|------------|--------|---------|
| Sector alignment is most important | **REJECTED** | Geographic match is 2x more predictive |
| Prior relationship predicts funding | **CONFIRMED** | 7.2x higher likelihood if previously funded |
| Large foundations prefer large grantees | **PARTIALLY CONFIRMED** | Weak correlation (r = 0.32) |
| Grant purpose text enables NLP matching | **LIMITED** | 91.9% of purposes <50 chars |
| Foundations prefer proven organizations | **CONFIRMED** | Funder diversity correlates with funding success |

### 2.4 Iterations and Pivots

**Original algorithm (pre-research):**
- Sector alignment: 30%
- Geographic match: 25%
- Grant size fit: 20%
- Other signals: 25%

**Final algorithm (post-research):**
- Prior relationship: 40%
- Geographic match: 15%
- Grant size alignment: 12%
- Repeat funding rate: 10%
- Other signals: 23%

**Key pivot:** Prior relationship was discovered to be 7.2x predictive (r = 0.72), completely reordering signal priorities.

---

## 3. Signal Definitions

### Signal 1: Prior Relationship Exists

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Prior Relationship |
| **Weight** | 40 points |
| **Data Source** | f990_2025.pf_grants table |
| **Correlation** | r = 0.72 (p < 0.001) |

**Calculation Logic:**
```python
def calculate_prior_relationship(foundation_ein, nonprofit_ein, nonprofit_names):
    """
    Check if foundation has funded this nonprofit before.
    Returns: 100 (funded before) or 0 (no prior relationship)
    """
    # Check EIN match
    if nonprofit_ein:
        ein_match = query("""
            SELECT COUNT(*) FROM f990_2025.pf_grants
            WHERE filer_ein = %s AND recipient_ein = %s
        """, [foundation_ein, nonprofit_ein])
        if ein_match > 0:
            return 100

    # Check fuzzy name match (95%+ similarity)
    for name in nonprofit_names:
        name_match = query("""
            SELECT COUNT(*) FROM f990_2025.pf_grants
            WHERE filer_ein = %s
            AND similarity(recipient_name, %s) > 0.95
        """, [foundation_ein, name])
        if name_match > 0:
            return 100

    return 0
```

**Why It Matters:** Foundations are 7.2x more likely to fund organizations they've funded before. This is the single strongest predictor in the dataset and reflects the risk-averse nature of philanthropic giving.

---

### Signal 2: Geographic Match (In-State)

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Geographic Match |
| **Weight** | 15 points |
| **Data Source** | pf_returns.state, nonprofit profile |
| **Correlation** | r = 0.58 (p < 0.001) |

**Calculation Logic:**
```python
def calculate_geographic_score(foundation_state, foundation_profile, nonprofit_state):
    """
    Score geographic alignment between foundation and nonprofit.
    Returns: 0-100 score
    """
    if nonprofit_state == foundation_state:
        return 100  # Same state - highest match

    if nonprofit_state in foundation_profile['top_states'][:5]:
        return 75   # In foundation's top 5 funded states

    if is_adjacent_state(nonprofit_state, foundation_state):
        return 50   # Border state spillover

    if same_region(nonprofit_state, foundation_state):
        return 25   # Same census region

    return 0  # No geographic connection
```

**Foundation Geographic Focus Distribution:**
- Hyper-Local (90%+ in-state): 22.9% of foundations
- State-Focused (70-90% in-state): 20.9%
- Regional (50-70% in-state): 18.1%
- Mixed (30-50% in-state): 11.9%
- National (<30% in-state): 26.2%

**Why It Matters:** 70%+ of foundations give primarily in-state. Even with perfect mission alignment, being out-of-state reduces funding probability by 60%.

---

### Signal 3: Grant Size Alignment

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Grant Size Alignment |
| **Weight** | 12 points |
| **Data Source** | pf_grants aggregate statistics |
| **Correlation** | r = 0.51 (p < 0.001) |

**Calculation Logic:**
```python
def calculate_grant_size_fit(foundation_profile, nonprofit_request_amount):
    """
    Score how well the nonprofit's ask fits the foundation's typical range.
    Returns: 0-100 score
    """
    median = foundation_profile['median_grant']
    q25 = foundation_profile['grant_25th_percentile']
    q75 = foundation_profile['grant_75th_percentile']

    # Perfect fit: within IQR
    if q25 <= nonprofit_request_amount <= q75:
        return 100

    # Good fit: within 2x of median
    if median * 0.5 <= nonprofit_request_amount <= median * 2:
        return 75

    # Acceptable: within 3x of median
    if median * 0.33 <= nonprofit_request_amount <= median * 3:
        return 50

    # Poor fit
    if nonprofit_request_amount < median * 0.1:
        return 25  # Ask too small
    if nonprofit_request_amount > median * 5:
        return 10  # Ask too large

    return 25
```

**Grant Size Distribution (Overall):**
- Median: $2,000
- Mean: $40,157
- 75th percentile: $10,000
- 95th percentile: $100,000

**Why It Matters:** Asking for $1M from a foundation that typically gives $5K wastes everyone's time. Grant size alignment prevents mismatched asks.

---

### Signal 4: Repeat Funding Rate

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Repeat Funding Rate |
| **Weight** | 10 points |
| **Data Source** | Calculated from pf_grants history |
| **Correlation** | r = 0.48 (p < 0.001) |

**Calculation Logic:**
```python
def calculate_repeat_potential(foundation_profile, nonprofit):
    """
    Score based on foundation's tendency to re-fund and nonprofit's track record.
    Returns: 0-100 score
    """
    repeat_rate = foundation_profile['repeat_funding_rate']  # 0-100%

    # Foundation's relationship style
    if repeat_rate > 60:
        style_multiplier = 1.0  # "Deep Partnerships"
    elif repeat_rate > 30:
        style_multiplier = 0.75  # "Mixed Repeat"
    elif repeat_rate > 10:
        style_multiplier = 0.5   # "Mostly New"
    else:
        style_multiplier = 0.25  # "Always New"

    # Nonprofit's existing funder count as validation
    funder_validation = min(nonprofit['existing_funder_count'] / 5.0, 1.0)

    return repeat_rate * style_multiplier * funder_validation
```

**Relationship Style Distribution:**
- Deep Partnerships (60%+ repeat): 3.0% of foundations
- Mixed Repeat (30-60%): 6.2%
- Mostly New (10-30%): 12.7%
- Always New (<10%): 78.0%

**Why It Matters:** Foundations with high repeat rates are looking for long-term partnerships. Knowing this helps position applications appropriately.

---

### Signal 5: Portfolio Concentration Match

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Portfolio Concentration |
| **Weight** | 8 points |
| **Data Source** | Foundation giving patterns |
| **Correlation** | r = 0.42 (p < 0.001) |

**Calculation Logic:**
```python
def calculate_portfolio_match(foundation_profile, nonprofit):
    """
    Score based on how focused the foundation is and whether nonprofit fits.
    Returns: 0-100 score
    """
    concentration = foundation_profile['concentration_level']

    if concentration == 'Highly Concentrated':
        # Must match existing archetypes closely
        archetype_similarity = calculate_archetype_similarity(
            nonprofit,
            foundation_profile['top_recipient_archetypes']
        )
        return archetype_similarity

    elif concentration == 'Moderately Concentrated':
        # Some flexibility
        archetype_similarity = calculate_archetype_similarity(
            nonprofit,
            foundation_profile['top_recipient_archetypes']
        )
        return max(archetype_similarity, 50)

    else:  # Diversified or Highly Diversified
        # Open to many types
        return 70
```

**Concentration Distribution:**
- Highly Concentrated (≤10 recipients): 35.8%
- Moderately Concentrated (11-50): 54.0%
- Diversified (51-200): 9.4%
- Highly Diversified (>200): 0.8%

**Why It Matters:** Highly concentrated foundations likely have pre-existing relationships. Don't waste time applying to these unless you match their archetype.

---

### Signal 6: Purpose Text Match

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Purpose Text Match |
| **Weight** | 5 points |
| **Data Source** | pf_grants.purpose field |
| **Correlation** | r = 0.38 (p < 0.01) |

**Calculation Logic:**
```python
def calculate_purpose_match(foundation_profile, nonprofit_mission_keywords):
    """
    Score keyword overlap between nonprofit mission and foundation's grant purposes.
    Returns: 0-100 score
    """
    if len(foundation_profile['common_keywords']) == 0:
        return 50  # Neutral if no data

    # Jaccard similarity of keyword sets
    foundation_keywords = set(foundation_profile['common_keywords'][:50])
    nonprofit_keywords = set(nonprofit_mission_keywords)

    overlap = foundation_keywords.intersection(nonprofit_keywords)
    union = foundation_keywords.union(nonprofit_keywords)

    jaccard = len(overlap) / len(union) if union else 0

    return jaccard * 100
```

**Top Keywords in Grant Purposes:**
1. "general support" (TF-IDF: 0.2144)
2. "general" (0.2089)
3. "charitable" (0.0549)
4. "unrestricted" (0.0380)
5. "scholarship" (0.0345)

**Limitation:** 91.9% of grant purposes are <50 characters, severely limiting NLP capabilities.

**Why It Matters:** While limited by data quality, keyword overlap can identify mission alignment when detailed purposes exist.

---

### Signal 7: Recipient Validation (Funder Diversity)

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Recipient Validation |
| **Weight** | 4 points |
| **Data Source** | Count of unique funders for nonprofit |
| **Correlation** | r = 0.35 (p < 0.01) |

**Calculation Logic:**
```python
def calculate_recipient_validation(nonprofit):
    """
    Score based on how many other foundations support this nonprofit.
    Returns: 0-100 score
    """
    funder_count = nonprofit['existing_funder_count']

    # More funders = more validation
    # Cap at 20 funders for max score
    validation_score = min(funder_count / 20.0, 1.0) * 100

    return validation_score
```

**Why It Matters:** Organizations funded by multiple foundations are validated as worthy recipients. This is a "social proof" signal.

---

### Signal 8: Foundation Size Alignment

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Foundation Size Alignment |
| **Weight** | 3 points |
| **Data Source** | pf_returns.total_assets_eoy_amt |
| **Correlation** | r = 0.32 (p < 0.01) |

**Calculation Logic:**
```python
def calculate_size_alignment(foundation_size_category, nonprofit_budget):
    """
    Score alignment between foundation size and nonprofit scale.
    Returns: 0-100 score
    """
    size_preferences = {
        'Mega': {'preferred_budget_min': 1_000_000, 'preferred_budget_max': None},
        'Large': {'preferred_budget_min': 500_000, 'preferred_budget_max': 50_000_000},
        'Medium': {'preferred_budget_min': 100_000, 'preferred_budget_max': 10_000_000},
        'Small': {'preferred_budget_min': 0, 'preferred_budget_max': 5_000_000},
        'Micro': {'preferred_budget_min': 0, 'preferred_budget_max': 1_000_000}
    }

    prefs = size_preferences.get(foundation_size_category, size_preferences['Medium'])

    if prefs['preferred_budget_min'] <= nonprofit_budget:
        if prefs['preferred_budget_max'] is None or nonprofit_budget <= prefs['preferred_budget_max']:
            return 100

    # Outside preferred range but not impossible
    return 50
```

**Why It Matters:** While correlation is weaker than expected, mega foundations have capacity for large grants that small foundations cannot match.

---

### Signal 9: Regional Proximity

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Regional Proximity |
| **Weight** | 2 points |
| **Data Source** | State clustering analysis |
| **Correlation** | r = 0.28 (p < 0.05) |

**Calculation Logic:**
```python
def calculate_regional_proximity(foundation_state, nonprofit_state):
    """
    Score cross-state giving within regional corridors.
    Returns: 0-100 score
    """
    REGIONAL_CLUSTERS = {
        'Northeast': ['CT', 'ME', 'MA', 'NH', 'RI', 'VT', 'NJ', 'NY', 'PA'],
        'Southeast': ['AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'SC', 'TN', 'VA', 'WV'],
        'Midwest': ['IL', 'IN', 'MI', 'OH', 'WI', 'IA', 'KS', 'MN', 'MO', 'NE', 'ND', 'SD'],
        'Southwest': ['AZ', 'NM', 'OK', 'TX'],
        'West': ['AK', 'CA', 'CO', 'HI', 'ID', 'MT', 'NV', 'OR', 'UT', 'WA', 'WY']
    }

    # Find regions
    foundation_region = None
    nonprofit_region = None

    for region, states in REGIONAL_CLUSTERS.items():
        if foundation_state in states:
            foundation_region = region
        if nonprofit_state in states:
            nonprofit_region = region

    if foundation_region and foundation_region == nonprofit_region:
        return 75  # Same region

    return 0
```

**Why It Matters:** Some foundations fund regionally even when not in-state. This captures "corridor effects" like Northeast foundations funding New England broadly.

---

### Signal 10: Grant Frequency

| Attribute | Value |
|-----------|-------|
| **Signal Name** | Grant Frequency |
| **Weight** | 1 point |
| **Data Source** | pf_grants count per year |
| **Correlation** | r = 0.25 (p < 0.05) |

**Calculation Logic:**
```python
def calculate_grant_frequency(foundation_profile):
    """
    Score based on how actively the foundation makes grants.
    Returns: 0-100 score
    """
    grants_per_year = foundation_profile['grants_per_year']

    if grants_per_year >= 100:
        return 100  # Very active
    elif grants_per_year >= 50:
        return 80   # Active
    elif grants_per_year >= 20:
        return 60   # Moderate
    elif grants_per_year >= 5:
        return 40   # Occasional
    else:
        return 20   # Sporadic
```

**Why It Matters:** Active grantmakers have more "slots" available. Sporadic grantmakers may have long-established relationships that don't change.

---

## 4. Scoring Mechanics

### 4.1 How Signals Combine into Final Score

```python
def calculate_match_score(foundation_profile, nonprofit):
    """
    Calculate final match score combining all 10 signals.
    Returns: dict with overall_score (0-100) and signal_breakdown
    """
    signals = {}

    # Signal 1: Prior Relationship (40%)
    prior_score = calculate_prior_relationship(
        foundation_profile['ein'],
        nonprofit['ein'],
        nonprofit['name_variants']
    )
    signals['prior_relationship'] = prior_score * 0.40

    # Signal 2: Geographic Match (15%)
    geo_score = calculate_geographic_score(
        foundation_profile['state'],
        foundation_profile,
        nonprofit['state']
    )
    signals['geographic'] = geo_score * 0.15

    # Signal 3: Grant Size Alignment (12%)
    size_score = calculate_grant_size_fit(
        foundation_profile,
        nonprofit['requested_amount']
    )
    signals['grant_size'] = size_score * 0.12

    # Signal 4: Repeat Funding Potential (10%)
    repeat_score = calculate_repeat_potential(foundation_profile, nonprofit)
    signals['repeat_potential'] = repeat_score * 0.10

    # Signal 5: Portfolio Concentration (8%)
    portfolio_score = calculate_portfolio_match(foundation_profile, nonprofit)
    signals['portfolio_match'] = portfolio_score * 0.08

    # Signal 6: Purpose Text Match (5%)
    purpose_score = calculate_purpose_match(
        foundation_profile,
        nonprofit['mission_keywords']
    )
    signals['purpose_alignment'] = purpose_score * 0.05

    # Signal 7: Recipient Validation (4%)
    validation_score = calculate_recipient_validation(nonprofit)
    signals['recipient_validation'] = validation_score * 0.04

    # Signal 8: Foundation Size Alignment (3%)
    foundation_size_score = calculate_size_alignment(
        foundation_profile['size_category'],
        nonprofit['annual_budget']
    )
    signals['size_alignment'] = foundation_size_score * 0.03

    # Signal 9: Regional Proximity (2%)
    regional_score = calculate_regional_proximity(
        foundation_profile['state'],
        nonprofit['state']
    )
    signals['regional_proximity'] = regional_score * 0.02

    # Signal 10: Grant Frequency (1%)
    frequency_score = calculate_grant_frequency(foundation_profile)
    signals['grant_frequency'] = frequency_score * 0.01

    # Calculate total
    total_score = sum(signals.values())

    return {
        'overall_score': total_score,
        'signal_breakdown': signals,
        'confidence': foundation_profile.get('confidence_score', 80)
    }
```

### 4.2 Score Ranges and Interpretation

| Score Range | Interpretation | Action |
|-------------|----------------|--------|
| **80-100** | Excellent Match | High priority - apply immediately |
| **60-79** | Good Match | Strong candidate - include in report |
| **40-59** | Moderate Match | Consider if geography/sector align |
| **20-39** | Weak Match | Only if few options available |
| **0-19** | Poor Match | Do not include in recommendations |

### 4.3 Thresholds for Inclusion

| Report Type | Minimum Score | Maximum Foundations |
|-------------|---------------|---------------------|
| Top Matches | 60+ | 25 |
| Extended List | 40+ | 100 |
| Full Research | 20+ | 500 |

---

## 5. Openness Score

### 5.1 Purpose

The Openness Score is a separate sub-algorithm that estimates the likelihood a foundation will fund **new grantees** (organizations they haven't funded before). This is critical because many foundations give primarily to pre-existing relationships.

### 5.2 Components

| Factor | Weight | Description |
|--------|--------|-------------|
| % First-Time Recipients | 40% | What percentage of grants went to first-time grantees? |
| Accepts Unsolicited | 25% | Does foundation have open application process? |
| Recipient Diversity | 20% | How many unique recipients per year? |
| Application Transparency | 15% | Is application process documented? |

### 5.3 Calculation

```python
def calculate_openness_score(foundation_profile):
    """
    Calculate likelihood foundation will fund new grantees.
    Returns: 0-100 score
    """
    components = {}

    # Factor 1: % First-Time Recipients (40%)
    first_time_rate = foundation_profile.get('first_time_recipient_rate', 50)
    components['first_time'] = first_time_rate * 0.40

    # Factor 2: Accepts Unsolicited (25%)
    accepts_unsolicited = foundation_profile.get('accepts_unsolicited', False)
    only_preselected = foundation_profile.get('only_contri_to_preselected_ind', True)

    if accepts_unsolicited and not only_preselected:
        components['unsolicited'] = 100 * 0.25
    elif not only_preselected:
        components['unsolicited'] = 75 * 0.25
    else:
        components['unsolicited'] = 0 * 0.25

    # Factor 3: Recipient Diversity (20%)
    unique_recipients_per_year = foundation_profile.get('unique_recipients_per_year', 10)
    if unique_recipients_per_year > 100:
        diversity_score = 100
    elif unique_recipients_per_year > 50:
        diversity_score = 80
    elif unique_recipients_per_year > 20:
        diversity_score = 60
    elif unique_recipients_per_year > 5:
        diversity_score = 40
    else:
        diversity_score = 20
    components['diversity'] = diversity_score * 0.20

    # Factor 4: Application Transparency (15%)
    has_website = foundation_profile.get('website_url') is not None
    has_guidelines = foundation_profile.get('application_process') is not None

    if has_website and has_guidelines:
        components['transparency'] = 100 * 0.15
    elif has_website or has_guidelines:
        components['transparency'] = 50 * 0.15
    else:
        components['transparency'] = 0 * 0.15

    return sum(components.values())
```

### 5.4 Integration with Main Scoring

The Openness Score acts as a **filter**, not a scoring component:

```python
def should_include_foundation(foundation_profile, nonprofit, min_openness=30):
    """
    Determine if foundation should be included based on openness.
    """
    # Check if nonprofit has prior relationship
    has_prior = calculate_prior_relationship(
        foundation_profile['ein'],
        nonprofit['ein'],
        nonprofit['name_variants']
    ) > 0

    # If prior relationship exists, always include
    if has_prior:
        return True

    # Otherwise, filter by openness score
    openness = calculate_openness_score(foundation_profile)
    return openness >= min_openness
```

### 5.5 Critical Database Filter

The most important filter for openness is the IRS field `only_contri_to_preselected_ind`:

```sql
-- Find foundations open to applications
SELECT ein, business_name, state, total_assets_eoy_amt
FROM f990_2025.pf_returns
WHERE grants_to_organizations_ind = TRUE
  AND (only_contri_to_preselected_ind = FALSE
       OR only_contri_to_preselected_ind IS NULL)
ORDER BY total_assets_eoy_amt DESC NULLS LAST;
```

---

## 6. Known Limitations

### 6.1 What the Algorithm Doesn't Capture

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Board relationships | Personal connections not visible | Future: network analysis |
| Grant proposal quality | Quality of ask matters | Outside algorithm scope |
| Foundation strategy shifts | Recent pivots may not show in data | Weight recent years higher |
| Multi-mission nonprofits | Algorithm uses single profile | Allow multiple profiles per nonprofit |
| New foundations | <5 grants = low confidence | Use foundation type averages |

### 6.2 Edge Cases

#### Case 1: Foundation with <5 Grants
```python
if foundation.total_grants < 5:
    return {
        'status': 'low_confidence',
        'message': 'Insufficient grant history for reliable matching.',
        'profile': get_foundation_type_average(foundation.type),
        'confidence': 20
    }
```

#### Case 2: Single-Recipient Foundation
```python
if foundation.unique_recipients == 1:
    return {
        'status': 'single_recipient',
        'message': 'Foundation only funds one organization.',
        'recommendation': 'NOT ACCEPTING APPLICATIONS',
        'confidence': 95
    }
```

#### Case 3: Highly Diversified (No Clear Pattern)
```python
if foundation.concentration_level == 'Highly Diversified':
    return {
        'status': 'open_grantmaker',
        'message': 'Broad giving patterns, many org types eligible.',
        'confidence': 60
    }
```

#### Case 4: Missing Grant Purposes (>50%)
```python
if foundation.avg_purpose_length < 10:
    # Disable language-based signals
    signals['purpose_alignment'] = 50 * 0.05  # Neutral score
    # Increase weight of other signals proportionally
```

#### Case 5: Dramatic Portfolio Shift
```python
# Weight recent years (2022-2024) 3x more than older years (2016-2020)
recent_weight = 3.0
historical_weight = 1.0
```

### 6.3 Future Improvements Needed

| Improvement | Priority | Complexity |
|-------------|----------|------------|
| Board member network analysis | High | High |
| Semantic embedding for mission matching | Medium | Medium |
| Multi-year trend detection | Medium | Medium |
| Recipient EIN enrichment | High | Low |
| Application deadline integration | High | Low |
| Real-time web scraping for openness | Medium | High |

---

## 7. Source Files

### 7.1 Original Research Documents

| File | Path | Content |
|------|------|---------|
| Research Specification | `OLD/Grant Matching Research/Foundation Goals Algorithm/PHASE_0_RESEARCH_SPECIFICATION.md` | 1,400+ lines research methodology |
| Executive Summary | `OLD/Grant Matching Research/Foundation Goals Algorithm/RESEARCH_EXECUTIVE_SUMMARY.md` | Top-line research findings |
| Full Research Report | `OLD/Grant Matching Research/Foundation Goals Algorithm/FOUNDATION_RECIPIENT_PREFERENCE_RESEARCH_REPORT.md` | Detailed statistical analysis |
| Algorithm Spec v1 | `OLD/Grant Matching Research/Foundation Goals Algorithm/WHAT_THEY_WANT_ALGORITHM_SPEC.md` | Original algorithm pseudocode |
| Manual Matching Plan | `OLD/Matching Research (Manual)/grant_matching_plan.md` | Three-tier matching framework |
| Data Model | `OLD/Matching Research (Manual)/grant_matching_data_model.md` | Database table specifications |

### 7.2 Database Schema

| File | Path | Content |
|------|------|---------|
| Data Dictionary | `1. Database/DATA_DICTIONARY.md` | Full table and field documentation |
| Schema SQL | `1. Database/F990-2025/schema.sql` | PostgreSQL table definitions |
| Database Credentials | `1. Database/Postgresql Info.txt` | Connection details |

### 7.3 Data Artifacts Generated

| File | Location | Content |
|------|----------|---------|
| foundation_preferences.csv | `OLD/Grant Matching Research/Foundation Goals Algorithm/` | 66,732 pre-calculated profiles (5.5 MB) |
| recipient_entities.csv | `OLD/Grant Matching Research/Foundation Goals Algorithm/` | Deduplicated recipient table (85 MB) |
| correlation_matrix.csv | `OLD/Grant Matching Research/Foundation Goals Algorithm/` | Signal correlation analysis |

### 7.4 Summary Reference

| File | Path | Content |
|------|------|---------|
| Project Summary | `THEGRANTSCOUT_SUMMARY 2025-12-5.md` | Current project status and algorithm overview |
| CLAUDE.md | `.claude/CLAUDE.md` | Project context and quick reference |

---

## 8. Quick Reference

### 8.1 Signal Weights Summary

| # | Signal | Weight | Correlation |
|---|--------|--------|-------------|
| 1 | Prior Relationship | 40% | 0.72 |
| 2 | Geographic Match | 15% | 0.58 |
| 3 | Grant Size Alignment | 12% | 0.51 |
| 4 | Repeat Funding Rate | 10% | 0.48 |
| 5 | Portfolio Concentration | 8% | 0.42 |
| 6 | Purpose Text Match | 5% | 0.38 |
| 7 | Recipient Validation | 4% | 0.35 |
| 8 | Foundation Size | 3% | 0.32 |
| 9 | Regional Proximity | 2% | 0.28 |
| 10 | Grant Frequency | 1% | 0.25 |

### 8.2 Key SQL Queries

**Find open foundations:**
```sql
SELECT ein, business_name, state, total_assets_eoy_amt
FROM f990_2025.pf_returns
WHERE grants_to_organizations_ind = TRUE
  AND (only_contri_to_preselected_ind = FALSE
       OR only_contri_to_preselected_ind IS NULL)
ORDER BY total_assets_eoy_amt DESC NULLS LAST;
```

**Get foundation grant history:**
```sql
SELECT recipient_name, recipient_state, amount, purpose, tax_year
FROM f990_2025.pf_grants
WHERE filer_ein = '123456789'
ORDER BY tax_year DESC, amount DESC;
```

**Calculate repeat funding rate:**
```sql
WITH grant_counts AS (
    SELECT filer_ein, recipient_name, COUNT(*) as grants
    FROM f990_2025.pf_grants
    GROUP BY filer_ein, recipient_name
)
SELECT
    filer_ein,
    COUNT(*) as total_recipients,
    SUM(CASE WHEN grants > 1 THEN 1 ELSE 0 END) as repeat_recipients,
    ROUND(100.0 * SUM(CASE WHEN grants > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as repeat_rate
FROM grant_counts
GROUP BY filer_ein;
```

### 8.3 Database Connection

```python
import psycopg2

db_conn = psycopg2.connect(
    host='172.26.16.1',
    port=5432,
    database='postgres',
    user='postgres',
    password='<see Postgresql_Info.txt>'
)
```

---

## 9. Validation Methodology

### 9.1 Cross-Validation (Recommended)

```python
def validate_algorithm_with_holdout():
    """
    K-fold cross-validation on historical data.
    """
    # Split foundations into 5 folds
    for fold in range(5):
        # Train on 80% of each foundation's grants
        training_grants = get_grants_by_fold(fold, 'train')

        # Generate profiles using only training data
        profiles = generate_all_profiles(training_grants)

        # Test: Do held-out grants score in top quartile?
        test_grants = get_grants_by_fold(fold, 'test')

        for grant in test_grants:
            score = calculate_match_score(
                profiles[grant.foundation_ein],
                create_nonprofit_from_grant(grant)
            )
            results.append({
                'actual': True,  # This grant actually happened
                'score': score['overall_score']
            })

    # Success: >75% of actual grants score in top quartile (score > 60)
    top_quartile_rate = sum(r['score'] > 60 for r in results) / len(results)
    return top_quartile_rate > 0.75
```

### 9.2 Expert Review

1. Generate profiles for 50 well-known foundations
2. Have grant professionals review for accuracy
3. Success threshold: >80% accuracy rating

### 9.3 A/B Testing (Post-Launch)

- Version A: Matches with full algorithm
- Version B: Simple geographic + sector matching
- Measure: Application rate, response rate, funding rate
- Success threshold: Version A outperforms by >20%

---

## Appendix A: Statistical Details

### Correlation Matrix (Top Signals)

| Signal 1 | Signal 2 | Correlation |
|----------|----------|-------------|
| Prior Relationship | Geographic | 0.42 |
| Prior Relationship | Grant Size | 0.35 |
| Geographic | Grant Size | 0.28 |
| Repeat Rate | Portfolio | 0.38 |

### Sample Sizes

- All correlations based on n > 100,000
- Foundation profiles based on min 5 grants (average: 24 grants)
- Statistical tests: Pearson correlation, t-tests, chi-square
- All reported correlations: p < 0.05
- Top 5 signals: p < 0.001

---

## Appendix B: Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-08 | 1.0 | Initial comprehensive specification compiled from research documents |
| 2025-11-15 | 0.5 | Phase 0 research completed |
| 2025-11-10 | 0.1 | Initial hypotheses documented |

---

## Appendix C: Complementary Opportunity Scoring System

In addition to the foundation-first matching algorithm documented above, TheGrantScout uses a complementary **Opportunity Scoring Engine** for matching nonprofits directly to grant opportunities (RFPs, federal grants, etc.).

### Opportunity Scoring vs Foundation Matching

| Aspect | Foundation Matching (This Doc) | Opportunity Scoring |
|--------|-------------------------------|---------------------|
| **Purpose** | Match nonprofits to foundations | Match nonprofits to specific grant RFPs |
| **Data source** | IRS 990-PF historical grants | Aggregated opportunity databases |
| **Signals** | 10 signals, 100 points max | 6 components, 130 points max |
| **Use case** | Prospecting, relationship building | Active grant applications |

### Opportunity Scoring Components (130 Points Max)

| Component | Points | Description |
|-----------|--------|-------------|
| Grant Size Fit | 25 | Overlap between nonprofit's target range and opportunity amount |
| Specific Need Match | 30 | Base keyword matching score |
| Keyword Bonus | 0-20 | Tiered bonus for multiple keyword matches |
| Program Area Alignment | 20 | Semantic similarity to mission focus |
| Geographic Preference | 15 | Location/scope alignment |
| Source Quality | 10 | Data quality and source reputation |
| Urgency Bonus | 0-10 | Additive points for deadline proximity |

### Hybrid Approach (Recommended)

Per research findings (November 2025), the recommended approach combines both systems:

1. **Stage 1:** Foundation-first matching (top 25 foundations per nonprofit) - 85-90% precision
2. **Stage 2:** Direct opportunity matching (top 25 opportunities) - 70-75% precision
3. **Stage 3:** Merge, deduplicate, re-rank for final recommendations

**Expected outcome:** 50+ high-quality matches per organization with 75-85% combined precision.

### Source Files for Opportunity Scoring

| File | Location |
|------|----------|
| Scoring Engine Code | `OLD/Opportunities/4. Opportunity Matching/Matching Take 1/scoring_engine.py` |
| Engine Documentation | `OLD/Opportunities/4. Opportunity Matching/Matching Take 1/SCORING_ENGINE_DOCUMENTATION.md` |
| Executive Report | `OLD/Opportunities/4. Opportunity Matching/Algorithm Research/FINAL_EXECUTIVE_REPORT.md` |

---

**Document Status:** PRODUCTION-READY
**Next Review:** After first beta report using algorithm
**Owner:** TheGrantScout Dev Team

---

*This specification was synthesized from Phase 0 research (1.6M grants analyzed) and is ready for implementation. Any engineer should be able to build the matching algorithm directly from this document.*
