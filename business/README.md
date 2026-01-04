# Business Operations

Non-technical folders for sales, marketing, client management, and website.

## Contents

| Folder | Purpose | Size |
|--------|---------|------|
| [sales-marketing/](sales-marketing/) | CRM, email campaigns, LinkedIn content | 39MB |
| [beta-testing/](beta-testing/) | Client feedback, questionnaires | 50MB |
| [website/](website/) | Landing page (Next.js) | ~50MB (excl. node_modules) |

## Sales & Marketing

- **CRM:** Supabase-based prospect tracking (`sales-marketing/CRM/`)
- **Email Campaign:** Automated outreach system
- **LinkedIn:** Content strategy and posting queue
- **Materials:** Call scripts, one-pagers

See `sales-marketing/README.md` for details.

## Beta Testing

- **Reports:** Client deliverables by round
- **Feedback:** Audio recordings, transcripts, summaries
- **Questionnaires:** Client intake forms

## Website

Next.js landing page at [thegrantscout.com](https://thegrantscout.com)

```bash
cd website/thegrantscout-landing
npm install  # Regenerate node_modules
npm run dev  # Start dev server
```

---

*Part of Cookie Cutter Data Science reorganization - 2026-01-04*
