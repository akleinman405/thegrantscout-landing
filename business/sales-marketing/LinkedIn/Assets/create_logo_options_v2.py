#!/usr/bin/env python3
"""
Generate more logo options for TheGrantScout (one word, capital T, G, S)
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

# Brand colors
NAVY = (30, 58, 95)       # #1e3a5f
GOLD = (212, 168, 83)     # #d4a853
WHITE = (255, 255, 255)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_font(size, bold=False):
    """Try to get a good font."""
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()


def create_option_9_tgs_monogram(size=400):
    """
    Option 9: TGS Monogram
    Clean three-letter monogram that's memorable.
    """
    img = Image.new('RGB', (size, size), NAVY)
    draw = ImageDraw.Draw(img)

    font = get_font(120, bold=True)
    text = "TGS"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((size - w) // 2, (size - h) // 2 - 20), text, fill=GOLD, font=font)

    return img


def create_option_10_beacon(size=400):
    """
    Option 10: Beacon/Lighthouse concept
    "Scout" finds things - a beacon guides to opportunities.
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    center_x = size // 2

    # Simple beacon shape - triangle with rays
    beacon_top = size * 0.15
    beacon_bottom = size * 0.55
    beacon_width = size * 0.12

    # Main beacon triangle
    beacon_points = [
        (center_x, beacon_top),
        (center_x - beacon_width, beacon_bottom),
        (center_x + beacon_width, beacon_bottom),
    ]
    draw.polygon(beacon_points, fill=NAVY)

    # Light rays emanating from top
    ray_length = size * 0.15
    ray_width = 4
    for angle in [-40, -20, 0, 20, 40]:
        rad = math.radians(angle - 90)
        end_x = center_x + ray_length * math.cos(rad)
        end_y = beacon_top - 10 + ray_length * math.sin(rad)
        draw.line([(center_x, beacon_top - 5), (end_x, end_y)], fill=GOLD, width=ray_width)

    # Text below
    font = get_font(32, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.70), text, fill=NAVY, font=font)

    return img


def create_option_11_scout_binoculars(size=400):
    """
    Option 11: Abstract Binoculars
    Scout = looking/searching, binoculars = finding opportunities.
    """
    img = Image.new('RGB', (size, size), NAVY)
    draw = ImageDraw.Draw(img)

    center_x = size // 2
    center_y = size * 0.40

    # Two circles for binocular lenses
    lens_r = size * 0.13
    spacing = size * 0.18
    thickness = int(size * 0.035)

    # Left lens
    draw.ellipse(
        [center_x - spacing - lens_r, center_y - lens_r,
         center_x - spacing + lens_r, center_y + lens_r],
        outline=GOLD, width=thickness
    )

    # Right lens
    draw.ellipse(
        [center_x + spacing - lens_r, center_y - lens_r,
         center_x + spacing + lens_r, center_y + lens_r],
        outline=GOLD, width=thickness
    )

    # Bridge connecting them
    bridge_y = center_y
    draw.line(
        [(center_x - spacing + lens_r, bridge_y), (center_x + spacing - lens_r, bridge_y)],
        fill=GOLD, width=thickness
    )

    # Text below
    font = get_font(30, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.70), text, fill=WHITE, font=font)

    return img


