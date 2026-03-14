# CLAUDE.md — TheGrantScout Website

**Repo:** `akleinman405/thegrantscout-landing` (separate from monorepo)
**Stack:** Next.js 14 + TypeScript + Tailwind CSS
**Host:** Netlify (auto-deploys on push to `main`)

---

## Quick Reference

| Item | Value |
|------|-------|
| Framework | Next.js 14.0.4 (App Router) |
| Styling | Tailwind CSS 3.3 |
| Fonts | Inter (body) + Raleway (headings) |
| Primary color | `#1e3a5f` (navy) |
| Accent color | `#d4a853` (gold) |
| Domain | thegrantscout.com |
| Netlify plugin | `@netlify/plugin-nextjs` |

---

## Commands

```bash
npm run dev        # localhost:3000
npm run build      # Build check (run before deploy)
npm run lint       # ESLint
git push origin main  # Deploy via Netlify auto-deploy
netlify deploy --prod # Instant deploy without git
```

---

## Routes

| Route | Purpose |
|-------|---------|
| `/` | Landing page |
| `/signup` | Self-service signup (multi-step form → Stripe Checkout) |
| `/signup/success` | Post-payment confirmation |
| `/how-to-use-your-report` | Interactive report guide |
| `/sample-report` | Sample report viewer |
| `/privacy` | Privacy policy |
| `/terms` | Terms of service |

## API Routes

| Route | Purpose |
|-------|---------|
| `/api/contact` | Contact form handler |
| `/api/checkout` | Creates Stripe Checkout Session |
| `/api/webhooks/stripe` | Stripe webhook handler |

---

## Design System

**CSS classes** (defined in `globals.css`):
- `btn-primary` — Gold button with navy text
- `btn-secondary` — Outlined navy button
- `form-input-mobile` — Touch-friendly input (min 48px, 16px font)
- `form-textarea-mobile` — Touch-friendly textarea
- `heading-1`, `heading-2`, `heading-3` — Heading styles
- `section-container` — Max-width centered section
- `card` — Elevated card with hover effect

**Tailwind colors:** `primary`, `primary-dark`, `primary-light`, `accent`, `accent-dark`, `accent-light`, `charcoal`, `success`, `error`

---

## Environment Variables

```
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_MONTHLY=price_...
STRIPE_PRICE_ID_ANNUAL=price_...
RESEND_API_KEY=re_...
DATABASE_URL=postgresql://...
ADMIN_EMAIL=alec@thegrantscout.com
```

---

## Project Structure

```
src/
├── app/
│   ├── api/
│   │   ├── checkout/route.ts
│   │   ├── contact/route.ts
│   │   └── webhooks/stripe/route.ts
│   ├── signup/
│   │   ├── page.tsx
│   │   └── success/page.tsx
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── signup/
│   │   ├── FormField.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── StepOrganization.tsx
│   │   ├── StepMission.tsx
│   │   ├── StepCapacity.tsx
│   │   ├── StepPreferences.tsx
│   │   └── StepReview.tsx
│   ├── GoogleAnalytics.tsx
│   └── StructuredData.tsx
├── hooks/
│   └── useSignupForm.ts
└── lib/
    ├── db.ts
    ├── email.ts
    └── signup-types.ts
```

---

## Gotchas

| Issue | Solution |
|-------|----------|
| iOS zooms on input focus | Use `font-size: 16px` (already in `form-input-mobile`) |
| Stripe webhook needs raw body | Use `request.text()` not `request.json()` in webhook handler |
| Netlify env vars | Set via Netlify dashboard, not `.env.local` |
| This is NOT the monorepo | Website changes go here, not in `TheGrantScout/` |
