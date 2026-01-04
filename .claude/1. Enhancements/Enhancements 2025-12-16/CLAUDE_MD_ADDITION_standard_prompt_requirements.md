# CLAUDE.md Addition: Standard Prompt Requirements

**Add this section after "Document Types (DOCTYPE)" section (~line 287)**

---

## Standard Prompt Requirements

Every PROMPT file should follow these conventions. Agents should read this section before starting any task.

### Required Prompt Sections
1. **Date** - When prompt was created
2. **For** - Target agent/team
3. **Situation** - Brief context (2-3 sentences max)
4. **Tasks** - Bulleted list of what to do
5. **Output** - Expected deliverables with file paths

### Required Output Elements
1. **File naming:** `DOCTYPE_YYYY-MM-DD_description.ext`
2. **Location:** Same folder as prompt, or `/mnt/user-data/outputs/`
3. **Report required:** Every task produces a REPORT unless purely code
4. **Lessons Learned section:** Include in every report:
   - What worked well
   - What was harder than expected
   - Recommendations for future

### Before Starting Any Task
1. Read this CLAUDE.md file fully
2. Check `LESSONS.md` for relevant prior work
3. State what "done" looks like before starting
4. If complexity is high (20+ tool calls), confirm scope with human first

### Before Finishing Any Task
1. Verify output follows naming convention
2. Include Lessons Learned section
3. Self-review: "If I were a critic, what would I flag?"
4. If files need renaming, propose names following convention

### Referencing These Standards

In prompts, simply add:
```
## Standards
Follow CLAUDE.md conventions for file naming, output format, and lessons learned.
```

This replaces repeating the full requirements in every prompt.

---

*Add this to CLAUDE.md to reduce redundancy in prompts and ensure consistent agent behavior.*
