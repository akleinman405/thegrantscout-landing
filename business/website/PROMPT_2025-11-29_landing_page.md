# Dev Team Prompt: TheGrantScout Landing Page

## Overview
Clone and customize the Finwise SaaS landing page template for TheGrantScout - a grant discovery and matching service for nonprofits.

## Template Source
- **Repository**: https://github.com/nexi-launch/finwise-landing-page
- **Demo**: https://finwise-omega.vercel.app
- **Stack**: Next.js + Tailwind CSS (MIT License)

## Setup Instructions
```bash
git clone https://github.com/nexi-launch/finwise-landing-page.git thegrantscout-landing
cd thegrantscout-landing
npm install
npm run dev
```

## Brand & Content Customization

### Site Details (`/src/data/siteDetails.ts`)
- **Name**: TheGrantScout
- **Tagline**: "Find the grants that find you"
- **Description**: AI-powered grant discovery that matches nonprofits with funding opportunities based on their mission, history, and funder relationships.

### Color Palette (update `globals.css`)
Use a professional, trust-building palette:
- **Primary**: Deep navy (#1e3a5f) or forest green (#2d5a47)
- **Accent**: Warm gold (#d4a853) or teal (#3d9991)
- **Background**: Clean white/off-white
- **Text**: Dark charcoal (#2d3748)

### Hero Section
**Headline**: "Stop searching. Start matching."
**Subheadline**: "TheGrantScout uses AI to find grant opportunities tailored to your nonprofit's mission, track record, and funder relationships."
**CTA**: "Get Your First 5 Matches Free" or "See How It Works"

### Features Section (3-4 key features)
1. **Smart Matching** - Our algorithm analyzes 85,000+ foundations and 1.6M+ historical grants to find opportunities where you have the highest chance of success.
2. **Relationship Intelligence** - We identify funders who already support organizations like yours. Prior relationships mean 67% success rates vs 8% for cold outreach.
3. **Weekly Opportunity Reports** - Receive 5-10 curated, prioritized opportunities with positioning strategies and application guidance.
4. **Foundation Profiles** - Deep insights into funder behavior, grant patterns, and what makes applications successful.

### How It Works Section
1. **Tell us about your nonprofit** - Mission, programs, geography, grant history
2. **We scan the landscape** - AI analyzes thousands of funders and opportunities daily
3. **Get matched opportunities** - Weekly reports with your best-fit grants, ranked by success probability
4. **Apply with confidence** - Each match includes positioning strategies and key insights

### Testimonials/Social Proof
(Placeholder for now - can add beta user quotes later)
- "TheGrantScout found opportunities we never would have discovered on our own."
- Include logos of beta orgs if permitted

### Pricing Section
**Option A - Simple**:
- "Early Access" - $X/month - Weekly reports, 5-10 opportunities, foundation insights

**Option B - Tiered** (if ready):
- Starter: $99/mo - 5 opportunities/week
- Growth: $249/mo - 10 opportunities/week + positioning strategies
- Enterprise: Custom - Full grant writing support

### FAQ Section
- "How is this different from Instrumentl?" → We focus on relationship intelligence and success probability, not just keyword matching.
- "What types of grants do you cover?" → Private foundations, government grants (SAM.gov), CDFIs, and corporate giving programs.
- "How do you calculate match scores?" → Our algorithm weighs prior relationships (67% weight), geographic fit, program alignment, and grant size fit.
- "Can you help write the applications?" → Coming soon - we're piloting full grant writing services.

### Footer
- Links: About, How It Works, Pricing, Contact, Privacy Policy
- Contact email
- "Built for nonprofits, by people who understand the grant landscape"

## Technical Notes
- Keep the existing responsive design and dark/light mode toggle
- Replace favicon with TheGrantScout logo (or placeholder)
- Update Open Graph images for social sharing
- Ensure all CTAs link to a signup form or Calendly booking link

## Deployment
Deploy to Vercel for quick hosting:
```bash
npm run build
vercel deploy
```

## Output
When complete, provide:
1. GitHub repo link (if created)
2. Live Vercel preview URL
3. List of any customization decisions made
