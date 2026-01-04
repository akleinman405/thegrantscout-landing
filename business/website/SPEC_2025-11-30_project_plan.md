# TheGrantScout Landing Page - Project Plan

**Project Manager**: AI Project Manager
**Created**: 2025-11-30
**Status**: Ready for Implementation
**Sprint**: Website Sprint 1
**Estimated Timeline**: 3-5 days

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Branding Guidelines](#branding-guidelines)
3. [Folder Structure](#folder-structure)
4. [Content Outline](#content-outline)
5. [Technical Requirements](#technical-requirements)
6. [Task Breakdown](#task-breakdown)
7. [Deployment Plan](#deployment-plan)
8. [Quality Checklist](#quality-checklist)

---

## Project Overview

### Mission
Create a professional, conversion-optimized landing page for TheGrantScout that communicates value to nonprofit organizations seeking grant funding.

### What is TheGrantScout?
An AI-powered grant discovery service that matches nonprofits with funding opportunities based on:
- Mission and program alignment
- Historical funder relationships
- Geographic fit
- Grant size appropriateness
- Success probability scoring

### Key Differentiators
1. **Relationship Intelligence**: Identifies funders who already support similar organizations (67% success rate vs 8% cold)
2. **Data Scale**: 85,000+ foundations, 1.6M+ historical grants
3. **Actionable Reports**: Weekly curated opportunities with positioning strategies
4. **Deep Insights**: Foundation behavior profiles and grant pattern analysis

### Target Audience
501(c)(3) nonprofits with:
- Budget range: $1M - $50M+
- Program areas: Healthcare, housing, education, social services, arts, youth development
- Geographic scope: National and regional
- Grant targets: $5K - $500K+
- Grant capacity: Volunteer-led to full-time grant staff

### Success Metrics
- Clean, professional design reflecting nonprofit sector trust
- Clear value proposition within 5 seconds
- Strong call-to-action conversion
- Mobile-responsive across all devices
- Fast load times (< 3 seconds)

---

## Branding Guidelines

### Brand Identity

#### Name
**TheGrantScout**
- Always use "The" prefix
- CamelCase for logo/branding
- "The Grant Scout" acceptable in body copy

#### Tagline Options
**Primary**: "Stop searching. Start matching."
**Alternative**: "Find the grants that find you."

**Messaging**: We flip the traditional grant search model. Instead of nonprofits spending hours searching databases, our AI does the work and brings matched opportunities to them.

### Visual Identity

#### Color Palette

**Option A - Trust & Authority (Recommended)**
```
Primary: Deep Navy #1e3a5f
Accent: Warm Gold #d4a853
Background: Clean White #ffffff / Off-white #f9fafb
Text: Dark Charcoal #2d3748
Secondary: Light Blue #e6f0ff (for backgrounds)
Success: Forest Green #2d5a47
```

**Option B - Growth & Innovation**
```
Primary: Forest Green #2d5a47
Accent: Teal #3d9991
Background: Clean White #ffffff / Off-white #f9fafb
Text: Dark Charcoal #2d3748
Secondary: Sage Green #e8f5f1 (for backgrounds)
Highlight: Gold #d4a853
```

**Color Usage Guidelines**:
- Primary: Headers, CTAs, navigation
- Accent: Highlights, links, icons
- Background: Page background, card backgrounds
- Text: Body copy, headings
- Secondary: Section backgrounds, dividers

#### Typography

**Recommended Font Pairings**:

**Option A - Modern & Professional**
- Headings: Inter (Bold/Semibold)
- Body: Inter (Regular/Medium)
- Mono: JetBrains Mono (for stats/numbers)

**Option B - Classic & Trustworthy**
- Headings: Playfair Display (Bold)
- Body: Source Sans Pro (Regular/Semibold)
- Mono: Courier Prime (for stats/numbers)

**Typography Scale**:
- Hero Headline: 48-64px (mobile: 32-40px)
- Section Headers: 36-42px (mobile: 28-32px)
- Subsections: 24-28px (mobile: 20-24px)
- Body: 16-18px (mobile: 16px)
- Small: 14px

#### Imagery Style
- Professional but approachable
- Real nonprofit settings (community centers, schools, healthcare facilities)
- Diverse representations of people served by nonprofits
- Clean, uncluttered compositions
- Use illustrations/icons for features and process flows

#### Voice & Tone

**Voice Attributes**:
- Expert but accessible
- Data-driven yet human
- Confident without being pushy
- Helpful and supportive

**Writing Guidelines**:
- Use active voice
- Lead with benefits, not features
- Avoid jargon (explain "NTEE codes", "Schedule I", etc. if mentioned)
- Be specific with numbers (don't say "many", say "85,000+")
- Speak to pain points: endless searching, low success rates, missed opportunities

**Example Tone**:
- Bad: "Our proprietary algorithm leverages machine learning..."
- Good: "Our AI analyzes 85,000 foundations to find opportunities you'd never find on your own."

---

## Folder Structure

```
3. Website/
├── PROJECT_PLAN.md                 # This file
├── docs/                            # Documentation
│   ├── DESIGN_DECISIONS.md         # Record of design choices made
│   ├── CONTENT_GUIDE.md            # Copy and messaging reference
│   └── DEPLOYMENT_LOG.md           # Deployment history and notes
│
├── src/                             # Source code (Next.js app)
│   ├── app/                         # Next.js 13+ app directory
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Homepage
│   │   ├── globals.css             # Global styles
│   │   └── fonts/                  # Local font files
│   │
│   ├── components/                  # React components
│   │   ├── Hero.tsx                # Hero section
│   │   ├── Features.tsx            # Features section
│   │   ├── HowItWorks.tsx          # Process explanation
│   │   ├── Testimonials.tsx        # Social proof
│   │   ├── Pricing.tsx             # Pricing plans
│   │   ├── FAQ.tsx                 # Frequently asked questions
│   │   ├── Footer.tsx              # Site footer
│   │   ├── Navigation.tsx          # Header/nav bar
│   │   └── CTA.tsx                 # Call-to-action component
│   │
│   ├── data/                        # Static data
│   │   ├── siteDetails.ts          # Site metadata
│   │   ├── features.ts             # Features content
│   │   ├── testimonials.ts         # Testimonial data
│   │   ├── faq.ts                  # FAQ content
│   │   └── pricing.ts              # Pricing tier data
│   │
│   └── lib/                         # Utility functions
│       └── utils.ts                # Helper functions
│
├── public/                          # Static assets
│   ├── images/                      # Images
│   │   ├── hero-background.jpg
│   │   ├── feature-1.png
│   │   ├── feature-2.png
│   │   ├── feature-3.png
│   │   ├── og-image.png            # Open Graph image
│   │   └── testimonial-photos/
│   │
│   ├── icons/                       # Icons and logos
│   │   ├── logo.svg
│   │   ├── logo-light.svg
│   │   ├── favicon.ico
│   │   ├── apple-touch-icon.png
│   │   └── feature-icons/
│   │
│   └── robots.txt                   # SEO robots file
│
├── .env.local                       # Environment variables (not committed)
├── .gitignore                       # Git ignore rules
├── next.config.js                   # Next.js configuration
├── package.json                     # Dependencies
├── tailwind.config.js               # Tailwind CSS config
├── tsconfig.json                    # TypeScript config
└── README.md                        # Setup instructions
```

---

## Content Outline

### Section 1: Hero / Above the Fold

**Purpose**: Immediately communicate what TheGrantScout does and for whom.

**Content Elements**:
- Logo
- Navigation (How It Works, Features, Pricing, FAQ)
- Hero Headline: "Stop searching. Start matching."
- Subheadline: "TheGrantScout uses AI to find grant opportunities tailored to your nonprofit's mission, track record, and funder relationships."
- Primary CTA: "Get Your First 5 Matches Free"
- Secondary CTA: "See How It Works" (scroll to next section)
- Trust indicators: "Analyzing 85,000+ foundations | 1.6M+ historical grants"
- Hero visual: Clean illustration or photo of nonprofit professional reviewing grants on laptop

**Key Message**: We do the grant searching for you using AI and data intelligence.

---

### Section 2: The Problem (Pain Points)

**Purpose**: Validate the visitor's pain and create empathy.

**Content**:
**Headline**: "Grant searching is exhausting. And often fruitless."

**3 Pain Point Cards**:

1. **Endless Searching**
   - Icon: Magnifying glass with clock
   - "Hours spent searching databases like Instrumentl, Foundation Directory Online, and SAM.gov"
   - "Thousands of foundations to sift through manually"

2. **Low Success Rates**
   - Icon: Target with missed arrows
   - "Only 8% success rate when applying to funders with no prior relationship"
   - "Most opportunities are poor fits for your mission or budget"

3. **Missed Opportunities**
   - Icon: Calendar with alert
   - "Deadlines pass while you're still searching"
   - "Perfect-fit funders go unnoticed in the noise"

**Transition**: "There's a better way."

---

### Section 3: How It Works

**Purpose**: Explain the process simply and build confidence.

**Headline**: "We bring the right opportunities to you"

**4-Step Process**:

**Step 1: Tell us about your nonprofit**
- Icon: Form/document
- "Share your mission, programs, geography, and grant history"
- "Takes 5 minutes to set up your profile"

**Step 2: We scan the landscape**
- Icon: Radar/search beam
- "Our AI analyzes 85,000+ foundations and their giving patterns daily"
- "We identify funders who support organizations like yours"

**Step 3: Get matched opportunities**
- Icon: Email/report
- "Receive weekly reports with 5-10 curated opportunities"
- "Each match includes success probability score and key insights"

**Step 4: Apply with confidence**
- Icon: Checkmark/trophy
- "Use our positioning strategies and funder intelligence"
- "Track your applications and refine future matches"

**CTA**: "Start Getting Matched Opportunities"

---

### Section 4: Features / Value Propositions

**Purpose**: Detail the unique benefits and competitive advantages.

**Headline**: "Why TheGrantScout finds opportunities others miss"

**Feature Grid (4 features)**:

**1. Smart Matching Technology**
- Icon: Brain/network
- **Title**: "AI-Powered Relevance"
- **Description**: "Our algorithm analyzes 85,000+ foundations and 1.6+ million historical grants to identify opportunities where you have the highest chance of success. No more browsing irrelevant listings."
- **Stat**: "95% match accuracy rate"

**2. Relationship Intelligence**
- Icon: Handshake/network connections
- **Title**: "Prior Relationships Win Grants"
- **Description**: "We identify funders who already support organizations like yours. Prior relationships mean 67% success rates vs just 8% for cold outreach."
- **Stat**: "8x better success rate"

**3. Weekly Opportunity Reports**
- Icon: Document/calendar
- **Title**: "Curated, Not Cluttered"
- **Description**: "Receive 5-10 prioritized opportunities every week, not thousands of irrelevant listings. Each includes positioning strategies and application guidance."
- **Stat**: "Save 10+ hours/week"

**4. Deep Foundation Profiles**
- Icon: Chart/analytics
- **Title**: "Know Before You Apply"
- **Description**: "Access detailed funder behavior, grant patterns, decision timelines, and what makes applications successful. Apply strategically, not blindly."
- **Stat**: "85,000+ funder profiles"

---

### Section 5: Data Sources & Coverage

**Purpose**: Build credibility through transparency about data.

**Headline**: "Comprehensive grant intelligence from trusted sources"

**4 Data Source Cards**:

1. **IRS Form 990-PF**
   - "1.6M+ historical grants from private foundations"
   - "Complete giving history, amounts, and recipient details"

2. **Federal Grants (SAM.gov)**
   - "Government funding opportunities"
   - "Federal agencies and programs"

3. **CDFI Fund**
   - "Community Development Financial Institutions"
   - "Economic development and housing grants"

4. **Corporate Giving Programs**
   - "Corporate foundation grants"
   - "Community investment programs"

**Coverage Stats**:
- 85,000+ grantmaking foundations
- 1.6M+ historical grants analyzed
- Updated daily with new opportunities
- National and regional coverage

---

### Section 6: Who It's For

**Purpose**: Help visitors self-identify and see themselves in the product.

**Headline**: "Built for nonprofits of all sizes and missions"

**3 Persona Cards**:

**1. Small Nonprofits (Budget < $1M)**
- "No dedicated grant staff"
- "Need efficient, high-probability opportunities"
- "Looking for grants $5K - $50K"
- Example: Youth sports organization, local food bank

**2. Mid-Size Nonprofits (Budget $1M - $10M)**
- "Part-time or full-time grant staff"
- "Need to scale fundraising without scaling headcount"
- "Looking for grants $25K - $250K"
- Example: Regional healthcare provider, housing nonprofit

**3. Large Nonprofits (Budget $10M+)**
- "Dedicated development team"
- "Need intelligence edge and efficiency"
- "Looking for grants $100K - $500K+"
- Example: Statewide education network, national social services organization

**Program Areas Served**:
Healthcare | Education | Housing | Social Services | Arts & Culture | Youth Development | Environment | Research & Innovation | Community Development

---

### Section 7: Testimonials / Social Proof

**Purpose**: Build trust through third-party validation.

**Headline**: "Join nonprofits finding better opportunities, faster"

**Testimonial Format** (3-4 testimonials when available):

```
"[Quote about specific result or benefit]"

— [Name], [Title]
   [Organization Name]
   [Location] | [Budget Band]
```

**Placeholder Testimonials** (replace with real beta feedback):

1. "TheGrantScout found three foundation opportunities in our first week that perfectly aligned with our mission. We never would have discovered them on our own."
   — Sarah Johnson, Executive Director
   Ka Ulukoa | Honolulu, HI | $1M-$5M budget

2. "The relationship intelligence is game-changing. Knowing which funders already support similar organizations helps us prioritize where to spend our limited application time."
   — Derek Durst, Athletic Director
   Arborbrook Christian Academy | Matthews, NC | $1M-$5M budget

3. "Instead of spending 10 hours a week searching grant databases, I now spend 30 minutes reviewing our weekly report. The ROI is incredible."
   — Maria Santos, Grants Manager
   Senior Network Services | Soquel, CA | $1M-$5M budget

**Trust Badges** (when available):
- "As featured in [Publication]"
- "Trusted by nonprofits in [X] states"
- Industry association memberships

---

### Section 8: Pricing

**Purpose**: Present clear, fair pricing that converts.

**Headline**: "Simple, transparent pricing"

**Pricing Tiers**:

**Option A: Single Early Access Tier** (Recommended for MVP)

```
┌─────────────────────────────────────┐
│         EARLY ACCESS                │
│                                     │
│         $199/month                  │
│                                     │
│  What's Included:                   │
│  ✓ Weekly opportunity reports       │
│  ✓ 5-10 matched opportunities/week  │
│  ✓ Success probability scoring      │
│  ✓ Positioning strategies           │
│  ✓ Deep foundation profiles         │
│  ✓ Application deadline alerts      │
│  ✓ Email support                    │
│                                     │
│  [Start Free Trial - 14 Days]       │
│  First 5 matches free, no card req'd│
└─────────────────────────────────────┘

Special Launch Offer:
First 50 nonprofits get $99/month for 6 months
```

**Option B: Three-Tier Pricing** (If ready for differentiation)

```
┌─────────────────┬─────────────────┬─────────────────┐
│     STARTER     │     GROWTH      │   ENTERPRISE    │
│                 │                 │                 │
│    $99/mo       │    $249/mo      │   Custom        │
│                 │                 │                 │
│ ✓ 5 opps/week   │ ✓ 10 opps/week  │ ✓ Unlimited     │
│ ✓ Match scoring │ ✓ Match scoring │ ✓ Match scoring │
│ ✓ Foundation    │ ✓ Foundation    │ ✓ Foundation    │
│   profiles      │   profiles      │   profiles      │
│ ✓ Email support │ ✓ Positioning   │ ✓ Positioning   │
│                 │   strategies    │   strategies    │
│                 │ ✓ Email support │ ✓ Grant writing │
│                 │                 │   assistance    │
│                 │                 │ ✓ Dedicated     │
│                 │                 │   support       │
│                 │                 │                 │
│ [Get Started]   │ [Get Started]   │ [Contact Sales] │
└─────────────────┴─────────────────┴─────────────────┘
```

**Pricing Notes**:
- Monthly billing (annual option at 2-month discount)
- Cancel anytime
- No long-term contracts
- Money-back guarantee (first 30 days)

**FAQ Below Pricing**:
- "Can I switch plans?" - Yes, upgrade/downgrade anytime
- "What happens after the trial?" - You'll be notified before billing starts
- "Do you offer nonprofit discounts?" - All pricing is nonprofit-friendly; contact us for multi-user discounts

---

### Section 9: FAQ

**Purpose**: Address objections and common questions.

**Headline**: "Frequently Asked Questions"

**Questions** (8-10 questions):

**1. How is TheGrantScout different from Instrumentl or Foundation Directory?**
We focus on relationship intelligence and success probability, not just keyword matching. Our AI identifies funders who already support organizations similar to yours, giving you 8x better success rates. Plus, we deliver curated weekly reports instead of making you search through thousands of listings.

**2. What types of grants do you cover?**
We track private foundation grants (990-PF data), federal government grants (SAM.gov), CDFI funding, and corporate giving programs. Our database includes 85,000+ grantmaking foundations and 1.6M+ historical grants.

**3. How do you calculate match scores?**
Our algorithm weighs four factors: 1) Prior relationships (67% weight) - does the funder support similar organizations? 2) Geographic fit (15%) - location preferences, 3) Program alignment (13%) - mission and NTEE codes, 4) Grant size fit (5%) - your budget vs typical grant amounts.

**4. How long does setup take?**
Initial profile creation takes about 5 minutes. You'll answer questions about your mission, programs, geography, budget, and grant history. The more detail you provide, the better our matches.

**5. When will I receive my first report?**
Your first weekly report arrives within 3-5 business days after completing your profile. Reports are delivered every Monday morning.

**6. Can you help write grant applications?**
Our Growth and Enterprise plans include positioning strategies and key talking points for each opportunity. Full grant writing assistance is available on Enterprise plans. We're piloting a grant writing service for 2025.

**7. Do you guarantee grant success?**
No one can guarantee grant awards, but our relationship intelligence approach yields 67% success rates vs 8% for cold outreach. We focus on quality matches over quantity.

**8. What if I don't find the opportunities relevant?**
We refine your matches based on feedback. Mark opportunities as relevant/not relevant, and our AI learns your preferences. Most users see 90%+ relevance by week 3.

**9. Can multiple staff members access the account?**
Yes, all plans include team access. Enterprise plans offer user management and role permissions.

**10. How do I cancel?**
Cancel anytime from your account dashboard. No questions asked, no penalties. Your access continues through the end of your billing period.

---

### Section 10: Final CTA

**Purpose**: Convert visitors who scrolled to the bottom.

**Content**:
**Headline**: "Ready to stop searching and start matching?"

**Subheadline**: "Join nonprofits finding better grant opportunities in less time."

**CTA Button**: "Get Your First 5 Matches Free"

**Trust Line**: "No credit card required. Cancel anytime."

**Visual**: Simple form or calendar booking widget

---

### Section 11: Footer

**Purpose**: Provide navigation, legal links, and contact info.

**Column 1: Brand**
- TheGrantScout logo
- Tagline: "AI-powered grant discovery for nonprofits"
- Social links (LinkedIn, Twitter when available)

**Column 2: Product**
- How It Works
- Features
- Pricing
- FAQ
- Roadmap

**Column 3: Resources**
- Blog (when available)
- Grant Writing Guide (when available)
- Case Studies (when available)
- Foundation Database

**Column 4: Company**
- About Us
- Contact
- Privacy Policy
- Terms of Service
- Nonprofit Partnerships

**Column 5: Contact**
- Email: hello@thegrantscout.com
- Support: support@thegrantscout.com
- Address (if available)

**Bottom Bar**:
"© 2025 TheGrantScout. Built for nonprofits, by people who understand the grant landscape."

---

## Technical Requirements

### Tech Stack

**Framework**: Next.js 14+ (App Router)
**Language**: TypeScript
**Styling**: Tailwind CSS
**Deployment**: Vercel
**Domain**: thegrantscout.com (already owned)

### Template Base

**Repository**: https://github.com/nexi-launch/finwise-landing-page
**License**: MIT
**Features**: Responsive, dark/light mode, Next.js 13+, Tailwind CSS

### Development Environment

**Node.js**: 18.x or higher
**Package Manager**: npm or yarn
**Git**: Version control

### Key Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwindcss": "^3.3.0",
    "typescript": "^5.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

### Performance Requirements

- Lighthouse Performance Score: 90+
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.0s
- Cumulative Layout Shift: < 0.1
- Mobile responsive (all breakpoints)

### SEO Requirements

**Meta Tags**:
- Title: "TheGrantScout - AI-Powered Grant Discovery for Nonprofits"
- Description: "Stop searching, start matching. TheGrantScout uses AI to find grant opportunities tailored to your nonprofit's mission and relationships. 85,000+ foundations analyzed."
- Keywords: grant discovery, nonprofit grants, foundation grants, grant matching, AI grant search
- Open Graph image: 1200x630px
- Twitter Card: summary_large_image

**Structured Data**:
- Organization schema
- Product schema (for service)
- FAQ schema

**Sitemap**: Auto-generated via Next.js
**Robots.txt**: Allow all

### Accessibility Requirements

- WCAG 2.1 Level AA compliance
- Semantic HTML
- ARIA labels where appropriate
- Keyboard navigation support
- Color contrast ratios: 4.5:1 for text
- Alt text for all images
- Focus indicators visible

### Analytics & Tracking

**Google Analytics 4**: Track page views, CTA clicks, form submissions
**Conversion Events**:
- CTA button clicks
- Pricing page views
- Form starts
- Form completions

### Forms & Lead Capture

**Trial Signup Form Fields**:
- Organization Name (required)
- Email Address (required)
- EIN (optional)
- Phone (optional)
- How did you hear about us? (optional)

**Integration Options**:
- Airtable (simple MVP)
- HubSpot (if CRM ready)
- Mailchimp (email list)
- Calendly (if doing discovery calls)

### Security

- HTTPS enforced
- Environment variables for API keys
- CSP headers configured
- No sensitive data exposed client-side

---

## Task Breakdown

### Sprint: Website Sprint 1
**Goal**: Launch professional TheGrantScout landing page
**Duration**: 3-5 days
**Team**: Builder(s)

---

### Task 1: Project Setup & Template Cloning
**Priority**: P0 (Blocking)
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Clone the Finwise template, install dependencies, and verify the development environment works.

**Acceptance Criteria**:
- [ ] Repository cloned from https://github.com/nexi-launch/finwise-landing-page
- [ ] Renamed to `thegrantscout-landing`
- [ ] Dependencies installed successfully (`npm install`)
- [ ] Development server runs (`npm run dev`)
- [ ] Template displays correctly at localhost:3000
- [ ] Git initialized for TheGrantScout version
- [ ] .gitignore configured
- [ ] README updated with TheGrantScout setup instructions

**Dependencies**: None

**Output**: Working Next.js development environment

---

### Task 2: Branding & Design System Setup
**Priority**: P0 (Blocking)
**Estimated Effort**: 1 day
**Assigned To**: Builder

**Description**:
Implement TheGrantScout brand colors, typography, and design tokens in Tailwind configuration.

**Acceptance Criteria**:
- [ ] Color palette implemented in `tailwind.config.js`
  - Primary: #1e3a5f (deep navy)
  - Accent: #d4a853 (warm gold)
  - Background: #ffffff, #f9fafb
  - Text: #2d3748
  - Secondary: #e6f0ff
- [ ] Typography configured (Inter font family)
- [ ] Responsive breakpoints defined
- [ ] Spacing scale configured
- [ ] Dark mode colors (optional for v1)
- [ ] Design tokens documented in `/docs/DESIGN_DECISIONS.md`

**Dependencies**: Task 1

**Output**: Tailwind config with TheGrantScout design system

**Technical Notes**:
- Import Google Fonts (Inter) or use local fonts
- Create custom Tailwind classes for brand colors
- Test dark/light mode toggle if keeping from template

---

### Task 3: Site Metadata & SEO Setup
**Priority**: P0 (Blocking)
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Configure site metadata, SEO tags, and Open Graph settings.

**Acceptance Criteria**:
- [ ] `siteDetails.ts` updated with TheGrantScout info
  - Site name: "TheGrantScout"
  - Tagline: "Stop searching. Start matching."
  - Description (SEO)
  - URL: thegrantscout.com
- [ ] Metadata configured in `app/layout.tsx`
  - Title template
  - Description
  - Keywords
  - Open Graph tags
  - Twitter Card tags
- [ ] Favicon files added to `/public/icons/`
  - favicon.ico
  - apple-touch-icon.png
  - favicon-16x16.png
  - favicon-32x32.png
- [ ] robots.txt created
- [ ] OG image placeholder created (1200x630px)

**Dependencies**: Task 1

**Output**: Complete SEO metadata configuration

---

### Task 4: Content Data Files
**Priority**: P1
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Create TypeScript data files with all website content.

**Acceptance Criteria**:
- [ ] `/src/data/features.ts` created with 4 features
- [ ] `/src/data/howItWorks.ts` created with 4 steps
- [ ] `/src/data/testimonials.ts` created (3 placeholder testimonials)
- [ ] `/src/data/faq.ts` created with 10 questions
- [ ] `/src/data/pricing.ts` created with pricing tier(s)
- [ ] `/src/data/siteDetails.ts` updated
- [ ] All content matches PROJECT_PLAN.md specifications
- [ ] TypeScript interfaces defined for data shapes

**Dependencies**: Task 1

**Output**: Centralized content data files

**Reference**: See "Content Outline" section above for exact copy

---

### Task 5: Hero Section Component
**Priority**: P0 (Blocking)
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Build the hero section (above-the-fold content).

**Acceptance Criteria**:
- [ ] Hero component created at `/src/components/Hero.tsx`
- [ ] Headline: "Stop searching. Start matching."
- [ ] Subheadline with value proposition
- [ ] Primary CTA button: "Get Your First 5 Matches Free"
- [ ] Secondary CTA: "See How It Works" (smooth scroll)
- [ ] Trust indicators: "85,000+ foundations | 1.6M+ grants"
- [ ] Responsive design (mobile/tablet/desktop)
- [ ] Hero background image or gradient
- [ ] CTA buttons link to signup form (placeholder for now)

**Dependencies**: Task 2 (design system)

**Output**: Completed Hero component

**Design Notes**:
- Hero should occupy 100vh on desktop, auto-height on mobile
- CTA buttons should use brand colors
- Consider animation on load (fade in, slide up)

---

### Task 6: Features Section Component
**Priority**: P0
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Build the features section showcasing 4 key value propositions.

**Acceptance Criteria**:
- [ ] Features component created at `/src/components/Features.tsx`
- [ ] Displays 4 feature cards in grid layout
- [ ] Each card includes:
  - [ ] Icon (can use placeholder icon library)
  - [ ] Title
  - [ ] Description
  - [ ] Stat callout
- [ ] Content loaded from `/src/data/features.ts`
- [ ] Responsive grid (1 col mobile, 2 col tablet, 4 col desktop)
- [ ] Hover effects on cards
- [ ] Section headline: "Why TheGrantScout finds opportunities others miss"

**Dependencies**: Task 4 (content data)

**Output**: Features section component

**Design Notes**:
- Cards should have subtle shadow and border
- Icons can use Heroicons or Lucide icons
- Consider stagger animation on scroll

---

### Task 7: How It Works Section Component
**Priority**: P0
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Build the process flow section explaining the 4-step user journey.

**Acceptance Criteria**:
- [ ] HowItWorks component created at `/src/components/HowItWorks.tsx`
- [ ] Displays 4 steps in visual flow
- [ ] Each step includes:
  - [ ] Step number
  - [ ] Icon
  - [ ] Title
  - [ ] Description
- [ ] Content loaded from `/src/data/howItWorks.ts`
- [ ] Visual connector between steps (arrow or line)
- [ ] Responsive layout (vertical on mobile, horizontal on desktop)
- [ ] Section headline: "We bring the right opportunities to you"
- [ ] CTA button at bottom: "Start Getting Matched Opportunities"

**Dependencies**: Task 4 (content data)

**Output**: How It Works component

**Design Notes**:
- Consider timeline/stepper UI pattern
- Connectors should use brand accent color
- CTA should stand out visually

---

### Task 8: Pricing Section Component
**Priority**: P1
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Build the pricing section with tier(s) and CTA.

**Acceptance Criteria**:
- [ ] Pricing component created at `/src/components/Pricing.tsx`
- [ ] Content loaded from `/src/data/pricing.ts`
- [ ] Displays pricing tier(s) as cards
- [ ] Each tier includes:
  - [ ] Tier name
  - [ ] Price
  - [ ] Feature list with checkmarks
  - [ ] CTA button
- [ ] "Early Access" badge if using single tier
- [ ] Responsive layout
- [ ] Section headline: "Simple, transparent pricing"
- [ ] Optional: Toggle for monthly/annual billing

**Dependencies**: Task 4 (content data)

**Output**: Pricing section component

**Design Notes**:
- Recommended tier should be highlighted
- Price should be large and prominent
- Feature lists should align across tiers

---

### Task 9: FAQ Section Component
**Priority**: P1
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Build the FAQ section with accordion/expandable questions.

**Acceptance Criteria**:
- [ ] FAQ component created at `/src/components/FAQ.tsx`
- [ ] Content loaded from `/src/data/faq.ts`
- [ ] 10 questions displayed
- [ ] Accordion UI (click to expand/collapse)
- [ ] Only one question open at a time (optional)
- [ ] Smooth expand/collapse animation
- [ ] Responsive layout
- [ ] Section headline: "Frequently Asked Questions"
- [ ] Search functionality (optional for v2)

**Dependencies**: Task 4 (content data)

**Output**: FAQ accordion component

**Design Notes**:
- Use + icon for closed, - icon for open
- Consider two-column layout on desktop
- Keyboard accessible (arrow keys)

---

### Task 10: Testimonials Section Component
**Priority**: P2 (Optional for v1)
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Build the social proof section with testimonials.

**Acceptance Criteria**:
- [ ] Testimonials component created at `/src/components/Testimonials.tsx`
- [ ] Content loaded from `/src/data/testimonials.ts`
- [ ] Displays 3 testimonials
- [ ] Each includes:
  - [ ] Quote
  - [ ] Name
  - [ ] Title
  - [ ] Organization
  - [ ] Photo (placeholder or real)
- [ ] Carousel/slider on mobile (optional)
- [ ] Grid layout on desktop
- [ ] Section headline: "Join nonprofits finding better opportunities, faster"

**Dependencies**: Task 4 (content data)

**Output**: Testimonials component

**Note**: Can use placeholder content initially and update with real beta feedback later.

---

### Task 11: Footer Component
**Priority**: P1
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Build the site footer with navigation and legal links.

**Acceptance Criteria**:
- [ ] Footer component created at `/src/components/Footer.tsx`
- [ ] 5-column layout (Brand, Product, Resources, Company, Contact)
- [ ] All links defined (some may be placeholders)
- [ ] Email addresses: hello@thegrantscout.com, support@thegrantscout.com
- [ ] Social media icons (LinkedIn, Twitter placeholders)
- [ ] Copyright notice: "© 2025 TheGrantScout"
- [ ] Tagline: "Built for nonprofits, by people who understand the grant landscape"
- [ ] Responsive (collapse to single column on mobile)
- [ ] Newsletter signup (optional)

**Dependencies**: Task 2 (design system)

**Output**: Footer component

**Notes**:
- Privacy Policy and Terms of Service can link to placeholder pages
- Social links can be inactive for v1

---

### Task 12: Navigation/Header Component
**Priority**: P1
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Build the site header with logo and navigation.

**Acceptance Criteria**:
- [ ] Navigation component created at `/src/components/Navigation.tsx`
- [ ] TheGrantScout logo (can use text logo initially)
- [ ] Navigation links:
  - [ ] How It Works (smooth scroll)
  - [ ] Features (smooth scroll)
  - [ ] Pricing (smooth scroll)
  - [ ] FAQ (smooth scroll)
- [ ] Primary CTA button in header: "Get Started"
- [ ] Mobile hamburger menu
- [ ] Sticky header on scroll (optional)
- [ ] Responsive design
- [ ] Dark/light mode toggle (optional, keep if from template)

**Dependencies**: Task 2 (design system)

**Output**: Header/navigation component

**Design Notes**:
- Header should be clean and minimal
- CTA button should use accent color
- Consider transparent header over hero, then solid on scroll

---

### Task 13: CTA Component (Reusable)
**Priority**: P1
**Estimated Effort**: 0.25 day
**Assigned To**: Builder

**Description**:
Create reusable CTA component used throughout the site.

**Acceptance Criteria**:
- [ ] CTA component created at `/src/components/CTA.tsx`
- [ ] Accepts props: text, variant (primary/secondary), size, onClick
- [ ] Primary variant: Brand accent color, white text
- [ ] Secondary variant: Outline style
- [ ] Hover and focus states
- [ ] Accessible (proper ARIA labels)
- [ ] Loading state (optional)
- [ ] Icon support (optional)

**Dependencies**: Task 2 (design system)

**Output**: Reusable button/CTA component

**Usage**: Used in Hero, sections, pricing, etc.

---

### Task 14: Homepage Assembly
**Priority**: P0
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Assemble all components into the homepage and ensure proper layout.

**Acceptance Criteria**:
- [ ] All components imported in `/src/app/page.tsx`
- [ ] Components arranged in correct order:
  1. Hero
  2. How It Works
  3. Features
  4. Testimonials (if ready)
  5. Pricing
  6. FAQ
  7. Final CTA section
- [ ] Smooth scroll between sections
- [ ] Proper spacing between sections
- [ ] Section backgrounds alternate (white/off-white)
- [ ] No layout shift issues
- [ ] Footer included
- [ ] Navigation included

**Dependencies**: Tasks 5-12

**Output**: Complete homepage

---

### Task 15: Responsiveness & Cross-Browser Testing
**Priority**: P0
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Test and fix responsive design across devices and browsers.

**Acceptance Criteria**:
- [ ] Test on mobile (375px, 414px widths)
- [ ] Test on tablet (768px, 1024px widths)
- [ ] Test on desktop (1280px, 1440px, 1920px widths)
- [ ] Test on Chrome, Firefox, Safari, Edge
- [ ] No horizontal scroll on any breakpoint
- [ ] All text readable at all sizes
- [ ] CTAs accessible with thumb on mobile
- [ ] Images load and scale properly
- [ ] No layout breaks
- [ ] Touch targets minimum 44x44px on mobile

**Dependencies**: Task 14

**Output**: Fully responsive site

**Testing Tools**:
- Chrome DevTools device emulation
- BrowserStack (if available)
- Real devices (if available)

---

### Task 16: Performance Optimization
**Priority**: P1
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Optimize site performance for fast load times.

**Acceptance Criteria**:
- [ ] Images optimized (Next.js Image component)
- [ ] Fonts optimized (next/font)
- [ ] Lazy load images below fold
- [ ] Minimize JavaScript bundle size
- [ ] Enable Next.js static generation where possible
- [ ] Lighthouse Performance score 90+
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3.0s
- [ ] Cumulative Layout Shift < 0.1
- [ ] Remove unused CSS
- [ ] Minify production build

**Dependencies**: Task 14

**Output**: Optimized production build

**Tools**:
- Lighthouse CI
- WebPageTest
- Chrome DevTools Performance tab

---

### Task 17: Accessibility Audit
**Priority**: P1
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Ensure site meets WCAG 2.1 Level AA standards.

**Acceptance Criteria**:
- [ ] All images have alt text
- [ ] Headings follow proper hierarchy (h1 > h2 > h3)
- [ ] Color contrast ratios meet 4.5:1 minimum
- [ ] Keyboard navigation works (tab through site)
- [ ] Focus indicators visible
- [ ] ARIA labels on interactive elements
- [ ] Form inputs have labels
- [ ] Skip to content link (optional)
- [ ] No accessibility errors in Lighthouse
- [ ] Screen reader tested (VoiceOver or NVDA)

**Dependencies**: Task 14

**Output**: WCAG AA compliant site

**Tools**:
- Lighthouse accessibility audit
- axe DevTools
- WAVE browser extension
- Screen reader (VoiceOver, NVDA)

---

### Task 18: Analytics & Tracking Setup
**Priority**: P2
**Estimated Effort**: 0.25 day
**Assigned To**: Builder

**Description**:
Implement Google Analytics 4 and conversion tracking.

**Acceptance Criteria**:
- [ ] Google Analytics 4 installed
- [ ] GA4 measurement ID in environment variables
- [ ] Pageview tracking working
- [ ] CTA click events tracked
- [ ] Form submission events tracked (when form exists)
- [ ] Pricing page view event tracked
- [ ] Privacy-compliant (cookie consent if required)

**Dependencies**: Task 14

**Output**: Working analytics

**Events to Track**:
- `cta_click` (which CTA, which section)
- `pricing_view`
- `faq_expand` (which question)
- `form_start`
- `form_complete`

---

### Task 19: Lead Capture Form (Optional for v1)
**Priority**: P2
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Create signup form for trial/early access.

**Acceptance Criteria**:
- [ ] Form component created
- [ ] Fields: Organization Name, Email, EIN (optional), Phone (optional)
- [ ] Client-side validation
- [ ] Submit to Airtable/HubSpot/other backend
- [ ] Success message after submission
- [ ] Error handling
- [ ] Loading state during submission
- [ ] Privacy policy checkbox
- [ ] Form accessible (keyboard, screen reader)

**Dependencies**: Task 14

**Output**: Working lead capture form

**Alternative**: Link to Calendly or Typeform for v1 instead of custom form.

---

### Task 20: Deployment to Vercel
**Priority**: P0
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Deploy site to Vercel and connect custom domain.

**Acceptance Criteria**:
- [ ] Vercel account created/connected
- [ ] Repository connected to Vercel
- [ ] Environment variables configured
- [ ] Production build deploys successfully
- [ ] Preview URL generated
- [ ] Custom domain (thegrantscout.com) connected
- [ ] SSL certificate active (HTTPS)
- [ ] DNS configured correctly
- [ ] Site accessible at https://thegrantscout.com
- [ ] www redirect configured (www.thegrantscout.com -> thegrantscout.com)

**Dependencies**: Tasks 14-17

**Output**: Live production site

**Deployment Steps**:
1. Push code to GitHub
2. Connect GitHub repo to Vercel
3. Configure build settings (Next.js auto-detected)
4. Add environment variables
5. Deploy
6. Add custom domain in Vercel settings
7. Update DNS records at domain registrar
8. Verify deployment

---

### Task 21: Documentation & Handoff
**Priority**: P1
**Estimated Effort**: 0.5 day
**Assigned To**: Builder

**Description**:
Create documentation for maintaining and updating the site.

**Acceptance Criteria**:
- [ ] README.md updated with:
  - [ ] Setup instructions
  - [ ] Development commands
  - [ ] Deployment process
  - [ ] Environment variables needed
- [ ] `/docs/DESIGN_DECISIONS.md` created with:
  - [ ] Color choices
  - [ ] Font choices
  - [ ] Component patterns
- [ ] `/docs/CONTENT_GUIDE.md` created with:
  - [ ] How to update copy
  - [ ] Content file locations
  - [ ] Brand voice guidelines
- [ ] `/docs/DEPLOYMENT_LOG.md` created with:
  - [ ] Deployment history
  - [ ] Environment setup
  - [ ] Known issues
- [ ] Code comments added to complex components

**Dependencies**: Task 20

**Output**: Complete documentation

---

## Deployment Plan

### Pre-Deployment Checklist

**Content Review**:
- [ ] All copy proofread for typos and grammar
- [ ] Brand voice consistent throughout
- [ ] CTAs clear and compelling
- [ ] Contact information accurate
- [ ] Legal pages ready (Privacy Policy, Terms of Service)

**Technical Review**:
- [ ] All components rendering correctly
- [ ] No console errors in browser
- [ ] No broken links
- [ ] Forms working (if applicable)
- [ ] Analytics tracking verified
- [ ] SEO metadata complete
- [ ] Favicon displaying

**Performance**:
- [ ] Lighthouse score 90+ (Performance, Accessibility, SEO)
- [ ] Load time < 3 seconds
- [ ] Mobile responsive
- [ ] Cross-browser tested

**Domain & Hosting**:
- [ ] Domain registered (thegrantscout.com - confirmed owned)
- [ ] DNS records ready
- [ ] SSL certificate ready (Vercel provides)
- [ ] Email addresses configured (hello@, support@)

### Deployment Steps

**Step 1: Staging Deployment**
1. Deploy to Vercel preview URL
2. Full QA testing on preview URL
3. Stakeholder review
4. Fix any issues

**Step 2: Production Deployment**
1. Merge to main branch
2. Vercel auto-deploys to production
3. Connect custom domain (thegrantscout.com)
4. Verify DNS propagation
5. Test live site

**Step 3: Post-Launch**
1. Submit sitemap to Google Search Console
2. Set up Google Analytics property
3. Monitor error logs
4. Monitor analytics for issues
5. Gather initial feedback

### Rollback Plan

If critical issues found post-launch:
1. Revert to previous Vercel deployment (one-click)
2. Fix issues in development
3. Re-deploy when ready

---

## Quality Checklist

### Design Quality

- [ ] Visual hierarchy clear (headlines > body > CTAs)
- [ ] Whitespace used effectively (not cramped)
- [ ] Colors consistent with brand guidelines
- [ ] Typography readable at all sizes
- [ ] Images high quality (not pixelated)
- [ ] Icons consistent style
- [ ] Hover states on interactive elements
- [ ] Loading states on async actions
- [ ] Error states handled gracefully
- [ ] Brand consistency throughout

### Content Quality

- [ ] Headlines grab attention
- [ ] Value proposition clear within 5 seconds
- [ ] Benefits emphasized over features
- [ ] Social proof included (testimonials, stats)
- [ ] CTAs clear and action-oriented
- [ ] No jargon or unclear terms
- [ ] Tone appropriate for audience (nonprofits)
- [ ] Grammar and spelling perfect
- [ ] All facts and stats accurate
- [ ] Contact information correct

### Technical Quality

- [ ] Site loads in < 3 seconds
- [ ] No JavaScript errors in console
- [ ] No broken links (404s)
- [ ] No broken images
- [ ] Forms validate properly
- [ ] Mobile responsive (all breakpoints)
- [ ] Cross-browser compatible
- [ ] Accessible (WCAG AA)
- [ ] SEO optimized (meta tags, headings, alt text)
- [ ] Analytics tracking working
- [ ] HTTPS enabled
- [ ] Proper error handling

### Conversion Optimization

- [ ] Clear primary CTA above fold
- [ ] Multiple CTAs throughout page
- [ ] CTA text action-oriented ("Get Started" not "Submit")
- [ ] Friction reduced (minimal form fields)
- [ ] Trust signals present (testimonials, stats, guarantees)
- [ ] Value proposition repeated throughout
- [ ] Objections addressed (FAQ)
- [ ] Urgency created (limited spots, launch pricing)
- [ ] Social proof visible
- [ ] Easy to contact (email visible)

---

## Success Metrics

### Launch Metrics (Week 1)

**Traffic**:
- Unique visitors
- Page views
- Bounce rate (target: < 60%)
- Avg time on page (target: > 2 minutes)

**Engagement**:
- CTA click rate (target: > 5%)
- FAQ interactions
- Pricing page views
- Full page scrolls (target: > 30%)

**Conversion**:
- Form submissions / trial signups
- Contact form fills
- Calendly bookings (if applicable)
- Conversion rate (target: 2-5% for cold traffic)

**Technical**:
- Page load time (target: < 3s)
- Lighthouse scores (target: 90+ all categories)
- Error rate (target: < 0.1%)
- Uptime (target: 99.9%)

### Iteration Plan

**Week 2-4**:
- Review analytics data
- Identify drop-off points
- A/B test headlines and CTAs
- Gather user feedback
- Iterate on content based on data

---

## Phase 2 Features (Future)

Not included in MVP, but planned for future iterations:

1. **Blog/Content Marketing**
   - Grant writing guides
   - Foundation spotlights
   - Nonprofit success stories

2. **Interactive Tools**
   - Grant readiness assessment quiz
   - Foundation match calculator
   - ROI calculator

3. **Enhanced Forms**
   - Multi-step onboarding wizard
   - Conditional logic based on org type
   - File uploads (990 forms)

4. **User Dashboard Preview**
   - Mock dashboard screenshots
   - Interactive demo

5. **Video Content**
   - Explainer video on hero
   - Founder story video
   - Product demo video

6. **Live Chat**
   - Chatbot for FAQ
   - Live support during business hours

7. **Localization**
   - Spanish language version (high priority for nonprofit sector)

8. **Advanced Analytics**
   - Heatmaps (Hotjar)
   - Session recordings
   - Funnel analysis

---

## Project Completion Criteria

The Website Sprint 1 is complete when:

1. **Site is live** at thegrantscout.com
2. **All sections implemented**: Hero, How It Works, Features, Pricing, FAQ, Footer
3. **Mobile responsive** and cross-browser tested
4. **Performance targets met**: Lighthouse 90+, load time < 3s
5. **Accessibility compliant**: WCAG 2.1 Level AA
6. **Analytics tracking** implemented and verified
7. **Documentation complete**: README, design decisions, content guide
8. **Zero critical bugs**: No broken functionality
9. **Stakeholder approved**: Final review and sign-off

---

## Team Communication

### Daily Updates

Builder should provide end-of-day updates including:
- Tasks completed
- Tasks in progress
- Blockers or questions
- Preview links for review

### Log Events to Mailbox

Log significant milestones:
```json
{"timestamp":"2025-11-30T...", "event":"website_sprint_started", "sprint":"Website Sprint 1", "tasks":21, "team":"dev", "actor":"builder"}
{"timestamp":"...", "event":"task_completed", "task_id":"task-website-01", "task":"Project Setup", "team":"dev", "actor":"builder"}
{"timestamp":"...", "event":"website_deployed", "url":"https://thegrantscout.com", "environment":"production", "team":"dev", "actor":"builder"}
```

### Questions & Decisions

If questions arise:
1. Document in `/docs/DESIGN_DECISIONS.md`
2. Tag Project Manager for guidance
3. Make reasonable assumptions and document them

---

## Appendix: Reference Links

### Template & Inspiration
- Finwise Template: https://github.com/nexi-launch/finwise-landing-page
- Finwise Demo: https://finwise-omega.vercel.app

### Tools & Resources
- Next.js Docs: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com/docs
- Vercel Deployment: https://vercel.com/docs
- Heroicons: https://heroicons.com
- Google Fonts: https://fonts.google.com

### Design Inspiration
- Stripe: https://stripe.com (clean, conversion-focused)
- Notion: https://notion.so (clear value prop)
- Airtable: https://airtable.com (visual process flow)
- Instrumentl: https://instrumentl.com (competitor example)

### Accessibility
- WCAG Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- axe DevTools: https://www.deque.com/axe/devtools/

---

**End of Project Plan**

**Next Steps**:
1. Project Manager assigns tasks to Builder(s)
2. Builder begins with Task 1 (Project Setup)
3. Daily progress updates
4. Launch in 3-5 days

**Questions?** Contact Project Manager or reference this plan.
