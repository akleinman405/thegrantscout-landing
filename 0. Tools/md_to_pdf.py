#!/usr/bin/env python3
"""
TheGrantScout Markdown → PDF Converter
========================================

Converts markdown reports to professionally styled PDFs via HTML + WeasyPrint.

Usage:
    python3 "0. Tools/md_to_pdf.py" --input report.md --output report.pdf
    python3 "0. Tools/md_to_pdf.py" --input report.md  # output = same name, .pdf extension

Pipeline: .md → markdown library → HTML → WeasyPrint → PDF
Brand: Navy (#1e3a5f) + Gold (#d4a853) + Charcoal (#2C3E50)
CSS extracted from VetsBoats report (proven, production-tested styling).

Dependencies:
    pip3 install markdown weasyprint
    brew install pango  (system dependency for WeasyPrint)

Formatting rules (apply to the SOURCE MARKDOWN, not this script):
    - Blank line required before tables/lists after **bold:** labels
    - Blank line required between consecutive **bold:** metadata lines
    - No ``` code blocks in client reports (use tables or bullet lists)
    - PAGE_BREAK markers: <!-- PAGE_BREAK -->
    - No em dashes in prose (use commas, periods, colons)
    - URLs as markdown links: [text](url)
    See memory/pdf_formatting_rules.md for full checklist.
"""

import argparse
import os
import re
import sys

# Allow importing branding.py from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import branding

import markdown
from weasyprint import HTML


def get_css():
    """Return the TGS-branded CSS for PDF rendering.

    Extracted from the VetsBoats report HTML (production-tested).
    All color/font values reference branding.py constants.
    """
    return f"""
@page {{
    size: letter;
    margin: 0.75in 1in;
    @top-right {{
        content: "{branding.BRAND_NAME}";
        font-family: {branding.FONT_BODY_FALLBACK};
        font-size: 10pt;
        color: {branding.NAVY_HEX};
        font-weight: bold;
    }}
    @bottom-center {{
        content: "{branding.WEBSITE}  |  {branding.TAGLINE}";
        font-family: {branding.FONT_BODY_FALLBACK};
        font-size: 8pt;
        color: {branding.GRAY_HEX};
    }}
    @bottom-right {{
        content: counter(page);
        font-family: {branding.FONT_BODY_FALLBACK};
        font-size: 8pt;
        color: {branding.GRAY_HEX};
    }}
}}

body {{
    font-family: {branding.FONT_BODY_FALLBACK};
    font-size: {branding.SIZE_BODY}pt;
    color: {branding.CHARCOAL_HEX.lower()};
    line-height: 1.5;
}}

h1 {{
    font-family: {branding.FONT_HEADING_FALLBACK};
    font-weight: 300;
    color: {branding.NAVY_HEX};
    font-size: 28pt;
    margin-top: 0;
    margin-bottom: 4pt;
    page-break-after: avoid;
}}

h1 + h1 {{
    font-size: 16pt;
    color: {branding.GRAY_HEX};
    font-weight: 300;
    margin-bottom: 12pt;
}}

h2 {{
    font-family: {branding.FONT_HEADING_FALLBACK};
    font-size: 18pt;
    font-weight: bold;
    color: {branding.NAVY_HEX};
    margin-top: 24pt;
    margin-bottom: 10pt;
    border-bottom: 2px solid {branding.GOLD_HEX};
    padding-bottom: 4pt;
    page-break-after: avoid;
}}

h3 {{
    font-family: {branding.FONT_HEADING_FALLBACK};
    font-size: {branding.SIZE_H2}pt;
    font-weight: bold;
    color: {branding.NAVY_DARK_HEX};
    margin-top: 16pt;
    margin-bottom: 8pt;
    page-break-after: avoid;
}}

h4 {{
    font-family: {branding.FONT_HEADING_FALLBACK};
    font-size: {branding.SIZE_H3}pt;
    font-weight: bold;
    color: {branding.CHARCOAL_HEX.lower()};
    margin-top: 12pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
}}

p {{
    margin-bottom: 8pt;
}}

a {{
    color: {branding.NAVY_HEX};
    text-decoration: underline;
    font-weight: bold;
}}

a:hover {{
    color: {branding.GOLD_HEX};
}}

/* TOC styling */
ol {{
    padding-left: 20pt;
}}

ol li {{
    margin-bottom: 4pt;
}}

ol li a {{
    color: {branding.NAVY_HEX};
    text-decoration: none;
    font-weight: normal;
}}

/* Tables */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: {branding.SIZE_TABLE_DATA}pt;
    page-break-inside: auto;
}}

thead th, th {{
    background-color: {branding.NAVY_HEX};
    color: white;
    font-weight: bold;
    padding: 8pt 10pt;
    text-align: left;
    border-bottom: 3px solid {branding.GOLD_HEX};
}}

td {{
    padding: 6pt 10pt;
    border-bottom: 1px solid {branding.BG_BORDER_LIGHT};
    vertical-align: top;
    overflow-wrap: break-word;
    word-break: break-word;
}}

tr:nth-child(even) td {{
    background-color: {branding.BG_LIGHT_GRAY};
}}

tr:nth-child(odd) td {{
    background-color: {branding.WHITE_HEX};
}}

/* Blockquotes as callout boxes */
blockquote {{
    background-color: {branding.BG_LIGHT_GOLD};
    border-left: 4px solid {branding.GOLD_HEX};
    padding: 12pt 16pt;
    margin: 12pt 0;
    font-weight: bold;
    color: {branding.NAVY_HEX};
}}

blockquote p {{
    margin: 0;
}}

/* Horizontal rules */
hr {{
    border: none;
    border-top: 1px solid {branding.GOLD_HEX};
    margin: 16pt 0;
}}

/* Code blocks */
code, pre {{
    font-family: {branding.FONT_MONO};
    font-size: 9pt;
    background-color: {branding.BG_LIGHT_GRAY};
    border: 1px solid {branding.BG_BORDER_LIGHT};
    border-radius: 3pt;
}}

pre {{
    padding: 12pt;
    margin: 10pt 0;
    white-space: pre-wrap;
    page-break-inside: avoid;
}}

code {{
    padding: 1pt 4pt;
}}

/* Bullet lists */
ul {{
    padding-left: 20pt;
    margin-bottom: 8pt;
}}

ul li {{
    margin-bottom: 4pt;
}}

/* Page breaks */
.page-break {{
    page-break-after: always;
}}

/* Bold metadata lines */
strong {{
    color: {branding.NAVY_HEX};
}}

/* Keep headings with following content */
h2, h3, h4 {{
    page-break-after: avoid;
}}

/* Prevent orphan rows */
tr {{
    page-break-inside: avoid;
}}
"""


