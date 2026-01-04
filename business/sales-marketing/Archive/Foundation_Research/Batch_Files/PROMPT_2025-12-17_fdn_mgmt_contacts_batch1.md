# PROMPT: Foundation Management Company Contacts - Batch 1 (Dedicated Managers + Trust Companies)

**Date:** 2025-12-17  
**For:** Claude Code CLI  
**Batch:** 1 of 4

---

## Standards

**FIRST:** Review `CLAUDE.md` for project conventions before starting.

**Output location:** Save all outputs in the same folder as this prompt.

---

## Situation

We're building a B2B sales channel targeting foundation management companies. These companies manage private foundations for wealthy families and could offer TheGrantScout as a capacity-building service to their clients' grantees.

We need to find the right contacts at each company — specifically people in "Philanthropic Services" or equivalent roles who decide what services to offer foundation clients.

**Reference:** Pegine Grayson at Whittier Trust has the title "Senior Vice President, Director of Philanthropic Services" — this is our model contact.

---

## Target Titles (in priority order)

1. **Director of Philanthropic Services**
2. **VP/SVP of Philanthropic Services**
3. **Head of Foundation Services**
4. **Managing Director, Philanthropy**
5. **Director of Client Services** (foundation-focused)
6. **Client Advisor, Philanthropic Services**
7. **Senior Program Officer** (if manages foundation relationships)

**Avoid:** General sales/marketing, Investment Managers only, Junior staff

---

## Companies to Research (Batch 1)

### 1. Foundation Source
- **Website:** foundationsource.com
- **HQ:** Fairfield, CT
- **Type:** Dedicated Foundation Manager
- **Scale:** 4,000+ clients, $26B+ AUM
- **Services:** Full administration, compliance, tax, grantmaking platform
- **Notes:** Largest dedicated manager. Recently acquired Pacific Foundation Services (2025), Giving Place, PG Calc. Partnerships with Northern Trust & Fidelity.

### 2. Sterling Foundation Management
- **Website:** sterlingfoundations.com
- **HQ:** Great Falls, VA
- **Type:** Dedicated Foundation Manager
- **Scale:** Unknown (hundreds of foundations per website)
- **Services:** Foundation administration, charitable remainder trusts, philanthropy consulting
- **Notes:** Oldest national firm (since 1998). CRT specialists.

### 3. Crewe Foundation Services
- **Website:** crewefoundationservices.com
- **HQ:** Salt Lake City, UT
- **Type:** Dedicated Foundation Manager
- **Services:** Private foundation setup/admin, DAFs, supporting orgs, charitable trusts
- **Notes:** Comprehensive planned giving. Full administration from setup to grant distribution.

### 4. BlueStone Services
- **Website:** bluestonesvc.com
- **HQ:** Timonium, MD
- **Type:** Outsourced Administration
- **Services:** Private foundation accounting, HR, admin support, grant administration
- **Notes:** Outsourced accounting and HR consulting. Strategic planning support.

### 5. Bessemer Trust
- **Website:** bessemertrust.com
- **HQ:** New York, NY
- **Type:** Multi-Family Office
- **Scale:** 3,000+ families/foundations/endowments, $200B+ AUM
- **Services:** Private foundation advisory, DAFs, investment management, family office
- **Notes:** Founded 1907. 98.4% retention. $10M minimum. 19 regional offices.

### 6. Glenmede Trust
- **Website:** glenmede.com
- **HQ:** Philadelphia, PA
- **Type:** Trust Company
- **Scale:** $40B+ AUM
- **Services:** Family philanthropy, private foundation management, OCIO
- **Notes:** Founded 1956 for Pew Trusts. Offices in NYC, NJ, Pittsburgh, DC, Cleveland, West Palm Beach, Wilmington.

### 7. Fiduciary Trust Company
- **Website:** fiduciary-trust.com
- **HQ:** Boston, MA
- **Type:** Trust Company
- **Scale:** $34B AUM
- **Services:** Foundation advisory, DAFs, estate planning, family office
- **Notes:** Founded 1885. Being acquired by GTCR (announced Nov 2025).

### 8. Arden Trust Company
- **Website:** ardentrust.com
- **HQ:** Wilmington, DE
- **Type:** Trust Company
- **Scale:** 60+ foundations, $5.4B AUA; parent Kestra has $92B
- **Services:** Charitable trusts, directed trusts, trust administration
- **Notes:** Part of Kestra Financial. Formerly Reliance Trust Company of Delaware.

---

## Research Tasks (for each company)

### Task 1: Find Primary Contact
- Search company website "Team" / "Staff" / "Leadership" / "Our People" pages
- Search LinkedIn: "[Company] philanthropic services"
- Search LinkedIn: "[Company] foundation services"
- Search LinkedIn: "[Company] client services"
- Look for Director/VP/Head of Philanthropic Services or equivalent

### Task 2: Find Secondary Contact(s)
- Find 1-2 additional people in same department
- Could be: Senior Client Advisor, Grants Manager, Program Director, Foundation Administrator

### Task 3: Gather Contact Details
For each person found:
- Full name
- Title
- LinkedIn URL
- Email (from website, or infer from pattern like firstname@company.com)
- Phone (if on website)
- Office location

### Task 4: Note Company Intel
- How they describe their philanthropic/foundation services
- Any recent news (acquisitions, new hires, partnerships)
- Client requirements/minimums
- Geographic focus or specialties

---

## Output

**File:** `REPORT_2025-12-17_fdn_mgmt_contacts_batch1.md`

For each company:

```markdown
### [Company Name]
**Website:** [url]
**Philanthropic Services Page:** [url if different]
**Type:** [Dedicated Manager / Trust Company / MFO]

**Primary Contact:**
- Name: 
- Title:
- LinkedIn:
- Email:
- Phone:
- Office:

**Secondary Contact(s):**
- Name:
- Title:
- LinkedIn:
- Email:

**Company Intel:**
- Services offered:
- Client requirements:
- Recent news:
- Notes:
```

**Also create:** `DATA_2025-12-17_fdn_mgmt_contacts_batch1.csv`

Columns:
```
company_name,company_type,contact_name,contact_title,contact_type,linkedin_url,email,email_source,phone,phone_source,office_location,notes
```

---

## Research Sources (in order)

1. Company website team/staff pages
2. LinkedIn search (company + relevant keywords)
3. ZoomInfo / RocketReach (for email patterns)
4. Press releases / news
5. Industry publications (Chronicle of Philanthropy)
6. Conference speaker lists (Exponent Philanthropy, NCFP)

---

## Notes

- Foundation Source is the biggest — find multiple contacts if possible
- Fiduciary Trust is being acquired — note any leadership changes
- Bessemer is huge ($200B) — look for dedicated philanthropy practice lead
- Glenmede originated from Pew Trusts — strong philanthropy DNA
- If no dedicated "Philanthropic Services" exists, find whoever leads foundation client relationships
