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

    return NextResponse.json({ orgs: filtered })
  } catch (err) {
    console.error('Orgs API error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
