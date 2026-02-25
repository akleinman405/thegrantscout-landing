# fact_foundation_client_scores Column Reference

**Schema:** f990_2025
**Table:** fact_foundation_client_scores
**Rows:** 12,652
**Description:** LASSO model scores pairing each eligible foundation with each client, used to rank foundation-client fit.

---

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| foundation_ein | character varying(20) | NO | Foundation EIN. Part of composite primary key. |
| client_ein | character varying(20) | NO | Client EIN (matches dim_clients.ein). Part of composite primary key. |
| lasso_score | numeric | YES | Raw LASSO logit score (unbounded). Higher = better fit. Used for ranking instead of probability to avoid saturation at extremes. |
| probability | numeric | YES | Predicted probability of a positive match (0 to 1). Derived from lasso_score via logistic function. |
| semantic_similarity | numeric | YES | Cosine similarity between client and foundation mission embeddings (0 to 1). Requires embedding regeneration since tables were archived 2026-01-04. |
| model_version | character varying(20) | YES | Model version that produced this score. Default: 'v6.1'. |
| calculated_at | timestamp without time zone | YES | When this score was computed. Default: now(). |

---

## Primary Key
- (`foundation_ein`, `client_ein`) -- Composite key, one score per foundation-client pair

## Foreign Keys
- `foundation_ein` -> `dim_foundations.ein` -- The scored foundation
- `client_ein` -> `dim_clients.ein` -- The client being matched

## Indexes
- See database for current indexes

## Notes
- The `lasso_score` (logit) is used for ranking, not `probability`. Logit scores spread out more at the extremes, giving better rank ordering among top candidates.
- Only foundations passing production filters are scored: has_grant_history = TRUE, assets >= $100K, unique_recipients >= 5, preselected_only = FALSE. This yields ~12,653 foundations.
- `semantic_similarity` may be NULL or stale since embedding tables were archived on 2026-01-04 to free 52GB disk space.
- The LASSO V6.1 model achieves test AUC of 0.94. See `3. Models/v6.1/REPORT_2026-01-03_v6.1_model_evaluation.md` for details.
- Model coefficients are stored in `4. Pipeline/config/coefficients.json`.
- Prior funders (from `dim_clients.known_funders`) are excluded from scoring results.
