# Round 2 Implementation Checklist
## TheGrantScout Database Optimization & Automation

**Based on:** Database State Assessment (November 30, 2025)
**Timeline:** 100 hours (2.5 weeks)
**Goal:** Transform manual beta into automated scalable platform

---

## WEEK 1: DATA FOUNDATION (32 hours)

### Day 1-2: Complete F990 Import
**Estimated: 26 hours (24h runtime + 2h setup/monitoring)**

- [ ] Navigate to import script directory
  ```bash
  cd "/mnt/c/.../TheGrantScout/1. Historical Data/F990/Upload Script"
  ```

- [ ] Resume incremental import (skip schema creation)
  ```bash
  python import_f990_incremental.py \
    --directory "../Raw IRS Data" \
    --skip-schema
  ```

- [ ] Monitor progress (check every 2-3 hours)
  ```sql
  SELECT zip_filename, status, files_processed,
         ROUND(files_processed::numeric / NULLIF(files_in_zip, 0) * 100, 1) as pct
  FROM f990_data.processed_zip_files
  ORDER BY created_at DESC;
  ```

- [ ] Verify completion
  - [ ] All 31 zip files processed
  - [ ] pf_grants table: 8-10M rows (vs 2.9M current)
  - [ ] schedule_i_recipients table: 5-7M rows (vs 1.4M current)
  - [ ] No errors in processed_zip_files status column

**Deliverable:** Complete historical grants dataset (2020-2025)

---

### Day 3: Migrate Array Storage (2 hours)

- [ ] Backup foundations table
  ```sql
  CREATE TABLE foundations_backup AS SELECT * FROM foundations;
  ```

- [ ] Migrate ntee_codes to ARRAY type
  ```sql
  ALTER TABLE foundations ADD COLUMN ntee_codes_array TEXT[];

  UPDATE foundations
  SET ntee_codes_array = string_to_array(ntee_codes, ',')
  WHERE ntee_codes IS NOT NULL;

  ALTER TABLE foundations DROP COLUMN ntee_codes;
  ALTER TABLE foundations RENAME COLUMN ntee_codes_array TO ntee_codes;
  ```

- [ ] Migrate program_areas to ARRAY type
  ```sql
  ALTER TABLE foundations ADD COLUMN program_areas_array TEXT[];

  UPDATE foundations
  SET program_areas_array = string_to_array(program_areas, ',')
  WHERE program_areas IS NOT NULL;

  ALTER TABLE foundations DROP COLUMN program_areas;
  ALTER TABLE foundations RENAME COLUMN program_areas_array TO program_areas;
  ```

- [ ] Verify migration
  ```sql
  SELECT ein, name, ntee_codes, program_areas
  FROM foundations
  WHERE ntee_codes IS NOT NULL
  LIMIT 10;
  ```

**Deliverable:** Consistent ARRAY storage across all tables

---

### Day 4: Database Cleanup (4 hours)

#### Delete Redundant Partitions
- [ ] Verify irs_bmf contains all records
  ```sql
  SELECT COUNT(*) FROM irs_bmf; -- Should be ~1,898,175
  ```

- [ ] Drop partition tables
  ```sql
  DROP TABLE IF EXISTS irs_bmf_eo1;
  DROP TABLE IF EXISTS irs_bmf_eo2;
  DROP TABLE IF EXISTS irs_bmf_eo3;
  DROP TABLE IF EXISTS irs_bmf_eo4;
  ```

#### Archive Staging Tables
- [ ] Create staging schema
  ```sql
  CREATE SCHEMA IF NOT EXISTS staging_archive;
  ```

- [ ] Move staging tables
  ```sql
  ALTER TABLE "f990 nonprofit comprehensive export"
    SET SCHEMA staging_archive;

  ALTER TABLE nonprofits_merged
    SET SCHEMA staging_archive;
  ```

#### Delete Compliance Risk
- [ ] Review emails_temp for any necessary data
- [ ] Delete emails_temp
  ```sql
  DROP TABLE IF EXISTS emails_temp;
  ```

- [ ] Verify cleanup
  ```sql
  SELECT schemaname, tablename,
         pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
  FROM pg_tables
  WHERE schemaname IN ('thegrantscout', 'staging_archive')
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
  ```

**Deliverable:** 50% database size reduction, cleaner schema

---

