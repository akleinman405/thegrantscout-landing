import { readdirSync } from 'fs'
import path from 'path'

const CALL_NOTES_DIR = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales/1. Leads/Video Call Notes'
const BRIEF_DIR = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales/1. Leads/1. Viability/1. Nonprofits'

export interface Meeting {
  contact: string
  orgAbbrev: string
  date: string
  notesFile: string
  orgSlug: string | null
}

/** Map org abbreviations to brief slugs */
const ABBREV_TO_SLUG: Record<string, string | null> = {
  CWW: 'community_works_west',
  GPHI: 'global_positive_health_institute',
  ANU: null,
  IVBCF: 'inland_valley_business_and_community_foundation',
  AME: 'association_for_manufacturing_excellence',
}

/**
 * Parse Video Call Notes filenames to extract meeting info.
 * Formats:
 *   "{Contact} {OrgAbbrev} {YYYY-MM-DD}.md"
 *   "{Contact} {OrgAbbrev} - {YYYY-MM-DD}.md"
 */
export function getMeetings(): Meeting[] {
  let files: string[]
  try {
    files = readdirSync(CALL_NOTES_DIR)
  } catch {
    return []
  }

  const meetings: Meeting[] = []

  for (const file of files) {
    if (!file.endsWith('.md')) continue

    const basename = file.replace(/\.md$/, '')
    // Match: "Contact OrgAbbrev YYYY-MM-DD" or "Contact OrgAbbrev - YYYY-MM-DD"
    const match = basename.match(/^(.+?)\s+([A-Z]{2,})\s*-?\s*(\d{4}-\d{2}-\d{2})$/)
    if (!match) continue

    const [, contact, orgAbbrev, date] = match
    const slug = ABBREV_TO_SLUG[orgAbbrev] ?? null

    // Verify slug has a brief file if mapped
    let orgSlug = slug
    if (orgSlug) {
      try {
        const briefPath = path.join(BRIEF_DIR, `BRIEF_${orgSlug}.html`)
        const fs = require('fs')
        if (!fs.existsSync(briefPath)) orgSlug = null
      } catch {
        orgSlug = null
      }
    }

    meetings.push({
      contact,
      orgAbbrev,
      date,
      notesFile: file,
      orgSlug,
    })
  }

  // Sort by date descending
  meetings.sort((a, b) => b.date.localeCompare(a.date))
  return meetings
}
