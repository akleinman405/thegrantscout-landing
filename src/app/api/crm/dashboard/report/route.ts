import { NextResponse } from 'next/server'
import { readdirSync, readFileSync } from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic'

const KPI_DIR = '/Users/aleckleinman/Documents/TheGrantScout/5. Operations/3. KPI\'s/KPI'

export async function GET() {
  try {
    const files = readdirSync(KPI_DIR)
      .filter((f) => f.startsWith('OUTPUT_') && f.includes('weekly_linkedin_report') && f.endsWith('.html'))
      .sort()
      .reverse()

    if (files.length === 0) {
      return new NextResponse('<p>No LinkedIn report found.</p>', {
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
      })
    }

    const html = readFileSync(path.join(KPI_DIR, files[0]), 'utf-8')
    return new NextResponse(html, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    })
  } catch (err) {
    console.error('Dashboard report error:', err)
    return new NextResponse('<p>Error loading report.</p>', {
      status: 500,
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    })
  }
}
