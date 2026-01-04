# Dev Team Prompt: Website Layout & Stats Updates

**Document Type:** PROMPT  
**Date:** December 15, 2025  
**Project Path:** `C:\TheGrantScout\3. Website\thegrantscout-landing`

---

## Situation

Several improvements needed to the landing page: section reordering, copy changes, and verifying database stats displayed on the site are accurate.

---

## Tasks

### 1. Move "What's Inside Each Report" section

**Current location:** Below pricing cards  
**New location:** After "How It Works", before "Save Time, Find Better Opportunities"

New page flow should be:
1. Hero
2. Data Advantage ("Our Data Advantage")
3. How It Works
4. **What's Inside Each Report** ← moved here
5. Save Time, Find Better Opportunities
6. Pricing
7. FAQ
8. Final CTA

---

### 2. Update "Save 20+ Hours Monthly"

Current: "Save 20+ Hours Monthly"  
Change to: "Save Hours Every Month"

(The 20+ hours claim feels inflated)

---

### 3. Make "See a Sample Report" more prominent

The "See a Sample Report" button in the hero should stand out more than "Book a Call" — it's our best conversion tool.

Options:
- Make it slightly larger
- Add a small report icon/thumbnail next to it
- Or reverse the button styling (make it the filled/primary button)

---

### 4. Verify and update database stats

The site currently shows:
- "1.6M+ Grants Analyzed"
- "85,000+ Foundations"

Run these queries against f990_2025 schema to get current counts:

```sql
-- Grant count
SELECT COUNT(*) FROM f990_2025.grants;

-- Foundation count  
SELECT COUNT(DISTINCT ein) FROM f990_2025.foundations;
```

Update the website with accurate numbers (round to nearest 100K for grants, nearest 1K for foundations).

---

## Output

- Updated component/section files
- Confirm new section order renders correctly
- Report actual database counts and what you updated on site
- Note all files changed