### Day 5: Create Missing Indexes (1 hour)

#### Matches Table (Critical for Performance)
- [ ] Create indexes
  ```sql
  CREATE INDEX idx_matches_nonprofit ON matches(nonprofit_ein);
  CREATE INDEX idx_matches_foundation ON matches(foundation_ein);
  CREATE INDEX idx_matches_score_desc ON matches(match_score DESC);
  CREATE INDEX idx_matches_status ON matches(status);
  CREATE INDEX idx_matches_date ON matches(match_date DESC);
  ```

#### Composite Indexes for Query Optimization
- [ ] Create composite indexes
  ```sql
  CREATE INDEX idx_foundations_state_ntee
    ON foundations(state, primary_ntee);

  CREATE INDEX idx_historical_grants_state_year
    ON historical_grants(recipient_state, tax_year);

  CREATE INDEX idx_historical_grants_funder_year
    ON historical_grants(foundation_ein, tax_year);
  ```

- [ ] Verify index creation
  ```sql
  SELECT schemaname, tablename, indexname, indexdef
  FROM pg_indexes
  WHERE tablename IN ('matches', 'foundations', 'historical_grants')
  ORDER BY tablename, indexname;
  ```

**Deliverable:** Optimized query performance for matching algorithm

---

## WEEK 2: MATCHING ENGINE (40 hours)

### Day 1-2: Tier 1 Matching - Direct Funders (16 hours)

#### Create Matching Functions
- [ ] Create SQL function for direct funder matching
  ```sql
  CREATE OR REPLACE FUNCTION match_tier1_direct_funders(
    p_nonprofit_ein TEXT,
    p_min_grant_count INT DEFAULT 1
  )
  RETURNS TABLE (
    foundation_ein TEXT,
    foundation_name TEXT,
    grant_count BIGINT,
    total_funded NUMERIC,
    avg_grant_size NUMERIC,
    last_grant_year INT,
    tier TEXT
  ) AS $$
  BEGIN
    RETURN QUERY
    SELECT
      f.ein,
      f.name,
      COUNT(hg.id) as grant_count,
      SUM(hg.grant_amount) as total_funded,
      AVG(hg.grant_amount) as avg_grant_size,
      MAX(hg.tax_year) as last_grant_year,
      'TIER_1_DIRECT'::TEXT as tier
    FROM foundations f
    JOIN historical_grants hg ON f.ein = hg.foundation_ein
    WHERE hg.recipient_ein = p_nonprofit_ein
    GROUP BY f.ein, f.name
    HAVING COUNT(hg.id) >= p_min_grant_count
    ORDER BY grant_count DESC, total_funded DESC;
  END;
  $$ LANGUAGE plpgsql;
  ```

#### Create Python Matching Script
- [ ] Create `matching_engine/tier1_direct.py`
- [ ] Implement:
  - Database connection
  - Call match_tier1_direct_funders function
  - Score results (frequency × recency × amount fit)
  - Generate match_reason JSONB
  - Insert into matches table

#### Test Tier 1
- [ ] Test with beta nonprofits
  ```sql
  SELECT * FROM match_tier1_direct_funders('XX-XXXXXXX', 1);
  ```
- [ ] Verify match quality
- [ ] Validate scoring logic

**Deliverable:** Working Tier 1 matching (direct historical funders)

---

### Day 3-4: Tier 2 Matching - Peer-Based (16 hours)

#### Create Peer Identification Function
- [ ] Create peer identification logic
  ```sql
  CREATE OR REPLACE FUNCTION identify_peers(
    p_nonprofit_ein TEXT,
    p_max_peers INT DEFAULT 50
  )
  RETURNS TABLE (
    peer_ein TEXT,
    peer_name TEXT,
    similarity_score NUMERIC
  ) AS $$
  BEGIN
    -- Match on NTEE code + state
    -- Score by budget similarity, program overlap
  END;
  $$ LANGUAGE plpgsql;
  ```

#### Create Peer-Based Funder Matching
- [ ] Create function to find funders who support ≥3 peers
  ```sql
  CREATE OR REPLACE FUNCTION match_tier2_peer_funders(
    p_nonprofit_ein TEXT,
    p_min_peer_support INT DEFAULT 3
  )
  RETURNS TABLE (
    foundation_ein TEXT,
    foundation_name TEXT,
    peer_support_count BIGINT,
    peer_overlap_score NUMERIC,
    tier TEXT
  ) AS $$
  -- Find funders who gave to multiple peer organizations
  END;
  $$ LANGUAGE plpgsql;
  ```

