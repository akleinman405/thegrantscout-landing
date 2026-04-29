# CLAUDE.md — TheGrantScout Landing Site

**Repo:** `akleinman405/thegrantscout-landing` (separate from monorepo)
**Stack:** Next.js 14 + TypeScript + Tailwind CSS
**Host:** Netlify (auto-deploys on push to `main`)
**Netlify site:** `thegrantscout-landing` (ID: `c514132b-8ab4-4341-96e9-d936f2bb06b7`)
**Custom domain:** `thegrantscout.com` (DNS via Cloudflare → Netlify)

> **WARNING:** This repo contains a stale `src/app/(crm)/` route group with old CRM pages. **Do NOT use it.** The active CRM is in a separate repo: `thegrantscout-crm/` deployed at `app.thegrantscout.com`. This repo is only for the marketing site, signup flow, and Stripe webhook.

> **SCHEMA RULE:** All Supabase schema changes MUST go through a numbered migration file in `supabase/migrations/`. Never edit columns/tables directly in Supabase Studio. Drift like that broke every signup for ~8 days in April 2026 (see migration 014 for the postmortem). Apply migrations via Supabase MCP `execute_dml_ddl_dcl_tcl`, then commit the `.sql` file in the same change.

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
npm run dev               # localhost:3000
npm run build             # Build check (run before deploy)
npm run lint              # ESLint
git push origin main      # Deploy via Netlify auto-deploy
netlify deploy --build --prod  # Build + deploy without git push (use when auto-deploy isn't triggering)
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

## CRM Routes (STALE — do not use)

> These routes exist in the codebase but are **superseded** by the `thegrantscout-crm` repo at `app.thegrantscout.com`. Do not modify or rely on them.

| Route | Status |
|-------|--------|
| `/crm/*` | STALE — replaced by `thegrantscout-crm` repo |
| `/api/crm/*` | STALE — replaced by `thegrantscout-crm` repo |

## API Routes (Active — this repo)

| Route | Purpose |
|-------|---------|
| `/api/contact` | Contact form handler |
| `/api/checkout` | Creates Stripe Checkout Session |
| `/api/webhooks/stripe` | Stripe webhook (updates subscribers + organizations on payment events) |

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

**Build-time (must be in Netlify env for build to succeed):**
```
NEXT_PUBLIC_SUPABASE_URL=https://...supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

**Runtime-only (needed for API routes/functions, not during build):**
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_MONTHLY=price_...
STRIPE_PRICE_ID_ANNUAL=price_...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DATABASE_URL=postgresql://...
RESEND_API_KEY=re_...
CRM_SECRET=...
CRM_PASSWORD=...
ADMIN_EMAIL=alec@thegrantscout.com  (has default fallback)
```

**Local only (.env.local, not needed in Netlify):**
```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
CONTACT_EMAIL=...
```

---

## Supabase Schema

**Database:** Supabase (hosted). Tables in `public` schema.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `organizations` | CRM master entity (clients, leads, nonprofits, funders) | `ein` (unique), `name`, `type`, `stage`, `locations` (JSONB), `stripe_*`, `subscription_*`, `contact_*`, `reports_sent_count` |
| `subscribers` | Signup form submissions (immutable audit log) | `ein`, `org_name`, `contact_*`, `locations` (JSONB), `stripe_*`, `subscription_status`, `plan_type` |
| `people` | Contacts linked to organizations | `org_id` FK, `first_name`, `last_name`, `email`, `title`, `linkedin_url` |
| `timeline_events` | Activity feed per org | `org_id` FK, `event_type`, `summary`, `details` (JSONB) |
| `tasks` | Follow-up tasks | `org_id` FK, `title`, `due_date`, `completed` |
| `follow_ups` | Scheduled follow-ups | `org_id` FK, `action`, `due_date`, `completed` |
| `meetings` | Meeting records | `org_id` FK, `meeting_date`, `summary`, `action_items` (JSONB) |
| `reports` | Client report tracking | `org_id` FK, `period`, `status`, `report_type`, `delivered_at` |
| `notes` | Freeform notes per org | `org_id` FK, `content`, `pinned` |
| `dripify_imports` | CSV import tracking | `filename`, `stats_data` (JSONB) |

