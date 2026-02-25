# PROMPT 3 of 4: VetsBoats — Contact Research for Relationship Leads

**Date:** 2026-02-21  
**Type:** Database queries + light web research  
**Schema:** f990_2025  
**Client:** VetsBoats Foundation (EIN 464194065, "Wooden Boats for Veterans")  
**Depends on:** PROMPT 1 output (complete)  
**Next:** PROMPT 4 (report generation, after Alec reviews)

---

## Situation

We've identified opportunity leads (Prompt 2, running in parallel) and now need to find the best people for VetsBoats to reach out to for relationship-driven funding. These are contacts at foundations that don't have open applications, connectors in the Bay Area sailing community, and program officers at larger funders.

---

## Target Organizations

### A. From deep crawl work (already known — high priority):

| Organization | EIN | Why |
|---|---|---|
| Hutton Family Foundation | 474305984 | Best thematic match overall. Funds Warrior Sailing (4 consecutive yrs) + St. Francis Sailing. Preselected, no unsolicited apps. Wende Hutton (Canaan Partners) is key contact. |
| Jerome Mirza Foundation | (look up) | Funds Judd Goldman $50K/yr for 6 consecutive years. Preselected. Need referral from Judd Goldman network. |

### B. From Prompt 1 (relationship target, not apply-here):

| Organization | EIN | Why |
|---|---|---|
| St. Francis Sailing Foundation | 942956977 | $75K to TISC, $65K to St. Francis YC Junior Sailing. Mission: "disabled access to the sport of sailing." 3 grants total — relationship-driven, not open applications. SF Bay based. |

### C. Bay Area sailing network organizations (for connector nodes):

Search the officers table for board members at these orgs:
- St. Francis Yacht Club
- Treasure Island Sailing Center (TISC)
- BAADS (Bay Area Association of Disabled Sailors)
- Warrior Sailing Program
- Achieve Tahoe
- Judd Goldman Adaptive Sailing Foundation
- Any other Bay Area sailing/adaptive sports orgs found in DB

---

## Tasks

### 1. Query officers table for board members at target foundations

```sql
-- Officers at PF targets
SELECT o.person_nm, o.title_txt, o.ein, pr.business_name, pr.tax_year
FROM f990_2025.officers o
JOIN f990_2025.pf_returns pr ON o.ein = pr.ein
WHERE o.ein IN ('474305984' /* Hutton */, /* Mirza EIN */)
AND pr.tax_year = (SELECT MAX(tax_year) FROM f990_2025.pf_returns pr2 WHERE pr2.ein = o.ein)
ORDER BY o.ein;
```

```sql
-- Officers at PC targets (St. Francis Sailing Foundation + sailing network orgs)
SELECT o.person_nm, o.title_txt, o.ein, nr.organization_name, nr.tax_year
FROM f990_2025.officers o
JOIN f990_2025.nonprofit_returns nr ON o.ein = nr.ein
WHERE o.ein IN ('942956977' /* St. Francis Sailing */, /* TISC EIN */, /* BAADS EIN */, /* other sailing org EINs */)
AND nr.tax_year = (SELECT MAX(tax_year) FROM f990_2025.nonprofit_returns nr2 WHERE nr2.ein = o.ein)
ORDER BY o.ein;
```

**Note:** You'll need to look up EINs for the sailing network orgs. Try name ILIKE searches against both `pf_returns` and `nonprofit_returns`.

### 2. Cross-reference for connector nodes

Find people who sit on multiple relevant boards — these are the highest-value contacts.

```sql
-- People on 2+ relevant org boards
SELECT o.person_nm, COUNT(DISTINCT o.ein) as board_count,
       ARRAY_AGG(DISTINCT COALESCE(nr.organization_name, pr.business_name)) as orgs
FROM f990_2025.officers o
LEFT JOIN f990_2025.nonprofit_returns nr ON o.ein = nr.ein
LEFT JOIN f990_2025.pf_returns pr ON o.ein = pr.ein
WHERE o.ein IN (
  -- All relevant EINs: targets + peer orgs + sailing orgs
  '474305984',  -- Hutton Family Foundation
  '942956977',  -- St. Francis Sailing Foundation
  -- Add: Mirza, TISC, BAADS, Warrior Sailing, Achieve Tahoe, Judd Goldman, St. Francis YC EINs
  -- Look these up first
)
GROUP BY o.person_nm
HAVING COUNT(DISTINCT o.ein) >= 2
ORDER BY board_count DESC;
```

**Specifically look for:**
- **Wende Hutton** — Known from deep crawl. Canaan Partners, Hutton Family Foundation board. Single highest-value relationship target. Confirm she appears in officers table and find any other board connections.
- Anyone on both a target foundation board AND a Bay Area sailing org board
- Anyone on both a peer org board AND a target foundation board

### 3. Light web search for top ~8 contacts

For the most promising people from steps 1-2:

```
"[person name]" "[org name]" email OR contact OR LinkedIn
```

Find:
- Current role confirmation (IRS data can be 1-2 years old)
- Email address if publicly available
- LinkedIn profile URL
- Any recent news/activity confirming involvement

**Keep it light.** 1-2 searches per person max.

### 4. Output contact cards

---

## Output

| File | Description |
|------|-------------|
| DATA_2026-02-21_vetsboats_contact_cards.md | Contact cards for Alec to review |
| DATA_2026-02-21_vetsboats_connector_nodes.json | Cross-reference query results |

### Format for contact cards

```
## [Person Name]
**Title:** [role] at [organization]
**Also connected to:** [other boards/orgs from cross-reference]
**Why they matter:** [which foundations/funding they unlock for VetsBoats]
**Outreach angle:** [what to say, what connection to reference]
**Contact:** [email, phone, LinkedIn if found]
**Confidence:** HIGH / MEDIUM / LOW (that info is current and accurate)
**⚠ Flags:** [anything to verify]
```

### STOP HERE

Do not write the client-facing contacts deliverable. Alec will review the cards and respond with:
- Which 5 contacts to include
- Any outreach angle edits
- Any contacts to add from his own network knowledge
