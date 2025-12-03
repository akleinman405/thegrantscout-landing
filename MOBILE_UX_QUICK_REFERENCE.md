# Mobile UX Quick Reference Card

**For:** TheGrantScout Developers
**Last Updated:** 2025-12-02

---

## Critical Numbers (Commit to Memory)

| Metric | Value | Standard |
|--------|-------|----------|
| Minimum touch target | **44x44px** | WCAG 2.1 AAA / Apple iOS |
| Recommended touch target | **48x48px** | Material Design / Android |
| Body text minimum | **16px** | WCAG / UX Best Practice |
| Line height for body | **1.5-1.6x** | WCAG 1.4.12 |
| Line height for headings | **1.2-1.3x** | Design systems standard |
| Contrast ratio (normal text) | **4.5:1** | WCAG AA |
| Contrast ratio (large text) | **3:1** | WCAG AA (18px+) |
| Touch target spacing | **8px min** | Material Design |
| LCP target | **< 2.5s** | Core Web Vitals |
| INP target | **< 200ms** | Core Web Vitals (2024) |
| Mobile line length | **30-50 chars** | Readability standard |

---

## Tailwind Mobile Patterns (Copy-Paste Ready)

### Sticky Footer CTA
```jsx
<div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg p-4 z-50 md:hidden">
  <button className="w-full min-h-[48px] bg-primary text-white rounded-lg font-semibold">
    Start Free Trial
  </button>
</div>
```

### Bottom Sheet Modal
```jsx
<div className="fixed inset-x-0 bottom-0 bg-white rounded-t-2xl shadow-xl
  transform translate-y-0 transition-transform max-h-[90vh] overflow-y-auto z-50">
  <button className="absolute top-4 left-4 w-10 h-10 flex items-center justify-center">
    ✕
  </button>
  {/* Content */}
</div>
```

### Touch-Friendly Input
```jsx
<input
  type="email"
  autoComplete="email"
  className="w-full h-12 px-4 border rounded-lg text-base"
  placeholder="you@nonprofit.org"
/>
```

### Responsive Typography
```jsx
<h1 className="text-3xl md:text-4xl lg:text-5xl font-bold leading-tight">
  Headline
</h1>
<p className="text-base leading-relaxed max-w-[40ch] md:max-w-prose">
  Body text
</p>
```

### Image Optimization (Hero/LCP)
```jsx
<Image
  src="/hero.jpg"
  width={800}
  height={600}
  priority={true}
  fetchpriority="high"
  alt="Grant funding for nonprofits"
/>
```

### Image Optimization (Below Fold)
```jsx
<Image
  src="/feature.jpg"
  width={600}
  height={400}
  loading="lazy"
  alt="Feature description"
/>
```

### Thumb-Zone Button Layout
```jsx
<div className="flex flex-col gap-3 sm:flex-row">
  <button className="min-h-[48px] px-6 bg-primary text-white rounded-lg">
    Primary
  </button>
  <button className="min-h-[48px] px-6 border rounded-lg">
    Secondary
  </button>
</div>
```

### Condensed Sticky Header
```jsx
const [scrolled, setScrolled] = useState(false);

useEffect(() => {
  const handleScroll = () => setScrolled(window.scrollY > 50);
  window.addEventListener('scroll', handleScroll);
  return () => window.removeEventListener('scroll', handleScroll);
}, []);

<header className={`sticky top-0 z-50 bg-white transition-all ${
  scrolled ? 'h-14 shadow-md' : 'h-20'
}`}>
  <div className="flex justify-between items-center h-full px-4">
    <Logo />
    <button className="w-12 h-12 md:hidden">☰</button>
  </div>
</header>
```

### Mobile-First Grid
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => <Card key={item.id} />)}
</div>
```

### Accessible Modal (Headless UI)
```jsx
import { Dialog } from '@headlessui/react'

