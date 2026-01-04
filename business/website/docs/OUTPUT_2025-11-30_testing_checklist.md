# TheGrantScout Website - Testing Checklist

Complete testing checklist for ensuring quality before launch.

## How to Use This Checklist

- Test items in order (top to bottom)
- Check off items as you complete them
- Retest after major changes
- Document any issues found
- Fix critical issues before moving forward
- Nice-to-have items marked with (Optional)

---

## Pre-Testing Setup

- [ ] Development server is running (`npm run dev`)
- [ ] Website loads at http://localhost:3000
- [ ] No console errors visible (press F12, check Console tab)
- [ ] All components are rendering

---

## Browser Compatibility Testing

Test on all major browsers to ensure consistent experience.

### Desktop Browsers

**Google Chrome (Latest Version)**
- [ ] Website loads correctly
- [ ] All images display
- [ ] Navigation works
- [ ] Smooth scrolling functions
- [ ] Forms work (if applicable)
- [ ] No console errors (F12 → Console)

**Microsoft Edge (Latest Version)**
- [ ] Website loads correctly
- [ ] All images display
- [ ] Navigation works
- [ ] Smooth scrolling functions
- [ ] Forms work (if applicable)
- [ ] No console errors (F12 → Console)

**Mozilla Firefox (Latest Version)**
- [ ] Website loads correctly
- [ ] All images display
- [ ] Navigation works
- [ ] Smooth scrolling functions
- [ ] Forms work (if applicable)
- [ ] No console errors (F12 → Console)

**Safari (if available on Mac)**
- [ ] Website loads correctly
- [ ] All images display
- [ ] Navigation works
- [ ] Smooth scrolling functions
- [ ] Forms work (if applicable)
- [ ] No console errors

### Mobile Browsers

**Chrome Mobile (Android/iOS)**
- [ ] Website loads on mobile
- [ ] Touch interactions work
- [ ] Text is readable without zooming

**Safari Mobile (iOS)**
- [ ] Website loads on iPhone
- [ ] Touch interactions work
- [ ] Text is readable without zooming

---

## Responsive Design Testing

Test at all common screen sizes to ensure proper layout.

### Desktop Sizes

**1920px (Full HD)**
- [ ] Layout looks balanced (not too stretched)
- [ ] Text is readable
- [ ] Images are properly sized
- [ ] Navigation bar fits properly
- [ ] Footer layout is correct
- [ ] No horizontal scrolling

**1440px (Laptop)**
- [ ] Layout looks balanced
- [ ] Text is readable
- [ ] Images are properly sized
- [ ] Navigation bar fits properly
- [ ] Footer layout is correct
- [ ] No horizontal scrolling

**1280px (Small Laptop)**
- [ ] Layout looks balanced
- [ ] Text is readable
- [ ] Images are properly sized
- [ ] Navigation bar fits properly
- [ ] Footer layout is correct
- [ ] No horizontal scrolling

### Tablet Sizes

**1024px (iPad Landscape)**
- [ ] Layout adapts appropriately
- [ ] Text is readable
- [ ] Touch targets are large enough (44x44px minimum)
- [ ] Navigation works (may show hamburger menu)
- [ ] Images scale correctly
- [ ] No horizontal scrolling

**768px (iPad Portrait)**
- [ ] Layout switches to mobile/tablet view
- [ ] Text is readable
- [ ] Touch targets are large enough
- [ ] Hamburger menu works (if applicable)
- [ ] Images scale correctly
- [ ] No horizontal scrolling

### Mobile Sizes

**414px (iPhone Plus/Max)**
- [ ] Layout is single column
- [ ] Text is readable without zooming
- [ ] Touch targets are thumb-friendly (44x44px minimum)
- [ ] Hamburger menu opens/closes smoothly
- [ ] Images load and fit screen
- [ ] No horizontal scrolling
- [ ] CTA buttons are prominent

**375px (iPhone Standard)**
- [ ] Layout is single column
- [ ] Text is readable without zooming
- [ ] Touch targets are thumb-friendly
- [ ] Hamburger menu opens/closes smoothly
- [ ] Images load and fit screen
- [ ] No horizontal scrolling
- [ ] CTA buttons are prominent

**360px (Android Standard)**
- [ ] Layout is single column
- [ ] Text is readable without zooming
- [ ] Touch targets are thumb-friendly
- [ ] Hamburger menu opens/closes smoothly
- [ ] Images load and fit screen
- [ ] No horizontal scrolling
- [ ] CTA buttons are prominent

