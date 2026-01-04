# Technical SEO Implementation

## Situation
TheGrantScout website needs technical SEO foundations to appear in search results. Currently invisible to Google. Site is Next.js.

## Tasks

1. **First, check current state:**
   - Look at `layout.tsx` for existing meta tags
   - Check if sitemap.xml, robots.txt already exist
   - Check if any schema markup exists
   - Report what's already in place

2. **Add sitemap generation:**
   - Install `next-sitemap` package
   - Configure for thegrantscout.com
   - Include main page, /privacy, /terms

3. **Add robots.txt:**
   - Allow all crawlers
   - Reference sitemap location

4. **Enhance meta tags in layout.tsx:**
   - Open Graph tags (title, description, url, siteName, type)
   - Twitter card tags (summary_large_image)
   - Keywords meta tag
   - Canonical URL
   - robots: index, follow

5. **Add JSON-LD structured data:**
   - Organization schema (name, url, description)
   - FAQPage schema for the FAQ section (extract existing Q&As)
   - SoftwareApplication or Service schema with pricing ($99/month)

## Notes
- Site URL: https://thegrantscout.com
- Pricing: $99/month
- Description: AI-powered grant matching for nonprofits, analyzes 85,000+ foundations and 1.6M+ grants

## Output
After implementation, list what was added/changed so I can verify before deploying.