### Signup → CRM Flow

1. User fills multi-step form at `/signup` → `INSERT INTO subscribers`
2. User completes Stripe Checkout → webhook fires `checkout.session.completed`
3. Webhook updates `subscribers.stripe_*` fields and `subscription_status = 'active'`
4. Webhook upserts `organizations` record (type=client, stage=active) with Stripe + contact data
5. Webhook sends welcome email (Resend) + internal notification email

**Key:** The webhook uses Supabase client (not `DATABASE_URL`/`query()`), so it works in Netlify serverless.

---

## Project Structure

```
src/
├── app/
│   ├── (crm)/
│   │   ├── CRMShell.tsx              # CRM layout wrapper (sidebar, auth gate)
│   │   ├── crm/
│   │   │   ├── page.tsx              # Dashboard
│   │   │   ├── login/page.tsx        # CRM login
│   │   │   ├── orgs/page.tsx         # Organizations list (tabbed)
│   │   │   ├── orgs/[slug]/page.tsx  # Org detail
│   │   │   ├── people/page.tsx       # People directory
│   │   │   └── people/[id]/page.tsx  # Person detail
│   │   └── layout.tsx
│   ├── api/
│   │   ├── checkout/route.ts
│   │   ├── contact/route.ts
│   │   ├── crm/
│   │   │   ├── dashboard/route.ts
│   │   │   ├── orgs/[slug]/route.ts
│   │   │   ├── orgs/[slug]/brief/route.ts
│   │   │   ├── people/route.ts
│   │   │   └── people/[id]/route.ts
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
    ├── supabase.ts
    └── signup-types.ts
supabase/
└── migrations/         # Run in order against Supabase SQL editor
    ├── 001_initial_schema.sql
    ├── 002_mockup_columns.sql
    ├── 003_subscribers.sql
    ├── 010_subscribers_playbook_fields.sql
    └── 011_organizations_locations.sql
```

---

## Audit Results

**IMPORTANT — Saving Audit Results:**
When running any audit (AuditBuffet or otherwise) against this project, always save the full JSON results to `audits/`. Use the naming convention:

```
audits/AUDIT_YYYY-MM-DD_audit-name.json
```

Examples:
- `audits/AUDIT_2026-03-18_api-security.json`
- `audits/AUDIT_2026-03-18_security-headers.json`

If the audit produces a markdown summary or recommendations, save that alongside the JSON:
- `audits/AUDIT_YYYY-MM-DD_audit-name.md`

This creates a persistent record of audit scores over time so we can track progress toward target grades.

---

## Gotchas

| Issue | Solution |
|-------|----------|
| iOS zooms on input focus | Use `font-size: 16px` (already in `form-input-mobile`) |
| Stripe webhook needs raw body | Use `request.text()` not `request.json()` in webhook handler |
| Netlify env vars | Set via Netlify dashboard, not `.env.local` |
| This is NOT the monorepo | Website changes go here, not in `TheGrantScout/` |
| Custom domain serves old build | Verify `thegrantscout.com` is on Netlify site `thegrantscout-landing` (not another site). Use `netlify deploy --build --prod` to force rebuild. |
| Auto-deploy not triggering | Check GitHub webhook connection in Netlify dashboard. Fallback: `netlify deploy --build --prod` |
| Build fails on Supabase | `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` must be set in Netlify env (build-time requirement) |
| `netlify deploys` CLI crash | Known bug in netlify-cli 23.x with Node 25. Use `netlify api listSiteDeploys --data '{"site_id":"c514132b-..."}'` instead |
| Em dash renders as `\u2014` | Netlify build encoding issue. Use JS escape `'\u2014'` or `{'\u2014'}` in JSX, not literal `—` character |
| Webhook fails on Netlify | Webhook must use Supabase client, not `query()`/`DATABASE_URL`. The `query()` import from `@/lib/db` requires `DATABASE_URL` which may not be set or may point to a different DB. |