### How to Test Responsive Sizes

**In Chrome/Edge/Firefox:**
1. Press `F12` to open Developer Tools
2. Press `Ctrl + Shift + M` (or click the mobile icon)
3. Select different device sizes from dropdown
4. Or manually enter width (e.g., 375px)

**Test Rotation:**
- [ ] Switch between portrait and landscape on mobile sizes
- [ ] Layout adapts correctly
- [ ] Nothing breaks or overlaps

---

## Functionality Testing

### Navigation

**Header/Navigation Bar**
- [ ] Logo is visible
- [ ] Logo links to homepage (if clickable)
- [ ] All navigation links are visible
- [ ] Navigation links go to correct sections
- [ ] Smooth scroll works when clicking navigation links
- [ ] Active section is highlighted (if applicable)
- [ ] Sticky header works on scroll (if applicable)

**Mobile Navigation**
- [ ] Hamburger icon displays on mobile (<768px)
- [ ] Hamburger menu opens when clicked
- [ ] All menu items visible in mobile menu
- [ ] Menu links work
- [ ] Menu closes after clicking a link
- [ ] Menu closes when clicking outside
- [ ] Menu is accessible (can tab through)

**Footer**
- [ ] All footer links are present
- [ ] Footer links go to correct pages (or placeholder)
- [ ] Email addresses are correct and clickable (mailto: links)
- [ ] Social media icons display (if applicable)
- [ ] Social links work (if active)
- [ ] Copyright notice is correct (© 2025)

### Call-to-Action (CTA) Buttons

**Primary CTAs**
- [ ] "Get Your First 5 Matches Free" button is visible
- [ ] Button stands out visually (gold accent color)
- [ ] Button is large enough to click/tap easily
- [ ] Hover state works (darkens on hover)
- [ ] Button links to correct destination
- [ ] Button works on mobile (tap)

**Secondary CTAs**
- [ ] "See How It Works" button is visible
- [ ] Button has distinct style from primary CTA
- [ ] Smooth scroll to "How It Works" section
- [ ] Button works on mobile

**All CTAs Checklist**
- [ ] Minimum 48px height (thumb-friendly)
- [ ] Clear, action-oriented text
- [ ] Sufficient contrast (readable)
- [ ] Loading state (if applicable for forms)
- [ ] No broken links

### Sections

**Hero Section**
- [ ] Headline displays correctly: "Stop searching. Start matching."
- [ ] Subheadline is readable
- [ ] CTAs are prominent
- [ ] Trust indicators visible: "85,000+ foundations | 1.6M+ grants"
- [ ] Hero image/background loads
- [ ] Text is readable over background
- [ ] Section height is appropriate (not too tall/short)

**How It Works Section**
- [ ] Section headline displays
- [ ] 4 steps are visible
- [ ] Step icons display
- [ ] Step numbers/connectors show
- [ ] Text is clear and readable
- [ ] Layout works on mobile (vertical stack)

**Features Section**
- [ ] Section headline displays
- [ ] 4 feature cards visible
- [ ] Feature icons display
- [ ] Titles and descriptions readable
- [ ] Stats/callouts are prominent
- [ ] Grid layout works (1 col mobile, 2-4 col desktop)
- [ ] Hover effects work on cards

**Pricing Section**
- [ ] Section headline displays
- [ ] Pricing tier(s) visible
- [ ] Price is prominent
- [ ] Feature list with checkmarks
- [ ] CTA button in pricing card works
- [ ] Launch offer badge/text visible (if applicable)
- [ ] Pricing is clear and not confusing

