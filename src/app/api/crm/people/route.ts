import { NextRequest, NextResponse } from 'next/server'
import { getMeetings } from '@/lib/meetings'
import { findLead } from '@/lib/dripify-leads'

export const dynamic = 'force-dynamic'

function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

export async function GET(request: NextRequest) {
  const q = (request.nextUrl.searchParams.get('q') || '').toLowerCase()
  const limit = Math.min(Math.max(parseInt(request.nextUrl.searchParams.get('limit') || '50', 10) || 50, 1), 100)
  const offset = Math.max(parseInt(request.nextUrl.searchParams.get('offset') || '0', 10) || 0, 0)

  try {
    const meetings = getMeetings()

    const people = meetings.map((m) => {
      const firstName = m.contact.split(' ')[0]
      const lead = findLead(firstName)

      return {
        id: slugify(m.contact),
        name: lead ? `${lead.firstName} ${lead.lastName}` : m.contact,
        title: lead?.title || null,
        company: lead?.company || m.orgAbbrev,
        email: lead?.email || null,
        phone: lead?.phone || null,
        linkedin_url: lead?.linkedinUrl || null,
        meeting_date: m.date,
        notes_file: m.notesFile,
        org_slug: m.orgSlug,
      }
    })

    const filtered = q
      ? people.filter(
          (p) =>
            p.name.toLowerCase().includes(q) ||
            (p.company && p.company.toLowerCase().includes(q))
        )
      : people

    const paginated = filtered.slice(offset, offset + limit)

    return NextResponse.json({ people: paginated, total: filtered.length, limit, offset })
  } catch (err) {
    console.error('People API error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
