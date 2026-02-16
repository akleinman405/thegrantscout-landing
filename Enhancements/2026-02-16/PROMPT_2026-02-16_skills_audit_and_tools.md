# PROMPT: Skills Audit, Tools Consolidation & CLAUDE.md Update

**Date:** 2026-02-16
**Agent:** Claude Code CLI
**Type:** Audit + reorganization

---

## Context

Over many sessions we've built various scripts for generating Word docs, PDFs, HTML reports, and Excel files. These are scattered across Enhancement folders with inconsistent branding and formatting. Every new session rebuilds these from scratch, wasting tokens and producing inconsistent output. We need to consolidate the best versions into a single tools location and update CLAUDE.md so future sessions use them automatically.

## Task (Use Planning Mode)

Before making any changes, audit everything and present findings for approval. Organize into 3 phases:

### Phase 1: Audit (report findings, don't change anything)

**A. Find all converter/generator scripts:**
- Scan all Enhancement folders, `0. Tools/`, and any other project directories
- Find every script that generates or converts: md to docx, md/html to pdf, xlsx generation, xlsx editing, html report generation
- For each script found: filename, location, what it does, what branding/styles it uses (fonts, colors, header styles)
- Note which is the best/most complete version of each type

**B. Audit CLAUDE.md:**
- Read the current CLAUDE.md file(s) in the project root and any subdirectories
- List what's currently documented
- List what's outdated or wrong
- List what's missing (especially: tool references, file generation workflows, Excel editing rules)

**C. Report gaps:**
- Which file types have no reusable script yet?
- Which scripts are duplicated across sessions?
- What TGS branding details exist (colors, fonts, logos) and where?

Present Phase 1 findings and get my approval before Phase 2.

### Phase 2: Consolidate Tools

After approval:

- Create `0. Tools/` directory if it doesn't exist
- Copy the best version of each converter script into `0. Tools/` with standardized names:
  - `md_to_docx.py` -- markdown to branded Word doc
  - `md_to_pdf.py` or `html_to_pdf.py` -- whatever pattern we've used most
  - `xlsx_utils.py` -- Excel generation and in-place editing helpers
- Standardize TGS branding across all scripts (pull colors, fonts, header styles from the most polished existing version)
- Each script should accept input/output file paths as arguments so they're reusable
- Don't build from scratch if nothing exists -- just note it as a gap

### Phase 3: Update CLAUDE.md

Add or update these sections:

1. **Tools Reference** -- list each script in `0. Tools/`, what it does, how to call it
2. **File Generation Rules:**
   - Always use existing scripts from `0. Tools/` for Word, PDF, Excel generation
   - Don't rebuild converter scripts each session
   - For Word/PDF deliverables: write content as markdown first, then convert using the tool script
3. **Excel Editing Rules:**
   - When editing existing Excel files: read the file first with openpyxl, modify only what's requested, save to the same filename
   - Never regenerate from scratch unless explicitly told to
   - Preserve all formatting, formulas, and manual edits
   - If the user has made manual changes, read the current file state before making edits
4. **TGS Branding Reference** -- document the standard colors, fonts, and header styles in one place so all scripts and future sessions are consistent

## Output

- Phase 1: Audit report (in chat, for my review)
- Phase 2: Scripts in `0. Tools/`
- Phase 3: Updated `CLAUDE.md`
- Session report in `Enhancements/2026-02-16/`

## Rules

- Use planning mode throughout
- Don't change or overwrite anything until I approve Phase 1 findings
- If a file type has no existing script at all, flag it -- don't build from scratch without approval
- Keep scripts simple and well-commented