def preprocess_markdown(md_text):
    """Apply formatting fixes before markdown conversion.

    Handles:
    - <!-- PAGE_BREAK --> → <div class="page-break"></div>
    """
    # Replace page break markers
    md_text = md_text.replace(
        '<!-- PAGE_BREAK -->',
        '<div class="page-break"></div>'
    )
    return md_text


def convert_markdown_to_pdf(md_path, pdf_path):
    """Convert markdown file to branded PDF."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Preprocess
    md_text = preprocess_markdown(md_text)

    # Convert markdown to HTML
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'toc', 'attr_list', 'fenced_code'],
        extension_configs={
            'toc': {'permalink': False}
        }
    )

    # Wrap in full HTML document with branding CSS
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
{get_css()}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""

    # Also write the intermediate HTML (useful for debugging)
    html_path = os.path.splitext(pdf_path)[0] + '.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_doc)
    print(f"Created: {html_path} (intermediate)")

    # Generate PDF
    HTML(string=html_doc).write_pdf(pdf_path)
    print(f"Created: {pdf_path}")


def main():
    parser = argparse.ArgumentParser(
        description='TheGrantScout Markdown to PDF Converter'
    )
    parser.add_argument('--input', '-i', required=True, help='Input markdown file')
    parser.add_argument('--output', '-o', help='Output .pdf file (default: same name, .pdf extension)')
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    if args.output:
        pdf_path = args.output
    else:
        pdf_path = os.path.splitext(args.input)[0] + '.pdf'

    output_dir = os.path.dirname(pdf_path)
    if output_dir and not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    convert_markdown_to_pdf(args.input, pdf_path)


if __name__ == '__main__':
    main()
