# TheGrantScout Website - Quick Start Guide for Builders

## What You're Building

A professional landing page to market TheGrantScout - an AI-powered grant discovery service for nonprofits.

### The Pitch (memorize this)
"TheGrantScout uses AI to match nonprofits with grant opportunities based on their mission and funder relationships. Instead of searching databases for hours, our AI analyzes 85,000+ foundations and delivers 5-10 curated, high-probability opportunities every week."

## 5-Minute Orientation

### What is TheGrantScout?
- AI grant matching service for 501(c)(3) nonprofits
- Analyzes 1.6M+ historical grants from IRS 990 data
- Identifies funders who already support similar organizations
- Delivers weekly curated opportunity reports

### Key Differentiator
**Relationship intelligence**: We find funders who already support organizations like yours (67% success rate vs 8% cold outreach).

### Target Customers
Nonprofits with $1M-$50M budgets in: healthcare, housing, education, social services, arts, youth development.

## Your Mission

Build a conversion-optimized landing page that:
1. Communicates value within 5 seconds
2. Explains the process clearly
3. Drives signups/trials
4. Looks professional and trustworthy
5. Works perfectly on mobile

## Critical Success Factors

### 1. Above-the-Fold (First 5 seconds)
Visitor should immediately understand:
- WHAT: Grant discovery service
- FOR WHOM: Nonprofits
- VALUE: Stop searching, AI matches you with opportunities
- ACTION: Get your first 5 matches free

### 2. Trust Signals
- 85,000+ foundations (data scale)
- 1.6M+ grants analyzed (credibility)
- 67% vs 8% success rate (proof)
- Real testimonials when available (social proof)

### 3. Clear Process
4 simple steps: Tell us about you → We scan → Get matches → Apply with confidence

### 4. No Confusion
- No jargon without explanation
- Benefits before features
- Specific numbers, not vague claims
- One clear CTA per section

## Task Sequencing Strategy

### Phase 1: Foundation (Day 1)
Start here - blocking tasks:
- Task 1: Clone template, verify it runs
- Task 2: Set up design system (colors, fonts)
- Task 3: Configure SEO metadata
- Task 4: Create content data files

### Phase 2: Components (Days 2-3)
Build in this order for fastest feedback:
1. Task 5: Hero (most important!)
2. Task 7: How It Works
3. Task 6: Features
4. Task 8: Pricing
5. Task 9: FAQ
6. Task 12: Navigation
7. Task 11: Footer
8. Task 10: Testimonials (optional for v1)

### Phase 3: Polish (Day 4)
- Task 14: Assemble homepage
- Task 15: Responsive testing
- Task 16: Performance optimization
- Task 17: Accessibility audit

### Phase 4: Launch (Day 5)
- Task 20: Deploy to Vercel
- Task 21: Documentation
- Final QA

### Optional (if time allows)
- Task 18: Analytics
- Task 19: Lead capture form

## Design Cheat Sheet

### Colors (copy these exact values)
```css
Primary Navy: #1e3a5f
Accent Gold: #d4a853
White: #ffffff
Off-white: #f9fafb
Text: #2d3748
Secondary: #e6f0ff
```

### Typography
- Font: Inter (Google Fonts)
- Hero headline: 48-64px (32-40px mobile)
- Section headers: 36-42px (28-32px mobile)
- Body: 16-18px
- Bold weight for headlines, Regular for body

### Spacing
- Section padding: 80-120px vertical
- Component spacing: 40-60px
- Element spacing: 16-24px
- Mobile: Reduce by 30-40%

