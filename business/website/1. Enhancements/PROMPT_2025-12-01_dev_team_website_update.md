# Dev Team Prompt: TheGrantScout Website Updates

## Project Overview

Implement website improvements to TheGrantScout landing page based on research recommendations. The goal is to better communicate the value of IRS-verified data and curated matching.

**Website Code Location:**
```
C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\3. Website\thegrantscout-landing
```

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS

**Key File:** `src/app/page.tsx`

---

## Important Notes

1. **KEEP the current tagline**: "Your mission deserves funding. We'll help you find it."
2. **KEEP the current color scheme** (navy #1e3a5f, gold #d4a853)
3. **DO NOT include FAQ section changes** in this update
4. **Focus on**: Adding trust indicators, updating feature copy, adding IRS data emphasis

---

## Changes to Implement

### 1. Hero Section Updates

**Location:** Lines 72-93 in `page.tsx`

**Add Trust Indicators Below Hero CTA**

After line 90 (`<p className="text-gray-300 mt-6 text-sm">No credit card required</p>`), add:

```tsx
{/* Trust Indicators */}
<div className="flex flex-wrap justify-center gap-4 md:gap-8 mt-8 text-gray-200 text-sm">
  <div className="flex items-center gap-2">
    <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
    <span>IRS-Verified Data</span>
  </div>
  <div className="flex items-center gap-2">
    <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>
    <span>1.6M+ Grants Analyzed</span>
  </div>
  <div className="flex items-center gap-2">
    <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
    <span>85,000+ Foundations</span>
  </div>
</div>
```

---

### 2. Add New Section: "Built on Authoritative Data" (After Hero, Before How It Works)

**Add this new section between the Hero and "How It Works" sections:**

```tsx
{/* Data Authority Section */}
<section className="py-16 md:py-20 bg-white border-b border-gray-100">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="text-center mb-12">
      <span className="inline-block px-4 py-1 bg-primary/10 text-primary rounded-full text-sm font-semibold mb-4">OUR DATA ADVANTAGE</span>
      <h2 className="text-3xl md:text-4xl font-bold text-primary mb-4">Built on the Most Authoritative Foundation Data</h2>
      <p className="text-xl text-gray-600 max-w-2xl mx-auto">
        Every match is grounded in official IRS filings—not web scraping or incomplete databases.
      </p>
    </div>

    <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
      {/* IRS Verified */}
      <div className="text-center p-6">
        <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <div className="text-3xl font-bold text-primary mb-2">IRS 990-PF</div>
        <div className="text-gray-600">Verified Data Source</div>
        <p className="text-sm text-gray-500 mt-2">Official foundation tax filings—the same data used by major research institutions.</p>
      </div>

      {/* Grants Analyzed */}
      <div className="text-center p-6">
        <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div className="text-3xl font-bold text-primary mb-2">1.6M+</div>
        <div className="text-gray-600">Grants Analyzed</div>
        <p className="text-sm text-gray-500 mt-2">Comprehensive giving history to identify foundations funding work like yours.</p>
      </div>

      {/* Years of Data */}
      <div className="text-center p-6">
        <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="text-3xl font-bold text-primary mb-2">8 Years</div>
        <div className="text-gray-600">Of Giving Patterns</div>
        <p className="text-sm text-gray-500 mt-2">Analyze trends from 2016-2024 to find consistent funders in your space.</p>
      </div>
    </div>
  </div>
</section>
```

---

### 3. Update "How It Works" Step 2 Copy

**Location:** Lines 119-127 in `page.tsx`

**Current:**
```tsx
<h3 className="text-xl font-semibold text-primary mb-3">AI Analyzes Patterns</h3>
<p className="text-gray-600">
  Our AI scans 85,000+ foundations to find those funding similar missions.
</p>
```

**Change to:**
```tsx
<h3 className="text-xl font-semibold text-primary mb-3">AI Analyzes IRS Data</h3>
<p className="text-gray-600">
  Our AI analyzes 1.6M+ grants from IRS Form 990-PF filings to identify foundations funding similar missions.
</p>
```

---

### 4. Update Features Section

**Location:** Lines 161-213 in `page.tsx`

#### Feature 1: Smart Matching

**Current (Line 172):**
```tsx
<div className="mt-4 text-sm text-accent font-semibold">67% higher success rate</div>
```

**Change to:**
```tsx
<div className="mt-4 text-sm text-accent font-semibold">Curated matches from verified data</div>
```

**Also update the description (Lines 168-171):**

**Current:**
```tsx
<p className="text-gray-600">
  Our AI analyzes foundation giving patterns to match you with funders who have a proven track record of supporting missions like yours.
</p>
```

**Change to:**
```tsx
<p className="text-gray-600">
  We analyze 8 years of IRS-verified giving data to match you with foundations that have a proven track record of funding organizations like yours.
</p>
```

---

### 5. Update Footer Description

**Location:** Lines 432-434 in `page.tsx`

**Current:**
```tsx
<p className="text-gray-300 leading-relaxed">
  AI-powered grant matching for nonprofits who deserve funding.
</p>
```

**Change to:**
```tsx
<p className="text-gray-300 leading-relaxed">
  AI-powered grant matching built on IRS-verified data. Helping nonprofits find foundations already funding work like theirs.
</p>
```

---

## Summary of Changes

| Section | Change Type | Description |
|---------|-------------|-------------|
| Hero | Add | Trust indicators (IRS-Verified, 1.6M grants, 85K foundations) |
| New Section | Add | "Built on Authoritative Data" section after hero |
| How It Works | Update | Step 2 copy to emphasize IRS data |
| Features | Update | Remove "67% higher success rate", replace with "Curated matches" |
| Features | Update | Smart Matching description to emphasize verified data |
| Footer | Update | Description to mention IRS-verified data |

---

## Testing Checklist

After implementing changes:

- [ ] Hero trust indicators display correctly on desktop and mobile
- [ ] New "Data Authority" section renders properly
- [ ] All icons display correctly
- [ ] Responsive layout works on mobile (trust indicators should wrap)
- [ ] Colors match existing theme (navy #1e3a5f, gold #d4a853)
- [ ] No TypeScript errors
- [ ] Run `npm run build` to verify production build succeeds

---

## Design Guidelines

**Keep existing design patterns:**
- Same card styles
- Same button styles (.btn-primary, .btn-secondary)
- Same section spacing (section-container class)
- Same typography (heading-2, heading-3 classes)

**Color usage:**
- Primary (navy): #1e3a5f - for headings and primary elements
- Accent (gold): #d4a853 - for highlights, icons, badges
- Gray-600: #4b5563 - for body text
- Gray-200: #e5e7eb - for light text on dark backgrounds

---

## Files to Modify

1. `src/app/page.tsx` - Main page component (all changes above)

No other files need modification.

---

## Notes for Dev Team

1. The tagline "Your mission deserves funding. We'll help you find it." stays exactly as-is
2. Do NOT modify the FAQ section in this update
3. The new "Data Authority" section should be inserted BETWEEN the hero section and "How It Works" section
4. All copy is provided exactly as written - do not modify wording
5. If any icons are unclear, use similar icons from the existing icon set (Heroicons outline style)
