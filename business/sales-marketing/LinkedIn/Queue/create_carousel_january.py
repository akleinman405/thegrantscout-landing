#!/usr/bin/env python3
"""
Create LinkedIn Carousel PDF: January Highlights
TheGrantScout - End of Month Recap
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
    x_offset, y_offset = create_slide(c, 1, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Date label
    draw_text_centered(c, "JANUARY 2025", center_x, y_offset + SLIDE_HEIGHT * 0.75, 20, GOLD, 'Helvetica')

    # Main number
    draw_text_centered(c, "5", center_x, y_offset + SLIDE_HEIGHT * 0.55, 140, GOLD)

    # Subtext
    draw_text_wrapped(c, "foundation insights that surprised everyone",
                      center_x, y_offset + SLIDE_HEIGHT * 0.35, SLIDE_WIDTH * 0.8, 28, WHITE)

    # Swipe indicator
    draw_text_centered(c, "Swipe to see the stats →", center_x, y_offset + 40, 14, GOLD, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_2_median(c):
    """Slide 2: Median Grant"""
    x_offset, y_offset = create_slide(c, 2, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number label
    draw_text_centered(c, "INSIGHT #1", center_x, y_offset + SLIDE_HEIGHT * 0.78, 18, GOLD, 'Helvetica')

    # Big stat
    draw_text_centered(c, "$3,500", center_x, y_offset + SLIDE_HEIGHT * 0.55, 80, GOLD)

    # Context
    draw_text_centered(c, "The median foundation grant", center_x, y_offset + SLIDE_HEIGHT * 0.40, 24, WHITE, 'Helvetica')

    # Comparison
    draw_text_wrapped(c, "Not $58,000 - that's the average, skewed by mega-grants. 53% of all grants are under $5,000.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.22, SLIDE_WIDTH * 0.8, 18, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_3_crossstate(c):
    """Slide 3: Cross-State Giving"""
    x_offset, y_offset = create_slide(c, 3, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number label
    draw_text_centered(c, "INSIGHT #2", center_x, y_offset + SLIDE_HEIGHT * 0.78, 18, GOLD, 'Helvetica')

    # Big stat
    draw_text_centered(c, "48%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 100, GOLD)

    # Context
    draw_text_centered(c, "of grants cross state lines", center_x, y_offset + SLIDE_HEIGHT * 0.40, 24, WHITE, 'Helvetica')

    # Implication
    draw_text_wrapped(c, "Your next funder might be 2,000 miles away. Don't limit prospecting to your state.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.22, SLIDE_WIDTH * 0.8, 18, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_4_small(c):
    """Slide 4: Small Foundations"""
    x_offset, y_offset = create_slide(c, 4, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number label
    draw_text_centered(c, "INSIGHT #3", center_x, y_offset + SLIDE_HEIGHT * 0.78, 18, GOLD, 'Helvetica')

    # Big stat
    draw_text_centered(c, "70%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 100, GOLD)

    # Context
    draw_text_centered(c, "have under $1M in assets", center_x, y_offset + SLIDE_HEIGHT * 0.40, 24, WHITE, 'Helvetica')

    # Implication
    draw_text_wrapped(c, "Most foundations are small. Smaller assets often mean simpler processes and less competition.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.22, SLIDE_WIDTH * 0.8, 18, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_5_website(c):
    """Slide 5: No Website"""
    x_offset, y_offset = create_slide(c, 5, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number label
    draw_text_centered(c, "INSIGHT #4", center_x, y_offset + SLIDE_HEIGHT * 0.78, 18, GOLD, 'Helvetica')

    # Big stat
    draw_text_centered(c, "43%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 100, GOLD)

    # Context
    draw_text_centered(c, "have no website", center_x, y_offset + SLIDE_HEIGHT * 0.40, 24, WHITE, 'Helvetica')

    # Implication
    draw_text_wrapped(c, "Google won't find nearly half of all foundations. You need 990-PF research to find the hidden funders.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.22, SLIDE_WIDTH * 0.8, 18, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_6_onetime(c):
    """Slide 6: One-Time Grants"""
    x_offset, y_offset = create_slide(c, 6, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number label
    draw_text_centered(c, "INSIGHT #5", center_x, y_offset + SLIDE_HEIGHT * 0.78, 18, GOLD, 'Helvetica')

    # Big stat
    draw_text_centered(c, "50%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 100, GOLD)

    # Context
    draw_text_centered(c, "are one-time only", center_x, y_offset + SLIDE_HEIGHT * 0.40, 24, WHITE, 'Helvetica')

    # Implication
    draw_text_wrapped(c, "Half of grants are 'first and last.' But get a second grant? You're likely to get many more. Stewardship matters.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.22, SLIDE_WIDTH * 0.8, 18, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_7_takeaway(c):
    """Slide 7: Takeaway"""
    x_offset, y_offset = create_slide(c, 7, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Header
    draw_text_centered(c, "THAT'S JANUARY", center_x, y_offset + SLIDE_HEIGHT * 0.78, 20, GOLD, 'Helvetica')

    # Main message
    draw_text_wrapped(c, "More data insights coming in February.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.58, SLIDE_WIDTH * 0.85, 28, WHITE)

    # Topics preview
    draw_text_centered(c, "Coming up:", center_x, y_offset + SLIDE_HEIGHT * 0.42, 20, GOLD, 'Helvetica')

    topics = [
        "Foundation relationships",
        "Research tactics",
        "Sector deep dives"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.35
    for topic in topics:
        draw_text_centered(c, "→ " + topic, center_x, y_pos, 20, LIGHT_GRAY, 'Helvetica')
        y_pos -= 32

    # CTA
    c.setFillColor(GOLD)
    c.roundRect(center_x - 120, y_offset + 60, 240, 45, 8, fill=True, stroke=False)
    draw_text_centered(c, "Follow for more", center_x, y_offset + 78, 18, NAVY, 'Helvetica-Bold')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def main():
    output_dir = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/6. Linkedin Outreach/Carousels/PDFs"
    output_file = os.path.join(output_dir, "CAROUSEL_2025-01-31_january_highlights.pdf")

    c = canvas.Canvas(output_file, pagesize=letter)

    slide_1_hook(c)
    c.showPage()

    slide_2_median(c)
    c.showPage()

    slide_3_crossstate(c)
    c.showPage()

    slide_4_small(c)
    c.showPage()

    slide_5_website(c)
    c.showPage()

    slide_6_onetime(c)
    c.showPage()

    slide_7_takeaway(c)

    c.save()
    print(f"Carousel PDF created: {output_file}")

if __name__ == "__main__":
    main()
