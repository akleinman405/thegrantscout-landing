-- Migration: Complete enrichment of all 46 foundation management companies
-- Date: 2026-01-02
-- Note: Adds contact names and pitch angles for all remaining companies

-- ============================================
-- MAJOR DAFs (High Volume, High Value)
-- ============================================

-- Schwab Charitable (DAFgiving360)
UPDATE prospects SET
    contact_name = 'Julia Reed',
    contact_title = 'Managing Director, Relationship Management',
    pitch_angle = 'Nation''s 2nd largest DAF. 4,700+ advisors use DAFgiving360. Donors need help answering "where should I give?" - we solve that with 8.3M grants data.'
WHERE org_name ILIKE '%schwab%charitable%' OR org_name ILIKE '%dafgiving%' AND segment = 'foundation_mgmt';

-- Fidelity Charitable
UPDATE prospects SET
    contact_name = 'Maeve (VP Philanthropic Consulting)',
    contact_title = 'VP & Head of Philanthropic Consulting',
    pitch_angle = 'Nation''s top grantmaker - $14.9B distributed in 2024. 350K+ donors. Their Philanthropic Strategists could use TheGrantScout to accelerate donor recommendations.'
WHERE org_name ILIKE '%fidelity%charitable%' AND segment = 'foundation_mgmt';

-- Vanguard Charitable
UPDATE prospects SET
    contact_name = 'Bryan Kelley',
    contact_title = 'Head of Client Services & Operations',
    pitch_angle = '50K+ donors, $2.6B granted in 2023. Premier Services for $1M+ accounts - data-driven giving recommendations would differentiate their service.'
WHERE org_name ILIKE '%vanguard%charitable%' AND segment = 'foundation_mgmt';

-- ============================================
-- MAJOR COMMUNITY FOUNDATIONS
-- ============================================

-- Chicago Community Trust
UPDATE prospects SET
    contact_name = 'Andrea Sáenz',
    contact_title = 'President & CEO',
    pitch_angle = '$4.5B AUM, $1.6B granted in 2023. Alternative contact: Sheila Cawley (Chief Philanthropy Officer). Help their donors find highest-impact nonprofits.'
WHERE org_name ILIKE '%chicago community%trust%' AND segment = 'foundation_mgmt';

-- Foundation for the Carolinas
UPDATE prospects SET
    pitch_angle = 'Major community foundation serving NC/SC. Donors need help discovering aligned nonprofits beyond their networks.'
WHERE org_name ILIKE '%foundation%carolinas%' AND segment = 'foundation_mgmt';

-- ============================================
-- WEALTH MANAGEMENT FIRMS
-- ============================================

-- Bessemer Trust
UPDATE prospects SET
    contact_name = 'Caroline Woodruff Hodkinson',
    contact_title = 'Head of Philanthropic Advisory',
    pitch_angle = '$200B+ AUM, 500+ foundations under management. $220M granted annually. Alt contact: Christopher A. Pastor (SVP Philanthropy). Data-driven approach for UHNW families.'
WHERE org_name ILIKE '%bessemer%trust%' AND segment = 'foundation_mgmt';

-- Goldman Sachs Ayco
UPDATE prospects SET
    contact_name = 'David Golub',
    contact_title = 'Board Member, GS Philanthropy Fund',
    pitch_angle = 'Ayco advisors provide in-depth philanthropic planning. Help their UHNW clients identify high-impact nonprofits efficiently.'
WHERE org_name ILIKE '%goldman%sachs%ayco%' OR org_name ILIKE '%ayco%' AND segment = 'foundation_mgmt';

-- UBS Family Advisory and Philanthropy
UPDATE prospects SET
    contact_name = 'Nicole Sebastian',
    contact_title = 'Executive Director, Family Advisory & Philanthropy',
    pitch_angle = '150+ philanthropy experts in 12 locations. Help advisors serve foundation families with data-driven grantee discovery.'