#### Implement Python Script
- [ ] Create `matching_engine/tier2_peers.py`
- [ ] Test with beta clients
- [ ] Validate peer identification accuracy

**Deliverable:** Tier 2 matching (funders supporting similar organizations)

---

### Day 5: Tier 3 Matching - Thematic/Geographic (8 hours)

#### Create Geographic Overlap Scoring
- [ ] Create function for state overlap analysis
  ```sql
  CREATE OR REPLACE FUNCTION calculate_geo_overlap(
    p_nonprofit_state TEXT,
    p_foundation_ein TEXT
  )
  RETURNS NUMERIC AS $$
  -- Calculate % of grants to nonprofit's state
  END;
  $$ LANGUAGE plpgsql;
  ```

#### Create Thematic Matching
- [ ] NTEE code similarity scoring
- [ ] Keyword matching in grant purposes
- [ ] Grant size fit analysis

#### Implement Python Script
- [ ] Create `matching_engine/tier3_thematic.py`
- [ ] Combine geographic + thematic scores
- [ ] Test and validate

**Deliverable:** Tier 3 matching (thematic and geographic fit)

---

## WEEK 3: SCRAPING AUTOMATION (20 hours)

### Day 1-2: Grants.gov Scraper (8 hours)

- [ ] Research Grants.gov API documentation
- [ ] Create `scrapers/grants_gov.py`
- [ ] Implement:
  - API authentication
  - Search filters (eligibility, categories)
  - Data extraction
  - current_grants table population
  - Deadline tracking

- [ ] Test scraper
  - [ ] Verify 200-500 grants extracted
  - [ ] Check data quality
  - [ ] Validate deadline parsing

- [ ] Schedule daily updates (cron job)

**Deliverable:** Automated Grants.gov opportunity ingestion

---

### Day 3-4: Foundation Website Scraper (8 hours)

- [ ] Identify top 500 foundations with online portals
- [ ] Create `scrapers/foundation_websites.py`
- [ ] Implement:
  - Selenium-based web scraping
  - Portal detection
  - Application deadline extraction
  - Contact information capture

- [ ] Prioritize foundations:
  - Large foundations (>$100M assets)
  - Hawaii-based foundations
  - Community foundations

- [ ] Schedule weekly updates

**Deliverable:** 100-300 foundation opportunities automated

---

### Day 5: State Portal Scraper (4 hours)

- [ ] Create `scrapers/state_portals.py`
- [ ] Target sources:
  - State CDBG programs (all 50 states)
  - Economic development grants
  - Recreation/facilities funding

- [ ] Test with priority states:
  - Hawaii
  - California
  - New York

**Deliverable:** 50-100 state/local opportunities automated

---

## WEEK 4: POLISH & TESTING (8 hours)

### Day 1: Foreign Key Constraints (2 hours)

- [ ] Add FK constraints
  ```sql
  ALTER TABLE matches
    ADD CONSTRAINT fk_matches_nonprofit
    FOREIGN KEY (nonprofit_ein) REFERENCES nonprofits(ein)
    ON DELETE CASCADE;

  ALTER TABLE matches
    ADD CONSTRAINT fk_matches_foundation
    FOREIGN KEY (foundation_ein) REFERENCES foundations(ein)
    ON DELETE CASCADE;

  ALTER TABLE historical_grants
    ADD CONSTRAINT fk_hgrants_foundation
    FOREIGN KEY (foundation_ein) REFERENCES foundations(ein)
    ON DELETE CASCADE;
  ```

- [ ] Verify constraints
  ```sql
  SELECT conname, conrelid::regclass, confrelid::regclass
  FROM pg_constraint
  WHERE contype = 'f'
  AND connamespace = 'thegrantscout'::regnamespace;
  ```

**Deliverable:** Referential integrity enforcement

---

### Day 2: Materialized Views (4 hours)

