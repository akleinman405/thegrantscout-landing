# Client Rules - TheGrantScout

Beta tester information and client management guidelines.

---

## Beta Group 1 (BG1)

| Code | Organization | Sector | Geography | Status |
|------|--------------|--------|-----------|--------|
| SNS | Senior Network Services | Senior services | California | Report 1 delivered, errors found |
| PSMF | Patient Safety Movement Foundation | Healthcare education | National/Global | Wants foundation-focused reports |
| RHF | Retirement Housing Foundation | Senior housing | Multi-state | Values organization/reminders |
| KU | Ka Ulukoa | Youth athletics | Hawaii | Report 2 held (deadline issue) |
| ACA | Arborbrook Christian Academy | K-12 athletics | North Carolina | Awaiting feedback |

**Source:** 3 from cold calls, 2 from cold emails

---

## Beta Group 2 (BG2)

| Code | Organization | Contact | Status |
|------|--------------|---------|--------|
| HN | Horizons National | Alex Hof | Form filled, ready for first report |

**Details:** Out-of-school K-8 programs, 6-week summer program, $43M decentralized network. Wants foundation prospecting + direct fundraising. Looking for hyperlocal funding.

---

## Key Feedback

### Mariam (SNS)
> "The way you broke down the work ensures no action is overlooked."

- Only 1 of 5 opps was truly new to her
- Suggested annual calendar with selective alerts (3/year vs weekly)
- Asked about grant writing concierge tier
- Validates need for DISCOVERY, not just reminders

### Andy (RHF)
> Info organized in one place was valuable even though he knew most opportunities.

- Validates "calendar manager" customer type
- Values comprehensive organization over discovery

### Consuelo (PSMF)
> Multi-mission orgs need foundation-first approach.

- Prefers ~5 foundations with relationship-building info
- Fellowship Program is priority funding target
- Interested in political/family foundation connections
- Prefers LOI prospecting strategy over formal applications

---

## Three Customer Types

| Type | Characteristics | What They Want | Example |
|------|-----------------|----------------|---------|
| Calendar Managers | Experienced grant writers, know most opps | Organization, reminders, nothing overlooked | Andy (RHF), Mariam (SNS) |
| Niche Seekers | Looking outside usual sources | Discovery of new/unexpected funders | Ka Ulukoa (Hawaii-specific) |
| Relationship Builders | Prefer prospecting over formal apps | Foundation profiles, LOI strategy, networking | Consuelo (PSMF) |

---

## Report Format Preferences

| Client | Preference |
|--------|------------|
| PSMF | Foundation-focused (~5 foundations with deep profiles) |
| SNS | Opportunity-focused with calendar view |
| RHF | Comprehensive organization of all opportunities |
| KU | Hawaii-specific foundations prioritized |
| HN | Hyperlocal funding by geography |

---

## Known Client Funders (Exclude from Reports)

When generating reports, check `dim_clients.known_funders` array to exclude foundations the client already has relationships with.

```sql
SELECT known_funders
FROM f990_2025.dim_clients
WHERE name ILIKE '%{client_name}%';
```

---

## Client Questionnaire Location

`~/Documents/TheGrantScout/2. Beta Testing/`

Each questionnaire captures:
- Mission and programs
- Geographic scope
- Budget and grant capacity
- Known funders (to exclude)
- Funding priorities

---

## Pricing

- **Target:** ~$100/mo (founding member rate)
- **Mariam feedback:** Didn't object to $100/mo
- **Model:** Monthly subscription with PDF reports

---

*See reports.md for report quality criteria. See CLAUDE.md for project overview.*
