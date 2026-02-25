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
        # Wider than expected, crop width instead
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
    y_start = banner_top + (banner_h - total_text_h) // 2 + 5  # nudge down slightly past fade

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

    # Crop and resize
    img = crop_and_resize(img)
    print(f"  Cropped/resized: {img.size[0]}x{img.size[1]}")

    # Enhance
    img = enhance(img)

    # Save enhanced (no text)
    img.save(OUT_ENHANCED, "JPEG", quality=95)
    size_kb = OUT_ENHANCED.stat().st_size / 1024
    print(f"  Saved enhanced: {OUT_ENHANCED.name} ({size_kb:.0f} KB)")

    # Add text overlay
    final = add_text_overlay(img)

    # Save final
    final.save(OUT_FINAL, "JPEG", quality=95)
    size_kb = OUT_FINAL.stat().st_size / 1024
    print(f"  Saved final: {OUT_FINAL.name} ({size_kb:.0f} KB)")

    print("Done!")


if __name__ == "__main__":
    main()
