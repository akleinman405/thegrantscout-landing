"""
TheGrantScout Brand Constants
==============================

Single source of truth for all TGS branding: colors, fonts, sizes, paths.
Imported by md_to_docx.py, md_to_pdf.py, xlsx_utils.py, and any future tools.

Brand Guide: 6. Business/4. website/docs/SPEC_2025-11-30_branding_guide.md
"""

# ============================================================================
# COLORS — Hex strings
# ============================================================================

# Primary
NAVY_HEX = "#1e3a5f"
NAVY_DARK_HEX = "#152b47"
GOLD_HEX = "#d4a853"
GOLD_DARK_HEX = "#b8923d"

# Text
CHARCOAL_HEX = "#2C3E50"
GRAY_HEX = "#6c757d"
WHITE_HEX = "#ffffff"

# Semantic
SUCCESS_HEX = "#28a745"
WARNING_HEX = "#ff8c42"
ERROR_HEX = "#dc3545"

# Backgrounds
BG_LIGHT_GRAY = "#f5f7fa"
BG_LIGHT_GOLD = "#fef9e7"
BG_LIGHT_NAVY = "#f0f4f9"
BG_BORDER_LIGHT = "#e8ebed"

# ============================================================================
# COLORS — RGB tuples (for python-docx RGBColor, openpyxl, etc.)
# ============================================================================

NAVY_RGB = (0x1E, 0x3A, 0x5F)
NAVY_DARK_RGB = (0x15, 0x2B, 0x47)
GOLD_RGB = (0xD4, 0xA8, 0x53)
GOLD_DARK_RGB = (0xB8, 0x92, 0x3D)
CHARCOAL_RGB = (0x2C, 0x3E, 0x50)
GRAY_RGB = (0x6C, 0x75, 0x7D)
WHITE_RGB = (0xFF, 0xFF, 0xFF)
SUCCESS_RGB = (0x28, 0xA7, 0x45)
WARNING_RGB = (0xFF, 0x8C, 0x42)
ERROR_RGB = (0xDC, 0x35, 0x45)

# ============================================================================
# COLORS — Bare hex (no #, for XML attributes like python-docx OxmlElement)
# ============================================================================

NAVY_BARE = "1e3a5f"
NAVY_DARK_BARE = "152b47"
GOLD_BARE = "d4a853"
GOLD_DARK_BARE = "b8923d"
CHARCOAL_BARE = "2c3e50"
GRAY_BARE = "6c757d"
WHITE_BARE = "ffffff"
BG_LIGHT_GRAY_BARE = "f5f7fa"
BG_LIGHT_GOLD_BARE = "fef9e7"
BG_LIGHT_NAVY_BARE = "f0f4f9"
BG_BORDER_LIGHT_BARE = "e8ebed"

# ============================================================================
# FONTS
# ============================================================================

FONT_HEADING = "Calibri Light"
FONT_HEADING_FALLBACK = "'Calibri Light', 'Helvetica Neue', sans-serif"
FONT_BODY = "Calibri"
FONT_BODY_FALLBACK = "'Calibri', 'Helvetica Neue', Arial, sans-serif"
FONT_MONO = "'Courier New', monospace"

# ============================================================================
# TYPOGRAPHY — Sizes in points
# ============================================================================

SIZE_TITLE = 32
SIZE_SUBTITLE = 18
SIZE_H1 = 20
SIZE_H2 = 14
SIZE_H3 = 12
SIZE_BODY = 11
SIZE_TABLE_HEADER = 10
SIZE_TABLE_DATA = 10
SIZE_CAPTION = 9
SIZE_HEADER_FOOTER = 9

# ============================================================================
# SPACING — in points (for Word/PDF)
# ============================================================================

SPACE_BEFORE_H1 = 24
SPACE_AFTER_H1 = 12
SPACE_BEFORE_H2 = 16
SPACE_AFTER_H2 = 8
SPACE_BEFORE_H3 = 12
SPACE_AFTER_H3 = 6
SPACE_AFTER_PARA = 8
SPACE_AROUND_TABLE = 12

# ============================================================================
# EXCEL-SPECIFIC (openpyxl)
# ============================================================================

EXCEL_ZOOM = 140
EXCEL_TABLE_STYLE = "TableStyleMedium2"
EXCEL_FONT = "Calibri"
EXCEL_FONT_SIZE = 10
EXCEL_HEADER_HEX = "2F5496"  # Dark blue for Excel headers (slightly different from Navy)
EXCEL_DATA_START_ROW = 2      # Row 2 (row 1 blank)
EXCEL_DATA_START_COL = 2      # Column B (column A blank)

# ============================================================================
# LOGO PATHS (relative to project root)
# ============================================================================

LOGO_512 = "6. Business/4. website/thegrantscout-landing/public/logo.png"
LOGO_400 = "6. Business/3. sales-marketing/6. LinkedIn/Assets/logo_400x400.png"

# ============================================================================
# COPY
# ============================================================================

TAGLINE = "Your mission deserves funding. We'll help you find it."
WEBSITE = "thegrantscout.com"
BRAND_NAME = "TheGrantScout"
