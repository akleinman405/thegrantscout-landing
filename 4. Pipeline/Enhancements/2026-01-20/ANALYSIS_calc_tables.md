# calc_ Tables Analysis

## Current State: 10 Tables, ~1.4 GB Total

### Category 1: Client-Specific Pipeline Tables (small, regenerated per run)

| Table | Size | Rows | Purpose |
|-------|------|------|---------|
| `calc_client_siblings` | 4 MB | 2,067 | Nonprofits similar to client |
| `calc_client_sibling_grants` | 4.5 MB | 13,042 | Grants to client's siblings |
| `calc_client_sibling_funders` | 56 KB | 168 | Foundations that funded siblings |
| `calc_client_foundation_scores` | 1.6 MB | 4,673 | Scores for foundation-client pairs |
| `calc_client_foundation_recommendations` | 96 KB | ? | Final recommendations |
| `calc_client_proof_of_fit_grants` | 48 KB | ? | Evidence grants for positioning |

**Total: ~10 MB** - These are pipeline working tables, regenerated for each client.

### Category 2: Pre-Computed Features (large, computed once)

| Table | Size | Rows | Purpose |
|-------|------|------|---------|
| `calc_foundation_avg_embedding` | 803 MB | 112,481 | Average embedding per foundation (for semantic similarity) |
| `calc_recipient_features` | 444 MB | 1,652,766 | ML features for recipients |
| `calc_foundation_features` | 92 MB | 143,184 | ML features for foundations |
| `calc_foundation_profiles` | 51 MB | 143,184 | Behavioral metrics for foundations |

**Total: ~1.39 GB** - Pre-computed for performance.

---

## Questions for Review

1. **calc_foundation_features vs calc_foundation_profiles** - Both have 143K rows (one per foundation). Are they redundant?

2. **calc_foundation_avg_embedding** (803 MB) - Used for semantic similarity. Is this still needed given embeddings were archived?

3. **calc_recipient_features** (444 MB) - ML features for recipients. Is this used in the current pipeline?

4. **Client tables** - Should these be kept between runs or recreated fresh each time?

---

## Column Comparison: foundation_features vs foundation_profiles

### calc_foundation_profiles (22 columns)
- ein, has_grant_history, total_grants_all_time, total_grants_5yr, total_giving_5yr
- unique_recipients_5yr, last_active_year, median_grant, avg_grant
- grant_range_min, grant_range_max, openness_score, repeat_rate
- new_recipients_5yr, geographic_focus, sector_focus, project_types
- typical_recipient_size, giving_trend, trend_pct_change
- accepts_applications, calculated_at

### calc_foundation_features (93 columns)
Everything in profiles PLUS:
- Financial ratios (payout_rate, expense_ratio, investment_income_ratio)
- Year-over-year changes (yoy_asset_change, yoy_giving_change)
- Officer data (officer_count, total_compensation, avg_compensation)
- Grant statistics (stddev_grant_amount, grant_25th_pct, grant_75th_pct)
- Sector analysis (primary_sector, primary_sector_pct)
- Purpose quality (good_purpose_pct, poor_purpose_pct)

**Conclusion**: calc_foundation_profiles is a SUBSET of calc_foundation_features. Profiles exists for simpler queries/reports, features exists for ML.

