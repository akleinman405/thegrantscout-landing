#!/usr/bin/env python3
"""
Create LinkedIn Carousel PDF: 5 Places to Research Foundations
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
    x_offset, y_offset = create_slide(c, 1, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Main number
    draw_text_centered(c, "5", center_x, y_offset + SLIDE_HEIGHT * 0.58, 140, GOLD)

    # Subtext
    draw_text_wrapped(c, "places to research foundations beyond Google",
                      center_x, y_offset + SLIDE_HEIGHT * 0.38, SLIDE_WIDTH * 0.8, 28, WHITE)

    # Context
    draw_text_wrapped(c, "43% of foundations have no website",
                      center_x, y_offset + SLIDE_HEIGHT * 0.22, SLIDE_WIDTH * 0.75, 18, LIGHT_GRAY, 'Helvetica')

    # Swipe indicator
    draw_text_centered(c, "Swipe to see the sources →", center_x, y_offset + 40, 14, GOLD, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_2_990pf(c):
    """Slide 2: 990-PF Filings"""
    x_offset, y_offset = create_slide(c, 2, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number
    draw_text_centered(c, "1", center_x, y_offset + SLIDE_HEIGHT * 0.78, 60, GOLD)

    # Title
    draw_text_centered(c, "990-PF Filings", center_x, y_offset + SLIDE_HEIGHT * 0.62, 36, WHITE)

    # Benefits
    benefits = [
        "Free and publicly available",
        "Covers every private foundation",
        "Shows actual grants given",
        "Updated annually"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.45
    for benefit in benefits:
        draw_text_centered(c, "→ " + benefit, center_x, y_pos, 20, LIGHT_GRAY, 'Helvetica')
        y_pos -= 35

    # Pro tip
    draw_text_wrapped(c, "Pro tip: Search on IRS Tax Exempt Organization Search",
                      center_x, y_offset + SLIDE_HEIGHT * 0.12, SLIDE_WIDTH * 0.8, 16, GOLD, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_3_state(c):
    """Slide 3: State Charity Registries"""
    x_offset, y_offset = create_slide(c, 3, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number
    draw_text_centered(c, "2", center_x, y_offset + SLIDE_HEIGHT * 0.78, 60, GOLD)

    # Title
    draw_text_centered(c, "State Charity Registries", center_x, y_offset + SLIDE_HEIGHT * 0.62, 32, WHITE)

    # Benefits
    benefits = [
        "Local foundations often missed",
        "Attorney General offices",
        "Registration requirements vary",
        "Great for regional research"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.45
    for benefit in benefits:
        draw_text_centered(c, "→ " + benefit, center_x, y_pos, 20, LIGHT_GRAY, 'Helvetica')
        y_pos -= 35

    # Pro tip
    draw_text_wrapped(c, "Pro tip: Search '[Your State] charity registration database'",
                      center_x, y_offset + SLIDE_HEIGHT * 0.12, SLIDE_WIDTH * 0.8, 16, GOLD, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_4_community(c):
    """Slide 4: Community Foundation Networks"""
    x_offset, y_offset = create_slide(c, 4, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number
    draw_text_centered(c, "3", center_x, y_offset + SLIDE_HEIGHT * 0.78, 60, GOLD)

    # Title
    draw_text_wrapped(c, "Community Foundation Networks",
                      center_x, y_offset + SLIDE_HEIGHT * 0.62, SLIDE_WIDTH * 0.9, 32, WHITE)

    # Benefits
    benefits = [
        "Warm introductions possible",
        "Local knowledge and context",
        "Donor-advised fund access",
        "Relationship-driven"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.42
    for benefit in benefits:
        draw_text_centered(c, "→ " + benefit, center_x, y_pos, 20, LIGHT_GRAY, 'Helvetica')
        y_pos -= 35

    # Pro tip
    draw_text_wrapped(c, "Pro tip: Ask your local CF for foundation referrals",
                      center_x, y_offset + SLIDE_HEIGHT * 0.12, SLIDE_WIDTH * 0.8, 16, GOLD, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_5_peer(c):
    """Slide 5: Peer Organization Grant Lists"""
    x_offset, y_offset = create_slide(c, 5, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number
    draw_text_centered(c, "4", center_x, y_offset + SLIDE_HEIGHT * 0.78, 60, GOLD)

    # Title
    draw_text_wrapped(c, "Peer Organization Grant Lists",
                      center_x, y_offset + SLIDE_HEIGHT * 0.62, SLIDE_WIDTH * 0.9, 32, WHITE)

    # Benefits
    benefits = [
        "See who funds orgs like yours",
        "Found in 990 Schedule A",
        "Proven interest in your sector",
        "Natural fit indicators"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.42
    for benefit in benefits:
        draw_text_centered(c, "→ " + benefit, center_x, y_pos, 20, LIGHT_GRAY, 'Helvetica')
        y_pos -= 35

    # Pro tip
    draw_text_wrapped(c, "Pro tip: Check similar nonprofits' 990s for funders",
                      center_x, y_offset + SLIDE_HEIGHT * 0.12, SLIDE_WIDTH * 0.8, 16, GOLD, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_6_annual(c):
    """Slide 6: Foundation Annual Reports"""
    x_offset, y_offset = create_slide(c, 6, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Number
    draw_text_centered(c, "5", center_x, y_offset + SLIDE_HEIGHT * 0.78, 60, GOLD)

    # Title
    draw_text_wrapped(c, "Foundation Annual Reports",
                      center_x, y_offset + SLIDE_HEIGHT * 0.62, SLIDE_WIDTH * 0.9, 32, WHITE)

    # Benefits
    benefits = [
        "Current priorities revealed",
        "Recent grants listed",
        "Leadership information",
        "Strategic direction clues"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.42
    for benefit in benefits:
        draw_text_centered(c, "→ " + benefit, center_x, y_pos, 20, LIGHT_GRAY, 'Helvetica')
        y_pos -= 35

    # Pro tip
    draw_text_wrapped(c, "Pro tip: Compare to 990-PF to spot changes",
                      center_x, y_offset + SLIDE_HEIGHT * 0.12, SLIDE_WIDTH * 0.8, 16, GOLD, 'Helvetica')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def slide_7_takeaway(c):
    """Slide 7: Takeaway"""
    x_offset, y_offset = create_slide(c, 7, 7)
    center_x = x_offset + SLIDE_WIDTH / 2

    # Header
    draw_text_centered(c, "THE TAKEAWAY", center_x, y_offset + SLIDE_HEIGHT * 0.78, 20, GOLD, 'Helvetica')

    # Main message
    draw_text_wrapped(c, "Layer multiple sources for the complete picture.",
                      center_x, y_offset + SLIDE_HEIGHT * 0.58, SLIDE_WIDTH * 0.85, 28, WHITE)

    # Summary
    draw_text_centered(c, "The best prospectors use all five:", center_x, y_offset + SLIDE_HEIGHT * 0.42, 20, GOLD, 'Helvetica')

    sources = [
        "1. 990-PF filings",
        "2. State registries",
        "3. Community foundations",
        "4. Peer organization 990s",
        "5. Annual reports"
    ]

    y_pos = y_offset + SLIDE_HEIGHT * 0.35
    for source in sources:
        draw_text_centered(c, source, center_x, y_pos, 18, LIGHT_GRAY, 'Helvetica')
        y_pos -= 28

    # CTA
    c.setFillColor(GOLD)
    c.roundRect(center_x - 120, y_offset + 60, 240, 45, 8, fill=True, stroke=False)
    draw_text_centered(c, "Save this for later", center_x, y_offset + 78, 18, NAVY, 'Helvetica-Bold')

    # Logo
    draw_text_centered(c, "TheGrantScout", center_x, y_offset + SLIDE_HEIGHT - 40, 16, GOLD, 'Helvetica')

def main():
    output_dir = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/6. Linkedin Outreach/Carousels/PDFs"
    output_file = os.path.join(output_dir, "CAROUSEL_2025-01-22_5_research_sources.pdf")

    c = canvas.Canvas(output_file, pagesize=letter)

    slide_1_hook(c)
    c.showPage()

    slide_2_990pf(c)
    c.showPage()

    slide_3_state(c)
    c.showPage()

    slide_4_community(c)
    c.showPage()

    slide_5_peer(c)
    c.showPage()

    slide_6_annual(c)
    c.showPage()

    slide_7_takeaway(c)

    c.save()
    print(f"Carousel PDF created: {output_file}")

if __name__ == "__main__":
    main()
