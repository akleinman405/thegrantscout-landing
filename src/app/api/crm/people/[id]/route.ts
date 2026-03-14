import { NextRequest, NextResponse } from 'next/server'
import { getMeetings } from '@/lib/meetings'
import { findLead } from '@/lib/dripify-leads'
import { readFileSync } from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic'

const CALL_NOTES_DIR = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales/1. Leads/Video Call Notes'

function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params

  try {
    const meetings = getMeetings()
    const meeting = meetings.find((m) => slugify(m.contact) === id)

    if (!meeting) {
      return NextResponse.json({ error: 'Person not found' }, { status: 404 })
    }

    const firstName = meeting.contact.split(' ')[0]
    const lead = findLead(firstName)

    // Read meeting notes
    let notesContent: string | null = null
    try {
      const mdPath = path.join(CALL_NOTES_DIR, meeting.notesFile)
      notesContent = readFileSync(mdPath, 'utf-8')
    } catch { /* file not found */ }

    return NextResponse.json({
      person: {
        name: lead ? `${lead.firstName} ${lead.lastName}` : meeting.contact,
        title: lead?.title || null,
        company: lead?.company || meeting.orgAbbrev,
        email: lead?.email || null,
        phone: lead?.phone || null,
        linkedinUrl: lead?.linkedinUrl || null,
        website: lead?.website || null,
      },
      meeting: {
        date: meeting.date,
        orgAbbrev: meeting.orgAbbrev,
        orgSlug: meeting.orgSlug,
      },
      notes: notesContent,
    })
  } catch (err) {
    console.error('Person detail API error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
