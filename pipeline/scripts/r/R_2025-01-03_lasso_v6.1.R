# R_2025-01-03_lasso_v6.1.R
# Train LASSO V6.1 model with size-matched negatives
#
# KEY IMPROVEMENTS FROM V6:
# 1. Size-matched negatives (removes size confounding)
# 2. Actual recipient embeddings for semantic similarity
# 3. Stratified validation by size bucket
#
# EXPECTED RESULTS (per agent review):
# - Overall AUC: 0.82-0.88 (down from 0.98 - this is GOOD)
# - Revenue coefficient: <1.5 (down from +4.07)
# - Semantic similarity: POSITIVE (fixed from -0.31)
# - All size buckets: AUC >0.75
#
# Usage:
#   Rscript scripts/r/R_2025-01-03_lasso_v6.1.R

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

TOTAL_STEPS <- 9

# ============================================================================
# Configuration
# ============================================================================

BASE_DIR <- "/Users/aleckleinman/Documents/TheGrantScout/5. TheGrantScout - Pipeline/Pipeline v2"
INPUT_DIR <- file.path(BASE_DIR, "outputs/v6.1")
OUTPUT_DIR <- file.path(BASE_DIR, "outputs/v6.1/model")

dir.create(OUTPUT_DIR, recursive = TRUE, showWarnings = FALSE)

