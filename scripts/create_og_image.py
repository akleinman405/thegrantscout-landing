#!/usr/bin/env python3
"""
Create OG image for TheGrantScout social sharing
Dimensions: 1200x630 pixels
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Dimensions for OG image
WIDTH = 1200
HEIGHT = 630

# Brand colors from tailwind.config.js
PRIMARY = '#1e3a5f'
PRIMARY_DARK = '#152b47'
ACCENT_GOLD = '#d4a853'
WHITE = '#ffffff'

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_og_image():
    # Create image with primary dark background
    img = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(PRIMARY_DARK))
    draw = ImageDraw.Draw(img)

    # Add a subtle gradient effect with rectangles
    for i in range(HEIGHT):
        # Create gradient from PRIMARY_DARK to PRIMARY
        ratio = i / HEIGHT
        r1, g1, b1 = hex_to_rgb(PRIMARY_DARK)
        r2, g2, b2 = hex_to_rgb(PRIMARY)
        r = int(r1 + (r2 - r1) * ratio * 0.5)
        g = int(g1 + (g2 - g1) * ratio * 0.5)
        b = int(b1 + (b2 - b1) * ratio * 0.5)
        draw.line([(0, i), (WIDTH, i)], fill=(r, g, b))

    # Add decorative gold accent line at top
    draw.rectangle([0, 0, WIDTH, 6], fill=hex_to_rgb(ACCENT_GOLD))

    # Add decorative gold accent line at bottom
    draw.rectangle([0, HEIGHT-6, WIDTH, HEIGHT], fill=hex_to_rgb(ACCENT_GOLD))

    # Try to use a nice font, fallback to default
    try:
        # Try Helvetica (macOS)
        title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 72)
        tagline_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
        subtitle_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 28)
    except:
        try:
            # Try Arial (Windows/common)
            title_font = ImageFont.truetype('Arial.ttf', 72)
            tagline_font = ImageFont.truetype('Arial.ttf', 32)
            subtitle_font = ImageFont.truetype('Arial.ttf', 28)
        except:
            # Fallback to default
            title_font = ImageFont.load_default()
            tagline_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()

    # Main title - TheGrantScout
    title = "TheGrantScout"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2
    title_y = 180

    # Draw title with gold color
    draw.text((title_x, title_y), title, font=title_font, fill=hex_to_rgb(ACCENT_GOLD))

    # Tagline
    tagline = "AI-Powered Grant Matching for Nonprofits"
    tagline_bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (WIDTH - tagline_width) // 2
    tagline_y = title_y + 100

    draw.text((tagline_x, tagline_y), tagline, font=tagline_font, fill=hex_to_rgb(WHITE))

    # Subtitle/value prop
    subtitle = "Find foundations already funding work like yours"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (WIDTH - subtitle_width) // 2
    subtitle_y = tagline_y + 60

    # Draw with slightly muted white
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(200, 200, 200))

    # Stats bar at bottom
    stats_y = HEIGHT - 120
    stats = ["143,000+ Foundations", "8M+ Grants Analyzed", "AI-Powered Matching"]
    stat_width = WIDTH // 3

    for i, stat in enumerate(stats):
        stat_bbox = draw.textbbox((0, 0), stat, font=subtitle_font)
        stat_text_width = stat_bbox[2] - stat_bbox[0]
        stat_x = (stat_width * i) + (stat_width - stat_text_width) // 2
        draw.text((stat_x, stats_y), stat, font=subtitle_font, fill=hex_to_rgb(ACCENT_GOLD))

    # Save the image
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'og-image.png')
    img.save(output_path, 'PNG', quality=95)
    print(f"Created OG image: {output_path}")

    return output_path

if __name__ == '__main__':
    create_og_image()
