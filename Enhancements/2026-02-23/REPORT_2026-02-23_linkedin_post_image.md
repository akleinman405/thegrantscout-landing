# LinkedIn Post Image: Complete Workflow Reference

**Date:** 2026-02-23
**Prompt:** Create professional LinkedIn lead-gen image from Golden Gate Bridge photo with branded text overlay; document full workflow for future skill creation
**Status:** Complete
**Owner:** Aleck

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-23 | Claude | Initial version |
| 2.0 | 2026-02-23 | Claude | Comprehensive rewrite: full workflow, script source, design decisions, skill-ready reference |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites](#prerequisites)
3. [Workflow Overview](#workflow-overview)
4. [Step 1: Source Image Analysis](#step-1-source-image-analysis)
5. [Step 2: Font Discovery](#step-2-font-discovery)
6. [Step 3: The Script](#step-3-the-script)
7. [Step 4: Design Decisions and Tweaks](#step-4-design-decisions-and-tweaks)
8. [Step 5: Run and Verify](#step-5-run-and-verify)
9. [Reuse Guide](#reuse-guide)
10. [Files Created/Modified](#files-createdmodified)
11. [Notes](#notes)

---

## Executive Summary

Built a LinkedIn lead-gen image (1200x627) from an original Golden Gate Bridge photograph. The workflow: crop to LinkedIn aspect ratio, color-enhance, add semi-transparent branded banner with text overlay. Two iterations were done: v1 had a gold CTA line ("Free List -- Comment to Get Yours"), v2 replaced it with an understated brand watermark ("Compiled by TheGrantScout"). This report documents everything needed to reproduce or generalize this into a reusable skill.

**Final output:** `linkedin_post_bay_area_foundations.jpg` (205 KB, 1200x627)

---

## Prerequisites

**Python packages:**
```
pip3 install Pillow
```

**System fonts (macOS):**
- `/System/Library/Fonts/HelveticaNeue.ttc` (ships with macOS)
- Bold = index 1, Medium = index 10 in the TTC collection

**Font index discovery command** (run once per font to find available faces):
```python
from PIL import ImageFont
ttc = "/System/Library/Fonts/HelveticaNeue.ttc"
for i in range(20):
    try:
        f = ImageFont.truetype(ttc, size=40, index=i)
        print(f"Index {i}: {f.getname()}")
    except Exception:
        break
```

Results for HelveticaNeue.ttc:

| Index | Face |
|-------|------|
| 0 | Regular |
| 1 | **Bold** |
| 2 | Italic |
| 3 | Bold Italic |
| 4 | Condensed Bold |
| 5 | UltraLight |
| 7 | Light |
| 9 | Condensed Black |
| 10 | **Medium** |
| 12 | Thin |

---

## Workflow Overview

```
Source photo (.JPG)
    |
    v
[1] Crop to 1.91:1 (LinkedIn ratio)
    |
    v
[2] Resize to 1200x627 (LANCZOS)
    |
    v
[3] Enhance (contrast, saturation, brightness, sharpness)
    |
    +---> Save enhanced version (no text)
    |
    v
[4] Add semi-transparent navy banner (lower 38%)
    |
    v
[5] Add text overlay (3 lines, centered)
    |
    v
[6] Save final version (.jpg, quality 95)
```

---

## Step 1: Source Image Analysis

Before writing any code, analyze the source photo to make cropping decisions.

**Source:** `DSCN0447_Original.JPG`
- **Dimensions:** 4453 x 3340 px (4:3 ratio, 14.8 MP)
- **Composition:** Bridge tower center-right, Marin Headlands behind, dark moody sky above, dark water below, golden sunlight on hillside

**Cropping math:**
- Current ratio: 4:3 (1.33:1)
- Target ratio: 1.91:1 (LinkedIn recommended 1200x627)
- Keep full width (4453px), calculate target height: `4453 / 1.91 = 2332px`
- Remove `3340 - 2332 = 1008px` total, split evenly: 504px from top, 504px from bottom
- This trims expendable dark sky and water while keeping the bridge tower and golden hillside

**Key insight:** The bottom of the frame (dark water) becomes the text overlay zone after cropping, so losing some water to the crop is fine.

---

## Step 2: Font Discovery

macOS stores many fonts in `.ttc` (TrueType Collection) files containing multiple faces. Pillow accesses them by index.

**Command to enumerate faces:**
```bash
fc-list ':family=Helvetica Neue' file style
```

**To test loading in Pillow** (see Prerequisites section for the Python loop).

**Chosen fonts:**
- Line 1 (headline): Helvetica Neue Bold (index 1), 48px
- Line 2 (subhead): Helvetica Neue Bold (index 1), 42px
- Line 3 (watermark): Helvetica Neue Medium (index 10), 20px

---

## Step 3: The Script

**File:** `Enhancements/2026-02-23/create_linkedin_image.py`

### Full source (final version)

```python
#!/usr/bin/env python3
"""Create LinkedIn lead-gen image from Golden Gate Bridge photo.

Crops to LinkedIn 1.91:1 ratio, enhances colors, adds branded text overlay.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# --- Config ---
SRC = Path(__file__).parent / "DSCN0447_Original.JPG"
OUT_ENHANCED = Path(__file__).parent / "golden_gate_enhanced.jpg"
OUT_FINAL = Path(__file__).parent / "linkedin_post_bay_area_foundations.jpg"

TARGET_W, TARGET_H = 1200, 627
RATIO = TARGET_W / TARGET_H  # 1.91:1

FONT_TTC = "/System/Library/Fonts/HelveticaNeue.ttc"
BOLD_IDX = 1
MEDIUM_IDX = 10

NAVY = (30, 58, 95)       # #1e3a5f
WHITE = (255, 255, 255)
LIGHT_GRAY = (190, 195, 200)  # understated watermark color
SHADOW = (10, 20, 40)


def crop_and_resize(img: Image.Image) -> Image.Image:
    """Center-crop to 1.91:1 ratio, then resize to 1200x627."""
    w, h = img.size
    target_h = int(w / RATIO)
    if target_h > h:
        target_w = int(h * RATIO)
        left = (w - target_w) // 2
        img = img.crop((left, 0, left + target_w, h))
    else:
        top = (h - target_h) // 2
        img = img.crop((0, top, w, top + target_h))
    return img.resize((TARGET_W, TARGET_H), Image.LANCZOS)


def enhance(img: Image.Image) -> Image.Image:
    """Subtle enhancement: contrast, saturation, brightness, sharpness."""
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Color(img).enhance(1.2)
    img = ImageEnhance.Brightness(img).enhance(1.05)
    img = ImageEnhance.Sharpness(img).enhance(1.3)
    return img


def add_text_overlay(img: Image.Image) -> Image.Image:
    """Add semi-transparent navy banner with text in lower third."""
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Banner dimensions
    banner_top = int(TARGET_H * 0.62)
    banner_h = TARGET_H - banner_top

    # Gradient fade zone at top of banner (20px)
    fade_h = 20
    for i in range(fade_h):
        alpha = int(180 * (i / fade_h))
        y = banner_top + i
        draw.line([(0, y), (TARGET_W, y)], fill=(*NAVY, alpha))

    # Solid banner below fade
    draw.rectangle(
        [(0, banner_top + fade_h), (TARGET_W, TARGET_H)],
        fill=(*NAVY, 180),
    )

    # Composite banner onto image
    img = Image.alpha_composite(img, overlay)

    # Now draw text
    draw = ImageDraw.Draw(img)

    font_l1 = ImageFont.truetype(FONT_TTC, size=48, index=BOLD_IDX)
    font_l2 = ImageFont.truetype(FONT_TTC, size=42, index=BOLD_IDX)
    font_l3 = ImageFont.truetype(FONT_TTC, size=20, index=MEDIUM_IDX)

    line1 = "150+ Bay Area Foundations"
    line2 = "Funding Youth & Education Programs"
    line3 = "Compiled by TheGrantScout"

    # Measure text
    bb1 = draw.textbbox((0, 0), line1, font=font_l1)
    bb2 = draw.textbbox((0, 0), line2, font=font_l2)
    bb3 = draw.textbbox((0, 0), line3, font=font_l3)
    w1, h1 = bb1[2] - bb1[0], bb1[3] - bb1[1]
    w2, h2 = bb2[2] - bb2[0], bb2[3] - bb2[1]
    w3, h3 = bb3[2] - bb3[0], bb3[3] - bb3[1]

    # Vertical layout: center the 3 lines in the banner area
    line_gap = 10
    total_text_h = h1 + h2 + h3 + 2 * line_gap
    y_start = banner_top + (banner_h - total_text_h) // 2 + 5

    # Draw each line centered with shadow
    for text, font, color, w_text, y_off in [
        (line1, font_l1, WHITE, w1, y_start),
        (line2, font_l2, WHITE, w2, y_start + h1 + line_gap),
        (line3, font_l3, LIGHT_GRAY, w3, y_start + h1 + h2 + 2 * line_gap),
    ]:
        x = (TARGET_W - w_text) // 2
        # Shadow
        draw.text((x + 2, y_off + 2), text, font=font, fill=(*SHADOW, 160))
        # Main text
        draw.text((x, y_off), text, font=font, fill=(*color, 255))

    return img.convert("RGB")


def main():
    print(f"Loading {SRC.name}...")
    img = Image.open(SRC)
    print(f"  Original: {img.size[0]}x{img.size[1]}")

    img = crop_and_resize(img)
    print(f"  Cropped/resized: {img.size[0]}x{img.size[1]}")

    img = enhance(img)

    img.save(OUT_ENHANCED, "JPEG", quality=95)
    size_kb = OUT_ENHANCED.stat().st_size / 1024
    print(f"  Saved enhanced: {OUT_ENHANCED.name} ({size_kb:.0f} KB)")

    final = add_text_overlay(img)

    final.save(OUT_FINAL, "JPEG", quality=95)
    size_kb = OUT_FINAL.stat().st_size / 1024
    print(f"  Saved final: {OUT_FINAL.name} ({size_kb:.0f} KB)")

    print("Done!")


if __name__ == "__main__":
    main()
```

### Script architecture

| Function | Purpose |
|----------|---------|
| `crop_and_resize()` | Handles any source aspect ratio. Calculates whether to trim height or width to hit 1.91:1, then LANCZOS downscale. |
| `enhance()` | Four `ImageEnhance` passes. Factors are all close to 1.0 for a natural look. |
| `add_text_overlay()` | Builds a separate RGBA overlay for the banner (allows alpha compositing), then draws text directly on the composited result. |
| `main()` | Orchestrates the pipeline, saves both intermediate and final outputs. |

---

## Step 4: Design Decisions and Tweaks

### Iteration 1 (v1): CTA version

| Element | Value | Rationale |
|---------|-------|-----------|
| Line 3 text | "Free List -- Comment to Get Yours" | Direct CTA for LinkedIn lead-gen |
| Line 3 font | Helvetica Neue Medium, **28px** | Visible but subordinate to headline |
| Line 3 color | **Gold #d4a853** | TGS brand accent, draws eye to CTA |

### Iteration 2 (v2, final): Brand watermark version

| Element | Changed to | Rationale |
|---------|-----------|-----------|
| Line 3 text | "Compiled by TheGrantScout" | Brand attribution, not a sales push |
| Line 3 font size | **20px** (was 28) | Smaller to feel like a watermark |
| Line 3 color | **Light gray (190, 195, 200)** (was gold) | Understated, doesn't compete with headline |

### Design decisions that stayed constant

| Decision | Value | Why |
|----------|-------|-----|
| Target size | 1200x627 (1.91:1) | LinkedIn recommended image dimensions |
| Crop strategy | Center vertical | Trims expendable sky/water, keeps bridge + hillside |
| Enhancement factors | Contrast 1.15, Color 1.2, Brightness 1.05, Sharpness 1.3 | Tested visually. Makes orange bridge and golden hillside pop without looking processed. |
| Banner position | Lower 38% (starts at 62% from top) | Dark water area after crop is natural text zone |
| Banner opacity | ~70% (alpha 180/255) | Dark enough for text readability, transparent enough to see water/bridge base |
| Gradient fade | 20px at top of banner | Avoids hard edge, looks polished |
| Font family | Helvetica Neue | Clean, professional, available on all Macs, familiar to business audience |
| Text shadow | 2px offset, dark navy at 63% opacity | Adds depth without being heavy |
| JPEG quality | 95 | High quality, keeps file under 250 KB |
| Output sizes | Enhanced 219 KB, Final 205 KB | Within LinkedIn's limits, fast loading |

### Color palette used

| Name | RGB | Hex | Usage |
|------|-----|-----|-------|
| Navy (TGS brand) | (30, 58, 95) | #1e3a5f | Banner background |
| White | (255, 255, 255) | #ffffff | Headline text (lines 1-2) |
| Light Gray | (190, 195, 200) | #bec3c8 | Watermark text (line 3) |
| Shadow | (10, 20, 40) | #0a1428 | Text drop shadow |

### What we tried that we could revisit

- **Gold CTA line (v1):** Works well for an explicit lead-gen post. Swap back by changing `LIGHT_GRAY` to `(212, 168, 83)`, text to the CTA, and font size to 28.
- **Banner height:** 38% covers a lot of the photo. Could try 30% for posts where the photo matters more. Adjust `0.62` to `0.70`.
- **Enhancement factors:** These work for moody/dark source photos. For brighter source images, reduce brightness factor to 1.0 and contrast to 1.1.

---

## Step 5: Run and Verify

**Run command:**
```bash
python3 "Enhancements/2026-02-23/create_linkedin_image.py"
```

**Expected output:**
```
Loading DSCN0447_Original.JPG...
  Original: 4453x3340
  Cropped/resized: 1200x627
  Saved enhanced: golden_gate_enhanced.jpg (219 KB)
  Saved final: linkedin_post_bay_area_foundations.jpg (205 KB)
Done!
```

**Verification checklist:**

| Check | Expected | How to verify |
|-------|----------|---------------|
| Dimensions | 1200 x 627 | Open image, check properties |
| File size | 150-400 KB | `ls -la` or Finder |
| Text readable | All 3 lines clear | Visual inspection |
| Text centered | Horizontally centered in banner | Visual inspection |
| Enhancement | Natural, not oversaturated | Compare to source photo |
| Banner fade | Smooth gradient at top edge | Look at banner-to-photo transition |
| Brand colors correct | Navy banner, white/gray text | Visual inspection |

---

## Reuse Guide

### To create a new LinkedIn image with different text

Edit these constants at the top of the script:

```python
SRC = Path(__file__).parent / "your_photo.jpg"
OUT_FINAL = Path(__file__).parent / "your_output.jpg"

# In add_text_overlay():
line1 = "Your Headline Here"
line2 = "Your Subheadline Here"
line3 = "Compiled by TheGrantScout"
```

### To generalize into a CLI tool

The script is already structured for this. The natural CLI arguments would be:

```
python3 create_linkedin_image.py \
  --input photo.jpg \
  --output final.jpg \
  --line1 "Headline" \
  --line2 "Subheadline" \
  --line3 "Watermark" \
  --line3-style watermark|cta
```

Where `--line3-style watermark` uses light gray 20px and `cta` uses gold 28px.

### To convert into a skill

A skill definition would need:

1. **Required inputs:** source photo path, 2-3 text lines, output path
2. **Optional inputs:** enhancement factors, banner height %, line3 style (watermark vs CTA)
3. **Dependencies:** Pillow (`pip3 install Pillow`)
4. **Brand constants:** Import from `0. Tools/branding.py` instead of hardcoding
5. **Font handling:** Could add fallback for non-macOS (e.g., DejaVu Sans Bold)

---

## Files Created/Modified

| File | Path | Description |
|------|------|-------------|
| Script | `Enhancements/2026-02-23/create_linkedin_image.py` | Pillow-based image processing (v2, final) |
| Enhanced photo | `Enhancements/2026-02-23/golden_gate_enhanced.jpg` | Enhanced photo, no text (219 KB) |
| Final image | `Enhancements/2026-02-23/linkedin_post_bay_area_foundations.jpg` | Final with watermark overlay (205 KB) |
| Report | `Enhancements/2026-02-23/REPORT_2026-02-23_linkedin_post_image.md` | This report |

## Notes

- **Pillow RGBA compositing** is the key technique. You can't draw semi-transparent rectangles directly on an RGB image. Build a separate RGBA overlay, draw on it, then `Image.alpha_composite()` it onto the RGBA-converted source.
- **`textbbox()` not `textsize()`**: Pillow deprecated `textsize()` in 10.0. Use `draw.textbbox((0,0), text, font=font)` and compute width/height from the bounding box.
- **TTC font index** is not documented anywhere obvious. The discovery loop in Prerequisites is essential for any new font file.
- **LANCZOS resampling** (Pillow's highest quality) matters at 4453 to 1200 downscale. Using BILINEAR would produce visible softness.
- The enhanced photo (no text) is saved as a reusable asset for future posts with different overlay text.

---

*Generated by Claude Code on 2026-02-23*