<Dialog open={isOpen} onClose={() => setIsOpen(false)} className="relative z-50">
  <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

  <div className="fixed inset-0 flex items-center justify-center p-4">
    <Dialog.Panel className="w-full max-w-md bg-white rounded-lg p-6">
      <Dialog.Title className="text-xl font-bold mb-4">
        Contact Us
      </Dialog.Title>
      {/* Form content */}
    </Dialog.Panel>
  </div>
</Dialog>
```

---

## Mobile Breakpoints (Tailwind Defaults)

```
(no prefix) → 0px       [Mobile default]
sm:         → 640px     [Large phones, small tablets]
md:         → 768px     [Tablets]
lg:         → 1024px    [Laptops]
xl:         → 1280px    [Desktops]
2xl:        → 1536px    [Large screens]
```

**Remember:** Tailwind is mobile-first. Write base styles without prefix, add larger breakpoints as needed.

---

## Accessibility Checklist

### Touch Targets
- [ ] All buttons minimum 44x44px
- [ ] All links minimum 44x44px
- [ ] All form inputs minimum 44px height
- [ ] All icon buttons minimum 44x44px
- [ ] 8px spacing between adjacent targets

### Typography
- [ ] Body text minimum 16px
- [ ] Line height 1.5x+ for body text
- [ ] Maximum 4 different font sizes
- [ ] Text resizable to 200% (use rem/em)

### Color Contrast
- [ ] Normal text: 4.5:1 minimum
- [ ] Large text (18px+): 3:1 minimum
- [ ] Test with WebAIM checker

### Keyboard & Screen Readers
- [ ] All modals have focus trap
- [ ] ESC key closes modals
- [ ] Tab navigation logical order
- [ ] Icon-only buttons have aria-label
- [ ] Form labels always visible (not placeholder-only)

### Images
- [ ] Hero image: NO lazy loading, has fetchpriority="high"
- [ ] Below-fold images: lazy loading enabled
- [ ] All images have width/height attributes
- [ ] All images have descriptive alt text

---

## Common Mistakes to Avoid

❌ **DON'T:**
- Lazy load hero/above-fold images
- Use placeholder-only form labels
- Make touch targets smaller than 44x44px
- Use hover effects on mobile
- Use fixed px for font sizes
- Stack multiple modals
- Hide critical navigation behind hamburger only

✅ **DO:**
- Use fetchpriority="high" on LCP image
- Use persistent labels + autocomplete on forms
- Test on actual mobile devices
- Implement progressive disclosure
- Use relative units (rem/em)
- Provide multiple access points to key actions
- Add sticky CTA for easy access

---

## Testing Commands

### Lighthouse Mobile Audit
```bash
# Chrome DevTools → Lighthouse → Mobile → Run audit
# Target: 90+ performance score
```

### Device Simulation
```bash
# Chrome DevTools → Toggle device toolbar (Cmd/Ctrl + Shift + M)
# Test: iPhone SE (375px), iPhone 12 (390px), Pixel 5 (393px)
```

### Network Throttling
```bash
# Chrome DevTools → Network → Throttling → Slow 3G
# Test page load time (target: < 5 seconds)
```

### Touch Visualization
```bash
# Chrome DevTools → Settings → Experiments →
# Enable "Emulation: Show touch event listeners"
```

---

## Performance Optimization Priority

### Critical (Do First)
1. Remove lazy loading from hero image
2. Add fetchpriority="high" to LCP element
3. Convert images to WebP
4. Set image width/height attributes
5. Minimize above-fold CSS/JS

### Important (Do Soon)
1. Implement responsive images (srcset)
2. Enable Next.js Image optimization
3. Remove mobile hover effects
4. Add loading states
5. Optimize font loading

### Nice to Have
1. Implement scroll animations
2. Add micro-interactions
3. Optimize third-party scripts
4. Implement service worker

---

## Trust Signal Patterns

### Logo Wall
```jsx
<section className="bg-gray-50 py-8">
  <p className="text-center text-sm text-gray-600 mb-4">
    Trusted by leading nonprofits
  </p>
  <div className="flex flex-wrap justify-center gap-6 opacity-60">
    <Image src="/client-1.png" width={80} height={40} alt="Client name" />
    <Image src="/client-2.png" width={80} height={40} alt="Client name" />
  </div>
