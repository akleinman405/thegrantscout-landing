# PROMPT: Phase 3 Operational Tables Build

**Date:** 2025-12-10  
**For:** Claude Code CLI  
**Schema:** f990_2025  
**Depends On:** Phase 1 (dim tables), Phase 2 (calc tables), matching algorithm script

---

## Context

The matching algorithm outputs JSON files. We need database tables to:
1. Store match results (don't re-run algorithm every time)
2. Track Scout/Validator review decisions
3. Record what was delivered to clients
4. Capture client feedback to improve algorithm

---

## Table 1: match_runs

Log of each algorithm execution.

```sql
CREATE TABLE f990_2025.match_runs (
    id SERIAL PRIMARY KEY,
    
    -- What was matched
    client_id INT REFERENCES f990_2025.dim_clients(id),
    
    -- Run metadata
    run_type VARCHAR(20) DEFAULT 'full',  -- 'full', 'incremental', 'test'
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',  -- 'running', 'completed', 'failed'
    
    -- Algorithm parameters (for reproducibility)
    params JSONB,  -- {"min_openness": 0.1, "min_grants": 5, "weights": {...}}
    
    -- Results summary
    candidates_evaluated INT,
    matches_generated INT,
    
    -- Version tracking
    algorithm_version VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_match_runs_client ON f990_2025.match_runs(client_id);
CREATE INDEX idx_match_runs_status ON f990_2025.match_runs(status);
```

---

## Table 2: match_results

Individual foundation matches from each run.

```sql
CREATE TABLE f990_2025.match_results (
    id SERIAL PRIMARY KEY,
    
    -- Links
    run_id INT NOT NULL REFERENCES f990_2025.match_runs(id),
    client_id INT NOT NULL REFERENCES f990_2025.dim_clients(id),
    foundation_ein VARCHAR(10) NOT NULL REFERENCES f990_2025.dim_foundations(ein),
    
    -- Ranking
    rank INT NOT NULL,
    score DECIMAL(5,4) NOT NULL,  -- 0.0000 to 1.0000
    
    -- Score breakdown
    score_semantic DECIMAL(5,4),
    score_collaborative DECIMAL(5,4),
    score_openness DECIMAL(5,4),
    score_geographic DECIMAL(5,4),
    score_sector DECIMAL(5,4),
    score_size_fit DECIMAL(5,4),
    
    -- Foundation snapshot (denormalized for historical record)
    foundation_name VARCHAR(255),
    foundation_state VARCHAR(2),
    foundation_assets BIGINT,
    foundation_median_grant INT,
    foundation_grants_5yr INT,
    foundation_openness DECIMAL(3,2),
    foundation_website VARCHAR(500),
    
    -- Evidence
    evidence_grants JSONB,  -- Top 5 similar grants with purpose, amount, year
    
    -- Review status
    review_status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'approved', 'rejected', 'maybe'
    reviewed_by VARCHAR(50),  -- 'scout', 'validator', 'auto'
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    
    -- Delivery status
    included_in_report BOOLEAN DEFAULT FALSE,
    report_id INT,  -- FK added after client_reports created
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_match_results_run ON f990_2025.match_results(run_id);
CREATE INDEX idx_match_results_client ON f990_2025.match_results(client_id);
CREATE INDEX idx_match_results_foundation ON f990_2025.match_results(foundation_ein);
CREATE INDEX idx_match_results_score ON f990_2025.match_results(client_id, score DESC);
CREATE INDEX idx_match_results_review ON f990_2025.match_results(review_status);
```

---

## Table 3: match_reviews

Detailed review history (allows multiple reviews per match).

```sql
CREATE TABLE f990_2025.match_reviews (
    id SERIAL PRIMARY KEY,
    
    match_result_id INT NOT NULL REFERENCES f990_2025.match_results(id),
    
    -- Review details
    reviewer_role VARCHAR(20) NOT NULL,  -- 'scout', 'validator', 'client'
    reviewer_name VARCHAR(100),
    
    -- Decision
    decision VARCHAR(20) NOT NULL,  -- 'approve', 'reject', 'escalate', 'needs_research'
    confidence VARCHAR(20),  -- 'high', 'medium', 'low'
    
    -- Reasoning
    rejection_reason VARCHAR(100),  -- 'inactive', 'wrong_sector', 'too_small', 'no_applications', etc.
    notes TEXT,
    
    -- Research findings (Scout adds this)
    website_status VARCHAR(20),  -- 'active', 'down', 'no_grants_page', 'applications_closed'
    recent_990_year INT,  -- Most recent 990 found
    application_info TEXT,  -- LOI process, deadlines, contact info
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_match_reviews_result ON f990_2025.match_reviews(match_result_id);
CREATE INDEX idx_match_reviews_decision ON f990_2025.match_reviews(decision);
```

---

## Table 4: client_reports

Reports delivered to clients.

```sql
CREATE TABLE f990_2025.client_reports (
    id SERIAL PRIMARY KEY,
    
    client_id INT NOT NULL REFERENCES f990_2025.dim_clients(id),
    
    -- Report metadata
    report_type VARCHAR(20) DEFAULT 'weekly',  -- 'weekly', 'monthly', 'custom'
    report_period_start DATE,
    report_period_end DATE,
    
    -- Content
    title VARCHAR(255),
    summary TEXT,
    opportunities_count INT,
    
    -- Delivery
    delivery_method VARCHAR(20),  -- 'email', 'pdf', 'portal'
    delivered_at TIMESTAMP,
    delivered_to VARCHAR(255),  -- email address
    
    -- File reference
    file_path VARCHAR(500),  -- Path to generated PDF/doc
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',  -- 'draft', 'review', 'delivered', 'archived'
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_client_reports_client ON f990_2025.client_reports(client_id);
CREATE INDEX idx_client_reports_delivered ON f990_2025.client_reports(delivered_at DESC);

-- Add FK from match_results to client_reports
ALTER TABLE f990_2025.match_results 
ADD CONSTRAINT fk_match_results_report 
FOREIGN KEY (report_id) REFERENCES f990_2025.client_reports(id);
```

---

## Table 5: match_feedback

Client feedback on recommendations (closes the learning loop).

```sql
CREATE TABLE f990_2025.match_feedback (
    id SERIAL PRIMARY KEY,
    
    match_result_id INT NOT NULL REFERENCES f990_2025.match_results(id),
    client_id INT NOT NULL REFERENCES f990_2025.dim_clients(id),
    foundation_ein VARCHAR(10) NOT NULL,
    
    -- Feedback type
    feedback_type VARCHAR(20) NOT NULL,  -- 'rating', 'application', 'outcome'
    
    -- Rating feedback (1-5 scale)
    relevance_rating INT CHECK (relevance_rating BETWEEN 1 AND 5),
    fit_rating INT CHECK (fit_rating BETWEEN 1 AND 5),
    
    -- Application feedback
    applied BOOLEAN,
    applied_date DATE,
    application_type VARCHAR(50),  -- 'loi', 'full_proposal', 'online_form'
    
    -- Outcome feedback (the gold - did they get funded?)
    outcome VARCHAR(20),  -- 'funded', 'declined', 'pending', 'no_response'
    outcome_date DATE,
    amount_requested BIGINT,
    amount_awarded BIGINT,
    
    -- Qualitative
    comments TEXT,
    would_apply_again BOOLEAN,
    
    -- Meta
    feedback_source VARCHAR(20),  -- 'survey', 'email', 'call', 'portal'
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_match_feedback_result ON f990_2025.match_feedback(match_result_id);
CREATE INDEX idx_match_feedback_client ON f990_2025.match_feedback(client_id);
CREATE INDEX idx_match_feedback_outcome ON f990_2025.match_feedback(outcome);
CREATE INDEX idx_match_feedback_foundation ON f990_2025.match_feedback(foundation_ein);
```

---

## Views for Common Queries

### Active Matches Awaiting Review

```sql
CREATE VIEW f990_2025.v_pending_reviews AS
SELECT 
    mr.id,
    c.name as client_name,
    mr.foundation_name,
    mr.rank,
    mr.score,
    mr.review_status,
    mr.created_at
FROM f990_2025.match_results mr
JOIN f990_2025.dim_clients c ON mr.client_id = c.id
WHERE mr.review_status = 'pending'
ORDER BY mr.created_at, mr.client_id, mr.rank;
```

### Match Success Rate by Algorithm Version

```sql
CREATE VIEW f990_2025.v_algorithm_performance AS
SELECT 
    run.algorithm_version,
    COUNT(DISTINCT mf.id) as total_feedback,
    AVG(mf.relevance_rating) as avg_relevance,
    COUNT(*) FILTER (WHERE mf.applied = TRUE) as applications,
    COUNT(*) FILTER (WHERE mf.outcome = 'funded') as funded,
    ROUND(100.0 * COUNT(*) FILTER (WHERE mf.outcome = 'funded') / 
          NULLIF(COUNT(*) FILTER (WHERE mf.applied = TRUE), 0), 1) as success_rate
FROM f990_2025.match_runs run
JOIN f990_2025.match_results mr ON run.id = mr.run_id
LEFT JOIN f990_2025.match_feedback mf ON mr.id = mf.match_result_id
GROUP BY run.algorithm_version;
```

---

## Validation Queries

```sql
-- 1. Table row counts
SELECT 'match_runs' as tbl, COUNT(*) FROM f990_2025.match_runs
UNION ALL SELECT 'match_results', COUNT(*) FROM f990_2025.match_results
UNION ALL SELECT 'match_reviews', COUNT(*) FROM f990_2025.match_reviews
UNION ALL SELECT 'client_reports', COUNT(*) FROM f990_2025.client_reports
UNION ALL SELECT 'match_feedback', COUNT(*) FROM f990_2025.match_feedback;

-- 2. Review status distribution
SELECT review_status, COUNT(*) 
FROM f990_2025.match_results 
GROUP BY review_status;

-- 3. Feedback coverage
SELECT 
    (SELECT COUNT(*) FROM f990_2025.match_results WHERE included_in_report = TRUE) as delivered,
    (SELECT COUNT(*) FROM f990_2025.match_feedback) as with_feedback,
    ROUND(100.0 * 
        (SELECT COUNT(*) FROM f990_2025.match_feedback) /
        NULLIF((SELECT COUNT(*) FROM f990_2025.match_results WHERE included_in_report = TRUE), 0)
    , 1) as feedback_rate;
```

---

## Output

1. SQL script creating all 5 tables + 2 views
2. Verify foreign keys work correctly
3. Brief report confirming creation
