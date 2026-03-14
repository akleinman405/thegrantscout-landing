# Signup Field Specification

**Created:** 2026-03-09
**Purpose:** Define the self-service signup form fields across 5 steps.

---

## Step 1: Organization Info (5 fields)

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Organization Name | text | Yes | Min 2 chars |
| EIN | text | Yes | 9 digits, accepts XX-XXXXXXX or XXXXXXXXX |
| Organization Type | select | Yes | See options below |
| Contact Name | text | Yes | Min 2 chars |
| Contact Email | email | Yes | Valid email format |

**Organization Types:** 501(c)(3) Public Charity, 501(c)(3) Private Foundation, 501(c)(4), 501(c)(6), Fiscal Sponsorship, Other

---

## Step 2: Mission & Focus (4 fields)

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Mission Statement | textarea | Yes | Min 50 chars |
| Focus Areas | multi-select | Yes | Min 1 selection |
| Programs/Services | textarea | Yes | Min 50 chars |
| Populations Served | multi-select | Yes | Min 1 selection |

**Focus Areas:** Arts & Culture, Education (K-12), Education (Higher Ed), Environment, Health & Medicine, Human Services, Housing & Shelter, Youth Development, Senior Services, Disabilities, Religion, Animal Welfare, International, Community Development, Science & Technology, Other

**Populations Served:** Children & Youth (0-17), Young Adults (18-25), Adults, Seniors (65+), Veterans, Immigrants/Refugees, People with Disabilities, LGBTQ+, Low-Income Communities, Communities of Color, Rural Communities, Unhoused Individuals, General Public, Other

---

## Step 3: Capacity & Geography (7 fields)

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| State | select | Yes | US state/territory |
| City | text | Yes | Min 2 chars |
| Geographic Scope | select | Yes | See options below |
| Annual Budget | select | Yes | See ranges below |
| Grant Size Seeking | select | Yes | See ranges below |
| Grant Types Preferred | multi-select | Yes | Min 1 selection |
| Grant Capacity | select | Yes | See options below |

**Geographic Scope:** Local (city/county), Regional (multi-county), Statewide, Multi-state/Regional, National, International

**Annual Budget Ranges:** Under $250K, $250K-$500K, $500K-$1M, $1M-$5M, $5M-$10M, $10M-$25M, $25M+

**Grant Size Seeking:** Under $10K, $10K-$25K, $25K-$50K, $50K-$100K, $100K-$250K, $250K-$500K, $500K+

**Grant Types:** General Operating Support, Program/Project Grants, Capital Campaigns, Capacity Building, Research, Scholarships/Fellowships, Emergency/Disaster, Seed Funding

**Grant Capacity:** New to grants, Some experience (1-5 grants), Experienced (5-20 grants), Highly experienced (20+ grants)

---

## Step 4: Preferences (4 fields, all optional)

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| NTEE Code | text | No | Format: letter + digits |
| Known Funders | textarea | No | Comma-separated names |
| Timeframe | select | No | See options below |
| Additional Notes | textarea | No | Max 1000 chars |

**Timeframe:** ASAP (within 1 month), Short-term (1-3 months), Medium-term (3-6 months), Long-term (6-12 months), Ongoing/No rush

---

## Step 5: Review & Plan Selection (1 field)

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Plan | radio | Yes | monthly or annual |

Displays summary of all previous answers + plan selection (Monthly $99/mo or Annual $83/mo billed at $999/yr).

---

## Total: 21 fields across 5 steps

- Required: 16
- Optional: 5 (all in Step 4 + plan defaults to monthly)
