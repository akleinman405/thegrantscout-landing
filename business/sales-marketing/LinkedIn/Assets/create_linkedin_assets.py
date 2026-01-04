#!/usr/bin/env python3
"""
Generate LinkedIn assets for TheGrantScout
- Logo (400x400px)
- Company banner (1128x191px)
- Personal banner (1584x396px)
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Brand colors
NAVY = (30, 58, 95)       # #1e3a5f
GOLD = (212, 168, 83)     # #d4a853
WHITE = (255, 255, 255)
LIGHT_NAVY = (40, 70, 110)  # Slightly lighter for gradient effect

# Output directory
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_font(size, bold=False):
    """Try to get a good font, fall back to default if needed."""
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

def create_logo(size=400):
    """Create the TheGrantScout logo (circular, matching favicon)."""
    # Create with transparent background for circle
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2
    radius = int(size * 0.47)  # Leave small margin

    # Draw circular navy background (matching favicon)
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=NAVY + (255,)
    )

    # Document shape - positioned relative to circle center
    # Scaled to fit nicely within circle
    doc_width = size * 0.35
    doc_height = size * 0.45
    doc_left = center - doc_width * 0.7
    doc_top = center - doc_height * 0.55
    doc_right = doc_left + doc_width
    doc_bottom = doc_top + doc_height
    fold_size = size * 0.08

    # Draw document body
    doc_points = [
        (doc_left, doc_top),
        (doc_right - fold_size, doc_top),
        (doc_right, doc_top + fold_size),
        (doc_right, doc_bottom),
        (doc_left, doc_bottom),
    ]
    draw.polygon(doc_points, fill=WHITE + (230,))  # Slightly transparent like favicon

    # Draw fold
    fold_points = [
        (doc_right - fold_size, doc_top),
        (doc_right - fold_size, doc_top + fold_size),
        (doc_right, doc_top + fold_size),
    ]
    draw.polygon(fold_points, fill=(220, 220, 220, 255))

    # Dollar sign on document
    dollar_font = get_font(int(size * 0.18), bold=True)
    dollar_text = "$"
    bbox = draw.textbbox((0, 0), dollar_text, font=dollar_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    dollar_x = doc_left + (doc_width - text_width) / 2
    dollar_y = doc_top + (doc_height - text_height) / 2 - size * 0.01
    draw.text((dollar_x, dollar_y), dollar_text, fill=NAVY + (255,), font=dollar_font)

    # Magnifying glass - positioned at bottom right within circle
    glass_center_x = center + size * 0.18
    glass_center_y = center + size * 0.18
    glass_radius = size * 0.12
    glass_thickness = int(size * 0.045)

    # Draw glass circle
    draw.ellipse(
        [glass_center_x - glass_radius, glass_center_y - glass_radius,
         glass_center_x + glass_radius, glass_center_y + glass_radius],
        outline=GOLD + (255,), width=glass_thickness
    )

    # Draw handle
    handle_start_x = glass_center_x + glass_radius * 0.7
    handle_start_y = glass_center_y + glass_radius * 0.7
    handle_end_x = center + size * 0.38
    handle_end_y = center + size * 0.38
    draw.line(
        [(handle_start_x, handle_start_y), (handle_end_x, handle_end_y)],
        fill=GOLD + (255,), width=glass_thickness
    )

    # Round the handle end
    draw.ellipse(
        [handle_end_x - glass_thickness/2, handle_end_y - glass_thickness/2,
         handle_end_x + glass_thickness/2, handle_end_y + glass_thickness/2],
        fill=GOLD + (255,)
    )

    # Convert to RGB with navy background for LinkedIn compatibility
    background = Image.new('RGB', (size, size), NAVY)
    background.paste(img, (0, 0), img)

    return background

def create_company_banner(width=1128, height=191):
    """
    Create the company page banner - clean, branded, professional.
    Logo overlaps bottom-left (~200px), so content is RIGHT-ALIGNED.
    """
    img = Image.new('RGB', (width, height), NAVY)
    draw = ImageDraw.Draw(img)

    # Safe zone: Logo covers ~200px from left on company pages
    # Keep all content to the right of that
    safe_left = 220  # Logo safe zone
    safe_right = 60  # Right margin
    content_area_center = safe_left + (width - safe_left - safe_right) // 2

    tagline_font = get_font(32, bold=True)
    subtitle_font = get_font(22)

    # Primary tagline - centered in safe area (right of logo)
    tagline = "Your mission deserves funding."
    bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
    tagline_width = bbox[2] - bbox[0]
    tagline_x = content_area_center - tagline_width // 2
    draw.text(
        (tagline_x, height // 2 - 40),
        tagline,
        fill=GOLD,
        font=tagline_font
    )

    # Subtitle
    subtitle = "AI-powered grant matching  •  143,000+ foundations  •  8M+ grants"
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = bbox[2] - bbox[0]
    subtitle_x = content_area_center - subtitle_width // 2
    draw.text(
        (subtitle_x, height // 2 + 15),
        subtitle,
        fill=WHITE,
        font=subtitle_font
    )

    return img

def create_personal_banner(width=1584, height=396):
    """
    Create the personal profile banner.
    Based on research: clear value prop, target audience, CTA, safe zones.
    """
    img = Image.new('RGB', (width, height), NAVY)
    draw = ImageDraw.Draw(img)

    # Safe zone: Profile photo covers ~350-400px from left on mobile
    # Keep all important content to the right of that
    safe_x = 420

    # Fonts - increased sizes for readability
    title_font = get_font(46, bold=True)
    cta_font = get_font(30)  # Increased for better readability

    # Main value proposition (what you help with)
    title = "Helping nonprofits find foundations"
    subtitle = "they didn't know existed"
    draw.text((safe_x, height // 2 - 75), title, fill=WHITE, font=title_font)
    draw.text((safe_x, height // 2 - 20), subtitle, fill=GOLD, font=title_font)

    # Target audience + what you share (CTA) - bigger now
    cta_text = "Follow for data insights on foundation giving"
    draw.text((safe_x, height // 2 + 55), cta_text, fill=WHITE, font=cta_font)

    # Right side: Key stat for credibility
    stat_font = get_font(24)  # Increased from 20
    stat_font_big = get_font(42, bold=True)  # Increased from 36

    stat_x = width - 250
    draw.text((stat_x, height // 2 - 45), "8M+", fill=GOLD, font=stat_font_big)
    draw.text((stat_x, height // 2 + 15), "grants analyzed", fill=WHITE, font=stat_font)

    return img

def main():
    """Generate all assets."""
    print("Creating LinkedIn assets...")

    # Create output directory if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Logo
    print("  - Logo (400x400px)...")
    logo = create_logo(400)
    logo_path = os.path.join(OUTPUT_DIR, "logo_400x400.png")
    logo.save(logo_path, "PNG")
    print(f"    Saved: {logo_path}")

    # Company banner
    print("  - Company banner (1128x191px)...")
    company_banner = create_company_banner(1128, 191)
    company_path = os.path.join(OUTPUT_DIR, "banner_company_1128x191.png")
    company_banner.save(company_path, "PNG")
    print(f"    Saved: {company_path}")

    # Personal banner
    print("  - Personal banner (1584x396px)...")
    personal_banner = create_personal_banner(1584, 396)
    personal_path = os.path.join(OUTPUT_DIR, "banner_personal_1584x396.png")
    personal_banner.save(personal_path, "PNG")
    print(f"    Saved: {personal_path}")

    print("\nDone! All assets created in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
