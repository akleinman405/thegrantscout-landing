# TheGrantScout CTA Implementation Guide

## Current CTA Setup (As of 2025-12-04)

### Primary CTA: Book a Call
All primary call-to-action buttons now link to Calendly:
```
https://calendly.com/alec_kleinman/meeting-with-alec
```

### Secondary CTA: Sample Report
Links to a downloadable PDF sample report:
```
/sample-report.pdf
```
Located in: `public/sample-report.pdf`

---

## How to Collect Form Responses (Future Options)

If you want to capture leads before/instead of sending them directly to Calendly, here are several approaches:

### Option 1: Calendly Native (Current - Recommended)
**Pros:** Zero development, instant scheduling, automatic reminders
**Cons:** Limited customization of pre-meeting questions

**How to get responses:**
1. Log into Calendly dashboard
2. Go to "Scheduled Events" or "Analytics"
3. Export booking data as CSV
4. Or use Calendly integrations (Zapier, native CRM integrations)

**Calendly Integrations:**
- Zapier (send to Google Sheets, Notion, CRM, etc.)
- Native integrations: HubSpot, Salesforce, Mailchimp
- Webhooks for custom integrations

### Option 2: Add a Form Before Calendly
Collect info first, then redirect to Calendly.

**Implementation (Next.js API Route):**

```typescript
// src/app/api/lead/route.ts
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const data = await request.json()

  // Option A: Send to Google Sheets via Sheets API
  // Option B: Send to Airtable
  // Option C: Send to your email via SendGrid/Resend
  // Option D: Store in database (Supabase, PlanetScale, etc.)

  // Example: Send to Google Sheets via API
  await fetch('https://sheets.googleapis.com/v4/spreadsheets/YOUR_SHEET_ID/values/Sheet1!A:E:append', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.GOOGLE_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      values: [[
        data.name,
        data.email,
        data.organization,
        data.fundingGoals,
        new Date().toISOString()
      ]]
    })
  })

  return NextResponse.json({ success: true })
}
```

### Option 3: Use a Form Service (No-Code)
**Best for quick setup without backend work:**

1. **Typeform** - Beautiful forms, easy setup
   - Create form at typeform.com
   - Embed or link from your site
   - Auto-exports to Google Sheets, Notion, etc.

2. **Tally.so** - Free, clean forms
   - Create at tally.so
   - Embed or redirect
   - Integrations with Zapier, webhooks

3. **Google Forms** - Free, simple
   - Auto-saves to Google Sheets
   - Less polished but functional

### Option 4: Email-Based Lead Capture
Simple approach: form submits to your email.

**Using Resend (recommended for Next.js):**

```bash
npm install resend
```

```typescript
// src/app/api/contact/route.ts
import { Resend } from 'resend'
import { NextResponse } from 'next/server'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function POST(request: Request) {
  const { name, email, organization, fundingGoals } = await request.json()

  await resend.emails.send({
    from: 'leads@thegrantscout.com',
    to: 'alec@thegrantscout.com',
    subject: `New Lead: ${organization}`,
    html: `
      <h2>New Lead from TheGrantScout</h2>
      <p><strong>Name:</strong> ${name}</p>
      <p><strong>Email:</strong> ${email}</p>
      <p><strong>Organization:</strong> ${organization}</p>
      <p><strong>Funding Goals:</strong> ${fundingGoals}</p>
    `
  })

  return NextResponse.json({ success: true })
}
```

**Environment variable needed:**
```
RESEND_API_KEY=re_xxxxxxxxxxxxx
```

### Option 5: Use Existing Modal + Backend
The website already has a contact modal. To activate it:

1. The modal form already posts to `/api/contact`
2. Create the API route to handle submissions
3. Store/forward the data as needed

**Current form fields captured:**
- Name
- Organization
- Email
- Funding Goals

---

## Recommended Setup for Sales Calls

### Immediate (Current Setup)
- Primary CTA: Direct to Calendly (implemented)
- Secondary CTA: Sample report PDF download (implemented)
- **Tracking:** Use Calendly dashboard + integrations

### Enhanced (If you want pre-call qualification)
1. Keep "Book a Call" button
2. Add a short Typeform/Tally form before Calendly redirect
3. Form asks 2-3 qualifying questions
4. On submit, redirect to Calendly link
5. Data flows to Google Sheets via Zapier

### Full CRM Integration
1. Set up HubSpot Free (or similar)
2. Connect Calendly to HubSpot
3. All bookings create contacts automatically
4. Track pipeline and follow-ups

---

## File Locations

| Item | Location |
|------|----------|
| Main page with CTAs | `src/app/page.tsx` |
| Sample report PDF | `public/sample-report.pdf` |
| API routes (if needed) | `src/app/api/` |
| Styles | `src/app/globals.css` |

---

## Quick Reference: Changing the Calendly Link

To change the Calendly URL, search and replace in `src/app/page.tsx`:
```
https://calendly.com/alec_kleinman/meeting-with-alec
```

The link appears in:
1. Desktop nav button
2. Mobile nav button
3. Hero section CTA
4. Pricing section CTA
5. Bottom CTA section
