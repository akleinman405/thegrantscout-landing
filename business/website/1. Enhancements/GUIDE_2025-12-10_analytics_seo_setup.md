# Analytics & SEO Setup Guide

**Date:** December 10, 2025

---

## Part 1: Google Analytics 4 Setup

### Step 1: Create GA4 Property

1. Go to [analytics.google.com](https://analytics.google.com)
2. Click **Admin** (gear icon)
3. Click **Create Property**
4. Enter property name: `TheGrantScout`
5. Select timezone and currency
6. Click **Next**, select "Business" industry
7. Click **Create**

### Step 2: Set Up Data Stream

1. Choose **Web** platform
2. Enter website URL: `https://thegrantscout.com`
3. Enter stream name: `TheGrantScout Website`
4. Click **Create stream**
5. **Copy the Measurement ID** (format: `G-XXXXXXXXXX`)

### Step 3: Add Measurement ID to Website

Create a `.env.local` file in the website root:

```
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

Replace `G-XXXXXXXXXX` with your actual Measurement ID.

The tracking code is already installed in the website. Once you add this environment variable and redeploy, GA4 will start collecting data.

### Step 4: Verify Installation

1. Visit your website
2. In GA4, go to **Reports > Realtime**
3. You should see your visit appear within seconds

---

## Part 2: Google Search Console Setup

### Step 1: Add Property

1. Go to [search.google.com/search-console](https://search.google.com/search-console)
2. Click **Add Property**
3. Choose **URL prefix** method
4. Enter: `https://thegrantscout.com`
5. Click **Continue**

### Step 2: Verify Ownership

**Recommended: HTML file method**

1. Download the verification HTML file Google provides
2. Add it to `/public/` folder in the website
3. Deploy the website
4. Click **Verify** in Search Console

**Alternative: DNS verification**

1. Add the TXT record Google provides to your domain's DNS settings
2. Wait for DNS propagation (can take up to 48 hours)
3. Click **Verify** in Search Console

### Step 3: Submit Sitemap

1. In Search Console, go to **Sitemaps**
2. Enter: `sitemap.xml`
3. Click **Submit**

The sitemap is auto-generated at `/sitemap.xml` by the website.

### Step 4: Request Indexing

1. Go to **URL Inspection**
2. Enter your homepage URL
3. Click **Request Indexing**
4. Repeat for `/privacy` and `/terms` pages

---

## Part 3: Connect GA4 and Search Console

1. In GA4, go to **Admin > Product Links**
2. Click **Search Console Links**
3. Click **Link**
4. Select your Search Console property
5. Click **Next** and **Submit**

This allows you to see search query data in GA4.

---

## Part 4: Set Up Conversions in GA4

### Track "Book a Call" as a Conversion

1. In GA4, go to **Configure > Events**
2. Find the `click` event (will appear after first clicks are recorded)
3. Click the three dots, select **Mark as conversion**

Or create a custom conversion:
1. Go to **Configure > Conversions**
2. Click **New conversion event**
3. Enter event name: `click`
4. Add condition: `event_label contains book_call`

---

## Part 5: CTA Click Events Reference

The website tracks these events automatically:

| Event Label | Location | Description |
|-------------|----------|-------------|
| `book_call_nav` | Top navigation | Desktop nav "Book a Call" |
| `book_call_mobile_nav` | Mobile menu | Mobile nav "Book a Call" |
| `book_call_hero` | Hero section | Main hero CTA button |
| `book_call_pricing` | Pricing card | Pricing section CTA |
| `book_call_cta_bottom` | Bottom CTA | Final CTA section |
| `sample_report_hero` | Hero section | "See Sample Report" link |
| `sample_report_pricing` | Pricing section | Sample report link |
| `sample_report_cta_bottom` | Bottom CTA | Sample report link |

### View Events in GA4

1. Go to **Reports > Engagement > Events**
2. Click on the `click` event
3. Add secondary dimension: `Event label`
4. See breakdown by CTA location

---

## Part 6: Daily CSV Dashboard (Future)

Once GA4 is collecting data, I can help set up a Python script that:
1. Pulls data from GA4 API daily
2. Appends to a CSV file with columns:
   - Date
   - Page views
   - Sessions
   - Users
   - Book a Call clicks (by location)
   - Sample Report clicks (by location)
   - Bounce rate

This requires:
1. A Google Cloud project
2. GA4 Data API enabled
3. Service account credentials

Let me know when you're ready to set this up.

---

## Checklist

- [ ] Create GA4 property
- [ ] Copy Measurement ID
- [ ] Add `.env.local` with Measurement ID
- [ ] Redeploy website
- [ ] Verify GA4 is receiving data
- [ ] Set up Search Console
- [ ] Verify domain ownership
- [ ] Submit sitemap
- [ ] Request indexing for pages
- [ ] Link GA4 and Search Console
- [ ] Set up conversion tracking
