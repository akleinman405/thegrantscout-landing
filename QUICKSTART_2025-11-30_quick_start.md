# TheGrantScout - Quick Start Guide

## Install & Run (3 Commands)

```bash
# Navigate to project
cd "/mnt/c/Business Factory (Research) 11-1-2025/01_VALIDATED_IDEAS/TIER_1_BOOTSTRAPPED/IDEA_062_Grant_Alerts/TheGrantScout/3. Website/thegrantscout-landing"

# Install dependencies
npm install

# Start development server
npm run dev
```

Open browser to: **http://localhost:3000**

## Project Structure

```
thegrantscout-landing/
├── src/app/
│   ├── page.tsx       # Main landing page (edit content here)
│   ├── layout.tsx     # Root layout
│   └── globals.css    # Styles
├── public/            # Add images/logos here
└── package.json       # Dependencies
```

## Brand Colors (Already Configured)

- Primary Navy: `#1e3a5f`
- Accent Gold: `#d4a853`
- Text Charcoal: `#2d3748`

Use in code: `bg-primary`, `text-accent`, `text-charcoal`

## Key Files

| File | Purpose |
|------|---------|
| `src/app/page.tsx` | Edit all page content here |
| `tailwind.config.js` | Change colors/fonts |
| `src/app/globals.css` | Custom styles |
| `package.json` | Dependencies |

## Common Tasks

### Change Content
Edit `src/app/page.tsx` - all sections are clearly marked with comments

### Add Logo
1. Put logo in `public/logo.png`
2. Update nav in `src/app/page.tsx`:
```tsx
<img src="/logo.png" alt="TheGrantScout" className="h-8" />
```

### Change Colors
Edit `tailwind.config.js` colors section

### Build for Production
```bash
npm run build
npm start
```

## Deployment

### Vercel (Easiest)
1. Push to GitHub
2. Import to Vercel.com
3. Auto-deploys

### Netlify
1. Push to GitHub
2. Import to Netlify.com
3. Build: `npm run build`

## Landing Page Sections

1. Navigation (fixed header)
2. Hero (main headline + CTA)
3. How It Works (4 steps)
4. Features (4 cards)
5. Pricing (3 tiers)
6. FAQ (8 questions)
7. CTA Form
8. Footer

## Need Help?

- Full setup: Read `SETUP_GUIDE.md`
- Project details: Read `PROJECT_SUMMARY.md`
- Next.js docs: https://nextjs.org/docs
- Tailwind docs: https://tailwindcss.com/docs

## Tech Stack

- Next.js 14 (React framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Inter font (Google Fonts)

---

**Status**: Ready to use
**To start**: `npm install && npm run dev`
