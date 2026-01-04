#!/usr/bin/env python3
"""
Create stat graphics for LinkedIn data insight posts.
Brand colors: Navy #1e3a5f, Gold #d4a853, White #ffffff
LinkedIn image size: 1200x627 (recommended for feed)
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Brand colors
NAVY = (30, 58, 95)
GOLD = (212, 168, 83)
WHITE = (255, 255, 255)
LIGHT_GRAY = (240, 240, 240)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# LinkedIn recommended image size
WIDTH = 1200
HEIGHT = 627

def get_font(size, bold=False):
    """Get font."""
    if bold:
        paths = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf"]
    else:
        paths = ["/System/Library/Fonts/Supplemental/Arial.ttf"]
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()


def draw_centered_text(draw, text, y, font, fill, width=WIDTH):
    """Draw text centered horizontally."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    draw.text((x, y), text, fill=fill, font=font)


def create_median_vs_average():
    """Jan 7: Average $58K vs Median $3,500"""
    img = Image.new('RGB', (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(img)

    # Main stats
    big_font = get_font(84, bold=True)
    label_font = get_font(38)
    small_font = get_font(30)

    # Average
    draw.text((200, 180), "$58,000", fill=WHITE, font=big_font)
    draw.text((200, 270), "Average Grant", fill=LIGHT_GRAY, font=label_font)

    # VS
    draw_centered_text(draw, "vs", 220, get_font(48, bold=True), GOLD)

    # Median
    draw.text((700, 180), "$3,500", fill=GOLD, font=big_font)
    draw.text((700, 270), "Median Grant", fill=LIGHT_GRAY, font=label_font)

    # Bottom text
    draw_centered_text(draw, "A few mega-grants skew the average. The median tells the real story.", 370, small_font, WHITE)
    draw_centered_text(draw, "Source: Analysis of 8.3M foundation grants | TheGrantScout", 540, get_font(28), LIGHT_GRAY)

    return img


def create_top5_states():
    """Jan 13: Top 5 states for foundations"""
    img = Image.new('RGB', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    title_font = get_font(48, bold=True)
    num_font = get_font(42, bold=True)
    label_font = get_font(34)
    small_font = get_font(28)

    # Title
    draw_centered_text(draw, "States with the Most Private Foundations", 40, title_font, NAVY)

    # Data
    states = [
        ("1.", "California", "14,180"),
        ("2.", "New York", "13,788"),
        ("3.", "Texas", "12,170"),
        ("4.", "Florida", "10,593"),
        ("5.", "Pennsylvania", "8,271"),
    ]

    y_start = 130
    y_spacing = 85

    for i, (rank, state, count) in enumerate(states):
        y = y_start + i * y_spacing
        # Rank
        draw.text((150, y), rank, fill=GOLD, font=num_font)
        # State
        draw.text((220, y), state, fill=NAVY, font=num_font)
        # Count bar background
        bar_width = int(int(count.replace(",", "")) / 14180 * 400)
        draw.rectangle([550, y + 5, 550 + bar_width, y + 40], fill=NAVY)
        # Count
        draw.text((970, y), count, fill=NAVY, font=num_font)

    # Source
    draw_centered_text(draw, "Source: IRS 990-PF filings | TheGrantScout", 580, small_font, LIGHT_GRAY)

    return img


def create_texas_spotlight():
    """Jan 14: Texas foundation stats"""
    img = Image.new('RGB', (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(img)

    title_font = get_font(52, bold=True)
    big_font = get_font(72, bold=True)
    label_font = get_font(30)
    small_font = get_font(28)

    # Title
    draw_centered_text(draw, "Texas Foundation Giving", 50, title_font, WHITE)

    # Stats in 2x2 grid
    stats = [
        ("12,170", "Foundations"),
        ("$22.7B", "Total Grants (2016-2023)"),
        ("$44,000", "Average Grant"),
        ("55%", "Stay In-State"),
    ]

    positions = [(150, 160), (650, 160), (150, 380), (650, 380)]

    for (value, label), (x, y) in zip(stats, positions):
        draw.text((x, y), value, fill=GOLD, font=big_font)
        draw.text((x, y + 75), label, fill=WHITE, font=label_font)

    # Source
    draw_centered_text(draw, "Source: IRS 990-PF filings | TheGrantScout", 580, small_font, LIGHT_GRAY)

    return img


def create_dc_receiver():
    """Jan 16: DC receives more than it gives"""
    img = Image.new('RGB', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    title_font = get_font(44, bold=True)
    big_font = get_font(84, bold=True)
    label_font = get_font(32)
    small_font = get_font(28)

    # Title
    draw_centered_text(draw, "Washington, DC: Net Receiver of Foundation Funding", 50, title_font, NAVY)

    # Big stat
    draw_centered_text(draw, "+$17.7B", 160, big_font, GOLD)
    draw_centered_text(draw, "More received than given", 260, label_font, NAVY)

    # Explanation
    draw_centered_text(draw, "National nonprofits are headquartered in DC.", 330, get_font(30), NAVY)
    draw_centered_text(draw, "Foundations nationwide fund them.", 375, get_font(30), NAVY)

    # Other receivers
    draw_centered_text(draw, "Other top net receivers:", 450, get_font(26, bold=True), NAVY)
    draw_centered_text(draw, "Massachusetts: +$10.2B", 490, get_font(26), NAVY)

    # Source
    draw_centered_text(draw, "Source: IRS 990-PF filings | TheGrantScout", 560, small_font, LIGHT_GRAY)

    return img


def create_no_website():
    """Jan 21: 43% of foundations have no website"""
    img = Image.new('RGB', (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(img)

    big_font = get_font(130, bold=True)
    label_font = get_font(42)
    sub_font = get_font(36)
    small_font = get_font(28)

    # Big stat
    draw_centered_text(draw, "43%", 140, big_font, GOLD)
    draw_centered_text(draw, "of foundations have no website", 290, label_font, WHITE)

    # Sub stats
    draw_centered_text(draw, "That's 13,000+ foundations invisible to Google.", 400, sub_font, LIGHT_GRAY)
    draw_centered_text(draw, "They're still giving grants. Just quietly.", 450, sub_font, LIGHT_GRAY)

    # Source
    draw_centered_text(draw, "Source: Analysis of 30,000+ foundation filings | TheGrantScout", 580, small_font, LIGHT_GRAY)

    return img


def create_onetime_grants():
    """Jan 23: 50% of relationships are one-time"""
    img = Image.new('RGB', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    title_font = get_font(44, bold=True)
    big_font = get_font(90, bold=True)
    label_font = get_font(34)
    stat_font = get_font(32)
    small_font = get_font(28)

    # Title
    draw_centered_text(draw, "Foundation-Grantee Relationships", 40, title_font, NAVY)

    # Big stat
    draw_centered_text(draw, "50%", 120, big_font, GOLD)
    draw_centered_text(draw, "are one-time grants", 220, label_font, NAVY)

    # Breakdown
    breakdown = [
        ("Single grant:", "49.5%"),
        ("2 grants:", "19.2%"),
        ("3-5 grants:", "24.5%"),
        ("6-10 grants:", "6.1%"),
        ("10+ grants:", "0.8%"),
    ]

    y_start = 310
    for i, (label, pct) in enumerate(breakdown):
        y = y_start + i * 45
        draw.text((350, y), label, fill=NAVY, font=stat_font)
        draw.text((550, y), pct, fill=GOLD if i == 0 else NAVY, font=get_font(22, bold=True))

    # Source
    draw_centered_text(draw, "Source: 1.95M foundation-recipient pairs | TheGrantScout", 580, small_font, LIGHT_GRAY)

    return img


def create_general_support():
    """Jan 28: 20% is general support"""
    img = Image.new('RGB', (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(img)

    big_font = get_font(110, bold=True)
    label_font = get_font(42)
    sub_font = get_font(36)
    small_font = get_font(28)

    # Big stat
    draw_centered_text(draw, "20%", 140, big_font, GOLD)
    draw_centered_text(draw, "of foundation giving is general support", 270, label_font, WHITE)

    # Details
    draw_centered_text(draw, "1.6 million grants  •  $57.6 billion total", 380, sub_font, LIGHT_GRAY)
    draw_centered_text(draw, "Average general support grant: $35,000", 430, sub_font, WHITE)

    # Source
    draw_centered_text(draw, "Source: IRS 990-PF filings | TheGrantScout", 580, small_font, LIGHT_GRAY)

    return img


def create_2020_surge():
    """Jan 30: 2020 foundation giving surge"""
    img = Image.new('RGB', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    title_font = get_font(44, bold=True)
    year_font = get_font(38, bold=True)
    num_font = get_font(60, bold=True)
    small_font = get_font(28)

    # Title
    draw_centered_text(draw, "Foundation Giving: The 2020 Surge", 40, title_font, NAVY)

    # Years data
    years = [
        ("2019", "$54.1B", 54.1),
        ("2020", "$94.6B", 94.6),
        ("2021", "$36.9B", 36.9),
    ]

    bar_max_width = 500
    bar_height = 60
    y_start = 150
    y_spacing = 120

    for i, (year, amount, value) in enumerate(years):
        y = y_start + i * y_spacing
        # Year
        draw.text((100, y + 10), year, fill=NAVY, font=year_font)
        # Bar
        bar_width = int(value / 94.6 * bar_max_width)
        color = GOLD if year == "2020" else NAVY
        draw.rectangle([200, y, 200 + bar_width, y + bar_height], fill=color)
        # Amount
        draw.text((720, y + 5), amount, fill=color, font=num_font)

    # Annotation
    draw_centered_text(draw, "COVID response nearly doubled foundation giving in 2020", 490, get_font(30), NAVY)

    # Source
    draw_centered_text(draw, "Source: IRS 990-PF filings | TheGrantScout", 580, small_font, LIGHT_GRAY)

    return img


def create_week1_recap():
    """Jan 10: Week 1 recap - grant size distribution"""
    img = Image.new('RGB', (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(img)

    title_font = get_font(48, bold=True)
    big_font = get_font(72, bold=True)
    label_font = get_font(32)
    stat_font = get_font(48, bold=True)
    pct_label_font = get_font(28)

    # Title
    draw_centered_text(draw, "Most Foundation Grants Are Small", 50, title_font, WHITE)

    # Main stat
    draw_centered_text(draw, "$3,500", 150, big_font, GOLD)
    draw_centered_text(draw, "Median Grant Size", 240, label_font, WHITE)

    # Supporting stats - two columns
    stats = [
        ("53%", "under $5,000"),
        ("82%", "under $25,000"),
    ]

    x_positions = [320, 880]
    y = 360

    for (pct, label), x in zip(stats, x_positions):
        pct_bbox = draw.textbbox((0, 0), pct, font=stat_font)
        pct_w = pct_bbox[2] - pct_bbox[0]
        draw.text((x - pct_w // 2, y), pct, fill=GOLD, font=stat_font)

        label_bbox = draw.textbbox((0, 0), label, font=pct_label_font)
        label_w = label_bbox[2] - label_bbox[0]
        draw.text((x - label_w // 2, y + 60), label, fill=LIGHT_GRAY, font=pct_label_font)

    # Takeaway
    draw_centered_text(draw, "Smaller asks = more foundations in your pipeline", 510, get_font(28), WHITE)

    # Source
    draw_centered_text(draw, "Source: Analysis of 8.3M foundation grants | TheGrantScout", 570, get_font(24), LIGHT_GRAY)

    return img


def create_company_welcome():
    """Jan 7: Company welcome/intro post"""
    img = Image.new('RGB', (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(img)

    title_font = get_font(64, bold=True)
    tagline_font = get_font(36)
    stat_font = get_font(32, bold=True)
    label_font = get_font(28)

    # Company name
    draw_centered_text(draw, "TheGrantScout", 100, title_font, WHITE)

    # Tagline
    draw_centered_text(draw, "Your mission deserves funding.", 190, tagline_font, GOLD)

    # Key stats
    stats = [
        ("143,000+", "foundations analyzed"),
        ("8M+", "historical grants"),
    ]

    x_positions = [280, 720]
    y = 320

    for (value, label), x in zip(stats, x_positions):
        # Center each stat block
        value_bbox = draw.textbbox((0, 0), value, font=stat_font)
        value_w = value_bbox[2] - value_bbox[0]
        draw.text((x - value_w // 2, y), value, fill=GOLD, font=stat_font)

        label_bbox = draw.textbbox((0, 0), label, font=label_font)
        label_w = label_bbox[2] - label_bbox[0]
        draw.text((x - label_w // 2, y + 50), label, fill=WHITE, font=label_font)

    # Bottom CTA
    draw_centered_text(draw, "We help nonprofits find funders they didn't know existed.", 480, get_font(28), LIGHT_GRAY)

    # Source/branding
    draw_centered_text(draw, "thegrantscout.com", 560, get_font(24), LIGHT_GRAY)

    return img


def main():
    """Generate all stat graphics."""
    print("Creating stat graphics for LinkedIn posts...")
    print()

    graphics = [
        ("2025-01-07_company_welcome.png", create_company_welcome, "Company welcome/intro"),
        ("2025-01-07_median_vs_average.png", create_median_vs_average, "Average $58K vs Median $3,500"),
        ("2025-01-10_company_week1_recap.png", create_week1_recap, "Week 1 recap - grant sizes"),
        ("2025-01-13_top5_states.png", create_top5_states, "Top 5 states for foundations"),
        ("2025-01-14_texas_spotlight.png", create_texas_spotlight, "Texas foundation stats"),
        ("2025-01-16_dc_receiver.png", create_dc_receiver, "DC net receiver"),
        ("2025-01-21_no_website.png", create_no_website, "43% no website"),
        ("2025-01-23_onetime_grants.png", create_onetime_grants, "50% one-time relationships"),
        ("2025-01-28_general_support.png", create_general_support, "20% general support"),
        ("2025-01-30_2020_surge.png", create_2020_surge, "2020 giving surge"),
    ]

    for filename, func, desc in graphics:
        print(f"  Creating {filename}... ({desc})")
        img = func()
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path, "PNG", quality=95)

    print()
    print(f"Done! {len(graphics)} stat graphics created in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
