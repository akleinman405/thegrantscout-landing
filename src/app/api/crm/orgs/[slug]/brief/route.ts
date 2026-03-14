import { NextRequest, NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import { existsSync } from 'fs'

export const dynamic = 'force-dynamic'

const BRIEF_DIR = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales/1. Leads/1. Viability/1. Nonprofits'

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params

  try {
    const briefPath = `${BRIEF_DIR}/BRIEF_${slug}.html`

    if (!existsSync(briefPath)) {
      return NextResponse.json({ error: 'No brief found' }, { status: 404 })
    }

    const html = await readFile(briefPath, 'utf-8')
    return new NextResponse(html, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    })
  } catch (err) {
    console.error('Brief API error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
