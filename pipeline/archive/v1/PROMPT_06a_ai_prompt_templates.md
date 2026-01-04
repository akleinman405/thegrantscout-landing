# PROMPT_06a: Phase 6a - AI Prompt Templates

**Date:** 2025-12-27
**Phase:** 6a
**Agent:** Research Team
**Estimated Time:** 3-4 hours
**Depends On:** PROMPT_04 (Report Assembly) complete
**Can Parallel With:** PROMPT_05 (Scraping)

---

## Objective

Design the AI prompt templates for generating narrative sections of the report. These prompts will be used with Claude API to generate "Why This Fits," "Positioning Strategy," and other text sections.

---

## Context

The report needs several AI-generated narrative sections:
1. **Why This Fits** - 3-4 sentences explaining the match
2. **Positioning Strategy** - 3-4 sentences of actionable advice
3. **Next Steps** - 3-5 action items with deadlines
4. **Key Strengths** - 3 bullet points for executive summary
5. **One Thing This Week** - Single most critical action

**Reference:** See `SPEC_2025-12-01_report_section_definitions.md` for detailed requirements.

---

## Tasks

### Task 1: Create `ai/prompts/why_this_fits.txt`

**Purpose:** Explain why this foundation is a good match for the client.

**Required Context (Input):**
- Client mission statement
- Client programs
- Client location
- Foundation name
- Foundation giving patterns (from Funder Snapshot)
- Comparable grant (if available)
- Current deadline (if known)

**Output Requirements:**
- 3-4 sentences maximum
- Must address: mission alignment, precedent (if available), timing
- Specific, not generic
- Reference actual data

**Prompt Template:**

```
You are writing the "Why This Fits" section for a grant opportunity report.

CLIENT INFORMATION:
- Organization: {client_name}
- Mission: {client_mission}
- Programs: {client_programs}
- Location: {client_city}, {client_state}
- Budget: {client_budget}

FOUNDATION INFORMATION:
- Foundation: {foundation_name}
- Annual Giving: ${annual_giving:,.0f} across {grant_count} grants
- Typical Grant: ${median_grant:,.0f} (range: ${min_grant:,.0f} - ${max_grant:,.0f})
- Geographic Focus: {top_state} ({top_state_pct:.0%}), {in_state_pct:.0%} in-state
- Giving Style: {general_support_pct:.0%} general support, {program_specific_pct:.0%} program-specific
- Funding Trend: {funding_trend}

COMPARABLE GRANT (if available):
{comparable_grant_text}

DEADLINE: {deadline}

INSTRUCTIONS:
Write 3-4 sentences explaining why this foundation is a good match for this client.

Address these points:
1. Mission/program alignment (1 sentence)
2. Precedent - similar organizations they've funded (1 sentence, if comparable grant available)
3. Timing rationale - why pursue now (1 sentence)

Be specific. Reference the actual data provided. Do not be generic.

Do NOT use phrases like "This foundation would be a good fit because..." - start with the substance directly.
```

**Example Good Output:**
> {Foundation_name}'s focus on education in California aligns directly with your after-school tutoring programs, and their 78% in-state giving pattern favors Bay Area organizations like yours. They funded Oakland Youth Services $45,000 last year for similar academic support work, demonstrating openness to your model. With their rolling deadline and your program expansion planned for fall, applying this quarter positions you well for consideration in their next funding cycle.

**Example Bad Output (too generic):**
> This foundation would be a great fit for your organization. They fund education programs and you do education work. Their giving patterns suggest they might be interested in your programs.

### Task 2: Create `ai/prompts/positioning_strategy.txt`

**Purpose:** Actionable advice on how to frame the application.

**Required Context:**
- All Funder Snapshot metrics
- Client strengths
- Any connections found
- Deadline info

**Output Requirements:**
- 3-4 sentences
- MUST reference specific Funder Snapshot data
- Include: giving style recommendation, ask amount, geographic/sector positioning, relationship leverage

**Prompt Template:**

```
You are writing the "Positioning Strategy" section for a grant opportunity report.

FUNDER SNAPSHOT:
- Annual Giving: ${annual_giving:,.0f} across {grant_count} grants
- Typical Grant: ${median_grant:,.0f} (range: ${min_grant:,.0f} - ${max_grant:,.0f})
- Geographic Focus: {top_state} ({top_state_pct:.0%}), {in_state_pct:.0%} in-state overall
- Repeat Funding Rate: {repeat_rate:.0%} of recipients funded 2+ times
- Giving Style: {general_support_pct:.0%} general support, {program_specific_pct:.0%} program-specific
- Recipient Profile: Typically ${budget_min:,.0f}-${budget_max:,.0f} budget, {primary_sector} focus
- Funding Trend: {funding_trend} ({trend_change_pct:+.0%} over 3 years)

CLIENT CONTEXT:
- Location: {client_city}, {client_state}
- Budget: {client_budget}
- Strengths: {client_strengths}

CONNECTIONS (if any):
{connections_text}

INSTRUCTIONS:
Write 3-4 sentences of actionable positioning advice.

You MUST reference specific data from the Funder Snapshot. Include:
1. Giving style recommendation - general support vs. program-specific framing (sentence 1)
2. Suggested ask amount based on their typical grant (sentence 2)
3. Geographic or sector positioning (sentence 3)
4. Relationship leverage or timing advice (sentence 4)

Be specific. Use actual numbers. Do not give generic advice.
```

