#!/usr/bin/env python3
"""
Create LinkedIn Carousel PDF: Foundation Size Distribution
TheGrantScout - Launch Week Content
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import os

# Brand Colors
NAVY = HexColor('#1B365D')
GOLD = HexColor('#C9A227')
WHITE = HexColor('#FFFFFF')
LIGHT_GRAY = HexColor('#F5F5F5')
DARK_GRAY = HexColor('#333333')

# Slide dimensions (1080x1350 = 4:5 ratio, scaled down)
SLIDE_WIDTH = 5.4 * inch
SLIDE_HEIGHT = 6.75 * inch

def create_slide(c, slide_num, total_slides):
    """Create a single slide"""
    # Page setup - center the slide on letter page
    page_width, page_height = letter
    x_offset = (page_width - SLIDE_WIDTH) / 2
    y_offset = (page_height - SLIDE_HEIGHT) / 2

    # Background
    c.setFillColor(NAVY)
    c.rect(x_offset, y_offset, SLIDE_WIDTH, SLIDE_HEIGHT, fill=True, stroke=False)

    return x_offset, y_offset

def draw_text_centered(c, text, x, y, font_size, color=WHITE, font='Helvetica-Bold'):
    """Draw centered text"""
    c.setFillColor(color)
    c.setFont(font, font_size)
    text_width = c.stringWidth(text, font, font_size)
    c.drawString(x - text_width/2, y, text)

def draw_text_wrapped(c, text, x, y, max_width, font_size, color=WHITE, font='Helvetica-Bold', leading=None):
    """Draw wrapped text centered"""
    if leading is None:
        leading = font_size * 1.3
    c.setFillColor(color)
    c.setFont(font, font_size)
    lines = simpleSplit(text, font, font_size, max_width)
    for i, line in enumerate(lines):
        text_width = c.stringWidth(line, font, font_size)
        c.drawString(x - text_width/2, y - (i * leading), line)
    return len(lines)

def slide_1_hook(c):
    """Slide 1: Hook"""
    x_offset, y_offset = create_slide(c, 1, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Main stat
    draw_text_centered(c, "70%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 120, GOLD)

    # Subtext
    draw_text_wrapped(c, "of US foundations are smaller than you think",
                      center_x, y_offset + SLIDE_HEIGHT * 0.38, SLIDE_WIDTH * 0.8, 28, WHITE)

    # Swipe indicator
    draw_text_centered(c, "Swipe to see the breakdown →", center_x, y_offset + 40, 14, GOLD, 'Helvetica')

    # Logo/brand
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_2_under_1m(c):
    """Slide 2: Under $1M"""
    x_offset, y_offset = create_slide(c, 2, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Category label
    draw_text_centered(c, "FOUNDATIONS WITH", center_x, y_offset + SLIDE_HEIGHT * 0.75, 18, GOLD, 'Helvetica')
    draw_text_centered(c, "Under $1M in Assets", center_x, y_offset + SLIDE_HEIGHT * 0.68, 32, WHITE)

    # Big stat
    draw_text_centered(c, "70.3%", center_x, y_offset + SLIDE_HEIGHT * 0.48, 100, GOLD)

    # Count
    draw_text_centered(c, "21,445 foundations", center_x, y_offset + SLIDE_HEIGHT * 0.32, 24, WHITE, 'Helvetica')

    # Context
    draw_text_wrapped(c, "Most are family foundations you've never heard of",
                      center_x, y_offset + SLIDE_HEIGHT * 0.18, SLIDE_WIDTH * 0.75, 20, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_3_1m_10m(c):
    """Slide 3: $1M-$10M"""
    x_offset, y_offset = create_slide(c, 3, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Category label
    draw_text_centered(c, "FOUNDATIONS WITH", center_x, y_offset + SLIDE_HEIGHT * 0.75, 18, GOLD, 'Helvetica')
    draw_text_centered(c, "$1M - $10M in Assets", center_x, y_offset + SLIDE_HEIGHT * 0.68, 32, WHITE)

    # Big stat
    draw_text_centered(c, "24.9%", center_x, y_offset + SLIDE_HEIGHT * 0.48, 100, GOLD)

    # Count
    draw_text_centered(c, "7,593 foundations", center_x, y_offset + SLIDE_HEIGHT * 0.32, 24, WHITE, 'Helvetica')

    # Context
    draw_text_wrapped(c, "The 'sweet spot' - substantial assets, less competition",
                      center_x, y_offset + SLIDE_HEIGHT * 0.18, SLIDE_WIDTH * 0.75, 20, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_4_10m_100m(c):
    """Slide 4: $10M-$100M"""
    x_offset, y_offset = create_slide(c, 4, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Category label
    draw_text_centered(c, "FOUNDATIONS WITH", center_x, y_offset + SLIDE_HEIGHT * 0.75, 18, GOLD, 'Helvetica')
    draw_text_centered(c, "$10M - $100M in Assets", center_x, y_offset + SLIDE_HEIGHT * 0.68, 32, WHITE)

    # Big stat
    draw_text_centered(c, "4.6%", center_x, y_offset + SLIDE_HEIGHT * 0.48, 100, GOLD)

    # Count
    draw_text_centered(c, "1,397 foundations", center_x, y_offset + SLIDE_HEIGHT * 0.32, 24, WHITE, 'Helvetica')

    # Context
    draw_text_wrapped(c, "The ones everyone is chasing",
                      center_x, y_offset + SLIDE_HEIGHT * 0.18, SLIDE_WIDTH * 0.75, 20, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_5_100m_plus(c):
    """Slide 5: $100M+"""
    x_offset, y_offset = create_slide(c, 5, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Category label
    draw_text_centered(c, "FOUNDATIONS WITH", center_x, y_offset + SLIDE_HEIGHT * 0.75, 18, GOLD, 'Helvetica')
    draw_text_centered(c, "$100M+ in Assets", center_x, y_offset + SLIDE_HEIGHT * 0.68, 32, WHITE)

    # Big stat
    draw_text_centered(c, "0.3%", center_x, y_offset + SLIDE_HEIGHT * 0.48, 100, GOLD)

    # Count
    draw_text_centered(c, "90 foundations", center_x, y_offset + SLIDE_HEIGHT * 0.32, 24, WHITE, 'Helvetica')

    # Context
    draw_text_wrapped(c, "Gates, Ford, Bloomberg... and 87 others",
                      center_x, y_offset + SLIDE_HEIGHT * 0.18, SLIDE_WIDTH * 0.75, 20, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_6_takeaway(c):
    """Slide 6: Takeaway"""
    x_offset, y_offset = create_slide(c, 6, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Header
    draw_text_centered(c, "THE TAKEAWAY", center_x, y_offset + SLIDE_HEIGHT * 0.78, 20, GOLD, 'Helvetica')

    # Main message
    draw_text_wrapped(c, "Stop chasing only the big names.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.60, SLIDE_WIDTH * 0.85, 32, WHITE)

    # Supporting points
    draw_text_centered(c, "Small foundations mean:", center_x, y_offset + SLIDE_HEIGHT * 0.45, 22, GOLD, 'Helvetica')

    points = [
        "→ Less competition for funding",
        "→ Simpler application processes",
        "→ More personal relationships"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.38
    for point in points:
        draw_text_centered(c, point, center_x, y_pos, 20, WHITE, 'Helvetica')
        y_pos -= 35

    # CTA
    c.setFillColor(GOLD)
    c.roundRect(center_x - 120, y_offset + 60, 240, 45, 8, fill=True, stroke=False)
    draw_text_centered(c, "Follow for more insights", center_x, y_offset + 78, 18, NAVY, 'Helvetica-Bold')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def main():
    output_dir = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/6. Linkedin Outreach"
    output_file = os.path.join(output_dir, "CAROUSEL_2025-01-09_foundation_size_distribution.pdf")

    c = canvas.Canvas(output_file, pagesize=letter)

    # Create all slides
    slide_1_hook(c)
    c.showPage()

    slide_2_under_1m(c)
    c.showPage()

    slide_3_1m_10m(c)
    c.showPage()

    slide_4_10m_100m(c)
    c.showPage()

    slide_5_100m_plus(c)
    c.showPage()

    slide_6_takeaway(c)

    c.save()
    print(f"Carousel PDF created: {output_file}")

if __name__ == "__main__":
    main()
