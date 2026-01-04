# TheGrantScout Website - Development Workboard

**Last Updated**: 2025-11-30 00:00:00

---

## Current Sprint: Website Sprint 1 (Nov 30 - Dec 5)

**Goal**: Launch professional TheGrantScout landing page at thegrantscout.com

**Status**: Planning Complete - Ready for Build

**Estimated Timeline**: 3-5 days

**Total Tasks**: 21 tasks
- P0 (Critical): 9 tasks
- P1 (High): 9 tasks
- P2 (Optional): 3 tasks

---

## Todo (21 tasks - All P0/P1 must complete for launch)

### Phase 1: Foundation (Day 1) - BLOCKING TASKS
**Priority: P0 - Start Here**

- **website-task-01**: Project Setup & Template Cloning (0.5 day)
  - Clone Finwise template
  - Install dependencies
  - Verify dev environment running
  - Status: Ready to start

- **website-task-02**: Branding & Design System Setup (1 day)
  - Implement TheGrantScout colors (#1e3a5f navy, #d4a853 gold)
  - Configure typography (Inter font)
  - Set up Tailwind config
  - Dependencies: Task 01
  - Status: Blocked by Task 01

- **website-task-03**: Site Metadata & SEO Setup (0.5 day)
  - Configure SEO tags
  - Open Graph metadata
  - Favicons
  - Dependencies: Task 01
  - Status: Blocked by Task 01

- **website-task-04**: Content Data Files (0.5 day)
  - Create features.ts, faq.ts, pricing.ts, etc.
  - All website copy in data files
  - Dependencies: Task 01
  - Status: Blocked by Task 01

### Phase 2: Component Development (Days 2-3)

**Core Sections - P0**

- **website-task-05**: Hero Section Component (0.5 day)
  - Headline: "Stop searching. Start matching."
  - Primary CTA: "Get Your First 5 Matches Free"
  - Trust indicators
  - Dependencies: Task 02
  - Status: Blocked by Task 02

- **website-task-06**: Features Section Component (0.5 day)
  - 4 value proposition cards
  - Icons + descriptions + stats
  - Dependencies: Task 04
  - Status: Blocked by Task 04

- **website-task-07**: How It Works Section Component (0.5 day)
  - 4-step process flow
  - Visual timeline
  - Dependencies: Task 04
  - Status: Blocked by Task 04

**Supporting Sections - P1**

- **website-task-08**: Pricing Section Component (0.5 day)
  - Early Access tier: $199/mo
  - Feature list
  - CTA buttons
  - Dependencies: Task 04
  - Status: Blocked by Task 04

- **website-task-09**: FAQ Section Component (0.5 day)
  - 10 questions in accordion
  - Expand/collapse functionality
  - Dependencies: Task 04
  - Status: Blocked by Task 04

- **website-task-10**: Testimonials Section Component (0.5 day) - OPTIONAL
  - Priority: P2
  - 3 testimonial cards
  - Can use placeholders for v1
  - Dependencies: Task 04
  - Status: Optional for launch

**Navigation & Layout - P1**

- **website-task-11**: Footer Component (0.5 day)
  - 5-column layout
  - Navigation links
  - Contact info
  - Dependencies: Task 02
  - Status: Blocked by Task 02

- **website-task-12**: Navigation/Header Component (0.5 day)
  - Logo + nav links
  - Mobile hamburger menu
  - CTA in header
  - Dependencies: Task 02
  - Status: Blocked by Task 02

- **website-task-13**: CTA Component (Reusable) (0.25 day)
  - Primary/secondary button styles
  - Hover states
  - Dependencies: Task 02
  - Status: Blocked by Task 02

**Assembly - P0**

- **website-task-14**: Homepage Assembly (0.5 day)
  - Combine all sections
  - Proper spacing
  - Smooth scroll
  - Dependencies: Tasks 05-12
  - Status: Blocked by components

### Phase 3: Testing & Polish (Day 4)

**Testing - P0**

- **website-task-15**: Responsiveness & Cross-Browser Testing (0.5 day)
  - Test mobile (375px, 414px)
  - Test tablet (768px, 1024px)
  - Test desktop (1280px+)
  - Chrome, Firefox, Safari, Edge
  - Dependencies: Task 14
  - Status: Blocked by Task 14

**Optimization - P1**

- **website-task-16**: Performance Optimization (0.5 day)
  - Lighthouse score 90+
  - Image optimization
  - Load time < 3s
  - Dependencies: Task 14
  - Status: Blocked by Task 14

- **website-task-17**: Accessibility Audit (0.5 day)
  - WCAG 2.1 Level AA
  - Screen reader testing
  - Keyboard navigation
  - Dependencies: Task 14
  - Status: Blocked by Task 14

**Optional Enhancements - P2**

- **website-task-18**: Analytics & Tracking Setup (0.25 day)
  - Google Analytics 4
  - Conversion events
  - Priority: P2
  - Dependencies: Task 14
  - Status: Optional for launch

- **website-task-19**: Lead Capture Form (0.5 day)
  - Signup form
  - Form validation
  - Backend integration
  - Priority: P2
  - Dependencies: Task 14
  - Status: Optional for launch (can use Calendly link instead)

### Phase 4: Launch (Day 5)

**Deployment - P0**

- **website-task-20**: Deployment to Vercel (0.5 day)
  - Deploy to production
  - Connect thegrantscout.com domain
  - SSL certificate
  - DNS configuration
  - Dependencies: Tasks 14, 15, 16, 17
  - Status: Blocked by testing

**Documentation - P1**

- **website-task-21**: Documentation & Handoff (0.5 day)
  - Update README
  - Design decisions documented
  - Content update guide
  - Dependencies: Task 20
  - Status: Blocked by deployment

---

## Doing (0 tasks)

No tasks currently in progress. Ready for builder to claim Task 01.

---

## Review (0 tasks)

No tasks awaiting review.

---

## Blocked (0 tasks)

No external blockers. All task dependencies are internal (prior task completion).

---

## Done (0 tasks)

Sprint just started. No completed tasks yet.

---

## Sprint Metrics

**Estimated Total Effort**: 9.75 days of work

**Task Distribution**:
- Setup & Config: 2.5 days (Tasks 01-04)
- Component Dev: 4.25 days (Tasks 05-13)
- Testing & Polish: 1.5 days (Tasks 15-17)
- Deployment & Docs: 1.0 day (Tasks 20-21)
- Optional: 1.25 days (Tasks 10, 18, 19)

**Critical Path** (must complete for launch):
1. Task 01 (Setup)
2. Task 02 (Design System)
3. Task 04 (Content Data)
4. Tasks 05-07 (Core Sections)
5. Tasks 11-12 (Navigation)
6. Task 14 (Assembly)
7. Task 15 (Responsive Testing)
8. Task 20 (Deployment)

**Recommended First Day Goals**:
- Complete Tasks 01-04 (Foundation)
- Start Task 05 (Hero Section)

---

## Risk Assessment

**Low Risk Overall**

**Identified Risks**:
1. Domain DNS propagation may take 24-48 hours (mitigation: start early)
2. Template customization complexity unknown (mitigation: template is MIT licensed, well-documented)
3. No dedicated designer (mitigation: follow brand guidelines strictly, keep it simple)

**Known Unknowns**:
- Exact template structure (will know after Task 01)
- Vercel deployment complexity (should be straightforward)
- Time needed for content polish (allocate buffer time)

---

## Next Steps

**For Builder**:
1. Read PROJECT_PLAN.md in full (30 minutes)
2. Read QUICK_START_GUIDE.md (10 minutes)
3. Claim website-task-01 in state.json
4. Log task start to mailbox
5. Clone template and verify setup
6. Log task completion when done
7. Move to Task 02

**For Project Manager**:
- Monitor daily progress
- Unblock any questions
- Review preview links
- Approve design decisions
- Track velocity

---

## Communication Protocol

**Daily Updates Expected**:
- End of day progress report
- Tasks completed
- Tasks started
- Any blockers or questions
- Preview link if available

**Log to Mailbox**:
- Task starts
- Task completions
- Blockers identified
- Design decisions
- Deployment milestones

---

## Success Criteria

Sprint complete when:
- [ ] All P0 tasks complete (9 tasks)
- [ ] All P1 tasks complete (9 tasks)
- [ ] Site live at https://thegrantscout.com
- [ ] Mobile responsive (tested on real devices)
- [ ] Lighthouse score 90+ (Performance, Accessibility, SEO)
- [ ] Cross-browser compatible
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Stakeholder approved

**P2 tasks optional but nice to have**:
- [ ] Testimonials section
- [ ] Analytics tracking
- [ ] Lead capture form

---

## Resources

**Planning Docs**:
- PROJECT_PLAN.md - Complete specification
- QUICK_START_GUIDE.md - Builder quick reference
- README.md - Project overview

**External**:
- Template: https://github.com/nexi-launch/finwise-landing-page
- Demo: https://finwise-omega.vercel.app
- Next.js: https://nextjs.org/docs
- Tailwind: https://tailwindcss.com

**Team State**:
- state.json - Task tracking
- mailbox.jsonl - Event log

---

**Sprint Status**: Ready to begin
**Next Action**: Builder claims Task 01

---

**End of Workboard**

Last updated by Project Manager on 2025-11-30 at 00:00:00
