# Lessons Learned: Prospect Call List Generation
**Date:** 2025-12-12

---

## What Worked Well

1. **Progressive filter diagnostics** — Testing each filter individually before combining revealed which criteria were too restrictive. This saved time vs. debugging a zero-result query.

2. **Prospects table already had contact columns** — The schema included `contact_name`, `contact_title`, `contact_phone` columns, though they were empty. This provided a clear target for enrichment.

3. **Officers table enrichment** — The officer ranking query (CEO > ED > President > Founder) successfully matched 25/27 prospects (93%) with a contact name.

4. **Relaxation order in prompt** — Having a pre-defined relaxation order (remove yoy first, then expand employee count, etc.) made decision-making straightforward when strict criteria returned < 20 results.

---

## What Was Harder Than Expected

1. **`likely_active_fundraiser` too restrictive** — Only 216 of 74,144 prospects (0.3%) have this flag set. Combined with other filters, it produced only 2 matches. This flag needs investigation — either the scoring is too strict or data population is incomplete.

2. **No phone numbers anywhere** — Expected some phone data in either prospects or officers table, but neither had it. Phone sourcing will require external enrichment (website scraping, LinkedIn API, or manual lookup).

3. **Credential file path mismatch** — CLAUDE.md referenced `Postgresql_Info.txt` but actual file was `Postgresql Info.txt` (space vs. underscore). Minor but caused initial read failure.

---

## What I Wish I Knew Going In

1. **The `likely_active_fundraiser` population rate** — Would have saved time knowing upfront this was a 0.3% flag. Prompt should note which filters are sparse.

2. **Contact columns in prospects are empty by design** — They're placeholders for enrichment, not pre-populated. Documentation could clarify.

3. **Officers table links to BOTH pf_return_id and np_return_id** — Had to use EIN for the join since prospect EINs could be from either return type.

---

## Data Quality Issues Discovered

| Issue | Impact | Recommendation |
|-------|--------|----------------|
| `likely_active_fundraiser` extremely sparse (0.3%) | Filter unusable in practice | Investigate scoring algorithm or expand criteria |
| Zero phone numbers in prospects table | All calls need manual phone lookup | Consider ProPublica/LinkedIn enrichment |
| 2/27 (7%) prospects had no officer match | Minor gap | Acceptable — these are small orgs that may not file officer info |
| `has_concrete_mission` very selective (10% of prospects) | May be filtering good candidates | Review mission classification criteria |

---

## Suggestions for Next Time

1. **Add filter population stats to prompt** — Show what % of prospects pass each filter before combining them.

2. **Pre-check filter combinations** — A diagnostic query that tests progressive filter combos would identify issues earlier.

3. **Phone enrichment workflow** — Create a separate step/tool for phone lookup (perhaps website scraping or API-based).

4. **Consider batch calling** — With only 27 prospects, this is a manageable list for manual calling. Future batches could be larger with relaxed criteria.

---

*Generated: 2025-12-12*
