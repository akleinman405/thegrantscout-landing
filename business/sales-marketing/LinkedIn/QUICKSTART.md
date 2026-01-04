# LinkedIn Launch Quickstart Guide

**Goal:** Get from zero to posting by January 6, 2025

---

## Folder Structure

```
LinkedIn/
├── Queue/           ← Posts ready to schedule
├── Carousels/
│   ├── PDFs/        ← 2 carousels ready (Jan 9, Jan 14)
│   └── Scripts/     ← Python generators for new carousels
├── Strategy/        ← Calendar, insights catalog, framework
├── Research/        ← Competitor analysis
└── Archive/         ← Old project files
```

---

## Phase 1: Setup (Do by Jan 5)

### 1.1 Create LinkedIn Company Page (15 min)

1. Go to: linkedin.com/company/setup/new
2. Fill in:
   - **Name:** TheGrantScout
   - **Tagline:** "Find foundations you didn't know existed"
   - **Industry:** Internet Publishing
   - **Size:** 2-10 employees
3. Upload logo (400x400px) and banner (1128x191px)
4. Copy About section from `Strategy/CHECKLIST_*.md`

### 1.2 Optimize Your Profile (15 min)

1. Update headline: `Building TheGrantScout | Foundation Funding Data & Insights for Nonprofits`
2. Enable Creator Mode: Settings → Resources → Creator mode
3. Select topics: #GrantWriting, #NonprofitFunding, #Philanthropy
4. Update banner with TheGrantScout branding
5. Add website to Featured section

### 1.3 Set Up Buffer (15 min)

1. Go to: buffer.com → Create free account
2. Connect your personal LinkedIn profile
3. Connect TheGrantScout company page
4. Set posting schedule:

| Channel | Days | Time |
|---------|------|------|
| Founder (your profile) | Mon-Fri | 8:00 AM MST |
| Company | Tue, Wed, Fri | 9:00 AM MST |

---

## Phase 2: Prepare Launch Week Content (Do by Jan 5)

### 2.1 Content Already Ready

| Date | Content | Location | Status |
|------|---------|----------|--------|
| Jan 9 | Foundation size carousel | `Carousels/PDFs/` | Ready |
| Jan 14 | Cross-state giving carousel | `Carousels/PDFs/` | Ready |

### 2.2 Content to Write

Create these files in `Queue/`:

```
Queue/
├── 2025-01-06_founder_origin_story.md
├── 2025-01-07_founder_median_grant.md
├── 2025-01-07_company_welcome.md
├── 2025-01-08_founder_poll_median.md
├── 2025-01-10_founder_timing_matters.md
└── 2025-01-10_company_week1_recap.md
```

**Where to find the content:** Full text for each post is in `Strategy/CALENDAR_*.md` under "Week 1: January 6-10, 2025"

### 2.3 Quick Template for Queue Files

```markdown
# [Topic]

**Date:** 2025-01-XX
**Channel:** Founder / Company
**Format:** Text / Poll / Carousel

---

[Paste post content here]

---

**Hashtags:** #GrantWriting #NonprofitFunding #FoundationGrants
```

---

## Phase 3: Schedule in Buffer (Jan 5)

### 3.1 Schedule Week 1

1. Open Buffer → Founder profile queue
2. For each post in `Queue/`:
   - Click "Create Post"
   - Paste content
   - Set date/time
   - For carousels: Upload PDF from `Carousels/PDFs/`
3. Repeat for Company page
4. Verify all 8 posts are scheduled

### 3.2 After Scheduling

1. Delete files from `Queue/` (or move to Archive if you want)
2. Update `Strategy/CONTENT_LOG.md` with what's scheduled

---

## Phase 4: Launch Day (Jan 6)

### Morning Checklist

- [ ] Verify first post went live at 8:00 AM
- [ ] Like and respond to any early comments
- [ ] Share from company page to personal (if applicable)

### Daily Engagement (30 min)

1. Check notifications → respond to all comments
2. Like 10-15 posts in your niche
3. Leave 3-5 substantive comments (15+ words)
4. Check DMs

---

## Weekly Routine (Ongoing)

### Sunday (1-2 hours)

1. Open `Strategy/CALENDAR_*.md` → see next week's content
2. Open `Strategy/DATA_*_insights_catalog.md` → grab hooks/data
3. Write posts, save to `Queue/` with date prefix
4. Create 1 carousel if scheduled (use Scripts/)

### Monday Morning

1. Open Buffer → schedule week's content
2. Delete scheduled files from Queue/
3. Update `Strategy/CONTENT_LOG.md`

### Friday (15 min)

1. Check Buffer analytics
2. Note top performer
3. Adjust next week if pattern emerges

---

## Key Files Reference

| Need | File |
|------|------|
| What to post this week | `Strategy/CALENDAR_*.md` |
| Data insights + hooks | `Strategy/DATA_*_insights_catalog.md` |
| How to write each format | `Strategy/CHECKLIST_*.md` |
| Voice and pillars | `Strategy/SPEC_*_content_framework.md` |
| Track what's posted | `Strategy/CONTENT_LOG.md` |
| Competitor tactics | `Research/REPORT_*_competitor_research.md` |

---

## Creating New Carousels

1. Copy existing script: `Carousels/Scripts/create_carousel.py`
2. Modify content in slide functions
3. Run: `python3 create_carousel.py`
4. Find PDF in `Carousels/PDFs/`

---

## Targets (First Month)

| Metric | Week 1 | Week 4 |
|--------|--------|--------|
| Founder followers | +50 | +250 |
| Company followers | 25 | 100 |
| Impressions/post | 200 | 500 |
| Engagement rate | 3% | 5% |

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Carousel won't upload | Ensure PDF, not PNG. Max 300 slides. |
| Low engagement | Check posting time, strengthen hook |
| Buffer limit hit | Free = 10 posts/channel. Schedule weekly. |
| Forgot to post | Use emergency content from CHECKLIST |

---

## Next Actions Checklist

**By Jan 5:**
- [ ] Create LinkedIn company page
- [ ] Optimize your profile + Creator Mode
- [ ] Set up Buffer account
- [ ] Connect both LinkedIn accounts to Buffer
- [ ] Write Week 1 posts (6 text posts)
- [ ] Schedule all 8 Week 1 posts in Buffer

**Jan 6 (Launch Day):**
- [ ] Verify first post is live
- [ ] Engage for 30 min
- [ ] Celebrate!

---

*Created 2025-12-31*