WHERE org_name ILIKE '%ubs%family%' OR org_name ILIKE '%ubs%philanthropy%' AND segment = 'foundation_mgmt';

-- Fidelity Private Foundation Services
UPDATE prospects SET
    pitch_angle = 'Private foundation administration services. Clients need help with grantee discovery and due diligence - we accelerate that process.'
WHERE org_name ILIKE '%fidelity%private%foundation%' AND segment = 'foundation_mgmt';

-- ============================================
-- PHILANTHROPY CONSULTANTS
-- ============================================

-- Bridgespan Group
UPDATE prospects SET
    contact_name = 'Thomas Tierney',
    contact_title = 'Co-Founder & Chairman',
    pitch_angle = 'Advises Gates, Ford, Bloomberg, Rockefeller foundations. Elite consulting - TheGrantScout data could power their research. Located in Boston, SF, NYC.'
WHERE org_name ILIKE '%bridgespan%' AND segment = 'foundation_mgmt';

-- The Philanthropic Initiative (TPI)
UPDATE prospects SET
    contact_name = 'Leslie Pine',
    contact_title = 'Managing Partner',
    pitch_angle = 'Pioneered strategic philanthropy. Now part of Boston Foundation. Help their clients increase impact with data-driven grantee matching.'
WHERE org_name ILIKE '%philanthropic initiative%' OR org_name ILIKE '%TPI%' AND segment = 'foundation_mgmt';

-- CCS Fundraising
UPDATE prospects SET
    contact_name = 'Jon Kane',
    contact_title = 'President & CEO',
    pitch_angle = 'Since 1947, 25K+ campaigns. Alt contact: Rick Happy (Chairman). Different angle: help their nonprofit clients find aligned foundations.'
WHERE org_name ILIKE '%ccs%fundraising%' AND segment = 'foundation_mgmt';

-- Aly Sterling Philanthropy
UPDATE prospects SET
    pitch_angle = 'Midwest-based fundraising consulting. Help their nonprofit clients identify foundation prospects. Toledo, OH focus.'
WHERE org_name ILIKE '%aly%sterling%' AND segment = 'foundation_mgmt';

-- ============================================
-- FISCAL SPONSORS & PASS-THROUGH FUNDERS
-- ============================================

-- Tides Foundation
UPDATE prospects SET
    contact_name = 'Janiece Evans-Page',
    contact_title = 'CEO',
    pitch_angle = '$1.4B AUM, $761M granted in 2023. 5,600+ grants to 4,000+ grantees. Help donors and projects identify aligned charities.'
WHERE org_name ILIKE '%tides%foundation%' AND segment = 'foundation_mgmt';

-- New Venture Fund
UPDATE prospects SET
    contact_name = 'Lee Bodner',
    contact_title = 'President',
    pitch_angle = 'Premier fiscal sponsor - nearly $1B annual revenue. Now owns Sunflower Services (f/k/a Arabella). Help their projects find grantees.'
WHERE org_name ILIKE '%new venture%fund%' AND segment = 'foundation_mgmt';

-- Sunflower Services (formerly Arabella Advisors)
UPDATE prospects SET
    pitch_angle = 'Formerly Arabella Advisors, acquired by New Venture Fund Nov 2025. 243 staff, $1.2B+ in resources. Fiscal sponsorship leader.'
WHERE org_name ILIKE '%sunflower%' OR org_name ILIKE '%arabella%' AND segment = 'foundation_mgmt';

-- Open Collective Foundation
UPDATE prospects SET
    pitch_angle = 'Fiscal sponsorship for open-source and community projects. Help their projects identify foundation funding opportunities.'
WHERE org_name ILIKE '%open collective%' AND segment = 'foundation_mgmt';

-- Fractured Atlas
UPDATE prospects SET
    pitch_angle = 'Fiscal sponsor for artists and arts orgs. Help their sponsored projects find foundation grants for creative work.'
