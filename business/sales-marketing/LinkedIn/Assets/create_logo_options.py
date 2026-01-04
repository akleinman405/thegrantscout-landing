#!/usr/bin/env python3
"""
Generate multiple logo options for TheGrantScout based on research.

Research findings:
- 72% of SaaS logos use icon + text combination
- 93% use sans-serif fonts
- 51% monochromatic, 18% blue
- 42% use lowercase text
- Simple, credible designs work best for B2B
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

# Brand colors
NAVY = (30, 58, 95)       # #1e3a5f
GOLD = (212, 168, 83)     # #d4a853
WHITE = (255, 255, 255)
LIGHT_GOLD = (232, 198, 123)
DARK_NAVY = (20, 40, 70)

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


def create_option_1_wordmark(size=400):
    """
    Option 1: Clean Wordmark
    Just the text "TheGrantScout" in clean typography.
    Professional, simple, builds name recognition.
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    # Two-line approach for square format
    font_the = get_font(42)
    font_main = get_font(52, bold=True)

    # "the" in gold, smaller
    draw.text((size * 0.15, size * 0.35), "the", fill=GOLD, font=font_the)

    # "GrantScout" in navy, bold
    draw.text((size * 0.15, size * 0.45), "GrantScout", fill=NAVY, font=font_main)

    return img


def create_option_2_wordmark_stacked(size=400):
    """
    Option 2: Stacked Wordmark
    "GRANT" over "SCOUT" - bold, modern, all caps.
    """
    img = Image.new('RGB', (size, size), NAVY)
    draw = ImageDraw.Draw(img)

    font = get_font(72, bold=True)

    # "GRANT" in white
    bbox = draw.textbbox((0, 0), "GRANT", font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.30), "GRANT", fill=WHITE, font=font)

    # "SCOUT" in gold
    bbox = draw.textbbox((0, 0), "SCOUT", font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.48), "SCOUT", fill=GOLD, font=font)

    return img


def create_option_3_compass_icon(size=400):
    """
    Option 3: Compass/Direction Icon + Text
    A simple compass or direction indicator - represents "scouting" and finding direction.
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    center_x = size // 2
    center_y = size * 0.38
    radius = size * 0.22

    # Outer circle
    draw.ellipse(
        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
        outline=NAVY, width=int(size * 0.02)
    )

    # Compass needle (north pointer) - gold triangle pointing up
    needle_height = radius * 0.7
    needle_width = radius * 0.25
    north_points = [
        (center_x, center_y - needle_height),  # top
        (center_x - needle_width, center_y),   # bottom left
        (center_x + needle_width, center_y),   # bottom right
    ]
    draw.polygon(north_points, fill=GOLD)

    # South pointer - navy triangle pointing down
    south_points = [
        (center_x, center_y + needle_height),  # bottom
        (center_x - needle_width, center_y),   # top left
        (center_x + needle_width, center_y),   # top right
    ]
    draw.polygon(south_points, fill=NAVY)

    # Center dot
    dot_r = size * 0.025
    draw.ellipse(
        [center_x - dot_r, center_y - dot_r, center_x + dot_r, center_y + dot_r],
        fill=NAVY
    )

    # Text below
    font = get_font(36, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.72), text, fill=NAVY, font=font)

    return img


def create_option_4_target_icon(size=400):
    """
    Option 4: Target/Bullseye Icon
    Represents precision, finding the right match.
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    center_x = size // 2
    center_y = size * 0.40

    # Three concentric circles
    for i, (r, color) in enumerate([
        (size * 0.24, NAVY),
        (size * 0.16, WHITE),
        (size * 0.08, GOLD),
    ]):
        draw.ellipse(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            fill=color, outline=NAVY if i == 1 else None, width=3
        )

    # Text below
    font = get_font(36, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.75), text, fill=NAVY, font=font)

    return img


