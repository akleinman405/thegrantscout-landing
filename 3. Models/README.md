# Matching Algorithm Models

This folder contains versioned foundation-nonprofit matching models.

## Current Version: V6.1

**Symlink:** `current/` → `v6.1/`

| Metric | Value |
|--------|-------|
| Model Type | LASSO Logistic Regression |
| Test AUC | 0.9421 |
| Training Data | 1.31M rows (size-matched negatives) |
| Foundations Available | 12,653 (after filters) |

### How It Works

The model predicts P(foundation funds nonprofit) using:

1. **Geographic match** - Foundation's historical state/region giving patterns
2. **Sector match** - Foundation's historical NTEE sector giving patterns
3. **Semantic similarity** - Cosine similarity between mission embeddings
4. **Foundation activity** - Grant volume, asset size
5. **Recipient characteristics** - Revenue, sector

See `v6.1/REPORT_2026-01-03_v6.1_model_evaluation.md` for full documentation.

## Version History

| Version | Date | AUC | Key Changes |
|---------|------|-----|-------------|
| v6.1 | 2026-01-03 | 0.94 | Size-matched negatives, fixed semantic similarity sign |
| v6 | 2026-01-02 | 0.98 | Overfitting due to size confounding |
| v5 | 2025-12-30 | 0.91 | Added semantic similarity (wrong sign) |

## Folder Structure

```
models/
├── current -> v6.1/          # Symlink to production version
├── v6.1/                     # Current production model
│   ├── model/                # Trained artifacts
│   │   ├── coefficients.json # Model coefficients
│   │   ├── scaling.json      # Feature scaling parameters
│   │   ├── roc_curve.png     # Performance visualization
│   │   └── ...
│   ├── feature_list.txt      # Features used
│   └── REPORT_*.md           # Model documentation
├── v6/                       # Previous version (archived)
├── v5/                       # Earlier version (archived)
└── archive/
    └── exploration/          # Early algorithm R&D
```

## Using the Model

```python
from pipeline.scripts.utils.scorer import score_foundations

# Load model from current version
results = score_foundations(
    client_profile=client,
    model_dir='models/current/model',
    top_k=100
)
```

## Training Data Location

Large training CSVs (500MB+) are stored in original location:
`5. TheGrantScout - Pipeline/Pipeline v2/outputs/v*/`

These are excluded from git due to size.

---

*Part of Cookie Cutter Data Science reorganization - 2026-01-04*
