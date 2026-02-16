---
description: Smart commit with conventional format and TheGrantScout conventions
argument-hint: Commit message hint (optional)
allowed-tools: Bash(git *), Bash(ls *), Read, Grep, Glob
---

# Smart Commit

Create a well-structured git commit following TheGrantScout conventions.

Optional hint for commit message: $ARGUMENTS

## Instructions

1. **Assess current state** by running in parallel:
   - `git status` to see all staged, unstaged, and untracked files
   - `git diff --cached --stat` to see what's staged
   - `git diff --stat` to see what's unstaged
   - `git log --oneline -5` to see recent commit style

2. **If nothing is staged**, suggest files to stage based on what's modified. Ask the user to confirm before staging. Prefer staging specific files over `git add -A`.

3. **Never stage these files** (warn if the user tries):
   - `.env`, `.env.*` files
   - `Postgresql Info.txt`
   - `*.pem`, `*.key`, `*.jks`
   - `credentials.json`, `google-services.json`

4. **Draft a commit message** using conventional commit format:

   ```
   type: brief description

   - Detail 1
   - Detail 2

   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
   ```

   Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `data`, `report`, `config`

   **TheGrantScout-specific types:**
   - `data:` — Database imports, data cleaning, schema changes
   - `report:` — Client report generation or delivery
   - `config:` — Pipeline config, model coefficients, client profiles

   Guidelines:
   - Keep the first line under 72 characters
   - Use imperative mood ("Add" not "Added")
   - Reference REPORT files in the body when applicable
   - If `$ARGUMENTS` was provided, use it as the basis for the message

5. **Present the commit message** to the user and ask for confirmation before committing.

6. **Execute the commit** using a HEREDOC for the message:
   ```bash
   git commit -m "$(cat <<'EOF'
   type: message

   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
   EOF
   )"
   ```

7. **Show the result**: Run `git log --oneline -3` to confirm the commit landed.

8. **Do NOT push** unless the user explicitly asks.
