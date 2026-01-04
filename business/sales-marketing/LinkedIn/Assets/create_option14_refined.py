#!/usr/bin/env python3
"""
Refined versions of Option 14 - Minimal Wordmark for TheGrantScout
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Brand colors
NAVY = (30, 58, 95)       # #1e3a5f
GOLD = (212, 168, 83)     # #d4a853
WHITE = (255, 255, 255)
LIGHT_GRAY = (245, 245, 245)
OFF_WHITE = (250, 248, 245)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_font(size, bold=False):
    """Try to get a good font."""
    if bold:
        paths = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    else:
        paths = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()


def create_14a_refined_centered(size=400):
    """
    14A: Refined centered wordmark
    - Better vertical centering
    - Slightly larger text
    - Clean white background
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    font = get_font(48, bold=True)

    the_text = "The"
    rest_text = "GrantScout"

    # Measure
    the_bbox = draw.textbbox((0, 0), the_text, font=font)
    the_w = the_bbox[2] - the_bbox[0]

    rest_bbox = draw.textbbox((0, 0), rest_text, font=font)
    rest_w = rest_bbox[2] - rest_bbox[0]

    total_w = the_w + rest_w
    h = the_bbox[3] - the_bbox[1]

    start_x = (size - total_w) // 2
    y = (size - h) // 2 - 10  # Slight upward adjustment for visual center

    draw.text((start_x, y), the_text, fill=GOLD, font=font)
    draw.text((start_x + the_w, y), rest_text, fill=NAVY, font=font)

    return img


def create_14b_with_underline(size=400):
    """
    14B: Wordmark with subtle gold underline accent
    - Adds visual interest
    - Still minimal
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    font = get_font(46, bold=True)

    the_text = "The"
    rest_text = "GrantScout"

    the_bbox = draw.textbbox((0, 0), the_text, font=font)
    the_w = the_bbox[2] - the_bbox[0]

    rest_bbox = draw.textbbox((0, 0), rest_text, font=font)
    rest_w = rest_bbox[2] - rest_bbox[0]

    total_w = the_w + rest_w
    h = the_bbox[3] - the_bbox[1]

    start_x = (size - total_w) // 2
    y = (size - h) // 2 - 15

    draw.text((start_x, y), the_text, fill=GOLD, font=font)
    draw.text((start_x + the_w, y), rest_text, fill=NAVY, font=font)

    # Subtle underline
    underline_y = y + h + 12
    underline_thickness = 4
    draw.rectangle(
        [start_x, underline_y, start_x + total_w, underline_y + underline_thickness],
        fill=GOLD
    )

    return img


def create_14c_navy_background(size=400):
    """
    14C: Reversed - on navy background
    - For dark mode / variety
    """
    img = Image.new('RGB', (size, size), NAVY)
    draw = ImageDraw.Draw(img)

    font = get_font(46, bold=True)

    the_text = "The"
    rest_text = "GrantScout"

    the_bbox = draw.textbbox((0, 0), the_text, font=font)
    the_w = the_bbox[2] - the_bbox[0]

    rest_bbox = draw.textbbox((0, 0), rest_text, font=font)
    rest_w = rest_bbox[2] - rest_bbox[0]

    total_w = the_w + rest_w
    h = the_bbox[3] - the_bbox[1]

    start_x = (size - total_w) // 2
    y = (size - h) // 2 - 10

    draw.text((start_x, y), the_text, fill=GOLD, font=font)
    draw.text((start_x + the_w, y), rest_text, fill=WHITE, font=font)

    return img


def create_14d_stacked_refined(size=400):
    """
    14D: Stacked version - "The" above "GrantScout"
    - Different layout option
    - More square-friendly
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    font_the = get_font(32, bold=False)
    font_main = get_font(52, bold=True)

    the_text = "The"
    main_text = "GrantScout"

    # Measure
    the_bbox = draw.textbbox((0, 0), the_text, font=font_the)
    the_w = the_bbox[2] - the_bbox[0]
    the_h = the_bbox[3] - the_bbox[1]

    main_bbox = draw.textbbox((0, 0), main_text, font=font_main)
    main_w = main_bbox[2] - main_bbox[0]
    main_h = main_bbox[3] - main_bbox[1]

    total_h = the_h + main_h + 5  # 5px gap
    start_y = (size - total_h) // 2 - 10

    # Center both horizontally
    the_x = (size - the_w) // 2
    main_x = (size - main_w) // 2

    draw.text((the_x, start_y), the_text, fill=GOLD, font=font_the)
    draw.text((main_x, start_y + the_h + 5), main_text, fill=NAVY, font=font_main)

    return img


