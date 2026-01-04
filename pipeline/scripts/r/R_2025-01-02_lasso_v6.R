# R_2025-01-02_lasso_v6.R
# Train LASSO V6 model with cleaned features
#
# Key changes from V5:
# - Training on first-time grants only (same as V5)
# - REMOVED leaky features (r_total_grants, r_total_funders, r_total_funding)
# - REMOVED multicollinear features (r_assets, r_employee_count, r_size_*)
# - ADDED semantic similarity and org age features
# - Expected: All coefficients should have intuitive signs
#
# Usage:
#   Rscript scripts/r/R_2025-01-02_lasso_v6.R
#
# Prerequisites:
#   - Run PY_2025-01-02_v6_foundation_embeddings.py
#   - Run SQL_2025-01-02_v6_training_data.sql
#   - Run PY_2025-01-02_v6_export_training.py

library(glmnet)
library(pROC)
library(ggplot2)
library(jsonlite)

# ============================================================================
# Configuration
# ============================================================================

BASE_DIR <- "/Users/aleckleinman/Documents/TheGrantScout/5. TheGrantScout - Pipeline/Pipeline v2"
INPUT_DIR <- file.path(BASE_DIR, "outputs/v6")
OUTPUT_DIR <- file.path(BASE_DIR, "outputs/v6/model")

# Create output directory
dir.create(OUTPUT_DIR, recursive = TRUE, showWarnings = FALSE)

cat("=" , rep("=", 59), "\n", sep = "")
cat("LASSO V6 Model Training\n")
cat("Cleaned features, no leakage, semantic similarity\n")
cat("=" , rep("=", 59), "\n\n", sep = "")

# ============================================================================
# Load Data
# ============================================================================

cat("Loading data...\n")

train <- read.csv(file.path(INPUT_DIR, "train.csv"))
validation <- read.csv(file.path(INPUT_DIR, "validation.csv"))
test <- read.csv(file.path(INPUT_DIR, "test.csv"))

cat(sprintf("  Train:      %s rows (%.1f%% positive)\n",
            format(nrow(train), big.mark = ","),
            mean(train$label) * 100))
cat(sprintf("  Validation: %s rows (%.1f%% positive)\n",
            format(nrow(validation), big.mark = ","),
            mean(validation$label) * 100))
cat(sprintf("  Test:       %s rows (%.1f%% positive)\n",
            format(nrow(test), big.mark = ","),
            mean(test$label) * 100))

# ============================================================================
# Prepare Features
# ============================================================================

cat("\nPreparing features...\n")

# Identify feature columns (exclude label and tax_year)
exclude_cols <- c("label", "tax_year")
feature_cols <- setdiff(names(train), exclude_cols)

cat(sprintf("  Features: %d\n", length(feature_cols)))

# Create matrices
X_train <- as.matrix(train[, feature_cols])
y_train <- train$label

X_val <- as.matrix(validation[, feature_cols])
y_val <- validation$label

X_test <- as.matrix(test[, feature_cols])
y_test <- test$label

# Handle any remaining NAs
X_train[is.na(X_train)] <- 0
X_val[is.na(X_val)] <- 0
X_test[is.na(X_test)] <- 0

# Scale features (z-score)
cat("  Scaling features...\n")
train_means <- colMeans(X_train)
train_sds <- apply(X_train, 2, sd)
train_sds[train_sds == 0] <- 1  # Avoid division by zero

X_train_scaled <- scale(X_train, center = train_means, scale = train_sds)
X_val_scaled <- scale(X_val, center = train_means, scale = train_sds)
X_test_scaled <- scale(X_test, center = train_means, scale = train_sds)

# ============================================================================
# Train LASSO with Cross-Validation
# ============================================================================

cat("\nTraining LASSO with 5-fold CV...\n")

set.seed(42)

cv_fit <- cv.glmnet(
  X_train_scaled, y_train,
  family = "binomial",
  alpha = 1,  # LASSO
  nfolds = 5,
  type.measure = "auc",
  standardize = FALSE,  # Already standardized
  parallel = FALSE,
  trace.it = 1  # Show progress
)

