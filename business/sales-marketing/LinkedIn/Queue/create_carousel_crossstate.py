#!/usr/bin/env python3
"""
Create LinkedIn Carousel PDF: Cross-State Giving Patterns
TheGrantScout - Launch Week Content (Week 2)
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

# Slide dimensions (4:5 ratio)
SLIDE_WIDTH = 5.4 * inch
SLIDE_HEIGHT = 6.75 * inch

def create_slide(c):
    """Create a single slide background"""
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
    x_offset, y_offset = create_slide(c)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Main stat
    draw_text_centered(c, "48%", center_x, y_offset + SLIDE_HEIGHT * 0.55, 120, GOLD)

    # Subtext
    draw_text_wrapped(c, "of foundation grants cross state lines",
                      center_x, y_offset + SLIDE_HEIGHT * 0.38, SLIDE_WIDTH * 0.8, 28, WHITE)

    # Swipe indicator
    draw_text_centered(c, "Here's where the money flows →", center_x, y_offset + 40, 14, GOLD, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_2_breakdown(c):
    """Slide 2: In-state vs Out-of-state"""
    x_offset, y_offset = create_slide(c)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Title
    draw_text_centered(c, "THE SPLIT", center_x, y_offset + SLIDE_HEIGHT * 0.78, 20, GOLD, 'Helvetica')

    # Two columns of data
    # In-state
    draw_text_centered(c, "In-State", center_x - 70, y_offset + SLIDE_HEIGHT * 0.62, 22, LIGHT_GRAY, 'Helvetica')
    draw_text_centered(c, "52%", center_x - 70, y_offset + SLIDE_HEIGHT * 0.50, 48, WHITE)

    # Divider
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(center_x, y_offset + SLIDE_HEIGHT * 0.45, center_x, y_offset + SLIDE_HEIGHT * 0.65)

    # Out-of-state
    draw_text_centered(c, "Out-of-State", center_x + 70, y_offset + SLIDE_HEIGHT * 0.62, 22, LIGHT_GRAY, 'Helvetica')
    draw_text_centered(c, "48%", center_x + 70, y_offset + SLIDE_HEIGHT * 0.50, 48, GOLD)

    # Total dollars
    draw_text_centered(c, "From 8.3 million grants analyzed", center_x, y_offset + SLIDE_HEIGHT * 0.32, 18, LIGHT_GRAY, 'Helvetica')

    # Context
    draw_text_wrapped(c, "Nearly half of all foundation giving crosses state boundaries",
                      center_x, y_offset + SLIDE_HEIGHT * 0.20, SLIDE_WIDTH * 0.8, 18, WHITE, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_3_top_corridor(c):
    """Slide 3: Top giving corridor"""
    x_offset, y_offset = create_slide(c)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Title
    draw_text_centered(c, "#1 GIVING CORRIDOR", center_x, y_offset + SLIDE_HEIGHT * 0.78, 18, GOLD, 'Helvetica')

    # Route
    draw_text_centered(c, "California → New York", center_x, y_offset + SLIDE_HEIGHT * 0.62, 32, WHITE)

    # Stats
    draw_text_centered(c, "$22.5 Billion", center_x, y_offset + SLIDE_HEIGHT * 0.48, 52, GOLD)
    draw_text_centered(c, "268,000+ grants", center_x, y_offset + SLIDE_HEIGHT * 0.36, 22, WHITE, 'Helvetica')

    # Context
    draw_text_wrapped(c, "CA foundations fund NY nonprofits more than any other cross-state pair",
                      center_x, y_offset + SLIDE_HEIGHT * 0.20, SLIDE_WIDTH * 0.75, 16, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_4_dc_magnet(c):
    """Slide 4: DC as a magnet"""
    x_offset, y_offset = create_slide(c)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Title
    draw_text_centered(c, "THE DC EFFECT", center_x, y_offset + SLIDE_HEIGHT * 0.78, 18, GOLD, 'Helvetica')

    # Main insight
    draw_text_wrapped(c, "DC is the only 'state' that receives MORE than it gives",
                      center_x, y_offset + SLIDE_HEIGHT * 0.62, SLIDE_WIDTH * 0.8, 24, WHITE)

    # Stat
    draw_text_centered(c, "+$3.75B", center_x, y_offset + SLIDE_HEIGHT * 0.42, 56, GOLD)
    draw_text_centered(c, "net inflow", center_x, y_offset + SLIDE_HEIGHT * 0.34, 20, LIGHT_GRAY, 'Helvetica')

    # Why
    draw_text_wrapped(c, "National nonprofits headquarter in DC. Foundations everywhere fund them.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.18, SLIDE_WIDTH * 0.75, 16, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_5_top_corridors(c):
    """Slide 5: Top 5 corridors"""
    x_offset, y_offset = create_slide(c)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Title
    draw_text_centered(c, "TOP 5 GIVING CORRIDORS", center_x, y_offset + SLIDE_HEIGHT * 0.82, 18, GOLD, 'Helvetica')

    corridors = [
        ("1. CA → NY", "$22.5B"),
        ("2. NY → DC", "$21.9B"),
        ("3. NY → CA", "$20.6B"),
        ("4. WA → NY", "$19.3B"),
        ("5. WA → DC", "$19.1B"),
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.68
    for route, amount in corridors:
        # Route on left
        c.setFillColor(WHITE)
        c.setFont('Helvetica', 18)
        c.drawString(x_offset + 30, y_pos, route)

        # Amount on right
        c.setFillColor(GOLD)
        c.setFont('Helvetica-Bold', 18)
        amount_width = c.stringWidth(amount, 'Helvetica-Bold', 18)
        c.drawString(x_offset + SLIDE_WIDTH - 30 - amount_width, y_pos, amount)

        y_pos -= 38

    # Note
    draw_text_wrapped(c, "WA = Gates Foundation effect",
                      center_x, y_offset + SLIDE_HEIGHT * 0.18, SLIDE_WIDTH * 0.75, 16, LIGHT_GRAY, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_6_takeaway(c):
    """Slide 6: Takeaway"""
    x_offset, y_offset = create_slide(c)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Header
    draw_text_centered(c, "THE TAKEAWAY", center_x, y_offset + SLIDE_HEIGHT * 0.80, 20, GOLD, 'Helvetica')

    # Main message
    draw_text_wrapped(c, "Don't limit yourself to local foundations.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.64, SLIDE_WIDTH * 0.85, 28, WHITE)

    # Supporting points
    draw_text_centered(c, "If you're prospecting nationally:", center_x, y_offset + SLIDE_HEIGHT * 0.48, 20, GOLD, 'Helvetica')

    points = [
        "→ NY, CA, WA foundations give everywhere",
        "→ DC-based? You have a geographic edge",
        "→ 48% of grants ignore state lines"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.40
    for point in points:
        draw_text_centered(c, point, center_x, y_pos, 17, WHITE, 'Helvetica')
        y_pos -= 32

    # CTA
    c.setFillColor(GOLD)
    c.roundRect(center_x - 120, y_offset + 55, 240, 45, 8, fill=True, stroke=False)
    draw_text_centered(c, "Follow for more data insights", center_x, y_offset + 73, 17, NAVY, 'Helvetica-Bold')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def main():
    output_dir = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/6. Linkedin Outreach"
    output_file = os.path.join(output_dir, "CAROUSEL_2025-01-14_cross_state_giving.pdf")

    c = canvas.Canvas(output_file, pagesize=letter)

    # Create all slides
    slide_1_hook(c)
    c.showPage()

    slide_2_breakdown(c)
    c.showPage()

    slide_3_top_corridor(c)
    c.showPage()

    slide_4_dc_magnet(c)
    c.showPage()

    slide_5_top_corridors(c)
    c.showPage()

    slide_6_takeaway(c)

    c.save()
    print(f"Carousel PDF created: {output_file}")

if __name__ == "__main__":
    main()
