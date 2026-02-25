# PROMPT: Email Feedback via Nonprofit Personas

**Date:** 2026-02-16
**For:** Claude Code CLI

---

## Situation

We drafted 20 cold emails to nonprofits offering free foundation funder lists. Before sending to real prospects, we want to stress-test them through realistic personas who represent our target recipients. The goal is to catch tone issues, awkward phrasing, and anything that would make someone delete instead of reply.

Read the edited emails first: `Enhancements/2026-02-16/EMAILS_2026-02-16_nonprofit_cohort_1.md`

---

## The 4 Personas

Adopt each persona fully. Read every email as that person — with their history, biases, inbox fatigue, and priorities. Be brutally honest. Don't be polite about what doesn't work.

### Persona 1: Maria — Skeptical Executive Director
- Runs a $1.2M human services nonprofit in Chicago. 12 years as ED.
- Gets 15-20 cold emails per week from consultants, software vendors, and fundraising platforms. Deletes 90% after the first sentence.
- Has been burned twice by "free" offers that turned into aggressive sales funnels.
- Immediately suspicious of anyone who claims to know something about her org without having met her.
- Will Google any foundation name you mention to see if it's real and relevant.
- **Her test:** "Do I believe a real human wrote this to ME specifically, or is this a mail merge?"

### Persona 2: James — Busy but Open Program Director
- Works at a $3M education nonprofit in Atlanta. Handles some grant writing on top of his program role.
- Not the ED but forwards useful stuff up. Would forward a genuinely good resource to his boss.
- Reads the first 2 sentences. If they don't hook him, he's gone. Doesn't read past the fold.
- Doesn't hate vendors but has no time for vague promises. Concrete = good. Fluffy = delete.
- **His test:** "Is there something immediately useful here, or do I have to reply/sign up/schedule a call to get any value?"

### Persona 3: Diane — Grant-Savvy Development Director
- 15 years in nonprofit fundraising, $4M health nonprofit in Boston.
- Knows her foundation landscape well. Has a Candid login, reads 990s occasionally, tracks RFPs.
- Will immediately judge whether the foundation names you dropped are actually relevant to her org. If you name-drop Ford Foundation for a small health nonprofit, she'll roll her eyes.
- Impressed by specificity and accuracy. Turned off by anything that feels like it came from a database without human judgment.
- **Her test:** "Does this person actually understand my sector, or did they just run a query?"

### Persona 4: Kevin — First-Time Grant Seeker
- ED of a $600K youth development nonprofit in rural Kansas. 3 years in the role, came from the corporate world.
- Has never applied for a foundation grant. Gets most funding from a state contract and one local United Way.
- Intimidated by the grant landscape. Would genuinely appreciate help but doesn't know what's legitimate.
- Suspicious of "free" — assumes there's a catch. But also the most likely to reply if it feels genuine.
- **His test:** "Is this person trying to help me or trying to sell me something?"

---

## For Each Email (all 20), Each Persona Answers:

1. **Subject line:** Would you open this? (Yes/Maybe/No) Why?
2. **First 2 sentences:** Would you keep reading? Where specifically would you stop if not?
3. **Tone flags:** Quote any phrase that feels off — salesy, presumptuous, generic, or weird. Explain why.
4. **Foundation names:** Do these feel relevant to this org? Would you bother Googling them?
5. **The ask ("Want a copy?"):** Would you reply? What's your hesitation if not?
6. **Overall verdict:** Reply / Maybe-Reply / Delete. One sentence on what would change your answer.

---

## Then Synthesize Across All 20:

### Pattern Analysis
- Which emails got the most "Reply" verdicts across all 4 personas? Why?
- Which got the most "Delete" verdicts? What's the common problem?
- Are there specific PHRASES that multiple personas flagged? List them.
- Are there specific STRUCTURES (opening line patterns, foundation name-drop style, closing ask) that consistently worked or didn't?

### Tone Issues
- Any emails where the sender sounds like a consultant instead of a person trying to help?
- Any emails where "federal funding" reference feels forced or exploitative?
- Any emails that sound like a mail merge despite the personalization?
- Any place where the email assumes a relationship that doesn't exist? (This was flagged in the Shirley email — "funders worth a look" sounds like you're already their advisor)

### Recommended Rewrites
For the 5 worst-performing emails (most "Delete" verdicts), write a specific rewrite that fixes the issues the personas identified. Keep the same prospect, same foundations, same structure — just fix the tone and phrasing.

### Global Recommendations
- If you could change ONE thing across all 20 emails to increase reply rate, what would it be?
- Are there any words or phrases that should be banned from all future emails?
- Is the "federal funding" opening line helping or hurting? Should some emails skip it entirely?
- Is the foundation name-drop format working, or should it be presented differently?

---

## Output

`REPORT_2026-02-16_email_persona_feedback.md` saved to `Enhancements/2026-02-16/`

Structure:
1. Per-email feedback grid (20 emails × 4 personas — use a compact table format, not 80 separate sections)
2. Pattern analysis
3. Tone issues
4. 5 recommended rewrites
5. Global recommendations
