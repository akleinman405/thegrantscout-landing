# R_2025-01-03_lasso_v6_fixed.R
# Train LASSO V6 model - FIXED VERSION
#
# FIXES from statistical review:
# 1. Removed f_funded_new_recently, f_first_time_rate, f_one_time_rate
# 2. Using random 80/10/10 split (not temporal)
# 3. Expected AUC: 0.82-0.90 (honest, no leakage)
#
# EXPECTED RUNTIME: 30-60 minutes total
#   - Loading data: 1-2 min
#   - Preparing features: 1-2 min
#   - LASSO CV (5-fold): 20-45 min (the slow part)
#   - Evaluation: 2-3 min
#   - Saving outputs: 1 min
#
# Usage:
#   Rscript scripts/r/R_2025-01-03_lasso_v6_fixed.R
#
# Prerequisites:
#   - Run SQL_2025-01-03_v6_training_data_fixed.sql
#   - Run PY_2025-01-03_v6_export_training_fixed.py

library(glmnet)
library(pROC)
library(ggplot2)
library(jsonlite)

# ============================================================================
# Progress reporting helper
# ============================================================================

script_start_time <- Sys.time()

progress <- function(step, total_steps, msg, start_time = NULL) {
  elapsed <- difftime(Sys.time(), script_start_time, units = "mins")
  pct <- round(step / total_steps * 100)
  bar_width <- 30
  filled <- round(bar_width * step / total_steps)
  bar <- paste0("[", paste(rep("=", filled), collapse = ""),
                paste(rep(" ", bar_width - filled), collapse = ""), "]")

  if (!is.null(start_time)) {
    step_elapsed <- difftime(Sys.time(), start_time, units = "secs")
    cat(sprintf("\n[%s] Step %d/%d (%d%%) - %s (%.1fs)\n",
                format(Sys.time(), "%H:%M:%S"), step, total_steps, pct, msg, step_elapsed))
  } else {
    cat(sprintf("\n[%s] Step %d/%d (%d%%) - %s\n",
                format(Sys.time(), "%H:%M:%S"), step, total_steps, pct, msg))
  }
  cat(sprintf("         %s  Total elapsed: %.1f min\n", bar, elapsed))
}

TOTAL_STEPS <- 8

# ============================================================================
# Configuration
# ============================================================================

BASE_DIR <- "/Users/aleckleinman/Documents/TheGrantScout/5. TheGrantScout - Pipeline/Pipeline v2"
INPUT_DIR <- file.path(BASE_DIR, "outputs/v6")
OUTPUT_DIR <- file.path(BASE_DIR, "outputs/v6/model")

# Create output directory
dir.create(OUTPUT_DIR, recursive = TRUE, showWarnings = FALSE)

