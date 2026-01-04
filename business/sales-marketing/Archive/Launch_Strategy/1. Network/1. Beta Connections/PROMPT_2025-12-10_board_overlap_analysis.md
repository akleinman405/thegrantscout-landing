# Claude Code CLI Prompt
## Board/Officer Overlap Analysis — Find Actual Personal Connections

**Goal:** Identify people who serve on BOTH beta client boards AND foundation boards — these are true warm intro opportunities.

---

## Input

**Beta Client Board Members:** (from previous research)
- Horizons National: Vicki Craver, Eric Cochran, Erick Hong, Melissa Hughes-Humphrey, Mark Steffensen, Lorna Smith, Robert DeSantis, John Downer, Julie Martin, Maritza McClendon, Doug Michelman, Jon Michael Reese, Melinda Rolfs
- PSMF: Mike Durkin, Michael Ramsay, Joe Kiani
- RHF: Donald Hart, Catherine Collinson, Jeff Pollock, Andrew Bunn, Stuart Hartman, Stephanie Titus
- Arborbrook: Derek Durst (contact), board unknown
- Friendship Circle SD: Lyn Zanders, Cherri Lebus-Cary, Chalom Boudjnah, Yeruchem Eilfort, Dovid Smoller, Elisheva Green

**Foundation Officers:** Query from F990 data

---

## Analysis

### Step 1: Get Foundation Officers from F990

```sql
-- Get all foundation officers from foundations that funded beta clients
-- Plus large foundations in beta client sectors/states
SELECT DISTINCT
    df.name AS foundation_name,
    df.ein AS foundation_ein,
    df.state,
    df.total_assets,
    fo.officer_name,
    fo.title
FROM f990_2025.dim_foundations df
JOIN f990_2025.dim_foundation_officers fo ON df.ein = fo.ein
WHERE df.ein IN (
    -- Foundations that funded beta clients
    '812297831', '472630731', '136161746', '061518993', '270961125',
    '854241768', '061606588', '201076114', '383668101', '203959759',
    '274175885', '912172214', '581586283', '136083839',
    -- Known funders from questionnaire
    '061514402', '061252486', '136092448', '237966458', '206790446',
    '136015562', '136107758'
)
ORDER BY df.total_assets DESC, fo.officer_name;
```

### Step 2: Name Matching

```python
import pandas as pd
from fuzzywuzzy import fuzz

# Beta client board members (flatten to list)
beta_board = [
    'Vicki Craver', 'Eric Cochran', 'Erick Hong', 'Melissa Hughes-Humphrey',
    'Mark Steffensen', 'Lorna Smith', 'Robert DeSantis', 'John Downer',
    'Julie Martin', 'Maritza McClendon', 'Doug Michelman', 'Jon Michael Reese',
    'Melinda Rolfs', 'Mike Durkin', 'Michael Ramsay', 'Joe Kiani',
    'Donald Hart', 'Catherine Collinson', 'Jeff Pollock', 'Andrew Bunn',
    'Stuart Hartman', 'Stephanie Titus', 'Lyn Zanders', 'Cherri Lebus-Cary',
    'Chalom Boudjnah', 'Yeruchem Eilfort', 'Dovid Smoller', 'Elisheva Green',
    'Derek Durst'
]

# Load foundation officers from query
foundation_officers = pd.read_sql(query, conn)

# Fuzzy match names
matches = []
for beta_name in beta_board:
    for _, row in foundation_officers.iterrows():
        score = fuzz.ratio(beta_name.lower(), row['officer_name'].lower())
        if score > 85:  # High confidence match
            matches.append({
                'beta_person': beta_name,
                'foundation_person': row['officer_name'],
                'foundation': row['foundation_name'],
                'foundation_assets': row['total_assets'],
                'match_score': score
            })

matches_df = pd.DataFrame(matches)
print(matches_df.sort_values('match_score', ascending=False))
```

### Step 3: LinkedIn Cross-Reference (Manual/Optional)

For any matches found, verify via LinkedIn:
- Same person? Or just same name?
- Current role?
- Connection strength?

---

## Output

Save as `DATA_2025-12-10_board_overlaps.csv`:

```
beta_client, beta_person, foundation_name, foundation_ein, foundation_assets, match_confidence, verified
```

If overlaps found, these are TRUE warm intros — beta client board member can directly introduce you to the foundation.

---

## Deliverables

- [ ] List of name matches between beta boards and foundation officers
- [ ] Verification notes (same person or just same name?)
- [ ] Prioritized warm intro opportunities

---

*Prompt: PROMPT_2025-12-10_board_overlap_analysis.md*
