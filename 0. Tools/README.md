# 0. Tools

Reusable converter scripts for document generation. All scripts share branding constants from `branding.py`.

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `branding.py` | Shared brand constants (colors, fonts, sizes) | `import branding` |
| `md_to_docx.py` | Markdown → branded Word doc | `python3 "0. Tools/md_to_docx.py" -i input.md -o output.docx` |
| `md_to_pdf.py` | Markdown → branded PDF | `python3 "0. Tools/md_to_pdf.py" -i input.md -o output.pdf` |
| `xlsx_utils.py` | Excel create/edit helpers | `from xlsx_utils import create_workbook, edit_workbook` |

## Dependencies

```bash
pip3 install python-docx markdown weasyprint openpyxl
brew install pango  # system dependency for WeasyPrint
```

## Branding

All brand colors, fonts, and sizes are defined in `branding.py`. This is the single source of truth. Other scripts import from it instead of hardcoding values.

Full branding guide: `6. Business/4. website/docs/SPEC_2025-11-30_branding_guide.md`