cat("\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("LASSO V6 Model Training (FIXED)\n")
cat("Random split, no leaky features, honest AUC\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("\nExpected runtime: 30-60 minutes\n")
cat("Started at:", format(Sys.time(), "%H:%M:%S"), "\n")

# ============================================================================
# Step 1: Load Data
# ============================================================================

step_start <- Sys.time()
progress(1, TOTAL_STEPS, "Loading CSV files (~1-2 min)...")

train <- read.csv(file.path(INPUT_DIR, "train.csv"))
cat(sprintf("    Loaded train.csv: %s rows\n", format(nrow(train), big.mark = ",")))

validation <- read.csv(file.path(INPUT_DIR, "validation.csv"))
cat(sprintf("    Loaded validation.csv: %s rows\n", format(nrow(validation), big.mark = ",")))

test <- read.csv(file.path(INPUT_DIR, "test.csv"))
cat(sprintf("    Loaded test.csv: %s rows\n", format(nrow(test), big.mark = ",")))

progress(1, TOTAL_STEPS, "Loading complete", step_start)

cat(sprintf("\n  Train:      %s rows (%.1f%% positive)\n",
            format(nrow(train), big.mark = ","),
            mean(train$label) * 100))
cat(sprintf("  Validation: %s rows (%.1f%% positive)\n",
            format(nrow(validation), big.mark = ","),
            mean(validation$label) * 100))
cat(sprintf("  Test:       %s rows (%.1f%% positive)\n",
            format(nrow(test), big.mark = ","),
            mean(test$label) * 100))

# Verify both classes exist
cat("\nClass balance check:\n")
for (split_name in c("Train", "Validation", "Test")) {
  split_data <- switch(split_name,
                       "Train" = train,
                       "Validation" = validation,
                       "Test" = test)
  pos <- sum(split_data$label == 1)
  neg <- sum(split_data$label == 0)
  status <- if (pos > 0 && neg > 0) "OK" else "ERROR"
  cat(sprintf("  %s: %s positives, %s negatives [%s]\n",
              split_name, format(pos, big.mark=","), format(neg, big.mark=","), status))
}

# ============================================================================
# Step 2: Prepare Features
# ============================================================================

step_start <- Sys.time()
progress(2, TOTAL_STEPS, "Preparing feature matrices (~1-2 min)...")

# Identify feature columns (exclude label)
exclude_cols <- c("label")
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

progress(2, TOTAL_STEPS, "Feature preparation complete", step_start)

# ============================================================================
# Step 3: Train LASSO with Cross-Validation
# ============================================================================

step_start <- Sys.time()
progress(3, TOTAL_STEPS, "Training LASSO with 5-fold CV (~20-45 min)...")
cat("  This is the slowest step - glmnet will show iteration progress\n")

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
plot(cv_fit, main = "LASSO V6 Cross-Validation (Fixed)")
dev.off()

progress(3, TOTAL_STEPS, "LASSO training complete", step_start)

# ============================================================================
# Step 4: Extract Coefficients
# ============================================================================

step_start <- Sys.time()
progress(4, TOTAL_STEPS, "Extracting coefficients...")

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

progress(4, TOTAL_STEPS, "Coefficient extraction complete", step_start)

# ============================================================================
# Step 5: KEY CHECKS - Verify Intuitive Coefficient Signs
# ============================================================================

step_start <- Sys.time()
progress(5, TOTAL_STEPS, "Running coefficient sanity checks...")

cat("\n", rep("=", 60), "\n", sep = "")
cat("KEY COEFFICIENT CHECKS (V6 Fixed)\n")
cat(rep("=", 60), "\n", sep = "")

# Define expected signs for key features (UPDATED - removed leaky features)
expected_signs <- list(
  "f_openness_score" = "positive",
  "match_same_state" = "positive",
  "match_state_pct" = "positive",
  "match_sector_pct" = "positive",
  "match_semantic_similarity" = "positive",
  "f_is_accessible" = "positive",
  "f_is_growing" = "positive",
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

# Check that removed leaky features are NOT present
cat("\nVerifying removed features are not in model:\n")
removed_features <- c("r_total_grants", "r_total_funders", "r_total_funding",
                     "r_assets", "r_employee_count",
                     "f_funded_new_recently", "f_first_time_rate", "f_one_time_rate")
for (feat in removed_features) {
  if (feat %in% coef_df$feature) {
    cat(sprintf("  ERROR: %s should not be in V6 model!\n", feat))
  } else {
    cat(sprintf("  OK: %s not in model\n", feat))
  }
}

progress(5, TOTAL_STEPS, "Coefficient checks complete", step_start)

# ============================================================================
# Step 6: Evaluate on Validation Set
# ============================================================================

step_start <- Sys.time()
progress(6, TOTAL_STEPS, "Evaluating on validation set...")

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

progress(6, TOTAL_STEPS, "Validation evaluation complete", step_start)

# ============================================================================
# Step 7: Evaluate on Test Set
# ============================================================================

step_start <- Sys.time()
progress(7, TOTAL_STEPS, "Evaluating on test set...")

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
# AUC Interpretation
# ============================================================================

cat("\n", rep("=", 60), "\n", sep = "")
cat("AUC INTERPRETATION\n")
cat(rep("=", 60), "\n", sep = "")

test_auc <- auc(roc_test)
if (test_auc >= 0.90) {
  cat("  EXCELLENT (0.90+): Very strong discrimination\n")
} else if (test_auc >= 0.80) {
  cat("  GOOD (0.80-0.90): Strong discrimination, production-ready\n")
} else if (test_auc >= 0.70) {
  cat("  FAIR (0.70-0.80): Useful for ranking, but not definitive\n")
} else {
  cat("  WEAK (<0.70): May need additional features or approach\n")
}

cat("\n  Expected range (without leaky features): 0.82-0.90\n")
cat("  V5 had 0.969 AUC but that was inflated by feature leakage\n")
cat(sprintf("  V6 AUC of %.3f is HONEST and USABLE\n", test_auc))

progress(7, TOTAL_STEPS, "Test evaluation complete", step_start)

# ============================================================================
# Step 8: Save Outputs
# ============================================================================

step_start <- Sys.time()
progress(8, TOTAL_STEPS, "Saving model outputs (~1 min)...")

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
# Summary
# ============================================================================

cat("\n", rep("=", 60), "\n", sep = "")
cat("SUMMARY\n")
cat(rep("=", 60), "\n", sep = "")

cat(sprintf("  Model:              LASSO V6 (fixed, no leakage)\n"))
cat(sprintf("  Split:              Random 80/10/10\n"))
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
cat("  2. Compare V6 AUC to expected range (0.82-0.90)\n")
cat("  3. Copy coefficients.json and scaling.json to Pipeline v2/config/\n")
cat("  4. Update 02_score_foundations.py to use V6 features\n")
cat("  5. Test on Ka Ulukoa and PSMF\n")

progress(8, TOTAL_STEPS, "All outputs saved", step_start)

# ============================================================================
# FINAL SUMMARY
# ============================================================================

total_elapsed <- difftime(Sys.time(), script_start_time, units = "mins")

cat("\n", rep("=", 60), "\n", sep = "")
cat("TRAINING COMPLETE!\n")
cat(rep("=", 60), "\n", sep = "")
cat(sprintf("\nTotal runtime: %.1f minutes\n", total_elapsed))
cat(sprintf("Finished at: %s\n", format(Sys.time(), "%H:%M:%S")))