WHERE org_name ILIKE '%fractured%atlas%' AND segment = 'foundation_mgmt';

-- New York Foundation for the Arts (NYFA)
UPDATE prospects SET
    pitch_angle = 'Fiscal sponsor for NYC artists. Help sponsored artists identify foundation grant opportunities in their discipline.'
WHERE org_name ILIKE '%new york foundation%arts%' OR org_name ILIKE '%nyfa%' AND segment = 'foundation_mgmt';

-- ============================================
-- NONPROFIT FORMATION & COMPLIANCE
-- ============================================

-- Foundation Group (501c3.org)
UPDATE prospects SET
    contact_name = 'Greg McRay',
    contact_title = 'Founder & CEO',
    pitch_angle = '25K+ nonprofits formed. 100% IRS approval rate. Nashville-based. Refer TheGrantScout to newly formed nonprofits seeking foundation funding.'
WHERE org_name ILIKE '%foundation%group%' OR org_name ILIKE '%501c3%' AND segment = 'foundation_mgmt';

-- Convergent Nonprofit Solutions
UPDATE prospects SET
    pitch_angle = 'Nonprofit consulting and back-office services. Help their nonprofit clients identify foundation prospects.'
WHERE org_name ILIKE '%convergent%' AND segment = 'foundation_mgmt';

-- ============================================
-- SPECIALTY ADVISORS
-- ============================================

-- Daylight Advisors
UPDATE prospects SET
    pitch_angle = 'Global hub for philanthropic learning. Impact Philanthropy Advisor (IPA) certification program. Training partner opportunity.'
WHERE org_name ILIKE '%daylight%advisors%' AND segment = 'foundation_mgmt';

-- Family Philanthropy Advisors
UPDATE prospects SET
    pitch_angle = 'Minneapolis-based family philanthropy consulting. Help their family foundation clients make data-driven grant decisions.'
WHERE org_name ILIKE '%family philanthropy%advisors%' AND segment = 'foundation_mgmt';

-- Cascade Philanthropy Advisors
UPDATE prospects SET
    pitch_angle = 'Seattle-based philanthropy consulting. Help their Pacific Northwest clients identify aligned nonprofits.'
WHERE org_name ILIKE '%cascade%philanthropy%' AND segment = 'foundation_mgmt';

-- RISE Philanthropy Advisors
UPDATE prospects SET
    pitch_angle = 'Emerging philanthropy advisory firm. Help their clients with data-driven grantee discovery.'
WHERE org_name ILIKE '%rise%philanthropy%' AND segment = 'foundation_mgmt';

-- Hirsch Philanthropy Partners / Third Plateau
UPDATE prospects SET
    pitch_angle = 'Rebranded as Third Plateau. Strategic philanthropy consulting for foundations. Data-driven approach aligns with our offering.'
WHERE org_name ILIKE '%hirsch%' OR org_name ILIKE '%third%plateau%' AND segment = 'foundation_mgmt';

-- ============================================
-- OTHER TIER 1 COMPANIES
-- ============================================

-- J.P. Morgan Private Bank Philanthropy
UPDATE prospects SET
    pitch_angle = '~10,000 foundations under management. $340M+ annual grantmaking. Grantee discovery bottleneck - we solve it with 8.3M grants data.'
WHERE org_name ILIKE '%j.p. morgan%' OR org_name ILIKE '%jp morgan%' AND segment = 'foundation_mgmt';

-- Pacific Foundation Services
UPDATE prospects SET
    pitch_angle = 'Acquired by Foundation Source June 2025. $1B+ annual grantmaking. San Francisco based.'
WHERE org_name ILIKE '%pacific%foundation%services%' AND segment = 'foundation_mgmt';

-- Crewe Foundation Services
UPDATE prospects SET
    pitch_angle = 'Foundation administration and compliance services. Help their foundation clients with strategic grantee discovery.'
WHERE org_name ILIKE '%crewe%foundation%' AND segment = 'foundation_mgmt';