**Example Good Output:**
> Emphasize general operating support—62% of their grants use this structure, and they rarely fund narrow project proposals. Their $45K median suggests requesting $40,000-50,000; their largest grant was $150K but that went to a university. Highlight your California presence prominently; 78% of their giving stays in-state. If possible, mention your connection to Oakland Youth Services, which they've funded for 5 consecutive years.

### Task 3: Create `ai/prompts/next_steps.txt`

**Purpose:** Generate actionable next steps for each opportunity.

**Required Context:**
- Foundation name
- Deadline
- Application requirements
- Contact info
- Prior relationship status

**Output Requirements:**
- 3-5 action items
- Each has: Action, Deadline, Owner
- Specific deliverables ("Draft 2-page LOI" not "Work on application")

**Prompt Template:**

```
You are generating "Next Steps" for a grant opportunity.

OPPORTUNITY:
- Foundation: {foundation_name}
- Deadline: {deadline}
- Contact: {contact_name}, {contact_email}
- Prior Relationship: {prior_relationship}

APPLICATION REQUIREMENTS:
{requirements_list}

TODAY'S DATE: {today}

INSTRUCTIONS:
Generate 3-5 specific next steps for pursuing this opportunity.

For each step, provide:
- Action: Specific task with deliverable
- Deadline: Target date (work backward from application deadline)
- Owner: Role (Grants Manager, ED, Program Director, Finance, Development)

Use specific verbs and deliverables:
- GOOD: "Draft 2-page LOI concept" 
- BAD: "Work on application"

If deadline is "Rolling", create reasonable internal deadlines.
If contact info available, include outreach as a step.

Output as JSON array:
[
  {{"action": "...", "deadline": "...", "owner": "..."}},
  ...
]
```

### Task 4: Create `ai/prompts/key_strengths.txt`

**Purpose:** Generate 3 key strengths for executive summary.

**Required Context:**
- Client profile
- This week's opportunities (all 5)
- Match rationale for each

**Output Requirements:**
- Exactly 3 bullet points
- Each 1 sentence
- Specific to intersection of client strengths AND this week's funders

**Prompt Template:**

```
You are writing "Key Strengths" for the executive summary of a grant report.

CLIENT:
- Organization: {client_name}
- Location: {client_city}, {client_state}
- Programs: {client_programs}
- Budget: {client_budget}

THIS WEEK'S TOP 5 FOUNDATIONS:
{opportunities_summary}

INSTRUCTIONS:
Write exactly 3 key strengths that position this client well for THIS WEEK'S opportunities.

Each strength should:
- Be 1 sentence
- Reference specific data (not generic)
- Connect client attribute to funder preference

Format:
1. **[Strength Name]:** [One sentence explanation]
2. **[Strength Name]:** [One sentence explanation]
3. **[Strength Name]:** [One sentence explanation]

Example:
**Proven Precedent:** Mid-Pacific School received $200,000 from Atherton for track facilities in 2024—direct model for your application.

Do NOT write generic strengths like "Strong mission" or "Good track record."
```

### Task 5: Create `ai/prompts/one_thing.txt`

**Purpose:** Single most critical action for busy executives.

**Required Context:**
- All 5 opportunities with deadlines
- Urgency assessment

**Output Requirements:**
- Exactly 1 sentence
- Most urgent action
- Specific deadline or contact

**Prompt Template:**

```
You are writing the "If You Only Do One Thing This Week" statement.

THIS WEEK'S OPPORTUNITIES:
{opportunities_with_deadlines}

INSTRUCTIONS:
Write exactly ONE sentence stating the single most critical action.

Selection criteria:
1. Nearest hard deadline, OR
2. Highest strategic impact if no urgent deadlines

Include specific:
- Action verb
- Foundation/contact name
- Date

Format as: **[Action with specific deadline or contact]**

Good example:
**Contact NIOSH program officer by November 25 to discuss your December 12 application.**

Bad example:
**Start working on your grant applications.**
```

---

## Output Files

| File | Description |
|------|-------------|
| `ai/prompts/why_this_fits.txt` | Why This Fits prompt template |
| `ai/prompts/positioning_strategy.txt` | Positioning Strategy prompt template |
| `ai/prompts/next_steps.txt` | Next Steps prompt template |
| `ai/prompts/key_strengths.txt` | Key Strengths prompt template |
| `ai/prompts/one_thing.txt` | One Thing prompt template |
| `ai/prompts/README.md` | Documentation of all prompts |

---

## Done Criteria

- [ ] All 5 prompt templates created
- [ ] Each template specifies required context variables
- [ ] Each template includes good/bad examples
- [ ] Templates follow report spec requirements
- [ ] README documents variable requirements for each prompt

---

## Verification

### Manual Testing

For each prompt:
1. Fill in with sample data
2. Run through Claude (claude.ai or API)
3. Evaluate output quality:
   - Is it specific (uses actual data)?
   - Is it the right length?
   - Does it avoid generic language?
   - Would it be useful to a grants manager?

### Test Data

Use one of the beta clients (PSMF, SNS, RHF) with real funder snapshot data.

---

## Notes

### Variable Placeholders

Use Python format string style: `{variable_name}`

For numbers with formatting: `{amount:,.0f}` (comma-separated, no decimals)
For percentages: `{rate:.0%}` (percentage with no decimals)

### Prompt Length

Keep prompts under 2000 tokens to leave room for context.

### Iteration

These prompts will be refined in PROMPT_06b based on output quality.

---

## Handoff

After completion:
1. Test each prompt manually with sample data
2. Document any quality issues observed
3. PM reviews before proceeding to PROMPT_06b

---

*Next: PROMPT_06b (AI Integration & Iteration)*
