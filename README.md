# TheGrantScout Landing Page

AI-powered grant matching for nonprofits. Built with Next.js 14, TypeScript, and Tailwind CSS.

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm or yarn

### Installation

1. Install dependencies:

```bash
npm install
```

2. Run the development server:

```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
thegrantscout-landing/
├── src/
│   └── app/
│       ├── globals.css      # Global styles and Tailwind
│       ├── layout.tsx        # Root layout with Inter font
│       └── page.tsx          # Main landing page
├── public/                   # Static assets
├── tailwind.config.js        # Tailwind configuration
├── tsconfig.json            # TypeScript configuration
├── next.config.js           # Next.js configuration
└── package.json             # Dependencies
```

## Brand Colors

- **Primary (Deep Navy)**: #1e3a5f
- **Accent (Warm Gold)**: #d4a853
- **Background**: #ffffff
- **Text (Charcoal)**: #2d3748

## Features

- Responsive design (mobile-first)
- Server-side rendering with Next.js 14
- TypeScript for type safety
- Tailwind CSS for styling
- Google Fonts (Inter)
- Smooth scroll navigation
- Interactive FAQ accordion
- Contact form
- SEO optimized

## Sections

1. **Navigation** - Fixed header with logo and links
2. **Hero** - Main value proposition with CTA
3. **How It Works** - 4-step process
4. **Features** - 4 key features in cards
5. **Pricing** - 3 pricing tiers
6. **FAQ** - 8 common questions with accordion
7. **CTA** - Lead capture form
8. **Footer** - Links and legal info

## Customization

To customize the content, edit `src/app/page.tsx`. The page is structured with clear section comments.

To change colors, update `tailwind.config.js` and the CSS variables in `src/app/globals.css`.

## Deployment

This project is ready to deploy on Vercel, Netlify, or any platform that supports Next.js.

### Deploy on Vercel

1. Push to GitHub
2. Import project to Vercel
3. Deploy

## License

Copyright 2024 TheGrantScout. All rights reserved.