### CTA Buttons
- Primary: Gold background (#d4a853), white text, bold
- Secondary: White background, navy border, navy text
- Size: 48px height minimum (thumb-friendly)
- Border radius: 6-8px (subtle rounding)
- Hover: Darken 10%

## Content Cheat Sheet

### Hero Section
```
Headline: "Stop searching. Start matching."

Subheadline: "TheGrantScout uses AI to find grant opportunities
tailored to your nonprofit's mission, track record, and funder
relationships."

Primary CTA: "Get Your First 5 Matches Free"
Secondary CTA: "See How It Works"

Trust Line: "Analyzing 85,000+ foundations | 1.6M+ historical grants"
```

### Value Props (Features Section)
1. Smart Matching - AI analyzes 85,000+ foundations to find your best fits
2. Relationship Intelligence - 67% success rate vs 8% for cold outreach
3. Weekly Reports - 5-10 curated opportunities, not thousands of irrelevant listings
4. Foundation Profiles - Know before you apply with deep funder insights

### Pricing (Option A - Simple)
```
Early Access
$199/month

Includes:
- Weekly opportunity reports
- 5-10 matched opportunities per week
- Success probability scoring
- Positioning strategies
- Foundation profiles
- Deadline alerts
- Email support

CTA: "Start Free Trial - 14 Days"
Subtext: "First 5 matches free, no credit card required"

Launch Offer: "First 50 nonprofits get $99/mo for 6 months"
```

## Common Pitfalls to Avoid

### Content Mistakes
- Using "we" or "our algorithm" instead of "you" and "your opportunities"
- Talking about features before benefits
- Using jargon: "NTEE codes", "Schedule I", "990-PF" without explanation
- Vague claims: "many foundations" instead of "85,000+ foundations"

### Design Mistakes
- Too much text above the fold (keep it simple!)
- Weak CTAs: "Submit" instead of "Get Your First 5 Matches"
- Buried pricing (don't hide it - transparency builds trust)
- Tiny mobile tap targets (minimum 44x44px)
- Slow images (optimize everything!)

### Technical Mistakes
- Not testing on real mobile devices
- Forgetting alt text on images
- Poor color contrast (text must be readable!)
- Skipping accessibility (nonprofit audience cares about this)
- No loading states on forms

## Testing Checklist (Use This Daily)

### Visual Check
- [ ] Does hero communicate value in 5 seconds?
- [ ] Are CTAs prominent and clear?
- [ ] Is text readable (not too small, good contrast)?
- [ ] Do images load and look crisp?
- [ ] Is spacing consistent?

### Mobile Check (Critical!)
- [ ] Test on 375px width (iPhone SE)
- [ ] All text readable without zooming
- [ ] Buttons easy to tap with thumb
- [ ] No horizontal scrolling
- [ ] Images don't overflow

### Interaction Check
- [ ] All links work
- [ ] Smooth scroll to sections works
- [ ] Hover states on buttons
- [ ] Forms validate
- [ ] No console errors

### Performance Check
- [ ] Page loads in < 3 seconds
- [ ] Run Lighthouse audit (target 90+)
- [ ] Images optimized
- [ ] No layout shift when loading

## When You Get Stuck

### Design Decision Needed?
Ask yourself:
1. What would Apple do? (simplicity)
2. What would Stripe do? (clarity)
3. What builds trust for nonprofit audience? (transparency)

### Technical Issue?
1. Check Next.js docs first
2. Check template example
3. Search error message
4. Ask Project Manager if blocked > 30 minutes

### Content Question?
Refer back to PROJECT_PLAN.md content outline. If still unclear, use your judgment but document the decision in `/docs/DESIGN_DECISIONS.md`.

## Daily Workflow

### Start of Day
1. Review PROJECT_PLAN.md task list
2. Pick next priority task
3. Log task start to mailbox
4. Focus on one task at a time

### During Work
5. Commit code frequently (every feature)
6. Test on mobile regularly
7. Preview in browser constantly
8. Document any design decisions

### End of Day
9. Log task completion to mailbox
10. Push code to repository
11. Note any blockers for tomorrow
12. Share preview link if ready for review

## Quick Wins (Do These First)

### Hour 1
- Clone template and verify it runs
- Change colors to TheGrantScout brand
- Update site name and tagline

### Hour 2
- Create all content data files
- Update hero section with TheGrantScout copy

### Hour 3
- Build How It Works section
- Build Features section

By end of Day 1, you should have a recognizable TheGrantScout homepage with hero, process flow, and features visible.

## Remember

- Mobile first (60% of traffic will be mobile)
- Clarity over cleverness (say it simply)
- Benefits over features (what's in it for them?)
- Trust over hype (nonprofits are skeptical)
- Speed matters (optimize everything)

## Resources at Your Fingertips

- **Full Plan**: `/PROJECT_PLAN.md`
- **Template Demo**: https://finwise-omega.vercel.app
- **Next.js Docs**: https://nextjs.org/docs
- **Tailwind Docs**: https://tailwindcss.com
- **Icons**: https://heroicons.com
- **Fonts**: https://fonts.google.com

## Success Looks Like

After 3-5 days:
- Beautiful, professional landing page
- Clear value proposition
- Mobile-perfect experience
- Fast load times (< 3s)
- Deployed at thegrantscout.com
- Ready to drive signups

You've got this! Start with Task 1 and build momentum.

---

**Questions?** Tag Project Manager in mailbox or document in `/docs/DESIGN_DECISIONS.md`.
