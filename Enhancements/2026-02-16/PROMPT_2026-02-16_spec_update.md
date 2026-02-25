# PROMPT: Update Email Pipeline Spec to 6-Phase Structure

**Date:** 2026-02-16
**Agent:** Claude Code CLI
**Type:** Documentation update

---

## Start in Planning Mode

Read the current spec file first, then confirm proposed changes before editing.

## Context

The current `SPEC_email_pipeline.md` has 5 phases. Based on how the pipeline has evolved, we need to restructure to 6 phases that reflect the actual workflow from raw data to closed deals.

## Task

Update `SPEC_email_pipeline.md` with this revised phase structure:

### Phase 1: Get URLs
- Clean IRS-filed URLs (scripts 01)
- Validate URLs are alive (script 02)
- Search for missing URLs (script 03)
- URL validation is part of this phase, not a separate phase

### Phase 2: Get Emails & Contacts
- Scrape websites for emails, staff, metadata (scripts 04-05)
- Validate emails — syntax, MX, SMTP (scripts 06-07)
- Email validation is part of this phase, not a separate phase
- Materialized view for best email per org

### Phase 3: Build Prospect Profiles
- NEW PHASE — does not exist yet
- Assemble per-contact data needed for personalized outreach
- Person info: name, title, personal email
- Org info: mission, budget, NTEE, geographic focus, grant history
- Hooks: federal funding dependency, specific lost funding sources, specific replacement funders
- Foundation-specific: grantee impact data, capacity-building angle
- Nonprofit-specific: government funding vulnerability, named alternative funders
- Data comes from: existing 990 data, grant tables, website scrapes, federal funding cuts research, external enrichment

### Phase 4: Write Emails
- NEW PHASE — does not exist yet
- AI-generated personalized emails using prospect profiles
- Different templates/angles for foundations vs nonprofits
- Review and quality control pipeline

### Phase 5: Send Emails
- Campaign manager with subdomain rotation and pacing
- Gmail filters for bounce/reply/auto-reply sorting
- Multi-sender infrastructure

### Phase 6: Track & Respond
- NEW PHASE — does not exist yet
- Track opens, replies, bounces
- Classify responses (interested, not interested, wrong person, auto-reply)
- Follow-up sequences
- Response handling workflow

## What to Update

- Restructure the phase sections to match above
- Move URL validation into Phase 1, email validation into Phase 2
- Add Phase 3, 4, 6 as new sections with status "not started" and brief descriptions of what they'll contain
- Update the pipeline flow diagram
- Update the database quick-reference if new tables are implied
- Keep all existing detail for phases 1, 2, 5 — just reorganize

## Output

Updated `SPEC_email_pipeline.md` in the same location

## Rules

- Read the existing spec first
- Confirm proposed changes before editing
- Don't delete existing detail — reorganize it
- New phases get placeholder sections with "not started" status