def create_14e_with_dot(size=400):
    """
    14E: Wordmark with gold dot accent
    - Subtle brand element
    - Can be used as standalone icon
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    font = get_font(44, bold=True)

    full_text = "TheGrantScout"

    bbox = draw.textbbox((0, 0), full_text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    start_x = (size - w) // 2
    y = (size - h) // 2

    # Gold dot before text
    dot_r = 8
    dot_x = start_x - dot_r * 3
    dot_y = y + h // 2
    draw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=GOLD
    )

    # All navy text
    draw.text((start_x, y), full_text, fill=NAVY, font=font)

    return img


def create_14f_split_color_clean(size=400):
    """
    14F: Clean split - "The" gold, "Grant" navy, "Scout" navy
    - Cleaner execution of the original
    - Better spacing
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    font = get_font(50, bold=True)

    the_text = "The"
    grant_text = "Grant"
    scout_text = "Scout"

    # Measure each part
    the_bbox = draw.textbbox((0, 0), the_text, font=font)
    the_w = the_bbox[2] - the_bbox[0]

    grant_bbox = draw.textbbox((0, 0), grant_text, font=font)
    grant_w = grant_bbox[2] - grant_bbox[0]

    scout_bbox = draw.textbbox((0, 0), scout_text, font=font)
    scout_w = scout_bbox[2] - scout_bbox[0]

    h = the_bbox[3] - the_bbox[1]
    total_w = the_w + grant_w + scout_w

    start_x = (size - total_w) // 2
    y = (size - h) // 2 - 10

    # Draw with precise positioning
    draw.text((start_x, y), the_text, fill=GOLD, font=font)
    draw.text((start_x + the_w, y), grant_text, fill=NAVY, font=font)
    draw.text((start_x + the_w + grant_w, y), scout_text, fill=NAVY, font=font)

    return img


def create_14g_boxed(size=400):
    """
    14G: Wordmark in a subtle rounded rectangle
    - More defined/contained look
    - Works well as profile picture
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    # Draw subtle border/box
    margin = size * 0.08
    box_color = (240, 240, 240)  # Very light gray
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=20,
        fill=None,
        outline=NAVY,
        width=3
    )

    font = get_font(42, bold=True)

    the_text = "The"
    rest_text = "GrantScout"

    the_bbox = draw.textbbox((0, 0), the_text, font=font)
    the_w = the_bbox[2] - the_bbox[0]

    rest_bbox = draw.textbbox((0, 0), rest_text, font=font)
    rest_w = rest_bbox[2] - rest_bbox[0]

    total_w = the_w + rest_w
    h = the_bbox[3] - the_bbox[1]

    start_x = (size - total_w) // 2
    y = (size - h) // 2 - 10

    draw.text((start_x, y), the_text, fill=GOLD, font=font)
    draw.text((start_x + the_w, y), rest_text, fill=NAVY, font=font)

    return img


def create_14h_larger_bolder(size=400):
    """
    14H: Larger, bolder text
    - Maximum impact
    - Fills the space better
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    font = get_font(56, bold=True)

    the_text = "The"
    rest_text = "GrantScout"

    the_bbox = draw.textbbox((0, 0), the_text, font=font)
    the_w = the_bbox[2] - the_bbox[0]

    rest_bbox = draw.textbbox((0, 0), rest_text, font=font)
    rest_w = rest_bbox[2] - rest_bbox[0]

    total_w = the_w + rest_w
    h = the_bbox[3] - the_bbox[1]

    start_x = (size - total_w) // 2
    y = (size - h) // 2 - 10

    draw.text((start_x, y), the_text, fill=GOLD, font=font)
    draw.text((start_x + the_w, y), rest_text, fill=NAVY, font=font)

    return img


def main():
    """Generate refined Option 14 variations."""
    print("Creating refined Option 14 variations...")
    print()

    options = [
        ("option_14a_centered.png", create_14a_refined_centered, "Clean centered"),
        ("option_14b_underline.png", create_14b_with_underline, "With gold underline"),
        ("option_14c_navy_bg.png", create_14c_navy_background, "Navy background"),
        ("option_14d_stacked.png", create_14d_stacked_refined, "Stacked layout"),
        ("option_14e_dot.png", create_14e_with_dot, "With gold dot accent"),
        ("option_14f_clean.png", create_14f_split_color_clean, "Clean split color"),
        ("option_14g_boxed.png", create_14g_boxed, "In rounded box"),
        ("option_14h_bold.png", create_14h_larger_bolder, "Larger & bolder"),
    ]

    for filename, func, desc in options:
        print(f"  Creating {filename}... ({desc})")
        img = func(400)
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path, "PNG")

    print()
    print(f"Done! {len(options)} refined versions created.")


if __name__ == "__main__":
    main()
