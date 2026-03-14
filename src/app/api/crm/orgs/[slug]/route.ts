import { NextRequest, NextResponse } from 'next/server'
import { existsSync } from 'fs'

export const dynamic = 'force-dynamic'

const BRIEF_DIR = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales/1. Leads/1. Viability/1. Nonprofits'

function slugToName(slug: string): string {
  return slug
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params

  try {
    const briefPath = `${BRIEF_DIR}/BRIEF_${slug}.html`
    const hasBrief = existsSync(briefPath)

    if (!hasBrief) {
      return NextResponse.json({ error: 'Org not found' }, { status: 404 })
    }

    return NextResponse.json({
      slug,
      name: slugToName(slug),
      hasBrief: true,
    })
  } catch (err) {
    console.error('Org detail API error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