</section>
```

### Mobile Testimonial
```jsx
<div className="bg-white p-6 rounded-lg shadow">
  <div className="flex items-center gap-3 mb-3">
    <Image
      src="/avatar.jpg"
      width={48}
      height={48}
      className="rounded-full"
      alt=""
    />
    <div>
      <p className="font-semibold text-base">Sarah Johnson</p>
      <p className="text-sm text-gray-600">Director, ABC Nonprofit</p>
    </div>
  </div>
  <div className="flex mb-2">⭐⭐⭐⭐⭐</div>
  <p className="text-gray-700 leading-relaxed">
    "TheGrantScout helped us secure $250k in funding this year."
  </p>
</div>
```

### Rating Badge
```jsx
<div className="flex items-center gap-2">
  <div className="flex text-yellow-400">★★★★★</div>
  <span className="text-sm text-gray-600">4.8/5 from 200+ nonprofits</span>
</div>
```

---

## Form Best Practices

### Progressive Form (Step 1)
```jsx
<form className="space-y-4">
  <div>
    <label className="block text-sm font-medium mb-1">
      Email Address
    </label>
    <input
      type="email"
      autoComplete="email"
      className="w-full h-12 px-4 border rounded-lg"
      placeholder="you@nonprofit.org"
    />
  </div>
  <button className="w-full h-14 bg-primary text-white rounded-lg font-semibold">
    Get Started
  </button>
</form>
```

### Input Types for Optimal Keyboards
```jsx
<input type="email" inputMode="email" autoComplete="email" />
<input type="tel" inputMode="tel" autoComplete="tel" />
<input type="url" inputMode="url" autoComplete="url" />
<input type="text" inputMode="numeric" /> {/* Numbers only */}
```

### Inline Validation
```jsx
{error && (
  <p className="text-sm text-red-600 mt-1 flex items-center gap-1">
    <AlertIcon className="w-4 h-4" />
    {error}
  </p>
)}
```

---

## Conversion Optimization Cheat Sheet

### Hero Section Must-Haves
- [ ] Clear outcome-focused headline (not feature-focused)
- [ ] Sub-headline with social proof ("Used by 500+ nonprofits")
- [ ] Primary CTA in thumb zone or sticky
- [ ] Trust badge (security, rating, certification)
- [ ] Hero image optimized (priority, fetchpriority)

### CTA Optimization
- [ ] Action-oriented copy ("Find My Grants" not "Submit")
- [ ] High contrast color
- [ ] Minimum 48x48px size
- [ ] Visible without scrolling (or sticky)
- [ ] Loading state on click

### Trust Building
- [ ] Logo wall above fold
- [ ] 1-2 testimonials with photos
- [ ] Star rating near CTA
- [ ] Specific success metrics ("$250k in funding")
- [ ] Security badges

---

## Resources

**Contrast Checker:** https://webaim.org/resources/contrastchecker/
**Lighthouse:** Chrome DevTools → Lighthouse tab
**WCAG Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
**Tailwind Docs:** https://tailwindcss.com/docs/responsive-design
**Headless UI:** https://headlessui.com/ (accessible components)

---

## Quick Wins (< 1 Hour)

1. Add sticky footer CTA on mobile
2. Increase form input heights to 48px
3. Add fetchpriority="high" to hero image
4. Fix any touch targets below 44x44px
5. Add autocomplete attributes to form fields
6. Verify all text meets contrast ratios
7. Add aria-labels to icon-only buttons
8. Enable Next.js Image optimization
9. Add trust badge to hero section
10. Change CTA copy to outcome-focused

Implement these 10 items for immediate impact on conversions and accessibility.

---

**Remember:** Test on real devices, not just simulators. User experience varies significantly between Chrome DevTools and actual iPhone/Android hardware.
