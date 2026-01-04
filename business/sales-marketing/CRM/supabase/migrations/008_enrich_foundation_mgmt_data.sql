-- Migration: Enrich foundation management prospects with contact names and pitch angles
-- Date: 2026-01-02
-- Note: Only updating specifically researched companies (not bulk data)

-- ============================================
-- TIER 1: HIGH PRIORITY
-- ============================================

-- Glenmede Trust Company
UPDATE prospects SET
    contact_name = 'Andrew K. Slade, CAP',
    contact_title = 'VP, E&F Advisory Team Lead',
    linkedin_url = 'https://linkedin.com/in/andrewslade',
    pitch_angle = '$42B AUM, dedicated foundation practice. Andrew leads E&F Advisory - perfect for partnership where Glenmede recommends us to foundation clients.'
WHERE org_name ILIKE '%glenmede%' AND segment = 'foundation_mgmt';

-- BlueStone Services
UPDATE prospects SET
    contact_name = 'Trey Gailey, CPA',
    contact_title = 'Managing Partner',
    pitch_angle = 'Small boutique firm ($1.8M rev). Foundation clients need grant strategy, not just compliance. Easy upsell at $100/mo as bundle with accounting.'
WHERE org_name ILIKE '%bluestone%' AND segment = 'foundation_mgmt';

-- GHJ Advisors
UPDATE prospects SET
    contact_name = 'Anant Patel',
    contact_title = 'Advisory Practice Leader',
    pitch_angle = 'Serves 10 of SoCal''s top 25 foundations. Strategic Grantmaking Service would be competitive moat for their advisory practice.'
WHERE org_name ILIKE '%ghj%' AND segment = 'foundation_mgmt';

-- Plante Moran
UPDATE prospects SET
    contact_name = 'Kellie Ray',
    contact_title = 'Not-for-Profit Practice Leader',
    pitch_angle = '100s of nonprofit clients. 34% report declining federal funding - they need foundation diversification fast. Position as grant strategy partner.'
WHERE org_name ILIKE '%plante moran%' AND segment = 'foundation_mgmt';

-- ============================================
-- TIER 2: MEDIUM PRIORITY
-- ============================================

-- Fiduciary Trust Company
UPDATE prospects SET
    pitch_angle = '$34B AUM, strong DAF practice. Being acquired by GTCR (leadership transition). DAF deployment challenge - families sit on balances, TheGrantScout accelerates decisions.'
WHERE org_name ILIKE '%fiduciary%trust%' AND segment = 'foundation_mgmt';

-- Arden Trust Company
UPDATE prospects SET
    contact_name = 'Doug Sherry',
    contact_title = 'Philanthropic Services',
    pitch_angle = '$7B+ AUA, growing charitable trust practice. Help advisors become philanthropic advisors - strengthens client relationships.'
WHERE org_name ILIKE '%arden%trust%' AND segment = 'foundation_mgmt';

-- Armanino
UPDATE prospects SET
    pitch_angle = '600+ nonprofit clients, huge reach. Their benchmarking platform (300K+ nonprofits) + TheGrantScout (8.3M grants) = comprehensive foundation intelligence.'
WHERE org_name ILIKE '%armanino%' AND segment = 'foundation_mgmt';

-- ============================================
-- TIER 3: COMMUNITY FOUNDATIONS
-- ============================================

-- Silicon Valley Community Foundation
UPDATE prospects SET
    contact_name = 'Nicole Taylor',
    contact_title = 'CEO',
    pitch_angle = '$3-5B AUM. Donors ask ''where should we give?'' constantly. Data-driven grantmaking at scale for Silicon Valley tech donors.'
WHERE org_name ILIKE '%silicon valley community%' AND segment = 'foundation_mgmt';

-- California Community Foundation
UPDATE prospects SET
    contact_name = 'Miguel A. Santana',
    contact_title = 'President & CEO',
    pitch_angle = '$2.3B AUM, 1,900 funds. Equity layer that helps smaller nonprofits get discovered, not just well-connected ones.'
WHERE org_name ILIKE '%california community%' AND segment = 'foundation_mgmt';

-- Cleveland Foundation
UPDATE prospects SET
    contact_name = 'Lillian Kuri',
    contact_title = 'President & CEO',
    pitch_angle = '$3B AUM, world''s first community foundation. Help their grantees diversify funding sources beyond Cleveland Foundation.'
WHERE org_name ILIKE '%cleveland%foundation%' AND segment = 'foundation_mgmt';

-- Marin Community Foundation
UPDATE prospects SET
    contact_name = 'Rhea Suh',
    contact_title = 'President & CEO',
    pitch_angle = '850+ funds with different donor priorities. AI matching helps donors make most impactful grants based on 8.3M real grants.'
WHERE org_name ILIKE '%marin community%' AND segment = 'foundation_mgmt';

-- ============================================
-- TIER 4: LARGE BANKS & OTHERS
-- ============================================

-- Foundation Source
UPDATE prospects SET
    pitch_angle = 'Largest dedicated manager - 2,288 foundations, $59B combined assets. Their clients ask ''where should we give?'' constantly.'
WHERE org_name ILIKE '%foundation source%' AND segment = 'foundation_mgmt';

-- J.P. Morgan Private Bank
UPDATE prospects SET
    pitch_angle = '~10,000 foundations under management. Grantee discovery bottleneck - limited time/resources to find quality nonprofit matches.'
WHERE org_name ILIKE '%jp morgan%' OR org_name ILIKE '%jpmorgan%' AND segment = 'foundation_mgmt';

-- Rockefeller Philanthropy Advisors
UPDATE prospects SET
    pitch_angle = '$500M+ annual giving, $4B+ granted historically. Premier philanthropic advisory - data-driven approach aligns with their brand.'
WHERE org_name ILIKE '%rockefeller%philanthropy%' AND segment = 'foundation_mgmt';

-- Northern Trust
UPDATE prospects SET
    pitch_angle = '$450B Wealth AUM. Foundation & Institutional Advisors practice - help them serve foundation clients better.'
WHERE org_name ILIKE '%northern trust%' AND segment = 'foundation_mgmt';

-- Whittier Trust
UPDATE prospects SET
    pitch_angle = '$20B+ AUM, oldest/largest multi-family office in the West. 140 foundations under management.'
WHERE org_name ILIKE '%whittier%trust%' AND segment = 'foundation_mgmt';

-- Sterling Foundation Management
UPDATE prospects SET
    pitch_angle = 'Oldest national firm (since 1998). CRT specialists - help their charitable trust clients identify aligned nonprofits.'
WHERE org_name ILIKE '%sterling%foundation%' AND segment = 'foundation_mgmt';

-- National Philanthropic Trust
UPDATE prospects SET
    pitch_angle = 'Largest independent DAF sponsor. $5.87B granted in 2024. Help DAF donors make faster, smarter grant decisions.'
WHERE org_name ILIKE '%national philanthropic%' AND segment = 'foundation_mgmt';