cat(sprintf("  Best lambda: %.6f\n", cv_fit$lambda.min))
cat(sprintf("  CV AUC: %.4f\n", max(cv_fit$cvm)))

# Save CV plot
png(file.path(OUTPUT_DIR, "cv_lambda_plot.png"), width = 800, height = 600)
plot(cv_fit, main = "LASSO V6 Cross-Validation")
dev.off()

# ============================================================================
# Extract Coefficients
# ============================================================================

cat("\nExtracting coefficients...\n")

coef_matrix <- coef(cv_fit, s = "lambda.min")
coef_df <- data.frame(
  feature = rownames(coef_matrix),
  coefficient = as.vector(coef_matrix),
  stringsAsFactors = FALSE
)

# Separate intercept
intercept <- coef_df$coefficient[coef_df$feature == "(Intercept)"]
coef_df <- coef_df[coef_df$feature != "(Intercept)", ]

# Sort by absolute value
coef_df$abs_coefficient <- abs(coef_df$coefficient)
coef_df <- coef_df[order(-coef_df$abs_coefficient), ]

# Non-zero coefficients
nonzero <- coef_df[coef_df$coefficient != 0, ]
cat(sprintf("  Non-zero coefficients: %d of %d\n", nrow(nonzero), nrow(coef_df)))

# ============================================================================
# KEY CHECKS: Verify Intuitive Coefficient Signs
# ============================================================================

cat("\n", rep("=", 60), "\n", sep = "")
cat("KEY COEFFICIENT CHECKS (V6 Validation)\n")
cat(rep("=", 60), "\n", sep = "")

# Define expected signs for key features
expected_signs <- list(
  "f_openness_score" = "positive",
  "match_same_state" = "positive",
  "match_state_pct" = "positive",
  "match_sector_pct" = "positive",
  "match_semantic_similarity" = "positive",
  "f_is_accessible" = "positive",
  "f_funded_new_recently" = "positive",
  "f_is_growing" = "positive",
  "f_first_time_rate" = "positive",
  "f_one_time_rate" = "positive",
  "f_is_recently_active" = "positive",
  "r_total_revenue" = "positive",
  "r_log_total_revenue" = "positive",
  "r_org_age" = "positive",
  "f_sector_hhi" = "negative",  # Concentrated = less likely for new
  "f_is_declining" = "negative"  # Declining foundations less likely
)

all_pass <- TRUE
for (feat in names(expected_signs)) {
  expected <- expected_signs[[feat]]
  coef_val <- coef_df$coefficient[coef_df$feature == feat]

  if (length(coef_val) > 0 && coef_val != 0) {
    actual <- if (coef_val > 0) "positive" else "negative"
    status <- if (actual == expected) "PASS" else "FAIL"
    if (status == "FAIL") all_pass <- FALSE

    cat(sprintf("  %-30s: %+.4f (%s) [expected %s] %s\n",
                feat, coef_val, actual, expected, status))
  } else {
    cat(sprintf("  %-30s: 0 (zeroed out by LASSO)\n", feat))
  }
}

if (all_pass) {
  cat("\n*** ALL KEY COEFFICIENTS HAVE EXPECTED SIGNS! ***\n")
} else {
  cat("\n*** WARNING: Some coefficients have unexpected signs ***\n")
}

# Check that leaky features are NOT present
cat("\nVerifying removed features are not in model:\n")
removed_features <- c("r_total_grants", "r_total_funders", "r_total_funding",
                     "r_assets", "r_employee_count")
for (feat in removed_features) {
  if (feat %in% coef_df$feature) {
    cat(sprintf("  ERROR: %s should not be in V6 model!\n", feat))
  } else {
    cat(sprintf("  OK: %s not in model\n", feat))
  }
}

# ============================================================================
# Evaluate on Validation Set
# ============================================================================

cat("\n", rep("=", 60), "\n", sep = "")
cat("VALIDATION SET PERFORMANCE\n")
cat(rep("=", 60), "\n", sep = "")

