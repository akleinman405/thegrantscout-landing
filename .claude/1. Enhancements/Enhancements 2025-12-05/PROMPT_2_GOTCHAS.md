# Prompt 2: Lessons Learned & Known Gotchas

Search the project for documented issues, bugs, fixes, and lessons learned. I need to compile a "Known Gotchas" section for CLAUDE.md.

**Search locations:**
1. Any lessons-learned folder or files
2. Git commit messages mentioning "fix", "bug", "issue"
3. Comments in code mentioning workarounds
4. CHANGELOG.md, BUILD_STATUS.md, any status reports mentioning issues
5. Parser files (especially 990-PF XML parsing issues)
6. matching_algorithm.py - any edge cases handled

**Look for patterns around:**
- XML/data parsing issues
- Grant amount formatting
- Foundation name normalization
- Database connection issues
- Common errors and their fixes
- Data quality issues discovered

**Output:**
1. A "Known Gotchas" table with: Issue | Details | Solution
2. A "Common Errors & Fixes" table with: Error Message | Cause | Fix
3. Any data quality notes worth documenting

**Format as markdown sections ready to paste into CLAUDE.md**
