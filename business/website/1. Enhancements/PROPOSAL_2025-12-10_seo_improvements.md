# SEO Improvement Proposal for TheGrantScout

**Date:** December 10, 2025
**Status:** Proposal

---

## Executive Summary

This document outlines recommended SEO improvements for TheGrantScout landing page to increase organic search visibility for nonprofits searching for grant funding solutions.

---

## Current State

The site has basic SEO elements in place:
- Title tag and meta description in `layout.tsx`
- Semantic HTML structure
- Mobile-responsive design

**Missing or underdeveloped:**
- No sitemap.xml
- No robots.txt
- Limited meta tags (no Open Graph, Twitter cards)
- Single-page site limits keyword targeting
- No structured data (Schema.org)
- No blog/content for long-tail keywords

---

## Recommended Improvements

### Priority 1: Technical SEO Foundations

| Item | Description | Effort |
|------|-------------|--------|
| **Add sitemap.xml** | Auto-generate with `next-sitemap` package | Low |
| **Add robots.txt** | Allow search engine crawling | Low |
| **Open Graph tags** | Better social sharing previews (Facebook, LinkedIn) | Low |
| **Twitter Card tags** | Better Twitter sharing previews | Low |
| **Canonical URLs** | Prevent duplicate content issues | Low |

### Priority 2: On-Page SEO

| Item | Description | Effort |
|------|-------------|--------|
| **Structured data** | Add Organization and Service schema (JSON-LD) | Medium |
| **Alt text for images** | Add descriptive alt text to any images/icons | Low |
| **Internal linking** | Link between Privacy, Terms, and main page | Low |
| **H1 optimization** | Ensure single H1 with primary keyword | Low |
| **Page speed** | Optimize images, enable caching headers | Medium |

### Priority 3: Content & Keywords

**Target Keywords (suggested):**
- Primary: "grant matching for nonprofits", "find foundation grants"
- Secondary: "nonprofit grant search", "foundation funding database", "AI grant matching"
- Long-tail: "how to find foundations that fund [cause]", "private foundation grants for nonprofits"

| Item | Description | Effort |
|------|-------------|--------|
| **Blog/Resources section** | Create content targeting long-tail keywords | High |
| **FAQ page expansion** | Dedicated FAQ page with more questions | Medium |
| **Location pages** | "Grant matching for California nonprofits" etc. | High |
| **Case studies** | Client success stories (when available) | Medium |

### Priority 4: Off-Page SEO

| Item | Description | Effort |
|------|-------------|--------|
| **Google Business Profile** | If applicable for local presence | Low |
| **Nonprofit directory listings** | List on nonprofit resource sites | Medium |
| **Guest content** | Articles on nonprofit blogs/publications | High |
| **Backlink building** | Outreach for quality backlinks | High |

---

## Implementation: Quick Wins

These can be implemented in the current `layout.tsx` with minimal effort:

```tsx
// Enhanced metadata for layout.tsx
export const metadata: Metadata = {
  title: 'TheGrantScout - AI-Powered Grant Matching for Nonprofits',
  description: 'Find foundations already funding work like yours. TheGrantScout uses AI to match nonprofits with grant opportunities from 85,000+ foundations and 1.6M+ grants.',
  keywords: 'grant matching, nonprofit grants, foundation funding, AI grant search, find foundation grants, nonprofit funding',
  authors: [{ name: 'TheGrantScout' }],
  openGraph: {
    title: 'TheGrantScout - AI-Powered Grant Matching for Nonprofits',
    description: 'Find foundations already funding work like yours. Monthly reports with curated opportunities, funder intel, and positioning strategy.',
    url: 'https://thegrantscout.com',
    siteName: 'TheGrantScout',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TheGrantScout - AI-Powered Grant Matching for Nonprofits',
    description: 'Find foundations already funding work like yours.',
  },
  robots: {
    index: true,
    follow: true,
  },
}
```

---

## Structured Data Example

Add to layout or page for rich search results:

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "TheGrantScout",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "description": "AI-powered grant matching service for nonprofits",
  "offers": {
    "@type": "Offer",
    "price": "99",
    "priceCurrency": "USD",
    "priceValidUntil": "2025-12-31"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "5",
    "ratingCount": "5"
  }
}
```

---

## Recommended Tools

| Tool | Purpose | Cost |
|------|---------|------|
| Google Search Console | Monitor search performance, indexing | Free |
| Google Analytics 4 | Track traffic sources, user behavior | Free |
| Ahrefs or SEMrush | Keyword research, competitor analysis | Paid |
| Screaming Frog | Technical SEO audits | Free (limited) |

---

## Measurement

Track these metrics monthly:
- Organic search impressions and clicks (Search Console)
- Keyword rankings for target terms
- Organic traffic to site (GA4)
- Conversion rate from organic traffic

---

## Recommended Implementation Order

1. **Week 1:** Technical foundations (sitemap, robots.txt, meta tags)
2. **Week 2:** Structured data, Open Graph tags
3. **Week 3:** Set up Search Console and GA4
4. **Ongoing:** Content creation, backlink building

---

## Notes

- SEO is a long-term strategy; expect 3-6 months for meaningful organic traffic growth
- The single-page design limits keyword targeting; consider adding dedicated pages for key topics
- Quality backlinks from nonprofit industry sites will have the most impact