pred_val <- predict(cv_fit, X_val_scaled, s = "lambda.min", type = "response")
roc_val <- roc(y_val, as.vector(pred_val), quiet = TRUE)

cat(sprintf("  AUC: %.4f\n", auc(roc_val)))

# Confusion matrix at 0.5 threshold
pred_class <- ifelse(pred_val > 0.5, 1, 0)
accuracy <- mean(pred_class == y_val)
precision <- sum(pred_class == 1 & y_val == 1) / max(sum(pred_class == 1), 1)
recall <- sum(pred_class == 1 & y_val == 1) / max(sum(y_val == 1), 1)
f1 <- 2 * precision * recall / max(precision + recall, 0.001)

cat(sprintf("  Accuracy:  %.4f\n", accuracy))
cat(sprintf("  Precision: %.4f\n", precision))
cat(sprintf("  Recall:    %.4f\n", recall))
cat(sprintf("  F1:        %.4f\n", f1))

# ============================================================================
# Evaluate on Test Set
# ============================================================================

cat("\n", rep("=", 60), "\n", sep = "")
cat("TEST SET PERFORMANCE\n")
cat(rep("=", 60), "\n", sep = "")

pred_test <- predict(cv_fit, X_test_scaled, s = "lambda.min", type = "response")
roc_test <- roc(y_test, as.vector(pred_test), quiet = TRUE)

cat(sprintf("  AUC: %.4f\n", auc(roc_test)))

pred_class_test <- ifelse(pred_test > 0.5, 1, 0)
accuracy_test <- mean(pred_class_test == y_test)
precision_test <- sum(pred_class_test == 1 & y_test == 1) / max(sum(pred_class_test == 1), 1)
recall_test <- sum(pred_class_test == 1 & y_test == 1) / max(sum(y_test == 1), 1)
f1_test <- 2 * precision_test * recall_test / max(precision_test + recall_test, 0.001)

cat(sprintf("  Accuracy:  %.4f\n", accuracy_test))
cat(sprintf("  Precision: %.4f\n", precision_test))
cat(sprintf("  Recall:    %.4f\n", recall_test))
cat(sprintf("  F1:        %.4f\n", f1_test))

# ============================================================================
# Save Outputs
# ============================================================================

cat("\nSaving outputs...\n")

# 1. All coefficients (CSV)
coef_df$direction <- ifelse(coef_df$coefficient > 0, "positive",
                           ifelse(coef_df$coefficient < 0, "negative", "zero"))
write.csv(coef_df, file.path(OUTPUT_DIR, "coefficients_all.csv"), row.names = FALSE)

# 2. Non-zero coefficients (CSV)
write.csv(nonzero, file.path(OUTPUT_DIR, "coefficients_nonzero.csv"), row.names = FALSE)

# 3. Scaling parameters (CSV)
scaling_df <- data.frame(
  feature = feature_cols,
  mean = train_means,
  sd = train_sds
)
write.csv(scaling_df, file.path(OUTPUT_DIR, "scaling_parameters.csv"), row.names = FALSE)

# 4. Coefficients JSON (for Pipeline v2)
coef_json <- list(
  intercept = intercept,
  coefficients = setNames(as.list(nonzero$coefficient), nonzero$feature)
)
write_json(coef_json, file.path(OUTPUT_DIR, "coefficients.json"), pretty = TRUE, auto_unbox = TRUE)

# 5. Scaling JSON (for Pipeline v2)
scaling_json <- setNames(
  lapply(1:nrow(scaling_df), function(i) {
    list(mean = scaling_df$mean[i], sd = scaling_df$sd[i])
  }),
  scaling_df$feature
)
write_json(scaling_json, file.path(OUTPUT_DIR, "scaling.json"), pretty = TRUE, auto_unbox = TRUE)