def create_option_5_letter_g(size=400):
    """
    Option 5: Stylized "G" Lettermark
    Modern lettermark that can stand alone.
    """
    img = Image.new('RGB', (size, size), NAVY)
    draw = ImageDraw.Draw(img)

    center = size // 2
    outer_r = size * 0.32
    inner_r = size * 0.20
    thickness = outer_r - inner_r

    # Draw G shape - outer arc (about 300 degrees)
    # Using ellipse and masking with rectangles
    draw.ellipse(
        [center - outer_r, center - outer_r, center + outer_r, center + outer_r],
        fill=GOLD
    )
    draw.ellipse(
        [center - inner_r, center - inner_r, center + inner_r, center + inner_r],
        fill=NAVY
    )

    # Cut out the opening of the G (right side)
    gap_width = size * 0.15
    draw.rectangle(
        [center, center - gap_width, center + outer_r + 10, center + gap_width],
        fill=NAVY
    )

    # Add the horizontal bar of the G
    bar_height = size * 0.06
    draw.rectangle(
        [center - size * 0.05, center - bar_height // 2, center + outer_r * 0.6, center + bar_height // 2],
        fill=GOLD
    )

    return img


def create_option_6_abstract_path(size=400):
    """
    Option 6: Abstract Path/Arrow
    Represents finding a path, direction, discovery.
    Modern and minimal.
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    # Draw an abstract curved arrow/path
    center_x = size // 2
    center_y = size * 0.42

    # Main curved line (like a swoosh going up-right)
    line_width = int(size * 0.05)

    # Draw a thick curved line using multiple line segments
    points = []
    for i in range(50):
        t = i / 49
        x = center_x - size * 0.25 + t * size * 0.5
        # Curve up then slightly down
        y = center_y + size * 0.1 - math.sin(t * math.pi) * size * 0.2
        points.append((x, y))

    # Draw the path
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=NAVY, width=line_width)

    # Arrow head at the end
    end_x, end_y = points[-1]
    arrow_size = size * 0.08
    arrow_points = [
        (end_x + arrow_size, end_y),
        (end_x - arrow_size * 0.3, end_y - arrow_size * 0.6),
        (end_x - arrow_size * 0.3, end_y + arrow_size * 0.6),
    ]
    draw.polygon(arrow_points, fill=GOLD)

    # Text below
    font = get_font(32, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.72), text, fill=NAVY, font=font)

    return img


def create_option_7_magnifier_modern(size=400):
    """
    Option 7: Modernized Magnifying Glass
    Cleaner, more abstract version of the current concept.
    """
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    # Magnifying glass - more stylized
    glass_center_x = size * 0.42
    glass_center_y = size * 0.38
    glass_radius = size * 0.18
    handle_width = int(size * 0.055)

    # Glass circle - just outline, thicker
    draw.ellipse(
        [glass_center_x - glass_radius, glass_center_y - glass_radius,
         glass_center_x + glass_radius, glass_center_y + glass_radius],
        outline=NAVY, width=handle_width
    )

    # Handle - angled
    handle_start_x = glass_center_x + glass_radius * 0.7
    handle_start_y = glass_center_y + glass_radius * 0.7
    handle_end_x = glass_center_x + glass_radius * 1.6
    handle_end_y = glass_center_y + glass_radius * 1.6

    draw.line(
        [(handle_start_x, handle_start_y), (handle_end_x, handle_end_y)],
        fill=GOLD, width=handle_width
    )

    # Rounded end
    draw.ellipse(
        [handle_end_x - handle_width//2, handle_end_y - handle_width//2,
         handle_end_x + handle_width//2, handle_end_y + handle_width//2],
        fill=GOLD
    )

    # Text to the right and below
    font = get_font(34, bold=True)
    text = "TheGrantScout"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((size - w) // 2, size * 0.78), text, fill=NAVY, font=font)

    return img


def create_option_8_lowercase_modern(size=400):
    """
    Option 8: Lowercase Modern Wordmark
    "thegrantscout" all lowercase, clean and modern.
    42% of SaaS logos use lowercase.
    """
    img = Image.new('RGB', (size, size), NAVY)
    draw = ImageDraw.Draw(img)

    # All lowercase, modern feel
    font = get_font(38, bold=True)

    # "the" in gold
    the_text = "the"
    bbox = draw.textbbox((0, 0), the_text, font=font)
    the_width = bbox[2] - bbox[0]

    # "grantscout" in white
    main_text = "grantscout"
    bbox = draw.textbbox((0, 0), main_text, font=font)
    main_width = bbox[2] - bbox[0]

    total_width = the_width + main_width
    start_x = (size - total_width) // 2

    draw.text((start_x, size * 0.44), the_text, fill=GOLD, font=font)
    draw.text((start_x + the_width, size * 0.44), main_text, fill=WHITE, font=font)

    return img


def main():
    """Generate all logo options."""
    print("Creating logo options based on research...")
    print()

    options = [
        ("option_1_wordmark.png", create_option_1_wordmark, "Clean wordmark on white"),
        ("option_2_stacked.png", create_option_2_wordmark_stacked, "GRANT/SCOUT stacked on navy"),
        ("option_3_compass.png", create_option_3_compass_icon, "Compass icon + wordmark"),
        ("option_4_target.png", create_option_4_target_icon, "Target/bullseye icon + wordmark"),
        ("option_5_letter_g.png", create_option_5_letter_g, "Stylized G lettermark"),
        ("option_6_path.png", create_option_6_abstract_path, "Abstract path/arrow"),
        ("option_7_magnifier.png", create_option_7_magnifier_modern, "Modern magnifying glass"),
        ("option_8_lowercase.png", create_option_8_lowercase_modern, "Lowercase wordmark on navy"),
    ]

    for filename, func, desc in options:
        print(f"  Creating {filename}... ({desc})")
        img = func(400)
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path, "PNG")

    print()
    print(f"Done! {len(options)} options created in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