#### Create Top Funders View
- [ ] Create materialized view
  ```sql
  CREATE MATERIALIZED VIEW mv_top_funders_by_state AS
  SELECT
    state,
    ein,
    name,
    total_giving,
    total_grants_count,
    avg_grant_size,
    primary_ntee
  FROM foundations
  WHERE total_grants_count > 10
  ORDER BY state, total_giving DESC;

  CREATE INDEX idx_mv_top_funders_state
    ON mv_top_funders_by_state(state);
  ```

#### Create Grant Statistics View
- [ ] Create aggregate statistics view
  ```sql
  CREATE MATERIALIZED VIEW mv_grant_statistics AS
  SELECT
    foundation_ein,
    COUNT(*) as total_grants,
    SUM(grant_amount) as total_amount,
    AVG(grant_amount) as avg_amount,
    MIN(grant_amount) as min_amount,
    MAX(grant_amount) as max_amount,
    array_agg(DISTINCT recipient_state) as states_served
  FROM historical_grants
  GROUP BY foundation_ein;
  ```

- [ ] Schedule nightly refresh
  ```sql
  -- Add to cron: daily at 2am
  REFRESH MATERIALIZED VIEW mv_top_funders_by_state;
  REFRESH MATERIALIZED VIEW mv_grant_statistics;
  ```

**Deliverable:** Pre-computed views for common queries

---

### Day 3-5: End-to-End Testing (2 hours)

#### Test Complete Workflow
- [ ] Test nonprofit onboarding
  - [ ] Insert test nonprofit
  - [ ] Verify profile creation

- [ ] Test matching pipeline
  - [ ] Run Tier 1 matching
  - [ ] Run Tier 2 matching
  - [ ] Run Tier 3 matching
  - [ ] Verify 500-1000 matches generated
  - [ ] Check match quality and scoring

- [ ] Test current grants ingestion
  - [ ] Verify scrapers running
  - [ ] Check opportunity count (500-1000)
  - [ ] Validate deadline tracking

- [ ] Performance testing
  - [ ] Match generation time <5 minutes
  - [ ] Query response time <2 seconds
  - [ ] Database size optimized

**Deliverable:** Fully functional automated system

---

## COMPLETION CHECKLIST

### Data Foundation
- [ ] F990 import 100% complete (31 of 31 files)
- [ ] Array storage migrated (foundations.ntee_codes, program_areas)
- [ ] Redundant tables deleted (irs_bmf_eo1-4, emails_temp)
- [ ] Staging tables archived
- [ ] All indexes created

### Matching Engine
- [ ] Tier 1 matching implemented and tested
- [ ] Tier 2 matching implemented and tested
- [ ] Tier 3 matching implemented and tested
- [ ] Match scoring algorithm validated
- [ ] 500-1000 matches per client achievable

### Current Grants Automation
- [ ] Grants.gov scraper deployed
- [ ] Foundation website scraper deployed
- [ ] State portal scraper deployed
- [ ] 500-1000 active opportunities in database
- [ ] Daily/weekly update schedule configured

### Database Optimization
- [ ] Foreign key constraints added
- [ ] Materialized views created
- [ ] Query performance optimized
- [ ] 50% database size reduction achieved

### Testing & Documentation
- [ ] End-to-end workflow tested
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Handoff complete

---

## SUCCESS METRICS

**Before Round 2:**
- Historical Grants: 1.6M
- Current Opportunities: 42
- Clients Supported: 3 (manual)
- Match Generation: Hours (manual)

**After Round 2:**
- Historical Grants: 8-10M ✅
- Current Opportunities: 500-1000 ✅
- Clients Supported: 100 (automated) ✅
- Match Generation: <5 minutes (automated) ✅

**Database Quality:**
- Data Coverage: 100% ✅
- Schema Utilization: 75% ✅
- Storage Optimization: 50% reduction ✅
- Query Performance: <2 seconds ✅

---

## NEXT STEPS AFTER COMPLETION

1. **User Acceptance Testing**
   - Test with 5-10 new nonprofits
   - Validate match quality
   - Gather feedback

2. **Production Launch**
   - Deploy to production environment
   - Enable client onboarding
   - Monitor system performance

3. **Round 3 Planning**
   - Board member network analysis
   - Temporal pattern calculation
   - Learning loop implementation
   - AI-powered grant writing assistance

---

**Prepared By:** Research Team - Analyst Agent
**Date:** November 30, 2025
**Estimated Completion:** 2.5 weeks (100 hours)
**Status:** Ready to begin