# 6. Metrics summary
metrics_df <- data.frame(
  metric = c("val_auc", "val_accuracy", "val_precision", "val_recall", "val_f1",
             "test_auc", "test_accuracy", "test_precision", "test_recall", "test_f1",
             "cv_auc", "intercept", "n_features_nonzero", "n_features_total"),
  value = c(auc(roc_val), accuracy, precision, recall, f1,
            auc(roc_test), accuracy_test, precision_test, recall_test, f1_test,
            max(cv_fit$cvm), intercept, nrow(nonzero), nrow(coef_df))
)
write.csv(metrics_df, file.path(OUTPUT_DIR, "metrics_summary.csv"), row.names = FALSE)

# 7. ROC curve plot
png(file.path(OUTPUT_DIR, "roc_curve.png"), width = 800, height = 600)
plot(roc_test, main = sprintf("LASSO V6 ROC Curve (Test AUC = %.3f)", auc(roc_test)),
     col = "blue", lwd = 2)
abline(a = 0, b = 1, lty = 2, col = "gray")
dev.off()

# 8. Score distribution
png(file.path(OUTPUT_DIR, "score_distribution.png"), width = 800, height = 600)
hist(pred_test, breaks = 50, main = "V6 Score Distribution (Test Set)",
     xlab = "Predicted Probability", col = "steelblue")
dev.off()

# ============================================================================
# Top 20 Coefficients
# ============================================================================

cat("\n", rep("=", 60), "\n", sep = "")
cat("TOP 20 COEFFICIENTS BY MAGNITUDE\n")
cat(rep("=", 60), "\n", sep = "")

top20 <- head(nonzero, 20)
for (i in 1:nrow(top20)) {
  cat(sprintf("  %2d. %-35s %+.4f\n", i, top20$feature[i], top20$coefficient[i]))
}

# ============================================================================
# V5 vs V6 Comparison
# ============================================================================

cat("\n", rep("=", 60), "\n", sep = "")
cat("V6 vs V5 COMPARISON\n")
cat(rep("=", 60), "\n", sep = "")

cat("\nKey improvements in V6:\n")
cat("  1. Removed r_total_grants, r_total_funders, r_total_funding (leakage)\n")
cat("  2. Removed r_assets, r_employee_count (multicollinear)\n")
cat("  3. Removed r_size_* dummies (redundant)\n")
cat("  4. Added match_semantic_similarity\n")
cat("  5. Added r_org_age, r_is_emerging\n")
cat("  6. Added f_is_accessible, f_is_small\n")
cat("  7. Added match_same_region, match_same_division\n")

# ============================================================================
# Summary
# ============================================================================

cat("\n", rep("=", 60), "\n", sep = "")
cat("SUMMARY\n")
cat(rep("=", 60), "\n", sep = "")

cat(sprintf("  Model:              LASSO V6 (cleaned features)\n"))
cat(sprintf("  Training samples:   %s\n", format(nrow(train), big.mark = ",")))
cat(sprintf("  Features:           %d (%d non-zero)\n", length(feature_cols), nrow(nonzero)))
cat(sprintf("  Validation AUC:     %.4f\n", auc(roc_val)))
cat(sprintf("  Test AUC:           %.4f\n", auc(roc_test)))
cat(sprintf("  Intercept:          %.4f\n", intercept))

cat("\nOutput files:\n")
cat(sprintf("  %s/coefficients.json\n", OUTPUT_DIR))
cat(sprintf("  %s/scaling.json\n", OUTPUT_DIR))
cat(sprintf("  %s/metrics_summary.csv\n", OUTPUT_DIR))
cat(sprintf("  %s/roc_curve.png\n", OUTPUT_DIR))

cat("\nNext steps:\n")
cat("  1. Review coefficient signs - all should be intuitive\n")
cat("  2. Compare V6 AUC to V5 AUC (0.969) - acceptable if > 0.90\n")
cat("  3. Copy coefficients.json and scaling.json to Pipeline v2/config/\n")
cat("  4. Update 02_score_foundations.py to use V6 features\n")
cat("  5. Test on Ka Ulukoa and PSMF\n")

cat("\n", rep("=", 60), "\n", sep = "")
cat("Done!\n")