def create_option_12_checkmark_find(size=400):
    """
    Option 12: Checkmark/Found concept
    Finding = success = checkmark. Simple and positive.
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    center_x = size // 2
    center_y = size * 0.38

    # Draw a bold checkmark
    check_width = int(size * 0.06)

    # Checkmark points
    start = (center_x - size * 0.18, center_y)
    mid = (center_x - size * 0.05, center_y + size * 0.15)
    end = (center_x + size * 0.22, center_y - size * 0.15)

    draw.line([start, mid], fill=GOLD, width=check_width)
    draw.line([mid, end], fill=NAVY, width=check_width)

    # Text below
    font = get_font(34, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.70), text, fill=NAVY, font=font)

    return img


def create_option_13_spotlight(size=400):
    """
    Option 13: Spotlight/Focus
    Shining light on hidden opportunities.
    """
    img = Image.new('RGB', (size, size), NAVY)
    draw = ImageDraw.Draw(img)

    center_x = size // 2

    # Spotlight cone
    cone_top_width = size * 0.08
    cone_bottom_width = size * 0.35
    cone_top_y = size * 0.18
    cone_bottom_y = size * 0.55

    cone_points = [
        (center_x - cone_top_width, cone_top_y),
        (center_x + cone_top_width, cone_top_y),
        (center_x + cone_bottom_width, cone_bottom_y),
        (center_x - cone_bottom_width, cone_bottom_y),
    ]
    draw.polygon(cone_points, fill=GOLD)

    # Light source circle at top
    source_r = size * 0.06
    draw.ellipse(
        [center_x - source_r, cone_top_y - source_r * 0.5,
         center_x + source_r, cone_top_y + source_r * 1.5],
        fill=WHITE
    )

    # Text below
    font = get_font(30, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.72), text, fill=WHITE, font=font)

    return img


def create_option_14_minimal_wordmark(size=400):
    """
    Option 14: Ultra-minimal wordmark
    Just "TheGrantScout" with subtle gold accent on "The".
    Clean, professional, timeless.
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    font = get_font(44, bold=True)

    # Measure full text
    full_text = "TheGrantScout"
    the_text = "The"
    rest_text = "GrantScout"

    the_bbox = draw.textbbox((0, 0), the_text, font=font)
    the_w = the_bbox[2] - the_bbox[0]

    full_bbox = draw.textbbox((0, 0), full_text, font=font)
    full_w = full_bbox[2] - full_bbox[0]
    full_h = full_bbox[3] - full_bbox[1]

    start_x = (size - full_w) // 2
    y = (size - full_h) // 2

    # "The" in gold
    draw.text((start_x, y), the_text, fill=GOLD, font=font)
    # "GrantScout" in navy
    draw.text((start_x + the_w, y), rest_text, fill=NAVY, font=font)

    return img


def create_option_15_dollar_radar(size=400):
    """
    Option 15: Dollar sign with radar/search rings
    Finding money/grants concept.
    """
    img = Image.new('RGB', (size, size), NAVY)
    draw = ImageDraw.Draw(img)

    center_x = size // 2
    center_y = size * 0.42

    # Radar rings
    for i, r in enumerate([size * 0.28, size * 0.21, size * 0.14]):
        alpha = 255 - i * 60
        draw.ellipse(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            outline=GOLD, width=2
        )

    # Dollar sign in center
    font = get_font(80, bold=True)
    text = "$"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((center_x - w // 2, center_y - h // 2 - 10), text, fill=WHITE, font=font)

    # Text below
    font_small = get_font(28, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font_small)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.78), text, fill=WHITE, font=font_small)

    return img


def create_option_16_arrow_up(size=400):
    """
    Option 16: Upward arrow
    Growth, success, finding better opportunities.
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    center_x = size // 2

    # Arrow pointing up
    arrow_width = size * 0.25
    arrow_height = size * 0.35
    arrow_top = size * 0.12
    stem_width = size * 0.10

    # Arrow head
    arrow_points = [
        (center_x, arrow_top),
        (center_x - arrow_width, arrow_top + arrow_height * 0.5),
        (center_x - stem_width, arrow_top + arrow_height * 0.5),
        (center_x - stem_width, arrow_top + arrow_height),
        (center_x + stem_width, arrow_top + arrow_height),
        (center_x + stem_width, arrow_top + arrow_height * 0.5),
        (center_x + arrow_width, arrow_top + arrow_height * 0.5),
    ]
    draw.polygon(arrow_points, fill=NAVY)

    # Gold accent - small bar at bottom of arrow
    bar_y = arrow_top + arrow_height - size * 0.03
    draw.rectangle(
        [center_x - stem_width, bar_y, center_x + stem_width, arrow_top + arrow_height],
        fill=GOLD
    )

    # Text below
    font = get_font(34, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.68), text, fill=NAVY, font=font)

    return img


def main():
    """Generate more logo options."""
    print("Creating additional logo options...")
    print()

    options = [
        ("option_09_tgs_monogram.png", create_option_9_tgs_monogram, "TGS monogram on navy"),
        ("option_10_beacon.png", create_option_10_beacon, "Beacon/lighthouse concept"),
        ("option_11_binoculars.png", create_option_11_scout_binoculars, "Scout binoculars"),
        ("option_12_checkmark.png", create_option_12_checkmark_find, "Checkmark/found"),
        ("option_13_spotlight.png", create_option_13_spotlight, "Spotlight concept"),
        ("option_14_minimal.png", create_option_14_minimal_wordmark, "Ultra-minimal wordmark"),
        ("option_15_dollar_radar.png", create_option_15_dollar_radar, "Dollar with radar rings"),
        ("option_16_arrow.png", create_option_16_arrow_up, "Upward arrow"),
    ]

    for filename, func, desc in options:
        print(f"  Creating {filename}... ({desc})")
        img = func(400)
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path, "PNG")

    print()
    print(f"Done! {len(options)} additional options created.")


if __name__ == "__main__":
    main()
