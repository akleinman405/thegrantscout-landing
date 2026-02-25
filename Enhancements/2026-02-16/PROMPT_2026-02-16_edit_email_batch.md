# PROMPT: Edit First Email Batch

**Date:** 2026-02-16
**For:** Claude Code CLI
**Schema:** f990_2025

---

## Situation

We just drafted 20 nonprofit cold emails in `Enhancements/2026-02-16/EMAILS_2026-02-16_nonprofit_cohort_1.md` and `Enhancements/2026-02-16/EMAIL_BATCH_2026-02-16_nonprofit_1.csv`. They need a few edits before sending. The full context is in `Enhancements/2026-02-16/REPORT_2026-02-16_email_prep_and_draft.md`.

Read all three files first, then make these edits to BOTH the .md and .csv files:

---

## Edits

### 1. Cap foundation list numbers at "top 200"

Several emails say things like "full 1,754-foundation list" or "full 975-foundation list." Nobody wants a 1,754-row spreadsheet — it sounds like a data dump, not a curated resource.

**Rule:**
- If the cohort has 200+ foundations → say "top 200" (e.g., "We have the top 200 list for free")
- If the cohort has fewer than 200 → use the real number (e.g., "full 67-foundation list" is fine)

Apply to all 20 emails.

### 2. Trim to 50-80 words

Some emails run ~90 words. Tighten them. Cut unnecessary clauses from opening lines — the shorter and more natural, the better. Don't sacrifice the "why" or the foundation names to hit the word count, but trim filler.

### 3. Verify Email #8 (Emergency Support Shelter)

The email references "domestic violence and safety work." Query np2 for this org's mission_description (EIN or org_name match) and make sure the email matches what they actually do. If it's broader than DV work, reword to match their actual mission.

### 4. Flag or replace Email #14 (Sojourner House)

This org is listed as MA but has a PA email domain (sjhpa.org). Query np2 for their actual state and mission. If it's actually a PA org:
- Replace the MA foundation names with PA-relevant foundations from cohort_foundation_lists (state='PA', ntee_sector matching their NTEE)
- Update the state reference in the email
- OR if the data is too messy, replace this prospect entirely with the next-highest-scoring MA prospect that passes all filters

### 5. Don't change these things
- Keep the "why" framing (federal funding uncertainty, trying to help)
- Keep the foundation names and dollar amounts (unless #8 or #14 require swaps)
- Keep "Alec" sign-off with no company name
- Keep the natural wording variation across emails

---

## Output

Overwrite both files in place:
- `Enhancements/2026-02-16/EMAILS_2026-02-16_nonprofit_cohort_1.md`
- `Enhancements/2026-02-16/EMAIL_BATCH_2026-02-16_nonprofit_1.csv`

Add a brief note at the top of the .md file: "v1.1 — Edited: capped list numbers at 200, trimmed to 50-80 words, verified #8 and #14"
