# APPROVAL: CRM Architecture Proposal

**Date:** 2025-12-31
**Reference:** ARCH_2025-12-31_crm_proposal.md
**Status:** ✅ APPROVED - Proceed to build

---

## Stack Confirmed

**Supabase + Cloudflare Pages** - Approved as proposed.

---

## Answers to Your Questions

| Question | Answer |
|----------|--------|
| 1. Confirm stack? | **Yes** - Supabase + Cloudflare Pages |
| 2. Tasks entity? | **Yes, include it** - Unified follow-ups across calls and emails |
| 3. Additional fields? | See below |
| 4. Cloudflare Access? | **Skip for now** - Keep it simple, add later if needed |

---

## Additional Fields to Include

Add these to the schema:

### prospects table
```sql
linkedin_url TEXT,           -- Have this in fdn_mgmt data, useful for research
tier INTEGER                 -- Foundation mgmt contacts have tier rankings (1-7)
```

### calls table
```sql
duration_minutes INTEGER     -- Optional, nice for tracking call length
```

### source_lists table
```sql
segment TEXT CHECK(segment IN ('nonprofit', 'foundation', 'foundation_mgmt'))  -- Default segment for prospects from this list
```

---

## Folder Path Change

**Change from:**
```
/4. Sales & Marketing/7. CRM/crm/
```

**Change to:**
```
/4. Sales & Marketing/CRM/
```

Simpler, less nesting.

---

## Proceed with Build

Execute in this order:

1. Create Supabase project via CLI
2. Apply database schema (with additional fields above)
3. Build mobile-first frontend
4. Set up Cloudflare Pages deployment
5. Create import script for existing data
6. Test locally/staging before migration
7. Report back when ready for data migration approval

---

## Reminder: Data Migration is Separate Approval

Do NOT migrate production data until:
- [ ] CRM is deployed and accessible
- [ ] All views working (queue, log call, import, search)
- [ ] User tests from phone and confirms workflow works
- [ ] User explicitly approves migration

---

**Go build it.**
