# Design Quick Reference Card
## TheGrantScout Navy + Gold Professional Reports

---

## COLORS (Copy-Paste Ready)

```
PRIMARY
Navy:              #1e3a5f
Gold:              #d4a853

NEUTRALS
White:             #ffffff
Off-White:         #fafbfc
Light Gray:        #e8ebed
Very Light Navy:   #f0f4f9

SEMANTIC
Success:           #36b37e
Warning:           #ff8c42
Error:             #ff5630
Info:              #0052cc
```

**WCAG Accessibility Status:**
- Navy (#1e3a5f) on White: 8.5:1 ✓ (AAA compliant)
- Gold (#d4a853) on Navy: 5.2:1 ✓ (AA compliant)
- Gold on White: 3.8:1 ⚠️ (AA only for large text 18pt+)

---

## TYPOGRAPHY (Quick Rules)

**Fonts:**
- Headings: Inter (Google Fonts)
- Body: Plus Jakarta Sans (Google Fonts)
- Code/Data: SF Mono or Monaco

**Sizes:**
```
Page Title:        40px, weight 700
Section Header:    28-32px, weight 600
Subheading:        20-24px, weight 600
Body Text:         14px, weight 400 ← STANDARD
Table Header:      14px, weight 600
Captions:          12px, weight 400
```

**Line Height:**
- Headings: 1.3x font size
- Body: 1.5x font size (14px = 21px)

---

## TABLES AT A GLANCE

```
Header Row:
├─ Background: Navy (#1e3a5f)
├─ Text: White
├─ Weight: 600
├─ Font size: 14px
└─ Border: Gold bottom (2px)

Data Row:
├─ Background: White or Light Gray (#f5f7fa) alternating
├─ Text: Navy (#1e3a5f)
├─ Weight: 400
├─ Font size: 14px
├─ Padding: 12px vertical, 16px horizontal
└─ Separator: 1px light gray or none

Mobile:
├─ Use card layout on screens <768px
├─ Stack data as key-value pairs
└─ Show only essential columns
```

---

## CALLOUT BOX TEMPLATE

```
┌─────────────────────────────┐
│ ⓘ Key Finding               │
├─────────────────────────────┤
│ Content goes here           │
│ Keep it to 3-4 sentences    │
└─────────────────────────────┘

Background:    Light Navy (#f0f4f9)
Left Border:   4px Gold (#d4a853)
Text:          Navy (#1e3a5f), 13px
Padding:       16px
Border Radius: 8px
Shadow:        0 2px 4px rgba(30,58,95,0.1)
```

---

## STATUS BADGE SYSTEM

```
Success   ✓ Approved      | Green (#36b37e) on white
Warning   ⏱ Pending      | Orange (#ff8c42) on white
Error     ⚠ Urgent       | Red (#ff5630) on white
Info      ⓘ Draft        | Blue (#0052cc) on white

Size:      12px font, 4px border-radius
Padding:   4px 8px
Weight:    600
```

---

## BUTTON STYLES

**Primary (Gold):**
```
Background: #d4a853
Text:       #1e3a5f
Padding:    12px 24px
Font:       14px, weight 600
Border:     None
Radius:     4px
Shadow:     0 2px 4px rgba(0,0,0,0.1)
Hover:      Darker gold, shadow 0 4px 8px
```

**Secondary (Navy Outline):**
```
Background: Transparent
Text:       #1e3a5f
Border:     2px solid #1e3a5f
Padding:    10px 22px
Font:       14px, weight 600
Radius:     4px
Hover:      Light navy background #f0f4f9
```

---

## SPACING RULES (8px Grid)

```
xs:   4px   (internal component spacing)
sm:   8px   (between list items)
md:   16px  (standard padding)
lg:   24px  (section padding)
xl:   32px  (major section separation)
2xl:  40px  (page breaks)

Example:
Card:      16px padding (md)
Between:   24px margin (lg)
Sections:  32-40px separation (xl-2xl)
```

---

## VISUAL HIERARCHY CHECKLIST

- [ ] One clear focal point per page
- [ ] Max 3-4 font sizes (not 7-8)
- [ ] Key metrics highlighted in gold or bold navy
- [ ] White space around emphasis (not crowded)
- [ ] Headings clearly larger than body text
- [ ] CTA button stands out (gold + shadow)
- [ ] Color used strategically (not on everything)

---

## SECTION DIVIDER OPTIONS

**Option 1: Banner**
```
[SECTION 2: ANALYSIS & FINDINGS]
Background: #f0f4f9
Text: Navy 20px weight 600
Padding: 16px all sides
Margin: 40px top/bottom
```

**Option 2: Line with Text**
```
────────────────────────
   ANALYSIS & FINDINGS
────────────────────────
Centered, Navy 18px weight 600
```

**Option 3: Icon Divider**
```
        ◆ ◆ ◆
   ANALYSIS & FINDINGS
        ◆ ◆ ◆
Gold icons, Navy text
```

---

## DOCUMENT STRUCTURE

```
Page 1:   Cover/Title
Page 2:   Table of Contents (if report >5 pages)
Page 3:   Executive Summary (1 page max)
Page 4+:  Main content with sections
Last:     Appendix (if needed)

Margins:  32-48px on sides, 24-32px top/bottom
Width:    600-900px optimal, max 1000px
Spacing:  32px between sections minimum
```

---

## ICON SPECIFICATIONS

```
Sizes:     16px, 20px, 24px, 32px (multiples of 4)
Format:    SVG only (not PNG/JPG)
Stroke:    1.5-2px (not too thin)
Color:     Navy (#1e3a5f) or Gold (#d4a853)
Margin:    8-12px right of text
Rule:      ALWAYS pair with text label
```

Common Icons:
- ℹ️ Information / Note
- ⚠️ Warning / Caution
- ✓ Success / Approved
- ⏱️ Deadline / Time-sensitive
- 📊 Data / Analytics
- 💡 Insight / Recommendation

---

## ACCESSIBILITY COMPLIANCE

**WCAG AA (Minimum - Recommended):**
- Text contrast: 4.5:1 (normal) or 3:1 (large 18pt+)
- Colors shouldn't be the only way to convey meaning
- Icons must have text labels
- Minimum font size: 12px body text, 14px preferred

**Test Tools:**
- WebAIM Contrast Checker: webaim.org/resources/contrastchecker/
- Colorblindness simulator: https://www.color-blindness.com/

---

## COMMON MISTAKES (DON'T DO THESE)

❌ Multiple fonts (stick to 2)
❌ Too many font sizes (max 4)
❌ Everything bold (defeats emphasis)
❌ Cramped spacing (use whitespace generously)
❌ Heavy drop shadows (subtle only)
❌ Light gray text on white (low contrast)
❌ Icons without text labels
❌ Tables with heavy gridlines
❌ More than one "hero" element per page

---

## FONT WEIGHTS QUICK GUIDE

```
400 = Regular      (body text)
500 = Medium       (labels, secondary)
600 = Semibold     (subheadings, emphasis)
700 = Bold         (main headings, CTAs)

DO: Use 400 for body, 600 for headings
DON'T: Make everything bold (looks unprofessional)
```

---

## RESPONSIVE BREAKPOINTS

```
Mobile (small):    <480px
Mobile (large):    480px-768px
Tablet:            768px-1024px
Desktop:           1024px+

Rule: Design mobile-first, then scale up
Tables: Use card layout <768px
Margins: Reduce on mobile (24px vs 48px desktop)
```

---

## QUICK COPY-PASTE: CSS VARIABLES

```css
:root {
  --navy: #1e3a5f;
  --gold: #d4a853;
  --white: #ffffff;
  --gray-light: #f5f7fa;
  --gray-lighter: #e8ebed;

  --success: #36b37e;
  --warning: #ff8c42;
  --error: #ff5630;

  --size-body: 14px;
  --line-body: 1.5;
  --weight-regular: 400;
  --weight-bold: 600;

  --shadow: 0 2px 4px rgba(30,58,95,0.1);
  --radius: 4px;
}
```

---

## REPORT TEMPLATE ELEMENTS

**Executive Summary:**
- Max 1 page
- 250-400 words
- Background: Light gray
- Border: Gold top/bottom (2px)

**Data Callout (Metrics):**
- Background: Very light navy (#f0f4f9)
- Border left: Gold (4px)
- Highlight metric in gold or bold
- Padding: 16px

**Action Button:**
- Gold background
- Navy text
- 12px padding, 4px radius
- Subtle shadow

**Section Header:**
- Navy, 28px, weight 600
- 40px margin above
- 24px margin below

---

## ONE-PAGE DESIGN CHECKLIST

Before publishing any report:

- [ ] Color palette: Navy + Gold + neutrals only
- [ ] Fonts: Inter (headings) + Plus Jakarta Sans (body)
- [ ] Font sizes: Max 4 different sizes
- [ ] Contrast: Tested with WebAIM (4.5:1 minimum)
- [ ] Tables: No internal gridlines, clear headers
- [ ] Callouts: Gold left border, proper padding
- [ ] Buttons: Gold with shadow
- [ ] Spacing: Consistent 8px grid
- [ ] Icons: Paired with text labels
- [ ] Mobile: Tested on phone (responsive)
- [ ] Accessibility: Color isn't only indicator of meaning

---

**Print-Friendly Version Available**
For a print-friendly checklist, remove colors and save as PDF.

**Last Updated:** December 4, 2025
**Format:** Quick Reference Card (One Page)
