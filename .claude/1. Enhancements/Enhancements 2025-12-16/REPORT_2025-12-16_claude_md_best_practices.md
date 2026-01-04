# REPORT: CLAUDE.md Best Practices Research

**Date:** 2025-12-16
**Prepared by:** Claude Code CLI
**Purpose:** Research optimal elements for CLAUDE.md files

---

## Executive Summary

Research across official Anthropic documentation and community best practices reveals that effective CLAUDE.md files share common characteristics: **brevity, actionability, and relevance filtering**. The key insight is that Claude may ignore CLAUDE.md content it deems irrelevant to the current task, so every line must earn its place.

---

## Sources Consulted

- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices) - Official Anthropic engineering blog
- [Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) - HumanLayer deep dive
- [Manage Claude's memory](https://code.claude.com/docs/en/memory) - Official Claude Code documentation
- [Claude MD file guide](https://apidog.com/blog/claude-md/) - Community best practices
- [Claude Code Tips & Tricks](https://cloudartisan.com/posts/2025-04-16-claude-code-tips-memory/) - Memory optimization

---

## Optimal CLAUDE.md Elements

### Tier 1: Essential (Always Include)

| Element | Purpose | Example |
|---------|---------|---------|
| **Tech Stack** | Prevent wrong assumptions | `Framework: Next.js 14, DB: PostgreSQL 16` |
| **Key Commands** | Enable immediate action | `npm run build`, `python manage.py test` |
| **Project Structure** | Navigate codebase | Brief map of key directories |
| **Environment Setup** | Connect to services | DB host, credentials location |
| **Critical Gotchas** | Prevent known errors | "Always use schema prefix for queries" |

### Tier 2: High Value (Include If Relevant)

| Element | Purpose | When to Include |
|---------|---------|-----------------|
| **Code Patterns** | Consistency | When patterns aren't obvious from code |
| **Testing Instructions** | Verify work | When test setup is non-standard |
| **Domain Context** | Business understanding | Domain-specific terminology |
| **File References** | Deep knowledge | Point to detailed docs vs. duplicating |

### Tier 3: Low Value (Avoid or Separate)

| Element | Why Problematic | Alternative |
|---------|-----------------|-------------|
| **Style Guidelines** | Linters do this better | Use eslint/prettier/black |
| **Detailed Workflows** | Too task-specific | Separate PROMPT files |
| **Full Documentation** | Bloats context | Reference with `@path/to/doc` |
| **Historical Information** | Rarely relevant | Move to changelog/wiki |

---

## Key Research Findings

### 1. Claude Filters Irrelevant Content

> "Claude will ignore the contents of your CLAUDE.md if it decides that it is not relevant to its current task."

**Implication:** Every section must be broadly applicable. Task-specific instructions belong in separate files or prompts.

### 2. Context Rot is Real

> "There's a phenomenon called 'context rot' where the model's output quality deteriorates when the context window gets too full."

**Implication:** Shorter is better. Target under 300 lines (ideally under 100 for core file).

### 3. Instruction Capacity is Limited

> "Frontier thinking LLMs can follow ~150-200 instructions with reasonable consistency."

Since Claude Code's system prompt already contains ~50 instructions, your CLAUDE.md competes for the remaining capacity.

### 4. Pointers Beat Copies

> "Use file:line references to point toward authoritative code examples rather than embedding snippets that quickly become outdated."

**Implication:** Reference files, don't duplicate content.

### 5. Multi-File Organization is Supported

> "All .md files in `.claude/rules/` are automatically loaded as project memory."

**Implication:** Split large CLAUDE.md into focused rule files for better organization.

---

## Effective Patterns

### Pattern 1: The Minimal Core

```markdown
# Project
[One sentence description]

# Stack
- Language: X
- Framework: Y
- Database: Z

# Commands
- `cmd1`: purpose
- `cmd2`: purpose

# Critical Rules
- Rule 1
- Rule 2
```

**~20-30 lines.** Universally applicable. Task-specific guidance in separate files.

### Pattern 2: The Structured Reference

```markdown
# Overview
Brief description + link to full docs

# Quick Reference
Essential commands and paths

# Gotchas
Known issues that cause repeated problems

# See Also
@path/to/detailed_guide.md
@path/to/architecture.md
```

Uses imports (`@path`) for depth while keeping core file lean.

### Pattern 3: The Rules Directory

```
.claude/
├── CLAUDE.md (minimal core)
└── rules/
    ├── database.md
    ├── testing.md
    └── client-reports.md
```

Separates concerns. Each rule file is loaded but can have `paths:` frontmatter to scope to specific file types.

---

## Anti-Patterns to Avoid

### 1. The Kitchen Sink
Including everything "just in case." Leads to context rot and ignored instructions.

### 2. The Duplicator
Copying content from other docs. Creates maintenance burden and staleness.

### 3. The Novelist
Long narrative explanations. Claude prefers bullet points and tables.

### 4. The Enforcer
Style rules that linters should handle. Wastes instruction capacity.

### 5. The Historian
Detailed changelog and historical context. Rarely relevant to current task.

---

## Recommended Structure

Based on research, the optimal CLAUDE.md structure is:

```markdown
# [Project Name]
One-line description.

## Quick Reference
| Item | Value |
|------|-------|
| Key metric 1 | value |
| Key metric 2 | value |

## Stack & Environment
- Language: X
- Database: Y (connection: see `path/to/creds`)

## Commands
- `command`: what it does

## Critical Rules
- IMPORTANT: Rule that prevents common errors
- IMPORTANT: Another critical rule

## Project Structure
Brief map, 5-10 lines max

## Gotchas
| Issue | Solution |
|-------|----------|
| Common problem | Fix |

## See Also
- @path/to/detailed/doc.md
```

**Target:** 50-100 lines for main file, with deeper content in referenced files.

---

## Lessons Learned

### What Works
1. **Bullet points and tables** - Scannable, parseable
2. **Imperative language** - "Use X" not "You should consider using X"
3. **Emphasis markers** - "IMPORTANT:", "CRITICAL:", "YOU MUST"
4. **File references** - `@path/to/file` for depth
5. **Quick reference tables** - Key metrics at a glance

### What Doesn't Work
1. **Long paragraphs** - Get skimmed or ignored
2. **Redundant information** - If obvious from code, don't state it
3. **Style enforcement** - Use linters instead
4. **Historical context** - Rarely relevant to current task
5. **Task-specific instructions** - Belong in PROMPT files

---

## Recommendations

1. **Audit for relevance** - Remove anything not applicable to 80%+ of sessions
2. **Use emphasis strategically** - "IMPORTANT" for truly critical rules
3. **Reference, don't duplicate** - Point to detailed docs
4. **Consider rules directory** - Split by concern for large projects
5. **Iterate based on results** - Refine when Claude ignores instructions

---

*Generated by Claude Code CLI on 2025-12-16*
