# PROMPT: Find Foundation Management Companies

**Date:** 2025-12-17  
**For:** Claude Code CLI  
**Database:** PostgreSQL, schema `f990_2025`

---

## Standards

**FIRST:** Review `CLAUDE.md` for project conventions before starting.

**Output location:** Save all outputs in the same folder as this prompt.

---

## Situation

We discovered that Whittier Trust Company manages 42 private foundations ($790M combined assets). This is a valuable B2B channel — one relationship with a foundation management company gives us access to dozens of foundations' grantees.

We want to find MORE companies like Whittier Trust that manage multiple foundations.

---

## Part 1: Database Approach (Address Clustering)

### Theory
Foundations managed by the same company often share an address (the management company's office). Find addresses with 5+ foundations = likely a management company.

### Task 1.1: Find Clustered Addresses

```sql
-- Find addresses with multiple foundations
SELECT 
    address_line_1,
    city,
    state,
    COUNT(DISTINCT ein) as foundation_count,
    SUM(total_assets) as combined_assets,
    SUM(total_grants_paid) as combined_grants
FROM [appropriate table]
WHERE [is private foundation]
GROUP BY address_line_1, city, state
HAVING COUNT(DISTINCT ein) >= 5
ORDER BY foundation_count DESC
LIMIT 50;
```

### Task 1.2: For Each Clustered Address

Pull the list of foundations at that address:
- Foundation names and EINs
- Total assets
- Annual grantmaking
- Any officer names that appear across multiple foundations (likely management company staff)

### Task 1.3: Identify Management Company Names

Look for patterns in officer/trustee names:
- "Trust Company" 
- "Foundation Services"
- "Philanthropy Advisors"
- "Private Bank"
- Company names appearing as trustees across multiple foundations

```sql
-- Find officer names appearing at multiple foundations
SELECT 
    officer_name,
    COUNT(DISTINCT foundation_ein) as foundations_served,
    STRING_AGG(DISTINCT foundation_name, '; ') as foundation_list
FROM [officers table]
WHERE officer_name ILIKE '%trust%'
   OR officer_name ILIKE '%foundation services%'
   OR officer_name ILIKE '%bank%'
   OR officer_name ILIKE '%philanthropy%'
GROUP BY officer_name
HAVING COUNT(DISTINCT foundation_ein) >= 3
ORDER BY foundations_served DESC;
```

---

## Part 2: Web Research Approach

### Task 2.1: Search for Known Industry Players

Search for and compile information on these known foundation management companies:

1. **Foundation Source** - foundationsource.com
2. **Rockefeller Philanthropy Advisors** - rockpa.org
3. **Sterling Foundation Management** - sterlingfoundations.com
4. **Hirsch Philanthropy Partners** - hirschphilanthropy.com
5. **Pacific Foundation Services** - pfs-llc.net
6. **The Philanthropic Initiative (TPI)** - tpi.org
7. **Arabella Advisors** - arabellaadvisors.com
8. **National Philanthropic Trust** - nptrust.org

For each, find:
- Headquarters address
- Number of foundations/clients managed (if disclosed)
- Total assets under management (if disclosed)
- Key staff in "Philanthropic Services" or equivalent roles
- Website URL

### Task 2.2: Search for Bank-Affiliated Programs

Major banks have philanthropy/foundation services divisions:

1. **J.P. Morgan Private Bank** - Philanthropy Services
2. **Bank of America Private Bank** - Philanthropic Solutions
3. **Northern Trust** - Foundation & Institutional Advisors
4. **U.S. Bank** - Charitable Services
5. **Wells Fargo Private Bank** - Philanthropic Services
6. **Goldman Sachs** - Ayco Charitable Foundation
7. **BNY Mellon Wealth Management** - Philanthropic Solutions

For each, find:
- Scale (foundations managed, assets, grants distributed)
- Key contacts in philanthropic services
- Geographic focus

### Task 2.3: Search for Regional Trust Companies

Search for: "[State] trust company foundation management"

Focus on major wealth centers:
- California (SF, LA)
- New York
- Texas (Houston, Dallas)
- Florida
- Illinois (Chicago)
- Massachusetts (Boston)

### Task 2.4: Industry Associations

Check member directories of:
- **Exponent Philanthropy** (small foundation focused)
- **National Center for Family Philanthropy**
- **Council on Foundations**
- **Advisors in Philanthropy**

---

## Part 3: Cross-Reference

### Task 3.1: Validate Database Findings with Web Research

For each clustered address found in Part 1:
- Search web for company at that address
- Confirm it's a foundation management company
- Find company website and key contacts

### Task 3.2: Search Database for Web-Found Companies

For companies found in Part 2:
- Search f990_2025 for their address
- Find foundations they manage
- Calculate their portfolio size

---

## Output Files

### File 1: REPORT_2025-12-17_foundation_management_companies.md

**Sections:**

1. **Executive Summary**
   - Total companies found
   - Combined foundations managed
   - Combined assets under management

2. **Top 20 Foundation Management Companies**

| Rank | Company | Foundations | Combined Assets | Annual Grants | HQ Location |
|------|---------|-------------|-----------------|---------------|-------------|

3. **Company Profiles** (for top 10)
   - Company name and website
   - Address
   - Foundations managed (list)
   - Combined assets
   - Key staff (names and titles)
   - Notes on focus/specialty

4. **Bank-Affiliated Programs**
   - Summary of major bank philanthropy divisions
   - Scale where known

5. **Regional Trust Companies**
   - By geography

6. **Methodology Notes**
   - Database queries used
   - Web sources consulted
   - Limitations

### File 2: DATA_2025-12-17_foundation_management_companies.csv

Columns:
```
company_name,website,hq_address,city,state,foundations_managed,combined_assets,combined_grants,key_contact_name,key_contact_title,key_contact_email,key_contact_linkedin,source,notes
```

### File 3: DATA_2025-12-17_clustered_addresses.csv

Raw database output of addresses with 5+ foundations:
```
address,city,state,foundation_count,combined_assets,combined_grants,foundation_names,likely_company
```

---

## Known Companies to Validate in Database

Already confirmed:
- **Whittier Trust** - 177 E Colorado Blvd, Pasadena, CA (42 foundations)

Check these addresses:
- **Pacific Foundation Services** - 44 Montgomery St or 101 Second St, San Francisco, CA
- **Foundation Source** - Fairfield, CT (or search for their name in officers)
- **Bessemer Trust** - New York, NY
- **Glenmede Trust** - Philadelphia, PA
- **Fiduciary Trust** - Boston, MA

---

## Notes

- Exclude community foundations (they're DAF sponsors, different model)
- Exclude law firms that serve as trustees (different relationship)
- Focus on companies with dedicated "Philanthropic Services" teams
- Bank programs may be harder to find via address (foundations may use family addresses)
- Some management companies are small (5-20 foundations) but still valuable targets
