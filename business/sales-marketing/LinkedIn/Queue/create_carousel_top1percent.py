#!/usr/bin/env python3
"""
Create LinkedIn Carousel PDF: Top 1% Concentration
TheGrantScout - Week 3 Content
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
    page_width, page_height = letter
    x_offset = (page_width - SLIDE_WIDTH) / 2
    y_offset = (page_height - SLIDE_HEIGHT) / 2

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
    draw_text_centered(c, "67%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 120, GOLD)

    # Subtext
    draw_text_wrapped(c, "of foundation giving comes from just 1% of foundations",
                      center_x, y_offset + SLIDE_HEIGHT * 0.38, SLIDE_WIDTH * 0.8, 26, WHITE)

    # Swipe indicator
    draw_text_centered(c, "Swipe to see the concentration problem →", center_x, y_offset + 40, 14, GOLD, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_2_top1(c):
    """Slide 2: Top 1%"""
    x_offset, y_offset = create_slide(c, 2, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Category label
    draw_text_centered(c, "THE TOP 1%", center_x, y_offset + SLIDE_HEIGHT * 0.75, 24, GOLD, 'Helvetica')

    # Big stat
    draw_text_centered(c, "67%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 100, GOLD)
    draw_text_centered(c, "of all dollars", center_x, y_offset + SLIDE_HEIGHT * 0.42, 28, WHITE, 'Helvetica')

    # Details
    draw_text_centered(c, "1,125 foundations", center_x, y_offset + SLIDE_HEIGHT * 0.28, 24, WHITE, 'Helvetica')
    draw_text_centered(c, "$325 billion in grants", center_x, y_offset + SLIDE_HEIGHT * 0.22, 20, LIGHT_GRAY, 'Helvetica')

    # Context
    draw_text_wrapped(c, "Gates, Ford, Bloomberg... everyone is chasing these",
                      center_x, y_offset + SLIDE_HEIGHT * 0.12, SLIDE_WIDTH * 0.75, 18, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_3_top2to5(c):
    """Slide 3: Top 2-5%"""
    x_offset, y_offset = create_slide(c, 3, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Category label
    draw_text_centered(c, "THE TOP 2-5%", center_x, y_offset + SLIDE_HEIGHT * 0.75, 24, GOLD, 'Helvetica')

    # Big stat
    draw_text_centered(c, "16%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 100, GOLD)
    draw_text_centered(c, "of all dollars", center_x, y_offset + SLIDE_HEIGHT * 0.42, 28, WHITE, 'Helvetica')

    # Details
    draw_text_centered(c, "4,500 foundations", center_x, y_offset + SLIDE_HEIGHT * 0.28, 24, WHITE, 'Helvetica')
    draw_text_centered(c, "$76 billion in grants", center_x, y_offset + SLIDE_HEIGHT * 0.22, 20, LIGHT_GRAY, 'Helvetica')

    # Context
    draw_text_wrapped(c, "Less competitive, still substantial capacity",
                      center_x, y_offset + SLIDE_HEIGHT * 0.12, SLIDE_WIDTH * 0.75, 18, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_4_bottom75(c):
    """Slide 4: Bottom 75%"""
    x_offset, y_offset = create_slide(c, 4, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Category label
    draw_text_centered(c, "THE BOTTOM 75%", center_x, y_offset + SLIDE_HEIGHT * 0.75, 24, GOLD, 'Helvetica')

    # Big stat
    draw_text_centered(c, "4%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 100, GOLD)
    draw_text_centered(c, "of all dollars", center_x, y_offset + SLIDE_HEIGHT * 0.42, 28, WHITE, 'Helvetica')

    # Details
    draw_text_centered(c, "84,310 foundations", center_x, y_offset + SLIDE_HEIGHT * 0.28, 24, WHITE, 'Helvetica')
    draw_text_centered(c, "$20 billion in grants", center_x, y_offset + SLIDE_HEIGHT * 0.22, 20, LIGHT_GRAY, 'Helvetica')

    # Context
    draw_text_wrapped(c, "Small grants, but far less competition",
                      center_x, y_offset + SLIDE_HEIGHT * 0.12, SLIDE_WIDTH * 0.75, 18, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_5_insight(c):
    """Slide 5: The Insight"""
    x_offset, y_offset = create_slide(c, 5, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Header
    draw_text_centered(c, "THE INSIGHT", center_x, y_offset + SLIDE_HEIGHT * 0.78, 20, GOLD, 'Helvetica')

    # Main message
    draw_text_wrapped(c, "Everyone chases the top 1%.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.62, SLIDE_WIDTH * 0.85, 32, WHITE)

    draw_text_wrapped(c, "The 2-25% is underworked.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.48, SLIDE_WIDTH * 0.85, 32, GOLD)

    # Supporting text
    draw_text_wrapped(c, "That middle tier represents 29% of all giving with far less competition for your proposal.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.28, SLIDE_WIDTH * 0.8, 20, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_6_takeaway(c):
    """Slide 6: Takeaway"""
    x_offset, y_offset = create_slide(c, 6, 6)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Header
    draw_text_centered(c, "THE TAKEAWAY", center_x, y_offset + SLIDE_HEIGHT * 0.78, 20, GOLD, 'Helvetica')

    # Main message
    draw_text_wrapped(c, "Target the middle tier.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.60, SLIDE_WIDTH * 0.85, 36, WHITE)

    # Supporting points
    points = [
        "Substantial grant capacity",
        "Less crowded applications",
        "Often simpler processes"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.42
    for point in points:
        draw_text_centered(c, "→ " + point, center_x, y_pos, 22, LIGHT_GRAY, 'Helvetica')
        y_pos -= 40

    # CTA
    c.setFillColor(GOLD)
    c.roundRect(center_x - 120, y_offset + 60, 240, 45, 8, fill=True, stroke=False)
    draw_text_centered(c, "Follow for more insights", center_x, y_offset + 78, 18, NAVY, 'Helvetica-Bold')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def main():
    output_dir = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/6. Linkedin Outreach/Carousels/PDFs"
    output_file = os.path.join(output_dir, "CAROUSEL_2025-01-20_top1percent_concentration.pdf")

    c = canvas.Canvas(output_file, pagesize=letter)

    slide_1_hook(c)
    c.showPage()

    slide_2_top1(c)
    c.showPage()

    slide_3_top2to5(c)
    c.showPage()

    slide_4_bottom75(c)
    c.showPage()

    slide_5_insight(c)
    c.showPage()

    slide_6_takeaway(c)

    c.save()
    print(f"Carousel PDF created: {output_file}")

if __name__ == "__main__":
    main()