cat("\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("LASSO V6.1 Model Training\n")
cat("Size-matched negatives, actual recipient embeddings\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("\nExpected: AUC 0.82-0.88, revenue coef <1.5\n")
cat("Started at:", format(Sys.time(), "%H:%M:%S"), "\n")

# ============================================================================
# Step 1: Load Data
# ============================================================================

step_start <- Sys.time()
progress(1, TOTAL_STEPS, "Loading CSV files...")

train <- read.csv(file.path(INPUT_DIR, "train.csv"))
cat(sprintf("    Loaded train.csv: %s rows\n", format(nrow(train), big.mark = ",")))

validation <- read.csv(file.path(INPUT_DIR, "validation.csv"))
cat(sprintf("    Loaded validation.csv: %s rows\n", format(nrow(validation), big.mark = ",")))

test <- read.csv(file.path(INPUT_DIR, "test.csv"))
cat(sprintf("    Loaded test.csv: %s rows\n", format(nrow(test), big.mark = ",")))

# Load full data with size buckets for stratified validation
full_data <- read.csv(file.path(INPUT_DIR, "full_with_buckets.csv"))

progress(1, TOTAL_STEPS, "Loading complete", step_start)

cat(sprintf("\n  Train:      %s rows (%.1f%% positive)\n",
            format(nrow(train), big.mark = ","), mean(train$label) * 100))
cat(sprintf("  Validation: %s rows (%.1f%% positive)\n",
            format(nrow(validation), big.mark = ","), mean(validation$label) * 100))
cat(sprintf("  Test:       %s rows (%.1f%% positive)\n",
            format(nrow(test), big.mark = ","), mean(test$label) * 100))

# ============================================================================
# Step 2: Prepare Features
# ============================================================================

step_start <- Sys.time()
progress(2, TOTAL_STEPS, "Preparing feature matrices...")

exclude_cols <- c("label")
feature_cols <- setdiff(names(train), exclude_cols)

cat(sprintf("  Features: %d\n", length(feature_cols)))

X_train <- as.matrix(train[, feature_cols])
y_train <- train$label

X_val <- as.matrix(validation[, feature_cols])
y_val <- validation$label

X_test <- as.matrix(test[, feature_cols])
y_test <- test$label

# Handle NAs
X_train[is.na(X_train)] <- 0
X_val[is.na(X_val)] <- 0
X_test[is.na(X_test)] <- 0

# Scale features
cat("  Scaling features...\n")
train_means <- colMeans(X_train)
train_sds <- apply(X_train, 2, sd)
train_sds[train_sds == 0] <- 1

X_train_scaled <- scale(X_train, center = train_means, scale = train_sds)
X_val_scaled <- scale(X_val, center = train_means, scale = train_sds)
X_test_scaled <- scale(X_test, center = train_means, scale = train_sds)

progress(2, TOTAL_STEPS, "Feature preparation complete", step_start)

# ============================================================================
# Step 3: Train LASSO with Cross-Validation
# ============================================================================

step_start <- Sys.time()
progress(3, TOTAL_STEPS, "Training LASSO with 5-fold CV...")

set.seed(42)

cv_fit <- cv.glmnet(
  X_train_scaled, y_train,
  family = "binomial",
  alpha = 1,
  nfolds = 5,
  type.measure = "auc",
  standardize = FALSE,
  parallel = FALSE,
  trace.it = 1
)

cat(sprintf("  Best lambda: %.6f\n", cv_fit$lambda.min))
cat(sprintf("  CV AUC: %.4f\n", max(cv_fit$cvm)))

png(file.path(OUTPUT_DIR, "cv_lambda_plot.png"), width = 800, height = 600)
plot(cv_fit, main = "LASSO V6.1 Cross-Validation")
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

intercept <- coef_df$coefficient[coef_df$feature == "(Intercept)"]
coef_df <- coef_df[coef_df$feature != "(Intercept)", ]

coef_df$abs_coefficient <- abs(coef_df$coefficient)
coef_df <- coef_df[order(-coef_df$abs_coefficient), ]

nonzero <- coef_df[coef_df$coefficient != 0, ]
cat(sprintf("  Non-zero coefficients: %d of %d\n", nrow(nonzero), nrow(coef_df)))

progress(4, TOTAL_STEPS, "Coefficient extraction complete", step_start)

# ============================================================================
# Step 5: KEY CHECKS - V6.1 Success Criteria
# ============================================================================

step_start <- Sys.time()
progress(5, TOTAL_STEPS, "Running coefficient sanity checks...")

cat("\n", rep("=", 60), "\n", sep = "")
cat("KEY COEFFICIENT CHECKS (V6.1)\n")
cat(rep("=", 60), "\n", sep = "")

# V6.1 success criteria
expected_signs <- list(
  "f_openness_score" = "positive",
  "match_same_state" = "positive",
  "match_state_pct" = "positive",
  "match_sector_pct" = "positive",
  "match_semantic_similarity" = "positive",  # MUST be positive in V6.1
  "f_is_growing" = "positive",
  "f_is_recently_active" = "positive",
  "f_sector_hhi" = "negative"
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

# Check revenue coefficient (should be <1.5)
rev_coef <- coef_df$coefficient[coef_df$feature == "r_total_revenue"]
log_rev_coef <- coef_df$coefficient[coef_df$feature == "r_log_total_revenue"]

cat("\n  REVENUE COEFFICIENT CHECK (Target: <1.5):\n")
if (length(rev_coef) > 0 && rev_coef != 0) {
  status <- if (abs(rev_coef) < 1.5) "PASS" else "FAIL"
  cat(sprintf("    r_total_revenue: %+.4f [%s]\n", rev_coef, status))
  if (status == "FAIL") all_pass <- FALSE
}
if (length(log_rev_coef) > 0 && log_rev_coef != 0) {
  cat(sprintf("    r_log_total_revenue: %+.4f\n", log_rev_coef))
}

if (all_pass) {
  cat("\n*** ALL V6.1 SUCCESS CRITERIA MET! ***\n")
} else {
  cat("\n*** WARNING: Some criteria not met ***\n")
}

progress(5, TOTAL_STEPS, "Coefficient checks complete", step_start)

# ============================================================================
# Step 6: Overall Performance
# ============================================================================

step_start <- Sys.time()
progress(6, TOTAL_STEPS, "Evaluating overall performance...")

pred_val <- predict(cv_fit, X_val_scaled, s = "lambda.min", type = "response")
roc_val <- roc(y_val, as.vector(pred_val), quiet = TRUE)

pred_test <- predict(cv_fit, X_test_scaled, s = "lambda.min", type = "response")
roc_test <- roc(y_test, as.vector(pred_test), quiet = TRUE)

cat("\n", rep("=", 60), "\n", sep = "")
cat("OVERALL PERFORMANCE\n")
cat(rep("=", 60), "\n", sep = "")
cat(sprintf("  Validation AUC: %.4f\n", auc(roc_val)))
cat(sprintf("  Test AUC:       %.4f\n", auc(roc_test)))

test_auc <- auc(roc_test)
if (test_auc >= 0.82 && test_auc <= 0.90) {
  cat("\n  AUC in expected range (0.82-0.90) - V6.1 SUCCESS!\n")
} else if (test_auc > 0.90) {
  cat("\n  WARNING: AUC still high - check for remaining confounding\n")
} else {
  cat("\n  WARNING: AUC below expected - model may need refinement\n")
}

progress(6, TOTAL_STEPS, "Overall evaluation complete", step_start)

# ============================================================================
# Step 7: STRATIFIED VALIDATION BY SIZE BUCKET
# ============================================================================

step_start <- Sys.time()
progress(7, TOTAL_STEPS, "Stratified validation by size bucket...")

cat("\n", rep("=", 60), "\n", sep = "")
cat("STRATIFIED AUC BY SIZE BUCKET (All should be >0.75)\n")
cat(rep("=", 60), "\n", sep = "")

# Get test set with size buckets
test_with_bucket <- full_data[full_data$split == "test", ]

# Prepare features for prediction
test_features <- as.matrix(test_with_bucket[, feature_cols])
test_features[is.na(test_features)] <- 0
test_features_scaled <- scale(test_features, center = train_means, scale = train_sds)

# Predict
test_with_bucket$predicted <- as.vector(predict(cv_fit, test_features_scaled, s = "lambda.min", type = "response"))

# Compute AUC by size bucket
buckets <- c("tiny", "small", "medium", "large")
bucket_results <- data.frame(
  bucket = character(),
  n = integer(),
  auc = numeric(),
  stringsAsFactors = FALSE
)

for (bucket in buckets) {
  subset <- test_with_bucket[test_with_bucket$size_bucket == bucket, ]
  if (nrow(subset) > 100 && length(unique(subset$label)) == 2) {
    bucket_auc <- auc(roc(subset$label, subset$predicted, quiet = TRUE))
    status <- if (bucket_auc >= 0.75) "PASS" else "FAIL"
    cat(sprintf("  %-8s: AUC = %.4f (n=%s) [%s]\n",
                bucket, bucket_auc, format(nrow(subset), big.mark=","), status))
    bucket_results <- rbind(bucket_results, data.frame(
      bucket = bucket,
      n = nrow(subset),
      auc = bucket_auc
    ))
  } else {
    cat(sprintf("  %-8s: Insufficient data (n=%d)\n", bucket, nrow(subset)))
  }
}

# Save stratified results
write.csv(bucket_results, file.path(OUTPUT_DIR, "stratified_auc.csv"), row.names = FALSE)

progress(7, TOTAL_STEPS, "Stratified validation complete", step_start)

# ============================================================================
# Step 8: Save Outputs
# ============================================================================

step_start <- Sys.time()
progress(8, TOTAL_STEPS, "Saving model outputs...")

# Coefficients
coef_df$direction <- ifelse(coef_df$coefficient > 0, "positive",
                           ifelse(coef_df$coefficient < 0, "negative", "zero"))
write.csv(coef_df, file.path(OUTPUT_DIR, "coefficients_all.csv"), row.names = FALSE)
write.csv(nonzero, file.path(OUTPUT_DIR, "coefficients_nonzero.csv"), row.names = FALSE)

# Scaling parameters
scaling_df <- data.frame(
  feature = feature_cols,
  mean = train_means,
  sd = train_sds
)
write.csv(scaling_df, file.path(OUTPUT_DIR, "scaling_parameters.csv"), row.names = FALSE)

# JSON for pipeline
coef_json <- list(
  intercept = intercept,
  coefficients = setNames(as.list(nonzero$coefficient), nonzero$feature)
)
write_json(coef_json, file.path(OUTPUT_DIR, "coefficients.json"), pretty = TRUE, auto_unbox = TRUE)

scaling_json <- setNames(
  lapply(1:nrow(scaling_df), function(i) {
    list(mean = scaling_df$mean[i], sd = scaling_df$sd[i])
  }),
  scaling_df$feature
)
write_json(scaling_json, file.path(OUTPUT_DIR, "scaling.json"), pretty = TRUE, auto_unbox = TRUE)

# Metrics summary
metrics_df <- data.frame(
  metric = c("val_auc", "test_auc", "cv_auc", "intercept",
             "n_features_nonzero", "n_features_total"),
  value = c(auc(roc_val), auc(roc_test), max(cv_fit$cvm), intercept,
            nrow(nonzero), nrow(coef_df))
)
write.csv(metrics_df, file.path(OUTPUT_DIR, "metrics_summary.csv"), row.names = FALSE)

# ROC curve
png(file.path(OUTPUT_DIR, "roc_curve.png"), width = 800, height = 600)
plot(roc_test, main = sprintf("LASSO V6.1 ROC Curve (Test AUC = %.3f)", auc(roc_test)),
     col = "blue", lwd = 2)
abline(a = 0, b = 1, lty = 2, col = "gray")
dev.off()

progress(8, TOTAL_STEPS, "Outputs saved", step_start)

# ============================================================================
# Step 9: Summary
# ============================================================================

progress(9, TOTAL_STEPS, "Generating summary...")

cat("\n", rep("=", 60), "\n", sep = "")
cat("TOP 20 COEFFICIENTS BY MAGNITUDE\n")
cat(rep("=", 60), "\n", sep = "")

top20 <- head(nonzero, 20)
for (i in 1:nrow(top20)) {
  cat(sprintf("  %2d. %-35s %+.4f\n", i, top20$feature[i], top20$coefficient[i]))
}

cat("\n", rep("=", 60), "\n", sep = "")
cat("V6.1 SUMMARY\n")
cat(rep("=", 60), "\n", sep = "")

cat(sprintf("  Model:              LASSO V6.1 (size-matched negatives)\n"))
cat(sprintf("  Training samples:   %s\n", format(nrow(train), big.mark = ",")))
cat(sprintf("  Features:           %d (%d non-zero)\n", length(feature_cols), nrow(nonzero)))
cat(sprintf("  Test AUC:           %.4f (target: 0.82-0.88)\n", auc(roc_test)))
cat(sprintf("  Intercept:          %.4f\n", intercept))

cat("\nOutput files:\n")
cat(sprintf("  %s/coefficients.json\n", OUTPUT_DIR))
cat(sprintf("  %s/scaling.json\n", OUTPUT_DIR))
cat(sprintf("  %s/stratified_auc.csv\n", OUTPUT_DIR))

cat("\nNext steps:\n")
cat("  1. Verify all size buckets have AUC >0.75\n")
cat("  2. Check semantic similarity coefficient is POSITIVE\n")
cat("  3. Run Ka Ulukoa and PSMF validation\n")
cat("  4. Copy to config/ and update pipeline\n")

total_elapsed <- difftime(Sys.time(), script_start_time, units = "mins")
cat("\n", rep("=", 60), "\n", sep = "")
cat("V6.1 TRAINING COMPLETE!\n")
cat(sprintf("Total runtime: %.1f minutes\n", total_elapsed))
cat(rep("=", 60), "\n", sep = "")
