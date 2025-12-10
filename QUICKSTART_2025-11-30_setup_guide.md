# TheGrantScout Landing Page - Complete Setup Guide

## Quick Start

### Step 1: Install Dependencies

```bash
cd "/mnt/c/Business Factory (Research) 11-1-2025/01_VALIDATED_IDEAS/TIER_1_BOOTSTRAPPED/IDEA_062_Grant_Alerts/TheGrantScout/3. Website/thegrantscout-landing"
npm install
```

### Step 2: Run Development Server

```bash
npm run dev
```

The site will be available at [http://localhost:3000](http://localhost:3000)

### Step 3: Build for Production

```bash
npm run build
npm start
```

## Project Overview

This is a production-ready Next.js 14 landing page for TheGrantScout, featuring:

- **Modern Stack**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Brand Colors**: Deep Navy (#1e3a5f), Warm Gold (#d4a853)
- **Font**: Inter from Google Fonts
- **Fully Responsive**: Mobile-first design
- **SEO Optimized**: Meta tags, semantic HTML

## File Structure

```
thegrantscout-landing/
│
├── src/
│   └── app/
│       ├── globals.css          # Tailwind imports + custom styles
│       ├── layout.tsx            # Root layout with metadata
│       └── page.tsx              # Main landing page
│
├── public/                       # Static assets (add images here)
│
├── Configuration Files:
├── package.json                  # Dependencies
├── tailwind.config.js            # Custom colors & fonts
├── tsconfig.json                 # TypeScript config
├── next.config.js                # Next.js config
├── postcss.config.js             # PostCSS config
├── .eslintrc.json                # ESLint config
├── .gitignore                    # Git ignore rules
│
└── Documentation:
    ├── README.md                 # Project readme
    └── SETUP_GUIDE.md            # This file
```

## Page Sections

The landing page (`src/app/page.tsx`) includes:

1. **Navigation Bar** - Fixed header with smooth scroll links
2. **Hero Section** - Main headline with CTA button
3. **How It Works** - 4-step process explanation
4. **Features** - 4 key features in card format
5. **Pricing** - 3 pricing tiers (Starter, Professional, Enterprise)
6. **FAQ** - 8 questions with accordion functionality
7. **CTA Section** - Lead capture form
8. **Footer** - Links and copyright

## Customization Guide

### Change Colors

Edit `tailwind.config.js`:

```javascript
colors: {
  primary: {
    DEFAULT: '#1e3a5f',  // Your navy color
    dark: '#152b47',
    light: '#2d5a8e',
  },
  accent: {
    DEFAULT: '#d4a853',  // Your gold color
    dark: '#b8923d',
    light: '#e6c680',
  },
}
```

### Change Content

All content is in `src/app/page.tsx`. Each section is clearly marked with comments:

```typescript
{/* Hero Section */}
{/* How It Works */}
{/* Features */}
// etc.
```

### Add Images/Logos

1. Place images in the `public/` directory
2. Reference them in components:

```typescript
<img src="/logo.png" alt="Logo" />
```

### Change Fonts

The project uses Inter from Google Fonts. To change:

1. Edit `src/app/layout.tsx`:

```typescript
import { YourFont } from 'next/font/google'

const yourFont = YourFont({
  subsets: ['latin'],
  variable: '--font-your-font',
})
```

2. Update `tailwind.config.js`:

```javascript
fontFamily: {
  sans: ['var(--font-your-font)', 'sans-serif'],
}
```

## Development Tips

### Run Linter

```bash
npm run lint
```

### Check TypeScript Errors

TypeScript will show errors in your IDE. To check manually:

```bash
npx tsc --noEmit
```

### Format Code

Install Prettier (optional):

```bash
npm install -D prettier
```

## Deployment Options

### Option 1: Vercel (Recommended)

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Vercel auto-detects Next.js and deploys

### Option 2: Netlify

1. Push code to GitHub
2. Go to [netlify.com](https://netlify.com)
3. Import repository
4. Build command: `npm run build`
5. Publish directory: `.next`

### Option 3: Traditional Hosting

Build static export:

1. Update `next.config.js`:

```javascript
const nextConfig = {
  output: 'export',
}
```

2. Build:

```bash
npm run build
```

3. Upload the `out/` directory to your host

## Environment Variables

If you add environment variables later:

1. Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://api.example.com
```

2. Access in code:

```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL
```

## Adding Features

### Connect Contact Form

The form in the CTA section is currently non-functional. To connect it:

1. Set up a form service (FormSpree, Netlify Forms, etc.)
2. Update the form in `src/app/page.tsx`

Example with FormSpree:

```typescript
<form action="https://formspree.io/f/YOUR_ID" method="POST">
  {/* form fields */}
</form>
```

### Add Analytics

Google Analytics:

1. Install package:

```bash
npm install @next/third-parties
```

2. Add to `src/app/layout.tsx`:

```typescript
import { GoogleAnalytics } from '@next/third-parties/google'

// In the component:
<GoogleAnalytics gaId="G-XXXXXXXXXX" />
```

## Troubleshooting

### Port Already in Use

If port 3000 is busy:

```bash
npm run dev -- -p 3001
```

### Build Errors

Clear cache and rebuild:

```bash
rm -rf .next
npm run build
```

### Style Not Updating

1. Stop dev server
2. Delete `.next` folder
3. Restart: `npm run dev`

## Performance Optimization

The site is already optimized with:

- Server-side rendering (Next.js)
- Automatic code splitting
- Image optimization (add next/image for images)
- Font optimization (Google Fonts via next/font)

### Further Optimizations

1. **Add next/image** for images:

```typescript
import Image from 'next/image'

<Image src="/hero.jpg" width={500} height={300} alt="Hero" />
```

2. **Enable compression** in `next.config.js`:

```javascript
const nextConfig = {
  compress: true,
}
```

## Security Notes

- Never commit `.env.local` (already in .gitignore)
- Keep dependencies updated: `npm audit`
- Use HTTPS in production

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## Next Steps

1. Add your logo to `public/`
2. Connect the contact form
3. Add Google Analytics
4. Set up custom domain
5. Test on mobile devices
6. Run Lighthouse audit in Chrome DevTools
7. Deploy to Vercel/Netlify

## Support

For issues with:
- **Next.js**: [nextjs.org/docs](https://nextjs.org/docs)
- **Tailwind**: [tailwindcss.com/docs](https://tailwindcss.com/docs)
- **TypeScript**: [typescriptlang.org/docs](https://typescriptlang.org/docs)

## License

Copyright 2024 TheGrantScout. All rights reserved.
