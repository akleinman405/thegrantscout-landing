import { NextRequest, NextResponse } from 'next/server'
import { readdirSync } from 'fs'

export const dynamic = 'force-dynamic'

const BRIEF_DIR = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales/1. Leads/1. Viability/1. Nonprofits'

function slugToName(slug: string): string {
  return slug
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

export async function GET(request: NextRequest) {
  const q = (request.nextUrl.searchParams.get('q') || '').toLowerCase()
  const limit = Math.min(Math.max(parseInt(request.nextUrl.searchParams.get('limit') || '50', 10) || 50, 1), 100)
  const offset = Math.max(parseInt(request.nextUrl.searchParams.get('offset') || '0', 10) || 0, 0)

  try {
    const files = readdirSync(BRIEF_DIR)
      .filter((f) => f.startsWith('BRIEF_') && f.endsWith('.html'))
      .sort()

    const orgs = files.map((f) => {
      const slug = f.replace(/^BRIEF_/, '').replace(/\.html$/, '')
      const name = slugToName(slug)
      return { slug, name, has_brief: true }
    })

    const filtered = q
      ? orgs.filter((o) => o.name.toLowerCase().includes(q))
      : orgs

    const paginated = filtered.slice(offset, offset + limit)

    return NextResponse.json({ orgs: paginated, total: filtered.length, limit, offset })
  } catch (err) {
    console.error('Orgs API error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
