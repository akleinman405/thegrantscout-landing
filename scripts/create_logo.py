#!/usr/bin/env python3
"""
Create square logo for TheGrantScout structured data
Dimensions: 512x512 pixels (will display well at any size down to 112x112)
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Dimensions for logo
SIZE = 512

# Brand colors from tailwind.config.js
PRIMARY = '#1e3a5f'
PRIMARY_DARK = '#152b47'
ACCENT_GOLD = '#d4a853'
WHITE = '#ffffff'

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_logo():
    # Create image with primary dark background
    img = Image.new('RGB', (SIZE, SIZE), hex_to_rgb(PRIMARY_DARK))
    draw = ImageDraw.Draw(img)

    # Add a subtle gradient effect with rectangles
    for i in range(SIZE):
        ratio = i / SIZE
        r1, g1, b1 = hex_to_rgb(PRIMARY_DARK)
        r2, g2, b2 = hex_to_rgb(PRIMARY)
        r = int(r1 + (r2 - r1) * ratio * 0.5)
        g = int(g1 + (g2 - g1) * ratio * 0.5)
        b = int(b1 + (b2 - b1) * ratio * 0.5)
        draw.line([(0, i), (SIZE, i)], fill=(r, g, b))

    # Add decorative gold border
    border_width = 8
    draw.rectangle([0, 0, SIZE-1, border_width], fill=hex_to_rgb(ACCENT_GOLD))
    draw.rectangle([0, SIZE-border_width, SIZE-1, SIZE-1], fill=hex_to_rgb(ACCENT_GOLD))
    draw.rectangle([0, 0, border_width, SIZE-1], fill=hex_to_rgb(ACCENT_GOLD))
    draw.rectangle([SIZE-border_width, 0, SIZE-1, SIZE-1], fill=hex_to_rgb(ACCENT_GOLD))

    # Try to use a nice font, fallback to default
    try:
        # Try Helvetica (macOS)
        title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 120)
        subtitle_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 36)
    except:
        try:
            # Try Arial (Windows/common)
            title_font = ImageFont.truetype('Arial.ttf', 120)
            subtitle_font = ImageFont.truetype('Arial.ttf', 36)
        except:
            # Fallback to default
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()

    # Main text - "TGS" as logo mark
    logo_text = "TGS"
    logo_bbox = draw.textbbox((0, 0), logo_text, font=title_font)
    logo_width = logo_bbox[2] - logo_bbox[0]
    logo_height = logo_bbox[3] - logo_bbox[1]
    logo_x = (SIZE - logo_width) // 2
    logo_y = (SIZE - logo_height) // 2 - 40

    # Draw logo text with gold color
    draw.text((logo_x, logo_y), logo_text, font=title_font, fill=hex_to_rgb(ACCENT_GOLD))

    # Subtitle
    subtitle = "TheGrantScout"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (SIZE - subtitle_width) // 2
    subtitle_y = logo_y + logo_height + 30

    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=hex_to_rgb(WHITE))

    # Save the image
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'logo.png')
    img.save(output_path, 'PNG', quality=95)
    print(f"Created logo: {output_path}")
    print(f"Size: {SIZE}x{SIZE} pixels")

    return output_path

if __name__ == '__main__':
    create_logo()