**FAQ Section**
- [ ] Section headline displays
- [ ] All questions are listed
- [ ] Questions can expand/collapse (accordion)
- [ ] Clicking a question opens the answer
- [ ] Icon changes when expanded (+/- or arrow)
- [ ] Smooth expand/collapse animation
- [ ] Only one question open at a time (if that's the design)
- [ ] Works with keyboard (tab to question, enter to open)

**Testimonials Section** (if included)
- [ ] Section headline displays
- [ ] 3 testimonials visible
- [ ] Quotes are formatted clearly
- [ ] Names and titles display
- [ ] Organization names visible
- [ ] Photos display (if included)
- [ ] Layout works on mobile

### Forms (if applicable)

**Lead Capture Form**
- [ ] Form fields display correctly
- [ ] Field labels are clear
- [ ] Required fields are marked
- [ ] Placeholder text is helpful
- [ ] Tab order is logical
- [ ] Email validation works
- [ ] Submit button is clear and prominent
- [ ] Loading state shows when submitting
- [ ] Success message displays after submission
- [ ] Error message shows if submission fails
- [ ] Form doesn't submit with invalid data
- [ ] Privacy policy checkbox (if required)

---

## Performance Testing

### Load Speed

**Initial Page Load**
- [ ] Page loads in under 3 seconds (on good connection)
- [ ] No long delays before content appears
- [ ] Images load progressively (not all at once)
- [ ] No layout shift while loading

**Lighthouse Audit (Chrome)**

Run Lighthouse test:
1. Open website in Chrome
2. Press `F12` to open Developer Tools
3. Click "Lighthouse" tab
4. Select "Desktop" or "Mobile"
5. Click "Generate report"

**Performance Score**
- [ ] Performance score: 90+ (target: 95+)
- [ ] First Contentful Paint: < 1.5 seconds
- [ ] Time to Interactive: < 3.0 seconds
- [ ] Speed Index: < 3.0 seconds
- [ ] Total Blocking Time: < 200ms
- [ ] Cumulative Layout Shift: < 0.1

**Accessibility Score**
- [ ] Accessibility score: 90+ (target: 100)
- [ ] All issues addressed or documented

**SEO Score**
- [ ] SEO score: 90+ (target: 100)
- [ ] Meta description present
- [ ] Title tag present
- [ ] Headings in correct order (h1 → h2 → h3)

**Best Practices Score**
- [ ] Best Practices score: 90+ (target: 100)

### Image Optimization

- [ ] All images are optimized (compressed)
- [ ] Using Next.js Image component (not `<img>` tags)
- [ ] Images have proper width and height attributes
- [ ] Images load lazy (below the fold)
- [ ] Images are WebP or modern format (when possible)
- [ ] No images larger than necessary
- [ ] Hero image loads quickly

### Bundle Size

- [ ] JavaScript bundle is minimal
- [ ] No unused dependencies
- [ ] Production build is minified
- [ ] No console.log statements in production

**Check Bundle Size:**
```cmd
npm run build
```
Look for output like:
```
Page                Size     First Load JS
┌ / (page)          5 kB       85 kB
```
Target: First Load JS < 150 kB

---

## Accessibility Testing

### Keyboard Navigation

- [ ] Can tab through entire site with keyboard
- [ ] Tab order is logical (top to bottom, left to right)
- [ ] All interactive elements receive focus
- [ ] Focus indicator is visible (outline or highlight)
- [ ] Can open/close mobile menu with keyboard
- [ ] Can expand/collapse FAQ with keyboard (Enter or Space)
- [ ] Can submit forms with keyboard (Enter)
- [ ] No keyboard traps (can always tab away)

### Screen Reader Testing (Optional but Recommended)

**Windows Screen Reader (Narrator):**
1. Press `Windows + Ctrl + Enter` to start Narrator
2. Navigate through site
3. Listen to what Narrator reads

**Checklist:**
- [ ] All images have alt text
- [ ] Alt text is descriptive (not just "image")
- [ ] Decorative images have empty alt (`alt=""`)
- [ ] Links have descriptive text (not "click here")
- [ ] Buttons announce their purpose
- [ ] Form fields have labels
- [ ] Headings announce correctly
- [ ] Page structure makes sense audibly

### Color Contrast

- [ ] Text is readable against background
- [ ] Minimum contrast ratio: 4.5:1 for normal text
- [ ] Minimum contrast ratio: 3:1 for large text (18px+)
- [ ] Links are distinguishable from body text
- [ ] CTA buttons have sufficient contrast

**Test Contrast:**
Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/

Example:
- Navy text (#1e3a5f) on white (#ffffff): Check it passes AA
- Gold button (#d4a853) with white text: Check it passes AA

### Semantic HTML

- [ ] Proper heading hierarchy (h1 → h2 → h3, no skipping)
- [ ] Only one h1 per page
- [ ] Using `<nav>` for navigation
- [ ] Using `<main>` for main content
- [ ] Using `<footer>` for footer
- [ ] Using `<button>` for buttons (not divs)
- [ ] Using `<a>` for links (not divs)
- [ ] Lists use `<ul>` or `<ol>` tags

### ARIA Labels

- [ ] Hamburger menu has aria-label="Menu"
- [ ] Icon-only buttons have aria-label
- [ ] Form inputs have aria-describedby (if helpful text)
- [ ] Expandable sections have aria-expanded
- [ ] Not overusing ARIA (semantic HTML is better)

---

## Content Quality Testing

### Copy Review

- [ ] No spelling errors
- [ ] No grammar errors
- [ ] Consistent voice and tone
- [ ] Benefits emphasized over features
- [ ] No jargon or unexplained technical terms
- [ ] Numbers are specific (not vague like "many")
- [ ] CTAs use action-oriented language
- [ ] Headlines grab attention

### Brand Consistency

- [ ] "TheGrantScout" spelled correctly throughout
- [ ] Tagline is correct: "Stop searching. Start matching."
- [ ] Stats are accurate:
  - [ ] 85,000+ foundations
  - [ ] 1.6M+ historical grants
  - [ ] 67% success rate vs 8% cold outreach
- [ ] Colors match brand guidelines
- [ ] Fonts match brand guidelines (Inter)
- [ ] Voice is expert but accessible

### Legal and Contact Information

- [ ] Email addresses are correct:
  - [ ] hello@thegrantscout.com
  - [ ] support@thegrantscout.com
- [ ] Copyright year is correct: © 2025
- [ ] Privacy Policy link present (even if placeholder)
- [ ] Terms of Service link present (even if placeholder)
- [ ] No broken promises (only advertise features that exist)

---

## SEO Testing

### Meta Tags

Open page source (Right-click → View Page Source) and check:

- [ ] `<title>` tag present and descriptive
- [ ] `<meta name="description">` present and compelling
- [ ] `<meta name="keywords">` present (optional)
- [ ] Open Graph tags present:
  - [ ] `<meta property="og:title">`
  - [ ] `<meta property="og:description">`
  - [ ] `<meta property="og:image">` (1200x630px)
  - [ ] `<meta property="og:url">`
- [ ] Twitter Card tags present:
  - [ ] `<meta name="twitter:card">`
  - [ ] `<meta name="twitter:title">`
  - [ ] `<meta name="twitter:description">`

### Content Structure

- [ ] Only one h1 tag (page title)
- [ ] Headings in logical order (h1 → h2 → h3)
- [ ] Important keywords in headings
- [ ] First paragraph contains main keywords
- [ ] URLs are clean (if multiple pages)
- [ ] No broken links (404 errors)

### Technical SEO

- [ ] Favicon displays in browser tab
- [ ] robots.txt file exists (allows all)
- [ ] Sitemap.xml exists or auto-generated
- [ ] Site is indexable (no noindex tags)
- [ ] HTTPS enabled (when deployed)

---

## Cross-Device Testing

### Physical Device Testing (Recommended)

If you have access to real devices, test on:

**Desktop/Laptop**
- [ ] Windows desktop
- [ ] MacBook (if available)

**Tablet**
- [ ] iPad (if available)
- [ ] Android tablet (if available)

**Mobile**
- [ ] iPhone (any model)
- [ ] Android phone (any model)

### What to Check on Real Devices

- [ ] Touch targets are easy to tap with finger
- [ ] Text is readable without zooming
- [ ] Scrolling is smooth
- [ ] Animations don't lag
- [ ] Images look sharp (not pixelated)
- [ ] Forms are easy to fill out on mobile keyboard
- [ ] No weird spacing or overflow issues

---

## Browser Developer Tools Testing

### Console Errors

**Check for JavaScript Errors:**
1. Press `F12` to open Developer Tools
2. Click "Console" tab
3. Refresh the page

- [ ] No red errors in console
- [ ] No security warnings
- [ ] No 404 errors (missing files)
- [ ] No CORS errors
- [ ] Only expected warnings (if any)

### Network Tab

**Check Resource Loading:**
1. Press `F12`
2. Click "Network" tab
3. Refresh page
4. Watch files load

- [ ] All files load successfully (green 200 status)
- [ ] No 404 errors (missing files - red)
- [ ] No 500 errors (server errors - red)
- [ ] Total page size < 2 MB
- [ ] Largest resources are identified and optimized

### Responsive Mode

**Test Breakpoints:**
1. Press `F12`
2. Press `Ctrl + Shift + M` (toggle device toolbar)
3. Drag the viewport width slowly

- [ ] Layout transitions smoothly at breakpoints
- [ ] No sudden jumps or breaks
- [ ] All content remains visible
- [ ] No overlapping elements

---

## Pre-Launch Final Checklist

### Content Final Check

- [ ] All placeholder content replaced with real content
- [ ] All images are real (not placeholder)
- [ ] All links go to correct destinations
- [ ] Contact information is accurate
- [ ] Pricing is correct
- [ ] Launch offer details are accurate (if applicable)

### Technical Final Check

- [ ] Production build works: `npm run build`
- [ ] Production build starts: `npm start`
- [ ] Environment variables set (if any)
- [ ] No hard-coded secrets or API keys
- [ ] Analytics tracking code added (if ready)
- [ ] Forms submit to correct endpoint (if applicable)
- [ ] All components render without errors

### Cross-Browser Final Check

- [ ] Tested on Chrome (latest)
- [ ] Tested on Edge (latest)
- [ ] Tested on Firefox (latest)
- [ ] Tested on Safari (if available)
- [ ] Tested on mobile Chrome
- [ ] Tested on mobile Safari

### Performance Final Check

- [ ] Lighthouse Performance: 90+
- [ ] Lighthouse Accessibility: 90+
- [ ] Lighthouse SEO: 90+
- [ ] Lighthouse Best Practices: 90+
- [ ] Page load time: < 3 seconds

### Accessibility Final Check

- [ ] Can navigate entire site with keyboard
- [ ] All images have alt text
- [ ] Color contrast passes WCAG AA
- [ ] Forms are accessible
- [ ] No accessibility errors in Lighthouse

---

## Post-Launch Monitoring

After the site goes live, monitor these:

### Week 1 Checks

- [ ] Site is accessible at thegrantscout.com
- [ ] HTTPS (SSL) is working
- [ ] No 404 errors in production
- [ ] Analytics tracking is working
- [ ] Forms are submitting correctly (if applicable)
- [ ] No console errors on live site

### Ongoing Monitoring

- [ ] Check Google Search Console for errors
- [ ] Monitor site speed with Lighthouse
- [ ] Review analytics for issues (high bounce rate, etc.)
- [ ] Test forms periodically
- [ ] Check all browsers every month

---

## Issue Tracking

When you find issues during testing, document them:

### Issue Template

```
Issue #: [number]
Priority: [Critical/High/Medium/Low]
Browser: [Chrome/Firefox/Safari/Edge/Mobile]
Description: [What's wrong]
Steps to Reproduce:
1. Go to...
2. Click...
3. See error...

Expected: [What should happen]
Actual: [What actually happens]
Screenshot: [If applicable]
```

### Priority Definitions

- **Critical**: Site is broken, cannot launch
  - Example: Site won't load, major functionality broken
- **High**: Major issue affecting user experience
  - Example: CTA buttons don't work, mobile menu broken
- **Medium**: Noticeable issue but site still usable
  - Example: Image too small, spacing off
- **Low**: Minor visual issue or nice-to-have
  - Example: Hover effect missing, text alignment slightly off

---

## Testing Tools Reference

### Browser Dev Tools
- Chrome: `F12` or `Ctrl + Shift + I`
- Firefox: `F12` or `Ctrl + Shift + I`
- Edge: `F12` or `Ctrl + Shift + I`
- Safari: `Cmd + Option + I` (Mac)

### Lighthouse
- Chrome only
- F12 → Lighthouse tab → Generate report

### Responsive Testing
- Dev Tools: `Ctrl + Shift + M`
- Or resize browser window manually

### Accessibility Checkers
- Lighthouse Accessibility audit
- axe DevTools extension: https://www.deque.com/axe/devtools/
- WAVE extension: https://wave.webaim.org/extension/

### Color Contrast
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/

### Screen Reader (Windows)
- Narrator: `Windows + Ctrl + Enter`

---

## Summary

This checklist covers:
- 4 browser types (Chrome, Edge, Firefox, Safari)
- 8 responsive breakpoints (1920px to 360px)
- 50+ functionality checks
- Performance, accessibility, and SEO audits
- Pre-launch and post-launch monitoring

**Before marking "DONE":**
- All Critical issues fixed
- All High issues fixed
- Medium issues documented (fix if time allows)
- Low issues documented (fix in future iteration)
- Lighthouse scores all 90+
- Site tested on real mobile device

---

**Questions?** Tag the Project Manager in the team mailbox.

**Ready to deploy?** See `docs/DEPLOYMENT_GUIDE.md` for launch steps.
