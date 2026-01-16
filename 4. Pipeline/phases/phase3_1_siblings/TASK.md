# TASK: Phase 3.1 - Build calc_client_siblings

**Purpose:** Identify similar nonprofits (siblings) for the client
**When:** After Phase 2 (client understanding complete, target_grant_purpose set)
**Folder:** `phases/phase3_1_siblings/`

---

## Overview

Siblings are nonprofits with similar missions and comparable budgets. Foundations that funded siblings are likely to fund our client.

**Definition:**
- **Sibling** = Nonprofit with mission similarity >= 0.50 AND budget 0.2x-5.0x of client

**Output:** Populated `calc_client_siblings` table

---

## Prerequisites

Before running this phase:
- [ ] Client exists in `dim_clients` with `mission_text` populated
- [ ] Client has `database_revenue` set (for budget filtering)
- [ ] `emb_nonprofit_missions` table available (see Note below)

**Note on Embeddings:** The `emb_nonprofit_missions` table was archived 2026-01-04 to save disk space. If running a new report, you may need to restore from backup at `1. Database/4. Semantic Embeddings/archive/`. See `REPORT_2026-01-04.1_embeddings_archived.md` for restore instructions.

---

## Step 3.1.1: Find Siblings via Embedding Similarity

### Part A: Generate Client Embedding

**Instructions for Claude Code CLI:**

1. Get the client's mission text:
```sql
SELECT ein, name, mission_text, database_revenue
FROM f990_2025.dim_clients
WHERE ein = '[client_ein]';
```

2. Generate the 384-dimension embedding using Python:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
client_embedding = model.encode(client_mission_text)

# Save to temp file for SQL use
import numpy as np
with open('/tmp/client_embedding.txt', 'w') as f:
    f.write('[' + ','.join(str(x) for x in client_embedding) + ']')
```

### Part B: Find Similar Nonprofits

**Instructions for Claude Code CLI:**

1. Calculate budget bounds:
   - Lower bound = database_revenue * 0.2
   - Upper bound = database_revenue * 5.0

2. Run pgvector similarity search:
```sql
SELECT
    enm.ein as sibling_ein,
    nr.organization_name as sibling_name,
    nr.total_revenue as sibling_budget,
    ROUND((1.0 - (enm.mission_embedding_v <=> '[embedding]'::vector(384)))::NUMERIC, 4) as similarity
FROM f990_2025.emb_nonprofit_missions enm
JOIN f990_2025.nonprofit_returns nr ON enm.ein = nr.ein
WHERE nr.total_revenue BETWEEN [lower_bound] AND [upper_bound]
  AND enm.ein != '[client_ein]'
  AND (enm.mission_embedding_v <=> '[embedding]'::vector(384)) <= 0.50
ORDER BY similarity DESC
LIMIT 200;
```

3. Review top 10-20 results to validate relevance

### Part C: Populate calc_client_siblings

**Instructions for Claude Code CLI:**

1. Create table if not exists:
```sql
CREATE TABLE IF NOT EXISTS f990_2025.calc_client_siblings (
    client_ein      VARCHAR(9) NOT NULL,
    sibling_ein     VARCHAR(9) NOT NULL,
    similarity      NUMERIC(6,4) NOT NULL,
    client_budget   BIGINT,
    sibling_budget  BIGINT,
    budget_ratio    NUMERIC(5,2),
    model_version   VARCHAR(50) DEFAULT 'all-MiniLM-L6-v2',
    computed_at     TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (client_ein, sibling_ein)
);
```

2. Insert siblings:
```sql
INSERT INTO f990_2025.calc_client_siblings
    (client_ein, sibling_ein, similarity, client_budget, sibling_budget, budget_ratio)
SELECT
    '[client_ein]' as client_ein,
    enm.ein as sibling_ein,
    ROUND((1.0 - (enm.mission_embedding_v <=> '[embedding]'::vector(384)))::NUMERIC, 4) as similarity,
    [client_budget] as client_budget,
    nr.total_revenue as sibling_budget,
    ROUND((nr.total_revenue::numeric / [client_budget]::numeric), 2) as budget_ratio
FROM f990_2025.emb_nonprofit_missions enm
JOIN f990_2025.nonprofit_returns nr ON enm.ein = nr.ein
WHERE nr.total_revenue BETWEEN [lower_bound] AND [upper_bound]
  AND enm.ein != '[client_ein]'
  AND (enm.mission_embedding_v <=> '[embedding]'::vector(384)) <= 0.50
ON CONFLICT (client_ein, sibling_ein) DO UPDATE SET
    similarity = EXCLUDED.similarity,
    sibling_budget = EXCLUDED.sibling_budget,
    budget_ratio = EXCLUDED.budget_ratio,
    computed_at = NOW();
```

---

## Quality Checks

- [ ] At least 30 siblings identified (if fewer, consider lowering threshold to 0.45)
- [ ] Top 10 siblings are relevant (spot-check mission statements)
- [ ] Budget ratios are within 0.2x-5.0x range
- [ ] No self-match (client EIN not in siblings)

**Verification Query:**
```sql
SELECT
    COUNT(*) as total_siblings,
    ROUND(AVG(similarity)::numeric, 3) as avg_similarity,
    ROUND(MIN(similarity)::numeric, 3) as min_similarity,
    ROUND(MAX(similarity)::numeric, 3) as max_similarity,
    ROUND(AVG(budget_ratio)::numeric, 2) as avg_budget_ratio
FROM f990_2025.calc_client_siblings
WHERE client_ein = '[client_ein]';
```

---

## PSMF Example Results

| Metric | Value |
|--------|-------|
| Total siblings | 91 |
| Avg similarity | 0.519 |
| Min similarity | 0.501 |
| Max similarity | 0.610 |
| Budget range | $73K - $1.8M (0.2x-5.0x of $365K) |

**Sample Siblings:**
- Healthcare education nonprofits
- Patient safety organizations
- Clinical training programs
- Medical fellowship programs

---

## Technical Notes

- **Embedding model:** all-MiniLM-L6-v2 (384 dimensions)
- **Distance operator:** `<=>` (pgvector cosine distance)
- **Similarity calculation:** `1.0 - cosine_distance` (so higher = more similar)
- **Threshold:** >= 0.50 (adjust if too few/many results)

---

*Task file created 2026-01-13*
